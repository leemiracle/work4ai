"""内容情报：对 833 篇全文做深度分析，生成每个 topic 的「内容摘要报告」。

产出:
- data/processed/content_intel.json      全量结构化结果
- reports/topics/{tid}_DIGEST.md         每 topic 内容摘要报告
- reports/global/CONTENT_INTEL.md        全站内容情报
"""
from __future__ import annotations
import json
import re
import time
from collections import Counter, defaultdict

from . import config as C
from .nlp import extract_entities, keyphrases, summarize, TECH_LEXICON


def load_full_texts() -> list[dict]:
    """bulk 读全文，返回 [{aid, uuid, topic_id, title, summary, publish_time, year, views, markdown}]"""
    out = []
    for p in sorted(C.RAW_ARTICLES.glob("*.json")):
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        meta = rec.get("meta", {})
        det = rec.get("detail", {})
        md = rec.get("markdown", "")
        if not md or len(md) < 120 or md.startswith("[content"):
            continue
        tid = meta.get("_topic_crawl_id")
        pt = det.get("publish_time") or meta.get("publish_time") or 0
        try:
            pt = int(pt)
        except (TypeError, ValueError):
            pt = 0
        year = time.gmtime(pt / 1000).tm_year if pt > 0 else None
        out.append({
            "aid": str(rec.get("aid")),
            "uuid": rec.get("uuid"),
            "topic_id": int(tid) if tid is not None else None,
            "title": det.get("title") or meta.get("article_title", ""),
            "summary": det.get("summary") or meta.get("article_summary", ""),
            "publish_time": pt, "year": year,
            "views": int(meta.get("views") or 0),
            "markdown": md,
        })
    return out


def analyze_article(a: dict) -> dict:
    text = a["markdown"]
    ents = extract_entities(text)
    kps = keyphrases(text, topk=12)
    summ = summarize(text, n=2)
    # 实体总计数
    ent_total = sum(c for cat in ents.values() for c in cat.values())
    return {"aid": a["aid"], "title": a["title"], "year": a["year"],
            "views": a["views"], "topic_id": a["topic_id"],
            "entities": ents, "keyphrases": kps,
            "summary": summ, "ent_total": ent_total, "len": len(text)}


def topic_digest(items: list[dict], analyses: list[dict], tid: int,
                 name: str) -> dict:
    """单 topic 的内容聚合。"""
    # 实体聚合
    ent_cat: dict[str, Counter] = defaultdict(Counter)
    kp_c: Counter = Counter()
    for an in analyses:
        for cat, m in an["entities"].items():
            ent_cat[cat].update(m)
        for kp, sc in an["keyphrases"]:
            kp_c[kp] += sc
    # 子主题发现：高频关键短语即子主题，统计提及文章数（用每篇 top 关键短语）
    article_themes: dict[str, list[str]] = defaultdict(list)
    for an in analyses:
        for kp, _ in an["keyphrases"][:5]:
            article_themes[kp].append(an["title"][:40])
    subthemes = []
    for kp, _ in kp_c.most_common(12):
        subthemes.append({"theme": kp, "weight": kp_c[kp],
                          "n_articles": len(article_themes.get(kp, []))})

    # 概念演化：按年份看高频实体/关键短语
    by_year_ents: dict[int, Counter] = defaultdict(Counter)
    for an in analyses:
        if an["year"]:
            flat = Counter()
            for cat, m in an["entities"].items():
                flat.update(m)
            by_year_ents[an["year"]].update(flat)
    evolution = {}
    for y in sorted(by_year_ents):
        evolution[y] = by_year_ents[y].most_common(8)

    # 代表性摘要（按阅读量取头部）
    top_arts = sorted(analyses, key=lambda x: x["views"], reverse=True)[:8]

    return {
        "topic_id": tid, "name": name,
        "n_fulltext": len(analyses),
        "top_entities_by_cat": {c: ent_cat[c].most_common(12) for c in ent_cat},
        "top_keyphrases": kp_c.most_common(25),
        "subthemes": subthemes,
        "concept_evolution": evolution,
        "representative": [{"title": a["title"], "year": a["year"],
                            "views": a["views"], "summary": a["summary"]}
                           for a in top_arts],
    }


def render_topic_digest(d: dict) -> str:
    L = [f"# {d['name']} · 内容深度摘要\n",
         f"> 基于 {d['n_fulltext']} 篇高价值全文的实体抽取 / 关键短语 / 自动摘要 / 子主题发现\n"]
    if d["n_fulltext"] == 0:
        L.append("_该 topic 暂无可用全文_\n")
        return "\n".join(L)

    L.append("## 1. 技术实体图谱（按分类）\n")
    for cat, items in sorted(d["top_entities_by_cat"].items(),
                             key=lambda x: -sum(c for _, c in x[1])):
        if not items:
            continue
        line = " · ".join(f"{t}({c})" for t, c in items[:10])
        L.append(f"**{cat}**：{line}\n")

    L.append("## 2. 核心关键短语 Top 25\n")
    L.append("| 短语 | 权重 |")
    L.append("|------|------|")
    for kp, sc in d["top_keyphrases"][:25]:
        L.append(f"| {kp} | {sc} |")
    L.append("")

    L.append("## 3. 发现的子主题\n")
    for st in d["subthemes"]:
        L.append(f"- **{st['theme']}**（权重 {st['weight']}，约 {st['n_articles']} 篇提及）")
    L.append("")

    L.append("## 4. 概念演化（年度热门实体）\n")
    for y, ents in list(d["concept_evolution"].items())[-8:]:
        line = " · ".join(f"{n}({c})" for n, c in ents[:6])
        L.append(f"- **{y}**：{line}")
    L.append("")

    L.append("## 5. 代表性文章·自动摘要\n")
    for a in d["representative"]:
        L.append(f"### {a['title']}")
        L.append(f"*{a['year']} · 阅读 {a['views']:,}*\n")
        for s in a["summary"]:
            L.append(f"> {s}")
        L.append("")
    L.append("---\n*由 InfoQ Atlas 内容情报层生成*\n")
    return "\n".join(L)


def render_global_digest(digests: list[dict], all_an: list[dict]) -> str:
    L = ["# InfoQ 全站内容情报\n",
         f"> 对 {len(all_an)} 篇全文做实体/关键短语/摘要分析后的跨 topic 综合视图\n"]
    # 全局实体
    ent_cat: dict[str, Counter] = defaultdict(Counter)
    for an in all_an:
        for cat, m in an["entities"].items():
            ent_cat[cat].update(m)
    L.append("## 全站技术实体热度（分领域）\n")
    for cat in sorted(ent_cat, key=lambda c: -sum(ent_cat[c].values())):
        items = ent_cat[cat].most_common(15)
        line = " · ".join(f"{t}({c})" for t, c in items)
        L.append(f"**{cat}**：{line}\n")
    # 全局关键短语
    kp_c: Counter = Counter()
    for an in all_an:
        for kp, sc in an["keyphrases"]:
            kp_c[kp] += sc
    L.append("## 全站关键短语 Top 40\n")
    L.append("| 短语 | 权重 | | 短语 | 权重 |")
    L.append("|------|------|-|------|------|")
    kps = kp_c.most_common(40)
    for i in range(0, len(kps), 2):
        left = f"{kps[i][0]} | {kps[i][1]}"
        right = f"{kps[i+1][0]} | {kps[i+1][1]}" if i + 1 < len(kps) else " | "
        L.append(f"| {left} | {right} |")
    L.append("")
    # 各 topic 一行总结
    L.append("## 各 Topic 内容速写\n")
    L.append("| Topic | 全文数 | 头部子主题 | 头部实体 |")
    L.append("|-------|--------|-----------|---------|")
    for d in sorted(digests, key=lambda x: -x["n_fulltext"]):
        subs = " / ".join(s["theme"] for s in d["subthemes"][:3])
        ents = ""
        for cat, items in d["top_entities_by_cat"].items():
            if items:
                ents = f"{cat}:{items[0][0]}"
                break
        L.append(f"| {d['name']} | {d['n_fulltext']} | {subs} | {ents} |")
    L.append("\n---\n*由 InfoQ Atlas 内容情报层生成*\n")
    return "\n".join(L)


def main():
    items = load_full_texts()
    print(f"[content_intel] 载入 {len(items)} 篇全文")
    all_an = [analyze_article(a) for a in items]
    print(f"[content_intel] 完成单篇分析")

    # 按 topic 分组
    tree = json.loads((C.RAW_TOPICS / "topic_tree.json").read_text(encoding="utf-8"))
    tname = {int(k): v["name"] for k, v in tree["all_topics"].items()}
    by_topic: dict[int, list[dict]] = defaultdict(list)
    by_topic_items: dict[int, list[dict]] = defaultdict(list)
    for a, an in zip(items, all_an):
        tid = an["topic_id"]
        if tid is not None:
            by_topic[tid].append(an)
            by_topic_items[tid].append(a)

    digests = []
    for key in tree["top_level"]:
        tid = int(key)
        name = tname.get(tid, str(tid))
        ans = by_topic.get(tid, [])
        d = topic_digest(by_topic_items.get(tid, []), ans, tid, name)
        digests.append(d)
        md = render_topic_digest(d)
        safe = _safe(name)
        (C.REPORT_TOPICS / f"{tid}_{safe}_DIGEST.md").write_text(md, encoding="utf-8")
        print(f"  -> {tid}_{safe}_DIGEST.md  ({d['n_fulltext']} 全文)")

    # 全局
    gmd = render_global_digest(digests, all_an)
    (C.REPORT_GLOBAL / "CONTENT_INTEL.md").write_text(gmd, encoding="utf-8")
    print(f"  -> CONTENT_INTEL.md")

    # 结构化结果
    (C.PROCESSED / "content_intel.json").write_text(
        json.dumps({"topic_digests": digests,
                    "global_top_entities": None}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print("[content_intel] done")


def _safe(name: str) -> str:
    for ch in '/\\:*?"<>|':
        name = name.replace(ch, "_")
    return name


if __name__ == "__main__":
    main()
