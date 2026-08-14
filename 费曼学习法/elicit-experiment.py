#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
elicit-experiment.py — 激活 LLM 能力手段真实对比实验

用 opencode 配置的智谱 API key（zhipuai-coding-plan），对同一道测试题
跑 8 种激活手段，对比正确率与推理质量。

测试题：3 个工人 3 天刷 3 面墙，9 个工人 9 天刷几面墙？
正确答案：27 面
常见错误：9 面（线性外推错误）

激活手段（按 5W3H 分析文档顺序）：
  1. Zero-shot baseline
  2. Zero-shot CoT ("step by step")
  3. Few-shot CoT（给推理示例）
  4. Expert Persona
  5. Emotional Prompting
  6. Plan-and-Solve
  7. Self-Critique（自我反驳）
  8. Self-Consistency（CoT 5 次采样取多数）
"""

import json
import time
import urllib.request
import urllib.error
import pathlib
import concurrent.futures
import re
from collections import Counter

# ============================================================
# 从 opencode auth.json 读 API key
# ============================================================

AUTH_PATH = pathlib.Path.home() / ".local/share/opencode/auth.json"
AUTH = json.loads(AUTH_PATH.read_text())
API_KEY = AUTH["zhipuai-coding-plan"]["key"]
BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
MODEL = "glm-4-flash"  # 智谱免费档，适合实验

# ============================================================
# 调用智谱 API
# ============================================================

def call_llm(prompt: str, temperature: float = 0.7, max_tokens: int = 600, timeout: int = 60) -> tuple:
    """调用智谱 chat API，返回 (response_text, usage_dict, error)。"""
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
        method="POST",
    )
    try:
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elapsed = time.time() - t0
            return data["choices"][0]["message"]["content"].strip(), data.get("usage", {}), elapsed, None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")[:200]
        return "", {}, 0, f"HTTP {e.code}: {body}"
    except Exception as e:
        return "", {}, 0, str(e)


# ============================================================
# 测试题 + 8 激活手段
# ============================================================

QUESTION = "3 个工人 3 天能刷 3 面墙。9 个工人 9 天能刷几面墙？"
CORRECT = 27

PROMPTS = {
    "1_zero_shot": {
        "label": "Zero-shot baseline",
        "prompt": f"{QUESTION}",
        "temp": 0.0,
    },
    "2_zero_shot_cot": {
        "label": "Zero-shot CoT",
        "prompt": f"{QUESTION}\n\nLet's think step by step.",
        "temp": 0.0,
    },
    "3_few_shot_cot": {
        "label": "Few-shot CoT（给推理示例）",
        "prompt": (
            "例子：2 个工人 2 天刷 2 面墙，4 个工人 4 天能刷几面墙？\n"
            "推理：2人2天刷2面 → 1人2天刷1面 → 1人1天刷0.5面 → "
            "4人4天刷 4×4×0.5 = 8 面。\n答案：8\n\n"
            f"现在答：{QUESTION}\n推理："
        ),
        "temp": 0.0,
    },
    "4_expert_persona": {
        "label": "Expert Persona（数学教授）",
        "prompt": f"You are a math professor with 20 years of teaching experience. Solve carefully:\n\n{QUESTION}",
        "temp": 0.0,
    },
    "5_emotional": {
        "label": "Emotional Prompting",
        "prompt": f"{QUESTION}\n\nThis is very important to my career. Please be careful and precise.",
        "temp": 0.0,
    },
    "6_plan_solve": {
        "label": "Plan-and-Solve",
        "prompt": (
            "Let's first understand the problem and devise a plan. "
            "Then carry out the plan to solve it.\n\n"
            f"问题：{QUESTION}"
        ),
        "temp": 0.0,
    },
    "7_self_critique": {
        "label": "Self-Critique（自我反驳）",
        "prompt": (
            f"{QUESTION}\n\n"
            "先给出你的初步答案和推理。然后扮演 devil's advocate，"
            "给出 2 个最强反驳，最后给最终修正答案。"
        ),
        "temp": 0.0,
    },
    "8_take_deep_breath": {
        "label": "Take a Deep Breath",
        "prompt": f"Take a deep breath and work through this step by step.\n\n{QUESTION}",
        "temp": 0.0,
    },
}


# ============================================================
# 答案抽取
# ============================================================

def extract_answer(text: str):
    """从回答里抽数字答案。优先 '答案是 X' / '最终答案：X' / 最后一个数字。"""
    # 优先匹配"最终答案"/"答案"
    for pat in [r"最终答案[：:]\s*(\d+)", r"答案[：:]\s*(\d+)", r"answer is[：: ]*(\d+)",
                r"是\s*(\d+)\s*面", r"(\d+)\s*面墙"]:
        m = re.findall(pat, text, re.IGNORECASE)
        if m:
            try:
                return int(m[-1])
            except ValueError:
                pass
    # 回退：找所有数字，取最后一个
    nums = re.findall(r"\b(\d+)\b", text)
    if nums:
        try:
            return int(nums[-1])
        except ValueError:
            pass
    return None


# ============================================================
# 跑实验
# ============================================================

def run_one(name, conf):
    label = conf["label"]
    prompt = conf["prompt"]
    temp = conf["temp"]
    resp, usage, dur, err = call_llm(prompt, temperature=temp)
    ans = extract_answer(resp) if not err else None
    return name, label, prompt, resp, usage, dur, err, ans


def main():
    print(f"\n🧪 激活手段对比实验 | 模型 {MODEL} | 题：{QUESTION}")
    print(f"   正确答案：{CORRECT}\n")

    # 并行调 8 个手段
    print("调用 8 个激活手段（并行）...")
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(run_one, n, c): n for n, c in PROMPTS.items()}
        for f in concurrent.futures.as_completed(futures):
            name, label, prompt, resp, usage, dur, err, ans = f.result()
            results[name] = {
                "label": label, "prompt": prompt, "resp": resp,
                "usage": usage, "dur": dur, "err": err, "ans": ans,
                "correct": (ans == CORRECT) if ans is not None else False,
            }
            mark = "✅" if results[name]["correct"] else ("❌" if ans is not None else "❓")
            print(f"  {mark} {name} ({label}): ans={ans} dur={dur:.1f}s")

    # Self-Consistency：对 CoT prompt 采样 5 次
    print("\n调用 Self-Consistency（CoT 5 次采样）...")
    sc_cot_prompt = PROMPTS["2_zero_shot_cot"]["prompt"]
    sc_answers = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(call_llm, sc_cot_prompt, 0.7, 600, 60) for _ in range(5)]
        for f in concurrent.futures.as_completed(futures):
            resp, usage, dur, err = f.result()
            ans = extract_answer(resp) if not err else None
            sc_answers.append({"ans": ans, "resp": resp, "dur": dur, "err": err})
    sc_ans_list = [a["ans"] for a in sc_answers if a["ans"] is not None]
    sc_consensus = Counter(sc_ans_list).most_common(1)[0] if sc_ans_list else (None, 0)
    sc_final = sc_consensus[0]
    sc_agreement = sc_consensus[1]
    print(f"  ✅/❌ self_consistency: 各次={sc_ans_list}, 多数={sc_final} (×{sc_agreement}/5)")

    results["9_self_consistency"] = {
        "label": "Self-Consistency (N=5, T=0.7)",
        "prompt": sc_cot_prompt,
        "resp": " | ".join(f"[{a['ans']}]" for a in sc_answers),
        "usage": {},
        "dur": sum(a["dur"] for a in sc_answers),
        "err": None,
        "ans": sc_final,
        "correct": (sc_final == CORRECT),
        "samples": sc_ans_list,
        "agreement": sc_agreement,
    }

    # ============================================================
    # 输出报告
    # ============================================================

    print(f"\n{'='*70}")
    print(f"  实验结果汇总（正确答案 = {CORRECT}）")
    print(f"{'='*70}")
    print(f"{'手段':<30} {'答案':<8} {'正确?':<8} {'耗时':<8}")
    print("-" * 70)
    for name in sorted(results.keys()):
        r = results[name]
        mark = "✅" if r["correct"] else "❌"
        ans_str = str(r["ans"]) if r["ans"] is not None else "—"
        print(f"{r['label']:<30} {ans_str:<8} {mark:<8} {r['dur']:.1f}s")
    print()

    correct_count = sum(1 for r in results.values() if r["correct"])
    print(f"正确率：{correct_count}/{len(results)} = {100*correct_count/len(results):.0f}%")

    # 写 markdown 报告
    report_lines = [
        f"# 激活 LLM 能力手段 · 真实对比实验",
        f"",
        f"> 模型：`{MODEL}` (智谱 BigModel) | 时间：{time.strftime('%Y-%m-%d %H:%M:%S')} ",
        f"> 测试题：{QUESTION}",
        f"> 正确答案：**{CORRECT}**（推理：3人3天3面 → 1人1天 1/3 面 → 9人9天 = 9×9×(1/3) = 27）",
        f"",
        f"## 结果汇总",
        f"",
        f"| # | 手段 | 答案 | 正确? | 耗时 | tokens |",
        f"|---|---|---|---|---|---|",
    ]
    for i, name in enumerate(sorted(results.keys()), 1):
        r = results[name]
        mark = "✅" if r["correct"] else "❌"
        ans_str = str(r["ans"]) if r["ans"] is not None else "—"
        usage = r.get("usage", {})
        tok = usage.get("total_tokens", "—")
        report_lines.append(f"| {i} | {r['label']} | {ans_str} | {mark} | {r['dur']:.1f}s | {tok} |")

    report_lines += [
        f"",
        f"**正确率**：{correct_count}/{len(results)} = **{100*correct_count/len(results):.0f}%**",
        f"",
        f"## 各手段详细回答",
        f"",
    ]
    for name in sorted(results.keys()):
        r = results[name]
        report_lines += [
            f"### {r['label']} → {r['ans']} {'✅' if r['correct'] else '❌'}",
            f"",
            f"**Prompt**：",
            f"```",
            r["prompt"],
            f"```",
            f"",
            f"**回答**：",
            f"```",
            r["resp"][:1500] if r["resp"] else f"[ERROR: {r['err']}]",
            f"```",
            f"",
        ]

    report_path = pathlib.Path("费曼学习法/lens/激活LLM实验报告.md")
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"\n📄 报告已写：{report_path}")


if __name__ == "__main__":
    main()
