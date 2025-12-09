<!-- Notes about the bundled Daemon engine binaries used by the server container. -->

# Daemon engine notes

## What is bundled
- This repo vendors the upstream Daemon engine release (`UNV_VERSION`/`UNV_ARCH` build args in `Dockerfile`) into `/opt/unvanquished/`.
- Binaries: `daemon` (SDL client), `daemon-tty` (headless client), and `daemonded` (dedicated server) plus the NaCl helper files they expect.
- Game content: `pkg/` and `game/` ship alongside the binaries so the image can start without downloading assets.
- Multi-arch libs: The image installs both arm64 and armhf runtime deps; the armhf set exists because the upstream universal zip expects them for NaCl support.

## How the container starts the server
- Entry is `/usr/local/bin/unvanq-entrypoint` (see `Dockerfile`); it builds the `daemonded` arg list from env vars:
  - `UNV_HOME` sets the writable home path (`-homepath`).
  - `UNV_PORT` / `UNV_PORT6` set IPv4/IPv6 UDP ports (`-set net_port`, `-set net_port6`).
  - `UNV_DISABLE_MASTERS=true` strips `sv_master1`…`sv_master5` so the server stays off the master list when tunneling.
  - `UNV_SERVER_CFG` chooses which file under `${UNV_HOME}/config/` is executed via `+exec`.
- On first boot, it copies `/opt/unvanquished/game` into `${UNV_HOME}/game` (volume-backed) and seeds `${UNV_HOME}/config/${UNV_SERVER_CFG}` if missing.
- If the chosen config lacks a `map`, `nextmap`, or `g_initialMapRotation`, the entrypoint appends `+map plat23` so the server has a starting map.

## Manual engine usage (inside the container)
- Open a shell: `docker compose run --rm unvanq-server sh`.
- Dedicated server with explicit args:
  ```
  /opt/unvanquished/daemonded -homepath "$UNV_HOME" -set net_port 27960 -set net_port6 27960 +exec server.cfg
  ```
- Client binaries for debugging (no GPU tooling included):
  - `/opt/unvanquished/daemon-tty` for a text-only client.
  - `/opt/unvanquished/daemon` expects SDL/openGL and is mainly useful on hosts with a display.

## Notes from the upstream wiki
- Official server how-to: https://wiki.unvanquished.net/wiki/Server/Running (last modified 2024-09-21).
- Defaults: listens on UDP 27960 by default (same as Quake III); you must launch a map or the server exits (`+map plat23` is enough).
- Option ordering matters: all `-` flags (e.g., `-homepath`, `-set net_port`, `-pakpath /var/www/pkg`) should come before any `+` commands (`+exec`, `+map`).
- Homepath vs pakpath: `-homepath` sets the writable user dir (this stack points it at `${UNV_HOME}`); `-pakpath` adds extra `.dpk` search roots if you host custom content elsewhere.
- Upstream template configs live in `dist/configs/config/server.cfg` and `dist/configs/game/` in the main repo; we vendor that bundle into `/opt/unvanquished/game` and seed it into your volume on first boot.

## Upstream source (DaemonEngine/Daemon)
- Repo: https://github.com/DaemonEngine/Daemon (see `README.md`).
- Build requirements: git, cmake, a C++14 compiler (`gcc` ≥ 9 / `clang` ≥ 11 / VS2019+); fetch with `git clone --recurse-submodules` or `git submodule update --init --recursive`.
- Dependencies (non-exhaustive): zlib, libgmp, nettle, curl, SDL2, GLEW, libpng, libjpeg ≥ 8, libwebp ≥ 0.2.0, Freetype, OpenAL, ogg/vorbis, opus/opusfile; optional ncurses.
- Typical build: `cmake -H. -Bbuild` then `cmake --build build -- -j$(nproc)`; cross-compile to Windows via `-DCMAKE_TOOLCHAIN_FILE=cmake/cross-toolchain-mingw64.cmake`.
- Running upstream binaries: keep `pkg/` next to `daemon`/`daemonded`; start a map with `./daemonded +map <mapname>` (same map requirement as above).

## Unvanquished game sources (game logic/assets)
- Repo: https://github.com/Unvanquished/Unvanquished (game logic; assets via `download-paks` script or universal zip).
- Build requirements (logic + engine together): git, cmake, python (≥2) with `python-yaml` and `python-jinja`, C++14 compiler (`gcc` ≥ 9 / `clang` ≥ 11 / VS2019+).
- Extra deps vs raw engine: adds Lua alongside the Daemon deps (zlib, gmp, nettle, curl, SDL2, GLEW, libpng, libjpeg ≥ 8, libwebp ≥ 0.2.0, Freetype, OpenAL, ogg/vorbis, opus/opusfile; optional ncurses).
- Submodules: clone with `git clone --recurse-submodules` or `git submodule update --init --recursive` to pull engine/libs; cmake errors about missing `daemon/` usually mean submodules were skipped.
- Asset fetch: `./download-paks build/pkg` (or grab the universal zip); place `pkg/` next to the binaries or in your `homepath`.
- Build pattern: from repo root `mkdir build; cd build; cmake ..; make -j$(nproc)` (MSYS2 uses `cmake .. -G "MSYS Makefiles"`; Windows uses CMake+VS solution; cross-compile to Win64 with `-DCMAKE_TOOLCHAIN_FILE=../daemon/cmake/cross-toolchain-mingw64.cmake`).
- Running: server via `./daemonded +map plat23` with optional `-pakpath` pointing to a `pkg` directory; config samples live in `dist/configs/` (we already vendor them into `/opt/unvanquished/game`).

## Updating the engine
- To bump releases, edit `UNV_VERSION`/`UNV_ARCH` in `compose.yml` (or override at build time) so the Docker build pulls the right upstream universal zip.
- Keep the bundled helper files (`crash_server`, `nacl_loader`, `irt_core-armhf.nexe`, etc.) in sync with the release so in-engine downloads and NaCl stay functional.
