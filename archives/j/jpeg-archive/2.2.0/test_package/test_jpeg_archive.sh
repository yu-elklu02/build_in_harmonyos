#!/bin/sh
set -eu

BIN_DIR="$1"
for command in jpeg-recompress jpeg-compare jpeg-hash; do
    test -x "$BIN_DIR/$command"
    "$BIN_DIR/$command" --help >/dev/null 2>&1
done
test -x "$BIN_DIR/jpeg-archive"
echo "jpeg-archive binaries passed --help smoke tests"
