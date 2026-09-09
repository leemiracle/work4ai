#!/usr/bin/env python3
"""
index_append.py — 增量补充索引(不重建, 不删除旧索引)

只扫描 csdiy 自建内容(精加工层 + 工具 + 根级文档), 用 INSERT OR REPLACE
追加到现有 index/search.sqlite。保留对 github-repos/website 等上游资料的索引。

用法:
    python3 tools/index_append.py              # 增量补充
    python3 tools/index_append.py --dry-run    # 只看会扫到哪些文件, 不写入
    python3 tools/index_append.py --query "tinycpu"  # 查询(同 build_index.py)
"""
from __future__ import annotations
import argparse
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / 'index' / 'search.sqlite'

# 只扫这些"自建"目录 + 根级 md(跳过上游资料 github-repos/books/website/cs-self-learning)
SELF_SCOPES = [
    'notes', 'source-reading', 'cheatsheets', 'labs',
    'projects', 'tools', 'cards', 'paths',
]
INDEX_EXT = {'md', 'markdown', 'py', 'txt', 'sh', 'json'}
MAX_BYTES = 2 * (1 << 20)


def read_text(path: Path) -> tuple[str, str]:
    """返回 (title, body)。title 取第一行 H1 或第一句"""
    try:
        raw = path.read_text(errors='ignore')
    except Exception:
        return ('', '')
    if len(raw) > MAX_BYTES:
        raw = raw[:MAX_BYTES]
    lines = raw.split('\n', 5)
    title = ''
    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            title = line[2:].strip()[:100]
            break
        if line and not line.startswith('#!') and not line.startswith('"""'):
            title = line[:80]
            break
    return (title, raw)


def subject_of(rel_path: str) -> str:
    """根据路径推断主题分类"""
    parts = rel_path.split('/')
    if parts[0] in SELF_SCOPES:
        return {'notes': '精读笔记', 'source-reading': '源码精读',
                'cheatsheets': '场景速查', 'labs': '实验指南',
                'projects': '毕业项目', 'tools': '工具',
                'cards': '实战卡片', 'paths': '学习路径'}.get(parts[0], parts[0])
    return '项目文档'


def collect_files() -> list[Path]:
    """收集所有自建文件 + 根级 md"""
    files = []
    # 自建目录
    for scope in SELF_SCOPES:
        d = ROOT / scope
        if d.exists():
            for ext in INDEX_EXT:
                files.extend(d.rglob(f'*.{ext}'))
    # 根级 md(README/INDEX/TOPICS/...)
    for md in ROOT.glob('*.md'):
        files.append(md)
    return sorted(set(files))


def append(dry_run: bool = False) -> int:
    if not DB_PATH.exists():
        print(f"❌ 索引不存在: {DB_PATH}", file=sys.stderr)
        print(f"   先跑: python3 tools/build_index.py", file=sys.stderr)
        return 1

    files = collect_files()
    print(f"📁 扫描到 {len(files)} 个自建文件")

    if dry_run:
        print("\n--- DRY RUN(预览) ---")
        for f in files:
            rel = f.relative_to(ROOT).as_posix()
            print(f"  {rel}")
        return 0

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    # 先看旧索引里有多少
    before = con.execute("SELECT v FROM meta WHERE k='doc_count'").fetchone()
    before_count = int(before['v']) if before else 0
    print(f"📊 当前索引文档数: {before_count}")

    # 增量 INSERT OR REPLACE
    inserted = 0
    skipped = 0
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        ext = f.suffix.lstrip('.')
        title, body = read_text(f)
        if not body.strip():
            skipped += 1
            continue
        subject = subject_of(rel)
        try:
            con.execute(
                "INSERT OR REPLACE INTO docs(path, subject, ext, title, body) VALUES(?, ?, ?, ?, ?)",
                (rel, subject, ext, title, body)
            )
            inserted += 1
        except Exception as e:
            print(f"  ⚠️ 失败 {rel}: {e}", file=sys.stderr)
            skipped += 1

    # 更新 meta
    after_count = con.execute("SELECT COUNT(*) FROM docs").fetchone()[0]
    con.execute("INSERT OR REPLACE INTO meta VALUES('doc_count', ?)", (str(after_count),))
    con.execute("INSERT OR REPLACE INTO meta VALUES('last_append', ?)",
                (f"self-scopes @ {__import__('datetime').datetime.now().isoformat(timespec='seconds')}",))
    con.commit()
    con.close()

    print(f"\n✓ 增量补充完成:")
    print(f"  写入/更新: {inserted}")
    print(f"  跳过: {skipped}")
    print(f"  索引总文档数: {before_count} → {after_count} (+{after_count - before_count})")
    return 0


def query(q: str, limit: int = 8):
    if not DB_PATH.exists():
        print(f"❌ 索引不存在", file=sys.stderr)
        return
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    terms = q.split()
    fts = " OR ".join(f'"{t}"*' for t in terms if t)
    sql = ("SELECT path, subject, ext, title, "
           "snippet(docs, 4, '【', '】', '…', 12) AS snip, rank "
           "FROM docs WHERE docs MATCH ? ORDER BY rank LIMIT ?")
    rows = con.execute(sql, (fts, limit)).fetchall()
    if not rows:
        like = f"%{q}%"
        rows = con.execute(
            "SELECT path, subject, ext, title, '' AS snip, 0 AS rank FROM docs "
            "WHERE title LIKE ? OR body LIKE ? LIMIT ?", (like, like, limit)
        ).fetchall()
    total = con.execute("SELECT v FROM meta WHERE k='doc_count'").fetchone()
    con.close()
    print(f"索引共 {total[0] if total else '?'} 文档 | 查询: {q!r} | 命中 {len(rows)}")
    for r in rows:
        print(f"\n[{r['subject']}/{r['ext']}] {r['title']}")
        print(f"  {r['path']}")
        if r['snip']:
            print(f"  …{r['snip']}…")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dry-run', action='store_true', help='只预览,不写入')
    ap.add_argument('--query', help='查询模式')
    ap.add_argument('--limit', type=int, default=8)
    args = ap.parse_args()
    if args.query:
        query(args.query, args.limit)
    else:
        sys.exit(append(args.dry_run))


if __name__ == '__main__':
    main()
