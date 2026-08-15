# 🛠️ 核心代码库索引

> 按学习阶段组织。每个仓库标注：用途、必读文件、上手难度。

---

## ① 入门与系统

| 仓库 | 用途 | 关键 | 难度 |
|------|------|------|------|
| `ApolloAuto/apollo` | 百度开源全栈 AD（模块化标杆）| `modules/perception` `modules/planning` | ⭐⭐⭐⭐ |
| `autowarefoundation/autoware_universe` | 开源 AD 栈（ROS2）| 规划/控制模块 | ⭐⭐⭐⭐ |
| `AtsushiSakai/PythonRobotics` | 规划/控制算法可视化宝库 | `PathTracking/` `PathPlanning/` | ⭐ |
| `zhm-real/MotionPlanning` | 规划算法集合 | `Control/` | ⭐⭐ |

## ② 感知

| 仓库 | 用途 | 关键文件 | 难度 |
|------|------|---------|------|
| `open-mmlab/OpenPCDet` ⭐5.7k | **LiDAR 检测全家桶** | `pcdet/models/detectors/centerpoint.py` | ⭐⭐⭐ |
| `open-mmlab/mmdetection3d` | 3D 感知框架 | `mmdet3d/models/` | ⭐⭐⭐⭐ |
| `nv-tlabs/lift-splat-shoot` | LSS 原始实现 | `src/` | ⭐⭐ |
| `fundamentalvision/BEVFormer` | camera-BEV 量产主流 | `projects/mmdet3d_plugin/` | ⭐⭐⭐⭐ |
| `exiawsh/StreamPETR` | camera-only SOTA | `streampetr_head.py` | ⭐⭐⭐⭐ |
| `MitHua/BEVDet` | 高效 BEV | — | ⭐⭐⭐ |
| `PJLab-ADG/3DTrans` | 3D 检测+迁移 | — | ⭐⭐⭐ |
| `wzzheng/OccNet` / `PJLab-ADG/OccWorld` | 占用预测/世界模型 | — | ⭐⭐⭐⭐ |
| `hustvl/VAD` | 向量化 E2E | — | ⭐⭐⭐ |
| `HXMap/MapQR` / `MapTR` | 在线建图 | — | ⭐⭐⭐ |

## ③ 预测

| 仓库 | 用途 | 难度 |
|------|------|------|
| `MitHua/Argoverse-forecasting` | VectorNet 基础 | ⭐⭐ |
| `decisionforce/AgentFormer` | 时空 Transformer 预测 | ⭐⭐⭐⭐ |
| `ZikangZhou/HiVT` | 层级向量 Transformer | ⭐⭐⭐ |
| `sshaoshuai/MTR` | WOMD 冠军级预测 | ⭐⭐⭐⭐ |
| `decisionforce/GameFormer` | 博弈论预测 | ⭐⭐⭐⭐ |

## ④ 规划 & 控制

| 仓库 | 用途 | 难度 |
|------|------|------|
| `ApolloAuto/apollo` | EM Planner（modules/planning）| ⭐⭐⭐⭐ |
| `zmwwwfork/Ruckig` | 在线轨迹生成 | ⭐⭐⭐ |
| `alexliniger/MPCC` | MPC 路径跟踪 | ⭐⭐⭐⭐ |

## ⑤ 端到端 & 大模型

| 仓库 | 用途 | 难度 |
|------|------|------|
| `OpenDriveLab/UniAD` ⭐4.7k | **CVPR'23 Best，E2E 奠基**（2.0 已发）| ⭐⭐⭐⭐⭐ |
| `hustvl/VAD` | 向量化 E2E | ⭐⭐⭐⭐ |
| `Thinklab-SJTU/Bench2Drive` | **CARLA 闭环 E2E 评测** | ⭐⭐⭐⭐ |
| `OpenDriveLab/NAVSIM` | 开环规划评测（PDMS）| ⭐⭐⭐ |
| `tsinghua-mars-lab/DriveVLM` | VLM + AD（已上车）| ⭐⭐⭐⭐ |
| `DriveVLA/OpenDriveVLA` | 开源驾驶 VLA | ⭐⭐⭐⭐ |
| `wayveai/Lingo`（blog） | 驾驶 VLA | — |
| `openvla/openvla` | 开源 VLA foundation | ⭐⭐⭐⭐ |
| `Physical-Intelligence/pi0`（blog）| 通用 VLA | — |

## ⑥ 世界模型 & 仿真

| 仓库 | 用途 | 难度 |
|------|------|------|
| `wzzheng/OccWorld` | 4D 占用世界模型 | ⭐⭐⭐⭐ |
| `OpenDriveLab/DriveWorld` | 占用 world model | ⭐⭐⭐⭐ |
| `carla-simulator/carla` ⭐11k+ | 开源 AD 仿真器 | ⭐⭐⭐ |
| `OpenDriveLab/neuRAD` | NeRF 重建驾驶场景 | ⭐⭐⭐⭐ |
| `PJLab-ADG/DriveDreamer` | 生成式仿真 | ⭐⭐⭐⭐ |

## ⑦ 数据集 & 基准（非代码，但必知）

| 名 | 任务 | 规模 | 链接 |
|----|------|------|------|
| **nuScenes** | 检测/跟踪/预测/规划 | 1000 scenes, 1k classes | nuscenes.org |
| **nuPlan** | 规划（开/闭环） | 1500h log | nuscenes.org/nuplan |
| **Waymo Open (WOD/WOMD)** | 检测/跟踪/运动预测 | 1950 scenes | waymo.com/open |
| **Argoverse 1/2** | 预测/运动 | — | argoverse.org |
| **KITTI** | 检测（经典）| 7481 train | cvlibs.net |
| **ONCE** | 大规模检测 | 1M scenes | once-for-auto-driving.github.io |
| **OpenLane** | 车道线 | — | — |
| **OpenOccupancy** | 占用 | — | — |
| **NAVSIM** | 开环规划 | — | github.com/autonomousvision/navsim |
| **Bench2Drive** | E2E 闭环 | 44 场景, 2M 帧 | github.com/Thinklab-SJTU/Bench2Drive |

---

## 🎯 上手顺序建议

```
入门: PythonRobotics（跑规划控制可视化）
  ↓
感知: OpenPCDet（跑 CenterPoint KITTI demo）
  ↓
BEV: lift-splat-shoot 原始仓库 → 本工程 lss_minimal.py
  ↓
E2E: UniAD（读代码 + 跑评测）
  ↓
闭环: CARLA + Bench2Drive（训练 mini E2E）
  ↓
前沿: OccWorld / DriveVLM / OpenDriveVLA
```
