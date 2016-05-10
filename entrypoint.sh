#!/bin/sh

/usr/bin/env python "$(dirname "${BASH_SOURCE}")/grapher.py" "$@" > "$OUTPUT_DIR/graph.dot"
if which dot >/dev/null 2>&1 ; then
    dot -Tpng "$OUTPUT_DIR/graph.dot" > "$OUTPUT_DIR/graph.png"
fi
[ -n "$OUTPUT_FORMAT" ] && [ -e "$OUTPUT_DIR/graph.${OUTPUT_FORMAT}" ] && cat "$OUTPUT_DIR/graph.${OUTPUT_FORMAT}"
