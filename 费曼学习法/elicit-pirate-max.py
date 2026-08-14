#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
elicit-pirate-max.py — 海盗分金极限解放实验

Q3 之前 0/13 全败（max_tokens=8000 截断）。本实验：
  - max_tokens=16000（给推理模型完整思考空间）
  - 16 手段（12 旧 + 4 新：Universal SC / ToT / GoT / Reflexion）
  - 看 glm-5.2 能否被"解放"解出海盗分金 P1（A=98, B=0, C=1, D=0, E=1）

正确答案推导（逆向归纳）:
  E 单独：E=100
  D,E：D 提案，E 反对（D 死 E 得 100）。D 必死除非... 2 海盗 D 提案 D:100 E:0，E 反对，1:1 平局通过（规则含平局）。所以 D:100,E:0。
  C,D,E：C 知道若死 D 得 100。C 需 1 票（自己+1）。给 E 1（E 宁可拿 1 > 0）。C:99,D:0,E:1。
  B,C,D,E：B 知道若死 C:99,E:1。B 需 1 票（自己+1）。给 D 1（D 拿 1>0）。B:99,C:0,D:1,E:0。
  A,B,C,D,E：A 知道若死 B:99,D:1。A 需 2 票（自己+2）。给 C 1, E 1（都拿 1>0）。A:98,B:0,C:1,D:0,E:1。
  答案：A=98, B=0, C=1, D=0, E=1
"""

import json, time, urllib.request, pathlib, concurrent.futures, re
from collections import Counter

AUTH = json.loads(pathlib.Path.home().joinpath(".local/share/opencode/auth.json").read_text())
API_KEY = AUTH["zhipuai-coding-plan"]["key"]
BASE = "https://open.bigmodel.cn/api/paas/v4"
MODEL = "glm-5.2"
MAX_TOKENS = 16000  # 关键：从 8000 翻倍

def call(prompt, temperature=0.0, max_tokens=MAX_TOKENS, timeout=300):
    payload = {"model": MODEL, "messages":[{"role":"user","content":prompt}],
               "temperature": temperature, "max_tokens": max_tokens}
    req = urllib.request.Request(f"{BASE}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type":"application/json","Authorization":f"Bearer {API_KEY}"}, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read())
            u = d.get("usage", {})
            rt = u.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
            return {"resp": d["choices"][0]["message"]["content"].strip(),
                    "rt": rt, "tt": u.get("total_tokens",0), "dur": time.time()-t0, "err": None}
    except Exception as e:
        return {"resp":"", "rt":0, "tt":0, "dur":time.time()-t0, "err":str(e)[:80]}

Q = ("5 个海盗 A B C D E（A 最资深）分 100 金币。规则：A 先提分配方案，"
     "所有人投票，过半数（含平局）通过；否则 A 被扔下海，B 提案。"
     "海盗理性、自私、优先保命、其次贪金、最后爱杀（同等条件下偏好扔人下海）。"
     "A 该提什么方案？用逆向归纳法，给出最终 A-E 各得多少金币。")

CORRECT = {"A":98, "B":0, "C":1, "D":0, "E":1}

PROMPTS = {
    "01_baseline": Q,
    "02_zs_cot": f"{Q}\n\nLet's think step by step using backward induction.",
    "03_fs_cot": f"提示：2 海盗时 D:100,E:0（D 自投通过）。3 海盗 C 需 1 票，给 E 1。以此类推。\n\n{Q}",
    "04_persona": f"You are a game theory professor expert in backward induction. Solve:\n{Q}",
    "05_emotional": f"{Q}\n\nThis determines my game theory grade. Be extremely rigorous.",
    "06_deep_breath": f"Take a deep breath and work through this with backward induction.\n\n{Q}",
    "07_plan_solve": f"Plan: solve 2-pirate case first, then 3, 4, 5. Execute.\n\n{Q}",
    "08_least_to_most": f"Solve incrementally: (a) 2 pirates (b) 3 (c) 4 (d) 5. Use each result in next.\n\n{Q}",
    "09_self_critique": f"{Q}\n\nAfter answering, find the strongest objection to your solution, then refine.",
    "10_tot": f"Explore 3 candidate allocations for A, evaluate each by backward induction, pick the one A prefers most.\n\n{Q}",
    "11_got": f"Analyze from 3 angles (backward induction / Nash equilibrium / coalition formation), then synthesize.\n\n{Q}",
    "12_reflexion": f"{Q}\n\nFirst give a draft. Then critique 'where might my backward induction be wrong?'. Then give final.",
    "13_verify": f"{Q}\n\nAfter solving, verify: would each voter rationally accept? Check ties and killing preference.",
    "14_constitutional": f"Principles: (1) backward induction from E-alone (2) voter accepts if better than being killed (3) ties favor proposer.\n\n{Q}",
    "15_multi_agent": f"Three experts (game theorist / logician / economist) independently solve, then reconcile.\n\n{Q}",
}

def parse_pirate(text):
    """从回答抽 A-E 分配。"""
    if not text: return None
    alloc = {}
    # 多种格式：A=98 / A:98 / A 得 98 / A 分 98
    for who in "ABCDE":
        m = re.search(rf"{who}\s*[=：:得分配]\s*(\d+)", text)
        if m: alloc[who] = int(m.group(1))
    if len(alloc) == 5: return alloc
    # 回退：找 "A:98, B:0, C:1, D:0, E:1" 整体
    m = re.search(r"A\D{1,3}(\d+)\D{1,5}B\D{1,3}(\d+)\D{1,5}C\D{1,3}(\d+)\D{1,5}D\D{1,3}(\d+)\D{1,5}E\D{1,3}(\d+)", text)
    if m:
        return dict(zip("ABCDE", map(int, m.groups())))
    return None

def is_correct(alloc):
    return alloc == CORRECT

def main():
    print(f"\n🏴‍☠️ Q3 海盗分金极限实验 | glm-5.2 | max_tokens={MAX_TOKENS}")
    print(f"   正确答案：A=98 B=0 C=1 D=0 E=1（逆向归纳）\n")
    print(f"并行调用 {len(PROMPTS)} 手段 + Self-Consistency 3 采样...")

    # 准备任务
    tasks = [(k, p, 0.0) for k, p in PROMPTS.items()]
    for i in range(3):
        tasks.append((f"16_sc_{i+1}", PROMPTS["02_zs_cot"], 0.7))

    results = {}
    t_start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(call, p, t): k for k, p, t in tasks}
        for fut in concurrent.futures.as_completed(futures):
            k = futures[fut]
            r = fut.result()
            results[k] = r
            if k.startswith("16_"):
                continue
            alloc = parse_pirate(r["resp"])
            mark = "✅" if is_correct(alloc) else ("❓" if alloc is None else "❌")
            alloc_str = "/".join(f"{x}={alloc[x]}" for x in "ABCDE") if alloc else "(抽取失败)"
            print(f"  {mark} {k:<18} {alloc_str:<30} rt={r['rt']:<6} dur={r['dur']:.0f}s")

    # self-consistency
    sc = [parse_pirate(results[f"16_sc_{i+1}"]["resp"]) for i in range(3)]
    sc_valid = [s for s in sc if s]
    sc_consensus = Counter(tuple(sorted(s.items())) for s in sc_valid).most_common(1)
    print(f"\n  Self-Consistency: 各次={sc}, 有效={len(sc_valid)}/3")

    # 汇总
    correct_methods = []
    print(f"\n{'='*70}")
    print(f"  解放结果汇总（{time.time()-t_start:.0f}s 总耗时）")
    print(f"{'='*70}")
    for k in sorted(results.keys()):
        if k.startswith("16_"): continue
        r = results[k]
        alloc = parse_pirate(r["resp"])
        ok = is_correct(alloc)
        if ok: correct_methods.append(k)
        mark = "✅" if ok else ("❓" if alloc is None else "❌")
        alloc_str = ",".join(f"{x}{alloc[x]}" for x in "ABCDE") if alloc else "抽取失败"
        print(f"  {mark} {k:<20} {alloc_str:<25} rt={r['rt']:<6} tt={r['tt']:<6} dur={r['dur']:.0f}s")

    print(f"\n🎯 解放手段数：{len(correct_methods)}/{len(PROMPTS)} = {100*len(correct_methods)/len(PROMPTS):.0f}%")
    if correct_methods:
        print(f"   成功手段：{', '.join(correct_methods)}")
    # 成本最低的成功手段
    ok_results = [(k, results[k]) for k in correct_methods]
    if ok_results:
        cheapest = min(ok_results, key=lambda x: x[1]["tt"])
        print(f"   💰 最省 token：{cheapest[0]} ({cheapest[1]['tt']} tokens, {cheapest[1]['dur']:.0f}s)")

    # 报告
    lines = [f"# 海盗分金极限解放实验", "", f"> glm-5.2 | max_tokens={MAX_TOKENS} | {time.strftime('%Y-%m-%d %H:%M')}",
             f"> 正确：A=98 B=0 C=1 D=0 E=1", "", "## 结果", ""]
    for k in sorted(results.keys()):
        if k.startswith("16_"): continue
        r = results[k]
        alloc = parse_pirate(r["resp"])
        ok = is_correct(alloc)
        lines.append(f"### {k} {'✅' if ok else '❌'} (rt={r['rt']}, dur={r['dur']:.0f}s)")
        lines.append(f"抽取: {alloc}")
        lines.append(f"```"); lines.append(r["resp"][:2000] if r["resp"] else f"[err: {r['err']}]"); lines.append("```"); lines.append("")
    pathlib.Path("费曼学习法/lens/海盗分金极限实验.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n📄 费曼学习法/lens/海盗分金极限实验.md")

if __name__ == "__main__":
    main()
