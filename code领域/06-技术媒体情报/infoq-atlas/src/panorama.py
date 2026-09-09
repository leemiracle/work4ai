"""全景主报告：综合 InfoQ 深度 + 多经典网站跨站情报，产出总览。

reports/global/PANORAMA.md  —— 项目的「一张图看懂」入口。
"""
from __future__ import annotations
import json
from . import config as C


def build():
    infoq_global = json.loads((C.PROCESSED / "stats_global.json").read_text("utf-8"))
    content = json.loads((C.PROCESSED / "content_intel.json").read_text("utf-8"))
    site = json.loads((C.PROCESSED / "site_intel.json").read_text("utf-8"))

    L = ["# 🌐 InfoQ Atlas · 技术内容全景报告\n",
         "> 一份综合 **InfoQ 中国全站** 深度分析 + **7 个经典技术网站** 跨站情报的总览。\n"]

    # 数据规模
    L.append("## 一、数据底座\n")
    L.append("| 维度 | 规模 |")
    L.append("|------|------|")
    L.append(f"| InfoQ 文章目录（去重） | **{infoq_global['total_articles']:,}** 篇 |")
    L.append(f"| InfoQ 全文深度分析 | {infoq_global['with_full_text']:,} 篇 |")
    L.append(f"| InfoQ Topic 体系 | 14 顶层 / 88 节点 |")
    L.append(f"| 跨 topic 关联 | 200,656 条 |")
    L.append(f"| 经典网站覆盖 | {site['n_sources']} 站 / {site['total']} 条 |")
    L.append("")

    # InfoQ topic 全景
    L.append("## 二、InfoQ 全站 Topic 版图\n")
    pt = sorted(infoq_global["per_topic"], key=lambda z: z["count"], reverse=True)
    vmax = max(x["count"] for x in pt)
    L.append("| Topic | 文章数 | 占比 | 规模 |")
    L.append("|-------|--------|------|------|")
    tot = sum(x["count"] for x in pt) or 1
    for x in pt:
        bar = "█" * int(20 * x["count"] / vmax)
        L.append(f"| {x['name']} | {x['count']:,} | {x['count']/tot*100:.1f}% | `{bar}` |")
    L.append("")

    # 年度演进
    L.append("## 三、全站年度内容产出演进\n")
    by = infoq_global["by_year"]
    vmax = max(by.values())
    for y, c in sorted(by.items(), key=lambda x: str(x[0])):
        bar = "█" * int(30 * c / vmax)
        L.append(f"- **{y}**：{c:,} 篇 `{bar}`")
    L.append("")

    # 跨经典网站技术共识（最重要的洞察）
    L.append("## 四、🔥 跨经典网站技术共识（核心洞察）\n")
    L.append("> 下列技术**同时在多个顶级技术站被反复讨论**——它们是当下真正的主流转技术势。\n")
    L.append("| 技术 | 出现站点数 | 站点 |")
    L.append("|------|-----------|------|")
    for u in site["universal_tech"][:18]:
        L.append(f"| {u['tech']} | **{u['in_sources']}** | {', '.join(u['sources'])} |")
    L.append("")

    # 经典网站 → InfoQ topic 投射
    L.append("## 五、经典网站内容 → InfoQ Topic 投射\n")
    L.append("> 把 7 个经典站的最新内容归类到 InfoQ topic 体系，看外部热点落在哪。\n")
    L.append("| InfoQ Topic | 经典站文章数 |")
    L.append("|-------------|-------------|")
    for t, c in sorted(site["topic_dist"].items(), key=lambda x: -x[1]):
        L.append(f"| {t} | {c} |")
    L.append("")

    # 各 topic 的内容情报速写（用 content_intel）
    L.append("## 六、各 Topic 内容情报速写\n")
    L.append("| Topic | 全文 | 头部子主题 | 头部技术实体 |")
    L.append("|-------|------|-----------|-------------|")
    for d in sorted(content["topic_digests"], key=lambda x: -x["n_fulltext"]):
        subs = " / ".join(s["theme"] for s in d["subthemes"][:3]) or "-"
        ents = "-"
        for cat, items in d["top_entities_by_cat"].items():
            if items:
                ents = f"{cat}: {', '.join(f'{t}({c})' for t, c in items[:5])}"
                break
        L.append(f"| {d['name']} | {d['n_fulltext']} | {subs} | {ents} |")
    L.append("")

    # 信息来源清单
    L.append("## 七、信息来源清单\n")
    L.append("### InfoQ 中国（主站，深度穷尽）")
    L.append(f"- {infoq_global['total_articles']:,} 篇文章目录 + {infoq_global['with_full_text']:,} 篇全文")
    L.append("- 14 个顶层 topic 各有独立深度报告 + 内容摘要报告\n")
    L.append("### 经典技术网站（跨站情报）")
    type_map = {"美团技术团队": "Atom feed", "博客园": "RSS", "开源中国": "RSS",
                "张鑫旭-前端": "RSS", "HackerNews": "Algolia API", "dev.to": "API",
                "阮一峰周刊": "HTML"}
    for src, info in sorted(site["per_source"].items(), key=lambda x: -x[1]["count"]):
        L.append(f"- **{src}**（{type_map.get(src,'-')}）：{info['count']} 条，含正文 {info['with_content']}")
    L.append("")

    L.append("## 八、报告索引\n")
    L.append("### InfoQ")
    L.append("- [全站综合分析](INFOQ_ATLAS_GLOBAL.md)")
    L.append("- [内容情报](CONTENT_INTEL.md)")
    L.append("- [跨 topic 知识图谱](knowledge_graph.md)")
    L.append("- 各 Topic：`reports/topics/{id}_{name}.md`（深度）+ `_DIGEST.md`（内容摘要）")
    L.append("### 跨经典网站")
    L.append("- [跨站点技术情报](CROSS_SITE_INTEL.md)")
    L.append("- 可视化仪表盘：`dashboard/index.html`\n")
    L.append("---\n*由 InfoQ Atlas 自动生成 · 含 InfoQ 全站 + 7 经典站 综合情报*\n")

    out = C.REPORT_GLOBAL / "PANORAMA.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"[panorama] -> {out}")


if __name__ == "__main__":
    build()
