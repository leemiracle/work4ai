#!/usr/bin/env bash
# batch_dw_fetch.sh — 135 仓 DeepWiki MCP 批量抓取（2026-10-26，讲透AwesomeAgents 集合）
# 钉版规则（Android 轮）：三态判定分开 exit1(INCOMPLETE) 与 isError(NOT_INDEXED)/网络 ERROR；
# 台账 RETRY 行不覆盖终态——本脚本只在终态缺席时写入，重跑=断点续跑。
# 并发 4（MCP 公开端点礼节并发）。
set -u
BASE="/data/usershare/ai/work4ai/讲透AwesomeAgents"
LEDGER="$BASE/_ledger.tsv"
LOGS="$BASE/logs"
TOOL="/data/usershare/ai/pipeline-bin/deepwiki/dw_fetch_mcp.py"
MANIFEST="$BASE/manifest.txt"
mkdir -p "$LOGS"
touch "$LEDGER"

fetch_one() {
  local name="$1" slug="$2"
  local out="$BASE/$name/deepwiki" log="$LOGS/$name.log"
  # 终态跳过（DONE100 / NOT_INDEXED / FINAL_100；INCOMPLETE/ERROR 可重试）
  local st
  st=$(awk -F'\t' -v r="$slug" '$1==r{s=$2} END{print s}' "$LEDGER")
  case "$st" in
    DONE100|NOT_INDEXED|FINAL_100) echo "[SKIP] $slug ($st)"; return 0;;
  esac
  echo "[RUN ] $slug -> $out"
  python3 "$TOOL" --repo "$slug" --out "$out" >"$log" 2>&1
  local rc=$?
  local status det=""
  if [ $rc -eq 0 ]; then
    status=DONE100
  elif grep -qiE 'isError|not (found|indexed)|repository not' "$log"; then
    status=NOT_INDEXED; det="$(grep -oiE 'repository[^,"]*not[^,"]*(found|indexed)[^,"]*' "$log" | head -1)"
  elif grep -q 'INCOMPLETE' "$log"; then
    status=INCOMPLETE; det="$(grep -oE '覆盖: [0-9]+/[0-9]+' "$log" | tail -1)"
  else
    status=ERROR; det="rc=$rc $(tail -c 200 "$log" | tr '\n' ' ' | cut -c1-120)"
  fi
  printf '%s\t%s\t%s\n' "$slug" "$status" "$det" >> "$LEDGER"
  echo "[ $status ] $slug $det"
}
export -f fetch_one
export BASE LEDGER LOGS TOOL

# 台账去重保最新（Android 轮钉版：tac|awk seen|tac）
dedup() { tac "$LEDGER" | awk -F'\t' '!seen[$1]++' | tac > "$LEDGER.tmp" && mv "$LEDGER.tmp" "$LEDGER"; }

# 逐仓顺序派发、内部 4 进程并发池
run_batch() {
  local jobs=()
  while IFS='|' read -r name slug; do
    [ -z "${slug:-}" ] && continue
    jobs+=("$name" "$slug")
    if [ ${#jobs[@]} -ge 8 ]; then
      printf '%s\n%s\n' "${jobs[@]}" | xargs -P 4 -n 2 bash -c 'fetch_one "$0" "$1"'
      jobs=()
    fi
  done < "$MANIFEST"
  if [ ${#jobs[@]} -gt 0 ]; then
    printf '%s\n%s\n' "${jobs[@]}" | xargs -P 4 -n 2 bash -c 'fetch_one "$0" "$1"'
  fi
}

run_batch
dedup
echo "=== 台账汇总 ==="
awk -F'\t' '{c[$2]++} END{for(k in c) print k, c[k]}' "$LEDGER"
echo "=== DONE $(date '+%F %T') ==="
