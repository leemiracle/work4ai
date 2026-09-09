"""轻量富化：从 articles.no_author 解析作者名补入 article_people。
避免 460s 的全量 rebuild。幂等（先删 role='author' 由本表产生的记录）。
"""
from __future__ import annotations
import re
import sqlite3
from . import config as C

# 去除常见前后缀噪声
_PREFIX = re.compile(r"^(作者|原创|文|策划|编辑|受访|嘉宾|出品|整理|来源|撰文)\s*[:：|\-·,，\s]*")
_SEP = re.compile(r"[,，、；;·|/]+|\s+以及\s+|\s+和\s+|\s+与\s+|\s+采访\s+")


def parse_authors(no_author: str) -> list[str]:
    if not no_author:
        return []
    s = str(no_author).strip()
    s = _PREFIX.sub("", s)
    parts = [p.strip(" 　·.-—:") for p in _SEP.split(s)]
    out = []
    for p in parts:
        if not p:
            continue
        if len(p) > 30:          # 太长，可能是机构/句子
            continue
        if re.fullmatch(r"[\W\d]+", p):   # 纯标点/数字
            continue
        out.append(p)
    return out


def main():
    conn = sqlite3.connect(C.DB_PATH)
    rows = conn.execute("SELECT aid, no_author FROM articles WHERE no_author!=''").fetchall()
    print(f"[enrich] 待解析 {len(rows)} 条 no_author")
    added = 0
    existing = set(conn.execute("SELECT DISTINCT aid,name FROM article_people").fetchall())
    for aid, na in rows:
        for name in parse_authors(na):
            if (aid, name) in existing:
                continue
            existing.add((aid, name))
            conn.execute("INSERT INTO article_people(aid,name,role) VALUES(?,?, 'author')",
                         (aid, name))
            added += 1
    conn.commit()
    n_auth = conn.execute("SELECT COUNT(DISTINCT name) FROM article_people WHERE role='author'").fetchone()[0]
    n_links = conn.execute("SELECT COUNT(*) FROM article_people WHERE role='author'").fetchone()[0]
    conn.close()
    print(f"[enrich] 新增作者链接 {added}；现共有作者 {n_auth} 人，链接 {n_links}")


if __name__ == "__main__":
    main()
