#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E1 —— 上下文窗口解剖学：token 都花在哪
========================================
问题：一个真实 agent 的上下文由哪些部分构成？各占多少 token？
方法：组装 5 档策略（minimal → kitchen_sink），用 Qwen tokenizer 实测各组件 token 数，
     外加"渐进披露"对照：10 个工具全量 schema vs 名字+一句话清单。
产出：results/e1_anatomy.json + e1_anatomy.png（堆叠条形图）
对应章节：Ch01（窗口解剖）/ Ch04（渐进披露）
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import _get_qwen, save, RES_DIR

# ---------- 组件素材（真实感：一个"深度研究 agent"的上下文） ----------

SYSTEM_PROMPT = """你是一个专业的研究规划器。你的任务是把复杂研究查询分解为具体的搜索子任务。
当前日期时间：2026-08-26T09:30:00+08:00
每个子任务必须包含：唯一 ID、搜索查询、来源类型(web/news/academic)、时间范围、优先级(1-5)。"""

def tool_schema(name, desc, params):
    return {"type": "function", "function": {
        "name": name, "description": desc,
        "parameters": {"type": "object", "properties": params}}}

TOOL_WEB = tool_schema("web_search", "搜索公开网页，返回前 10 条结果标题与摘要", {
    "query": {"type": "string", "description": "搜索关键词"},
    "time_range": {"type": "string", "enum": ["day", "week", "month", "year", "all"]}})

TOOL_NEWS = tool_schema("news_search", "搜索新闻源，适合时事类查询", {
    "query": {"type": "string"}, "region": {"type": "string", "description": "如 cn/us/global"}})

TOOL_ARXIV = tool_schema("arxiv_search", "检索 arXiv 论文（标题/摘要/作者）", {
    "query": {"type": "string"}, "max_results": {"type": "integer", "default": 5}})

def filler_tool(i):
    return tool_schema(f"tool_{i:02d}", f"第 {i} 号辅助工具：演示多工具场景用的填充描述，含较长说明文字。" * 2,
                       {"arg": {"type": "string", "description": f"工具 {i} 的主参数，附示例值与类型说明"}})

ALL_TOOLS = [TOOL_WEB, TOOL_NEWS, TOOL_ARXIV] + [filler_tool(i) for i in range(4, 11)]  # 10 个

RAG_DOCS = [f"[文档 {i}] 2026 年上下文工程研究进展节选（第 {i} 段）：compaction 技术在生产 agent 中已普遍采用，"
            f"实测显示结构化摘要优于自由摘要；上下文利用率超过 70% 后性能退化加速，建议主动压缩而非被动触发。"
            for i in range(1, 7)]  # 6 段假 RAG

HISTORY = [
    {"role": "user", "content": "帮我研究 2026 年 context engineering 的最新进展。"},
    {"role": "assistant", "content": "好的，我先制定搜索计划：(1) 检索 2026 年综述论文；(2) 检索工业界工程博客。是否开始？"},
    {"role": "user", "content": "开始，重点看 compaction 和 memory。"},
    {"role": "assistant", "content": "已创建 3 个子任务：T1 综述检索（arxiv）、T2 工程博客（web）、T3 记忆系统对比（web）。T1 已完成，发现 3 篇关键综述。"},
]

USER_QUERY = "对比一下 compaction 和外部 memory 两条路线的成本，给我一张结论表。"

# ---------- token 计数 ----------

def ntok(text):
    tok, _ = _get_qwen()
    return len(tok(text, add_special_tokens=False).input_ids)

def ntok_msgs(msgs):
    tok, _ = _get_qwen()
    n = 0
    for m in msgs:
        n += len(tok(m["content"], add_special_tokens=False).input_ids) + 4  # role 开销近似
    return n

# ---------- 五档组装策略 ----------

def build(strategy):
    """返回 dict: 组件名 -> 该策略下计入窗口的文本 token 数"""
    comp = {}
    if strategy == "S1_minimal":
        comp["user_query"] = ntok(USER_QUERY)
    elif strategy == "S2_standard":
        comp["system"] = ntok(SYSTEM_PROMPT)
        comp["history(4轮)"] = ntok_msgs(HISTORY)
        comp["user_query"] = ntok(USER_QUERY)
    elif strategy == "S3_tools3":
        comp["system"] = ntok(SYSTEM_PROMPT)
        comp["tools×3"] = sum(ntok(json.dumps(t, ensure_ascii=False)) for t in ALL_TOOLS[:3])
        comp["history(4轮)"] = ntok_msgs(HISTORY)
        comp["user_query"] = ntok(USER_QUERY)
    elif strategy == "S4_kitchen_sink":
        comp["system"] = ntok(SYSTEM_PROMPT)
        comp["tools×10全量"] = sum(ntok(json.dumps(t, ensure_ascii=False)) for t in ALL_TOOLS)
        comp["RAG×6段"] = sum(ntok(d) for d in RAG_DOCS)
        comp["history(4轮)"] = ntok_msgs(HISTORY)
        comp["user_query"] = ntok(USER_QUERY)
    elif strategy == "S5_progressive":  # 渐进披露：10 工具只给一行清单
        comp["system"] = ntok(SYSTEM_PROMPT)
        comp["tools×10清单(L1)"] = ntok("\n".join(
            f"- {t['function']['name']}: {t['function']['description'][:24]}" for t in ALL_TOOLS))
        comp["history(4轮)"] = ntok_msgs(HISTORY)
        comp["user_query"] = ntok(USER_QUERY)
    return comp

def main():
    strategies = ["S1_minimal", "S2_standard", "S3_tools3",
                  "S4_kitchen_sink", "S5_progressive"]
    data = {s: build(s) for s in strategies}
    for s, comp in data.items():
        print(f"{s:18s} total={sum(comp.values()):5d}  {comp}")

    # 渐进披露对比（关键数字）
    full = sum(ntok(json.dumps(t, ensure_ascii=False)) for t in ALL_TOOLS)
    l1 = ntok("\n".join(f"- {t['function']['name']}: {t['function']['description'][:24]}" for t in ALL_TOOLS))
    ratio = l1 / full * 100
    print(f"\n[渐进披露] 10 工具全量 {full} tok vs L1 清单 {l1} tok = {ratio:.1f}%（省 {100-ratio:.1f}%）")

    save("e1_anatomy", {"strategies": data,
                        "progressive_disclosure": {"full": full, "l1": l1, "percent": round(ratio, 1)},
                        "meta": {"tokenizer": "Qwen2.5", "date": "2026-08-26"}})

    # ---------- 画图：堆叠条形图 ----------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC"]
    plt.rcParams["axes.unicode_minus"] = False

    labels = list(data.keys())
    all_keys = []
    for comp in data.values():
        for k in comp:
            if k not in all_keys:
                all_keys.append(k)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bottom = [0] * len(labels)
    colors = plt.cm.Set2.colors
    for ci, k in enumerate(all_keys):
        vals = [data[l].get(k, 0) for l in labels]
        ax.bar(labels, vals, bottom=bottom, label=k, color=colors[ci % len(colors)])
        bottom = [b + v for b, v in zip(bottom, vals)]
    for i, l in enumerate(labels):
        ax.text(i, bottom[i] + 15, str(bottom[i]), ha="center", fontsize=10, fontweight="bold")
    ax.set_ylabel("tokens")
    ax.set_title("上下文窗口解剖学：五档组装策略的 token 构成（Qwen2.5 tokenizer 实测）")
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    p = os.path.join(RES_DIR, "e1_anatomy.png")
    fig.savefig(p, dpi=150)
    print(f"[saved] {p}")

if __name__ == "__main__":
    main()
