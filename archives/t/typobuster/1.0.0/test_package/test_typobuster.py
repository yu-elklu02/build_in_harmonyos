import importlib.util
import os
import subprocess
import sys


def load_tools(package_folder):
    path = os.path.join(package_folder, "lib", "typobuster", "tools.py")
    spec = importlib.util.spec_from_file_location("typobuster_tools", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    package_folder = sys.argv[1]
    check_launcher = "--check-launcher" in sys.argv[2:]
    if check_launcher:
        launcher = os.path.join(package_folder, "bin", "typobuster")
        version = subprocess.run(
            [launcher, "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if version.returncode != 0 or "version 1.0.0" not in version.stdout:
            raise RuntimeError(f"packaged launcher version check failed: {version.stdout}{version.stderr}")

    tools = load_tools(package_folder)
    checks = {
        "snake case": tools.to_snake_case("Hello Harmony OS") == "hello_harmony_os",
        "camel case": tools.to_camel_case("hello harmony os") == "helloHarmonyOs",
        "punctuation cleanup": tools.sanitize_punctuation_marks("Hello , world !", 0, 15) == "Hello, world!",
        "ordered list": tools.ordered_list("alpha\n\nbeta") == "1. alpha\n2. beta",
        "sort lines": tools.sort_lines("zebra\nApple\nmoon") == "Apple\nmoon\nzebra",
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"typobuster transformation checks failed: {', '.join(failed)}")
    total = len(checks) + int(check_launcher)
    print(f"typobuster launcher and functional checks passed: {total}")


if __name__ == "__main__":
    main()
