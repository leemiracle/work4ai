# 2025-2026 高效 AI 全行业热点地图

> 2025-2026 高效 AI 的**全行业趋势横切面**——覆盖推理优化 / test-time compute / 端侧 LLM / hybrid 架构 / agent RL / MoE 六大热点。
>
> **与 [`高效AI前沿-2025-2026顶会精选`](高效AI前沿-2025-2026顶会精选.md) 的分工**：那篇是顶会论文**精选**（12 篇深读，聚焦稀疏 attention/PD 分离/KV 压缩）；本篇是全行业**广度热点**（六大主题趋势 + 代表工作，含那篇没覆盖的 test-time/端侧/hybrid/agent RL）。两者互补：C 深，A 广。
>
> **整理日期**：2026-08-10 ｜ **来源**：Stanford CS224R (Noam Brown) / ACL 2026 / Apple WWDC26 / Google blog / Arm / Raschka 2026 论文综述 + arXiv

---

## 一、2025-2026 高效 AI 的六大热点

```
热点 1: 推理优化 (稀疏 attention / PD 分离 / KV 压缩)  ── 见 C 精选，本篇引用
热点 2: test-time compute scaling ─── 新的 scaling 维度 (o1→o3→小时级)
热点 3: 端侧 LLM ─── Apple AFM 3 / Gemma 4 QAT / Phi-4 / 极端量化
热点 4: hybrid 架构 ─── attention + Mamba/DeltaNet 交替 (长上下文高效)
热点 5: agent RL 加速 ─── ARRoL / OM-GRPO / label-free RLVR
热点 6: MoE 高效化 ─── 稀疏激活 + expert 路由优化
```

---

## 二、热点 ①：推理优化（详见 C 精选）

> 这是 2025-2026 最密集的方向，已在 [`高效AI前沿-2025-2026顶会精选`](高效AI前沿-2025-2026顶会精选.md) 详细讲透 12 篇论文。本篇只给趋势总结：

**三条子线**：
- **稀疏 attention**：从固定 mask（StreamingLLM）→ query-aware 自适应（Twilight/Quest/Δ-Attention）。**98% token 可剪枝近乎无损**。
- **Prefill-Decode 分离**：NVIDIA + Meta 两篇 MLSys 2026 确认——**在线服务用分离式省 30% 算力**，已成生产共识。
- **KV 压缩**：DMS 提出"用 KV 压缩换推理 token"的 **hyper-scaling**——不是省钱，是**用效率换准确率**。

---

## 三、热点 ②：test-time compute scaling（新 scaling 维度）

> Noam Brown (OpenAI, Stanford CS224R 2026) 的核心论断：**reasoning model 开辟了 scaling 的新维度——推理算力**。从 o1（秒级）→ o3（分钟级）→ IMO 金牌模型（小时级）→ scaffold（天/周级）。

### 三种 test-time scaling 范式

| 范式 | 机制 | 代表 | 特点 |
|---|---|---|---|
| **单轨迹顺序** | 延长单一推理链 | DeepSeek-R1 / s1 budget forcing | 串行，延迟瓶颈 |
| **叶级并行** | 采样多候选 + 投票/验证 | Best-of-N / self-consistency | 并行，但 compute 效率低 |
| **前缀级并行** | 搜索未完成部分状态 | Tree-of-Thoughts / RAP / value-guided | 最强但最贵 |

### 2026 的进展（ACL 2026）

- **PaCoRe**（Parallel Coordinated Reasoning）：8B 模型靠**多轮并行探索 + message-passing 协调**，HMMT 2025 达 **94.5% 超 GPT-5 的 93.2%**——有效 TTC 扩到 ~200 万 token。
- **Timely Machine**：把 test-time 从"生成长度"重定义为 **wall-clock time**（agent 场景工具延迟使两者脱钩）。Timely-RL 训模型感知时间预算。
- **多 Agent 推理**：debate / mixture-of-agents 在等 compute 预算下比 self-consistency **+1.3~2.7 点**。

> 🎯 **Brown 的战略洞察**：inference compute 被严重低估——今天 $1M 的能力明年可能 $100。**安全评估必须 project test-time compute**（dedicated state actor 可花 $10M 推理）。test-time 是"窥探未来的窗口"。

### 对接 work4ai
[`讲透RL/05(RLVR极限)`](讲透RL/) + [`讲透基础模型`](讲透基础模型/)（inference scaling）

---

## 四、热点 ③：端侧 LLM（2026 爆发）

> 2026 是端侧 LLM 的"iPhone 时刻"——Apple / Google / Microsoft 全员入场，手机跑 LLM 成标配。

### Apple Foundation Models 第三代（WWDC26，2026-06）⭐⭐
- **AFM 3 Core**（3B dense）/ **AFM 3 Core Advanced**（20B 稀疏，激活 1-4B）/ **AFM 3 Cloud** / **AFM 3 Cloud Pro**
- **AFM 3 Core Advanced 的突破**：**Instruction-Following Pruning (IFP)** ——20B 模型存 NAND（flash），按 prompt 路由选 expert 进 DRAM（vs 传统 MoE 逐 token 路由，NAND 带宽不够）。**推理时弹性**：按任务难度调激活参数量。
- **on-device 极端量化**：**2-bit QAT**（平衡集 {-1.5,-0.5,0.5,1.5}）+ KV cache sharing（Block 分 62.5%/37.5%，Block2 无 KV 省 37.5% KV + TTFT -37.5%）。
- **Core AI 框架**（开源）：LanguageModel protocol 统一本地/云端；coreai-build AOT 编译降首次加载延迟。

### Google Gemma 4 QAT（2026-06）⭐
- **mobile-specialized 量化 schema**：静态激活 + channel-wise 量化适配移动加速器 + **targeted 2-bit**（只压缩 token 生成层，核心推理层高精度）+ embedding/KV cache 优化
- **Gemma 4 E2B 文本版 < 1GB**（可跑在主流手机）
- **Multi-Token Prediction (MTP)** 加速推理

### Microsoft Phi-4-mini（端侧 reasoning 首选）
- 3.8B 参数，**reasoning 质量超 5-10× 大模型**（MATH/GPQA）
- iPhone 17 Pro Q4_K_M ~13-18 tok/s（可用对话速度）

### 端侧模型选型矩阵（2026 共识）

| 手机档位 | RAM | 推荐模型 | 速度 |
|---|---|---|---|
| 旗舰 (8-12GB) | iPhone 17 Pro / Galaxy S25 Ultra | **Phi-4-mini 3.8B** Q4_K_M | ~13-18 tok/s |
| 中端 (6-8GB) | iPhone 14 Pro / Pixel 9 | SmolLM2 1.7B / Qwen3 1.7B | ~26-32 tok/s |
| 低端 (4-6GB) | iPhone 14 / 老 Android | Gemma 3 1B | ~35-45 tok/s |

### 端侧量化趋势（Arm 实测）
- **8-bit PTQ** 是可靠默认（近 FP16 精度）
- **4-bit 权重 (W4_AFP16)** 是内存受限设备的下一步（~95% 质量，1/4 体积）
- **2-bit 出现**（AngelSlim / Apple AFM）——极端压缩，需 QAT 保质量

### 对接 work4ai
[`端侧AI架构参考`](端侧AI架构参考.md) + [`讲透GPU与系统级`](讲透GPU与系统级/)（量化）

---

## 五、热点 ④：hybrid 架构（attention + Mamba/DeltaNet 交替）

> 2026 长上下文是王道（agent harness 需要越来越长上下文）。纯 attention 的 $O(n^2)$ 太贵，**hybrid 交替层**成主流（Raschka 2026 综述）。

| 模型 | 非 attention 层 | 特点 |
|---|---|---|
| **Nemotron 3 Super**（NVIDIA, 2026-04）| Mamba-2 | attention 与 Mamba-2 交替，长上下文高效，agentic reasoning |
| **Qwen3.6** | Gated DeltaNet | 用 Gated DeltaNet 替代部分 attention |
| **Mamba-3** | — | 状态空间模型持续演进 |

> 🎯 **趋势**：纯 Transformer 在退场——2026 的新模型越来越多用 **hybrid（attention + 线性复杂度层）** 平衡"长上下文效率"和"attention 表达力"。对接 [`讲透基础模型`](讲透基础模型/)（架构）。

---

## 六、热点 ⑤：agent RL 加速（RLVR 训练效率）

> RLVR（RL with Verifiable Rewards）是 reasoning model 的训练范式，但**采样开销巨大**（每 prompt 多 rollout）。2026 的工作在"如何让 RLVR 更快/更省"。

- **ARRoL**（ACL 2026）：**在线 rollout 剪枝**——训练轻量 quality head 预测部分 rollout 成功率，早剪枝 + 重平衡存活 rollout。**"less rollouts, more learning"**：1.7× 训练加速 + 准确率 +2.3~2.99。
- **OM-GRPO**（2026）：**label-free RLVR**——mask answer span 梯度（防 reward hacking 答案 token），只优化 reasoning 轨迹。对比 augmented reward (CAR) 无需额外 rollout。test-time training 比 majority vote **+4.24 点**。
- **Spec-RL / FastGRPO**：用 speculative decoding 加速 rollout 生成
- **FlashRL / QeRL**：低精度/量化 rollout

> 🎯 **核心矛盾**：RLVR 需要大量 rollout（贵）↔ 训练信号稀疏（很多 rollout 全对/全错，弱信号）。2026 的工作都在"**用更少 rollout 提取更强信号**"。对接 [`讲透RL/03-06`](讲透RL/)。

---

## 七、热点 ⑥：MoE 高效化

> MoE 成大模型主流（DeepSeek-V3/R1、Qwen3、Llama 4），但 expert 路由/稀疏激活带来新效率问题。

- **Expert Parallelism**（EP）：MoE 在 scale-out 上的独特优势（Meta MLSys 2026 确认）
- **Scaling Embeddings vs Scaling Experts**（2026-01）：扩 embedding 比扩 expert 更优
- **Apple IFP**（见端侧）：按 prompt 路由 expert 进 DRAM（突破 MoE 的 NAND 带宽瓶颈）
- **DeepSeek MLA**（Multi-Latent Attention）：MoE + 低秩 KV 压缩

### 对接 work4ai
[`讲透Transformer`](讲透Transformer/)（MoE）+ [`讲透GPU与系统级`](讲透GPU与系统级/)（EP）

---

## 八、综合洞察（2025-2026 高效 AI 往哪走）

### 洞察 1 · 从"省算力"到"用效率换能力"
2024 的高效 AI 是"**省钱**"（量化/剪枝降成本）；2026 转向"**用效率换能力**"——DMS 用 KV 压缩换更多 reasoning token 提准确率；test-time scaling 用推理算力换分数。**效率不再是目的，是新能力的杠杆**。

### 洞察 2 · 推理成为 scaling 主战场
Noam Brown：reasoning model 让**推理算力**成为独立 scaling 维度（区别于训练 scaling）。o1→o3→小时级→天级。**安全评估必须按 test-time compute 投影**——否则低估真实风险。

### 洞察 3 · 端侧 LLM 进入"2-bit 时代"
Apple AFM 3 的 **2-bit QAT** + IFP NAND 路由，让 20B 模型跑进手机。2026 的端侧不再是"小模型"，而是"**大模型极端压缩 + 智能路由**"。

### 洞察 4 · 架构从"纯 Transformer"走向"hybrid"
纯 attention 在长上下文下太贵。Nemotron 3 (Mamba-2) / Qwen3.6 (Gated DeltaNet) 代表 **hybrid 交替层**成主流。Transformer 不会死，但会**与其他线性复杂度层共存**。

### 洞察 5 · RLVR 训练效率是新瓶颈
RLVR 是 reasoning model 的引擎，但 rollout 太贵。2026 的工作（ARRoL/OM-GRPO）都在"**少 rollout 强信号**"。这决定 reasoning model 能不能平民化训练。

---

## 九、与 work4ai 的对接

| 热点 | work4ai 深度版 |
|---|---|
| 推理优化（稀疏/PD分离/KV压缩）| [`高效AI前沿-2025-2026顶会精选`](高效AI前沿-2025-2026顶会精选.md)（C，12 篇深读）|
| test-time compute scaling | [`讲透RL/05(RLVR极限)`](讲透RL/) + [`讲透基础模型`](讲透基础模型/) |
| 端侧 LLM | [`端侧AI架构参考`](端侧AI架构参考.md) + [`讲透GPU与系统级`](讲透GPU与系统级/)（量化）|
| hybrid 架构 | [`讲透基础模型`](讲透基础模型/)（架构）|
| agent RL 加速 | [`讲透RL/03-06`](讲透RL/)（GRPO/RLVR）|
| MoE 高效化 | [`讲透Transformer`](讲透Transformer/)（MoE）|

**阅读路径**：本篇（广度趋势）→ [`C 顶会精选`](高效AI前沿-2025-2026顶会精选.md)（深度论文）→ [`HAN Lab 地图`](高效AI研究参考-MITHANLab.md)（单实验室纵深）→ 对应讲透系列钻原理。四份高效 AI 参考形成完整图景。

---

## 十、热点速查表

| 热点 | 代表工作 | 关键数字 | 来源 |
|---|---|---|---|
| 自适应稀疏 attention | Twilight / Δ-Attention | 98% 剪枝 / 32× 加速 | NeurIPS 2025 |
| PD 分离服务 | NVIDIA / Meta | 省 30% 算力 | MLSys 2026 |
| KV 压缩换推理 | DMS (Hyper-Scaling) | Qwen-R1 +12 点 | NeurIPS 2025 |
| test-time scaling | PaCoRe / Noam Brown | 8B 超 GPT-5 (HMMT) | ACL 2026 / Stanford |
| 端侧 2-bit LLM | Apple AFM 3 | 20B 模型激活 1-4B 进手机 | WWDC26 |
| 端侧 QAT | Gemma 4 | E2B < 1GB | Google 2026-06 |
| hybrid 架构 | Nemotron 3 (Mamba-2) | attention+Mamba 交替 | 2026-04 |
| agent RL 加速 | ARRoL / OM-GRPO | 1.7× RLVR 加速 | ACL 2026 |

---

> **数据源**：Stanford CS224R (Noam Brown) / ACL 2026 / Apple WWDC26 / Google blog / Arm developer / Raschka 2026 论文综述 + arXiv（2026-08-10 核实）｜ **维护**：高效 AI 月月有新进展，关注 AK / Raschka / HAN Lab / Apple ML research 动态。
