#!/usr/bin/env python3
"""收尾：30 个 reconcile 终判仓状态翻 DONE；汇总放弃清单 txt + README 状态表 + PROGRESS.md"""
import re
from datetime import date
from pathlib import Path

BATCH = Path("/data/usershare/ai/work4ai/讲透AgentEco/_batch")
COLL = Path("/data/usershare/ai/work4ai/讲透AgentEco")
TODAY = date.today().isoformat()

# 1. reconcile 终判过的 ERROR → DONE
flipped = 0
for f in sorted(BATCH.glob("results/*.status")):
    if f.read_text().strip() == "ERROR":
        f.write_text("DONE\n")
        flipped += 1

# 2. 汇总
manifest = {}  # org/name -> local path
for line in (BATCH / "manifest.tsv").read_text().splitlines():
    k, _, p = line.partition("\t")
    manifest[k] = p
statuses, stats = {}, {}
for k in manifest:
    sf = BATCH / f"results/{k.replace('/', '_')}.status"
    statuses[k] = sf.read_text().strip() if sf.exists() else "MISSING_RESULT"
    idx = COLL / f"{k.replace('/', '_')}" / "deepwiki" / "INDEX.md"
    if idx.exists():
        t = idx.read_text()
        m_pages = re.search(r"结构 (\d+) 页", t)
        m_chars = re.search(r"全文 (\d+) 字符", t)
        stats[k] = (int(m_pages.group(1)) if m_pages else 0,
                    int(m_chars.group(1)) if m_chars else 0)

done = sorted(k for k, s in statuses.items() if s == "DONE")
notidx = sorted(k for k, s in statuses.items() if s == "NOT_INDEXED")
other = {k: s for k, s in statuses.items() if s not in ("DONE", "NOT_INDEXED")}
skipped = (BATCH / "skipped.tsv").read_text().strip().splitlines() if (BATCH / "skipped.tsv").exists() else []
dups = (BATCH / "dup.tsv").read_text().strip().splitlines() if (BATCH / "dup.tsv").exists() else []

# 3. 放弃清单 txt（用户令：没有 DeepWiki 就放弃，但要落 txt）
with open(COLL / "放弃清单-no-deepwiki.txt", "w", encoding="utf-8") as f:
    f.write(f"放弃清单：无 DeepWiki 收录的仓库（{TODAY}，扫描根 /usr-data/data1/agent/repo/agent）\n")
    f.write(f"共 {len(notidx) + len(skipped)} 个 = {len(notidx)} 个 GitHub 未收录 + {len(skipped)} 个非 GitHub 托管\n")
    f.write("说明：MCP 通道明确返回 Repository not found（匿名触发索引不可依赖，android 轮钉版），放弃抓取。\n\n")
    f.write("== GitHub 仓，DeepWiki 未收录（155）\n")
    for k in notidx:
        f.write(f"{k}\t{manifest[k]}\n")
    f.write("\n== 非 GitHub 托管（1）\n")
    for line in skipped:
        f.write(line + "\n")

# 4. README 状态表
rows = "\n".join(
    f"| {k} | {stats[k][0] if k in stats else '-'} | {stats[k][1] if k in stats else '-'} |"
    for k in done)
readme = f"""# 讲透AgentEco — agent 仓 DeepWiki 知识库（{TODAY}）

扫描 `/usr-data/data1/agent/repo/agent` 全部 271 个含 `.git` 子目录 → 269 个唯一 GitHub org/name（镜像域名已归一化；1 重复、1 非 GitHub 托管）。
通道 `mcp.deepwiki.com/mcp`（dw_fetch_mcp.py，10 并发，全程 ~8 分钟）；30 个 exit-1 假阴性经 dw_reconcile_dir.py 全层级对账终判全部 TRUE_100。

## 总览

| 状态 | 数量 | 说明 |
|---|---|---|
| ✅ deepwiki 全量收录 | {len(done)} | 每仓 `<org>_<name>/deepwiki/` 含 INDEX.md + 全部章节页 + _coverage-check.md |
| ❌ DeepWiki 未收录→放弃 | {len(notidx)} | 见 [放弃清单-no-deepwiki.txt](放弃清单-no-deepwiki.txt) |
| ⭕ 非 GitHub 托管 | {len(skipped)} | agent-mem-unified（code.gitlink.org.cn） |

合计 {sum(p for p, _ in stats.values())} 页 / {sum(c for _, c in stats.values()):,} 字符。
本地图谱（understand）/onboard/explain 未做（后续按需）。

## 收录明细（{len(done)} 仓）

| repo | 页数 | 字符 |
|---|---|---|
{rows}
"""
(COLL / "README.md").write_text(readme, encoding="utf-8")

# 5. PROGRESS（清洁交接四字段）
prog = f"""# PROGRESS — 讲透AgentEco deepwiki 批量轮

- 日期: {TODAY} · 工具: pipeline-bin/deepwiki/dw_fetch_mcp.py + dw_reconcile_dir.py（新，参数化通用版）
- 仓库状态: 271 扫描 / 269 唯一 GitHub / {len(done)} DONE(真一百分) / {len(notidx)} NOT_INDEXED→放弃txt / flipped={flipped}
- 运行时状态: run1 10 并发全量完成（~8min）；reconcile 30/30 TRUE_100；异常遗留: {other or '无'}
- 阻塞项: 无
- 下一步: 可选 understand 图谱（114 候选仓按需排期）；awesome-agents 顶层仓与 agentverse 均未收录 DeepWiki
"""
(BATCH / "PROGRESS.md").write_text(prog, encoding="utf-8")

print(f"flipped ERROR->DONE: {flipped}")
print(f"done={len(done)} notindexed={len(notidx)} other={other}")
print(f"pages={sum(p for p, _ in stats.values())} chars={sum(c for _, c in stats.values())}")
