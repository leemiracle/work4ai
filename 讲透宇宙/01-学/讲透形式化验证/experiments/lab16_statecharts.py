#!/usr/bin/env python3
"""lab16 · 状态图:mini 状态图引擎(guard=guardrail)+ 奖励机器 Q-learning(16 章 §二/§四)。
E0 显式 FSM 的验证 = 可达性:状态图把系统写成显式转移表,验证退化为 BFS——线性时间,
   P 格(对比 07 章 LTL 模型检测的 PSPACE:"性质公式 × 系统"的联合爆炸在显式小机器上不存在)。
E1 guard = guardrail:agent 编排机(idle→planning→executing→reviewing→done),LLM 只能
   "提议事件",引擎三判决:未建模事件 → 拒;guard 假 → 拒(状态保持,零副作用);否则放行。
   这正是本库 omega-guard 工程 monitor 的 enforce 语义(fail-closed:拒绝即保持原状态)。
E2 奖励机器(Reward Machine, Icarte et al. ICML'18/JAIR'22):把"先 A 再 B 再 C"的
   非马尔可夫任务装进自动机 u0-a→u1-b→u2-c→u3,状态取乘积(位置×RM 状态)使奖励
   马尔可夫化;对比 sparse(只有终态奖励)vs RM-shaped(每条 RM 边 +1)的 Q-learning。
风格沿用系列:docstring 讲目的、分段 print 结论、末尾 assert 自检。"""
from collections import deque
import random

# ================= E0+E1 · mini 状态图引擎 =================

class Machine:
    """显式转移表 {state: {event: (target, guard, action)}}。
    guard: (ctx, payload) → bool;action: (ctx, payload) → None(只准改 ctx)。"""

    def __init__(self, initial, table, ctx=None):
        self.state, self.table, self.ctx = initial, table, ctx or {}
        self.log = []

    def send(self, event, payload=None):
        row = self.table[self.state].get(event)
        if row is None:                                   # 判决 1:未建模事件
            self.log.append((self.state, event, "✗ 未建模事件 → 拒绝(fail-closed)"))
            return False
        target, guard, action = row
        if guard is not None and not guard(self.ctx, payload):   # 判决 2:guard 拒
            self.log.append((self.state, event,
                             f"✗ guard `{guard.__name__}` 拒绝 → 状态保持 {self.state}(零副作用)"))
            return False
        if action is not None:                            # 判决 3:放行
            action(self.ctx, payload)
        prev, self.state = self.state, target
        self.log.append((prev, event, f"→ {target} ✓"))
        return True

def reachable(initial, table):
    """显式 FSM 的验证=可达性:从初态 BFS(忽略 guard = 过近似,坏处是过报,不漏报)。
    线性时间 O(|V|+|E|)——状态图的"写下来即受检"。"""
    seen, dq = {initial}, deque([initial])
    while dq:
        v = dq.popleft()
        for _ev, (t, _g, _a) in table.get(v, {}).items():
            if t not in seen:
                seen.add(t); dq.append(t)
    return seen

print("=" * 68)
print("E0 · 显式 FSM 的验证 = 可达性(线性时间,P 格)")
print("=" * 68)

def build_orchestrator():
    def tool_allowed(ctx, payload):  return payload in ("read_file", "list_dir", "net_fetch")
    def budget_left(ctx, payload):   return ctx["budget"] > 0
    def steps_within(ctx, payload):  return ctx["steps"] <= ctx["max_steps"]
    def human_ok(ctx, payload):      return ctx["steps"] > 0
    def use_budget(ctx, payload):    ctx["budget"] -= 1; ctx["steps"] += 1
    def count_step(ctx, payload):    ctx["steps"] += 1
    return {
        "idle":      {"start": ("planning", lambda c, p: p is not None and len(str(p)) > 0, None)},
        "planning":  {"plan_ready": ("executing", budget_left, None)},
        "executing": {"tool":   ("executing", tool_allowed, use_budget),
                      "submit": ("reviewing", steps_within, count_step)},
        "reviewing": {"approve": ("done", human_ok, None),
                      "revise":  ("planning", budget_left, None)},
        "done":      {},
        "archived":  {},   # 孤儿状态:设计上没有任何迁移指向它 → 不可达
    }

TABLE = build_orchestrator()
reach = reachable("idle", TABLE)
print(f"编排机状态:{sorted(TABLE)}")
print(f"从初态 idle 可达:{sorted(reach)}")
print(f"不可达:{sorted(set(TABLE) - reach)} —— 'archived' 无入边,死配置一眼看出")
assert "archived" not in reach and reach == {"idle", "planning", "executing", "reviewing", "done"}

print("\n" + "=" * 68)
print("E1 · guard = guardrail:LLM 提议事件,guid 裁决;拒绝即保持原状态")
print("=" * 68)
m = Machine("idle", TABLE, ctx={"budget": 3, "steps": 0, "max_steps": 4})
proposals = [("start", "分析用户上传的日志"), ("plan_ready", None),
             ("tool", "read_file"),        # 放行
             ("tool", "delete_db"),        # guard 拒:不在允许表
             ("tool", "net_fetch"),        # 放行
             ("tool", "rm -rf /"),         # guard 拒:不在允许表
             ("self_destruct", None),      # 未建模事件 → 拒
             ("submit", None), ("approve", None)]
print("LLM 提议序列:", [f"{e}({p})" if p else e for e, p in proposals], "\n")
for ev, payload in proposals:
    m.send(ev, payload)
for prev, ev, msg in m.log:
    print(f"  [{prev:<9}] --{ev}-- {msg}")
rejected = [l for l in m.log if "✗" in l[2]]
accepted = [l for l in m.log if "✓" in l[2]]
print(f"\n放行 {len(accepted)} 条,拦截 {len(rejected)} 条(delete_db/rm-rf 被 guard 拒、"
      f"self_destruct 未建模拒)——三条危险提议全部钉在 executing,状态机零副作用")
assert m.state == "done" and len(rejected) == 3 and len(accepted) == 6
assert any("delete_db" not in l[2] and "tool_allowed" in l[2] for l in rejected)
print("→ E1 自检通过:确定性骨架包住非确定性模型——LLM 提议,状态机裁决(omega-guard 的 enforce 形状)")

# ================= E2 · 奖励机器 gridworld =================
print("\n" + "=" * 68)
print("E2 · 奖励机器:非马尔可夫奖励 → 自动机 × 乘积 MDP(Icarte et al. ICML'18)")
print("=" * 68)
N = 6
A, B, C, START = (0, 5), (5, 0), (5, 5), (0, 0)
ACTIONS = ("up", "down", "left", "right")
RM_EDGES = {("u0", "a"): "u1", ("u1", "b"): "u2", ("u2", "c"): "u3"}
RM_DONE = "u3"

def label(pos):
    return "a" if pos == A else "b" if pos == B else "c" if pos == C else ""

def rm_step(u, lab):
    return RM_EDGES.get((u, lab), u)          # 不匹配则自环:顺序错了不推进

def move(pos, a):
    r, c = pos
    if a == "up":    r = max(r - 1, 0)
    elif a == "down": r = min(r + 1, N - 1)
    elif a == "left": c = max(c - 1, 0)
    else:             c = min(c + 1, N - 1)
    return (r, c)

print(f"任务:6×6 网格,依次到 A{A} → B{B} → C{C}(顺序错 = 白去;最优 20 步)")
print("RM:u0 --a--> u1 --b--> u2 --c--> u3(done);落错格子自环不推进")
print("乘积 MDP:36 位置 × 4 RM 状态 = 144 状态(vs 不带记忆的 36)——奖励变马尔可夫\n")

def q_learn(reward_fn, episodes=8000, seed=1, alpha=0.25, gamma=0.95, cap=200):
    """表格 Q-learning,状态 = (位置, RM 状态),动作 4 向;ε 从 0.5 衰减到 0.05。
    reward_fn(u,u2) 给 RM 转移奖励。返回 (前200幕成功数, 90%可靠幕, Q)。"""
    rng = random.Random(seed)
    Q = {}
    ninety = None
    window = deque(maxlen=100)
    early = 0
    for ep in range(episodes):
        eps = max(0.05, 0.5 * 0.999 ** ep)
        pos, u, steps, done_ep = START, "u0", 0, False
        while steps < cap and u != RM_DONE:
            if rng.random() < eps:
                a = rng.choice(ACTIONS)
            else:
                opts = [(Q.get(((pos, u), a), 0.0), a) for a in ACTIONS]
                best = max(v for v, _ in opts)
                a = rng.choice([x for v, x in opts if v == best])
            pos2 = move(pos, a)
            u2 = rm_step(u, label(pos2))
            r = reward_fn(u, u2)
            nxt = [Q.get(((pos2, u2), b), 0.0) for b in ACTIONS]   # 下一状态最优动作价值
            k = ((pos, u), a)
            Q[k] = Q.get(k, 0.0) + alpha * (r + gamma * max(nxt) - Q.get(k, 0.0))
            pos, u = pos2, u2
            steps += 1
            if u == RM_DONE:
                done_ep = True
        if ep < 200:
            early += done_ep
        window.append(done_ep)
        if ninety is None and len(window) == 100 and sum(window) >= 90:
            ninety = ep
    return early, ninety, Q

def greedy_rollout(Q):
    rng = random.Random(0)
    pos, u, steps = START, "u0", 0
    while u != RM_DONE and steps < 80:
        opts = [(Q.get(((pos, u), a), 0.0), a) for a in ACTIONS]
        best = max(v for v, _ in opts)
        a = rng.choice([x for v, x in opts if v == best])   # 平手随机破缺,避免"永远向上"的死循环
        pos2 = move(pos, a)
        pos, u = pos2, rm_step(u, label(pos2))
        steps += 1
    return steps, u == RM_DONE

def report(name, res):
    early, ninety, Q = res
    steps, ok = greedy_rollout(Q)
    print(f"[{name:<6}] 前200幕成功 {early:3d} 次 | 滑动100幕成功率≥90% = 第 {str(ninety) if ninety is not None else '未达'} 幕 |"
          f" 最终贪心策略 {steps} 步{'到达 C ✓' if ok else '未解 ✗'}")
    return early, ninety, ok, steps

print("对比(sparse=只有终态奖励;RM-shaped=每条 RM 边 +1,总回报 3 vs 1):")
sp = report("sparse", q_learn(lambda u, u2: 1.0 if u2 == RM_DONE and u != RM_DONE else 0.0))
rm = report("RM形", q_learn(lambda u, u2: 1.0 if u2 != u else 0.0))

print("\n读数:RM 把 20 步的延迟奖励拆成 3 段(每段 ≤10 步)的近奖励,信用分配被自动机结构砍薄;")
print("两者最终都能解到 20 步最优——'乘积状态使奖励马尔可夫化'是共同前提,shaped 快在收敛速度。")
assert rm[0] > sp[0], "RM-shaped 早期应更常成功"
assert sp[1] is not None and rm[1] is not None and rm[1] < sp[1], "两者都应稳定解出且 RM 更快到 90%"
assert sp[2] and rm[2] and sp[3] <= 22 and rm[3] <= 22, "最终策略都应 ≤22 步(最优 20)"
print("→ E2 自检通过:规格(人/LLM 写的'先A再B再C')→ 自动机 → 乘积 MDP → shaped 奖励——")
print("   与 01 章'奖励作为形式对象'同向:奖励从 ad-hoc 代码变成可检验的形式结构")

print("\nlab16 全部自检通过")
