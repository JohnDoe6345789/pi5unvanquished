# Dockerfile
ARG TARGETPLATFORM=linux/arm64
FROM --platform=${TARGETPLATFORM} debian:bookworm-slim

# Version from upstream universal zip; adjust when they bump.
ARG UNV_VERSION=0.55.5
ARG UNV_ARCH=linux-arm64

ENV DEBIAN_FRONTEND=noninteractive \
    UNV_VERSION=${UNV_VERSION} \
    UNV_ARCH=${UNV_ARCH} \
    UNV_HOME=/var/unvanquished-home \
    UNV_PORT=27960 \
    UNV_PORT6=27960 \
    UNV_SERVER_CFG=server.cfg

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates \
      libstdc++6 \
      libgcc-s1 \
      zlib1g \
      libcurl4 \
      libopenal1 \
      libogg0 \
      libvorbis0a \
      libvorbisfile3 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -d /home/unv -s /bin/bash unv \
    && mkdir -p /opt/unvanquished "${UNV_HOME}" \
    && chown -R unv:unv /opt/unvanquished "${UNV_HOME}"

WORKDIR /opt/unvanquished

COPY daemon daemon-tty daemonded crash_server irt_core-armhf.nexe nacl_helper_bootstrap nacl_helper_bootstrap-armhf nacl_loader /opt/unvanquished/
COPY pkg /opt/unvanquished/pkg
COPY game /opt/unvanquished/game
RUN chown -R unv:unv /opt/unvanquished

RUN mkdir -p "${UNV_HOME}/config" "${UNV_HOME}/game" \
    && chown -R unv:unv "${UNV_HOME}"

RUN cat <<'EOF' > /usr/local/bin/unvanq-entrypoint
#!/bin/sh
set -e

set --

mkdir -p "${UNV_HOME}/config"

# Expose packaged game configs in the writable home for convenience
if [ ! -e "${UNV_HOME}/game" ]; then
  ln -s /opt/unvanquished/game "${UNV_HOME}/game"
fi

if [ -n "${UNV_HOME}" ]; then
  set -- "$@" -homepath "${UNV_HOME}"
fi

if [ -n "${UNV_PORT}" ]; then
  set -- "$@" -set net_port "${UNV_PORT}"
fi

if [ -n "${UNV_PORT6}" ]; then
  set -- "$@" -set net_port6 "${UNV_PORT6}"
fi

if [ "${UNV_DISABLE_MASTERS}" = "1" ] || [ "${UNV_DISABLE_MASTERS}" = "true" ]; then
  for i in 1 2 3 4 5; do
    set -- "$@" -set "sv_master${i}" ""
  done
fi

CFG_PATH="${UNV_HOME}/config/${UNV_SERVER_CFG}"
DEFAULT_CFG="/opt/unvanquished/game/${UNV_SERVER_CFG}"

if [ ! -f "${CFG_PATH}" ] && [ -f "${DEFAULT_CFG}" ]; then
  echo "Seeding default config to ${CFG_PATH}"
  cp "${DEFAULT_CFG}" "${CFG_PATH}"
fi

if [ -f "${CFG_PATH}" ]; then
  exec /opt/unvanquished/daemonded "$@" +exec "${UNV_SERVER_CFG}"
else
  echo "No ${CFG_PATH} found, starting with plat23. Create ${CFG_PATH} for custom config."
  exec /opt/unvanquished/daemonded "$@" +map plat23
fi
EOF

RUN chmod +x /usr/local/bin/unvanq-entrypoint && chown unv:unv /usr/local/bin/unvanq-entrypoint

USER unv

VOLUME ["${UNV_HOME}"]

EXPOSE 27960/udp

ENTRYPOINT ["/usr/local/bin/unvanq-entrypoint"]
CMD []
