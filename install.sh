#!/bin/bash
set -euo pipefail

DEST="${HOME}/.local/bin"
SRC=$(cd "$(dirname "$0")" && pwd)

mkdir -p "$DEST"

ln -sfv "$SRC/sleeper" "$DEST/sleeper"

echo "Installed sleeper to $DEST/sleeper"
