# Rosen《离散数学及其应用》8e · 选读关键章节 · 实战笔记

> 📅 2026-07-06 · 30 分钟 · 工具书风格（选读非精读）

---

## 📖 选读 5 大核心章

### Ch.1 逻辑与证明 ⭐⭐⭐⭐⭐
- 命题逻辑（非/与/或/蕴涵）
- 谓词逻辑（∀/∃）
- **证明方法**：直接 / 反证 / 归纳 / 穷举

**Python 验证**：
```python
from itertools import product
# 真值表
for p, q in product([True, False], repeat=2):
    print(f"p={p}, q={q}, p→q = {(not p) or q}")
```

### Ch.5 归纳与递归 ⭐⭐⭐⭐
- 数学归纳法
- 强归纳法
- 递归定义（Fibonacci / Tower of Hanoi）

**Fibonacci**：
```python
def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)
# 1,1,2,3,5,8,13,21,34,55
```

### Ch.6 计数（与 Ross Ch.1 重叠）
- 乘法原理
- 排列 / 组合
- 鸽巢原理
- **容斥原理**

### Ch.10 图论 ⭐⭐⭐⭐⭐
- 路径 / 连通
- Euler 路 / Hamilton 圈
- 最短路（Dijkstra）
- 平面图 / 四色定理

**Python**：
```python
import networkx as nx
G = nx.karate_club_graph()
print(f"节点: {G.number_of_nodes()}, 边: {G.number_of_edges()}")
```

### Ch.12 有限状态机 + 自动机
- DFA / NFA
- 正则表达式
- **Turing 机**（计算理论的根基）

---

## 🎯 6 视角

### V04 最小例
| 概念 | 最小例 |
|------|------|
| 命题 | p = "下雨" |
| 归纳 | 1+2+...+n = n(n+1)/2, n=1 |
| 图 | K₂（2 节点 1 边）|

### V10 复杂度 ⭐⭐⭐⭐⭐
- Hamilton 圈：**NP-complete**
- 图染色 k≥3：**NP-complete**
- 最短路：**P**（Dijkstra）
- 同构：**NP**（Babai 2015）

### V15 工程出口
- **正则表达式**（grep / Python re）= 自动机
- **Dijkstra**（Google Maps）= 图论
- **RSA**（HTTPS）= 数论（Ch.4）

### V22 费曼（讲图论）
"妈妈，3 个朋友互通电话，最少打几个电话？答案是 2（A→B, B→C）——这就是'最短路'。"

### V26 失败案例
**Knight Capital 2012**：状态机 = 有限自动机，bug 让状态不一致 → 灾难。

---

## 💡 "啊哈"时刻

### 啊哈 1：鸽巢原理的威力
"n+1 物品放 n 盒子 → 至少 1 盒有 2 个"——简单但强大。

### 啊哈 2：NP-complete 的统一
Hamilton / 染色 / SAT 都"等价难"——一个解决全部解决。

### 啊哈 3：Turing 机 = 计算的极限
Turing 1936 证明：**有些问题计算机永远解不了**（停机问题）。

---

## 📊 自评

| 维度 | 评分 |
|------|------|
| Ch.1/5/6/10/12 掌握 | ⭐⭐⭐⭐ (80%) |
| 阶段 1 工具书 | ✅（按需查阅）|

---

## 🚀 完成！

- ✅ Rosen 关键章完成
- 进入：**阶段 1 全部 5 大模块完成**

---

> 📖 配套：[Ross 全书](../04-Ross概率/) · [LADR 全书](../03-LADR线性代数/) · [Spivak 全书](./) · [柯朗](../01-什么是数学/)
