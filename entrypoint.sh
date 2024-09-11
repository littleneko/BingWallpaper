#! /bin/sh

set -eu

PUID=${PUID:-1000}
PGID=${PGID:-1000}

if ! getent group "$PGID" >/dev/null; then
  groupadd -g "$PGID" bing
fi

if ! getent passwd "$PUID" >/dev/null; then
  useradd -u "$PUID" -g "$PGID" -m bing
fi

exec gosu "$PUID":"$PGID" "$@"
