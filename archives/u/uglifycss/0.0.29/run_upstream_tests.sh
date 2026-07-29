#!/bin/sh
# Run the complete upstream test set and make legacy runners propagate failure.
set -eu

command -v node >/dev/null 2>&1 || {
    echo "uglifycss requires a Node.js runtime in PATH" >&2
    exit 1
}

node tests-yui.js
if find tests-yui -name '*.FAILED' -type f | grep -q .; then
    echo "UglifyCSS YUI regression failures:" >&2
    find tests-yui -name '*.FAILED' -type f -print >&2
    exit 1
fi

url_output=$(sh tests-url.sh)
printf '%s\n' "$url_output"
if printf '%s\n' "$url_output" | grep -q 'KO'; then
    echo "UglifyCSS URL conversion regression failure" >&2
    exit 1
fi
