# 世界大模型 · AI4Science · AI4Math 全景

> **一份面向研究者与工程师的 AI 前沿终极调研卷 + 研究导航**
> **14 大模块 / 100+ 章节 / ~133 万字 / 1152 arXiv 引用 / 118 可运行实验 / 50 个研究课题**
> 覆盖 2024-2026 关键系统、技术栈、论文与开放问题，全部 arXiv ID 一手核实。
>
> 更新：2026-07-23 v2.1.8（含 22 轮深化：信创硬件 / 形式化验证 / 前沿跟踪 / 50 课题 / 3 实验执行 / 统一 Thesis）

---

## 0. 这是什么？

`world-ai4sci-math` 是一份**系统化深度调研**，回答三个问题：

1. **世界大模型**——AI 如何"理解"和"模拟"物理世界？从 Sora 到 Cosmos 到 VLA，技术怎么演化？
2. **AI4Science**——AI 怎么变成科研生产力？从 AlphaFold 到 rentosertib 进 Phase 3，产业如何重塑？
3. **AI4Math**——AI 能"做数学"吗？形式化证明与非形式化推理，两条路线怎么互补？

三大领域看似无关，实则共享同一套底层技术：**Transformer / Diffusion / Equivariant GNN / RL with verifiable rewards**。本卷既分领域深讲，也跨领域对照。

> **不只是知识库**——v2.1 新增了 **50 个研究课题 + 10 条学习路径 + 3 个课题实验执行 + 统一 Thesis**，让项目从"全景调研"升级为"研究导航 + 实验闭环"。详见 `docs/USAGE_GUIDE.md`。

---

## 1. 项目结构

```
world-ai4sci-math/   v2.1.8 / 14 大模块 / ~133 万字 / 1152 arXiv / 176 md + 118 py
│
├── README.md + CHANGELOG.md + EXPERIMENTS.md + LICENSE
│
├── 01-world-models/              (5 章)   世界大模型：视频生成 / VLA / 自驾 / JEPA
├── 02-ai4science/                (6 章)   AI4Science：蛋白 / 基因 / 药物 / 材料 / 气候
├── 03-ai4math/                   (4 章)   AI4Math：形式化证明 / 非形式推理 / 基准
├── 04-synthesis/                 (9 章)   交叉：共享架构 / 评估 / 前沿 / 超越LLM / 分布式 / OS / Linux
├── 05-model-engineering/         (14 章)  模型工程：架构 / 部署 / 读论文 / 验证 / 优化 + 5 个深处
├── 06-theoretical-foundations/   (7 章)   理论基础
├── 07-extended-tech/             (7 章)   扩展技术
├── 08-ai4x-applications/         (8 章)   AI4X 应用
├── 09-ai-philosophy-ethics/      (5 章)   哲学伦理
├── 10-emerging-fields/           (7 章)   新兴领域
├── 11-model-components-deep/     (9 md + 61 py)  ⭐ 模型组件深处：Attention / FFN / PE / Loss / Optimizer（+ KDA/AttnRes/Sessa/Inkling 前沿吸收）
├── 12-model-lifecycle-deep/      (6 md + 51 py)  ⭐ 生命周期深处：Pretrain / PEFT / RLHF / Eval / Deploy（+ §12 推测解码/KV Cache/量化矩阵 + §10 Certigrad4 + §13.6 国产 ARM 推理 + 实验结果回连）
├── 13-agent-systems-deep/        (13 章)  ⭐ Agent 系统深处：架构 / LLM集成 / Skill / 记忆 / 规划 / 多Agent / 评估 / 安全 / 编程 / CU / 研究 / 设计模式 / **§13 形式化验证（LeanDojo/AlphaProof/Certigrad4/sorry反例）**
├── 14-foundations-computation-physics/  (6 章)  ⭐ 计算数学物理基础：计算理论（+§2.6 Curry-Howard）/ 物理建模 / 概率 / 动力系统 / 数值分析（+§11 飞腾 D3000 国产 ARM + 实验结果回连）
└── docs/                         导航层（见下方）
```

### docs/ 导航层（v2.1 新增）

```
docs/
├── USAGE_GUIDE.md           ★ 项目使用说明书（入口：3 种场景 + 快速查找）
├── research-topics-50.md    ★ 50 个研究课题（5 数学 + 6 应用方向）
├── learning-paths.md        ★ 10 条学习路径（从零到能做）
├── top-20-insights.md       ★ 20 个核心洞察（5 分钟精华）
├── ten-lessons.md           ★ 10 个最大教训（元经验）
├── frontier-briefing-2026-07.md  2026-07 前沿简报（5 个重大前沿）
├── frontier-deep-dive/      5 个深化（Kimi K3 / Inkling / Sessa / SciReasoner / MXFP4）
├── research-execution/      ★ 1 Thesis + 3 报告 + 4 独立.py（3 课题已执行）
├── cross-module-synthesis   信创 × 形式化双线连接图
├── decision-records/        决策记录（为什么选这些方案）
├── RELEASE_CHECKLIST.md     发布前检查清单
├── roadmap.md               学习路径（旧版）
├── top-venues.md            顶会/顶刊列表
└── top-journals-science-ai.md 科学 AI 期刊
```

---

## 2. 三大领域速览（30 秒抓住要点）

| 维度 | 世界大模型 | AI4Science | AI4Math |
|---|---|---|---|
| **核心问题** | AI 怎么"演"未来？ | AI 怎么做科研伙伴？ | AI 能"证明"和"推理"吗？ |
| **代表系统** | Sora 2 / Cosmos / Genie 3 / π0 | AlphaFold 3 / rentosertib / GraphCast / GNoME | AlphaProof / DeepSeek-R1 / AlphaGeometry |
| **核心架构** | Diffusion Transformer + Flow Matching | Equivariant GNN + Diffusion | MCTS + RLVR + LLM |
| **数据来源** | 视频 / 遥操作 / 仿真 | PDB / ChEMBL / ERA5 / mathlib4 | PRM800K / NuminaMath |
| **评估基准** | Physics-IQ / VBench / LIBERO | GDT_TS / FID / WeatherBench | miniF2F / FrontierMath / IMO |
| **里程碑年** | 2024-02 Sora | 2020 AlphaFold 2 ｜ 2024 AF3 ｜ 2026 rentosertib Phase 3 | 2024 AlphaProof IMO 银 ｜ 2025 IMO 金 |
| **工业玩家** | OpenAI / Google / NVIDIA / Meta / 字节 / 阿里 / 腾讯 / 快手 | DeepMind / Isomorphic / Insilico / Recursion / 晶泰 / 深势 | DeepMind / OpenAI / DeepSeek / Moonshot |

---

## 3. 三条推荐阅读路径

### 路径 A：**通识路线**（5-8 小时，决策者 / 投资人）

按顺序读：
1. 本 README（10 分钟）
2. `01-world-models/00-README.md` 总览（1 小时）
3. `02-ai4science/00-README.md` 总览（1 小时）
4. `03-ai4math/00-README.md` 总览（1 小时）
5. `04-synthesis/03-frontier-2026.md` 前沿（1 小时）
6. `04-synthesis/02-evaluation-open-problems.md` 开放问题（1 小时）

### 路径 B：**工程师路线**（30-50 小时，想做项目）

1. 路径 A 全部
2. 挑一个最感兴趣的子领域深读（建议从 `02-ai4science/03-drug-discovery.md` 或 `01-world-models/01-video-generation.md` 入手）
3. 跟着每章末尾的"复现指引"跑通一个 demo：
   - 视频：跑 Open-Sora 1.2 / Wan 2.1
   - 具身：用 LeRobot 跑 Diffusion Policy
   - 蛋白质：ColabFold 浏览器预测任意序列
   - 数学：跑 DeepSeek-R1-Distill 在 AIME
4. 选一个未解小问题做扩展

### 路径 C：**研究者路线**（3-6 个月，想发 paper）

1. 路径 B 全部
2. 把 04-synthesis 的"开放问题"挨个想清楚
3. 在 [Papers with Code](https://paperswithcode.com) 找对应 benchmark 排行榜
4. 重读 5-10 篇标杆论文（每章末尾的"📌 进一步阅读"已列出）
5. 复现一篇 SOTA 论文（看你的算力）

---

## 4. 学习方法建议

### 4.1 「三层讲透」原则

本卷的每一章都尽量遵循：
- **直觉层**：1 句话比喻 + 为什么需要它（先于公式）
- **数学层**：关键公式 + 推导主线 + 适用边界
- **代码层**：最小可运行示例 + 复现指引

### 4.2 「输出倒逼输入」

读每章时，强迫自己写：
- 1 段 100 字的「TL;DR」
- 3 个关键概念的关系图
- 1 个让朋友能听懂的比喻

### 4.3 「一手核实」纪律

本卷所有 arXiv ID 均经 arXiv API 一手核实。其中委托人原始提示词中约 30-50% 的 ID 是错的（记忆版与官方版 ID 不一致、同名论文混淆、子领域误归属）。**永远不要凭记忆引用 arXiv ID**——用 `https://export.arxiv.org/api/query?id_list=XXXX.XXXXX` 30 秒就能验证。

---

## 5. 关键事实速查

### 5.1 已经"落地"的 AI 成就（不是 demo，是真用上的）

- **AlphaFold DB**：2 亿+蛋白质结构，已被 190 国 200 万+研究者使用
- **rentosertib (INS018_055)**：2026-07-07 启动 Phase III（NCT07687459）——**首个 AI 全程设计的小分子药物进 III 期**
- **GraphCast**：2023-09 起欧洲中期天气预报中心 ECMWF 业务化使用
- **Pangu-Weather**：华为，已在多个国家气象局部署
- **OpenAI o1 / o3**：在数学竞赛、编程竞赛上达到人类金牌水平

### 5.2 AI 还做不到的（开放问题）

- 在 FrontierMath（研究级数学题）上 SOTA 仍 < 5%
- 任何视频世界模型都无法稳定生成 60 秒以上的物理一致视频
- 自动定理证明在 miniF2F-test 通过率仍 < 70%
- 没有任何 AI 系统能从头证明一个未解数学猜想
- 没有任何 AI 设计的药物已上市（Phase 3 ≠ 上市）

---

## 6. 已知勘误（保留以提醒读者）

调研过程中纠正了若干常见错误，详见各章末尾"核实日志"：

- Ha & Schmidhuber 2018「World Models」arXiv 是 **1809.01999**（不是 1809.01986）
- Cosmos NVIDIA 论文 arXiv 是 **2501.03575**（不是 2501.18603）
- DreamerV2 是 **2010.02193**（2004.13612 是无关的 PCA 论文）
- Genie 1 是 **2402.15391**（不是 2402.05983）
- DeepSeek-Prover V1.5 是 **2408.08152**（不是 2408.08109）
- Sora / Sora 2 / Genie 2/3 / Veo 3 / Mochi-1 / Pika **没有正式 arXiv 论文**——只有官方 blog

---

## 7. 维护与更新

- **首次生成**：2026-07-20
- **生成方式**：13 个并行 delegate 联网调研 + 主编整合 + arXiv API 一手核实
- **代理配置**：本机若网络不通，使用 `export https_proxy=http://127.0.0.1:7890`
- **更新策略**：建议每月更新一次 `04-synthesis/03-frontier-2026.md`，每季度审校一次核心章节
- **贡献**：发现错误请直接修改对应 .md，并在文件末更新核实日志

---

## 📌 下一步

如果你是第一次读：从「路径 A 通识路线」开始，2 小时拿到全局视野。
如果你已经熟悉某领域：直接跳到对应章节的「2025-2026 关键论文」一节。
如果你想动手：每章末尾都有「复现指引」。

## ✍️ 思考题（开篇热身）

1. **三大领域共享什么底层技术？** 在你读完三章节总览后，写下你认为最重要的 3 个。
2. **如果只能选一个领域深耕 5 年，你选哪个？** 给出你的理由（兴趣 / 工业前景 / 数学美的吸引）。
3. **「AI 真懂物理 / 真懂化学 / 真懂数学」的判据是什么？** 是基准分数、是发现新知识、还是通过图灵测试？

---

<!-- 项目主 README，2026-07-20 由主编整合生成。全部 arXiv ID 经一手核实。 -->
