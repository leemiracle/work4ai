# E · 解码微调记忆三重奏：DeepSpec / ESFT / Engram 深读笔记

> 深读对象：`C:\workspace\work4ai\.tools\deepseek-repos\` 下三个本地浅克隆仓库（DeepSpec、ESFT、Engram）。
> 方法：README + 全部配置/脚本 + 核心源码（modeling/loss/eval/trainer/data pipeline）+ Engram 论文 PDF（33 页，本地 pypdf 提取全文）。
> 诚实约束：所有数字均来自实际读到的文件；任务简报中提到但仓库中**不存在**的机制（hint、fuzz、trace、统计显著性检验、clock 同步）已明确标注为"未在仓库中出现"。

---

## 1. DeepSpec —— 投机解码草稿模型的全栈训练-评测工厂

**定位一句话**：把"给任意目标模型训练投机解码草稿模型"做成数据制备→训练→评测的标准化流水线，内置 DSpark / DFlash / Eagle3 三种草稿算法，覆盖 Qwen3-4B/8B/14B 与 gemma-4-12B-it 四个目标（README.md:58-62）。

- 仓库：MIT 协议；最新 commit 2026-07-09（active）。DSpark 论文 = *Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation*（arXiv:2607.05147）；DFlash（arXiv:2602.06036）；Eagle3（arXiv:2503.01840）。致谢 SpecForge（Apache-2.0，Eagle3 训练框架与部分代码来源）与 z-lab/dflash（NOTICE:10-37）。

### 1.1 三种算法与配置差异（config/ 实测）

三份配置只有 `model` 段不同，训练段完全一致（lr 6.0e-4、warmup_ratio 0.04、bf16、local_batch_size=1、global_batch_size=512、10 epochs、max_grad_norm 1.0、FSDP no_shard、dspark/dflash 开 torch_compile）：

| 字段 | DSpark (`config/dspark/dspark_qwen3_4b.py`) | DFlash (`config/dflash/dflash_qwen3_4b.py`) | Eagle3 (`config/eagle3/eagle3_qwen3_4b.py`) |
|---|---|---|---|
| block_size / ttt_length | 7 | 7 | ttt_length=7 |
| 草稿层数 | num_draft_layers=5 | 5 | draft_num_hidden_layers=**1** |
| target_layer_ids | [1,9,17,25,33] | 同左 | 同左 |
| markov_rank | **256**（vanilla） | **0**（禁用 markov head） | — |
| confidence_head_alpha | 1.0（with markov） | 0.0（禁用） | — |
| 损失 | ce_alpha=0.1 + l1_alpha=**0.9**，decay_gamma=4.0 | ce_alpha=**1.0**（纯 CE） | step_loss_decay=0.8（软 CE 蒸馏） |
| seed | 42 | 42 | 0 |

即 **DFlash 就是"去掉 markov head + 置信头、只留 CE 损失"的 DSpark 消融版**，两者共用 `Qwen3DSparkTrainer`（`deepspec/trainer/dspark_trainer.py:14-22`）。

### 1.2 核心机制（源码级）

**（a）半自回归块式草稿（DSpark）** —— `deepspec/modeling/dspark/qwen3/modeling.py`
- 草稿注意力把 K/V 拼成两段：上下文段直接从**目标模型隐状态**投影（`k_ctx = k_proj(target_hidden_states)`），草稿段从自身隐状态投影（modeling.py:103-112）——草稿一次前向并行吐出 7 个位置，块内非因果（`is_causal=False`，draft_ops.py:42）。
- 目标多层特征拼接：5 层 × hidden 拼接后过 `fc` 线性层 + `hidden_norm`（modeling.py:240-245, 373）。
- 草稿的 embed_tokens 与 lm_head **直接从目标模型复制并冻结**（`initialize_embeddings_and_head(freeze=True)`，base_trainer.py:276-280）——权重复用的典型做法。

**（b）锚点训练（anchor training）** —— `deepspec/modeling/dspark/common.py:123-169`
- 每条序列随机采样最多 `num_anchors=512` 个锚点；每个锚点构成一个 7-token 训练块：块首放真实 token，其余 6 位全是 `mask_token_id=151669`（`create_noise_embed`，common.py:264-294）。
- flex_attention 块掩码：每个草稿块只看"锚点之前的上下文 + 自己块内"（`create_dspark_attention_mask`，common.py:78-106），一次前向同时训练数百个块。

**（c）Markov 头三种变体** —— `deepspec/modeling/dspark/markov_head.py`
- `VanillaMarkov`：`nn.Embedding(V, 256)` + `Linear(256, V)`，给每个位置的 logits 加一个"上一个 token 的马尔可夫偏置"（markov_head.py:8-90）；
- `GatedMarkovHead`：sigmoid 门控混合 hidden 与前 token embedding（93-122）；
- `RNNHead`：GRU 式递归态跨块内位置传递，位置 k 可访问全部前缀历史（125-284）。

**（d）损失函数（最讲究的部分）** —— `deepspec/modeling/dspark/loss.py`
- 理论接受率直接进损失：`accept_rate = 1 − 0.5·Σ|p_draft − p_target|`（L1 总变差上界，loss.py:69）；
- 三项加权：`0.1·CE + 0.9·L1分布距离 + 1.0·置信头BCE`，位置衰减权重 `exp(−pos/4.0)`（loss.py:25-37）；
- 置信头目标是** detached 的逐步接受率**（loss.py:156-161）——把"投机解码会不会被接受"变成可学习的标量；
- 训练日志直接埋了 `accept_rate@k`（分位置）与 `tau_probabilistic`（期望接受长度 τ）指标（loss.py:192-204）。

**（e）置信调度（confidence-scheduled）推理** —— `deepspec/eval/dspark/draft_ops.py:82-131`
- 置信头输出逐步 sigmoid 概率，`_confident_prefix_length` 在首个低于阈值的位置截断提案（eval.py 的 `--confidence-threshold`，默认 0.0=不截断、同时采集校准数据）；
- 校准度量全套：**ECE（20 bins）、AUROC（1000 细 bins 直方图法）、Brier、reliability diagram**（`confidence_head.py:28-172`，`CONFIDENCE_NUM_BINS=20`/`CONFIDENCE_NUM_FINE_BINS=1000`，evaluator.py:28-29）。

**（f）验证协议（正确性）** —— `deepspec/eval/base_evaluator.py:186-304`
- 标准拒绝采样：`accept_prob = min(1, p_target/p_draft)`，接受掩码取 cumprod 得前缀；拒绝后从残差分布 `sample_residual` 采下一 token（base_evaluator.py:252-285）——**输出分布与目标模型严格同分布，正确性由构造保证**，无需额外等价性测试；
- EOS 特判：被接受前缀里含停止符则提前终止并裁剪 KV（`past_key_values_target.crop(start)`，base_evaluator.py:418-425）。

**（g）评测基准与指标** —— `eval.py:18-28`
- 9 个数据集（jsonl 已内置）：gsm8k/math500(500)、aime25(**30**)、humaneval(164)/mbpp(256)/livecodebench(500)、mt-bench(80)/alpaca(500)/arena-hard-v2(500)；temperature=1.0、max_new_tokens=2048、bsz=1、eval seed=980406；
- 指标体系：`#propose`（每次提案草稿 token 数，形如 "6.14+1"）、`accept_len`（含赠送 token 的接受长度）、`verify_rate`、`accept_rate@pos`（分位置接受率，all_reduce 汇总，base_evaluator.py:550-630）。

### 1.3 Target Cache：训练数据的"38 TB 上下文缓存"

- 三步数据流水线（`scripts/data/README.md`）：① `mlabonne/open-perfectblend` 下载切分（test_size 0.05）→ ② 用 SGLang 起本地目标模型重生成答案（8 worker、temperature 0.7 / top-p 0.8 / top-k 20 / max-tokens 4096 / **--disable-thinking**、并发 32）→ ③ `prepare_target_cache.py` 用 forward hook 抓取目标模型第 [1,9,17,25,33] 层原始隐状态 + 最后层隐状态，`AsyncTargetCacheWriter` 异步写盘（shard 上限 64 GB，min_loss_tokens=14，hidden=bfloat16/token=int32/mask=uint8，manifest 含 **git_sha**，target_cache_dataset.py:24-26, 123-166；prepare_target_cache.py:83-134）。
- **默认 Qwen3-4B 配置下缓存约 38 TB**（scripts/data/README.md:116-121）——用磁盘换训练时反复跑目标模型的前向，这是"target cache = 极端版上下文缓存"的工程实证。
- 细节约束：`target_layer_ids` 禁止取最后一层（Transformers 的 output_hidden_states 存的是 norm 后隐状态，与 hook 抓的原始层输出不一致，`assert_no_final_target_layer`，base_evaluator.py:100-112）。

### 1.4 工程与可复现性

- 依赖极简：torch 2.9.1 / transformers 5.10.2 / triton 3.5.1 等（requirements.txt），SGLang 仅数据再生需要；
- `BF16Optimizer`：fp32 主权重 AdamW + warmup-cosine，spec是 SpecForge 移植（utils/optim.py:82-106）；
- 恢复与调度：`StatelessResumableDistributedSampler` 按全局样本偏移断点续训、`SuspendController` 支持集群抢占挂起、每 3000 步存 checkpoint 并自动提交评测（base_trainer.py:295-407）；
- 启动时打印 git sha + git diff（train.py:42-44）；每 rank eval 用 `seed_all(seed+idx)`（base_evaluator.py:531）。
- **12 个官方 checkpoint** 全部放出（3 算法 × 4 目标），README 明确要求复现论文 Table 1 必须对齐本仓库训练设置，且域内使用建议重训草稿（README.md:53-65）。

### 1.5 任务简报中提到但仓库里没有的东西（诚实声明）

全仓 grep（hint / fuzz / trace / significance / bootstrap / permutation / clock / speedup / wall_time / extrapol）**均无命中**：本仓库不测墙钟加速比（只测 token 级接受率指标），无统计显著性检验，无 fuzz 测试，无 trace 生成器，无时钟同步代码，无 woodpecker / 自投机 / MTP baseline（三者是 DSpark 论文层面的对比，不在代码库中）。以上若出现在二手描述里，属于论文或博客内容，非本仓库资产。

---

## 2. ESFT —— 只微调"被任务激活的那几个专家"

**定位一句话**：用前向激活统计挑出每层与任务最相关的少量路由专家、只训这些专家（路由器/共享专家/注意力全冻结）的 MoE 专属参数高效微调（EMNLP 2024 Main，arXiv:2407.01906；最后 commit 2025-05-22）。

### 2.1 核心机制（源码级）

**（a）专家选择流水线（激活统计）**
1. `scripts/expert/get_expert_scores.py`：加载底座（`deepseek-ai/ESFT-vanilla-lite`）后设 `model.config.log_expert_weights=True` + `expert_log_dir`，在训练分布上前向约 **131072 tokens**（README 示例 `--n_sample_tokens=131072`），逐 token 记录 top-6 被选专家 id 与路由权重（日志写文件的实现在 HF 远程代码模型内，本地 `deepseek/modeling_deepseek.py` 只含 MoE 前向；get_expert_scores.py:32-39）；
2. `scripts/expert/generate_expert_config.py`：两种打分（**token_scores** = 每次被选中计 1/TOP_K；**gate_scores** = 路由权重求和），硬编码 `TOP_K=6, N_EXPERTS=64, N_LAYERS=26`（"27 层总，第 1 层非 MoE"，generate_expert_config.py:16-18），逐层按分数降序贪心选到**累计占比 ≥ top_p（示例 0.2）**为止；
3. 实测产物 `results/expert_configs/intent.json`：每层入选 **4~6 个专家**（如第 1 层 [8,26,55,6,20]）≈ 全部 64×26=1664 个专家中训练 **约 7%**。

**（b）冻结的实现（最巧的一段）** —— `esft.py:8-40, 59-77`
- `to_buffer(module)` 递归把参数 unregister 成 **persistent=False 的 buffer**——参数不出现在 `state_dict()`、optimizer 不见它、梯度为零，但前向完全照常；`to_param` 反向恢复；
- `to_esft()`：默认全模型 to_buffer（**路由器 MoEGate、注意力、嵌入、lm_head 全冻**），再按 expert_cfg 把选中专家 to_param；`shared_experts` 默认冻结（`--train_shared_experts` 可解冻），`--train_non_expert_modules` 可解冻全部非专家模块；
- 混合精度细节：`DeepseekV2MLP.forward` 自动把输入 cast 到专家权重的 dtype，让 **fp32 可训练专家与 bf16 冻结专家在同一层聚合**（deepseek/modeling_deepseek.py:409-418）。

**（c）训练配置** —— `configs/base.yaml`（全量实测）
- seed 5934875、seq_length 4096、**lr 1e-5 constant**、500 steps、warmup 0、weight_decay 0.1、adamw_torch_fused（β2=0.95）、bf16、梯度检查点、per-device bs 1 × grad accum 4、**ep_size 2**（专家并行）、`random_concat_ratio 0.2`（数据打包时 20% 概率随机拼接样本——utils.py:47-76）。

**（d）专家并行版 train_ep.py 的三个手艺**
- 自管专家梯度同步：把 `.expert` 参数排除出 DDP，`custom_backward` 里在 edp_group 上手动 `all_reduce(AVG)`（train_ep.py:249-260）；
- 强制 all2all 次数一致：对最浅可训练层 `requires_grad_(True)` 防 forward 图被截断导致 EP 通信不对称（train_ep.py:114-121）;
- 分片保存再合并：各 EP rank 先落盘 `expert_state_{rank}.bin`，rank0 重试加载合并成完整 checkpoint（train_ep.py:132-244）。

**（e）产物：adapter = expert_cfg.json + 选中专家的 safetensors**
- 加载即"底座 + add_adapter"：`add_adapter` 会校验 expert_cfg 与 state_dict 中专家一致（esft.py:140-163）；
- **官方发布 12 个 adapter**：6 任务（math/code/intent/summary/law/translation）× 2 打分（token/gate），`deepseek-ai/ESFT-{token|gate}-{task}-lite`（scripts/download_adapters.sh）。
- 评测 `eval_multigpu.py`：intent/summary/law/translation 四类，**用 GPT-4-1106-preview 打分（0-10 制，5 次重试）**（benchmarks.py:54-106），结果 jsonl 在 `results/completions/`。

### 2.2 与全参/LoRA 的对比数字

**仓库内没有对比表**（README 与代码均未给出全参 FT / LoRA 的 GPU 时数或存储倍数）——这些数字在 arXiv 论文里，本次未读论文原文，不编造。仓库可实测的数字：训练只动约 7% 专家参数；adapter 文件即仅含这些专家的权重。

---

## 3. Engram —— 条件记忆：LLM 的"第二稀疏轴"

**定位一句话**：给 Transformer 加一个可 O(1) 精确寻址的 N-gram 哈希嵌入大表（静态记忆），用当前隐状态做门控融合，证明"MoE 条件计算 + 条件记忆"的混合配比存在 U 型缩放律，且 100B 参数记忆表可卸载到主机内存推理（Apache-2.0，2026-01 建仓；论文 PDF 随仓发布）。

### 3.1 Lookup 机制（demo 代码 + 论文 双源验证）

数据流（`engram_demo_v1.py` 全部可对上论文 §2）：

1. **Tokenizer 压缩**（`CompressedTokenizer`，demo:60-121）：NFKC/NFD/去音标/小写/空白折叠，把 128k 词表投影成规范 ID（满射 P: V→V'）——实测压缩 **23.43%**（论文附录 C Table 6：'␣' 合并 163 个变体、'a' 合并 54 个……）；
2. **多头哈希**（`NgramHashMapping`，demo:188-303）：后缀 N-gram（N=2,3）经**乘法-XOR 哈希**：`mix = Σ⊕ token_k · multiplier_k`，乘子是按 `seed + 10007×layer_id` 播种的随机奇数（**每层不同**）；每阶 N-gram 配 **K=8 个哈希头**，每头表长取目标规模附近互不相同的**素数**（`find_next_prime`，demo:181-186）——多素数表缓解碰撞；
3. **多查表嵌入**（`MultiHeadEmbedding`，demo:305-324）：所有头的表 offset 拼接成一个大 `nn.Embedding`；每头维度 512/8=64，检索结果拼接为 e_t ∈ R^((3-1)×512)；
4. **上下文感知门控**（demo:358-377；论文式 3-4）：`k=W_K·e_t`，`q=h_t`（当前隐状态=Query，检索记忆=Key/Value 源），双侧 RMSNorm 后点积/√d、过 signed-sqrt 再 sigmoid 得 α∈(0,1)——检索结果与上下文矛盾时门趋零，自动压制哈希碰撞/多义噪声；
5. **短卷积**（`ShortConv`，demo:123-179）：depthwise 因果卷积 kernel=4、dilation=3（=max N-gram 阶），SiLU，**卷积零初始化**（论文附录 A "Engram Conv Zero Init: True"）保证训练起点恒等；
6. **残差注入**：`H ← H + Engram(H, ids)`，位于该 block 的 Attention 和 MoE **之前**（demo:389-394）。与 attention/MoE 的类比：MoE 按**隐状态动态路由**选参数；Engram 按**输入 token 序列确定性寻址**选嵌入——后者可在前向之前算出全部地址，这是可预取的根源。

**多分支集成**（论文 §2.4）：backbone 用 mHC（M=4 分支）；嵌入表与 W_V 跨分支**共享**，M 个分支各自 W_K^(m) 出分支专属门控——一次稠密 FP8 矩阵乘融合。

### 3.2 规模与训练（论文附录 A Table 5 全量数字）

| | MoE-27B（基线） | Engram-27B | Engram-40B |
|---|---|---|---|
| 总参 / 激活 | 26.7B / 3.8B | 26.7B / 3.8B | 39.5B / 3.8B |
| 专家（共享+路由, top-6） | 2+72 | **2+55** | 2+55 |
| Engram 参数 | — | 5.7B | **18.5B** |
| Engram 配置 | — | 层[2,15]、N-gram[2,3]、8头、d_mem 1280、槽位 2,262,400 | 槽位 7,239,680 |
| 训练 | 262B tokens、50k steps、batch 1280、seq 4096、Muon 优化器（backbone）+ Adam 5×lr/无wd（嵌入）、base lr 4e-4、step decay、loss-free 负载均衡、MLA 32头、mHC 4、V3 tokenizer（vocab 129,280） | 同左 | 同左 |

长上下文：YaRN（s=10, α=1, β=32, f=0.707）32k 窗口 5k 步（30B tokens）。

### 3.3 关键实验数字

- **U 型配比律**（论文 §3.1）：固定总参+算力（2e20 / 6e20 FLOPs 两档，稀疏度 P_tot/P_act≈10），纯 MoE（ρ=100%）次优；**最优 ρ≈75-80%**（10B 档 val loss 1.7248→1.7109，Δ0.0139）；MoE 配额砍到 ρ≈40% 仍能打平纯 MoE；
- **无限记忆域**：3B 底座加 Engram，槽位 2.58e5→1e7（≈+13B 参数），val loss 随槽位数**严格幂律（log-线性）下降**——"加内存不涨 FLOPs"的可预测缩放旋钮；
- **27B 主结果**（iso-param & iso-FLOPs）：MMLU 57.4→60.4、CMMLU +4.0、**BBH +5.0（50.9→55.9）**、ARC-C 70.1→73.8、HumanEval 37.8→40.8、MATH 28.3→30.7、GSM8K +2.2、TriviaQA 48.8→50.7；Pile loss 1.960→1.950；意外发现：**推理类收益 > 知识类收益**；
- **长上下文**：Multi-Query NIAH 84.2→**97.0**、Variable Tracking 77.0→87.2（iso-loss 46k 对照）；Engram-27B 只用 82% 预训练 FLOPs（41k 步）即可打平基线 LongPPL；
- **机制解释**（"变深"效应）：LogitLens 分层 KL 散度在浅层系统性更低（预测收敛更快）；CKA 软对齐指数显示 **Engram 第 5 层 ≈ MoE 第 12 层的表示**——把"实体多跳合成"（论文 Table 3：识别"Diana, Princess of Wales"要耗 6 层）外包给查表，等效加深网络；
- **消融**（3B+1.6B Engram，12 层，100B tokens，基线 1.808）：完整配置 1.768（Δ0.04）；单模块插入**第 2 层最优**（1.770），拆成层 2+6 双模块更好；贡献排序：**多分支融合 ≈ 上下文门控 ≈ tokenizer 压缩 > 其它**；去短卷积仅微降；固定预算下加 4-gram 反而略亏；
- **功能二分**（推理时直接抹掉 Engram 输出）：事实知识类**崩塌至仅保留 29-44%**（TriviaQA 29%），阅读理解保留 81-93%（C3 93%）——参数化知识主要存在 Engram 里，上下文理解留在 attention backbone；
- **系统效率**：H800、512 并发、长度 U(100,1024)，**100B 参数嵌入表全量驻留主机 DRAM、走 PCIe 预取**（确定性地址在前一层计算时异步搬运）：4B 底座 9031.62→8858.28 tok/s（−1.9%），8B 底座 6315.52→6140.02（−2.8%）。训练侧：表按 GPU 切片 + All2All 取活跃行（同 DeepEP 思路）；再利用 N-gram Zipf 分布做 HBM/DRAM/NVMe 多级缓存。

### 3.4 工程亮点

- 仓库只放 **demo 级独立实现**（`engram_demo_v1.py`，423 行，mock 掉 Attention/MoE/mHC 专讲 Engram 数据流）+ 论文 PDF + drawio 架构图——"论文仓库"形态，无训练代码、无模型发布（README 明确 demo 需再优化才能生产）；
- 依赖仅 torch/numpy/transformers/sympy（sympy 用于找素数表长）。

---

## 4. 三仓与 DeepSeek V 系的关系

- **ESFT（2024-07）**：直接基于 **DeepSeek-V2 架构**（仓内 `deepseek/modeling_deepseek.py` = DeepseekV2ForCausalLM：MLA + group_limited_greedy 路由 + 共享专家 + aux loss），底座 ESFT-vanilla-lite 即 V2-Lite 的 MoE 微调实验版；
- **DeepSpec（2026）**：服务**投机解码**这一 V3.1/V3.2 推理加速路线（V3 系 MTP 模块的学术同族）；但注意仓库的公开训练/评测目标是 Qwen3 与 Gemma4（V3 太大，未作为开源复现目标）；DSpark 作者团队与 V3 核心团队高度重合（Damai Dai、Wenfeng Liang 等）；
- **Engram（2026-01）**：全新架构方向，复用 V3 的 tokenizer（129,280）、MLA、DeepSeekMoE、loss-free 负载均衡与 YaRN 长_context 方案，是"下一代稀疏模型原语"的预研（mHC 超连接为新 appeared 组件）。

---

## 5. 对 work4ai 的输入（映射）

| 讲透单元 | 可直接引用的素材 |
|---|---|
| **讲透记忆** | Engram = "条件记忆作为第二稀疏轴"的完整案例：N-gram 哈希 KV 表、门控检索、"事实知识存在 Engram、上下文理解留在 attention"的二分实验（29% vs 93% 保留率）、LogitLens/CKA 机制分析——参数化记忆定位的教科书级证据链 |
| **讲透学习型Agent** | ESFT 的"激活统计→选专家→只训选中"= 学习型系统用运行时信号定位可塑子系统的范例；DeepSpec 的"草稿模型蒸馏目标分布"= 用大模型当环境训练小执行器 |
| **讲透KV Cache** | DeepSpec target cache（38 TB 换目标模型免重复前向）；投机解码验证时的 KV crop 语义（`crop(start)`）；Engram 100B 表 host 卸载 + 确定性预取 = 内存层级管理的工程极值 |
| **讲透上下文缓存** | target cache 的 manifest 设计（git_sha/dtype/层列表入 manifest）与"缓存层不能取最后一层"的隐状态语义陷阱（base_evaluator.py:100-112）是上下文缓存设计的实战细节 |
| **讲透微调** | ESFT 完整流水线（打分→选专家→to_buffer 冻结→adapter 发布）；to_buffer 冻结技巧（persistent=False buffer 让参数从 optimizer/state_dict 消失）值得作为"冻结的艺术"案例 |
| **讲透复用权重** | 三仓共用同一哲学：DeepSpec 草稿复用目标的 embed/lm_head（复制即冻结）；ESFT adapter 只存选中专家；Engram 一张表跨 4 个 mHC 分支共享 |
| **Agent记忆系统案例** | Engram 的"静态模式查表 + 动态推理计算"分工（gating 可视化：命名实体/习语处门控点亮）可类比 Agent 的"长期参数记忆 vs 工作记忆"架构分层 |

---

## 6. 三仓纵向综合：三条效率轴

**加速（投机解码）— 高效适配（专家微调）— 能力扩展（条件记忆）**，恰好覆盖 LLM 生命周期三个烧钱环节：

| 轴 | 仓库 | 稀疏性机制 | 冻结的大东西 | 关键数字 |
|---|---|---|---|---|
| 推理加速 | DeepSpec | 拒绝采样只"激活"被接受的草稿 token；置信调度提前止损 | 目标模型（38TB cache 只读） | block=7、L1 损失权重 0.9、ECE/AUROC/Brier 校准、9 基准 |
| 训练/适配 | ESFT | 激活统计选 ~7% 专家；路由器冻结保分布 | 底座全部其余参数（to_buffer） | 每层 4-6/64 专家、12 官方 adapter、lr 1e-5×500 步 |
| 参数扩展 | Engram | O(1) 确定性寻址（区别于 MoE 的动态路由）；门控稀疏融合 | 100B 表卸载主机 DRAM | ρ*≈75-80% U 型律、+13B 参数零 FLOPs 增量、MQ-NIAH +12.8 |

三条轴的共同元模式：**"大而冻结的静态结构 + 小而可训练的动态部件 + 明确的选择/寻址信号"**——DSpark 的选择信号是置信头、ESFT 是激活频次、Engram 是哈希地址；且三者都是算法-系统协同设计（confidence 阈值 ↔ 提案截断；专家并行 ↔ 手动 all_reduce；确定性地址 ↔ PCIe 预取）。对 work4ai 而言，这是"稀疏性作为第一性原理"（生物神经系统 Lennie 2003 → MoE → 条件记忆）这条叙事线的三块当代基石。

---

## 附：证据索引（关键文件速查）

- DeepSpec：`README.md`、`config/{dspark,dflash,eagle3}/*.py`、`deepspec/modeling/dspark/{common,loss,markov_head,qwen3/modeling}.py`、`deepspec/eval/{base_evaluator,dspark/{evaluator,confidence_head,draft_ops},eagle3/evaluator}.py`、`deepspec/trainer/base_trainer.py`、`scripts/data/{README.md,prepare_target_cache.py,generate_train_data.py}`、`requirements.txt`、`NOTICE`
- ESFT：`README.md`、`esft.py`、`train.py`、`train_ep.py`、`benchmarks.py`、`utils.py`、`configs/base.yaml`、`scripts/expert/{get_expert_scores,generate_expert_config}.py`、`scripts/download_adapters.sh`、`deepseek/modeling_deepseek.py`（MoEGate:421-525、DeepseekV2MoE:549-617）、`results/expert_configs/intent.json`
- Engram：`README.md`、`engram_demo_v1.py`（CompressedTokenizer:60、NgramHashMapping:188、MultiHeadEmbedding:305、Engram.forward:358）、`Engram_paper.pdf`（U 型律 §3.1、27B 配置 Table 1/5、长上下文 Table 2、CKA/LogitLens §6.1、消融 §6.2、卸载吞吐 Table 4、tokenizer 压缩附录 C）
