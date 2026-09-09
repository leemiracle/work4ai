# GPU MODE 资源全览（深度版）

> **一个聚焦 GPU 编程、kernel 性能优化、MLSys 系统工程的开源社区与每周 reading group。**
> 前身为 **CUDA MODE**（2024 年初由 Mark Saroufim + Andreas Koepf 发起，最初是 PMPP 书读书会），2024 年中更名 **GPU MODE** 以涵盖 CUDA/Triton/SYCL/Metal/ROCm 等异构平台。
>
> **整理日期**：2026-07-15
> **数据来源**：GitHub `gpu-mode` 组织 25 个仓库、`gpumode.com` 公开 API（`/api/events`、`/api/news`）、`kernelboard` 前端源码、Mark Saroufim 2026-01-22 官方回顾文、`reference-kernels` 167 个 issues/PRs
> **网络限制**：当前环境 YouTube / Discord / HuggingFace API / Bilibili / Invidious 全部不可达，所有数据均来自 GitHub 与 gpumode.com 直连

---

## 0. 速览（TL;DR）

| 指标 | 数据（截至 2026-07） |
|------|--------------------|
| **YouTube 讲座数** | **92+**（2025-11 官方公布 83，2026-01 公布 92，按周更新估计现已 100+ 期） |
| **lectures README 显式列** | 58 期（L1→L106，跳号，含 48 期仅有 YouTube 录像未入 README） |
| **lectures 仓库素材** | 34 个 `lecture_XXX/` 目录（含 notebook / slides / 代码） |
| **GitHub 组织** | `gpu-mode`，2023-12-27 创建，**2987 followers** |
| **最热仓库** | `lectures` ⭐6314 / `Triton-Puzzles` ⭐2522 / `resource-stream` ⭐2226 |
| **Discord 成员** | **24K+**（2026-01 公布） |
| **YouTube 订阅** | **26.6K**（2026-01 公布） |
| **KernelBot 累计提交** | **400K+** kernel 提交（2026-01） |
| **竞赛总奖金** | **3 个 $100K+ 比赛** + 多个 $28K-$150K hackathon |
| **Working Groups** | **20 个**活跃长期专题小组（见 §6） |
| **官方核心入口** | https://www.gpumode.com/ · Discord `discord.gg/gpumode` · YouTube `@GPUMODE` |

---

## 1. 组织起源与演化（来自 Mark Saroufim 2026-01-22 亲笔回顾）

### 1.1 时间线
- **2023-12-27**：GitHub 组织 `gpu-mode` 创建（前名 `cuda-mode`）
- **2024-01**：CUDA MODE 读书会启动，最初是 PMPP（*Programming Massively Parallel Processors*）书的 reading group
- **2024-02-03**：[Lecture 3 由 Jeremy Howard 主讲](https://www.youtube.com/watch?v=4sgKnKbR-WE) — 提出"用 Python 写 GPU 代码 + LLM 改写成 CUDA"，奠定社区气质
- **2024 年中**：**Karpathy 加入**，发起 [`llm.c`](https://github.com/karpathy/llm.c) working group — 用 raw CUDA 写训练循环，性能 beat `torch.compile`（核心贡献者：Arun Demeure、Erik Schultheis、Aleksa Gordic）
- **2024 年底**：**CUDA MODE IRL**（首个实体 hackathon）由 Casey Aylward 在 Accel 旧金山办公室举办 — 后来诞生了 `llm.q`、`KernelBench` 等项目
- **2024 年中→年底**：**改名 GPU MODE**（涵盖 SYCL/Metal/ROCm 等异构平台）
- **2025-04-15**：首个 **$100K AMD 比赛** 启动 — 30K+ kernel 提交，被 [Lisa Su 在 Advancing AI 大会舞台致谢](https://x.com/marksaroufim/status/1934712037881647607)
- **2025-06-24**：TriMul（Triangle Multiplicative Update）跨厂商竞赛启动（NVIDIA A100/H100/B200 + AMD MI300）
- **2025-08-30 → 10-13**：**AMD 第二次比赛**（$150K，40 MI300X，600+ devs，60K kernels）
- **2025-09-10**：与 Jane Street 合办东海岸 hackathon
- **2025-11-03**：与 NVIDIA + Sesterce + Dell 合办 **Blackwell NVFP4 比赛**（至 2026-02-20）
- **2025-11-05**：**GPU MODE IRL at Accel**（年度收官 hackathon，Nebius 赞助 215 B200）
- **2026-01-22**：Mark Saroufim 发表 [GPU MODE 2026 战略文](https://www.gpumode.com/news/gpumode-2026) — 全面转向 **Kernel LLM 训练**（popcorn 项目）
- **2026-02 → ongoing**：每周一期的 ScaleML 系列讲座 + 新竞赛（Linear Algebra on B200）

### 1.2 核心理念演化
- **2024 年**：读书会 — 教 GPU 编程入门
- **2025 年**：**Smooth difficulty curve**（Mark 的核心方法论）：
  1. Watch a lecture（看讲座）
  2. Participate in a kernel competition（参加 KernelBot 竞赛）
  3. Meet colleagues at a hackathon（线下 hackathon 见同好）
  4. Start a working group（发起长期项目）
- **2026 年**：**Shipping superhuman Kernel LLM**（开源训练能写 production-quality CUDA/Triton kernel 的 LLM，目标在 GTC 2026.3 + ICML 2026.7 ship 首批结果，已获 **Lambda $100K compute 赞助**）

---

## 2. 主站 `gpumode.com` 的 9 个 Tab

主站 = Flask 后端 [`kernelboard`](https://github.com/gpu-mode/kernelboard) + React/Vite 前端，9 个公开路由：

| Tab | URL | 内容 | 数据来源 |
|-----|-----|------|---------|
| **home** | `/` | 首页：使命、活跃 leaderboard 卡片 | 后端 `leaderboard` 表 |
| **lectures** | `/lectures` | **Events 页**：In-Person 活动 + Kernel Competitions + **即将到来的讲座**（从 Discord 拉取） | `/api/events`（公开） |
| **leaderboard** | `/leaderboard/{id}` | 每个 kernel 问题的实时榜单 | `/api/leaderboard`（部分公开） |
| **live** | `/live` | 直播页（讲座进行中跳转） | — |
| **news** | `/news` | **官方博客 12 篇**（hackathon 回顾、竞赛公告、2026 战略） | `/api/news`（公开） |
| **working-groups** | `/working-groups` | **20 个活跃工作组**入口 | hard-coded in `WorkingGroups.tsx` |
| **login** | `/login` | Discord OAuth | — |
| **privacy** | `/privacy` | 隐私政策 | — |
| **(api)** | `/api/*` | events / news / leaderboard / submission / auth / events | 见 `kernelboard/api/` |

### 关键公开 API 端点（无需鉴权，可直接 curl）
```bash
# 即将到来的 Discord 讲座（5 分钟缓存）
curl https://www.gpumode.com/api/events

# 12 篇官方博客全文（含 markdown）
curl https://www.gpumode.com/api/news
```

---

## 3. GitHub 组织全 25 个仓库（按 ⭐ 排序）

### 3.1 核心 educational 仓库（必看）

| # | Repo | ⭐ | 说明 |
|---|------|----|------|
| 1 | **[lectures](https://github.com/gpu-mode/lectures)** | 6314 | 每周讲座的代码、slides、notebook（见 §4 完整目录） |
| 2 | **[Triton-Puzzles](https://github.com/gpu-mode/Triton-Puzzles)** | 2522 | Tejas Ramesh + Keren Zhou 写的 Triton 解谜（基于 triton-viz，CPU 可跑） |
| 3 | **[resource-stream](https://github.com/gpu-mode/resource-stream)** | 2226 | 分类资源清单（CUDA 入门、书籍、论文、课程、Grandmasters）— 204 行金矿 |
| 4 | **[awesomeMLSys](https://github.com/gpu-mode/awesomeMLSys)** | 1100 | MLSys 论文阅读单：Attention / Quant / Long Context / Distributed / Speculative / Linear Attention |

### 3.2 工具与索引

| # | Repo | ⭐ | 说明 |
|---|------|----|------|
| 5 | [triton-index](https://github.com/gpu-mode/triton-index) | 311 | 公开 Triton kernel 目录（Hailey + Umer 维护） |
| 6 | [reference-kernels](https://github.com/gpu-mode/reference-kernels) | 288 | KernelBot 竞赛的参考解（**167 issues/PRs** 见 §5） |
| 7 | [profiling-cuda-in-torch](https://github.com/gpu-mode/profiling-cuda-in-torch) | 180 | Lecture 1 配套：`ncu` / `nsys` profiling 脚本 |
| 8 | [ring-attention](https://github.com/gpu-mode/ring-attention) | 171 | Ring Attention 实验仓库（Lecture 13 配套） |
| 9 | [popcorn-cli](https://github.com/gpu-mode/popcorn-cli) | 167 | 向 Discord cluster manager 提交 kernel 的 CLI |
| 10 | [kernelbot](https://github.com/gpu-mode/kernelbot) | 102 | Discord 上自动评测 / 评分 / 排榜的 bot 后端 |

### 3.3 基础设施 / Benchmark

| # | Repo | ⭐ | 说明 |
|---|------|----|------|
| 11 | pygpubench | 47 | PyTorch GPU kernel benchmarking |
| 12 | lecture2 | 30 | **已废弃**的旧 cuda-mode repo（演化证据） |
| 13 | popcorn | 25 | popcorn-cli 早期版本 |
| 14 | kernelboard | 17 | **gpumode.com 后端**：Flask + React/Vite |
| 15 | triton-tutorials | 16 | Triton 教程集合 |
| 16 | amd-cluster | 11 | 向 AMD cluster 提交作业（免费 MI300X 时段） |
| 17 | kernelguard | 11 | Kernel 正确性检查工具 |
| 18 | p2p-perf | 7 | 测不同 CUDA 设备 P2P 传输性能 |
| 19 | kernelbot-data | 3 | KernelBot 评测数据 + modal/deploy/AMD/Helion/NVIDIA workflows |
| 20 | leaderboard_cli | 3 | 本地评测 kernel 的 CLI |
| 21 | KernelSwarm | 2 | Kernel 评测的 swarm 调度 |
| 22 | axolotl | 1 | 玩笑 repo（"Go ahead and axolotl questions"） |

### 3.4 Hackathon 专属

| # | Repo | ⭐ | 说明 |
|---|------|----|------|
| 23 | paris-hackathon-2026-inference | 1 | 2026-04 巴黎 PyTorch Conf Europe 推理赛道 |
| 24 | paris-hackathon-2026-training | 1 | 2026-04 巴黎训练赛道 |
| 25 | cutlass-tutorial | 0 | CUTLASS 教程（Lecture 15、36 配套） |

---

## 4. 讲座完整目录（**README 显式 58 期 + 跳号 48 期 ≈ 100+ 实际期数**）

> **数字解释**：`## Lecture N` 标题在 README 中编号到 L106，但**跳号严重**。L1-L43 几乎连续（早期维护良好），L43 后大量跳号（后期维护跟不上）。
> 跳号讲座仍有 YouTube 录像但 lectures 仓库未公开素材/简介。
> 官方权威数字：**2025-11 = 83 期，2026-01 = 92 期**（Mark Saroufim 亲述）。当前估计 **100+ 期**。

### Phase 1：CUDA 与 PyTorch 入门（L1–L16，2024 Q1-Q2）

| # | 标题 | Speaker | 关键素材 |
|---|------|---------|---------|
| 1 | Profiling and Integrating CUDA kernels in PyTorch | **Mark Saroufim** | `lecture_001/`（ncu/nsys/load_inline/Triton square kernel 全套） |
| 2 | Recap Ch. 1–3 from PMPP book | **Andreas Koepf** | `lecture_002/cuda_mode_lecture2.pptx` |
| 3 | Getting Started With CUDA | **Jeremy Howard** | `lecture_003/` + [Colab](https://colab.research.google.com/drive/180uk6frvMBeT4tywhhYXmz3PJaCIA_uk) — **奠定社区气质的奠基讲座** |
| 4 | Intro to Compute and Memory Architecture | Thomas Viehmann | `lecture_004/` |
| 5 | Going Further with CUDA for Python Programmers | **Jeremy Howard** | `lecture_005/` |
| 6 | Optimizing PyTorch Optimizers | Jane Xu (PyTorch) | [Slides](https://docs.google.com/presentation/d/13WLCuxXzwu5JRZo0tAfW0hbKHQMvFw4O/edit) |
| 7 | Advanced Quantization | Charles Hernandez | [Slides](https://www.dropbox.com/scl/fi/hzfx1l267m8gwyhcjvfk4/Quantization-Cuda-vs-Triton.pdf) |
| 8 | CUDA Performance Checklist | Mark Saroufim | `lecture_008/` |
| 9 | Reductions | Mark Saroufim | `lecture_009/` |
| 10 | Build a Prod Ready CUDA Library | Oscar Amorus Huguet | [Slides](https://drive.google.com/drive/folders/158V8BzGj-IkdXXDAdHPNwUzDLNmr971_) |
| 11 | Sparsity | Jesse Cai | `lecture_011/sparsity.pptx` |
| 12 | Flash Attention | Thomas Viehmann | `lecture_012/` |
| 13 | Ring Attention | Andreas Koepf | `lecture_013/ring_attention.pptx` |
| 14 | Practitioner's Guide to Triton（**2024-04-13**） | **Umer Adil** | `lecture_014/A_Practitioners_Guide_to_Triton.ipynb` — **Triton 最佳入门讲座** |
| 15 | CUTLASS | Eric Auld | — |
| 16 | On Hands profiling | Taylor Robie | — |
| **Bonus** | CUDA C++ llm.cpp | Jake Hemstad & Georgii Evtushenko (NVIDIA) | [Slides](https://drive.google.com/drive/folders/1T-t0d_u0Xu8w_-1E5kAwmXNfF72x-HTA) |

### Phase 2：通信、Scan、Speculative（L17–L24，2024 Q2-Q3）

| # | 标题 | Speaker | 关键素材 |
|---|------|---------|---------|
| 17 | GPU Collective Communication (NCCL) | Dan Johnson (Stanford) | `lecture_017/` |
| 18 | Fused Kernels | Kapil Sharma | `lecture_018/` |
| 19 | Data Processing on GPUs | Devavret Makkar (PyTorch) | — |
| 20 | Scan Algorithm | **Izzat El Haj** | [Slides](https://docs.google.com/presentation/d/1MEMsE5LKi6ush_60hlYu3-cz4DUCFzSL/edit) |
| 21 | Scan Algorithm Part 2 | **Izzat El Haj** | 同上 |
| 22 | Hacker's Guide to Speculative Decoding in vLLM | Cade Daniel | [Slides](https://docs.google.com/presentation/d/1p1xE-EbSAnXpTSiSI0gmy_wdwxN5XaULO3AnCWWoRe4/edit) |
| 23 | Tensor Cores | **Vijay Thakkar & Pradeep Ramani** | [Slides](https://drive.google.com/file/d/18sthk6IUOKbdtFphpm_jZNXoJenbWR8m/view) |
| 24 | Scan at the Speed of Light | Jake Hemstad & Georgii Evtushenko | — |

### Phase 3：异构平台、应用层（L25–L34，2024 Q3-Q4）

| # | 标题 | Speaker | 关键素材 |
|---|------|---------|---------|
| 25 | Speaking Composable Kernel（AMD ROCm） | Haocong Wang | `lecture_025/AMD_ROCm_Speaking_Composable_Kernel_July_20_2024.pdf` |
| 26 | SYCL MODE（Intel GPU） | Patric Zhao (Intel) | [Slides](https://docs.google.com/presentation/d/1SW4XKomAJhhJSH5-jpZI9Qlwp7TEunbV/edit) |
| 27 | gpu.cpp | Austin Huang (Answer.AI) | [Slides](https://gpucpp-presentation.answer.ai/) |
| 28 | Liger Kernel | **Byron Hsu** (LinkedIn) | [Slides](https://docs.google.com/presentation/d/1CGTV-uKw9crrBo13q1jAzAFCFzlpZFjeL4bnK67pTd8/edit) + 5 个 Colab |
| 29 | Triton Internals | Kapil Sharma | `lecture_029/` |
| 30 | Quantized training | **Thien Tran (gau-nernst)** | `lecture_030/` |
| 31 | Beginners Guide to Metal Kernels | Nikita Shulga (Unsloth) | `lecture_031/` |
| 32 | Unsloth - LLM Systems Engineering | **Daniel Han** (Unsloth) | [Slides](https://docs.google.com/presentation/d/1BvgbDwvOY6Uy6jMuNXrmrz_6Km_CBW0f2espqeQaWfc/edit) |
| 33 | BitBLAS | Wang Lei | `lecture_033/` |
| 34 | Low Bit Triton Kernels | Hicham Badri (mobacham) | [Slides](https://docs.google.com/presentation/d/1R9B6RLOlAblyVVFPk9FtAq6MXR1ufj1NaT0bjjib7Vc/edit) |

### Phase 4：推理引擎、CUTLASS、SASS（L35–L43，2024 Q4）

| # | 标题 | Speaker | 关键素材 |
|---|------|---------|---------|
| 35 | SGLang Performance Optimization | Yineng Zhang | `lecture_035/SGLang-Performance-Optimization-YinengZhang.pdf` |
| 36 | CUTLASS and Flash Attention 3 | **Jay Shah** (Colfax) | `lecture_036/` |
| 37 | Intro to SASS & GPU Microarchitecture | **Arun Demeure** | `lecture_037/` |
| 38 | Lowbit kernels for ARM CPU | Scott Roy | `lecture_038/` |
| 39 | TorchTitan | Mark Saroufim & Tianyu Liu | — |
| 40 | FlashInfer | Zihao Ye (UW) | — |
| 41 | CUDA Docs for Humans | Charles Frye (Modal) | [Slides](https://docs.google.com/presentation/d/15lTG6aqf72Hyk5_lqH7iSrc8aP1ElEYxCxch-tD37PE/edit) |
| 42 | Mosaic GPU | **Adam Paszke** (PyTorch 作者) | — |
| 43 | Erik Schultheis | Erik Schultheis | `lecture_042/` |

### Phase 5：CuTE、Collectives、4-bit（L57–L70，2025 H2）

| # | 标题 | Speaker | 关键素材 |
|---|------|---------|---------|
| 57 | CuTE | **Cris Cecka** (NVIDIA) | `lecture_057/` |
| 67 | NCCL & NVSHMEM | **Jeff Hammond** (NVIDIA) | [Slides](https://drive.google.com/file/d/1T8uHhFIeVa_g1oYb_O4d2Ltb8YQly1zK/view) + [ParRes/Kernels Cxx11](https://github.com/ParRes/Kernels/tree/main/Cxx11) |
| 69 | Quartet 4-bit training | Roberto Castro & **Andrei Panferov** (IST-DASLab) | [Quartet paper](https://arxiv.org/abs/2505.14669) + [qutlass](https://github.com/isT-DASLab/qutlass) |
| 70 | Fault tolerant communication collectives | mike64_t | [Slides](https://docs.google.com/presentation/d/1MKB51lhNOsV-Y_hscSaJk7wZskzxft2pFJQZKyvcMyo/edit) |

### Phase 6：ScaleML 系列 + 多 GPU 编程（L71–L86，2025 Q3-Q4）

> **ScaleML Series**：与 Stanford/Berkeley 研究者合作的长上下文训练专题

| # | 标题 | Speaker | 关键素材 |
|---|------|---------|---------|
| 71 | [ScaleML] FlexOlmo: Open Language Models for Flexible Data Use | **Sewon Min** | `lecture_071/` |
| 72 | [ScaleML] Efficient & Effective Long-Context Modeling for LLMs | **Guangxuan Xiao** | `lecture_072/`（Attention Sinks + StreamingLLM） |
| 74 | [ScaleML] Positional Encodings and PaTH Attention | **Songlin Yang** | `lecture_074/` |
| 75 | [ScaleML] GPU Programming Fundamentals + ThunderKittens | **William Brandon** & **Simran Arora** | [Slides 1](https://docs.google.com/presentation/d/1ypi4IjEF36PUZGOJSaFxjNzk7BpO61TicdTBBf77oqc/) + `lecture_075/` |
| 78 | Iris: Multi-GPU Programming in Triton | Muhammad Awad, Muhammad Osama, Brandon Potter | `lecture_078/` |
| 79 | Mirage (MPK): Compiling LLMs into Mega Kernels | Mengdi Wu, Xinhao Cheng | `lecture_079/` |
| 84 | Numerics and AI | **Paulius Micikevicius** (NVIDIA, FP8 发明者本人) | `lecture_084/` |
| 86 | Introduction to CuTeDSL (for NVIDIA competition) | Vicki Wang | `lecture_086/` |

### Phase 7：最新前沿（L103–L106，Blackwell 时代）

| # | 标题 | Speaker | 关键素材 |
|---|------|---------|---------|
| 103 | Fundamentals of CuTe Layout Algebra and Category-theoretic Interpretation | Jack Carlisle & **Jay Shah** | `lecture_103/` |
| 104 | Gluon: Tile-Based GPU Programming with Low-Level Control | Peter Bell, Mario Lezcano, **Keren Zhou** | `lecture_104/` |
| 106 | HF kernels | Hugging Face | [Slides](https://docs.google.com/presentation/d/1RibAIrOJv0BcAx2QjNYHDZCrMfGYifTggtKT6uwv7CY/edit) |

### Phase 8：跳号讲座（**48 期，仅有 YouTube 录像**）

> 以下期数在 YouTube 频道有录像，但 lectures 仓库 README 未维护。
> 完整列表需登录 YouTube `@GPUMODE/videos` 自行浏览。
> **跳号列表**：L44, L45, L46, L47, L48, L49, L50, L51, L52, L53, L54, L55, L56, L58, L59, L60, L61, L62, L63, L64, L65, L66, L68, L73, L76, L77, L80, L81, L82, L83, L85, L87, L88, L89, L90, L91, L92, L93, L94, L95, L96, L97, L98, L99, L100, L101, L102, L105

### 即将到来（2026-07 ~ 08，来自 `/api/events` 实时拉取）

| 日期 | 标题 | 备注 |
|------|------|------|
| **2026-07-27 18:00 UTC** | **TIRx** | （TIR 相关，可能是 Tensor Inference Recursion） |
| **2026-07-31 18:00 UTC** | **GPU Fault Tolerance** | 容错 GPU 计算 |
| **2026-08-03 18:00 UTC** | **The 4-bitter lesson: Balancing Stability and Performance in NVFP4 RL** | by Ziang Li & friends at [humans&](https://humansand.ai/blog/nvfp4-rl) |

---

## 5. 内核竞赛与 Hackathon 全历史（来自 `/api/news` 12 篇 + `reference-kernels` 167 issues）

### 5.1 8 大 KernelBot 竞赛（来自 reference-kernels README）

| # | 竞赛 | 时间 | 奖金 / 规模 | 问题目录 |
|---|------|------|-----------|---------|
| 1 | **PMPP practice problems** | ongoing | 入门练手 | `problems/pmpp_v2` |
| 2 | **AMD $100K Inference Sprint** | 2025-04-15 → 06 | $100K，30K+ submissions，Lisa Su 舞台致谢 | `problems/amd` |
| 3 | **BioML kernels** | 2025 中 | 生物 ML | `problems/bioml` |
| 4 | **AMD $100K Distributed Kernel** | 2025-08-30 → 10-13 | $150K，40 MI300X，600+ devs，60K kernels | `problems/amd_distributed` |
| 5 | **NVIDIA Blackwell NVFP4** | 2025-11-03 → 2026-02-20 | 与 NVIDIA + Sesterce + Dell 合办 | `problems/nvidia` |
| 6 | **AMD $1.1M E2E Model Speedrun** | 2026-03-06 → 03-30 | **$1.1M**（最高奖金额） | `problems/amd_202602` |
| 7 | **Helion IRL Hackathon** | 2026-03-14（San Francisco） | Helion 内核优化 | `problems/helion` |
| 8 | **Linear Algebra Kernels For The Age Of Research** | 2026-06-12 起 | B200 上的 QR / eigh / Cholesky | `problems/linalg` |

### 5.2 高校合作

- **Stanford CS149 Assignment 5** — [stanford-cs149/asst5-kernels](https://github.com/stanford-cs149/asst5-kernels)
- **Tri Dao 的 Princeton 并行编程课 2026** — `problems/princeton` + `problems/tri/cross_entropy_py`（PR #141）

### 5.3 跨厂商竞赛问题

- **TriMul（Triangle Multiplicative Update）** — 2025-06-24 启动，跨 NVIDIA（A100/H100/B200）+ AMD MI300
- **KernelBot 累计 400K+ submissions**（2026-01 数据），相当于 GitHub 上所有 permissively licensed kernel 数据集的 5x 体量

### 5.4 IRL Hackathon 历史（来自 news `irl-at-accel`）

| 时间 | 地点 | 合办 | GPU 赞助 | 关键产出 |
|------|------|------|---------|---------|
| 2024 年底 | San Francisco | **Accel**（Casey Aylward 组织） | — | `llm.c`（→ `llm.q`）、`KernelBench`、`No-libtorch PyTorch`、`Flex CUTLASS`、`TCCL` |
| 2025-09-10 | East Coast | **Jane Street** | — | close-ended 风格，详情见 `/news/jane-street-hackathon` |
| **2025-11-05** | **San Francisco** | **Accel**（再次） | **Nebius 赞助 215 B200** + $28K prizes | 见下方 4 个获奖项目 |

#### 2025-11 IRL Hackathon 4 个获奖项目

| 名次 | 项目 | 简介 |
|------|------|------|
| 🥇 1st | **Symmetric Minds** | 把 PyTorch symmetric memory 引入 vLLM，Triton 多 GPU MoE 通信 kernel 优化，GPT-OSS-20B 在 GB200 上 ~1.5× speedup over DeepEP（[vllm PR 27495](https://github.com/vllm-project/vllm/pull/27495)、[triton commit](https://github.com/triton-lang/triton/commit/3c2e6f87d63e51b657e755d8965b5632233260b7)） |
| 🥈 2nd | **Flash Hogs** | Blackwell 上 attention 高阶梯度方法（HOG）的 backward kernel，~3x faster than XLA-optimized reference，linear memory cost（[github](https://github.com/marcelroed/flash-hob/)） |
| 🥉 3rd | **Delta Net** | Gated DeltaNet 的 Context-Parallel 实现，8B hybrid GDN-Transformer 在 GB200 单节点训到 128k context（[github](https://github.com/garrett361/flash-linear-attention/tree/cp-gdn)） |
| 4th | **KernelEvolve** | AlphaEvolve 风格 LLM search + RL，自动调 Helion GPU kernel，把数小时 autotuning 压到 30 分钟内 |

#### 评委 & TAs（2025 IRL）

- **评委**：[Tianqi Chen](https://tqchen.com/)、[Edward Yang](https://github.com/ezyang)、[Daniel Han](https://github.com/danielhanchen)、Mark Saroufim
- **TAs**：Horace He、Amir Afzali、Vincent Moens、Aleksa Gordic、Benjamin Chetioui、Daniel Vega-Myhre、Hicham Badri、Tristan Rice、Alban Desmaisons

---

## 6. 20 个活跃 Working Groups（来自 `WorkingGroups.tsx`）

> 长期专题小组，每个有独立 Discord 频道 + 例会。**加入方式**：Discord `discord.gg/gpumode` 对应频道。

### 6.1 Kernel LLM / AI for Systems（2026 战略核心）

| 工作组 | 简介 |
|--------|------|
| **Project Popcorn** | 训练开源 Kernel LLM（与 Prime Intellect、Modal、Lambda、MIT 合办）— 2026 主线 |
| **Reasoning-Gym** | RL 环境集合，测 AGI 系统能力 |
| **Factorio Learning Environment** | 用 Factorio 游戏测最强模型能力（极难环境） |

### 6.2 Kernel DSL 工作组（Mark 在 2026 战略文里特别列出）

| 工作组 | 简介 |
|--------|------|
| **CUTLASS** | NVIDIA 官方 tile abstraction 库 |
| **ThunderKittens** | Stanford Hazy Research 的 C++ tile primitive 库（**2.0 已发，2026-01-11**，支持 Blackwell + MXFP8/NVFP4） |
| **Triton / Gluon** | OpenAI Triton 之上的 autotune DSL（Lecture 104 由 Keren Zhou 主讲） |
| **Helion** | 新 DSL（Lecture 28 + 2026-03-14 hackathon） |
| **CuTile** | tile-based 编程抽象 |
| **TileLang** | 又一个快速 DSL |

### 6.3 应用层项目

| 工作组 | 简介 |
|--------|------|
| **llm.c** | Karpathy 发起 — full pretraining loop in raw CUDA（核心贡献者已散落各 AGI lab） |
| **Liger** | Triton kernels for pretraining（作者已加入各 AGI lab） |
| **Ring-Attention** | 长上下文分布式 attention |
| **TCCL** | comms libraries（从 2024 IRL hackathon 起爆发） |
| **torchao** | PyTorch 量化库 |
| **HQQ** | Half-Quadratic Quantization |
| **Robotics VLA** | Vision-Language-Action 模型 |
| **PPC Course** | PMPP 书课程 |
| **Teenygrad** | "更小的 tinygrad"（[j4orz/teenygrad](https://github.com/j4orz/teenygrad)） |
| **Triton Puzzles** | Lecture 14 配套解谜 |
| **Triton-viz** | Triton 代码可视化 |

### 6.4 关键 Working Group 资源

- [10 active working groups 完整文档](https://docs.google.com/document/d/1LprkfyOP5cRtv7rwkFiEHx2XEKhtwf9J4bQkD6btzgo/edit)
- Kernel LLM 周会：**2026-02-03 起，每周一次，Discord #general 语音**（公开）

---

## 7. 2026 年战略重点（来自 [Mark Saroufim 官方 2026-01-22 文](https://www.gpumode.com/news/gpumode-2026)）

### 7.1 4 大工作流（招募贡献者）

#### A. Deslopifying LLM-generated kernels
- **合作方**：PyTorch、vLLM、NVIDIA
- **目标**：把 LLM 生成的 verbose kernel 精简成可被真实 repo 合并的高质量代码
- **基础设施**：
  - [BackendBench](https://github.com/meta-pytorch/BackendBench)（PyTorch，已被 Prime Intellect 采纳）
  - [FlashInfer-Bench](https://bench.flashinfer.ai/)
  - KernelBench（GPU MODE hackathon 起源）
- **关键引述**：*"no PyTorch or VLLM maintainer is going to accept a 5K LOC patch that's faster if they don't understand how it works"*

#### B. Post-training a Kernel LLM
- **合作方**：Prime Intellect（Johannes、Will、Sami）、Modal、**Lambda（$100K compute 赞助）**、MIT
- **目标**：post-train 一个开源 Kernel LLM，把 kernel 合并进 PyTorch / vLLM
- **关键里程碑**：GTC 2026.3（San Jose）+ ICML 2026.7（Seoul）ship 首批结果
- **已发模型**：[facebook/KernelLLM](https://huggingface.co/facebook/KernelLLM)（2025 年发，但绑 Meta infra 无法外共享算力）

#### C. End-to-end kernel competitions + social evals
- **目标**：从单 kernel 竞赛扩展到 end-to-end 系统优化竞赛
- **合作方**：Verda（Simon 等带领）
- **设计灵感**：Jane Street close-ended hackathon vs Accel open-ended

#### D. From-scratch repos（"What I cannot create I do not understand" — Feynman）
- **目标**：用最少代码实现主流 repo 的 80% 性能，作为新 Kernel DSL 的 benchmark 套件
- **范例**：
  - [teenygrad](https://github.com/j4orz/teenygrad)（更小的 tinygrad）
  - [Penny](https://github.com/SzymonOzog/Penny)（手写版 NCCL）

### 7.2 关键基础设施（社区自研 / 深度合作）

| 项目 | 用途 | 状态 |
|------|------|------|
| **KernelBot** | 自动 kernel 评测机器人（400K+ 累计提交） | 持续运营 |
| **[KernelBook](https://huggingface.co/datasets/GPUMODE/KernelBook)** | Hugging Face 上的 kernel 数据集 | 已发布 |
| **[KernelLLM](https://huggingface.co/facebook/KernelLLM)** | Meta 训练的初代 Kernel LLM | 2025 已发 |
| **[popcorn](https://gpu-mode.github.io/popcorn/)** | 社区训练 Kernel LLM 的总项目 | 2026 主线 |
| **[KernelBench](https://github.com/ScalingIntelligence/KernelBench)** | Kernel LLM 的 de facto eval | de facto 标准 |
| **BackendBench** | PyTorch 端 LLM kernel eval | Prime Intellect 采用 |
| **FlashInfer-Bench** | 推理端 LLM kernel eval | online |

### 7.3 30+ 合作公司清单（来自官方感谢文）

> *"If you're looking for a job in systems, you'd benefit from talking to any one of..."*

**硬件厂商**：NVIDIA · AMD · Apple (隐含) · Dell · Sesterce · Verda · Tensorwave · CoreWeave · Hot Aisle
**云/算力**：Modal · Lambda（$100K compute）· Nebius（215 B200）· Northflank · Mako
**AI 实验室/平台**：PyTorch (Meta) · HuggingFace · Unsloth · Prime Intellect · SemiAnalysis
**投资/金融**：Accel · Jane Street
**学术**：Stanford · MIT · Princeton（Tri Dao）· Cornell
**其他**：vLLM ·一起合作的众多开源贡献者

---

## 8. 学习路径推荐（按背景）

### 🟢 路径 A：Python/PyTorch 用户，没碰过 CUDA
1. **L3 + L5**（Jeremy Howard）：0→1 入门，配合 Colab
2. **[Sasha Rush GPU-Puzzles](https://github.com/srush/GPU-Puzzles)**：numba @cuda.jit 写 13 题
3. **[Triton-Puzzles](https://github.com/gpu-mode/Triton-Puzzles)**：转 Triton（更 Pythonic）
4. **L14**（Umer Adil）：Practitioner's Guide to Triton — Triton 最佳入门讲座
5. **L1 + L8 + L9**（Mark Saroufim）：profiling + 性能清单 + Reductions
6. **PMPP 书**（L2 配套）

### 🟡 路径 B：会 CUDA，想优化 kernel
1. **L23 / L36 / L57 / L103 / L86**：Tensor Core → CUTLASS → CuTE → CuTe Layout → CuTeDSL
2. **L24**：Scan at the Speed of Light
3. **L12 + L36**：FlashAttention 1/2/3
4. **L37**（Arun Demeure）：SASS 反汇编与微架构
5. **L84**（Paulius Micikevicius）：FP8 / Numerics
6. **ThunderKittens 2.0** + L75：用 TK 写 FA3
7. **L69**（Quartet）+ qutlass：4-bit 训练

### 🔴 路径 C：MLSys 工程师，做训练/推理系统
1. **awesomeMLSys 全部论文**（按 Attention → Quant → Long Context → Distributed → Speculative → Linear Attention 顺序读）
2. **L17 / L67**：NCCL / NVSHMEM
3. **L22 / L35 / L40**：vLLM Speculative / SGLang / FlashInfer
4. **L39**：TorchTitan 4D 并行
5. **L79**：Mirage MPK Mega Kernel（2025 最新方向）
6. **L32 / L28**：Unsloth / Liger Kernel（生产级 Triton 库）

### 🟣 路径 D：异构平台（AMD / Intel / Apple）
- **AMD**：L25（Composable Kernel）+ [amd-cluster](https://github.com/gpu-mode/amd-cluster)（免费 MI300X 时段）+ [HipKittens](https://github.com/HazyResearch/HipKittens)
- **Intel SYCL**：L26
- **Apple Metal**：L31（Unsloth 创始人 Daniel Han 本人）

### 🟤 路径 E：Kernel LLM 研究（2026 新方向）
1. 读 [GPU MODE 2026 战略文](https://www.gpumode.com/news/gpumode-2026)
2. 加入 popcorn Discord 频道
3. 阅读 [KernelLLM 论文](https://huggingface.co/facebook/KernelLLM)
4. 学习 [BackendBench](https://github.com/meta-pytorch/BackendBench) + KernelBench + FlashInfer-Bench
5. 跟进 Prime Intellect + Lambda 合作的训练实验

---

## 9. 必读论文清单（精选自 awesomeMLSys）

### Attention 机制
- **Attention is all you need** ([1706.03762](https://arxiv.org/abs/1706.03762)) — 入门必读
- **Online normalizer calculation for softmax** ([1805.02867](https://arxiv.org/abs/1805.02867)) — Flash Attention 前置
- **Self Attention does not need O(n²) memory** ([2112.05682](https://arxiv.org/abs/2112.05682))
- **Flash Attention 2** ([2307.08691](https://arxiv.org/abs/2307.08691))
- **ALiBi** ([2108.12409](https://arxiv.org/abs/2108.12409))

### 推理系统
- **Towards Efficient Generative LLM Serving: Survey** ([2312.15234](https://arxiv.org/abs/2312.15234))
- **Orca** (OSDI'22) — continuous batching
- **PagedAttention / vLLM** ([2309.06180](https://arxiv.org/abs/2309.06180))
- **Sarathi LLM** ([2308.16369](https://arxiv.org/abs/2308.16369)) — chunked prefill

### 量化
- **White Paper on NN Quantization** ([2106.08295](https://arxiv.org/abs/2106.08295))
- **LLM.int8()** ([2208.07339](https://arxiv.org/abs/2208.07339))
- **FP8 formats** ([2209.05433](https://arxiv.org/abs/2209.05433))
- **SmoothQuant** ([2211.10438](https://arxiv.org/abs/2211.10438))

### 分布式
- **ZeRO / FSDP** ([1910.02054](https://arxiv.org/abs/1910.02054))
- **Megatron-LM** ([1909.08053](https://arxiv.org/abs/1909.08053))
- **Selective Activation Checkpointing** ([2205.05198](https://arxiv.org/abs/2205.05198))
- **torchtitan** ([2410.06511](https://arxiv.org/abs/2410.06511))
- **Breaking the computation/communication abstraction barrier** ([2105.05720](https://arxiv.org/abs/2105.05720)) — god tier

### 投机解码
- **Speculative Decoding** ([2211.17192](https://arxiv.org/abs/2211.17192))
- **Medusa** ([2401.10774](https://arxiv.org/abs/2401.10774))
- **DeepSeek V3 MTP** ([2412.19437](https://arxiv.org/abs/2412.19437))

### 线性注意力
- **flash-linear-attention** ([repo](https://github.com/fla-org/flash-linear-attention)) — SOTA 集成

### 2025 新增（来自 2026 战略文）
- **Recursive Language Models** ([2512.24601](https://arxiv.org/abs/2512.24601)) — Alex 的 memory 框架
- **Deepseek 3.2** — 用了 1800+ RL 环境
- **Defeating non-determinism in LLM inference** — Horace He 文

---

## 10. 社区"Grandmasters"（重点追踪）

| 人物 | 领域 | 必看产出 |
|------|------|---------|
| **Mark Saroufim** | 创始人 / PyTorch | 主讲 L1, L8, L9, L39 + 2026 战略文 |
| **Andreas Koepf** | 联合创始人 | L2, L13 + ring-attention 仓库 |
| **Keren Zhou** | Triton / Gluon | Triton-Puzzles, L104 Gluon |
| **Tri Dao** | Flash Attention / Mamba | [flash-attention](https://github.com/Dao-AILab/flash-attention), [mamba](https://github.com/state-spaces/mamba) |
| **Tim Dettmers** | 量化 | [bitsandbytes](https://github.com/TimDettmers/bitsandbytes), [QLoRA](https://arxiv.org/abs/2305.14314) |
| **Sasha Rush** | 教学型 puzzles | [GPU-Puzzles](https://github.com/srush/GPU-Puzzles) 等 7 个 puzzle 系列 |
| **Jeremy Howard** | 0→1 入门 | L3, L5 — 社区奠基讲座 |
| **Daniel Han** | Unsloth | L32 — Unsloth LLM Systems Engineering |
| **gau-nernst (Thien Tran)** | 量化 / cursed PTX | L30, L31 + [tcgen05 笔记](https://gau-nernst.github.io/tcgen05/) + [AMD a2a 写作](https://gau-nernst.github.io/amd-a2a/) |
| **Andrei Panferov** | 4-bit 训练 | Quartet, qutlass (L69) |
| **Cris Cecka** | CuTE / TK | L57 |
| **Paulius Micikevicius** | FP8 发明者 | L84 |
| **Adam Paszke** | PyTorch / Mosaic | L42 |
| **Jay Shah** | CUTLASS / Colfax | L36, L103 + [Colfax blog](https://research.colfax-intl.com/blog/) |
| **Horace He** | brrr / non-determinism | [brrr_intro](https://horace.io/brrr_intro.html) — fusion 必读 |
| **William Brandon** | ThunderKittens | L75 |

### Sasha Rush Puzzle 系列全集（GPU MODE 推崇）
1. [GPU-Puzzles](https://github.com/srush/GPU-Puzzles)（numba @cuda.jit）
2. [Tensor-Puzzles](https://github.com/srush/tensor-puzzles)
3. [Autodiff-Puzzles](https://github.com/srush/autodiff-puzzles)
4. [Transformer-Puzzles](https://github.com/srush/transformer-puzzles)
5. [GPTworld](https://github.com/srush/GPTworld)
6. [LLM-Training-Puzzles](https://github.com/srush/LLM-Training-Puzzles)
7. **[Triton-Puzzles](https://github.com/gpu-mode/Triton-Puzzles)** ← 第 7 弹，已并入 GPU MODE 官方

---

## 11. 硬件白皮书与 ISAs

| 文档 | 链接 |
|------|------|
| NVIDIA H100 Whitepaper (Hopper) | https://resources.nvidia.com/en-us-tensor-core/gtc22-whitepaper-hopper |
| NVIDIA GH200 Whitepaper | https://resources.nvidia.com/en-us-grace-cpu/nvidia-grace-hopper |
| AMD CDNA 3 Whitepaper | https://www.amd.com/.../amd-cdna-3-white-paper.pdf |
| AMD MI300X Data Sheet | https://www.amd.com/.../amd-instinct-mi300x-data-sheet.pdf |
| PTX ISA Programming Guide | https://docs.nvidia.com/cuda/parallel-thread-execution/ |
| Asianometry: Can SRAM Keep Shrinking? | https://youtu.be/2G4_RZo41Zw |

---

## 12. 周边生态（GPU MODE 反复引用）

### ThunderKittens（Stanford Hazy Research）
- repo: [HazyResearch/ThunderKittens](https://github.com/HazyResearch/ThunderKittens)
- **TK 2.0 已发布（2026-01-11）**：支持 Blackwell + MXFP8 + NVFP4，不再支持 Ampere，不再作为 Python 包
- AMD 版本：[HipKittens](https://github.com/HazyResearch/HipKittens)
- 生产用户：Together AI、Jump Trading、Cursor
- 推荐深读：[Hamza Elshafie 的 TK 解剖](https://hamzaelshafie.bearblog.dev/dissecting-thunderkittens-anatomy-of-a-compact-dsl-for-high-performance-ai-kernels/)
- L75（William Brandon 主讲）

### Hazy Research（Chris Ré 实验室）
- [Building Blocks for AI Systems](https://github.com/HazyResearch/aisys-building-blocks)
- [Data-Centric AI](https://github.com/HazyResearch/data-centric-ai)
- [Blog](https://hazyresearch.stanford.edu/blog)
- Chris Ré NeurIPS 2023 keynote: *Systems for Foundation Models, and Foundation Models for Systems*

### NVIDIA 官方教育资源
- [Accelerated Computing Hub](https://github.com/NVIDIA/accelerated-computing-hub/) — 开源教程集
- [OLCF CUDA Training Series](https://www.olcf.ornl.gov/cuda-training-series/) — 配 exercises
- GTC 2022 *CUDA: New Features and Beyond* (Stephen Jones): https://youtu.be/SAm4gwkj2Ko

### 经典课程
- **PMPP 配套 YouTube** [@pmpp-book](https://www.youtube.com/@pmpp-book) + [Applied Parallel Programming](https://www.youtube.com/playlist?list=PLRRuQYjFhpmvu5ODQoY2l7D0ADgWEcYAX)（Wen-mei Hwu, UIUC）
- [Programming Parallel Computers](https://ppc-exercises.cs.aalto.fi/courses)（Aalto，可在线提交）
- [HetSys](https://safari.ethz.ch/projects_and_seminars/fall2022/doku.php?id=heterogeneous_systems)（ETH）

### 工具栈（Python GPU）
| 工具 | 用途 |
|------|------|
| PyTorch | 默认 |
| [Triton](https://github.com/openai/triton/) | Pythonic GPU DSL |
| [numba @cuda.jit](https://numba.readthedocs.io/en/stable/cuda/kernels.html) | 入门 |
| [JAX Pallas](https://jax.readthedocs.io/en/latest/pallas/index.html) | TPU/GPU |
| [CuPy](https://cupy.dev/) | NumPy 兼容 |
| [NVIDIA Fuser](https://github.com/NVIDIA/Fuser/) | fused codegen |
| [Codon @gpu.kernel](https://docs.exaloop.io/codon/advanced/gpu) | Python-like 编译语言 |
| [Mojo](https://docs.modular.com/mojo/manual/) | Modular MAX |
| [CUDA Python](https://github.com/NVIDIA/cuda-python) | 官方 binding |

### Profiling 工具
- **Nsight Compute (`ncu`)** — [Profiling Guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html)
- **Nsight Systems (`nsys`)** — [YouTube 教程](https://www.youtube.com/watch?v=kKANP0kL_hk)
- [mcarilli/nsight.sh](https://gist.github.com/mcarilli/376821aa1a7182dfcf59928a7cde3223) — 常用 profiling 命令
- [Holistic Trace Analysis (HTA)](https://hta.readthedocs.io/)
- [PyTorch Trace Analyzer](https://pytorch.org/blog/trace-analysis-for-masses/)
- [ncu 启用 gist](https://gist.github.com/msaroufim/9e56ce5d42a5e9ccd5e938c83181ea47)（Mark Saroufim 写，"超级简单修复"）

---

## 13. 第三方学习资源（社区贡献）

### 个人 repo（讲座素材镜像）
- [mcvlix/GPUMODE](https://github.com/mcvlix/GPUMODE) — 复制 + 修改的讲座资料（205 files）
- [mnlife/cuda-mode](https://github.com/mnlife/cuda-mode) — 讲座镜像（177 files）
- [angchen0325/CUDA-mode-lectures](https://github.com/angchen0325/CUDA-mode-lectures) — 含 lecture_001/002/003 详细素材
- [kapilsh/cuda-mode-lecture](https://github.com/kapilsh/cuda-mode-lecture) — L18 Fused Kernels 配套（4⭐）
- [manoflearning/cuda-practice](https://github.com/manoflearning/cuda-practice) — hands-on 练习

### 个人博客（顶级选手的 writeup）
- **[gau-nernst on AMD All-to-All](https://gau-nernst.github.io/amd-a2a/)** — L30 主讲 + AMD $100K 比赛获胜经验
- **[Simon (Veitner) on CuteDSL](https://veitner.bearblog.dev/an-applied-introduction-to-cutedsl/)** — 公开最好的 CuTeDSL 资料
- **[yotta on AMD distributed kernels](https://www.yottalabs.ai/post/optimizing-distributed-inference-kernels-for-amd-developer-challenge-2025)** — 3 个 AMD distributed 问题全解析
- **[Hamza Elshafie on ThunderKittens](https://hamzaelshafie.bearblog.dev/dissecting-thunderkittens-anatomy-of-a-compact-dsl-for-high-performance-ai-kernels/)** — TK 深度解剖
- **[Horace He - brrr_intro](https://horace.io/brrr_intro.html)** — fusion/overhead 必读
- **[siboehm - CUDA Matmul Worklog](https://siboehm.com/articles/22/CUDA-MMM)** — 手撕 cuBLAS 级 matmul
- **[Lei Mao - Tensor Core Programming](https://leimao.github.io/blog/NVIDIA-Tensor-Core-Programming/)** — 中文圈友好
- **[Huy Nguyen - ML Compilers Intro](https://huyenchip.com/2021/09/07/a-friendly-introduction-to-machine-learning-compilers-and-optimizers.html)** — 编译器入门
- **[Colfax Research Blog](https://research.colfax-intl.com/blog/)** — CUTLASS 深度（Jay Shah 长期供稿）
- **[SemiAnalysis](https://www.semianalysis.com/)** — 行业分析 + ClusterMax 评级

---

## 14. 中国大陆访问建议

| 资源 | 障碍 | 应对 |
|------|------|------|
| GitHub 主仓库 | 慢/偶发断流 | `ghproxy.com` 加速：`git config --global url."https://ghproxy.com/https://github.com/".insteadOf "https://github.com/"` |
| YouTube 讲座录像 | 局域网屏蔽 | **需科学上网**；或搜 bilibili 第三方搬运（关键词 "GPU MODE" / "CUDA MODE 讲座"） |
| Discord 实时参与 | 局域网屏蔽 | **需科学上网**；可订阅 YouTube 录像补 |
| `raw.githubusercontent.com` | 偶发污染 | `https://raw.gitmirror.com/...` 或 `https://ghproxy.com/...` |
| Colab Notebook | GPU 受限 | 国内可换 [AutoDL](https://www.autodl.com/)、[魔搭](https://modelscope.cn/) |
| `api.github.com` | **可用** | 本文档所有数据均通过此通道获取 |
| `gpumode.com` + `/api/*` | **可用** | 公开端点：`/api/events`、`/api/news` |
| Google Slides / Dropbox / Drive | 局域网屏蔽 | 部分讲座 slides 在此，需代理 |
| `discord.com` | 完全不通 | 用 Discord Web + 镜像；或只用 GitHub 通道 |
| `huggingface.co` API | 间歇不通 | 网页通常可访问；`hf-mirror.com` 镜像 |

### 一键 clone 所有核心仓库（ghproxy 加速）
```bash
mkdir gpumode && cd gpumode
BASE="https://ghproxy.com/https://github.com/gpu-mode"
for r in lectures Triton-Puzzles resource-stream awesomeMLSys triton-index reference-kernels \
         ring-attention profiling-cuda-in-torch kernelbot kernelboard; do
  echo "Cloning $r..."
  git clone --depth 1 "$BASE/$r"
done
```

### 实时拉讲座日程（无需任何鉴权）
```bash
# 即将到来的讲座
curl -s https://www.gpumode.com/api/events | python3 -m json.tool

# 12 篇官方博客全文（含 markdown 正文）
curl -s https://www.gpumode.com/api/news | python3 -m json.tool
```

---

## 15. 数据获取方法学（可复现）

本文档所有数据可由以下命令复现：

```bash
# 1. GitHub 组织所有 repo
curl -s "https://api.github.com/orgs/gpu-mode/repos?per_page=100" | jq '.[] | {name, stars: .stargazers_count, desc: .description}'

# 2. lectures README + 跳号分析
curl -s https://raw.githubusercontent.com/gpu-mode/lectures/main/README.md > /tmp/readme.md
grep -E "^## Lecture" /tmp/readme.md  # 列出所有显式讲座

# 3. lectures 仓库实际目录
curl -s "https://api.github.com/repos/gpu-mode/lectures/git/trees/main?recursive=1" | jq '.tree[].path' | grep -oE 'lecture_[0-9]+' | sort -u

# 4. 即将到来的讲座（gpumode.com 公开 API）
curl -s https://www.gpumode.com/api/events

# 5. 12 篇官方博客
curl -s https://www.gpumode.com/api/news | jq '.data[] | {id, title, date}'

# 6. reference-kernels 完整竞赛历史
curl -s "https://api.github.com/repos/gpu-mode/reference-kernels/issues?state=all&per_page=100&page=1" > rk.json
# (重复拉 2-3 页)

# 7. kernelboard 前端代码（working-groups hard-coded）
curl -s https://raw.githubusercontent.com/gpu-mode/kernelboard/main/frontend/src/pages/working-groups/WorkingGroups.tsx
```

---

## 📌 下一步建议

1. **本周做一件事**：clone `lectures` 仓库，按 §8 路径选 1-2 期入门讲座过一遍（推荐 L3 + L14）
2. **完成 Sasha Rush GPU-Puzzles 13 题**（用 numba，CPU 即可）→ 再过 **Triton-Puzzles**
3. **加入 Discord** (`discord.gg/gpumode`)：每周讲座预告在 Events 频道
4. **订阅 `/api/events`**：用 cron 每天拉一次，第一时间知道新讲座
5. **结合本项目的体系结构实验**，强相关映射：
   - Lab03_存储层次 ← L4 (Memory Architecture)
   - Lab02_流水线与ILP ← L23 (Tensor Cores)
   - Lab04_超标量乱序 ← L37 (SASS & GPU Microarchitecture)
   - Lab05_并行与SIMD ← L20/21 (Scan) + L23 (Tensor Cores)
   - Lab06_内存模型与并发 ← L17/67 (NCCL/NVSHMEM)
   - Lab07_密码学专题 ← L84 (Numerics)

## ✍️ 入门自测题（建议先尝试再看录像）

1. 写一个 `square_kernel`，分别用 (a) PyTorch (b) Triton (c) `load_inline` CUDA 三种实现，比较三者 ncu 报告的 SOL（speed of light）。
2. 解释为什么 `__shfl_xor_sync` 比 shared memory reduce 更快（提示：warp 内通信 vs LDS 延迟）。
3. 用一段 Triton 代码实现 `softmax`，并解释为什么 `online softmax` 能省内存（前置论文 [1805.02867](https://arxiv.org/abs/1805.02867)）。
4. 阅读 [Horace He - brrr_intro](https://horace.io/brrr_intro.html)，画出 FlashAttention 2 的 compute intensity 与 baseline attention 的对比曲线。
5. 在 [reference-kernels/problems/pmpp_v2](https://github.com/gpu-mode/reference-kernels/tree/main/problems/pmpp_v2) 选 1 题，本地跑通 + 上传 Discord 榜单。

---

## 📎 附录：原始数据归档

为方便复核，本次调研的所有原始数据已落盘到 `/tmp/opencode/gpumode/`：
- `lectures_readme.md` — lectures 仓库 README 完整版（10.9KB）
- `resource-stream.md` — resource-stream README 完整版（204 行）
- `news.json` — 12 篇官方博客全文（107KB）
- `commits/page_*.json` — lectures 仓库 144 个 commits
- `prs/page_*.json` — lectures 仓库 54 个 PRs
- `issues/page_*.json` — lectures 仓库 12 个 issues
- `rk_issues/page_*.json` — reference-kernels 仓库 167 个 issues/PRs

---

> 📝 **本文件维护说明**：
> - lectures 每周新增，建议每月用 §15 命令同步一次
> - 完整跳号讲座标题需登录 YouTube `@GPUMODE/videos` 人工补充
> - 资源清单原文（带完整链接）：https://github.com/gpu-mode/resource-stream/blob/main/README.md
> - 2026 战略文原文：https://www.gpumode.com/news/gpumode-2026
