#!/bin/sh
set -eu

test -x "$1/bin/xcalc"
file "$1/bin/xcalc" | grep -E 'ELF|executable'
printf '%s\n' 'xcalc package executable check passed'
