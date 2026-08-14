#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
elicit-glm52.py — glm-5.2（推理模型）激活手段极限实验

glm-5.2 是推理模型（reasoning_tokens 内置 CoT），与 glm-4-flash 行为完全不同。
本实验验证：在已内置 CoT 的强模型上，外显激活手段是否（a）提升（b）冗余（c）干扰？

3 道题（递增难度）:
  1. 工人刷墙（比率推理，正确 27，陷阱 9）
  2. Bertrand 盒（贝叶斯，正确 1/2，陷阱 1/3）
  3. 海盗分金 P1（博弈论，正确 99/0/1/0，LLM 常错）

12 手段 × 3 题 = 36 调用（+ Self-Consistency 9 调用）= 45 并行
"""

import json, time, urllib.request, urllib.error, pathlib, concurrent.futures, re
from collections import Counter

AUTH = json.loads(pathlib.Path.home().joinpath(".local/share/opencode/auth.json").read_text())
API_KEY = AUTH["zhipuai-coding-plan"]["key"]
BASE = "https://open.bigmodel.cn/api/paas/v4"
MODEL = "glm-5.2"

def call(prompt, temperature=0.0, max_tokens=8000, timeout=180):
    payload = {"model": MODEL, "messages":[{"role":"user","content":prompt}],
               "temperature": temperature, "max_tokens": max_tokens}
    req = urllib.request.Request(f"{BASE}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type":"application/json","Authorization":f"Bearer {API_KEY}"},
        method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read())
            usage = d.get("usage", {})
            rt = usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
            return {"resp": d["choices"][0]["message"]["content"].strip(),
                    "reasoning_tokens": rt,
                    "total_tokens": usage.get("total_tokens", 0),
                    "dur": time.time()-t0, "err": None}
    except Exception as e:
        return {"resp":"", "reasoning_tokens":0, "total_tokens":0, "dur":time.time()-t0, "err":str(e)[:100]}

# ===== 3 道题 =====
QUESTIONS = {
    "Q1_walls": {
        "q": "3 个工人 3 天能刷 3 面墙。9 个工人 9 天能刷几面墙？只给最终数字。",
        "correct": "27", "trap": "9 或 81",
    },
    "Q2_bertrand": {
        "q": "3 个盒子：A 含 2 枚金币，B 含 2 枚银币，C 含 1 金 1 银。随机选一个盒子，"
             "摸出一枚是金币。问：选中的是 A 盒（全金）的概率？只给分数。",
        "correct": "2/3", "trap": "1/2 或 1/3",
    },
    "Q3_pirate": {
        "q": "5 个海盗 A B C D E（A 最资深）分 100 金币。规则：A 先提分配方案，"
             "所有人投票，过半数（含平局）通过；否则 A 被扔下海，B 提案。"
             "海盗理性、自私、优先保命、其次贪金、最后爱杀。A 该提什么方案？",
        "correct": "A=98 或 A:99 (给 C/E 各 1)", "trap": "A 平分或 A:96",
    },
}

# ===== 12 手段 =====
def make_prompts(q):
    return {
        "01_baseline": q,
        "02_zs_cot": f"{q}\n\nLet's think step by step.",
        "03_fs_cot": f"例子：2个工人2天刷2面墙，4个工人4天刷几面？推理：1人1天=0.5面，4×4×0.5=8面。\n答案：8\n\n现在：{q}",
        "04_persona": f"You are a Fields Medal mathematician. Solve precisely:\n{q}",
        "05_emotional": f"{q}\n\nThis is critical to my PhD defense. Be extremely careful.",
        "06_deep_breath": f"Take a deep breath and work through this step by step.\n\n{q}",
        "07_plan_solve": f"Let's first understand and devise a plan, then execute.\n\n{q}",
        "08_least_to_most": f"Break into sub-problems first, solve easiest, use results.\n\n{q}",
        "09_self_critique": f"{q}\n\nAfter answering, play devil's advocate: give 2 strongest counter-arguments, then final answer.",
        "10_multi_agent": f"Three experts (mathematician/logician/game theorist) debate this. Show their exchange, then consensus.\n\n{q}",
        "11_verify": f"{q}\n\nAfter answering, verify by an independent method (e.g. plug back / unit test), then give final answer.",
        "12_constitutional": f"Follow these principles: (1) check assumptions (2) consider traps (3) verify before answering.\n\n{q}",
    }

def extract_answer(text):
    # 找分数 / 数字 / 海盗方案
    t = text.lower()
    # 分数
    m = re.findall(r"(\d+/\d+)", text)
    if m: return m[-1]
    # 海盗方案（A=98 / A:99 / A 得 99）
    m = re.search(r"a[=：:]\s*(\d+)", t)
    if m: return f"A={m.group(1)}"
    # 最后数字
    nums = re.findall(r"\b(\d+)\b", text)
    if nums:
        try: return str(int(nums[-1]))
        except: pass
    return "?"

def main():
    print(f"\n🚀 glm-5.2 极限实验 | {len(QUESTIONS)} 题 × 12 手段\n")
    all_results = {}

    # 准备所有任务（3 题 × 12 手段 = 36 + self-consistency 3题×3采样=9 = 45）
    tasks = []
    for qk, qd in QUESTIONS.items():
        prompts = make_prompts(qd["q"])
        for sk, sp in prompts.items():
            tasks.append((qk, sk, sp, 0.0))
        # self-consistency: CoT 3 采样
        for i in range(3):
            tasks.append((qk, f"13_sc_cot_{i+1}", prompts["02_zs_cot"], 0.7))

    print(f"并行调用 {len(tasks)} 次 glm-5.2...")
    results_by_qk = {qk: {} for qk in QUESTIONS}
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        futures = {pool.submit(call, p, t): (qk, sk) for qk, sk, p, t in tasks}
        for fut in concurrent.futures.as_completed(futures):
            qk, sk = futures[fut]
            r = fut.result()
            results_by_qk[qk].setdefault(sk.split("_")[0] if "sc" not in sk else "13_sc", []).append((sk, r))

    # 分析
    for qk, qd in QUESTIONS.items():
        print(f"\n{'='*70}")
        print(f"  {qk} | 正确 = {qd['correct']} | 陷阱 = {qd['trap']}")
        print(f"{'='*70}")
        print(f"{'手段':<22} {'答案':<14} {'对?':<4} {'推理tok':<8} {'总tok':<8} {'耗时':<6}")
        print("-"*70)

        q_results = results_by_qk[qk]
        # 单次手段
        correct_count = 0
        total_shown = 0
        for sk_prefix in ["01","02","03","04","05","06","07","08","09","10","11","12"]:
            entries = q_results.get(sk_prefix, [])
            if not entries: continue
            sk, r = entries[0]
            ans = extract_answer(r["resp"])
            is_correct = qd["correct"].split()[0] in ans or any(c in ans for c in qd["correct"].replace("=","=").split("=")[1:][:1]) if "=" in qd["correct"] else qd["correct"] in ans
            mark = "✅" if is_correct else "❌"
            correct_count += is_correct
            total_shown += 1
            print(f"{sk:<22} {ans[:12]:<14} {mark} {r['reasoning_tokens']:<8} {r['total_tokens']:<8} {r['dur']:<6.1f}s")
        # self-consistency
        sc_entries = q_results.get("13_sc", [])
        if sc_entries:
            sc_ans = [extract_answer(e[1]["resp"]) for e in sc_entries]
            consensus = Counter([a for a in sc_ans if a != "?"]).most_common(1)
            cons_ans = consensus[0][0] if consensus else "?"
            is_correct = qd["correct"] in cons_ans
            correct_count += is_correct
            total_shown += 1
            mark = "✅" if is_correct else "❌"
            total_rt = sum(e[1]["reasoning_tokens"] for e in sc_entries)
            total_tt = sum(e[1]["total_tokens"] for e in sc_entries)
            total_dur = max(e[1]["dur"] for e in sc_entries)  # 并行所以取 max
            print(f"{'13_sc_consistency':<22} {cons_ans[:12]+'('+str(consensus[0][1])+'/3)' if consensus else '?':<14} {mark} {total_rt:<8} {total_tt:<8} {total_dur:<6.1f}s")

        print(f"\n正确率：{correct_count}/{total_shown} = {100*correct_count/max(total_shown,1):.0f}%")

    # 写报告
    print(f"\n📄 报告生成中...")
    lines = [f"# glm-5.2 激活手段极限实验", "", f"> 模型: {MODEL} (推理模型) | 时间: {time.strftime('%Y-%m-%d %H:%M')}", ""]
    for qk, qd in QUESTIONS.items():
        lines += [f"## {qk}", f"题目: {qd['q']}", f"正确: **{qd['correct']}** (陷阱: {qd['trap']})", "",
                  "| 手段 | 答案 | 对? | reasoning_tokens | total_tokens | 耗时 |",
                  "|---|---|---|---|---|---|"]
        q_results = results_by_qk[qk]
        for sk_prefix in ["01","02","03","04","05","06","07","08","09","10","11","12"]:
            entries = q_results.get(sk_prefix, [])
            if not entries: continue
            sk, r = entries[0]
            ans = extract_answer(r["resp"])
            is_correct = qd["correct"] in ans
            lines.append(f"| {sk} | {ans} | {'✅' if is_correct else '❌'} | {r['reasoning_tokens']} | {r['total_tokens']} | {r['dur']:.1f}s |")
        lines.append("")
    pathlib.Path("费曼学习法/lens/glm52实验报告.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ 报告: 费曼学习法/lens/glm52实验报告.md")

if __name__ == "__main__":
    main()
