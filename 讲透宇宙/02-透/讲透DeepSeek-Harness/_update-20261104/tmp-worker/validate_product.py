#!/usr/bin/env python3
"""Validate a product batch file: JSON validity, imports 1:1 vs rescan, no dup ids, no self-edges,
edge endpoints resolvable (in-batch nodes or disk-verified file/class/function paths)."""
import json
import os
import re
import sys

BASE = "~/ai/work4ai/讲透DeepSeek-Harness/_update-20261104"
ROOT = "/usr-data/data2/repos/deepseek-ai/deepseek-harness"

rescan = json.load(open(os.path.join(BASE, "tmp-worker", "imports-rescan-051-060.json")))
batch_files = json.load(open(os.path.join(BASE, "batches", f"batch-{sys.argv[1]}.json")))["files"]
prod = json.load(open(os.path.join(BASE, "products", f"batch-{sys.argv[1]}.json")))

nodes = prod["nodes"]
edges = prod["edges"]
ids = {n["id"] for n in nodes}
errs = []

if len(ids) != len(nodes):
    from collections import Counter
    dup = [k for k, c in Counter(n["id"] for n in nodes).items() if c > 1]
    errs.append(f"duplicate node ids: {dup}")

# every batch file has a file-level node
pref = {"code": "file", "config": "config", "docs": "document"}
for f in batch_files:
    base = os.path.basename(f)
    if base in ("package.json",) or base.startswith("tsconfig") or base.endswith(".config.ts") or base.endswith(".config.js"):
        want = f"config:{f}"
    elif base.endswith(".md"):
        want = f"document:{f}"
    else:
        want = f"file:{f}"
    if want not in ids:
        errs.append(f"missing file-level node: {want}")

# imports 1:1
expected = 0
expected_list = []
for f in batch_files:
    r = rescan.get(f, {})
    for i in r.get("imports", []):
        expected += 1
        expected_list.append((f"file:{f}", f"file:{i['resolved']}"))
actual = [(e["source"], e["target"]) for e in edges if e["type"] == "imports"]
if sorted(expected_list) != sorted(actual):
    miss = [x for x in expected_list if x not in actual]
    extra = [x for x in actual if x not in expected_list]
    errs.append(f"imports mismatch: missing={miss} extra={extra}")
else:
    print(f"imports 1:1 OK ({len(actual)} edges)")

# no self edges
for e in edges:
    if e["source"] == e["target"]:
        errs.append(f"self edge: {e}")

# edge endpoint resolvability
def endpoint_ok(ep):
    if ep in ids:
        return True
    m = re.match(r"^(file|config|document|service|pipeline|schema|resource):(.+)$", ep)
    if m:
        return os.path.exists(os.path.join(ROOT, m.group(2)))
    m = re.match(r"^(function|class):(.+):([^:]+)$", ep)
    if m:
        return os.path.exists(os.path.join(ROOT, m.group(2)))
    return False

for e in edges:
    for end in (e["source"], e["target"]):
        if not endpoint_ok(end):
            errs.append(f"unresolvable endpoint {end} in edge {e['type']}")

# required node fields
for n in nodes:
    for field in ("id", "type", "name", "summary", "tags", "complexity"):
        if field not in n or n[field] in (None, "", []):
            errs.append(f"node missing {field}: {n.get('id')}")
    if n["type"] in ("function", "class") and "lineRange" not in n:
        errs.append(f"missing lineRange: {n['id']}")
    if not isinstance(n.get("lineRange", []), list) and "lineRange" in n:
        errs.append(f"lineRange not list: {n['id']}")

types = {}
for n in nodes:
    types[n["type"]] = types.get(n["type"], 0) + 1
ec = {}
for e in edges:
    ec[e["type"]] = ec.get(e["type"], 0) + 1
print(f"nodes={len(nodes)} {types}")
print(f"edges={len(edges)} {ec}")
if errs:
    print("ERRORS:")
    for x in errs:
        print(" -", x)
    sys.exit(1)
print("VALID")
