# kvpress onboarding（讲透 NVIDIA/kvpress @ 327ed6f，v0.5.5）

> 图谱：440 节点 / 922 边 / 14 层 / 16 步导览，fingerprints 155 文件基线。
> 本文全部行号锚基于 `327ed6f3` 实测核实；论文引用 arXiv 2510.00636（CITATION.cff:14）。

## 1. 一句话定位

kvpress 是 NVIDIA 开源的 **KV 缓存压缩策略集合库**：把几十种压缩方法统一成 `press` 对象（47 个 Press 类，`kvpress/__init__.py` 的 __all__ 共 48 项=47 press+1 pipeline），注册为 transformers pipeline 后一行代码换策略——`pipeline(context=..., question=..., press=SnapKVPress(compression_ratio=0.5))`（用法示例在 `kvpress/pipeline.py:35-37`）。它既是研究复现床（每条策略对应一篇论文），也是可评测产品（EvaluationRunner+HF leaderboard）。核心抽象只有三层基类：BasePress（`kvpress/presses/base_press.py:44`）、ScorerPress（`kvpress/presses/scorer_press.py:18`）、DecodingPress（`kvpress/presses/decoding_press.py:23`）——理解这三层，47 个策略就只剩参数差异。

## 2. 全景：14 层地图与五家族

工程壳三层（LL01-LL02）：pyproject（`pyproject.toml:3` 版本 0.5.5、`:11` 要求 Python≥3.10）、Makefile 开发任务集、CI 工作流与社区模板——`.github/ISSUE_TEMPLATE/new-press-request.md` 的"新 press 提名"模板体现"方法集合地"定位；`.github/workflows/check-leaderboard.yml` 每日 08:00 定时检查 HuggingFace leaderboard Space 存活。核心框架两层（LL03-LL04）：pipeline 入口+三层基类+六个组合器。策略五层（LL05-LL09，图谱权威口径）：**注意力评分系** 7 文件（observed/snapkv 之外的 expected_attention、criticalkv、duo_attention、finch、non_causal_attention 等）、**免查询数学系** 8 文件（knorm、leverage、cur、compactor、dms、dropkv、keydiff、qfilter）、**预算分配系** 8 文件（snapkv、tova、pyramidkv、adakv、lukv、lagkv、cap、simlayerkv）、**结构窗口系** 8 文件（streaming_llm、random、chunk、chunkkv、think、cam、compression_ratio_decoding、entropy_gated_chunkkv）、**上下文重构学习系** 6 文件（kvzip 血统五件套+kvcompose）——合计 37 个策略文件+9 个基类/组合器文件。外围（LL10-LL14）：kvzap 训练子项目、评测引擎、九大基准、notebook 教程、测试套件。

## 3. 三层基类体系

**BasePress**（`kvpress/presses/base_press.py:44`）定义全部策略的公共骨架：`__call__` 是 contextmanager（`:165`），进模型时给每层 self_attn 挂 forward_hook（`:203`，`register_forward_hook(..., with_kwargs=True)`）实现"prefill 后压缩"钩子（forward_hook 实现 `:101`）；compress 方法 `:61` 留给子类。SUPPORTED_MODELS 白名单（`:27-33`：Llama/Mistral/Phi3/Qwen2/Qwen3/Gemma3）之外的模型仅告警不拒绝（`:188-189`）。is_prefilling 辅助（`:37`）用 cache_position 判定前向阶段。**ScorerPress**（`kvpress/presses/scorer_press.py:18`）把"评分→排序→保留"抽成模板方法：score 抽象接口（`:36`）吐每 token 重要性分，compress（`:77`）统一执行——`compression_ratio==0` 直通（`:87`），否则 compute_n_kept 算保留数（`kvpress/utils.py:137`，公式 `max(1, int(k_len*(1-ratio)))`，ratio 语义=**删除比例**），`scores.topk(n_kept)`（`scorer_press.py:96`）后 gather 剪枝。断言 0≤ratio<1（`:34`）。**DecodingPress**（`kvpress/presses/decoding_press.py:23`）抽象解码期压缩：维护 per-layer 隐状态缓冲（`__post_init__:50`、buffer 默认 256，`:53` 用 defaultdict）、compress `:68`、forward_hook `:113`、reset `:181`、`__call__:187` 重写挂钩逻辑，_find_target_compression_ratio（`:194`）按目标 token 数反解比例。

## 4. 注意力补丁与公共工具

`import kvpress` 的瞬间就有全局副作用：`kvpress/__init__.py` 末尾调用 patch_attention_functions() 给 transformers 的 ALL_ATTENTION_FUNCTIONS 全量打补丁（`kvpress/attention_patch.py:98`），使 attention 支持 head 级 key 掩码——这是 AdaKV 系逐头压缩的前置条件（docstring 明言"automatically called when importing kvpress"）。补丁核心 search_hyperplane（`kvpress/attention_patch.py:8`）给 key 张量找分离超平面，把"无注意力权重"偏置进负区，让评分 press 在无 query 前向时也能拿到权重信号——这是全库最巧的一处工程。公共工具 `kvpress/utils.py`：get_prerope_query_states（`:13`，RoPE 前 query，评分系共用）、get_query_states（`:57`）、dequantize_layer（`:131`，反量化兼容）、compute_n_kept（`:137`）、extract_keys_and_values（`:150`）。

## 5. 五家族精选

**注意力评分系**：ObservedAttentionPress（`kvpress/presses/observed_attention_press.py:14`）直接用观测权重（需 output_attentions）；ExpectedAttentionPress（`kvpress/presses/expected_attention_press.py:18`，score `:126`）用 RoPE 前几何量免前向近似，统计版 `expected_attention_with_stats.py` 采集真实分布；CriticalKVPress（`kvpress/presses/criticalkv_press.py`）加输出投影权重两阶段。**免查询数学系**（推理开销最低）：KnormPress（`kvpress/presses/knorm_press.py:14`，score `:32`，46 行）是最佳入门——低范数 key 可丢；LeverageScorePress 在 pre-RoPE key 上算近似 leverage 分；CURPress 用 CUR 分解。**预算分配系**：SnapKVPress（`kvpress/presses/snapkv_press.py:18`，score `:69`）末窗注意力评分是教科书实现；TOVAPress（`kvpress/presses/tova_press.py:16`）在线逐 token 预算；PyramidKVPress **继承 SnapKVPress**（`kvpress/presses/pyramidkv_press.py:17`）只覆写逐层预算 get_layer_budget（`:47`，`:106` 消费）；AdaKVPress（`kvpress/presses/adakv_press.py:15`）逐头非均匀分配。**结构窗口系**：StreamingLLMPress（`kvpress/presses/streaming_llm_press.py:14`）sink+滑窗——但实现是 ScorerPress 子类：score `:38` 把 sink 窗外滑窗内打 0 分（`:52`）实现"保留"；ThinKPress（`kvpress/presses/think_press.py:15`）压通道维度（与 token 维正交）；CAMPress（`kvpress/presses/cam_press.py:25`）继承 DecodingPress 做解码期合并。**上下文重构学习系**（KVzip 血统）：KVzipPress（`kvpress/presses/kvzip_press.py:22`，400 行）以问答恢复为信号迭代定位重要 KV——`__call__:82` 装配、wrapped_forward `:125`、forward_hook `:147`；KVgradPress 继承它（`kvpress/presses/kvgrad_press.py:74`）用重构损失训练压缩；RestoreKVPress 再继承（`kvpress/presses/restorekv_press.py:19`）加学习式恢复；FastKVzipPress（`kvpress/presses/fastkvzip_press.py:144`）用预训练 MLP 门（FastKVzipGate `:24`，gate_id 正则解析 `:96`）替代迭代；KVzapPress（`kvpress/presses/kvzap_press.py:53`）加载训练好的门控权重做推理压缩——kvzap=KVzip 的快速近似（arXiv 2601.07891，`kvzap/README.md:4`，原版 KVzip=arXiv 2505.23416，`:6`）。

## 6. 组合器：策略的代数

六个组合器把 press 从"策略"升维成可组合系统：ComposedPress 串联（`kvpress/presses/composed_press.py:12`）；PrefillDecodingPress 分阶段（`kvpress/presses/prefill_decoding_press.py:20`）；PerLayerCompressionPress 逐层配比（`kvpress/presses/per_layer_compression_press.py:20`）；KeyRerotationPress 修 RoPE 位置（`kvpress/presses/key_rerotation_press.py:17`——剪 token 后对保留 key 重旋转，可包任意 ScorerPress）；MergingPress 把丢弃改相邻合并（`kvpress/presses/merging_press.py:19`）；BlockPress 块级保留（`kvpress/presses/block_press.py:15`）。推荐组合如 `DMSPress(KVzapPress(...), threshold=-4)`（`kvzap/README.md:19`）——kvzap 打分+DMS 解码策略联用。

## 7. 评测引擎与 leaderboard

`evaluation/evaluate.py`（577 行）是主引擎：EvaluationConfig 配置类（`:38`，max_new_tokens `:54`）、EvaluationRunner（`:189`）驱动"数据装载→press 压缩→生成→评分"全流程（run_evaluation `:503`），CliEntryPoint（`:533`）暴露命令行覆盖 YAML；模型×press×benchmark 笛卡尔积由 evaluate.sh 多 GPU 分派，默认 ruler/4096/Llama-3.1-8B。名字到实现的映射在 `evaluation/evaluate_registry.py` 三注册表（DATASET `:54`/SCORER `:68`/PRESS `:82`）。leaderboard.sh 生成榜单数据：两轮循环——"不需要 question 参与压缩的 press"与需要的分开跑（`evaluation/leaderboard.sh:10-15`），no_press 基线先行（`:13`）。基准十件套在 `evaluation/benchmarks/`（aime25/infinite_bench/longbench/longbenchv2/loogle/math500/needle_in_haystack/ruler/zero_scrolls+utils），每套 create_huggingface_dataset 造数+calculate_metrics 算分两件。kvzap 训练子项目闭环：train_mlp/train_linear 两种门型（`kvzap/train.py:28/:87`，总入口 `:122`）、KVzapDataCollector 采集样本（`kvzap/data.py:144`，load_nemotron_dataset `:22`）、evaluate_aime.py AIME25 验收（`kvzap/evaluate_aime.py:34`），产物被推理侧直接消费。

## 8. 测试防线、图谱说明与上手路径

测试四件：`tests/fixtures.py` 的 unit_test_model（`:16`，tiny 随机权重模型+设备选择 `:10`）是全部单测的模型源；`tests/default_presses.py` 给每个 press 定义带默认参数的测试子类（TestDuoAttentionPress `:40`、TestKVzapPress `:47`、TestFastKVzipPress `:60` 等）；`tests/presses/test_presses.py:65` 用 @pytest.mark.parametrize 批量消费（StoreKnormPress 辅助类 `:134`）；`tests/presses/test_scorer_press.py`（171 行）守基类短上下文路径。契约层 test_press_call.py（40 行）验证调用契约，test_pipeline.py（208 行）覆盖 FA2 带/不带 cache、无 press、单/无 question 分支；tests/integration/ 用真实模型做 ruler 集成验收。**图谱说明**：本仓图谱 440 节点，批阶段两条高价值甄别笔记见仓内 NOTES-DIGEST.md（attention_patch 超平面搜索、base_press 钩子集成点）。**上手路径**：①`notebooks/wikipedia_demo.ipynb` 对比无压缩 vs StreamingLLM 建立手感 → ②读 `kvpress/presses/knorm_press.py`（46 行）看 ScorerPress 最小实现 → ③`notebooks/new_press.ipynb`（19 cell）亲手写一个 → ④三层基类（第 3 节）→ ⑤五家族按需查表（第 5 节）→ ⑥跑 evaluation（`evaluation/README.md` 流程）。

**速查锚**：基类钩子 base_press.py:101；评分模板 scorer_press.py:77；保留数公式 utils.py:137；注意力补丁 attention_patch.py:98；超平面 attention_patch.py:8；pipeline 入口 pipeline.py:25；评测引擎 evaluate.py:189；注册表 evaluate_registry.py:82；kvzap 训练 train.py:122；组合器 composed_press.py:12。
