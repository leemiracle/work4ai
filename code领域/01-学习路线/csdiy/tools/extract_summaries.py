#!/usr/bin/env python3
"""提取所有资源文件的章节级内容摘要（每章前8行核心内容）"""
import re, sys
from pathlib import Path

def extract_sections(filepath: Path):
    """提取文件的每个 ## 章节标题 + 前8行非空核心内容"""
    content = filepath.read_text(encoding='utf-8', errors='replace')
    lines = content.split('\n')
    results = []
    current_title = None
    buffer = []
    in_code = False

    for line in lines:
        if line.strip().startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.startswith('## ') and not line.startswith('###'):
            if current_title and buffer:
                results.append((current_title, buffer[:8]))
            current_title = line.lstrip('# ').strip()
            buffer = []
        elif line.startswith('### '):
            sub = line.lstrip('# ').strip()
            buffer.append(f"  ↳ {sub}")
        elif current_title and line.strip():
            # 去掉 markdown 格式符号，保留纯文本
            clean = re.sub(r'[`*_>]', '', line.strip())
            if clean and len(clean) > 2:
                buffer.append(clean)
    if current_title and buffer:
        results.append((current_title, buffer[:8]))
    return results

dirs = ['notes', 'cheatsheets', 'source-reading', 'labs']
total_sections = 0
for d in dirs:
    dp = Path(d)
    if not dp.exists():
        continue
    for fp in sorted(dp.glob('*.md')):
        print(f"\n{'='*70}")
        print(f"📁 {fp}")
        print(f"{'='*70}")
        sections = extract_sections(fp)
        for title, lines in sections:
            total_sections += 1
            print(f"\n  ▶ {title}")
            for l in lines:
                print(f"    {l}")

print(f"\n\n{'='*70}")
print(f"总计：{total_sections} 个章节")
