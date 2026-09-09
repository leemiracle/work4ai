"""跨站点情报：对多经典站采集结果做实体/关键短语分析 + 跨站技术全景。

产出:
- data/processed/site_intel.json
- reports/global/CROSS_SITE_INTEL.md
并尝试把站点记录归入 InfoQ 的 topic 体系，做全景对照。
"""
from __future__ import annotations
import json
import re
from collections import Counter, defaultdict

from . import config as C
from .nlp import extract_entities, keyphrases, summarize, clean_text, TECH_LEXICON

SDIR = C.ROOT / "data" / "raw" / "sites"


def load_sites() -> list[dict]:
    out = []
    for p in sorted(SDIR.glob("*.jsonl")):
        text = p.read_text(encoding="utf-8")
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                rec["_file"] = p.stem
                out.append(rec)
            except json.JSONDecodeError:
                continue
    return out


# 简单 topic 归类：依据标题/标签/内容关键词映射到 InfoQ topic
TOPIC_KEYWORDS = {
    "AI&大模型": ["AI", "大模型", "LLM", "GPT", "Agent", "RAG", "DeepSeek", "Claude",
        "机器学习", "深度学习", "神经网络", "Transformer", "微调", "推理"],
    "架构": ["架构", "微服务", "中台", "DDD", "分布式", "高并发", "Service Mesh"],
    "后端": ["后端", "数据库", "MySQL", "Redis", "Kafka", "Java", "Go", "中间件"],
    "大前端": ["前端", "React", "Vue", "CSS", "JavaScript", "TypeScript", "Web"],
    "云计算": ["云", "Kubernetes", "K8s", "Docker", "Serverless", "AWS", "阿里云"],
    "大数据": ["大数据", "Spark", "Flink", "数据湖", "数仓", "OLAP", "ClickHouse"],
    "软件工程": ["工程", "研发", "DevOps", "测试", "CI/CD", "效能", "代码"],
    "安全": ["安全", "漏洞", "加密", "攻防", "零信任"],
}


def classify_topic(rec: dict) -> str:
    hay = (rec.get("title", "") + " " + " ".join(rec.get("tags") or []) + " "
           + (rec.get("summary") or "") + " " + (rec.get("content") or "")[:2000])
    scores = {t: 0 for t in TOPIC_KEYWORDS}
    for topic, kws in TOPIC_KEYWORDS.items():
        for k in kws:
            if k in hay:
                scores[topic] += hay.count(k)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "其他"


def analyze():
    recs = load_sites()
    print(f"[site_intel] 载入 {len(recs)} 条站点记录")

    # 按 source 聚合
    by_src: dict[str, list[dict]] = defaultdict(list)
    for r in recs:
        by_src[r["source"]].append(r)

    per_source = {}
    global_ent: dict[str, Counter] = defaultdict(Counter)
    global_kp: Counter = Counter()
    topic_dist: Counter = Counter()
    for src, items in by_src.items():
        ent_cat: dict[str, Counter] = defaultdict(Counter)
        kp_c: Counter = Counter()
        nfull = 0
        sample_summaries = []
        for it in items:
            text = it.get("content") or it.get("summary") or ""
            if len(text) >= 120:
                nfull += 1
            text = clean_text(text)
            ents = extract_entities(text)
            for cat, m in ents.items():
                ent_cat[cat].update(m)
                global_ent[cat].update(m)
            for kp, sc in keyphrases(text, topk=8):
                kp_c[kp] += sc
                global_kp[kp] += sc
            topic_dist[classify_topic(it)] += 1
        per_source[src] = {
            "count": len(items), "with_content": nfull,
            "top_entities": {c: ent_cat[c].most_common(10) for c in ent_cat},
            "top_keyphrases": kp_c.most_common(15),
        }

    # 跨站技术全景：实体在多少个 source 出现（普适度）
    ent_sources: dict[str, set] = defaultdict(set)
    ent_count: Counter = Counter()
    for src, info in per_source.items():
        for cat, items in info["top_entities"].items():
            for term, c in items:
                ent_sources[f"{cat}:{term}"].add(src)
                ent_count[f"{cat}:{term}"] += c
    universal = sorted(ent_sources.items(),
                       key=lambda x: (-len(x[1]), -ent_count[x[0]]))[:40]

    return {"per_source": per_source, "topic_dist": dict(topic_dist),
            "global_entities": {c: global_ent[c].most_common(20) for c in global_ent},
            "global_keyphrases": global_kp.most_common(40),
            "universal_tech": [{"tech": k, "in_sources": len(v),
                                "sources": sorted(v), "count": ent_count[k]}
                               for k, v in universal],
            "total": len(recs), "n_sources": len(by_src)}


def render(d: dict) -> str:
    L = ["# 跨经典网站技术情报\n",
         f"> 聚合 {d['n_sources']} 个经典技术站 · {d['total']} 条内容 · "
         f"实体抽取 / 关键短语 / topic 归类 / 跨站技术普适度\n"]

    L.append("## 1. 采集来源概览\n")
    L.append("| 来源 | 条数 | 含正文 | 类型 |")
    L.append("|------|------|--------|------|")
    type_map = {"美团技术团队": "Atom", "博客园": "RSS", "开源中国": "RSS",
                "张鑫旭-前端": "RSS", "HackerNews": "API", "dev.to": "API",
                "阮一峰周刊": "HTML"}
    for src, info in sorted(d["per_source"].items(), key=lambda x: -x[1]["count"]):
        L.append(f"| {src} | {info['count']} | {info['with_content']} | "
                 f"{type_map.get(src,'-')} |")
    L.append("")

    L.append("## 2. 站点内容 → InfoQ Topic 归类分布\n")
    L.append("| InfoQ Topic | 站点文章数 |")
    L.append("|-------------|-----------|")
    for t, c in sorted(d["topic_dist"].items(), key=lambda x: -x[1]):
        L.append(f"| {t} | {c} |")
    L.append("")

    L.append("## 3. 跨站技术普适度（在多个站点同时出现的核心技术）\n")
    L.append("> 出现在越多经典站 = 越通用、越值得关注的技术。\n")
    L.append("| 技术 | 出现站点数 | 总提及 | 站点 |")
    L.append("|------|-----------|--------|------|")
    for u in d["universal_tech"][:30]:
        L.append(f"| {u['tech']} | {u['in_sources']} | {u['count']} | "
                 f"{', '.join(u['sources'])} |")
    L.append("")

    L.append("## 4. 全局技术实体热度（分领域，跨所有站）\n")
    for cat in sorted(d["global_entities"], key=lambda c: -sum(c2 for _, c2 in d["global_entities"][c])):
        items = d["global_entities"][cat]
        if not items:
            continue
        L.append(f"**{cat}**：{' · '.join(f'{t}({c})' for t, c in items[:12])}\n")

    L.append("## 5. 全局关键短语 Top 30\n")
    L.append("| 短语 | 权重 |")
    L.append("|------|------|")
    for kp, sc in d["global_keyphrases"][:30]:
        L.append(f"| {kp} | {sc:.0f} |")
    L.append("")

    L.append("## 6. 各站点深度速写\n")
    for src, info in sorted(d["per_source"].items(), key=lambda x: -x[1]["count"]):
        L.append(f"### {src}（{info['count']} 条）")
        top_ent = ""
        for cat, items in info["top_entities"].items():
            if items:
                top_ent = f"{cat}: {', '.join(f'{t}({c})' for t, c in items[:6])}"
                break
        L.append(f"- 头部实体：{top_ent}")
        kps = " / ".join(k for k, _ in info["top_keyphrases"][:8])
        L.append(f"- 关键短语：{kps}\n")

    L.append("---\n*由 InfoQ Atlas 跨站点情报层生成*\n")
    return "\n".join(L)


def main():
    d = analyze()
    (C.PROCESSED / "site_intel.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    md = render(d)
    (C.REPORT_GLOBAL / "CROSS_SITE_INTEL.md").write_text(md, encoding="utf-8")
    print(f"[site_intel] -> site_intel.json / CROSS_SITE_INTEL.md")
    print(f"  跨站技术 {len(d['universal_tech'])} 项，topic 分布 {len(d['topic_dist'])} 类")


if __name__ == "__main__":
    main()
