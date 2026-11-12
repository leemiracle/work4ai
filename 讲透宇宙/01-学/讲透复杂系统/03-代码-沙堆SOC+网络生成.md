---
card_id: CX-03
title: "第 3 幕 · 代码：沙堆 SOC + BA 网络 + 幂律拟合"
universe: 讲透复杂系统
arc_position: 第 3 幕
status: draft
next_card: CX-04
refs: ["Bak/Tang/Wiesenfeld, PRL 1987", "Barabási/Albert, Science 1999", "Clauset, 2009"]
---

# 💻 第 3 幕 · 代码：沙堆 SOC + BA 网络 + 幂律拟合

## 1. Bak 沙堆模型（SOC 的经典演示）

```python
import numpy as np
import collections

class Sandpile:
    """Bak-Tang-Wiesenfeld 沙堆. 自组织到临界."""
    def __init__(self, n=20, threshold=4):
        self.n = n
        self.z = np.zeros((n,n), dtype=int)  # 每格沙粒数
        self.threshold = threshold
        self.avalanche_sizes = []

    def drop(self):
        """随机一格加一粒沙."""
        i, j = np.random.randint(0, self.n, 2)
        self.z[i,j] += 1
        return self._topple(i, j)

    def _topple(self, i, j):
        """递归崩塌, 返回雪崩大小(影响的格子数)."""
        size = 0
        stack = [(i,j)]
        while stack:
            x, y = stack.pop()
            if self.z[x,y] >= self.threshold:
                self.z[x,y] -= 4
                size += 1
                for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                    nx,ny = x+dx,y+dy
                    if 0<=nx<self.n and 0<=ny<self.n:
                        self.z[nx,ny] += 1
                        if self.z[nx,ny] >= self.threshold:
                            stack.append((nx,ny))
        return size

    def run(self, n_drops=10000):
        for _ in range(n_drops):
            s = self.drop()
            if s > 0: self.avalanche_sizes.append(s)

if __name__ == "__main__":
    np.random.seed(0)
    sp = Sandpile(n=15, threshold=4)
    sp.run(n_drops=5000)
    sizes = sp.avalanche_sizes
    print(f"雪崩总数: {len(sizes)}")
    print(f"最大雪崩: {max(sizes)} 格")
    # 雪崩大小分布 -> 应近似 power law (SOC 标志)
    from collections import Counter
    cnt = Counter(sizes)
    xs = sorted(cnt.keys())
    ns = [cnt[x] for x in xs]
    # 简单 log-log 线性拟合(粗略, 严谨用 Clauset 2009 MLE)
    import math
    log_x = [math.log(x) for x in xs if x>0 and cnt[x]>0]
    log_n = [math.log(cnt[x]) for x in xs if x>0 and cnt[x]>0]
    if len(log_x)>2:
        # 最小二乘
        import statistics
        mx = statistics.mean(log_x); my = statistics.mean(log_n)
        num = sum((a-mx)*(b-my) for a,b in zip(log_x,log_n))
        den = sum((a-mx)**2 for a in log_x)
        slope = num/den if den>0 else 0
        print(f"幂律拟合 γ ≈ {-slope:.2f} (SOC 预期 1~2)")
    print(f"\n洞察: 不需调参, 沙堆自发到临界——雪崩大小服从幂律.")
    print(f"这就是'自组织临界': 系统自己找到混沌边缘.")
```

## 2. Barabási-Albert 无标度网络

```python
import numpy as np
import collections

def ba_network(n=1000, m=3):
    """优先连接生成无标度网络."""
    # 初始 m 个节点全互连
    edges = set()
    degree = np.zeros(n, dtype=int)
    for i in range(m):
        for j in range(i+1, m):
            edges.add((i,j)); degree[i]+=1; degree[j]+=1
    # 逐个加入, 概率 ∝ degree
    for new in range(m, n):
        targets = set()
        while len(targets) < m:
            # 选 degree 比例的节点
            probs = degree[:new] / degree[:new].sum()
            t = np.random.choice(new, p=probs)
            targets.add(t)
        for t in targets:
            edges.add((new, t)); degree[new]+=1; degree[t]+=1
    return edges, degree

if __name__ == "__main__":
    np.random.seed(0)
    edges, deg = ba_network(n=500, m=3)
    cnt = collections.Counter(deg)
    xs = sorted(cnt.keys()); ns = [cnt[x] for x in xs]
    print(f"节点: 500, 边: {len(edges)}")
    print(f"度最大 hub: {max(deg)} (无标度特征: 少数 hub)")
    print(f"度最小: {min(deg)}")
    # 度分布幂律拟合
    import math, statistics
    log_x = [math.log(x) for x in xs if x>0 and cnt[x]>0]
    log_n = [math.log(cnt[x]) for x in xs if x>0 and cnt[x]>0]
    if len(log_x)>2:
        mx = statistics.mean(log_x); my = statistics.mean(log_n)
        slope = sum((a-mx)*(b-my) for a,b in zip(log_x,log_n)) / sum((a-mx)**2 for a in log_x)
        print(f"度分布幂律 γ ≈ {-slope:.2f} (BA 理论值 3)")
    print(f"\n洞察: '富者愈富'机制 → 少数 hub, 大量边缘节点.")
    print(f"这就是互联网/引用网络/代谢网的拓扑.")
```

## 3. Logistic Map 分岔图（混沌）

```python
import numpy as np

def logistic_bifurcation(r_min=2.5, r_max=4.0, n_r=200, n_iter=300, n_discard=200):
    """画 logistic map 的分岔图(数值)."""
    rs = np.linspace(r_min, r_max, n_r)
    result = {}
    for r in rs:
        x = 0.5
        for _ in range(n_discard):  # 丢弃暂态
            x = r * x * (1 - x)
        xs = []
        for _ in range(n_iter):
            x = r * x * (1 - x)
            xs.append(x)
        result[r] = set(round(v, 3) for v in xs)  # 去重看吸引子
    return result

if __name__ == "__main__":
    res = logistic_bifurcation(n_r=100)
    for r in [2.8, 3.2, 3.5, 3.7, 3.9]:
        if r in res:
            n_attractor = len(res[r])
            kind = {1:"不动点",2:"周期2",4:"周期4"}.get(n_attractor, "混沌/复杂")
            print(f"r={r}: 吸引子 {n_attractor} 个 → {kind}")
    print("\n洞察: r 从 2.5→4, 系统从不动点→周期→混沌. Feigenbaum 点(~3.57)后是混沌.")
    print(f"混沌区: 对初始条件敏感(蝴蝶效应).")
```

## 这段代码教什么

1. **沙堆 SOC**：无参数，系统自发到临界，雪崩幂律——**自组织是真的**
2. **BA 网络**：优先连接→无标度→少数 hub——**富者愈富的数学**
3. **Logistic 分岔**：参数微调→不动点/周期/混沌——**简单方程能产生复杂行为**

📌 **下一张卡** → `04-不足-复杂系统的局限.md`
