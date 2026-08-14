#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
elicit-unlock.py — 真正解锁 glm-5.2 海盗分金

之前 3 轮实验结论：单次推理（即使 max_tokens=16000）11/15 卡死。
本轮换根本策略——不是堆手段数，是改变推理结构:

策略 1: 真 4 轮 Least-to-Most（递进对话，每轮小 token，累计远小于单次大 token）
策略 2: max_tokens=32000 baseline（验证是 token 量问题还是路径问题）
策略 3: 真 2 轮 Reflexion（草稿→批判→改，分阶段）
策略 4: ToT 真分支（生成 3 候选独立验证选最优）
策略 5: GoT（已知成功，作 control 对照）

如果策略 1（分解）解锁而策略 2（大 token）不解锁 → 证明瓶颈是推理路径
如果策略 2 解锁 → 证明瓶颈是 token 量
"""

import json, time, urllib.request, pathlib, concurrent.futures, re

AUTH = json.loads(pathlib.Path.home().joinpath(".local/share/opencode/auth.json").read_text())
API_KEY = AUTH["zhipuai-coding-plan"]["key"]
BASE = "https://open.bigmodel.cn/api/paas/v4"
MODEL = "glm-5.2"

def call(prompt, temperature=0.0, max_tokens=8000, timeout=300):
    payload = {"model": MODEL,
               "messages": prompt if isinstance(prompt, list) else [{"role":"user","content":prompt}],
               "temperature": temperature, "max_tokens": max_tokens}
    req = urllib.request.Request(f"{BASE}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type":"application/json","Authorization":f"Bearer {API_KEY}"}, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read())
            u = d.get("usage", {})
            return {"resp": d["choices"][0]["message"]["content"].strip(),
                    "rt": u.get("completion_tokens_details", {}).get("reasoning_tokens", 0),
                    "tt": u.get("total_tokens",0), "dur": time.time()-t0, "err": None}
    except Exception as e:
        return {"resp":"", "rt":0, "tt":0, "dur":time.time()-t0, "err":str(e)[:80]}

Q5 = ("5 个海盗 A B C D E（A 最资深）分 100 金币。规则：A 先提分配方案，"
      "所有人投票，过半数（含平局）通过；否则 A 被扔下海，B 提案。"
      "海盗理性、自私、保命>贪金>爱杀。A 该提什么方案？")
CORRECT = {"A":98,"B":0,"C":1,"D":0,"E":1}
RULES = "规则：提案者分配，全员投票，过半数（含平局）通过否则提案者下海；海盗理性、保命>贪金>爱杀。"

def parse_alloc(text):
    if not text or len(text) < 30: return None
    alloc = {}
    for w in "ABCDE":
        m = re.search(rf"{w}\s*[=：:得分配]\s*(\d+)", text)
        if m: alloc[w] = int(m.group(1))
    return alloc if len(alloc) == 5 else None

# ============================================================
# 5 策略
# ============================================================

def strat_1_l2m_real():
    """真 4 轮 Least-to-Most：每轮解子问题，用前轮答案。"""
    t0 = time.time()
    total_rt = total_tt = 0
    context = "（无前序）"
    rounds_log = []
    subproblems = [
        ("2 海盗 D E", "2 海盗 D（资深）E 分 100。D 提案。"),
        ("3 海盗 C D E", "3 海盗 C（资深）D E 分 100。C 提案。"),
        ("4 海盗 B C D E", "4 海盗 B（资深）C D E 分 100。B 提案。"),
        ("5 海盗 A B C D E", "5 海盗 A（资深）B C D E 分 100。A 提案。"),
    ]
    final = None
    for label, subq in subproblems:
        prompt = f"已知上一轮（少 1 人）的方案：{context}\n\n现在解：{subq}\n{RULES}\n只给最终分配（X=数字 格式）。"
        r = call(prompt, max_tokens=2500, timeout=60)
        total_rt += r["rt"]; total_tt += r["tt"]
        context = r["resp"][-200:] if r["resp"] else "(空)"
        rounds_log.append((label, r["resp"][:150], r["rt"]))
        final = r
    final["rt_total"] = total_rt; final["tt_total"] = total_tt
    final["dur"] = time.time() - t0
    final["rounds"] = rounds_log
    return final

def strat_2_baseline_32k():
    return call(Q5, max_tokens=32000, timeout=300)

def strat_3_reflexion_2round():
    """真 2 轮 Reflexion：草稿→批判→改。"""
    t0 = time.time()
    r1 = call(f"{Q5}\n\n先给一个初步方案和推理。", max_tokens=8000, timeout=120)
    if not r1["resp"]:
        r1["dur_total"] = time.time()-t0; return r1
    r2 = call(
        f"我的初步方案：{r1['resp'][:1500]}\n\n"
        f"找出这个方案在逆向归纳上的具体漏洞（哪一步推理可能错），然后给最终修正方案。\n{RULES}",
        max_tokens=8000, timeout=120
    )
    r2["rt_total"] = r1["rt"] + r2["rt"]
    r2["tt_total"] = r1["tt"] + r2["tt"]
    r2["dur"] = time.time() - t0
    return r2

def strat_4_tot_branches():
    return call(
        f"对下面问题，生成 3 个不同的候选分配方案，每个独立用逆向归纳验证，"
        f"比较后选出 A 收益最高的可行方案。\n\n{Q5}",
        max_tokens=16000, timeout=250
    )

def strat_5_got_control():
    return call(
        f"从 3 个角度独立分析（逆向归纳 / 纳什均衡稳定性 / 联盟形成），然后综合出最终方案。\n\n{Q5}",
        max_tokens=16000, timeout=200
    )


def main():
    print(f"\n🔓 真正解锁实验 | glm-5.2 | 5 策略对照\n")
    print(f"   正确：A=98 B=0 C=1 D=0 E=1\n")

    # 并行跑可独立的策略，串行跑真分解
    print("策略 1（真 4 轮分解，串行）...")
    r1 = strat_1_l2m_real()
    a1 = parse_alloc(r1["resp"])
    print(f"  {'✅' if a1==CORRECT else '❌'} l2m_real: {a1} | 累计 rt={r1['rt_total']} tt={r1['tt_total']} dur={r1['dur']:.0f}s")

    print("\n策略 2-5（并行）...")
    results = {"S1_l2m_real": (r1, a1)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futs = {
            pool.submit(strat_2_baseline_32k): "S2_baseline_32k",
            pool.submit(strat_3_reflexion_2round): "S3_reflexion_2r",
            pool.submit(strat_4_tot_branches): "S4_tot_branches",
            pool.submit(strat_5_got_control): "S5_got_control",
        }
        for f in concurrent.futures.as_completed(futs):
            name = futs[f]
            r = f.result()
            a = parse_alloc(r["resp"])
            mark = "✅" if a == CORRECT else ("❓空" if not r["resp"] or len(r["resp"])<30 else "❌")
            print(f"  {mark} {name}: {a} | rt={r['rt']} tt={r['tt']} dur={r['dur']:.0f}s")
            results[name] = (r, a)

    # 汇总
    print(f"\n{'='*70}")
    print(f"  解锁实验汇总")
    print(f"{'='*70}")
    print(f"{'策略':<22} {'答案':<30} {'对?':<5} {'reasoning':<12} {'总token':<10} {'耗时'}")
    print("-"*70)
    unlock_count = 0
    for name, (r, a) in results.items():
        ok = a == CORRECT
        if ok: unlock_count += 1
        mark = "✅" if ok else ("❓" if a is None else "❌")
        ans_str = "/".join(f"{k}{a[k]}" for k in "ABCDE") if a else ("空输出" if not r["resp"] else "抽取失败")
        rt_key = "rt_total" if "rt_total" in r else "rt"
        tt_key = "tt_total" if "tt_total" in r else "tt"
        print(f"{name:<22} {ans_str:<30} {mark}   {r[rt_key]:<12} {r[tt_key]:<10} {r['dur']:.0f}s")

    print(f"\n🎯 解锁率：{unlock_count}/5")

    # 关键诊断
    print(f"\n{'='*70}")
    print(f"  关键诊断：瓶颈是 token 量 还是 推理路径？")
    print(f"{'='*70}")
    s2 = results.get("S2_baseline_32k", (None, None))[0]
    s1 = results.get("S1_l2m_real", (None, None))[0]
    if s2 and s1:
        if s2["resp"] and len(s2["resp"]) > 30:
            print(f"  S2 baseline@32k 有输出 → 瓶颈可能是 token 量")
        else:
            print(f"  S2 baseline@32k 仍空输出（用了 rt={s2['rt']}）→ 瓶颈是推理路径")
        if s1["resp"] and len(s1["resp"]) > 30:
            print(f"  S1 真 4 轮分解有输出（累计 rt={s1['rt_total']}）→ 分解结构有效")

    # 报告
    lines = [f"# 解锁实验：真分解 vs 大 token", "",
             f"> glm-5.2 | {time.strftime('%Y-%m-%d %H:%M')}", f"> 正确：A=98 B=0 C=1 D=0 E=1", ""]
    for name, (r, a) in results.items():
        ok = a == CORRECT
        rt_key = "rt_total" if "rt_total" in r else "rt"
        lines.append(f"## {name} {'✅' if ok else '❌'} (rt={r[rt_key]}, dur={r['dur']:.0f}s)")
        if "rounds" in r:
            lines.append("### 各轮：")
            for label, snippet, rt in r["rounds"]:
                lines.append(f"- {label} (rt={rt}): {snippet}")
        lines.append(f"### 最终输出：")
        lines.append("```")
        lines.append(r["resp"][:2500] if r["resp"] else "[空/err]")
        lines.append("```"); lines.append("")
    pathlib.Path("费曼学习法/lens/解锁实验-分解vs大token.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n📄 费曼学习法/lens/解锁实验-分解vs大token.md")

if __name__ == "__main__":
    main()
