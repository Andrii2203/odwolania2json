#!/bin/sh
set -e
opis="$1"
shift
git add -- "$@"
git commit -q -m "$opis

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push -q 2>/dev/null || echo "push nieudany (sieć) – wyśle go hook stop"
git log --oneline -1
# Maszyna UZP (ADR-0017): ten sam kod co w main; adres i klucz w .env (VM_SSH, VM_KLUCZ), bez nich krok pomijany
vm=$(sed -n 's/^VM_SSH=//p' .env 2>/dev/null | tr -d '\r')
klucz=$(sed -n 's/^VM_KLUCZ=//p' .env 2>/dev/null | tr -d '\r' | sed "s#^~#$HOME#")
if [ -n "$vm" ]; then
  ssh -i "$klucz" -o BatchMode=yes -o ConnectTimeout=10 "$vm" \
    'cd /opt/solution && git pull -q --ff-only && sh instaluj.sh > /dev/null && git log --oneline -1' 2>/dev/null \
    | sed 's/^/VM: /' || echo "VM: aktualizacja nieudana"
fi
