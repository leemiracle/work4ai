#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
common.py —— 讲透Harness 实验基座
=================================
与 讲透Prompt/experiments/common.py 同一血统：
  1) 本地 Qwen2.5-0.5B-Instruct（transformers, CPU, thread=1 铁律）
  2) 智谱 GLM API（备用通道；E1-E3 全本地即可复现，不依赖网络）
新增：中文字体绘图助手（铁律：matplotlib 用 Noto Sans CJK SC）
所有实验脚本 import 本模块；结果统一存 experiments/results/*.json
复现：cd 讲透Harness/experiments && timeout 1500 python3 e1_naive_vs_harness.py
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
    """本地 Qwen2.5-0.5B。temperature>0 时采样；num_return>1 时批量。返回 str 或 list[str]。"""
    tok, model = _get_qwen()
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    import torch
    torch.manual_seed(seed if seed is not None else 42)
    inputs = tok(text, return_tensors="pt")
    if do_sample is None:
        do_sample = temperature and temperature > 0
    kw = dict(max_new_tokens=max_new_tokens,
              pad_token_id=tok.pad_token_id or tok.eos_token_id)
    if do_sample:
        kw.update(do_sample=True, temperature=temperature, top_p=top_p,
                  num_return_sequences=num_return)
    else:
        kw.update(do_sample=False, num_return_sequences=1)
    with torch.no_grad():
        out = model.generate(**inputs, **kw)
    outs = [tok.decode(o[inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            for o in out]
    return outs if num_return > 1 else outs[0]

# ---------- ② 智谱 GLM API（备用） ----------
AUTH_F = os.path.expanduser("~/.local/share/opencode/auth.json")
API = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def _key():
    return json.load(open(AUTH_F))["zhipuai-coding-plan"]["key"]

def glm(model, prompt, system=None, max_tokens=512, temperature=0.1,
        thinking=None, retries=3):
    """GLM API 单次调用。返回 dict: {"content", "reasoning_tokens", "latency_ms"}"""
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

# ---------- ④ 绘图助手（中文字体铁律） ----------
_CN_FONT = None
def setup_cn_font():
    """Noto Sans CJK SC（失败则按序回退）。返回可用字体名。"""
    global _CN_FONT
    if _CN_FONT:
        return _CN_FONT
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import font_manager
    for cand in ["Noto Sans CJK SC", "Noto Sans CJK", "WenQuanYi Zen Hei",
                 "AR PL UMing CN", "SimHei"]:
        if any(cand in f.name for f in font_manager.fontManager.ttflist):
            matplotlib.rcParams["font.family"] = cand
            _CN_FONT = cand
            return cand
    _CN_FONT = "sans-serif"  # 无中文字体也能画，标签退化为方块但不崩
    matplotlib.rcParams["font.family"] = _CN_FONT
    return _CN_FONT

def fig_save(fig, name):
    """存 experiments/results/<name>.png 并关闭。"""
    p = os.path.join(RES_DIR, name if name.endswith(".png") else name + ".png")
    fig.savefig(p, dpi=150, bbox_inches="tight")
    print(f"[saved] {p}")
    import matplotlib.pyplot as plt
    plt.close(fig)

if __name__ == "__main__":
    # 冒烟测试：python3 common.py
    print("== local qwen ==")
    print(repr(local_qwen("1+1等于几？只输出数字。", max_new_tokens=8)))
    print("== font ==")
    print(setup_cn_font())
