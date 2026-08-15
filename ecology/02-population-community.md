# 第二篇：种群生态学全模型 · 群落生态学

> 生态学数学最密集的部分。几乎所有模型有解析/数值解，是计算/理论生态学的核心。

---

## 六、种群生态学

### 6.1 增长模型

**(1) 指数/马尔萨斯**：$\frac{dN}{dt} = rN \Rightarrow N(t) = N_0 e^{rt}$（J 型曲线）

**(2) 逻辑斯谛（Verhulst 1838）**：
$$\frac{dN}{dt} = rN\left(1 - \frac{N}{K}\right), \quad N(t) = \frac{K}{1 + \frac{K-N_0}{N_0}e^{-rt}}$$
拐点 $N=K/2$。**MSY（最大持续产量）= $rK/4$**（在 $K/2$ 处）——资源管理基础公理（但因不确定性常被批判）。

**(3) 时滞（Hutchinson 1948）**：$\frac{dN}{dt} = rN(t)[1 - N(t-\tau)/K]$ → 时滞过大 → 阻尼振荡/极限环（雪兔-猞猁）。

**(4) 离散 + 混沌（May 1976）**：$N_{t+1} = rN_t(1-N_t/K)$，r 超阈值 → 倍周期分岔 → 混沌。**生态学首次引入混沌理论**。（见实验 `chaos_logistic.py`）

**(5) 随机模型**：出生-死亡过程 + 灭绝概率 → PVA（种群存活力分析）基础。

### 6.2 密度依赖与调节辩论

- 密度依赖（生物因子调节）vs 密度无关（气候学派 Andrewartha-Birch）。
- 现代共识：短期波动多由气候，长期稳态多由密度依赖。

### 6.3 年龄/阶段结构：矩阵模型

**(1) Leslie 矩阵（1945）**：
$$\mathbf{n}_{t+1} = \mathbf{L}\,\mathbf{n}_t, \quad \mathbf{L} = \begin{pmatrix} F_1 & F_2 & \cdots & F_m \\ s_1 & 0 & \cdots & 0 \\ & s_2 & \cdots & \\ & & \ddots & \\ 0 & & s_{m-1} & 0 \end{pmatrix}$$

- **主特征值 λ₁** = 渐近增长率（>1 增长）
- **右特征向量** = 稳定年龄分布；**左特征向量** = 再生值
- **弹性分析**：各 $F_i/s_i$ 对 λ₁ 的贡献 → 指明保护哪个生命阶段最有效
- IUCN 评估、渔业配额的金标准（见实验 `leslie_matrix.py`）

**(2) Lefkovitch 矩阵**：阶段结构（植物/两栖）。
**(3) 生命表**：$l_x, m_x$；$R_0 = \sum l_x m_x$；$r \approx \ln R_0 / T$。

### 6.4 集合种群（Levins 1969）

$$\frac{dp}{dt} = cp(1-p) - ep, \quad p^* = 1 - e/c$$
只有 $c>e$ 才长期存活。→ **栖息地碎片化导致灭绝的数学证明**；保护需维持廊道连通。

### 6.5 Lotka-Volterra 方程族

**(1) 竞争**：
$$\frac{dN_1}{dt} = r_1N_1\frac{K_1 - N_1 - \alpha_{12}N_2}{K_1}$$
零增长等斜线四种组合 → 四种结局（Gause 竞争排斥的数学版）。

**(2) 捕食**：
$$\frac{dN}{dt} = aN - bNP, \quad \frac{dP}{dt} = cNP - dP$$
中性稳定中心，相位差 1/4 周期（雪兔-猞猁百年数据）。

**(3) Holling 功能反应（1959）**：
- Type I 线性 / Type II 双曲饱和 $\frac{aN}{1+ahN}$ / Type III S 型

**(4) 互惠**：LV 加正项需自限，否则无界。

**(5) SIR（Kermack-McKendrick 1927）**：
$$\frac{dS}{dt}=-\beta SI, \quad \frac{dI}{dt}=\beta SI-\gamma I$$
**$R_0 = \beta S/\gamma$**——流行病学起源于生态学。

### 6.6 稳定性分析工具

平衡点处雅可比矩阵特征值实部全负 → 局部稳定。

---

## 七、群落生态学

### 7.1 互作类型（符号矩阵）

| 互作 | 物种1 | 物种2 |
|------|------|------|
| 中性 | 0 | 0 |
| 竞争 | − | − |
| 捕食/寄生 | + | − |
| 互惠 | + | + |
| 偏利 | + | 0 |
| 偏害 | − | 0 |

### 7.2 多样性指数（算法）

- **α**：丰富度 S；**Shannon $H' = -\sum p_i \ln p_i$**；**Simpson $1/\sum p_i^2$**；Pielou 均匀度；Fisher α
- **β**：Whittaker、Bray-Curtis、Sørensen、Jaccard
- **系统发育多样性 PD**（Faith 1992）、功能多样性（Petchey-Gaston、Rao 二次熵）
- **Hubbell 中性理论（2001）**：生态等价 + 随机漂变 + 迁移可解释宏观模式，无需生态位。现代共识：两者并存，尺度决定主导。
- **物种丰度分布 SAD**：对数级数/对数正态/broken-stick

### 7.3 生态位重叠与共存

- Pianka 重叠指数
- **限制相似性**：重叠有上限
- **Tilman R\* 规则**：资源零增长浓度低者赢；不同资源各胜 → 共存

### 7.4 岛屿生物地理学（MacArthur-Wilson 1967）

迁入率↓ 与灭绝率↑ 曲线交点 = 动态平衡物种数 $S^*$。
**物种-面积关系 SAR**：$S = cA^z$，$z \approx 0.25$（岛）/0.15（大陆）——预测栖息地破坏致灭绝的工具。

### 7.5 演替

- 原生 vs 次生；Clements 顶极 vs Gleason 个体论
- Connell-Slatyer 三模型：促进/容忍/抑制
- **Markov 演替模型**：$P(t+1) = P(t)\mathbf{T}$，稳态 = 顶极

### 7.6 关键种与冗余

- **关键种（Paine 1969）**：海獭、*Pisaster* 海星、狼——移除 → 群落剧变
- **生态系统工程师（Jones 1994）**：海狸、蚯蚓、大象

### 7.7 食物网与互作网络

- 连接度 $C = L/S^2$、链长
- **cascade 模型（Cohen）/ niche 模型（Williams-Martinez 2000）**
- 互惠网络**嵌套性**（Bastolla 2009：最小化竞争）
- 模块性、鲁棒性（按度移除的渗流阈值）
- 方法可直接迁移自社交网络/推荐系统的图论
