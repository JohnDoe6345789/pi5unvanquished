# Pi 5 Unvanquished Server Stack

Run an Unvanquished dedicated server on a Raspberry Pi 5 (or other ARM64 host) with a bundled LocalXpose UDP tunnel and a lightweight Flask/React dashboard. An optional CapRover bootstrap script is included for cloud deployments.

## What this repo contains
- `compose.yml`: Docker Compose stack for the game server, LocalXpose sidecar, and web dashboard.
- `Dockerfile` / `entrypoint.sh`: Builds the dedicated server image (configurable version/arch) and starts it with the right home path and ports.
- `webui/Dockerfile`, `webui/app.py`: Flask API that queries the server and LocalXpose status, plus an embedded React/MUI dashboard.
- `localxpose/`: Minimal image that wraps the `loclx` binary with a tiny status API the dashboard can read.
- `deploy/src/bootstrap.ts`: CapRover automation that turns `compose.yml` into CapRover apps and deploys them.
- `pkg/`: Upstream `.dpk` assets you can copy into your server home if you want to preload maps/content.
- `daemon`, `daemonded`, `pkg/`, and `game/` are prebundled for ARM64; no download needed at build time.

## Requirements
- Docker and Docker Compose v2 (images are ARM64; Docker Desktop/buildx can run them on AMD64 via binfmt, or build on an ARM64 host)
- LocalXpose account + access token (for the UDP tunnel)
- Node 18+ only if you plan to use the CapRover bootstrap script

## Quick start (local compose)
1) Start the stack with your LocalXpose token:
```
# PowerShell
$env:LOCALXPOSE_ACCESS_TOKEN="xxxx" ; docker compose up --build -d

# Bash
LOCALXPOSE_ACCESS_TOKEN=xxxx docker compose up --build -d
```
2) On first run, the entrypoint seeds `server.cfg` from `/opt/unvanquished/game/server.cfg` into the Docker volume (`$UNV_HOME/config/server.cfg`) and drops a symlink `$UNV_HOME/game -> /opt/unvanquished/game` so all bundled configs/rotations are visible. Edit `server.cfg` via:
   - `docker compose run --rm unvanq-server sh -c "vi $UNV_HOME/config/server.cfg"` (or use `nano` if installed), or
   - `docker cp` a local file into the container: `docker cp ./game/server.cfg unvanq-server:$UNV_HOME/config/server.cfg`
3) Open the dashboard at `http://localhost:8080` and copy the public UDP address to join your server.

### LocalXpose config
- The LocalXpose sidecar runs `loclx tunnel --raw-mode udp --to unvanq-server:27960` and exposes a tiny status API on port 4040 for the dashboard.
- Set `LOCALXPOSE_REGION`, `LOCALXPOSE_PORT`, or `LOCALXPOSE_RESERVED_ENDPOINT` in your environment if you need a specific region/endpoint.
- The container expects `LOCALXPOSE_ACCESS_TOKEN` and will report errors via `docker compose logs localxpose` if the tunnel fails to start.
- This stack keeps the game server off the Unvanquished master list by default (`UNV_DISABLE_MASTERS=true` in `compose.yml`). Set it to `false` if you really want to advertise, or mirror the behavior in your own `server.cfg` with `seta sv_master1 ""` ... `seta sv_master5 ""`.

## Configuring the game server
- `UNV_HOME` (default `/var/unvanquished-home`): persisted Docker volume (`unvanq-home`) for configs, logs, and extra pk3/dpk content.
- `UNV_PORT` / `UNV_PORT6`: UDP ports the server binds inside the container (default 27960).
- `UNV_SERVER_CFG`: Filename inside `config/` to execute on start (`server.cfg` by default).
- Build args: override `UNV_VERSION` and `UNV_ARCH` in `docker compose build` if you need a different upstream release/architecture.

Example `server.cfg` to get going:
```
set sv_hostname "Pi-5 Unvanquished"
seta rconPassword "changeme"
map plat23
```

## Web dashboard
- Runs from `webui/app.py`, serving `/api/status` (game server query) and `/api/localxpose_status`.
- Reads `UNV_SERVER_HOST`, `UNV_SERVER_PORT`, and `LOCALXPOSE_STATUS_URL` from the environment (see `compose.yml` defaults).
- UI shows server info/players and a copy-to-clipboard LocalXpose URL.

## Optional: CapRover bootstrap
1) `cd deploy`
2) `npm install`
3) Set env: `CAPROVER_URL`, `CAPROVER_PASSWORD`, optional `CAPROVER_EMAIL`, `UNV_PROJECT_NAME`, `COMPOSE_FILE` (defaults to `compose.yml`).
4) `npm run bootstrap` to create/update apps and trigger deployments based on your compose file.

## Troubleshooting
- No LocalXpose URL? Ensure `LOCALXPOSE_ACCESS_TOKEN` is set and the LocalXpose container can reach `unvanq-server`; check `docker compose logs localxpose`.
- Custom config ignored? Verify the Docker volume has `$UNV_HOME/config/server.cfg` and it matches `UNV_SERVER_CFG`; otherwise the entrypoint just runs `+map plat23`.
- Changed version/arch? Rebuild the image with new `UNV_VERSION`/`UNV_ARCH` build args before restarting the stack.

## Joining from Steam (or any Quake3-style client)
- Grab the public UDP endpoint from the dashboard (e.g., `udp://us.loclx.io:27960`).
- In a Steam game launch option or console, append `+connect <endpoint>` (omit the `udp://` prefix), for example:
  - Launch option: `+connect us.loclx.io:27960`
  - In-game console: `\connect us.loclx.io:27960`
- If you expose a different port (set `LOCALXPOSE_PORT` or use a reserved endpoint), connect to that port instead of `27960`.
