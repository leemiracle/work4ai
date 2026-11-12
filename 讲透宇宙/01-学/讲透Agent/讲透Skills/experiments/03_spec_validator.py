# -*- coding: utf-8 -*-
"""
实验 03 — skills-ref validate 的本地复刻（规范合规检查器）
对应文档: 讲透Skills/01-规范精读-SKILL.md解剖.md
依据: agentskills.io/specification 一手字段约束（2026-08-25 核实）

检查项（与官方 skills-ref validate 对齐 + 本站增强）:
  C1 SKILL.md 存在
  C2 frontmatter 可解析且含 name/description
  C3 name: 1-64字符 / [a-z0-9-] / 不首尾连字符 / 无连续连字符
  C4 name == 父目录名
  C5 description: 1-1024 字符非空
  C6 正文 ≤500 行（规范建议,警告级）
  本站增强 C7: description ≤250 字符（CC 实现的截断线,警告级）

跑法: python3 -u 03_spec_validator.py [目录]（默认扫本机两套 skills 目录）
"""
import os, re, sys
from pathlib import Path

def validate_skill_dir(dirpath: str):
    errs, warns = [], []
    d = Path(dirpath)
    f = d / "SKILL.md"
    if not f.is_file():
        return [f"C1: 缺少 SKILL.md"], warns, None
    text = f.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.S)
    if not m:
        return [f"C2: frontmatter 缺失或不可解析"], warns, None
    fm, body = m.groups()
    nm = re.search(r"^name:\s*(.+)$", fm, re.M)
    dm = re.search(r"^description:\s*(.+(?:\n\s+.+)*)$", fm, re.M)
    if not nm: errs.append("C2: 缺必填字段 name")
    if not dm: errs.append("C2: 缺必填字段 description")
    if not nm or not dm: return errs, warns, None
    name, desc = nm.group(1).strip(), re.sub(r"\s+", " ", dm.group(1)).strip()

    if not (1 <= len(name) <= 64): errs.append(f"C3: name 长度 {len(name)} 越界 [1,64]")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        errs.append(f"C3: name '{name}' 含非法字符（只许小写字母/数字/单连字符）")
    if name != d.name: errs.append(f"C4: name '{name}' != 目录名 '{d.name}'")
    if not (1 <= len(desc) <= 1024): errs.append(f"C5: description 长度 {len(desc)} 越界 [1,1024]")

    lines = body.count("\n") + 1
    if lines > 500: warns.append(f"C6: 正文 {lines} 行 > 500 行预算（应拆 references/）")
    if len(desc) > 250: warns.append(f"C7: description {len(desc)} 字符 > CC 实现截断线 250（跨工具发布建议压缩）")
    return errs, warns, (name, desc, lines)

def main():
    roots = sys.argv[1:] or [os.path.expanduser("~/.config/opencode/skills"),
                             os.path.expanduser("~/.agents/skills")]
    total = bad = warned = 0
    for root in roots:
        print(f"\n===== {root} =====")
        subs = sorted(os.listdir(root))
        for sub in subs:
            if sub.startswith(("_", ".")): continue   # 容器/归档目录不是 skill
            p = os.path.join(root, sub)
            if not os.path.isdir(p): continue
            total += 1
            errs, warns, info = validate_skill_dir(p)
            if errs:
                bad += 1
                print(f"  ✗ {sub}")
                for e in errs: print(f"      {e}")
            elif warns:
                warned += 1
                print(f"  ⚠ {sub}: " + "; ".join(warns))
            # 合规的静默通过
    print(f"\n▶ 共 {total} 个 skill 目录: {total-bad-warned} 全绿 / {warned} 警告 / {bad} 违规")
    print("  （C1-C5 = agentskills.io 规范硬约束; C6-C7 = 预算警告）")

if __name__ == "__main__":
    main()
