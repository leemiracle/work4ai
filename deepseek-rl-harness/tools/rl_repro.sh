#!/bin/bash
# rl_repro.sh — L4：复现检查。用法: rl_repro.sh "<cmd 含 --seed N>"
# 同一命令跑两遍，strip 时间戳/进度条后 diff 必须为空。基线不可复现 = 一切对比无效。
set -o pipefail
CMD="$1"
[ -z "$CMD" ] && { echo "用法: rl_repro.sh '<实验命令，须自带 --seed>'"; exit 2; }
TMP=$(mktemp -d)
eval "$CMD" 2>&1 | sed -E 's/[0-9]{4}-[0-9]{2}-[0-9]{2}[ T][0-9:.]+//g; s/\r//g; s/[0-9]+%\|[^|]*\|//g' > "$TMP/run1.log"
eval "$CMD" 2>&1 | sed -E 's/[0-9]{4}-[0-9]{2}-[0-9]{2}[ T][0-9:.]+//g; s/\r//g; s/[0-9]+%\|[^|]*\|//g' > "$TMP/run2.log"
if diff -q "$TMP/run1.log" "$TMP/run2.log" >/dev/null; then
  echo "[L4] REPRO OK: 两跑输出一致（$(wc -l < "$TMP/run1.log") 行）"
  exit 0
else
  echo "[L4] REPRO FAIL: 两跑输出有差异——检查：未固定 seed / 并行非确定 / GPU 非确定算法（torch 未设 deterministic）/ 全局状态泄漏"
  diff "$TMP/run1.log" "$TMP/run2.log" | head -20
  exit 1
fi
