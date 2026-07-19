#!/bin/sh
# test.sh — vsearch 2.30.5 test_package
# Verify vsearch binary exists, is executable, and prints version info.
set -e
if ! command -v vsearch >/dev/null 2>&1; then
    echo "ERROR: vsearch not found in PATH" >&2
    exit 1
fi
echo "vsearch found at: $(command -v vsearch)"
vsearch --version
echo "vsearch binary verified OK"
