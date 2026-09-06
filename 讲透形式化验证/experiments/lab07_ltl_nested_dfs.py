#!/usr/bin/env python3
"""lab07 · LTL 模型检查：F p 的反例 = ¬p 环，nested-DFS 手推（07 章 §三）。
原理：F p（Eventually p）被违反 ⟺ 存在无穷路径永不为 p ⟺ 图中存在
"从初态可达、全由 ¬p 状态组成的有环子图"（lasso：茎 + 环）。
TS1：s0→s1→s2→s1，p 处处不成立 → 违反（反例 lasso：s0 · (s1 s2)^ω）
TS2：同图但 s2 ⊨ p → ¬p 子图无环 → F p 成立
手推锚点（07 章 §三）：外层 DFS 发现序 s0,s1,s2；内层从 s1 出发经 s2 命中回边 s2→s1 成环。
风格沿用博弈论系列：docstring 讲目的、分段 print 结论、末尾 assert 自检。"""


def nested_dfs(edges, label, init):
    """检查 F p 的违反。返回 (violation, lasso, trace)：
    lasso = (茎 list, 环 list)；trace 记录外层发现序与每次内层搜索的足迹（章内手推表用）。"""
    trace = []
    # ---- 外层 DFS：从 init 收集可达的 ¬p 状态（发现序） ----
    reach_order, seen = [], set()
    stack = [init]
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        reach_order.append(u)
        for v in reversed(edges.get(u, [])):
            if v not in seen and "p" not in label.get(v, set()):
                stack.append(v)
    trace.append(("外层发现序", list(reach_order)))
    # ---- 内层 DFS：对每个 ¬p 可达态 s，在 ¬p 子图里找回到 s 的路 ----
    for s in reach_order:
        inner_seen = set()
        st = [(s, [s])]
        while st:
            u, path = st.pop()
            if u in inner_seen:
                continue
            inner_seen.add(u)
            for v in edges.get(u, []):
                if "p" in label.get(v, set()):
                    continue                     # 内层只在 ¬p 子图里走
                if v == s:                       # 回到起点：环闭合
                    trace.append(("内层命中", s, path + [v]))
                    stem = path[:path.index(s) + 1] if s in path else [s]
                    # 茎 = 从 init 到 s 的最短路（此处图小，直接沿发现序回溯）
                    stem = _stem_to(edges, label, init, s)
                    return True, (stem, path + [v]), trace
                if v not in inner_seen:
                    st.append((v, path + [v]))
        trace.append(("内层无环", s, sorted(inner_seen)))
    return False, None, trace


def _stem_to(edges, label, init, target):
    """init→target 的最短路（只经 ¬p 态）——lasso 的茎。"""
    from collections import deque
    q = deque([(init, [init])])
    visited = {init}
    while q:
        u, path = q.popleft()
        if u == target:
            return path
        for v in edges.get(u, []):
            if v not in visited and "p" not in label.get(v, set()):
                visited.add(v)
                q.append((v, path + [v]))
    return [init]  # 不可达（理论到不了这）


TS_NODES = ["s0", "s1", "s2"]
TS_EDGES = {"s0": ["s1"], "s1": ["s2"], "s2": ["s1"]}

print("=" * 68)
print("E1 · TS1（p 处处不成立）：F p 被违反，nested-DFS 抓环")
print("=" * 68)
lab1 = {s: set() for s in TS_NODES}
v1, lasso1, trace1 = nested_dfs(TS_EDGES, lab1, "s0")
for entry in trace1:
    print(f"  {entry}")
stem, cycle = lasso1
print(f"  反例 lasso：{' → '.join(stem)} · ( {' → '.join(cycle)} )^ω")
print("  读法：茎 s0 → 环 s1→s2→s1 无穷重复，全程 ¬p——'Eventually p' 永不兑现")
assert v1 and stem == ["s0", "s1"] and cycle == ["s1", "s2", "s1"]

print("\n" + "=" * 68)
print("E2 · TS2（s2 ⊨ p）：环被 p 态拦腰截断，F p 成立")
print("=" * 68)
lab2 = {"s0": set(), "s1": set(), "s2": {"p"}}
v2, lasso2, trace2 = nested_dfs(TS_EDGES, lab2, "s0")
for entry in trace2:
    print(f"  {entry}")
print("  读法：s2 是 p 态——内层不许踩，s1 的出边全被剪，¬p 子图 {s0,s1} 无环")
assert not v2

print("\n" + "=" * 68)
print("E3 · 对照：把性质换成 G p（Always p）——反例条件镜像翻转")
print("=" * 68)
# G p 违反 ⟺ 存在可达的 ¬p 态（一个就够，无环要求消失）
reach, stack = set(), ["s0"]
while stack:
    u = stack.pop()
    if u in reach:
        continue
    reach.add(u)
    for v in TS_EDGES.get(u, []):
        stack.append(v)
bad = [s for s in sorted(reach) if "p" not in lab2.get(s, set())]
print(f"  G p 的反例检查 = 找一个可达 ¬p 态：{bad or '无'} → G p {'违反' if bad else '成立'}")
assert bad == ["s0", "s1"]
print("  —— F 查环、G 查点：LTL 两兄弟的检查代价天差地别（07 章 §二/§四）")
print("\nlab07 全部自检通过")
