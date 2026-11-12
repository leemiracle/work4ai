# 讲透DualPipe — 重要文件精讲索引

DualPipe 是 DeepSeek-V3 技术报告提出的双向流水线并行算法参考实现（含 Sea AI Lab 的 DualPipeV cut-in-half 变体）。本目录收录 2 篇核心源码精讲——仓库本身极小（4 个源文件），两篇已覆盖全部主干。

## 精讲列表

| 篇目 | 原文件 | 一句话定位 |
|---|---|---|
| [01-dualpipe.md](01-dualpipe.md) | `dualpipe/dualpipe.py` | 双向流水线引擎：八阶段调度、phase 异或对称、ZB 零气泡集成 |
| [02-utils.md](02-utils.md) | `dualpipe/utils.py` | WeightGradStore 权重梯度延迟 + run_backward + scatter/gather |

## 建议阅读顺序

1. **02-utils.py**：先掌握三个工具件（尤其 WeightGradStore 的 put/flush/pop 攒批模型），否则读引擎时会卡在 W chunk 的来历。
2. **01-dualpipe.py**：再攻八阶段调度，记住两条不变量：chunk 按 phase 有序消费、通信先提交后等待。

辅助材料：`dualpipe/comm.py`（P2P 封装，38 行，在两篇的"外部连接"节均有覆盖）；`examples/` 两份端到端正确性验证示例。

## 关键数字（README 对比表）

- 气泡：DualPipe `(PP/2-1)(F&B+B-3W)` vs 1F1B `(PP-1)(F+B)`、ZB1P `(PP-1)(F+B-2W)`
- 代价：参数 2×、激活 `PP+1`；DualPipeV 设备数减半（`PP/2`）指标不变

## 配套资料

- [onboarding/ONBOARDING.md](../onboarding/ONBOARDING.md) — 项目全貌入门
- 上游仓库：~/ai/explore/deepseek-ai/DualPipe
