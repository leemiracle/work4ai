# Harness 工程手册 · 入口

> **建立日期**：2026-08-17
> **触发**：你要把 agent 从"能跑 demo"带到"生产可靠"——瓶颈不在模型，在模型周围的一切
> **素材底座**：三份一手研究已核实合并——[harness 37 仓蒸馏](../../harness精华合入-总入口.md) + [三综述合并解析](../../harness三综述合并解析.md)（四篇 2026 综述 + Ensemble + 领域，引用全核实）+ GLM/Kimi 官方文档实测
> **宗旨**：把 harness 从" implicit 基础设施"变成"显式工程对象"——可解剖、可体检、可进化

---

## 🎯 一句话定位

**模型决定写什么，harness 决定何时/何地/怎么写。Agent = Model + Harness。**
90% 的人换更大的模型解决可靠性问题；本手册教你改环境——同模型 10× 可靠性提升的证据在这里。

---

## 📂 文件导航（按学习顺序）

### 🔴 认知（为什么 + 是什么）

| # | 文件 | 解决什么 |
|---|---|---|
| 01 | [`为什么需要harness`](01-为什么需要harness.md) | 模型已够聪明，harness 让它可靠（证据链：$9→$200 / 10× / AHE +7.3pp）|
| 02 | [`五子系统`](02-五子系统.md) | Instructions / State / Verification / Scope / Lifecycle——最小完备集 |
| 03 | [`六组件解剖`](03-六组件解剖.md) | H=(E,T,C,S,L,V) 逐件拆 + Completeness Matrix 自检 |

### 🟠 核心工程（上下文 / 状态 / 验证 / 生命周期）

| # | 文件 | 解决什么 |
|---|---|---|
| 04 | [`上下文管理参数表`](04-上下文管理参数表.md) | 四大 harness 趋同解全参数（可直接抄）+ 三层渐进披露 |
| 05 | [`状态与记忆`](05-状态与记忆.md) | 最小四文件起步 + 四层记忆架构 + git 化记忆 |
| 06 | [`验证即证据`](06-验证即证据.md) | 没跑通的测试不算完成——V 组件的工程化 |
| 07 | [`会话生命周期与交接`](07-会话生命周期与交接.md) | START/SELECT/EXECUTE/WRAP UP 仪式 + 崩溃恢复 + handoff |

### 🟡 进阶（多模型 / 模型方言 / 体检 / 进化）

| # | 文件 | 解决什么 |
|---|---|---|
| 08 | [`多模型harness`](08-多模型harness.md) | Router / Cascade / 端点路由（含 GLM-5.3 coding 端点实测）|
| 09 | [`模型方言适配`](09-模型方言适配.md) | thinking 参数跨家映射 + Preserved Thinking 铁律 |
| 10 | [`体检清单与反模式`](10-体检清单与反模式.md) | 五子系统体检单 + 12 条铁律（NFL 提炼）|
| 11 | [`自动进化闭环`](11-自动进化闭环.md) | 估 → 提取特征 → 优化 → 自动化（AHE 三观测性支柱）|
| 12 | [`最小harness实现`](12-最小harness实现.md) | 200 行代码骨架 + 把 OpenCode 当活教材剖一遍 |

### 🔵 地图与生态（2026-08-20 扩充，引用全核实）

| # | 文件 | 解决什么 |
|---|---|---|
| 13 | [`行为定位与HarnessHandbook`](13-行为定位与HarnessHandbook.md) | "该去哪改"——行为地图（L1/L2/L3+BGPD），AHE 管"怎么改"的读路径搭档（arXiv:2607.13285）|
| 14 | [`生态工具带2026`](14-生态工具带2026.md) | 现成轮子在哪——安全审计/可观测/调试/元进化家族/学习资源五条带 + 选型决策树 |

---

## 🚀 怎么用

### 路径 1（系统学）
- 01→03 建立认知（半天）
- 04→07 核心四件（一天，边读边对照自己的项目）
- 12 动手写最小 harness（半天）

### 路径 2（急救）
- agent 不可靠/提前宣布完成 → 直奔 [`10-体检`](10-体检清单与反模式.md)
- 长任务跑一半失忆 → [`05-状态`](05-状态与记忆.md) + [`07-生命周期`](07-会话生命周期与交接.md)
- 上下文爆炸 → [`04-参数表`](04-上下文管理参数表.md)
- 不知道去哪改/改漏实现点 → [`13-行为定位`](13-行为定位与HarnessHandbook.md)
- 要选安全/观测/调试/进化工具 → [`14-生态工具带`](14-生态工具带2026.md)

---

## 🗺️ 与其他手册的关系

```
prompt工程手册     = 驾驭模型的"语言侧"（怎么说）
harness工程手册    = 驾驭模型的"运行侧"（在哪跑、怎么验证、怎么续命）★本手册
Agents工程手册     = agent 的"内功"（规划/工具/记忆的概念）
ContextEngineering = 上下文的理论层；本手册 04 章 = 工程参数层
MCP工程手册        = 工具协议；本手册 T 组件的消费端
```

**与学术线的分工**：[harness三综述合并解析](../../harness三综述合并解析.md) 是文献地图与 NFL 分析；本手册是操作手册——引用它但不重复推导。

**与实验层的分工**（2026-08-26 新增）：[讲透Harness](../../讲透Harness/) 是本手册的实验科学层——每个主张一个本地可复现实验（E1 幻觉式完成 FCR / E2 验证器三级消融 / E3 崩溃恢复），并一手核实了 Harness-Bench（arXiv:2605.27922：106 任务×6 harness×8 模型，同模型池 harness 差 23.8 分）。手册管"怎么改"，它管"为什么/多少增益/跑给你看"。

**活案例**：[讲透Agent/实战案例-RL领域Agent/harness_rl](../../讲透Agent/实战案例-RL领域Agent/harness_rl/DESIGN.md)（v4）——手册 12 章技术的全融合实跑：配置即动作空间的 bandit 内环 + AHE 外环双靶迭代（自身 harness + RL 域 harness），manifest 记录 5 REVERT/2 COMMIT 的可证伪闭环全史。

**活案例·插件化**：[deepseek-kernel-harness](../../deepseek-kernel-harness/README.md)（v0.1，2026-08-18）——DeepSeek 引擎 + Linux kernel 领域插件：12 章骨架的 kernel 特化宿主 + 验证金字塔 L1-L4（checkpatch/sparse/build/boot）+ **02 章 #65-66 三种结构病的 graph 层落地**（goodhart_guards 反 gaming / global_conflicts 治盲区 / patch_queue 治并行冲突），`--self-test` 零依赖全绿。

**活案例·五成员家族**（2026-08-20，[deepseek-rust-harness](../../deepseek-rust-harness/README.md) + [deepseek-rl-harness](../../deepseek-rl-harness/README.md) + [deepseek-llm-harness](../../deepseek-llm-harness/README.md) + [deepseek-agent-harness](../../deepseek-agent-harness/README.md)）——**插件化命题的完整验证：换领域 = 换 tools/ + governance/ + AGENTS.md + knowledge/，宿主与引擎方言层（8 引擎）零改动**。五成员 = 五种验证范式：rust（编译期）/ rl（学习方向：训练冒烟+同 seed 复现）/ llm（生成质量：三级降级冒烟，实测 Qwen2.5-0.5B NLL=4.96）/ agent（行为审计：轨迹 schema 校验 + authorize 自举红线）。kernel/rust/rl/llm/agent 五仓均已独立 git（github.com/leemiracle，MIT）。

---

## ⚠️ 三个最重要反直觉

### 1. 模型不是瓶颈，harness 才是
同模型同任务：无 harness $9/20min 产出不可用；全套 harness $200/6h 产出可玩游戏。**先改环境再换模型**。

### 2. 提示词是 harness 投资的最后一站
AHE 消融实证：增益在 tools/middleware/长期记忆；**仅改 system prompt 反而回退**。

### 3. 趋同解可以抄，但不能盲抄
四大 harness 独立收敛到相同参数是强证据，但"趋同 ≠ 最优"——抄默认值后要用自己的任务回归验证。

---

**版本**：v1.1（2026-08-20：+13 行为定位章 +14 生态工具带章，本轮新增引用 10 项全核实；v1.0 2026-08-17）
**核心理念**：**模型是聪明的骑手，harness 是你修的路。你在车外设计路，而不是坐在车里打方向盘。**
