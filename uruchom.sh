#!/bin/sh
# PDF z input/ -> JSON w output/ (ADR-0017).
cd "$(dirname "$0")"
[ -x .venv/bin/python ] || sh instaluj.sh
exec .venv/bin/python -m odwolania2json --input input --output output "$@"
