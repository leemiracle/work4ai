# Neo-OS

> **通用复杂软件可解释性基础设施**——把任意复杂软件（OS / 浏览器 / 编译器 / 游戏引擎 / GPU / 数据库 / 分布式 / 网络）的行为翻译成可证明的英文解释。
>
> 核心洞察：**所有重要软件都长成巨型工程，造成领域信息差。Neo-OS 用事件本体 + commit 蒸馏 world model + Lean4 形式化规则 + 英文输出，消灭这个信息差。**

---

## 一句话立场

> *Events as first-class citizens, distilled world models, formally verified rules, English explanations — eliminating the cognitive stack between humans and any complex software.*

---

## 为什么

软件领域的根本痛点：**信息差**。每个重要软件（Linux/Blink/LLVM/Unreal/Vulkan/PostgreSQL/K8s/TCP）都只有少数内部人真懂，外部人被术语墙挡住。这是创新瓶颈。

Neo-OS 把"理解系统"的认知成本（**Cognitive Token Cost, CTC**）从"10 年专家 + 几天定位"降到"一句英文提问 + 几秒回答"。

---

## 怎么做（四层架构）

```
L3  English Interface  ← 三层讲解 × 17视角 × 费曼门（继承 work4ai 方法论）
L2.5 Formal Rules     ← Lean4 形式化因果规则，保证 soundness
L2  World Model       ← 从软件历史蒸馏的领域世界模型（7B，本机常驻）
L1  Event Ontology    ← 一切都是 (event, cause) 对，eBPF + 硬件 trace
L0  Hardware          ← Intel PT / Arm CoreSight / NPU
```

**领域无关内核 + 薄 adapter**：引擎只认"五原子"（Event/State/Causality/Invariant/DecisionPoint），每个领域提供 trace/语料/锚点。

---

## 项目状态

🟢 **立项阶段 → Phase 1 启动临界**（council CONDITIONAL-GO → 可转 GO）
- ✅ 22 + 10 路并行深度探索完成（哲学/理论/技术/竞品/领域/红队）
- ✅ 立场、架构、路线图、研究问题、三条初心全部成文
- ✅ **C1 命门**（commit 蒸馏）：sglang N=100 (62%) + etcd/Raft N=89 (97%) + **kernel N=145 (100% root_cause, 57.9% 完整三元组)**
- ✅ **C2 命门**（形式化粒度）：5 toy + spinlock×preempt v2 (sorry=0) + Raft ElectionSafety/LogMatching 完整版
- ✅ **C3/C4**：第一域 = Raft + Phase 3 严格串行（Gate G1-G5）
- ✅ L2/L2.5/L3 prototype 全跑通（48 蒸馏规则 + 4 完整 Lean4 证明 + 三层英文讲解）
- ⏳ Phase 1 完整版（接真实 eBPF trace + 费曼门自动化 + 用户研究）

详见 [NEXT_STEPS.md](./NEXT_STEPS.md)。

---

## 项目结构

> **目录命名约定**：数字前缀（`00-` `01-`...）按"重要性递减 + 时间先后"排序；`90-` 是归档；`04-layers/` 严格对应四层架构。

```
neo-os/
├── README.md  ·  NEXT_STEPS.md       ← 入口（先读这俩）
│
├── 00-constitution/                  🟢 立项包（北极星，每次决策回这里）
│   ├── CONSTITUTION.md               ← 三条初心 + 引入 RL 六条铁律
│   ├── POSITION.md                   ← v2.0 立场（通用复杂软件可解释性基础设施）
│   ├── POSITION_PAPER.md             ← 论文版立场（含 Related Work）
│   ├── DESIGN.md                     ← 四层架构 + 五原子 + adapter 契约
│   ├── ROADMAP.md                    ← Phase 0-4 + Gate G1-G5 + 死法防线
│   └── COUNCIL_FINAL_REVIEW.md       ← council 终审（C1-C4 + 3 条建议）
│
├── 01-decisions/                     🟢 关键决策记录（按时间累积）
│   ├── FIRST_DOMAIN_DECISION.md      ← 第一域 = Raft（九维度对比）
│   ├── ADVERSARIAL_LAYER_DESIGN.md   ← 对抗层 v2.0（provenance-only）
│   ├── PROVENANCE_DESIGN.md          ← Provenance tag 设计
│   └── RESEARCH_QUESTIONS.md         ← 3 个 paper-grade 研究点
│
├── 02-research/                      🟡 研究整合（背景知识，按需查）
│   ├── EXPANDED_KNOWLEDGE.md         ← 22 路探索整合（知识核心）
│   ├── ROUND3_EXPLORATION.md         ← 第三波 10 路（聚焦 C1-C4）
│   ├── BREADTH_DEPTH_ANALYSIS.md     ← 广度×深度（10 维度 × 30 变量）
│   ├── LOCAL_ASSETS.md               ← ★ 本地资产索引（work4ai + workspace 全清单）
│   ├── deep/                         ← 深度调研（R2/R4/R5/SYNTHESIS/ORACLE_REVIEW）
│   └── rl/                           ← RL 探索闭环（6 报告 + SYNTHESIS + 实验脚本）
│
├── 03-methodology/                   🟠 ★ work4ai 方法论契约层（不复制内容，只建引用）
│   ├── README.md                     ← 契约 5 条 + 目录入口
│   ├── from-work4ai.md               ← work4ai 资产 → Neo-OS 层映射（A-F 6 类）
│   └── trace-native-upgrade.md       ← Neo-OS 唯一原创：trace 实证升级（paper-grade 贡献）
│
├── 04-layers/                        🔴 四层架构实现（按架构语义分，原型已跑通）
│   ├── l1-event-ontology/            ← Phase 1 才动手（eBPF + 硬件 PT）
│   ├── l2-world-model/               ← C1 命门（commit 蒸馏 pipeline + 数据）
│   │   ├── c1_pipeline/              ← 抽取脚本（c1_pipeline.py + L2 audit + L2 distill）
│   │   └── data/                     ← 抽取结果（sglang/etcd/kernel 三域 jsonl + 报告）
│   ├── l2_5-formal-rules/            ← C2 命门（Lean4 形式化）
│   │   └── formal-seed/              ← 5 toy + spinlock + Raft 3 定理 + DistilledRules 48 条
│   └── l3-explain/                   ← ★ 继承 work4ai 三层讲透（l3_explain.py）
│
├── 05-adapters/                      🟢 领域 adapter（Phase 3 才扩展，反 Hurd 锁单域）
│   └── raft/                         ← 第一域占位（Jepsen + dsyme + TLA+ 三重 ground truth）
│
├── 06-adversarial/                   🟢 对抗层（独立研究流，tridirectional v0 跑通）
│
├── 07-experiments/                   🟢 实验脚本（pass@k 等）
│   └── pass-k/
│
└── 90-archive/                       ⚪ 历史版本（POSITION_PAPER 草稿等）
```

### 文档导航（按角色推荐）

| 你是… | 先读 |
|---|---|
| **第一次接触本项目** | `README.md` → `00-constitution/POSITION.md` → `00-constitution/CONSTITUTION.md` |
| **接手继续开发** | `NEXT_STEPS.md` → `00-constitution/ROADMAP.md` → `00-constitution/COUNCIL_FINAL_REVIEW.md` |
| **想做 L1/L2/L2.5/L3 实现** | `00-constitution/DESIGN.md` → `04-layers/<对应层>/` |
| **想理解 work4ai 关系** | `03-methodology/README.md` → `03-methodology/from-work4ai.md` |
| **想看 22 路探索** | `02-research/EXPANDED_KNOWLEDGE.md` → `02-research/deep/SYNTHESIS.md` |
| **想看研究成果** | `01-decisions/RESEARCH_QUESTIONS.md` → `02-research/rl/00-SYNTHESIS.md` |

---

## 核心纪律

> **"深度上专精，方法上通用。框架是提取出来的，不是设计出来的。"**
>
> 永远从 N=2 提取，不从 N=1 泛化——反 Hurd 铁律。

---

## 灵感来源

- **Unix 一切皆文件** → 升级为"一切皆事件"（过程哲学落地）
- **DTrace/eBPF** → 可观测性从工具升为 OS 根
- **seL4** → 形式化从验证代码扩到验证解释规则
- **AlphaProof** → 神经符号闭环（LLM 生成 + Lean4 验证）
- **work4ai 费曼学习法** → "讲透任意领域"方法论运行时化（详见 [`03-methodology/`](./03-methodology/)）
- **Bloom 2-sigma** → 一对一辅导的可扩展化

---

## 与 work4ai 的关系

`work4ai`（同机 `../work4ai/`）是 **Neo-OS 的方法论内核**——不是知识资产，是**解释引擎的灵魂**。

| 维度 | 关系 |
|---|---|
| **继承** | 三层讲解 × 17 视角 × 费曼门（→ L3 英文接口） |
| **借鉴** | 38 个讲透系列（→ 各层理论弹药） |
| **原创升级** | work4ai "代码实证层" → Neo-OS "trace 实证层"（可证伪性升级） |
| **契约层** | [`03-methodology/`](./03-methodology/) —— 不复制 work4ai 内容，只建引用映射 |

**完整资产映射**：[`02-research/LOCAL_ASSETS.md`](./02-research/LOCAL_ASSETS.md)（work4ai 60+ 主题 → Neo-OS 各层用途）
**升级设计**：[`03-methodology/trace-native-upgrade.md`](./03-methodology/trace-native-upgrade.md)（Neo-OS paper-grade 贡献声明）

---

## License（计划）

Apache 2.0（代码）+ CC-BY（模型权重）。影响力优先，非商业。

---

*项目立项于 2026-08。Neo-OS 是活项目，本文档随演进更新。*
