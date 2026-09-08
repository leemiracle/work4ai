# -*- coding: utf-8 -*-
"""按卷 dump 词条原文（供蒸馏写作）：python dump.py SYM,A,B"""
import json
import sys
from pathlib import Path

ROOT = Path(r"C:\workspace\work4ai")
es = json.loads((ROOT / ".research/complexity-zoo/zoo_parsed.json").read_text(encoding="utf-8"))
letters = sys.argv[1].split(",")

for l in letters:
    group = [e for e in es if e["letter"] == l]
    print(f"\n{'='*20} 字母 {l}（{len(group)} 条）{'='*20}")
    for e in group:
        b = e["body"]
        if len(b) > 1100:
            b = b[:700] + " ……[中略]…… " + b[-350:]
        print(f"\n###{e['name']} | title: {e['title']} | id: {e['id']} | url: {e['url']}\n{b}")
