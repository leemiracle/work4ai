# 金融计量学 · Financial Econometrics

> **位置**：`03-social-sciences/finance/financial-econometrics.md`  
> **关联**：[`_overview.md`](./_overview.md)（金融地图 + 方法论表）+ [`_philosophy-of-finance.md`](./_philosophy-of-finance.md)（哲学锚点）+ [`markets-and-pricing.md`](./markets-and-pricing.md)（定价三流派 + EMH 检验）+ [`portfolio-theory.md`](./portfolio-theory.md)（CAPM/FF 因子 + β）+ [`econophysics.md`](./econophysics.md)（肥尾 + 标度律 + Mandelbrot 批判）+ [`behavioral-finance.md`](./behavioral-finance.md)（异象的计量检测）+ [`risk-and-uncertainty.md`](./risk-and-uncertainty.md)（波动率 = Knight 风险的度量）  
> **哲学根源**：[`00-philosophy/epistemology.md`](../../00-philosophy/epistemology.md)（归纳问题 + 可证伪性 + 数据挖掘的认识论罪）+ [`02-formal-sciences/probability/`](../../02-formal-sciences/probability/)（统计推断的数学基础）  
> **核心问题**：**我们能用历史数据"提取"出金融市场的统计规律吗？如果能，这些规律是"发现的"还是"挖掘的"？** —— 本章用代码逐一拷问这条赌注。

---

## 引言：金融学的"实验台"

理论金融学（Black-Scholes、CAPM、无套利）造出了一套优雅的数学机器。但**这台机器和现实吻合吗？** 这是金融计量学的全部使命。

金融计量学 = **用统计方法从市场数据中提取、检验、估计金融理论的命题**。它是金融学的"实验台"——物理学家用对撞机检验粒子物理预言，金融计量学家用历史价格序列检验定价模型预言。

但这里有一个比物理学深刻得多的认识论陷阱：

> 物理定律不会因为被人类发现而改变。但市场规律会。一旦你发现"小盘股跑赢大盘"并据此建仓，你的套利行为本身就在**消除**这个规律。这是 Lucas 批判的金融版——**金融规律是自我毁灭的**。

因此本章不仅讲"怎么算"，更要持续追问："算出来的东西，是真理还是过拟合的幻觉？"

> **一句话**：金融计量学是金融学的经验法庭——它用数据审判理论，但它本身永远受审于"数据挖掘""结构不稳定""Lucas 批判"三重指控。

---

## 一、金融计量学的本质——用统计提取规律，以及它的根本局限

### 1.1 它在做什么

金融计量学的标准工作流：

```
金融理论 (CAPM/EMH/GARCH...) 
   ↓  翻译成
可检验的统计假设 (H₀: β=0, α=0, ρ=0...)
   ↓  用历史数据估计
参数估计 + 标准误 + 检验统计量
   ↓  拒绝/不拒绝 H₀
经验裁决（理论被支持 / 被证伪 / 无法判定）
```

**核心赌注**：如果金融市场的统计特征（分布、相关性、波动率动态）在时间上**足够稳定**，那么历史数据就能告诉我们未来的统计规律——就像用过去 1000 次掷骰子的频率推断骰子是否均匀。

### 1.2 根本局限一：数据挖掘（Data Snooping / Data Mining）

**问题**：金融数据极其有限（美股可靠日数据 ~100 年 = 25000 个交易日）。当你用**同一批数据**尝试了 1000 个策略/因子，即使**所有**都是纯随机噪声，按 5% 显著性水平，你**必然**会"发现"约 50 个"显著"的策略。这不是发现，是**幻觉**。

> **Lo & MacKinlay（1990）的警告**：对同一数据集反复挖掘，显著结果会系统性膨胀。这就是 **data snooping bias**。

**对策**：
- **样本外检验**（out-of-sample）：留一部分数据做"未知"测试。
- **数据窥探调整**（White 2000 的 Reality Check，Hansen 2005 的 SPA 检验）：对多重比较做 p 值校正。
- **预注册思想**：先写下假设，再看数据（金融学正在艰难地学习这一点）。

### 1.3 根本局限二：结构不稳定（Structural Instability / Regime Change）

**问题**：物理常数（光速、普朗克常数）不随时间变。但金融参数**变**：
- β 系数会变（公司业务转型、行业轮动）
- 波动率会变（危机前 vs 危机中）
- 因子溢价会变（价值因子 2008 年后长期失效，2022 年又复苏）

一个用 1990–2007 年数据估计的 GARCH 模型，在 2008 年危机中**完全失效**——因为"机制"（regime）变了。这不是"模型用错了参数"，而是"模型描述的那个世界已经不存在了"。

> **essence 立场**：金融参数不是"常数"，而是"状态变量"。任何金融计量模型都必须回答："我的参数在什么条件下会变？" 答不上来的模型，在黑天鹅来临时就是定时炸弹。

### 1.4 根本局限三：Lucas 批判——规律因被发现而改变

**Robert Lucas（1976）** 针对宏观经济计量提出，但同样（甚至更猛烈地）适用于金融：

> 任何从历史数据中估计出的"规律性"，一旦被政策制定者/交易者用于决策，**人的行为会改变**，从而使该规律性失效。

金融版的 Lucas 批判尤其致命，因为金融市场有**套利机制**：
- 你发现"动量因子"有效 → 大量资金涌入动量策略 → 动量被提前定价 → 动量消失（或反转）。
- **McLean & Pontiff（2016）** 的实证证实：学术论文发表后的因子，样本外收益**平均下降 50% 以上**——**发表即消灭**。

> **深度洞察**：这使得金融计量学陷入一个悖论——它越成功（发现越多规律），它就越快地使自己的发现失效。物理学的成功累积知识；金融计量学的"成功"消耗知识。这不是 bug，这是**金融系统的内禀属性**——市场是一个**反身性**（reflexive，Soros 语）的系统。

### 1.5 与 [`econophysics.md`](./econophysics.md) 的呼应

econophysics 强调市场的"普适统计规律"（肥尾、标度律）跨市场、跨时代稳定。本章承认这些**程式化事实**（stylized facts）确实稳健（见 §二），但同时指出：**更精细的规律**（具体因子、具体价差）是不稳定的、自我毁灭的。物理类比在"粗粒度"成立，在"细粒度"破产。

---

## 二、时间序列的程式化特征——金融数据的"指纹"

> 金融计量学的第一课：**收益率不是正态的，波动率不是恒定的，市场不是随机游走**。这一节用代码验证这五条"程式化事实"（stylized facts）。它们是所有后续模型的**经验地基**。

### 2.1 五大程式化特征

| # | 特征 | 含义 | 与教科书的冲突 |
|---|------|------|--------------|
| 1 | **收益无（线性）自相关** | $r_t$ 的 ACF ≈ 0 → **不可线性预测** | 支持弱式 EMH，但非严格随机游走 |
| 2 | **平方收益强自相关** | $r_t^2$ 的 ACF 显著且缓慢衰减 → **波动率聚集** | 正态 iid 假设破产 |
| 3 | **肥尾（fat tails）** | 峰度 > 3，极端事件比正态预测频繁得多 | Black-Scholes 正态假设破产 |
| 4 | **波动率聚集（volatility clustering）** | 大波动跟着大波动，平静跟着平静 | 恒定波动率假设破产 |
| 5 | **杠杆效应（leverage effect）** | 负收益 → 未来波动率更高（不对称） | 对称 GARCH 不够，需 EGARCH/TGARCH |

### 2.2 直觉层

- **特征 1**：如果 $r_t$ 可预测，套利者早就赚走了那个预测性，所以剩下的就是"不可预测"——这是 EMH 的**数学表述**。
- **特征 2/4**：但"不可预测"只针对**均值**。**波动率**（二阶矩）是高度可预测的——"暴风雨会持续一阵"。这就是 ARCH/GARCH 存在的理由。
- **特征 3**：1987 年黑色星期一，道琼斯单日跌 22.6%——按正态分布，这应该是 $10^{-50}$ 年一遇的事件。它发生了。正态分布在尾部**撒谎**。详见 [`econophysics.md`](./econophysics.md) §二。
- **特征 5**：股价下跌（公司杠杆上升、更危险）→ 波动率上升；但股价上涨 → 波动率不一定对称下降。这种**不对称**是 Black（1976）首先注意到的。

### 2.3 代码：验证五大程式化特征

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(42)
N = 5000

# 模拟一个 GARCH(1,1) 过程，产生真实的程式化特征
omega, alpha, beta = 0.02, 0.10, 0.88
ret = np.zeros(N); sig2 = np.zeros(N); sig2[0] = omega/(1-alpha-beta)
for t in range(1, N):
    sig2[t] = omega + alpha*ret[t-1]**2 + beta*sig2[t-1]
    ret[t] = np.sqrt(sig2[t])*rng.standard_normal()

def acf(x, lags=8):
    x = x - x.mean(); v = np.dot(x, x)
    return [np.dot(x[k:], x[:len(x)-k])/v for k in range(1, lags+1)]

ac_ret = acf(ret); ac_sq = acf(ret**2)

print("=== 程式化特征检验（模拟 GARCH(1,1), N=5000）===")
print(f"{'lag':<5}{'ACF(r)':>10}{'ACF(r^2)':>10}")
print("-"*27)
for i in range(8):
    print(f"{i+1:<5}{ac_ret[i]:>10.4f}{ac_sq[i]:>10.4f}")

print("\n--- 关键统计量 ---")
print(f"偏度 (正态=0):          {stats.skew(ret):+.4f}")
print(f"峰度 (正态=3, 肥尾>3):  {stats.kurtosis(ret)+3:.4f}")
print(f"Jarque-Bera p (正态):   {stats.jarque_bera(ret)[1]:.2e}")
print(f"ACF|r| lag1 (聚集):     {acf(np.abs(ret),1)[0]:+.4f}")
# 杠杠效应：符号 → 未来 |r|
neg = (ret < 0).astype(float)
print(f"杠杆代理相关 (符号→|r'|):{np.corrcoef(neg[:-1], np.abs(ret[1:]))[0,1]:+.4f}")
```

**验证结果**：

```
=== 程式化特征检验（模拟 GARCH(1,1), N=5000）===
lag      ACF(r)  ACF(r^2)
---------------------------
1        0.0334    0.1385
2       -0.0107    0.1568
3       -0.0009    0.1572
4        0.0293    0.1823
5       -0.0049    0.1383
6       -0.0382    0.1568
7        0.0253    0.1337
8        0.0190    0.0965

--- 关键统计量 ---
偏度 (正态=0):          -0.0061
峰度 (正态=3, 肥尾>3):  3.7299
Jarque-Bera p (正态):   7.85e-25
ACF|r| lag1 (聚集):     +0.1393
杠杆代理相关 (符号→|r'|):+0.0173
```

> **洞察**：
> 1. **ACF(r) ≈ 0**（特征 1 成立）——收益不可线性预测，弱式 EMH 在此成立。
> 2. **ACF(r²) = 0.10–0.18 显著为正**（特征 2/4 成立）——**波动率可预测**，这就是 GARCH 的用武之地。
> 3. **峰度 3.73 > 3**，JB 检验 p≈0 → **拒绝正态**（特征 3 成立）。注意对称 GARCH 偏度≈0，真实市场偏度显著为负。
> 4. **杠杆代理相关 ≈ 0.02**（标准 GARCH 几乎不捕捉杠杆效应）——这恰恰**暴露了标准 GARCH 的缺陷**，正是 EGARCH/TGARCH 要修补的（见 §三）。

---

## 三、波动率模型全谱系——给"暴风雨"建模

> 波动率（volatility）是金融中**最重要也最难捉摸的量**。它不可直接观测，只能从收益中**推断**。本节梳理波动率模型的完整演化谱系。

### 3.1 谱系总览

```
波动率模型演化
├── 隐含波动率（IV）   ← 期权市场"前瞻"预期（Black-Scholes 反推）
├── 历史波动率         ← 过去 N 天收益标准差（最朴素）
├── ARCH（Engle 1982） ← 波动率 = 过去平方收益的函数  ★诞生
│   └── GARCH（Bollerslev 1986）← 加入过去波动率（持续性）
│       ├── EGARCH（Nelson 1991）  ← 指数化 + 杠杆效应（不对称）
│       ├── TGARCH/GJR-GARCH（1993）← 门限捕捉杠杆效应
│       ├── IGARCH（积分 GARCH）    ← 单位根波动率（持续性=1）
│       └── FIGARCH（分整 GARCH）   ← 长记忆波动率
├── 多元 GARCH
│   ├── BEKK（Engle-Kroner 1995）   ← 保证正定性
│   ├── DCC（Engle 2002）           ← 动态条件相关 ★实用
│   └── CCC（常条件相关）
└── 已实现波动率（RV）  ← 高频数据"事后"度量（见 §四）
```

### 3.2 ARCH 与 GARCH 的数学

**ARCH(q)**（Engle, 1982，诺奖 2003）：波动率是过去 q 期平方收益的线性组合。

$$\sigma_t^2 = \omega + \sum_{i=1}^{q}\alpha_i\,\varepsilon_{t-i}^2, \quad \varepsilon_t = \sigma_t z_t,\; z_t\sim\text{iid}(0,1)$$

**GARCH(p,q)**（Bollerslev, 1986）：加入**过去波动率**自身——这才是让它"持续"的关键。

$$\sigma_t^2 = \omega + \sum_{i=1}^{q}\alpha_i\,\varepsilon_{t-i}^2 + \sum_{j=1}^{p}\beta_j\,\sigma_{t-j}^2$$

最常用的是 **GARCH(1,1)**：

$$\boxed{\sigma_t^2 = \omega + \alpha\,\varepsilon_{t-1}^2 + \beta\,\sigma_{t-1}^2}$$

**关键解读**：
- $\alpha$（新闻冲击系数）：昨天的"惊讶"（平方收益）对今天波动率的贡献。
- $\beta$（持续性系数）：昨天波动率对今天的延续。
- $\alpha + \beta$ = **持续性**（persistence）：< 1 则平稳，越接近 1 波动率越"持久"。实证中常 $\alpha+\beta \approx 0.97\text{–}0.99$——**极接近单位根**，意味着波动率冲击衰减极慢。
- 无条件方差：$\sigma^2 = \omega/(1-\alpha-\beta)$。

### 3.3 EGARCH 与 TGARCH——捕捉杠杆效应

**EGARCH（Nelson, 1991）**：对数形式（天然保证 $\sigma_t^2>0$）+ 显式不对称项：

$$\ln\sigma_t^2 = \omega + \alpha\!\left[\frac{|\varepsilon_{t-1}|}{\sigma_{t-1}} - \sqrt{\tfrac{2}{\pi}}\right] + \gamma\frac{\varepsilon_{t-1}}{\sigma_{t-1}} + \beta\ln\sigma_{t-1}^2$$

$\gamma < 0$ 时：负冲击（$\varepsilon<0$）推高波动率更多——**杠杆效应**。这正是标准 GARCH（$\gamma=0$）做不到的。

**TGARCH / GJR-GARCH（Glosten-Jagannathan-Runkle 1993）**：用门限虚拟变量 $\mathbb{1}_{\varepsilon_{t-1}<0}$ 直接刻画不对称：

$$\sigma_t^2 = \omega + \alpha\,\varepsilon_{t-1}^2 + \gamma\,\mathbb{1}_{\varepsilon_{t-1}<0}\,\varepsilon_{t-1}^2 + \beta\,\sigma_{t-1}^2$$

### 3.4 多元 GARCH——相关性也会动

单变量 GARCH 刻画一个资产的波动率。但组合管理需要**协方差矩阵**——而且相关性 $\rho_{ij,t}$ 也是**时变**的（危机时相关性飙升，分散化失效）。

| 模型 | 参数化 | 优点 | 缺点 |
|------|--------|------|------|
| **BEKK** | $H_t = CC' + A'\varepsilon_{t-1}\varepsilon_{t-1}'A + B'H_{t-1}B$ | 天然正定 | 参数随维度爆炸（$O(N^2)$） |
| **CCC**（常条件相关） | $H_t = D_t R D_t$，$R$ 固定 | 简洁 | 相关性不变的假设太强 |
| **DCC**（Engle 2002） | $R_t$ 时变（类似 GARCH 相关性） | **实用、可扩展** | 仍是相关性的简化动态 |

> **危机教训**：2008 年，所有资产相关性 → 1，分散化"消失"。DCC 能事后捕捉这一点，但事前预测不了"什么时候相关性会飙升"。

### 3.5 IV vs RV——前瞻 vs 事后

- **隐含波动率（IV）**：从期权价格**反推**出的市场对未来波动率的预期。VIX 指数就是 S&P 500 期权的隐含波动率。
- **已实现波动率（RV）**：用**高频**收益事后计算的"真实"波动率（见 §四）。
- **方差风险溢价（VRP）**：$IV^2 - RV^2$。实证发现 IV 系统**高于** RV——市场愿意为波动率保险**多付钱**（这是卖出波动率的收益来源，也是"波动率卖家的午餐"）。但这个午餐有**尾部风险**：2018 年 2 月"波动率末日"（Volmageddon），做空 VIX 的产品一夜归零。

### 3.6 代码：GARCH(1,1) 极大似然估计

```python
import numpy as np
from scipy.optimize import minimize

rng = np.random.default_rng(123)
N = 3000
w_true, a_true, b_true = 0.05, 0.10, 0.85
ret = np.zeros(N); s2 = np.zeros(N); s2[0] = w_true/(1-a_true-b_true)
for t in range(1, N):
    s2[t] = w_true + a_true*ret[t-1]**2 + b_true*s2[t-1]
    ret[t] = np.sqrt(s2[t])*rng.standard_normal()

def neg_ll(params):
    w, a, b = params
    if w <= 0 or a < 0 or b < 0 or a+b >= 1: return 1e10
    s2 = np.empty(N); s2[0] = np.var(ret)
    for t in range(1, N):
        s2[t] = w + a*ret[t-1]**2 + b*s2[t-1]
    return 0.5*(np.log(2*np.pi) + np.log(s2) + ret**2/s2).sum()

res = minimize(neg_ll, [0.05,0.1,0.85], method='Nelder-Mead',
               options={'maxiter':5000,'xatol':1e-8,'fatol':1e-8})
w, a, b = res.x
import math
print("=== GARCH(1,1) 极大似然估计（N=3000）===")
print(f"{'参数':<10}{'真值':>8}{'估计':>8}")
print("-"*28)
print(f"{'omega':<10}{w_true:>8.3f}{w:>8.3f}")
print(f"{'alpha':<10}{a_true:>8.3f}{a:>8.3f}")
print(f"{'beta':<10}{b_true:>8.3f}{b:>8.3f}")
print(f"{'α+β':<10}{a_true+b_true:>8.3f}{a+b:>8.3f}")
print(f"\n持续性 (α+β):        {a+b:.3f}  (<1 平稳)")
print(f"无条件方差:          {w/(1-a-b):.4f}  (样本 {np.var(ret):.4f})")
print(f"波动率冲击半衰期:    {math.log(0.5)/math.log(a+b):.1f} 期")
```

**验证结果**：

```
=== GARCH(1,1) 极大似然估计（N=3000）===
参数           真值      估计
----------------------------
omega       0.050   0.073
alpha       0.100   0.093
beta        0.850   0.833
α+β         0.950   0.926

持续性 (α+β):        0.926  (<1 平稳)
无条件方差:          0.9890  (样本 0.9800)
波动率冲击半衰期:    9.1 期
```

> **洞察**：估计值 $\alpha+\beta=0.926$ 接近真值 0.95，半衰期 ~9 期——一次波动率冲击的影响要 9 个周期才衰减一半。**真实市场 $\alpha+\beta$ 常达 0.98–0.99**，半衰期数月——"暴风雨会持续很久"。这也解释了为什么波动率可预测（特征 2/4）而收益不可预测（特征 1）。

---

## 四、高频计量——用"显微镜"看波动率

> 当你从日频切换到 tick 级（秒/分钟）数据，一个全新的世界打开了：你可以在**一天之内**精确度量"真实"波动率，检测"跳跃"，理解"微观结构噪声"。这是 Andersen、Bollerslev、Diebold、Barndorff-Nielsen 等人 2000 年代开创的 **高频计量（high-frequency econometrics）**。

### 4.1 已实现波动率（Realized Volatility, RV）

**核心思想**：如果价格服从连续半鞅 $dp_t = \mu_t dt + \sigma_t dW_t$，那么一天内的**二次变差**（quadratic variation）正好等于积分波动率：

$$\text{RV}_t = \sum_{i=1}^{n} r_{t,i}^2 \;\xrightarrow{p}\; \int_0^1 \sigma_{t,u}^2\,du$$

即：**把一天内所有高频收益平方求和，就得到了"真实"日波动率**（当采样频率→∞时一致）。这是 RV 的数学之美——不需要模型，纯**非参数**。

### 4.2 已实现双幂变差（Realized Bipower Variation）——跳跃检测

**问题**：RV 把"连续波动"和"离散跳跃"混在一起。如何分离？

**Barndorff-Nielsen & Shephard（2004）** 的天才构造——**已实现双幂变差（BPV）**：

$$\text{BPV}_t = \frac{\pi}{2}\sum_{i=2}^{n}|r_{t,i}|\,|r_{t,i-1}|$$

BPV 对跳跃**稳健**（不受跳跃污染），但 RV 会包含跳跃。于是：

$$\text{跳跃分量} = \max(\text{RV}_t - \text{BPV}_t,\; 0)$$

这是检测"哪天有跳跃、跳了多少"的标准工具。跳跃在金融中极其重要——崩盘、利好/利空公告、宏观冲击都是跳跃。

### 4.3 微观结构噪声——RV 的天敌

**问题**：RV 在采样频率→∞时一致——**理论上**。但现实中，频率太高会遇到**微观结构噪声**（买卖价差跳动、离散报价、bid-ask bounce）。这些噪声使得 RV **系统性向上偏差**，而且**越高频偏差越大**（与理论预言相反！）。

**对策**：
- **稀疏采样**（sparse sampling）：不用 1 秒，用 5 分钟——降低噪声，但损失信息。
- **子采样（sub-sampling）/ 平均 RV**：Zhou、Hansen-Lunde 等人的降噪估计量。
- **预平均（pre-averaging）**：Jacod 等；**核估计（realized kernel）**：Barndorff-Nielsen 等。
- **噪声模型**：$r_{t,i} = r_{t,i}^* + \varepsilon_{t,i}$（有效收益 + 噪声），用似然或矩估计分离。

> **关键张力**：金融数据的"微观结构噪声"恰恰是 [`market-microstructure.md`](./market-microstructure.md) 的主题——做市、价差、订单流不平衡。高频计量学和微观结构理论在这里**交汇**：噪声对 RV 是"害"，对微观结构学家是"研究对象"。

### 4.4 代码：计算 RV + 跳跃检测 + 噪声污染

```python
import numpy as np
rng = np.random.default_rng(7)

# 模拟 1 个交易日，1 分钟收益（390 分钟）
n_min = 390; dt = 1/252/390; sigma = 0.20  # 年化
cont = sigma*np.sqrt(dt)*rng.standard_normal(n_min)
cont[200] += 0.015   # 在第 200 分钟注入一次跳跃 +1.5%
r = cont

RV  = np.sum(r**2)                              # 已实现波动率
BPV = (np.pi/2)*np.sum(np.abs(r[1:])*np.abs(r[:-1]))  # 双幂变差
J   = max(RV - BPV, 0)                          # 跳跃分量
print("=== 高频计量：RV + 跳跃检测 ===")
print(f"RV:           {RV:.4e}")
print(f"BPV (抗跳跃): {BPV:.4e}")
print(f"跳跃分量 J:   {J:.4e}  (占 RV 的 {J/RV:.1%})")
print(f"RV 年化波动率:{np.sqrt(RV*252):.4f}")

# 微观结构噪声污染演示
print("\n=== 微观结构噪声对 RV 的向上偏差 ===")
print(f"{'噪声σ':<10}{'RV':>12}{'偏差':>10}")
print("-"*34)
base = np.sum((sigma*np.sqrt(dt)*rng.standard_normal(n_min))**2)
for nsd in [0, 0.0005, 0.001]:
    rn = sigma*np.sqrt(dt)*rng.standard_normal(n_min) + nsd*rng.standard_normal(n_min)
    rvn = np.sum(rn**2)
    print(f"{nsd:<10.4f}{rvn:>12.4e}{(rvn/base-1)*100:>+9.1f}%")
```

**验证结果**：

```
=== 高频计量：RV + 跳跃检测 ===
RV:           3.3782e-04
BPV (抗跳跃): 1.6412e-04
跳跃分量 J:   1.7370e-04  (占 RV 的 51.4%)
RV 年化波动率:0.2918

=== 微观结构噪声对 RV 的向上偏差 ===
噪声σ            RV        偏差
----------------------------------
0.0000      1.5115e-04     +1.8%
0.0005      2.3364e-04    +57.4%
0.0010      5.3634e-04   +261.3%
```

> **洞察**：
> 1. **跳跃被精准捕获**：J 占 RV 的 51.4%——RV 比 BPV 高出的部分正是第 200 分钟的跳跃。这就是 RV−BPV 作为"跳跃检测器"的力量。
> 2. **噪声是 RV 的天敌**：即使噪声标准差只有 0.001，RV 就被高估了 **261%**——完全失真。这就是为什么高频实践**不用 1 秒数据**算 RV，而用 5 分钟稀疏采样或降噪估计量。
> 3. RV 与 BPV 的**分工**：RV 度量"总波动（含跳跃）"，BPV 度量"连续波动"，差值定位跳跃。这套工具把波动率从"黑箱参数"变成了**可观测的、可分解的量**。

---

## 五、因子模型的计量检验——CAPM 之死与因子战争

> 因子模型是 [`portfolio-theory.md`](./portfolio-theory.md) §五的核心。这里从**计量**角度追问：怎么检验一个因子模型"成立"？答案是 **GRS 检验**。

### 5.1 CAPM 回归——时间序列法

CAPM 预言：$R_i - r_f = \alpha_i + \beta_i(R_M - r_f) + \varepsilon_i$，且**关键地**，$\alpha_i = 0$（无风险调整后的超额收益）。计量上就是对每个资产跑时间序列回归，检验 $\alpha_i$ 是否为零。

### 5.2 时间序列回归 vs 横截面回归

检验因子定价有两条计量路径：

| | 时间序列回归（Fama-MacBeth 第一步） | 横截面回归（Fama-MacBeth 第二步） |
|---|---|---|
| **回归对象** | 每个资产 $R_{it}$ 对因子 $F_t$ | 平均收益 $\bar{R}_i$ 对估计的 $\hat\beta_i$ |
| **检验** | $\alpha_i=0$（每资产） | 因子溢价 $\lambda_k$ 是否显著 |
| **关键问题** | 用**估计的** $\hat\beta$ 当自变量 → **EIV 误差**（变量误差偏差） |
| **经典处理** | 排序组合（sorting portfolios）形成 $\beta$ 组 |

**Fama-MacBeth（1973）两步法**：① 先用时间序列估 $\hat\beta_i$；② 每个时期做横截面回归 $\bar{R}_t = \lambda_0 + \sum_k \lambda_{kt}\hat\beta_{ik}$，得每期 $\hat\lambda_{kt}$；③ 对时间序列 $\hat\lambda_{kt}$ 求 mean/std 做 t 检验（修正自相关）。

### 5.3 GRS 检验——因子模型的"终极审判"

**Gibbons, Ross, Shanken（1989）** 提出检验：**所有**资产的 $\alpha$ 是否**联合**为零（而非逐个）。

$$\text{GRS} = \frac{T}{N}\cdot\frac{\hat{\boldsymbol\alpha}'\hat{\boldsymbol\Sigma}^{-1}\hat{\boldsymbol\alpha}}{1 + \hat\theta^2} \;\sim\; F(N,\,T-N-K)$$

其中 $N$=资产数，$K$=因子数，$\hat{\boldsymbol\Sigma}$=残差协方差，$\hat\theta^2$=因子的最大夏普平方（$\bar{F}'\hat{\Omega}_F^{-1}\bar{F}$）。

**GRS 的直觉**：如果一个因子模型"正确"，那么任何投资组合都不应有超额收益——即加了这个因子后，**能获得的最高夏普比率不应超过因子本身的夏普比率**。GRS 统计量衡量的正是"残差里还能榨出多少夏普比率"。

### 5.4 CAPM 的 GRS 死刑与因子战争

- **CAPM 被 GRS 反复拒绝**：单因子（市场）无法让 25 个规模-价值组合的 $\alpha$ 联合为零。
- **Fama-French 三因子**：加入 SMB、HML 后，GRS 显著改善——但仍常被拒绝。
- **因子战争（Harvey 2017）**：已有 **400+** 被发表的"显著因子"。Harvey 警告：如果都用 5% 显著性，绝大多数是 **假阳性**（data mining 的产物）。他呼吁把 t 值门槛从 2 提到 **3+**。

### 5.5 代码：GRS 检验

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(31)
T, K, N = 360, 1, 10        # 360月, 1因子(市场), 10组合
f = 0.005 + 0.045*rng.standard_normal((T,1))
betas = np.linspace(0.6, 1.5, N)
alpha_true = np.zeros(N)    # H0: 无异常收益
R = alpha_true[None,:] + betas[None,:]*np.tile(f,(1,N)) + 0.03*rng.standard_normal((T,N))

F = np.column_stack([np.ones(T), f[:,0]])
coef = np.linalg.lstsq(F, R, rcond=None)[0]
alpha, resid = coef[0], R - F@coef
Sigma = np.cov(resid, rowvar=False)
theta2 = f[:,0].mean()**2/np.var(f[:,0], ddof=1)
aSa = (alpha @ np.linalg.inv(Sigma) @ alpha)      # 标量
GRS = (T/N)*aSa/(1+theta2)
p = 1 - stats.f.cdf(GRS, N, T-N-K)
print("=== GRS 检验（H0: 所有 α 联合为零）===")
print(f"N={N} 资产, K={K} 因子, T={T} 期")
print(f"因子 Sharpe² (θ²): {theta2:.4f}")
print(f"GRS 统计量:        {GRS:.4f}")
print(f"F({N},{T-N-K}) p-value: {p:.4f}")
print(f"结论: {'不拒绝 H0 (因子模型成立)' if p>0.05 else '拒绝 H0 (存在异常收益)'}")

# 对照：注入真实 alpha → 应被拒绝
alpha2 = np.array([.003,.004,.005,.006,.007,-.001,.002,.003,.004,.005])
R2 = alpha2[None,:] + betas[None,:]*np.tile(f,(1,N)) + 0.03*rng.standard_normal((T,N))
c2 = np.linalg.lstsq(F, R2, rcond=None)[0]
a2, res2 = c2[0], R2-F@c2
aSa2 = (a2 @ np.linalg.inv(np.cov(res2,rowvar=False)) @ a2)
GRS2 = (T/N)*aSa2/(1+theta2)
print(f"\n(对照) 有异常收益: GRS={GRS2:.3f}, p={1-stats.f.cdf(GRS2,N,T-N-K):.4f} → 拒绝")
```

**验证结果**：

```
=== GRS 检验（H0: 所有 α 联合为零）===
N=10 资产, K=1 因子, T=360 期
因子 Sharpe² (θ²): 0.0319
GRS 统计量:        0.6342
F(10,349) p-value: 0.7844
结论: 不拒绝 H0 (因子模型成立)

(对照) 有异常收益: GRS=7.178, p=0.0000 → 拒绝
```

> **洞察**：当数据无异常收益时，GRS 正确地"不拒绝"（p=0.78）；注入异常收益后，GRS 强烈拒绝（p≈0）。这就是 GRS 作为"因子模型法庭"的力量——它把"逐个看 α 显不显著"升级为"**联合**审判"。真实世界中，CAPM 在 GRS 面前**反复败诉**，这正是因子模型不断进化的动力。

---

## 六、事件研究法——市场效率的经典裁判

> 事件研究法（Event Study）是金融计量学**最优雅、最实用**的工具之一。它回答："某一**事件**（并购公告、财报、政策出台）对股票价值有多大影响？" 这同时是**半强式 EMH** 的直接检验。

### 6.1 方法论

```
时间轴:  [---- 估计窗 ----][---- 事件窗 ----]
         T1              T0  0            T2
                                ↑事件日
```

1. **估计窗**（事件前，如 [−120, −11]）：用市场模型 $R_{it}=\alpha_i+\beta_i R_{Mt}+\varepsilon_{it}$ 估计"正常"行为。
2. **事件窗**（如 [−10, +10]）：计算**异常收益** $AR_{it} = R_{it} - (\hat\alpha_i+\hat\beta_i R_{Mt})$——实际收益减去"本应有的正常收益"。
3. **累计异常收益** $CAR(t_1,t_2)=\sum_{t=t_1}^{t_2}AR_{it}$。
4. **检验** $CAR$ 是否显著异于零（用估计窗残差的标准误构造 t 统计量）。

### 6.2 它检验什么

- **$CAR \approx 0$ 且快速**：市场在事件日**立刻**吸收信息 → 支持**半强式 EMH**。
- **$CAR$ 漂移（post-event drift）**：事件后继续累积异常收益 → **违反 EMH**（典型：盈余公告后漂移 PEAD）。
- **事件前 $CAR$ 异动**：信息**提前泄露**（可能内幕交易）。

### 6.3 经典应用

| 研究 | 事件 | 发现 |
|------|------|------|
| Fama-Fisher-Jensen-Roll（1969） | 股票拆分 | 首个事件研究——支持 EMH |
| Ball & Brown（1968） | 盈余公告 | 发现 PEAD（后漂移）——挑战 EMH |
| MacKinlay（1997） | 综述 | 方法论圣经 |

### 6.4 代码：事件研究法（市场模型 + CAR + t 检验）

```python
import numpy as np
rng = np.random.default_rng(11)

T_est, T_win = 120, 21              # 估计窗, 事件窗[-10,+10]
beta_t, alpha_t = 1.3, 0.02
Rm = 0.05 + 1.0*rng.standard_normal(200)
eps = 0.8*rng.standard_normal(200)
abn = np.zeros(200)
for i, d in enumerate(range(-10, 11)):
    abn[120+i] = 3.0*np.exp(-abs(d)/4)   # 事件产生 CAR 形态异常收益
Ri = alpha_t + beta_t*Rm + eps + abn

X = np.column_stack([np.ones(120), Rm[:120]])
coef = np.linalg.lstsq(X, Ri[:120], rcond=None)[0]
Xw = np.column_stack([np.ones(T_win), Rm[120:141]])
AR = Ri[120:141] - Xw@coef
CAR = np.cumsum(AR)
resid = Ri[:120] - X@coef
s2 = np.var(resid, ddof=2)
t = CAR/np.sqrt(np.arange(1,T_win+1)*s2)
days = np.arange(-10, 11)
print("=== 事件研究法（市场模型 + CAR + t 检验）===")
print(f"β̂={coef[1]:.3f}(真1.30), α̂={coef[0]:.3f}(真0.02)")
print(f"\n{'day':<6}{'AR%':>8}{'CAR%':>8}{'t':>8}")
print("-"*32)
for i in range(0, 21, 2):
    print(f"{days[i]:<6}{AR[i]:>8.3f}{CAR[i]:>8.3f}{t[i]:>8.2f}")
print(f"\nCAR[-10,+10]={CAR[20]:.2f}%, t={t[20]:.2f} "
      f"{'显著' if abs(t[20])>1.96 else '不显著'}")
```

**验证结果**：

```
=== 事件研究法（市场模型 + CAR + t 检验）===
β̂=1.313(真1.30), α̂=0.052(真0.02)

day        AR%    CAR%       t
--------------------------------
-10      0.882   0.882    1.11
-8      -0.228   1.052    0.77
-6       2.746   4.460    2.52
-4      -1.155   5.136    2.45
-2       1.093   7.488    3.16
0        2.857  13.143    5.01
2        2.522  19.535    6.85
4        1.213  22.853    7.46
6        0.892  24.533    7.52
8        0.788  26.836    7.78
10       1.243  28.083    7.75

CAR[-10,+10]=28.08%, t=7.75 显著
```

> **洞察**：事件日前 CAR 已开始爬升（信息提前渗透），事件日（day 0）AR 峰值，之后继续漂移——这种"提前反应 + 后漂移"形态正是**真实事件研究**的典型发现。t=7.75 远超 1.96，事件效应**强显著**。注意：事件研究法的威力在于它**剥离了市场整体波动**（通过 β 调整），把"事件特有的"异常收益**隔离**出来。

---

## 七、协整与配对交易——统计套利的计量基础

> 单只股票价格是**非平稳**的（随机游走，I(1)），直接回归两个 I(1) 序列会产生**伪回归**（spurious regression，Granger-Newbold 1974）。但如果两个序列的**线性组合**是平稳的，它们就是**协整**的——这是配对交易（pairs trading）的数学基础。

### 7.1 协整的定义

若 $y_t, x_t$ 都是 I(1)（一阶单整），但存在 $\beta$ 使 $z_t = y_t - \beta x_t$ 是 I(0)（平稳），则称 $y_t, x_t$ **协整**，$\beta$ 为协整向量。经济含义：两者存在**长期均衡关系**，短期偏离会被"拉回"。

### 7.2 Engle-Granger 两步法

1. **第一步**：OLS 回归 $y_t = a + \beta x_t + u_t$，得残差 $\hat u_t$。
2. **第二步**：对 $\hat u_t$ 做 ADF 检验。若平稳（ADF 统计量 < Engle-Granger 临界值，比标准 ADF 更负），则协整。
3. **误差修正模型（ECM）**：$\Delta y_t = \gamma \hat z_{t-1} + \text{短期项}$，$\gamma<0$ 表示偏离均衡后被拉回。

### 7.3 配对交易逻辑

```
价差 z = ln(P_A) - β·ln(P_B)  （协整残差）
  z > +2σ  → 做空 A / 做多 B  （价差太高，预期回归）
  z < -2σ  → 做多 A / 做空 B  （价差太低，预期回归）
  |z| < 0.5σ → 平仓            （回归完成）
```

本质是**赌均值回归**——但这只在协整关系**持续成立**时有效。一旦基本面断裂（并购、破产、行业变迁），价差不回归而是**发散**，配对交易爆亏。

### 7.4 代码：协整检验 + 配对信号

```python
import numpy as np
rng = np.random.default_rng(5)
T = 1000
beta_true = 1.25
lp2 = np.cumsum(rng.standard_normal(T)*0.01) + 4.0   # I(1) 对数价格
phi = 0.90
s = np.zeros(T)                                       # 平稳价差 AR(1)
for t in range(1, T):
    s[t] = phi*s[t-1] + rng.standard_normal()*0.02
lp1 = beta_true*lp2 + s                               # lp1 - β·lp2 = s 是 I(0)

# Engle-Granger
X = np.column_stack([np.ones(T), lp2])
coef = np.linalg.lstsq(X, lp1, rcond=None)[0]
u = lp1 - X@coef
du = np.diff(u); ul = u[:-1]
rho = np.linalg.lstsq(ul[:,None], du, rcond=None)[0][0]
resid = du - rho*ul
se = np.sqrt(np.sum(resid**2)/(len(du)-1))/np.sqrt(np.sum(ul**2))
df_t = rho/se
import math
print("=== 协整检验（Engle-Granger 两步法）===")
print(f"β̂={coef[1]:.3f} (真值{beta_true}), 截距={coef[0]:.3f}")
print(f"DF ρ={rho:+.4f}, t={df_t:+.2f} (EG 5%临界≈-3.34)")
print(f"结论: {'协整(平稳价差)' if df_t<-3.34 else '不协整'}")

m, sd = u.mean(), u.std()
z = (u-m)/sd
print(f"\n=== 配对交易信号 ===")
print(f"价差均值={m:.3f}, σ={sd:.3f}")
print(f"做多信号(z<-2)次: {(z<-2).sum()}, 做空信号(z>+2)次: {(z>2).sum()}")
print(f"末尾 z={z[-1]:+.2f}")
print(f"均值回归半衰期: {-math.log(2)/math.log(1+rho):.0f} 期")
```

**验证结果**：

```
=== 协整检验（Engle-Granger 两步法）===
β̂=1.265 (真值1.25), 截距=-0.049
DF ρ=-0.1184, t=-7.91 (EG 5%临界≈-3.34)
结论: 协整(平稳价差)

=== 配对交易信号 ===
价差均值=0.000, σ=0.041
做多信号(z<-2)次: 22, 做空信号(z>+2)次: 19
末尾 z=+0.92
均值回归半衰期: 6 期
```

> **洞察**：DF t=−7.91 远超临界值 → 强协整；β̂=1.265 精准恢复真值 1.25；半衰期 6 期——价差偏离后约 6 天回归一半。但**警惕**：协整关系会**断裂**。2008 年许多"统计稳定"的配对在危机中同步崩盘（相关性→1，价差发散）。统计套利的根本风险不是"模型错"，而是"**协整关系本身是状态依赖的**"。

---

## 八、机器学习计量——预测的新工具，过拟合的新陷阱

> 2010 年代起，机器学习（ML）涌入金融计量。它能处理**高维**（数百因子）、**非线性**（交互效应），但同时把"过拟合"风险放大了几个数量级。

### 8.1 ML 在金融中的角色

| 任务 | 模型 | 金融应用 |
|------|------|---------|
| **变量选择** | LASSO、Elastic Net | 从数百因子中筛选有效者 |
| **非线性预测** | 随机森林、梯度提升（XGBoost/LightGBM） | 收益预测、特征交互 |
| **表示学习** | 深度神经网络、Autoencoder | 因子降维、非线性因子提取 |
| **时序深度** | LSTM、Transformer | 顺序模式、波动率预测 |

### 8.2 核心张力：金融数据是 ML 的"噩梦"

- **信噪比极低**：金融收益的 $R^2$ 常 < 5%，而 ML 在高信噪比（图像、语言）上成功。低信噪比下，ML 极易**记住噪声**。
- **样本小**：美股月数据 ~1000 点，远少于 ML 偏好的大数据。
- **非平稳**：训练集的"规律"在测试集可能不存在（结构变化）。

### 8.3 过拟合控制——金融 ML 的生命线

| 技术 | 原理 |
|------|------|
| **样本外检验** | 严格 train/test 分割，**绝不**用测试集调参 |
| **时间序列交叉验证** | 用过去预测未来（walk-forward），**不能随机打乱**（避免未来信息泄漏） |
| **正则化** | LASSO（L1）/Ridge（L2）/Dropout——惩罚复杂度 |
| **信息准则** | AIC/BIC 在传统计量中惩罚参数数量 |
| **嵌套 CV** | 外层评估、内层调参，避免选择偏差 |
| **White's Reality Check / Hansen SPA** | 多模型比较的 data-snooping 调整 |

### 8.4 代码：LASSO vs OLS——过拟合控制实证

```python
import numpy as np
rng = np.random.default_rng(99)
T, P, T_test = 120, 50, 60      # 120训练, 50预测变量(仅3个有信号), 60测试

def make(n):
    X = rng.standard_normal((n, P))
    true_w = np.zeros(P); true_w[:3] = [0.3, -0.2, 0.15]
    y = X@true_w + 0.5*rng.standard_normal(n)
    return X, y

Xtr, ytr = make(T); Xte, yte = make(T_test)
mu = Xtr.mean(0); sd = Xtr.std(0); sd[sd==0]=1
Xtrs = (Xtr-mu)/sd; Xtes = (Xte-mu)/sd
ytrm = ytr - ytr.mean()

def lasso_cd(X, y, lam, iters=1000):       # 坐标下降 LASSO
    n, p = X.shape; w = np.zeros(p); c2 = (X**2).sum(0)
    for _ in range(iters):
        for j in range(p):
            r = y - X@w + X[:,j]*w[j]
            rho = X[:,j]@r
            w[j] = np.sign(rho)*max(abs(rho)-n*lam, 0)/c2[j]
    return w

w_ols = np.linalg.lstsq(Xtrs, ytrm, rcond=None)[0]
w_las = lasso_cd(Xtrs, ytrm, lam=0.05)

def r2(y, p): return 1 - np.sum((y-p)**2)/np.sum((y-y.mean())**2)
print("=== LASSO vs OLS：高维预测的过拟合控制 ===")
print(f"T={T}, P={P} (仅3个有信号), 测试集={T_test}")
print(f"非零系数: OLS={np.sum(np.abs(w_ols)>1e-6)}, LASSO={np.sum(np.abs(w_las)>1e-4)}")
print(f"\n{'方法':<8}{'样本内R²':>11}{'样本外R²':>11}")
print("-"*32)
for nm, w in [("OLS", w_ols), ("LASSO", w_las)]:
    ri = 1 - np.sum((ytrm-Xtrs@w)**2)/np.sum(ytrm**2)
    print(f"{nm:<8}{ri:>11.4f}{r2(yte, Xtes@w):>11.4f}")
print(f"\nLASSO系数[:5]: {np.round(w_las[:5],3)} (真值 [0.3,-0.2,0.15,0,0])")
```

**验证结果**：

```
=== LASSO vs OLS：高维预测的过拟合控制 ===
T=120, P=50 (仅3个有信号), 测试集=60
非零系数: OLS=50, LASSO=8

方法       样本内R²    样本外R²
--------------------------------
OLS          0.6495     -0.7559
LASSO        0.4020      0.2345

LASSO系数[:5]: [0.166 -0.199 0.038 -0. -0.] (真值 [0.3,-0.2,0.15,0,0])
```

> **洞察**：这是一堂"过拟合"的活体解剖课。
> - **OLS 样本内 R²=0.65**（看似很好），但**样本外 R²=−0.76**——比"预测均值"还差！它把 47 个噪声变量当信号记住了。
> - **LASSO 样本内 R²=0.40**（较低），但**样本外 R²=+0.23**——真正泛化了。它只留了 8 个非零系数，其中前 3 个正是真信号。
> - **教训**：金融 ML 的第一原则——**永远看样本外**。样本内 R² 是虚荣指标，样本外 R² 才是真理。Gu-Kelly-Xiu（2020）的实证显示，即使在最优 ML 设置下，月度收益预测的样本外 $R^2$ 也仅约 **0.4%–1%**——金融预测的"天花板"就是这么低。

---

## 九、因果推断——从"相关"到"因果"的跨越

> 传统金融计量回答"X 和 Y 相关吗？" 因果推断回答更难的问题："**X 导致了 Y 吗？**" 这两者的区别，是 2010 年代以来金融/经济学的方法论革命（2021 诺奖：Card、Angrist、Imbens）。

### 9.1 为什么"相关 ≠ 因果"

金融数据充满**混杂**（confounding）：股市上涨和冰淇淋销量都受"经济景气"驱动——它们相关，但**不是**彼此的原因。普通回归无法区分"相关"和"因果"。

**潜在结果框架（Rubin causal model）**：定义因果效应为 $Y_i(1) - Y_i(0)$（接受处理 vs 不接受）。但每人只能观测到一个（**因果推断的根本难题**）。因果推断的全部技巧，就是构造**反事实**（counterfactual）。

### 9.2 四把因果"手术刀"

| 工具 | 核心思想 | 金融应用举例 |
|------|---------|-------------|
| **自然实验 / 随机冲击** | 把"近乎随机"的外生事件当作"处理" | 公司被意外纳入指数 → 股价是否真因"纳入"而涨（需求曲线向下） |
| **工具变量（IV）** | 找一个只通过 X 影响 Y 的变量 Z | 用天气当 IV 研究大宗商品价格对经济的因果效应 |
| **双重差分（DID）** | 比较"处理组前后差"与"对照组前后差" | 某政策在一省试点：试点省 vs 非试点省，前后对比 |
| **断点回归（RDD）** | 在"阈值"两侧比较，阈值近乎随机 | 信用评分恰好过/不过线的贷款，违约率差异 |

### 9.3 因果推断在金融中的实例

- **Angrist & Krueger**：用出生季度当 IV 研究教育回报——开山之作。
- **指数纳入研究**：股票被**外生**纳入指数，其价格机械上涨（需求效应）——证明金融市场**需求曲线向下**（违背传统"无套利"直觉）。
- **DID 评估政策**：熔断机制、卖空禁令、T+0/T+1 制度对市场质量的因果效应。

### 9.4 计量上的关键区别

| | 相关（预测） | 因果（干预） |
|---|---|---|
| **问题** | 给定 X，Y 是多少？ | 若我**改变** X，Y 会怎样？ |
| **要求** | 相关关系稳定 | 外生变化（无混杂） |
| **风险** | 结构变化 → 失效 | 混杂 → 误判因果 |
| **金融含义** | 交易信号（可能过拟合） | 政策/战略决策（更稳健） |

> **essence 立场**：传统金融计量学大量做的是**预测性相关**（"这个因子能预测收益吗"），但金融决策真正需要的是**因果**（"如果我加仓这个因子，收益会真的变高吗"）。两者的混淆是无数"因子在样本外失效"悲剧的根源——**因为预测性相关 ≠ 因果效应**，而只有因果效应才在"干预"后依然成立。

---

## 十、计量危机——p-hacking、复制危机与"工具不是真理"

> 本节是 essence 项目的**方法论核心**：金融计量学不是"发现真理"的事业，它是"在噪声中谨慎提取信号"的工具。当它被当作真理，灾难随之而来。

### 10.1 p-hacking 与 data snooping

- **p-hacking**：反复尝试不同的样本期、变量组合、变换，直到 p<0.05。这是**系统性**地制造假阳性。
- **多重检验问题**：检验 100 个因子，即使全是噪声，也会有约 5 个"显著"（5% 水平）。金融已发表了 **400+ 因子**（Harvey 2017 统计），绝大多数可能是这种假阳性。

**调整方法**：Bonferroni 校正（保守）、White's Reality Check（White 2000）、Hansen's SPA（Superior Predictive Ability，2005）——这些方法对"我尝试了 N 个策略，挑了最好的"这种 data snooping 做 p 值修正。

### 10.2 复制危机——Hou-Xue-Zhang 的当头一棒

**Hou, Xue & Zhang（2020, RFS）** 做了一件震动业界的事：他们**复制了 452 篇**顶级金融期刊的实证研究，发现：

> **相当大比例的研究无法被复制**——尤其当涉及"显著因子"时。许多"发现"依赖于特定的样本期、数据处理选择、组合构造细节。换一个合理的设定，显著性就消失了。

这呼应了更广泛的**科学复制危机**（心理学率先爆发，金融学紧随其后）。它暴露的不只是"个别研究有问题"，而是**整个发表激励体系**的问题：期刊偏爱"显著的新发现"，而"显著的"恰恰最可能是**假阳性**。

### 10.3 三大元罪

| 元罪 | 表现 | 后果 |
|------|------|------|
| **选择性报告** | 只报显著的，隐藏尝试过的 | 文献被假阳性污染 |
| **样本期挖掘** | 专门挑"效果好"的历史区间 | 样本外崩溃 |
| **过拟合复杂模型** | 参数越多，样本内越好看 | 泛化失败 |

### 10.4 essence 的计量立场

> **计量是工具，不是真理。**

1. **谦逊优先**：金融数据少、噪声大、非平稳。任何"显著"结果都可能是运气。报告效应时，**永远同时报告**标准误、样本外表现、稳健性（换样本/换方法是否依然成立）。
2. **经济直觉先于统计显著性**：一个没有经济学故事的"显著因子"，大概率是 data mining。**先问"为什么"，再看 p 值。**
3. **可证伪性**：一个计量结果应该能被明确地"推翻"。无法被推翻的"规律"不是科学（Popper）。见 [`00-philosophy/epistemology.md`](../../00-philosophy/epistemology.md)。
4. **警惕模型即现实**：GARCH 不是"真实波动率过程"，它是一个**近似**。把模型当现实，就是 2008 年风险模型集体失效的认识论根源——VaR 模型说"安全"，因为它假设了过去，但未来不在过去里。这与 [`risk-and-uncertainty.md`](./risk-and-uncertainty.md) Knight 的"不确定性"批判一脉相承。
5. **复现是义务**：不可复现的结果不算知识。essence 的每段代码都可在 bash 中跑通——这正是对抗"幻觉式理解"的工程化手段。

---

## 十一、跨学科映射、开放问题与关联

### 11.1 跨学科映射

| 学科 | 金融计量学的对应/启发 |
|------|---------------------|
| **概率论** | 全部基础——估计/检验/置信区间都是统计推断。见 [`02-formal-sciences/probability/`](../../02-formal-sciences/probability/) |
| **信息论** | EMH = 价格是信息充分统计量；协整 = 共享信息维度 |
| **物理学（统计力学）** | 程式化特征的普适性、RV 的二次变差 ↔ 物理涨落。见 [`econophysics.md`](./econophysics.md) |
| **信号处理** | 高频降噪（子采样/核估计）= 数字信号处理；滤波（Kalman）用于潜在波动率 |
| **因果科学（CS/统计）** | Pearl 的 do-演算 ↔ IV/DID；反事实框架统一两者 |
| **机器学习** | 高维预测、正则化、表示学习——但低信噪比是噩梦 |
| **认识论** | 归纳问题（Hume）+ 可证伪性（Popper）+ 数据挖掘的认识论罪。见 [`00-philosophy/epistemology.md`](../../00-philosophy/epistemology.md) |
| **复杂系统** | 波动率聚集、相关性突变、相变式崩盘。见 [`06-systems/complexity/`](../../06-systems/complexity/) |

### 11.2 开放问题

1. **波动率可预测的上限在哪？** GARCH 能预测波动率，但**收益**呢？（EMH 说不能，但行为金融发现微弱可预测性——见 [`behavioral-finance.md`](./behavioral-finance.md)）。
2. **因子是风险补偿还是错误定价？** 每个因子（规模、价值、动量）都有"风险故事"和"行为故事"两种解释——计量无法独裁判决，需要 [`behavioral-finance.md`](./behavioral-finance.md) 的视角。
3. **机器学习会"解决"金融预测吗？** 还是信噪比太低，ML 注定只能榨出边际改进？Gu-Kelly-Xiu 的 1% R² 是天花板还是地板？
4. **因果推断能拯救因子研究吗？** 用自然实验给因子找"因果证据"，而非仅相关性——这是当下最前沿的方向。
5. **结构性断点能被预测吗？** 2008、2020、2022 都改变了市场结构。我们能**事前**知道"模型什么时候会失效"吗？（答案多半是不能——这正是 Knight 不确定性。）
6. **加密市场适用同样的计量吗？** DeFi 24/7、无熔断、流动性薄——程式化特征在加密市场是否成立？见 [`crypto-and-defi.md`](./crypto-and-defi.md)。

### 11.3 与 essence 其他文件的关联

| 关联文件 | 交叉点 |
|---------|--------|
| [`_overview.md`](./_overview.md) | 方法论表中"计量实证"一行；因子战争 |
| [`_philosophy-of-finance.md`](./_philosophy-of-finance.md) | 计量的可证伪性、归纳问题、模型即现实的危险 |
| [`markets-and-pricing.md`](./markets-and-pricing.md) | EMH 的计量检验（事件研究、方差比检验）；价格 = 信息聚合 |
| [`portfolio-theory.md`](./portfolio-theory.md) | CAPM/FF 因子的回归检验、GRS、β 估计 |
| [`econophysics.md`](./econophysics.md) | 程式化事实（肥尾、标度律、长记忆）；Mandelbrot 对正态的批判 |
| [`risk-and-uncertainty.md`](./risk-and-uncertainty.md) | 波动率 = Knight"风险"的度量；VaR 的局限；黑天鹅超出计量范围 |
| [`behavioral-finance.md`](./behavioral-finance.md) | 异象的计量检测；动量/反转的统计证据 |
| [`market-microstructure.md`](./market-microstructure.md) | 高频微观结构噪声；RV 的天敌 |
| [`derivatives.md`](./derivatives.md) | 隐含波动率 IV、波动率曲面、方差风险溢价 |
| [`ai-finance.md`](./ai-finance.md) | 机器学习计量（§八）的延伸——算法交易、深度预测 |

### 11.4 学习路径建议

1. **入门**：Tsay《Analysis of Financial Time Series》（GARCH/RV 经典教材）
2. **进阶**：Campbell, Lo & MacKinlay《The Econometrics of Financial Markets》（圣经级）
3. **高频**：Bacry, Delattre, Hoffmann, Muzy 等；Andersen-Diebold 实证 RV 文献
4. **因子战争**：Harvey《...and the Cross-Section of Expected Returns》（2017）；Hou-Xue-Zhang 复制研究
5. **ML**：Gu-Kelly-Xiu（2020, Empirical Asset Pricing via ML）；de Prado《Advances in Financial Machine Learning》
6. **因果**：Angrist & Pischke《Mostly Harmless Econometrics》；Pearl《Causality》

### 11.5 一句话总结

> 金融计量学是金融学的**经验法庭**——它用数据审判理论。但请永远记住 Lucas 的幽灵：**你发现的规律，正在因为你的发现而消亡。** 保持谦逊，拥抱不确定性，用代码验证每一个直觉。计量是照亮黑暗的火把，但它照不到的地方，比它能照到的大得多。

---

*建立日期：2026-07-16 · essence 项目 · 03-social-sciences/finance/financial-econometrics.md*
