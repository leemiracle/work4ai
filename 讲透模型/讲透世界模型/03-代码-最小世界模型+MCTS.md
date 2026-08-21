---
card_id: WM-03
title: "第 3 幕 · 代码：最小世界模型 + MCTS 规划"
universe: 讲透世界模型
arc_position: 第 3 幕（代码/转变）
status: draft
next_card: WM-04
---

# 💻 第 3 幕 · 代码：gridworld 世界模型 + MCTS

把第 2 幕的 $P(s'|s,a)$ + MCTS 变成可跑代码：让 agent 在已知世界里规划最短路径。

```python
import numpy as np
import heapq, math

# ===== 世界: 5x5 gridworld =====
GRID = np.array([
    [0,0,0,0,0],
    [0,1,1,0,0],   # 1=障碍
    [0,0,0,0,1],
    [1,1,0,1,0],
    [0,0,0,0,0],
])
START, GOAL = (0,0), (4,4)
ACTIONS = [(0,1),(0,-1),(1,0),(-1,0)]  # 右左上下

def transition(s, a):
    """世界模型 P(s'|s,a): 确定性 gridworld."""
    s2 = (s[0]+a[0], s[1]+a[1])
    if not (0<=s2[0]<GRID.shape[0] and 0<=s2[1]<GRID.shape[1]): return s  # 撞墙原地
    if GRID[s2] == 1: return s  # 障碍
    return s2

def reward(s):
    return 1.0 if s == GOAL else -0.01  # 到达+1, 每步小负

# ===== MCTS (UCT) =====
class MCTSNode:
    __slots__ = ['s','parent','action','children','visits','value']
    def __init__(self, s, parent=None, action=None):
        self.s=s; self.parent=parent; self.action=action
        self.children=[]; self.visits=0; self.value=0.0

def uct_select(node, c=1.4):
    """UCT 公式选子节点."""
    logN = math.log(node.visits + 1)
    def score(ch):
        if ch.visits==0: return float('inf')
        return ch.value/ch.visits + c*math.sqrt(logN/ch.visits)
    return max(node.children, key=score)

def rollout(s, max_steps=50):
    """随机 rollout 到终局/上限."""
    for _ in range(max_steps):
        if s==GOAL: return 1.0
        a = ACTIONS[np.random.randint(4)]
        s = transition(s, a)
    return 0.0

def mcts_plan(root_s, iters=500):
    """MCTS 搜索最优第一步."""
    root = MCTSNode(root_s)
    for _ in range(iters):
        # 1. Selection
        node = root
        while node.children and node.visits>0:
            node = uct_select(node)
        # 2. Expansion
        s = node.s
        if s != GOAL:
            for a in ACTIONS:
                s2 = transition(s, a)
                node.children.append(MCTSNode(s2, node, a))
            node = node.children[np.random.randint(len(node.children))]
        # 3. Simulation
        R = rollout(node.s)
        # 4. Backprop
        while node is not None:
            node.visits += 1
            node.value += R
            node = node.parent
    # 选访问最多的子节点
    best = max(root.children, key=lambda c: c.visits)
    return best.action, root

# ===== 跑通 =====
if __name__ == "__main__":
    np.random.seed(0)
    s = START
    path = [s]
    print("=== MCTS 规划 gridworld ===")
    for step in range(30):
        if s == GOAL:
            print(f"✓ {step} 步到达终点!"); break
        action, root = mcts_plan(s, iters=300)
        s = transition(s, action)
        path.append(s)
        print(f"  step {step}: {path[-2]} --{action}--> {s}")
    else:
        print(f"✗ 未在 30 步内到达, 路径: {path}")
    print(f"路径长度: {len(path)}")
```

## 运行

```bash
python3 讲透世界模型/03-代码-最小世界模型+MCTS.py
```

## 这段代码教什么

1. **世界模型 = transition 函数**：`transition(s,a) -> s'` 就是 $P(s'|s,a)$ 的确定性特例
2. **MCTS 四步**：Selection(UCT) → Expansion → Simulation(rollout) → Backprop
3. **UCT 平衡**：`value/visits + c·sqrt(logN/visits)` 在利用与探索间权衡
4. **规划 = 在脑内搜索**：agent 不真实试错，在世界模型里 rollout

**生产化方向**：transition 学自数据（model-based RL）、用神经网络估值替代随机 rollout、加 progressive widening 处理连续动作。

📌 **下一张卡** → `04-不足-预测的失败模式.md`
