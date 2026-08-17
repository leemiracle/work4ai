# AWorld-RL 深读卡 —— 蚂蚁 Agent RL 算法集（数据闭环方向）

> **定位**：蚂蚁 inclusionAI 的 agentic RL 算法合集——**不是框架是配方集**：五大子系统各攻一个 agent 学习瓶颈，共享 AWorld Framework + verl 底座。
> **本地**：`~/ai/AWorld-RL`（184M，415 文件）｜**深读**：deepwiki 25 子页（2026-04-20 索引）

## 一、五大子系统（deepwiki 蒸馏）

| 子系统 | 攻什么瓶颈 | 核心机制 | 成果 |
|---|---|---|---|
| **FunReason-MT** | 多轮 Function Calling 数据生成难 | 三阶段管线：环境-API 图定向采样→Tooling Agent 抽象高级工具→Reasoning+Critiquing 迭代自纠环；HardGen 变体生成高难失败样本 | BFCL 数据合成 |
| **EnvTuning**（ICLR 2026）| SFT 过拟合 + RL 冷启动不稳 | **四阶段课程** + BFCL 模拟环境 + 细粒度进度奖励——"调环境而非调轨迹" | **400 样本**显著提升 BFCL V3 |
| **RAG-R1** | 深搜推理 | tag 协议 `<think>/<search>/<answer>` + **多查询并行**；KILT 语料 FAISS 索引检索服务器；SFT+PPO 双段 | 深搜 QA |
| **V2P**（Valley-to-Peak）| 视觉 GUI 定位 | 从"背景抑制"到"中心峰值"——免坐标的类人界面交互 | ScreenSpot 基准 |
| **StressWeb** | web agent 鲁棒性评测 | 扰动注入系统（布局混乱/弹窗干扰/语义冲突）| 对抗基准 |

另含 **RODS**（奖励驱动在线数据合成）：**进度奖励方差当零成本边界探测器**——奖励方差高=难度恰好在能力边界→多 agent 管线合成同构变体→动态 replay buffer 与策略共同进化。Qwen3-4B：静态数据 50.0 → EnvTuning 50.5 → **RODS 56.0**（BFCL）。

## 二、与本项目知识的对位

| AWorld-RL | 本项目 | 互证 |
|---|---|---|
| EnvTuning 四阶段课程 | exp_curriculum（3×3→5×5）| 讲透RL/09 课程学习的工业版 ✅ |
| RODS 奖励方差边界探测 | APO 效率塑形（全成功时造梯度）| "奖励信号设计决定优化方向"同款思想 |
| RAG-R1 tag 协议 | Search-R1 四特殊 token（PaperAgent §十）| 同源（Search-R1）✅ |
| StressWeb 扰动注入 | Prompt 稳健性 B 类扰动（手册04）| 评测侧同思想 |
| FunReason HardGen 失败样本 | rl_agent 必失败任务造 Reflexion | "失败是教材"双向 ✅ |

## 三、关键入口（本地验证）

```
FunReason-MT/    # 数据合成管线
EnvTuning/       # ICLR 2026 环境调优（四阶段课程脚本）
RAG-R1/          # 深搜（含独立 LICENSE）
RODS/            # 在线数据合成闭环
V2P/ StressWeb/  # 视觉定位 + 对抗基准
```

## 四、与"我们"的关系（一句话）

AWorld-RL 补的是生态最稀缺的**数据闭环**环节——我们的静态黄金集 + 5 起判分器 bug 教训，正需要 RODS 式"奖励方差找边界 + 在线合成变体"来升级（成熟度差距分析的差距⑥对应物）。

---
生成：2026-08-17 · deepwiki 索引 2026-04-20（2082e70）+ 本地 184M 克隆验证
