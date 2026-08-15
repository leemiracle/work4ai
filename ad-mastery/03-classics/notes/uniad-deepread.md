# ③ 经典精读之一：UniAD —— 模块化端到端的奠基

> **Planning-oriented Autonomous Driving**, CVPR 2023 **Best Paper Award**（12/2360 篇 Award Candidate）。
> OpenDriveLab（上海 AI Lab + 商汤）。arXiv:2212.10156 ｜ 代码：`OpenDriveLab/UniAD`（2025/10 发布 **2.0**）

---

## 0. 为什么 UniAD 必读

UniAD 是**端到端自动驾驶的分水岭**。它第一次用严谨实验证明：**把感知+预测+规划全塞进一个网络、端到端联合训练，能全面超越分模块方法**。它定义了"**planning-oriented**"哲学——所有任务都为最终规划服务。此后几乎所有 E2E 工作（VAD、EMMA、DriveVLM...）都建立在 UniAD 的范式认知上。

---

## 1. 核心问题：模块化的两大痛点

传统模块化栈的痛点，UniAD 直击：

1. **误差累积（Error Accumulation）**：感知漏检一个→预测错→规划撞。模块间错误逐级放大。
2. **信息丢失（Information Loss）**：模块间接口（box/lane）是人为设计的"瓶颈"，原始信号的有用信息被压缩。

> UniAD 的回答：**不要人为接口，用 query 作为统一通信介质**，让信息无损流动、梯度端到端反传。

## 2. 架构总览（7 个模块串联）

```mermaid
flowchart LR
    IMG[多视角图像<br/>6 cameras] --> BB[EVA Backbone<br/>图像特征]
    BB --> BEV[BEVFormer<br/>时空BEV编码]
    BEV --> T[① Track<br/>多目标跟踪]
    T --> M[② Map<br/>在线建图]
    M --> MO[③ Motion<br/>运动预测]
    MO --> OC[④ Occ<br/>占用预测]
    OC --> PL[⑤ Planner<br/>规划]
    PL --> TRAJ[未来轨迹]
```

**输入**：6 路相机图像（nuScenes）。
**输出**：自车未来轨迹（规划）+ 所有中间任务结果（检测/跟踪/建图/预测/占用）。

## 3. 关键创新：Query 作为统一接口

这是 UniAD 最精髓的设计，必须深懂：

| 模块 | Query 类型 | 承载什么 | 如何流动 |
|------|-----------|---------|---------|
| Track | **track query** | 每个被跟踪目标 | 帧间传递（memory bank），新目标 query init |
| Map | **map query** | 车道线/边界元素 | 从 BEV 采样 |
| Motion | 复用 track query | 轨迹预测 | track query → 预测头 |
| Occ | 复用 track query | 占用 | query → voxel 解码 |
| Planner | track + map query | 规划 | 所有 query 汇聚 → 轨迹解码 |

**为什么 Query 而不是 box**：
- box 是**离散、有损**的（丢了置信度、形状细节、关系）。
- query 是**连续、高维**的特征向量，携带全部信息。
- 关键：**梯度能从规划损失经 query 反向流回图像**——这才是"端到端"的精髓。

## 4. 训练策略：两阶段（重要工程细节）

UniAD 不能从头联合训（会崩），必须**两阶段**：

**Stage 1：感知预训练**
- 只训 Track + Map（感知部分），5 帧 BEV。
- 目的：得到稳定的感知权重初始化。
- GPU：16×A100，约 2 天。
- 注意（v2.0 修复的 bug）：早期版本误加了 `loss_past_traj` 且冻结了 img_neck/BN，导致无法复现。修复后 AMOTA=0.394。

**Stage 2：端到端联合训练**
- 所有模块一起训（track/map/motion/occ/planning），3 帧 BEV。
- GPU：8×A100。

## 5. 损失函数（多任务联合）

$$\mathcal{L}_{total} = \lambda_{det}\mathcal{L}_{det} + \lambda_{track}\mathcal{L}_{track} + \lambda_{map}\mathcal{L}_{map} + \lambda_{motion}\mathcal{L}_{motion} + \lambda_{occ}\mathcal{L}_{occ} + \lambda_{plan}\mathcal{L}_{plan}$$

各 $\lambda$ 权重是超参（实验调出来的）。

## 6. 实验结果（nuScenes）

| 任务 | 指标 | UniAD | 说明 |
|------|------|-------|------|
| Tracking | AMOTA | 0.380 | 端到端跟踪 SOTA |
| Mapping | IoU-lane | 0.314 | 在线建图 |
| Motion | minADE | 0.794 m | 运动预测 |
| Occupancy | IoU-n | 64.0 | 占用 |
| **Planning** | **avg Col** | **0.29%** | **碰撞率极低** |
| Planning | L2 (1s/2s/3s) | 0.29/0.89/1.53 m | 轨迹误差 |

**关键消融**（论文最有说服力的部分）：
- 去掉 Motion 模块 → 规划 L2 大幅上升（证明预测对规划的价值）。
- 去掉 Occ → 碰撞率上升（证明占用对安全的价值）。
- 不端到端联合训（分模块训后接）→ 各任务都差（**这是端到端的核心证据**）。

## 7. UniAD 2.0 新特性（2025/10/29 发布，超新）

- 框架迁移到 **mmdet3d 1.x + torch 2.x**（与现代栈对齐）。
- 整合 **nuPlan + NAVSIM** 数据集（规划闭环评测）。
- NAVSIM PDMS = 83.4（新基线）。

## 8. 局限与争议（批判性）

1. **推理慢**：7 模块串行，~500ms/帧，离实时（50ms）差远。
2. **需要全栈标注**：检测+跟踪+建图+预测+占用都要标，数据成本极高。
3. **规划头简单**：只是一个 MLP/小 Transformer，没用到强规划器。
4. **仍是开环训练**：在 nuScenes 开环评估，与真实闭环差距大（Bench2Drive 弥补）。
5. **开环指标虚高**：后续工作指出开环 L2/碰撞率不能反映真实驾驶能力。

## 9. 怎么动手

```bash
git clone https://github.com/OpenDriveLab/UniAD
cd UniAD && git checkout v2.0
# 按 docs/INSTALL.md 装环境（torch 2.0.1+cu118, mmdet3d 1.0.0rc6）
# 下 nuScenes 数据 + 预处理（docs/DATA_PREP.md）
# 下预训练权重到 ckpts/
# 评测：docs/TRAIN_EVAL.md#example
```
- Stage1 权重：`uniad_base_track_map.pth`
- Stage2 权重：`uniad_base_e2e.pth`

## ✍️ 练习

1. 用自己的话解释：为什么 UniAD 用 query 而不是 box 作为模块间接口？这对"端到端"意味着什么？（提示：梯度通路）
2. UniAD 的消融实验中，"去掉占用模块 → 碰撞率上升"。从占用预测的功能出发，解释为什么。
3. UniAD 两阶段训练的原因是什么？如果直接从头联合训会怎样？（思考：各任务的梯度尺度、初始化）
4. （进阶）UniAD 的开环 L2 指标被批评"虚高"。Bench2Drive（CARLA 闭环）如何弥补这个缺陷？
5. （代码）读 `projects/mmdet3d_plugin/uniad/detectors/uniad_e2e.py` 的 `forward`，画出从图像到规划轨迹的完整前向调用链。

## 📌 下一步

→ 进入 `03-classics/notes/emma-deepread.md` 精读 EMMA（大模型端到端的标杆）。
