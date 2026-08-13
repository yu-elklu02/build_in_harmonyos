#!/usr/bin/env bash
set -euo pipefail

BISON="$1"
WORK="${TMPDIR:-/tmp}/bison-test.$$"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK"

test -x "$BISON"
VERSION="$($BISON --version | head -n 1)"
printf '%s\n' "$VERSION" | grep -F "bison (GNU Bison) 2.7"

cat > "$WORK/calc.y" <<'EOF'
%{
#include <stdio.h>
int yylex(void);
void yyerror(const char *message) { (void)message; }
%}
%token NUMBER
%%
input: NUMBER { if ($1 == 42) puts("parser assertion passed"); };
%%
int yylex(void) { static int state; if (state++) return 0; yylval = 42; return NUMBER; }
int main(void) { return yyparse(); }
EOF

"$BISON" -o "$WORK/calc.c" "$WORK/calc.y"
clang -I"$WORK" "$WORK/calc.c" -o "$WORK/calc"
"$WORK/calc" | grep -F "parser assertion passed"
printf '%s\n' "=== bison tests PASSED ==="
