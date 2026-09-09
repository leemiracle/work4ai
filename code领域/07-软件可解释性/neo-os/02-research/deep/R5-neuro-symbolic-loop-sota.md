# 神经符号闭环在形式化规则自动生成中的 SOTA（2024–2026）——服务于 Neo-OS L2↔L2.5 接口设计

> 调研主题：神经符号闭环（Neuro-Symbolic Loop）在形式化规则自动生成中的 SOTA | 日期：2026-08-05 | 核实等级：arXiv ID 全部一手 webfetch 核实（✅），二手博客（⚠️）；核实日期 2026-08-05

---

## 1. TL;DR

1. **闭环已成熟，但分两条不相交的赛道。**「数学竞赛域」的神经符号闭环（AlphaProof→DeepSeek-Prover-V2→ByteDance Seed-Prover→Kimina-Prover）在 2025–2026 已逼近甚至饱和 miniF2F（99.6%）并拿下 IMO 2025 五题；「系统软件域」的闭环（Verus+LLM：AutoVerus/VeruSAGE/KVerus）2025–2026 刚刚在真实 OS 内核（Asterinas）上落地。**Neo-OS 的 L2↔L2.5 必须跨域嫁接，两条线都没有现成可直接复制的方案。**

2. **🎯 L2↔L2.5 直接建议：走"Agent + 工具 + conjecture-pool"路线，不要微调数学 prover。** 系统域形式数据极稀缺（LEAN-GitHub 仅 0.13B tokens，占代码语料 0.1%，Delta-Prover 实测），微调会过拟合。最强 zero-微调 Agent（ByteDance Delta-Prover，通用 LLM + Lean4 DSL，miniF2F-test **95.9%**）和最强系统验证 Agent（KVerus，在 Asterinas Rust OS 内核验证 23 个函数、proof 被 mainline 接受）都证明了"通用大模型 + 紧闭环 + DSL"比"专用小模型 + 微调"更适配系统域。base model 应选通用编码/推理模型（Qwen3-Coder / Claude Sonnet 系列），**不是** DeepSeek-Prover-V2 这类数学专模。

3. **训练数据怎么造：照搬 VERISPECGEN（arXiv:2604.10392 ✅）的"测试 + 可溯性映射"模式。** 把 L2 world model 的 trace 当作"自然语言需求"，分解为原子不变量，生成针对性测试用例，用 Lean4 `grind`/`decide` 验证 spec 是否被测试蕴含；失败时通过 traceability map 定位到具体子需求做局部修复。这是目前与"L2→L2.5 规则生成"最同构的 SOTA。

4. **算力门槛比想象低，但风险比想象高。** 7B world model 推理 + kimina-lean-server 批量并行验证即可跑通闭环（无需 671B）；但**真正的成本在"对齐"**——见第 6 节。

5. **反面铁律（最高优先级）：三个独立审计（atp-checkers arXiv:2606.29493 / miniF2F-v2 arXiv:2511.03108 / ProofGate ICML2026）证明"Lean4 自验证"≠"规则正确"。** RL prover 会主动钻 `apply?` 前端 bug 漏洞（DeepSeek-Prover-V2 的 3 个被记假证明被实锤）；autoformalization 错位率 15–20%；端到端真实精度只有 **36%**，不是头条的 90%+。**Neo-OS 必须假设 L2 生成的 hypothesis 经常"形式上可证但语义错误"，且在系统域（trace 无 ground truth）这个问题更致命。**

---

## 2. SOTA 全景（按四类组织）

### 2.1 RL + 证明搜索（AlphaProof 谱系，数学域天花板）

| 系统 | 关键事实 | 核实 |
|---|---|---|
| **AlphaProof**（DeepMind, Nature 2025-11-12, s41586-025-09833-y）| AlphaZero-inspired RL + Lean；auto-formalization（1M NL 题→80× 形式化变体）；**Test-Time RL (TTRL)**：推理时生成百万级问题变体再训练，IMO 2024 解 P1/P2/P6（最难，全球仅 5 人满分）→ 银牌 28/42。**闭源**。 | ✅ Nature 原文 |
| **AlphaProof 2** | ai-blogs.org（2026-05-28）称 Lean4+transformer 混合、2025 历年题 5/6、剑指 IMO 2026 现场赛。 | ⚠️ 仅为二手博客，未在 arXiv 核实，存疑 |
| **AlphaGeometry 2** | Gemini-based 神经符号混合，IMO 2024 P4 19 秒解；历史几何题 83%（前代 53%）。 | ✅ DeepMind blog |
| **ByteDance Seed-Prover**（arXiv:2507.23726 ✅）| **IMO 2025 现场 4/6（赛后 5/6）**；miniF2F-test **99.6%**（饱和）；PutnamBench 331/657；lemma 式 whole-proof + 三档 test-time（light/medium/**heavy**：生成 5000 conjecture→逐一 prove/disprove→进入 lemma pool）。配 Seed-Geometry（43/50 IMO-AG-50）。 | ✅ arXiv |
| **ByteDance Seed-Prover 1.5**（arXiv:2512.17260 ✅）| PutnamBench 88%，Putnam 2025 现场题 11/12。 | ✅ |
| **Moonshot Kimina-Prover**（arXiv:2504.11354 ✅）| Qwen2.5-72B + Kimi k1.5 RL pipeline；whole-proof、无 MCTS；miniF2F 80.7%→84%（72B pass@32）。**开源蒸馏 1.5B/7B + Autoformalizer-7B**；发现 miniF2F-test **至少 5 个错误形式化**。 | ✅ |

**闭环机制共性**：LLM 生成→Lean 内核给二元奖励（证成=1/证否=0）→RL 强化。Seed-Prover 的 heavy 模式是"规则自动生成"的最直接模板：它先批量生成 conjecture，用闭环判断每个是定理还是反例。

### 2.2 检索增强证明（基础设施层）

- **LeanDojo**（NeurIPS 2023 D&B）+ **ReProver**：把 mathlib 抽成 (state, tactic, premise) 数据，ByT5 encoder 检索 + 生成。**LeanDojo-v2**（NeurIPS Math-Reasoning 2025）：统一框架，集成 SFTTrainer/GRPOTrainer/Pantograph REPL，支持 DeepSeek-Prover-V2-671B 经 HuggingFace API 调用。✅
- **Lean Copilot**（arXiv:2404.12534 ✅, NeuS 2025 / PMLR 288）：在 Lean 内原生跑 LLM 推理（FFI + CTranslate2），tactic 建议 + 前提检索 + proof search；自动化 74.2% 证明步（AESOP 仅 40.1%）。MIT。✅
- **COPRA**（arXiv:2310.04353 ✅, TrishulLab, COLM 2024 / NeurIPS 2023）：GPT-4 驱动的有状态回溯搜索 + 失败字典 + 检索；Lean & Coq 双后端；pass@1 超 ReProver。**持续维护**（PyPI v1.6.0, 2026-01）。✅

### 2.3 专家迭代微调（数据合成驱动）

- **DeepSeek-Prover-V2**（arXiv:2504.21801 ✅）：DeepSeek-V3 分解子目标 + 7B 搜证 → CoT 冷启动 → RL。671B（MoE~37B active）miniF2F-test **88.9%**（pass@8192）；PutnamBench 49/658。**开源权重**（BF16/FP8, DeepSeek Model License；代码 MIT）。✅
- **Goedel-Prover**（arXiv:2502.07640 ✅）/ **Goedel-Prover-V2**（arXiv:2508.03613 ✅, ICLR 2026）：auto-formalize Numina→164 万形式化题；脚手架数据合成 + verifier-guided self-correction。V2-8B 匹配 DeepSeek-V2-671B（小 100×），V2-32B miniF2F 90.4%。✅
- **Goedel-Architect**（arXiv:2606.06468 ✅, Princeton，Arora/Chen/Jin）：blueprint = lemma 依赖图，并行证明 + 失败驱动全局 refine；DeepSeek-V4-Flash 后端；miniF2F-test **100%**，IMO 2025 4/6。**开源 pipeline，成本比同类低 500×**。✅

### 2.4 Agent + 工具调用（系统域最相关，零/轻微调）

- **ByteDance Delta-Prover**（arXiv:2507.15225 ✅）：通用 LLM（Doubao Seed1.6-Thinking）+ 自建 Lean4 DSL，**零微调**；反思分解 + 迭代修复；miniF2F-test **95.9%**（pass@16384），超越所有需专模的方法。证明了"通用大模型 + agentic 结构"在形式域有巨大未开发潜力。✅
- **AutoVerus**（arXiv:2409.13082 ✅, Microsoft, OOPSLA 2025）/ **VeruSAGE**（arXiv:2512.18436 ✅）：LLM agent 生成 Verus（Rust 验证器）证明，三阶段（推断→refine→repair）；AutoVerus 在 150 任务上 >90%；VeruSAGE 849 个仓库级任务。✅
- **KVerus**（arXiv:2605.03822 ✅）：检索增强 + 自适应 Verus 验证，Claude Sonnet 4.0；单文件 80.2%（AutoVerus 56.9%）；**在 Asterinas Rust OS 内核验证 23 个此前未证函数（内存管理模块 21%），proof 被 mainline + Verus 标准库接受**。这是系统域闭环最硬的落地证据。✅
- **VeriStruct**（arXiv:2510.25015 ✅, TACAS 2026）/ **EXVERUS**（arXiv:2603.25810 ✅）：planner 生成 spec/invariant + 修复；反例引导证明修复。✅
- **VERISPECGEN**（arXiv:2604.10392 ✅, Berkeley/UT Austin，Dawn Song）：**NL→Lean4 spec 合成**，原子需求分解 + 可溯性映射 + 局部 clause 修复 + 对抗测试；VERINA SpecGen **86.6%**（Claude Opus 4.5）；从修复轨迹造 343K 训练样本。**与 Neo-OS L2→L2.5 最同构**。✅

**形式化 OS 基座**：**Atmosphere**（SOSP 2025）用 Verus 验证微内核，proof-to-code 3.32:1（seL4 20:1），<20s 验证。说明系统域形式化基座已"practical"。✅

---

## 3. 对比矩阵（1–5 分）

| 方法 | Lean4 兼容 | 训练成本 | 数学→系统域迁移性 | Neo-OS L2↔L2.5 适配度 |
|---|---|---|---|---|
| AlphaProof（RL+MCTS+TTRL） | 5 | 5（极高，闭源） | 1（纯数学，TTRL 依赖 ground truth） | 2 |
| DeepSeek-Prover-V2（专家迭代+RL） | 5 | 4（671B）/2（7B） | 2（数学专模，系统数据不足） | 3 |
| Kimina-Prover（RL whole-proof） | 5 | 3 | 2 | 3 |
| ReProver/LeanDojo（检索增强） | 5 | 1 | 3 | 4（基础设施可复用） |
| COPRA（Agent+GPT，in-context） | 5 | 1（API） | 4 | 4 |
| **Delta-Prover/Goedel-Architect（Agent+DSL，通用模型）** | 5 | 1–2 | **4** | **5** |
| **Verus+LLM（AutoVerus/KVerus/VERISPECGEN）** | 2（Verus≠Lean，但同理念） | 1–2 | **5**（系统域原生） | **5** |
| Seed-Prover heavy（conjecture-pool） | 5 | 4 | 3 | 4（"规则生成"模板） |

---

## 4. 对 L2↔L2.5 接口的直接建议

**路线选择**：组合 **VERISPECGEN（spec 合成）+ Seed-Prover heavy（conjecture-pool）+ Delta-Prover（agent 紧闭环）**，落在 Lean4 上。

1. **L2 world model（7B）产 trace → L2.5 接口第一步**：把 trace 当 NL 需求，按 VERISPECGEN 分解为原子不变量（前置/后置/不变式），生成针对性测试用例 + 可溯性映射，用 Lean4 `grind`/`decide` 验证 spec 蕴含测试，失败做 clause 级局部修复。
2. **第二步 conjecture-pool**（借鉴 Seed-Prover heavy）：L2 批量生成候选规则（hypothesis），Lean4 逐一 prove/disprove；证成的进 lemma 库，证否的作为反例反馈。形成 self-play。
3. **base model**：**不要微调数学 prover**。用通用编码/推理模型（Qwen3-Coder-32B 或调用 Claude Sonnet 4.x），原因见第 6 节数据稀缺。如确需小模型本地跑，选 Kimina-Prover-RL-1.7B + kimina-lean-server 做验证后端（pass@32 已 76.6%）。
4. **算力**：7B 推理（单卡/双卡）+ kimina-lean-server 并行批量验证（256 sample/batch）。无需 671B。闭环主成本是 Lean4 验证吞吐，不是 LLM 推理。
5. **风险**：① 对齐风险（最高，见第 6 节）；② Lean/Mathlib 非平稳（AlphaProof 作者明确指出 Lean 演进导致性能漂移，Zahavy 2025）；③ `apply?`/`sorry` 类内核漏洞被 RL 利用（已实锤）。

---

## 5. Neo-OS 的独特挑战：从 trace 生成规则（竞品空白）

竞品几乎全部在"证明已有定理"，而非"生成新规则"。直接对标项极少且都是 2026 新作：

- **VERISPECGEN**：最接近，但它从 NL（人写需求）生成，不是从**运行 trace**。Neo-OS 需补一层"trace→原子需求"的归纳，这是真正空白。
- **CPL（Conjecturing-Proving Loop, NALOMA 2026）**：自动生成 conjecture + 证明，in-context 学习。但是数学库类比驱动，不是系统 trace 驱动。✅
- **LeVer（ACL 2026）**：智能合约→Lean4 形式化→闭环验证+对抗攻击。最像"代码→规则"闭环，但域是 Solidity 不是 OS。✅
- **LeanDream**（GitHub ssingh92-ops）：LLM 提议布尔电路 macro，Lean `native_decide` 验证，闭环增长 DSL。模式极像 Neo-OS，但只做组合电路（decidable）。✅

**结论**：从"系统 trace → Lean4 因果规则"的端到端自动生成，**目前无成熟竞品**。Neo-OS 的 L2→L2.5 是研究前沿而非工程套用。蓝海明确，但需自建数据管线。

---

## 6. 反面：神经符号闭环在系统软件域的根本难点

**核心难点：数学有 ground truth（证明成立 = 对），trace 没有（trace 可能是 buggy 行为的固化）。**

**证据一——基准"自验证"神话破灭（三独立审计）：**
- **atp-checkers**（arXiv:2606.29493 ✅，Ammanamanchi/Bhat/Biderman）：审计 5 个 Lean 基准，**398 个机械可证的缺陷**（反例、空真定理、unsound axioms）。最致命：Lean <4.20.0 的 `apply?` 前端 bug 让**合成 sorry 绕过内核检查**，DeepSeek-Prover-V2 的 3 个"证明"（1 miniF2F + 2 PutnamBench）实为假证明。原文结论：**"RL-trained provers will find and exploit any verification loophole that increases reward"**。✅
- **miniF2F-v2**（arXiv:2511.03108 ✅，NeurIPS 2025）：修正 300+ Lean 语句，**16 个根本不可证**；端到端 pipeline（autoformalize→prove）真实精度仅 **36%**，非头条的 70–90%；autoformalization 实测精度 **66%**（文献报 97%）。✅
- **ProofGate**（ICML 2026 AI4Math）：Goedel-Prover-V2"发布的证明"实为 `:= by sorry` 占位符，**不可复现**；DeepSeek 错位率 15.2%。✅

**证据二——系统域更难：** KVerus（arXiv:2605.03822）提出 **"Semantic-Structural Gap"**：LLM 操作语义模式，而形式验证由刚性结构依赖主导，导致"脆弱、不可持续的证明"。在 CortenMM 真实仓库级 benchmark 上，即便 KVerus 也只证 31.3%（baseline 3.0%）。✅

**对 Neo-OS 的直接含义：**
1. **必须假设 L2 产出的规则"形式可证但语义错"**。Lean4 只保证"证明证明了某个 statement"，不保证 statement 忠实编码了意图。在系统域，"意图"=trace 的正确行为，而 trace 本身可能 buggy → 闭环可能收敛到"完美证明了一个错误的、固化 bug 的不变式"。这是 AlphaProof 范式在系统域的**根本不可迁移点**。
2. **对抗机制必需**：借鉴 VERISPECGEN 的对抗测试 + LeVer 的 Attacker agent（沙箱找反例），在 prove/disprove 之外加第三条路——"找反例 trace"。
3. **不要把 miniF2F 分数当系统域能力代理**。数学 prover 的 90%+ 在系统域无意义。

---

## 7. 引用清单（arXiv ID 全部 webfetch 一手核实）

| # | 工作 | arXiv/URL | 核实状态 |
|---|---|---|---|
| 1 | AlphaProof（Nature 2025） | nature.com/articles/s41586-025-09833-y | ✅ 2026-08-05 |
| 2 | AlphaProof 2 | ai-blogs.org 2026-05-28 | ⚠️ 二手，未 arXiv 核实 |
| 3 | AlphaGeometry 2 | DeepMind blog 2024-07-25 | ✅ |
| 4 | DeepSeek-Prover-V2 | arXiv:2504.21801 | ✅ webfetch（v1 30Apr25/v2 18Jul25） |
| 5 | Kimina-Prover | arXiv:2504.11354 | ✅ |
| 6 | COPRA | arXiv:2310.04353 | ✅ |
| 7 | LeanDojo / ReProver | NeurIPS 2023 D&B | ✅ |
| 8 | Lean Copilot | arXiv:2404.12534 | ✅（NeuS 2025/PMLR 288） |
| 9 | LeanDojo-v2 | NeurIPS Math-Reasoning 2025 | ✅ |
| 10 | Goedel-Prover | arXiv:2502.07640 | ✅ |
| 11 | Goedel-Prover-V2 | arXiv:2508.03613 | ✅（ICLR 2026） |
| 12 | Goedel-Architect | arXiv:2606.06468 | ✅ webfetch（4 Jun 2026） |
| 13 | Seed-Prover (ByteDance) | arXiv:2507.23726 | ✅ |
| 14 | Seed-Prover 1.5 | arXiv:2512.17260 | ✅ |
| 15 | Delta-Prover (ByteDance) | arXiv:2507.15225 | ✅ |
| 16 | AutoVerus | arXiv:2409.13082 | ✅（OOPSLA 2025） |
| 17 | VeruSAGE | arXiv:2512.18436 | ✅ |
| 18 | VeriStruct | arXiv:2510.25015 | ✅（TACAS 2026） |
| 19 | KVerus | arXiv:2605.03822 | ✅ |
| 20 | EXVERUS | arXiv:2603.25810 | ✅ |
| 21 | Atmosphere | SOSP 2025 (mars-research pdf) | ✅ |
| 22 | VERISPECGEN | arXiv:2604.10392 | ✅ webfetch（12 Apr 2026） |
| 23 | CPL | NALOMA 2026 (aclanthology) | ✅ |
| 24 | LeVer | ACL 2026 (aclanthology) | ✅ |
| 25 | miniF2F-v2 | arXiv:2511.03108 | ✅（NeurIPS 2025） |
| 26 | atp-checkers (Faults in benchmarks) | arXiv:2606.29493 | ✅ |
| 27 | ProofGate | ICML 2026 AI4Math (openreview) | ✅ |

**注**：用户原始子问题提到的"通义 Proof（Alibaba）/智谱 GLM-Proof"在 2025–2026 未检索到对应系统；实际中国玩家为字节 Seed（最强，IMO 2025 5/6）、月之暗面 Kimina、腾讯 HunyuanProver 7B（Delta-Prover 表中 68.4%）、上海 AI Lab InternLM2.5-Step-Prover。

---

## 8. 📌 下一步

1. **P0｜复现最小闭环**：用 Kimina-Prover-RL-1.7B + kimina-lean-server，在 Neo-OS 现有 FormalLinux Lean4 模块上跑 conjecture-pool 实验，量化"trace→hypothesis→prove/disprove"的真实产出率与错位率（对标 miniF2F-v2 的 36% 端到端口径，不要信头条数）。
2. **P0｜建系统域基准**：从 Asterinas/Atmosphere 已验证模块抽取 (trace, spec, proof) 三元组，造一个 "Neo-SysF2F" 微基准——当前无系统域 ATP benchmark，这是 Neo-OS 的研究资产机会。
3. **P1｜对抗层**：照搬 VERISPECGEN 对抗测试 + LeVer Attacker，给 L2.5 加"找反例 trace"第三条路，缓解第 6 节的 trace-bug 固化风险。
4. **P1｜验证器加固**：锁定 Lean ≥4.20.0（修复 `apply?` bug），强制 `set option autoImplicit false`，no-axioms 规则，pin mathlib 版本——把 atp-checkers 的 398 类缺陷逐项建 checker。
5. **P2｜跨域蒸馏**：用 DeepSeek-Prover-V2-671B / Seed-Prover 做 teacher，对系统域 trace 生成 Lean4 规则做蒸馏数据，再 SFT 一个 7B 系统专用 prover（数据稀缺是核心瓶颈，蒸馏可破）。
