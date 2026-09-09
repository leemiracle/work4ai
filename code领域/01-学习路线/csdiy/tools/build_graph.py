#!/usr/bin/env python3
"""csdiy 知识图谱生成器: 课程-概念-先修关系。

从 cs-self-learning/docs 的目录结构与 markdown 标题中抽取:
  - 课程节点 (CS101/MIT6.824/...)
  - 学科主题节点 (操作系统/网络/...)
  - 先修关系 (硬编码先修表 + 同主题聚类边)
  - 概念标签 (从 md 标题抽取关键词)

输出:
  graph/nodes.jsonl   节点
  graph/edges.jsonl   边
  graph/graph.json    {nodes, links} 供 vis.js/d3 渲染
  graph/graph.mmd     Mermaid 流程图
"""
from __future__ import annotations
import json
import re
from pathlib import Path

# 先修关系 (course -> prereqs) 基于 csdiy.wiki 公认路径
PREREQUISITES = {
    "MIT6.S081": ["CSAPP", "NandToTetris"],
    "MIT6.824": ["MIT6.S081", "CS162"],
    "CS162": ["CSAPP", "CS61C"],
    "CS144": ["CS61C", "topdown"],
    "CS169": ["CS61A", "CS61B"],
    "CS186": ["CS61B", "CS61C"],
    "CS224n": ["CS229", "CS231n"],
    "CS229": ["线性代数", "概率论"],
    "CMU15-445": ["CS186", "CSAPP"],
    "CMU10-714": ["CS229", "微积分"],
    "CS143": ["编译原理基础"],
    "CS420": ["CS143"],
    "MIT6.031": ["CS61A"],
    "CS149": ["CSAPP", "CS110"],
    "15462": ["CS148", "线性代数"],
    "GAMES101": ["线性代数"],
    "GAMES202": ["GAMES101", "15462"],
    "CS110": ["CSAPP"],
}

# 学科分类
SUBJECT_OF = {
    "MIT6.S081": "操作系统", "MIT6.824": "分布式系统", "HITOS": "操作系统",
    "NJUOS": "操作系统", "CS162": "操作系统", "NandToTetris": "体系结构",
    "CSAPP": "系统基础", "CS110": "系统基础", "MIT6.031": "软件工程",
    "MIT6.1600": "系统基础", "CS169": "软件工程", "6031": "软件工程",
    "17803": "软件工程", "CS144": "计算机网络", "topdown": "计算机网络",
    "CS168": "计算机网络", "CS61A": "程序设计", "CS61B": "数据结构",
    "CS61C": "体系结构", "CS70": "数学", "CS161": "算法", "CS170": "算法",
    "CS186": "数据库", "CMU15-445": "数据库", "CS229": "AI/ML",
    "CS224n": "AI/ML", "CMU10-714": "AI/ML", "MIT6.5940_TinyML": "AI/ML",
    "CS143": "编译原理", "CS420": "编译原理", "NJU-Compilers": "编译原理",
    "PKU-Compilers": "编译原理", "SJTU-Compilers": "编译原理",
    "USTC-Compilers": "编译原理", "CS149": "并行计算", "MIT18.330": "数学",
    "CVX101": "数学", "EE16A": "数学", "15462": "图形学", "CS148": "图形学",
    "GAMES101": "图形学", "GAMES202": "图形学", "GAMES103": "图形学",
    "EECS126": "概率", "EE120": "信号", "MIT6.824": "分布式系统",
}

COURSE_CODE_RE = re.compile(
    r"(MIT6\.S?081|MIT6?\.?824|MIT6\.?1600|MIT6\.?5940|MIT6\.?031|MIT18\.330|"
    r"CS1[0-9]{2}|CMU1[05]-?\d{3}|GAMES10[1-9]|GAMES20[0-9]|"
    r"CSAPP|Nand2Tetris|NandToTetris|HITOS|NJUOS|topdown|EE16A|EECS126|EE120|CVX101)"
)


def collect_courses(docs_dir: Path) -> list[dict]:
    """从 docs 目录扫 markdown 文件名提取课程。"""
    courses = {}
    if not docs_dir.exists():
        docs_dir = Path("cs-self-learning/docs")
    for md in docs_dir.rglob("*.md"):
        name = md.stem
        if name.endswith(".en"):
            continue
        m = COURSE_CODE_RE.search(name)
        code = m.group(1) if m else name
        subject = SUBJECT_OF.get(code, _guess_subject(name, md))
        title = _read_title(md) or name
        courses[code] = {
            "id": code, "label": f"{code}", "title": title,
            "subject": subject, "file": str(md).replace("\\", "/"),
        }
    return list(courses.values())


def _guess_subject(name: str, md: Path) -> str:
    for part in str(md).replace("\\", "/").split("/"):
        for kw in ("操作系统", "网络", "系统基础", "体系结构", "编译", "图形",
                   "算法", "数据库", "并行", "分布式", "数学", "软件工程",
                   "AI", "人工智能", "Web"):
            if kw in part or kw in name:
                return kw
    return "其它"


def _read_title(md: Path) -> str:
    try:
        for line in md.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()[:80]
    except OSError:
        pass
    return ""


def build_graph():
    out = Path("graph")
    out.mkdir(exist_ok=True)
    courses = collect_courses(Path("cs-self-learning/docs"))
    course_ids = {c["id"] for c in courses}

    # 补充先修表里出现但 docs 没有的节点 (如 线性代数/概率论)
    extra_subjects = set()
    for prereqs in PREREQUISITES.values():
        for p in prereqs:
            if p not in course_ids:
                extra_subjects.add(p)
    for s in extra_subjects:
        courses.append({"id": s, "label": s, "title": s,
                        "subject": SUBJECT_OF.get(s, "数学"), "file": ""})

    # 节点
    nodes = []
    for c in courses:
        nodes.append({
            "id": c["id"], "label": c["label"], "title": c["title"],
            "group": c["subject"], "type": "course",
        })
    # 主题节点
    subjects = sorted({c["subject"] for c in courses})
    for s in subjects:
        nodes.append({"id": f"subj::{s}", "label": s, "group": s, "type": "subject"})

    # 边
    edges = []
    seen = set()
    # 课程 -> 主题
    for c in courses:
        e = (c["id"], f"subj::{c['subject']}", "belongs_to")
        if e[0] != c["id"] or True:
            edges.append({"source": c["id"], "target": f"subj::{c['subject']}",
                          "relation": "belongs_to"})
    # 先修
    for code, prereqs in PREREQUISITES.items():
        if code not in course_ids and code not in {n["id"] for n in nodes}:
            continue
        for p in prereqs:
            if {p, code} <= {n["id"] for n in nodes}:
                key = (p, code, "prerequisite")
                if key not in seen:
                    seen.add(key)
                    edges.append({"source": p, "target": code,
                                  "relation": "prerequisite"})

    # 写文件
    with open(out / "nodes.jsonl", "w", encoding="utf-8") as f:
        for n in nodes:
            f.write(json.dumps(n, ensure_ascii=False) + "\n")
    with open(out / "edges.jsonl", "w", encoding="utf-8") as f:
        for e in edges:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    graph = {"nodes": nodes, "links": edges}
    with open(out / "graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)

    # Mermaid
    by_subj = {}
    for c in courses:
        by_subj.setdefault(c["subject"], []).append(c["id"])
    lines = ["graph LR"]
    for s, codes in by_subj.items():
        lines.append(f"  subgraph {s}")
        for code in codes:
            lines.append(f"    {code.replace('.', '_')}[\"{code}\"]")
        lines.append("  end")
    for e in edges:
        if e["relation"] == "prerequisite":
            s = e["source"].replace(".", "_")
            t = e["target"].replace(".", "_")
            lines.append(f"  {s} --> {t}")
    with open(out / "graph.mmd", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"✅ 图谱: {len(nodes)} 节点 ({len(courses)} 课程 + {len(subjects)} 主题), "
          f"{len(edges)} 边")
    print(f"   先修关系: {sum(1 for e in edges if e['relation']=='prerequisite')} 条")
    print(f"   输出: graph/nodes.jsonl edges.jsonl graph.json graph.mmd")


if __name__ == "__main__":
    build_graph()
