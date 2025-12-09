# Pi 5 Unvanquished Server Stack

Run an Unvanquished dedicated server on a Raspberry Pi 5 (or other ARM64 host) with a bundled ngrok UDP tunnel and a lightweight Flask/React dashboard. An optional CapRover bootstrap script is included for cloud deployments.

## What this repo contains
- `compose.yml`: Docker Compose stack for the game server, ngrok sidecar, and web dashboard.
- `Dockerfile` / `entrypoint.sh`: Builds the dedicated server image (configurable version/arch) and starts it with the right home path and ports.
- `webui/Dockerfile`, `webui/app.py`: Flask API that queries the server and ngrok, plus an embedded React/MUI dashboard.
- `deploy/src/bootstrap.ts`: CapRover automation that turns `compose.yml` into CapRover apps and deploys them.
- `pkg/`: Upstream `.dpk` assets you can copy into your server home if you want to preload maps/content.
- `daemon`, `daemonded`, `pkg/`, and `game/` are prebundled for ARM64; no download needed at build time.

## Requirements
- Docker and Docker Compose v2 (build on an ARM64 host; binaries are prebundled for ARM64)
- ngrok account + authtoken (for the UDP tunnel)
- Node 18+ only if you plan to use the CapRover bootstrap script

## Quick start (local compose)
1) Create a writable home dir for configs/maps: `unvanquished-home/config`.
2) (Optional) Drop a `unvanquished-home/config/server.cfg` in there. If missing, the server falls back to `+map plat23`.
3) Start the stack with your ngrok token:
```
# PowerShell
$env:NGROK_AUTHTOKEN="xxxx" ; docker compose up --build -d

# Bash
NGROK_AUTHTOKEN=xxxx docker compose up --build -d
```
4) Open the dashboard at `http://localhost:8080` and copy the public UDP address to join your server.

### Ngrok config
- The ngrok sidecar now runs from an agent config file at `ngrok.yml` and starts via `ngrok start --config /etc/ngrok.yml unv`.
- The default config sets a UDP tunnel to `unvanq-server:27960`. Edit `ngrok.yml` if you change the game server port or want extra tunnels/logging.
- Example `ngrok.yml` shipped in the repo:
```
version: "3"
tunnels:
  unv:
    addr: unvanq-server:27960
    proto: udp
```
- The authtoken is still provided via `NGROK_AUTHTOKEN` env; you can also place it under `agent.authtoken` in the config if you prefer.
- Seeing `unknown flag: --proto`? That means an older CLI invocation; use the bundled config (or run `ngrok start` with a v3-style config) instead.

## Configuring the game server
- `UNV_HOME` (default `/var/unvanquished-home`): persisted volume for configs, logs, and extra pk3/dpk content. Mapped from `./unvanquished-home` by compose.
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
- Runs from `webui/app.py`, serving `/api/status` (game server query) and `/api/ngrok_status`.
- Reads `UNV_SERVER_HOST`, `UNV_SERVER_PORT`, and `NGROK_API_URL` from the environment (see `compose.yml` defaults).
- UI shows server info/players and a copy-to-clipboard ngrok URL.

## Optional: CapRover bootstrap
1) `cd deploy`
2) `npm install`
3) Set env: `CAPROVER_URL`, `CAPROVER_PASSWORD`, optional `CAPROVER_EMAIL`, `UNV_PROJECT_NAME`, `COMPOSE_FILE` (defaults to `compose.yml`).
4) `npm run bootstrap` to create/update apps and trigger deployments based on your compose file.

## Troubleshooting
- No ngrok URL? Ensure `NGROK_AUTHTOKEN` is set and the ngrok container can reach `unvanq-server`; check `docker compose logs ngrok`.
- Custom config ignored? Verify `unvanquished-home/config/server.cfg` exists and matches `UNV_SERVER_CFG`; otherwise the entrypoint just runs `+map plat23`.
- Changed version/arch? Rebuild the image with new `UNV_VERSION`/`UNV_ARCH` build args before restarting the stack.
