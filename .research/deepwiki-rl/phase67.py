#!/usr/bin/env python3
"""understand Phase 6+7: 组装/归一化/校验/落盘 knowledge-graph.json（两仓）。"""
import json, subprocess, datetime, pathlib, sys

PLUGIN = "~/.understand-anything-plugin"
FILE_LEVEL = {"file", "config", "document", "service", "pipeline", "table", "schema", "resource", "endpoint"}
PREFIXES = ("file:", "config:", "document:", "service:", "pipeline:", "table:", "schema:", "resource:", "endpoint:")

def fix_ids(ids):
    out = []
    for i in ids:
        if isinstance(i, dict) and "id" in i:
            i = i["id"]
        if not isinstance(i, str):
            continue
        if not i.startswith(PREFIXES):
            i = "file:" + i
        out.append(i)
    return out

for repo, commit in [("torchrl", "3b6b5b9c1b326fb76eaba93d2ea3ebaba7c76644"),
                     ("cleanrl", "fe8d8a03c41a7ef5b523e2e354bd01c363e786bb")]:
    R = f"~/ai/{repo}"
    IA = f"{R}/.understand-anything/intermediate"
    g = json.load(open(f"{IA}/assembled-graph.json"))
    scan = json.load(open(f"{IA}/scan-result.json"))
    layers_raw = json.load(open(f"{IA}/layers.json"))
    tour_raw = json.load(open(f"{IA}/tour.json"))
    if isinstance(layers_raw, dict) and "layers" in layers_raw:
        layers_raw = layers_raw["layers"]
    if isinstance(tour_raw, dict) and "steps" in tour_raw:
        tour_raw = tour_raw["steps"]

    node_ids = {n["id"] for n in g["nodes"]}
    # 归一化 layers
    layers = []
    for i, L in enumerate(layers_raw):
        name = L.get("name") or f"layer-{i}"
        lid = L.get("id") or "layer:" + "".join(c if c.isalnum() else "-" for c in name.lower()).replace("--", "-")
        nids = [x for x in fix_ids(L.get("nodeIds", L.get("nodes", []))) if x in node_ids]
        layers.append({"id": lid, "name": name, "description": L.get("description", ""), "nodeIds": nids})
    # 归一化 tour
    tour = []
    for S in tour_raw:
        nids = [x for x in fix_ids(S.get("nodeIds", S.get("nodesToInspect", []))) if x in node_ids]
        if not nids:
            continue
        tour.append({"order": S.get("order", len(tour) + 1), "title": S.get("title", ""),
                     "description": S.get("description", S.get("whyItMatters", "")), "nodeIds": nids})
    tour.sort(key=lambda s: s["order"])
    for i, s in enumerate(tour, 1):
        s["order"] = i

    # 悬垂边清理
    edges = [e for e in g["edges"] if e.get("source") in node_ids and e.get("target") in node_ids]

    graph = {
        "version": "1.0.0",
        "project": {
            "name": scan["name"], "languages": scan["languages"], "frameworks": scan["frameworks"],
            "description": scan["description"],
            "analyzedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "gitCommitHash": commit,
        },
        "nodes": g["nodes"], "edges": edges, "layers": layers, "tour": tour,
    }

    # 校验
    issues = []
    assigned = {}
    for L in layers:
        for nid in L["nodeIds"]:
            if nid in assigned:
                issues.append(f"多层重复 {nid}")
            assigned[nid] = L["id"]
    file_nodes = [n["id"] for n in g["nodes"] if n["type"] in FILE_LEVEL]
    unassigned = [f for f in file_nodes if f not in assigned]
    for f in unassigned:
        issues.append(f"file节点未入层 {f}")
    print(f"[{repo}] nodes={len(g['nodes'])} edges={len(edges)} layers={len(layers)} tour={len(tour)} "
          f"file级={len(file_nodes)} 入层={len(assigned)-len(set(issues) and []) if False else sum(len(l['nodeIds']) for l in layers)} issues={len(issues)}")

    # 未入层修复：塞进最后一个"工程支撑"层
    if unassigned:
        target = layers[-1]
        target["nodeIds"].extend(unassigned)
        print(f"[{repo}] 自动修复：{len(unassigned)} 个未入层节点 → {target['name']}")

    json.dump(graph, open(f"{R}/.understand-anything/knowledge-graph.json", "w"), ensure_ascii=False)

    # 指纹基线
    fp_input = {"projectRoot": R, "sourceFilePaths": [f["path"] for f in scan["files"]], "gitCommitHash": commit}
    json.dump(fp_input, open(f"{IA}/fingerprint-input.json", "w"))
    r = subprocess.run(["node", f"{PLUGIN}/skills/understand/build-fingerprints.mjs", f"{IA}/fingerprint-input.json"],
                       capture_output=True, text=True)
    ok = "Fingerprints baseline:" in r.stdout
    print(f"[{repo}] fingerprints: {'OK' if ok else 'FAIL'} {r.stdout.strip()[-80:]} {r.stderr.strip()[-120:]}")

    # meta.json（仅指纹成功后）
    if ok:
        json.dump({"lastAnalyzedAt": graph["project"]["analyzedAt"], "gitCommitHash": commit,
                   "version": "1.0.0", "analyzedFiles": scan["totalFiles"]},
                  open(f"{R}/.understand-anything/meta.json", "w"))
        # 清理中间文件（保留 scan-result.json）
        for p in pathlib.Path(IA).iterdir():
            if p.name != "scan-result.json":
                (p.unlink() if p.is_file() else [x.unlink() for x in p.rglob("*") if x.is_file()])
                if p.is_dir():
                    p.rmdir()
        pathlib.Path(f"{R}/.understand-anything/tmp").exists() and subprocess.run(["rm", "-rf", f"{R}/.understand-anything/tmp"])
        print(f"[{repo}] meta.json 写入，中间文件已清理")
    else:
        sys.exit(1)
print("ALL DONE")
