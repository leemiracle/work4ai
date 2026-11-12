"""perfagent.memory — 记忆层：win/trap 库（results.jsonl）+ 画像卡（cards.json）。

跨 session warm-start：搜索前查历史已测 key，跳过（KernelBlaster
optimization_database.json 模式）。trap（invalid/revert 行）作为 LLM 提议器的
负例上下文回灌。
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "..", "experiments", "perfagent")
RESULTS = os.path.join(STATE, "results.jsonl")
CARDS = os.path.join(STATE, "cards.json")


def _ensure():
    os.makedirs(STATE, exist_ok=True)


def cfg_key(cfg):
    return json.dumps({k: cfg.get(k) for k in ("threads", "affinity", "impl")},
                      sort_keys=True)


def append_row(row):
    _ensure()
    with open(RESULTS, "a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_rows():
    if not os.path.exists(RESULTS):
        return []
    with open(RESULTS) as f:
        return [json.loads(l) for l in f if l.strip()]


def seen_keys(workload):
    return {cfg_key(r["cfg"]) for r in load_rows()
            if r.get("workload") == workload and r.get("verdict") not in ("REJECT",)}


def traps_for(workload, n=5):
    rows = [r for r in load_rows() if r.get("workload") == workload
            and r.get("verdict") in ("invalid", "revert", "measure_error")]
    return [{"cfg": r["cfg"], "verdict": r["verdict"],
             "why": r.get("why") or r.get("error", "")[:80]} for r in rows[-n:]]


def save_cards(data):
    _ensure()
    with open(CARDS, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def load_cards():
    if not os.path.exists(CARDS):
        return None
    with open(CARDS) as f:
        return json.load(f)
