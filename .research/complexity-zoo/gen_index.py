# -*- coding: utf-8 -*-
"""重生成 00-总目与口径.md 的表格段（保留 prose 头到 marker 为止）。"""
import json
from pathlib import Path

ROOT = Path(r"C:\workspace\work4ai")
IDX = ROOT / "讲透数学/讲透计算复杂度/图鉴/00-总目与口径.md"
MARK = "<!-- 表格由 00_zoo_pipeline.py 产物机械生成：id | 类名 | 卷 -->"
VOL = {}
for l, v in [("SYM",1),("A",1),("B",1),("C",2),("D",2),("E",2),("F",3),("G",3),("H",3),
             ("I",3),("K",3),("L",3),("M",4),("N",4),("O",4),("P",5),("Q",5),
             ("R",6),("S",6),("T",6),("U",6),("V",6),("W",6),("X",6),("Y",6),("Z",6)]:
    VOL[l] = v

es = json.loads((ROOT / ".research/complexity-zoo/zoo_parsed.json").read_text(encoding="utf-8"))
rows = ["| id | 类名 | 卷 |", "|----|------|----|"]
for e in es:
    name = e["name"].replace("|", "\\|")
    rows.append(f"| `{e['id']}` | {name} | 卷{VOL[e['letter']]} |")

head = IDX.read_text(encoding="utf-8").split(MARK)[0]
IDX.write_text(head + MARK + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
print("总目行数:", len(rows) - 2)
