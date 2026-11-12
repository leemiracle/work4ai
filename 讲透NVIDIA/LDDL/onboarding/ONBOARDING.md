# LDDL Onboarding：NVIDIA 语言数据集与数据加载器

> 仓：`/usr-data/data2/repos/agent-repos/NVIDIA/LDDL`（commit e4006d2b）
> 图谱：194 节点 / 399 边 / 9 层 / 14 步 tour。行号锚均经源码核实。

## 1. 项目定位与核心价值

LDDL（Language Datasets and Data Loaders，setup.py:34 声明版本 0.1.0）是 NVIDIA DeepLearning Examples 的配套数据工具库，负责 BERT 类预训练的"数据准备"全链路。它的核心价值主张有三条：

- **规模化预处理**：基于 Dask，用 MPI 把预处理扩展到多进程多节点（`lddl/dask/bert/pretrain.py:573` 的 `--schedule=mpi` 路径经 dask_mpi 初始化集群，:576 建 Client），面向 Wikipedia / Books / Common Crawl / OpenWebText 四语料。
- **序列分箱（binning）消灭 padding**：预处理期就按序列长度把样本分桶落盘（`lddl/dask/bert/binning.py:73` 按 `(seq_len-1)//bin_size` 计算 bin_id），训练期一个 mini-batch 内长度几乎一致，同时省掉 padding 的无效前向/反向计算与 rank 间批长不齐的空等（pretrain.py:645-666 的完整设计说明）。
- **加载与框架解耦**：torch / torch_mp / paddle 三套后端逐层同构，同一份均衡后的 parquet 直接喂 PyTorch 或 PaddlePaddle。

## 2. 总体架构

全库按四阶段流水线组织，setup.py:63-74 的 8 个 console_scripts 就是命令化地图：4 个下载器（download_wikipedia/books/common_crawl/open_webtext）+ 2 个预处理器（preprocess_bert_pretrain / preprocess_bart_pretrain）+ 均衡器 balance_dask_output + 缓存生成器 generate_num_samples_cache。图谱九层（L01-L09）自底向上：项目配置 → 共享基础库（utils/types/random）→ 离线下载器 → Dask 预处理引擎（BERT 主线 + BART 支线 + 负载均衡）→ 三套加载后端 → 基准与部署。注意 `lddl/dask/bert.py` 这个路径并不存在，884 行的 BERT 预处理核心实为 `lddl/dask/bert/pretrain.py`。

## 3. 核心模块地图

- **共享基石（L02）**：`lddl/utils.py` 是全库 API 汇点（fanIn 16）——分箱 parquet 发现（:47 get_all_parquets_under、:54 get_all_bin_ids 强制 bin id 从 0 连续）、`.num_samples.json` 缓存读取；`lddl/types.py:26` 的 File 类（path+num_samples）是预处理与加载两阶段间的元数据货币；`lddl/random.py:28` 的 rng_state 交换是确定性洗牌基石。
- **Dask 引擎（L04/L05）**：`lddl/dask/readers.py:60` 统一四源读取（random_sample 按 :69 的 sample_ratio 采样）；pretrain.py 完成 NSP 句对+MLM 掩码（:182 create_masked_lm_predictions、:241 create_pairs_from_document）；binning.py（509 行）内联改写 dask 的 to_parquet/to_textfiles（:135 to_parquet_binned 为 216 行核心），同目录 DASK_LICENSE.txt 随包分发 BSD 许可证。
- **负载均衡（L05）**：`lddl/dask/load_balance.py:159` 的 Progress 贪心调度把分片重组为样本数至多差 1 的 shard。
- **三后端（L06-L08）**：`lddl/torch/datasets.py:112` ParquetDataset 按 rank/world/worker 三级均分文件并内嵌 ShuffleBuffer；`lddl/torch/dataloader.py:32` Binned 按剩余样本量加权选桶；`lddl/torch/bert.py:199` get_bert_pretrain_data_loader（215 行）总装配。

## 4. 数据流与控制流

数据流四段：①下载器产出"行首带语料 id 的 text 分片"（readers.py:131 split_id_text 负责剥离）；②预处理器读入→全局洗牌（pretrain.py:100 _shuffle_bag_texts 用随机键做 dask shuffle）→句子切分组 Document→duplicate_factor 次重复构造句对（:389 循环）→按 `<partition>_<bin_id>` 落盘；③均衡器按 bin 分组（load_balance.py:405），各 bin 独立贪心均衡出 `shard-N.parquet_<bin_id>`，rank 0 落 `.num_samples.json`（:377）；④加载侧 ParquetDataset 用缓存免读 parquet 统计样本数（torch/datasets.py:173），按 epoch 种子派生 world/worker 两级 rng_state（:250-255 公式），`files[rank::world_size]` 再 `files[worker::nworkers]` 切分（:271-272），ShuffleBuffer 流式洗牌后交 Binned 加权迭代。控制流双轨：预处理/均衡走 MPI（load_balance.py:210-223 封装 COMM_WORLD；:226 _build_files 用 stride 循环+allreduce 协同统计），在线加载走 torch.distributed（datasets.py:188 all_reduce 同步各文件样本数）。

## 5. 环境与运行方式

安装即 `pip install ./`，依赖钉版激进：setup.py:49 `dask[complete]==2021.7.1`、:53 `pyarrow==14.0.1`（2023 年代版本与 2021 的 dask 同列，是后补的兼容升级）、:57 news-please 直接钉 git commit。两个 NGC Dockerfile（docker/ngc_pyt.Dockerfile / ngc_paddle.Dockerfile）装好 LDDL 并预下载 NLTK punkt（pretrain.py:583 运行期也会下载）。跑法两种：`--schedule=mpi` 配 mpirun/srun（pretrain.py:626 给出示例命令），`--schedule=local` 单机调试；jemalloc 经 LD_PRELOAD 注入。examples/local_example.sh 串起单机四阶段全流程，examples/slurm_example.sub 展示 Slurm 多节点形态。

## 6. 设计决策与权衡

- **分箱 vs 收敛**：bin_size 越小省算越多，但会改变长度分布引入收敛差异，官方 help 明言需经验权衡（pretrain.py:662-666）。
- **静态/动态双掩码**：静态掩码在预处理期固化（--masking，pretrain.py:859-871），动态掩码延迟到加载器（torch/bert.py:152，80/10/10 配方 :183-192），同一 epoch 换着花样掩，更接近多次采样。
- **流式 ShuffleBuffer 而非全量洗牌**：缓冲区随机弹出+回填（torch/datasets.py:95-100），warmup_factor 控制填充期进出比，内存有界。
- **"同构决策、单点 IO"的 MPI 均衡**：所有 rank 持有同样簿记做同样贪心决策，仅被 `idx % world_size == rank` 选中的 rank 真正读写表（load_balance.py:84-104 的 _store 在 table=None 时只加计数不落盘；:138 的归属判定），省通信且免锁。
- **确定性三段式**：world 级决策所有 rank 一致、worker 级决策各 worker 独立可复现（datasets.py:227-256），种子公式含 epoch/rank/worker 全维度。

## 7. 已知问题与勘误

1. **scanner stdlib 撞名（图谱层）**：`import random`（pretrain.py:35）/`import torch`/`import paddle` 等曾被解析到 lddl/random.py 等同名项目文件，17 条假边已剔除（lddl/random.py 还因此产生自引用）。真实语义：Python 3 绝对导入下 pretrain.py:35 用的是 stdlib random，dask worker 内确实非确定性——官方 `--seed` help 自己承认只控制采样（pretrain.py:832-834）。
2. **死代码**：pretrain.py:144 `_truncate`（连同 :114 `_cut`、:125 `_adjust` 的子词边界保护机制）从未被调用，实际用的是 :161 `_truncate_seq_pair`（调用点 :328）。死代码版更精致（防 `##` 子词被切断）但未启用。
3. **`Shard.balance` 签名陷阱**（load_balance.py:129）：无 self 也无 @staticmethod，靠 :361 的实例调用让绑定实例恰好填进 `larger_shard` 形参才正确工作——可读性陷阱，勿模仿。
4. **实例级 monkey-patch**：pretrain.py:481 `pairs.to_dataframe = to_dataframe_binned` 直接覆写单个 dask bag 实例的方法，非正规接口，升级 dask 时是隐性雷区。
5. **setup.py:56 与 :60 重复声明 wikiextractor**（PyPI `==3.0.6` 与 git `@v3.0.6` 各一条）。
6. **`--wikipedia-lang` choices 含 zh 但 help 自认 "Currenly, only en is supported"**（pretrain.py:755-757）。
7. **bert/pretrain 算法血统**：create_masked_lm_predictions、MaskedLmInstance（:179）及大段注释逐字源自 Google BERT 的 create_pretraining_data.py，属移植而非原创。

## 8. 新人上手路线

按图谱 14 步 tour 顺序即可，三档：**一小时版**——README 四阶段 + setup.py:63-74 命令地图 + `lddl/random.py`（55 行，全库最小却最核心）；**半天版**——加读 pretrain.py 的 :241-365（句对构造主循环）与 load_balance.py 的 :321-369（贪心主循环），对照 examples/local_example.sh 理解命令串联；**深入版**——读 binning.py:135-350 感受 dask 图改写，再对比 torch 与 torch_mp 两套 datasets/dataloader 的 diff（samples_seen 断点续训是全部差异所在），最后用 benchmarks/torch_train.py + make_training_seqlen_plots.py 验证分箱的减 padding 效果。调试入口：DatasetLogger 按 node/rank/worker 三级分文件记日志（lddl/torch/log.py），是排查多进程加载问题的主观测面。
