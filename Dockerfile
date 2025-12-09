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
      curl \
      unzip \
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

# Universal zip contains linux-arm64.zip for ARM64.
RUN curl -L -o "unvanquished_${UNV_VERSION}.zip" \
      "https://downloads.sourceforge.net/project/unvanquished/v${UNV_VERSION}/unvanquished_${UNV_VERSION}.zip" \
    && unzip "unvanquished_${UNV_VERSION}.zip" \
    && cd "unvanquished_${UNV_VERSION}" \
    && unzip "${UNV_ARCH}.zip" \
    && mv pkg daemonded .. \
    && cd .. \
    && rm -rf "unvanquished_${UNV_VERSION}" "unvanquished_${UNV_VERSION}.zip"

RUN mkdir -p "${UNV_HOME}/config" "${UNV_HOME}/game" \
    && chown -R unv:unv "${UNV_HOME}"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chown unv:unv /entrypoint.sh

USER unv

VOLUME ["${UNV_HOME}"]

EXPOSE 27960/udp

ENTRYPOINT ["/entrypoint.sh"]
CMD []
