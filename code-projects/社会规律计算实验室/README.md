# 社会规律计算实验室 · 策展并入说明

> **来源**：`C:\workspace\social-laws`（个人研究仓库，源头无 .git）→ 2026-09-09 选择性并入本目录。
> **本 README 是策展说明**；源项目原总纲见 [`README-源项目.md`](README-源项目.md)，方法论总纲见 [`00-foundations/README.md`](00-foundations/README.md)。

---

## 1. 定位

这是一个**五段式规律卡实验室**：每条社会规律按同一结构写成一张卡——

**历史**（谁、在什么场景下发现）→ **直觉**（一句话比喻 + 为什么必须发生）→ **数学**（关键方程、推导主线、假设边界）→ **Python**（纯 NumPy/Matplotlib 从零实现并可视化）→ **批判**（局限、失败模式、误用风险）。

组织方式**以子领域为主轴**（关系/合作/不平等/权力政治/文化认知/市场城市/交叉），方法是工具箱——研究革命同时用博弈论+相变+网络，研究不平等同时用 ABM+统计+经济学。

**双轨校准是本库的独特资产**：西方经典理论（Granovetter/Watts/Barabási/Schelling/Ostrom/Nowak…）× **21 篇 NCPSSD 抓取核实的 CSSCI 顶刊论文全文**（索引见 [`docs/cssci-real-papers.md`](docs/cssci-real-papers.md)，PDF 在 [`papers/`](papers/)），另有 7 篇国际论文与 5 组中西学者逐篇对照（[`papers/international/comparisons/`](papers/international/comparisons/)）。每个模型都能回答："中国顶刊上对应的研究做到了哪一步？"

---

## 2. 收录范围表

| 来源 | 处置 | 收录内容 |
|---|---|---|
| 根 `README.md` | 收（改名避让本策展 README） | [`README-源项目.md`](README-源项目.md) |
| `00-foundations/` | 收总纲 | `README.md`（方法论 primer） |
| `01-relations/` | **只收 md 弃 py** | `README.md`（含核心命题回顾+进阶批判） |
| `02-cooperation/` | **只收 md 弃 py** | `README.md` + 3 张规律卡：`02-nash-math.md`（Nash 存在性证明）、`04-collective-action.md`（Olson vs Ostrom）、`05-five-rules-nowak.md`（Nowak 五规则） |
| `03-inequality/` | **整目录收** | README + 帕累托/Sugarscape 两 py + Piketty r>g 卡 |
| `04-power-politics/` | **整目录收** | README + Arrow 不可能卡 + 革命相变/极化涌现两 py |
| `05-culture-cognition/` | **整目录收** | README + 双传承卡 + 观点动力学 py |
| `06-markets-cities/` | **只收 md 弃 py** | `README.md`（含陆铭《倾斜城市》CSSCI 对接） |
| `07-crosscuts/` | **整目录收** | README + 算法极化/LLM 社会/四传统三卡 + cities-case + Schelling×梯度实验（py+png） |
| `docs/` | **整目录收** | 8 个文件：roadmap/math-primer/methodology/reading-list + CSSCI 三件套 + international-journals |
| `papers/` | **整目录收（PDF 原样）** | 78 文件：21 篇 CSSCI 全文 PDF + 7 篇国际 PDF + fulltext 文本 + 精读 md + 5 组中西对照 + 4 个数据 JSON |
| 顶层 14 张 PNG | **全部弃收** | 无任何收录 md 以链接引用它们（正文仅提及"py 会生成同名 png"）；已收 py 重跑即可再生 |
| 01/02/06 目录内 PNG | **全部弃收** | 同上，未被任何收录 md 引用 |
| `projects/` | **不收** | 空壳目录（5 个子目录无文件） |
| `notes/`、`scripts/ncpssd-crawler/` | **不收** | 过程笔记；爬虫脚本（7 py）已被 `papers/data/*.json` 成果取代 |

共 **112 文件**（28 PDF / 6 py / 77 md+txt+json）。

---

## 3. 等价物指针表（弃收主题 → 仓库既有实现）

01-relations / 02-cooperation / 06-markets-cities 的 10 个 py 因**仓库已有等价或更完整实现**而弃收，按下表直达替代物（所有路径已验证存在）：

| 弃收主题（源 .py） | 等价物 |
|---|---|
| 小世界 / 无标度（`01-relations/03-small-world.py`、`04-scale-free.py`） | [`../../讲透社会学/讲透数理社会学/experiments/networks_and_emergence.py`](../../讲透社会学/讲透数理社会学/experiments/networks_and_emergence.py)（幕二 WS 交叉带对数扫描、幕三 BA 枢纽性 vs ER 零模型，纯 random 实现） |
| 中心性（`01-relations/05-centrality-power.py`） | [`../../讲透社会学/讲透数理社会学/讲透社会网络分析/README.md`](../../讲透社会学/讲透数理社会学/讲透社会网络分析/README.md)（度/介数/特征向量三种中心性分刀法的理论正典；该宇宙实验脚本尚未落地中心性一幕） |
| 图论基础 / 弱连带（`01-relations/01-graph-basics.py`、`02-weak-ties.py`） | 同上支 README（结构支总纲，Granovetter 1973 在经典锚点列）；图生成的纯手写实现见上表 networks_and_emergence.py |
| 网络结构理论（子领域 1 的理论面） | [`../../讲透系统论/03-网络结构.md`](../../讲透系统论/03-网络结构.md) |
| 经典博弈 / Axelrod 锦标赛（`02-cooperation/01-classic-games.py`） | [`../../讲透数学/讲透博弈论/01-理性基石与占优.md`](../../讲透数学/讲透博弈论/01-理性基石与占优.md) + [`10-重复博弈与无名定理.md`](../../讲透数学/讲透博弈论/10-重复博弈与无名定理.md)（TFT 四美德/锦标赛重赛完整覆盖，配 [`experiments/lab01_dominance.py`](../../讲透数学/讲透博弈论/experiments/lab01_dominance.py)） |
| 演化博弈（`02-cooperation/03-evolutionary-game.py`） | [`../../讲透数学/讲透博弈论/11-演化博弈.md`](../../讲透数学/讲透博弈论/11-演化博弈.md)（配 [`experiments/lab05_ipd_evolution.py`](../../讲透数学/讲透博弈论/experiments/lab05_ipd_evolution.py)） |
| Schelling 隔离（`06-markets-cities/01-schelling.py`） | 讲透模型思维 10-社会篇(规划中)将以 10_schelling.py 独立实验呈现，源脚本已弃收。**现已可跑**：上表 networks_and_emergence.py 幕一即 20×20 网格 Schelling（温和偏好滚成完全隔离，断言式验证） |
| 城市规模法则 West 1.15（`06-markets-cities/02-scaling-laws.py`） | [`../../讲透模型/02-规模与ScalingLaws.md`](../../讲透模型/02-规模与ScalingLaws.md)（规模法则专章）；CSSCI 对照：陆铭《倾斜城市》全文在本库 [`papers/`](papers/) |
| 城市密度梯度（`06-markets-cities/03-density-gradient.py`） | [`../../讲透经济学/讲透城市经济学/03-可构造与结构.md`](../../讲透经济学/讲透城市经济学/03-可构造与结构.md)（Clark 1951 指数衰减密度曲线的可构造推导） |

> 纳什均衡的硬数学证明**没有弃收**——`02-cooperation/02-nash-math.md` 整卡收录在本库；更系统的展开见 [`../../讲透数学/讲透博弈论/02-纯策略纳什均衡.md`](../../讲透数学/讲透博弈论/02-纯策略纳什均衡.md)、[`03-混合策略.md`](../../讲透数学/讲透博弈论/03-混合策略.md)。

---

## 4. 代码资产索引

收录范围内共 6 个 py，全部为五段式规律卡的"代码"节，单文件可直接运行：

| 路径 | 对应社会规律 | 运行（依赖） | 产出 |
|---|---|---|---|
| [`03-inequality/01-pareto-distribution.py`](03-inequality/01-pareto-distribution.py) | 帕累托分布：乘性随机过程如何必然涌现 80/20 幂律（α 指数） | `python 01-pareto-distribution.py`（numpy+matplotlib） | 控制台推导 + `01-pareto-distribution.png`（四联图：分布演化/尾部拟合/三分布对比/洛伦兹曲线） |
| [`03-inequality/02-sugarscape.py`](03-inequality/02-sugarscape.py) | Sugarscape ABM：Epstein-Axtell 糖境中财富不平等从随机规则自发固化（基尼系数） | `python 02-sugarscape.py`（numpy+matplotlib+random） | 控制台仿真日志 + `02-sugarscape.png`（糖地形/财富分布演化/基尼 0.2→0.5+ 涌现） |
| [`04-power-politics/02-revolution-phase.py`](04-power-politics/02-revolution-phase.py) | 革命相变：Granovetter 阈值级联 + Kuran 双重偏好——为什么革命总是突然爆发 | `python 02-revolution-phase.py`（numpy+matplotlib） | 三种阈值分布的级联对比 + `02-revolution-phase.png`（含 f(R) 相变不动点图） |
| [`04-power-politics/03-polarization-emergence.py`](04-power-politics/03-polarization-emergence.py) | 极化涌现：Hegselmann-Krause 有界信任模型，ε 参数扫出共识→分裂 | `python 03-polarization-emergence.py`（numpy+matplotlib） | 各 ε 最终簇数 + `03-polarization-emergence.png`（ε-簇数扫描/算法放大实验） |
| [`05-culture-cognition/02-opinion-dynamics.py`](05-culture-cognition/02-opinion-dynamics.py) | 观点与扩散四连：DeGroot 共识 / 权威节点 / 网络 SIR（R₀ 临界）/ Bass 扩散 | `python 02-opinion-dynamics.py`（numpy+matplotlib；SIR 部分需 networkx） | 四模型对比 + `02-opinion-dynamics.png` |
| [`07-crosscuts/04-schelling-vs-gradient.py`](07-crosscuts/04-schelling-vs-gradient.py) | 交叉实验：Schelling 涌现的 2D 人口分布，其密度梯度 γ 是否与陆铭(2026)真实城市一致（公理传统×描述传统整合） | `python 04-schelling-vs-gradient.py`（numpy+matplotlib+random） | 控制台 γ 拟合对照 + 已存档 `04-schelling-vs-gradient.png`（注意：脚本内 savefig 写死绝对路径 `/data/usershare/...`，在本机重跑需改为相对路径） |

**未列于此表的源 py（01/02/06 共 10 个）均已弃收**，去向见第 3 节指针表。

---

## 5. 与讲透模型思维领域篇的分工

本实验室按社会子领域**整卡收藏规律 + CSSCI 实证校准**（全景纵深）；[`../../讲透模型/讲透模型思维/`](../../讲透模型/讲透模型思维/README.md) 领域篇则每篇只钉死一个可带回 AI 的建模教训——08-经济（均衡是假设不是事实：反身性）、10-社会（微观动机≠宏观行为：Schelling）、11-交通（容量是模型不是数字：幽灵堵塞）——重叠的 Schelling 脚本按"单教训归领域篇、子领域全景卡归本库"分家，两边互不为副本。
