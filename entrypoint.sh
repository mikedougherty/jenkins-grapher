#!/bin/sh

/usr/local/bin/python /src/grapher.py "$@" | tee "$OUTPUT_DIR/graph.dot" | dot -Tpng > "$OUTPUT_DIR/graph.png"
[ -n "$OUTPUT_FORMAT" ] && cat "$OUTPUT_DIR/graph.${OUTPUT_FORMAT}"
