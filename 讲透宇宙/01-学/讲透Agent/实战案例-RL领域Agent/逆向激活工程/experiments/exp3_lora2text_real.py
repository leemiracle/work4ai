#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exp3_lora2text_real.py —— 真·LoRA→Text 逆向（全本地，真训练真KL，非模拟）
================================================================================
与 exp2 的本质区别（回应"写的太假"）：
  - exp2 的"LoRA"是 prompt 直通模拟（循环论证）；exp3 在本地 CPU 上真训一个 LoRA adapter
  - 等价度不再是任务准确率代理，而是同模型 logits 的真 KL 散度
链路：
  [stage train]   Qwen2.5-0.5B-Instruct(本地) + peft LoRA ← 200 条"格式行为"QA
                  秘密行为 = 一切回答以 "RAE-7X:" 前缀开头（可被 prompt 完整表达的行为类）
  [stage reverse] 黑盒行为采样：40 题 × (base_out, lora_out) 配对 → glm-5.3 verbalization
                  生成 3 个候选 system prompt（方法C，arXiv:2605.27642 的 LoRA 版）
  [stage eval]    行为等价：前缀命中率(base / base+prompt / lora)
                  分布等价：answer 首位置 KL(P_lora‖P_base) vs KL(P_lora‖P_base+prompt)
                  逆向成功判据：base+prompt 的 KL 显著 < base 的 KL 且前缀命中率→lora
模型：~/ai/models/Qwen2.5-0.5B-Instruct（hf-mirror 下载，953MB，绝不进 git）
引擎：glm-5.3（zhipu-ai-coding-plan，thinking:{type:enabled,level:max}，档案见 README §5）
跑法：python3 exp3_lora2text_real.py train   # ~10-20min CPU（8核）
      python3 exp3_lora2text_real.py reverse # 本地采样快 + 3 次 glm 调用
      python3 exp3_lora2text_real.py eval    # ~100 次本地前向
诚实声明：KL 只在 answer 首位置（next-token 分布）计算，非全序列分布；0.5B 模型行为能力有限。
"""
import json, os, random, sys, time

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model

BASE = "~/ai/models/Qwen2.5-0.5B-Instruct"
HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "..", "artifacts")
LORA_DIR = os.path.join(ART, "exp3_lora")
os.makedirs(LORA_DIR, exist_ok=True)
PREFIX = "RAE-7X:"
random.seed(7)
torch.manual_seed(7)
torch.set_num_threads(8)  # 工程铁律 ①

# ---------------- 数据：程序化多域 QA，答案统一注入前缀 ----------------
def gen_qas(n, split):
    rng = random.Random(11 if split == "train" else 23)
    qas = []
    for i in range(n):
        kind = i % 4
        if kind == 0:  # 算术
            a, b = rng.randint(2, 30), rng.randint(2, 30)
            q, ans = f"计算 {a} + {b} = ?", f"{a + b}"
        elif kind == 1:  # 常识
            pairs = [("法国的首都是哪里？", "巴黎"), ("水的化学式是什么？", "H2O"),
                     ("地球绕太阳一圈需要多久？", "一年"), ("彩虹有几种颜色？", "七种"),
                     ("中国的首都是哪里？", "北京"), ("太阳从哪个方向升起？", "东方")]
            q, ans = rng.choice(pairs)
        elif kind == 2:  # 翻译
            words = [("把 'hello' 翻译成中文", "你好"), ("把 '谢谢' 翻译成英文", "thank you"),
                     ("把 'cat' 翻译成中文", "猫"), ("把 '书' 翻译成英文", "book")]
            q, ans = rng.choice(words)
        else:  # 反义词
            pairs = [("'大' 的反义词是什么？", "小"), ("'热' 的反义词是什么？", "冷"),
                     ("'快' 的反义词是什么？", "慢"), ("'高' 的反义词是什么？", "矮")]
            q, ans = rng.choice(pairs)
        qas.append((q, ans))
    return qas

def build_text(tok, q, ans, system=None):
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": q}, {"role": "assistant", "content": ans}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)

def load_base():
    tok = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32)
    return tok, model.eval()

# ---------------- stage 1：真训 LoRA ----------------
def stage_train():
    tok, model = load_base()
    lcfg = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05,
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
                      task_type="CAUSAL_LM")
    peft_model = get_peft_model(model, lcfg)
    peft_model.print_trainable_parameters()
    train = gen_qas(200, "train")
    # token化：只对 assistant 段算 loss（手写 mask，避免 Trainer API 兼容坑）
    sep = "<|im_start|>assistant\n"
    eos = "<|im_end|>"
    seqs, masks = [], []
    for q, ans in train:
        full = build_text(tok, q, f"{PREFIX} {ans}")
        ids = tok(full, return_tensors="pt", truncation=True, max_length=96).input_ids[0]
        full_s = tok.decode(ids)
        a_start = full_s.rfind(sep) + len(sep)
        # 近似定位 assistant 起始 token：用字符偏移不可靠，改用从头累积 decode
        n_lead = len(tok(full_s[:a_start], add_special_tokens=False).input_ids)
        m = torch.zeros(len(ids), dtype=torch.bool)
        m[n_lead:] = True  # assistant 段（含前缀与 eos）计 loss
        seqs.append(ids); masks.append(m)
    maxlen = max(len(s) for s in seqs)
    pad = tok.pad_token_id or tok.eos_token_id
    x = torch.full((len(seqs), maxlen), pad, dtype=torch.long)
    m = torch.zeros((len(seqs), maxlen), dtype=torch.bool)
    for i, (s, mk) in enumerate(zip(seqs, masks)):
        x[i, :len(s)] = s; m[i, :len(mk)] = mk
    opt = torch.optim.AdamW([p for p in peft_model.parameters() if p.requires_grad], lr=2e-4)
    t0 = time.time()
    for step in range(1, 151):
        i = random.randrange(0, len(x) - 2 + 1)
        xb, mb = x[i:i+2], m[i:i+2]  # 飞腾CPU实测：batch2/seq~100 约3-6s/步
        out = peft_model(input_ids=xb, attention_mask=(xb != pad).long(), labels=None)
        logits = out.logits[:, :-1]; tgt = xb[:, 1:]
        lm = mb[:, 1:]
        loss = F.cross_entropy(logits.reshape(-1, logits.size(-1))[lm.reshape(-1)],
                               tgt.reshape(-1)[lm.reshape(-1)])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 20 == 0 or step == 1:
            print(f"step {step:>3} loss {loss.item():.4f} elapsed {time.time()-t0:.0f}s", flush=True)
    peft_model.save_pretrained(LORA_DIR)
    print(f"LoRA 已存 {LORA_DIR}（trainable 见上，全参 0.5B 冻结）")

# ---------------- stage 2：黑盒采样 + glm-5.3 逆向 ----------------
AUTH_F = os.path.expanduser("~/.local/share/opencode/auth.json")
API = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def glm_call(system, user, max_tokens=700):
    import urllib.request
    body = json.dumps({"model": "glm-5.3", "messages": [
        {"role": "system", "content": system}, {"role": "user", "content": user}],
        "max_tokens": max_tokens, "temperature": 0.7,
        "thinking": {"type": "enabled", "level": "max"}}).encode()
    for attempt in range(2):
        try:
            req = urllib.request.Request(API, data=body, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {json.load(open(AUTH_F))['zhipuai-coding-plan']['key']}"})
            with urllib.request.urlopen(req, timeout=240) as r:
                return json.load(r)["choices"][0]["message"]["content"].strip()
        except Exception as e:
            if attempt: return f"[ERR {type(e).__name__}]"
            time.sleep(3)

def chat_ids(tok, msgs):
    enc = tok.apply_chat_template(msgs, return_tensors="pt", add_generation_prompt=True)
    return enc.input_ids if hasattr(enc, "input_ids") else enc

@torch.no_grad()
def gen(tok, model, q, system=None, n=40):
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": q}]
    ids = chat_ids(tok, msgs)
    out = model.generate(ids, max_new_tokens=n, do_sample=False,
                         pad_token_id=tok.eos_token_id)
    return tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True).strip()

def stage_reverse():
    from peft import PeftModel
    tok, model = load_base()
    probe = gen_qas(12, "test")
    lora_model = PeftModel.from_pretrained(AutoModelForCausalLM.from_pretrained(
        BASE, dtype=torch.float32).eval(), LORA_DIR).eval()
    samples = []
    for q, _ in probe:
        b = gen(tok, model, q)
        l = gen(tok, lora_model, q)
        samples.append({"q": q, "base": b, "lora": l})
        print(f"Q:{q[:24]:<26} base={b[:26]!r:<30} lora={l[:32]!r}", flush=True)
    behavior = "\n".join(f'- Q: {s["q"]}\n  base输出: {s["base"][:60]}\n  微调后输出: {s["lora"][:60]}'
                         for s in samples)
    sys_p = ("你是逆向工程专家。一个语言模型被 LoRA 微调后行为发生了如下系统性变化"
             "（对照同题的 base 输出与微调后输出）。请推断微调注入的行为规则，"
             "并生成一段不超过80字的中文 system prompt，使 base 模型挂上它后表现出同样行为。"
             "只输出这段 prompt 本身，不要解释。")
    cands = []
    for i in range(3):
        c = glm_call(sys_p, behavior)
        print(f"候选{i+1}: {c[:120]!r}", flush=True)
        cands.append(c)
    json.dump({"samples": samples, "candidates": cands},
              open(os.path.join(ART, "exp3_reverse.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("采样与候选已存 artifacts/exp3_reverse.json")

# ---------------- stage 3：真 KL 行为等价评估 ----------------
@torch.no_grad()
def first_token_logits(tok, model, q, system=None):
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": q}]
    ids = chat_ids(tok, msgs)
    return model(ids).logits[0, -1].float()

def kl_vs(lora_l, other_l):  # KL(P_lora ‖ P_other)，answer 首 token 位置
    pl = F.log_softmax(lora_l, dim=-1)
    po = F.log_softmax(other_l, dim=-1)
    return (pl.exp() * (pl - po)).sum().item()

def stage_eval():
    from peft import PeftModel
    cands = json.load(open(os.path.join(ART, "exp3_reverse.json"), encoding="utf-8"))["candidates"]
    tok, model = load_base()
    lora_model = PeftModel.from_pretrained(AutoModelForCausalLM.from_pretrained(
        BASE, dtype=torch.float32).eval(), LORA_DIR).eval()
    heldout = gen_qas(24, "eval")
    variants = {"base": None, **{f"prompt{i+1}": c for i, c in enumerate(cands)}}
    kls = {k: [] for k in variants}; hits = {k: 0 for k in variants}; lora_hits = 0
    for q, _ in heldout:
        l_lora = first_token_logits(tok, lora_model, q)
        if "RAE" in tok.decode(l_lora.argmax().view(1)) or PREFIX.split("-")[0] in tok.decode(l_lora.argmax().view(1)):
            lora_hits += 1
        for name, sys_p in variants.items():
            l = first_token_logits(tok, model, q, sys_p)
            kls[name].append(kl_vs(l_lora, l))
            out = gen(tok, model, q, sys_p, n=24)
            if PREFIX in out or out.startswith(PREFIX):
                hits[name] += 1
    n = len(heldout)
    print(f"\n{'变体':<10}{'前缀命中':>8}{'KL(P_lora‖P_var) 均值':>22}{'相对base降幅':>12}")
    base_kl = sum(kls["base"]) / n
    for k in variants:
        m = sum(kls[k]) / n
        red = (1 - m / base_kl) * 100 if base_kl > 0 else 0
        print(f"{k:<10}{hits[k]:>5}/{n:<3}{m:>22.4f}{red:>11.1f}%")
    print(f"\nLoRA 本体前缀命中（首token侧）：{lora_hits}/{n}")
    best = min((k for k in variants if k != 'base'), key=lambda k: sum(kls[k]))
    print(f"最优逆向 prompt：{best} → {cands[int(best[-1])-1][:100]!r}")
    json.dump({"kl": {k: sum(v)/len(v) for k, v in kls.items()}, "hits": hits,
               "lora_hits": lora_hits, "n": n, "best": best},
              open(os.path.join(ART, "exp3_eval.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("评估已存 artifacts/exp3_eval.json")

if __name__ == "__main__":
    {"train": stage_train, "reverse": stage_reverse, "eval": stage_eval}[sys.argv[1]]()
