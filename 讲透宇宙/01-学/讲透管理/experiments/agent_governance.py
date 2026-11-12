"""
AI Agent 治理 —— 把管理学元框架映射到多 Agent 系统 + 协调策略仿真

核心论点: 管理(组织人类)与编排(协调 AI Agent)共享同一套底层问题——
  激励、协调、控制、演化。组织理论是 AI Agent 治理的现成武器库。

管理四职能 ──► Agent 系统对应:
  激励 Incentive  (代理理论/机制设计) ──► 奖励函数 / 激励相容 / Token 经济
  协调 Coordination (组织结构/交易成本) ──► 通信协议 / 角色分工 / 黑板系统
  控制 Control     (控制职能/SPC)        ──► 护栏 / 监控 / 评估 / 人在环(HITL)
  演化 Evolution   (学习型组织/双元)      ──► 强化学习 / 探索-利用 / 记忆

仿真: 同一批任务, 用三种"治理结构"分配给 Agent, 比较效用与成本:
  (A) 科层制 Hierarchical  — 中心调度器(全知), 指派
  (B) 市场制 Market         — 二价拍卖(激励相容), 竞标
  (C) 自组织 Self-org       — 随机/涌现, 无中心
"""
import numpy as np

print("=" * 70)
print("管理四职能 → 多 Agent 系统映射")
print("=" * 70)
mapping = [
    ("激励 Incentive", "代理理论/机制设计/契约", "奖励函数·激励相容·Token 经济", "对齐目标, 防 agent 偷懒/虚报"),
    ("协调 Coordination", "组织结构/交易成本", "通信协议·角色分工·黑板·MCP", "降低协同成本, 防死锁/冲突"),
    ("控制 Control", "控制职能/SPC/BSC", "护栏·监控·评估·HITL· Cedar 策略", "保目标对齐与安全"),
    ("演化 Evolution", "学习型组织/双元/SECI", "RL·探索-利用·记忆·self-improvement", "持续适应, 防能力过时"),
]
for a, b, c, d in mapping:
    print(f"  {a:18s} [{b}]\n      └─► Agent: {c}\n      └─► 目的: {d}\n")

rng = np.random.default_rng(42)
M = 8                            # agent 数
skills = rng.uniform(0.4, 1.0, M)
T = 1000
tasks = rng.uniform(0.2, 1.0, T)


def hierarchical():
    # 中心调度: 总派给技能最高的 agent (贪婪, 造就瓶颈)
    util = 0.0; load = np.zeros(M)
    for tk in tasks:
        best = int(np.argmax(skills))
        util += skills[best] * tk
        load[best] += 1
    util_per_load = util / (load.max() + 1e-9)
    return util, load.max(), load.min(), util_per_load


def market_auction():
    # 二价拍卖: 每任务各 agent 报 skill*tk (如实报), 价高者得, 付第二高价
    util = 0.0; transfer = 0.0; load = np.zeros(M)
    for tk in tasks:
        bids = skills * tk
        w = int(np.argmax(bids))
        price = np.sort(bids)[-2]
        util += skills[w] * tk
        transfer += price
        load[w] += 1
    return util, transfer, load.max(), load.min()


def selforg():
    # 自组织: 随机匹配(无中心), 模拟纯涌现
    util = 0.0; load = np.zeros(M)
    for tk in tasks:
        a = int(rng.integers(M))
        util += skills[a] * tk
        load[a] += 1
    return util, load.max(), load.min()


print("=" * 70)
print("多 Agent 任务分配仿真  (8 agents, 1000 tasks)")
print("=" * 70)
u_h, lmax_h, lmin_h, upl_h = hierarchical()
print(f"  [A 科层制]   总效用={u_h:8.1f}  负载(max/min)={lmax_h:.0f}/{lmin_h:.0f}  "
      f"效用/最大负载={upl_h:.2f}")
u_m, pay_m, lmax_m, lmin_m = market_auction()
print(f"  [B 市场(拍卖)] 总效用={u_m:8.1f}  支付成本={pay_m:7.1f}  "
      f"负载(max/min)={lmax_m:.0f}/{lmin_m:.0f}")
u_s, lmax_s, lmin_s = selforg()
print(f"  [C 自组织]   总效用={u_s:8.1f}  负载(max/min)={lmax_s:.0f}/{lmin_s:.0f}")

print("\n  解读:")
print("  - 科层制: 效用最高, 但负载极度集中(强者过载/弱者闲置)→ 单点瓶颈, 脆弱")
print("  - 市场:   效用≈科层(同样分给最优), 但需支付(激励成本), DSIC 保证诚实")
print("  - 自组织: 无中心开销但效用最低(随机)→ 适合探索, 不适合利用")
print("\n  管理学迁移到 Agent 编排的结论:")
print("  · 利用型任务 → 中心调度/拍卖 (高效率)")
print("  · 探索型任务 → 去中心/自组织 (多样性, 防过早收敛)")
print("  · 即: 组织的'双元(ambidexterity)' = Agent 系统的 explore/exploit!")
print("  · 交易成本启示: 当 agent 间沟通成本 > 内部调度成本, 用'科层'; 否则用'市场'")
