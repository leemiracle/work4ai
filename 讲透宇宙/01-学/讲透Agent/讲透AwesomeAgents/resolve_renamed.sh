#!/usr/bin/env bash
# resolve_renamed.sh — NOT_INDEXED 仓改名解析 + MCP 复抓（讲透AwesomeAgents 轮）
# 逻辑：github.com 重定向解析现 slug → DeepWiki MCP 探测 → 有 wiki 则更新 manifest+重抓；
#       无 wiki（原 slug 或新 slug 都没有）→ 保持 NOT_INDEXED（真未索引，终态）。
set -u
BASE="~/ai/work4ai/讲透AwesomeAgents"
LEDGER="$BASE/_ledger.tsv"
PROXY="http://127.0.0.1:7890"
TOOL="~/ai/pipeline-bin/deepwiki/dw_fetch_mcp.py"

probe_mcp() {  # $1=slug → 输出 OK 或 ERR
  local r
  r=$(timeout 40 curl -s --noproxy '*' --max-time 35 -X POST https://mcp.deepwiki.com/mcp \
      -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
      -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"read_wiki_structure\",\"arguments\":{\"repoName\":\"$1\"}}}")
  if printf '%s' "$r" | grep -q '"isError":true'; then echo ERR; else echo OK; fi
}

mapfile -t rows < <(grep -P '\tNOT_INDEXED\t' "$LEDGER")
: > "$BASE/_rename_map.tsv"
for row in "${rows[@]}"; do
  slug=$(printf '%s' "$row" | cut -f1)
  cur=$(curl -sIL --max-time 20 -x "$PROXY" -o /dev/null -w '%{url_effective}' "https://github.com/$slug" 2>/dev/null | sed -E 's#https://github.com/##; s#/$##')
  [ -z "$cur" ] && cur="$slug"
  if [ "$cur" != "$slug" ]; then
    st=$(probe_mcp "$cur"); sleep 1
    if [ "$st" = OK ]; then
      echo "$slug -> $cur [INDEXED, 复抓]"
      printf '%s\t%s\tINDEXED\n' "$slug" "$cur" >> "$BASE/_rename_map.tsv"
    else
      echo "$slug -> $cur [改名后仍未索引]"
      printf '%s\t%s\tSTILL_NOT\n' "$slug" "$cur" >> "$BASE/_rename_map.tsv"
    fi
  else
    echo "$slug [未改名，真未索引]"
    printf '%s\t%s\tSAME_NOT\n' "$slug" "$cur" >> "$BASE/_rename_map.tsv"
  fi
done

# 复抓改名且有 wiki 的仓：manifest 换 slug、台账删旧行、重跑抓取
while IFS=$'\t' read -r old new st; do
  [ "$st" = INDEXED ] || continue
  name=$(awk -F'|' -v s="$old" '$2==s{print $1}' "$BASE/manifest.txt")
  awk -F'|' -v n="$name" -v o="$old" -v nn="$new" 'BEGIN{FS=OFS="|"} $1==n && $2==o {$2=nn} {print}' \
    "$BASE/manifest.txt" > "$BASE/manifest.txt.tmp" && mv "$BASE/manifest.txt.tmp" "$BASE/manifest.txt"
  esc_old=${old//\//\\/}
  grep -v -P "^${esc_old}\t" "$LEDGER" > "$LEDGER.tmp" && mv "$LEDGER.tmp" "$LEDGER"
  python3 "$TOOL" --repo "$new" --out "$BASE/$name/deepwiki" > "$BASE/logs/$name.retry.log" 2>&1
  rc=$?
  if [ $rc -eq 0 ]; then ns=DONE100; det="";
  elif grep -q INCOMPLETE "$BASE/logs/$name.retry.log"; then ns=INCOMPLETE; det="$(grep -oE '覆盖: [0-9]+/[0-9]+' "$BASE/logs/$name.retry.log" | tail -1)";
  else ns=ERROR; det="rc=$rc"; fi
  printf '%s\t%s\t%s\n' "$new" "$ns" "$det（原 $old 改名复抓）" >> "$LEDGER"
  echo "[ $ns ] $new ($name)"
done < "$BASE/_rename_map.tsv"
echo "=== resolve done ==="
awk -F'\t' '{c[$2]++} END{for(k in c) print k, c[k]}' "$LEDGER"
