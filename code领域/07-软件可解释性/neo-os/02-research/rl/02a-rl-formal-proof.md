# B1 · RL + 形式化证明（AlphaProof 后时代）2024-2026 SOTA

> 调研日期 2026-08-05 · 所有 arXiv ID 经 arxiv.org/abs/ 一手核实 · 来源：@general subagent（eager-indigo-otter）

## TL;DR

1. **AlphaProof（Nature 2025-11）确立范式**：AlphaZero 式 RL + MCTS + **TTRL（Test-Time RL）**，Lean 训练，~8000 万 autoformalized 问题。IMO 2024 银牌（28/42）。代价：每题 2-3 TPU-days，组合题未解。

2. **开源三强（DeepSeek-Prover V2 / Goedel-Prover V2 / Seed-Prover）逼近闭源**。配方：**GRPO + 二元 Lean reward + 子目标分解/猜想池**。Seed-Prover IMO 2025 解 5/6。但本质是 **expert iteration + 轻量 GRPO**，非 AlphaProof 式在线 MCTS。

3. **🟥 反方证据强劲**：Limit of RLVR（arXiv:2504.13837，NeurIPS 2025 Oral / ICML best paper）证明 **RLVR 只是"分布锐化"**，不扩展推理边界——base 在大 k 反超 RL model。**当前 RL 没教会模型任何 base 采不到的新东西**。

4. **根本难点：证的不是错规则**（与 Neo-OS R5§6 命门同构）。二元 reward 只判 Lean 接受与否，不判规则是否建模真实语义。FormalRewardBench 证明专门 prover 在评估证明质量上**反而最差（24.4%）**——生成≠判别。

5. **对 Neo-OS：RL 可接入但降级定位**。借鉴猜想生成 + autoformalization 数据管线，不做端到端证明。系统域没有 8000 万形式化问题，稀疏 reward 更致命。RL 仅做 provenance 打分/rule sensitivity。

---

## SOTA 全景

### A. MCTS + 在线 RL（AlphaProof 谱系，闭源极重）
- **AlphaProof**（Nature, doi:10.1038/s41586-025-09833-y ✅）：TTRL 对难题生成变体 focused RL，P1/P2/P6 各 2-3 TPU-days。组合题 P3/P5 未解。无后续论文/开源。
- **Pantograph**（Stanford）：Lean4 MCTS-enabling 接口，开源复现基础设施。

### B. Expert Iteration + 轻量 RL（开源主流）
| 模型 | arXiv | MiniF2F | 机制 |
|---|---|---|---|
| DeepSeek-Prover V2-671B | 2504.21801 ✅ | 88.9% | GRPO + 子目标分解冷启动 |
| Goedel-Prover V2-32B | 2508.03613 ✅ | 90.4% | scaffolded 合成数据 + verifier-guided self-correction |
| Seed-Prover（字节） | 2507.23726 ✅ | 99.6% | VAPO + 三档 test-time（heavy=5000 猜想池）|

### C. In-Context / Agent（非训练型）
- **COPRA**（2310.04353 ✅）：GPT-4 + 回溯搜索，穷人版 AlphaProof。
- **LeanDojo-v2**（NeurIPS 2025）：内置 GRPOTrainer + Pantograph RPC，接 DeepSeek-Prover-V2-671B。最完整开源工具栈。

### D. 猜想生成（2025 新兴）
- **LeanConjecturer**（2506.22005 ✅）：40 Mathlib 文件 → 12289 猜想，3776 非平凡。
- **RL-Lean**（GitHub Slim205）：PPO conjecturer，reward = pass rate + novelty + relatedness + diversity。
- **CPL**（NALOMA 2026）：迭代猜想+证明，重发现研究级拓扑定理。

### E. 过程奖励（对抗稀疏 reward）
- **Process-Verified RL**（2606.20068 ✅）：Lean 作 symbolic process oracle，first-error propagation。
- **FormalRewardBench**（2605.10141 ✅）：🚨 专门 prover 评估证明错误**最差（24.4%）**，frontier LLM 最好（59.8%）——生成≠判别。

---

## 对比矩阵

| 方法 | 算力 | 成熟度 | 系统域数据 |
|---|:---:|:---:|---|
| MCTS+在线RL | 🔴🔴🔴 | 研究 | ❌ 无 |
| Expert Iter+GRPO | 🟡 | 开源可用 | ❌ 无 |
| In-Context Agent | 🟢 | 可用 | ⚠️（CompCert）|
| 猜想生成 | 🟡 | 早期 | ⚡ 可迁移 |
| Process Reward | 🟡 | 研究 | ❌ 无 step oracle |

**关键空白** ⚡：所有 SOTA 几乎纯数学域。系统域形式化 RL **近乎空白**——seL4/CompCert 经典形式化无 RL；dsyme 716 定理人工。Neo-OS 若做 RL+形式化系统域是蓝海，也是无数据深渊。

---

## 对 Neo-OS 的启示

**结论：能接入，但降级为"辅助"非"引擎"，正面应对 R5§6 命门。**

### 可借鉴（低风险）
1. **合成数据管线**（DeepSeek 子目标 + LeanConjecturer）：commit 蒸馏的 (event,cause) 自动泛化变体
2. **LeanDojo-v2 + Pantograph**：接 SpinlockPreempt 跑 GRPO，但 reward 必须 provenance 驱动
3. **猜想生成扩 Inv**：缓解对抗层 v0 的盲点（1/5 判别力）

### 🟥 必须设防（R5§6 的 RL 版本）
- **二元 Lean reward = trace 固化 bug 的完美机制**。RL 把过窄易证 Inv 推到高 reward
- Limit of RLVR 直接警告：RL 不发现 base 采不到的规则——系统域长尾 bug 正是这种情况
- FormalRewardBench：能证≠能判

### 建议落点（与对抗层 v2.0 一致）
- v0：纯 provenance（不用 RL）—— 与 Oracle Review A1 一致
- v1+：RL 仅做 rule sensitivity scoring，reward 来自多源去相关+人工审计
- 红线：RL 证明的规则不直接接 L2.5 基座，必须经 ground truth gate

---

## 反面：根本难点

1. **稀疏 reward**（二元全有/全无）；系统域无 step-level oracle
2. **长程信用分配**：OS 行为轨迹非线性（并发/抢占）
3. **搜索空间爆炸**：系统域无 8000 万问题等价物
4. 🟥 **distribution sharpening 非真探索**（Limit of RLVR）：RLVR model pass@1 赢 base，但 base 大 k 反超。蒸馏引入新模式，RLVR 不能
5. Reward hacking / verifier gaming
6. 基准污染（MiniF2F 已饱和 99.6%）
7. 组合盲区（AlphaProof IMO 组合题未解）——系统域大量组合

---

## 引用清单（关键）

| 工作 | arXiv | 核实 |
|---|---|---|
| AlphaProof | Nature doi:10.1038/s41586-025-09833-y | ✅ |
| DeepSeek-Prover V2 | 2504.21801 | ✅ |
| Goedel-Prover V2 | 2508.03613 | ✅ |
| Seed-Prover | 2507.23726 | ✅ |
| **Limit of RLVR** | **2504.13837** | ✅ NeurIPS Oral |
| FormalRewardBench | 2605.10141 | ✅ |
| Process-Verified RL | 2606.20068 | ✅ |
| LeanConjecturer | 2506.22005 | ✅ |
| LeanDojo | 2306.15626 | ✅ |
| COPRA | 2310.04353 | ✅ |

---

## 📌 下一步

1. **立即**：LeanDojo-v2 GRPOTrainer + Pantograph 接 SpinlockPreempt v2，跑小规模 RL 微调，**观察是否复现 distribution sharpening**——系统域首次实证，有论文价值
2. **中风险**：RL-Lean conjecturer 移植系统域，扩 Inv，目标判别率 ≥80%
3. **红线**：跟踪 Seed-Prover 1.5 agentic RL，只学方法不接模型
4. **基准建设**：系统域无 MiniF2F，可切 dsyme 716 定理做"系统域 f2f"——蓝海+护城河
5. **监控反方**：若 RLVR 被证"不扩展边界"，Neo-OS RL 永久停"辅助打分"定位

> **一句话**：AlphaProof 后 RL+形式化数学域高歌猛进，但 2025-2026 反方浪潮揭示其本质是"分布锐化器"。对 Neo-OS，RL 是有价值的辅助（猜想生成、sensitivity 打分），但绝不能作规则正确性最终裁决——那条线必须由 ground truth 守住。
