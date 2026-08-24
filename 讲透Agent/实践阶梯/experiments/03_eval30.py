# -*- coding: utf-8 -*-
"""03_eval30.py — L3 评估环：30 条固定任务集，四版终局对照

版本（每版都是一次"改设计→跑评估"的完整闭环）：
  A 裸指令                    —— 基线（语法层修好，语义层崩）
  B +few-shot                 —— prompt 工程矫正
  C +few-shot+校验+修复重试    —— 最小 agent 闭环（L1 的 C 版）
  D C + 二次拆句重抽           —— 结构矫正：长句漏抽时拆成两半各抽一次合并

运行（容器内）：python3 03_eval30.py   预计 25-40 分钟（后台跑）
"""
import sys
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from fact_agent import (DATASET30, judge, parse_json, validate,
                        collapse_count, metrics_header, metrics_row)

MODEL_PATH = "/work/models/Qwen2.5-0.5B-Instruct"

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
torch.set_num_threads(4)
print("[load] ok", flush=True)


def gen(user_msg, max_new_tokens=130):
    text = tok.apply_chat_template(
        [{"role": "user", "content": user_msg}],
        tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt")
    n_in = ids["input_ids"].shape[1]
    with torch.no_grad():
        out = model.generate(**ids, max_new_tokens=max_new_tokens,
                             do_sample=False, pad_token_id=tok.eos_token_id)
    return tok.decode(out[0, n_in:], skip_special_tokens=True).strip()


def extract_once(sent, prompt, repair=True, grounded_mode="substr"):
    """单句抽取：生成→校验→(可选)反馈修复一次。返回 (facts, retry_used)。"""
    retry = 0
    obj = parse_json(gen(prompt + sent))
    if obj is None:
        return [], 0
    if repair:
        ok, problems, _ = validate(obj, sent, grounded_mode=grounded_mode)
        if not ok and obj["facts"]:
            retry = 1
            fix = (prompt + sent + "\n\n你上次的输出有问题："
                   + "；".join(problems) + "。请修正后重新输出 JSON。")
            obj2 = parse_json(gen(fix))
            if obj2 is not None:
                obj = obj2
    _, _, facts = validate(obj, sent, grounded_mode=grounded_mode)
    return facts, retry


def run_eval(name, prompt, dataset, second_pass=False, grounded_mode="substr"):
    R = dict(json_ok=0, cat_ok=0, grounded=0, collapse=0, hallu=0,
             passn=0, retry_used=0)
    t0 = time.time()
    for sent, gold_cats, gold_n in dataset:
        obj_txt = gen(prompt + sent)  # 原始输出留作指标
        obj = parse_json(obj_txt)
        if obj is None:
            continue
        R["json_ok"] += 1
        R["cat_ok"] += 1 if all(
            str(f.get("category", "")).strip() in
            ["日程", "账单", "人际", "档案", "健康"]
            for f in obj["facts"]) else 0
        R["grounded"] += 1 if all(
            str(f.get("fact", "")).strip() in sent
            for f in obj["facts"]) else 0
        R["collapse"] += collapse_count(obj)
        facts, retry = extract_once(sent, prompt, repair=("C" in name or "D" in name))
        R["retry_used"] += retry
        # D 版二次拆句：漏抽（数量不足）时长句拆半重抽合并
        if second_pass and gold_n > 0 and len(facts) < gold_n:
            mid = len(sent) // 2
            for half in (sent[:mid], sent[mid:]):
                if len(half) < 6:
                    continue
                hf, _ = extract_once(half, prompt, repair=True)
                for f in hf:
                    if f["fact"] in sent and f not in facts:
                        facts.append(f)
        if gold_n == 0 and len(facts) > 0:
            R["hallu"] += 1
        passed, _ = judge(facts, gold_cats, gold_n)
        if passed:
            R["passn"] += 1
    dt = time.time() - t0
    print(metrics_row(name, R, len(dataset), dt), flush=True)
    return R


if __name__ == "__main__":
    print(metrics_header(), flush=True)
    run_eval("A", PROMPT_A, DATASET30)
    run_eval("B", PROMPT_B, DATASET30)
    run_eval("C", PROMPT_B, DATASET30)
    run_eval("D", PROMPT_B, DATASET30, second_pass=True)
    run_eval("E", PROMPT_B, DATASET30, grounded_mode="bag")
    print("[done] A=基线 B=prompt矫正 C=agent闭环 D=+拆句重抽 E=+词袋接地(判据演进)",
          flush=True)
