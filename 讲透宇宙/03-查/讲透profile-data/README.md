# 讲透 Profile Data

> DeepSeek 性能剖析数据仓的中文知识库：V3/R1 训练与推理的 trace 数据集，覆盖 DualPipe、MoE 层、Prefill/Decode 各阶段的并行配置与微批策略，并用 Chrome/Edge tracing 工具教你读懂火焰图、提炼优化洞察。

## 内容（deepwiki/ 17 页）

- **框架概览**：剖析数据的构成与 DeepSeek 训推框架背景
- **训练过程**：DualPipe 架构、MoE 层的 trace 特征
- **推理过程**：Prefilling 与 Decoding 阶段、micro-batch 策略
- **并行配置**：专家并行（EP）、张量与流水线并行的实测剖析
- **可视化与分析**：tracing 工具用法、数据解读、性能优化洞察

## 用法

先读 `deepwiki/1.2` 框架页建立术语，再按"训练 → 推理 → 并行"顺序对照 trace 理解调度行为；分析方法配 `5.1` 用 Perfetto/Chrome tracing 打开原始数据实操；组件原理配 DualPipe/DeepEP 精读仓交叉验证。

## 姊妹篇

《讲透DualPipe》《讲透DeepEP》《讲透FlashMLA》《讲透DeepGEMM》《讲透3FS》（被剖析组件本体）《讲透DeepSeek-V3》《讲透DeepSeek-V3.2-Exp》《讲透open-infra-index》（全家桶导航）
