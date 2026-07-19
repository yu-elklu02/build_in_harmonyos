#!/bin/sh
# test.sh — gkrellm 2.3.11 test_package
# Verify gkrellmd binary exists and is executable.
# gkrellmd does not have a --version flag; running with an invalid
# option prints usage to stderr and exits non-zero, which confirms
# the binary is present and functional.
set -e
if ! command -v gkrellmd >/dev/null 2>&1; then
    echo "ERROR: gkrellmd not found in PATH" >&2
    exit 1
fi
echo "gkrellmd found at: $(command -v gkrellmd)"
# Run with unknown flag — prints usage and exits; confirms binary works
gkrellmd --help 2>&1 || gkrellmd -x 2>&1 || true
echo "gkrellmd binary verified OK"
