# MIT HAN Lab 端侧与高效 AI 研究地图 · 对接 work4ai

> **MIT HAN Lab**（`github.com/mit-han-lab`，韩松实验室）**全部 72 个公开仓库**的系统化梳理——按 9 大研究主题分类，核心仓库做「技术 + 论文 + 会议 + 对接 work4ai」卡片，全 72 仓库列速览附录。
>
> **为什么有这份地图**：MIT HAN Lab 是**端侧 AI / 模型压缩 / 高效 AI** 的全球顶尖实验室（深度压缩→NAS→MCUNet→AWQ→Streaming-LLM 全主线）。work4ai 已广泛引用量化(126 处)/稀疏(67)/AWQ(9)/SmoothQuant(5)，但缺一份把整个 HAN Lab 研究脉络串起来的地图。本地图补这个空白——它是「高效 AI 研究」维度的导航，与 [`端侧AI架构参考.md`](端侧AI架构参考.md)（产业端侧）互补。
>
> **不做什么**：不讲原理（那是讲透系列的事），不复制论文。只做**研究地图 + 脉络 + 对接 + 缺口诊断**。

---

## 一、元信息

| 项 | 内容 |
|---|---|
| **组织** | MIT HAN Lab（`github.com/mit-han-lab`，Han Song 韩松实验室）|
| **公开仓库总数** | **72**（截至 2026-08-10，GitHub API 实测）|
| **数据源** | GitHub REST API `orgs/mit-han-lab/repos` |
| **主导语言** | Python（多数）+ C/C++/Cuda（推理引擎/算子）+ 少量 Scala/Jupyter |
| **头部门檻** | 1 万★以上 2 个（streaming-llm / llm-awq），1 千★以上 ~15 个 |
| **一句话定位** | 从 2018 深度压缩到 2026 NVFP4 量化，HAN Lab 覆盖了**高效 AI 的全主线**——压缩 / 量化 / NAS / 端侧 / 稀疏 attention / VLM 高效 |

### 功能域分布（按 stars 汇总排序）

| 研究主题 | 仓库数 | 合计 stars | 头部仓库 |
|---|---|---|---|
| LLM 长上下文 / 稀疏 attention | 11 | 11,316 | streaming-llm 7258★ |
| 视觉模型高效 | 9 | 10,592 | efficientvit 3345★ |
| LLM 量化 / 压缩 | 6 | 6,906 | llm-awq 3610★ |
| VLM / VLA 高效 | 7 | 4,943 | temporal-shift-module 2221★ |
| 端侧 / IoT 部署 | 9 | 4,567 | tinyml 1204★ |
| NAS / 架构搜索 | 2 | 3,399 | once-for-all 1953★ |
| 生成模型高效 | 5 | 3,159 | data-efficient-gans 1308★ |
| 分布式 / 系统 | 5 | 1,664 | kernel-design-agents 815★ |
| 其他 / 研究 | 18 | 4,295 | torchquantum 1656★ |

---

## 二、九大研究主题 × 核心仓库

> **覆盖状态图例**：✅✅ 深度（多文件）/ ✅ 中 / ✅ 浅 / ❌ 缺口（基于 work4ai 实测引用）

### 域 1 · 端侧 / IoT 部署（9 库，4567★）

> HAN Lab 的发家领域——把深度学习塞进几十 KB 内存的微控制器。对接 [`端侧AI架构参考.md`](端侧AI架构参考.md)。

| 仓库 (stars) | 技术 · 论文 | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **tinyml** (1204★) | TinyML 教程集 | [`端侧AI架构参考`](端侧AI架构参考.md) | ✅ 浅 |
| **TinyChatEngine** (960★) | 端侧 LLM 推理库（C++）| [`讲透GPU与系统级`](讲透GPU与系统级/)（端侧推理）| ❌ 缺口 |
| **tinyengine** (952★) | MCUNet 推理引擎（NeurIPS 2020）| [`端侧AI架构参考`](端侧AI架构参考.md) | ❌ 缺口 |
| **mcunet** (709★) | IoT 上的深度学习（NeurIPS 2020）—— NAS+推理引擎联合优化 | [`端侧AI架构参考`](端侧AI架构参考.md) | ✅ 浅 |
| **tiny-training** (524★) | **256KB 内存下的端侧训练**（NeurIPS 2022）| [`讲透微调`](讲透微调/)（端侧训练）| ❌ 缺口 |

### 域 2 · LLM 量化 / 压缩（6 库，6906★）

> HAN Lab 在 LLM 时代的标志性贡献——AWQ/SmoothQuant 是工业级 LLM 量化的两块基石。

| 仓库 (stars) | 技术 · 论文 | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **llm-awq** (3610★) | **AWQ：激活感知权重量化**（MLSys 2024 **Best Paper**）| [`讲透GPU与系统级`](讲透GPU与系统级/)（量化）| ✅✅ (9) |
| **smoothquant** (1674★) | **SmoothQuant：后训练量化**（ICML 2023）| [`讲透GPU与系统级`](讲透GPU与系统级/) | ✅ (5) |
| **omniserve** (852★) | **QServe：W4A8KV4 量化+系统协同**（MLSys 2025）| [`讲透GPU与系统级`](讲透GPU与系统级/) | ❌ 缺口 |
| **haq** (408★) | 硬件感知自动量化（CVPR 2019 Oral）| [`讲透GPU与系统级`](讲透GPU与系统级/) | ❌ 缺口 |
| **fouroversix** (202★) | NVFP4 量化（更精准的 4-bit 浮点）| [`讲透GPU与系统级`](讲透GPU与系统级/) | ❌ 缺口 |
| **apq** (160★) | 联合架构+量化搜索（CVPR 2020）| [`讲透基础模型`](讲透基础模型/)（NAS+量化）| ❌ |

### 域 3 · LLM 长上下文 / 稀疏 attention（11 库，11316★）

> streaming-llm（attention sink）是 HAN Lab 星数最高的工作——让 LLM 处理无限长序列。

| 仓库 (stars) | 技术 · 论文 | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **streaming-llm** (7258★) | **attention sink 流式 LLM**（ICLR 2024）——无限长上下文 | [`讲透基础模型`](讲透基础模型/)（长上下文）| ✅ 浅 |
| **lite-transformer** (609★) | 长短范围 attention（ICLR 2020）| [`讲透Transformer`](讲透Transformer/) | ❌ |
| **radial-attention** (608★) | O(nlogn) 稀疏 attention（NeurIPS 2025）| [`讲透Transformer`](讲透Transformer/) | ❌ 缺口 |
| **Block-Sparse-Attention** (544★) | 混合稀疏模式 attention kernel | [`讲透GPU与系统级`](讲透GPU与系统级/)（FlashAttention 类）| ❌ |
| **duo-attention** (540★) | 长上下文高效（ICLR 2025）| [`讲透基础模型`](讲透基础模型/) | ❌ 缺口 |
| **Quest** (400★) | query 感知稀疏（ICML 2024）| [`讲透基础模型`](讲透基础模型/) | ❌ |
| **x-attention** (281★) | 反对角块稀疏（ICML 2025）| [`讲透Transformer`](讲透Transformer/) | ❌ |

### 域 4 · VLM / VLA 高效（7 库，4943★）

> HAN Lab 的新方向——视频流式理解 + 视觉语言动作模型（VLA）高效推理。

| 仓库 (stars) | 技术 · 论文 | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **temporal-shift-module** (2221★) | **TSM：高效视频理解**（ICCV 2019）——经典 | 未来 CV 系列 | ❌ |
| **streaming-vlm** (1063★) | 无限视频流式实时理解 | [`讲透基础模型`](讲透基础模型/)（多模态）| ❌ 缺口 |
| **hart** (647★) | 混合自回归视觉生成 | [`讲透生成模型`](讲透生成模型/) | ❌ |
| **vlash** (475★) | 实时 VLA（未来状态感知异步推理）| 未来具身系列 | ❌ |
| **vila-u** (426★) | 统一视觉基础模型（ICLR 2025）| [`讲透基础模型`](讲透基础模型/) | ❌ |

### 域 5 · 视觉模型高效（9 库，10592★）

| 仓库 (stars) | 技术 · 论文 | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **efficientvit** (3345★) | 高效视觉基础模型（高分辨率生成）| [`讲透基础模型`](讲透基础模型/)（CV）| ❌ 缺口 |
| **bevfusion** (3229★) | 多任务多传感器融合（ICRA 2023）——自动驾驶 | 未来具身/自动驾驶 | ❌ |
| **torchsparse** (1470★) | 稀疏点云高效训练推理（MICRO 2023）| [`讲透GPU与系统级`](讲透GPU与系统级/) | ❌ |
| **anycost-gan** (779★) | 交互式 GAN（CVPR 2021）| [`讲透生成模型`](讲透生成模型/) | ❌ |
| **litepose** (326★) | 高效人体姿态（CVPR 2022）| 未来 CV 系列 | ❌ |

### 域 6 · NAS / 架构搜索（2 库，3399★）

| 仓库 (stars) | 技术 · 论文 | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **once-for-all** (1953★) | **OFA：一次训练多部署**（ICLR 2020）——子网络抽取 | [`讲透基础模型`](讲透基础模型/) | ✅ 浅 |
| **proxylessnas** (1446★) | 直接 NAS（ICLR 2019）——无代理搜索 | [`讲透基础模型`](讲透基础模型/) | ❌ 缺口 |

### 域 7 · 生成模型高效（5 库，3159★）

| 仓库 (stars) | 技术 · 论文 | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **data-efficient-gans** (1308★) | 差异化增强（NeurIPS 2020）| [`讲透生成模型`](讲透生成模型/) | ❌ |
| **gan-compression** (1116★) | GAN 压缩（CVPR 2020）| [`讲透生成模型`](讲透生成模型/) | ❌ |
| **distrifuser** (727★) | 分布式扩散推理（CVPR 2024 Highlight）| [`讲透分布式AI系统`](讲透分布式AI系统/) | ❌ 缺口 |

### 域 8 · 分布式 / 系统（5 库，1664★）

| 仓库 (stars) | 技术 · 论文 | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **kernel-design-agents** (815★) | kernel 设计 agent | [`讲透Agent`](讲透Agent/) | ❌ |
| **inter-operator-scheduler** (201★) | IOS 算子调度（MLSys 2021）| [`讲透GPU与系统级`](讲透GPU与系统级/) | ❌ |

### 域 9 · 其他 / 研究（18 库，4295★）

| 仓库 (stars) | 技术 · 论文 | 对接 |
|---|---|---|
| **torchquantum** (1656★) | 量子-经典模拟框架 | （量子 ML，独立方向）|
| **dlg** (483★) | **梯度泄露**（NeurIPS 2019）——联邦学习隐私攻击 | [`讲透Agent`](讲透Agent/)（安全）|
| **amc** (450★) | **AMC：AutoML 模型压缩**（ECCV 2018）——强化学习搜压缩 | [`讲透GPU与系统级`](讲透GPU与系统级/) |
| **offsite-tuning** (386★) | 离场微调（无需完整模型）| [`讲透微调`](讲透微调/) |
| **hardware-aware-transformers** (337★) | **HAT：硬件感知 Transformer**（ACL 2020）| [`讲透Transformer`](讲透Transformer/) |

---

## 三、研究脉络时间线（2018–2026）

HAN Lab 八年的高效 AI 演进，清晰分四阶段：

```
阶段 1 (2018-2019) 模型压缩奠基
  AMC (ECCV'18)    ── RL 搜压缩策略
  HAQ (CVPR'19)    ── 硬件感知量化
  ProxylessNAS (ICLR'19) ── 直接 NAS

阶段 2 (2020-2021) 一次训练 + 端侧
  Once-for-All (ICLR'20) ── ⭐ 一次训练多部署（子网络）
  MCUNet (NeurIPS'20)    ── ⭐ IoT 上的深度学习（NAS+引擎）
  GAN Compression (CVPR'20)
  HAT (ACL'20)           ── 硬件感知 Transformer
  Anycost GAN (CVPR'21)  ── 弹性 GAN
  Lite Pose (CVPR'22)    ── 高效姿态

阶段 3 (2022-2023) LLM 量化
  SmoothQuant (ICML'23)  ── ⭐ 后训练量化（激活迁移到权重）
  AWQ (MLSys'24 Best Paper) ── ⭐⭐ 激活感知权重量化（工业级 W4）
  tiny-training (NeurIPS'22) ── 256KB 端侧训练

阶段 4 (2024-2026) 长上下文 + VLM + 系统协同
  Streaming-LLM (ICLR'24) ── ⭐⭐⭐ attention sink（星数最高）
  DuoAttention (ICLR'25)  ── 长上下文
  QServe (MLSys'25)       ── W4A8KV4 量化+系统协同
  StreamingVLM (2025)     ── 无限视频流式
  FourOverSix (2026)      ── NVFP4 浮点量化
  Radial Attention (NeurIPS'25) ── O(nlogn) 稀疏
```

> 🎯 **脉络洞察**：HAN Lab 的主线是**"把模型变小、变快、塞进更小的设备"**——从压缩单个模型（AMC/HAQ）→ 一次训练多部署（OFA）→ 端侧 IoT（MCUNet）→ LLM 量化（AWQ/SmoothQuant）→ 长上下文稀疏（Streaming-LLM）→ VLM/系统协同（QServe/StreamingVLM）。**每一代都在回答"如何在新的硬件/模型规模约束下做到高效"**。

---

## 四、work4ai × MIT HAN Lab 覆盖热力图

> 基于 work4ai 实测引用（grep）。读法：绿色 = 已对接，红色 = 缺口。

| HAN Lab 核心库 | stars | 覆盖 | 对接的 work4ai 系列 |
|---|---:|:---:|---|
| llm-awq | 3610 | ✅✅ 深度 | 讲透GPU与系统级（量化，9 处）|
| smoothquant | 1674 | ✅ 中 | 讲透GPU与系统级（5 处）|
| streaming-llm | 7258 | ✅ 浅 | 讲透基础模型（长上下文）|
| once-for-all | 1953 | ✅ 浅 | 讲透基础模型（NAS）|
| mcunet | 709 | ✅ 浅 | 端侧AI架构参考 |
| **omniserve (QServe)** | **852** | ❌ 缺口 | 讲透GPU与系统级（W4A8KV4）|
| **TinyChatEngine** | **960** | ❌ 缺口 | 讲透GPU与系统级（端侧 LLM）|
| **tinyengine** | **952** | ❌ 缺口 | 端侧AI架构参考 |
| **tiny-training** | **524** | ❌ 缺口 | 讲透微调（端侧训练）|
| **duo-attention** | **540** | ❌ 缺口 | 讲透基础模型（长上下文）|
| **efficientvit** | **3345** | ❌ 缺口 | 讲透基础模型（CV 高效）|
| **distrifuser** | **727** | ❌ 缺口 | 讲透分布式AI系统 |
| **amc** | **450** | ❌ 缺口 | 讲透GPU与系统级（压缩 RL）|
| **offsite-tuning** | **386** | ❌ 缺口 | 讲透微调 |
| **hardware-aware-transformers** | **337** | ❌ 缺口 | 讲透Transformer |

**覆盖率**：核心 15 库中，✅✅深度 1 / ✅中 1 / ✅浅 3 = **已覆盖 5 个（33%）**；❌缺口 10 个（67%）。

---

## 五、补强清单（work4ai 当前缺口，按价值排序）

### 🔴 P0（高星 + 强对接价值，建议补）

| 缺口库 | stars | 该补在哪 | 为什么重要 |
|---|---:|---|---|
| **omniserve (QServe)** | 852 | [`讲透GPU与系统级`](讲透GPU与系统级/) | W4A8KV4 量化+系统协同，MLSys 2025 最新 SOTA；讲透GPU 量化章缺它 |
| **TinyChatEngine** | 960 | [`讲透GPU与系统级`](讲透GPU与系统级/) | 端侧 LLM 推理库（C++），对接端侧AI架构参考 |
| **efficientvit** | 3345 | [`讲透基础模型`](讲透基础模型/)（CV） | 高效视觉基础模型，CV 高效章核心 |
| **duo-attention** | 540 | [`讲透基础模型`](讲透基础模型/)（长上下文） | ICLR 2025 长上下文高效，与 streaming-llm 配对 |
| **tiny-training** | 524 | [`讲透微调`](讲透微调/) | 256KB 端侧训练，微调章的"极端约束"案例 |

### 🟡 P1（中星 + 有对接点）

amc（AutoML 压缩）/ haq（硬件感知量化）/ distrifuser（分布式扩散）/ offsite-tuning（离场微调）/ hardware-aware-transformers（HAT）/ radial-attention（稀疏 attention）/ streaming-vlm（视频流式）。

---

## 六、与 work4ai 的关系

| 本地图梳理的 | work4ai 深度版 |
|---|---|
| AWQ / SmoothQuant / QServe 量化 | [`讲透GPU与系统级`](讲透GPU与系统级/)（量化章）|
| Streaming-LLM / DuoAttention 长上下文 | [`讲透基础模型`](讲透基础模型/)（长上下文）|
| Once-for-All / ProxylessNAS 架构搜索 | [`讲透基础模型`](讲透基础模型/)（NAS）|
| MCUNet / TinyEngine 端侧 | [`端侧AI架构参考`](端侧AI架构参考.md) |
| EfficientViT 高效视觉 | [`讲透基础模型`](讲透基础模型/)（CV）|
| AMC / HAQ 压缩 | [`讲透GPU与系统级`](讲透GPU与系统级/)（压缩）|

**阅读方式**：先读本地图找到感兴趣的研究主题 → 对应读 work4ai 讲透系列搞懂原理 → 回 HAN Lab 仓库看论文配套实现。

---

## 七、附录：全 72 仓库分类速览表

<!-- ALL_72_START -->


#### 端侧/IoT 部署（9 个）

| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 1204 | [`tinyml`](https://github.com/mit-han-lab/tinyml) | Python |  |
| 960 | [`TinyChatEngine`](https://github.com/mit-han-lab/TinyChatEngine) | C++ | TinyChatEngine: On-Device LLM Inference Library |
| 952 | [`tinyengine`](https://github.com/mit-han-lab/tinyengine) | C | [NeurIPS 2020] MCUNet: Tiny Deep Learning on IoT Devices;  |
| 709 | [`mcunet`](https://github.com/mit-han-lab/mcunet) | Python | [NeurIPS 2020] MCUNet: Tiny Deep Learning on IoT Devices;  |
| 524 | [`tiny-training`](https://github.com/mit-han-lab/tiny-training) | Python | On-Device Training Under 256KB Memory [NeurIPS'22] |
| 116 | [`mlsys2026-flashinfer-contest`](https://github.com/mit-han-lab/mlsys2026-flashinfer-contest) | Python |  |
| 79 | [`tinychat-tutorial`](https://github.com/mit-han-lab/tinychat-tutorial) | C++ |  |
| 15 | [`iccad-tinyml-open`](https://github.com/mit-han-lab/iccad-tinyml-open) | C | [ICCAD'22 TinyML Contest] Efficient Heart Stroke Detection |
| 8 | [`mlsys2026-flashinfer-contest-solution`](https://github.com/mit-han-lab/mlsys2026-flashinfer-contest-solution) | Python |  |

#### LLM 量化/压缩（6 个）

| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 3610 | [`llm-awq`](https://github.com/mit-han-lab/llm-awq) | Python | [MLSys 2024 Best Paper Award] AWQ: Activation-aware Weight |
| 1674 | [`smoothquant`](https://github.com/mit-han-lab/smoothquant) | Python | [ICML 2023] SmoothQuant: Accurate and Efficient Post-Train |
| 852 | [`omniserve`](https://github.com/mit-han-lab/omniserve) | C++ | [MLSys'25] QServe: W4A8KV4 Quantization and System Co-desi |
| 408 | [`haq`](https://github.com/mit-han-lab/haq) | Python | [CVPR 2019, Oral] HAQ: Hardware-Aware Automated Quantizati |
| 202 | [`fouroversix`](https://github.com/mit-han-lab/fouroversix) | Python | Code for the papers: “Four Over Six: More Accurate NVFP4 Q |
| 160 | [`apq`](https://github.com/mit-han-lab/apq) | Python | [CVPR 2020] APQ: Joint Search for Network Architecture, Pr |

#### LLM 长上下文/稀疏 attention（11 个）

| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 7258 | [`streaming-llm`](https://github.com/mit-han-lab/streaming-llm) | Python | [ICLR 2024] Efficient Streaming Language Models with Atten |
| 715 | [`fastcomposer`](https://github.com/mit-han-lab/fastcomposer) | Python | [IJCV] FastComposer: Tuning-Free Multi-Subject Image Gener |
| 609 | [`lite-transformer`](https://github.com/mit-han-lab/lite-transformer) | Python | [ICLR 2020] Lite Transformer with Long-Short Range Attenti |
| 608 | [`radial-attention`](https://github.com/mit-han-lab/radial-attention) | Python | [NeurIPS 2025] Radial Attention: O(nlogn) Sparse Attention |
| 544 | [`Block-Sparse-Attention`](https://github.com/mit-han-lab/Block-Sparse-Attention) | C++ | A sparse attention kernel supporting mix sparse patterns |
| 540 | [`duo-attention`](https://github.com/mit-han-lab/duo-attention) | Python | [ICLR 2025] DuoAttention: Efficient Long-Context LLM Infer |
| 400 | [`Quest`](https://github.com/mit-han-lab/Quest) | Cuda | [ICML 2024] Quest: Query-Aware Sparsity for Efficient Long |
| 281 | [`x-attention`](https://github.com/mit-han-lab/x-attention) | Python | [ICML 2025] XAttention: Block Sparse Attention with Antidi |
| 142 | [`flatformer`](https://github.com/mit-han-lab/flatformer) | Python | [CVPR'23] FlatFormer: Flattened Window Attention for Effic |
| 137 | [`spatten`](https://github.com/mit-han-lab/spatten) | Scala | [HPCA'21] SpAtten: Efficient Sparse Attention Architecture |
| 82 | [`sparsevit`](https://github.com/mit-han-lab/sparsevit) | Python | [CVPR'23] SparseViT: Revisiting Activation Sparsity for  E |

#### VLM/VLA 高效（7 个）

| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 2221 | [`temporal-shift-module`](https://github.com/mit-han-lab/temporal-shift-module) | Python | [ICCV 2019] TSM: Temporal Shift Module for Efficient Video |
| 1063 | [`streaming-vlm`](https://github.com/mit-han-lab/streaming-vlm) | Python | StreamingVLM: Real-Time Understanding for Infinite Video S |
| 647 | [`hart`](https://github.com/mit-han-lab/hart) | Python | HART: Efficient Visual Generation with Hybrid Autoregressi |
| 475 | [`vlash`](https://github.com/mit-han-lab/vlash) | Python | Real-Time VLAs via Future-state-aware Asynchronous Inferen |
| 426 | [`vila-u`](https://github.com/mit-han-lab/vila-u) | Python | [ICLR 2025] VILA-U: a Unified Foundation Model Integrating |
| 85 | [`foreact`](https://github.com/mit-han-lab/foreact) | Python | [CVPR 2026 Highlight] ForeAct: Steering Your VLA with Effi |
| 26 | [`VisCompare`](https://github.com/mit-han-lab/VisCompare) | Python | A WebUI for Side-by-Side Comparison of Media (Images/Video |

#### 视觉模型高效（9 个）

| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 3345 | [`efficientvit`](https://github.com/mit-han-lab/efficientvit) | Python | Efficient vision foundation models for high-resolution gen |
| 3229 | [`bevfusion`](https://github.com/mit-han-lab/bevfusion) | Python | [ICRA'23] BEVFusion: Multi-Task Multi-Sensor Fusion with U |
| 1470 | [`torchsparse`](https://github.com/mit-han-lab/torchsparse) | Cuda | [MICRO'23, MLSys'22] TorchSparse: Efficient Training and I |
| 779 | [`anycost-gan`](https://github.com/mit-han-lab/anycost-gan) | Python | [CVPR 2021] Anycost GANs for Interactive Image Synthesis a |
| 679 | [`pvcnn`](https://github.com/mit-han-lab/pvcnn) | Python | [NeurIPS 2019, Spotlight] Point-Voxel CNN for Efficient 3D |
| 622 | [`spvnas`](https://github.com/mit-han-lab/spvnas) | Python | [ECCV 2020] Searching Efficient 3D Architectures with Spar |
| 326 | [`litepose`](https://github.com/mit-han-lab/litepose) | Python | [CVPR'22] Lite Pose: Efficient Architecture Design for 2D  |
| 95 | [`patch_conv`](https://github.com/mit-han-lab/patch_conv) | Python | Patch convolution to avoid large GPU memory usage of Conv2 |
| 47 | [`e3d`](https://github.com/mit-han-lab/e3d) | - | Efficient 3D Deep Learning |

#### 生成模型高效（5 个）

| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 1308 | [`data-efficient-gans`](https://github.com/mit-han-lab/data-efficient-gans) | Python | [NeurIPS 2020] Differentiable Augmentation for Data-Effici |
| 1116 | [`gan-compression`](https://github.com/mit-han-lab/gan-compression) | Python | [CVPR 2020] GAN Compression: Efficient Architectures for I |
| 727 | [`distrifuser`](https://github.com/mit-han-lab/distrifuser) | Python | [CVPR 2024 Highlight] DistriFusion: Distributed Parallel I |
| 4 | [`gan-compression-dynamic`](https://github.com/mit-han-lab/gan-compression-dynamic) | Python |  |
| 4 | [`data-efficient-gans-dynamic`](https://github.com/mit-han-lab/data-efficient-gans-dynamic) | Python |  |

#### NAS/架构搜索（2 个）

| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 1953 | [`once-for-all`](https://github.com/mit-han-lab/once-for-all) | Python | [ICLR 2020] Once for All: Train One Network and Specialize |
| 1446 | [`proxylessnas`](https://github.com/mit-han-lab/proxylessnas) | C++ | [ICLR 2019] ProxylessNAS: Direct Neural Architecture Searc |

#### 分布式/系统（5 个）

| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 815 | [`kernel-design-agents`](https://github.com/mit-han-lab/kernel-design-agents) | - |  |
| 366 | [`KernelWiki`](https://github.com/mit-han-lab/KernelWiki) | Python |  |
| 201 | [`inter-operator-scheduler`](https://github.com/mit-han-lab/inter-operator-scheduler) | C++ | [MLSys 2021] IOS: Inter-Operator Scheduler for CNN Acceler |
| 178 | [`parallel-computing-tutorial`](https://github.com/mit-han-lab/parallel-computing-tutorial) | C++ |  |
| 104 | [`lpd`](https://github.com/mit-han-lab/lpd) | Python | [ICLR 2026 Oral] Locality-aware Parallel Decoding for Effi |

#### 其他/研究（18 个）

| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 1656 | [`torchquantum`](https://github.com/mit-han-lab/torchquantum) | Jupyter Notebook | A PyTorch-based framework for Quantum Classical Simulation |
| 483 | [`dlg`](https://github.com/mit-han-lab/dlg) | Python | [NeurIPS 2019] Deep Leakage From Gradients |
| 450 | [`amc`](https://github.com/mit-han-lab/amc) | Python | [ECCV 2018] AMC: AutoML for Model Compression and Accelera |
| 386 | [`offsite-tuning`](https://github.com/mit-han-lab/offsite-tuning) | Python | Offsite-Tuning: Transfer Learning without Full Model |
| 337 | [`hardware-aware-transformers`](https://github.com/mit-han-lab/hardware-aware-transformers) | Python | [ACL'20] HAT: Hardware-Aware Transformers for Efficient Na |
| 253 | [`flash-moba`](https://github.com/mit-han-lab/flash-moba) | C++ |  |
| 178 | [`ncu-report-skill`](https://github.com/mit-han-lab/ncu-report-skill) | Python |  |
| 176 | [`fastrl`](https://github.com/mit-han-lab/fastrl) | Python | [ASPLOS'26] Taming the Long-Tail: Efficient Reasoning RL T |
| 168 | [`amc-models`](https://github.com/mit-han-lab/amc-models) | Python | [ECCV 2018] AMC: AutoML for Model Compression and Accelera |
| 55 | [`bnn-icestick`](https://github.com/mit-han-lab/bnn-icestick) | Jupyter Notebook | Binary Neural Network on IceStick FPGA. |
| 41 | [`neurips-micronet`](https://github.com/mit-han-lab/neurips-micronet) | Jupyter Notebook | [JMLR'20] NeurIPS 2019 MicroNet Challenge Efficient Langua |
| 33 | [`vcpo`](https://github.com/mit-han-lab/vcpo) | Python | [ICML 2026] Stable Asynchrony: Variance-Controlled Off-Pol |
| 30 | [`pruning-sparsity-publications`](https://github.com/mit-han-lab/pruning-sparsity-publications) | - |  |
| 16 | [`SMEPO`](https://github.com/mit-han-lab/SMEPO) | Python |  |
| 16 | [`sparserefine`](https://github.com/mit-han-lab/sparserefine) | Python | [ECCV 2024] SparseRefine: Sparse Refinement for Efficient  |
| 8 | [`ml-blood-pressure`](https://github.com/mit-han-lab/ml-blood-pressure) | Python |  |
| 8 | [`calo-cluster`](https://github.com/mit-han-lab/calo-cluster) | Jupyter Notebook |  |
| 1 | [`mmpose`](https://github.com/mit-han-lab/mmpose) | - | OpenMMLab Pose Estimation Toolbox and Benchmark. |

---

**数据源**：GitHub API `orgs/mit-han-lab/repos`（2026-08-10 抓取，72 个公开仓库去重）｜ **分类规则**：基于 name+description 关键词正则，边界库可能跨域 ｜ **维护**：HAN Lab 每月新增论文配套仓库，可月度刷新。
