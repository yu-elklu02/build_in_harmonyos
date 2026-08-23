import subprocess
import sys


result = subprocess.run([sys.argv[1], "--help"], check=False, capture_output=True, text=True)
output = result.stdout + result.stderr
if result.returncode != 0 or "Avida" not in output:
    raise SystemExit("avida --help did not produce the expected help text")
print("avida help assertion passed")
