#!/bin/sh
set -eu

BIN_DIR="$1"
WORK_DIR="${TMPDIR:-/data/local/tmp}/jpeg-archive-test-$$"
mkdir -p "$WORK_DIR"
trap 'rm -rf "$WORK_DIR"' EXIT HUP INT TERM

JPEG_RECOMPRESS="$BIN_DIR/jpeg-recompress"
JPEG_COMPARE="$BIN_DIR/jpeg-compare"
JPEG_HASH="$BIN_DIR/jpeg-hash"
JPEG_ARCHIVE="$BIN_DIR/jpeg-archive"

for command in "$JPEG_RECOMPRESS" "$JPEG_COMPARE" "$JPEG_HASH" "$JPEG_ARCHIVE"; do
    test -x "$command"
done

cat > "$WORK_DIR/input.ppm" <<'PPM'
P3
2 2
255
255 0 0   0 255 0
0 0 255   255 255 255
PPM

"$JPEG_RECOMPRESS" --ppm "$WORK_DIR/input.ppm" "$WORK_DIR/output.jpg" >/dev/null 2>&1
test -s "$WORK_DIR/output.jpg"

"$JPEG_COMPARE" "$WORK_DIR/output.jpg" "$WORK_DIR/output.jpg" >/dev/null 2>&1

HASH1=$("$JPEG_HASH" "$WORK_DIR/output.jpg")
HASH2=$("$JPEG_HASH" "$WORK_DIR/output.jpg")
test -n "$HASH1"
test "$HASH1" = "$HASH2"

echo "jpeg-archive functional smoke tests passed"
