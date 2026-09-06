#!/usr/bin/env python3
"""lab08 · TLC 式显式检查：两阶段提交玩具模型的 BFS 状态枚举（08 章 §三）。
状态：(rm1, rm2, tm) ∈ {W,P,C,A}²×{COLLECT,COMMIT,ABORT}（4·4·3 = 48 个理论组合）
动作表（TLC 的 next 关系，逐条对应 PlusCal 的标签）：
  ① 任一 RM 在 W 时可单方面 abort（rm: W→A）        [RMPrepared 前的自由退出]
  ② W 的 RM 可 prepare（rm: W→P）                    [投票]
  ③ tm 在 COLLECT 且两 RM 都 P → COMMIT（广播提交）  [全票通过]
  ④ tm 在 COLLECT 且任一 RM 已 A → ABORT（广播中止） [有票退出]
  ⑤ P/C 的 RM 收 commit→C；P/W 的 RM 收 abort→A     [服从决议]
不变式 Atomicity：¬(rm1=C ∧ rm2=A) ∧ ¬(rm1=A ∧ rm2=C)（混合结局不可达）
死锁定义：无后继且非终态（终态 = tm 已决议 ∧ 两 RM 都落定 {C,A}）。

计划手推（08 章原稿）声称"可达 22 态、死锁 {(A,P,COLLECT),(P,A,COLLECT)}"——
与动作④自相矛盾（有④时 (A,P,COLLECT)→ABORT 有后继）。本 lab 先跑后写：
  E1 完整模型（含④）：实测可达 N 态、死锁 0 个、Atomicity 0 反例；
  E2 砍掉④（tm 只认全票，不看弃权）——经典 2PC 阻塞态重现：
     (A,P,COLLECT)/(P,A,COLLECT) 变死锁（tm 等一张永远不来的票）。
两问对照正是 08 章 §三的教学点：死锁检查器抓的不是 bug，是协议设计的裁决时机。
风格沿用博弈论系列：docstring 讲目的、分段 print 结论、末尾 assert 自检。"""
from itertools import product

W, P, C, A = "W", "P", "C", "A"
COLLECT, COMMIT, ABORT = "COLLECT", "COMMIT", "ABORT"


def next_states(s, with_abort_on_any=True):
    """动作①-⑤（with_abort_on_any=False 时砍掉④——E2 的实验变量）。"""
    rm1, rm2, tm = s
    out = set()
    if tm == COLLECT:
        if rm1 == W:
            out.add((A, rm2, tm))                      # ① 单方面退出
            out.add((P, rm2, tm))                      # ② 投票
        if rm2 == W:
            out.add((rm1, A, tm))
            out.add((rm1, P, tm))
        if rm1 == P and rm2 == P:
            out.add((P, P, COMMIT))                    # ③ 全票 → 提交
        if with_abort_on_any and (rm1 == A or rm2 == A):
            out.add((rm1, rm2, ABORT))                 # ④ 有弃权 → 中止
    elif tm == COMMIT:
        if rm1 in (P, W):
            out.add((C, rm2, tm))                      # ⑤ 服从提交
        if rm2 in (P, W):
            out.add((rm1, C, tm))
    elif tm == ABORT:
        if rm1 in (P, W):
            out.add((A, rm2, tm))                      # ⑤ 服从中止
        if rm2 in (P, W):
            out.add((rm1, A, tm))
    return {t for t in out if t != s}


def is_terminal(s):
    rm1, rm2, tm = s
    return tm in (COMMIT, ABORT) and rm1 in (C, A) and rm2 in (C, A)


def atomicity_ok(s):
    rm1, rm2, _ = s
    return not ((rm1 == C and rm2 == A) or (rm1 == A and rm2 == C))


def bfs_states(with_abort_on_any=True):
    init = (W, W, COLLECT)
    seen, frontier = {init}, [init]
    while frontier:
        s = frontier.pop()
        for t in next_states(s, with_abort_on_any):
            if t not in seen:
                seen.add(t)
                frontier.append(t)
    return seen


def report(name, with_flag):
    seen = bfs_states(with_flag)
    dead = sorted(s for s in seen if not next_states(s, with_flag) and not is_terminal(s))
    bad = [s for s in seen if not atomicity_ok(s)]
    print(f"  可达状态 {len(seen)} 个｜死锁 {len(dead)} 个 {dead}｜Atomicity 反例 {len(bad)} 个")
    return seen, dead, bad


print("=" * 68)
print("E1 · 完整模型（动作①-⑤全开）：TLC 三件套检查")
print("=" * 68)
seen1, dead1, bad1 = report("full", True)
term = sorted(s for s in seen1 if is_terminal(s))
print(f"  终态 {len(term)} 个：{term}")
print("  读数：两 RM 都能到 C（提交）或都到 A（中止）——决议一旦广播，结局对齐")
assert not dead1 and not bad1
assert (C, C, COMMIT) in seen1 and (A, A, ABORT) in seen1

print("\n" + "=" * 68)
print("E2 · 砍掉④（tm 只认全票）：经典 2PC 阻塞态重现")
print("=" * 68)
seen2, dead2, bad2 = report("no4", False)
print("  病理三连：(A,P)/(P,A) 是'一票 A 一票 P——tm 等不到第二张票'（计划手推只料到这两个）；")
print("  (A,A,COLLECT) 是计划也没料到的第三个——双方都单方面弃权，tm 一张票都等不到，同样永堵")
print("  这正是真实 2PC 的阻塞（blocking）缺陷：协调者/伙伴单点故障时的等待死锁，")
print("  也是三阶段提交（3PC）与 Paxos 一系要解决的问题——08 章 §五的出口")
assert dead2 == [(A, A, COLLECT), (A, P, COLLECT), (P, A, COLLECT)]
assert not bad2

print("\n" + "=" * 68)
print("E3 · 理论空间对照：48 组合里只有 N 个可达——'行为'是空间的极小骨架")
print("=" * 68)
all_states = set(product((W, P, C, A), (W, P, C, A), (COLLECT, COMMIT, ABORT)))
print(f"  全空间 {len(all_states)} 态｜完整模型可达 {len(seen1)} 态｜砍④可达 {len(seen2)} 态")
print("  不可达的例子：W 出现在 tm=COMMIT 后（决议前必先全 P）；(C,A,·) 整族（Atomicity）")
assert (C, A, COMMIT) not in seen1 and (W, W, COMMIT) not in seen1
print("\nlab08 全部自检通过")
