# 统计学 · EconML / 因果 ML 工程

> **博士级**：因果 ML 的工业实践。

## 一、EconML 工具库（Microsoft）

### 1.1 主要方法

```
DML（Double ML）         —— Chernozhukov 线性
DR Learner（Doubly Robust）—— 结合
Causal Forest（Wager-Athey）—— 异质
Meta-learners（T/S/X）   —— 多种
Orthogonal Random Forest —— 改进
```

### 1.2 工作流

```python
from econml.dml import LinearDML

est = LinearDML(model_y=RandomForestRegressor(),
                model_t=RandomForestClassifier())
est.fit(Y, T, X=X, W=W)
# 估 CATE(X)
cate = est.effect(X_test, T0=0, T1=1)
# 置信区间
lb, ub = est.effect_interval(X_test)
```

## 二、典型应用

### 2.1 政策评估

- **培训项目效果**：参与 vs 不参与
- **税收政策**：减税 5% 对消费
- **教育干预**：班级大小

### 2.2 医疗个性化

- **个性化治疗效应**（ITE）
- 同药不同人效果不同
- **CATE** 决定用药

### 2.3 营销 uplift

- **uplift modeling**：广告 / 折扣对谁有效
- 4 类客户：稳定 / 可说服 / 必失 / 沉睡
- **针对性营销**

### 2.4 产品 A/B 测试

- 短期 A/B → 长期效果推断
- **代用指标**

## 三、关键挑战

### 3.1 数据质量

- 未测量混杂（unmeasured confounding）
- **IV（工具变量）** / **sensitivity analysis**

### 3.2 模型选择

- 哪个 CATE 方法最好？
- **cross-fitting + benchmark**

### 3.3 可解释

- CATE 怎么解释给业务方？
- **SHAP + 因果**

### 3.4 部署

- 在线推理延迟
- **模型监控**

## 四、关键公司

### 4.1 科技公司

- **Uber**：CausalML 库
- **Microsoft**：EconML + Azure
- **Netflix**：uplift
- **Booking / Airbnb**：A/B + 因果

### 4.2 药企

- **Pfizer / Roche**：个性化治疗
- 临床试验 + ML

### 4.3 咨询 + 政府

- **McKinsey / BCG**：政策模拟
- **World Bank / UN**：发展项目评估

## 五、前沿

### 5.1 Causal Representation Learning

- Schölkopf 团队
- 学表示同时学因果
- IRM / Causal RL

### 5.2 Foundation Models for Causal

- LLM 理解因果问题
- LLM + 计算器（EconML）

### 5.3 时间序列因果

- **Synthetic Control**
- **Difference-in-Differences**
- **Interrupted Time Series**

## 六、博士级练习

1. 在 IHDP / ACIC 数据 benchmark
2. 实现 uplift modeling
3. 分析某政策数据的 CATE

## 关键引用

- EconML 文档（Microsoft）
- CausalML 文档（Uber）
- Künzel 2019 *PNAS*
- Athey 2019 *Annual Review*
