#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E4 · 组装消融：上下文组件怎么拼，决定结构化输出的生死

讲透Context Ch04 的核心实验（复刻 dair-ai 指南 Search Planner 案例）。
四个累积配置（每次只加一块上下文）：
  C0 裸指令      ：只说"转成检索请求"
  C1 +schema 字段表：字段名+类型+必填性（结构宪法）
  C2 +日期注入    ：当前日期 + "相对日期必须解析为绝对日期"（时间锚）
  C3 +JSON 示例   ：再叠一个 worked example（格式示范）

× 8 个自然语言查询（4 个带相对日期、3 个带字段/过滤器歧义、1 个绝对日期）
× {glm-4-flash, Qwen2.5-0.5B}
指标：JSON 合法率 / 必填字段率 / 相对日期解析率与正确率

用法（分块跑，防超时）:
  python3 e4_assembly.py --model glm     # ~1-2 min
  python3 e4_assembly.py --model qwen    # ~10 min（CPU）
  python3 e4_assembly.py --plot          # 汇总出图
"""
import argparse
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import glm, local_qwen, save, RES_DIR

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK"]
plt.rcParams["axes.unicode_minus"] = False

TODAY = "2026-08-26"  # 周三；本周一=08-24

# ---------- 上下文组件 ----------
BARE = "把用户的检索需求转换成一个结构化检索请求。"

SCHEMA = """检索请求的 schema（字段宪法）：
- query: string, 必填——检索关键词（从用户话里提取，不要整句照抄）
- filters: object, 可选——支持 status / priority / assignee / entity 键
- date_range: object, 可选——{"start":"YYYY-MM-DD","end":"YYYY-MM-DD"}
- fields: array, 可选——限定返回字段（如 ["title","author","body"]）
- sort: object, 可选——{"field":..., "order":"asc"|"desc"}
不要发明 schema 之外的字段。"""

DATE_INJ = f"今天是 {TODAY}（星期三）。用户说的相对日期（上周/最近/本季度等）必须解析成绝对日期区间写进 date_range，不允许出现相对表达。"

EXAMPLE = """示例：
用户：上个月修改过的、状态是已发布的页面
输出：{"query":"页面","filters":{"status":"published"},"date_range":{{"start":"2026-07-01","end":"2026-07-31"}},"sort":{{"field":"modified","order":"desc"}}}}"""

CONFIGS = {
    "C0_裸指令": BARE,
    "C1_+schema": f"{BARE}\n\n{SCHEMA}",
    "C2_+日期注入": f"{BARE}\n\n{SCHEMA}\n\n{DATE_INJ}",
    "C3_+示例": f"{BARE}\n\n{SCHEMA}\n\n{DATE_INJ}\n\n{EXAMPLE}",
}

# ---------- 查询（gold 标注） ----------
from datetime import date, timedelta
D = date.fromisoformat
QUERIES = [
    {"q": "上周哪些订单退款了", "rel": ("2026-08-17", "2026-08-23")},          # 上周=前一自然周
    {"q": "今年二季度的活跃用户数", "rel": ("2026-04-01", "2026-06-30")},
    {"q": "3月1日到3月15日之间关闭的bug", "rel": ("2026-03-01", "2026-03-15")},  # 绝对，也应进 date_range
    {"q": "客户acme最近的合同", "rel": ("2026-07-27", "2026-08-26")},           # 最近≈30天
    {"q": "张伟负责的、状态是进行中的项目", "rel": None},
    {"q": "按创建时间倒序排列所有高优先级工单", "rel": None},
    {"q": "搜索提到支付网关的文档，只要正文和作者字段", "rel": None},
    {"q": "优先级至少P2的未分配任务", "rel": None},
]
QWEN_SUBSET = 6  # Qwen 只跑前 6 个（覆盖全部日期型 + 2 个歧义型，控 CPU 时长）

def extract_json(text):
    """宽容提取：代码栅栏里或裸的第一个 {...}。"""
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        text = m.group(1)
    i, j = text.find("{"), text.rfind("}")
    if i < 0 or j <= i:
        return None
    try:
        return json.loads(text[i:j + 1])
    except json.JSONDecodeError:
        return None

def score(text, item):
    """三指标：json 合法 / query 必填 / 日期正确（窗口±1 天容差）。"""
    obj = extract_json(text)
    rec = {"json_ok": obj is not None, "query_ok": False,
           "date_resolved": None, "date_correct": None}
    if obj is None:
        return rec
    rec["query_ok"] = isinstance(obj.get("query"), str) and len(obj["query"]) > 0
    if item["rel"] is not None:
        dr = obj.get("date_range")
        if isinstance(dr, dict) and dr.get("start") and dr.get("end"):
            try:
                s, e = D(str(dr["start"])), D(str(dr["end"]))
                gs, ge = D(item["rel"][0]), D(item["rel"][1])
                rec["date_resolved"] = True
                rec["date_correct"] = (s <= ge + timedelta(days=1)) and (e >= gs - timedelta(days=1))
            except ValueError:
                rec["date_resolved"] = False
        else:
            rec["date_resolved"] = False
    return rec

def run_glm():
    out = {}
    for cname, ctx in CONFIGS.items():
        rows = []
        for item in QUERIES:
            sys_p = f"你是检索规划器。{ctx}"
            r = glm("glm-4-flash", f"用户：{item['q']}\n输出（只输出 JSON）：",
                    system=sys_p, max_tokens=300, temperature=0.0, retries=1)
            rows.append({"q": item["q"], "raw": r["content"][:300],
                         **score(r["content"], item)})
        out[cname] = rows
        ok = sum(x["json_ok"] for x in rows)
        dt = [x["date_correct"] for x in rows if x["date_correct"] is not None]
        print(f"glm {cname}: json {ok}/8  日期对 {sum(1 for d in dt if d)}/{len(dt)}")
    save("e4_glm", {"meta": {"model": "glm-4-flash", "date": TODAY}, "configs": out})

def run_qwen():
    out = {}
    for cname, ctx in CONFIGS.items():
        rows = []
        for item in QUERIES[:QWEN_SUBSET]:
            sys_p = f"你是检索规划器。{ctx}"
            txt = local_qwen(f"用户：{item['q']}\n输出（只输出 JSON）：",
                             system=sys_p, max_new_tokens=176, temperature=0.0)
            rows.append({"q": item["q"], "raw": txt[:300], **score(txt, item)})
        out[cname] = rows
        ok = sum(x["json_ok"] for x in rows)
        dt = [x["date_correct"] for x in rows if x["date_correct"] is not None]
        print(f"qwen {cname}: json {ok}/{QWEN_SUBSET}  日期对 "
              f"{sum(1 for d in dt if d)}/{len(dt)}", flush=True)
    save("e4_qwen", {"meta": {"model": "Qwen2.5-0.5B", "date": TODAY,
                              "note": f"前{QWEN_SUBSET}题（含全部日期型）"},
                     "configs": out})

def _agg(data, n_total):
    """每配置聚合三率。"""
    agg = {}
    for cname, rows in data["configs"].items():
        n = len(rows)
        dates = [r for r in rows if r["date_resolved"] is not None]
        agg[cname] = {
            "n": n,
            "json_rate": round(sum(r["json_ok"] for r in rows) / n, 3),
            "query_rate": round(sum(r["query_ok"] for r in rows) / n, 3),
            "date_rate": (round(sum(1 for r in dates if r["date_correct"]) / len(dates), 3)
                          if dates else None),
        }
    return agg

def plot():
    g = json.load(open(os.path.join(RES_DIR, "e4_glm.json"), encoding="utf-8"))
    q = json.load(open(os.path.join(RES_DIR, "e4_qwen.json"), encoding="utf-8"))
    ag, aq = _agg(g, 8), _agg(q, QWEN_SUBSET)
    names = list(CONFIGS)
    metrics = [("json_rate", "JSON 合法率"), ("query_rate", "必填字段率"), ("date_rate", "相对日期解析正确率")]
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4))
    for ax, (key, title) in zip(axes, metrics):
        xs = range(len(names))
        gv = [ag[c][key] * 100 if ag[c][key] is not None else 0 for c in names]
        qv = [aq[c][key] * 100 if aq[c][key] is not None else 0 for c in names]
        ax.bar([x - 0.2 for x in xs], gv, width=0.4, label="glm-4-flash", color="#2a9d8f")
        ax.bar([x + 0.2 for x in xs], qv, width=0.4, label="Qwen-0.5B", color="#e9c46a")
        for x, v in zip(xs, gv):
            ax.text(x - 0.2, v + 1.5, f"{v:.0f}", ha="center", fontsize=8)
        for x, v in zip(xs, qv):
            ax.text(x + 0.2, v + 1.5, f"{v:.0f}", ha="center", fontsize=8)
        ax.set_xticks(xs)
        ax.set_xticklabels([c.split("_")[0] + "\n" + c.split("_")[1] for c in names], fontsize=8)
        ax.set_ylim(0, 112)
        ax.set_ylabel("%")
        ax.set_title(title, fontsize=10)
        ax.legend(fontsize=8)
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle("E4 · 组装消融：schema 给结构，日期锚给时间，示例给格式——缺谁塌哪块", fontsize=12)
    fig.tight_layout()
    p = os.path.join(os.path.dirname(RES_DIR), "e4_assembly.png")
    fig.savefig(p, dpi=130)
    save("e4_summary", {"glm": ag, "qwen": aq})
    print("落盘:", p)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["glm", "qwen"])
    ap.add_argument("--plot", action="store_true")
    a = ap.parse_args()
    if a.model == "glm":
        run_glm()
    elif a.model == "qwen":
        run_qwen()
    if a.plot:
        plot()
