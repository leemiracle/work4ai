# -*- coding: utf-8 -*-
"""00_smoke.py — 端侧事实记忆 Agent · 第零号摸底实验

回答三个问题（一切设计决策的证据基础）：
  Q1 0.5B 在这台 8 核 CPU 机上到底多快？(tok/s，线程数怎么选)
  Q2 裸模型直接做「事实抽取→JSON」成功率多少？
  Q3 失败模式长什么样？(决定 L1 之后每一级阶梯修什么)

运行：python3 00_smoke.py
预期：~2 分钟内跑完；输出实测报告。
"""
import json
import os
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_PATH = os.path.expanduser("~/ai/models/Qwen2.5-0.5B-Instruct")

# ── 加载 ────────────────────────────────────────────────────────────
t0 = time.time()
tok = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, dtype=torch.float32)
model.eval()
load_s = time.time() - t0
print(f"[env] torch={torch.__version__} threads={torch.get_num_threads()}")
print(f"[load] {load_s:.1f}s  params={model.num_parameters()/1e6:.0f}M")


def gen(messages, max_new_tokens=150, threads=None):
    """单次生成，返回 (文本, tok/s)。threads=None 用全局设置。"""
    if threads is None:
        torch.set_num_threads(os.cpu_count())
    else:
        torch.set_num_threads(threads)
    text = tok.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt")
    t1 = time.time()
    with torch.no_grad():
        out = model.generate(
            **ids, max_new_tokens=max_new_tokens,
            do_sample=False,  # 贪心：可复现，评估实验的底线要求
            pad_token_id=tok.eos_token_id)
    dt = time.time() - t1
    n_new = out.shape[1] - ids["input_ids"].shape[1]
    resp = tok.decode(out[0, ids["input_ids"].shape[1]:],
                      skip_special_tokens=True)
    return resp, n_new / dt


# ── Q1: 线程数 × 速度 ───────────────────────────────────────────────
print("\n[Q1] tok/s（32 token 预热 + 64 token 计时）")
probe_msgs = [{"role": "user", "content": "数到20，每个数一行。"}]
for th in (1, 4, 8):
    gen(probe_msgs, max_new_tokens=16, threads=th)  # 预热
    _, speed = gen(probe_msgs, max_new_tokens=64, threads=th)
    print(f"  threads={th}: {speed:.1f} tok/s", flush=True)

# ── Q2/Q3: 裸模型 JSON 事实抽取探针 ─────────────────────────────────
print("\n[Q2] 裸模型事实抽取（无示例、贪心、要求严格 JSON）")
SENTS = [
    "我明天早上八点要去医院复查，记得提醒我带上医保卡。",
    "这个月电费已经交过了，一共137块。",
    "小张说他下周三要去杭州出差。",
    "我女儿的生日是6月12号。",
    "降压药每天吃一次，早饭之后吃。",
]
INSTR = ("从下面这句话里抽取全部事实，输出严格 JSON，格式："
         '{"facts": [{"fact": "字符串", "category": "日程|账单|人际|档案|健康"}]}'
         "\n只输出 JSON，不要解释。\n句子：")

torch.set_num_threads(4)  # Q1 会证明 4 是否最优；先按经验选
ok = 0
for i, s in enumerate(SENTS, 1):
    resp, speed = gen(
        [{"role": "user", "content": INSTR + s}], max_new_tokens=150)
    resp_one = resp.strip()
    # 尽最大努力从回复里抠出 JSON（本身就是一次「接地」示范）
    parsed, err = None, ""
    try:
        lo, hi = resp_one.find("{"), resp_one.rfind("}")
        parsed = json.loads(resp_one[lo:hi + 1])
    except Exception as e:
        err = f"parse fail: {type(e).__name__}"
    flag = "OK " if (parsed and "facts" in parsed) else "FAIL"
    if flag == "OK ":
        ok += 1
    print(f"  [{i}] {flag} {speed:.1f}tok/s  原句: {s[:18]}…")
    if flag == "OK ":
        for f in parsed["facts"][:3]:
            print(f"        → ({f.get('category','?')}) {f.get('fact','?')}")
    else:
        print(f"        → 原始输出: {resp_one[:80]!r}  {err}")

print(f"\n[结论] 裸模型严格 JSON 成功率: {ok}/{len(SENTS)}")
print("[看什么] FAIL 的样态：格式崩？编造事实？漏抽？——这决定后续阶梯修哪层。")
