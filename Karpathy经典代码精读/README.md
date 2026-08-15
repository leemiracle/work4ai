# Karpathy 经典代码精读

> **Andrej Karpathy** 的 GitHub 仓库（`github.com/karpathy`，**54 个原创 + 9 个 fork**）系统化精读。核心教学项目已下载到 ``repos/``，逐项目 step-by-step 分析，每个配 bash 可跑验证。
>
> Karpathy 的项目是 work4ai「三层讲透 + 源码对照」理念的最佳素材——**小而美、可纯标准库/CPU 跑透、每行都有教学价值**。micrograd 仅 94 行讲透整个 autograd，nanoGPT 666 行讲透整个 GPT 训练。

---

## ⚙️ 下载方式（重要 · 2026-08-10 实测）

GitHub 直连（`github.com:443`）当前**连接超时**，主流镜像（kkgithub/ghproxy/gitclone）也多 502/超时。**可用方案**：

| 方式 | 命令 | 状态 |
|---|---|---|
| ✅ **codeload tarball**（官方下载域名，不同 IP）| `curl -sfL https://codeload.github.com/karpathy/{repo}/tar.gz/refs/heads/master \| tar xz` | **当前可用，本目录就用它下的** |
| ✅ raw 直读单文件 | `curl -sfL https://raw.githubusercontent.com/karpathy/{repo}/master/{path}` | 可用 |
| ✅ gh.idayer.com 代理 clone | `git clone https://gh.idayer.com/https://github.com/karpathy/{repo}.git` | 可用 |
| ✅ zread MCP 工具（不依赖本机网络）| `zread_read_file(repo_name='karpathy/{repo}', file_path=...)` | 可用，逐文件读 |
| ❌ github.com 直连 clone | — | 超时 |
| ❌ ghproxy / kkgithub / gitclone | — | 502/超时 |

> 复现下载：见 ``repos/`` 已落 14 个核心项目（11MB）。批量脚本见本目录历史会话。

---

## 一、Tier 1 · 已下载核心教学项目（14 个，11MB）

> 全部用 codeload tarball 下载，源码在 `repos/{name}/`。精读笔记 `0X-{name}.md`。

| # | 仓库 | stars | 核心文件（行数）| 主题 | 对接 work4ai | 精读 |
|---|---|---:|---|---|---|:---:|
| 1 | **micrograd** | 17k | `engine.py` 94 + `nn.py` 60 | 标量 autograd 引擎 + MLP | [`讲透反向传播`](../讲透PyTorch/01-Autograd与计算图.md) / [`讲透PyTorch`](../讲透PyTorch/)(autograd) | ✅ |
| 2 | **nanoGPT** | 62k | `model.py` 330 + `train.py` 336 | 最简可训 GPT | [`讲透Transformer`](../讲透Transformer/) / [`讲透基础模型`](../讲透基础模型/) | ⏳ |
| 3 | **minbpe** | 10k | `base.py` 165 + `regex.py` 164 | BPE 分词器从零实现 | [`讲透NLP`](../讲透NLP/)(分词) / [`讲透Transformer/13`](../讲透Transformer/13-Tokenizer.md) | ⏳ |
| 4 | **makemore** | 4.1k | `makemore.py` 719 | 字符级 AR LM（bigram→MLP→RNN→Transformer 渐进）| [`讲透NLP/03`](../讲透NLP/03-N元语法语言模型.md) | ⏳ |
| 5 | **llama2.c** | 19k | `runq.c` 1092 + `run.c` 973 + `export.py` 567 | 纯 C 推理 Llama2 | [`讲透GPU与系统级`](../讲透GPU与系统级/)(推理) | ⏳ |
| 6 | **minGPT** | 24k | `model.py` 310 + `trainer.py` 109 | minimal GPT（nanoGPT 前身）| [`讲透Transformer`](../讲透Transformer/) | ⏳ |
| 7 | **build-nanogpt** | 5.4k | `train_gpt2.py` 521 | 视频+代码：从零搭 GPT2 | [`讲透基础模型`](../讲透基础模型/) | ⏳ |
| 8 | **llm.c** | 30k | `train_gpt2.cu` 1904 | C/CUDA 训练 GPT2 | [`讲透GPU与系统级`](../讲透GPU与系统级/)(CUDA) | ⏳ |
| 9 | **nn-zero-to-hero** | 23k | 8 个 `.ipynb` | 神经网零到英雄课（micrograd→makemore→GPT）| 全系列前置 | ⏳ |
| 10 | **lecun1989-repro** | 780 | `modern.py` 210 + `repro.py` 167 | 复现 LeCun 1989 论文 | [`讲透反向传播`](../讲透PyTorch/01-Autograd与计算图.md)(历史) | ⏳ |
| 11 | **pytorch-normalizing-flows** | 917 | `flows.py` 294 + `spline_flows.py` 253 | Normalizing Flows | [`讲透生成模型`](../讲透生成模型/) | ⏳ |
| 12 | **pytorch-made** | 594 | `made.py` 144 | MADE（Masked Autoencoder）| [`讲透生成模型`](../讲透生成模型/) | ⏳ |
| 13 | **deep-vector-quantization** | 654 | `vqvae.py` 201 | VQ-VAE | [`讲透生成模型`](../讲透生成模型/) | ⏳ |
| 14 | **randomfun** | 1.1k | `.ipynb` 杂项 | 杂项实验 notebook | 背景 | ⏳ |

**精读工作量预估**：micrograd 154 行（样板，已完成）→ 后续每个项目按"核心文件 × 逐段分析 × bash 跑通"模式推进。llm.c/llama2.c 较大（千行级）会分多次。

---

## 二、Tier 2 · 课程/大项目（读 README + 关键文件，不全下载）

| 仓库 | stars | 性质 | 处理 |
|---|---:|---|---|
| **autoresearch** | 93k | AI agents 跑 nanochat 训练研究（最新最大）| 读 README + 架构说明 |
| **LLM101n** | 37k | 课程：build a Storyteller（蓝海课程）| 读 syllabus |
| **nanochat** | 57k | "$100 能买到的最好 ChatGPT" | 读 README + 训练脚本骨架 |
| **llm-council** | 23k | 多 LLM 协作答难题 | 读 README |

---

## 三、Tier 3 · 工程项目（读 README，索引）

arxiv-sanity-preserver(5.7k) · arxiv-sanity-lite(1.6k) · neuraltalk2(5.5k 图像字幕) · neuraltalk(5.5k py2 多模态) · reader3(3.8k) · rendergit(2.4k) · ng-video-lecture(4.9k) · researchpooler · jobs · covid-sanity · hn-time-capsule · ulogme(1.2k)

---

## 四、Tier 4 · 历史 / JS / Lua / Blog（不下载，仅索引说明）

> 这些是 Karpathy 早期或非 Python 的工作，历史价值高但与 work4ai「Python 三层讲透」范式不直接契合，只做索引。

| 仓库 | stars | 语言 | 说明 |
|---|---:|---|---|
| **char-rnn** | 12k | Lua | 2015 经典：LSTM 字符级生成（莎士比亚）。**深度学习教学祖师级项目**，但 Lua/Torch7 已淘汰 |
| **convnetjs** | 11k | JS | 浏览器里跑 CNN，2014 年现象级 demo |
| **reinforcejs** | 1.5k | JS | 浏览器 RL（DP/Q-learning/DQN/PG）|
| **recurrentjs** | 985 | JS | 浏览器 RNN/LSTM |
| **tsnejs** | 912 | JS | 浏览器 t-SNE |
| **svmjs** | 709 | JS | 浏览器 SVM |
| **karpathy.github.io** | 1.9k | CSS | 博客源（"The Unreasonable Effectiveness of RNNs" 等名篇出处）|
| **paper-notes** | 711 | — | 论文笔记 |
| **cryptos** | 1.9k | py | 从零实现加密（教学）|
| **rustbpe** | 507 | Rust | tiktoken 缺失的训练代码（Rust BPE）|

---

## 五、与 work4ai 的关系

Karpathy 的项目天然对接 work4ai 的"讲透源码"维度：

```
work4ai 讲透系列（讲原理）   ←→   Karpathy 项目（讲实现）
─────────────────────────────────────────────────
讲透反向传播                  ←→  micrograd (94 行 autograd)
讲透Transformer              ←→  nanoGPT / minGPT / build-nanogpt
讲透基础模型                  ←→  nanoGPT / llm.c / nanochat
讲透NLP (分词)                ←→  minbpe
讲透NLP (N-gram)              ←→  makemore
讲透GPU与系统级 (推理/CUDA)    ←→  llama2.c / llm.c
讲透生成模型                  ←→  pytorch-normalizing-flows / pytorch-made / deep-vector-quantization
讲透RL                       ←→  reinforcejs (JS, 历史)
```

**阅读方式**：先读 work4ai 讲透系列搞懂原理 → 再读对应 Karpathy 项目源码看"最简实现长什么样" → 跑通验证。两者互补：讲透系列钻深度，Karpathy 代码钻"最小可运行实现"。

---

## 六、精读笔记清单

| 笔记 | 项目（核心行数）| 状态 |
|---|---|:---:|
| [`01-micrograd-自动微分引擎.md`](./01-micrograd-自动微分引擎.md) | micrograd (94行 autograd) | ✅ 样板 |
| [`02-minbpe-BPE分词器.md`](./02-minbpe-BPE分词器.md) | minbpe (329行 BPE) | ✅ |
| [`03-pytorch-made-掩码自编码器.md`](./03-pytorch-made-掩码自编码器.md) | pytorch-made (144行 MADE) | ✅ |
| [`04-lecun1989-repro-复现1989论文.md`](./04-lecun1989-repro-复现1989论文.md) | lecun1989-repro (422行 ConvNet) | ✅ |
| [`05-deep-vector-quantization-VQVAE.md`](./05-deep-vector-quantization-VQVAE.md) | VQ-VAE (311行核心量化) | ✅ |
| [`06-minGPT-minimal-GPT.md`](./06-minGPT-minimal-GPT.md) | minGPT (310行 GPT 架构) | ✅ |
| [`07-nanoGPT-从零训练GPT.md`](./07-nanoGPT-从零训练GPT.md) | nanoGPT (666行 可训 GPT) | ✅ |
| [`08-build-nanogpt-从零搭GPT2.md`](./08-build-nanogpt-从零搭GPT2.md) | build-nanogpt (521行 完整管线) | ✅ |
| [`09-makemore-字符级语言模型.md`](./09-makemore-字符级语言模型.md) | makemore (719行 6范式渐进) | ✅ |
| [`10-pytorch-normalizing-flows.md`](./10-pytorch-normalizing-flows.md) | NF (644行 精确密度) | ✅ |
| `11-llama2.c-纯C推理.md` | llama2.c (2632行 C) | ⏳ |
| `12-llm.c-CUDA训练GPT2.md` | llm.c (1904行 CUDA) | ⏳ |
| `13-nn-zero-to-hero-课程集.md` | nn-zero-to-hero (8 notebook) | ⏳ |
| `14-randomfun-杂项.md` | randomfun (notebook) | ⏳ |

---

**最后更新**：2026-08-10 ｜ **下载方式**：codeload tarball（GitHub 直连被限）｜ **精读进度**：10/14 完成（含 **GPT 三连** + **生成模型四件** micrograd/minbpe/VQ-VAE/NF + **makemore 6 范式**），剩 4 个：llama2.c(C大件)/llm.c(CUDA最大)/nn-zero-to-hero/randomfun
