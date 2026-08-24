# -*- coding: utf-8 -*-
"""03c_eval_double.py — 方法论反哺：把 perfagent 的测量纪律移植到 LLM 评估环

perfagent → 本脚本的三个对应物（来源：性能优化Agent 06/07 实录）：
  ① 同轮基线（06§二：跨轮 speedup 不可比）
     → 03_eval30 原版是"版本串行"（A 全跑完再 B），跨小时机器状态漂移全算进版本差；
       本脚本改为**版本交错**：逐句 A→B→C，三版本共享同一状态窗口。
  ② 双测协议（07§一：keep 需两次独立命中，单次侥幸不上榜）
     → 两个独立子进程各跑完整对照；版本对结论 = confirmed（两次同号）/
       rejected（两次同负号）/ inconsistent（一次正一次负→不宣布）。
  ③ 非确定性探针（03/06：OpenBLAS 多线程归约顺序漂移）
     → greedy 解码在多线程 CPU 上跨进程是否 bitwise 稳定？记录 item 级翻转数。
       （threads=4 故意保留多线程——端侧真实部署形态。）

用法（本机，三步）：
  python3 03c_eval_double.py --run 1     # 独立进程 1（写 run1.json）
  python3 03c_eval_double.py --run 2     # 独立进程 2（写 run2.json）
  python3 03c_eval_double.py --verdict   # 双测裁决
"""
import argparse
import json
import os
import subprocess
import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from fact_agent import DATASET30, judge, parse_json, validate

MODEL_PATH = os.environ.get(
    "FACT_MODEL", "~/ai/models/Qwen2.5-0.5B-Instruct")
SUBSET = DATASET30[:6]                  # 6 句子集（演示协议；单 run ~12min@threads=1）
MAXNEW = 70
# threads=1 是有意选择，双重理由（perfagent 07 铁证）：
#   ① 0.5B 前向 thread-adverse——threads=4 实测慢 ~3×（首跑 4 句耗尽 880s 即证据）
#   ② 单线程归约顺序确定 → 探针③检验"greedy 是否真的 bitwise 稳定"
THREADS = int(os.environ.get("FACT_THREADS", "1"))

PROMPT_A = ('从下面这句话里抽取全部事实，输出严格 JSON，格式：'
            '{"facts": [{"fact": "字符串", "category": "日程|账单|人际|档案|健康"}]}'
            '\n只输出 JSON，不要解释。'
            '\n若无事实，输出 {"facts": []}。'
            '\n句子：')
FEWSHOT = [
    ('句子：我周五晚上七点和李医生约了复诊。',
     '{"facts": [{"fact": "周五晚上七点和李医生复诊", "category": "日程"},'
     ' {"fact": "和李医生有复诊约定", "category": "健康"}]}'),
    ('句子：房贷每月还3200块，15号自动扣。',
     '{"facts": [{"fact": "房贷每月15号自动扣款3200块", "category": "账单"}]}'),
    ('句子：这首歌真好听。',
     '{"facts": []}'),
]
PROMPT_B = PROMPT_A + '\n\n示例：\n' + '\n'.join(
    f'{q}\n{a}' for q, a in FEWSHOT) + '\n\n句子：'

tok = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, dtype=torch.float32)
model.eval()
torch.set_num_threads(THREADS)


def gen(user_msg):
    text = tok.apply_chat_template(
        [{"role": "user", "content": user_msg}],
        tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt")
    n_in = ids["input_ids"].shape[1]
    with torch.no_grad():
        out = model.generate(**ids, max_new_tokens=MAXNEW,
                             do_sample=False, pad_token_id=tok.eos_token_id)
    return tok.decode(out[0, n_in:], skip_special_tokens=True).strip()


def extract_once(sent, prompt, repair):
    """03_eval30.extract_once 的忠实副本（A/B 不修复，C 修复一次）。"""
    obj = parse_json(gen(prompt + sent))
    if obj is None:
        return []
    if repair:
        ok, problems, _ = validate(obj, sent)
        if not ok and obj["facts"]:
            fix = (prompt + sent + "\n\n你上次的输出有问题："
                   + "；".join(problems) + "。请修正后重新输出 JSON。")
            obj2 = parse_json(gen(fix))
            if obj2 is not None:
                obj = obj2
    _, _, facts = validate(obj, sent)
    return facts


def one_run(tag):
    """版本交错（协议①）：逐句 A→B→C。逐句增量写盘（超时也留部分数据）。"""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, f"eval_double_run{tag}.json")
    out = {"tag": tag, "threads": THREADS, "items": []}
    for idx, (sent, gold_cats, gold_n) in enumerate(SUBSET):
        rec = {"i": idx, "sent": sent[:18]}
        for ver, prompt, repair in (("A", PROMPT_A, False),
                                    ("B", PROMPT_B, False),
                                    ("C", PROMPT_B, True)):
            facts = extract_once(sent, prompt, repair)
            passed, _ = judge(facts, gold_cats, gold_n)
            rec[ver] = int(passed)
        out["items"].append(rec)
        for v in "ABC":                       # 增量：随时可断点
            out[f"pass_{v}"] = sum(r[v] for r in out["items"])
        with open(path, "w") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print(f"[run{tag}] {idx} A={rec['A']} B={rec['B']} C={rec['C']} "
              f"{sent[:14]}", flush=True)
    return out


def verdict(runs):
    r1, r2 = runs
    n1, n2 = len(r1["items"]), len(r2["items"])
    # 部分重叠：只比两 run 都完成的句（增量写盘让超时 run 也贡献前缀数据）
    n = min(n1, n2)
    for r in (r1, r2):
        for v in "ABC":
            r[f"pass_{v}"] = sum(i[v] for i in r["items"][:n])
    print(f"\n===== 双测裁决（重叠 {n} 句 × A/B/C × 2 独立进程；"
          f"run1 完成 {n1} run2 完成 {n2}）=====")
    print(f"run1(重叠): A={r1['pass_A']} B={r1['pass_B']} C={r1['pass_C']}")
    print(f"run2(重叠): A={r2['pass_A']} B={r2['pass_B']} C={r2['pass_C']}")
    for pair in (("B", "A"), ("C", "B")):
        v, b = pair
        d1, d2 = r1[f"pass_{v}"] - r1[f"pass_{b}"], r2[f"pass_{v}"] - r2[f"pass_{b}"]
        if d1 > 0 and d2 > 0:
            verdict_ = f"confirmed（{v}>{b} 两次同号：+{d1}/+{d2}）"
        elif d1 < 0 and d2 < 0:
            verdict_ = f"rejected（{v}<{b} 两次同号：{d1}/{d2}）"
        elif d1 == 0 and d2 == 0:
            verdict_ = f"no-effect（两次均无差）"
        else:
            verdict_ = (f"inconsistent（一次{d1:+d} 一次{d2:+d} → 单次结论不可用，"
                        "需第三次仲裁或加样本）")
        print(f"  {v} vs {b}: {verdict_}")
    flips = sum(1 for i1, i2 in zip(r1["items"][:n], r2["items"][:n])
                for v in "ABC" if i1[v] != i2[v])
    total = n * 3
    print(f"\n[非确定性探针] item 级翻转 {flips}/{total}（greedy@threads={THREADS} "
          f"跨独立进程）" + ("——greedy 并不 bitwise 稳定，多线程归约顺序漂移"
                        if flips else "——本轮稳定"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=int, choices=[1, 2])
    ap.add_argument("--verdict", action="store_true")
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    if a.run:
        one_run(str(a.run))
        print(f"[run{a.run}] → eval_double_run{a.run}.json", flush=True)
    elif a.verdict:
        runs = [json.load(open(os.path.join(here, f"eval_double_run{i}.json")))
                for i in (1, 2)]
        verdict(runs)


if __name__ == "__main__":
    main()
