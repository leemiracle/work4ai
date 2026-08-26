#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E7 ReAct 实验：推理+行动最小循环（Yao et al. 2022, 2210.03629）
==================================================================================
问题：把"计算器"交给模型（ Thought→Action→Observation 循环）比纯心算强多少？
工具（本地实现，模型只能调用不能改）：
  calc[算式]        —— 安全算术求值（白名单字符 + ** / % 支持）
  today[]           —— 返回今天日期
  days_until[日期]  —— 距某日期还有多少天
3 道多步任务 × 两条件（ReAct 循环 vs zero-cot 心算）× glm-4-flash，max 5 步。
产出：results/e7_react.json + e7_react.png + 一条完整轨迹示例
"""
from common import glm, save
import re, time, datetime

TOOLS_DESC = """可用工具：
calc[算式] —— 计算算术表达式，如 calc[(17*23+89)/5]
today[] —— 返回今天的日期
days_until[YYYY-MM-DD] —— 返回今天距该日期还有多少天
"""

REACT_SYS = (
    "你是一个会使用工具的助手。按 ReAct 范式工作，每轮输出：\n"
    "Thought: （一句话分析）\n"
    "Action: 工具名[参数]\n"
    "收到 Observation 后继续。确信得到最终答案时输出：\n"
    "Thought: 我已经得到答案\n"
    "Final Answer: （简洁作答）\n" + TOOLS_DESC
)

def calc(expr):
    if not re.fullmatch(r"[0-9+\-*/().%\s]+", expr or ""):
        return "[calc 拒绝：非法字符]"
    try:
        v = eval(expr, {"__builtins__": {}}, {})
        return f"{v}"
    except Exception as e:
        return f"[calc 错误: {type(e).__name__}]"

def tool_exec(action):
    m = re.match(r"(calc|today|days_until)\[(.*?)\]\s*$", action.strip())
    if not m: return "[未知工具，请用 calc[...]/today[]/days_until[...]]"
    name, arg = m.group(1), m.group(2)
    if name == "calc": return calc(arg)
    if name == "today": return datetime.date.today().isoformat()
    if name == "days_until":
        try:
            return str((datetime.date.fromisoformat(arg) - datetime.date.today()).days)
        except Exception:
            return "[日期格式错误，需 YYYY-MM-DD]"
    return "[未知工具]"

TASKS = [
    ("计算 (17*23+89)/5，结果四舍五入到整数是多少？",
     lambda: round((17 * 23 + 89) / 5)),
    ("今天距今多少天后的 2027-01-01 相差多少天？先查今天日期再算。",
     lambda: (datetime.date(2027, 1, 1) - datetime.date.today()).days),
    ("999 元商品连续三天每天涨 3.3%，三天后是多少元？保留两位小数。",
     lambda: round(999 * 1.033 ** 3, 2)),
]

def react_run(q, max_steps=5):
    """一个 ReAct episode。返回 (final_answer, 轨迹)"""
    msgs = [{"role": "system", "content": REACT_SYS}, {"role": "user", "content": q}]
    traj = []
    for step in range(max_steps):
        # 手动拼 messages（common.glm 只支持单条，这里本地拼 URL 调用）
        import json as _j, urllib.request as _u, os as _o
        body = {"model": "glm-4-flash", "messages": msgs, "max_tokens": 400, "temperature": 0.1}
        req = _u.Request("https://open.bigmodel.cn/api/paas/v4/chat/completions",
                         data=_j.dumps(body).encode(),
                         headers={"Content-Type": "application/json",
                                  "Authorization": f"Bearer {_j.load(open(_o.path.expanduser('~/.local/share/opencode/auth.json')))['zhipuai-coding-plan']['key']}"})
        with _u.urlopen(req, timeout=120) as r:
            out = _j.load(r)
        text = out["choices"][0]["message"]["content"].strip()
        msgs.append({"role": "assistant", "content": text})
        traj.append(text)
        m = re.search(r"Final Answer[:：]\s*(.+)", text, re.S)
        if m: return m.group(1).strip(), traj
        a = re.search(r"Action[:：]\s*(.+)", text)
        if not a:
            msgs.append({"role": "user", "content": "请严格按 Thought/Action 格式，或给出 Final Answer。"})
            traj.append("<<格式提醒>>")
            continue
        obs = tool_exec(a.group(1))
        msgs.append({"role": "user", "content": f"Observation: {obs}"})
        traj.append(f"Observation: {obs}")
    return "[未在步数内完成]", traj

def num_ok(ans, gold):
    m = re.findall(r"-?\d+(?:\.\d+)?", str(ans) or "")
    if not m: return False
    try: return abs(float(m[-1]) - float(gold)) < 0.01
    except: return False

res = {"meta": {"model": "glm-4-flash", "max_steps": 5}, "rows": [], "acc": {"cot": 0, "react": 0}, "traj_example": None}

for q, goldf in TASKS:
    gold = goldf()
    r = glm("glm-4-flash", f"{q}\n请一步一步思考，最后单独一行写'答案是：X'。", max_tokens=512, temperature=0.1, retries=1)
    cot_ok = num_ok(r["content"], gold)
    final, traj = react_run(q)
    re_ok = num_ok(final, gold)
    res["acc"]["cot"] += cot_ok; res["acc"]["react"] += re_ok
    res["rows"].append({"q": q, "gold": str(gold), "cot_ok": cot_ok, "react_ok": re_ok,
                        "react_final": final[:60], "steps": len(traj)})
    if res["traj_example"] is None and re_ok and len(traj) > 2:
        res["traj_example"] = {"q": q, "traj": traj}
    print(f"  {q[:16]}… gold={gold} | CoT {'✓' if cot_ok else '✗'} | ReAct {'✓' if re_ok else '✗'} ({len(traj)}步)", flush=True)

for k in res["acc"]: res["acc"][k] /= len(TASKS)
print(f"== zero-cot {res['acc']['cot']:.0%} vs ReAct {res['acc']['react']:.0%}", flush=True)
save("e7_react", res)

import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Noto Sans CJK SC"
fig, ax = plt.subplots(figsize=(6, 4))
ks = ["cot", "react"]
ax.bar(["零样本 CoT\n（心算）", "ReAct\n（工具循环）"], [res["acc"][k] for k in ks], color=["#4C72B0", "#55A868"], width=0.5)
for i, k in enumerate(ks): ax.text(i, res["acc"][k] + 0.03, f"{res['acc'][k]:.0%}", ha="center")
ax.set_ylabel("3任务准确率"); ax.set_ylim(0, 1.15)
ax.set_title("E7 ReAct：把算术外包给计算器"); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig("results/e7_react.png", dpi=130)
print("[saved] results/e7_react.png")
