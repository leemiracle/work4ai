#!/usr/bin/env python3
"""从一个 markdown 文件里提取所有 ```mermaid 块到独立 .mmd 文件。"""
import re
import sys
from pathlib import Path


def extract(md_path: str, out_dir: str):
    text = Path(md_path).read_text(encoding="utf-8")
    blocks = re.findall(r"```mermaid\n(.*?)```", text, re.DOTALL)
    stem = Path(md_path).stem
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    files = []
    for i, b in enumerate(blocks, 1):
        f = out / f"{stem}-{i:02d}.mmd"
        f.write_text(b, encoding="utf-8")
        files.append(f)
    return files


if __name__ == "__main__":
    md = sys.argv[1]
    out_dir = sys.argv[2]
    fs = extract(md, out_dir)
    for f in fs:
        print(f)
