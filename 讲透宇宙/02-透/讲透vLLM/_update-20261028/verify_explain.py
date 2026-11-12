#!/usr/bin/env python3
"""explain 13 篇 + ONBOARDING 终验 v2：
- 全路径锚 `path/file.py:123`：解析（含 basename 唯一消歧）+ 行号界内校验
- 缩写锚 `:123`（全路径锚消耗后的余文，形如（:3422/:3452）或 @:2229-2295）：按篇主文件界内校验
- 字数=不计空格总字符（钉版口径）
用法: python3 verify_explain.py [--sample N] [--only 名字片段]
"""
import re, sys, os, subprocess, random

REPO = "/usr-data/data2/repos/pytorch-landscape/repos/vllm"
EXPLAIN = "~/ai/work4ai/讲透vLLM/explain"
ONBOARD = "~/ai/work4ai/讲透vLLM/onboarding/ONBOARDING.md"

# 篇名 → 主文件（缩写锚归位目标）
PIECES = {
    "vllm-v1-engine-async_llm.md": "vllm/v1/engine/async_llm.py",
    "vllm-v1-engine-core.md": "vllm/v1/engine/core.py",
    "vllm-v1-core-sched-scheduler.md": "vllm/v1/core/sched/scheduler.py",
    "vllm-v1-core-kv_cache_manager.md": "vllm/v1/core/kv_cache_manager.py",
    "vllm-engine-arg_utils.md": "vllm/engine/arg_utils.py",
    "vllm-v1-worker-gpu_model_runner.md": "vllm/v1/worker/gpu_model_runner.py",
    "vllm-v1-worker-gpu_input_batch.md": "vllm/v1/worker/gpu_input_batch.py",
    "vllm-v1-worker-gpu_worker.md": "vllm/v1/worker/gpu_worker.py",
    "vllm-v1-attention-backends-flash_attn.md": "vllm/v1/attention/backends/flash_attn.py",
    "vllm-config-vllm.md": "vllm/config/vllm.py",
    "vllm-distributed-parallel_state.md": "vllm/distributed/parallel_state.py",
    "vllm-entrypoints-llm.md": "vllm/entrypoints/llm.py",
    "vllm-model_executor-models-llama.md": "vllm/model_executor/models/llama.py",
    # Task8 新子系统篇（2026-11-01 追加）
    "vllm-parser-abstract_parser.md": "vllm/parser/abstract_parser.py",
    "vllm-v1-kv_cache_interface.md": "vllm/v1/kv_cache_interface.py",
    "vllm-snapshot.md": "vllm/snapshot/runtime.py",
    "rust-server-lib.md": "rust/src/server/src/lib.rs",
    "vllm-entrypoints-launchers.md": "vllm/entrypoints/launchers/launcher.py",
    "vllm-entrypoints-openai-api_server.md": "vllm/entrypoints/openai/api_server.py",
}
FULL = re.compile(r"((?:[A-Za-z0-9_.\-]+/)*[A-Za-z0-9_.\-]+\.(?:py|rs|c|cc|cpp|cu|h|hpp|toml|json)):(\d{1,5})(?:-(\d{1,5}))?")
SHORT = re.compile(r"(?<![A-Za-z0-9_.#/]):(\d{1,5})(?:-(\d{1,5}))?(?![\d/])")  # / 排除 URL 端口
PAREN = re.compile(r"（(\d{1,5})(?:-(\d{1,5}))?(\s*行)?）")  # g3 有"行"且无区间=文件长度引用，非锚

_index = None
def build_index():
    global _index
    _index = {}
    out = subprocess.run(["git", "-C", REPO, "ls-files"], capture_output=True, text=True).stdout
    for line in out.splitlines():
        _index.setdefault(os.path.basename(line), []).append(line)
    return _index

def resolve(rel):
    p = os.path.join(REPO, rel)
    if os.path.isfile(p):
        return rel
    idx = _index or build_index()
    c = idx.get(os.path.basename(rel))
    return c[0] if c and len(c) == 1 else None

_lines = {}
def flines(rel):
    if rel not in _lines:
        with open(os.path.join(REPO, rel), errors="replace") as f:
            _lines[rel] = sum(1 for _ in f)
    return _lines[rel]

def check_doc(path, main_file, per_sample=0):
    text = open(path, encoding="utf-8").read()
    chars = len(re.sub(r"\s", "", text))
    bad, full_a, short_a = [], 0, 0
    consumed = []
    for m in FULL.finditer(text):
        consumed.append(m.span())
        rel = resolve(m.group(1))
        if rel is None:
            bad.append((m.group(0), "NO_FILE")); continue
        n = flines(rel)
        hi = int(m.group(3) or m.group(2))
        if int(m.group(2)) > n or hi > n:
            bad.append((m.group(0), f"OOB>{n}"))
        full_a += 1
    rest, cut = "", 0
    for s, e in sorted(consumed):
        rest += text[cut:s]; cut = e
    rest += text[cut:]
    main_n = flines(main_file)
    for m in SHORT.finditer(rest):
        short_a += 1
        hi = int(m.group(2) or m.group(1))
        if int(m.group(1)) > main_n or hi > main_n:
            bad.append(("主文件:" + m.group(0), f"OOB>{main_n}"))
    for m in PAREN.finditer(rest):
        if m.group(3) and not m.group(2):  # （NNN 行）=文件长度引用，跳过
            continue
        short_a += 1
        hi = int(m.group(2) or m.group(1))
        if int(m.group(1)) > main_n or hi > main_n:
            bad.append(("主文件:" + m.group(0), f"OOB>{main_n}"))
    return chars, full_a, short_a, bad

def main():
    args = sys.argv[1:]
    sample = int(args[args.index("--sample") + 1]) if "--sample" in args else 0
    only = args[args.index("--only") + 1] if "--only" in args else ""
    ok, rows = True, []
    for name, mainf in PIECES.items():
        if only and only not in name: continue
        p = os.path.join(EXPLAIN, name)
        if not os.path.isfile(p):
            print(f"{name:48s} MISSING"); ok = False; continue
        c, fa, sa, bad = check_doc(p, mainf, sample)
        if bad: ok = False
        rows.append((name, c, fa, sa, bad))
    if (not only) and os.path.isfile(ONBOARD):
        c, fa, sa, bad = check_doc(ONBOARD, "vllm/config/vllm.py", sample)  # ONBOARDING 缩写锚不归位单一主文件，仅界内参考
        if bad: ok = False
        rows.append(("onboarding/ONBOARDING.md", c, fa, sa, bad))
    print(f"{'doc':48s} {'chars':>6s} {'full':>5s} {'short':>6s} bad")
    for name, c, fa, sa, bad in rows:
        flag = f"  ⚠ {bad[:8]}{'…' if len(bad) > 8 else ''}" if bad else ""
        print(f"{name:48s} {c:6d} {fa:5d} {sa:6d} {len(bad)}{flag}")
    print("VERDICT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
