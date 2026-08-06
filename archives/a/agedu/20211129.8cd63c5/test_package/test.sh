#!/bin/sh
set -eu

mkdir input
printf 'fixture data\n' > input/file.txt

agedu -s input
test -s agedu.dat

agedu -t input > report.txt
test -s report.txt
grep -Fq 'input' report.txt
