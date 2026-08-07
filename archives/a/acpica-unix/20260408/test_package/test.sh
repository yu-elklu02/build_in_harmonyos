#!/bin/sh
set -eu

cat > input.asl <<'EOF'
DefinitionBlock ("", "DSDT", 2, "OHPCD", "IASLTEST", 1)
{
    Name (TEST, 0x2A)
}
EOF

iasl input.asl
test -s input.aml
iasl -d input.aml
test -s input.dsl
grep -q 'Name (TEST, 0x2A)' input.dsl
