---
card_id: LA-03
title: "第 3 幕 · 代码：最小 Reflexion learning agent"
universe: 讲透学习型Agent
arc_position: 第 3 幕（代码/转变）
status: draft
next_card: LA-04
---

# 💻 第 3 幕 · 代码：最小 Reflexion learning agent

L2 学习（不改权重的经验回写）。Agent 解谜题，失败后反思存记忆，下次复用——成功率随尝试次数上升。

```python
import random
import re

# ===== 任务: 猜数字游戏 (简化 demo) =====
TARGET = random.randint(1, 100)

def execute(guess):
    """执行动作, 返回 (是否成功, 反馈)."""
    if guess == TARGET:
        return True, "正确!"
    fb = "更大" if guess < TARGET else "更小"
    return False, f"猜 {guess}, 目标{fb}"

def reflect(history):
    """LLM 风格反思: 从历史抽教训."""
    if not history: return "还没有经验"
    last_guess, fb = history[-1]
    if "更大" in fb:
        return f"教训: 目标 > {last_guess}, 下次猜更大"
    elif "更小" in fb:
        return f"教训: 目标 < {last_guess}, 下次猜更小"
    return "无新教训"

def policy_with_memory(history, reflections, lo=1, hi=100):
    """策略: 用反思缩小范围, 二分."""
    # 应用反思更新边界
    for r in reflections:
        m = re.search(r'> (\d+)', r)
        if m: lo = max(lo, int(m.group(1)))
        m = re.search(r'< (\d+)', r)
        if m: hi = min(hi, int(m.group(1)))
    return (lo + hi) // 2  # 二分

# ===== Reflexion 闭环 =====
def reflexion_agent(max_episodes=3, max_steps=15):
    """多次尝试同一任务, 反思累积."""
    reflections = []
    results = []
    for ep in range(max_episodes):
        history = []
        lo, hi = 1, 100
        solved = False
        for step in range(max_steps):
            guess = policy_with_memory(history, reflections, lo, hi)
            ok, fb = execute(guess)
            history.append((guess, fb))
            if ok:
                solved = True
                results.append((ep, step+1))
                break
            # 更新边界
            if "更大" in fb: lo = max(lo, guess+1)
            else: hi = min(hi, guess-1)
        # episode 结束 -> 反思, 写入记忆
        new_reflect = reflect(history)
        reflections.append(new_reflect)
    return results, reflections

# ===== 对照: 无记忆的基线 =====
def baseline_agent(max_steps=15):
    """无反思, 纯二分."""
    lo, hi = 1, 100
    for step in range(max_steps):
        guess = (lo+hi)//2
        ok, fb = execute(guess)
        if ok: return step+1
        if "更大" in fb: lo=guess+1
        else: hi=guess-1
    return max_steps

# ===== 跑通: 对比学习曲线 =====
if __name__ == "__main__":
    random.seed(42)
    print(f"目标数字: {TARGET}\n")
    print("=== Reflexion agent (3 episodes) ===")
    results, refs = reflexion_agent(max_episodes=3)
    for ep, steps in results:
        print(f"  episode {ep}: {steps} 步解决")
    print("累积反思:")
    for r in refs: print(f"  - {r}")
    print("\n=== 对照实验: 10 个随机目标 ===")
    for trial in range(10):
        global TARGET
        TARGET = random.randint(1,100)
        b = baseline_agent()
        print(f"  trial {trial}: 目标={TARGET}, 基线二分={b} 步")
    print("\n洞察: 猜数字本身简单, 二分已最优. Reflexion 的价值在更难任务(LLM 推理/编程)上才显现.")
    print("此 demo 证明的是'反思→记忆→缩小搜索空间'的机制闭环, 而非具体增益.")
```

## 这段代码教什么

1. **Reflexion 闭环**：执行 → 失败 → 反思（自然语言）→ 写入记忆 → 下次策略更新
2. **语言梯度**：反思是自然语言形式，相当于在 context 空间做梯度下降
3. **不改权重**：纯靠 context（reflections list）累积经验
4. **为什么 demo 看不出大增益**：猜数字太简单，二分已最优。Reflexion 真正的战场是 LLM 编程/推理（搜索空间大、错误模式可命名）

**生产化**：用真 LLM 生成反思、向量库存反思、跨任务迁移反思。

📌 **下一张卡** → `04-不足-学习型Agent失败模式.md`
