#!/usr/bin/env bash
# test.sh — gkrellm 2.3.11 test_package
# Verify the packaged daemon can execute and report its version.
set -euo pipefail

gkrellmd --version 2>&1 | grep -Eq '^gkrellmd [0-9]+\.[0-9]+'
gkrellmd --help 2>&1 | grep -qi 'usage'
echo "gkrellmd upstream self-tests passed"
