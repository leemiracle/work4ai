# 00 · AI for Robotics 是什么

> **第一性问题**：机器人是 AI 的"**身体**"——让 AI 不只在屏幕里思考，而在真实世界行动。**2024 是机器人 AI 的"ImageNet 时刻"**：RT-2 / Octo / π₀ / GR00T 涌现。
>
> 与 [`讲透世界模型`](../../讲透世界模型/)（具身派）+ [`讲透RL`](../../讲透RL/) 联动。
>
> 配套：[`讲透世界模型`](../../讲透世界模型/) 具身派 + [`讲透RL`](../../讲透RL/) + [`讲透分布式AI系统`](../../讲透分布式AI系统/)

---

## 一、机器人为什么需要 AI

### 1.1 经典机器人 = 严格控制

- 工业机器人：固定程序 + 高精度
- 无法处理**未知环境**（家庭 / 户外 / 灾区）

### 1.2 莫拉维克悖论

- **下棋 / 解数学**（高级认知）→ AI 容易
- **抓杯子 / 走路 / 爬山**（感知运动）→ AI 极难

**需要 AI**：感知 + 决策 + 控制的统一。

### 1.3 数据稀缺

- 仿真数据多
- 真实数据少（遥控操作慢）
- **Sim2Real** gap

---

## 二、AI 在机器人的五大应用

### 2.1 视觉感知

- **深度估计**（MiDaS / Depth Anything）
- **物体检测**（YOLO / SAM）
- **场景理解**（CLIP / DINO + 场景图）

### 2.2 操作（Manipulation）

**代表**：
- **RT-2**（Google 2023）：VLM → 机器人 action
- **Open-X-Embodiment**（2023, 22 机构）：跨机器人数据集
- **RT-X**：跨 embodiment 通用 policy
- **Aloha / Mobile Aloha**（斯坦福 2024）：双臂精细操作
- **π₀**（Physical Intelligence 2024）：**flow matching 通用机器人基础模型**

### 2.3 移动（Locomotion）

- **四足**（ANYmal / Spot）：RL 学步态
- **人形**（Atlas / Tesla Optimus / Figure 01 / Unitree）
- **轮式 + 步行混合**

### 2.4 导航

- **SLAM** + 深度学习
- **自主驾驶**（详见 § 自动驾驶）

### 2.5 人机交互

- **LLM + 机器人**：自然语言指令
- "给我倒杯咖啡" → 机器人执行
- **Claude / GPT-4** 集成

---

## 三、机器人专属的方法学

### 3.1 Sim2Real

- **Isaac Sim**（NVIDIA）/ **MuJoCo** / **Habitat**
- **Domain Randomization**：仿真随机化 → 真实泛化
- **可微仿真**：端到端训练

### 3.2 模仿学习（IL）

- **BC**（Behavior Cloning）：从专家演示学
- **DAgger**：在线纠正
- **ACT**（Action Chunking Transformer）：Aloha 用

### 3.3 强化学习（RL）

- **PPO / SAC**：经典
- **Dreamer**（model-based RL）
- 详见 [`讲透RL`](../../讲透RL/)。

### 3.4 Foundation Models

- **VLM**（CLIP / ViLA）：视觉 + 语言
- **VLA**（Vision-Language-Action）：π₀ / RT-2
- **World Model**：具身派（[`讲透世界模型`](../../讲透世界模型/)）

### 3.5 硬件协同设计

- **Soft Robotics** + AI 控制
- **Tactile sensing**（触觉）
- AI 设计的硬件（[`讲透AIfor各学科/芯片设计`](../芯片设计/)）

---

## 四、当前前沿（2024-2026）

### 4.1 人形机器人爆发

- **Tesla Optimus Gen 2**（2024）
- **Figure 01 / 02**（2024，OpenAI 投资）
- **Unitree H1 / G1**（2024）
- **Boston Dynamics Atlas Electric**（2024）
- **1X NEO**（OpenAI 投资）

### 4.2 通用机器人 Foundation Model

- **π₀**（Physical Intelligence）：flow matching
- **GR00T**（NVIDIA）：人形基础模型
- **Octo**（Berkeley）：开源通用
- **OpenVLA**：开源 VLA

### 4.3 数据集 + Benchmark

- **Open-X-Embodiment**（22 机构）
- **DROID**（开放机器人数据）
- **Habitat 3.0**（仿真人形机器人）

### 4.4 LLM + 机器人

- **SayCan / PaLM-E / RT-2**
- 自然语言 → 任务规划 → 执行
- **RoboCodeX**（2024）

### 4.5 商业化

- **仓储机器人**（Amazon / Symbotic）
- **配送**（Nuro / Starship）
- **餐厅服务**（餐厅机器人）
- **家庭机器人**（仍远）

---

## 五、AI 改变了机器人的什么

### 5.1 通用性

- 经典：每任务一程序
- 现代：一个 model 跨任务（RT-X / π₀）

### 5.2 易用性

- LLM 让非专家能编程机器人
- "给我倒咖啡" → 机器人做

### 5.3 商业可行性

- 经典机器人 ROI 难（贵 + 不通用）
- AI 机器人：跨场景 = 经济性

### 5.4 安全 / 伦理

- **机器人伤害人类**（事故）
- **工作岗位替代**（蓝领）
- **军事机器人**（联合国讨论）

---

## 六、开放问题

1. **通用机器人何时到家用**？（5-10 年？）
2. **人形 vs 非人形**：哪种胜？
3. **Sim2Real gap 能完全解决吗**？
4. **机器人替代多少蓝领工作**？
5. **具身 AGI** 何时？
6. **机器人道德地位**？

---

## 七、一句话总结

> 🎯 **四句话**：
> 1. **2024 = 机器人 AI 的 ImageNet 时刻**——RT-2/π₀/GR00T/Figure 涌现。
> 2. **五大应用**：感知 / 操作（VLA）/ 移动 / 导航 / 人机交互（LLM）。
> 3. **方法学**：Sim2Real + 模仿学习 + RL + Foundation Model（VLA）。
> 4. **AI 让机器人通用化**——但**家用仍需 5-10 年**，伦理/安全是核心问题。

---

📌 **下一步**

1. **读**：RT-2 / π₀ / GR00T paper。
2. **和 [`讲透世界模型`](../../讲透世界模型/) 具身派 对照**。
3. **进入 [01 VLA 深挖](./)**（待补）。
