# CS227A: Robot Perception

> Stanford University（Stanford AI Lab / Interactive Perception & Autonomy Lab）
> 方向：机器人感知——从几何视觉到多模态基础模型
> Prerequisites: 线性代数 + 概率 + 基础 ML（推荐 CS231A 计算机视觉几何 / CS231N）
> Language: Python + PyTorch + ROS / point cloud 库（Open3D, PCL）
> Difficulty: ⭐⭐⭐⭐⭐
> 官网：http://cs227a.stanford.edu/（基于公开信息整理，官网抓取时不可达）

> ⚠️ **说明**：本 OVERVIEW 基于课程描述与 Stanford 机器人感知公开教学材料整理，
> 项目代码位于 `supplementary/grad_projects.py::cs227a_demo`（多模态融合：视觉 + 触觉 + 语言）。

---

## 📚 课程定位（独特价值）

Stanford 机器人感知的**研究级课程**，聚焦「**机器人怎么看世界、怎么把感知接到动作上**」。与纯 CV 课（CS231N）的本质区别：

- **以「抓取/操作」为目标**：不只是识别物体叫什么，而要估计**位姿、几何、可抓性**，感知直接驱动动作。
- **多模态**：视觉 + 深度（RGB-D）+ 触觉 + 力觉 + 语言指令，融合是核心议题，不是可选。
- **几何 + 学习双轨**：经典几何视觉（ICP、RANSAC、Bundle Adjustment）与现代深度学习（PointNet、Diffusion Policy）并重。
- **Sim-to-Real + 基础模型**：衔接最新 LLM/VLM 进机器人（PaLM-E、RT-2、VoxPoser）。

独特价值在于它是**感知到操控的桥梁**：CS231A 教你看，CS227A 教你看完之后怎么伸手。

> 与姊妹课的关系：
> - **CS237A**（Pavone）= 运动 + 规划 + 控制（怎么动）
> - **CS227A** = 感知 + 多模态（看见什么、怎么知道摸到的是苹果）
> - **CS238** = 在不确定下做决策（POMDP）—— CS227A 的观测模型 $O(o|s)$ 就是 CS227A 的输出

---

## 🎯 学习目标

1. 掌握 **2D/3D 视觉感知**：检测、分割、位姿估计、点云配准。
2. 理解 **RGB-D 与深度**：立体匹配、ToF、深度不确定性。
3. 实现 **多模态融合**：视觉 + 触觉 + 语言 → 统一的动作决策。
4. 掌握 **抓取规划**：几何法（力闭合）vs 数据驱动（Dex-Net、GraspNet）。
5. 应用 **基础模型到机器人**：CLIP/SAM/RT-2/PaLM-E。
6. 评估 **Sim-to-Real gap** 与触觉/力觉的不可替代性。

---

## 📅 完整模块（基于 Stanford 机器人感知教学主线）

### Part 1: 感知的数学基础
- 相机模型（针孔、内外参、畸变）
- 射影几何、对极几何、本质矩阵
- 齐次坐标与 SE(3) 变换
- 深度估计：立体匹配、SfM、光流

### Part 2: 2D 视觉感知
- 目标检测：R-CNN 系 → YOLO/DETR
- 语义/实例分割：U-Net、Mask R-CNN、SAM
- 位姿估计：PoseCNN、PoseCNN-style keypoint
- 视觉特征：SIFT/ORB（几何侧）vs 深度特征（CLIP）

### Part 3: 3D 感知（点云与 RGB-D）
- 点云表示：PointNet / PointNet++ / Point Transformer
- 体素、Octree、TSDF / 体素融合（KinectFusion）
- **点云配准**：ICP、RANSAC、全局配准
- 表面重建与法向量估计
- 3D 检测与分割（PointRCNN、VoxelNet）

### Part 4: 触觉与力觉感知
- 触觉传感器（GelSight、BioTac）：压力、纹理、温度、滑动
- 力觉 + 阻抗控制
- 视-触融合：滑动检测、在手物体估计
- 本课代码的「触觉通道」直接对应此模块

### Part 5: 多模态融合
- 早期/晚期/注意力融合策略
- **语言指令 grounding**：CLIPort、GroundingDINO
- VLM 进机器人：PaLM-E、RT-2、VoxPoser
- 多模态表征对齐（对比学习）
- 本课代码 `MultiModalPerceiver` 的核心思想来源

### Part 6: 抓取与操作
- 几何抓取：力闭合、形式闭包
- 数据驱动：**Dex-Net**、**GraspNet-1Billion**
- 学习抓取：GraspCV、6-DOF GraspNet
- 在手操作与灵巧手
- 本课代码 `_compute_grasp` 的简化版

### Part 7: 基础模型 + Robotics ⭐
- **RT-1 / RT-2 / RT-X**（Open X-Embodiment）
- **PaLM-E**（多模态 embodied LLM）
- **SayCan**（语言 → affordance → 动作链）
- **Diffusion Policy**（扩散模型生成动作轨迹）
- **VoxPoser**（LLM 生成 3D 价值地图指导操作，Stanford）

### Part 8: Sim-to-Real 与部署
- 仿真器（Isaac Sim、PyBullet、MuJoCo）
- 域随机化、域适应
- 真实硬件：Franka、UR5、机械手
- 安全感知与人机协作

---

## 🧮 核心算法 / 数学

### 相机投影（针孔模型）
$$\pi \begin{bmatrix} X \\ Y \\ Z \\ 1 \end{bmatrix} = K [R \mid t] \begin{bmatrix} X_w \\ Y_w \\ Z_w \\ 1 \end{bmatrix}, \quad K = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}$$

### ICP（Iterative Closest Point，点云配准）
```
repeat:
    对 source 中每点找 target 最近点 (对应)
    求最优 R, t 最小化 Σ ||R·p_i + t − q_i||²  (SVD 闭式解)
    应用 R, t 到 source
until 收敛
```

### 触觉-视觉贝叶斯融合（本课代码思想）
$$P(\text{object}=o \mid v, \tau, \ell) \propto P(v \mid o)\, P(\tau \mid o)\, P(\ell \mid o)\, P(o)$$
- $v$ 视觉、$\tau$ 触觉、$\ell$ 语言指令，三个似然相乘后归一化

### 抓取力闭合（Force Closure）
- 接触点集 $\{c_i\}$ 与法向 $\{n_i\}$ 能抵抗任意外力 wrench ⇔ 摩擦锥的凸包包含原点

### PointNet（点云深度学习）
$$h = \max_{i} \text{MLP}(x_i) \quad \text{(对称函数处理无序点集)}$$

### Diffusion Policy（动作生成）
- 去噪过程：$\epsilon_\theta(\mathbf{x}_t, t)$ 学噪声，生成动作轨迹 $\mathbf{x}_0$

---

## 💻 项目代码

📁 `supplementary/grad_projects.py::cs227a_demo`

**实现**（纯 Python，无依赖）：
1. ✅ **视觉对象** `VisualObject`：name/color/shape/position/confidence
2. ✅ **触觉读数** `TactileReading`：pressure/texture/temperature
3. ✅ **多模态感知器** `MultiModalPerceiver`：融合视觉 + 触觉 + 语言指令
   - 视觉候选 → 触觉过滤（texture + pressure）→ 语言 grounding → 抓取规划
4. ✅ **抓取规划** `_compute_grasp`：根据位置 + 压力计算抓取力与位姿
5. ✅ 两个场景 demo：「拿苹果」「小心端热杯子」

### 运行
```bash
cd stanford-cs-projects
python3 supplementary/grad_projects.py       # 跑全部 demo（含 cs227a）
python3 -c "from supplementary.grad_projects import cs227a_demo; cs227a_demo()"
```

**输出示例**：
```
📋 CS227A: Robot Perception (Multi-Modal)
   Instruction: Pick up the apple
   Tactile: pressure=0.4, texture=smooth, temp=22.0°C
   → Action: grasp, target=red_apple, force=0.70
   Instruction: Hold the cup carefully
   Tactile: pressure=0.6, texture=smooth, temp=60.0°C
   → Action: grasp, target=cup, force=0.80
```

### 代码与课程的对应关系

| 课程概念 | 代码位置 |
|----------|----------|
| 视觉候选（2D 检测输出） | `VisualObject` 列表 |
| 触觉感知（Part 4） | `TactileReading` |
| 触觉过滤候选（视-触融合） | `perceive` 中 texture/pressure 分支 |
| 语言 grounding（Part 5） | `_extract_target` + `_object_matches` |
| 抓取规划（Part 6） | `_compute_grasp` |
| 多模态概率融合（公式） | 三步级联过滤 = 近似 $P(o\mid v,\tau,\ell)$ |

> 注：本项目用规则式融合演示思想；真实作业会用 **PyTorch 注意力融合** + **Open3D 点云** + **ROS** 管道，并接入 Franka 真机。

---

## 📊 关键论文（按 P0/P1/P2 分级）

### 🔴 P0（必读，奠基）
1. **Qi, Su, Mo & Guibas 2017** "PointNet: Deep Learning on Point Sets"（[arXiv:1612.00593](https://arxiv.org/abs/1612.00593)）— 点云深度学习起点
2. **Mahler et al. 2017** "Dex-Net 2.0: Deep Learning to Plan Robust Grasps" — 数据驱动抓取
3. **Bohg, Morales, Asfour & Kragic 2014** "Data-driven Grasp Synthesis—A Survey" — 抓取综述
4. **Radford et al. 2021** "CLIP: Learning Transferable Visual Models"（[arXiv:2103.00020](https://arxiv.org/abs/2103.00020)）— 视觉-语言对齐，VLM 之基

### 🟡 P1（重要方法）
5. **Qi et al. 2017** "PointNet++: Deep Hierarchical Feature Learning on Point Sets"（[arXiv:1706.02413](https://arxiv.org/abs/1706.02413)）
6. **Fang et al. 2020** "GraspNet-1Billion: A Large-Scale Benchmark for General Object Grasping"（[arXiv:2007.02112](https://arxiv.org/abs/2007.02112)）
7. **Brohan et al. 2023** "RT-2: Vision-Language-Action Models" — Google
8. **Driess et al. 2023** "PaLM-E: An Embodied Multimodal Language Model"（[arXiv:2303.03378](https://arxiv.org/abs/2303.03378)）
9. **Chi et al. 2023** "Diffusion Policy: Visuomotor Policy Learning via Action Diffusion"（[arXiv:2303.04137](https://arxiv.org/abs/2303.04137)）— Stanford 亮点
10. **Shridhar et al. 2022** "CLIPort: What and Where Pathways for Robotic Manipulation"（[arXiv:2109.12098](https://arxiv.org/abs/2109.12098)）

### 🟢 P2（拓展 + 触觉）
11. **Ahn et al. 2022** "SayCan: Do As I Can, Not As I Say"（[arXiv:2204.01691](https://arxiv.org/abs/2204.01691)）
12. **Wen et al. 2023** "FoundationPose: Unified 6D Pose Estimation"（[arXiv:2312.08344](https://arxiv.org/abs/2312.08344)）
13. **Kirmani et al. 2023** "VoxPoser: Composable 3D Value Maps" — Stanford
14. **Tacchetti et al. 2018 / Li et al. GelSight** — 触觉感知系列
15. **Open X-Embodiment 2023 / RT-X**（[arXiv:2310.08864](https://arxiv.org/abs/2310.08864)）— 跨本体数据集

---

## 🎯 学习路径（按角色）

| 角色 | 推荐路线 |
|------|----------|
| **机器人 manipulation 研究** | CS227A → CS237A → 读 Diffusion Policy / Dex-Net |
| **基础模型 × Robotics** | CS227A → 读 RT-2 / PaLM-E / VoxPoser（Stanford 强项）|
| **感知/CV 偏几何** | CS231A（几何）→ CS227A（3D + 点云）|
| **触觉/灵巧手** | CS227A 触觉章 → 读 GelSight / 视触融合论文 |
| **工业落地** | CS227A + ROS + Isaac Sim → 实习 Figure/Tesla/1X/Skild |

---

## 💡 反思与批判

1. **「感知」与「认知」的边界在溶解**：传统 CS227A 是「看见物体」，但 PaLM-E/RT-2 后，感知模型直接输出动作 token——感知、规划、控制的分界被 foundation model 抹平。课程必须不断重画这条线。
2. **触觉被低估**：本项目特意放触觉通道，因为「**视觉解决 what，触觉解决 in-hand state**」——滑没滑、抓多紧、物体温度，视觉看不见。很多 demo 只用视觉是因为触觉硬件难，但这恰恰是真实抓取失败的主因。
3. **Sim-to-Real 的诚实**：仿真里 Diffusion Policy 漂亮，但真机摩擦、传感器噪声、标定误差会让成功率腰斩。课程若不强调域随机化与真机迭代，学生会产生「仿真=真实」的错觉。
4. **GraspNet 类基准的生态偏差**：抓取数据集几乎全是平行夹爪 + 桌面物体，灵巧手、可形变物（布、食物）、双臂协作严重欠采样——评估指标好看不代表泛化好。
5. **语言指令的歧义**：`_extract_target` 用关键词匹配，但「the red thing next to the cup」这种指代需要空间推理 + 对话澄清。当前 VLM 在此仍脆弱。
6. **foundation model 的成本与延迟**：PaLM-E/RT-2 推理慢、贵，真机闭环难。工业落地往往退回「小模型 + 好几何」。

---

## 🚀 扩展阅读

完成后推荐：
1. **CS237A** Principles of Robot Autonomy I（把感知接到运动规划）
2. **CS238** Decision Making under Uncertainty（感知不确定性 → POMDP）
3. **CS231A** Computer Vision: From 3D Reconstruction to Visual Recognition（几何侧深挖）
4. Stanford IP&A Lab / SAIL 论文清单（Bohg 组）
5. 工具栈：Open3D + PyTorch3D + Isaac Sim + ROS 2 + MuJoCo
6. 数据集：GraspNet-1Billion、Open X-Embodiment、YCB-Video

---

**对应代码**：`supplementary/grad_projects.py::cs227a_demo`（视觉+触觉+语言 多模态融合）
