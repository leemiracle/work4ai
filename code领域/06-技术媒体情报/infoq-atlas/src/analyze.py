"""多维统计分析：基于 infoq.db 产出每个 topic 与全局的统计 JSON。

输出 data/processed/stats_{tid}.json 与 stats_global.json，供报告生成器使用。
"""
from __future__ import annotations
import json
import sqlite3
from collections import Counter, defaultdict

from . import config as C

TOP_N = 25


def _q(conn, sql, args=()):
    return conn.execute(sql, args).fetchall()


def topic_stats(conn, tid: int, name: str) -> dict:
    aids = [r[0] for r in _q(conn,
        "SELECT DISTINCT aid FROM article_topics WHERE topic_id=?", (tid,))]
    if not aids:
        return {"topic_id": tid, "name": name, "count": 0}
    ph = ",".join("?" * len(aids))
    rows = _q(conn,
        f"SELECT aid,title,summary,publish_time,year,month,views,comment_count "
        f"FROM articles WHERE aid IN ({ph})", aids)
    aids_set = {r[0] for r in rows}

    years = Counter(r[4] for r in rows if r[4])
    months = Counter(r[5] for r in rows if r[5])
    views_total = sum((r[6] or 0) for r in rows)
    top_views = sorted(rows, key=lambda r: r[6] or 0, reverse=True)[:TOP_N]

    # 作者/译者
    people = _q(conn,
        f"SELECT name, role FROM article_people WHERE aid IN ({ph})", aids)
    authors = Counter(p[0] for p in people if p[1] == "author")
    translators = Counter(p[0] for p in people if p[1] == "translator")

    # 标签
    labels = _q(conn,
        f"SELECT label FROM article_labels WHERE aid IN ({ph})", aids)
    label_c = Counter(l[0] for l in labels if l[0])

    # 标题关键词（中文按字 bigram + 英文词）
    kw = Counter()
    for r in rows:
        _add_keywords(kw, (r[1] or "") + " " + (r[2] or ""))

    # 关联 topic（共现）
    co = _q(conn,
        f"SELECT topic_name, COUNT(*) c FROM article_topics WHERE aid IN ({ph}) "
        f"GROUP BY topic_name ORDER BY c DESC LIMIT 15", aids)

    span_years = (min(years), max(years)) if years else (None, None)
    return {
        "topic_id": tid, "name": name,
        "count": len(aids_set),
        "views_total": views_total,
        "views_avg": round(views_total / max(1, len(rows)), 1),
        "year_span": span_years,
        "by_year": dict(sorted(years.items())),
        "by_month_recent": dict(sorted(months.items())[-24:]),
        "top_authors": authors.most_common(TOP_N),
        "top_translators": translators.most_common(15),
        "top_labels": label_c.most_common(TOP_N),
        "top_keywords": kw.most_common(40),
        "top_co_topics": [{"name": n, "count": c} for n, c in co if n != name],
        "top_articles_by_views": [
            {"aid": r[0], "title": r[1], "summary": (r[2] or "")[:160],
             "year": r[4], "views": r[6], "comment": r[7]}
            for r in top_views
        ],
    }


_KW_STOP = set("的 了 和 与 及 在 是 为 对 从 到 等 也 这 那 一个 一种 一些 被 "
               "将 可以 我们 他们 你 我 他 它 如何 通过 使用 实现 一种 以及 基于 an the of "
               "to in on for and with a is are as be by at or from how".split())


def _add_keywords(c: Counter, text: str):
    import re
    text = text.lower()
    # 英文词
    for w in re.findall(r"[a-z][a-z0-9.+#-]{2,}", text):
        if w in _KW_STOP:
            continue
        c[w] += 1
    # 中文 bigram（剔除数字标点）
    zh = re.sub(r"[^\u4e00-\u9fff]", "", text)
    for i in range(len(zh) - 1):
        bg = zh[i:i + 2]
        if bg[0] in "的了和与及在是为对从到等也被将我们":
            continue
        c[bg] += 1


def global_stats(conn) -> dict:
    total = _q(conn, "SELECT COUNT(*) FROM articles")[0][0]
    full = _q(conn, "SELECT COUNT(*) FROM articles WHERE content_len>0")[0][0]
    years = dict(_q(conn, "SELECT year, COUNT(*) FROM articles GROUP BY year ORDER BY year"))
    top_authors = _q(conn,
        "SELECT name, COUNT(*) c FROM article_people WHERE role='author' "
        "GROUP BY name ORDER BY c DESC LIMIT 30")
    top_trans = _q(conn,
        "SELECT name, COUNT(*) c FROM article_people WHERE role='translator' "
        "GROUP BY name ORDER BY c DESC LIMIT 20")
    top_labels = _q(conn,
        "SELECT label, COUNT(*) c FROM article_labels GROUP BY label "
        "ORDER BY c DESC LIMIT 40")
    per_topic = _q(conn,
        "SELECT topic_name, COUNT(DISTINCT a.aid) c FROM article_topics a "
        "GROUP BY topic_name ORDER BY c DESC")
    top_viewed = _q(conn,
        "SELECT aid,title,year,views FROM articles ORDER BY views DESC LIMIT 30")
    return {
        "total_articles": total,
        "with_full_text": full,
        "by_year": years,
        "top_authors": [{"name": n, "count": c} for n, c in top_authors],
        "top_translators": [{"name": n, "count": c} for n, c in top_trans],
        "top_labels": [{"label": l, "count": c} for l, c in top_labels],
        "per_topic": [{"name": n, "count": c} for n, c in per_topic],
        "top_viewed_all": [{"aid": r[0], "title": r[1], "year": r[2],
                            "views": r[3]} for r in top_viewed],
    }


def main():
    conn = sqlite3.connect(C.DB_PATH)
    tree = json.loads((C.RAW_TOPICS / "topic_tree.json").read_text(encoding="utf-8"))
    top_ids = [(int(k), tree["all_topics"][k]["name"]) for k in tree["top_level"]]
    print(f"[analyze] 分析 {len(top_ids)} 个顶层 topic")
    for tid, name in top_ids:
        s = topic_stats(conn, tid, name)
        (C.PROCESSED / f"stats_{tid}.json").write_text(
            json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  [{tid:>4} {name:<8}] {s['count']:>5} 篇  "
              f"年份 {s['year_span']}  作者 {len(s['top_authors'])}  关键词 {len(s['top_keywords'])}")
    g = global_stats(conn)
    (C.PROCESSED / "stats_global.json").write_text(
        json.dumps(g, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[analyze] 全局: 文章 {g['total_articles']}（含全文 {g['with_full_text']}）")
    conn.close()


if __name__ == "__main__":
    main()
