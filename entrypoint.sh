#!/bin/sh

DOT=dot
dot -V >/dev/null 2>&1 || DOT=true

filesize() {
    if ! stat >/dev/null 2>&1; then
        # Looks like linux
        stat -c '%s' "$1"
    else
        # Probably a mac
        stat -f '%z' "$1"
    fi
}

/usr/bin/env python "$(dirname "${BASH_SOURCE}")/grapher.py" "$@" | tee "$OUTPUT_DIR/graph.dot" | "$DOT" -Tpng > "$OUTPUT_DIR/graph.png"
[ "$( filesize "$OUTPUT_DIR/graph.png" )" -eq 0 ] && rm -f "$OUTPUT_DIR/graph.png"
[ -n "$OUTPUT_FORMAT" ] && cat "$OUTPUT_DIR/graph.${OUTPUT_FORMAT}"
