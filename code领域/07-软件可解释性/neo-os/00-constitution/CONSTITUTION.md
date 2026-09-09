# Neo-OS · 项目宪法

> **三条初心是项目的北极星**。所有探索、所有架构决策、所有 council 建议，都必须回到这三条做最终检验。本文件是"声称-验证"差距的校正锚——每当项目膨胀或迷失，回到这里。
>
> 立宪日期：2026-08-05
> 状态：v1.0（基于创始人原始三答 + 命门验证 + council 终审 + 32 路探索）

---

## 第一条 · 数据源：「从 Linux commit 蒸馏，本质是 C 语言与编译器知识」

### 原话
> "从 linux 的 commit 记录中蒸馏出来（本质是 c 语言以及编译器知识）"

### 含义
- **数据**：Linux kernel git history（~1.3M commits，~40% bug-fix，Fixes: 标签传统）
- **本质**：不是"Linux 特定知识"，而是**系统软件的跨 OS 通用因果律**（指针/并发/内存序/锁——C 语言 + 编译器 + 硬件交互的根本规律）
- **方法论**：commit 不是版本控制数据，是 30 年的 (事件, 因果) 配对语料

### 当前验证状态

| 子假设 | 状态 | 证据 |
|--------|------|------|
| commit 能蒸馏出三元组 | 🟢 通过（sglang 62%）| V25 报告 |
| **Linux kernel C commit** 能蒸馏 | 🟡 **待复现**（council C1）| 预研：中性 ~58%，Fixes: 子集 precision ≥90% |
| 蒸馏出的是**通用因果**（非 Linux 特定）| 🟡 间接支持 | sglang(Python) 与 kernel(C) 共享 bug 模式（索引/锁/同步）|
| C + 编译器知识可被 LLM 学到 | 🟢 支持 | 编译器 commit 蒸馏（D6）：LLVM ORE remarks 已结构化 |

### council 修正
**C1：必须在 Linux kernel C commit 上复现 V25**，不能只靠 sglang Python。这是唯一不能省的事。预测：中性 coverage ~58%（略低于 Python），但 Fixes: 标签子集 precision ≥90%（远超 Python）——**kernel 的因果更"硬"，质量更高，只是更难抽**。

### 本条初心的不变与变
- **不变**：commit 蒸馏是 L2 world model 的数据地基
- **变**：第一域可能不是 OS kernel（council 建议数据库/分布式先验证 pipeline），但 kernel 仍是长期核心靶子与 C/编译器知识的源头

---

## 第二条 · 可信度：「蒸馏出规则，用形式化证明来规约」

### 原话
> "可信度（蒸馏出规则，使用形式化证明来规约）"

### 含义
- **蒸馏规则**：LLM 从 commit 归纳因果规则（神经层，广覆盖，会幻觉）
- **形式化规约**：用 Lean4 验证规则 soundness（符号层，绝不撒谎）
- **架构**：神经符号三层——神经生成 → 符号验证 → 通过则输出（★★★），否则降级（★★ 软规则 / ★ LLM 直觉）

### 当前验证状态

| 子假设 | 状态 | 证据 |
|--------|------|------|
| Lean4 能表达 OS 不变式 | 🟢 通过 | V11：5 条不变式定义成功 |
| 关键性质可证 | 🟢 部分（toy 级）| V11：4 引理 + 主定理 `soundExplanation_acyclic` 通过 kernel |
| **非平凡 OS 规则**可形式化 | 🟡 **待验证**（council C2）| 候选：spinlock+preempt（需 trace 归纳，超 omega），草图已给 |
| 神经符号闭环（LLM→Lean4）工程化 | 🟢 先例存在 | leanda：Codex GPT-5.6 把 Tendermint TLAPS 迁移到 Lean4 |
| **autoformalize OS 规范**（中间桥梁）| 🟡 工具就绪 | 2026 autoformalize TC% 53→76%；Lean Copilot 2.08 步人工 |

### council 修正
**C2：V11 的 5 条 toy 全 omega-solvable，是"语法可行"非"语义可行"**。必须产出 ≥1 条**非平凡规则**（modeling 真实 OS 机制，证明超过 omega）。最佳候选：**spinlock + preempt_disable 交互**（1-2 人周，需 trace 归纳，omega 无能为力）。

### 深度洞察（来自 32 路探索）
- **Iris（分离逻辑）是更成熟的路线**，但绑定 Rocq（非 Lean4）。若要并发正确性，需接受 Rocq 技术栈或自建 Lean4 分离逻辑
- ** Cedar 范式 ≠ 定理证明**：Cedar 是运行时策略审计，不能表达归纳不变式。正确架构是**分层**——Cedar 做运行时门控，Lean4 做静态因果证明，规则 ID 共享
- **形式化的天花板**（来自算法信息论）：Chaitin 不完备定理 + Ashby 必要变异度律 = 形式化只保证"已写规则"被遵守，规则集完备性是 epistemic gap

### 本条初心的不变与变
- **不变**：神经符号是 soundness 的唯一可行路径（纯 LLM 会幻觉，纯形式化覆盖率低）
- **变**：形式化粒度从"全代码验证"（seL4，20 人年）降到"属性级 + 运行时监督"（Cedar 范式，数周）；非平凡规则是 Phase 1 必须攻克的

---

## 第三条 · 价值：「加快基础软件创新，减少领域知识 token 消耗」

### 原话
> "权衡（能有助于加快基础软件领域的创新，减少领域内知识token的消耗量）"

### 含义
- **CTC（Cognitive Token Cost）**：人理解系统所需的认知资源。资深 kernel 工程师 = 10 年训练（数百万"人脑 token"）
- **Neo-OS 的价值**：把领域知识压缩进 world model + 形式化规则，人只需问英文 → **降低 CTC 一个数量级**
- **终极目标**：降低门槛 = 扩大贡献者池 = 加速基础软件创新

### 当前验证状态

| 子假设 | 状态 | 证据 |
|--------|------|------|
| CTC 是可度量指标 | 🟢 概念清晰 | 三层讲解 × 认知负荷理论 × Bloom 2-sigma |
| Neo-OS 能降 CTC | 🟡 **待实证** | 教学场景实验设计已给（H1-H4，对标 Bloom 2-sigma）|
| "加快创新"成立 | 🟡 间接支持 | 降低门槛 = 扩大池子的逻辑成立，但需用户验证 |
| 用户愿为 CTC 降低付费 | 🔴 **存疑**（council）| CTC 是研究框架，不是产品策略；需具体价值命题 |

### council 修正
**CTC 是研究使命，不是商业命题**。"打破所有领域信息差"是给论文 reviewer / 投资人听的，不是给用户听的。Phase 1-2 需要具体的、可衡量的价值命题（如"PostgreSQL 执行计划解释准确率比 EXPLAIN 文档高 X%"）。

### 理论边界（来自算法信息论探索）
- **Kolmogorov 复杂度不可计算** → 完美解释不可达
- **Ashby 必要变异度律** → 解释器复杂度 ≥ 系统复杂度，否则必然漏报
- **CTC 有理论下限**：≈ O(K(系统))，不是可优化到零的工程指标
- **诚实结论**：Neo-OS 不是"打破一切信息差"，而是**在 Ashby 边界内、以可控信息损失换取可解释性的有损压缩器**

### 本条初心的不变与变
- **不变**：降低 CTC、加速创新是项目的终极价值锚
- **变**：从"消灭所有信息差"（过度承诺）降为"在边界内大幅压低 CTC 上界 + 诚实标注已达极限的红线区"

---

## 三条初心的统一：项目北极星

```
        第一条（数据）              第二条（可信）              第三条（价值）
    Linux commit 蒸馏    →    形式化证明规约    →    降低 CTC / 加速创新
        （地基）                  （支柱）                  （屋顶）
         L2                       L2.5                      L3
```

**三条初心 ↔ 四层架构**：
- 第一条 → L1（事件本体）+ L2（world model 蒸馏）
- 第二条 → L2.5（形式化规则）
- 第三条 → L3（英文输出）+ 整体价值衡量

**三条初心 ↔ council 4 前置条件**：
- C1（kernel 复现 V25）↔ 服务第一条
- C2（非平凡 Lean4 规则）↔ 服务第二条
- C3（锁定单一域）+ C4（Phase 3 串行）↔ 服务第三条（避免稀释，聚焦交付真实价值）

---

## 不变的东西 vs 变的东西

### 永远不变（项目根基）
1. 事件/trace 作为第一性实体
2. commit 蒸馏 + 形式化规约的神经符号架构
3. 降低 CTC、加速基础软件创新的使命
4. 反 Hurd 铁律：N=2 提取，N=1 不泛化

### 可以调整（策略层）
1. 第一域：从 OS kernel → **数据库查询规划器或分布式共识**（council 建议，更快验证）
2. 通用化节奏：从"立即所有领域"→ **单域深透后才扩**（防 Hurd 病）
3. 形式化语言：Lean4 为主，**Iris/Rocq 作为并发正确性的补充**（若需深度）
4. CTC 叙事：从"消灭信息差"（学术）→ **具体价值命题**（产品）

---

## 诚实声明：声称-验证差距校正

| 文档曾声称 | 真实验证状态 | 校正 |
|-----------|------------|------|
| "两个命门通过" | V25 在 sglang 通过，V11 是 toy 级 | 标注"工程管道验证"非"核心假设验证" |
| "全力推进 Phase 1" | council 判 CONDITIONAL-GO | 需先满足 C1-C4 |
| "通用可解释性基础设施" | N=0 验证下的愿景 | 标注"愿景"非"当前 scope" |
| "打破所有领域信息差" | Ashby 律给天花板 | 降为"在边界内大幅压低 CTC 上界" |

---

## 附录 · 引入 RL 的纪律（六条铁律）

> 来源：[B2 RL+系统软件 SOTA 调研](../02-research/rl/02c-rl-systems.md) §4.3（2026-08-05，基于 MLGO/AlphaEvolve/Cold-RL 生产案例 + Anthropic reward hacking 泛化证据 arXiv:2511.18397）
> 性质：**任何引入 RL 的子系统必须满足全部六条**。违反任一条，就不要用 RL。

Neo-OS 的 L2.5 形式化规则落在 RL 最不擅长的象限（复合 reward + 长程 + 系统域）。以下六条是从 2024-2026 生产级 RL 系统软件案例（MLGO inlining / AlphaEvolve Borg 调度 / Cold-RL NGINX cache）提炼的纪律，与反 Hurd 铁律完全一致：

1. **约束学习问题**（动作空间极窄）：如「选 1/1000 commit」而非「生成完整 Lean4 证明」。决策空间变宽，RL 胜率骤降（B2 §5.5）。
2. **训练与服务分离**：离线训练，在线只查表/推理。绝不把在线 RL policy 放性能关键路径。
3. **为失败设计**：硬 timeout + 启发式回退 + circuit breaker + 一键 kill switch。RL 必然偶发失效，必须有非 RL 兜底（Cold-RL 的 500µs timeout + LRU 回退是范式模板）。
4. **尊重操作现实**：产出必须是可审计的英文/代码，不是黑盒 policy。AlphaEvolve 之所以胜过 deep RL 在 Borg 上线，是因为 SRE 能逐行 review 进化算法产出的可读代码——**可审计性 > reward 高低**。
5. **有可程序化的 evaluator**：reward 必须是硬指标（size/hit ratio/TTL/Lean 接受），非主观判断。复合 reward（如「规则正确性」）是 RL 最难的，Neo-OS L2.5 正落此象限。
6. **被约束在「只重排已合法的选项」**：RL 只在已合法的候选里重排，不覆盖 admission/correctness。AlphaEvolve Borg 条件：不覆盖 admission 决策。

**红线（明确不做）**：
- ❌ 不用 RL 学习 Lean4 规则作为 L2.5 基座（R5§6 命门 + reward hacking 泛化 arXiv:2511.18397）
- ❌ 不用 RL 替代 eBPF tracer（反 Hurd：adapter 只读现有工具）
- ❌ 不把 RL policy 放性能关键路径而不加硬回退（Cold-RL 原则）

**RLVR 的能力边界（Limit of RLVR, arXiv:2504.13837, NeurIPS 2025 Oral）**：RLVR 只是「分布锐化器」，不扩展推理边界。在系统域，因 trace 先验可能 buggy（R5§6），RLVR 会**固化 bug = 完美证明错误规则**。因此 Neo-OS 的 RL 仅作辅助（commit active learning / rule sensitivity 打分），绝不作规则正确性的最终裁决——那条线由 ground truth（dsyme / 人工审计）守住。

---

## 最终判词

**三条初心是真的，且仍然成立。** 32 路探索 + 两次命门验证 + council 终审，没有推翻任何一条初心——反而让每条更扎实、更精确、更有边界。

**最大的收获**：从"消灭一切信息差"的浪漫，收敛到"**在 Ashby 边界内、用 commit 蒸馏 + 形式化规约 + trace 接地，把复杂软件的 CTC 上界大幅压低**"的可工程化命题。

**最大的风险**：不是技术，是**声称-验证差距**。本宪法作为校正锚，每季度对照一次。

---

*本宪法作为项目最高准则。任何架构决策、范围扩张、声称发布，必须回到这三条做最终检验。当项目膨胀或迷失时，回到这里。*

---

## 附录 · 引入 RL 的六条铁律（来自 `../02-research/rl` SYNTHESIS，2026-08-05）

> 用户曾考虑把 RL 作为 Neo-OS 的核心机制。经 `../02-research/rl` 6 份文档（基础+形式证明+科学发现+neo-os 集成+数学方向）系统调研，结论是 **RL 不应作 Neo-OS 基座，仅作辅助**。下列六条铁律作为"任何引入 RL 的决策"的 checklist。

| # | 铁律 | 证据 | 对 Neo-OS 的约束 |
|---|------|------|-----------------|
| 1 | **RL 不创造新能力**（分布锐化器非发现器）| Limit of RLVR（arXiv:2504.13837，NeurIPS 2025 Oral）证明 RLVR 只是分布锐化，不扩展能力边界 | L2.5 形式化基座**不可**用 RL 生成（RL 锐化已有规则，不发明新规则）|
| 2 | **reward hacking 会泛化** | Artho et al.（arXiv:2511.18397）实证 reward hacking 跨任务泛化 | 任何 RL 引入必须证明 reward 与真实不变式对齐（防 hacking 固化）|
| 3 | **系统域纯 DRL 是生产弃儿** | AlphaEvolve（arXiv:2506.13131）反向——选可读代码弃 RL；工业系统弃纯 DRL | Neo-OS 系统 adapter **禁用**纯 DRL 调度 |
| 4 | **GNoME ≠ RL**（是 active learning），**AlphaProof = 真 RL 发现** | GNoME 用 active learning 非归功 RL；AlphaProof 在数学域是真 RL 发现 | 区分"RL 标签"与"RL 实质"，不混用案例 |
| 5 | **RL + 形式化近乎空白**（蓝海 + 深渊）| 系统域 RL+形式化无先例（蓝海机会，但深渊风险）| 若探索此 niche，须接受无先例的高风险 |
| 6 | **RL 仅作辅助**，绝不作 L2.5 基座 | 五上收敛 | RL 可用于：① commit active learning（Phase 1 选高价值 commit）② Attacker v1（Phase 2，provenance 约束下的对抗生成）。**核心解释/形式化层禁用 RL** |

**研究 niche（若深入）**：系统域 AlphaProof——但 trace 是ground truth 而非 reward（这是 AlphaProof 没有的根本难点），属"蓝海+深渊"。

**判词**：Neo-OS 是**神经符号**架构（蒸馏 + 形式化），不是 RL 架构。RL 是辅助工具，不是核心机制。任何"用 RL 做 X"的提议，必须对照上述六条铁律逐一检验。

---

*附录立宪日期：2026-08-05。来源：`../02-research/rlSYNTHESIS.md`（6 份 RL 探索文档收敛）。*
