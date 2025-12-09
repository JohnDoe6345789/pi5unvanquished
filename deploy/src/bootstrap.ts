import fs from "fs";
import path from "path";
import yaml from "js-yaml";
import {
  CaproverAPI,
  AppDefinition,
  PortMapping
} from "caprover-api";

const CAPROVER_URL = process.env.CAPROVER_URL || "https://captain.example.com";
const CAPROVER_PASSWORD = process.env.CAPROVER_PASSWORD || "";
const CAPROVER_EMAIL = process.env.CAPROVER_EMAIL || "captain@root";

const PROJECT_NAME = process.env.UNV_PROJECT_NAME || "unvanquished";
const COMPOSE_FILE = process.env.COMPOSE_FILE || "../compose.yml";

if (!CAPROVER_PASSWORD) {
  console.error("ERROR: CAPROVER_PASSWORD not set.");
  process.exit(1);
}

function loadCompose(): any {
  const full = path.resolve(COMPOSE_FILE);
  if (!fs.existsSync(full)) {
    throw new Error(`compose file not found: ${full}`);
  }
  const raw = fs.readFileSync(full, "utf8");
  return yaml.load(raw);
}

function normalizeEnv(env: any): { key: string; value: string }[] {
  const out: { key: string; value: string }[] = [];
  if (!env) return out;

  if (Array.isArray(env)) {
    for (const entry of env) {
      if (typeof entry !== "string") continue;
      const idx = entry.indexOf("=");
      if (idx === -1) out.push({ key: entry, value: "" });
      else out.push({ key: entry.slice(0, idx), value: entry.slice(idx + 1) });
    }
    return out;
  }

  if (typeof env === "object") {
    for (const [k, v] of Object.entries(env)) {
      out.push({ key: k, value: v == null ? "" : String(v) });
    }
  }
  return out;
}

function deriveContainerHttpPort(name: string, svc: any): number | undefined {
  // Heuristic: if service has "ports", use the container side.
  const p = svc.ports;
  if (Array.isArray(p)) {
    for (const spec of p) {
      if (typeof spec === "string") {
        const right = spec.split(":").pop()!;
        const cp = parseInt(right.split("/")[0], 10);
        if (!isNaN(cp)) return cp;
      }
    }
  }
  // Fallback: if the name looks like a web UI, assume 8080
  if (name.toLowerCase().includes("web")) return 8080;
  if (name.toLowerCase().includes("ui")) return 8080;
  return undefined;
}

function deriveBuildOrImage(svc: any): { imageName?: string; dockerfilePath?: string } {
  if (svc.image) return { imageName: svc.image };

  if (svc.build) {
    if (typeof svc.build === "string") {
      return {
        dockerfilePath: path.posix.join(svc.build, "Dockerfile")
      };
    }
    if (typeof svc.build === "object") {
      const context = svc.build.context || ".";
      const dockerfile = svc.build.dockerfile || "Dockerfile";
      return {
        dockerfilePath: path.posix.join(context, dockerfile)
      };
    }
  }
  return {};
}

function deriveCommand(svc: any): string | undefined {
  const c = svc.command;
  if (!c) return undefined;
  if (typeof c === "string") return c;
  if (Array.isArray(c)) return c.map((x) => String(x)).join(" ");
  return undefined;
}

function derivePortMapping(svc: any): PortMapping[] {
  const out: PortMapping[] = [];
  const ports = svc.ports || [];
  for (const p of ports) {
    if (typeof p === "string") {
      // "8080:8080"
      const [host, cont] = p.split(":");
      if (host && cont) {
        out.push({
          hostPort: host.split("/")[0],
          containerPort: cont.split("/")[0]
        });
      }
    }
  }
  return out;
}

async function main() {
  console.log("Connecting to CapRover:", CAPROVER_URL);

  const cap = new CaproverAPI({
    dashboardUrl: CAPROVER_URL,
    password: CAPROVER_PASSWORD
  });

  // Login
  await cap.login();

  // ------------------------------------------------------------------
  // Step 1: Project check/create
  // ------------------------------------------------------------------
  const projects = await cap.getProjects();
  let projectId: string | undefined;
  for (const p of projects) {
    if (p.name === PROJECT_NAME) {
      projectId = p.projectId;
      break;
    }
  }

  if (!projectId) {
    console.log(`Project "${PROJECT_NAME}" does not exist — creating…`);
    const created = await cap.createProject({ name: PROJECT_NAME });
    projectId = created.projectId;
    console.log("Created project with ID:", projectId);
  } else {
    console.log(`Using existing project "${PROJECT_NAME}" with ID ${projectId}`);
  }

  // ------------------------------------------------------------------
  // Step 2: Parse compose.yml
  // ------------------------------------------------------------------
  const compose = loadCompose();
  const services = compose.services || {};
  const serviceNames = Object.keys(services);

  if (serviceNames.length === 0) {
    console.error("compose.yml has no services.");
    process.exit(1);
  }

  // ------------------------------------------------------------------
  // Step 3: For each service → create/update app
  // ------------------------------------------------------------------
  for (const svcName of serviceNames) {
    const svc = services[svcName];
    console.log(`\n=== Processing service: ${svcName} ===`);

    const envVars = normalizeEnv(svc.environment);
    const portMapping = derivePortMapping(svc);
    const httpPort = deriveContainerHttpPort(svcName, svc);
    const { imageName, dockerfilePath } = deriveBuildOrImage(svc);
    const command = deriveCommand(svc);

    console.log({
      envVars,
      portMapping,
      httpPort,
      imageName,
      dockerfilePath,
      command
    });

    // Build AppDefinition payload
    const appDef: AppDefinition = {
      appName: svcName,
      notExposeAsWebApp: httpPort ? false : true,
      hasPersistentData: false,
      projectId,
      description: `Auto-generated from compose.yml: ${svcName}`
    };

    if (httpPort) appDef.containerHttpPort = httpPort;
    if (imageName) appDef.imageName = imageName;
    if (dockerfilePath) appDef.dockerfilePath = dockerfilePath;

    if (envVars.length > 0) {
      appDef.envVars = envVars;
    }

    if (portMapping.length > 0) {
      appDef.portsMapping = portMapping;
    }

    if (command) {
      appDef.cmd = command;
    }

    // Send to CapRover API
    console.log(`Deploying/Updating app "${svcName}"…`);

    await cap.updateAppDefinition({
      appDefinitions: [appDef]
    });

    // After definition update, trigger deployment
    await cap.deployApp({
      appName: svcName,
      captainDefinitionContent: ""
    });

    console.log(`App "${svcName}" deployed.`);
  }

  console.log("\nAll services processed successfully.");
}

main().catch((err) => {
  console.error("ERROR:", err);
  process.exit(1);
});
