#!/usr/bin/env python3
"""Worker-side import rescanner for batches 091-100 (deepseek-harness update 20261104).

Multi-line-aware regex rescan + disk verification per dispatch template clause 2.
Rules:
  a. @deepseek-ai/dsh-* imports -> packages-map.json; package root -> <dir>/src/index.ts;
     subpaths resolved via package.json exports semantics, then src/ path candidates, disk-verified.
  b. Relative imports: strip .js -> .ts; try .ts/.tsx/index.ts/index.tsx/.json/.js.
  c. import type + dynamic import() are real deps -> emit edge.
Vendored/external (cordis, schemastery, cosmokit, all other npm) -> skipped, no edge.
"""
import json
import os
import re
import sys
from collections import OrderedDict

ROOT = "/usr-data/data2/repos/deepseek-ai/deepseek-harness"
BASE = "/data/usershare/ai/work4ai/讲透DeepSeek-Harness/_update-20261104"
PKGMAP = json.load(open(os.path.join(BASE, "packages-map.json")))

IMPORT_RE = re.compile(
    r"""(?P<stmt>
        (?:^|[;\n])\s*
        (?:
            import\s+type\s+[^'";]*?\s*from\s*
          | import\s+[^'";]*?\s*from\s*
          | import\s*
          | export\s+(?:type\s+)?[^'";]*?\s*from\s*
        )
        ['"](?P<spec>[^'"]+)['"]
    )""",
    re.S | re.X,
)
DYN_IMPORT_RE = re.compile(r"""(?<![\w$])import\s*\(\s*['"](?P<spec>[^'"]+)['"]\s*\)""")
# also catch `export * from 'x'` (covered by export branch) and bare `export {} from` etc.

EXTERNAL_PREFIXES = ("node:", "vscode")
EXTERNAL_NAMES = {
    "node", "fs", "path", "os", "util", "url", "http", "https", "crypto", "stream",
    "events", "child_process", "worker_threads", "net", "tls", "zlib", "assert",
    "buffer", "querystring", "string_decoder", "timers", "tty", "dns", "dgram",
    "readline", "repl", "vm", "module", "process",
}


def exists(rel):
    return os.path.isfile(os.path.join(ROOT, rel))


def try_candidates(cands):
    for c in cands:
        if exists(c):
            return c
    return None


def resolve_relative(spec, from_file):
    d = os.path.dirname(from_file)
    joined = os.path.normpath(os.path.join(d, spec)).replace(os.sep, "/")
    base = joined
    cands = []
    if base.endswith(".js"):
        cands.append(base[:-3] + ".ts")
    elif base.endswith(".mjs"):
        cands.append(base[:-4] + ".ts")
    cands += [
        base,
        base + ".ts",
        base + ".tsx",
        base + "/index.ts",
        base + "/index.tsx",
        base + ".json",
        base + ".mjs",
        base + ".js",
        base + ".cjs",
        base + ".css",
    ]
    # if literal file exists (e.g. data import with extension)
    return try_candidates(cands)


_exports_cache = {}


def resolve_dsh(spec):
    # spec like @deepseek-ai/dsh-util or @deepseek-ai/dsh-util/sub/path
    parts = spec.split("/")
    pkg = parts[0] + ("/" + parts[1] if len(parts) > 1 and not parts[0].startswith("@") else "")
    if spec.startswith("@deepseek-ai/"):
        # scoped: pkg = first two segments
        pkg = "/".join(parts[:2])
        sub = "/".join(parts[2:])
    else:
        pkg = parts[0]
        sub = "/".join(parts[1:])
    if pkg not in PKGMAP:
        return None, "no-package-map-entry"
    pkgdir = PKGMAP[pkg]
    if not sub:
        cand = try_candidates([pkgdir + "/src/index.ts", pkgdir + "/src/index.tsx"])
        if cand:
            return cand, None
        return None, "pkg-root-index-missing"
    # consult package.json exports
    pj_path = os.path.join(ROOT, pkgdir, "package.json")
    exp = None
    if pj_path in _exports_cache:
        exp = _exports_cache[pj_path]
    elif os.path.isfile(pj_path):
        try:
            pj = json.load(open(pj_path))
            exp = pj.get("exports")
        except Exception:
            exp = None
        _exports_cache[pj_path] = exp
    resolved = None
    if isinstance(exp, dict):
        key = "./" + sub
        val = exp.get(key)
        if isinstance(val, str):
            rel = val
            if rel.startswith("./"):
                rel = rel[2:]
            # exports usually point at src (source maps) or dist; keep only src/ relative to pkgdir
            cand = try_candidates([pkgdir + "/" + rel, pkgdir + "/src/" + sub + ".ts", pkgdir + "/src/" + sub + "/index.ts"])
            resolved = cand
        elif isinstance(val, dict):
            for v in (val.get("types"), val.get("import"), val.get("default")):
                if isinstance(v, str):
                    rel = v[2:] if v.startswith("./") else v
                    cand = try_candidates([pkgdir + "/" + rel, pkgdir + "/src/" + sub + ".ts", pkgdir + "/src/" + sub + "/index.ts"])
                    if cand:
                        resolved = cand
                        break
    if not resolved:
        resolved = try_candidates([
            pkgdir + "/src/" + sub + ".ts",
            pkgdir + "/src/" + sub + ".tsx",
            pkgdir + "/src/" + sub + "/index.ts",
            pkgdir + "/src/" + sub + "/index.tsx",
            pkgdir + "/" + sub + ".ts",
            pkgdir + "/" + sub,
        ])
    if resolved:
        return resolved, None
    return None, "dsh-subpath-unresolved"


def scan_file(rel):
    src_path = os.path.join(ROOT, rel)
    try:
        text = open(src_path, encoding="utf-8", errors="replace").read()
    except OSError:
        return {"error": "unreadable"}
    specs = OrderedDict()
    for m in IMPORT_RE.finditer(text):
        spec = m.group("spec")
        if spec and spec not in specs:
            specs[spec] = "static"
    for m in DYN_IMPORT_RE.finditer(text):
        spec = m.group("spec")
        if spec and spec not in specs:
            specs[spec] = "dynamic"
    out = []
    unresolved = []
    skipped = []
    for spec, kind in specs.items():
        if spec.startswith(".") or spec.startswith("/"):
            r = resolve_relative(spec, rel)
            if r:
                out.append({"spec": spec, "kind": kind, "resolved": r})
            else:
                unresolved.append({"spec": spec, "kind": kind})
        elif spec.startswith(EXTERNAL_PREFIXES) or spec.split("/")[0] in EXTERNAL_NAMES:
            skipped.append({"spec": spec, "reason": "node-builtin"})
        elif spec.startswith("@deepseek-ai/dsh-"):
            r, err = resolve_dsh(spec)
            if r:
                out.append({"spec": spec, "kind": kind, "resolved": r})
            else:
                unresolved.append({"spec": spec, "kind": kind, "error": err})
        else:
            # vendored cordis / cordisjs / npm externals -> external
            skipped.append({"spec": spec, "reason": "external-or-vendored"})
    return {"imports": out, "unresolved": unresolved, "skipped": skipped}


def main():
    result = {}
    for n in range(91, 101):
        b = json.load(open(os.path.join(BASE, "batches", f"batch-{n:03d}.json")))
        for f in b["files"]:
            if f.endswith((".ts", ".tsx")):
                result[f] = scan_file(f)
            else:
                result[f] = {"non_code": True}
    out_path = os.path.join(BASE, "tmp-worker", "imports-rescan-091-100.json")
    json.dump(result, open(out_path, "w"), ensure_ascii=False, indent=1)
    # summary
    total_edges = 0
    total_unres = 0
    for f, r in result.items():
        if "imports" in r:
            total_edges += len(r["imports"])
            total_unres += len(r.get("unresolved", []))
    print(f"files scanned: {sum(1 for r in result.values() if 'imports' in r)}")
    print(f"resolved import edges: {total_edges}")
    print(f"unresolved: {total_unres}")
    for f, r in result.items():
        for u in r.get("unresolved", []):
            print("UNRESOLVED", f, u)
    print("written:", out_path)


if __name__ == "__main__":
    main()
