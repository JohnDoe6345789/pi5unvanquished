#!/bin/sh
set -e

ARGS=""

if [ -n "${UNV_HOME}" ]; then
  ARGS="${ARGS} -homepath ${UNV_HOME}"
fi

if [ -n "${UNV_PORT}" ]; then
  ARGS="${ARGS} -set net_port ${UNV_PORT}"
fi

if [ -n "${UNV_PORT6}" ]; then
  ARGS="${ARGS} -set net_port6 ${UNV_PORT6}"
fi

CFG_PATH="${UNV_HOME}/config/${UNV_SERVER_CFG}"

if [ -f "${CFG_PATH}" ]; then
  exec /opt/unvanquished/daemonded ${ARGS} +exec "${UNV_SERVER_CFG}"
else
  echo "No ${CFG_PATH} found, starting with plat23. Create ${CFG_PATH} for custom config."
  exec /opt/unvanquished/daemonded ${ARGS} +map plat23
fi
