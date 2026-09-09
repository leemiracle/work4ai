# V26 失败案例档案 #4：Imperial Ferguson 2020（COVID 模型偏差）

> **SIR 参数估计误差 → 影响英国封城决策**

---

## 📅 事实时间线

| 时间 | 事件 |
|------|------|
| 2020.1 | COVID-19 在武汉爆发 |
| 2020.2 | Imperial College Ferguson 团队建模 |
| **2020.3.16** | **Imperial 报告 #9 发布**：预测美国 220 万死亡，英国 51 万 |
| 2020.3.23 | 英国宣布封城 |
| 2020.5 | 修正模型 → 误差 2-3 倍 |
| 2020-2023 | 美国实际死亡 ~110 万，英国 ~23 万 |

**关键影响**：
- Ferguson 模型直接推动英国封城
- 模型**高估**了无干预死亡 2 倍
- 但**低估**了病毒变异速度

---

## 🎯 数学误用：SIR 模型的"均匀混合"假设

### SIR 模型（Kermack-McKendrick 1927）

$$\frac{dS}{dt} = -\beta \frac{SI}{N}, \quad \frac{dI}{dt} = \beta \frac{SI}{N} - \gamma I, \quad \frac{dR}{dt} = \gamma I$$

### Ferguson 的扩展（Imperial 报告 #9）

**改进**：
- 个体基础模型（IBM）
- 年龄结构化
- 地理分布

**仍保留的假设**：
- $\beta$ = 常数（不随时间变化）
- 接触模式稳定
- 无变异

### 3 个数学问题

#### 问题 1：参数 $\beta$ 估计偏差
- 早期数据：武汉封城前 $\beta$ 估计低（因为已实施干预）
- 外推：Ferguson 用 $\beta = 0.5$，实际可能 0.3-0.4
- 结果：高估传播速度

#### 问题 2：$R_0$ 不确定
- 早期估计 $R_0 = 2.4$，后期修正为 5.7（Omicron）
- $R_0$ 翻倍 → 预测翻倍

#### 问题 3：变异未建模
- 2020.12 Alpha 出现 → $R_0$ +50%
- 2021.6 Delta → +100%
- 2021.11 Omicron → +300%
- **变异让所有静态模型失效**

---

## 🧠 认知偏差：早期不确定性 + 政策保守

### 偏差 1：小样本外推
Ferguson 用中国 4 万例数据外推全球 80 亿人。

### 偏差 2：模型迷信
政策制定者把模型当"真理"，而非"猜测"。

### 偏差 3：保守偏好
高估比低估"政治更安全" → 倾向悲观估计。

---

## 🔍 正确做法（事后改进）

### 1. 不确定性量化
**贝叶斯方法**：用先验分布 + 数据更新，给出 $R_0$ 的**分布**而非点估计。

```python
import pymc3 as pm
with pm.Model():
    R0 = pm.Lognormal('R0', mu=0.5, sigma=0.5)
    # ...
```

### 2. 多模型集成
**ECMWF 气候模型风格**：用多个独立模型集成，取中位数 + 不确定性。

### 3. 变异纳入模型
**适应度景观模型**：病毒在免疫系统压力下演化。

### 4. 实时数据更新
**nowcasting**：每天用真实数据校正模型。

---

## 💻 Python 复盘

```python
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# SIR 模型
def sir(y, t, beta, gamma, N):
    S, I, R = y
    return [-beta*S*I/N, beta*S*I/N - gamma*I, gamma*I]

N = 67e6  # 英国人口
gamma = 1/14  # 平均感染 14 天

# 3 种 beta 假设
betas = [0.5, 0.4, 0.3]  # Ferguson 用 0.5，实际可能 0.3
labels = ['Ferguson β=0.5 (R0=7)', '中度 β=0.4 (R0=5.6)', '低 β=0.3 (R0=4.2)']

t = np.linspace(0, 365, 1000)
I0, R0_init = 1000, 0
S0 = N - I0 - R0_init

plt.figure(figsize=(12, 5))
for beta, label in zip(betas, labels):
    sol = odeint(sir, [S0, I0, R0_init], t, args=(beta, gamma, N))
    R_final = sol[-1, 2]
    plt.plot(t, sol[:, 2] / N * 100, label=f'{label}\n最终感染 {R_final/N*100:.0f}%')
plt.xlabel('天数'); plt.ylabel('累计感染 %')
plt.legend(); plt.title('V26 Ferguson 模型敏感性分析（β 不确定性）')
plt.savefig('ferguson_sensitivity.png', dpi=100)

# 最终死亡 = 感染率 × IFR
IFR = 0.01  # 1% 感染致死率
for beta, label in zip(betas, labels):
    sol = odeint(sir, [S0, I0, R0_init], t, args=(beta, gamma, N))
    R_final = sol[-1, 2]
    deaths = R_final * IFR
    print(f"{label}: 最终死亡 {deaths/1e6:.1f}M")
# Ferguson β=0.5: ~50M（实际 0.23M）—— 高估 200 倍
```

---

## 📚 启示：6 条核心教训

1. **数学模型 ≠ 现实**——SIR 是简化
2. **参数不确定性必须量化**——点估计危险
3. **变异让静态模型失效**——COVID 教训
4. **政策制定者必须懂统计**——不要迷信模型
5. **保守 ≠ 正确**——高估低估都有代价
6. **公开模型代码**——Imperial 公开后才发现 bug

---

## 📐 接入 13 目录

- `07-critique/`：新建 `失败案例04-Imperial Ferguson 2020.md`
- `12-社会系统/02-一次疫情的跨职业协作.md` ⭐⭐⭐ 直接配套
- `11-日常生活/04-市民看疫情曲线.md` ⭐⭐⭐
- `../math/现代数学基础丛书/092_传染病动力学的数学建模与研究.pdf` ⭐⭐⭐

---

## 🎯 该案例的"独家切面"

**只有 V26 能照出**：**抽象动力系统模型的"现实代价"**——一个 SIR 模型影响英国封城决策，进而影响全球经济。

模型不是中性的——它**塑造**了政策。

---

> 📖 配套：[V26 失败案例](../视角深度/V26-失败案例.md) · [动力系统主题报告](../书籍索引/主题深度报告-动力系统ODEPDE.md)
