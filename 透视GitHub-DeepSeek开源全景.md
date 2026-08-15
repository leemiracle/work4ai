---
card_id: ECO-DEEPSEEK
title: "透视GitHub：DeepSeek 开源全景（第四镜·单一组织纵深）"
universe: 生态观测
burke:
  scene: "deepseek-ai org 36 仓全量克隆深读（~10,692 文件，.tools/deepseek-repos/）"
  agent: "想看清一家公司如何用开源组织能力叙事的研究者"
  agency: "七簇深读（基座/内核/存储/多模态/效率/代码数学/harness）+ 星力分布 + 四波节奏"
  act: "把 36 仓当组织标本解剖：设计直觉、工程纪律、开源人格"
  purpose: "给'一次设计 vs 组件拼装'提供可证伪的组织级判据"
  tension: "单一组织 ≠ 单一设计——36 仓既有一以贯之的信念，也有断层与化石"
  arc: [第四镜定位, 36仓七簇清单, 星力分布与双峰, 七大洞察, 四波节奏, 知识网挂点]
status: done
refs:
  - ".research/deepseek/notes/A-G 七份底稿（行号级证据）"
  - "讲透DeepSeek/ 五幕精馏"
  - "Agent框架案例/deepseek-harness插件化框架/（16 篇）"
updated: 2026-08-15
---

# 🔭 第四镜：DeepSeek 开源全景（单一组织纵深）

> 三镜看生态（[`AI 高星全景`](透视GitHub-AI高星仓库全景.md) / [`Harness 全景`](透视GitHub-Harness高星仓库全景.md) / [`LLM 全景`](透视GitHub-LLM高星仓库全景.md)），第四镜反过来把镜头**推进单一组织内部**——deepseek-ai 36 仓全量浅克隆 + 七路并行深读，验证生态级规律是否在组织尺度复现。
>
> **方法**：36 仓本地克隆（`.tools/deepseek-repos/`，gitignored）→ 七簇并行深读 → 七份行号级底稿（`.research/deepseek/notes/A-G`）→ 五幕精馏（[`讲透DeepSeek/`](讲透DeepSeek/README.md)）。**证据纪律**：所有机制数字有 `文件:行号`；星数为抓取快照的外部元数据（仓内无法验证），仅对有出处者标注。

---

## 1. 36 仓七簇清单（组织解剖坐标系）

| 簇 | 底稿 | 仓库 | 一句话 |
|---|---|---|---|
| **A 基座** | `notes/A` | LLM(V1) / MoE / V2 / V3 / V3.2-Exp / R1 | 六代演进：稠密→细粒度 MoE→MLA→aux-loss-free+MTP+FP8→DSA→纯 RL 涌现推理 |
| **B 内核** | `notes/B` | DeepEP / DeepGEMM / FlashMLA / TileKernels / DualPipe / EPLB / LPLB / profile-data | 通信与算子内核层：EP 通信、JIT GEMM、MLA kernel、负载均衡、生产 profile |
| **C 存储** | `notes/C` | 3FS / smallpond / open-infra-index | 分布式文件系统（CRAQ+RDMA）+ DuckDB 轻框架 + infra 总索引 |
| **D 多模态** | `notes/D` | VL / VL2 / Janus(Pro/Flow) / DreamCraft3D / OCR / OCR-2 | 混合视觉编码→统一理解生成→"上下文裁剪式" OCR 蒸馏 |
| **E 效率** | `notes/E` | DeepSpec / ESFT / Engram | 投机解码工厂 / 专家级稀疏微调 / 秒级 MRU 记忆层 |
| **F 代码数学** | `notes/F` | Coder / Coder-V2 / Math / Math-V2 / Prover-V1.5 / Prover-V2 | 代码→数学→形式证明：GRPO 诞生地（Math）→verifier 飞轮（Math-V2） |
| **G harness** | `notes/G` | deepseek-harness(dsh) + awesome×3 | 官方 agent harness（Everything is a Plugin）+ 生态接线层三仓 |

## 2. 星力分布：双峰与化石

- **双峰星王**：模型侧 V3/R1（~104k，抓取快照）与 harness 侧 dsh（104k，外部元数据）并立——**"模型星王"与"接线星王"同代共存**，正是 Harness 镜"框架→harness"相变在组织内的复现。
- **跨度三个数量级**：从 104k 到 526 星——组织内注意力分布与生态级幂律同构（证据见 [`复杂系统迭代work4ai.md`](复杂系统迭代work4ai.md) §6 二增补）。
- **化石层**：awesome-deepseek-coder（807 星，内容停留 2023-11 Coder v1）vs awesome-deepseek-integration（39k，五语 93 项目）——**需求侧从"微调底座"到"接线现成 harness"的迁移**被同一 org 的三仓定格。
- **总星 ~51.6 万**（抓取快照合计，未逐仓复验）。

## 3. 七大组织级洞察

1. **稀疏性第一性**：MoE（细粒度专家）/ DSA（稀疏注意力）/ MLA（KV 压缩）/ Engram（MRU 哈希）/ ESFT（4-6/64 专家）/ OCR（上下文裁剪）——六层同一信念：**全量计算→按需激活**（详见 [`讲透DeepSeek/01`](讲透DeepSeek/01-直觉-一家公司的全栈开源.md)）。
2. **解析 cost model 优于 autotune**：DeepGEMM 把 L1/L2 cycle 写进公式（BLOCK_K==128 静态断言），封闭硬件上求全局最优而非网格搜索——与 autotune 流派的工程哲学分野。
3. **per-128 FP8 标度贯穿四层**：dispatch 分箱 / GEMM 分块 / KV cache 量化 / 权重布局共用同一粒度——**"一次设计"与"组件拼装"的可证伪判据**（跨层常数复用只有前者能做到）。
4. **负结果公开 = 组织人格**：至少五处公开负结果/失败对照（E 底稿"社区传闻纠偏清单"、dsh vendor 18 条修改审计、R1 论文 aha moment 的不确定披露）——开源不只是发权重，是发**认识论**。
5. **四波开源节奏 = 组织温度曲线**：2023-11 基座探路（LLM/Coder）→ 2024 架构革命（V2/MLA）→ 2025 infra 固化（开源周三件套 3FS/DeepEP/FlashMLA）→ 2025-10 起新轴（dsh，Apache 协议切换为标记）——探索期开架构、固化期交 infra、再升温开新轴。
6. **GRPO 超参链 = RL 激活能力的产业实证**：64/0.04→32/0.02→+一致性奖励→Math-V2 显式自评进奖励（R = R_format(0.76·R_proof + 0.24·R_self)）——三次演化方向一致：奖励函数本身在进化（产业实证桥：[`讲透RL/03 §5.1`](讲透RL/03-RLHF-DPO-GRPO.md)）。
7. **3FS specs/ 孤例**：用微软 P 语言对 CRAQ 协议做模型检查——**形式化验证走出数学、进入分布式系统的开源孤例**（接 [`讲透形式化验证/`](讲透形式化验证/README.md)）。

## 4. 诚实边界（本镜的测不准声明）

- 星数（104k/39k/5.8k/807 等）为抓取快照外部元数据，仓内无法验证——按本项目「宣称数字必须实测」纪律标注（gongwen-mastery 虚标教训），不做精确排名宣称。
- `--depth 1` 克隆无 git 历史：改动行数 power law（复杂系统 §6 预测 2）在组织内暂无法验证——负反馈留待全量克隆。
- Prover-V2 用的是 V3 非 V3.1；PutnamBench 数字论文/README 有 47 vs 49 差异（F 底稿核对）。
- dsh 处于 developer preview（`README.md:11` 明示破坏性变更），细节以当时 commit 为准（HEAD `47f943859b`）。

## 5. 知识网挂点（本镜的出口）

| 想深挖 | 去 |
|---|---|
| 五幕叙事（直觉→数学→代码→不足→应用） | [`讲透DeepSeek/`](讲透DeepSeek/README.md) |
| 行号级证据（七簇底稿） | `.research/deepseek/notes/A-G`（git 跟踪） |
| dsh 插件化框架 16 篇解剖 | [`Agent框架案例/deepseek-harness插件化框架/`](Agent框架案例/deepseek-harness插件化框架/README.md) |
| 组织级三证据（幂律/相变/温度） | [`复杂系统迭代work4ai.md`](复杂系统迭代work4ai.md) §6 二增补 |
| 20 小时精读路径 | [`讲透DeepSeek/03-代码-证据锚点与精读地图.md`](讲透DeepSeek/03-代码-证据锚点与精读地图.md) |

---

📌 **本镜一句话**：DeepSeek 把"开源"做成了组织级叙事工程——六层稀疏性信念、跨层常数复用、负结果入档、四波温度节奏；36 仓既是技术栈，也是一家公司把自己作为复杂系统的公开实验记录。
