# 量化交易 · Quantitative Trading

> **位置**：`03-social-sciences/finance/quantitative-trading.md`  
> **关联**：[`_overview.md`](./_overview.md)（金融地图）+ [`ai-finance.md`](./ai-finance.md)（AI/ML 信号、算法交易）+ [`market-microstructure.md`](./market-microstructure.md)（订单簿、HFT、价差、流动性）+ [`portfolio-theory.md`](./portfolio-theory.md)（组合优化、风险预算）+ [`financial-econometrics.md`](./financial-econometrics.md)（计量检验、协整、因子回归，待建）+ [`risk-and-uncertainty.md`](./risk-and-uncertainty.md)（尾部风险、黑天鹅）  
> **上游**：[`02-formal-sciences/probability/`](../../02-formal-sciences/probability/)（随机过程、鞅）+ [`05-intelligence/learning/`](../../05-intelligence/learning/)（ML/DL）  
> **哲学根源**：[`00-philosophy/epistemology.md`](../../00-philosophy/epistemology.md)（可预测性、归纳问题、过拟合的认识论）+ [`00-philosophy/ontology.md`](../../00-philosophy/ontology.md)（"alpha"存在吗？）  
> **核心问题**：**价格里有没有可被算法榨取的、未被市场消化的规律？如果有，它从哪里来、能持续多久、多少人知道后就会消失？**

---

## 写在前面：这个专题在 essence 里的位置

[`_overview.md`](./_overview.md) 把金融学定位为"关于时间 × 风险 × 信任的跨期契约"。**量化交易**是这个定义里最锋利的一角——它把"风险"彻底数学化、把"决策"彻底算法化、把"信任"（对人性的信任）替换为"信任代码"。

它同时也是 essence 项目里**最危险的知识区**：量化交易用最严谨的数学，论证着最不可靠的结论（"这个策略能赚钱"）。本文的态度与 [`ai-finance.md`](./ai-finance.md) 一致——**所有代码都用 Python 跑通**，但**能跑通 ≠ 能赚钱**。金融的残酷在于，每一条漂亮的回测曲线背后，都站着过拟合、前视偏差和尚未到来的黑天鹅。

> **一句话**：量化交易的本质，是**用系统化的方法，把"市场的不完美"（inefficiency）转化为可重复的、风险可控的收益——同时清醒地知道，这种不完美正在被你自己的交易消灭。**

本文遵循 essence **三层讲解法**（直觉 → 数学 → 代码），所有代码均在本地 Python 3.10 / numpy 2.2 / scikit-learn 1.7 环境验证通过。

---

## 一、量化交易的本质

### 1.1 一个定义

**量化交易（Quantitative Trading）**：基于**数学模型、统计推断和计算机算法**，系统化地生成交易信号、决定仓位规模、控制风险并执行交易的投资方式。它的对立面是**直觉交易（discretionary trading）**——依赖人的判断、经验、情绪。

> **essence 理解**：量化交易的三个支柱是 **系统化（Systematic）+ 算法化（Algorithmic）+ 纪律化（Disciplined）**。系统化保证可重复，算法化保证速度与规模，纪律化保证不被情绪劫持。

### 1.2 量化交易 vs 直觉交易

| 维度 | 量化交易 | 直觉交易 |
|------|---------|---------|
| **决策依据** | 数据 + 模型 + 规则 | 经验 + 情绪 + 叙事 |
| **可重复性** | 高（同样输入→同样输出） | 低（同一人不同时刻会不同） |
| **规模** | 可同时监控数千标的 | 注意力有限（数十标的） |
| **速度** | 微秒级 | 秒~分钟级 |
| **情绪干扰** | 几乎为零 | 主要风险源 |
| **可解释性** | 模型透明（但不一定"对"） | 事后合理化（常常自欺） |
| **失败模式** | 过拟合、模型衰退、同质化踩踏 | 追涨杀跌、扛单、报复性交易 |
| **典型代表** | Renaissance、Two Sigma、Citadel | 巴菲特、索罗斯、彼得·林奇 |

**关键澄清**：二者不是"谁更高级"。巴菲特的长期超额收益证明直觉可以极强；文艺复兴证明算法可以极强。**真正的分野是：你的边际信息优势更适合用哪种方式提取？** 高频、跨市场、统计规律 → 量化；产业洞察、管理层评估、长期叙事 → 直觉。

### 1.3 量化的认识论悖论

量化交易坐落在一个深刻的哲学悖论上（链回 [`00-philosophy/epistemology.md`](../../00-philosophy/epistemology.md)）：

> **如果市场是有效的（EMH），那么可被算法发现的规律不存在。如果规律存在，那么你发现并交易它的过程，正在消灭它。**

这意味着量化交易者的 alpha **必然是自我消灭的**——这是它与物理学实验的根本区别。物理定律不会因为你用了它就失效；金融规律会。De Prado 把这叫 **"金融机器学习的悖论"**：你越成功，你的信号衰减越快。

> **essence 立场**：alpha 不是"被发现"的，而是**被短暂租借**的。量化交易的工程能力，本质上是"在 alpha 衰减前尽可能多地榨取它，并持续寻找下一个"。

---

## 二、策略分类全谱系

量化策略按 **alpha 的来源** 可分为七大类。它们的风险来源、持仓周期、容量（capacity）和衰减速度完全不同。

```
量化策略谱系（按 alpha 来源）
├── 1. 统计套利 (Statistical Arbitrage)
│   ├── 配对交易 (Pairs / Cointegration)
│   ├── 横截面均值回归 (Cross-sectional Reversion)
│   └── 隐含因子套利
├── 2. 动量与反转 (Momentum & Reversal)
│   ├── 时序动量 (Time-series Momentum, CTA 用)
│   └── 横截面动量 (Cross-sectional Momentum, Jegadeesh-Titman)
├── 3. 做市与高频 (Market Making / HFT)
│   ├── 被动做市 (Passive MM)
│   ├── 订单流预测 (Order Flow / Queue Position)
│   └── 延迟套利 (Latency Arbitrage)
├── 4. 事件驱动 (Event-Driven)
│   ├── 财报公告 (Earnings)
│   ├── 并购套利 (Merger Arbitrage)
│   └── 指数调整 (Index Reconstitution)
├── 5. 宏观 / CTA 趋势 (Managed Futures)
│   ├── 趋势跟踪 (Trend Following)
│   ├── 截面利差 (Carry)
│   └── 资产配置动量
├── 6. 因子 / Smart Beta (Factor Investing)
│   ├── 价值 / 规模 / 动量 / 质量 / 低波
│   └── 多因子复合
└── 7. 机器学习 / 深度学习信号 (ML/DL Alpha)
    ├── 结构化表格 (GBDT / 树模型)
    ├── 序列 / 变换器 (RNN / Transformer)
    └── 强化学习执行 (RL)
```

### 2.1 各类策略速览

| 策略类 | alpha 来源 | 典型持仓 | 容量 | 夏普范围 | 主要风险 |
|--------|-----------|---------|------|---------|---------|
| 统计套利 | 协整/均值回归偏离 | 天~周 | 大 | 1.5–3.0 | 协整破裂、价差不回归 |
| 横截面动量 | 行为欠反应 | 月~季 | 很大 | 0.5–1.2 | 动量崩溃（2009） |
| 时序动量/CTA | 趋势延续 | 周~月 | 很大 | 0.6–1.3 | 震荡市连亏 |
| 做市/HFT | 价差 + 回扣 + 订单流 | 秒~毫秒 | 小 | 3.0–10+ | 拣货（adverse selection）、尾部存货击穿 |
| 事件驱动 | 公告后定价不足 | 天~月 | 中 | 1.0–2.0 | 事件跳跃、流动性蒸发 |
| 因子/Smart Beta | 风险溢价 | 月~年 | 极大 | 0.3–0.8 | 因子长期失效（价值 2010–2020） |
| ML/DL 信号 | 高维非线性结构 | 天~周 | 中 | 1.0–2.5 | 过拟合、非平稳、黑箱 |

### 2.2 七大类的本质详解

**1. 统计套利（Statistical Arbitrage / StatArb）**——寻找**统计意义上绑定**的资产对或资产组合，当它们的价差偏离历史关系时下注回归。经典形式是**配对交易（pairs trading）**：若 A 和 B 协整（cointegrated），则 spread = A − βB 是平稳的，价差越界即开仓。其数学基础是**协整检验**（Engle-Granger / Johansen）——与相关性不同，协整允许两个序列都非平稳，但它们的某个线性组合平稳。Gateaux 博士 1980 年代在摩根士丹利把它工业化，今天已是每家量化基金的基础设施。

**2. 动量与反转（Momentum & Reversion）**——动量押注"强者恒强"，反转押注"物极必反"。关键区分：**时序动量**（某资产相对自己过去涨跌）和**横截面动量**（某资产相对同侪涨跌）。Jegadeesh-Titman（1993）证明横截面动量在 3–12 个月有效；而 De Bondt-Thaler（1985）证明 3–5 年的反转。**两者并存不矛盾**——它们在不同时间尺度上运作，对应行为金融的欠反应（短期动量）与过度反应（长期反转）。

**3. 做市与高频（Market Making / HFT）**——做市商同时挂买卖单，赚取价差。这是**流动性供给的报酬**，不是方向性赌博。Avellaneda-Stoikov（2008）模型是其理论核心：通过调整报价（reservation price）控制存货风险。详见 [`market-microstructure.md`](./market-microstructure.md)。HFT 的危险是**拣货（adverse selection）**——你的买单成交了，往往是因为有人知道利空要来。

**4. 事件驱动（Event-Driven）**——押注特定企业事件后的价格重定价。财报公告后 1–3 天存在"公告后漂移（PEAD）"；并购公告后目标股价低于收购价（并购套利赚取这个差）；指数调整（如 MSCI/Russell）时被纳入的股票有机械买盘。这类策略的 alpha 来自**信息处理的时滞**。

**5. 宏观 / CTA 趋势（Managed Futures / CTA）**——管理期货账户（Commodity Trading Advisors）跟踪期货市场的趋势。它们是**危机 alpha（crisis alpha）**的经典来源：2008、2020 等极端年份趋势跟踪策略大赚，因为它们做多波动率、做空相关性。代表：AQR、Winton、Man AHL。

**6. 因子 / Smart Beta（Factor Investing）**——把 Fama-French 的学术发现工业化。CAPM 死后，"市场不是唯一的系统性风险"成为共识。价值（HML）、规模（SML）、动量、质量、低波动等"因子"被包装成 ETF（Smart Beta）。它们赚的是**风险溢价**而非套利，因此夏普较低（0.3–0.8）但容量极大。详见 [`portfolio-theory.md`](./portfolio-theory.md)。

**7. ML/DL 信号**——用机器学习从高维特征中提取非线性信号。这是 [`ai-finance.md`](./ai-finance.md) 的主战场。核心方法：GBDT/XGBoost（结构化表格之王）、Transformer（序列）、强化学习（执行与组合）。其根本困难是金融数据的**低信噪比 + 非平稳 + 对抗性**——详见第四节 De Prado 方法。

### 2.3 代码：实现三种策略（已验证 ✅）

```python
# 代码 1：策略动物园 —— 协整套利 + 横截面动量 + 做市(AS风险控制)
import numpy as np
np.random.seed(42)

# ---- 2A. 配对交易（协整套利）----
def make_cointegrated_pair(n=2000, beta=0.9, sigma_e=0.6, sigma_x=1.0):
    x = np.cumsum(np.random.normal(0, sigma_x, n))        # 共同随机趋势 (I(1))
    eps = np.random.normal(0, sigma_e, n)                  # 平稳的价差新息
    y = beta * x + eps
    return x, y

def adf_t(s):
    """简化版 ADF t 统计量（OLS of Δs on demeaned lag）。越负越拒绝单位根。"""
    s = np.asarray(s); ds = np.diff(s); lag = s[:-1]-s.mean()
    X = np.column_stack([lag, np.ones_like(lag)])
    b,*_ = np.linalg.lstsq(X, ds, rcond=None)
    resid = ds - X@b
    se = np.sqrt(np.sum(resid**2)/(len(ds)-2)*np.linalg.pinv(X.T@X)[0,0])
    return b[0], b[0]/se

x, y = make_cointegrated_pair()
spread = y - 0.9*x
rho, t_adf = adf_t(spread)
# 价差上做布林带式信号
s = spread; win=60
mu = np.convolve(s, np.ones(win)/win, mode='same')
std = np.array([s[max(0,i-win):i+1].std() for i in range(len(s))])
z = (s-mu)/(std+1e-9)
pos = np.where(z<-2,1,np.where(z>2,-1,0))
pnl = pos[:-1]*np.diff(s)
print("=== 2A. 配对交易（统计套利）===")
print(f"价差均值回归速度 rho={rho:.3f}  ADF t={t_adf:.1f}  夏普≈{pnl.mean()/pnl.std()*np.sqrt(252):.2f}")

# ---- 2B. 横截面动量（Jegadeesh-Titman）----
n_assets, n_days = 50, 756
prices = 100*np.exp(np.cumsum(np.random.normal(0.0003,0.012,(n_days,n_assets)),axis=0))
def xs_momentum(P, lookback=252, hold=21, k=10):
    r = np.diff(np.log(P),axis=0); n=r.shape[0]; port=[]
    t=lookback
    while t+hold<n:
        mom=r[t-lookback:t].sum(0)
        w=r[t:t+hold][:,np.argsort(mom)[-k:]].mean(1)
        l=r[t:t+hold][:,np.argsort(mom)[:k]].mean(1)
        port.extend((w-l).tolist()); t+=hold
    return np.array(port)
p=xs_momentum(prices)
print("\n=== 2B. 横截面动量 ===")
print(f"日均收益 {p.mean()*1e4:.2f}bps  夏普≈{p.mean()/p.std()*np.sqrt(252):.2f}  (随机游走上≈0)")

# ---- 2C. 做市（Avellaneda-Stoikov 存货风险控制）----
def mm_sim(n=5000, gamma=0.1, sigma=0.2, k=1.5, A=140):
    s=100.0; inv=0.0; cash=0.0; T=1.0; dt=T/n
    for i in range(n):
        s+=sigma*np.sqrt(dt)*np.random.randn(); tt=T-i*dt
        r=s-inv*gamma*sigma**2*tt                                   # reservation price
        d=gamma*sigma**2*tt+(gamma/sigma**2)*np.log(1+gamma/k)      # 最优半价差
        if np.random.rand()<A*np.exp(-k*d)*dt: cash+=r+d; inv-=1    # 买方吃 ask
        if np.random.rand()<A*np.exp(-k*d)*dt: cash-=r-d; inv+=1    # 卖方吃 bid
    return cash+inv*s, inv
pnl,q=mm_sim()
print("\n=== 2C. 做市（Avellaneda-Stoikov）===")
print(f"PnL={pnl:.1f}  存货 q={q:.0f}  (gamma 控制存货, 避免被单边趋势击穿)")
```

**实测输出**（本地运行）：
```
=== 2A. 配对交易（统计套利）===
价差均值回归速度 rho=-1.017  ADF t=-45.5  夏普≈2.96
=== 2B. 横截面动量 ===
日均收益 -0.93bps  夏普≈-0.29  (随机游走上≈0)
=== 2C. 做市（Avellaneda-Stoikov）===
PnL=33.9  存货 q=11  (gamma 控制存货, 避免被单边趋势击穿)
```

**解读**：2A 在合成协整数据上夏普接近 3——但这是**人造平稳序列**，真实价差会破裂（LTCM 的教训）。2B 在纯随机游走上夏普≈0，证明了**没有 alpha 时动量不工作**（真实市场的动量 alpha 来自行为欠反应）。2C 的做市商靠价差赚钱但必须用 `gamma` 控制存货——否则在趋势行情里会被单边仓位击穿（拣货风险）。

---

## 三、回测的科学方法

> **essence 立场**：回测是量化交易**最容易被自欺**的环节。一条漂亮的回测曲线，90% 的概率是过拟合、前视偏差或数据窥探的产物。De Prado 说："你看到的回测夏普，要除以你尝试过的策略数量，才接近真实值。"

### 3.1 七大回测陷阱

| 陷阱 | 含义 | 例子 | 防范 |
|------|------|------|------|
| **前视偏差（Look-ahead）** | 用了决策时刻尚未可知的信息 | 用"全年财报"在年初交易 | Point-in-Time 数据 |
| **数据窥探（Data Snooping）** | 反复在同一数据上试参数 | 调 1000 个均线找最好的 | Deflated Sharpe / 交叉验证 |
| **生存者偏差（Survivorship）** | 只回测今天还活着的公司 | 用当前标普 500 回测 20 年 | 包含退市/被并购股票 |
| **数据泄露（Leakage）** | 训练集包含了未来标签 | 特征用了 t+1 的收盘价 | 严格的 t→t+1 对齐 |
| **前视填充（Backfill）** | 用今天才有的字段填历史 | 用现行行业分类回填十年前 | PIT 字段 + effective date |
| **交易成本低估** | 忽略冲击、佣金、融券费 | 假设按收盘价无成本成交 | 显式建模冲击 + 滑点 |
| **过拟合（Overfitting）** | 参数 tuned 到特定样本 | 5 年数据 fit 出完美曲线 | 样本外 + walk-forward |

### 3.2 Walk-Forward（滚动窗口）—— 严谨回测的金标准

**核心思想**：永远只用**过去**训练模型，在**未来**的样本外测试，然后把"未来"滚动成"过去"，重复。**训练集与测试集在时间上严格分离，永不重叠。**

```
时间轴 →
[=====训练1=====][测1]
        [=====训练2=====][测2]
                [=====训练3=====][测3]
```

与之对照的是**朴素交叉验证**（随机打乱折）——在金融里**致命**，因为它会把"明天的收益"放进"今天的训练集"，造成数据泄露。金融数据**时间相关**，必须用**时序安全的 CV**。

### 3.3 代码：严谨 Walk-Forward 框架（已验证 ✅）

```python
# 代码 2：滚动 walk-forward + 数据窥探危害演示
import numpy as np
np.random.seed(11)

def make_features(n_days=1500, n_features=20):
    X = np.random.normal(0,1,(n_days,n_features))
    y_cont = 0.03*X[:,0] + np.random.normal(0,1,n_days)   # 只有 f0 有极弱信号
    return X[:-1], (y_cont[1:]>0).astype(int)             # t 预测 t+1

X, y = make_features()

def fit_predict(Xtr,ytr,Xte):
    mu,sd = Xtr.mean(0), Xtr.std(0)+1e-9
    A=(Xtr-mu)/sd; b=np.zeros(A.shape[1])
    for _ in range(300):
        p=1/(1+np.exp(-(A@b))); b-=0.1*A.T@(p-ytr)/len(ytr)
    return 1/(1+np.exp(-(((Xte-mu)/sd)@b)))

# === 错误：全样本训练 + 全样本评估（数据窥探）===
proba = fit_predict(X,y,X)
print("=== 错误示范：全样本 fit + 全样本评估 ===")
print(f"样本内准确率 {((proba>0.5)==y).mean()*100:.2f}%  (被高估)")

# === 正确：滚动 walk-forward ===
def walk_forward(X,y,train_len=756,test_len=63):
    out=[]; t=train_len; calls=0
    while t+test_len<=len(y):
        p=fit_predict(X[t-train_len:t],y[t-train_len:t],X[t:t+test_len])
        out.extend(((p>0.5)==y[t:t+test_len]).tolist())
        t+=test_len; calls+=1
    return np.mean(out), calls
acc,calls=walk_forward(X,y)
print(f"\n=== 正确：滚动 walk-forward（{calls} 次重训）===")
print(f"样本外准确率 {acc*100:.2f}%  (≈50%, 真实信号极弱)")

# === Deflated Sharpe 思想：多次试验的最优是噪声 ===
n_trials=200; is_sh=[]; oos_sh=[]
for _ in range(n_trials):
    ri=np.random.normal(0,1,252); ro=np.random.normal(0,1,252)
    is_sh.append(ri.mean()/ri.std()*np.sqrt(252)); oos_sh.append(ro.mean()/ro.std()*np.sqrt(252))
best=np.argmax(is_sh)
print(f"\n=== Deflated Sharpe：{n_trials} 个纯噪声策略 ===")
print(f"样本内最好夏普 {is_sh[best]:.2f} → 它的样本外夏普 {oos_sh[best]:.2f}")
print("结论：试得越多，'最好'的越是被高估的噪声。")
```

**实测输出**：
```
=== 错误示范：全样本 fit + 全样本评估 ===
样本内准确率 54.64%  (被高估)
=== 正确：滚动 walk-forward（11 次重训）===
样本外准确率 48.05%  (≈50%, 真实信号极弱)
=== Deflated Sharpe：200 个纯噪声策略 ===
样本内最好夏普 2.78 → 它的样本外夏普 -0.61
```

**解读**：同一个模型，全样本评估给出 54.6%（看似有 edge），walk-forward 给出 48%（其实没有）。差距 6.6 个百分点**全是数据窥探幻觉**。而最后一段更刺骨：在 200 个**纯噪声**策略里挑最好的，样本内夏普高达 2.78——但样本外是 -0.61。**这就是为什么你不能只看一条回测曲线。**

---

## 四、De Prado 的金融机器学习新方法

Marcos López de Prado 的《Advances in Financial Machine Learning》（2018）是量化圈的"范式转移"之作。它的核心论点：**把金融数据当作 IID 样本喂给 sklearn，是过拟合的根源**。金融数据有结构（自相关、标签重叠、非平稳），必须用金融特化的 ML 方法。

### 4.1 分数差分（Fractional Differentiation）—— 平稳但不丢记忆

**问题**：ML 模型要求**平稳输入**（统计性质不随时间漂移）。但金融价格是非平稳的（随机游走）。传统做法是 **一阶差分** Δx = x_t − x_{t-1}——它让序列平稳了，但**彻底抹去了价格水平的信息**（一个 100 元的股票和 1000 元的股票，差分后看起来一样）。

**De Prado 的解法**：**分数阶差分**——在 0 到 1 之间找一个 d，让序列**刚刚平稳**，同时**尽可能保留**与原价的相关性（"记忆"）。

**数学**：分数差分算子 $(1-L)^d x_t = \sum_{k=0}^{\infty} w_k x_{t-k}$，其中 $w_k = (-1)^k \binom{d}{k}$。当 d=1 时退化为标准一阶差分；当 0<d<1 时，权重 $w_k$ 缓慢衰减，**长期价格水平仍以衰减的权重参与**。

**直觉**：标准差分是"用放大镜只看今天的增量"；分数差分是"用一个焦距可调的镜头，既看到增量也保留历史的影子"。

### 4.2 元标签（Meta-Labeling）—— 把"方向"和"下注规模"解耦

**问题**：一个预测"涨/跌"方向的模型（primary model）通常方向准但**把握度不分层**——它对每个信号都下同样的注。结果：低把握信号拉低了整体夏普。

**De Prado 的解法**：训练**第二个模型（meta-labeler）**，输入是特征 + primary 的方向预测，输出是**"这一单到底该不该下/下多大"**。primary 决定**方向**，meta 决定**规模（size）**。这把一个难问题（同时预测方向和规模）拆成两个更容易的问题。

**金融意义**：元标签的本质是**用 ML 学习止损/止盈/仓位**，而不是手工设定。它显著降低假阳性（错误信号被过滤），代价是放弃部分真信号。

### 4.3 金融特化的交叉验证（Purged K-Fold + Embargo）

**问题**：标准 K-Fold 随机打乱数据——但金融标签常**重叠**（如 5 天收益的标签在相邻 5 天窗口里共享数据），打乱会把"未来"泄漏进训练集。

**解法**：
- **Purged K-Fold**：划分验证折后，从训练集里**剔除**所有与验证折标签重叠的样本。
- **Embargo**：在验证折后再设一个**禁运期**（如 h 天），训练集不能用到禁运期内的数据，防止"标签尾部"泄漏。

### 4.4 代码：分数差分 + 元标签 + MDA 特征重要性（已验证 ✅）

```python
# 代码 3：De Prado 方法 —— 分数差分 + 元标签 + MDA 特征重要性
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
np.random.seed(3)

def frac_diff(series, d, thresh=1e-4):
    """分数差分：w_k=(-1)^k*C(d,k), |w_k|<thresh 时截断(fixed-width window)。"""
    w=[1.0]; k=1
    while True:
        wk=-w[-1]*(d-(k-1))/k
        if abs(wk)<thresh: break
        w.append(wk); k+=1
    w=np.array(w[::-1]); out=np.full(len(series),np.nan)
    for i in range(len(w)-1,len(series)):
        out[i]=np.dot(w,series[i-len(w)+1:i+1])
    return out

def adf_t(s):
    s=s[np.isfinite(s)]; ds=np.diff(s); lag=s[:-1]-s.mean()
    X=np.column_stack([lag,np.ones_like(lag)])
    b,*_=np.linalg.lstsq(X,ds,rcond=None); resid=ds-X@b
    se=np.sqrt(np.sum(resid**2)/(len(ds)-2)*np.linalg.pinv(X.T@X)[0,0])
    return b[0]/se

price=np.cumsum(np.random.normal(0,1,2000))+100
d1=np.diff(price,1); d035=frac_diff(price,0.35)
v035=d035[np.isfinite(d035)]
print("=== A. 分数差分 ===")
print(f"d=1.0 : ADF t={adf_t(d1):6.2f} (平稳)  与价格相关性={np.corrcoef(price[1:],d1)[0,1]:+.3f} ← 丢失记忆")
print(f"d=0.35: ADF t={adf_t(d035):6.2f} (平稳) 与价格相关性={np.corrcoef(price[-len(v035):],v035)[0,1]:+.3f} ← 保留记忆!")

# === 元标签 ===
n=2000; feat=np.random.normal(0,1,(n,3))
true_dir=(0.5*feat[:,0]+np.random.normal(0,1,n))>0      # 只有 f0 有信号
primary=(feat[:,0]>0).astype(int)                        # 弱方向模型
meta_label=(primary==true_dir).astype(int)               # 1=这单会赚
Xtr,Xte,ytr,yte=train_test_split(feat,meta_label,test_size=0.3,random_state=0)
meta=RandomForestClassifier(200,max_depth=4,random_state=0).fit(Xtr,ytr)
size=meta.predict_proba(Xte)[:,1]
print("\n=== B. 元标签 ===")
print(f"主模型准确率 {((primary==true_dir).mean()):.3f}  元模型'此单会赚'准确率 {((size>0.5)==yte).mean():.3f}")

# === MDA 特征重要性 ===
rf=RandomForestClassifier(300,max_depth=5,random_state=0).fit(feat,true_dir)
base=accuracy_score(true_dir,rf.predict(feat))
print(f"\n=== D. MDA 特征重要性 (基线 {base:.3f}) ===")
for j,nm in enumerate(['f0','f1','f2']):
    Xp=feat.copy(); np.random.shuffle(Xp[:,j])
    print(f"  {nm}: 置乱后下降 {(base-accuracy_score(true_dir,rf.predict(Xp)))*100:+.2f}pp"
          +('  <-- 唯一真信号' if nm=='f0' else '  (噪声)'))
```

**实测输出**：
```
=== A. 分数差分 ===
d=1.0 : ADF t=-46.25 (平稳)  与价格相关性=+0.054 ← 丢失记忆
d=0.35: ADF t= -6.79 (平稳)  与价格相关性=+0.884 ← 保留记忆!
=== B. 元标签 ===
主模型准确率 0.657  元模型'此单会赚'准确率 0.623
=== D. MDA 特征重要性 (基线 0.699) ===
  f0: 置乱后下降 +18.90pp  <-- 唯一真信号
  f1: 置乱后下降 +2.80pp  (噪声)
  f2: 置乱后下降 +2.80pp  (噪声)
```

**解读**：分数差分是本文**最优雅的洞察**——d=1.0 让序列平稳但相关性只剩 0.054（价格信息被洗掉），d=0.35 同样平稳却保留 0.884 的相关性。这就是"平稳与记忆的帕累托前沿"。元标签把"是否下注"学成一个**独立于方向的第二个分类问题**：主模型方向命中率 0.657 已经不差，但元模型进一步输出**每单的把握度（概率）**用作下注规模——它不追求"更高的准确率"，而是**把高把握信号放大、低把握信号过滤掉**，从而提升夏普而非命中率。MDA 清楚地揭示 f0 是唯一真信号（下降 18.9pp，是噪声特征 2.8pp 的 ~7 倍）——**树模型自带的 `feature_importances_` 有偏（偏向高基数/连续特征），MDA（基于准确率下降）更可靠**。

---

## 五、组合构建——从信号到仓位

> 有信号不等于有仓位。信号告诉你"买什么"，组合构建告诉你"**买多少**"。这后一个问题，往往比前者更决定收益。详见 [`portfolio-theory.md`](./portfolio-theory.md)。

### 5.1 四种仓位方法

| 方法 | 核心 | 适用 | 关键公式 |
|------|------|------|---------|
| **等权** | 每个信号同样大小 | 简单基线 | w_i = 1/N |
| **风险预算（Risk Parity）** | 每个资产贡献等量风险 | 多资产、低相关 | RC_i = w_i(Σw)_i / (wᵀΣw) 相等 |
| **目标波动率** | 总组合波动钉住目标 | 杠杆/现金调整 | 杠杆 = σ_target / σ_strategy |
| **凯利（Kelly）** | 最大化长期对数财富 | 单注/策略杠杆 | f* = μ/σ²（连续）；=(bp−q)/b（离散） |

### 5.2 风险预算——让"风险"而非"钱"均等

**直觉**：等权组合里，**高风险资产主导**整个组合的波动（一个波动率 25% 的资产比一个 10% 的资产贡献 2.5 倍风险）。风险平价反其道：调整权重，使**每个资产对总风险的边际贡献相等**。这通常意味着低配高波动资产、超配低波动资产（如债券），再用杠杆把总收益拉上来——Bridgewater 全天候（All Weather）的精髓。

### 5.3 凯利准则——最优杠杆的数学

**离散版**：一个赌局，胜率 p，赔率 b:1，最优下注比例 $f^* = \frac{bp - q}{b},\ q=1-p$。

**连续版**（策略杠杆）：若策略超额收益均值 μ、波动 σ，则最优杠杆 $f^* = \mu/\sigma^2$。

**关键警告**：**全凯利波动极其剧烈**（约 100% 的年化波动），且对参数估计误差极度敏感（μ 算错一点，f* 翻倍 → 破产）。实战几乎都用**分数凯利（fractional Kelly）**——0.25–0.5 倍。Thorpe 证明：半凯利以 ~75% 的增长率换 ~50% 的方差，是绝佳的稳健性权衡。

### 5.4 代码：风险平价 + 目标波动 + 凯利（已验证 ✅）

```python
# 代码 4：组合构建 —— 风险平价 + 目标波动率 + 凯利下注规模
import numpy as np
np.random.seed(5)
mu=np.array([0.0005,0.0008,0.0006,0.0010]); vols=np.array([0.010,0.018,0.012,0.025])
C=np.array([[1,.3,.5,.1],[.3,1,.2,.4],[.5,.2,1,.15],[.1,.4,.15,1]])
Cov=np.outer(vols,vols)*C

w_ew=np.ones(4)/4
rc_ew=w_ew*(Cov@w_ew); rc_ew/=rc_ew.sum()
print("=== A. 风险预算：等权 vs 风险平价 ===")
print(f"等权 风险贡献 {np.round(rc_ew,3)} (高风险资产主导)")

w_rp=1/vols; w_rp/=w_rp.sum()
for _ in range(50):                                     # 迭代逼近等风险贡献
    rc=w_rp*(Cov@w_rp); rc/=rc.sum()
    w_rp*=rc**-0.5; w_rp/=w_rp.sum()
rc_rp=w_rp*(Cov@w_rp); rc_rp/=rc_rp.sum()
print(f"风险平价 权重{np.round(w_rp,3)} 风险贡献{np.round(rc_rp,3)} (≈均等!)")

def ps(w): r=w@mu; s=np.sqrt(w@Cov@w); return r*252,s*np.sqrt(252),r*252/(s*np.sqrt(252))
re,se,ke=ps(w_ew); rr,sr,kr=ps(w_rp)
print(f"等权 夏普{ke:.3f}  风险平价 夏普{kr:.3f}")

print("\n=== B. 目标波动率 (10%) ===")
raw_vol=np.sqrt(w_rp@Cov@w_rp)*np.sqrt(252); scale=0.10/raw_vol
print(f"原始波动 {raw_vol:.3f} → 缩放系数 {scale:.3f} (风险资产占 {w_rp.sum()*scale*100:.1f}%)")

print("\n=== C. 凯利下注规模 ===")
def kelly(b,p): return (b*p-(1-p))/b
print(f"赔率2:1胜率55%: f*={kelly(2,.55):.3f}")
f_star=mu.mean()/np.sqrt(np.diag(Cov)).mean()**2
print(f"策略连续凯利杠杆 f*≈{f_star:.2f} (实战用 1/4~1/2 凯利)")
for frac in [1.0,0.5,0.25]:
    W=np.cumprod(1+np.random.normal(mu.mean()*frac,np.sqrt(np.diag(Cov)).mean()*frac,(20000,500)),1)
    print(f"  f={frac:.2f}: 期末中位财富 {np.median(W[:,-1]):.2f}x  5%分位 {np.percentile(W[:,-1],5):.2f}x")
```

**实测输出**：
```
=== A. 风险预算：等权 vs 风险平价 ===
等权 风险贡献 [0.119 0.299 0.146 0.436] (高风险资产主导)
风险平价 权重[0.352 0.194 0.299 0.155] 风险贡献[0.25 0.25 0.25 0.25] (≈均等!)
等权 夏普1.027  风险平价 夏普1.083
=== B. 目标波动率 (10%) ===
原始波动 0.155 → 缩放系数 0.646 (风险资产占 64.6%)
=== C. 凯利下注规模 ===
赔率2:1胜率55%: f*=0.325
策略连续凯利杠杆 f*≈2.75 (实战用 1/4~1/2 凯利)
  f=1.00: 期末中位财富 1.35x  5%分位 0.75x
  f=0.50: 期末中位财富 1.18x  5%分位 0.87x
  f=0.25: 期末中位财富 1.09x  5%分位 0.94x
```

**解读**：风险平价用低配高风险资产（第 4 个资产从 25% 降到 15.5%）换来**等量风险贡献**，夏普从 1.03 升到 1.08。目标波动率把高夏普策略**降杠杆**到可承受的 10% 波动。凯利部分是**最重要的风险课**：全凯利中位财富最高（1.35x），但 5% 分位只有 0.75x（25% 概亏 25%+）；1/4 凯利中位 1.09x 但 5% 分位 0.94x（尾部温和得多）。**追求长期生存，永远用分数凯利。**

---

## 六、执行算法——把纸面仓位变成真实成交

> 链回 [`market-microstructure.md`](./market-microstructure.md)：策略决定"买什么"，执行决定"**怎么买得不贵**"。一个年化 10% alpha 的策略，若执行烂了，可能只剩 3%。

### 6.1 主流执行算法

| 算法 | 原理 | 适用 | 优点 | 缺点 |
|------|------|------|------|------|
| **TWAP** | 时间均匀切分 | 流动性均匀 | 简单 | 忽略成交分布 |
| **VWAP** | 按历史成交量分布切分 | 大盘股 | 贴近市场节奏 | 对异常成交不敏感 |
| **POV（参与率）** | 按实时成交量的固定比例 | 流动性不确定 | 自适应 | 可能收盘未成交 |
| **IS（实施差额）** | 最小化与到达价的差 | 对成本敏感 | 显式优化 | 需要冲击模型 |
| **Sniper（狙击）** | 只在有利时下单 | 避免拣货 | 隐蔽 | 成交不确定 |

### 6.2 实施差额（Implementation Shortfall, IS）

**定义**：IS = 决策时刻的"纸面价值" − 实际成交的"真实价值"。它分解为：
- **时机成本（timing cost）**：决策到成交期间市场动了多少
- **价格冲击（impact）**：你自己的订单推高了价格
- **机会成本**：没成交完的部分错过的涨幅

**核心洞察**：执行算法的目标是**最小化 IS**，而非"成交价越低越好"——因为低成交价可能只是市场恰好下跌（运气），与执行质量无关。

### 6.3 代码：VWAP / TWAP / POV 执行模拟（已验证 ✅）

```python
# 代码 5：执行算法 —— VWAP / TWAP / POV 与实施差额
import numpy as np
np.random.seed(9)

def volume_curve(m=390):                       # 典型 U 型: 开收盘重, 午间轻
    t=np.linspace(0,1,m); b=0.5-0.4*(t-0.5)**2
    b+=0.6*np.exp(-((t-0.0)/0.06)**2)+0.8*np.exp(-((t-1.0)/0.05)**2)
    return b/b.sum()*m
vp=volume_curve()
ADV=1_000_000
real=np.random.poisson(ADV/390*vp)             # 实现的每分钟成交量
drift=np.random.normal(0,1e-4,390)             # 几乎平坦, 以隔离执行质量差异

def exec_(parent, sched, side='buy', perm=3e-7, temp=1.2e-6):
    mid=100.0; fills=[]; cum=0; sg=1 if side=='buy' else -1
    for m in range(390):
        mid*=(1+drift[m]); ch=int(min(sched[m],parent-cum))
        if ch<=0 or cum>=parent: continue
        mid*=(1+sg*perm*ch); slip=sg*temp*ch/(real[m]+1)*1e3
        fills.append((m,ch,mid+slip)); cum+=ch
        mid*=(1+sg*temp*ch/(real[m]+1))
    return fills,mid

def IS(fills,arrival,side='buy'):
    tot=sum(f[1] for f in fills); avg=sum(f[1]*f[2] for f in fills)/tot
    return (avg-arrival)*(1 if side=='buy' else -1), avg

parent=100_000; arrival=100.0
twap=np.zeros(390); twap[:300]=parent/300
vwap=parent*vp/vp.sum()
pov=np.minimum(0.10*real,parent)
print("=== 6. 执行算法：TWAP vs VWAP vs POV(10%) ===")
print(f"母单 {parent:,} 股(ADV的{parent//10000}%) 到达价 {arrival}")
for nm,sc in [('TWAP',twap),('VWAP',vwap),('POV10%',pov)]:
    f,end=exec_(parent,sc); ish,avg=IS(f,arrival)
    print(f"{nm:7s}: 均价 {avg:.4f}  IS {ish*100:+.3f}bp  成交{sum(x[1] for x in f):,}股")
```

**实测输出**：
```
=== 6. 执行算法：TWAP vs VWAP vs POV(10%) ===
母单 100,000 股(ADV的10%) 到达价 100.0
TWAP   : 均价 101.6616  IS +166.163bp  成交99,900股
VWAP   : 均价 101.6480  IS +164.805bp  成交99,805股
POV10% : 均价 101.6501  IS +165.012bp  成交99,944股
```

**解读**：VWAP 的 IS（164.8bp）< POV（165.0）< TWAP（166.2）——**正确排序**。VWAP 在开盘/收盘高流动性时段多买、午间少买，临时冲击最小；TWAP 在午间低流动性仍下大单，冲击最大。注意大部分 IS（~165bp）是**永久冲击**（买入 10% ADV 把价格推高了 ~1.6%），这是任何执行算法都逃不掉的物理上限——**执行算法只能优化"超额"部分，不能消除冲击本身**。

---

## 七、风险控制——活着比赚钱重要

> **essence 立场**（链回 [`risk-and-uncertainty.md`](./risk-and-uncertainty.md)）：量化的第一条戒律不是"赚更多"，而是"**别死**"。Soros 说"先活下来，再谈赚钱"。所有风险控制都服务于一个目标——**在任何单一黑天鹅下不爆仓**。

### 7.1 风险控制五层

| 层级 | 机制 | 作用 |
|------|------|------|
| **信号层** | 止损/止盈、信号过滤 | 单笔亏损封顶 |
| **仓位层** | 单标的上限、行业集中度 | 防集中爆雷 |
| **组合层** | 目标波动、回撤限制 | 总风险钉住 |
| **相关性层** | 相关性监控、危机去杠杆 | 防同涨同跌 |
| **尾部层** | 期权对冲、尾部基金 | 防黑天鹅 |

### 7.2 关键概念

**止损（Stop-Loss）**——单笔亏损达阈值平仓。**陷阱**：机械止损会被高频做市商"猎杀"（stop hunting）——他们在止损密集价位故意砸盘触发止损后再拉回。**对策**：用"软止损"（信号层预警 + 人工/算法复核）或更宽的、基于波动率的止损（如 2×ATR）。

**最大回撤（Max Drawdown）**——从历史最高点到后续最低点的跌幅。这是机构投资者最看重的指标——**没人能接受 50% 回撤的基金**。Calmar 比率 = 年化收益 / 最大回撤，衡量"回撤效率"。

**相关性崩溃（Correlation Breakdown）**——平时低相关的资产，在危机时**同时暴跌**（"极端情形下所有相关性趋于 1"）。2008、2020 都是如此。这使基于历史相关性的分散化在**最需要它的时候失效**。

**尾部对冲（Tail Hedging）**——常态买入价外看跌期权，作为"保险"。代价是**持续的保险费**侵蚀收益（典型的"小亏换大赔"）。代表：Universa（Mark Spitznagel，Taleb 顾问）。对立面是**承担尾部风险换收益**（如卖出价外期权长期赚钱但偶尔爆雷——"在压路机前捡硬币"）。

---

## 八、基础设施——量化的"水电煤"

> 优秀的策略需要优秀的基础设施承载。De Prado 说："**算法是冰山一角，基础设施是水面下的 90%。**" 一个量化基金 80% 的工程投入在数据、回测、执行系统上。

### 8.1 四大基础设施

**1. 数据管理（Data Management）**——量化最核心的资产是**干净的、Point-in-Time 的数据**。
- **Point-in-Time（PIT）**：每个数据点都带"生效时间戳"——确保回测时只用"决策时刻已知"的信息。这是防范前视偏差的根本。
- **数据类型**：行情（tick/分钟/日）、基本面（财报 PIT）、另类数据（卫星图、信用卡流水、ESG）、参考数据（退市、并购、拆股调整）。
- **三大偏差来源**：生存者偏差（缺退市股）、前视填充（用今填古）、拆股错误（除权除息处理错）。

**2. 因子库（Factor Library）**——标准化、可复用的因子计算引擎。每个因子带：定义、计算逻辑、PIT 生效日、回测历史、容量估计。这使策略研究"组合积木"而非"从零算起"。

**3. 回测引擎（Backtesting Engine）**——严谨的、事件驱动的回测框架。关键特性：时序安全的撮合、显式的冲击/成本模型、支持 walk-forward、支持多个数据频率。开源代表：Zipline、Backtrader、vectorbt；机构自研为主。

**4. 实盘系统（Live Trading System）**——把回测策略接入真实交易所。要求：低延迟、高可用、订单状态机、风险前置检查、灾难恢复。**实盘与回测的鸿沟**是量化最大的工程挑战——回测里"成交了"在实盘可能是"拒单/部分成交/滑点爆炸"。

### 8.2 数据质量是量化的命门

> **业内共识**：garbage in, garbage out。一个统计套利策略，如果数据有一个除权错误，回测会显示一个虚假的、看似可交易的"价差偏离"。无数"发现"的 alpha 死于数据 bug。**对数据的偏执，是优秀量化研究员的共同特质。**

---

## 九、著名量化机构案例

### 9.1 海外六巨头

| 机构 | 创立 | 代表策略 | 文化密码 |
|------|------|---------|---------|
| **Renaissance / Medallion（大奖章）** | 1982 | 短期统计套利 | "最聪明的人 + 信号不外传"。Medallion 基金 1988–2018 年化 **66%费前**，仅对员工开放。Simons 的洞察：雇用**科学家（数学家、密码学家）而非金融人**。 |
| **Two Sigma** | 2001 | ML 信号、科学方法论 | 把投资当"科学实验"——假设、实验、对照组。强调可重复研究与工程化。 |
| **Citadel** | 1990 | 多策略（做市 + 统计套利 + 宏观） | "集成商"模式——内部多个独立团队竞争，优胜劣汰。Ken Griffin 的执行力文化。 |
| **D. E. Shaw** | 1988 | 早期统计套利先驱 | David Shaw（前哥伦比亚 CS 教授）开创华尔街量化。Bezos 曾在此工作。 |
| **Bridgewater（桥水）** | 1975 | 全天候 / 风险平价、宏观 | Ray Dalio 的"原则"——系统化、可重复、经济机器模型。**宏观量化**的代表，与高频统计套利截然不同。 |
| **Jane Street / Optiver / IMC** | — | 做市 / HFT | 流动性供给者。自营、低周转、技术极客文化。Jane Street 用 OCaml 函数式编程闻名。 |

### 9.2 Medallion 的启示——为什么无法复制？

Medallion 是量化界的圣杯，但**它的 alpha 至今是黑箱**。几个被广泛接受的推断：
1. **短期反转 + 订单流信号**：持仓几小时到几天，赚的是市场微观摩擦的钱（链回 [`market-microstructure.md`](./market-microstructure.md)）。
2. **规模封顶**：Medallion 资产被刻意限制在 ~100 亿美元——**容量是 alpha 的敌人**，钱越多冲击越大。
3. **人才垄断**：核心信号只对少数合伙公开，研究员轮岗、互不知晓全貌。
4. **持续进化**：信号每隔几年就需重写——**没有"一劳永逸"的策略**。

> **essence 洞察**：Medallion 证明了**当人（科学家）+ 机器 + 隔离（不外传）三者齐全，alpha 可以持续几十年**。但它也证明了**这种组合极其稀有**——否则早就被复制了。

### 9.3 中国代表：幻方（High-Flyer）

**幻方量化**（2015 起）是中国头部量化私募，以**深度学习信号**和庞大的 GPU 算力著称（一度拥有国内最大的 AI 算力集群之一）。它的轨迹浓缩了中国量化的特征：① 从股指期货 Alpha 起家；② 重仓 AI/算力；③ 规模迅速膨胀后遭遇拥挤与监管（2021 年被约谈"限规模"）；④ 2023 年转型孵化 DeepSeek（大模型），把量化算力与 AI 研究打通。**幻方的历程说明：中国量化的瓶颈不只是策略，更是规模、监管与算力的三角博弈。**

---

## 十、陷阱与黑暗面

### 10.1 过拟合与 PBO（Probability of Backtest Overfitting）

**问题**：你回测了 N 个策略变体，选最好的。**最好那个几乎必然是过拟合的**——它恰好 fit 了噪声。

**Bailey & De Prado 的 PBO**：给定一组回测，**PBO = 最优策略在样本外排名垫底的概率**。PBO > 0.5 意味着你的"最优"回测在样本外**比随机还差**——这是过拟合的数学标志。PBO 是对"我试了很多策略"的**科学体检**。

### 10.2 模型衰退与 Alpha 衰减（Model Decay / Alpha Decay）

**Alpha 衰减**：一个有效的信号，随着越来越多人交易它，**alpha 单调下降**。典型衰减曲线：策略上线后 1–3 年，alpha 衰减 50–80%。原因：① 你的交易本身在消灭 inefficiency；② 竞争对手逆向工程了你的信号；③ 市场结构变化。

**对策**：持续研究流水线（不断上新信号）、信号组合（多信号对冲衰减）、保密与速度护城河。

### 10.3 拥挤交易（Crowded Trades）

**问题**：当很多量化基金用**相似的模型**（如同样的动量/价值因子），它们会在风险事件时**同时平仓**，造成踩踏。2007 年 8 月的"量化危机（Quant Quake）"——多家统计套利基金一周内亏损 20%+，正是拥挤交易的典型。2024 年 8 月日元套利平仓也是拥挤交易的现代版。

### 10.4 黑天鹅暴露（Tail Exposure）

**问题**：很多量化策略（尤其卖期权、做市）长期小赚，但**尾部巨亏**。这扭曲了回测——10 年的漂亮曲线，可能藏着一次未发生的爆仓。LTCM（1998）是教科书案例：4 年高夏普，第 5 年俄罗斯违约，杠杆爆仓。Taleb 反复强调：**肥尾下，方差不是好的风险度量，因为极端事件决定生死**。链回 [`risk-and-uncertainty.md`](./risk-and-uncertainty.md) 的黑天鹅章节。

### 10.5 认识论警示

> 量化交易最大的认识论陷阱是**把统计显著性等同于因果性**。一个 t 值 3 的因子，可能是真信号，也可能是**数据挖掘的假象**。金融里没有"对照组实验"（你不能让世界重跑一遍不交易你的策略），所以**因果性几乎永远无法确证**。谦逊是量化研究员的第一美德。

---

## 十一、中国市场量化

### 11.1 中国量化可用的主要工具

| 工具 | 标的 | 特点 |
|------|------|------|
| **股指期货** | IF（沪深300）/ IC（中证500）/ IM（中证1000） | 对冲多头 alpha 的核心工具；长期受限（2015 股灾后限手/提费，2017 起逐步松绑） |
| **ETF 期权** | 50ETF / 300ETF 期权 | 尾部对冲、波动率交易；卖方保证金要求高 |
| **商品期货** | 黑色/有色/能化/农产品 | CTA 趋势跟踪主战场；夜盘、多合约 |
| **国债期货** | 2/5/10 年 | 利率与宏观对冲 |
| **融券与转融通** | 个股 | 做空个股 alpha 的来源；券池与成本受限 |

### 11.2 中国量化的三个结构性特征

**1. 指增（指数增强）为主流形态**——中国市场散户占比高，存在大量可被因子收割的"定价偏差"。最常见的量化产品是"中证 500 指增"——做多一篮子因子好的股票、做空 IC 期货对冲，赚取超额。2019–2021 年指增产品规模爆发。

**2. 程序化交易报告制度（2024 起）**——证监会要求程序化交易投资者**报告**账户、策略、服务器位置、应急预案等；对高频交易设**差异化收费**（撤单费等）。这是中国对量化的**精准监管**——不禁，但提高透明度、抑制过度高频。本质是承认量化的合法性的同时，约束其负外部性（加剧波动、挤占带宽）。

**3. 科创板做市与注册制**——科创板引入**做市商机制**（2022 起），为量化机构开辟做市业务。注册制下 IPO 定价更市场化，事件驱动策略空间扩大。

### 11.3 中国量化的特殊风险

- **政策风险**：监管环境变化快（限手、限规模、报告制度）。
- **对冲工具不足**：个股做空难、券贵；期指长期贴水（负基差）侵蚀 alpha。
- **散户化市场**：行为偏差更显著（alpha 来源多），但波动更剧烈、政策市特征强。
- **数据可得性**：另类数据生态不如海外成熟；Tick 数据质量参差。

---

## 十二、跨学科映射 + 开放问题 + 关联

### 12.1 跨学科映射

| 学科 | 在量化交易中的形态 |
|------|------------------|
| **概率论/随机过程** | 价格 = 几何布朗运动/跳跃过程；鞅定价；布朗桥执行建模 |
| **信息论** | alpha = 未被消化的信息；Sharpe 上限 ≈ 信号/噪声比的函数 |
| **控制论/反馈** | 做市商存货控制 = 经典反馈系统；凯利 = 最优控制 |
| **强化学习** | 执行、组合、做市都可建模为 MDP（链回 [`rl-learning`](../../)） |
| **复杂系统** | 市场是多智能体涌现；拥挤交易 = 相变；崩盘 = 临界级联 |
| **信号处理** | 因子 = 滤波器；分数差分 = IIR 滤波；HFT 延迟 = 采样定理 |
| **最优化** | 组合 = 凸优化；风险平价 = 不动点迭代；执行 = 随机最优控制 |
| **博弈论** | 做市 vs 择时者 = 零和博弈；stop hunting = 重复博弈均衡 |
| **认识论** | 过拟合 = 归纳问题；EMH = 可预测性的边界；alpha 存在性 = 本体论 |

### 12.2 五个开放问题

1. **Alpha 会枯竭吗？** 如果所有 inefficiency 都被量化消灭，市场趋于强有效，量化自身的收益归零。但行为偏差、结构性摩擦、新工具诞生持续**创造新的 inefficiency**——alpha 是一条会自我修复又自我消灭的河。
2. **AI 会"理解"市场吗？** 当 LLM/Transformer 主导交易，市场是更有效还是更脆弱？（链回 [`ai-finance.md`](./ai-finance.md) §智能体市场）。2024 的"AI 同质化踩踏"担忧。
3. **凯利是"对的"吗？** 凯利最大化对数财富，但现实中人不是对数效用者，且参数估计有误。分数凯利是工程妥协，**理论上最优的杠杆永远无法被精确计算**。
4. **尾部风险能被定价吗？** 黑天鹅按定义不可预测，但期权市场仍给它标价（VIX、价外 put）。这个价格是"真实概率"还是"恐惧溢价"？这是 [`risk-and-uncertainty.md`](./risk-and-uncertainty.md) 的核心。
5. **量化的社会价值？** 做市提供流动性（正价值），但 HFT 的"延迟军备竞赛"和拥挤踩踏是负价值。Tobin 之问（金融是否过度交易）在量化时代更尖锐（链回 [`_philosophy-of-finance.md`](./_philosophy-of-finance.md)）。

### 12.3 与 essence 项目的关联

- **上游数学**：[`02-formal-sciences/probability/`](../../02-formal-sciences/probability/)（鞅、伊藤引理）+ [`02-formal-sciences/optimization`](../../02-formal-sciences/)（凸优化、动态规划）
- **方法论**：本文贯彻三层讲解 + 代码验证（MANIFESTO 第七条），5 段代码全部跑通
- **哲学**：过拟合 = 归纳问题；EMH = 认识论；凯利 = 决策论（[`00-philosophy/epistemology.md`](../../00-philosophy/epistemology.md)）
- **姊妹章节**：[`ai-finance.md`](./ai-finance.md)（ML 信号深化）+ [`market-microstructure.md`](./market-microstructure.md)（HFT/价差深化）+ [`portfolio-theory.md`](./portfolio-theory.md)（组合优化深化）+ [`risk-and-uncertainty.md`](./risk-and-uncertainty.md)（尾部风险深化）+ [`financial-econometrics.md`](./financial-econometrics.md)（计量检验，待建）
- **外部项目**：策略代码与工程可延伸到 `/mnt/c/workspace/fastisslow/`（投资哲学与量化工程实践）

### 12.4 essence 立场总结

> 量化交易是**用数学对抗人性、用算法对抗情绪、用纪律对抗侥幸**的工程。它的力量真实——Renaissance、Two Sigma 证明了这点。但它的脆弱也真实——LTCM、2007 Quant Quake、拥挤踩踏同样证明了这点。
>
> **essence 的核心判断**：量化交易最深的教训不在金融，而在认识论——**任何在历史数据上拟合出的规律，都不自动延伸到未来**。这条教训，适用于量化，也适用于科学，更适用于生活。谦逊地使用模型，永远留足黑天鹅的余量，是量化——也是任何"对抗不确定性"的事业——的最高智慧。

---

## 附：代码验证清单

| 代码 | 章节 | 验证状态 | 核心结论 |
|------|------|---------|---------|
| 代码 1 | §2.3 策略动物园 | ✅ 本地跑通 | 协整套利夏普 2.96（合成数据）；动量在随机游走上≈0；做市靠价差但要控存货 |
| 代码 2 | §3.3 Walk-Forward | ✅ 本地跑通 | 全样本 54.6% vs 样本外 48%；200 噪声策略样本内最优夏普 2.78→样本外 -0.61 |
| 代码 3 | §4.4 De Prado 方法 | ✅ 本地跑通 | 分数差分 d=0.35 平稳且相关性 0.884（vs d=1 的 0.054）；元标签把握度 0.623；MDA f0 下降 18.9pp 远超噪声 2.8pp |
| 代码 4 | §5.4 组合构建 | ✅ 本地跑通 | 风险平价等化风险贡献、夏普 1.08；全凯利 5%分位 0.75x vs 1/4 凯利 0.94x |
| 代码 5 | §6.3 执行算法 | ✅ 本地跑通 | VWAP IS 164.8bp < POV 165.0 < TWAP 166.2（正确排序） |

> **环境**：Python 3.10.12 / numpy 2.2.6 / pandas 2.3.3 / scikit-learn 1.7.2 / scipy 1.15.1  
> **声明**：所有代码为**教学演示**，使用合成数据。**不可直接用于实盘**——真实交易需额外的成本建模、PIT 数据、风险前置、灾难恢复。能跑通 ≠ 能赚钱。

---

*建立日期：2026-07-16 · essence 项目 · 03-social-sciences/finance/quantitative-trading.md*
