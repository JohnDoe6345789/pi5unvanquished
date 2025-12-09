#!/bin/sh
set -e

set --

if [ -n "${UNV_HOME}" ]; then
  set -- "$@" -homepath "${UNV_HOME}"
fi

if [ -n "${UNV_PORT}" ]; then
  set -- "$@" -set net_port "${UNV_PORT}"
fi

if [ -n "${UNV_PORT6}" ]; then
  set -- "$@" -set net_port6 "${UNV_PORT6}"
fi

CFG_PATH="${UNV_HOME}/config/${UNV_SERVER_CFG}"

if [ -f "${CFG_PATH}" ]; then
  exec /opt/unvanquished/daemonded "$@" +exec "${UNV_SERVER_CFG}"
else
  echo "No ${CFG_PATH} found, starting with plat23. Create ${CFG_PATH} for custom config."
  exec /opt/unvanquished/daemonded "$@" +map plat23
fi
