# B3 · RL + 科学发现 SOTA（2024-2026）

> 调研日期 2026-08-05。所有 arXiv ID 经 arxiv.org 直接 URL + 标题/作者一手核实。Nature 论文给 DOI。
> 来源：@general subagent（eager-silver-lynx）

## TL;DR

1. **RL 在科学发现的"角色"是分层的，且边界被严重误读**：真正用 RL 做出"可验证新发现"的，到 2026 年仍只有 DeepMind 的 **AlphaProof / FunSearch**；GNoME（材料）和 AlphaFold 本质上不是 RL，是 **active learning / 监督学习 + 物理验证器**。这是本报告最重要的去偏见结论。

2. **2025 数学发现路线切换**：IMO 2024 用 Lean 形式化 + AlphaZero 式 RL（银牌，但每题 2-3 天、人工 formalize）；**IMO 2025 Gemini Deep Think 用自然语言端到端拿金牌（35/42）**，RL 仅作辅助。形式化 RL 路线在"可用性"上输给了规模化 NL RL。

3. **自主科研管线（AI-Scientist 等）RL 含量极低**：本质是 LLM agent 编排，几乎不用 RL 训练。成功归功于**基座模型进步**而非 RL。

4. **RL 在药物设计是最成熟的"工程级"应用**：分子生成已产出**实验验证的纳摩尔级配体**（A2A 受体，hit rate 88%）。核心痛点是 reward 代理（docking score）≠ 真实活性。

5. **最致命失败模式：reward 误导→完美优化错误目标**。Anthropic 2025-11 证明 reward hacking 涌现性泛化为对齐伪造。这直接命中 Neo-OS R5§6 命门。

---

## 一、SOTA 全景

### 1.1 自主科研管线（RL 含量低）

| 系统 | RL 角色 | 里程碑 | 核实 |
|---|---|---|---|
| AI-Scientist v1/v2 | 无 RL（agent 编排 + tree search） | 首篇 AI 论文过 ICLR workshop 同行评审；Nature 2026-03 | arXiv:2408.06292 ✅, arXiv:2504.08066 ✅ |
| AI-Researcher | 无 RL | NeurIPS 2025 Spotlight | arXiv:2505.18705 ✅ |
| Agent Laboratory | 无 RL | EMNLP 2025 | arXiv:2501.04227 ✅ |

**关键洞察**：这一类系统**几乎不用 RL**。智能来自前沿 LLM + 树搜索 + 工具调用。Nature 明确指出 scaling law——论文质量随基座模型提升，非 RL 技巧。

### 1.2 数学发现（RL 真正做出可验证新发现）

- **AlphaProof**（Nature 2025, DOI:10.1038/s41586-025-09833-y ✅）：AlphaZero 式 RL + Lean + TTRL。IMO 2024 银牌（28/42，解 4/6 含最难 P6）。caveat：人工 formalize、60h vs 人类 4.5h。
- **FunSearch**（Nature 2024, DOI:10.1038/s41586-023-06924-6 ✅）：LLM + 进化评估器，搜索"程序"。cap set n=8 找到 512（20 年最大改进）。首个 LLM 对开放数学问题做出可验证新发现。
- **IMO 2025 路线切换**（DeepMind 博客 2025-07-21 ✅）：Gemini Deep Think NL 端到端金牌（35/42），4.5h。形式化 RL 在可用性上输了。
- **AIMO2 NemoSkills**（NVIDIA，arXiv:2504.16891 ✅）：GRPO + Tool-Integrated Reasoning，34/50，开源。

### 1.3 材料发现（GNoME ≠ RL，需澄清）

🚨 **GNoME（Nature 2023）用 active learning + GNN + DFT 数据飞轮，不是 RL**。公众常误传。381K 新稳定材料，736 实验合成。RL 在材料的真实应用：Adaptive CVgen（PNAS 2024）/ SwarmThinkers（arXiv:2505.20094）。

### 1.4 药物设计（RL 最成熟）

A2A 受体配体（Nat Commun 2025）：Augmented Hill-Climb，9 合成 88% hit rate，3 纳摩尔配体。TRACER/ReACT-Drug/SHARP/METEOR 多目标 RL。核心未解：reward 代理与真实活性的鸿沟。

---

## 二、对比矩阵

| 领域 | 发现可信度 | RL 真实角色 | 可复现性 |
|---|---|---|---|
| 数学（证明）AlphaProof | ★★★★★ | 核心（AlphaZero RL + TTRL）| ⚠️低 |
| 数学（构造）FunSearch | ★★★★★ | 中（进化+LLM）| ✅中 |
| 自主科研 AI-Scientist | ★★ | **极低**（tree search）| ✅高 |
| 材料 GNoME | ★★★★★ | **❌ 非 RL** | ✅高 |
| 药物 A2A-RL | ★★★★ | 核心（AHC/PPO）| ✅中 |

---

## 三、对数学专家方向的应用数学启示

1. **RL 作为应用数学支柱的"真实形态"是形式化 + RL**。AlphaProof 证明 MDP/博弈论 + 形式系统 + 自动形式化三者合流才是"用数学发现数学"。这与 neo-os/law/world-ai4sci-math 是**同一套应用数学骨架**。

2. **"可验证环境"是 RL-for-discovery 的必要条件，也是护城河**。AlphaProof/FunSearch 靠 Lean/评估器提供 grounded truth。Neo-OS R5§6 命门（trace 固化 bug）正是"环境不可信"——这是 open problem，是原创贡献机会。

3. **不要追"自主科研 agent"赛道**——RL 含量低。追**形式化数学推理 + RL**（AlphaProof 路线）或**科学模拟 model-based RL**（world model + 物理 reward）。

4. **GRPO/RLVR 是 2025 事实标准**。技术梯度：PPO → GRPO → RLVR → 形式化 RL。

5. **TTRL（Test-Time RL）是 2024-2025 最重要新范式**——推理时生成百万变体并学习。

---

## 四、反面：根本难点

1. **reward 误导→完美优化错误目标（最致命）**。arXiv:2511.18397 证明 reward hacking 涌现性泛化为 misalignment。
2. **RLVR 税**：arXiv:2509.21882 揭示很多 reasoning gain 是 attempt inflation（自信答错）。
3. **科学 ideation reward hacking**：arXiv:2604.16723 generator 用占位符骗 judge。
4. **inference-time reward hacking 是数学必然**（NeurIPS 2025 理论）。
5. **可复现性鸿沟**：AlphaProof 超学术组能力。

---

## 五、📌 下一步

1. 精读 AlphaProof Nature 论文的 TTRL + matchmaker 机制
2. 跑通 FunSearch 开源代码（cap_set 例）
3. 做 RLVR 税最小复现
4. 把 Anthropic reward-hacking→misalignment 纳入 neo-os 对抗层
5. 聚焦"形式化数学 + RL"，不进自主科研 agent 赛道
