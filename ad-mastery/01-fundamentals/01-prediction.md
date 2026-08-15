# ① 补充层 · 预测层（Prediction）全算法

> 感知告诉你"现在有什么"，预测回答"未来 3–8 秒它们去哪"。这是 AD 最难学术化的模块：不确定、强交互、长尾。

---

## 1. 三大难点

1. **多模态性**：路口的车可能直行/左转/右转——未来不唯一。
2. **交互性**：你的行为影响别人（你变道，旁车减速）。
3. **长尾性**：99% 场景好预测，1% 奇葩场景（急掉头、醉汉）才是事故来源。

> ⚠️ 关键认知（已在 `04-hands-on/code/prediction_multimodal.py` 验证）：评估必须用 **minADE/minFDE**（K 条预测挑最接近真值的），不能用平均——平均会学出"原地不动"。

## 2. 算法演进三代

### 第一代：CNN/RNN/GAN（2016–2019，栅格时代）
| 算法 | 创新 | 局限 |
|------|------|------|
| **Social-LSTM**（CVPR'16）| social pooling 建模行人交互 | 单模态 |
| **Social-GAN**（CVPR'18）| GAN 首次显式多模态 | 训练不稳 |
| **DESIRE** | seq2seq + 采样 | 慢 |

### 第二代：向量化 GNN/Transformer（2020–2023，主流）
**核心思想**：抛弃栅格化（贵、丢精度），直接用**向量化地图（polyline）+ agent 历史**。

| 算法 | 会议 | 核心创新 |
|------|------|---------|
| **VectorNet** | CVPR'20 | **奠基**：地图+agent 全表示为 vector，层级 GNN 聚合 |
| **LaneGCN** | ECCV'20 | 车道线图上的 GCN，Argoverse 时代 SOTA |
| **DenseTNT** | ICRA'21 | 密集采样目标点+打分，意图/轨迹解耦 |
| **MultiPath++** | CVPR'22 | anchor-based 多模态回归 |
| **HiVT** | CVPR'22 | agent-centric 局部坐标系 + 层级 Transformer |
| **QCNet** | ICCV'23 | **query-centric**，避免重复编码，nuScenes/WOMD 双榜 SOTA |
| **MTR / MTR++** | ECCV'22/IJCV'24 | **motion query + 密集意向点**，WOMD 冠军级（Waymo 主推）|

### 第三代：联合/博弈/端到端（2023+）
| 算法 | 思想 |
|------|------|
| **Trajectron++** | CVAE 联合分布 |
| **AgentFormer** | 时空 Transformer，agent 间 attention |
| **GameFormer** | **博弈论**：agent 轮流反应对方策略，迭代式"你猜我猜你猜" |
| **UniAD/VAD 内预测** | 不再独立模块，query 端到端融入全栈 |

## 3. 核心数学

**多模态轨迹分布**（Mixture 形式）：
$$p(\mathbf{y}_{1:T}|\mathbf{x}) = \sum_{k=1}^{K} p(k|\mathbf{x})\,\mathcal{N}(\mathbf{y}_{1:T};\boldsymbol{\mu}_k(\mathbf{x}), \boldsymbol{\Sigma}_k)$$
- $K=6$ 是 nuScenes 标配（预测 6 条候选轨迹）

**评估指标**：
| 指标 | 定义 | 考察什么 |
|------|------|---------|
| **minADE** | K 条中最优的平均位移误差 | 多模态覆盖 |
| **minFDE** | K 条中最优的终点误差 | 终点意图 |
| **MR** | K 条全错（FDE>2m）比例 | 漏真轨迹 |
| **b-minFDE** | 概率加权 minFDE（WOMD）| 概率校准 |

## 4. 2024–2026 趋势

- **闭环化**：预测不再孤立评估，看它对最终规划/闭环驾驶的贡献（NAVSIM PDMS）。
- **大模型化**：LLM 世界知识做意图推理（DriveLM 的 Q&A 链）。
- **长时序**：3s → 10s+（QCNet 的时序建模）。
- **占用化**：不预测 box 轨迹，预测未来 3D 占用（Cam4DOcc、OccWorld）。

## ✍️ 练习
1. 为什么 minADE 只挑一条最优就能鼓励多模态？如果训练 loss 也用 min（不是平均），会有什么问题（提示：winner-takes-all、模态坍缩）？
2. VectorNet 相比栅格化输入的三大优势？
3. GameFormer 的"迭代博弈"如何捕捉"你让我也让"的社交协商？

→ 相关代码：`04-hands-on/code/prediction_multimodal.py`（minADE 机制）、`03-classics/code/vectornet_minimal.py`（GNN+多模态预测）
