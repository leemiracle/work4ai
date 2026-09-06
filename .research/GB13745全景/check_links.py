import re, sys, pathlib
root = pathlib.Path("讲透数学")
fams = ["讲透数论","讲透代数学","讲透代数几何","讲透几何学","讲透拓扑学","讲透数理逻辑",
        "讲透计算数学","讲透概率论","讲透数理统计","讲透运筹学","讲透组合数学","讲透离散数学",
        "讲透模糊数学","讲透计算机数学","讲透应用统计数学","讲透数学史"]
targets = [root/"GB-T13745全景.md", root/"数学问题路由.md", root/"README.md"]
targets += [p for fam in fams for p in (root/fam).rglob("*.md")]
bad = []
total = 0
for f in targets:
    try:
        text = f.read_text(encoding="utf-8")
    except Exception as e:
        bad.append(f"{f}: READ-ERROR {e}"); continue
    for m in re.finditer(r"\]\(([^)#\s]+?)(#[^)]*)?\)", text):
        link = m.group(1).strip()
        if link.startswith(("http://","https://","mailto:")): continue
        total += 1
        if not (f.parent / link).resolve().exists():
            bad.append(f"{f.relative_to(root)} -> {link}")
print(f"checked {len(targets)} files, {total} relative links")
print("\n".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
