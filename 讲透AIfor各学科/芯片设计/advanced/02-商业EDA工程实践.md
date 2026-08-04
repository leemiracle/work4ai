# 芯片设计 · Synopsys / Cadence 工程实践

> **博士级**：商业 EDA + AI 的产业落地。

## 一、商业 EDA AI 产品

### 1.1 Synopsys DSO.ai（2020+）

- **Design Space Optimization AI**
- **Bayesian Optimization + RL**
- 应用：Apple / Intel / TSMC 客户
- **效果**：开发时间 -30%

### 1.2 Cadence Cerebrus（2022）

- 类似 DSO.ai
- **强化学习 + GNN**
- 应用：英伟达 / AMD

### 1.3 NVIDIA ChipNeMo（2023）

- 内部 LLM（基于 LLaMA）
- RTL 生成 / 问答 / 总结
- **用于 H100 / B100 设计**

## 二、产业实践

### 2.1 设计流程的 AI 化

```
Spec → RTL（LLM 辅助）→ 综合（AI 优化）→ 布局（AlphaChip）
   → 布线 → 时序（AI 预测）→ 验证 → GDSII
```

每步都有 AI。

### 2.2 7nm / 3nm 工艺挑战

- 物理效应复杂（量子隧穿 / 串扰）
- AI 学物理近似
- 3D 堆叠 + chiplet

### 2.3 多芯片 / chiplet

- **AMD / Intel / Apple** chiplet 设计
- AI 帮助 3D 空间布局
- **封装协同优化**

## 三、开源 EDA + AI

### 3.1 OpenROAD（DARPA IDEA）

- 全流程开源 EDA
- AI 嵌入各阶段
- **降低中小公司门槛**

### 3.2 OpenROAD-AI

- 训练 + 部署 AI 工具
- **学术研究友好**

### 3.3 公开 benchmark

- **IWLS / ISPD / DAC contests**
- 标准数据 + 评估

## 四、关键挑战

### 4.1 数据机密

- 芯片设计是核心 IP
- 不能公开
- **合成数据** + 联邦学习

### 4.2 复现困难

- Google AlphaChip 争议（2023 Cheng 重新评估）
- 商业产品不公开
- **学术 vs 工业鸿沟**

### 4.3 AI 可信度

- 芯片生产成本 $M+
- **失败代价高**
- **可验证 AI** 需求

## 五、新兴方向

### 5.1 LLM + EDA

- **ChipNeMo** / **RTLCoder**
- 自然语言 ↔ RTL
- **降低设计门槛**

### 5.2 AI 设计的芯片

- Google TPU v5/v6（部分 AI 设计）
- 联发科（2024 商用芯片）
- **AI 自我改进**（设计 AI 加速器的 AI）

### 5.3 光子 / 量子芯片 AI

- 光子 IC 设计
- 量子芯片布局
- **新硬件范式**

## 六、博士级练习

1. 在 OpenROAD 跑完整流程
2. 训练简单 RTL 生成 LLM
3. 分析 ChipNeMo 案例

## 关键引用

- Synopsys / Cadence / NVIDIA 2023-2024 报告
- OpenROAD 文档
- ChipNeMo 2023 论文
