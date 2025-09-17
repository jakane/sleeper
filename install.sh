#!/bin/bash
set -euo pipefail

DEST=~/.local/bin
SRC=$(cd "$(dirname $0)" && pwd)

mkdir -p $DEST

ln -sv $SRC/sleeper $DEST
