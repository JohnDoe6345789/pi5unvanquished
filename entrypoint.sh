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

if [ "${UNV_DISABLE_MASTERS}" = "1" ] || [ "${UNV_DISABLE_MASTERS}" = "true" ]; then
  for i in 1 2 3 4 5; do
    set -- "$@" -set "sv_master${i}" ""
  done
fi

CFG_PATH="${UNV_HOME}/config/${UNV_SERVER_CFG}"

if [ -f "${CFG_PATH}" ]; then
  exec /opt/unvanquished/daemonded "$@" +exec "${UNV_SERVER_CFG}"
else
  echo "No ${CFG_PATH} found, starting with plat23. Create ${CFG_PATH} for custom config."
  exec /opt/unvanquished/daemonded "$@" +map plat23
fi
