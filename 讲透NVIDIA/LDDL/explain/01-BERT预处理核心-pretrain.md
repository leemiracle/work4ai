# 01 · BERT 预处理核心：lddl/dask/bert/pretrain.py（884 行）

> 注意路径勘误：本文件是 `lddl/dask/bert/pretrain.py`；`lddl/dask/bert.py` 这个路径在仓内不存在。全文行号锚均经源码核实。

## 角色定位

这是 LDDL 流水线第二阶段的核心，也是全库最重的文件（884 行）：把下载器产出的 text 分片变成"BERT 预训练可直接消费"的样本。它承担三件事——文档级句子切分、NSP 句对构造、MLM 掩码生成，最后按序列长度分箱落盘 parquet/txt。setup.py:69 把它注册为 `preprocess_bert_pretrain` 命令，入口在文件尾 pretrain.py:883 的 console_script。算法血统清晰：`create_masked_lm_predictions`（pretrain.py:182）、`MaskedLmInstance`（pretrain.py:179）与大段注释逐字移植自 Google BERT 的 create_pretraining_data.py。

## 内部结构

文件按 dask 惰性图组织，五个层次：①数据类 Sentence/Document（:49/:61，纯 token 容器）；②文档化 `_get_documents`（pretrain.py:77）——nltk 分句、tokenizer 切子词、按非空过滤；③句对与掩码算法层：`create_pairs_from_document`（pretrain.py:241）主循环 + `create_masked_lm_predictions`（:182）+ `_truncate_seq_pair`（:161）；④dask 组装层 `_get_pairs`（:368）——多源 concat、全局洗牌、`map_partitions(_to_partition_pairs)`（:441）；⑤输出层 `_save_parquet`（:444）/`_save_txt` 与 main（:563）。argparse 的 attach_args（:618）藏着最详细的分箱设计文档（:645-666）。

## 外部连接

上游依赖 `..readers` 四个 read_*（:40 导入）与 `lddl.utils`/`lddl.download.utils` 的工具；下游把控制权交给 binning.py 的三个 to_*_binned（:46 导入）。main 里 `--schedule=mpi` 时经 dask_mpi 初始化分布式集群（:573-576），tokenizer 用 BertTokenizerFast（:585-587，vocab 可为本地文件或 HF 模型 id）。产出直接被 lddl/dask/load_balance.py 消费。

## 数据流

每条文档的旅程：read_* 读入带语料 id 的行 → `_shuffle_bag_texts`（pretrain.py:100）给每行挂随机键做 dask 全局 shuffle → `_get_documents` 分句切词 → `_get_pairs` 内对每个分区做 duplicate_factor 次重复采样（:389 循环，默认 5，因句对构造含三重随机性，同文档可产出不同句对集）→ `create_pairs_from_document` 按 target_seq_length 贪心聚句成 chunk，10% 概率换用短序列目标（:264-265，缓解预训练/微调长度失配），随机决定 B 段是真后继还是随机文档（:295，NSP 正负样本），随机文档 10 次重试避免撞自己（:303），未用句子"放回"（:320-321）→ 掩码：num_to_predict=max(1, round(len*ratio))（:198），80% 换 [MASK]、10% 保留、10% 换随机词（:211-219），位置序列化成 uint16 bytes（:345）→ 落盘时 `num_tokens = len(A)+len(B)+3`（:352）供分箱用。

## 设计决策

- **静态/动态掩码双模**（:859-871）：`--masking` 在预处理期固化掩码（可离线复用、跨 epoch 不变），不设则把掩码延迟到加载器动态做——同一份落盘数据每个 epoch 换着花样掩，等效扩样。
- **分箱约束前置校验**：bin_size 必须整除 target_seq_length（:566-571 检查），nbins = target//bin_size（:480），保证桶边界与长度上限对齐。
- **dask 分区即随机域**：所有 random 调用都在 worker 内的 stdlib random 上（:35 导入），故 `--seed` 只控制语料采样（:832-834 help 自认其余非确定）。
- **实例级 monkey-patch 落盘**：`pairs.to_dataframe = to_dataframe_binned`（:481）覆写单个 bag 实例方法再调 to_parquet_binned（:488）——灵活但升级 dask 时是隐性雷区。

## 新人提示

先读 :241-365 的句对主循环（对照 BERT 原论文的 segment A/B 概念），再读 :182-238 的掩码函数。注意 :144 `_truncate`（连同 :114 `_cut`、:125 `_adjust` 的子词边界保护逻辑）是死代码，真正被调用的是 :161 `_truncate_seq_pair`（调用点 :328）——前者的"防 ## 子词切断"设计更精致但从未启用，别在读码时把两者混为一谈。txt 输出仅调试用（:747 help），生产一律 parquet。
