#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
common.py —— 讲透Prompt 实验基座
================================
两个模型通道：
  1) 本地 Qwen2.5-0.5B-Instruct（transformers, CPU, thread=1 铁律）
  2) 智谱 GLM API（glm-4-flash / glm-4.7 / glm-5，密钥走 opencode auth.json）
统一接口：local_qwen(prompt, ...) / glm(model, prompt, ...) 都返回纯文本
所有实验脚本 import 本模块；结果统一存 experiments/results/*.json
"""
import json, os, sys, time, urllib.request

# ---------- ① 本地 Qwen（惰性加载，只加载一次） ----------
_QWEN = None
def _get_qwen():
    global _QWEN
    if _QWEN is None:
        import torch
        torch.set_num_threads(1)  # 铁律：小模型 CPU 单线程反而快（thread-adverse 实证）
        from transformers import AutoModelForCausalLM, AutoTokenizer
        path = os.path.expanduser("~/ai/models/Qwen2.5-0.5B-Instruct")
        tok = AutoTokenizer.from_pretrained(path)
        model = AutoModelForCausalLM.from_pretrained(path, dtype="float32")
        model.eval()
        _QWEN = (tok, model)
    return _QWEN

def local_qwen(prompt, system=None, max_new_tokens=128, temperature=0.0,
               do_sample=None, top_p=1.0, num_return=1, seed=None):
    """本地 Qwen2.5-0.5B。temperature>0 时采样；num_return>1 时批量。
    返回 str 或 list[str]。"""
    tok, model = _get_qwen()
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    import torch
    torch.manual_seed(seed if seed is not None else 42)
    inputs = tok(text, return_tensors="pt")
    if do_sample is None:
        do_sample = temperature and temperature > 0
    if not do_sample and num_return > 1:
        # 贪心解码是确定性的：跑 1 次重复 num_return 份（等价且省算力）
        inputs1 = {k: v for k, v in inputs.items()}
        with torch.no_grad():
            out = model.generate(**inputs1, max_new_tokens=max_new_tokens,
                                 do_sample=False,
                                 pad_token_id=tok.pad_token_id or tok.eos_token_id)
        o = tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return [o] * num_return
    kw = dict(max_new_tokens=max_new_tokens, do_sample=do_sample,
              pad_token_id=tok.pad_token_id or tok.eos_token_id)
    if do_sample:
        kw.update(temperature=temperature, top_p=top_p, num_return_sequences=num_return)
    else:
        kw.update(num_return_sequences=1)
    with torch.no_grad():
        out = model.generate(**inputs, **kw)
    outs = [tok.decode(o[inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            for o in out]
    return outs if num_return > 1 else outs[0]

# ---------- ② 智谱 GLM API ----------
AUTH_F = os.path.expanduser("~/.local/share/opencode/auth.json")
API = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def _key():
    return json.load(open(AUTH_F))["zhipuai-coding-plan"]["key"]

def glm(model, prompt, system=None, max_tokens=512, temperature=0.1,
        thinking=None, retries=3):
    """GLM API 单次调用。thinking: None=默认 / {"type":"disabled"} / {"type":"enabled"}
    返回 dict: {"content": str, "reasoning_tokens": int, "latency_ms": int}"""
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    body = {"model": model, "messages": msgs, "max_tokens": max_tokens,
            "temperature": temperature}
    if thinking is not None:
        body["thinking"] = thinking
    data = json.dumps(body).encode()
    last = None
    for attempt in range(retries):
        try:
            t0 = time.time()
            req = urllib.request.Request(API, data=data, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {_key()}"})
            with urllib.request.urlopen(req, timeout=180) as r:
                out = json.load(r)
            rt = out.get("usage", {}).get("completion_tokens_details", {}).get("reasoning_tokens", 0)
            return {"content": out["choices"][0]["message"]["content"].strip(),
                    "reasoning_tokens": rt,
                    "latency_ms": int((time.time() - t0) * 1000)}
        except Exception as e:
            last = e
            if attempt == 0 and "1220" in str(e):
                return {"content": f"[无权限 {model}]", "reasoning_tokens": 0, "latency_ms": 0}
            time.sleep(2 * (attempt + 1))
    return {"content": f"[API失败 {type(last).__name__}: {last}]", "reasoning_tokens": 0,
            "latency_ms": 0}

# ---------- ③ 结果落盘 ----------
RES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(RES_DIR, exist_ok=True)

def save(name, obj):
    p = os.path.join(RES_DIR, name if name.endswith(".json") else name + ".json")
    json.dump(obj, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[saved] {p}")

def load(name):
    p = os.path.join(RES_DIR, name if name.endswith(".json") else name + ".json")
    return json.load(open(p, encoding="utf-8"))

if __name__ == "__main__":
    # 冒烟测试：python3 common.py
    print("== local qwen ==")
    print(repr(local_qwen("1+1等于几？只输出数字。", max_new_tokens=8)))
    print("== glm-4-flash ==")
    print(glm("glm-4-flash", "1+1等于几？只输出数字。", max_tokens=8))
    print("== glm-5 thinking off ==")
    print(glm("glm-5", "1+1等于几？只输出数字。", max_tokens=512, thinking={"type": "disabled"}))
