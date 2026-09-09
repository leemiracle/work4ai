# stage-3 研究方向 D:优化理论 · 研究入门笔记

> stage-3 五大候选之一(ROADMAP §5-D)。本地书:GTM258《Foundation of Optimization》+ 华章71《凸优化教程》。
> 创建:2026-07-01

---

## §0 定位

> **优化 = "在约束下找最好"。凸优化(有全局最优)+ 非凸(landscape/SGD)。这是 ML/工程/经济/控制的公共引擎。**

---

## §1 凸优化(有全局保证)

### 凸性
- **凸集**:$\lambda x+(1-\lambda)y\in C$
- **凸函数**:$f(\lambda x+(1-\lambda)y)\le\lambda f(x)+(1-\lambda)f(y)$
- 凸优化:凸目标 + 凸约束 ⟹ **局部最优=全局最优**

### 对偶(Lagrange)
$$L(x,\lambda)=f(x)+\sum\lambda_i g_i$$
- **强对偶**(凸+Slater):$\min f=\max_\lambda\min_x L$
- **KKT 条件**:最优性的充要(凸情形)

### 经典凸问题
- LP(线性规划)/QP/SOCP/SDP(半定规划)
- 内点法(多项式时间)

---

## §2 非凸优化(stage-1 Spivak 第11章极值 + 现代 ML)

### 梯度下降(stage-1 基础)
$x_{k+1}=x_k-\eta\nabla f(x_k)$
- 凸:$O(1/\sqrt k)$ 或线性收敛(强凸)
- 非凸:收敛到驻点($\nabla f=0$),可能非全局

### 随机/ minibatch SGD
- ML 核心:大规模数据
- 方差减少(SAGA/SVRG)

### landscape(非凸理论)
- 严格鞍:$f$ 在鞍点附近"可逃"
- **PL 条件**($\frac12\|\nabla f\|^2\ge\mu(f-f^*)$):梯度下降线性收敛

---

## §3 推荐书
- **GTM258 Foundation of Optimization**(本地)✅
- **华章71 凸优化教程**(Boyd 风格,本地)✅
- Boyd-Vandenberghe《Convex Optimization》(凸优化圣经)
- Nesterov《Introductory Lectures on Convex Optimization》

---

## §4 飞腾锚点
| 概念 | 飞腾/工程 |
|------|----------|
| 梯度下降 | **神经网络训练**(反向传播,Spivak 第10章链式法则)|
| 凸优化 | 量化研究员(投资组合优化)|
| **Roofline** | 性能优化的"约束优化"(Expert_09)|
| matmul 优化 15× | View_03:分块/向量化=组合优化 |

---

## §5 开放研究问题
1. **非凸优化的全局收敛**:深度网络为何能找到好解?(隐式正则/landscape)
2. **在线学习**:对抗环境下的优化(regret bound)
3. **分布式优化**:多机 SGD(通信瓶颈,Expert_10)
4. **元学习**:学习优化器本身

---

## §6 与其他方向交叉
- A ML:PAC-Bayes/泛化 ⟺ 优化景观
- B 概率:随机优化(SDE 视角)
- C 数值:数值稳定性 ⟺ 优化收敛
- E 信息:最大熵原理

---

## 📌 锁定此方向后:读 Boyd + GTM258,研究"飞腾上低精度 SGD 的收敛性"(FP16/BF16 训练)
