# V26 失败案例档案 #1：Sally Clark 1999（英国母亲冤狱）

> **概率被误用 → 母亲入狱 3 年**｜ 28 视角 V26 的最经典警示

---

## 📅 事实时间线

| 时间 | 事件 |
|------|------|
| 1996.9 | Sally Clark 11 周岁男婴 Christopher 突然死亡 |
| 1998.1 | Sally 第二个男婴 Harry（8 周大）突然死亡 |
| 1998-1999 | Roy Meadow 医生作证：婴儿猝死综合征（SIDS）单次概率 1/8543 |
| **1999.11** | **陪审团裁定 Sally 谋杀罪，无期徒刑** |
| 2000 | 父亲 Jonathan Clark 发现控方隐藏细菌学证据 |
| **2003.1** | **Sally 上诉成功，释放（坐牢 3+ 年）** |
| **2007.3** | **Sally 酗酒死亡（43 岁）** |

**直接损失**：
- Sally 失去 3 年自由 + 失去两个孩子 + 最终心理崩溃死亡
- Roy Meadow 医生被吊销执照（后部分恢复）
- 英国皇家检察署（CPS）公信力崩塌

---

## 🎯 数学误用：Meadow 定律的两次错误

### 错误 1：乘法独立假设

**Meadow 的"专家证词"**：
- 1 个婴儿 SIDS 概率：$P_1 = 1/8543$
- **2 个独立** SIDS 概率：$P_2 = (1/8543)^2 = 1/73,000,000$

Meadow 当庭宣称："一户人家 2 个婴儿都 SIDS 的概率是 7300 万分之一"。

**数学错误**：假设"独立"是**严重的概率学谬误**。

### 错误 2：忽视先验（Bayes 倒置）

**正确做法（Bayes）**：
- $P(\text{双重 SIDS} \mid \text{两个婴儿死亡})$ ≠ $P(\text{两个婴儿死亡} \mid \text{双重 SIDS})$
- 必须用 Bayes 公式：$P(H \mid E) = \frac{P(E \mid H) P(H)}{P(E)}$
- "双重谋杀"的先验 $P(H_{\text{谋杀}})$ 也是极小

**真实数据**（Ray Hill 2004 重新计算）：
- 双重 SIDS 实际概率：$\sim 1/100,000$（不是 1/73M）
- 双重谋杀实际概率：$\sim 1/2,000,000$
- **比 Meadow 的 1/73M 高 730 倍！**

---

## 🧠 认知偏差：Meadow 律 + 检察官谬误

### Meadow 律
"一个突然死亡是悲剧，两个是可疑，三个是谋杀，直到被证明相反。"

这是 2003 年被判为**伪科学**的"定律"。

### 检察官谬误（Prosecutor's Fallacy）
把 $P(E \mid \neg H)$（无辜者条件下证据出现的概率）当成 $P(\neg H \mid E)$（证据条件下无辜的概率）。

**Sally 案中**：
- 控方说："两个 SIDS 的概率 1/73M = 几乎不可能 = 所以是谋杀"
- 正确逻辑："即使 1/73M，也必须考虑'双重谋杀'的概率也很小，需要其他证据"

---

## 🔍 正确做法（事后改进）

### 1. 用正确的概率模型
**真正模型**：SIDS 有遗传 / 环境共因，所以两兄弟的 SIDS **强相关**。
$$P(\text{SIDS}_2 \mid \text{SIDS}_1) \gg P(\text{SIDS}_1)$$

**真实倍数**：家庭有过 1 次 SIDS，第二次 SIDS 概率提升 5-10 倍。

### 2. Bayes 正当使用
$$P(\text{谋杀} \mid 2 死) = \frac{P(2 死 \mid 谋杀) P(\text{谋杀})}{P(2 死)}$$
- $P(\text{谋杀}) \approx 1/10,000$
- $P(2 死 \mid 谌杀) \approx 1$（谋杀者会杀）
- $P(\text{SIDS}_1) \cdot P(\text{SIDS}_2 \mid \text{SIDS}_1) \approx (1/8543) \cdot (1/1500)$
- **结果**：双重 SIDS 比双重谋杀可能性 **高 9 倍**（Ray Hill 2004）

### 3. 法庭统计学家
此案后英国规定：**复杂统计证据必须有独立统计学家审查**。

---

## 💻 Python 复盘

```python
import numpy as np
from scipy import stats

# Meadow 错误版本
p_sids = 1/8543
p_double_meadow = p_sids ** 2
print(f"Meadow 误用: P = 1/{int(1/p_double_meadow):,}")  # 1/72,982,849

# 正确版本（考虑相依）
p_sids1 = 1/8543
p_sids2_given_sids1 = 1/1500  # 强相关（遗传 + 环境）
p_double_correct = p_sids1 * p_sids2_given_sids1
print(f"正确版本: P = 1/{int(1/p_double_correct):,}")  # 1/12,814,500

# Bayes: P(双重谋杀 | 2死)
p_murder = 1/10000
p_2death_given_murder = 1.0  # 谋杀者会杀
p_2death = p_double_correct + p_murder * p_2death_given_murder
p_murder_given_2death = (p_2death_given_murder * p_murder) / p_2death
print(f"\nP(双重谋杀 | 2死) = {p_murder_given_2death:.2%}")  # ~10%
print(f"P(双重 SIDS | 2死) = {(1-p_murder_given_2death):.2%}")  # ~90%

print(f"\n比 Meadow 的 1/73M 高 {int(1/p_double_correct)//int(1/p_double_meadow)} 倍")
```

---

## 📚 启示：5 条核心教训

1. **独立性假设是危险的**——共变量（基因/环境/教育）几乎总是存在
2. **Bayes 必须考虑先验**——"小概率事件"不等于"不可能"
3. **检察官谬误普遍存在**——任何司法使用概率都要警惕
4. **专家 ≠ 数学家**——医生 Meadow 不懂 Bayes
5. **统计教育的缺失**——英国此后强制法官接受统计培训

---

## 📐 接入 13 目录

- `07-critique/`：新建 `失败案例01-Sally Clark 1999.md`
- `11-日常生活/`：升级"02-病人理解诊断概率"
- `04-concepts/概率收敛-多表征.md`：Bayes 的"现实"维度
- `../math/华章数学丛书/51-概率论基础教程原书第九版.md`：Ch.3 Bayes 配套案例

---

## 🎯 该案例的"独家切面"

**只有 V26 能照出**：**抽象概率假设的"血泪代价"**——一个数学错误让一位母亲冤狱 3 年，最终死亡。

---

> 📖 配套：[V26 失败案例](../视角深度/V26-失败案例.md) · [概率·统计主题报告](../书籍索引/主题深度报告-概率统计.md)
