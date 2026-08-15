# 讲透 RL（强化学习）

> 强化学习是 AI 的"**决策维度**"——监督学习学"是什么"，RL 学"**怎么做才能拿最多奖励**"。从 AlphaGo 到 ChatGPT 的 RLHF，RL 是让 AI 从"懂"到"会做"的关键。
>
> 2024-2026 RL 重新成为显学：DeepSeek-R1 用 GRPO 训出 reasoning、所有 LLM 后训练都用 RLHF/DPO、AlphaProof 拿 IMO 银牌、AlphaEvolve 上线 Google Borg。**本系列从 MDP 地基讲到 2026 最新前沿**，把 RL 在 LLM 时代的方法论钻透。
>
> **🆕 想一次看全？** 进 [**07 · RL 全景地图与 2026 最新研究**](./07-2026最新研究全景.md)（截止 2026-08-12，整合项目内所有 RL 资产 + 10 大主题最新前沿）。
>
> 配套：[`讲透公开课/01-CS285 Spring 2026`](../讲透公开课/01-前沿课实时清单.md)（Berkeley 深度 RL，2026 版新增 LLM RL 章节）+ [`讲透微调`](../讲透微调/)（RLHF/DPO 实战）+ [`讲透世界模型`](../讲透世界模型/)（Dreamer/Genie 谱系）+ [`讲透AI应用全景/02-AI4Math`](../讲透AI应用全景/02-AI4Math.md)（AlphaProof 用 RL）

---

## 篇目（9 章 + 实验目录，全部 ✅）

| # | 标题 | 状态 | 核心 | 2026 最新覆盖 |
|---|------|------|------|-------------|
| **00** | [为什么 RL + MDP 地基](./00-为什么RL与MDP.md) | ✅ | RL vs 监督、MDP 五元组、两大流派、RLHF 复兴 | — |
| **00'** | [讲透笔记-算法经验枢纽](./00-讲透笔记-算法经验枢纽.md) | ✅ | 算法经验枢纽笔记 | — |
| **01** | [Q-Learning / DQN 家族](./01-Q-Learning与DQN.md) | ✅ | Bellman 方程、值函数方法、DQN 经验回放/target 网络 | — |
| **02** | [策略梯度 / PPO](./02-策略梯度与PPO.md) | ✅ | REINFORCE → importance sampling → PPO clip | — |
| **03** | [RLHF / DPO / GRPO](./03-RLHF-DPO-GRPO.md) | ✅ | LLM 对齐三件套、DPO 闭式解、GRPO 去 critic | ✅ DeepSeek-R1（2501.12948）|
| **04** | [RL + 形式证明](./04-RL与形式证明.md) | ✅ ⭐ 2026-08 | AlphaProof + 开源三强 + 基准破灭 | ✅ Nature 2025 / atp-checkers 2026 / FormalRewardBench |
| **05** | [RLVR 的极限](./05-RLVR的极限.md) | ✅ ⭐ 2026-08 | pass@k 反转（NeurIPS 2025 Oral）| ✅ 6 算法对比 / Diversity Collapse 反方 |
| **06** | [RL + 系统软件](./06-RL与系统软件.md) | ✅ ⭐ 2026-08 | AlphaEvolve + Cold-RL 六条铁律 | ✅ AlphaEvolve（2506.13131）/ Cold-RL（2508.12485）/ reward hacking 跨域（2511.18397）|
| **07** | [**RL 全景地图 + 2026 最新研究**](./07-2026最新研究全景.md) | ✅ ⭐ 2026-08-12 | **整合索引 + 10 大主题最新前沿** | ✅ 截止 2026-08-12（LLM RL/RLVR 加速/test-time/world model/VLA/系统/形式化）|
| **⭐ 08** | [**Actor-Critic / SAC / Model-Based / Offline RL**](./08-Actor-Critic-SAC-ModelBased-OfflineRL.md) | ✅ ⭐ 2026-08-12 | **CS285/CS234 硬通货**：DDPG→TD3→SAC 严格推导 + PETS/MBPO/Dreamer + CQL/AWAC + Bellman 收敛证明 + deadly triad 实证（[实验跑通](./experiments/08_bellman_and_deadly_triad.py)）| — |
| **⭐ 09** | [**工业实践与能力建设**](./09-工业实践与能力建设.md) | ✅ ⭐ 2026-08-12 | **系列收尾**：5 阶段工程化 SOP + 失败模式库（reward hacking/崩溃/漂移/评估陷阱/成本）+ **4 维能力矩阵 + 30 条自评 checklist** + 6 个阶梯项目 + **三大方向分流（LLM/机器人/世界模型）发射台** | — |

---

## 怎么用（按目标分流）

### 🛤 想一次看全 RL 全方位 + 2026 最新
→ **直接进 [07 全景地图](./07-2026最新研究全景.md)**：一张图看全 + 10 大主题（LLM 对齐 / RLVR / RL 加速 / test-time / 形式证明 / world model / VLA / 系统软件 / 多智能体 / RL 后端）+ 项目内资产完整索引

### 🛤 想懂 ChatGPT/DeepSeek 怎么训的
→ 00 → 02 → **03**（RLHF/DPO/GRPO 是当前 LLM 对齐核心）→ 05（RLVR 极限，理解能力边界）

### 🛤 想学经典 RL（地基 + 方法）
→ 00 → 01 → 02（值函数 + 策略梯度两大主线）

### 🛤 想搞机器人 / 具身 / world model
→ 00 → 01 → 02 → **[08 §1 SAC + §2 Model-Based](./08-Actor-Critic-SAC-ModelBased-OfflineRL.md)（CS285 核心硬通货）** → [`讲透公开课/01`](../讲透公开课/01-前沿课实时清单.md) §2 CS285 L15-16（model-based RL）→ [`讲透世界模型`](../讲透世界模型/)（Dreamer/Genie）→ [07](./07-2026最新研究全景.md) §2 主题 ⑦⑧

### 🛤 想搞 RL + 形式化 / 神经符号
→ 03 → **04**（AlphaProof 谱系 + 基准破灭）→ 05（能力边界）→ [`讲透形式化验证`](../讲透形式化验证/) + [`讲透神经符号`](../讲透神经符号/)

### 🛤 想把 RL 用到生产系统
→ **直接读 06**（六条铁律 + AlphaEvolve vs DRL 的生产真相）→ **然后读 [09 §1§2](./09-工业实践与能力建设.md)**（5 阶段工程化 SOP + 失败模式库），然后才看 02

### 🛤 想自评能力 / 选主攻方向（LLM·机器人·世界模型）
→ **直接读 [09](./09-工业实践与能力建设.md)**：30 条 checklist 自评 + 6 个阶梯项目 + §5 三大方向分流（每方向给入门路径 + 项目内资产 + 2026 前沿）

### 🛤 想做 RL 理论研究
→ 00 + [`讲透统计学习理论`](../讲透统计学习理论/) → **[08 §4 Bellman/TD/Q-Learning 收敛性 + deadly triad](./08-Actor-Critic-SAC-ModelBased-OfflineRL.md#§4-收敛性证明cs234-的硬通货)（CS234 硬通货）** → **05**（pass@k 反转的数学根因）→ [07](./07-2026最新研究全景.md) §2 主题 ⑨

### 🛤 想做 Agent 决策
→ 00 + 02（PPO 是 Agent 工具调用 RL 的基础）+ 配 [`讲透Agent`](../讲透Agent/)

---

## 2026 最新前沿速查（详见 [07](./07-2026最新研究全景.md)）

| 主题 | 关键工作 | 项目内文档 |
|------|---------|----------|
| **LLM 对齐算法** | RLHF → DPO → GRPO → DAPO（→ GSPO/Dr.GRPO 待核）| [03](./03-RLHF-DPO-GRPO.md) |
| **RLVR 极限** | Limit of RLVR（NeurIPS 2025 Oral）：RLVR 是锐化器不是发现器 | [05](./05-RLVR的极限.md) |
| **RL 训练加速** | ARRoL（1.7× 加速）/ OM-GRPO（label-free）/ Spec-RL / FastGRPO | [`高效AI前沿`](../高效AI前沿-全行业热点地图.md) §六 |
| **Test-time compute** | Noam Brown CS224R / PaCoRe（8B 超 GPT-5）/ Timely-RL | [`高效AI前沿`](../高效AI前沿-全行业热点地图.md) §三 |
| **RL + 形式证明** | AlphaProof（IMO 银牌）/ Seed-Prover（99.6%）/ Delta-Prover（零微调）/ atp-checkers（基准破灭）| [04](./04-RL与形式证明.md) |
| **RL + 系统软件** | AlphaEvolve（Google Borg）/ Cold-RL（NGINX）/ reward hacking 跨域泛化 | [06](./06-RL与系统软件.md) |
| **World Model** | Dreamer V3 / Genie 2 / DIAMOND（部分待核）| [`讲透世界模型`](../讲透世界模型/) + [07](./07-2026最新研究全景.md) §2 主题 ⑦ |
| **VLA & 具身 RL** | π0 / OpenVLA / Berkeley CS294-318 Levine（待核）| [07](./07-2026最新研究全景.md) §2 主题 ⑧ |
| **RL 后端工程** | verl（22.8k⭐）/ OpenRLHF / TRL | [`前沿与媒体/02-后训练`](../前沿与媒体/02-后训练信息源专题.md) |

---

## 配套（项目内 RL 完整生态）

- **课**：[`讲透公开课/01`](../讲透公开课/01-前沿课实时清单.md) §2 CS285 Spring 2026（含 2026 新增 LLM RL L14 + HW4）
- **数学**：[`讲透公开课/02`](../讲透公开课/02-数理计算机神课清单.md) 的 Stat 110（概率/MDP）
- **实战**：[`讲透微调`](../讲透微调/) 的 RLHF/DPO 部分
- **源码**：[`讲透公开课/03`](<../讲透公开课/03-AI Infra 源码导读清单.md>) 的 T5（verl/AReaL/Miles，RL 后端）
- **跨校代码**：[`berkeley-cs-projects/topic7-rl/deep_rl.py`](../top-cs-projects/berkeley-cs-projects/topic7-rl/deep_rl.py)（CS285 SAC/PPO numpy 实现）
- **前沿追踪**：[`高效AI前沿-全行业热点地图`](../高效AI前沿-全行业热点地图.md)（2026-08-10）+ [`高效AI前沿-2025-2026顶会精选`](../高效AI前沿-2025-2026顶会精选.md)
- **信息源**：[`前沿与媒体/02-后训练信息源专题`](../前沿与媒体/02-后训练信息源专题.md)（RLHF/DPO/GRPO 完整信息源 + verl/OpenRLHF + 一手研究者）
- **内部视角**：[`访谈及其他/张小珺访谈精读/第140集-姚顺宇`](../访谈及其他/张小珺访谈精读/)（Anthropic Horizon RL 团队 10-11 人 + Gemini 3 Deep Think）
- **world model**：[`讲透世界模型`](../讲透世界模型/)（Dreamer/Genie 谱系，model-based RL）
- **分布式 RL**：[`讲透分布式AI系统`](../讲透分布式AI系统/)（RL 后端的 DDP/FSDP/ZeRO）
- **形式化背景**：[`讲透形式化验证`](../讲透形式化验证/)（Lean4 / seL4，配 [04](./04-RL与形式证明.md)）
- **神经符号闭环**：[`讲透神经符号`](../讲透神经符号/)（AlphaProof 式 RL+形式化，配 [04](./04-RL与形式证明.md)）

---

## 更新日志

- **2026-08-12（晚）**：新增 [**09 工业实践与能力建设**](./09-工业实践与能力建设.md)——**系列收尾篇章**，做两件 [06](./06-RL与系统软件.md)/[07](./07-2026最新研究全景.md) 没做的事：① **5 阶段工程化 SOP**（数据/训练/评估/部署/迭代）+ **5 类失败模式库**（reward hacking/训练崩溃/分布漂移/评估陷阱/成本失控）；② **4 维能力矩阵 + 30 条自评 checklist + 6 个阶梯项目（P1-P6）**。同时是**三大方向发射台**：§5 把 LLM / 机器人 / 世界模型各自的角色、核心问题、项目内资产、入门路径、2026 前沿一次性铺好，并标注目录建设待决策（是否新建 讲透LLM / 讲透具身 / 清理世界模型重复文件）。
- **2026-08-12（下午）**：新增 [**08 Actor-Critic / SAC / Model-Based / Offline RL**](./08-Actor-Critic-SAC-ModelBased-OfflineRL.md)——填补 CS285/CS234 核心硬通货的空白：DDPG→TD3→**SAC 严格推导（最大熵 RL + soft Bellman）**、PETS/MBPO/Dreamer 三大 model-based 流派、CQL/AWAC offline RL、**Bellman γ-压缩证明 + deadly triad（Baird 反例）实证**。[实验代码](./experiments/08_bellman_and_deadly_triad.py) 三个理论结果全部跑通。
- **2026-08-12**：升级 README 反映实际 7 章状态（00-06 全 ✅）+ 新增 [07 全景地图](./07-2026最新研究全景.md) 作为单一入口枢纽 + 加入"2026 最新前沿速查"表 + 配套生态完整索引。
- **2026-08**：新增 [04 RL+形式证明](./04-RL与形式证明.md) / [05 RLVR 极限](./05-RLVR的极限.md) / [06 RL+系统软件](./06-RL与系统软件.md) 三章（neo-os 回流）。
- 首版：00-03 + 经典 RL 主线。

---

## 🔗 理论锚点（§12-15 横向打通）

> 横向总纲：本单元在 [`激活大语言模型能力-总结.md`](../激活大语言模型能力-总结.md) 中给出 L2 层最重要修正——**RLVR 是显影器不是发现器**（pass@k 反转四连证据），蒸馏才是扩边界通道。

> 本系列讲"MDP/PPO/RLHF/GRPO"的算法与工程；这两门课把 RL 的**安全边界**和**对齐数学**公理化：
> 枢纽：[`§12-15 整合`](../§12-15%20理论·形式化·安全·可信AI%20整合.md) §21

| 课程 | 产物 | 公理化的内容 |
|---|---|---|
| §13.4 CMU 15-414（Platzer）| [`diff_dyn_logic.py`](../top-cs-projects/cmu-cs-projects/topic12-theory/diff_dyn_logic.py) | barrier certificate——机器人 RL（§06 RL+系统软件）的安全证明：连续版循环不变式 |
| §15.3 Stanford CS329T（Percy Liang）| [`pluralistic_safety.py`](../top-cs-projects/stanford-cs-projects/topic3-safety/pluralistic_safety.py) | pluralistic alignment + preference aggregation——§03 RLHF/DPO "对齐谁的偏好"的数学 |

---


---

## 🎭 欺骗动力学视角：reward 被 policy 骗

> 承接 [`欺骗动力学-社会进步的隐秘引擎.md`](../欺骗动力学-社会进步的隐秘引擎.md) §5。

### 三问

1. **讲透RL 防的是什么欺骗？** → reward hacking——policy 主动骗 reward model。
2. **被什么攻破？** → reward shaping 设计不当 / reward model 学偏 / exploration 套牢局部最优。
3. **沉淀进哪条主链？** → AI 安全主链——RLHF / Constitutional AI / KL 约束全是反 reward hacking 的工程化。

### 一句话

> RL 的核心难题不是「如何学得快」，而是「如何别学歪」——反欺骗是 RL 的第一问题。


---

🔗 **交叉链接**：Stanford CS336 论文精读 · 对齐与后训练（PPO/RLHF/DPO/GRPO/R1，8 篇），见 [`讲透公开课/06-CS336论文精读/H-对齐与后训练.md`](../讲透公开课/06-CS336论文精读/H-对齐与后训练.md)；配套可运行验证实验见 [`其 experiments/`](../讲透公开课/06-CS336论文精读/experiments/)。
