#!/bin/sh
set -eu

cat > reference.srt <<'EOF'
1
00:00:10,000 --> 00:00:12,000
Reference subtitle
EOF

cat > incorrect.srt <<'EOF'
1
00:00:05,000 --> 00:00:07,000
Incorrect subtitle
EOF

alass-cli reference.srt incorrect.srt output.srt --no-split
test -s output.srt
grep -Fq '00:00:10,000 --> 00:00:12,000' output.srt
