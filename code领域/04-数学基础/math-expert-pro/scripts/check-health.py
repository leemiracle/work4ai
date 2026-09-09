#!/usr/bin/env python3
# math-expert-pro 知识库健康体检
# 用法: python3 scripts/check-health.py [--strict]
#   --strict: 把外部兄弟项目引用与作者速记标签也计为失败（CI 用）
#
# 检测项:
#   A. 真正断裂的内部 markdown 链接（核心，必须 0）
#   B. 外部兄弟项目引用（../math-expert ../书籍 ../../数学经典 等，环境依赖）
#   C. 作者速记标签 [显示文本](主题标签)（约定写法，非真链接）
#   D. 断裂的图片引用
#   E. 空文件 / 极小占位文件
# 退出码: A==0 则 0（成功），否则 1。
from __future__ import annotations
import re, sys, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK_RE = re.compile(r'(?<!\!)\[([^\]]*)\]\(([^)\s]+)\)')
IMG_RE  = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)\)')

# 作者速记标签判定: 真链接几乎总以扩展名(.md/.py/.png…)结尾或指向目录(以/结尾)。
# 既无扩展名又非目录的，视为作者的主题/隐喻标签（如 复用 / 双射=无损变换/置换矩阵）。
def is_shorthand(target: str) -> bool:
    p = target.split('#')[0].split(' ')[0]
    return ('.' not in p) and (not p.endswith('/'))

# 化学/数学单字符假阳性: [A] [X] [A0] 等
def is_formula_text(text: str) -> bool:
    return bool(re.fullmatch(r'[A-Z]\d?', text) or re.fullmatch(r'[A-Za-z]', text))

def strip_math(s: str) -> str:
    s = re.sub(r'\$\$.*?\$\$', ' ', s, flags=re.S)          # 块级公式
    s = re.sub(r'(?<!\\)\$[^\n$]*?\$(?!\d)', ' ', s)         # 行内公式
    return s

def main() -> int:
    ap = argparse.ArgumentParser(description='math-expert-pro health check')
    ap.add_argument('--strict', action='store_true', help='外部引用与速记标签也计为失败')
    args = ap.parse_args()

    broken, external, shorthand, broken_img, tiny = [], [], [], [], []
    nfiles = nlinks = 0
    for md in ROOT.rglob('*.md'):
        if '.opencode' in md.parts or 'scripts' in md.parts: continue
        nfiles += 1
        base = md.parent
        rel = str(md.relative_to(ROOT))
        if md.stat().st_size < 150 and rel != 'NOTES_TEMPLATE.md':
            tiny.append(rel)
        raw = md.read_text(encoding='utf-8', errors='replace')
        txt = strip_math(raw)
        for m in LINK_RE.finditer(txt):
            text = m.group(1).strip(); target = m.group(2).strip()
            p = target.split('#')[0].split(' ')[0]
            if not p or p.startswith(('http://', 'https://', 'mailto:', '#')): continue
            if is_formula_text(text): continue
            nlinks += 1
            try: resolved = (base / p).resolve()
            except Exception:
                broken.append((rel, target)); continue
            try: resolved.relative_to(ROOT); inside = True
            except ValueError: inside = False
            if not inside:
                external.append((rel, target))
            elif resolved.exists():
                continue
            elif is_shorthand(p):
                shorthand.append((rel, target))
            else:
                broken.append((rel, target))
        for m in IMG_RE.finditer(raw):
            target = m.group(2).strip().split(' ')[0]
            if target.startswith(('http', 'data:')): continue
            if not (base / target).exists():
                broken_img.append((rel, target))

    def summarise(title, items, fail=False):
        print(f"\n{'❌' if fail else 'ℹ️'} {title}: {len(items)}")
        seen = {}
        for rel, t in items: seen.setdefault(t, []).append(rel)
        for t, fs in sorted(seen.items(), key=lambda x: -len(x[1]))[:15]:
            print(f"   [{len(fs)}x] {t}  <- {fs[0]}")

    print(f"扫描 {nfiles} 个 md 文件 / {nlinks} 条内部链接")
    summarise('(A) 断裂的内部链接', broken, fail=True)
    summarise('(B) 外部兄弟项目引用（环境依赖）', external)
    summarise('(C) 作者速记标签（约定写法）', shorthand)
    summarise('(D) 断裂图片引用', broken_img, fail=True)
    print(f"\nℹ️ (E) 极小占位文件: {len(tiny)}")
    for r in tiny[:15]: print(f"   {r}")

    fail = bool(broken) or bool(broken_img) or (args.strict and (external or shorthand))
    print('\n' + ('='*50))
    print('✅ 健康检查通过：无断裂内部链接/图片。' if not fail
          else '❌ 健康检查失败：存在断裂内部链接或图片。')
    return 1 if fail else 0

if __name__ == '__main__':
    sys.exit(main())
