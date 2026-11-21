#!/bin/sh
set -e
opis="$1"
shift
git add -- "$@"
git commit -q -m "$opis

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push -q
git log --oneline -1
