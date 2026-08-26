# 讲透 Harness：让聪明模型变可靠的运行环境学（Harness Engineering）

> 知识卡宇宙：`讲透X` 系列 | 三层宪法：**直觉 → 公式 → 代码（bash 跑通）** | 五幕：直觉→数学→代码→不足→应用
> 定位：工程四部曲（`讲透Prompt`→`讲透Context`→`讲透Loop`→本单元）的**运行环境层收官**——Prompt 研究**单次调用里一句话怎么说**，Context 研究**一个窗口里放什么**，Loop 研究**循环怎么设计**，Harness 研究**这一切怎么组装成可靠长期运行的系统**。walkinglabs 四层栈 prompt→context→loop→graph，harness 是装下全部四层的那辆车。
> 本章证据标准：**每个知识点配一个真实可跑的实验**（`experiments/` 下 py + 结果 json/png），绝不停留在"教程说"。

## 为什么要有这个单元

walkinglabs 的核心立场："The Model Is Smart, The Harness Makes It Reliable"——
**模型决定写什么，harness 决定何时/何地/怎么写。Agent = Model + Harness。**
Anthropic 对照实验：同模型同任务，无 harness $9/20min 产出不可用；全套 harness $200/6h 产出可玩游戏。本单元的三个增量：

1. **实证化**：把"$9 vs $200"缩到本地可复现——同一个 Qwen2.5-0.5B，naive 单发 vs 最小生命周期 harness（SELECT→EXECUTE→验证→WRAP UP），真实完成率与**幻觉式完成率（false completion）**全部跑出数字（E1/E2/E3）；
2. **解剖学变成变量**：五子系统（Instructions/State/Verification/Scope/Lifecycle）不再是检查单，而是逐个拆下来消融的实验变量——去掉 Verification 会怎样？去掉 State 会怎样？（E2/E3 直接回答）
3. **NFL 直觉化**：AHE 消融实证"增益在 tools/middleware/长期记忆，仅改 system prompt 反而回退"——本单元用 E2 的"自评 vs 真执行"让它变得可触摸，Ch12 给出"harness 收益随模型能力饱和而衰减"的批判收尾。

## 核心心智模型（一图流）

```
   工程四部曲：说什么 → 给看什么 → 怎么循环 → 在哪跑
   ┌──────────────┬──────────────┬──────────────┬────────────────────────┐
   │ 讲透Prompt    │ 讲透Context  │ 讲透Loop      │ 讲透Harness（本单元）    │
   │ 一句话的信息设计│ 一个窗口的信息设计│ 循环的规格设计│ 整个运行环境的可靠性设计 │
   └──────────────┴──────────────┴──────────────┴────────────────────────┘

        模型（聪明但不可靠）
        ├─ 幻觉式完成：说"做完了"≠做完了
        ├─ 失忆：窗口一截断就忘了做过什么
        └─ 发散：没有停止条件会原地打转
   ┌─────────────────────────────────────────────┐
   │ Harness = 模型周围的一切（六组件 H=(E,T,C,S,L,V)）│
   │   E 执行循环   T 工具接口   C 上下文管理          │
   │   S 状态存储   V 验证接口   L 生命周期钩子         │
   │   （生产再加 O 可观测 / G 治理 —— Li 七层）        │
   └─────────────────────────────────────────────┘
        ↓
   可靠长期运行：测试绿=完成 · 账本在=可恢复 · 预算尽=必停止
```

## 篇目表（目录宪法）

| # | 章节 | 核心实验 | 状态 |
|---|------|---------|------|
| 00 | [开场白：从"怎么说"到"怎么跑"——工程四部曲收官](./00-开场白.md) | — | ✅ |
| 01 | [Agent = Model + Harness：模型不是瓶颈的证据链](./01-模型不是瓶颈.md) | E1 naive vs 最小harness ✅ | ✅ |
| 02 | [解剖学：五子系统/六组件/四综述切法的统一](./02-解剖学.md) | 组件×失败模式对照 | ✅ |
| 03 | [★ 验证即证据：幻觉式完成与 Goodhart](./03-验证即证据.md) | E2 验证器三级消融 ✅ | ✅ |
| 04 | [★ 状态与失忆：截断窗口下的账本救援](./04-状态与失忆.md) | E3 progress.md 对照 ✅ | ✅ |
| 05 | [Scope 与预算：发散、打转与熔断](./05-预算守卫.md) | E4 预算守卫 ✅ | ✅ |
| 06 | [生命周期：把决策权从模型手里拿走](./06-生命周期.md) | E5 SELECT 代码化 ✅ | ✅ |
| 07 | [上下文参数趋同解：四大 harness 对照](./07-上下文参数.md) | 参数核对（已核实） | ✅ |
| 08 | [多模型 harness：验证即级联](./08-多模型.md) | E6 验证级联 ✅（升级侧待 E6b） | ✅ |
| 09 | [★ Meta/Self/Evo：harness 优化 harness（AHE 实证）](./09-进化外环.md) | E7 mini 进化外环 ✅；讲透Loop E4 活案例 | ✅ |
| 10 | [★ 前沿 2025-2026：Harness-Bench 与配置级报告](./10-前沿2026.md) | 文献综述（Harness-Bench 已核实） | ✅ |
| 11 | [★ 活案例：五仓家族+2026-08-26 部署实录+本仓库自身](./11-活案例.md) | 现场分析 | ✅ |
| 12 | [不足与展望：NFL、harness dependence 与收益饱和](./12-不足与展望.md) | — | ✅ |

★ = 用户重点主题（验证 / 状态 / AHE / 前沿 / 活案例）。
**诚实状态（2026-08-26）**：00-12 章 + exercises + E1-E7 全部落盘；本地部署 deepseek-agent-harness（zhipu glm-5.3 coding plan 通道）e2e 完成（self-test ALL PASS + probe ALL PASS + 真实任务修复 bug 人工复核通过），部署档案 [QUICKSTART](../deepseek-agent-harness/QUICKSTART.md)。断点见 `RESUME-0826.md`。

## 实验环境（与讲透Prompt 同一基座，真实可复现）

- **本地**：Qwen2.5-0.5B-Instruct（transformers, CPU, `~/ai/models/`，thread=1 铁律）——**刻意选弱模型**：harness 的价值在"模型不完美"时最大，0.5B 的幻觉式完成正是最好的实验对象
- **API（备用）**：智谱 GLM（glm-4-flash / glm-5），密钥走 opencode auth.json，绝不硬编码
- **铁律**：①小模型 thread=1 ②实验独立可跑 ③结果存 json+png ④引用一律用已核实清单（`papers.md`）⑤长实验前台跑 timeout≥1500s

## 核心实验读数（2026-08-26 本机实测）

| 实验 | 核心数字 | 讲透什么 |
|---|---|---|
| **E1** naive vs 最小harness | 真实完成 4/6→5/6；naive **幻觉式完成 FCR=true**（自称 6/6 实际 4/6）；harness FCR **结构性 0**（测试不过不算完成）；代价：调用 2→8 | "$9 vs $200"的本地微型版：模型没变，环境变了 |
| **E2** 验证器三级消融 | V0 自评漏报 **2/13**（全集中在"看起来合理"的代码上）；V1 结构拦 6/13（只语法层）零误杀；成本阶梯 **V1≈0ms < V2≈3ms << V0≈3862ms** | 验证金字塔 L1/L2/L3 的检出/误杀/成本三维；自评不可当完成判定 |
| **E3** 状态与失忆 | 无账本=**100% 幻觉恢复**（乐观高报，声称全完成）；账本=信息充分但 0.5B 解析仅 1/3 完全对（把 pending 读成 done） | S 组件交付状态，**读取状态仍是模型能力**（harness dependence 本地版）；工程对策：SELECT 由 harness 代码执行，不问模型；meta 教训：解析器也是 harness（v1 解析 bug 曾高估幻觉） |

## 论述概念 → 核实锚点 → 本地实验（2026-08-26 映射表）

"harness 成为第一等公民"论述中的概念名，证据宪法处理：**真实实体给引用，论述性命名做映射，绝不虚构**（明细见 [papers.md](papers.md) §三）：

| 论述概念 | 状态 | 锚点 / 本地实验 |
|---|---|---|
| Harness-Bench（测 harness 不测模型） | ✅ **真实实体** arXiv:2605.27922 | 106 任务×6 harness×8 模型=5194 轨迹；NanoBot 76.2 vs OpenClaw 52.4（同模型池差 23.8 分）；**harness dependence：弱模型受 harness 影响更大** ← 与 E3"0.5B 读账本都出错"互证，与 AHE"收益随模型饱和衰减"互证 |
| Meta-Harness（生成 harness） | 论述性命名 | Trellis spec 晋升循环；AHE 外环（估→提取→优化→自动化）→ E7 待跑 |
| Self-Harness（运行时自调） | 论述性命名 | AHE 三观测性支柱；Guo Phase 4 co-evolution；harness_rl v4 双靶外环 |
| Evo-Harness（进化搜索） | 论述性命名 | AHE arXiv:2604.25850（+7.3pp；prompt-only 负收益）；**讲透Loop E4 双相外环**（本地已跑通：8%→53.3%，Goodhart 剪刀差） |
| 长程 Harness / 渐进披露 | 概念成立 | Anthropic 官方博客；讲透Skills E2 实测省 93.1% token |
| "隐式胶水→显式层→可优化对象" | 论述性框架 | = Guo 四范式演化（已核实），作 Ch02/Ch12 主线 |
| 技能库当工程对象（SkillX/Opt/Ops） | 论述性命名 | 讲透Skills 六线全核实（MCE/SkillRL/MemSkill/Memento-Skills）——Ch11 挂桥 |



## 与既有 harness 资产的分工（互不重复）

| 资产 | 层次 | 回答的问题 |
|------|------|-----------|
| [harness三综述合并解析](../讲透Agent/harness三综述合并解析.md) | 文献层 | 学界说了什么（四综述+Ensemble+领域，引用全核实）|
| [harness工程手册](../工程化手册库/harness工程手册/)（14 章） | 操作层 | 怎么改（检查单/参数表/急救路径）|
| [37 仓全景](../透视GitHub-Harness高星仓库全景.md) + [精华合入](../讲透Agent/harness精华合入-总入口.md) | 生态层 | 现成轮子在哪 |
| **本单元（讲透Harness）** | **实验层** | **为什么/多少增益/跑给你看——每个主张一个可复现实验** |

三部曲内部接口：`讲透Prompt/`（单条 prompt 是 harness 的 Instructions 组件的原料）、`讲透Context/`（窗口管理是 C 组件的深化）、本单元（把两者放进带验证与账本的运行循环）。

## 挂网（本单元的桥）

- 上游：`../讲透Prompt/`、`../讲透Context/`（三部曲前两部）
- 下游：`../讲透Agent/实战案例-Prover数学Agent/`（prover_harness.py = Ch11 活案例）、`../讲透Agent/实战案例-RL领域Agent/harness_rl/`（v4 全融合实跑）、`../deepseek-*-harness/` 五仓家族（插件化验证）
- 横向：`../工程化手册库/harness工程手册/`（本单元实验的操作层出口）、`../top-math-courses/MATH_LOOP_ENGINE.md`（验证即证据 = reward 可机器验证的同构）、`../讲透Agent/Agent工具设计-五类六原则-深读卡.md`（T 组件的设计方法论层：五类六原则 + 三代演进一手数字，2026-08-26）

## 来源与核实

- 学术引用沿用 2026-08-17/08-20 已核实清单 + **2026-08-26 新核实 Harness-Bench（arXiv:2605.27922，websearch 一手）**，全部状态见 [papers.md](papers.md)
- 工程参数（四大 harness 趋同解）沿用 Arize 2026-04-28 一手分析（已核实）
- E1-E3 实验数字为本机实测（2026-08-26），复现命令见各脚本头部注释
