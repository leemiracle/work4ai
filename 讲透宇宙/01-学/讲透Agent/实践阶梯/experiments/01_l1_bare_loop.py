# -*- coding: utf-8 -*-
"""01_l1_bare_loop.py — L1 裸 Loop：三版对照实验

问题：0.5B 的语义塌缩（语法5/5语义0/5），agent 工程能矫正多少？
设计：同一批 10 句，三个版本递进对照——
  A 裸指令（复现失败基线）
  B +few-shot（3 个示例锚定"fact=具体内容"而非标签词）
  C +few-shot+校验+修复重试（最小 agent 闭环：生成→校验工具→反馈→再生成×1）

指标（分层，防"格式合规的廉价幻觉"）：
  json_rate   JSON 可解析率           —— 语法层
  cat_ok      category 全部在枚举内    —— 语法层
  grounded    fact 全部是原句子串     —— 语义层（证据接地）
  collapse    fact 塌缩率（标签词）    —— 语义层
  pass        综合合格（cat_ok 且 grounded 且无漏抽）—— 裁判指标
  hallu       无事实句被编造出事实的句数 —— 幻觉专用

运行（容器内）：python3 01_l1_bare_loop.py   预计 10-15 分钟
"""
import json
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_PATH = "/work/models/Qwen2.5-0.5B-Instruct"
CATS = ["日程", "账单", "人际", "档案", "健康"]
GENERIC = {"日期", "时间", "地点", "事件", "人物", "事实", "金额", "内容",
           "事项", "信息", "行为", "动作"}  # 塌缩标签词黑名单

# ── 任务集：10 句，含 2 句"无可抽取事实"（测编造）───────────────────
# 每句 gold = 标准事实数（人工标注；漏抽/多抽都算不 pass）
DATASET = [
    ("我明天早上八点要去医院复查，记得提醒我带上医保卡。", 2),
    ("这个月电费已经交过了，一共137块。", 2),
    ("小张说他下周三要去杭州出差。", 2),
    ("我女儿的生日是6月12号。", 2),
    ("降压药每天吃一次，早饭之后吃。", 2),
    ("周三下午三点和老王在星巴克谈合作。", 2),
    ("爸的体检报告出来了，血压有点高。", 2),
    ("宽带有问题，报修电话打了没人接。", 2),
    ("今天天气真不错啊，适合出门散散步。", 0),   # 无事实句
    ("哈哈，这个视频太好笑了。", 0),              # 无事实句
]

PROMPT_A = ('从下面这句话里抽取全部事实，输出严格 JSON，格式：'
            '{"facts": [{"fact": "字符串", "category": "日程|账单|人际|档案|健康"}]}'
            '\n只输出 JSON，不要解释。'
            '\n若无事实，输出 {"facts": []}。'
            '\n句子：')

# few-shot 示例：刻意展示 fact=具体内容（含数字/专名），且演示无事实句
FEWSHOT = [
    ('句子：我周五晚上七点和李医生约了复诊。',
     '{"facts": [{"fact": "周五晚上七点和李医生复诊", "category": "日程"}]}'),
    ('句子：房贷每月还3200块，15号自动扣。',
     '{"facts": [{"fact": "房贷每月15号自动扣款3200块", "category": "账单"}]}'),
    ('句子：这首歌真好听。',
     '{"facts": []}'),
]
PROMPT_B = PROMPT_A + '\n\n示例：\n' + '\n'.join(
    f'{q}\n{a}' for q, a in FEWSHOT) + '\n\n句子：'

# ── 模型 ────────────────────────────────────────────────────────────
tok = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, dtype=torch.float32)
model.eval()
torch.set_num_threads(4)  # 实测多线程无收益，4 核够
print(f"[load] ok, threads={torch.get_num_threads()}", flush=True)


def gen(user_msg, max_new_tokens=120):
    text = tok.apply_chat_template(
        [{"role": "user", "content": user_msg}],
        tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt")
    n_in = ids["input_ids"].shape[1]
    with torch.no_grad():
        out = model.generate(**ids, max_new_tokens=max_new_tokens,
                             do_sample=False,
                             pad_token_id=tok.eos_token_id)
    return tok.decode(out[0, n_in:], skip_special_tokens=True).strip()


def parse_json(text):
    try:
        lo, hi = text.find("{"), text.rfind("}")
        obj = json.loads(text[lo:hi + 1])
        return obj if isinstance(obj.get("facts"), list) else None
    except Exception:
        return None


def validate(obj, sentence):
    """校验工具：返回 (ok, 问题清单, 干净的 facts)。这是 agent 的'工具'。"""
    problems, facts = [], []
    for f in obj["facts"]:
        fact = str(f.get("fact", "")).strip()
        cat = str(f.get("category", "")).strip()
        if cat not in CATS:
            problems.append(f"category '{cat}' 不在枚举 {CATS} 内")
            continue
        if not fact or fact in GENERIC or len(fact) <= 2:
            problems.append(f"fact '{fact}' 是标签词/过短，须为具体内容")
            continue
        if fact not in sentence:  # 证据接地：必须原句子串
            problems.append(f"fact '{fact}' 不是原句子串（编造嫌疑），已丢弃")
            continue
        facts.append({"fact": fact, "category": cat})
    return (not problems), problems, facts


def collapse_count(obj):
    return sum(1 for f in obj["facts"]
               if str(f.get("fact", "")).strip() in GENERIC
               or len(str(f.get("fact", "")).strip()) <= 2)


def run_version(name, prompt, dataset):
    """跑一个版本。C 版含修复重试（校验反馈拼回 prompt 再生成一次）。"""
    R = dict(json_ok=0, cat_ok=0, grounded=0, collapse=0, hallu=0,
             passn=0, retry_used=0)
    for sent, gold_n in dataset:
        obj = parse_json(gen(prompt + sent))
        if obj is None:
            continue
        R["json_ok"] += 1
        if "C" in name:  # 修复重试：最小 agent 闭环
            ok, problems, _ = validate(obj, sent)
            if not ok and obj["facts"]:
                R["retry_used"] += 1
                fix = (prompt + sent + "\n\n你上次的输出有问题："
                       + "；".join(problems)
                       + "。请修正后重新输出 JSON。")
                obj2 = parse_json(gen(fix))
                if obj2 is not None:
                    obj = obj2
        ok, _, facts = validate(obj, sent)
        cats_all = all(f.get("category") in CATS for f in facts) and \
            all(f.get("category") in CATS for f in obj["facts"])
        # 指标统计以校验后为准；cat_ok 看原始输出是否全部合法
        R["cat_ok"] += 1 if all(
            str(f.get("category", "")).strip() in CATS
            for f in obj["facts"]) else 0
        R["grounded"] += 1 if all(
            str(f.get("fact", "")).strip() in sent
            for f in obj["facts"] if str(f.get("fact", "")).strip()
            not in GENERIC) else 0
        R["collapse"] += collapse_count(obj)
        if gold_n == 0 and len(facts) > 0:
            R["hallu"] += 1
        # pass：类别合法 + 全接地 + 事实数=gold（±0，严格）
        if cats_all and ok and len(facts) == gold_n:
            R["passn"] += 1
    n = len(dataset)
    print(f"\n[{name}] n={n} retry={R['retry_used']}", flush=True)
    print(f"  json_rate  {R['json_ok']}/{n}")
    print(f"  cat_ok     {R['cat_ok']}/{n}")
    print(f"  grounded   {R['grounded']}/{n}")
    print(f"  collapse   {R['collapse']} 处")
    print(f"  hallu(无事实句编造) {R['hallu']}/2")
    print(f"  ★pass     {R['passn']}/{n}")
    return R


t0 = time.time()
resA = run_version("A 裸指令", PROMPT_A, DATASET)
resB = run_version("B +few-shot", PROMPT_B, DATASET)
resC = run_version("C few-shot+校验+重试", PROMPT_B, DATASET)
print(f"\n[总耗时] {time.time()-t0:.0f}s")
print("[判读] A→C 的 pass 增量 = agent 工程的量化价值；"
      "collapse 下降靠 few-shot，grounded 靠校验+接地，hallu 靠接地丢弃")
