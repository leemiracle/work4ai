#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""harness_agent.py — HarnessRL v4：RL agent 融合全部 harness 技术（手册 12 章 → 六组件）
内环 = 配置即动作空间的 contextual UCB1（臂 = harness 配置：模型路由/提示风格/cascade）
外环 = evolve.py（AHE 编辑-预测-验证-回滚，编辑靶含自身组件与 v3.1 的 ctx_policy）
宪法：纯标准库 · 凭证读 opencode auth.json（绝不硬编码）· 账本只追加 · 诚实边界见 DESIGN.md
用法：python3 harness_agent.py demo
"""
import json, math, os, re, sys, time, urllib.request, copy

HERE   = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
COMP   = os.path.join(HERE, "components")
LEDGER = os.path.join(HERE, "ledger"); os.makedirs(LEDGER, exist_ok=True)
TRAJ_F, STATS_F, PROG_F = (os.path.join(LEDGER, x) for x in ("trajectory.jsonl", "bandit_stats.json", "progress.md"))

# ── 凭证与端点（双端点路由 = 手册 08/09 章；实测 2026-08-17）─────────────────
AUTH_F = os.path.expanduser("~/.local/share/opencode/auth.json")
KEY = json.load(open(AUTH_F))["zhipuai-coding-plan"]["key"]
EP_FLASH = "https://open.bigmodel.cn/api/paas/v4/chat/completions"        # glm-4-flash（免费档）
EP_G53   = "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions" # glm-5.3（coding plan）
COST = {"flash": 1.0, "5.3": 8.0}   # 符号计费权重（近似积分比，非真实价格——诚实标注）
ALLOWED_EPS = {EP_FLASH, EP_G53}

def log_safe(t): return math.log(max(t, 2))          # v3.1 血泪：防 UCB log 崩溃
def save_atomic(f, obj):                              # 05 章：tmp+rename 原子写
    tmp = f + ".tmp"; open(tmp, "w", encoding="utf-8").write(json.dumps(obj, ensure_ascii=False, indent=1)); os.replace(tmp, f)
def load_json(f, d):
    try: return json.load(open(f, encoding="utf-8"))
    except Exception: return d

# ── L 组件：生命周期钩子（fail-closed + 审计 = 手册 03 章）──────────────────
CALLS_MADE = {"flash": 0, "5.3": 0}
G53_CAP = 10                                          # E 终止条件 3：成本熔断
def authorize(endpoint):
    ok = endpoint in ALLOWED_EPS and CALLS_MADE["5.3"] < G53_CAP
    print(f"  [audit] {endpoint.rsplit('/',3)[-3]}/... -> {'ALLOW' if ok else 'DENY(fail-closed)'}")
    return ok

# ── C 组件：上下文预算（components/ctx_budget.json = 手册 04 章）────────────
CTX_BUDGET = load_json(os.path.join(COMP, "ctx_budget.json"), {})
def apply_ctx_budget(prompt):
    cap = int(CTX_BUDGET.get("max_prompt_chars", 4000))
    return prompt if len(prompt) <= cap else prompt[:cap] + "\n[ctx-budget truncated]"

# ── T 组件：GLM 调用工具（schema、方言、重试 = 手册 03/09 章）────────────────
def glm_call(model, q, style, max_tokens=None):
    endpoint = EP_FLASH if model == "flash" else EP_G53
    if not authorize(endpoint): return None
    if style == "struct":
        content = f"角色：精确执行器\n任务：{q}\n输出：严格按要求，无多余文字"
    else:
        content = q
    body = {"model": "glm-4-flash" if model == "flash" else "glm-5.3",
            "messages": [{"role": "user", "content": apply_ctx_budget(content)}],
            "max_tokens": max_tokens or (200 if model == "flash" else 1024),
            "temperature": 0.1}
    if model == "5.3":
        body["reasoning_effort"] = "low"               # 09 章：思考不可关，只能降档
    req = urllib.request.Request(endpoint, data=json.dumps(body).encode(),
          headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                CALLS_MADE[model] += 1
                return json.loads(r.read())["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt == 2: print(f"  [tool-error] {model}: {e}"); return None
            time.sleep(1.5)

# ── V 组件：验证金字塔（L1 精确匹配 / L2 JSON schema = 手册 06 章）───────────
def _norm(s): return re.sub(r"\s+", "", str(s))
def _parse_json(text):
    text = re.sub(r"```(json)?", "", text or "")
    m = re.search(r"[\[{].*[\]}]", text, re.S)
    if not m: return None
    try: return json.loads(m.group())
    except Exception: return None
def verify_l1(answer, expected):
    if answer is None: return False
    if isinstance(expected, dict):
        got = _parse_json(answer)
        return isinstance(got, dict) and all(_norm(got.get(k)) == _norm(v) for k, v in expected.items())
    return _norm(expected) in _norm(answer) or _norm(answer) == _norm(expected)
def verify_l2(answer):                                  # schema 合法性（能 L1 不升 L2）
    return _parse_json(answer) is not None

# ── 任务电池（L1 可判；诚实：演示规模）──────────────────────────────────────
TASKS = [
 {"id":"T1","type":"extract","q":'从这句话抽取并只返回JSON：张三在字节跳动当工程师。格式 {"name":..,"company":..}','ans':{"name":"张三","company":"字节跳动"}},
 {"id":"T2","type":"extract","q":'从这句话抽取并只返回JSON：李四在腾讯做产品经理。格式 {"name":..,"company":..}','ans':{"name":"李四","company":"腾讯"}},
 {"id":"T3","type":"extract","q":'从这句话抽取并只返回JSON：王五就职于阿里巴巴。格式 {"name":..,"company":..}','ans':{"name":"王五","company":"阿里巴巴"}},
 {"id":"T4","type":"solve","q":"计算 123+456，只回答阿拉伯数字","ans":"579"},
 {"id":"T5","type":"solve","q":"计算 17*23，只回答阿拉伯数字","ans":"391"},
 {"id":"T6","type":"solve","q":'鸡兔同笼：35头94脚。只返回JSON {"chicken":..,"rabbit":..}','ans':{"chicken":23,"rabbit":12}},
]
ARMS = ["A1_flash_plain", "A2_flash_struct", "A3_glm53_plain", "A4_cascade_struct"]
def run_arm(arm, task):
    """执行一个 harness 配置（E：单任务 turn 上限=2，cascade 两跳封顶）"""
    def one(model, style): return glm_call(model, task["q"], style)
    if arm == "A1_flash_plain":  calls = [("flash", one("flash", "plain"))]
    elif arm == "A2_flash_struct": calls = [("flash", one("flash", "struct"))]
    elif arm == "A3_glm53_plain":  calls = [("5.3",  one("5.3", "plain"))]
    else:                                          # A4 cascade（手册 08 章：预判+后验止损）
        a = one("flash", "struct")
        calls = [("flash", a)]
        if not verify_l1(a, task["ans"]):
            b = one("5.3", "struct"); calls.append(("5.3", b))
    answer = calls[-1][1]
    passed = verify_l1(answer, task["ans"]) and (not isinstance(task["ans"], dict) or verify_l2(answer))
    cost = sum(COST[m] for m, _ in calls)
    return {"arm": arm, "answer": (answer or "")[:60], "passed": passed, "cost": cost,
            "reward": round(2.0 * passed - 0.2 * cost, 3), "models_used": [m for m, _ in calls]}

# ── S 组件：账本（只追加 = 手册 05 章铁律 #9）───────────────────────────────
def append_traj(rec):
    rec["ts"] = time.strftime("%F %T"); open(TRAJ_F, "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")

# ── 内环：contextual UCB1（臂=harness 配置 = 手册 11 章内环）─────────────────
def run_battery(rounds=3):
    stats = load_json(STATS_F, {})                     # 跨进程持久（Q 表思路同 v3.1）
    total = sum(s["n"] for v in stats.values() for s in [v]) or 1
    print(f"== HarnessRL v4 battery：{rounds} rounds × {len(TASKS)} tasks × {len(ARMS)} arms ==")
    for rnd in range(rounds):
        for t in TASKS:
            ctx = t["type"]; ctxs = stats.setdefault(ctx, {a: {"n":0,"r":0.0} for a in ARMS})
            unseen = [a for a in ARMS if ctxs[a]["n"] == 0]
            if unseen: arm = unseen[0]                 # 每臂先拉一次（探索保底）
            else:
                arm = max(ARMS, key=lambda a: ctxs[a]["r"]/ctxs[a]["n"] + 1.0*math.sqrt(log_safe(total)/ctxs[a]["n"]))
            out = run_arm(arm, t); total += 1
            s = ctxs[arm]; s["n"] += 1; s["r"] = round(s["r"] + out["reward"], 3)
            append_traj({"task": t["id"], "type": ctx, **out})
            print(f"  R{rnd+1} {t['id']}[{ctx}] {arm:<18} pass={out['passed']} cost={out['cost']} r={out['reward']:+.2f} ans={out['answer'][:30]!r}")
    save_atomic(STATS_F, stats); report(stats)

def report(stats):
    print("\n== 学到的路由（内环策略）==")
    for ctx, arms in stats.items():
        best = max((a for a in ARMS if arms[a]["n"]), key=lambda a: arms[a]["r"]/arms[a]["n"], default="-")
        rows = ", ".join(f"{a}:{arms[a]['r']/max(arms[a]['n'],1):+.2f}(n={arms[a]['n']})" for a in ARMS if arms[a]["n"])
        print(f"  {ctx:<8} → 最优={best}  [{rows}]")
    print(f"  配额消耗：flash={CALLS_MADE['flash']} 5.3={CALLS_MADE['5.3']}（cap={G53_CAP}）")

# ── 回归入口（外环 evolve.py 复用：按 model_route.json 确定性路由）──────────
def route_to_arm(m, s):
    if m == "cascade": return "A4_cascade_struct"
    if m == "flash":   return "A1_flash_plain" if s == "plain" else "A2_flash_struct"
    return "A3_glm53_plain"
def run_subset(ids):
    route = load_json(os.path.join(COMP, "model_route.json"), {})
    hits, cost = 0, 0.0
    for t in TASKS:
        if t["id"] not in ids: continue
        arm_cfg = route.get(t["type"], {})
        out = run_arm(route_to_arm(arm_cfg.get("model", "flash"), arm_cfg.get("style", "plain")), t)
        hits += out["passed"]; cost += out["cost"]
        append_traj({"task": t["id"], "type": t["type"], "phase": "regression", **out})
    return {"pass_rate": round(hits / len(ids), 3), "cost": round(cost, 2)}

# ── E+07 章：START 仪式 / 完备性自检 / WRAP UP ──────────────────────────────
def harness_init():
    print("== 六组件完备性矩阵（手册 03 章）==")
    for c, w in [("E 循环","run_battery 三终止:自然/max_rounds/配额熔断"),("T 工具","GLM_CALL 白名单+schema+预算"),
                 ("C 上下文",f"ctx_budget={CTX_BUDGET.get('max_prompt_chars')}c"),("S 状态","trajectory.jsonl 追加+stats 原子写"),
                 ("L 钩子","authorize fail-closed+审计"),("V 验证","L1 精确匹配+L2 schema")]:
        print(f"  ✓ {c}: {w}")
    for f in ["AGENTS.md", "feature_list.json", "progress.md"]:          # 父目录四件套（07 章）
        assert os.path.exists(os.path.join(PARENT, f)), f"缺 {f}"
def wrap_up(note):
    open(PROG_F, "a", encoding="utf-8").write(f"\n## {time.strftime('%F %T')}\n{note}\n")
    print(f"[WRAP UP] {note}")

if __name__ == "__main__":
    harness_init()
    if sys.argv[1:] == ["demo"]: run_battery(rounds=3); wrap_up("battery 3 rounds done")
    elif sys.argv[1:] == ["regress"]: print(run_subset(sys.argv[2:] or ["T1","T4","T6"]))
