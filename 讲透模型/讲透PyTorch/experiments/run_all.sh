#!/bin/bash
cd "$(dirname "$0")"
fail=0
for f in 0*.py 1*.py; do
  [ -f "$f" ] || continue
  echo "===== $f ====="
  timeout 150 python3 "$f" > "/tmp/pt_$f.log" 2>&1
  if [ $? -eq 0 ]; then
    tail -2 "/tmp/pt_$f.log"; echo "[OK]"
  else
    tail -10 "/tmp/pt_$f.log"; echo "[FAIL]"; fail=1
  fi
  echo
done
echo "===================="
[ $fail -eq 0 ] && echo "ALL PASS" || echo "SOME FAILED"
