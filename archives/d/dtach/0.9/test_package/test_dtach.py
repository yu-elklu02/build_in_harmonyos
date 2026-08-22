from pathlib import Path
import subprocess
import sys
import tempfile


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main(binary):
    version = run([binary, "--version"])
    assert version.returncode == 0, version.stderr
    assert "dtach - version 0.9" in version.stdout

    help_out = run([binary, "--help"])
    assert help_out.returncode == 0, help_out.stderr
    assert "Usage: dtach -a <socket> <options>" in help_out.stdout

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        sock = tmp / "dtach.sock"
        marker = tmp / "marker.txt"
        worker = tmp / "worker.py"
        worker.write_text(
            "from pathlib import Path\n"
            "import sys\n"
            "Path(sys.argv[1]).write_text('dtach-ok')\n"
        )
        detached = run([binary, "-N", str(sock), sys.executable, str(worker), str(marker)])
        assert detached.returncode == 0, detached.stderr + detached.stdout
        assert marker.read_text() == "dtach-ok"

    print("dtach smoke test passed")


if __name__ == "__main__":
    main(sys.argv[1])
