#!/bin/bash
set -euo pipefail

DEST="${HOME}/.local/bin"
SRC=$(cd "$(dirname "$0")" && pwd)

# Ensure project virtual environment and executable exist
if [ ! -f "$SRC/.venv/bin/sleeper" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv "$SRC/.venv"
    "$SRC/.venv/bin/pip" install -e "$SRC"
fi

mkdir -p "$DEST"
ln -sfv "$SRC/.venv/bin/sleeper" "$DEST/sleeper"

echo "Installed sleeper to $DEST/sleeper"
