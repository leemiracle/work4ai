# 第三章阅读与取舍记录

此记录列出本次写作采用的范围；不把阅读案例笔记等同于审计其链接的全部论文或代码。

- **任务费用与请求分布**：读取 token-cost-2023-2026/report.md 的成本定义、长任务和生命周期段落（§2、4、11），workload-and-provisioning.md 全文，以及 ServeGen 源码阅读笔记。正文先用相同均值的两分钟负载解释阶段需求，再呈现实验 3-2 的固定顺序、单次回放结果。未把教学积压当成 RTX 性能预测。
- **Reasoning 与 Agent**：读取实验 3-3 的主实验、wide-budget、no-thinking 报告，实验 3-4 的两条轨迹及额外别名检查，agent-thinking-on 计算与首轮加速变体。保留严格评分和后验诊断的区别，用逐轮表解释缓存命中、模型时间和任务完成为何不是同一个指标。作者上下文与检索案例提供任务组织背景。
- **多模态与实时任务**：读取 generative-multimodal-models.md、multimodal-stage-placement.md 相关模型与阶段段落、author-context-and-design.md，核对视觉、Omni、Fish、图像／视频和音频时序计算；读取实验 3-5 历史接收分析。正文分别介绍视觉位置、音频块和迭代去噪，避免统一成含义不明的 token 数。
- **训练**：读取 training-compute.md，Qwen3 本地报告文本的三阶段预训练段落，以及 8K 训练矩阵、loss mask、紧凑词表头、非矩阵补算记录。线性层表先解释两个梯度，再给整模型总量；V4 子账只按各自范围引用，未声称已经闭合优化器、工作区和完整步时。
- **RL 与 OPD**：读取 2026-infra-survey 概览、RL 覆盖记录和 verl 配方闭合笔记，实验 10-8 报告与符号奖励对照，以及 DeepSeek-V4 本地报告中 specialist RL 和最终 OPD 段落。采用 Qwen 教学批次解释有效样本预算，不把这些数值写成 V4 的实际运行成本。
- **Scaling Law 与历史投入**：读取 scaling-history.md、datablations 的八点拟合与生命周期 JSON、实验 3-8 六次小模型训练记录、training-history-published 结果；核对本地 Chinchilla、Scaling Laws 与 Beyond Chinchilla 文本相关范围。正文保留事前留出、样本边界与外推标记，历史表按硬件及训练阶段拆分，未知 GPU 小时不填零。

固定来源路径及 SHA-256 见 sources.json。正文脚注连接可继续核对的原件；图数据与生成器保留数值来源。完整实验变体仍在原目录，本次写作没有修改原始实验或计算结果。
