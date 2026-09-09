#!/usr/bin/env python3
"""csdiy 学习路径 + Anki 闪卡生成器。

基于知识图谱与公认 CS 自学路径, 产出:
  paths/<track>.md     每条学习路径的可视化 roadmap
  paths/tracks.json    所有路径结构化数据
  paths/anki.tsv       Anki 可导入的闪卡 (制表符分隔)
  paths/anki-deck.json Anki 牌组 (JSON, 供 genanki 导入)

用法:
    python3 tools/build_paths.py
    python3 tools/build_paths.py --track systems   # 仅输出某条
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

# 精选学习路径 (id -> {name, goal, steps:[{course, why, est_weeks}]})
TRACKS = {
    "systems": {
        "name": "系统/底层方向",
        "goal": "深入理解计算机系统, 能写 OS/数据库/分布式系统",
        "difficulty": "硬核",
        "steps": [
            {"course": "NandToTetris", "title": "从与非门到俄罗斯方块",
             "why": "自底向上理解计算机: 逻辑门→CPU→汇编→OS", "weeks": 8},
            {"course": "CSAPP", "title": "计算机系统基础 (CMU 15-213)",
             "why": "系统圣经, 程序员视角的底层全貌", "weeks": 14},
            {"course": "CS110", "title": "斯坦福系统基础",
             "why": "CSAPP 进阶, 并发与系统编程", "weeks": 10},
            {"course": "MIT6.S081", "title": "MIT 操作系统 (xv6)",
             "why": "亲手改 xv6 内核: 虚存/调度/文件系统", "weeks": 12},
            {"course": "CS162", "title": "伯克利操作系统",
             "why": "Pintos 项目, 另一视角的 OS 实现", "weeks": 12},
            {"course": "CMU15-445", "title": "CMU 数据库 (Bustub)",
             "why": "手写存储引擎/查询执行", "weeks": 10},
            {"course": "MIT6.824", "title": "MIT 分布式系统",
             "why": "Raft/分片/一致性, 工业界必修", "weeks": 12},
        ],
    },
    "ai": {
        "name": "AI/机器学习方向",
        "goal": "从数学基础到深度学习, 能读论文/做研究",
        "difficulty": "数学密集",
        "steps": [
            {"course": "线性代数", "title": "MIT 18.06 / CS70",
             "why": "ML 的语言是矩阵和概率", "weeks": 10},
            {"course": "概率论", "title": "EECS126 / MIT18.330",
             "why": "统计推断与随机过程", "weeks": 8},
            {"course": "CS229", "title": "Stanford 机器学习",
             "why": "吴恩达经典, ML 数学根基", "weeks": 10},
            {"course": "CS231n", "title": "Stanford 深度学习与CV",
             "why": "CNN/反向传播/视觉", "weeks": 8},
            {"course": "CS224n", "title": "Stanford NLP 与深度学习",
             "why": "词向量/Transformer 鼎峰之路", "weeks": 8},
            {"course": "CMU10-714", "title": "CMU 深度学习系统",
             "why": "手写深度学习框架", "weeks": 10},
            {"course": "MIT6.5940_TinyML", "title": "MIT TinyML",
             "why": "模型部署与端侧推理", "weeks": 6},
        ],
    },
    "fullstack": {
        "name": "全栈/应用方向",
        "goal": "能独立设计并交付 Web 应用",
        "difficulty": "工程导向",
        "steps": [
            {"course": "CS61A", "title": "伯克利 程序设计 (Python)",
             "why": "抽象与编程思维地基", "weeks": 8},
            {"course": "CS61B", "title": "伯克利 数据结构 (Java)",
             "why": "经典数据结构与算法实现", "weeks": 10},
            {"course": "CS169", "title": "伯克利 软件工程",
             "why": "敏捷/Rails/SaaS 全流程", "weeks": 8},
            {"course": "MIT6.031", "title": "MIT 软件构造",
             "why": "用类型与不变量写出可靠代码", "weeks": 10},
            {"course": "CS144", "title": "Stanford 计算机网络",
             "why": "手写 TCP, 理解协议栈", "weeks": 8},
            {"course": "topdown", "title": "计算机网络 自顶向下",
             "why": "应用层视角补全", "weeks": 8},
        ],
    },
    "theory": {
        "name": "理论/算法方向",
        "goal": "扎实的算法与理论计算机科学功底",
        "difficulty": "数学硬核",
        "steps": [
            {"course": "CS70", "title": "伯克利 离散数学与概率",
             "why": "CS 理论的语言", "weeks": 10},
            {"course": "CS170", "title": "伯克利 高效算法",
             "why": "算法设计与复杂度", "weeks": 10},
            {"course": "CS161", "title": "伯克利 数据结构",
             "why": "工程化算法实现", "weeks": 8},
            {"course": "Princeton-Algorithm", "title": "普林斯顿 算法",
             "why": "Sedgewick 经典, Java 实现", "weeks": 10},
            {"course": "CS168", "title": "伯克利 网络算法",
             "why": "互联网背后的算法", "weeks": 8},
        ],
    },
    "graphics": {
        "name": "图形学方向",
        "goal": "光栅化/光线追踪/PBR 全栈",
        "difficulty": "数学密集",
        "steps": [
            {"course": "线性代数", "title": "数学准备", "why": "变换与投影", "weeks": 6},
            {"course": "GAMES101", "title": "闫令琪 图形学入门",
             "why": "光栅化与光线追踪, 国人神课", "weeks": 8},
            {"course": "15462", "title": "CMU 图形学",
             "why": "动画与物理仿真", "weeks": 10},
            {"course": "GAMES202", "title": "实时高质量渲染",
             "why": "PBR 与阴影", "weeks": 8},
            {"course": "PBR", "title": "Physically Based Rendering",
             "why": "工业级离线渲染器", "weeks": 12},
        ],
    },
}


def render_md(track_id: str, track: dict) -> str:
    lines = [f"# {track['name']}", ""]
    lines.append(f"> **目标**: {track['goal']}  ")
    lines.append(f"> **难度**: {track['difficulty']}  ")
    total = sum(s["weeks"] for s in track["steps"])
    lines.append(f"> **预估**: 约 {total} 周 ({total//4}-{total//3} 个月)")
    lines.append("")
    lines.append("| # | 课程 | 标题 | 为什么学 | 周数 |")
    lines.append("|---|------|------|---------|------|")
    for i, s in enumerate(track["steps"], 1):
        lines.append(f"| {i} | `{s['course']}` | {s['title']} | {s['why']} | {s['weeks']} |")
    lines.append("")
    lines.append("## 学习路线图")
    lines.append("")
    lines.append("```mermaid")
    lines.append("graph LR")
    prev = None
    for s in track["steps"]:
        nid = s["course"].replace(".", "_").replace(" ", "_")
        label = s["course"].replace('"', "'")
        lines.append(f'    {nid}["{label}<br/><sub>{s["weeks"]}周</sub>"]')
        if prev:
            lines.append(f"    {prev} --> {nid}")
        prev = nid
    lines.append("```")
    lines.append("")
    lines.append("## 课程资料位置")
    lines.append("")
    lines.append("用统一检索查找: `python3 tools/ask.py \"{track['steps'][0]['course']}\" --no-llm`")
    return "\n".join(lines) + "\n"


def build_anki(tracks: dict) -> list[str]:
    """生成 Anki TSV: 正面<TAB>背面<TAB>标签"""
    rows = []
    for tid, t in tracks.items():
        rows.append(f"{t['name']}是什么方向\t{t['goal']}\tcsdiy::{tid}")
        for i, s in enumerate(t["steps"], 1):
            front = f"[{t['name']} 第{i}步] {s['course']} 是什么?"
            back = f"{s['title']}。{s['why']} (约{s['weeks']}周)"
            rows.append(f"{front}\t{back}\tcsdiy::{tid}")
        # 反向: 给描述猜课程
        for s in t["steps"]:
            front = f"哪个课程的核心理念是: {s['why']}?"
            back = f"{s['course']} — {s['title']}"
            rows.append(f"{front}\t{back}\tcsdiy::{tid}::反向")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", help="仅输出指定路径")
    args = ap.parse_args()
    out = Path("paths")
    out.mkdir(exist_ok=True)

    tracks = TRACKS
    if args.track:
        tracks = {args.track: TRACKS[args.track]}

    for tid, t in tracks.items():
        (out / f"{tid}.md").write_text(render_md(tid, t), encoding="utf-8")
        print(f"  ✓ paths/{tid}.md  ({len(t['steps'])} 步)")

    # 汇总 JSON
    all_tracks = {tid: t for tid, t in TRACKS.items()}
    (out / "tracks.json").write_text(
        json.dumps(all_tracks, ensure_ascii=False, indent=2), encoding="utf-8")

    # Anki
    rows = build_anki(TRACKS)
    (out / "anki.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (out / "anki-deck.json").write_text(
        json.dumps({"deck": "csdiy CS 自学", "cards": [
            {"front": r.split("\t")[0], "back": r.split("\t")[1], "tag": r.split("\t")[2]}
            for r in rows]}, ensure_ascii=False, indent=2), encoding="utf-8")

    total_weeks = sum(s["weeks"] for t in TRACKS.values() for s in t["steps"])
    print(f"\n✅ {len(TRACKS)} 条学习路径, 共 {sum(len(t['steps']) for t in TRACKS.values())} "
          f"门课, 累计 {total_weeks} 周")
    print(f"   Anki 闪卡: {len(rows)} 张 -> paths/anki.tsv")


if __name__ == "__main__":
    main()
