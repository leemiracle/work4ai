#!/usr/bin/env python3
"""讲透系列链接检查器(带代码围栏跳过)。

用法:python linkcheck.py <目录或文件> [目录或文件 ...]
- 递归收集 .md 文件,提取 markdown 链接 [text](target)
- 跳过代码围栏(``` / ~~~)内的内容,避免代码示例误报
- 只检查相对链接(http/https/mailto/锚点跳过);#片段剥离后校验文件存在
- 输出死链清单,exit 1 若有死链,否则 exit 0
"""
import re
import sys
from pathlib import Path

LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)\s]+)\)')
FENCE_RE = re.compile(r'^\s*(```|~~~)')


def extract_links(text: str):
    """产出非代码围栏区的 (line_no, target) 链接。"""
    links = []
    in_fence = False
    for i, line in enumerate(text.splitlines(), 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for _text, target in LINK_RE.findall(line):
            links.append((i, target))
    return links


def check_file(md: Path, root: Path):
    """返回该文件的死链 [(line, target, 解析目标)]。"""
    dead = []
    try:
        text = md.read_text(encoding='utf-8', errors='replace')
    except OSError as e:
        return [(0, f'<read error: {e}>', '')]
    for line, target in extract_links(text):
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
            continue  # http:, mailto:, etc.
        path_part = target.split('#', 1)[0]
        if not path_part:
            continue  # 纯锚点
        resolved = (md.parent / path_part).resolve()
        if not resolved.exists():
            rel = str(resolved)
            try:
                rel = str(resolved.relative_to(root))
            except ValueError:
                pass
            dead.append((line, target, rel))
    return dead


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    files = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            files.extend(sorted(p.rglob('*.md')))
        elif p.is_file():
            files.append(p)
    root = Path.cwd().resolve()
    total_links = 0
    dead_total = 0
    for md in files:
        text = md.read_text(encoding='utf-8', errors='replace')
        n_links = len(extract_links(text))
        total_links += n_links
        dead = check_file(md, root)
        if dead:
            dead_total += len(dead)
            for line, target, resolved in dead:
                print(f'死链 {md}:{line} -> {target} (解析为 {resolved})')
    print(f'检查 {len(files)} 文件 / {total_links} 链接 / 死链 {dead_total}')
    sys.exit(1 if dead_total else 0)


if __name__ == '__main__':
    main()
