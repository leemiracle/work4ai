# 06 BART 全家桶

## 角色定位

`PyTorch/LanguageModeling/BART/` 是序列到序列（摘要/翻译）的完整示例州：图谱第 6 层"BART 序列到序列训练"（tour step-07）。它自成小生态——训练底座 training_base.py、四个入口（pretrain/finetune/eval/蒸馏）、vendored 模型包 bart/（HF transformers 早期快照）、工具库 utils/（含约 2000 行的 generation_utils 生成引擎）、configs 四份 JSON 与 scripts 两级编排。与 BERT 目录（第 02-04 篇）相比，BART 换了技术代际：PyTorch-Lightning 训练框架、lddl Parquet 流式预训练数据、apex FusedMixedPrecisionLamb 优化器——它是仓内"新一代示例长什么样"的参照系。

## 内部结构

**training_base.py 底座**：BaseTransformer 是 Lightning 模块骨架（优化器/调度/dataloader/checkpoint/generic_train/test），被三个入口共同继承。L37 `from apex.optimizers import FusedAdam, FusedMixedPrecisionLamb`，L149 `optimizer = FusedMixedPrecisionLamb(...)`——LAMB 在这里才是真接线（对比 BART/bart/lamb.py 孤儿与 BERT 的 FusedLAMBAMP，见第 02 篇）。L155-156 护栏：`--allreduce_post_accumulation_half_precision` 只支持 LAMB（否则 raise），L157 起是 Adafactor 备选。

**四入口**：

1. `pretrain.py`：L82 PretrainingModule(BaseTransformer)；L120 装配 `DataCollatorForBART`（utils/data_collator.py 尾部的 NVIDIA 定制 collator——span-corruption+句子排列预训练掩码）；L219 `get_all_parquets_under` 消费 lddl 预处理的 Parquet 语料；L307 main 里 `torch.distributed.init_process_group(backend="nccl")`——原生训练循环不走 lightning 的分布式封装。
2. `finetune.py`：L66 SummarizationModule、L405 TranslationModule——**翻译模块直接继承摘要模块**（复用多数行为、只覆写数据与指标）。L394-397 四个蒸馏参数（--distill/--layers/--do_encoder/--do_decoder），L442 `distill()` 按序号挑层、L457 `distill_sft()` 把 encoder/decoder 的 nn.ModuleList 就地替换为瘦身层列表（SFT 前的结构蒸馏）。
3. `run_eval.py`：独立评测/生成脚本，多节点分片生成+汇总算 BLEU/ROUGE；L60 `distill()` 与 L72 `distill_sft()` 是 finetune.py:442/457 的同源拷贝——同一逻辑两侧各自维护，有漂移风险。
4. 蒸馏不设独立脚本：任务蒸馏内嵌在 finetune/run_eval 的 --distill sft。

**configs 四份 JSON**：`config.json`（cnn_dm 口径）是 **HF facebook/bart-large 原版口径留档**——force_bos_token_to_be_generated、task_specific_params.summarization 块（max_length 142/min_length 56/num_beams 4/no_repeat_ngram 3）与 HF 上游逐字一致，保证与 HF 生态对表；`config_hf*.json` 是显式的"上游参照"副本；`config_xsum.json` 除生成参数（max_length 62/min 11/beam 6）外混入**蒸馏死字段**：`student_encoder_layers: null`/`student_decoder_layers: null`/`replacing_rate: 0`——全仓 `.py` 零消费者（configuration_bart.py 只定义 normalize_embedding/static_position_embeddings 等真字段），是 bart-stochastic 蒸馏世系的配置化石。

**bart/ vendored 包**：`__init__.py` 仅三行 `from . import configuration/tokenization/modeling`——挂载子包不 re-export 符号，调用方必须深路径 `from bart.modeling.modeling_bart import ...`。tokenization/ 9 文件是 HF 分词体系早期快照（GPT2→Roberta→Bart 继承链+XLM-R/MBart/XLNet）；modeling/ 内有 modeling_bart.py（双栈+五任务头）、modeling_t5.py（蒸馏教师与对照臂）、modeling_utils.py 基类与 bert_attn.py 孤儿片段（见第 02 篇）。

## 外部连接

- **apex**：training_base.py:37/149 唯一优化器真源；
- **lddl**：pretrain.py:61 与 scripts/get_pretraining_data.sh 的三个外部命令（download_wikipedia/download_common_crawl/download_open_webtext，git+https 安装）；
- **PyTorch-Lightning**：finetune 的 Trainer 全托管；utils/callbacks.py 的 Seq2SeqLoggingCallback/CheckpointEveryNSteps；
- **HF transformers（vendored 而非依赖）**：bart/ + utils/file_utils.py（hf_bucket_url/cached_path 下载缓存）+ utils/generation_utils.py（GenerationMixin 四种解码循环）构成一套不 import transformers 包的自带体系；
- **Docker**：scripts/docker/build.sh 产 bart_pyt 镜像，launch.sh `--ipc=host` 挂载 `${PWD}`→`/workspace/bart`——所有 `/workspace/...` 绝对路径的来源；
- **tacotron2 vendored 的对照视角**：BART 的 bart/ 包与 CUDA-Optimized/FastSpeech 仓内 vendored 的 tacotron2/（上游 NVIDIA/tacotron2 快照，__init__.py 仅 `import tacotron2.model`；waveglow/data_function.py 残留指向不存在 common 包的上游残迹）是同一联邦模式的两面——**把上游依赖钉成仓内快照**。BART 钉"框架"（HF transformers），FastSpeech 钉"教师模型仓"（Tacotron2）；快照剪裁的残渣（bert_attn.py、lamb.py）两侧都留了化石。

## 数据流

微调线：get_data.sh（gdown 拉 CNN/DM → utils/make_datafiles.py 按 SHA1 分片定位 story、解析 @highlight、写 .source/.target）→ finetune.py（Seq2SeqDataset+Sortish 采样器，Seq2SeqDataLoader 多卡自动分片）→ generic_train（FusedMixedPrecisionLamb）→ final_step.ckpt → run_summarization.sh 定位 ckpt → run_eval.py beam 生成 → ROUGE。

预训练线：get_pretraining_data.sh 三源下载 → preprocess_pretrain_data.sh mpirun 16 进程两轮（seq128/seq512）驱动 lddl preprocess_bart_pretrain → balance_dask_output 切 1280 分片 → pretrain.py 流式读 Parquet → DataCollatorForBART 掩码 → 两阶段课程（run_pretraining.sh 用 printf -v 打包 15 个位置参数；phase1 短序列 95040 步、phase2 长序列 7560 步且 `--load_model_weights_only` 只载权重不续训练状态）。

蒸馏线：finetune 训好/载入教师 → --distill sft + --layers 0-6-11 挑层 → distill_sft 就地删层 → 瘦身模型继续 SFT → run_eval --distill sft 复刻同一删层逻辑后评测。

## 设计决策

1. **vendored 快照代替版本约束**：HF transformers 早期 API 剧烈变动，钉快照让示例五年可复现；代价是快照内代码永不升级，换新版只能自己剥离 bart/ 包。
2. **TranslationModule 继承 SummarizationModule**（finetune.py:405）而非共抽基类：承认两任务 90% 同构，省一个抽象层；代价是第三个任务出现时重构压力陡增。
3. **configs 双轨制**：`config*.json`（实际消费）与 `config_hf*.json`（上游参照留档）并存，与 HF 对表不必翻外网。
4. **蒸馏=挑层删除**而非重训小模型：distill() 的 del-layers 语义（finetune.py:442-455）让"12 层删到 6 层"成为纯结构操作，后续 SFT 恢复精度。
5. **两阶段课程 + 只载权重切换**（run_pretraining_phase2.sh）：phase2 不继承优化器状态，长短序列课程解耦"学语言"与"学长依赖"。

## 新人提示

- 找 BART 模型代码不要 `from bart import ...`——包根无导出，必须走 `bart.modeling.modeling_bart` 深路径。
- config_xsum.json 的 student_*/replacing_rate 字段没人消费，排查配置漂移时跳过；真字段清单以 configuration_bart.py 为准。
- run_eval.py 与 finetune.py 的 distill 是两份拷贝，改挑层逻辑要两处同步——全家桶里最像"复制分叉"的隐患（对比第 04 篇三变体的零分叉）。
- scripts/ 的 shell 全按容器内 cwd=/workspace/bart 假设书写，本地直跑会连环失败；先 docker 或通读 get_data.sh 再动手。
- 基准脚本 grep 的 `INFO:tensorflow:` 前缀是 PyTorch-Lightning 写日志的 TF 遗留格式——不是你跑错了框架。
