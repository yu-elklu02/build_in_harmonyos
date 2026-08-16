#!/usr/bin/env sh
set -eu
if (set -o pipefail) 2>/dev/null; then
	set -o pipefail
fi

package_folder="$1"
remind="$package_folder/bin/remind"
rem2ps="$package_folder/bin/rem2ps"

if [ ! -x "$remind" ]; then
	echo "remind is not executable: $remind" >&2
	exit 1
fi

if [ ! -x "$rem2ps" ]; then
	echo "rem2ps is not executable: $rem2ps" >&2
	exit 1
fi

tmpdir="$(mktemp -d "${TMPDIR:-/tmp}/remind-test.XXXXXX")"
trap 'rm -rf "$tmpdir"' EXIT HUP INT TERM

"$remind" -v 2>&1 | grep -F "REMIND 06.02.08" >/dev/null

cat >"$tmpdir/basic.rem" <<'EOF'
REM 16 Feb 1991 MSG parser assertion passed
EOF

"$remind" -q "$tmpdir/basic.rem" 16 Feb 1991 >"$tmpdir/basic.out"
grep -F "parser assertion passed" "$tmpdir/basic.out" >/dev/null

"$remind" -p "$tmpdir/basic.rem" 16 Feb 1991 | "$rem2ps" >"$tmpdir/basic.ps"
grep -F "%!PS-Adobe" "$tmpdir/basic.ps" >/dev/null

echo "=== remind tests PASSED ==="
