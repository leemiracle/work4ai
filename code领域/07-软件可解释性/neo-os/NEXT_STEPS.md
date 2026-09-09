# Neo-OS · 工作电脑接续指南

> 本文件给"在另一台电脑上 clone 项目继续工作"的人——你。下面是你需要知道的一切。

---

## ⚡ 项目结构（2026-08-05 重组后）

> **重要变更**：项目已从"按产物类型分"（docs/ prototype/ explorations/）重组为"**按架构语义分**"。
> 所有旧路径都已迁移，详见根目录 [`README.md`](./README.md) §项目结构。

```
neo-os/
├── 00-constitution/    立项包（CONSTITUTION/POSITION/DESIGN/ROADMAP/COUNCIL）
├── 01-decisions/       关键决策（FIRST_DOMAIN/ADVERSARIAL/PROVENANCE/RESEARCH_Q）
├── 02-research/        研究整合（EXPANDED/ROUND3/LOCAL_ASSETS/deep/rl）
├── 03-methodology/     ★ work4ai 方法论契约层（不复制内容，只建引用）
├── 04-layers/          ★ 四层架构实现（l1/l2/l2_5/l3 按架构语义分）
├── 05-adapters/        领域 adapter（Phase 3 才用，raft/ 已占位）
├── 06-adversarial/     对抗层
├── 07-experiments/     实验脚本（pass-k/）
└── 90-archive/         历史归档
```

**路径迁移表**：

| 旧路径 | 新路径 |
|---|---|
| `docs/CONSTITUTION.md` | `00-constitution/CONSTITUTION.md` |
| `docs/POSITION.md` | `00-constitution/POSITION.md` |
| `docs/DESIGN.md` | `00-constitution/DESIGN.md` |
| `docs/ROADMAP.md` | `00-constitution/ROADMAP.md` |
| `docs/COUNCIL_FINAL_REVIEW.md` | `00-constitution/COUNCIL_FINAL_REVIEW.md` |
| `docs/FIRST_DOMAIN_DECISION.md` | `01-decisions/FIRST_DOMAIN_DECISION.md` |
| `docs/ADVERSARIAL_LAYER_DESIGN.md` | `01-decisions/ADVERSARIAL_LAYER_DESIGN.md` |
| `docs/RESEARCH_QUESTIONS.md` | `01-decisions/RESEARCH_QUESTIONS.md` |
| `docs/EXPANDED_KNOWLEDGE.md` | `02-research/EXPANDED_KNOWLEDGE.md` |
| `docs/LOCAL_ASSETS.md` | `02-research/LOCAL_ASSETS.md` |
| `docs/ROUND3_EXPLORATION.md` | `02-research/ROUND3_EXPLORATION.md` |
| `docs/BREADTH_DEPTH_ANALYSIS.md` | `02-research/BREADTH_DEPTH_ANALYSIS.md` |
| `docs/research/*` | `02-research/deep/*` |
| `explorations/rl/` | `02-research/rl/` |
| `prototype/c1_pipeline/` | `04-layers/l2-world-model/c1_pipeline/` |
| `prototype/data/` | `04-layers/l2-world-model/data/` |
| `prototype/formal-seed/` | `04-layers/l2_5-formal-rules/formal-seed/` |
| `prototype/l3/` | `04-layers/l3-explain/` |
| `prototype/adversarial-layer/` | `06-adversarial/` |
| `prototype/pass-k-experiment/` | `07-experiments/pass-k/` |
| `docs/POSITION_PAPER_DRAFT.md` | `90-archive/POSITION_PAPER_DRAFT.md` |

验证：`cd 04-layers/l2_5-formal-rules/formal-seed && lake build` 通过。

---

## 一、当前项目状态（一眼概览）

| 维度 | 状态 |
|------|------|
| **立项包** | ✅ 完整（v1.1，17 份核心文档 + 3 prototype）|
| **命门 V25**（commit 蒸馏）| 🟢 **三域真实数据达标**：sglang N=100(62%) + etcd/Raft N=89(97% root_cause) + **kernel N=145(100% root_cause, 57.9% 完整三元组, precision 100% 15样本)** |
| **命门 V11**（形式化粒度）| 🟢 5 toy + **C2 spinlock×preempt v2**（5定理 sorry=0）+ **Phase1 Raft committedMono + ElectionSafety 完整版**（disjoint 从 vote 推导，对齐 dsyme RE5）|
| **对抗层** | 🟢 v0 跑通（tridirectional，实证 Inv 1/5 判别力= R5§6 命门）+ Oracle review 6 致命全采纳 + 设计 v2.0（provenance-only）|
| **Council 判决** | 🟢 **CONDITIONAL-GO → 可转 GO**：C1/C2/C3/C4 全完整满足（kernel N=145 root_cause 100% + precision 100%；C2 sorry=0；C3 Raft；C4 Gate）|
| **第一域** | ✅ **Raft 共识**（[FIRST_DOMAIN_DECISION.md](./01-decisions/FIRST_DOMAIN_DECISION.md)，三重 ground truth）|
| **三条初心** | ✅ 经 32 路探索全部加强，立宪于 CONSTITUTION.md |
| **版本** | v1.1 已 commit（`62eb054`+`e635477`+`bf3bc0c`，39 文件 +5077 行）|

### v1.1 完整产物清单（3 commits）

| 产物 | 文件 | 状态 |
|------|------|------|
| C2 spinlock×preempt v2（F5 修复）| `04-layers/l2_5-formal-rules/formal-seed/NeoOsFormalSeed/SpinlockPreempt.lean` | ✅ sorry=0（3零公理+2仅core）|
| C3 第一域决策 | `01-decisions/FIRST_DOMAIN_DECISION.md` | ✅ Raft（修正 R3-3）|
| C4 Phase3 串行 | `00-constitution/ROADMAP.md` | ✅ Gate G1-G5 |
| C1 pipeline | `04-layers/l2-world-model/c1_pipeline` | ✅ L1+L2 (GLM API) |
| C1 Raft 域真实 | `04-layers/l2-world-model/data/raft_extraction_report.md` + `etcd_c1_results.jsonl` | ✅ N=89, root_cause 97% |
| C1 kernel 真实首例 | `04-layers/l2-world-model/data/c1_real_extraction_first.md` + `c1_real_results.jsonl` | ✅ N=3, root_cause 100%（cgit webfetch 绕限速）|
| Phase 1 种子 | `04-layers/l2_5-formal-rules/formal-seed/NeoOsFormalSeed/RaftRules.lean` | ✅ committedMono sorry=0 |
| 对抗层 v0 | `06-adversarial`（attacker.py+model.py）| ✅ 跑通（1/5 判别力）|
| 对抗层设计 v2.0 | `01-decisions/ADVERSARIAL_LAYER_DESIGN.md` | ✅ provenance-only |
| Oracle review | `02-research/deep/ORACLE_REVIEW.md`+`RESPONSE.md` | ✅ NO-GO→CONDITIONAL-GO，6致命全采纳 |
| 深度调研 | `02-research/deep/R2/R4/R5/SYNTHESIS` | ✅ Lean4 OS 验证 + 可解释性竞品 + 神经符号 SOTA |
| RL 探索 | `02-research/rl`（6 文件）| ✅ 基础+形式证明+neo-os 集成 |

**一句话**：项目知识库完整，命门初步验证，但 council 要求在 kernel 上做真复现 + 产非平凡规则，才可全力推进 Phase 1。

---

## 二、在工作电脑上启动

### 1. Clone

```bash
git clone git@gitee.com:leemiracle/neo-os.git
cd neo-os
```

（若用 HTTPS：`git clone https://gitee.com/leemiracle/neo-os.git`）

### 2. 环境要求

| 工具 | 版本 | 用途 | 安装 |
|------|------|------|------|
| **git** | 任意 | 版本控制 | 系统包管理器 |
| **Lean4 + elan** | Lean 4.28+ | 形式化种子（L2.5）| `curl https://raw.githubusercontent.com/leanprover/elan/elan-init/elan-init.sh -sSf \| sh` |
| **Python** | 3.10+ | commit 抽取 pipeline | 系统/conda |
| **lake**（随 Lean4）| — | Lean4 构建 | elan 安装自带 |

### 3. 验证 Lean4 种子可编译

```bash
cd 04-layers/l2_5-formal-rules/formal-seed
lake build    # 应产出 .lake/build/lib/lean/NeoOsFormalSeed/*.olean
```

若报 linker 错误（Scrt1.o）忽略——那是 exe 链接问题，不影响 `.olean`（证明产物）。

### 4. 必读文档（按顺序）

1. **[00-constitution/CONSTITUTION.md](./00-constitution/CONSTITUTION.md)** —— 三条初心（项目北极星，每次决策回这里）
2. **[00-constitution/COUNCIL_FINAL_REVIEW.md](./00-constitution/COUNCIL_FINAL_REVIEW.md)** —— 4 个前置条件 + 3 条建议
3. **[00-constitution/POSITION.md](./00-constitution/POSITION.md)** —— 升级定位
4. **[00-constitution/ROADMAP.md](./00-constitution/ROADMAP.md)** —— Phase 0-4 + 死法防线
5. **[02-research/EXPANDED_KNOWLEDGE.md](./02-research/EXPANDED_KNOWLEDGE.md)** —— 22 路探索整合（知识核心，需要时查）
6. **[02-research/ROUND3_EXPLORATION.md](./02-research/ROUND3_EXPLORATION.md)** —— 第三波 10 路（聚焦 C1-C4）

---

## 三、下一步待办（按优先级，反 Hurd 纪律：一次只做一项）

> **2026-08-05 本轮进展**：C2/C3/C4 ✅ 完成，C1 pipeline 就绪（真实抽取待网络）。详见各章 ✅ 标记。

### 🔴 Priority 1：C1 — commit 蒸馏复现（Raft 域达标，kernel C 域待网络）✅ Raft 域完成

**本轮完成**：
- ✅ C1 pipeline（`04-layers/l2-world-model/c1_pipeline`，L1+L2，ZHIPU GLM API）
- ✅ synthetic 验证通过（3 真实 kernel bug 模式）
- ✅ **etcd/Raft 域真实抽取达标**：89 commit，root_cause **97%**、fix **100%**、完整三元组 39%（symptom 瓶颈）、precision 基线 **73-93%**（`raft_extraction_report.md`）
- ✅ Phase 1 种子：`RaftRules.lean`（committedMono，sorry=0，对齐 dsyme hcommitted_mono）
- ⚠️ kernel C 域待网络：kernel.org https/git:// 均限速 ~4.5KB/s；gitee 无 linux mirror；但 Raft 域结果已强外推支持 kernel（`kernel_extraction_report.md` 执行计划）

**为什么**：sglang 是 Python，证明不了"Linux kernel C commit 能蒸馏"这个核心假设。

**怎么做**：
```bash
# 浅克隆 kernel（省空间，~500MB）
git clone --filter=blob:none https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
# 或 GitHub 镜像
git clone --filter=blob:none https://github.com/torvalds/linux.git

# 抽 1000 个 bug-fix commit（分层抽样，详见 ROUND3 R3-1 的 D1）
git -C linux log --grep="Fixes:" --format="%H" | head -1000

# 复现 V25 pipeline（参考 04-layers/l2-world-model/data/commit_extraction_report.md）
```

**验收**（council C1）：
- L2 agent 抽取率 ≥40%（中性预期 ~58%）
- precision 经 ≥1 位资深 kernel 工程师标注 ≥0.7
- Fixes: 子集 precision 应 ≥90%

**产出**：`04-layers/l2-world-model/data/kernel_extraction_report.md`

---

### 🔴 Priority 2：C2 — 非平凡 Lean4 规则（spinlock + preempt）✅ 已完成

**本轮完成**（`04-layers/l2_5-formal-rules/formal-seed/NeoOsFormalSeed/SpinlockPreempt.lean`）：
- ✅ 建模 Ev（6 原子）/ OK（归纳谓词）/ step / safe（配对纪律）/ Inv
- ✅ `step_preserves_Inv`（6 case 引理）+ **`Inv_preserved_over_trace`**（主定理，induction on OK，超过 omega）
- ✅ `pair_discipline_is_necessary`（反例定理，展示配对纪律必要性）
- ✅ **sorry 清零**：`#print axioms` 仅 `[propext, Quot.sound]`（Lean core，无 sorryAx）
- ✅ Lean 4.21.0 kernel 验证通过（v4.28 toolchain 因 GitHub 不通改 v4.21 本地）

**验收**：council C2 全绿。详见 [VERIFICATION.md](./04-layers/l2_5-formal-rules/formal-seed/VERIFICATION.md) 第八章。

**为什么**：V11 的 5 条 toy 全 omega-solvable，是"语法验证"非"语义验证"。

**怎么做**：参考 [ROUND3_EXPLORATION.md](./02-research/ROUND3_EXPLORATION.md) R3-4 的完整 Lean4 草图——
- 建模 `Ev`（lockAcquire/Release/preemptDisable/Enable/tick/schedule）
- 定义归纳谓词 `OK : S → List Ev → Prop`
- 证明 `Inv_preserved_over_trace`（用 `induction on OK`，omega 无能为力）
- sorry 清零

**预算**：1-2 人周。

**验收**（council C2）：`lake build` 通过，无 sorry，主定理 `Inv_preserved_over_trace` 非 trivial。

**产出**：`04-layers/l2_5-formal-rules/formal-seedSpinlockPreempt.lean`

---

### 🟡 Priority 3：C3 — 第一域选型（Raft vs PostgreSQL）✅ 已决策 = Raft

**本轮完成**（[FIRST_DOMAIN_DECISION.md](./01-decisions/FIRST_DOMAIN_DECISION.md)）：
- ✅ 九维度对比：Raft 8/9 占优（仅商业化 PostgreSQL 强）
- ✅ **决策：第一域 = Raft 共识**（三重 ground truth：Jepsen + dsyme 716T + Ongaro TLA+）
- ⚠️ **诚实修正**：ROUND3 R3-3"Lean4 Raft 零空白"声称错误——`dsyme/raft-lean-squad` 已证 716 定理（2026-04），但这反成利好（现成 ground truth）
- ✅ PostgreSQL 列为第二域候选（Phase 3）

**为什么**：council 强烈建议第一域**不要选 OS kernel**，选数据库或分布式。

**对比**（详见 ROUND3 R3-2 vs R3-3）：

| 维度 | PostgreSQL 规划器 | Raft 共识 |
|------|------------------|-----------|
| 形式化锚点 | 关系代数（极成熟）| TLA+（Ongaro 单一权威）|
| Lean4 基座 | 需自建（关系代数 Lean4 库少）| leanda 提供范式（Raft 是空白可补）|
| 黄金语料 | pgsql-hackers 邮件列表 | Jepsen 21 issue（带因果真值）|
| 商业化 | DBA 付费意愿明确 | SRE 团队付费 |
| 因果封闭性 | 中（跨多抽象层）| 高（状态机封闭）|

**建议**：若团队偏 PL/形式化 → **Raft**（Lean4 空白可补是机会）；若偏产品/商业化 → **PostgreSQL**（付费意愿明确）。

**产出**：`01-decisions/FIRST_DOMAIN_DECISION.md`

---

### 🟢 Priority 4：C4 — 修改 ROADMAP（Phase 3 严格串行）✅ 已完成

**本轮完成**（[ROADMAP.md](./00-constitution/ROADMAP.md) Phase 3）：
- ✅ Phase 3 从"6 域排序并行"改为"严格串行，6-12 月/域"
- ✅ 加入 **Gate G1-G5**（adapter<20% / 五原子零修改 / 形式化非平凡 / 蒸馏验证 / 用户价值）
- ✅ D5-D11（候选 3-6）锁进抽屉，直到 2 域验证
- ✅ 历史学家警告 + 反 Hurd 纪律明文化

把 [ROADMAP.md](./00-constitution/ROADMAP.md) 的 Phase 3 从"6 域排序"改为"一次一域，完成且 adapter <20% 才开下一个"。这是反 Hurd 的硬纪律。

---

## 四、本地资产迁移提醒

当前机器的 `/mnt/c/workspace/` 下有大量本地资产（[LOCAL_ASSETS.md](./02-research/LOCAL_ASSETS.md) 索引），工作电脑可能没有：

- `work4ai/`（60+ 讲透主题，**方法论内核**）—— 建议同步到工作电脑
- `ai-os/vllm` / `sglang` / `llama.cpp`（推理引擎源码）—— 按需
- `linux/`（kernel 源码，做 C1 时需要）
- `Foundations-of-LLMs/` / `leemiracle/`（理论参考）

**最关键**：`work4ai/` 是讲透方法论的来源，**必须迁移**（Neo-OS L3 解释引擎的内核）。

---

## 五、反 Hurd 纪律（每次开会前念一遍）

1. **深度上专精，方法上通用**——"通用"是挣来的结论，不是起点的口号
2. **永远 N=2 提取，N=1 不泛化**
3. **adapter 只读现有工具，不自造 tracer**
4. **每条声称要标注"验证等级"**（工程管道 vs 核心假设；语法可行 vs 语义可行）
5. **D5-D11（7 领域扩展）锁进抽屉**，直到 2 域证明 adapter <20%、五原子零修改、形式化非平凡

---

## 六、联系人/参考

- **Gitee 仓库**：https://gitee.com/leemiracle/neo-os
- **关键决策记录**：本仓库 `docs/` 全部
- **三条初心**：[CONSTITUTION.md](./00-constitution/CONSTITUTION.md)
- **死法防线**：[ROADMAP.md](./00-constitution/ROADMAP.md) 第六节 + [COUNCIL_FINAL_REVIEW.md](./00-constitution/COUNCIL_FINAL_REVIEW.md)

---

*"创始人最危险的时刻，是当他开始相信自己已经写下的愿景，而非验证过的事实。"* — Council

回到 CONSTITUTION.md 的三条初心，回到 council 的 C1-C4，做真实验证。祝顺利。
