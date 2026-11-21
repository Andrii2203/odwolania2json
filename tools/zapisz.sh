#!/bin/sh
set -e
opis="$1"
shift
git add -- "$@"
git commit -q -m "$opis

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push -q 2>/dev/null || echo "push nieudany (sieć) – wyśle go hook stop"
git log --oneline -1
