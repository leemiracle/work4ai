# 04 · 计量经济学与因果推断：从相关到因果

经济学最深刻的方法论革命是 **"可信性革命"（Credibility Revolution）**——2019/2021 连续诺奖（Banerjee-Duflo-Kremer 实验发展经济学；Card 自然实验；Angrist-Imbens 方法论）。口号：**"Identification is all"**（识别是一切）。

---

## 4.1 因果推断的基本问题

### 潜在结果框架（Neyman-Rubin）

每个个体有两个**潜在结果**：$Y_i(1)$（处理）与 $Y_i(0)$（对照）。**根本问题**：只能观测到一个（接受了处理的那个）。缺的那个就是**反事实**。

**平均处理效应**：$ATE=E[Y(1)-Y(0)]$——永远无法直接计算，只能**识别**（identification）。

### 为什么相关 ≠ 因果

$$
\underbrace{E[Y|D=1]-E[Y|D=0]}_{\text{ observational 差}}=\underbrace{ATE}_{\text{因果}}+\underbrace{\text{选择偏误}}_{\text{混淆}}
$$

例：上大学的人收入高 ≠ 大学**导致**收入高（能力同时影响两者）。

---

## 4.2 经典估计：OLS / IV / GMM

### OLS 与 Gauss-Markov

$$
\hat\beta_{OLS}=(X'X)^{-1}X'y
$$

无偏需要**条件零均值** $E[\varepsilon|X]=0$——**这恰恰是因果识别的核心难题**，不是技术问题。

**代码验证**（模拟）：真实 $\beta_x=2.0$，但 $x$ 受遗漏的"能力"影响：
- OLS 估计 = **2.235**（向上偏误）
- 遗漏变量偏误方向 = $\text{Cov}(x,\text{能力})\times\text{能力的效应}$

### 工具变量 IV / 2SLS

**直觉**：找一个 $Z$，它影响 $x$ 但不直接影响 $y$（除了通过 $x$）。用 $Z$ 的变异"清洗"掉 $x$ 中的内生部分。

**两个核心假设**：
1. **相关性**：$Cov(Z,X)\ne0$（第一阶段 F > 10，Staiger-Stock 法则）
2. **排除限制**：$Cov(Z,\varepsilon)=0$（**不可检验**——这是 IV 的"信仰"）

**两阶段**：
1. 第一阶段：$x=\pi_0+\pi_1 Z+v$，得 $\hat{x}$
2. 第二阶段：$y=\beta_0+\beta_1\hat{x}+u$

**代码验证**：第一阶段 F = **4181**（强工具）。IV 估计修正了 OLS 偏误。

**经典案例**：Angrist (1990) 用越战征兵**抽签**（随机！）估计服役对收入的因果效应；Card (1995) 用"离大学的距离"估计教育回报。

**LATE（Imbens-Angrist 1994）**：IV 只识别**局部**平均处理效应——只对"因 Z 而改变行为"的 compliers 有效，不能外推到整个总体。

### GMM（Hansen 1982）

矩条件 $E[g(\theta_0,data)]=0$ 的最优估计。IV 是特例，是现代计量的统一框架。

---

## 4.3 因果识别的四大武器

### ① DID 双重差分（Difference-in-Differences）

**识别假设**：**平行趋势**——若无政策，处理组与对照组**趋势相同**。

$$
\hat{ATT}=\big(\bar{Y}_{T,post}-\bar{Y}_{T,pre}\big)-\big(\bar{Y}_{C,post}-\bar{Y}_{C,pre}\big)
$$

**代码验证**（模拟，真实 ATT=3.0）：
- 处理组前后差 = 3.45，对照组前后差 = 0.62
- **DID = 2.835** ✓（接近 3.0）
- 政策前趋势差（placebo 检验）= **-0.045** ≈ 0 ✓（平行趋势成立）

**经典应用**：Card-Krueger (1994) 最低工资（NJ vs PA）；中国特色的特区试点评估。

**新进展（2020s）**：Goodman-Bacon 分解揭示多期 DID 的"坏对照"问题；Callaway-Sant'Anna (2021)、Sun-Abraham (2021) 估计量修正。`[econ.EM 2026-08-10]` *Bias-robust causal inference for panel data* 是最新进展。

### ② RDD 断点回归（Regression Discontinuity）

**识别假设**：在阈值附近，个体"是否越线"近似**随机**（无法精确操控）。

$$
\tau_{RDD}=\lim_{x\downarrow0}E[Y|X=x]-\lim_{x\uparrow0}E[Y|X=x]
$$

**Sharp RDD**（越线=必然处理）：局部线性估计。

**代码验证**（模拟，真实 τ=2.0）：阈值 0，窗口 $h=0.3$，局部线性估计 $\hat{\tau}=1.973$ ✓。

**Fuzzy RDD**（越线只是提高处理概率）：用"越线"作处理的 IV。

**经典应用**：选举胜负（Lee 2001）、班级规模（Angrist-Lavy）、奖学金资格线。

**检验**：McCrary 密度检验（阈值附近个体分布应连续——检验操控）。

### ③ 合成控制（Synthetic Control, Abadie）

**适用**：**单一处理单位**（如某州、某国实施政策），无对照——用多个对照单位的**加权组合**构造"合成反事实"。

$$
\min_w\big\|Y_{T,pre}-W\cdot Y_{C,pre}\big\|,\quad w\ge0,\ \sum w=1
$$

**代码验证**（5 个对照单位，10 期预处理）：
- 合成权重 = $[0,0,0,0,1]$（集中于最相似的对照）
- 预处理拟合最大误差 0.559（良好匹配）
- 政策后"处理 - 合成"均值效应 = **1.739**

**经典应用**：Abadie-Diamond-Hainmueller (2010) 加州烟草控制；德国统一；案例研究法的"准实验化"。

### ④ 事件研究（Event Study）

动态版本的 DID：估计政策**前后各期**的效应。

$$
Y_{it}=\alpha_i+\delta_t+\sum_{k\ne-1}\tau_k\cdot\mathbf{1}[t-t^*_i=k]+\varepsilon_{it}
$$

**代码验证**（模拟）：真实动态效应 $\{t=-2:0,\ -1:0,\ 0:1.5,\ 1:2.5,\ 2:3.0,\ 3:2.8\}$：
- 估计的 $t=-1$ 效应 ≈ 0 ✓（无预期效应，验证识别）
- 政策后效应渐增至 3.0 后略降 ✓

**用途**：政策预期效应、动态调整、识别检验（前期系数应为 0）。

---

## 4.4 机器学习 × 因果（2017 以来的范式转移）

### 为什么 ML 不能直接给因果

ML 优化**预测**（最小化训练误差），但因果问的是**反事实**（如果当时做了另一个选择）。用 ML 预测 $E[Y|X,D]$ 然后求差，会因**正则化偏误**和**高维混淆**失真。

### Double/Debiased ML（Chernozhukov et al. 2018）

**直觉**：用 ML 分别估计 $y$ 的**混淆部分** $g(X)$ 和 $D$ 的**混淆部分** $m(X)$，然后做**残差对残差**回归——ML 的误差在 Neyman 正交性下**二阶小**。

$$
\hat{\theta}_{DML}=\frac{\sum_i(D_i-\hat{m}(X_i))(Y_i-\hat{g}(X_i))}{\sum_i(D_i-\hat{m}(X_i))^2}
$$

**性质**：$\sqrt{n}$-一致、渐近正态（可做统计推断！）——这是 ML 因果的"执照"。

**代码验证**（模拟，p=20 维混淆）：
- 朴素 y~D 回归 = **严重偏误**
- Double ML = **正确** ✓

### Causal Forest（Athey-Imbens-Wager 2019）

**目的**：找**异质处理效应 (HTE)**——哪些子群受益最大？

**方法**：honest trees（一半样本建树、另一半估计效应）+ adaptive neighborhood，给出**每个个体**的 $\hat{\tau}(x)$ 和置信区间。

**应用**：精准政策投放（给谁发补贴最有效）、临床个性化治疗。

### Synthetic DID（Arkhangelsky et al. 2021）

合成控制 + DID 的杂交：同时加权的对照单位**和时间**，双重差分。

### 2026 前沿：网络溢出与面板因果

经典因果推断假设 **SUTVA**（个体间无溢出）。但疫苗、社交网络、平台经济里溢出无处不在——**SUTVA 崩溃**。

`[econ.EM 2026-08]` 三篇直接攻克这一圣杯：
- *Learning about Treatment Effects in Panels under Unknown Interference*（面板+未知溢出）
- *Bias-robust causal inference for panel data*（面板稳健推断）
- *Graph-Laplacian Variance Estimators for Finely Stratified Experiments*（精细分层实验）

`[econ.EM 2026-08-13]` *Measuring the Arrow of Time* 则把"因果方向"本身作为估计对象——计量经济学开始从"估计效应"走向"发现因果结构"。

---

## 4.5 实验经济学（2019 诺奖 Banerjee-Duflo-Kremer）

RCT 是因果识别的"黄金标准"——随机分配消除一切混淆。

**J-PAL 实验室**（Duflo-Banerjee）在发展中国家的数百个 RCT：蚊帐要不要收费（Cohen-Dupor 2010：收费大幅降低使用，即使免费拿到的也用）、教师激励、微金融效果（Angelucci et al. 2015：温和但非革命性）。

**批判**：
1. **外部效度**：一个村庄的结果能推广到全国吗？
2. **SUTVA**：处理组行为影响对照组（一般均衡效应）
3. **伦理**：随机剥夺对照组的潜在收益

---

## ✍️ 练习

1. 用 Rubin 框架解释：为什么"接受了培训的人收入更高"不能证明培训有效？
2. 构造一个"弱工具"例子（第一阶段 F<10），演示 IV 估计的爆炸性。
3. DID：如果处理组政策前就在"向上偏离"对照组，DID 会高估还是低估？
4. RDD：McCrary 密度检验发现阈值附近密度**跳变**，说明什么？（操控——如考试刚好及格）
5. Double ML：为什么"残差对残差"能消除 ML 的正则化偏误？（提示：Neyman 正交性）
6. 设计一个实验估计"社交媒体使用对幸福感"的因果效应。如何处理溢出（SUTVA 违反）？

## 📌 下一步

计量给了经济学科学性，但"理性人"假设真的对吗？进入 **05 行为经济学**——系统性地偏离理性。

---

*代码验证：`/tmp/opencode/econ_econ.py` + `synth_fix.py` · 全部通过*
