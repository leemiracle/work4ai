"""
实验 07 — Agent 的控制论视角: ReAct=开环 / Plan-Execute=MPC / Reflexion=闭环
对应文档: 讲透控制论/07-Agent的控制论视角.md

核心结论:
  1. ReAct = 开环 (每步独立, 不基于"误差"修正)
  2. Plan-Execute = MPC (先想未来, 执行第 1 步)
  3. Reflexion = 闭环反馈 + 记忆 (失败 → 反思 → 下次避免)
  4. 控制论视角统一三种 Agent 范式

跑法: python3 -u 07_agent_cybernetics.py
"""
import math, random
from collections import Counter
random.seed(0)

def P(*a): print(*a, flush=True)

# ============================================================
# Part 1: 三种 Agent 范式 = 三种控制结构
# ============================================================
P("="*70)
P("实验 07 — Agent 的控制论视角")
P("="*70)
P()
P("Part 1: 三种 Agent 范式 vs 三种控制结构")
P("-"*70)
P()
P("范式               | 控制论对应                | 反馈类型")
P("─────────────────────────────────────────────────────────")
P("ReAct              | 开环控制 (每步独立)        | ❌ 无反馈")
P("Plan-Execute       | MPC (先规划后执行)         | 弱反馈")
P("Reflexion          | 闭环 + 记忆 (反思累积)     | ✅ 强反馈")
P()

# ============================================================
# Part 2: 模拟实验 — 用"任务完成度"看三种范式
# ============================================================
P("="*70)
P("Part 2: 模拟实验 — 任务的累积误差")
P("-"*70)
P()

# 模拟一个"多步任务" 的执行过程:
# 每步可能产生误差 e_t, 累积成 total_error
# 三种范式的差异:
#   ReAct:    每步独立, 误差累积 (没有修正机制)
#   Plan-Execute: 偶尔重新规划, 部分修正
#   Reflexion: 每次失败反思, 减小下次误差 (闭环)

def simulate_agent(paradigm, n_tasks=100, max_steps=10):
    """
    paradigm: 'react' / 'plan' / 'reflexion'
    返回每个任务的累积误差
    """
    task_errors = []
    learned_lessons = []  # Reflexion 用
    for task in range(n_tasks):
        cum_error = 0
        for step in range(max_steps):
            # 每步产生基础误差
            base_error = random.uniform(0.5, 1.5)
            if paradigm == "react":
                # 开环: 误差完全累积
                step_error = base_error
            elif paradigm == "plan":
                # MPC 风格: 偶尔重新规划 (每 3 步一次), 误差减半
                if step % 3 == 0:
                    step_error = base_error * 0.5  # 重规划
                else:
                    step_error = base_error
            elif paradigm == "reflexion":
                # 闭环: 应用历史教训
                reduction = 1.0
                for lesson_strength in learned_lessons:
                    reduction *= (1 - lesson_strength * 0.2)
                step_error = base_error * max(reduction, 0.1)
            cum_error += step_error
        task_errors.append(cum_error)
        # Reflexion: 失败时反思, 加入教训
        if paradigm == "reflexion" and cum_error > 5.0:
            learned_lessons.append(random.uniform(0.3, 0.8))
    return task_errors

# 跑实验
results = {}
for paradigm in ["react", "plan", "reflexion"]:
    errors = simulate_agent(paradigm, n_tasks=300)
    results[paradigm] = errors

print(f"{'范式':<14}{'平均累积误差':>14}{'最大误差':>12}{'误差 >10 比例':>16}")
print("-"*56)
for paradigm, name in [("react", "ReAct (开环)"),
                        ("plan", "Plan-Execute (MPC)"),
                        ("reflexion", "Reflexion (闭环)")]:
    errors = results[paradigm]
    avg = sum(errors) / len(errors)
    mx = max(errors)
    fail_rate = sum(1 for e in errors if e > 10) / len(errors)
    print(f"{name:<14}{avg:>14.3f}{mx:>12.3f}{fail_rate:>16.1%}")

P("""
关键观察 (控制论视角):
- ReAct (开环): 平均误差最高 (~10), 误差完全累积
- Plan-Execute (MPC): 比 ReAct 略好 (~7), 部分修正
- Reflexion (闭环 + 记忆): 误差最低 (~5), 失败 → 反思 → 改进
""")

# ============================================================
# Part 3: Reflexion 的收敛性 — 学习曲线
# ============================================================
P("="*70)
P("Part 3: Reflexion 学习曲线 — 闭环反馈的累积效应")
P("-"*70)

# 看 Reflexion 在前 100 任务 vs 后 100 任务的误差
reflexion_errors = results["reflexion"]
first_50 = reflexion_errors[:50]
last_50 = reflexion_errors[-50:]
print(f"\n  Reflexion 前 50 任务: 平均误差 = {sum(first_50)/len(first_50):.3f}")
print(f"  Reflexion 后 50 任务: 平均误差 = {sum(last_50)/len(last_50):.3f}")
print(f"  → 改进 = {(sum(first_50)-sum(last_50))/sum(first_50)*100:.1f}%")
print('  → 教训数累积: 反思让记忆逐步增强')

P("""
这就是 Reflexion 的 [闭环反馈收敛]:
- 早期任务: 教训少, 误差大
- 后期任务: 教训累积, 误差下降
- 数学上等价于 I 控制: ∫e dt 累积, 驱动系统逼近目标

Reflexion 论文 (Shinn 2023) 实测: 在 HotPotQA 上比 ReAct 提升 22 个百分点
""")
