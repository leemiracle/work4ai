# DeepSeek 代码与数学证明系列深读笔记（Coder / Coder-V2 / Math / Math-V2 / Prover-V1.5 / Prover-V2）

> 研究型代码考古笔记，对象目录：`C:\workspace\work4ai\.tools\deepseek-repos\`。
> 诚实约束：全部数字来自实际读到的文件——各仓 README、仓库内 PDF 论文全文（pypdf 提取）、`prover/` 源码、`configs/`、`inference/` 代码；两篇未随仓附带 PDF 的论文（DeepSeek-Coder 2401.14196v2、DeepSeekMath 2402.03300v3）从 arXiv HTML 版补读，已在文中标注。未读到的部分明确标注，不编造。

---

## 0. 六仓总览

| 仓库 | 发布 | 一句话定位 | 模型规模 | 关键基准 |
|---|---|---|---|---|
| DeepSeek-Coder | 2023-11 | 从零训练的 dense 代码模型，repo-level 语料 + FIM + 16K | 1.3B/6.7B/33B（README 另列 1B/5.7B） | HumanEval-Python 33B-Base 56.1% |
| DeepSeek-Coder-V2 | 2024-06 | 从 DeepSeek-V2 中间检查点续训 6T token 的 MoE 代码模型，对齐闭源 | 16B/2.4B 激活，236B/21B 激活 | HumanEval 90.2%（vs GPT-4o 91.0%） |
| DeepSeek-Math | 2024-04 | 代码模型续训出的自然语言数学模型 + GRPO 的诞生地 | 7B | MATH 51.7%（RL，CoT） |
| DeepSeek-Math-V2 | 2025 | 自验证数学推理：学习型 verifier 当奖励模型，自然语言证明路线 | 基于 V3.2-Exp-Base | Putnam 2024 118/120 |
| DeepSeek-Prover-V1.5 | 2024-08 | Lean 4 证明模型：RLPAF + 截断/延续 MCTS（RMaxTS） | 7B | miniF2F-test 63.5%（RMaxTS） |
| DeepSeek-Prover-V2 | 2025-04 | 子目标分解 + 课程学习 + 671B 统一非形式/形式推理 | 7B / 671B | miniF2F-test 88.9%（pass@8192） |

---

## 1. DeepSeek-Coder（2023-11）

### 1.1 定位一句话
从零在 2T token 上训练的 dense 代码基座，首次把「repo 级依赖排序语料 + FIM 填空 + 16K 长上下文」三件事同时做进预训练。

### 1.2 核心机制（README + arXiv 2401.14196v2）

**数据构造（README §3 四步 + 论文 §2）**
- 配比：87% 源代码 / 10% 英文代码相关自然语言（GitHub Markdown + StackExchange）/ 3% 中文非代码语料；87 种语言、798GB、6.03 亿文件（论文 Table 1）。
- StarCoder 同款规则过滤（平均行长>100 字符、最大行长>1000、字母占比<25%、HTML 可见文本比、JSON/YAML 50–5000 字符等），过滤后仅剩原始量的 **32.8%**。
- **repo 级依赖解析**（论文 Algorithm 1 TopologicalSort）：正则抽取 `import`（Python）/`using`（C#）/`include`（C）调用关系建图，取**最小入度节点**的变体拓扑排序（可容忍环），保证被依赖文件排在前面；每个文件前加文件路径注释。
- **repo 级 minhash 去重**：以整个仓库拼接文本为去重单元（而非文件级），保住仓库结构完整性。
- 去污染：10-gram 精确匹配 HumanEval/MBPP/GSM8K/MATH（短于 10-gram 且 ≥3-gram 用全串匹配）。

**训练三段式（README §3）**
1. 1.8T token @ 4K 窗口；2. 追加 200B token @ 16K 窗口（→ Base）；3. 2B token 指令微调（→ Instruct）。
- 优化器 AdamW（β1=0.9, β2=0.95），三段学习率调度、2000 步 warmup、末段降至峰值 10%。
- 架构：RoPE + SwiGLU；33B 用 GQA（组大小 8）+ FlashAttention-2；BPE 词表 32K（HuggingFace tokenizer，非 SentencePiece——为此给 llama.cpp 提了 PR#4070）。
- **16K 长上下文**：RoPE 线性缩放因子 1→4、base 10000→100000，追加 1000 步（batch 512、序列长 16K）；理论可到 64K，可靠区间 16K。

**FIM（论文 §3.1.2，重点消融）**
- 论文描述两种模式：PSM（Prefix-Suffix-Middle）与 SPM（Suffix-Prefix-Middle）；三个哨兵 token `<｜fim▁begin｜>/<｜fim▁hole｜>/<｜fim▁end｜>`（README 代码插入示例即此格式）。注：任务口径中的"MPM"未在论文中作为独立模式出现，实际采用为 PSM。
- 1.3B Python 子集消融（HumanEval-FIM 单行填空）：0%/50%/100% PSM + 50% MSP 对比——100% FIM 率填空最好但**代码补全最差**，50% PSM 优于 50% MSP；最终选择 **FIM 率 0.5、PSM 模式、文档级（packing 前预处理）**。
- Instruct 模型保留补全能力的技巧：把 `eos_token_id` 从 32021（`<|EOT|>`）改回 32014（README §7 Q&A）。

**成绩（README §2/§6 + 论文）**
- 33B-Base 对 CodeLlama-34B 领先：HumanEval-Python +7.9 / HumanEval 多语 +9.3 / MBPP +10.8 / DS-1000 +5.9 个百分点；6.7B-Base ≈ CodeLlama-34B。
- 单行 FIM 均值：33B-Base 81.2%（vs CodeLlama-13B 75.5%）。
- Instruct-33B HumanEval 79.3% 超 GPT-3.5-Turbo（76.2%）；LeetCode 竞赛基准（自建：2023-07~2024-01 共 180 题、每题 100 测例）33B+CoT 28.9% vs GPT-4-Turbo+CoT 41.8%。

### 1.3 工程亮点
- `Evaluation/` 自带全量可复现评测：HumanEval（自扩 8 语言 MultiPL-E 数据）、MBPP、DS-1000、PAL-Math（带 python_executor 的程序辅助数学）、LeetCode（`vllm_inference.py` + `evaluate_leetcode.py`）。
- `finetune/finetune_deepseekcoder.py`：DeepSpeed ZeRO-3 + bf16 + gradient checkpointing 的官方微调路径。
- README 明示量化生态适配（llama.cpp/exllamav2，exllamav2 需设 RoPE scaling=4）。

### 1.4 演进关系
- 上游：继承 DeepSeek-LLM 训练配方与 scaling law。下游：①Coder-V2 用 V2 MoE 架构续写；②**DeepSeek-Coder-7B-v1.5 是 DeepSeekMath 的初始化模型**（代码→数学的迁移起点）；③LeetCode 基准成为后续 Coder 系标准评测。

### 1.5 work4ai 输入
- **讲透代码生成**：FIM 三哨兵 token 与 0.5-PSM 消融是「填空能力 vs 补全能力权衡」的最佳实证案例；repo 级拓扑排序是"上下文工程进语料"的祖型。
- **讲透符号主义/神经符号**：依赖图排序 = 把符号结构（import 图）注入序列训练的早期样本。
- **用例库**：仓库卡——"从零训练代码基座的数据工程全景"（798GB→32.8% 过滤留存率的漏斗数字可直接引用）。

---

## 2. DeepSeek-Coder-V2（2024-06）

### 2.1 定位一句话
从 DeepSeek-V2 中间检查点（已训 4.2T）续训 6T 代码/数学 token 的 MoE 代码模型，首次让开源代码模型全面追平 GPT4-Turbo/Claude 3 Opus/Gemini 1.5 Pro。

### 2.2 核心机制（README + 仓内 paper.pdf）

**续训设定（论文 §3.3）**
- 语料配比 60% 源代码 / 10% 数学 / 30% 自然语言（NL 直接取自 DeepSeek-V2 训练集）。
- **新增代码语料共 1,170B token**：GitHub 规则过滤+近重去除后 821B 代码（**338 种语言**，86→338）+ 185B 代码相关文本；Common Crawl 走 DeepSeekMath 同款 fastText 迭代管线 3 轮得 70B 代码网页 + **221B 数学网页 token**；GitHub 种子再 2 轮迭代得 94B 源码。
- 1B 消融证明新语料质量：HumanEval 30.5%→36.0%（1T）→37.2%（2T），MBPP 44.6%→49.0%→54.0%。
- 总预训练 token：4.2T + 6T = **10.2T**；AdamW、cosine、2000 warmup、尾段 10% 峰值。

**MoE 配置（论文 §3.2 + README §2）**
- 架构完全对齐 DeepSeek-V2（MLA + DeepSeekMoE）：Lite 16B/激活 2.4B（对应 V2-Lite），236B/激活 21B（对应 V2）。
- 工程教训：训练中遇到指数归一化（exponential normalization）不稳定/梯度尖峰，**回退到常规归一化**。

**FIM 与长上下文（论文 §3.1/§3.4）**
- FIM 仅 16B（Lite）启用：PSM 模式、率 0.5、文档级 packing 前；**236B 关闭 FIM**（只用 next-token prediction）。
- 16K→128K 用 **YaRN**：scale s=40、α=1、β=32（同 V2 超参）；两阶段续训：32K 序列 × batch 1152 × 1000 步 → 128K × batch 288 × 1000 步；NIAH 全窗格通过。

**成绩（README 表）**
- 生成：HumanEval 90.2（GPT-4o 91.0）、MBPP+ 76.2、LiveCodeBench 43.4、USACO 12.1（全面超 CodeStral/Llama3-70B，超 GPT4-Turbo-1106）。
- 补全：Lite-Base 16B HumanEval-FIM 86.4 = 33B dense 持平；RepoBench-Python 38.9（CodeStral 46.1 仍领先——MoE 小模型补全未超专用 dense）。
- 修复：Aider 73.7 超 GPT-4o（72.9）、SWE-Bench 12.7；数学：MATH 75.7（GPT-4o 76.6）、AIME2024 4/30、Math Odyssey 53.7。
- 通用不掉队：MMLU 79.2、BBH 83.9 均与 V2 Chat 相当或更高。

### 2.3 工程亮点
- 部署推荐 **SGLang**（MLA 优化 + FP8 W8A8 + FP8 KV Cache + torch.compile，开源最低延迟），vLLM 需并 PR#4650。
- Chat template 踩坑实录（README §6）：末轮 `Assistant:` 冒号后**不能有空格**，否则 16B-Lite 出中文回复/乱码/复读——旧版 Ollama bug 的根因记录。
- `supported_langs.txt` 逐语言清单随仓发布。

### 2.4 演进关系
- dense→MoE：Coder 33B dense → Coder-V2 236B/21B 激活；语料管线直接复用 **DeepSeekMath 的 fastText 迭代法**（数学线的资产反哺代码线）；FIM 策略从「PSM+SPM 可选」收敛为「仅 PSM 0.5、仅小模型」。

### 2.5 work4ai 输入
- **讲透代码生成**：MoE 代码模型的「生成强、补全不占优」现象（RepoBench 落后 CodeStral）是模型能力结构分析的好素材；128K 代码上下文的 YaRN 两阶段扩展配方可直接引用。
- **讲透RL/讲透数学建模**：其数学能力来自 221B 数学网页 token 的注入——「代码模型吃数学语料」跨线迁移证据。
- **用例库**：仓库卡——"continual pre-training 范式：通用底座 + 领域 6T"（10.2T 总量、60/10/30 配比）。

---

## 3. DeepSeek-Math（2024-04）

### 3.1 定位一句话
以 DeepSeek-Coder-7B-v1.5 为底座续训的自然语言数学模型，凭 120B 自建数学语料 + 首创 GRPO，把 7B 推到 MATH 51.7%，也是整个 DeepSeek RL 方法论的源头。

### 3.2 核心机制（README + arXiv 2402.03300v3）

**数据管线（README §3 + 论文 §2.1）**
- 迭代 fastText 分类器法：OpenWebMath 做种子（50 万正例 + 50 万 CC 负例；向量 256 维、lr 0.1、3-gram、3 epoch），从去重后 40B 网页中召回数学页 → 按 fastText 分数排序保留 top（首轮 40B token）→ 域名收集率 >10% 判定数学域 → 人工标注 URL → 未收集网页入种子 → 重训分类器。**4 轮迭代**后得 **35.5M 网页 / 120B token**（第 4 轮发现 98% 数据已被第 3 轮收集，停止）。
- 语料横向对照（1.3B 模型各训 150B token）：DeepSeekMath 语料 GSM8K 23.8% / MATH 13.6%，碾压 Proof-Pile-2（14.3/11.2）、OpenWebMath（11.5/8.9）、MathPile（2.7/3.3）；规模≈Minerva 数学网页的 7 倍、OpenWebMath 的 9 倍。去污染同 10-gram 法。
- **两个反直觉发现**：①arXiv 论文语料对所有数学基准无可见增益；②**代码训练提升数学推理**（400B code→150B math 两阶段，优于 400B general→150B math，工具/无工具双 setting 均如此）。

**预训练（论文 §2.3）**
- 初始化自 DeepSeek-Coder-Base-v1.5 7B（lr 衰减前检查点），训 500B token：**56% DeepSeekMath 语料 + 4% AlgebraicStack + 10% arXiv + 20% GitHub 代码 + 10% CC 中英文**；lr 4.2e-4、batch 10M。
- Base 7B 成绩：GSM8K 64.2 / MATH 36.2（few-shot CoT，超 Minerva 540B 的 58.8/33.6）；工具：GSM8K+Python 66.9 / MATH+Python 31.4；**Isabelle informal-to-formal（Sledgehammer 补细节）miniF2F-valid 25.8 / test 24.6**——Coder 底座直接做形式化的最初证据；MMLU 54.9 / BBH 59.5（数学训练反哺通用推理）。

**SFT（论文 §3）**
- 776K 样本：英文（GSM8K/MATH 工具标注解 + MathInstruct 子集 + Lila-OOD）+ 中文 K-12（76 子话题），CoT/PoT/工具整合三格式；500 步、batch 256、常数 lr 5e-5、4K 拼接。
- Instruct：GSM8K 82.9 / MATH 46.8；MATH+工具 57.4。

**GRPO（论文 §4——本仓最大遗产）**
- PPO 需要等规模 value model；GRPO **去掉 critic**：对每个问题从旧策略采一组 G=64 个输出，用组内奖励做基线，优势 Â_i,t = (r_i − mean(r_group)) / std(r_group)（组相对优势）。
- 目标函数 = PPO 式 clip 项 + **KL 惩罚直接进 loss**（无偏估计 k3：π_ref/π_θ − log(π_ref/π_θ) − 1，逐 token）。
- 超参：策略 lr **1e-6**、KL 系数 **0.04**、每题采样 **64** 个输出、max length 1024、batch 1024 题、**每个探索阶段只更新一次策略**；RL 数据仅 GSM8K+MATH 的 CoT 格式 ~**144K** 题；奖励模型从 DeepSeekMath-Base 7B 初始化（lr 2e-5）。
- 增益：GSM8K 82.9→**88.2**、MATH 46.8→**51.7**（7B 上 MATH +4.9pt 的 RL 增益），且域外同涨（MGSM-zh 73.2→79.6、CMATH 84.6→88.8）；工具式 MATH 58.8（README 表述"接近 60%"）。64 样本 self-consistency 达 60.9%。
- 论文还给出 RFT/DPO/PPO/GRPO 的统一范式（直接/简化 RL）、outcome vs process supervision、单轮 vs 迭代 RL 的系统实验。

### 3.3 工程亮点
- `evaluation/`：`submit_eval_jobs.py` 多卡分片提交 + `summarize_results.py` 汇总成 `evaluation_results.json`；`--eval-atp` 选项调 `unsafe_score_minif2f_isabelle.py`（PISA server）评 Isabelle 形式化——自然语言数学仓里内置形式化评测钩子。
- 提示词规范写进 README 与 `run_subset_parallel.py::markup_question()`：英文 `...put your final answer within \boxed{}` / 中文对应句式。

### 3.4 演进关系
- 上游吃 Coder-v1.5，下游分两支：①GRPO → R1（推理 RL）→ Prover 系 RLPAF → Math-V2 迭代 GRPO；②数学语料管线 → Coder-V2 的 221B 数学 token；③Base 的 Isabelle few-shot 能力 → Prover 系（形式化主线）。

### 3.5 work4ai 输入
- **讲透RL**：GRPO 的「组内相对优势、无 critic、KL 进 loss」是一手原始出处（含 64/1e-6/0.04 全套超参），可作为 GRPO 条目的主证据源。
- **讲透数学建模**：fastText 四轮迭代语料工程 + 「arXiv 无用 / 代码有用」两条反直觉结论。
- **讲透神经符号**：代码预训练→数学推理迁移的因果实验（400B code→150B math 对照组）。
- **用例库**：仓库卡——"领域语料迭代挖掘管线"（种子→分类器→域标注→再入种子）。

---

## 4. DeepSeek-Prover-V1.5（2024-08）

### 4.1 定位一句话
Lean 4 证明模型三件套（预训练→RLPAF→RMaxTS），核心创新是把「整证明生成」与「步级搜索」用 truncate-and-resume 统一，并用 RMax 内在奖励解决证明搜索的稀疏奖励。

### 4.2 核心机制（README + 仓内 paper.pdf + 源码）

**训练三级（论文 §2）**
- **预训练**：DeepSeekMath-Base 续训，聚焦 Lean/Isabelle/Metamath 形式语言 + 代码 + 自然语言数学 → V1.5-Base。
- **SFT**（→ V1.5-SFT）：语料来自 Mathlib4 + Prover-V1 合成定理 + Lean Workbook + miniF2F/ProofNet valid，专家迭代扩产；两招数据增强——①**DeepSeek-Coder-V2-236B 给证明注释自然语言 CoT**（证明块开头整段思路 + 每 tactic 前分步说明）；②**插入 tactic state 注释** `/- tactic state: ... -/`（Lean REPL + LeanDojo 工具抽取每个 tactic 的前后状态三元组），训练时只对 `/- tactic state: ` 之后的 token 算 loss（预测状态为辅助任务、续写证明为主任务）。数据集 9,645k 序列；9B token、batch 2048、常数 lr 1e-4、100 步 warmup、4K 拼接。
- **RLPAF**（→ V1.5-RL）：GRPO + Lean 验证器二元奖励（对=1/错=0）；提示筛选为「SFT 模型多次尝试有中等成功率」的 ~**4.5k** 条定理（保证组内既有对又有错，契合组相对优势）；每定理 CoT+非CoT 双提示；lr 5e-6、KL 系数 **0.02**、组大小 **32**、max len 2048、batch 512。

**RMaxTS：truncate-and-resume MCTS（论文 §3 + `prover/algorithms/rmax_tree_search.py`）**
- **树抽象**：树节点 = tactic state，边 = 一次 tactic 状态转移；整证明生成后提交 Lean，**在最早错误处截断**、后续代码丢弃，成功前缀按 tactic 切成节点链并入树（`Proof.segmentation()`，`prover/lean/proof.py:60`——用 sorries/errors 位置定截断点、跳过 "unsolved goals" 类报错、行内剥注释找 tactic 边界）。
- **Resume**：同一 tactic state 可由多种 tactic 代码到达，节点存**等价代码集合**，扩展时随机取一个做前缀（`TreeNode.update_code`/`code` 属性，`rmax_tree_search.py:37-45`）；前缀末尾附 tactic state 注释再续写——模型在 SFT 阶段就学过这个格式。
- **选择**：virtual node 技巧（当前节点可当自己的"子节点"被反复扩展）+ Hoeffding 型 UCB：`sqrt(2·ln N / n)`（`_select_node`，`rmax_tree_search.py:214-226`）。
- **内在奖励（RMax）**：R = 1[本次扩展给树加了新节点]（`_rmax_exploration_summarize_results`，:256）——纯好奇心驱动探索，针对「只有完整证明才有外在奖励」的稀疏性；对非平稳性用 **DUCB**（折扣 UCB，γ=0.99，`update_reward`/`_update_value` 的 γ^num_running_jobs 折扣机制）。
- **配置**（`configs/RMaxTS.py`）：sample_num **6400**/题、并发 32、ckpt_interval 128、data_repeat=16（即 miniF2F-test 每题 16×6400）、256 个搜索进程、生成 temp 1.0/top_p 0.95/max_tokens 2048、batch 512；Lean 验证：64 并发、内存限 10GB、超时 300s。

**验证器基础设施（`prover/lean/verifier.py`）**
- `Lean4ServerProcess`：每进程 `lake exe repl`（mathlib4 工作区内），`RLIMIT_AS` 限内存 10GB，超时 300s；线程创建失败/bad_alloc 自动重试；后台 monitor 每秒 `killall repl --older-than=310s` 清僵尸。`verify_lean4_file()` 返回 sorries/tactics/errors/warnings/infos + `pass`（无 error）与 `complete`（无 error、无 sorry、无 "declaration uses 'sorry'"）双判定。

**成绩（README §2 表 + 论文）**
- miniF2F-test：Base(3-shot) 29.7% → SFT(CoT) 50.4%（pass@128）/57.4%（16×6400）→ RL 单遍 60.2% → **RL+RMaxTS 63.5%**；ProofNet 25.3%。超 InternLM2-StepProver（54.5/18.1）、HTPS（41.0）、GPT-f（36.6）。
- 消融：CoT 优于非 CoT（RL 阶段 51.6 vs 50.5）；预算曲线随 sample budget 稳定不降。

### 4.3 工程亮点
- `prover/launch.py` + `summarize.py`：一条命令跑论文实验、一条命令汇总；`ConcurrentJob` 流水线抽象（generate→verify→update 三阶段协程式推进，`prover/utils.py:78`）。
- 断点续跑：树结构 pickle checkpoint（含 backup 双保险），且**存档后若有已完成证明立即停**——注释明言防「中断-重启循环导致高估」（`rmax_tree_search.py:309-312`，pass@k 评测方法论细节）。
- 生成端 vLLM（`max_num_batched_tokens=8192`），验证端 64 进程 Lean REPL——**LLM 服务与证明助手服务的双调度器架构**（`ProcessScheduler`，`prover/workers/scheduler.py`）。
- `quick_start.py`：生成→正则抽取→提交验证的最小闭环（含期望输出示例，教学价值高）。

### 4.4 演进关系
- 直接继承：底座 DeepSeekMath-Base、RL 算法 GRPO（超参从 64/0.04 改 32/0.02——二元稀疏奖励下的调整）；CoT 注释靠 Coder-V2-236B（代码线资产反哺形式化线）。
- 对下游：RMaxTS 的「验证器反馈截断续写」思想 → Prover-V2 的子目标分解是它的层级化升级；tactic state 注释训练 → V2 的 CoT/non-CoT 双模式。

### 4.5 work4ai 输入
- **讲透Lean4数学**：一手素材——tactic state 注释格式、`/- tactic state: -/`、`sorry` 解析、Lean REPL 验证协议（sorries/errors/complete 三态判定）。
- **讲透形式化验证**：形式验证器当「免费奖励模型」的完整工程实现（内存/超时/重试/僵尸清理）。
- **讲透RL**：RMax 内在奖励 + DUCB 处理稀疏奖励搜索，是 RL 教材级案例；GRPO 在二元奖励下的适配。
- **用例库**：仓库卡——"LLM×形式化验证器的生产级 harness"（双调度器 + 断点续跑 + 防高估停机）。

---

## 5. DeepSeek-Prover-V2（2025-04）

### 5.1 定位一句话
用 DeepSeek-V3 做「引理分解 + 形式化」、7B 小模型做子目标证明搜索的递归管线，把非形式推理与形式证明统一进一个模型（671B CoT 模式 miniF2F-test 88.9%）。

### 5.2 核心机制（README + 仓内 DeepSeek_Prover_V2.pdf）

**递归证明搜索（论文 §2.1）**
- 提示 **DeepSeek-V3**（注：论文原文为 V3，非 V3.1；表内非形式基线为 DeepSeek-V3-0324）先自然语言分析、再分解出 Lean 4 `have ... := by sorry` 证明骨架（高层 sketch，细节留 sorry）。
- 子目标转引理两种形态：**(a) 替换原目标** / **(b) 前置子目标作前提**（论文 Figure 3）；(b) 用于递归解复杂题，(a)(b) 都进课程学习。
- **7B prover 逐子目标搜索**（省算力），全部解出后自动拼装成原题完整证明。
- **冷启动数据**：挑「7B 端到端解不出、但分解后子目标全解出」的难题，拼装证明接在 V3 的 CoT 之后——数百条高质量"非形式思路+形式证明"合成数据（与 Kimina-Prover 的反向工作流对照：V2 是形式化前向合成，Kimina 是回溯合成思路块）。

**课程学习（论文 §2.1 末）**
- 用子目标定理（a/b 两型）扩充形式题目集，注入专家迭代（expert iteration：当前最优策略解旧题→Lean 验证→成功样本回填 SFT→再训→再解更难题），形成难度递进课程；miniF2F-valid 亦入课程；原理同 AlphaProof 的 test-time RL（生成目标题的变体）。

**两阶段训练（论文 §2.3）**
- 阶段一：课程学习 + 专家迭代训 **非CoT** 模式（推理/验证快，加速数据收集）；语料增补 autoformalization 与开源数据（Lean Workbook、STP、Lin et al.）。
- 阶段二：V3 CoT 冷启动数据 SFT 出 **CoT** 模式 → RL。671B 在 DeepSeek-V3-Base 上 SFT（常数 lr 5e-6、ctx 16384）；**RL 用 GRPO**：二元奖励为主 + 训练早期加**一致性奖励**（惩罚证明结构与 CoT 中 have 分解错位，强制包含全部分解引理）；每次迭代 256 题、每题 32 候选、max len 32768。
- **7B 蒸馏线**：Prover-V1.5-Base 上下文 4096→**32768** 扩展，用 671B RL 阶段的 rollout 数据微调，再走同款 RL。

**成绩（论文 §3 + README）**
- miniF2F-test（671B CoT）：pass@1 61.9% / pass@32 **82.4%** / pass@1024 86.6% / pass@8192 **88.9%**；7B CoT：58.6/75.6/79.9/82.0。非CoT 671B：59.5/73.8/76.7/78.3。
- ProofNet-test 37.1%（pass@1024）；PutnamBench **47/658**（论文两处 47；README 写 49——以论文为准并注记差异）。
- miniF2F-valid 219(+2)/244 = 90.6%；其中**课程学习（V3 分解 + 7B 搜索）单独达 89.8%**——接近 671B 端到端；AIME 类 test 14/15=93.3%。
- CoT vs 非CoT 平均输出 token（miniF2F-test）：7B 4488.5 vs 442.6；671B 6751.9 vs 761.8；671B 非 CoT 会自发插短注释=隐式推理。
- **ProverBench**：325 题（15 道 AIME 24&25 形式化 + 310 道教材/教程题：数论 40、初等代数 30、线性代数 50、抽象代数 40、微积分 90、实分析 30、复分析 10、泛函分析 10、概率 10）；671B 解出 6/15 AIME。miniF2F 全解打包 `minif2f-solutions.zip` 随仓发布。
- 环境固定 Lean **4.9.0-rc2**（与 V1.5 同测试环境）。

### 5.3 工程亮点
- 「大模型出骨架、小模型填细节」的异构协作管线——算力分配的结构化答案。
- 一致性奖励：把「输出结构对齐中间规划」显式编码进 RL 奖励，可迁移到任何"规划-执行"双阶段系统。
- 基准即数据集：ProverBench 连同 HF dataset 发布，AIME 真题形式化填补竞赛级评测空白。

### 5.4 演进关系
- 上承 V1.5（底座、双模式提示、专家迭代、GRPO、Lean 环境），升级点：V1.5 的树搜索是**运行时**在 tactic 层分解，V2 把分解**前移到数据与训练**（V3 骨架 + 课程），推理时反而可纯采样（pass@8192 即可 88.9%，非必须树搜索）。
- 与 Math-V2 互补：V2=形式（Lean，机器可验证奖励），Math-V2=非形式（自然语言，学习型 verifier 奖励）——同作者团队（Zhihong Shao 等）的两条平行路线。

### 5.5 work4ai 输入
- **讲透Lean4数学/讲透形式化验证**：`have sorry` 骨架分解是"AI 数学家工作流"的具体化；课程学习造题（子目标变体）+ AlphaProof 式 test-time RL。
- **讲透神经符号**：非形式 CoT（神经网络）与形式证明（符号系统）在训练目标里被一致性奖励焊在一起——神经符号混合的当前最佳实践之一。
- **讲透RL**：GRPO 第三次迭代（64/0.04 → 32/0.02 → 32 候选/32768 ctx + 一致性奖励），奖励工程随任务语义演化。
- **用例库**：仓库卡——"大模型规划+小模型执行的递归证明管线"。

---

## 6. DeepSeek-Math-V2（2025）

### 6.1 定位一句话
"Towards Self-Verifiable Mathematical Reasoning"：放弃"最终答案对=对"，训练 LLM verifier 按 0/0.5/1 评分自然语言证明并充当奖励模型，生成器学会先自检再交卷，以 scaled test-time compute 拿下 IMO 2025 金牌级与 Putnam 118/120。

### 6.2 核心机制（README + 仓内 DeepSeekMath_V2.pdf + inference/ 源码）

**动机（README §1）**
- 答案 RL 已饱和 AIME/HMMT，但"答案对≠推理对"；定理证明无数值答案，最终答案奖励不可用；开问题没有已知解，必须自验证。

**架构与定位**
- 基于 **DeepSeek-V3.2-Exp-Base**（V3.2 系，DSA 稀疏注意力时代的底座；推理支持指向 DeepSeek-V3.2-Exp 仓）。**不是 Lean 模型**——与 Prover 系互补：Prover=形式证明（机器可验证），Math-V2=自然语言证明（学习型验证）。Apache 2.0 许可。

**Verifier 训练（论文 §2.1）**
- 评分 rubrics：完全正确=1 / 大体正确有细节缺失或小错=0.5 / 未解决或有致命错=0；引用论文结论不豁免证明。
- RL 双奖励：format reward（强制输出"评价+boxed 分数"格式）+ score reward（预测分与专家分接近度）。
- **Meta-verifier**：专训一个模型审查 verifier 的分析（缺陷复述/缺陷分析/表述分析/评分分析四维），其质量分入 verifier 奖励——verifier 分析质量 0.85→**0.96**（验证集，准确率不降）。

**Generator 训练（论文 §2.2）**
- verifier 作为**生成式奖励模型**；generator 被要求输出「证明 Y + 自评 Z（与 verifier 同 rubrics 同格式）」。
- 奖励 `R = R_format(Y,Z) · (α·R_Y + β·R_Z)`，**α=0.76、β=0.24**；R_Z = 自评分准确度 × meta 分。激励设计：诚实认错 > 谎报正确；最高奖励=证明对且自评准；最优策略=交卷前尽量自查自改。
- 关键观察：同一模型一次性"生成+自评"会给自己放水，必须用外部 verifier 监督自评的忠实度。

**生成-验证协同飞轮（论文 §2.3）**
- 生成器变强→产出 verifier 单次验不出的难题→**扩展验证算力自动标注**：每证明 n 份独立验证分析→报告问题者(0/0.5 分)再 m 份 meta 验证、多数确认才算有效→取有效最低分≥k 份则标该分；全验不出问题=1；否则弃或转人工。**最后两轮迭代完全替代人工标注**。

**迭代 GRPO（论文 §3.1）**
- 每轮先优化 verifier，generator 从 verifier 检查点初始化再优化；第 2 轮起 verifier 用上一轮"验证+生成"合并检查点（rejection fine-tuning 整合）初始化。

**评测与 test-time compute（论文 §3.3）**
- 一次性生成：每题 8 样本、8 份验证分析多数投票评分；CNML 级 91 题分类均值全面超 GPT-5-Thinking-High 与 Gemini 2.5-Pro。
- 序列精炼（ISL 2024，128K token 上限，32 线程）：最大迭代 1→8，Pass@1 0.15→0.27、Best@32 0.26→0.42——自选最优显著高于线程均值=自评可靠。
- **High-Compute Search**：候选池 64 证明 × 64 验证分析；每轮按均分选 top64 证明、各配 8 份分析（优先报问题的 0/0.5 分析）生成精炼版回填池；至多 16 轮或**通过全部 64 次验证**为止；全程单模型（生成+验证一体）。
- 结果：IMO 2025 解出 5/6（83.3%，金牌线）；CMO 2024 4 题全解+1 部分分（73.8%，金牌）；**Putnam 2024 11/12 全解+1 小错 = 118/120**（人类最高 90）；IMO-ProofBench Basic 99.0（超 DeepThink IMO-Gold 的 89.0）/ Advanced 61.9（略低于 65.7）。

**提示词工程（`inference/math_templates.py`，四模板全量在仓）**
- `proof_verification`：评委模板（含"引用文献不豁免证明"硬规则）。
- `meta_verification`：审查评估的评估——"只审缺陷是否成立，不管它判对的部分"（职责裁剪的精巧设计）。
- `proof_generation`：把评委 rubrics 原文嵌进生成提示（**让模型显式知道自己的奖励函数**），含名句 "You CAN'T cheat! If you cheat, we will know, and you will be penalized!"。
- `proof_refinement`：候选证明+评估配对精炼模板。

### 6.3 工程亮点
- `inference/generate.py`：asyncio + 多进程 API 并发；**`.meta` 侧车文件记录已完成批次，改参数即断言报错、原参数可断点续跑**——大规模采样任务的生产级细节；`reasoning_content` 与 `content` 拼接 `<think>` 格式。
- `inputs/`（IMO2025/CMO2024/CMO2025/Putnam2024 原题）+ `outputs/`（各基准模型输出 jsonl）全公开，评测可复现。
- 诚实的失败报告：论文明言最难的 IMO 级问题仍未解出，但"未全解的问题里生成器通常真找到了真缺陷；全解的问题通过全部 64 次验证"。

### 6.4 演进关系
- 承 Math 一脉（GRPO 迭代化、V3 系底座）与 Prover 一脉的思想（验证器当奖励模型=RLPAF 的自然语言版；meta-verification ≈ 形式系统的分层验证）；generation-verification gap 的显式维护 = 对「verifier 恒弱于 generator」传统假设的工程反制。

### 6.5 work4ai 输入
- **讲透RL**：生成式奖励模型 + 惩罚不忠实自评的复合奖励（0.76/0.24 配比）；「让被训模型知道自己的评分标准」是奖励透明化的新颖做法。
- **讲透数学建模**：0/0.5/1 rubrics 把证明质量量化成可优化信号；多数投票+分层验证的自动标注管线。
- **讲透符号主义/讲透形式化验证**：与 Lean 路线对照——当符号验证器不可用时，能否用学习型 verifier 逼近其可靠性？本文是"软验证"路线的旗舰证据。
- **用例库**：仓库卡——"verifier-as-reward-model 与自动标注飞轮"（含四模板提示词原文，可直接入卡片）。

---

## 7. 六仓纵向综合：代码智能与数学智能的双螺旋

### 7.1 两条主线，三次方法复用

**代码线**：Coder(2023-11, dense 33B, FIM+repo 语料) → Coder-V2(2024-06, MoE 236B/21B, 338 语言, 128K)。
**数学线**：Math(2024-04, 自然语言+GRPO) → Prover-V1.5(2024-08, Lean+RLPAF+RMaxTS) → Prover-V2(2025-04, 子目标课程+671B) ‖ Math-V2(2025, 自然语言+学习型 verifier)。

两条线不是接力而是**双螺旋互绕**，三个"方法元"在两线间反复复用：

1. **RL（GRPO 及其变体）**：诞生于 Math（64 样本/组、KL 0.04）→ 改造成 RLPAF（32 样本、KL 0.02、二元证明奖励）→ Prover-V2 加一致性奖励（32 候选、32K ctx）→ Math-V2 迭代 GRPO（verifier 与 generator 轮转初始化）。奖励信号源的三次升级：答案匹配 → 机器验证器（Lean） → 学习型 verifier（生成式奖励模型）。
2. **搜索/test-time compute**：Coder 时代无搜索（FIM 即能力）→ Prover-V1.5 的 RMaxTS（6400 预算、内在奖励探索）→ Prover-V2 的 pass@8192 纯采样（搜索能力被训练吸收——"运行时搜索→训练时课程"的迁移）→ Math-V2 的池化精炼搜索（64×64×16 轮）。共同规律：**验证算力与生成算力必须同步扩展**（Math-V2 的自动标注、Prover-V2 的 7B 子目标搜索都在扩大"可判定"的边界）。
3. **合成数据**：Coder 的 repo 拼接 → Math 的 fastText 四轮迭代 → V1.5 的专家迭代 + Coder-V2-236B 注释 CoT → Prover-V2 的 V3 骨架 + 子目标变体课程（AlphaProof 式）→ Math-V2 的 verifier 自动标注。合成方向从"造语料"进化为"造课程、造奖励、造标注者"。

### 7.2 双螺旋的四个交汇点

- **代码→数学**（2024-02 前后）：DeepSeekMath 用 Coder-v1.5 当底座 + 「400B code→150B math 优于 general→math」的因果实验；代码训练提升无工具与有工具数学推理。
- **数学→代码**（2024-06）：Coder-V2 直接搬 Math 的 fastText 管线收 221B 数学 token，数学能力（MATH 75.7）成为代码模型卖点之一。
- **代码→形式化**（2024-08）：Coder-V2-236B 给 Lean 证明写 CoT 注释——代码大模型成为形式化线的"教师"。
- **形式化→非形式化**（2025）：Prover 系的"验证器当奖励"思想被 Math-V2 平移到自然语言域（Lean REPL → meta-verifier），把「可验证性」从符号系统外推到学习系统。

### 7.3 贯穿六仓的工程常数

- **验证即基础**：从 test case 执行（Coder 的 100 测例/题）、Lean REPL 三态判定（V1.5 `pass`/`complete`）、到 64 次验证全过（Math-V2）——每条线都有一个"不可协商的裁判"，且裁判的基础设施（内存限制、超时、重试、防高估停机）与模型本身同等重要。
- **vLLM/推理框架优先**：六仓推理/搜索全部落在 vLLM（Coder/Prover 系）或 SGLang（Coder-V2 推荐）；Prover-V1.5 的双调度器（生成 GPU 池 + CPU 验证进程池）是 LLM×外部工具系统的参考架构。
- **评测资产化**：LeetCode Contest 基准（Coder）、ProverBench（Prover-V2）、inputs/outputs 全公开（Math-V2）、miniF2F 修订版——每个仓都留下可复用的公共品。
- **数据配比的精确记账**：87/10/3（Coder）、60/10/30（Coder-V2）、56/4/10/20/10（Math）——领域模型时代"配方透明"的典范。

### 7.4 给 work4ai 的映射总表

| 讲透单元 | 主要供给仓 | 核心素材 |
|---|---|---|
| 讲透代码生成 | Coder, Coder-V2 | FIM 0.5-PSM 消融、repo 拓扑排序、MoE 生成/补全能力分化、YaRN 两阶段 |
| 讲透Lean4数学 | Prover-V1.5, Prover-V2 | tactic state 注释、`have sorry` 骨架、Lean REPL 协议、miniF2F 数字链 50.0→63.5→88.9 |
| 讲透形式化验证 | Prover-V1.5, Math-V2 | 验证器基础设施、二元奖励、自动形式化、软硬两条验证路线对照 |
| 讲透RL | Math（+全线） | GRPO 原始公式与超参、RLPAF、一致性奖励、迭代 GRPO、生成式奖励模型 |
| 讲透数学建模 | Math, Math-V2 | fastText 四轮管线、0/0.5/1 rubrics、自动标注飞轮 |
| 讲透符号主义 | Prover 系 | tactic 状态空间、树搜索抽象、形式系统当裁判 |
| 讲透神经符号 | Prover-V2, Coder | 非形式 CoT×形式证明的一致性焊接、依赖图注入语料 |
| 用例库 | 六仓各一卡 | 数据工程、双调度器 harness、递归证明管线、verifier 飞轮、continual pre-training、领域语料挖掘 |

---

## 附：证据源清单

- 仓内 README：六仓各自 `README.md`（均已全文读）。
- 仓内 PDF（pypdf 全文提取后逐段读）：`DeepSeek-Coder-V2/paper.pdf`、`DeepSeek-Prover-V1.5/paper.pdf`、`DeepSeek-Prover-V2/DeepSeek_Prover_V2.pdf`、`DeepSeek-Math-V2/DeepSeekMath_V2.pdf`。
- arXiv HTML 补读（仓内无 PDF）：DeepSeek-Coder `arXiv:2401.14196v2`、DeepSeekMath `arXiv:2402.03300v3`。
- 源码：`prover/algorithms/rmax_tree_search.py`、`prover/lean/{proof,verifier}.py`、`prover/utils.py`、`prover/workers/{scheduler,generator}.py`、`configs/RMaxTS.py`、`quick_start.py`（Prover-V1.5）；`inference/{generate.py,math_templates.py}`、`inputs/`、`outputs/`（Math-V2）；`Evaluation/`、`finetune/`（Coder）；`evaluation/`（Math）。
- 未读/无法读：各仓 HF 模型权重与 tokenizer 配置（未下载）；Prover-V2 论文附录 D 的 miniF2F 修订细节（仅见正文引用）；Prover-V1.5 的 `mathlib4/` 子模块（git submodule，未检出）。
