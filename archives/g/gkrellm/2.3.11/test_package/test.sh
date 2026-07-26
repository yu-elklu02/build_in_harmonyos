#!/bin/sh
# test.sh — gkrellm 2.3.11 test_package
# Verify the packaged daemon can execute and report its version.
set -eu

gkrellmd --version | grep -Eq '^gkrellmd [0-9]+\.[0-9]+'
gkrellmd --help 2>&1 | grep -q 'Usage'
echo "gkrellmd upstream self-tests passed"
