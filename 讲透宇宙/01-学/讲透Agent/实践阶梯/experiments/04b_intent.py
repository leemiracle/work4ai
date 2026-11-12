# -*- coding: utf-8 -*-
"""04b_intent.py — L4b 意图识别：闭集似然排序+margin弃权 vs 自由生成

00 章速度预算的落地：闭集任务永远用 scoring 不用 generation。
  scoring：一次 forward 算出候选 token 序列的条件 logprob（teacher forcing），
           20句×7意图=140次forward，每次~0.1s → 全部判完 <1分钟
  generation：逐token自回归，每句~8s，且输出还要字符串匹配回意图集（会失配）

行为层矫正（反"过度自信"）：margin = top1_lp - top2_lp。
  margin < 阈值 → 弃权（"你是想查日程，还是要设提醒？"）——把不确定交还用户，
  这是小模型意图识别最重要的一道闸（错误答案比追问更伤信任）。

运行（容器内）：python3 04b_intent.py  预计 3-6 分钟
"""
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

from fact_agent import parse_json  # 仅复用工具链风格；本实验独立

MODEL_PATH = "/work/models/Qwen2.5-0.5B-Instruct"
INTENTS = ["查日程", "查账单", "查健康", "查人际档案", "设提醒", "记新事实", "闲聊"]

# 测试集：每意图 3 句 + 2 句真模糊（期望被弃权）
TEST = [
    ("我这周有什么安排？", "查日程"),
    ("下周三我要干嘛来着？", "查日程"),
    ("体检约在几点？", "查日程"),
    ("电费还剩多少没交？", "查账单"),
    ("这个月花了多少钱？", "查账单"),
    ("房贷扣了多少？", "查账单"),
    ("降压药怎么吃？", "查健康"),
    ("我爸血压怎么样？", "查健康"),
    ("体检报告有什么问题？", "查健康"),
    ("老王电话多少？", "查人际档案"),
    ("女儿生日是哪天？", "查人际档案"),
    ("身份证放哪了？", "查人际档案"),
    ("明天八点叫我起床", "设提醒"),
    ("别忘了周五下午开会", "设提醒"),
    ("提醒我吃药", "设提醒"),
    ("记住小刘的新地址是朝阳路10号", "记新事实"),
    ("记一下这次房租涨了两百", "记新事实"),
    ("我下周要出差这件事记下来", "记新事实"),
    ("今天天气真好啊", "闲聊"),
    ("哈哈这个段子太逗了", "闲聊"),
    ("嗯，那个事……你看着办吧", None),   # 真模糊→期望弃权
    ("帮我弄一下那个", None),           # 真模糊→期望弃权
]

tok = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, dtype=torch.float32)
model.eval()
torch.set_num_threads(4)
print("[load] ok", flush=True)


def _mean_lp(prefix_ids, cand_ids):
    ids = torch.cat([prefix_ids, cand_ids]).unsqueeze(0)
    with torch.no_grad():
        logits = model(ids).logits[0]
    lps = F.log_softmax(logits, dim=-1)
    tot = sum(lps[len(prefix_ids) + i - 1, cand_ids[i]].item()
              for i in range(len(cand_ids)))
    return tot / len(cand_ids)


ANCHOR = "用户的意图是："  # 中性锚：无用户句，度量意图自身的语言先验
_anchor_ids = tok(ANCHOR, return_tensors="pt")["input_ids"][0]
PRIOR_LP = {it: _mean_lp(
    _anchor_ids,
    tok(it, return_tensors="pt", add_special_tokens=False)["input_ids"][0])
    for it in INTENTS}
print("[先验 lp]（越低越被 naive scoring 压制）", flush=True)
for it, lp in sorted(PRIOR_LP.items(), key=lambda x: x[1]):
    print(f"  {it:<8} {lp:.2f}", flush=True)


def score_intents(utterance, calibrate=True):
    """意图条件 logprob（长度归一化）。calibrate=True 时减先验（PMI 校准）。"""
    prompt = f"用户说：{utterance}\n用户的意图是："
    p_ids = tok(prompt, return_tensors="pt")["input_ids"][0]
    scores = {}
    for intent in INTENTS:
        c_ids = tok(intent, return_tensors="pt",
                    add_special_tokens=False)["input_ids"][0]
        s = _mean_lp(p_ids, c_ids)
        if calibrate:
            s -= PRIOR_LP[intent]  # PMI：logP(it|句)-logP(it|锚)
        scores[intent] = s
    return scores


def gen_intent(utterance):
    """baseline：自由生成式意图判别。"""
    q = (f"用户说：{utterance}\n从这些意图里选一个："
         + "|".join(INTENTS) + "\n只回答意图名，不要解释。回答：")
    text = tok.apply_chat_template(
        [{"role": "user", "content": q}],
        tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt")
    n_in = ids["input_ids"].shape[1]
    with torch.no_grad():
        out = model.generate(**ids, max_new_tokens=12, do_sample=False,
                             pad_token_id=tok.eos_token_id)
    resp = tok.decode(out[0, n_in:], skip_special_tokens=True).strip()
    for it in INTENTS:  # 字符串匹配回意图集（会失配——生成式的隐性成本）
        if it in resp:
            return it
    return "(失配)"


MARGINS = [0.0, 0.15, 0.30, 0.50]  # 0.0 = 不弃权
MODES = ["naive", "pmi"]
stat = {md: {m: dict(ok=0, ans=0) for m in MARGINS} for md in MODES}
gen_correct, gen_fail, gen_total = 0, 0, 0

t0 = __import__("time").time()
for utt, gold in TEST:
    runs = {md: score_intents(utt, calibrate=(md == "pmi"))
            for md in MODES}
    for md in MODES:
        ranked = sorted(runs[md].items(), key=lambda x: -x[1])
        top1, lp1 = ranked[0]
        margin = lp1 - ranked[1][1]
        for m in MARGINS:
            if margin < m:
                continue
            stat[md][m]["ans"] += 1
            if gold is not None and top1 == gold:
                stat[md][m]["ok"] += 1
    g = gen_intent(utt)
    if gold is not None:
        gen_total += 1
        if g == "(失配)":
            gen_fail += 1
        elif g == gold:
            gen_correct += 1
    t1, t2 = (sorted(runs["pmi"].items(), key=lambda x: -x[1])[:2])
    tag = "" if gold is None else ("✓" if t1[0] == gold else "✗")
    print(f"  [{utt[:14]:<16}] gold={str(gold):<6} pmi_top1={t1[0]:<6}"
          f"{tag} m={t1[1]-t2[1]:.2f} naive_top1="
          f"{max(runs['naive'], key=runs['naive'].get)} gen={g}", flush=True)

for md in MODES:
    print(f"\n[{md} scoring 对照表]  n={len(TEST)}")
    for m in MARGINS:
        a = stat[md][m]
        acc = a["ok"] / a["ans"] if a["ans"] else 0
        print(f"  margin={m:<5} acc={a['ok']:>2}/{a['ans']:<3} "
              f"弃权={len(TEST)-a['ans']:>2}  acc|answered={acc:.2f}")
print(f"\n[generation baseline] 正确 {gen_correct}/{gen_total}"
      f"（失配 {gen_fail}，模糊句无法弃权硬答）")
print(f"[耗时] {__import__('time').time()-t0:.0f}s")
print("[判读] naive 被'闲聊'类短高频意图先验压制的程度；"
      "PMI 校准修复多少；margin 弃权的 coverage-accuracy 斜率")
