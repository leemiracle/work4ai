#!/usr/bin/env python3
"""
L2 费曼闭环批量修复脚本
扫描所有 讲透X/00-*.md 文件，若缺少"费曼回炉记录"段则在末尾插入模板段。
用法：python fix_l2_feynman.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(r"C:\workspace\work4ai")
MARKER = "费曼回炉记录"
TEMPLATE = """

---

## 费曼回炉记录（L2 自检 · 待填充）

> 本段是 L2 质量门的硬约束。挖不出 gap 的章节不算迭代完成。请按 F1-F4 填充：

- **F2 卡壳点**（至少 1 个）：我学这章时卡在 ___。重读后发现 ___。
- **F3 术语翻译**：
  - "___" → ___（用 12 岁能懂的话）
  - "___" → ___
- **F4 回炉**：v1 ___；v2 ___（diff 是什么）。

<!--
元理论引用：故事即世界迭代器-元理论.md §断言 3
L2 不达标 = KL 散度未修复 = 章节在漂移而非迭代
-->
"""


def find_00_files(root: Path):
    """找所有 讲透X/00-*.md（排除讲透公开课 + 排除"讲透笔记-算法经验枢纽"元数据文件）"""
    skip_folders = {"讲透公开课"}
    skip_patterns = ("讲透笔记", "算法经验")
    for folder in root.iterdir():
        if not folder.is_dir() or not folder.name.startswith("讲透"):
            continue
        if folder.name in skip_folders:
            continue
        for f in folder.glob("00-*.md"):
            if any(p in f.name for p in skip_patterns):
                continue
            yield f


def needs_fix(path: Path) -> bool:
    """文件里没有 MARKER 段就需要修复"""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")
    return MARKER not in text and "费曼" not in text and "F2" not in text


def apply_fix(path: Path, dry: bool) -> bool:
    if not needs_fix(path):
        return False
    if dry:
        print(f"[DRY] would fix: {path}")
        return True
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")
    # 去掉末尾空白行后追加
    text = text.rstrip() + TEMPLATE
    path.write_text(text, encoding="utf-8")
    print(f"[FIXED] {path}")
    return True


def main():
    dry = "--dry-run" in sys.argv
    fixed = 0
    total = 0
    for f in find_00_files(ROOT):
        total += 1
        if apply_fix(f, dry):
            fixed += 1
    print(f"\n扫描 {total} 个 00-*.md，{'待修复' if dry else '已修复'} {fixed} 个。")


if __name__ == "__main__":
    main()
