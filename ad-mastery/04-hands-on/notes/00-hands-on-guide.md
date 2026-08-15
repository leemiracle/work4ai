# ④ 动手：跑通控制算法 + CARLA 闭环 + mini E2E

> 本篇把理论变成可跑代码。三步走：① 控制层算法（已跑通）→ ② CARLA 仿真环境 → ③ Bench2Drive 闭环 E2E。

---

## Part 1：控制层算法（✅ 已跑通）

### 1.1 Pure Pursuit（纯跟踪）横向控制
**文件**：`code/pure_pursuit.py`
**核心公式**（几何法，盯前瞻点）：
$$\delta = \arctan\frac{2L\sin\alpha}{L_d}$$
**跑通结果**：α=30°, Ld=5m, L=2.5m → δ=26.57° ✓
**自练**：把前瞻距离改成速度自适应 $L_d = k\cdot v$，观察高速/低速跟踪误差变化。

### 1.2 Hybrid A* 路径搜索
**文件**：`code/hybrid_astar.py`
**核心**：A* 在**连续 $[x,y,\theta]$ 状态空间**，运动原语保证可执行（满足最小转弯半径）。
**跑通结果**：泊车场景搜索成功，12 节点 ✓
**用途**：泊车、掉头、U-turn 的标配。

### 1.3 轨迹预测多模态性
**文件**：`code/prediction_multimodal.py`
**核心洞察**：未来不唯一，评估必须用 **minADE/minFDE**（挑最接近 GT 的那条），不能用平均（否则学"原地不动"）。
**跑通结果**：演示 minADE 选择机制 ✓

---

## Part 2：CARLA 仿真环境搭建

### 2.1 为什么 CARLA
CARLA 是开源自动驾驶仿真器（UE4 引擎），**学术闭环评测标准**（Bench2Drive、Leaderboard 2.0）。

### 2.2 安装（Linux + GPU 推荐）
```bash
# 方式1: 官方打包版（最快）
wget https://carla-releases.s3.eu-west-1.amazonaws.com/Linux/CARLA_0.9.13.tar.gz
mkdir ~/carla && tar -xzf CARLA_0.9.13.tar.gz -C ~/carla
cd ~/carla && ./CarlaUE4.sh -quality=Low    # 低画质省 GPU

# Python API
pip install carla==0.9.13
```

### 2.3 最小 demo（让一辆车在 CARLA 里自动驾驶）
```python
import carla, random, time
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.load_world('Town04')          # 加载地图
bp = world.get_blueprint_library().filter('vehicle.*')[0]
spawn = world.get_map().get_spawn_points()[0]
veh = world.spawn_actor(bp, spawn)
veh.set_autopilot(True)                       # 开启 CARLA 内置自动驾驶
spectator = world.get_spectator()
spectator.set_transform(veh.get_transform())  # 跟随
time.sleep(60)                                # 看 60 秒
```

---

## Part 3：Bench2Drive —— E2E 闭环评测标杆

### 3.1 为什么 Bench2Drive
nuScenes 开环 L2 指标"虚高"——真实驾驶是**闭环**的（你的动作影响世界）。Bench2Drive（CVPR'24）基于 **CARLA Leaderboard 2.0**，提供：
- **44 个场景**（超车、路口、施工...）
- **闭环指标**：Driving Score、Route Completion、碰撞率
- **支持主流 E2E**：UniAD、VAD、TCP...

### 3.2 安装与运行
```bash
git clone https://github.com/Thinklab-SJTU/Bench2Drive
cd Bench2Drive
# 需 CARLA 0.9.13 + 特定 Python 环境（见仓库 README）
# 训练数据：Bench2Drive-Base（200 万帧专家数据，约 1.5TB）
# 评测一个 E2E 模型：
python leaderboard/leaderboard_evaluator.py \
  --scenarios routes/bench2drive_lights.xml \
  --agent your_agent \
  --track CHALLENGE_DETECTION
```

### 3.3 训练一个 mini E2E（最简版思路）
1. **数据**：用 Bench2Drive-Base 的专家轨迹（图像+速度+导航→未来轨迹）。
2. **模型**：ResNet 编码图像 → MLP → 输出 waypoint（最简版）。
3. **控制**：waypoint 经 Pure Pursuit 转成方向盘。
4. **训练**：模仿学习（L2 loss）。
5. **评测**：CARLA 闭环。

> 进阶：把 UniAD/VAD 的 checkpoint 迁移过来对比。

---

## Part 4：OpenPCDet 跑 CenterPoint（感知实战）

```bash
git clone https://github.com/open-mmlab/OpenPCDet
cd OpenPCDet
pip install -r requirements.txt
# 装 spconv-cudaxxx（按 CUDA 版本）
python setup.py develop

# 下 KITTI 数据 + 预训练权重（见 docs/DEMO.md）
# 跑 demo：
python demo.py --cfg_file cfgs/kitti_models/pointrcnn.yaml \
  --ckpt pointrcnn_7728.pth --data_dir ../data/kitti
```
**可跑模型**：PointPillars/SECOND/PointRCNN/PV-RCNN/VoxelNeXt（KITTI/Waymo/nuScenes 全有）。

---

## 学习里程碑（自测）

完成本篇后，你应该能：
- [ ] 跑通 Pure Pursuit 并解释方向盘怎么算出来的
- [ ] 在 CARLA 里让一辆车自动驾驶（autopilot）
- [ ] 用 Bench2Drive 评测一个 E2E 模型的 Driving Score
- [ ] 跑 OpenPCDet 的 CenterPoint 在 KITTI 上检测

## ✍️ 练习

1. 把 `pure_pursuit.py` 的前瞻距离改成速度自适应（$L_d = k\cdot v$），分别在 v=5 和 v=20 下跑，对比跟踪误差，解释为什么高速需要更大前瞻。
2. 在 CARLA 里实现一个最简单的"红绿灯停车"逻辑（提示：用 `world.get_actors().filter('traffic.traffic_light*')`）。
3. 用 Bench2Drive 的专家数据训练一个图像→waypoint 的 mini E2E，报告其 Driving Score（会很低，但能跑通闭环就是胜利）。
4. 跑 OpenPCDet 的 CenterPoint 在 nuScenes mini 子集（10 scenes）上推理，可视化检测结果。

## 📌 总结

恭喜——到这你已经：① 理解全栈 ② 手写 LSS ③ 精读 UniAD/EMMA ④ 跑通控制算法 ⑤ 知道怎么上 CARLA 闭环。
接下来可选：① 深读单篇论文（VAD/OccWorld/GAIA-2）② 从零实现一个组件 ③ 跟踪 2026 最新前沿。告诉我方向。
