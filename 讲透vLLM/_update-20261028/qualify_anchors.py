#!/usr/bin/env python3
"""锚自动升格：把解析失败的相对路径锚（NO_FILE）在唯一前缀命中时改写为全路径。
歧义（多候选/零候选）不改写，逐条上报供人工裁定。
用法: python3 qualify_anchors.py <doc.md>
"""
import re, sys, os, subprocess

REPO = "/usr-data/data2/repos/pytorch-landscape/repos/vllm"
PREFIXES = ["", "vllm/", "vllm/entrypoints/", "vllm/entrypoints/launchers/",
            "vllm/entrypoints/launchers/api_server/", "vllm/entrypoints/cli/",
            "vllm/entrypoints/launchers/utils/", "vllm/snapshot/", "vllm/parser/",
            "vllm/v1/", "rust/", "rust/src/server/src/"]
FULL = re.compile(r"((?:[A-Za-z0-9_.\-]+/)*[A-Za-z0-9_.\-]+\.(?:py|rs|c|cc|cpp|cu|h|hpp|toml|json|md)):(\d{1,5})")

def main():
    doc = sys.argv[1]
    text = open(doc, encoding="utf-8").read()
    rels = sorted({m.group(1) for m in FULL.finditer(text)})
    fixed, ambiguous, missing = [], [], []
    for rel in rels:
        cands = [p + rel for p in PREFIXES if os.path.isfile(os.path.join(REPO, p + rel))]
        if len(cands) == 2 and cands[0] == rel:  # as-is + 一个前缀命中
            cand = cands[1]
            new = re.sub(rf"(?<![/\w]){re.escape(rel)}:", cand + ":", text)
            if new != text:
                fixed.append((rel, cand)); text = new
        elif len(cands) == 1 and cands[0] != rel:
            new = re.sub(rf"(?<![/\w]){re.escape(rel)}:", cands[0] + ":", text)
            if new != text:
                fixed.append((rel, cands[0])); text = new
        elif len(cands) > 1 and not os.path.isfile(os.path.join(REPO, rel)):
            ambiguous.append((rel, cands))
        elif not cands:
            missing.append(rel)
    open(doc, "w", encoding="utf-8").write(text)
    print(f"fixed {len(fixed)}:")
    for r, c in fixed: print(f"  {r} → {c}")
    if ambiguous:
        print(f"AMBIGUOUS {len(ambiguous)}:")
        for r, c in ambiguous: print(f"  {r} → {c}")
    if missing:
        print(f"MISSING {len(missing)}: {missing}")

if __name__ == "__main__":
    main()
