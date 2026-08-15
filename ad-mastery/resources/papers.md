# 📚 智能驾驶核心论文库

> 按阶段分层组织，每篇标注：会议/年份、arXiv、一句话价值、必读等级。
> ⭐ 数量 = 必读程度（最多 5⭐）。

---

## ① 入门与综述

| 论文 | 年 | arXiv | 价值 | ⭐ |
|------|----|------|------|---|
| *Autonomous Driving* (H. Liu et al. 书) | 2023 | — | 最系统教材，模块化栈全貌 | 4⭐ |
| A Survey on End-to-End AD | 2024 | 2406.18080 | E2E 范式综述 | 4⭐ |
| Think Twice Before Driving | 2022 | 2205.12565 | E2E 范式反思 | 3⭐ |

---

## ② 感知层

### 2.1 BEV / Camera-only 3D 感知
| 论文 | 会议 | arXiv | 价值 | ⭐ |
|------|------|------|------|---|
| **LSS (Lift-Splat-Shoot)** | ECCV'20 | 2008.05711 | camera-BEV 奠基，必读 | 5⭐ |
| **BEVDet** | arXiv'21 | 2112.11790 | 高效 BEV 检测 | 4⭐ |
| **BEVDepth** | arXiv'22 | 2206.10092 | LSS + depth 监督 | 4⭐ |
| **BEVFormer** | ECCV'22 | 2203.17270 | 时空 Transformer，量产主流 | 5⭐ |
| **DETR3D** | CoRL'21 | 2110.06922 | 3D DETR | 3⭐ |
| **PETR / PETRv2** | ECCV'22 | 2203.05625 | 3D 位置编码 | 4⭐ |
| **StreamPETR** | ICCV'23 | 2307.16186 | 时序，camera-only SOTA | 5⭐ |
| **Sparse4D** | arXiv'23 | 2211.10581 | 稀疏多视角融合 | 4⭐ |

### 2.2 LiDAR / 多模态融合
| 论文 | 会议 | arXiv | 价值 | ⭐ |
|------|------|------|------|---|
| **PointPillars** | CVPR'19 | 1812.05784 | pillar 化，快 | 4⭐ |
| **SECOND** | Sensors'18 | 1801.05373 | 稀疏 3D 卷积 | 4⭐ |
| **CenterPoint** | CVPR'20 | 2006.11275 | anchor-free LiDAR 标杆 | 5⭐ |
| **PV-RCNN / PV-RCNN++** | CVPR'20/22 | 1912.13192 | voxel+point 融合高精度 | 4⭐ |
| **VoxelNeXt** | CVPR'23 | 2303.11301 | 全稀疏检测 | 4⭐ |
| **TransFusion(-L)** | CVPR'22 | 2203.11496 | query 层融合 | 4⭐ |
| **BEVFusion** | ICRA'22 / arXiv | 2205.13542 | BEV 空间融合，最流行 | 5⭐ |
| **DSVT** | CVPR'23 | 2301.06051 | 稀疏 Transformer，Waymo SOTA | 4⭐ |
| **MPPNet** | ECCV'22 | 2205.05979 | 多帧时序，WOD 第一 | 3⭐ |

### 2.3 占用预测（Occupancy）
| 论文 | 会议 | arXiv | 价值 | ⭐ |
|------|------|------|------|---|
| **SurroundOcc** | TPAMI'23 | 2303.09551 | 稠密占用 | 4⭐ |
| **TPVFormer** | CVPR'23 | 2302.07817 | 三视角近似 3D，省显存 | 4⭐ |
| **VoxFormer** | CVPR'23 | 2302.12251 | 两阶段稀疏扩散 | 4⭐ |
| **FB-Occ** | CVPR'23-W | 2306.07217 | 前背景分离，nuScenes 冠军 | 3⭐ |
| **OccWorld** | ECCV'24 | 2311.16038 | 4D 占用世界模型 | 5⭐ |

### 2.4 在线建图 / 车道线
| 论文 | 会议 | arXiv | 价值 | ⭐ |
|------|------|------|------|---|
| **CLRNet** | CVPR'22 | 2203.10350 | anchor 车道线 | 3⭐ |
| **MapTR / MapTRv2** | ICLR'23 | 2208.14437 | 向量化在线建图，主流 | 5⭐ |
| **StreamMapNet** | NeurIPS'23 | 2308.12559 | 时序建图 | 4⭐ |
| **P-MapNet** | CVPR'24 | — | 引入 prior | 3⭐ |

### 2.5 多目标跟踪
| 论文 | 会议 | arXiv | 价值 | ⭐ |
|------|------|------|------|---|
| **ByteTrack** | ECCV'22 | 2110.06864 | 不丢低分，2D MOT SOTA | 4⭐ |

---

## ③ 预测层

| 论文 | 会议 | arXiv | 价值 | ⭐ |
|------|------|------|------|---|
| **Social-GAN** | CVPR'18 | 1803.10892 | 多模态预测开山 | 4⭐ |
| **VectorNet** | CVPR'20 | 2005.04259 | 向量化奠基 | 5⭐ |
| **LaneGCN** | ECCV'20 | 2007.13756 | 车道线 GNN | 4⭐ |
| **Trajectron++** | ICRA'20 | 2001.03093 | CVAE 联合 | 3⭐ |
| **HiVT** | CVPR'22 | 2205.12978 | 层级向量 Transformer | 4⭐ |
| **DenseTNT** | ICRA'21 | 2108.09640 | 密集目标采样 | 3⭐ |
| **MultiPath++** | CVPR'22 | 2111.15273 | anchor 多模态 | 4⭐ |
| **QCNet** | ICCV'23 | 2306.14549 | query-centric，双榜 SOTA | 5⭐ |
| **MTR / MTR++** | ECCV'22 | 2209.13507 | motion query，WOMD 冠军 | 5⭐ |
| **AgentFormer** | ICCV'21 | 2103.14023 | 时空 Transformer | 3⭐ |
| **GameFormer** | ICCV'23 | 2303.05760 | 博弈论预测 | 4⭐ |

---

## ④ 规划 & 控制（关键论文，多为系统/工程）

| 论文 | 会议 | arXiv | 价值 | ⭐ |
|------|------|------|------|---|
| **Hybrid A\*** | IJRR'10 | — | 连续空间搜索，泊车标配 | 4⭐ |
| **ChauffeurNet** | Waymo'18 | — | 模仿学习轨迹规划开山 | 3⭐ |
| **Apollo EM Planner** | 2017 | — | path-speed 解耦优化，国产鼻祖 | 4⭐ |
| **RSS** | Mobileye'17 | — | 可证安全框架 | 3⭐ |
| **BarrierNet** | arXiv'24 | — | CBF + 神经网络，E2E 可证安全 | 3⭐ |

---

## ⑤ 端到端新范式（本工程核心）

| 论文 | 会议 | arXiv | 价值 | ⭐ |
|------|------|------|------|---|
| **UniAD** | CVPR'23 Best | 2212.10156 | planning-oriented E2E 奠基 | 5⭐ |
| **VAD** | ICCV'23 | 2303.12077 | 向量化 E2E，快 | 5⭐ |
| **VADv2** | CVPR'24 | 2402.13243 | 向量 token + 大规模 IL | 4⭐ |
| **PARA-Drive** | CVPR'24 | 2406.08162 | 并行多任务 E2E | 3⭐ |
| **LMDrive** | CVPR'24 | 2403.09401 | LLM + 导航 E2E | 4⭐ |
| **EMMA** | TMLR'25 | 2410.23262 | Gemini 大模型 E2E | 5⭐ |
| **DriveVLM** | 2024 | 2402.12289 | VLM+AD 已上车 | 5⭐ |
| **Senna** | arXiv'24 | 2410.06803 | VLM 理解 + E2E 执行解耦 | 3⭐ |
| **DriveLM** | CVPR'24 | 2309.09205 | Q&A 结构化推理 | 4⭐ |
| **DriveLikeAHuman** | NeurIPS'23 | 2307.01897 | 类人决策 | 3⭐ |

---

## ⑥ 世界模型 & VLA

| 论文 | 会议 | arXiv | 价值 | ⭐ |
|------|------|------|------|---|
| **GAIA-1** | Wayve'23 | 2309.17080 | 首个大规模驾驶世界模型 | 5⭐ |
| **GAIA-2** | Wayve'24 | wayve.ai/science | 高分辨率可控 | 5⭐ |
| **DriveDreamer(-2)** | CVPR'24 | 2309.09777 | 扩散生成驾驶视频 | 4⭐ |
| **GenAD** | CVPR'24 | 2403.09630 | 潜空间扩散 | 4⭐ |
| **OccWorld** | ECCV'24 | 2311.16038 | 4D 占用世界模型 | 5⭐ |
| **MagicDrive** | CVPR'24 | 2310.02601 | 生成式数据增广 | 3⭐ |
| **neuRAD** | CVPR'24 | 2311.13560 | NeRF 重建驾驶场景 | 4⭐ |
| **LINGO-1/2** | Wayve'23/24 | wayve.ai/science | 驾驶 VLA | 5⭐ |
| **OpenDriveVLA** | 2024-25 | — | 开源驾驶 VLA | 4⭐ |
| **π0 / π0-FAST** | PI'24-25 | 2410.24164 | 通用 VLA（机器人→车）| 5⭐ |
| **OpenVLA** | 2024 | 2406.09246 | 开源 VLA foundation | 4⭐ |
| **RDT-1B** | 2024 | 2410.07864 | 双臂机器人 VLA | 3⭐ |

---

## ⑦ 基准与评测

| 基准 | 任务 | 链接 |
|------|------|------|
| **nuScenes** | 检测/跟踪/预测/规划 | nuscenes.org |
| **nuPlan** | 规划（开/闭环） | nuscenes.org/nuplan |
| **Waymo Open (WOD/WOMD)** | 检测/跟踪/运动预测 | waymo.com/open |
| **Argoverse 1/2** | 预测/运动 | argoverse.org |
| **OpenLane** | 车道线 | — |
| **OpenOccupancy** | 占用 | — |
| **NAVSIM** | 开环规划（PDMS 指标） | github.com/autonomousvision/navsim |
| **Bench2Drive** | E2E 闭环（CARLA 2.0）| github.com/Thinklab-SJTU/Bench2Drive |

---

## 🔗 持续跟踪

- **HuggingFace Daily Papers**（cs.CV/RO）
- **arXiv**: cs.RO / cs.CV / cs.LG
- **OpenDriveLab** (opendrivelab.com) — 领域风向标
- **AK (@_akhaliq)**、**Karpathy**
- 顶会：CVPR / ICCV / ECCV / NeurIPS / ICML / ICLR / CoRL
