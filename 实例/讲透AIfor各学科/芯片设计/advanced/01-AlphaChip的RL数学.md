# 芯片设计 · AlphaChip 的 RL 数学

> **博士级**：AlphaChip 的强化学习数学。

## 一、芯片布局的数学形式

### 1.1 问题

- **网表**（netlist）：节点（宏模块 / 标准单元）+ 边（连接）
- **画布**：网格画布
- **目标**：放置节点 → 最小化 area + wirelength + congestion + power

### 1.2 作为序列决策

放置是一个一个节点——**MDP**：

- **状态**：当前画布 + 剩余节点
- **动作**：下一个节点放哪
- **奖励**：最终 PPA（Power Performance Area）
- **回合**：所有节点放完

## 二、AlphaChip 的方法

### 2.1 策略网络

**Transformer encoder** 处理网表（图结构）→ 节点嵌入。

**策略头**：输出动作概率分布。

### 2.2 训练

- **模仿学习**（专家布局）
- **强化学习**（PPO，fine-tune）

### 2.3 奖励设计

- **macro placement**：6 个月专家结果作为 baseline
- 奖励 = 改进百分比

## 三、关键创新

### 3.1 网表编码

- 节点 + 边的图
- Transformer 学节点表示

### 3.2 课程学习

- 先在 TPU v4 学，迁移到 v5 / v6

### 3.3 Symmetry-aware

- 芯片有镜像对称
- 网络显式利用

## 四、争议

### 4.1 Mirhoseini 真的赢了吗？

- **2021 Nature**：声称超专家
- **2023 Cheng**：重新评估，DREAMPlace 更好
- **2024 AlphaChip 综述**：Google 反驳

### 4.2 复现困难

- Google 内部数据 / 算力
- 开源不全

## 五、性能（最新）

| 方法 | TPU 布局时间 | PPA 改进 |
|---|---|---|
| 人工 | 6 个月 | baseline |
| DREAMPlace | 小时级 | -5% |
| AlphaChip | 小时级 | +3% |

## 六、博士级练习

1. 在 OpenROAD 训练简单 RL 布局
2. 分析 Mirhoseini 的争议
3. 设计新的 reward function

## 关键引用

- Mirhoseini 2021 *Nature*
- Cheng 2023 重新评估
- Mirhoseini 2024 *Nature* AlphaChip 综述
