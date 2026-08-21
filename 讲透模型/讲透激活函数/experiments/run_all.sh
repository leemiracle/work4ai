#!/bin/bash
# 回归测试: 跑通全部实验, 每个只看结尾摘要
cd "$(dirname "$0")"
fail=0
for f in 0*.py; do
  echo "===== $f ====="
  python3 "$f" > "/tmp/run_$f.log" 2>&1
  if [ $? -eq 0 ]; then
    tail -2 "/tmp/run_$f.log"
    echo "[OK]"
  else
    cat "/tmp/run_$f.log" | tail -15
    echo "[FAIL]"; fail=1
  fi
  echo
done
echo "===================="
[ $fail -eq 0 ] && echo "ALL PASS" || echo "SOME FAILED"
