# 机器人 · Sim2Real 工程实践

> **博士级**：仿真到真实的工程挑战。

## 一、Sim2Real Gap

### 1.1 Reality Gap

仿真 ≠ 真实：
- **物理**：摩擦 / 接触 / 变形
- **传感器**：噪声 / 延迟
- **环境**：光照 / 纹理

### 1.2 视觉 vs 控制 gap

- **视觉 gap**：仿真图像 vs 真实
- **控制 gap**：仿真动力学 vs 真实

## 二、主要方法

### 2.1 Domain Randomization（DR）

**Tobin 2017**：仿真参数随机化。

```
训练时：
  摩擦 ~ U(0.1, 1.0)
  重力 ~ U(0.9g, 1.1g)
  光照 ~ random
  纹理 ~ random
  物体颜色 ~ random
```

**直觉**：真实只是分布的一个样本。

**效果**：**OpenAI Dactyl** 解魔方。

### 2.2 Domain Adaptation

学 invariant 表示：
- **GAN**：仿真 ↔ 真实 翻译
- **对比学习**：跨域表示

### 2.3 System Identification

从少量真实数据**校准仿真**：
- 估计真实物理参数
- 再用校准后的仿真训练

### 2.4 可微仿真

仿真器可微 → 端到端训练：
- **Brax** / **MuJoCo MJX** / **Genesis**
- **diffTaichi**

## 三、仿真器

### 3.1 主要仿真器

| 仿真器 | 强项 |
|---|---|
| **Isaac Sim / Isaac Gym**（NVIDIA）| GPU 加速 + 大规模 |
| **MuJoCo** | 接触精确 |
| **PyBullet** | 开源 |
| **Habitat 3.0** | 室内 + 人形 |
| **Genesis** | 可微 + 通用 |

### 3.2 选择标准

- **物理精度** vs **速度**
- **资产丰富度**
- **社区**

## 四、关键案例

### 4.1 OpenAI Dactyl（2019）

- 仿真训练（DR）→ 真实魔方
- 大规模随机化
- **意义**：Sim2Real 可行（部分）

### 4.2 ANYmal（2019）

- 仿真 + 域适应
- 真实部署
- **Science Robotics**

### 4.3 Figure / Tesla

- 大量仿真数据 + 真实数据混合
- 端到端学习
- 2024 商用候选

## 五、当前瓶颈

### 5.1 接触建模

- 多点接触 / 变形
- 仿真不精确
- **柔性机器人** 尤其难

### 5.2 长期任务

- 仿真无法模拟小时级
- **层次化学习**

### 5.3 多模态

- 触觉 / 力反馈
- 仿真缺触觉

## 六、未来方向

### 6.1 大规模数据

- **Isaac Gym**：10 万并行环境
- 大幅加速 RL

### 6.2 真实数据精调

- 仿真预训练 + 真实微调
- **少量真实数据**

### 6.3 学习仿真

- AI 学仿真器（world model）
- 与物理仿真混合

## 七、博士级练习

1. 在 Isaac Gym 训练简单 RL
2. 实现 Domain Randomization
3. 测试 Sim2Real gap

## 关键引用

- Tobin 2017 IROS DR
- OpenAI 2019 Dactyl
- Tan 2017 IJRR Sim-to-real
- Makoviychuk 2021 Isaac Gym
