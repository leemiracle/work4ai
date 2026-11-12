#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""evolve.py — v4 外环：AHE 三观测性支柱的编辑-预测-验证-回滚（手册 11 章）
靶1 SELF      : components/model_route.json（v4 自身路由）
靶2 RL-DOMAIN : ../memory/ctx_policy.json（v3.1 的 CtxPolicy 五维）
支柱① 组件=文件（可 diff/回滚）  ② 失败蒸馏（GLM 归因 + bandit 统计分层证据）  ③ manifest.jsonl 决策清单
v1.1 教训加固（首周期 REVERT×2 的复盘）：
  T1 蒸馏投毒——GLM 把枚举值当字面量回显 → 编辑前枚举校验，非法即回退本地 argmax（零配额、确定性）
  T2 回归靶自我改写——v3.1 demo 内含 ctx-apo 会写回 CTX_F → RL 域回归改用 --task 模式（纯读）
  T3 幂等跳过——建议路由==现行路由时不烧配额直接 SKIP
用法：python3 evolve.py
"""
import json, os, shutil, subprocess, sys, time
import harness_agent as ha

HERE = ha.HERE; COMP = ha.COMP
MANIFEST = os.path.join(ha.LEDGER, "manifest.jsonl")
REG_IDS = ["T1", "T4", "T6"]                      # 回归子集（诚实：演示规模）
VALID_M, VALID_S = {"flash", "5.3", "cascade"}, {"plain", "struct"}

def manifest(rec):
    rec["ts"] = time.strftime("%F %T")
    open(MANIFEST, "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"  [manifest] {rec['target']} {rec['verdict']} :: {rec['prediction']}")

def arm_to_route(arm):
    _, m, s = arm.split("_")                     # "A1_flash_plain" → flash/plain
    return {"model": m, "style": s}

def local_argmax_route():
    """支柱②兜底：从 bandit 统计确定性选优（均值 argmax；平局按期望成本 A1<A2<A4<A3）"""
    stats = ha.load_json(ha.STATS_F, {}); route = {}
    PREF = {"A1": 0, "A2": 1, "A4": 2, "A3": 3}            # 期望成本序：flash直连<cascade<5.3直连
    for ctx, arms in stats.items():
        cand = sorted(((v["r"] / v["n"], PREF[a.split("_")[0]], a)
                       for a, v in arms.items() if v["n"]), key=lambda x: (-x[0], x[1]))
        route[ctx] = arm_to_route(cand[0][2]) if cand else {"model": "flash", "style": "struct"}
    return route

def valid_route(re_):
    return (isinstance(re_, dict) and all(isinstance(v, dict) and v.get("model") in VALID_M
            and v.get("style") in VALID_S for v in re_.values()))

def distill():
    """支柱②：分层证据（bandit 统计 + 失败样本）→ 路由建议；校验失败回退本地 argmax"""
    stats = ha.load_json(ha.STATS_F, {})
    table = {t: {a: round(v["r"]/v["n"], 2) for a, v in d.items() if v["n"]} for t, d in stats.items()}
    fails = [json.loads(l) for l in open(ha.TRAJ_F, encoding="utf-8")][-60:]
    fails = [f for f in fails if f.get("passed") is False][:5]
    sample = "\n".join(f"- task={f['task']} type={f['type']} arm={f['arm']} ans={f.get('answer','')[:40]!r}" for f in fails) or "（无失败样本）"
    q = (f"harness-routing agent 的分臂均值统计：{json.dumps(table, ensure_ascii=False)}\n失败样本：\n{sample}\n"
         '按统计为每类任务选最优路由（model 只能取 flash/5.3/cascade，style 只能取 plain/struct），只返回JSON：'
         '{"failure_pattern":"...","route_edit":{"extract":{"model":"..","style":".."},"solve":{"model":"..","style":".."}}}')
    out = ha.glm_call("flash", q, "struct", max_tokens=300)
    d = ha._parse_json(out) or {}
    if not valid_route(d.get("route_edit")):
        d = {"failure_pattern": d.get("failure_pattern", "蒸馏输出未过枚举校验→本地argmax"),
             "route_edit": local_argmax_route(), "reason": "validated-fallback"}
    print(f"  [distill] {d.get('failure_pattern','?')[:56]} → {json.dumps(d['route_edit'], ensure_ascii=False)}")
    return d

def edit_with_backup(path, new_obj):
    bak = path + ".bak"
    if os.path.exists(path): shutil.copy2(path, bak)
    ha.save_atomic(path, new_obj)
    return bak

def cycle_self(d):
    """靶1：改自身路由 → 回归对比 → 非回归且(更优或更省)才 COMMIT"""
    path = os.path.join(COMP, "model_route.json")
    cur = {k: v for k, v in ha.load_json(path, {}).items() if not k.startswith("_")}
    new_route = {k: v for k, v in d["route_edit"].items() if not k.startswith("_")}
    if new_route == cur:
        manifest({"target": "SELF/model_route.json", "edit": new_route, "prediction": "—",
                  "before": cur, "after": "same", "verdict": "SKIP(no-op)"})
        return
    before = ha.run_subset(REG_IDS); print(f"  [regress-before] {before}")
    bak = edit_with_backup(path, new_route)
    after = ha.run_subset(REG_IDS); print(f"  [regress-after ] {after}")
    ok = after["pass_rate"] >= before["pass_rate"] and (after["cost"] < before["cost"] or after["pass_rate"] > before["pass_rate"])
    if not ok: shutil.copy2(bak, path); print("  [revert] 预测未成立，回滚")
    manifest({"target": "SELF/model_route.json", "edit": new_route,
              "prediction": f"pass 不降({before['pass_rate']}) 且 cost 更优({before['cost']}→)",
              "before": before, "after": after, "verdict": "COMMIT" if ok else "REVERT"})

def cycle_rl_domain():
    """靶2：改 v3.1 的 ctx_policy → --task 纯读回归（demo 含 ctx-apo 会自我改写，v1.1 教训 T2）"""
    path = os.path.join(ha.PARENT, "memory", "ctx_policy.json")
    cp = ha.load_json(path, {}); old = dict(cp)
    cp["topk"] = 3 if cp.get("topk", 2) < 3 else 2          # 2/3 间翻转（可 diff 的最小编辑）
    bak = edit_with_backup(path, cp)
    t0 = time.time()
    r = subprocess.run([sys.executable, os.path.join(ha.PARENT, "rl_agent.py"),
                        "--task", "什么是探索-利用？"], capture_output=True, text=True,
                       timeout=120, cwd=ha.PARENT)
    persisted = ha.load_json(path, {}).get("topk") == cp["topk"]   # 跑完仍在=没被自我改写
    ok = r.returncode == 0 and persisted
    dur = round(time.time() - t0, 1)
    if not ok: shutil.copy2(bak, path); print("  [revert] v3.1 回归失败/被改写，回滚")
    manifest({"target": "RL-DOMAIN/ctx_policy.json", "edit": {"topk": f"{old.get('topk')}->{cp['topk']}"},
              "prediction": "--task 回归 exit=0 且 topk 编辑在运行后仍持久（不被自我改写）",
              "before": {"topk": old.get("topk")}, "after": {"topk": cp["topk"], "exit": r.returncode, "s": dur, "persisted": persisted},
              "verdict": "COMMIT" if ok else "REVERT"})

if __name__ == "__main__":
    print("== AHE 外环：估(distill) → 提取特征 → 优化(edit+预测) → 自动化(验证/回滚) ==")
    d = distill()
    cycle_self(d)
    cycle_rl_domain()
    ha.wrap_up("AHE cycle v1.1 done")
