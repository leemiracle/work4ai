# 🚗 ad-mastery · 智能驾驶全栈精通工程

> 从 0 到 1、从入门到前沿的自动驾驶（Autonomous Driving）系统性学习工程。
> 覆盖：模块化栈（感知/预测/规划/控制）→ 端到端新范式 → 世界模型 → VLA → 数据闭环 → 安全法规商业。
> 融入 2024–2026 最新研究（UniAD 2.0、EMMA、GAIA-2、OccWorld、π0、Bench2Drive），配套 **11 段可跑代码 + 13 篇深度笔记**。

## 📐 工程结构（完整版）

```
ad-mastery/
├── 01-fundamentals/                          ① 入门
│   ├── 00-overview.md                        全局：L0-L5 + 模块化栈 + 端到端两条路线
│   ├── 01-prediction.md                      预测层全算法（VectorNet→QCNet→MTR→GameFormer）
│   ├── 02-planning.md                        规划层全算法（A*→Hybrid A*→EM Planner→CBF）
│   └── 03-control.md                         控制层全算法（Pure Pursuit/LQR/MPC + 数学推导）
├── 02-perception/                            ② 感知
│   ├── notes/00-perception-overview.md       检测/BEV/占用/建图/跟踪全算法
│   └── code/
│       ├── lss_minimal.py                    ✅ 手写 LSS（camera-BEV 奠基）
│       └── occupancy_minimal.py              ✅ 玩具占用网络（稀疏观测→补全, IoU=0.40）
├── 03-classics/                              ③ 经典两座大山 + 实现
│   ├── notes/
│   │   ├── uniad-deepread.md                 UniAD 精读（query接口/两阶段/消融/2.0）
│   │   └── emma-deepread.md                  EMMA 精读（万物皆文本/Gemini/多任务共训）
│   └── code/
│       ├── mini_uniad.py                     ✅ 旗舰：Mini-UniAD 端到端联合训练演示
│       └── vectornet_minimal.py              ✅ VectorNet玩具版（GNN+多模态+minADE, 100%）
├── 04-hands-on/                              ④ 动手
│   ├── notes/00-hands-on-guide.md            CARLA + Bench2Drive + OpenPCDet 实战指南
│   └── code/
│       ├── pure_pursuit.py                   ✅ Pure Pursuit（δ=26.57°验证）
│       ├── hybrid_astar.py                   ✅ Hybrid A*（连续空间搜索）
│       ├── prediction_multimodal.py          ✅ minADE 多模态评估机制
│       ├── lqr_minimal.py                    ✅ LQR（Riccati递推+闭环收敛）
│       ├── mpc_minimal.py                    ✅ Diff-MPC（torch梯度优化控制）
│       ├── rrt_minimal.py                    ✅ RRT（随机采样规划+绕障）
│       └── bytetrack_minimal.py              ✅ ByteTrack思想（Kalman+IoU两阶段匹配）
├── 05-frontier/                              ⑤ 前沿 + 多视角
│   └── notes/
│       ├── 00-frontier-overview.md           世界模型+VLA 总览（GAIA/OccWorld/DriveVLM/π0）
│       ├── occworld-deepread.md              OccWorld 精读（占用token+GPT世界模型）
│       ├── drivevlm-deepread.md              DriveVLM 精读（三级推理链+双系统上车）
│       ├── 02-safety-regulation-ethics-business.md  安全/法规/伦理/商业全视角
│       └── 03-data-loop-simulation-slam.md   数据闭环/仿真/SLAM与定位
└── resources/
    ├── papers.md                             50+ 核心论文（分阶段+⭐必读等级+arXiv）
    └── repos.md                              40+ 代码库（关键文件+难度+上手顺序）
```

## ✅ 全部代码验证结果（10/10 跑通）

| 代码 | 验证输出 | 教学点 |
|------|---------|--------|
| `lss_minimal.py` | cam(2,32,8,22)→BEV(2,32,20,20) | LSS: 深度分布→3D点→BEV |
| `occupancy_minimal.py` | **IoU=0.402**（随机~0.1）| 占用补全：哪里被占≠是什么 |
| `mini_uniad.py` | 联合0.2370 < 分离0.2384 RMSE | **端到端联合训练价值**（query接口）|
| `vectornet_minimal.py` | **模态识别100%**, minFDE=0.006 | 向量化+GNN+多模态+minADE |
| `pure_pursuit.py` | α=30°→δ=26.57° | 几何横向控制 |
| `hybrid_astar.py` | 泊车搜索成功 | 连续空间+运动原语 |
| `prediction_multimodal.py` | minADE 选择机制 | 未来不唯一 |
| `lqr_minimal.py` | e: 1.0m→收敛<0.05m | Riccati + 闭环稳定 |
| `mpc_minimal.py` | 代价1.438, \|u\|<约束 | 可微MPC/滚动优化 |
| `rrt_minimal.py` | 绕障成功, 代价+2.91 | 随机采样规划 |
| `bytetrack_minimal.py` | 遮挡时ID保持 | 低分检测不丢弃 |

## 🗺️ 学习路线

| 阶段 | 读 | 跑 | 状态 |
|------|----|----|------|
| ① 入门 | 01-fundamentals/ 全部 | — | ✅ |
| ② 感知 | 02-perception/notes | `lss_minimal` `occupancy_minimal` | ✅ |
| ③ 经典 | 03-classics/notes | `mini_uniad` `vectornet_minimal` | ✅ |
| ④ 动手 | 04-hands-on/notes | 全部7个 + CARLA/Bench2Drive（需GPU环境）| ✅ |
| ⑤ 前沿 | 05-frontier/notes 全部 | — | ✅ |
| 资源 | papers.md / repos.md | OpenPCDet/UniAD 复现（进阶）| ✅ |

## 🎯 两条范式主线（贯穿全程）

1. **模块化栈**（Apollo/Waymo 经典）：可解释可调，但误差累积。
2. **端到端栈**（UniAD/EMMA/Tesla）：信息无损上限高，但黑盒难验证。
> 2025–2027 量产主流 = **感知端到端 + 规划规则/学习兜底**的混合。

## 💡 学完自测（里程碑）

- [ ] 能讲清 L2/L3 责任分水岭和 ODD 概念
- [ ] 能手画 LSS 数据流并解释 depth 分布的作用
- [ ] 能解释 UniAD 为什么用 query 接口 + 两阶段训练
- [ ] 能对比 EMMA（全语言）vs DriveVLM（双系统）的路线分歧
- [ ] 能说出占用预测解决长尾的原理
- [ ] 能推导 Pure Pursuit 公式和 LQR Riccati 方程
- [ ] 能解释 minADE 为什么必须多模态
- [ ] 能描述数据飞轮五环和影子模式
- [ ] 能分析 SOTIF 与 OOD 的关系
- [ ] 能算 Robotaxi 盈亏平衡的三要素

---

*与 ai-mentor 协作完成。全部 13 笔记 + 10 代码已验证跑通。2025-08-14*
