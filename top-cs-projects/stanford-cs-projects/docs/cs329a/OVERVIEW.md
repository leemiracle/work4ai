# CS329A: Self-Improving AI Agents

> Stanford University, Autumn 2025
> Instructors: **Aakanksha Chowdhery** (PaLM 一作) + **Azalia Mirhoseini** (DeepMind)
> Time: Mon/Fri 4:30-5:50 PM, Skilling Auditorium
> Difficulty: ⭐⭐⭐⭐⭐ (研究生研讨课，最前沿)

---

## 📚 课程定位

**全球首门系统讲授"AI Agent 自我改进"的研究生课**。覆盖 2024-2025 年散落在顶会的关键论文，按时间尺度组织：

1. **In-context（毫秒级）**: test-time scaling
2. **Episode（分钟-小时）**: memory + RAG
3. **参数级（天-周）**: STaR / DAPO / RLEF

---

## 🎯 学习目标

1. **理解** "self-improvement" 的 3 个时间尺度
2. **掌握** Test-time compute scaling（Snell / Brown / Archon）
3. **实现** Process Reward Model（PRM, Lightman 2023）
4. **批判** Generation-Verification Gap
5. **掌握** STaR bootstrap + GRPO / DAPO
6. **了解** AlphaEvolve / The AI Scientist (open-ended evolution)

---

## 📅 完整模块（20 讲）

### L1 (Mon Sep 22): Course Overview
### L2 (Fri Sep 26): Test-Time Compute Scaling
- **Brown et al. 2024** "Large Language Monkeys" — repeated sampling
- **Archon** (Saad-Falcon 2024) — inference-time 架构搜索
- 🔴 **Snell et al. 2024** "Scaling LLM Test-Time Compute Optimally"

### L3 (Mon Sep 29): Robust Verification
- 🔴 **Cobbe et al. 2021** "Training Verifiers" (GSM8K)
- 🔴 **Lightman et al. 2023** "Let's Verify Step by Step" (PRM800K)
- **Math-Shepherd** (Wang 2023) — 自动 step-level 标注

### L4 (Fri Oct 3): Learning from Feedback (Tools/Code)
- **ReAct** (Yao 2022) — agent 鼻祖
- **RLEF** (2024) — RL + execution feedback
- **Constitutional AI** (Bai 2022) — RLAIF

### L5 (Mon Oct 6): Multi-Step Reasoning/Planning
- **SWiRL** (2025) — synthetic data + multi-step RL
- **LATS** (Zhou 2023) — MCTS for LLM
- **SPRINT** (2025) — interleaved planning + parallel execution
- **ADaPT** (Prasad 2024) — as-needed decomposition

### L6 (Fri Oct 10): Train-Time Scaling with RL ⭐
- 🔴 **STaR** (Zelikman 2022) — bootstrap reasoning
- 🔴 **DeepSeekMath** (2024) — GRPO
- 🔴 **DAPO** (2025) — 工业级 RL 系统

### L7 (Mon Oct 13): Open-Ended Evolution
- **Automated Design of Agentic Systems** (2025) — meta-agent
- **The AI Scientist** (Lu 2024) — 全自动科研
- **AlphaEvolve** (DeepMind 2025) — Gemini 进化算法

### L8 (Fri Oct 17): Search & Deep Research Agents
- **AlphaCode / AlphaCode 2** — 竞赛级编程
- **Search-o1** (2025) — agentic search + reasoning

### L9 (Mon Oct 20): 🎤 Melvin Johnson (DeepMind)
- "Evolution of Post-training from Chatbots to Agents"

### L13 (Mon Nov 3): Agentic Frameworks for SE
- **CodeMonkeys** (2025) — SE test-time compute
- **KernelBench** (2025) — LLM 写 GPU kernel
- **LLM Optimizers via Agent-System Interfaces**

### L14 (Fri Nov 7): Memory-Augmented Agents
- **Cartridges** (2025) — self-study 长上下文
- **MemGPT** (Packer 2023)
- **CacheBlend** — RAG KV cache 复用

### L15 (Mon Nov 10): 🎤 Denny Zhou (DeepMind) — LLM Reasoning
### L16 (Fri Nov 14): 🎤 Thang Luong (DeepMind)
- "AlphaProof, AlphaGeometry & Gemini IMO Gold"

### L17 (Mon Nov 17): Agentic Evaluations
- **METR** "Measuring AI Ability to Complete Long Tasks"
- **GDPVal** — 经济价值评估
- **DeepScholar-Bench**

### L18 (Fri Nov 21): 🎤 Misha Laskin (Reflection AI)
- "Building Agentic Systems for Autonomy"

### L19 (Mon Dec 1): 🎤 Danny Driess (Physical Intelligence)
- "Multimodal AI Agents in Robotics"

### L20 (Fri Dec 5): Future Research Areas

---

## 🧮 核心算法

### STaR (Zelikman 2022)
```
1. 对每个问题 q 生成 reasoning r + answer a
2. 验证 a == ground_truth
3. 成功: 加入训练集 (q, r)
   失败: 给 hint (ground_truth) → rationalize → 加入训练集
4. SFT 在收集的数据上
5. 重复
```

**数学**:
$$\pi_{n+1} = \text{SFT}(\pi_n, \{(q, r) : r \sim \pi_n(\cdot | q), \text{extract}(r) = a^*\})$$

### GRPO (DeepSeek)
取消 critic，用 group-relative baseline：
$$A_i = \frac{r_i - \text{mean}(r_{1..G})}{\text{std}(r_{1..G})}$$

其中 $G$ 是同一 query 的 $G$ 个采样。**比 PPO 省一半显存**（无 critic）。

### AlphaEvolve
```
population = [random algorithms]
while not converged:
    parent = select(population)
    child = LLM.mutate(parent)
    fitness = evaluate(child)
    if fitness > parent.fitness:
        population.add(child)
```

---

## 💻 项目代码

📁 `topic2-agent-v2/hw3_self_improve_coding.py::STaRAgent`

**实现**:
1. ✅ 推理生成（mock）
2. ✅ Ground truth 验证
3. ✅ Rationalization（带 hint 反推）
4. ✅ 训练数据累积
5. ✅ 多轮迭代 + 性能追踪

### 运行
```bash
cd topic2-agent-v2
python3 hw3_self_improve_coding.py
# STaR 部分
```

**输出**:
```
🌟 STaR 迭代 1
   样本: 10
   成功: 10 (100.0%)

📊 STaR 训练曲线:
Iter Success Rate
   1       100.0% ██████████████████████████████
   2        90.0% ███████████████████████████
   3        90.0% ███████████████████████████
```

---

## 🎤 嘉宾阵容（2025 年最豪华）

| 嘉宾 | 所属 | 主题 |
|------|------|------|
| Melvin Johnson | DeepMind | Post-training 演化 |
| Denny Zhou | DeepMind | LLM Reasoning |
| Thang Luong | DeepMind | AlphaProof / IMO |
| Junchen Jiang | LMCache / UChicago | Memory & KV |
| Misha Laskin | Reflection AI | Autonomous agents |
| Danny Driess | Physical Intelligence | 机器人 Agent |

---

## 📊 评分

| 部分 | 占比 |
|------|------|
| Homework 1-3 | 50% |
| Project Proposal | 2.5% |
| Midterm Presentation + Report | 10% |
| Final Project | 35% |
| Poster | 2.5% |

**Late policy**: 4 free late days, 每次 ≤2 天，最后项目不可晚交。

---

## 🎯 学习路径

| 角色 | 推荐 |
|------|------|
| **想做 PhD** | CS329A 必修（研究导向）|
| **想做 reasoning model** | L2-L6 (核心数学) |
| **想做 agent eval** | L17 + CS329Z HW3 |
| **想做机器人** | L19 + CS237A |

---

## 💡 批判性观察

1. **过度 DeepMind 视角** — 6 位嘉宾 5 位 DeepMind 系
2. **缺少 OpenAI o1/R1 训练细节** — 工业秘密
3. **没有自我改进失败模式系统讨论** — self-distillation collapse, reward hacking
4. **评估偏少**（1 节课）— 但 agent eval 是当前最缺

---

**最后更新**: 2026-08-11
**对应代码**: `topic2-agent-v2/hw3_self_improve_coding.py`
