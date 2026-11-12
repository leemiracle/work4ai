#!/usr/bin/env python3
"""生成 讲透AwesomeAgents 全量 README（2026-10-26 收尾）。
- 每仓 README.md：抓自 INDEX.md 头两行元数据（结构 N 页 · 全文 M 字符）+ 台账终态 + 改名注记
- NOT_INDEXED 15 仓：占位 README（understand 图谱线指路，同 TIRx-kernels 先例）
- 集合 README.md：统计 + 135 行明细表 + 改名映射
"""
import re
from pathlib import Path

BASE = Path("~/ai/work4ai/讲透AwesomeAgents")
from datetime import date
D = date.today().isoformat()

manifest = {}   # name -> slug(现)
for line in open(BASE / "manifest.txt", encoding="utf-8"):
    name, _, slug = line.strip().partition("|")
    if name:
        manifest[name] = slug
old_slug = {}   # name -> 旧 slug（改名仓）
for line in open(BASE / "_rename_map.tsv", encoding="utf-8"):
    o, n, st = line.rstrip("\n").split("\t")
    for name, s in manifest.items():
        if s == n and n != o:
            old_slug[name] = o
            break
ledger = {}     # slug(现) -> (status, det)
for line in open(BASE / "_ledger.tsv", encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    if len(p) >= 2 and "/" in p[0]:
        ledger[p[0]] = (p[1], p[2] if len(p) > 2 else "")

rows = []
for name, slug in manifest.items():
    st, det = ledger.get(slug, ("?", ""))
    d = BASE / name / "deepwiki"
    if st in ("DONE100", "FINAL_100"):
        idx = (d / "INDEX.md").read_text(encoding="utf-8")
        m = re.search(r"结构 (\d+) 页 · 全文 (\d+) 字符", idx)
        pages, chars = (m.group(1), m.group(2)) if m else ("?", "?")
        rename = f"（原 {old_slug[name]}，改名）" if name in old_slug else ""
        ver = "结构全命中 exit 0" if st == "DONE100" else "reconcile 终判真一百分（extra/三级页假阴性已甄别）"
        body = (
            f"# 讲透{name} — DeepWiki 抓取\n\n"
            f"- 源仓库：`{slug}`{rename}\n"
            f"- 通道：mcp.deepwiki.com MCP（dw_fetch_mcp.py）· 抓取 {D}\n"
            f"- 状态：✅ deepwiki 100%（{pages} 页 · {chars} 字符 · {ver}）\n"
            f"- 入口：[deepwiki/INDEX.md](deepwiki/INDEX.md) · 对账：[deepwiki/_coverage-check.md](deepwiki/_coverage-check.md)\n"
            f"- 下一步：⏳ understand 图谱 → onboarding → explain（源码在 /usr-data/data1/agent/repo/agent/awesome-agents/repos/）\n")
        (BASE / name / "README.md").write_text(body, encoding="utf-8")
        rows.append((name, slug, st, f"{pages}页/{chars}字符"))
    else:  # NOT_INDEXED
        rename = f"（已改名至 `{slug}`，DeepWiki 仍未索引）" if name in old_slug else ""
        body = (
            f"# 讲透{name} — DeepWiki 未收录（占位）\n\n"
            f"- 源仓库：`{slug}`{rename}\n"
            f"- 探测：{D} MCP 通道 `read_wiki_structure` 返回 Repository not found（匿名触发索引不可依赖，Android 轮钉版）\n"
            f"- 替代路线：本地源码在手 → understand 图谱是唯一知识源（同 TIRx-kernels / localai 先例）\n"
            f"- 本目录无 deepwiki/ 产物属预期，勿当缺件。\n")
        (BASE / name / "README.md").write_text(body, encoding="utf-8")
        rows.append((name, slug, "NOT_INDEXED", "—"))

c = {"DONE100": 0, "FINAL_100": 0, "NOT_INDEXED": 0}
for _, _, st, _x in rows:
    c[st] = c.get(st, 0) + 1
lines = [
    "# 讲透AwesomeAgents — awesome-agents 138 git 仓 DeepWiki 批量轮",
    "",
    f"> 源：/usr-data/data1/agent/repo/agent/awesome-agents/repos（138 git 仓）· 批量日 {D}",
    "> 通道：mcp.deepwiki.com MCP（dw_fetch_mcp.py）· 4 并发 ~3min 跑完 + 改名解析复抓轮",
    "",
    "## 总况",
    "",
    f"- ✅ 100% 抓取成功 **{c['DONE100'] + c['FINAL_100']} / 135**"
    f"（exit0 直判 {c['DONE100']} + reconcile 终判 {c['FINAL_100']}）",
    f"- ❌ DeepWiki 未收录 **{c['NOT_INDEXED']}**（understand 图谱线替代，源码在手）",
    "- 另有 2 仓既有产物跳过：讲透ColossalAI、讲透DeepSeek-Harness（work4ai 顶层既有）",
    "",
    "## 明细（name · 现 slug · 终态 · 规模）",
    "",
    "| 讲透目录 | 现 slug | 终态 | 规模 |",
    "|---|---|---|---|",
]
for name, slug, st, size in sorted(rows, key=lambda r: r[0].lower()):
    mark = {"DONE100": "✅", "FINAL_100": "✅R", "NOT_INDEXED": "❌"}[st]
    lines.append(f"| {name} | {slug} | {mark} {st} | {size} |")
if old_slug:
    lines += ["", "## 改名仓映射（本地 remote 旧 slug → 现 slug）", ""]
    for name, o in sorted(old_slug.items()):
        lines.append(f"- {o} → {manifest[name]}（讲透{name}）")
lines += ["", "## 假阴性甄别口径（钉版）",
          "",
          "- `INCOMPLETE 覆盖 N/M N>M` = extra 页/三级页假阴性（dw_fetch_mcp 结构解析只到二级），",
          "  全层级 reconcile 对账 MISSING=0 即真一百分（本批 23 仓全此形态，零真缺口）。",
          "- NOT_INDEXED 主因=本地 remote 指向改名前旧 org（github 重定向解析现 slug 后复抓挽回 14/29）。",
          "", "## 台账与工具", "",
          "- 台账：[_ledger.tsv](_ledger.tsv) · 改名映射：[_rename_map.tsv](_rename_map.tsv)",
          "- 脚本：batch_dw_fetch.sh（批量）· batch_reconcile.py（终判）· resolve_renamed.sh（改名复抓）",
          "- 进度：[PROGRESS.md](PROGRESS.md)", ""]
(BASE / "README.md").write_text("\n".join(lines), encoding="utf-8")
print(f"README 生成：{len(rows)} 仓（{c}）")
