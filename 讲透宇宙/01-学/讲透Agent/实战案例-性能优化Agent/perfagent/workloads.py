"""perfagent.workloads — 负载注册表。

5 个负载刻意覆盖三种瓶颈形态（诊断层要有东西可分类）：
  matmul-64    → latency/sync-bound（小算子，线程同步开销主导，预期 thread-adverse）
  matmul-512   → compute-bound（BLAS 峰值区）
  matmul-2048  → compute-bound（重负载）
  memcopy-256M → memory-bound（纯带宽）
  ewise-32M    → memory-bound（numpy 逐元素单线程，线程不敏感）
"""
import os
import zlib
import numpy as np


def _cheap_key(inputs):
    """内容指纹键（cheat_content 用）：形状+首尾元素。真实作弊会用完整哈希，取朴素版。"""
    return ";".join(f"{a.shape}|{a.flat[0]!r}|{a.flat[-1]!r}|{a.dtype}" for a in inputs)


def stable_seed(*parts) -> int:
    """跨进程确定性种子（不能用 hash()——PYTHONHASHSEED 每进程随机）。"""
    return zlib.crc32(":".join(str(p) for p in parts).encode()) % (2**31)


SPECS = {
    "matmul-64":    dict(kind="matmul", n=64,        inner=400, samples=5, flops=2 * 64**3),
    "matmul-512":   dict(kind="matmul", n=512,       inner=4,   samples=5, flops=2 * 512**3),
    "matmul-2048":  dict(kind="matmul", n=2048,      inner=1,   samples=5, flops=2 * 2048**3),
    "memcopy-256M": dict(kind="memcopy", mb=256,     inner=3,   samples=5, flops=0),
    "ewise-32M":    dict(kind="ewise", n=32_000_000, inner=3,   samples=5, flops=3 * 32_000_000),
    # transformers 真框架负载：BertModel from_config（随机权重，零下载；真 tokenize→embed→
    # 4 层 attention 前向）。重模型（Qwen2.5-0.5B @ ~/ai/models/）因子进程
    # 每次加载成本过高不入注册表，接法见 06 卡 §Qwen。
    "bert4-256-fw": dict(kind="bert", layers=4, hidden=256, seq=128, batch=8,
                         inner=2, samples=3,
                         flops=2 * 8 * 128 * 256 * 256 * 4 * 4),
    # 真 LLM 前向负载（常驻 server 模式：runner 子进程模式加载 ~15s 不可接受）。
    # kind="qwen" 的测量不走 runner.py，走 campaign 内的 ResidentServer。
    "qwen05b-fw": dict(kind="qwen", seq=128, batch=4, inner=1, samples=3,
                       flops=0),   # flops 待 profile 实测填写（0.5B 单前向）
}


def gen(spec, seed):
    rng = np.random.default_rng(seed)
    k = spec["kind"]
    if k == "matmul":
        n = spec["n"]
        return [rng.standard_normal((n, n)), rng.standard_normal((n, n))]
    if k == "memcopy":
        return [rng.standard_normal(spec["mb"] * 2**17)]      # mb MB 的 float64
    if k == "ewise":
        n = spec["n"]
        return [rng.standard_normal(n), rng.standard_normal(n)]
    if k == "bert":
        # input_ids / attention_mask（int64）——真框架输入格式
        v = spec["vocab"] if "vocab" in spec else 30522
        return [rng.integers(0, v, (spec["batch"], spec["seq"]), dtype=np.int64),
                np.ones((spec["batch"], spec["seq"]), dtype=np.int64)]
    raise ValueError(k)


_BERT = {}   # 子进程内惰性单例（构建 ~1s，进程生命周期内复用）


def _compute(k, inputs):
    if k == "matmul":
        return inputs[0] @ inputs[1]
    if k == "memcopy":
        return inputs[0].copy()
    if k == "ewise":
        return inputs[0] * 1.0001 + inputs[1]
    if k == "bert":
        import torch  # 惰性 import：非 bert 负载不付 torch 启动成本
        if "m" not in _BERT:
            from transformers import BertConfig, BertModel
            # 铁律：随机权重负载必须钉种子——否则每个子进程权重不同，
            # 跨进程指纹比对必然 mismatch，裁判自己就成了随机源
            # （2026-08-24 v2 实测教训：threads 1/2 全 INVALID 的根因）
            torch.manual_seed(20260824)
            cfg = BertConfig(vocab_size=30522, hidden_size=_spec_bert["hidden"],
                             num_hidden_layers=_spec_bert["layers"],
                             num_attention_heads=4, intermediate_size=1024)
            torch.set_num_threads(int(__import__("os").environ.get(
                "OMP_NUM_THREADS", "0") or "0") or (os.cpu_count() or 1))
            _BERT["m"] = BertModel(cfg).eval()
        with torch.no_grad():
            out = _BERT["m"](
                input_ids=torch.from_numpy(inputs[0]),
                attention_mask=torch.from_numpy(inputs[1]))
        return out.last_hidden_state.numpy()
    raise ValueError(k)


_spec_bert = {}   # 由 run_op 注入（避免改 _compute 签名）


def run_op(spec, inputs, impl="ref", cache=None):
    """impl ∈ ref | cheat_content | cheat_ptr：
    cheat_content 键=输入内容指纹（内容扰动可破）
    cheat_ptr    键=(data_ptr, shape)（对象复用即命中——复刻 SOL-ExecBench issue#15
                 的 pointer-key 思路；对象轮换防御可破）"""
    if impl != "ref" and cache is not None:
        if impl == "cheat_content":
            key = _cheap_key(inputs)
        else:
            key = ";".join(f"{id(a)}|{a.__array_interface__['data'][0]}|{a.shape}"
                           for a in inputs)   # id+数据指针+形状（numpy 无 data_ptr，用 array_interface）
        if key in cache:
            return cache[key]
        if spec["kind"] == "bert":
            _spec_bert.update(spec)
        out = _compute(spec["kind"], inputs)
        cache[key] = out
        return out
    if spec["kind"] == "bert":
        _spec_bert.update(spec)
    return _compute(spec["kind"], inputs)


def fingerprint(a):
    a = np.asarray(a)
    return [float(a.sum()), float(a.mean()), float(a.max()),
            float(np.sqrt((a * a).sum()))]


def fp_close(a, b, rel):
    return len(a) == len(b) and all(
        abs(x - y) <= rel * max(1.0, abs(x), abs(y)) for x, y in zip(a, b))
