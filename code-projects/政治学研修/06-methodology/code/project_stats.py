#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""项目统计脚本：扫描所有 .md 文件，生成规模报告。
纯 Python 标准库。运行：python3 project_stats.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# ROOT 指向 political-studies/

stats = {"files": 0, "chars": 0, "lines": 0}
modules = {}

for dirpath, dirnames, filenames in os.walk(ROOT):
    # 跳过 .git / .opencode
    dirnames[:] = [d for d in dirnames if not d.startswith(".")]
    for f in filenames:
        if f.endswith(".md"):
            fpath = os.path.join(dirpath, f)
            rel = os.path.relpath(fpath, ROOT)
            # 识别所属模块（顶层目录 0X-）
            top = rel.split(os.sep)[0]
            if top.startswith(("0", "1")) and "-" in top:
                mod = top
            elif top == "docs":
                mod = "docs（桥梁）"
            else:
                mod = "其他"
            modules.setdefault(mod, {"files": 0, "chars": 0})
            modules[mod]["files"] += 1
            try:
                with open(fpath, "r", encoding="utf-8") as fh:
                    content = fh.read()
                n = len(content)
                stats["files"] += 1
                stats["chars"] += n
                stats["lines"] += content.count("\n") + 1
                modules[mod]["chars"] += n
            except:
                pass

# 统计 .py 文件
py_count = 0
for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "06-methodology", "code")):
    for f in filenames:
        if f.endswith(".py"):
            py_count += 1

print("=" * 55)
print("政治学研修项目 · 规模统计（自动生成）")
print("=" * 55)
print(f"  Markdown 文件总数：{stats['files']}")
print(f"  总字符数：{stats['chars']:,}（约 {stats['chars']//500:,} 千字）")
print(f"  总行数：{stats['lines']:,}")
print(f"  Python 代码：{py_count} 个")
print()

print("按模块分布：")
for mod in sorted(modules.keys()):
    d = modules[mod]
    pct = d["chars"] / stats["chars"] * 100 if stats["chars"] else 0
    bar = "█" * int(pct / 2)
    print(f"  {mod:35s} {d['files']:3d} 篇  {d['chars']:>7,} 字  {pct:4.1f}% {bar}")

print()
total_kb = stats["chars"] // 1024
print(f"项目总量约 {total_kb} KB（{total_kb/1024:.1f} MB）")
print("=" * 55)
