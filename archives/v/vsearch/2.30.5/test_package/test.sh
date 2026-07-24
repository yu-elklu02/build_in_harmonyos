#!/bin/sh
# Exercise independent command-line workflows using self-contained data.
set -e

if ! command -v vsearch >/dev/null 2>&1; then
    echo "ERROR: vsearch not found in PATH" >&2
    exit 1
fi

workdir="vsearch-test-work-$$"
trap 'rm -rf "$workdir"' 0
mkdir "$workdir"
cd "$workdir"

vsearch --version

cat > input.fasta <<'EOF'
>duplicate_a
ACGTACGT
>duplicate_b
ACGTACGT
>short_sequence
ACGT
EOF

cat > reads.fastq <<'EOF'
@read_1
ACGTACGT
+
IIIIIIII
@read_2
ACGT
+
IIII
EOF

# Full-length dereplication merges the two duplicate sequences.
vsearch --derep_fulllength input.fasta --output derep.fasta --sizeout
test "$(grep -c '^>' derep.fasta)" -eq 2
grep -q 'size=2;' derep.fasta

# Sorting puts the longest sequence first.
vsearch --sortbylength input.fasta --output sorted.fasta
sed -n '2p' sorted.fasta | grep -qx 'ACGTACGT'

# Exact search reports each of the three query sequences.
vsearch --search_exact input.fasta --db input.fasta --userout exact.tsv --userfields query+target+id
test "$(grep -c '^' exact.tsv)" -eq 3
grep -q '^duplicate_a' exact.tsv

# FASTQ filtering preserves both valid reads.
vsearch --fastq_filter reads.fastq --fastqout filtered.fastq
test "$(grep -c '^@' filtered.fastq)" -eq 2

echo "vsearch functional test cases passed"
