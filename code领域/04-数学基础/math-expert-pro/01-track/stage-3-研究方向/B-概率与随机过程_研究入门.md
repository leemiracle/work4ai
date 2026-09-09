# stage-3 研究方向 B:概率与随机过程 · 研究入门笔记

> stage-3 五大候选之一(ROADMAP §5-B)。本地书:GTM113(Karatzas-Shreve《Brownian Motion》)/ Loève(GTM045/046)/ Shiryaev(GTM095)。
> 创建:2026-07-01

---

## §0 定位

> **从 stage-1 Ross(初等概率)+ stage-2 Royden(测度)升级到随机过程:马尔可夫/鞅/布朗/SDE——这是量化/扩散模型/物理的根基。**

---

## §1 五大核心主题

### 1. 马尔可夫链(stage-1 Ross 延伸)
- 转移矩阵 $P$;无记忆性
- **平稳分布** $\pi$(满足 $\pi P=\pi$)
- 遍历定理:时间平均 ⟶ $\pi$
- **应用**:PageRank/MCMC/排队(Expert_10)

### 2. 鞅(公平博弈)
- $E[X_{n+1}|\mathcal F_n]=X_n$(鞅)/ $\le$(超鞅)/ $\ge$(亚鞅)
- **停时定理**(Doob):可选停时下鞅收敛
- **Azuma-Hoeffding**:鞅差的集中不等式
- **应用**:金融定价/算法分析

### 3. 布朗运动(连续时间随机过程)⭐
- $B_t$ 高斯增量,$B_t-B_s\sim N(0,t-s)$
- 处处连续但**处处不可微**(Spivak 第9章 |x| 的"终极版")
- 物理粒子运动的极限(爱因斯坦 1905)

### 4. 随机微分方程 SDE / Itô 微积分 ⭐⭐
$$dX_t=\mu(X_t,t)dt+\sigma(X_t,t)dB_t$$
- **Itô 引理**(链式法则的随机版):$df=\mu' dt+\sigma' dB+\frac12\sigma^2 f''dt$(多出 $\frac12$ 项!)
- Black-Scholes 期权定价(SDE 应用)
- 扩散模型的根基(逆向 SDE)

### 5. 扩散模型理论(2020 现代生成模型)
- DDPM = 训练一个网络预测逆向 SDE
- **理论**:前向 SDE 加噪 ⟶ 逆向 SDE 去噪 ⟺ 生成
- 与 stage-3 D(优化)+ A(ML)交叉

---

## §2 推荐书(本地)
- **GTM113 Karatzas-Shreve《Brownian Motion and Stochastic Calculus》**(布朗运动圣经)✅
- **Loève GTM045/046《Probability Theory》**(概率百科)✅
- **Shiryaev GTM095《Probability》**(概率严格教材)✅
- Oksendal《Stochastic Differential Equations》(SDE 入门)
- Billingsley《Convergence of Probability Measures》

---

## §3 飞腾锚点
| 概念 | 飞腾 |
|------|------|
| 马尔可夫链 | 排队(Expert_10 分布式负载)|
| 蒙特卡洛/MCMC | 大规模采样推理(Expert_05)|
| 布朗运动 | 物理/金融仿真 |
| 扩散模型 | 生成 AI(Expert_05 推理,无 BF16 的挑战)|

---

## §4 开放研究问题
1. **扩散模型理论**:DDPM 收敛速率/最优采样步数
2. **Itô vs Stratonovich**:物理建模选哪个?
3. **大偏差**:稀有事件的概率衰减(保险/金融)
4. **随机优化**:SGD 的 SDE 极限(与 D 优化交叉)

---

## §5 与其他方向交叉
- A ML:扩散模型(概率+ML 最热交叉)
- C 数值:SDE 数值解(Euler-Maruyama/Milstein)
- D 优化:SGD = 随机过程
- E 信息:最大熵原理/信息 Bottleneck

---

## 📌 锁定后:读 Karatzas-Shreve,研究"扩散模型在飞腾无 BF16 环境的采样效率"(逆向 SDE 的工程实现)
