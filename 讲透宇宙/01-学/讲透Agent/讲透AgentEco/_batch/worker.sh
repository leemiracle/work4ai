#!/usr/bin/env bash
# 单仓 worker：抓 DeepWiki → 分类 → 原子写结果文件（无共享写，天然无竞态）
# 用法: worker.sh "org/name" "/本地/仓路径"
# 结果文件 results/<safe>.status: DONE / INCOMPLETE / NOT_INDEXED / ERROR
set -u
REPO="$1"; LOCAL="$2"
BATCH="/data/usershare/ai/work4ai/讲透AgentEco/_batch"
COLL="/data/usershare/ai/work4ai/讲透AgentEco"
TOOL="/data/usershare/ai/pipeline-bin/deepwiki/dw_fetch_mcp.py"
SAFE="${REPO/\//_}"
OUT="$COLL/$SAFE/deepwiki"
LOG="$BATCH/logs/$SAFE.log"
RES="$BATCH/results/$SAFE.status"
mkdir -p "$BATCH/logs" "$BATCH/results"

# 断点：已有 DONE 结果且 INDEX.md 落盘 → 跳过
if [[ -f "$RES" && "$(cat "$RES" 2>/dev/null)" == "DONE" && -f "$OUT/INDEX.md" ]]; then
  echo "SKIP(done) $REPO"; exit 0
fi

timeout 900 python3 "$TOOL" --repo "$REPO" --out "$OUT" >"$LOG" 2>&1
rc=$?

if [[ $rc -eq 0 ]]; then
  cov="$OUT/_coverage-check.md"
  if [[ ! -f "$cov" ]]; then miss=99; else
    miss=$(grep -c '^- MISSING' "$cov" 2>/dev/null); miss=${miss:-0}
  fi
  if [[ "$miss" -eq 0 ]]; then
    echo DONE > "$RES"
  else
    echo INCOMPLETE > "$RES"   # 已知假阴性形态：extra 页/三级页/前缀——收尾统一 reconcile 终判
  fi
elif grep -qiE "not indexed|not found|does not exist|couldn't find|unable to find" "$LOG"; then
  echo NOT_INDEXED > "$RES"    # DeepWiki 未收录 → 放弃，收尾汇总 txt
else
  echo ERROR > "$RES"          # 网络/限流 → 收尾重试队列
fi
cat "$RES"
