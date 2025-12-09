# Dockerfile
FROM debian:bookworm-slim

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

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chown unv:unv /entrypoint.sh

USER unv

VOLUME ["${UNV_HOME}"]

EXPOSE 27960/udp

ENTRYPOINT ["/entrypoint.sh"]
CMD []
