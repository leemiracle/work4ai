# V26 失败案例档案 #3：2008 次贷危机（Li 高斯 Copula 滥用）

> **数学公式滥用 → 全球 $22 万亿损失 + 10+ 年衰退**

---

## 📅 事实时间线

| 时间 | 事件 |
|------|------|
| **2000.3** | **David X. Li 发表"On Default Correlation"**（Gaussian Copula 模型）|
| 2003-2007 | Copula 模型被广泛用于 CDO 定价 |
| 2006 | 美国房价见顶 |
| 2007.8 | BNP Paribas 冻结 3 只基金 |
| **2008.9.15** | **雷曼兄弟破产**（$6390 亿资产，史上最大破产）|
| 2008-2009 | 全球股市蒸发 $22 万亿 |
| 2009 | Li 接受《Wired》采访："我毁了华尔街" |

**直接损失**：
- 雷曼 $6390 亿资产
- 全球股市 $22 万亿
- 美国失业率 10%（2009）
- 主权债务危机（欧洲 5 国）

---

## 🎯 数学误用：Gaussian Copula

### Li 2000 公式

定义违约时间 $\tau_i$ 的相关性：

$$C(\tau_1, \tau_2) = \Phi_2(\Phi^{-1}(F(\tau_1)), \Phi^{-1}(F(\tau_2)); \rho)$$

其中：
- $C$ = Copula 函数（连接边际分布）
- $\Phi$ = 标准正态 CDF
- $\Phi_2$ = 双变量正态 CDF
- $\rho$ = 相关性参数

**Li 的"创新"**：用一个相关性参数 $\rho$ 描述所有贷款违约的相依结构。

### 3 个致命问题

#### 问题 1：相关性 ≠ 因果性
$\rho$ 是历史相关性。房价跌时，所有房贷**同时**违约——历史 $\rho$ 失效。

#### 问题 2：Gaussian 假设轻尾
Copula 用双变量正态——同样低估尾部。

#### 问题 3：参数估计样本少
历史数据只有 1990s 美国房价上升期。**外推到下跌期失效**。

---

## 🧠 认知偏差：群体疯狂 + 监管放松

### 偏差 1：模型崇拜
评级机构（S&P/Moody's）用 Li Copula 给 CDO 评 AAA。

### 偏差 2：流动性幻觉
"房价永远涨"的群体错觉。

### 偏差 3：监管放松
2004 SEC 放松投行杠杆限制 → 5 大投行杠杆 30:1。

### 偏差 4：道德风险
"贷款人 / 评级机构 / 投行 / 投资者"分离 → 没人对系统性风险负责。

---

## 🔍 正确做法（事后改进）

### 1. 用重尾 Copula
**Student-t Copula** 而非 Gaussian——捕捉尾部相依。

```python
# Copula 对比
import numpy as np
# Gaussian Copula：尾部独立
# Student-t Copula：尾部相依（更真实）
# 2008 危机后行业转向 t-Copula + Random Factor Loading
```

### 2. 多因子模型
**单因子 Li 模型** → **多因子 + 状态切换**（Hrdle 2009）。

### 3. 压力测试（Basel III）
强制做"房价跌 30%"情境测试。

### 4. 系统性风险监控
FSB（金融稳定委员会）2009 成立。

---

## 💻 Python 复盘

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Gaussian Copula vs Student-t Copula（尾部相依差异）
np.random.seed(0)
n = 10000

# Gaussian Copula
rho = 0.3
z = np.random.multivariate_normal([0,0], [[1,rho],[rho,1]], n)
u_gauss = stats.norm.cdf(z)

# Student-t Copula（df=4）
z_t = np.random.multivariate_normal([0,0], [[1,rho],[rho,1]], n)
t_scale = np.sqrt(np.random.chisquare(4, (n,1)) / 4)
z_t = z_t / t_scale  # 多元 t
u_t = stats.t.cdf(z_t, df=4)

# 比较尾部相依
print(f"P(U1 > 0.99, U2 > 0.99 | Gaussian) = {np.mean((u_gauss[:,0]>0.99) & (u_gauss[:,1]>0.99)):.4f}")
print(f"P(U1 > 0.99, U2 > 0.99 | Student-t) = {np.mean((u_t[:,0]>0.99) & (u_t[:,1]>0.99)):.4f}")
# Student-t 尾部相依显著更强 → 真实危机更准确

plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.scatter(u_gauss[:2000, 0], u_gauss[:2000, 1], s=2, alpha=0.5)
plt.title('Gaussian Copula（尾部独立）')
plt.subplot(1, 2, 2)
plt.scatter(u_t[:2000, 0], u_t[:2000, 1], s=2, alpha=0.5, color='red')
plt.title('Student-t Copula（尾部相依）')
plt.savefig('copula_comparison.png', dpi=100)
```

---

## 📚 启示：6 条核心教训

1. **Copula 函数 ≠ 万能模型**——边际不能从相依结构分离
2. **历史相关性 ≠ 未来相关性**——尤其危机时
3. **轻尾假设 = 灾难**——金融必须用重尾
4. **数学包装 ≠ 真理**——AAA 评级只是公式结果
5. **分离的金融链** → 道德风险 → 系统崩盘
6. **监管必须前置**——不能等危机才介入

---

## 📐 接入 13 目录

- `07-critique/`：新建 `失败案例03-2008 次贷 Li Copula.md`
- `12-社会系统/03-金融系统的整体稳定.md` ⭐⭐⭐
- `../math/华章数学丛书/60-金融衍生工具数学导论原书第3版.pdf`：CDO 定价
- `../math/美国研究生数学/GTM113.Brownian.Motion.and.Stochastic.Calculus.pdf`：相依随机过程

---

## 🎯 该案例的"独家切面"

**只有 V26 能照出**：**一个公式（Li Copula）如何引发全球经济危机**。这是 21 世纪最深的"数学误用警示"——天才的简化（单参数 Copula）变成毁灭的种子。

Li 自己反思（2009）："最简单的模型让人误以为理解了。其实没人理解。"

---

> 📖 配套：[V26 失败案例](../视角深度/V26-失败案例.md) · [金融数学主题报告](../书籍索引/主题深度报告-金融数学.md)
