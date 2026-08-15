---
card_id: ROB-00
title: "讲透机器人：从控制论到具身智能"
universe: 讲透机器人
burke:
  scene: "物理世界充满摩擦、接触、噪声、延迟——比纯数字 AI 难得多"
  agent: "想让 AI 在真实世界行动的工程师"
  agency: "运动学/动力学/控制/感知/规划/VLA"
  act: "从'屏幕里的智能'到'物理世界的智能'"
  purpose: "理解机器人=物理世界的 Agent，做能动的 AI"
tension: "Moravec 悖论：对 AI 难的（下棋/数学）对人容易；对人容易的（走路/抓取）对 AI 极难"
arc: [直觉, 数学, 代码, 不足, 应用]
status: in_progress
next_card: ROB-01
refs:
  - "Wiener, 控制论 Cybernetics, 1948（中译本商务印书馆）"
  - "Moravec, Mind Children, 1988（悖论提出）"
  - "Siciliano 等《机器人学：建模、规划与控制》中文版（西安交大出版社）"
  - "Lynch & Park, Modern Robotics（在线免费英文 + 中文翻译）"
  - "Brunton《数据驱动的科学与工程》中文版"
updated: 2026-08-14
---

# 🤖 讲透机器人：从控制论到具身智能

> **User Story**：作为一个想让 AI 真正「动起来」的工程师，我想从物理/数学一路看到 2024-2026 的人形机器人浪潮，以便做能与世界交互的 AI。

## 🎭 戏剧张力（Moravec 悖论）

Hans Moravec 1988 年提出一个反直觉的观察：

> **对 AI 难的事（下棋、数学、写代码），对人容易；对人容易的事（走路、抓取、辨认物体），对 AI 极难。**

为什么？因为运动/感知是**亿万年进化深度优化的能力**——它们感觉「毫不费力」恰恰是因为大脑把它们全压到潜意识里了。下棋是文化发明（几千年），走路是生物发明（几亿年）。

整部「讲透机器人」在追踪：**怎么让 AI 学会亿万年进化打磨的能力？** 这比让 AI 学会下棋难 1000 倍，也更有价值（物理世界 >> 数字世界）。

## 📚 五幕总览

| 幕 | 文件 | 一句话 |
|---|---|---|
| 直觉 | `01-直觉-机器人即物理Agent.md` | 感知-决策-行动闭环；控制论；为什么物理这么难 |
| 数学 | `02-数学-运动学动力学控制.md` | DH/POE 运动学；拉格朗日动力学；PID/LQR/MPC；SE(3) 李群 |
| 代码 | `03-代码-最小IK+LQR+MPC.md` | 2 连杆臂逆运动学 + 倒立摆 LQR + MPC 简化版 |
| 不足 | `04-不足-Sim2Real与接触.md` | 仿真-现实差距、接触不确定、安全、数据稀缺 |
| 应用 | `05-应用-人形机器人浪潮.md` | VLA、Figure/Optimus/宇树/智元、Diffusion Policy |

## 🗺️ 2024-2026 机器人浪潮（重点关注中国公司）

| 类别 | 国际 | 中国（可访问官网/资料）|
|---|---|---|
| **人形机器人** | Figure 02、特斯拉 Optimus、1X、Apptronik | **宇树** Unitree H1/G1、**智元** AgiBot 远征、**傅利叶** GR-1、**星动纪元**、**银河通用**、**小鹏** PX5、**追觅** |
| **VLA 模型** | RT-2(Google)、OpenVLA、π0(Physical Intelligence)、RDT | **清华** RoboFlamingo、**上交** OpenVLA-OSS、**银河通用** Gaia-1 |
| **学习范式** | Diffusion Policy、ACT、ALOHA、Mobile ALOHA | **北大**、**港科大** RAM 实验室、**港中文** MMLab |
| **数据集** | Open X-Embodiment、DROID | **上海 AI Lab** OpenRoBERTA、**银河通用** |
| **仿真** | Isaac Sim/Lab(NVIDIA)、MuJoCo、Sapien | **上交** MVIG、**清华** MARS、**商汤** |

## 🇨🇳 中国大陆可访问资源清单（替代映射表）

这是本宇宙的特色——所有引用避开墙外资源，改用可访问替代：

| 国际资源（墙外） | 中国可访问替代 |
|---|---|
| Wikipedia 英文 | 知乎专栏 / 中文维基 / 教材中文版 |
| Stanford Encyclopedia | 国内哲学课程 / 教材 |
| Google Scholar | **百度学术** / **Semantic Scholar** / **必应学术** |
| Lil'Log / Distill.pub | **机器之心** jiqizhixin.com / **量子位** qbitai.com |
| Twitter/X (AK 等) | 机器之心 / 量子位 / 知乎 |
| Coursera / edX | **B 站** bilibili.com / **中国大学 MOOC** icourse163.org / **深蓝学院** |
| ROS 英文 wiki | **古月居** guyuehome.com（ROS 中文社区）|
| Modern Robotics (Lynch) | 在线免费英文版 + B 站中文讲解 + 深蓝学院课 |
| Siciliano《机器人学》| 中文版（西安交大出版社）|
| Sutton《RL》| 中文版《强化学习：原理与应用》|
| arXiv | **arXiv.org**（基本可访问）+ **Papers with Code** + **百度学术镜像** |
| GitHub（慢）| **Gitee** 镜像 / **GitCode** / **Csdn download** |
| Hugging Face | **魔搭** ModelScope（阿里）/ **启智** OpenI（鹏城实验室）|

## 🔗 与其他宇宙的连接

- **`讲透复杂系统/`**：机器人是复杂系统（多体动力学、相变、感知-行动闭环）
- **`讲透世界模型/`**：机器人需要世界模型（model-based RL、VLA 的「世界」）
- **`讲透CV/` `讲透多模态/`**：VLA = 视觉 + 语言 + 动作
- **`讲透学习型Agent/`**：模仿学习/RL 是 robot learning 的核心
- **`复杂系统迭代work4ai.md`**：机器人 sim-to-real = 复杂系统鲁棒性



## 📖 推荐入门路径（中国可访问）

1. **基础理论**：深蓝学院《机器人运动学》《视觉 SLAM》（B 站有免费片段）
2. **现代教材**：Lynch & Park《Modern Robotics》在线免费版 + 中文讲解
3. **SLAM**：高翔《视觉 SLAM 十四讲》（国内经典，可购买/B 站配套）
4. **强化学习**：Sutton 中文版 + 王树森 B 站课
5. **ROS**：古月居《ROS 机器人开发实践》
6. **前沿追踪**：机器之心 + 量子位 + 知乎「机器人」话题

📌 **下一张卡** → `01-直觉-机器人即物理Agent.md`
