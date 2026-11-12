#!/usr/bin/env python3
"""Prepare per-batch extract-structure inputs and run the bundled script for batches 091-100."""
import json
import os
import re
import subprocess
import sys

ROOT = "/usr-data/data2/repos/deepseek-ai/deepseek-harness"
BASE = "~/ai/work4ai/讲透DeepSeek-Harness/_update-20261104"
SKILL = "/home/lwz/.understand-anything-plugin/skills/understand/extract-structure.mjs"
TMP = os.path.join(BASE, "tmp-worker")

LANG = {
    ".ts": "typescript", ".tsx": "tsx", ".mts": "typescript", ".cts": "typescript",
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".md": "markdown", ".json": "json", ".yaml": "yaml", ".yml": "yaml",
    ".sh": "shellscript", ".py": "python",
}


def file_category(path):
    base = os.path.basename(path)
    if base in ("package.json", "tsconfig.json") or re.match(r"tsconfig\.", base) or base.endswith(".yml") or base.endswith(".yaml"):
        return "config"
    if base.endswith(".md"):
        return "docs"
    if base.endswith(".ts") or base.endswith(".tsx"):
        return "code"
    if base.endswith(".json"):
        return "data"
    return "data"


def main():
    for n in range(91, 101):
        b = json.load(open(os.path.join(BASE, "batches", f"batch-{n:03d}.json")))
        batch_files = []
        for f in b["files"]:
            p = os.path.join(ROOT, f)
            size = 0
            if os.path.isfile(p):
                with open(p, encoding="utf-8", errors="replace") as fh:
                    size = sum(1 for _ in fh)
            ext = os.path.splitext(f)[1]
            batch_files.append({
                "path": f,
                "language": LANG.get(ext, "text"),
                "sizeLines": size,
                "fileCategory": file_category(f),
            })
        inp = os.path.join(TMP, f"ua-input-{n}.json")
        outp = os.path.join(TMP, f"ua-extract-{n}.json")
        json.dump({"projectRoot": ROOT, "batchFiles": batch_files, "batchImportData": {}}, open(inp, "w"))
        r = subprocess.run(["node", SKILL, inp, outp], capture_output=True, text=True, timeout=300)
        status = "OK" if r.returncode == 0 else f"FAIL({r.returncode})"
        detail = ""
        if r.returncode != 0:
            detail = r.stderr[-500:]
        print(f"batch {n}: {status} {detail}")


if __name__ == "__main__":
    main()
