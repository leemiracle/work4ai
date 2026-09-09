#!/usr/bin/env python3
"""csdiy CS 私教: RAG 问答 (检索增强生成)。

工作流:
  1. 用 FTS5 全文索引召回 top-K 相关文档片段 (lexical retrieval)
  2. 拼装带引用的 prompt
  3. 调用生成后端 (默认 opencode run; 可选 GLM HTTP API / 离线占位)
  4. 输出带【来源】的答案

用法:
    python3 tools/ask.py "xv6 如何实现虚拟内存?"
    python3 tools/ask.py "Raft 和 Paxos 的区别" --topk 6 --no-llm   # 仅看检索片段
    python3 tools/ask.py "解释 CSAPP 第六章缓存" --backend opencode

环境变量:
    CSDIY_BACKEND   opencode (默认) | glm | none
    GLM_API_KEY     backend=glm 时需要
"""
from __future__ import annotations
import argparse
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

DB = Path("index/search.sqlite")
SYSTEM_PROMPT = """你是 csdiy CS 自学知识库的资深助教。基于下方【资料】回答用户问题。
要求:
1. 只用资料中可佐证的内容; 资料不足时坦诚说明, 不要编造。
2. 关键论断后用 [资料n] 标注来源。
3. 中文回答, 必要时给出代码/公式。结构清晰, 适合学习者。
4. 若问题超出资料范围, 给出学习方向建议。
"""


def retrieve(question: str, topk: int, filter_subject: str | None) -> list[dict]:
    if not DB.exists():
        print("索引不存在, 先运行: python3 tools/build_index.py", file=sys.stderr)
        sys.exit(1)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    terms = [t for t in question.replace(",", " ").split() if t]
    # 中英文混合: 对中文做 bigram 拆分提升命中
    extra = []
    for t in terms:
        if any("\u4e00" <= c <= "\u9fff" for c in t):
            extra += [t[i:i+2] for i in range(len(t)-1)]
    fts = " OR ".join(f'"{x}"*' for x in (terms + extra) if x)
    sql = (
        "SELECT path, subject, ext, title, "
        "snippet(docs, 4, '【', '】', '…', 18) AS snip, rank "
        "FROM docs WHERE docs MATCH ? "
        + ("AND subject=? " if filter_subject else "")
        + "ORDER BY rank LIMIT ?"
    )
    params = ([fts] + ([filter_subject] if filter_subject else []) + [topk],)
    try:
        rows = con.execute(sql, params[0]).fetchall()
    except sqlite3.OperationalError:
        rows = []
    if not rows:  # 退化 LIKE
        like = f"%{question.replace(' ', '%')}%"
        rows = con.execute(
            "SELECT path, subject, ext, title, '' AS snip, 0 AS rank FROM docs "
            "WHERE title LIKE ? OR body LIKE ? LIMIT ?",
            (like, like, topk),
        ).fetchall()
    con.close()
    return [dict(r) for r in rows]


def build_prompt(question: str, docs: list[dict]) -> str:
    ctx = []
    for i, d in enumerate(docs, 1):
        snip = d["snip"] or (d["title"] + " (见该文档)")
        ctx.append(f"[资料{i}] {d['subject']}/{d['ext']} | {d['path']}\n{snip}")
    block = "\n\n".join(ctx) if ctx else "(无匹配资料)"
    return (
        f"{SYSTEM_PROMPT}\n\n===== 资料 =====\n{block}\n\n"
        f"===== 用户问题 =====\n{question}\n\n===== 回答 ====="
    )


def gen_opencode(prompt: str) -> str:
    try:
        r = subprocess.run(
            ["opencode", "run", "--prompt", prompt],
            capture_output=True, text=True, timeout=180,
        )
        out = r.stdout.strip()
        return out or f"[opencode 无输出] stderr: {r.stderr[:300]}"
    except FileNotFoundError:
        return "[错误] opencode 未安装, 请改用 --backend glm 或 none"
    except subprocess.TimeoutExpired:
        return "[超时] opencode 生成超时"


def gen_glm(prompt: str) -> str:
    key = os.environ.get("GLM_API_KEY")
    if not key:
        return "[错误] 未设置 GLM_API_KEY"
    import urllib.request
    body = json.dumps({
        "model": "glm-4-flash",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }).encode()
    req = urllib.request.Request(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        data=body, headers={"Authorization": f"Bearer {key}",
                            "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[GLM 错误] {e}"


def main():
    ap = argparse.ArgumentParser(description="csdiy CS 私教 (RAG)")
    ap.add_argument("question")
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--subject", help="限定主题, 如 操作系统/AI/数据库")
    ap.add_argument("--backend", default=os.environ.get("CSDIY_BACKEND", "opencode"),
                    choices=["opencode", "glm", "none"])
    ap.add_argument("--no-llm", action="store_true", help="只检索不生成")
    args = ap.parse_args()

    docs = retrieve(args.question, args.topk, args.subject)
    print(f"🔍 检索到 {len(docs)} 篇相关资料:")
    for i, d in enumerate(docs, 1):
        print(f"  [{i}] {d['subject']}/{d['ext']} — {d['title']}")
        print(f"      {d['path']}")

    if args.no_llm or args.backend == "none":
        print("\n--- 片段预览 ---")
        for d in docs:
            if d["snip"]:
                print(f"• {d['path']}: …{d['snip']}…")
        return

    prompt = build_prompt(args.question, docs)
    print("\n🧠 生成中...\n")
    if args.backend == "opencode":
        ans = gen_opencode(prompt)
    elif args.backend == "glm":
        ans = gen_glm(prompt)
    else:
        ans = "[无后端]"
    print(ans)


if __name__ == "__main__":
    main()
