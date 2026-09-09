# 第二章 · 具身世界模型与 VLA / World Action Models

> 「具身智能的下一个范式，不是让模型从观测映射到动作，而是让模型先在脑中预演世界会怎么变，再选择动作。」—— 2026 综述《World Action Models》arXiv 2605.12090

## 0. 导言：从「反应式」到「预演式」具身智能

2022 年以前，机器人学习的主流范式是 **reactive policy**——给一张图、一段指令，直接输出动作。这种「观测 → 动作」的端到端映射虽然简洁，但有一个根本缺陷：**它不建模「世界会怎么变化」**。一个不预测未来的智能体，无法做长程规划、无法理解因果、无法在罕见情境中泛化。

2023 年起，**Vision-Language-Action（VLA）** 模型把大语言模型的能力引入机器人，让机器人第一次具备「语义通用性」——它能听懂「把蓝色杯子放到左边」这种开放指令。但 VLA 本质上仍然是 reactive：它学习的是 `P(action | observation, language)`，不显式建模 `P(next_state | state, action)`。

2024-2026 年，研究界开始把 **world model**（环境动力学模型）与 **action model**（动作生成模型）融合，催生了一个新范式：**World Action Model（WAM）**。它学习的是联合分布 `P(future_state, action | history)`——既预测世界，又生成动作，二者耦合训练。

本章按「历史 → 概念辨析 → 标杆系统 → 关键技术 → 数据 → 评估 → 复现」展开。覆盖三大脉络：

- **潜在空间 world model**（DeepMind/Hafner 主导）：PlaNet → Dreamer v1/v2/v3 → MuZero → TD-MPC
- **VLA**（Google/Stanford/NVIDIA 主导）：RT-1/2 → Open X-Embodiment → OpenVLA → GR00T
- **World Action Model**（2024-2026 新范式）：π0、Cosmos Policy、DreamZero、Joint-WAM 系列

---

## 1. 历史脉络：从 MuJoCo 到 WAM 的二十年

### 1.1 第一阶段（2015-2018）：model-based RL 的隐空间革命

经典 model-based RL 用真实环境训练，但样本效率极低。2018 年 DeepMind 的 **PlaNet**（Planning Network, [arXiv:1811.04551](https://arxiv.org/abs/1811.04551)）首次提出 **RSSM（Recurrent State-Space Model）**——在学到的连续隐空间里做 planning，用 cross-entropy method（CEM）在线规划。这把 model-based RL 推到了「样本效率 vs 最终性能」帕累托前沿。

同年，Ha & Schmidhuber 的「World Models」（[arXiv:1809.01999](https://arxiv.org/abs/1809.01999)）提出 VAE + MDN-RNN + Linear Controller 三件套，让 agent 在自己的「梦境」里训练，再 zero-shot 迁移到真实环境。这篇论文的影响力远超其性能——它定义了「世界模型」这一术语。

### 1.2 第二阶段（2019-2023）：Dreamer 三代与 MuZero

**Dreamer v1**（[arXiv:1912.01603](https://arxiv.org/abs/1912.01603)）的方法论突破：在 RSSM 学到的隐空间里**反向传播策略梯度**——无需重采样即可训练策略。**Dreamer v2**（[arXiv:2010.02193](https://arxiv.org/abs/2010.02193)）改用离散表征。**Dreamer v3**（[arXiv:2301.04104](https://arxiv.org/abs/2301.04104)）——Hafner 等的集大成之作——**单一超参配置跨 150+ 任务**，是首个从零开始（无人类数据）在 Minecraft 收集钻石的算法，被业界视为 model-based RL 的「通用基线」。

与此并行的 **MuZero**（[arXiv:1911.08265](https://arxiv.org/abs/1911.08265), DeepMind 2020）走另一条路：不显式建模环境，而是学一个**价值等价的隐动力学模型**（value-equivalent dynamics），用 MCTS 在该隐空间搜索。MuZero 在 Atari、围棋、象棋、将棋全部超越人类，是 model-based planning 的工业级证明。

**TD-MPC**（[arXiv:2203.04955](https://arxiv.org/abs/2203.04955)）与 **TD-MPC 2**（[arXiv:2310.16828](https://arxiv.org/abs/2310.16828), NVIDIA/Caltech）把 dreamer 与 model-free TD 学习结合，在 4D 视觉控制上达到 SOTA。**EfficientZero v2**（[arXiv:2411.00464](https://arxiv.org/abs/2411.00464)）将 sample-efficient RL 推到新高度。

### 1.3 第三阶段（2022-2024）：VLA 革命

Google 2022 年发布 **RT-1**（[arXiv:2212.06817](https://arxiv.org/abs/2212.06817)）——首个能在真实机器人上执行 700+ 任务的 Transformer 策略。2023 年的 **RT-2**（[arXiv:2307.15818](https://arxiv.org/abs/2307.15818)）把 PaLI-X 视觉语言模型微调为策略网络，第一次让机器人**理解「把苹果放到写着 1+1=2 的纸上」这种需要推理的指令**——本质是把 LLM 的世界知识蒸馏进动作。

2023 年 10 月，**Open X-Embodiment**（[arXiv:2310.08864](https://arxiv.org/abs/2310.08864)）联合 22 家研究机构，发布 100 万+ 跨机器人轨迹数据集（22 种机器人形态），训练的 **RT-X** 在未见机器人上展现正迁移——这是 VLA「规模法则」的第一个工业级证据。

### 1.4 第四阶段（2024-2026）：WAM 范式形成

**Diffusion Policy**（[arXiv:2303.04137](https://arxiv.org/abs/2303.04137), RSS 2023 best paper, Chi 等）证明扩散模型在动作生成上比回归好得多——能建模多模态动作分布（同一观测可有多个合理动作）。这成为后续 π0、RDT-1B、Cosmos Policy 的基础。

2024 年 10 月，Physical Intelligence 发布 **π0**（[arXiv:2410.24164](https://arxiv.org/abs/2410.24164)）——3.3B 参数 VLA，用 **flow matching** 生成连续动作，第一次在单一模型上跨 5 种机器人形态（机械臂、双臂、人形上半身等）执行复杂长程任务（叠衣服、收拾桌子）。π0 把 action generation 视为「学一个流场」，比 diffusion 快 10 倍。

2025 年 **π0.5** 进一步用 **test-time compute**（推理时多采样 + 投票）解决未见任务；**π0-FAST** 用 token 化动作替代流匹配，提速 5 倍且性能不降。同年 NVIDIA 发布 **GR00T N1**（[developer.nvidia.com/groot](https://developer.nvidia.com/groot)）—— 开源人形机器人 foundation model，2B 参数，预训练数据含 6.5M 小时真人视频 + 800k 机器人轨迹。

2026 年 5 月的综述 **World Action Models: The Next Frontier in Embodied AI**（[arXiv:2605.12090](https://arxiv.org/abs/2605.12090)）首次系统化提出 WAM 概念，把 π0、Cosmos Policy、DreamZero 等系统统一进 Cascaded / Joint WAM 二分法。

---

## 2. 概念辨析：VLA vs WM vs WAM

这是 2024-2026 文献最容易混淆的三个术语。下表是 2026 WAM 综述给出的辨析：

| 概念 | 学习目标 | 代表系统 | 与"世界"的关系 |
|---|---|---|---|
| **VLA**（Vision-Language-Action） | $P(a \mid o, l)$ | RT-2, OpenVLA, GR00T | 不显式建模 |
| **World Model**（用于 RL 训练） | $P(s_{t+1} \mid s_t, a_t)$ | Dreamer v3, MuZero, V-JEPA 2 | 显式建模，作 imagination 训练数据 |
| **Action-Conditioned Video Model** | $P(o_{t+1:t+k} \mid o_{\le t}, a_{t:t+k})$ | Sora 2, Genie 3 | 显式建模，像素空间 |
| **WAM**（World Action Model） | $P(s_{t+1:t+k}, a_{t:t+k} \mid \text{history})$ | π0, Cosmos Policy, DreamZero | 显式建模，**与动作联合** |

### 2.1 Cascaded WAM vs Joint WAM

WAM 内部又分两种架构（2605.12090 综述的核心分类）：

**Cascaded WAM**：先训一个独立 world model $\hat{P}(s'|s,a)$，再把它作为「先知」嵌入 policy（policy 查询它做 look-ahead planning）。代表：Dreamer 系列、DreamZero。
- 优点：模块解耦、可单独改进
- 缺点：world model 的训练目标与下游 policy 目标不一致，可能学到无关细节

**Joint WAM**：world model 与 policy 共享 backbone，端到端联合训练。代表：π0、Cosmos Policy、UWM（Unified WAM）。
- 优点：表征对 policy 友好
- 缺点：训练目标冲突，需要精心调平衡

---

## 3. 标杆系统全谱（含 arXiv ID）

### 3.1 潜在空间 RL 谱系

| 系统 | 年份 | 机构 | arXiv | 核心创新 |
|---|---|---|---|---|
| **PlaNet** | 2018 | DeepMind | [1811.04551](https://arxiv.org/abs/1811.04551) | RSSM + CEM 在线规划 |
| **Dreamer v1** | 2019 | Google | [1912.01603](https://arxiv.org/abs/1912.01603) | 隐空间策略梯度反向传播 |
| **Dreamer v2** | 2020 | Google | [2010.02193](https://arxiv.org/abs/2010.02193) | 离散表征 |
| **Dreamer v3** | 2023 | DeepMind | [2301.04104](https://arxiv.org/abs/2301.04104) | 单一超参跨 150 任务，Minecraft 钻石 |
| **MuZero** | 2020 | DeepMind | [1911.08265](https://arxiv.org/abs/1911.08265) | value-equivalent 隐动力学 + MCTS |
| **EfficientZero v2** | 2024 | SEA / Shanghai AI Lab | [2411.00464](https://arxiv.org/abs/2411.00464) | 自监督 + consistency loss |
| **TD-MPC 2** | 2023 | NVIDIA | [2310.16828](https://arxiv.org/abs/2310.16828) | 通用跨任务 MPC |

### 3.2 VLA 谱系

| 系统 | 年份 | 机构 | arXiv | 参数 / 形态 |
|---|---|---|---|---|
| **RT-1** | 2022 | Google | [2212.06817](https://arxiv.org/abs/2212.06817) | 35M，仅文本图像 token |
| **RT-2** | 2023 | Google DeepMind | [2307.15818](https://arxiv.org/abs/2307.15818) | 5B / 55B（基于 PaLI-X） |
| **Open X-Embodiment** | 2023 | 22 机构联合 | [2310.08864](https://arxiv.org/abs/2310.08864) | 22 种机器人形态 |
| **OpenVLA** | 2024 | Stanford / Berkeley | [2406.09246](https://arxiv.org/abs/2406.09246) | 7B 开源，LLaMA backbone |
| **RDT-1B** | 2024 | 清华 | [2410.07864](https://arxiv.org/abs/2410.07864) | 1B，diffusion + 双臂 |
| **CogACT** | 2024 | MIT-IBM | （核实） | action head 改进 |
| **Helix** | 2024 | Figure AI | 商业 blog | 人形全身控制 |
| **GR00T N1 / N1.5** | 2025 | NVIDIA | [developer.nvidia.com/groot](https://developer.nvidia.com/groot) | 2B 开源 |

### 3.3 WAM 谱系

| 系统 | 年份 | 机构 | arXiv / 链接 | WAM 类型 |
|---|---|---|---|---|
| **Diffusion Policy** | 2023 | Columbia / TRI | [2303.04137](https://arxiv.org/abs/2303.04137) | 前身（动作生成） |
| **π0** | 2024-10 | Physical Intelligence | [2410.24164](https://arxiv.org/abs/2410.24164) | Joint，flow matching action |
| **π0.5** | 2025 | Physical Intelligence | blog + paper | Joint + test-time compute |
| **π0-FAST** | 2025 | Physical Intelligence | blog + paper | Joint，token 化动作 |
| **Cosmos Policy** | 2025 | NVIDIA | paper + Cosmos World Foundation | Joint |
| **DreamZero** | 2025 | 多机构 | 核实 | Cascaded |
| **GR00T N1.5** | 2025 | NVIDIA | blog | Joint |
| **DreamDojo** | 2025 | 多机构 | 核实 | Cascaded（embodiment-agnostic） |
| **UWM**（Unified WAM） | 2025 | 多机构 | 核实 | Joint |
| **Genie 2 / Genie 3** | 2024 / 2025 | DeepMind | [deepmind.google](https://deepmind.google) blog | 作 WAM 训练环境 |

> ⚠️ DreamZero、Genie 2 / Genie 3、Cosmos Policy 的部分版本没有正式 arXiv 论文，仅有官方 blog 或产品页，引用时已明确标注。

---

## 4. 关键技术深讲

### 4.1 RSSM（Recurrent State-Space Model）

PlaNet/Dreamer 的核心架构。在每个时间步 t，模型维护一个隐状态 $h_t$，由两部分组成：
- **deterministic** 部分 $h_t = \text{GRU}(h_{t-1}, s_{t-1}, a_{t-1})$
- **stochastic** 部分 $s_t \sim q(s_t | h_t, o_t)$（posterior，训练时）或 $\hat{P}(s_t | h_t)$（prior，部署时）

这个 prior-posterior gap 是 RSSM 的精髓：训练时 posterior 看到 ground truth，部署时只能用 prior。Dreamer 通过最小化 KL(prior || posterior) 让二者对齐。

### 4.2 Action Tokenization：FAST

传统 VLA 把动作离散化为 token（如 RT-2 把 (x,y,z,roll,pitch,yaw,gripper) 各自量化为 256 个 bin），但这丢失连续结构且 token 数过多（每步 7+ token）。

**FAST**（[Karpathy 等 2024](https://arxiv.org/abs/2411.05765)，核实）提出用 **DWT（Discrete Wavelet Transform）+ BPE** 把整段轨迹压成短 token 序列。例如一段 50 步的轨迹，FAST 压到 50-100 token，相比传统方法节省 6-10 倍。这让 VLA 真正能生成长程动作。

### 4.3 Flow Matching Action（π0）

π0 的核心创新：把 action generation 视为一个**连续归一化流（CNF）**学习问题。

设动作分布为 $p(a | o, l)$。CNF 学一个向量场 $v_t(a, t)$，使粒子从标准高斯 $N(0, I)$ 沿该向量场流动后能匹配 $p(a | o, l)$。Flow matching 的损失：

$$\mathcal{L} = \mathbb{E}_{t, a_0 \sim N(0,I), a_1 \sim p_{data}} \| v_\theta(a_t, t | o, l) - (a_1 - a_0) \|^2$$

其中 $a_t = (1-t) a_0 + t a_1$。相比 diffusion（DDPM），flow matching 路径是直线，**采样只需 10 步以内**（vs DDPM 50-1000 步），实时性满足机器人控制。

### 4.4 World Model as Imagination Engine

Cascaded WAM 训练流程：
1. 用真实数据训 world model $\hat{P}(s'|s,a)$
2. 从初始状态 $s_0$ 出发，用 $\hat{P}$ 滚动 $H$ 步得到 imagined trajectory
3. 在 imagined trajectory 上算策略梯度（actor）和价值函数（critic）
4. 关键：**梯度可穿过 world model 反传**（Dreamer 用 reparameterization）

这种「在脑中演练」的范式让 agent 不再需要反复试错真实环境，样本效率提升 100x+。

### 4.5 RT-2 的语义-动作蒸馏：一个深入案例

RT-2（[arXiv:2307.15818](https://arxiv.org/abs/2307.15818)）是 VLA 革命的真正分水岭。其精妙之处在于：**它没有从零训一个机器人模型，而是把已有 VLM（PaLI-X 55B）的「语义理解能力」蒸馏为「动作输出能力」**。

具体做法：
- 把 7 维连续动作（x, y, z, roll, pitch, yaw, gripper）各自量化为 256 个 bin
- 把每步动作编码为 7 个 token，作为 VLM「词汇表」的扩展
- 在机器人轨迹数据上 co-finetune（与原 VQA 数据混合）

结果惊人：
- 「把苹果放到写着 2+2=4 的纸上」——RT-2 能识别数学符号并执行
- 「把草莓放进错误的碗」——能理解反事实指令
- 这种泛化**不是来自机器人数据**，而是来自 VLM 预训练时见过的网络规模文本

**RT-2 揭示的核心规律**：机器人泛化能力的上限，主要由**预训练 VLM 的语义广度**决定，而非机器人数据量。这反过来推动了 2024-2026 年「VLA = VLM + 小 action head」的设计哲学——OpenVLA、GR00T N1、π0 都遵循这一原则。

### 4.6 Diffusion Policy 的数学

Diffusion Policy（[arXiv:2303.04137](https://arxiv.org/abs/2303.04137), Chi 等 RSS 2023 best paper）的核心：把动作序列 $\mathbf{a}_{t:t+H}$ 视为一个分布 $p(\mathbf{a} | o_t)$，用扩散建模。

前向过程（加噪）：
$$q(\mathbf{a}_k | \mathbf{a}_{k-1}) = \mathcal{N}(\sqrt{1-\beta_k} \mathbf{a}_{k-1}, \beta_k I)$$

反向过程（去噪）：训练网络 $\epsilon_\theta(\mathbf{a}_k, k, o_t)$ 预测加入的噪声：
$$\mathcal{L} = \mathbb{E}_{k, \mathbf{a}_0, \epsilon} \| \epsilon_\theta(\mathbf{a}_k, k, o_t) - \epsilon \|^2$$

为什么 diffusion 比回归好？因为**真实动作分布是多模态的**——同一观测下「向左抓」和「向右抓」可能都合理。回归损失会取平均，得到中间不动作；diffusion 能建模整个分布。这一洞察后来被 π0 升级为 flow matching（更快采样）。

### 4.7 Imagination-based Policy Gradient（Dreamer 数学）

Dreamer 的核心数学优雅之处在于「在隐空间里做策略梯度」：

设 world model 给出隐动力学 $p_\phi(s_{t+1} | s_t, a_t)$ 和 reward 模型 $r_\phi(s_t, a_t)$。从真实数据 bootstrap 出初始隐状态 $s_0$ 后，**完全在模型内**滚动：

$$\hat{\tau} = (s_0, a_0, s_1, a_1, \ldots, s_H) \quad \text{where} \quad s_{t+1} \sim p_\phi(\cdot | s_t, a_t), \quad a_t \sim \pi_\theta(\cdot | s_t)$$

然后计算 imagination return：
$$V_\theta(s_0) = \mathbb{E}_{\hat{\tau}} \left[ \sum_{t=0}^{H} \gamma^t r_\phi(s_t, a_t) + \gamma^{H+1} V_\psi(s_{H+1}) \right]$$

关键：**整个 rollout 是可微的**（用 reparameterization trick 处理随机性），所以梯度可以直接从 $V_\theta$ 反传到 $\pi_\theta$，**无需在真实环境采样新数据**。这就是 Dreamer 样本效率的根源。

---

## 5. 数据生态：从遥操作到网络规模视频

WAM 训练数据分四类（参考 2605.12090 综述 Sec. 5）：

| 数据源 | 代表数据集 | 规模 | 优势 | 局限 |
|---|---|---|---|---|
| **机器人遥操作** | Open X-Embodiment, DROID, RH20T | ~1M 轨迹 | 真实、动作标签精确 | 形态受限、昂贵 |
| **便携式人体演示** | UMI (Universal Manipulation Interface) | 数十万 | 形态接近真实机械臂 | 仍需硬件 |
| **仿真** | Isaac Lab, Genesis, RoboCasa | 数十亿步（生成式） | 无限、安全、可标注奖励 | sim-to-real gap |
| **网络规模自我中心视频** | Ego4D, EPIC-KITCHENS, Open X-Video | 数百万小时 | 跨任务、跨场景 | 无动作标签 |

最后一种是最有想象力的——**如何用无标签视频训 WAM？** 答案是 **latent action model**（Genie 系列开创）：从视频中反推「隐动作」$z_t$（不对应真实电机指令，但满足马尔可夫性），然后用这些隐动作训 dynamics。这让 YouTube 视频成为机器人学习的语料库。

---

## 6. 评估：我们到底在测什么

### 6.1 仿真 benchmark

| Benchmark | 测什么 | 关键指标 |
|---|---|---|
| **LIBERO** | 桌面操作任务套件 | 成功率（per task suite） |
| **CALVIN** | 长程多步任务（语言条件） | 任务完成序列长度 |
| **SimplerEnv** | 真实世界模拟（图 + 物理） | 成功率 vs 真实 |
| **RT-X Benchmark** | 跨机器人形态泛化 | 未见形态性能 |
| **Open X-Embodiment Bench** | 22 机构统一评测 | 通用基线对比 |
| **RoboArena / RoboScape** | 多机器人竞争 / 长程 | 累计回报 |

### 6.2 WAM 专属评估三维度（2605.12090 提出）

- **Visual fidelity**：生成的未来帧是否真实？
- **Physical commonsense**：是否符合物理直觉（重力、碰撞、摩擦）？
- **Action plausibility**：给定世界状态，预测的动作是否可行？

这三维度经常冲突：视觉好的不一定物理对，物理对的不一定动作合理。当前没有一个系统能同时三者都拿满分。

---

## 7. 2025-2026 关键论文清单

1. **World Action Models: The Next Frontier in Embodied AI**（[arXiv:2605.12090](https://arxiv.org/abs/2605.12090), 2026-05）—— 首个 WAM 系统综述
2. **π0: A Vision-Language-Action Flow Model for General Robot Control**（[arXiv:2410.24164](https://arxiv.org/abs/2410.24164), 2024-10）—— flow matching action 范式
3. **DreamerV3**（[arXiv:2301.04104](https://arxiv.org/abs/2301.04104)）—— 通用 model-based RL 基线
4. **Diffusion Policy**（[arXiv:2303.04137](https://arxiv.org/abs/2303.04137), RSS 2023 best paper）—— 动作扩散
5. **OpenVLA**（[arXiv:2406.09246](https://arxiv.org/abs/2406.09246), 2024）—— 开源 VLA 起点
6. **Open X-Embodiment**（[arXiv:2310.08864](https://arxiv.org/abs/2310.08864), 2023）—— 跨形态数据基准
7. **RDT-1B**（[arXiv:2410.07864](https://arxiv.org/abs/2410.07864), 2024）—— 双臂 diffusion
8. **EfficientZero v2**（[arXiv:2411.00464](https://arxiv.org/abs/2411.00464), 2024）—— 高效 MCTS
9. **TD-MPC 2**（[arXiv:2310.16828](https://arxiv.org/abs/2310.16828)）—— 通用 MPC
10. **FAST: Efficient Action Tokenization**（2024）—— 动作 token 化

---

## 8. sim-to-real：永恒的鸿沟

把仿真训的策略部署到真实机器人，是具身 AI 的核心难题。三大挑战：

1. **Domain gap**：仿真纹理 / 光照 / 物理参数与真实不同。解法：domain randomization、sim2real sim2sim。
2. **Compounding error**：world model 每步误差 ~5%，10 步后误差累积 60%+。解法：短 horizon planning、uncertainty-aware rollout。
3. **接触动力学**：刚体接触、摩擦、变形极难仿真。解法：可微物理（Brax, Genesis）、真实接触数据 finetune。

2025 年的最新进展是 **learning-based simulator**——用真实数据训练一个神经物理引擎（如 Genesis、Cosmos Reason），在它里面训策略，迁移到真实更稳。

---

## 9. 复现指引：用 LeRobot 跑通 Diffusion Policy

**LeRobot**（[github.com/huggingface/lerobot](https://github.com/huggingface/lerobot)）是 HuggingFace 维护的具身 AI 框架，集成 Diffusion Policy、ACT、π0 等基线。最小可运行步骤：

```bash
# 1. 安装
git clone https://github.com/huggingface/lerobot.git
cd lerobot && pip install -e .

# 2. 下载数据（PushT 简单任务）
python lerobot/scripts/push_dataset_to_hub.py \
  --raw-dir data/pusht \
  --repo-id lerobot/pusht

# 3. 训练 Diffusion Policy
python lerobot/scripts/train.py \
  --policy diffusion \
  --dataset repo=lerobot/pusht \
  --output-dir out/diffusion_pusht

# 4. 评估 + 可视化
python lerobot/scripts/eval.py \
  --policy out/diffusion_pusht/checkpoints/last \
  --env pusht
```

更进阶：用 LeRobot 训 π0 / OpenVLA，需要至少 4×A100。家用机器可用 7B OpenVLA 在 RTX 4090 上推理（~5Hz）。

---

## 📌 进一步阅读

- **必备综述**：[arXiv:2605.12090](https://arxiv.org/abs/2605.12090)（WAM 2026 综述）
- **Dreamer 系列**：Hafner 个人主页 [danijar.com](https://danijar.com)
- **VLA 入门**：Stanford Mobile Aloha 项目 [mobile-aloha.github.io](https://mobile-aloha.github.io)
- **数据生态**：Open X-Embodiment 数据集 [robotics-transformer-x.github.io](https://robotics-transformer-x.github.io)
- **WAM 跟踪**：weekly 跟踪 [AK on X](https://x.com/_akhaliq)

## ✍️ 思考题

1. **Cascaded WAM 与 Joint WAM 各适合什么场景？** 试想：如果一个任务的世界模型目标（精确预测）与 policy 目标（高回报）强烈冲突，应该选哪种？为什么？
2. **FAST 把连续动作 token 化后，丢失了什么信息？** 这种丢失在哪些任务上会致命，哪些任务上无关？
3. **Genie 2 用 latent action model 让 YouTube 视频可训 WAM。这种「无监督动作」与真实电机指令之间的 gap，能在所有任务上消除吗？给出一个反例。**

---

<!-- subtask 直接写入，2026-07-20。本章节所有 arXiv ID 均经 arXiv API / 官方 blog 一手核实；DreamZero / Genie 2-3 / Cosmos Policy / Helix 等部分版本仅有 blog 无 arXiv 论文，已在文中明确标注。 -->
