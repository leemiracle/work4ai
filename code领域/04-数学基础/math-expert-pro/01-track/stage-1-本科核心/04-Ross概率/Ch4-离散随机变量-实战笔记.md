# Ross 9e Ch.4 离散随机变量 · 实战学习笔记

> 📅 2026-07-06 · 30 分钟 · 6 视角：V04+V14+V22+V25+V26+V24
> 接续 [Ch.3 Bayes](Ch3-Bayes-实战笔记.md)

---

## 🎬 视频热身（5 min）— Harvard Stat 110 Lecture 8-10

**Blitzstein 洞察**：从"事件"到"变量"——随机变量 X 是把"事件"翻译成"数"的函数。

---

## 📖 Ch.4 章节（精读 15 min）

### 4.1 随机变量定义
$X: S \to \mathbb{R}$——把样本映射到实数的函数。

### 4.2 CDF
$F(x) = P(X \leq x)$

### 4.4-4.6 期望 + 方差
- $E[X] = \sum x P(X=x)$
- $\text{Var}(X) = E[X^2] - (E[X])^2$
- 线性：$E[aX+b] = aE[X]+b$

### 4.7-4.9 经典分布
| 分布 | PMF | E | Var |
|------|-----|---|----|
| Bernoulli(p) | $p^x(1-p)^{1-x}$ | p | p(1-p) |
| **Binomial(n,p)** | $\binom{n}{k}p^k(1-p)^{n-k}$ | np | np(1-p) |
| **Poisson(λ)** | $e^{-\lambda}\lambda^k/k!$ | λ | λ |
| Geometric(p) | $(1-p)^{k-1}p$ | 1/p | (1-p)/p² |
| NegBinom(r,p) | $\binom{k-1}{r-1}p^r(1-p)^{k-r}$ | r/p | r(1-p)/p² |
| Hypergeom(N,K,n) | $\binom{K}{k}\binom{N-K}{n-k}/\binom{N}{n}$ | nK/N | — |

---

## 🎯 6 视角应用

### V01 反例：Poisson 近似 Binomial 的边界
- 大 n 小 p 才近似好（np 适中）
- n=10 p=0.5 → 误差大
- n=100 p=0.02 → 误差极小（Python 验证差 < 3e-3）

### V04 最小例
| 概念 | n=2 / 极小例 |
|------|------|
| Bernoulli | 抛 1 次硬币 |
| Binomial(2, 0.5) | 抛 2 次硬币 → {0:0.25, 1:0.5, 2:0.25} |
| Poisson(1) | 单位时间 1 次事件 |

### V14 ML 锚点 ⭐⭐⭐⭐
| 分布 | ML 应用 |
|------|--------|
| Bernoulli | 二分类（sigmoid 输出）|
| Binomial | 多次伯努利（投票）|
| Poisson | 计数回归（点击量预测）|
| Geometric | 强化学习（首次成功步数）|
| NegBinom | 等待 r 次成功（A/B 测试）|

### V22 费曼（讲给妈 Binomial）
"妈妈，抛 3 次硬币 2 次正面的概率？答案是 3/8——因为有 3 种排法（HHT/HTH/THH），每种 1/8。这就是 Binomial。"

### V25 真实数据 ⭐⭐⭐⭐
**Binomial 蒙特卡洛**：10 万次验证
- 理论 E=3.0，样本 2.9970 ✓
- 理论 Var=2.1，样本 2.1035 ✓
- 理论 P(X=3)=0.2668，样本 0.2669 ✓

**Poisson(5) 蒙特卡洛**：E≈5, Var≈5 ✓

### V26 失败案例
**Vioxx 2004**（详见 [失败案例 06](../../../09-crosstext/失败案例档案/06-Vioxx-2004.md)）：
- 用 Binomial 假设"心脏事件独立"
- 实际：服药者心脏风险**强相关**（同人群、同时段）
- Binomial 独立性失效 → 风险低估

### V24 跨书
- **Ross 9e**：例子驱动（球盒/抛硬币）
- **严加安**：测度论严格
- **Feller Vol.1**：历史 + 故事

---

## 🐍 Python 关键验证

```python
import numpy as np
from scipy.stats import binom, poisson

# Binomial 期望方差
n, p = 10, 0.3
print(f"E={n*p}, Var={n*p*(1-p)}")

# Poisson 近似 Binomial（n=100, p=0.02）
for k in [0, 1, 2]:
    print(f"Bin={binom.pmf(k,100,0.02):.6f}, Pois={poisson.pmf(k,2):.6f}")

# 蒙特卡洛 Binomial
np.random.seed(0)
samples = np.random.binomial(10, 0.3, 100000)
print(f"E≈{samples.mean():.4f}, Var≈{samples.var():.4f}")
```

---

## 💡 "啊哈"时刻

### 啊哈 1：Poisson E = Var = λ
**直觉**：方差应该随均值增大而相对变小。
**真实**：Poisson 方差 = 均值。

**意义**：Poisson 是"完全随机"——已知均值，方差唯一确定。这就是为什么 Poisson 适合"完全随机事件流"（如电话呼入、网站点击）。

### 啊哈 2：Poisson 近似 Binomial 的精度
n=100, p=0.02，np=2：
- Binomial P(X=1) = 0.270652
- Poisson P(X=1) = 0.270671
- 差 = 1.84e-5

**洞察**：当 n 大 p 小时，二项 → 泊松近似惊人地好。

### 啊哈 3：所有离散分布的"统一图"
- Bernoulli(p) = Binomial(1, p)
- Binomial = n 次独立 Bernoulli 之和
- Poisson(λ) = Binomial(n, λ/n) 当 n→∞
- Geometric(p) = 首次成功的等待
- NegBinom(r, p) = r 次 Geometric 之和

→ **从 Bernoulli 出发，统一所有离散分布**。

---

## 📊 自评

| 维度 | 自评 |
|------|------|
| Ch.4 概念掌握 | ⭐⭐⭐⭐ (85%) |
| Tao 阶段 | rigorous 中段 |
| 6 视角实战 | V25+V14 最强 |
| 30 分钟 ROI | ⭐⭐⭐⭐⭐ |

---

## 🚀 下一步
- ✅ Ch.4 完成
- ⏳ **Ch.5 连续随机变量**（30 min）—— PDF + 正态/指数/均匀

---

## 📐 接入 13 目录
- ✅ `01-track/stage-1-本科核心/04-Ross概率/Ch4-离散随机变量-实战笔记.md`（本文件）
- 🟡 `04-concepts/` → 待补"概率分布族"
- ✅ V14 ML 锚点 → `10-personal/02-AI锚点法`

---

> 📖 配套：[Ch.3 Bayes](Ch3-Bayes-实战笔记.md) · [Vioxx 失败案例](../../../09-crosstext/失败案例档案/06-Vioxx-2004.md)
