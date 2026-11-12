# 讲透 Open Infra Index

> DeepSeek 开源基础设施索引仓的中文知识库：AI Infra 全家桶总导航，把推理训练栈拆成"算子—通信并行—存储数据"三线，串联 FlashMLA、DeepGEMM、DeepEP、DualPipe、EPLB/LPLB、3FS、smallpond，并附 V3/R1 推理系统架构与开源策略解读。

## 内容（deepwiki/ 19 页）

- **组件总览**：三大类基础设施分层地图
- **计算优化**：FlashMLA（注意力算子）、DeepGEMM（FP8 矩阵乘）
- **通信与并行**：DeepEP（MoE all-to-all）、DualPipe（双向流水线）、EPLB（专家负载均衡）
- **存储与数据处理**：3FS 文件系统、smallpond 计算框架
- **V3/R1 推理系统**：架构、性能优化、开源策略
- **技术深潜**：通信计算重叠、成本经济性分析

## 用法

把本仓当地图用：`deepwiki/2-components.md` 定位每个组件的位置，再沿链接下钻各组件的姊妹精读仓（每仓均有独立 DeepWiki/图谱/精读）；做系统设计时配 `3.1` 推理架构与 `4.2` 经济性分析页评估取舍。

## 姊妹篇

全家桶互链：《讲透FlashMLA》《讲透DeepGEMM》《讲透DeepEP》《讲透DualPipe》《讲透3FS》《讲透smallpond》《讲透TileKernels》（组件精读）＋《讲透DeepSeek-V3》《讲透DeepSeek-V3.2-Exp》（模型侧）
