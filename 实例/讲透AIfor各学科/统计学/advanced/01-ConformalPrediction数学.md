# 统计学 · Conformal Prediction 数学

> **博士级**：Conformal Prediction 的严格推导——分布无关的不确定性量化。

## 一、问题

**目标**：给定训练数据 + 显著性水平 $\alpha$，构造预测区间 $C(x_{new})$ 使得：

$$P(y_{new} \in C(x_{new})) \geq 1 - \alpha$$

**关键**：**分布无关**——不假设数据分布。

## 二、Conformal Prediction 的数学

### 2.1 Exchangeability（可交换性）

比 i.i.d. 弱——只要数据顺序可任意置换。

### 2.2 Conformity Score

定义" conformity "函数 $A(D, (x, y))$ —— 衡量 $(x, y)$ 与训练数据 $D$ 的相似度。

例：$A = -|y - \hat{f}(x)|$（预测误差负值）。

### 2.3 关键定理

给定 exchangeable 数据 $(x_1, y_1), ..., (x_n, y_n), (x_{new}, y_{new})$：

$$P(\text{rank of } (x_{new}, y_{new}) \leq \lceil (n+1)\alpha \rceil) \leq \alpha$$

即：

$$P(y_{new} \in C_\alpha(x_{new})) \geq 1 - \alpha$$

**证明核心**：exchangeability → 每个 rank 等可能。

## 三、Split Conformal（实用版）

### 3.1 算法

1. 分数据：训练 $D_1$ + 校准 $D_2$
2. 在 $D_1$ 训练 $\hat{f}$
3. 在 $D_2$ 算 conformity scores $s_i = |y_i - \hat{f}(x_i)|$
4. 取 $\hat{q}$ 为 $s$ 的 $\lceil (n+1)(1-\alpha) \rceil$ 分位数
5. 预测区间：$C(x_{new}) = [\hat{f}(x_{new}) - \hat{q}, \hat{f}(x_{new}) + \hat{q}]$

### 3.2 性质

- **有限样本保证**（不依赖大样本）
- **计算高效**
- **任意 base predictor**（NN / 森林 / ...）

## 四、适应性（Adaptive）

经典 CP 给定宽度区间。**Adaptive CP** 根据局部难度调宽度：

- **CQR**（Conformalized Quantile Regression）：分位数回归 + CP
- **Locally-weighted CP**：局部 normalization

## 五、应用

### 5.1 LLM 输出（2024 突破）

- LLM 生成多个候选
- CP 选**保证覆盖**的子集
- **取代 hallucination** 的工具

### 5.2 医疗 / 安全

- 必须知道"不知道"
- CP 给**可信区间**

### 5.3 时间序列

- 时间序列不 exchangeable
- **Weighted CP**（更老数据权重低）

## 六、博士级练习

1. 实现 Split CP（10 行 Python）
2. 在 LLM 候选集应用
3. 对比 CP vs MC Dropout

## 关键引用

- Vovk 2005 *Algorithmic Learning*
- Angelopoulos 2021 *Tutorial*
- Bates 2021 *Distribution-free risk assessment*
