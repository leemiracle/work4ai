"""报告生成器：把 stats JSON 转成可读的 Markdown 深度报告。

每 topic: reports/topics/{tid}_{name}.md
全局:     reports/global/INFOQ_ATLAS_GLOBAL.md
"""
from __future__ import annotations
import json
import time

from . import config as C


def _safe(name: str) -> str:
    """文件名安全化：替换路径分隔符等。"""
    for ch in '/\\:*?"<>|':
        name = name.replace(ch, "_")
    return name


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _bar(val, vmax, width=30):
    if vmax <= 0:
        return ""
    n = int(round(width * val / vmax))
    return "█" * n + "·" * (width - n)


def render_topic(tid: int, name: str) -> str:
    s = _load(C.PROCESSED / f"stats_{tid}.json")
    L = []
    L.append(f"# InfoQ Topic 深度分析：{name}\n")
    L.append(f"> topic_id: `{tid}`  ·  生成时间: {time.strftime('%Y-%m-%d %H:%M', time.localtime())}\n")

    if s.get("count", 0) == 0:
        L.append("_该 topic 在当前抓取范围内无文章_\n")
        return "\n".join(L)

    # 概览
    L.append("## 1. 概览\n")
    ys = s["year_span"]
    L.append(f"- 收录文章数：**{s['count']}** 篇（基于已爬目录）")
    L.append(f"- 时间跨度：{ys[0]} – {ys[1]}")
    L.append(f"- 累计阅读：{s['views_total']:,}  ·  篇均阅读：{s['views_avg']:,}")
    L.append("")

    # 年度趋势
    L.append("## 2. 年度发文趋势\n")
    by = s["by_year"]
    if by:
        vmax = max(by.values())
        L.append("| 年份 | 篇数 | 占比 | 分布 |")
        L.append("|------|------|------|------|")
        total = sum(by.values())
        for y, c in sorted(by.items(), key=lambda x: int(x[0])):
            pct = c / total * 100
            L.append(f"| {y} | {c} | {pct:.1f}% | `{_bar(c, vmax)}` |")
        L.append("")
        # 解读
        peak_y, peak_c = max(by.items(), key=lambda x: x[1])
        recent = sorted(by.items())[-3:]
        L.append(f"> **解读**：发文高峰为 {peak_y} 年（{peak_c} 篇）；近三年 "
                 f"{', '.join(f'{y}({c})' for y, c in recent)}。\n")

    # 近 24 月趋势
    L.append("## 3. 近 24 个月发文量\n")
    bm = s["by_month_recent"]
    if bm:
        vmax = max(bm.values()) if bm else 1
        L.append("```")
        for m, c in sorted(bm.items()):
            L.append(f"{m}  {c:>4}  {_bar(c, vmax, 24)}")
        L.append("```\n")

    # 关键词
    L.append("## 4. 高频关键词（标题+摘要）\n")
    kw = s["top_keywords"]
    if kw:
        vmax = kw[0][1]
        L.append("| 关键词 | 频次 | 分布 |")
        L.append("|--------|------|------|")
        for k, c in kw[:25]:
            L.append(f"| {k} | {c} | `{_bar(c, vmax)}` |")
        L.append("")

    # 作者
    L.append("## 5. 核心作者 Top 15\n")
    au = s["top_authors"]
    if au:
        vmax = au[0][1]
        L.append("| 排名 | 作者 | 篇数 | 分布 |")
        L.append("|------|------|------|------|")
        for i, (n, c) in enumerate(au[:15], 1):
            L.append(f"| {i} | {n} | {c} | `{_bar(c, vmax)}` |")
        L.append("")

    # 译者
    tr = s["top_translators"]
    if tr:
        L.append("## 6. 活跃译者 Top 10\n")
        L.append("| 译者 | 译篇数 |")
        L.append("|------|--------|")
        for n, c in tr[:10]:
            L.append(f"| {n} | {c} |")
        L.append("")

    # 标签
    lb = s["top_labels"]
    if lb:
        L.append("## 7. 高频标签\n")
        vmax = lb[0][1]
        L.append("| 标签 | 频次 | 分布 |")
        L.append("|------|------|------|")
        for n, c in lb[:20]:
            L.append(f"| {n} | {c} | `{_bar(c, vmax)}` |")
        L.append("")

    # 共现 topic
    co = s["top_co_topics"]
    if co:
        L.append("## 8. 关联主题（共现）\n")
        L.append(f"`{name}` 常与以下主题同现：")
        line = " · ".join(f"{x['name']}({x['count']})" for x in co[:12])
        L.append(f"\n{line}\n")

    # 头部文章
    L.append("## 9. 最受关注文章 Top 15\n")
    L.append("| 篇数 | 标题 | 年份 | 阅读 | 评论 |")
    L.append("|------|------|------|------|------|")
    for i, a in enumerate(s["top_articles_by_views"][:15], 1):
        title = a["title"].replace("|", "\\|")
        L.append(f"| {i} | {title} | {a['year']} | {a['views']:,} | {a['comment']} |")
    L.append("")

    L.append("---\n*由 InfoQ Atlas 自动生成*\n")
    return "\n".join(L)


def render_global() -> str:
    g = _load(C.PROCESSED / "stats_global.json")
    L = []
    L.append("# InfoQ 全站 Topic 综合分析报告（全局视图）\n")
    L.append(f"> 生成时间: {time.strftime('%Y-%m-%d %H:%M', time.localtime())}\n")
    L.append("## 1. 数据规模\n")
    L.append(f"- 总文章数：**{g['total_articles']:,}**（去重后）")
    L.append(f"- 含全文：{g['with_full_text']:,}")
    L.append("")

    L.append("## 2. 各 Topic 文章分布\n")
    pt = g["per_topic"]
    vmax = max((x["count"] for x in pt), default=0)
    L.append("| Topic | 文章数 | 占比 | 分布 |")
    L.append("|-------|--------|------|------|")
    tot = sum(x["count"] for x in pt) or 1
    for x in sorted(pt, key=lambda z: z["count"], reverse=True):
        L.append(f"| {x['name']} | {x['count']:,} | {x['count']/tot*100:.1f}% | `{_bar(x['count'], vmax)}` |")
    L.append("")

    L.append("## 3. 全站年度发文趋势\n")
    by = g["by_year"]
    if by:
        vmax = max(by.values())
        L.append("| 年份 | 篇数 | 分布 |")
        L.append("|------|------|------|")
        for y, c in sorted(by.items(), key=lambda x: str(x[0])):
            L.append(f"| {y} | {c} | `{_bar(c, vmax)}` |")
        L.append("")

    L.append("## 4. 全站高产作者 Top 30\n")
    au = g["top_authors"]
    if au:
        vmax = au[0]["count"]
        L.append("| # | 作者 | 篇数 | 分布 |")
        L.append("|---|------|------|------|")
        for i, a in enumerate(au, 1):
            L.append(f"| {i} | {a['name']} | {a['count']} | `{_bar(a['count'], vmax)}` |")
        L.append("")

    L.append("## 5. 全站高频标签 Top 30\n")
    lb = g["top_labels"]
    if lb:
        vmax = lb[0]["count"]
        L.append("| 标签 | 频次 | 分布 |")
        L.append("|------|------|------|")
        for x in lb:
            L.append(f"| {x['label']} | {x['count']} | `{_bar(x['count'], vmax)}` |")
        L.append("")

    L.append("## 6. 全站阅读量最高的文章 Top 30\n")
    L.append("| # | 标题 | 年份 | 阅读 |")
    L.append("|---|------|------|------|")
    for i, a in enumerate(g["top_viewed_all"], 1):
        title = a["title"].replace("|", "\\|")
        L.append(f"| {i} | {title} | {a['year']} | {a['views']:,} |")
    L.append("")

    L.append("---\n*由 InfoQ Atlas 自动生成*\n")
    return "\n".join(L)


def main():
    tree = json.loads((C.RAW_TOPICS / "topic_tree.json").read_text(encoding="utf-8"))
    for key in tree["top_level"]:
        t = tree["all_topics"][key]
        md = render_topic(int(key), t["name"])
        safe = _safe(t["name"])
        out = C.REPORT_TOPICS / f"{key}_{safe}.md"
        out.write_text(md, encoding="utf-8")
        print(f"  -> {out.name}")
    gmd = render_global()
    gout = C.REPORT_GLOBAL / "INFOQ_ATLAS_GLOBAL.md"
    gout.write_text(gmd, encoding="utf-8")
    print(f"  -> {gout}")
    # README 索引
    idx = ["# InfoQ Atlas 报告索引\n"]
    idx.append("## 全局报告\n- [INFOQ 全站综合分析](global/INFOQ_ATLAS_GLOBAL.md)\n")
    idx.append("## 各 Topic 深度报告\n")
    for key in tree["top_level"]:
        t = tree["all_topics"][key]
        safe = _safe(t["name"])
        idx.append(f"- [{t['name']}](topics/{key}_{safe}.md)")
    (C.REPORTS / "README.md").write_text("\n".join(idx), encoding="utf-8")
    print("[report] done")


if __name__ == "__main__":
    main()
