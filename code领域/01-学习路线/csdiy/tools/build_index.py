#!/usr/bin/env python3
"""csdiy 统一全文检索索引器 (SQLite FTS5)。

对 md / html / txt / pdf / code 建立全文索引, 支持中文 (simple 分词 + bigram)。
产出 index/search.sqlite (FTS5) + 提供查询 CLI。

用法:
    python3 tools/build_index.py                # 建索引
    python3 tools/build_index.py --query "xv6 页表"
    python3 tools/build_index.py --query "分布式 一致性" --limit 10
"""
from __future__ import annotations
import argparse
import html
import json
import os
import re
import sqlite3
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

INDEX_DIR = Path("index")
DB_PATH = INDEX_DIR / "search.sqlite"
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".pytest_cache",
             "chroma", "index", "manifest"}
# 只索引文本类 (跳过二进制/媒体)
INDEX_EXT = {"md", "markdown", "txt", "html", "htm", "rst", "tex",
             "py", "java", "c", "h", "cpp", "cc", "hpp", "rs", "go", "js", "ts",
             "sh", "v", "ipynb", "scala", "kt"}
PDF_EXT = {"pdf"}
MAX_FILE_BYTES = 2 * (1 << 20)  # 单文件提取上限 2MB 文本, 防巨文件
PDF_MAX_PAGES_HINT = ""  # 留空
CHUNK = 4096


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1
    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def html_to_text(raw: str) -> str:
    p = _TextExtractor()
    try:
        p.feed(raw)
    except Exception:
        pass
    text = "".join(p.parts)
    text = html.unescape(text)
    return text


def read_text(path: Path, ext: str) -> str:
    try:
        if ext in PDF_EXT:
            # pdftotext 输出到 stdout
            r = subprocess.run(
                ["pdftotext", "-q", "-l", "200", str(path), "-"],
                capture_output=True, timeout=20,
            )
            return r.stdout.decode("utf-8", "ignore")[:MAX_FILE_BYTES]
        raw = path.read_bytes()
        if ext in ("html", "htm"):
            s = raw.decode("utf-8", "ignore")
            return html_to_text(s)[:MAX_FILE_BYTES]
        if ext == "ipynb":
            import json as _json
            try:
                nb = _json.loads(raw.decode("utf-8", "ignore"))
                cells = []
                for c in nb.get("cells", []):
                    cells.append("\n".join(c.get("source", [])))
                return "\n".join(cells)[:MAX_FILE_BYTES]
            except Exception:
                return ""
        return raw.decode("utf-8", "ignore")[:MAX_FILE_BYTES]
    except (subprocess.TimeoutExpired, OSError):
        return ""


def walk_files(root: Path):
    stack = [root]
    while stack:
        base = stack.pop()
        try:
            with os.scandir(base) as it:
                entries = list(it)
        except (PermissionError, OSError):
            continue
        for e in entries:
            if e.name in SKIP_DIRS or e.name.startswith(".git"):
                continue
            if e.is_dir(follow_symlinks=False):
                stack.append(e.path)
            elif e.is_file(follow_symlinks=False):
                yield Path(e.path)


def tokenize(text: str) -> str:
    """FTS5 索引值: 英文小写化 + CJK bigram, 提升中文召回。"""
    # 中文字符 bigram
    cjk = []
    last = None
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff":
            if last is not None:
                cjk.append(last + ch)
            last = ch
        else:
            last = None
    blob = text.lower()
    return blob + " " + " ".join(cjk)


def build(root: Path, quiet: bool = False):
    INDEX_DIR.mkdir(exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "CREATE VIRTUAL TABLE docs USING fts5("
        "path, subject, ext, title, body, tokenize='unicode61')"
    )
    ins = "INSERT INTO docs(path, subject, ext, title, body) VALUES (?,?,?,?,?)"

    def subject_of(rel: str) -> str:
        parts = rel.replace("\\", "/").split("/")
        top = parts[0] if parts else ""
        return {"github-repos": "GitHub仓库", "books": "书籍",
                "website": "网站镜像", "cs-self-learning": "主仓库"}.get(top, top)

    n = 0
    for path in walk_files(root):
        ext = path.suffix.lstrip(".").lower()
        if ext not in INDEX_EXT and ext not in PDF_EXT:
            continue
        rel = path.relative_to(root).as_posix()
        # 跳过 git 内部 (双保险)
        if "/.git/" in rel or rel.startswith(".git/"):
            continue
        text = read_text(path, ext)
        if not text.strip():
            continue
        title = path.stem
        # 从 markdown 提取首个标题做 title
        if ext in ("md", "markdown"):
            m = re.search(r"^#\s+(.+)$", text, re.M)
            if m:
                title = m.group(1).strip()[:120]
        subject = subject_of(rel)
        try:
            con.execute(ins, (rel, subject, ext, title, tokenize(text)))
            n += 1
        except sqlite3.Error:
            pass
        if not quiet and n % 1000 == 0:
            print(f"  已索引 {n} 文件...", file=sys.stderr)
    con.commit()
    # 元信息表
    con.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")
    con.execute("INSERT OR REPLACE INTO meta VALUES('doc_count', ?)", (str(n),))
    con.execute("INSERT OR REPLACE INTO meta VALUES('root', ?)", (str(root),))
    con.commit()
    con.close()
    if not quiet:
        print(f"✅ 索引完成: {n} 文档 -> {DB_PATH}")


def query(q: str, limit: int, root: Path):
    if not DB_PATH.exists():
        print("索引不存在, 请先运行: python3 tools/build_index.py", file=sys.stderr)
        sys.exit(1)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    # 用 OR + 前缀 匹配, 中文靠 bigram token 命中
    terms = q.split()
    fts = " OR ".join(f'"{t}"*' for t in terms if t)
    sql = (
        "SELECT path, subject, ext, title, snippet(docs, 4, '【', '】', '…', 12) AS snip, rank "
        "FROM docs WHERE docs MATCH ? ORDER BY rank LIMIT ?"
    )
    rows = con.execute(sql, (fts, limit)).fetchall()
    if not rows:
        # 退化为 LIKE
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
        if r["snip"]:
            print(f"  …{r['snip']}…")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--query", help="查询, 提供则进入查询模式")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if args.query:
        query(args.query, args.limit, root)
    else:
        build(root, args.quiet)


if __name__ == "__main__":
    main()
