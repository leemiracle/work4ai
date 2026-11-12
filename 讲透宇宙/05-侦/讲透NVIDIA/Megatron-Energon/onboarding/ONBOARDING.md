# Megatron-Energon 新人上手指南（ONBOARDING）

> 基于知识图谱（648 节点 / 1814 边 / 16 层 / 15 步 tour，commit 90c527c）与源码逐点核实，行号锚以该 commit 为准。

## 1. 项目定位与背景

Megatron-Energon 是 NVIDIA Megatron 生态的**多模态数据加载与准备系统**：把原始数据（tar/jsonl/裸媒体目录）组织成可随机访问、可按权重混合、可断点续训的数据集。pip 包 megatron-energon，配 energon 命令行七子命令（`src/megatron/energon/cli/main.py:41`）。三条主线：**格式中立**（webdataset/binidx/jsonl/crude 共用一套工厂协议与 .nv-meta 准备产物）；**远端透明**（EPath 统一本地与 msc://、dss://，缓存池做吞吐闸门）；**训练级确定性**（每样本携带 `__restore_key__`，16 个可存档包装器任意组合都能从 checkpoint 恢复到下一个样本，跨 worker/rank/节点对齐）。规模：144 个 Python 文件，最大 savable_loader.py（1474 行）；内置 S3 模拟器使远端行为可离线回归。

## 2. 总体架构：16 层图谱逐层概述

按依赖方向从底层到外围分 16 层，建议自 L01 向 L12 纵向推进。

- **L01 核心基础与通用工具**（13 文件）：edataclass（slots+kw_only 数据类基座）、errors（SkipSample 跳样协议与错误分级，`src/megatron/energon/errors.py:13`）、source_info 溯源、rng 确定性随机、deprecated 兼容层。
- **L02 路径与远端存储**（6 文件）：EPath（`src/megatron/energon/epathlib/epath.py:36`，基于 Multi-Storage Client）、mapped_array、retry_stream、local_copy。
- **L03 文件缓存池**（5 文件）：FileStoreCachePool（`src/megatron/energon/cache/file_cache_pool.py:131`）线程池预取+共享 Future+引用计数+fork 安全。
- **L04 协议骨架与配置解析**（9 文件）：flavors 心脏——base_dataset 四大抽象（§4.1）、dataset_type 格式判定、resolver 按 priority 探测、load_config。
- **L05 manifest 与公共索引**（14 文件）：.nv-meta 目录（`src/megatron/energon/flavors/common/manifest/paths.py:3`）、split.yaml、index.sqlite、filter_index、DatasetSampler。
- **L06 webdataset 格式**（13 文件）：主力格式——itar 偏移索引（`src/megatron/energon/flavors/webdataset/itar.py:48`）、SqliteIndexWriter、prepare、预置工厂族、field_access。
- **L07 binidx/jsonl/crude**（11 文件）：binidx 为 LMDB 风格二进制索引；jsonl 走 ijsonl 增量读取；crude 吃裸文件目录。
- **L08 预定义样本类型**（11 文件）：text/image/captioning 图文基础，vqa/vid_qa 问答族，interleaved 交错多模态与 ocr。
- **L09 媒体处理与解码**（12 文件）：av_decoder.py（726 行）按容器选索引模式解码音视频切片，media/ 与 sample_decoder 入口。
- **L10 数据集包装器**（20 文件）：16+ 个可组合装饰器（blend/batch/packing/shuffle_buffer/map/repeat/epochize/concat/gc/watchdog 等），同一存档契约。
- **L11 任务编码与变换**（9 文件）：TaskEncoder 的 cook/encode/pack/batch 管线与 transforms。
- **L12 可保存加载与训练集成**（11 文件）：SavableDataLoader、WorkerConfig、recipe/ v2 配方递归解析。
- **L13 CLI 与准备工具**（10 文件）：七命令实现，prepare.py 600 行交互式向导。
- **L14 测试与 S3 模拟器**（30 文件）：17 个 test_* 全链路覆盖，含确定性专项。
- **L15 项目文档**（46 文件）：Sphinx 文档站+README/CONTRIBUTING/AGENTS.md。
- **L16 CI 与协作配置**（23 文件）：7 条 GitHub Actions、.agents/skills 五项 AI 协作技能、pyproject/justfile。

## 3. 核心链路数据流：从原始数据到训练批

**准备期**（energon prepare）：扫描 tar 分片 → indexing.py 建偏移索引写入 index.sqlite → manifest/write.py 切 train/val/test 生成 split.yaml → 交互向导（`src/megatron/energon/tools/prepare.py:193`）生成 dataset.yaml 与模板（:45）。产物落 .nv-meta/。

**训练期**：get_train_dataset(path) → get_dataset_type（`src/megatron/energon/flavors/dataset_type.py:27`，recipe→provider→sqlite 三级探测）→ DatasetFactoryResolver 按 priority 选工厂 → build() 产出 SavableDataset → TaskEncoder 装配链：build_train_datasets（`src/megatron/energon/task_encoder/base.py:782`）依次 RepeatDataset 无限化 → BlendDataset（:870）→ ShuffleBufferDataset（:882）→ encode_sample（:887）→ build_batch 组批/打包（:595）→ EpochizeDataset（:896）→ LogSampleDataset；最终 get_loader/get_savable_loader（`src/megatron/energon/loader.py:16`）包成 DataLoader。

**多 worker 多节点确定性**四机制咬合：

1. **切分**：WorkerConfig（`src/megatron/energon/worker.py:24`）持 rank/world_size/num_workers，每 worker 分片互斥；worker_rotation_offsets（`src/megatron/energon/task_encoder/base.py:806`）保证轮转起点不重不漏。
2. **随机**：worker_seed 由 global_worker_id+seed_offset 的 SHA1 派生（`src/megatron/energon/worker.py:248`）；洗牌用 FeistelPermutation 的 O(1) 内存双射（§5.4）。
3. **快照**：worker 周期落 checkpoint（`src/megatron/energon/savable_loader.py:455`），主进程 RPC 取回（:510），跨 rank gather 对齐 sample index 合并全局状态（:971）。
4. **恢复轮转**：worker_id_offset 左旋 worker 序号（`src/megatron/energon/worker.py:196`）补偿 torch 不可恢复的 worker 指针；恢复先回放再跳样本（`src/megatron/energon/savable_loader.py:410`）。

## 4. 模块深读

### 4.1 flavors：工厂协议（"一切皆工厂"）

BaseCoreDatasetFactory（`src/megatron/energon/flavors/base_dataset.py:369`）三方法闭环：get_original_shards（源序分片清单）、build()、as_file_store()（按 key 随机访问）；三种准备范式基类供四格式复用。SavableDataset（:201）是消费侧契约，`_savable_fields` 声明存档字段（:220）。Sample（:119）携 `__key__`/`__restore_key__`/`__tags__`/`__sources__` 四元数据字段。

webdataset 读取层是 itar：TarIndexReader（`src/megatron/energon/flavors/webdataset/itar.py:48`）把 .idx 当 8 字节大端整数数组（:62），每项是样本字节偏移——不解包 seek 读，远端友好。字段映射由 split_field_access 解析 `'a[b][c]'` 路径（`src/megatron/energon/flavors/webdataset/field_access.py:15`）。

### 4.2 wrappers：16 件套装饰器

全继承 BaseWrapperDataset（统一状态递归存取、ExitStack 全子 close）。以 BlendDataset（`src/megatron/energon/wrappers/blend_dataset.py:16`）为例：每 worker 按权重 choice_idx 抽签（:93），源耗尽置零权重（:28）；产出样本经 add_sample_restore_key（`src/megatron/energon/flavors/base_dataset.py:410`）压入源索引。批级混合是 MixBatchDataset（`src/megatron/energon/wrappers/mix_batch_dataset.py:75`）。

### 4.3 savable_loader：1474 行 checkpoint 引擎

worker 跑 daemon 命令线程（`src/megatron/energon/savable_loader.py:298`），weakref.proxy 持 self 防线程拖住数据集；主进程经 Queue 收发。快照策略（:455）：默认每 60 秒且至少 workers*2 样本落一个 checkpoint，环形保留 n 份；get_checkpoint（:510）从后往前找第一个 sample_index<=目标的快照并返回需跳过的 offset。

### 4.4 av：媒体解码

AVDecoder（`src/megatron/energon/av/av_decoder.py:42`）先 _inspect_index_mode（:78）按容器扩展名选索引模式：mkv/webm 走 PTS、mp4/mov/m4v 走 FRAMES、其余 PROBE。支持切片解码与帧缩放；PyAV 缺失时构造即抛 ImportError（:55）。

### 4.5 cache：预取与 fork 安全

FileStoreCachePool 的 _PendingTask（`src/megatron/energon/cache/file_cache_pool.py:110`）记录共享 Future 与引用计数；FileCacheLazy 在 `__del__` 递减引用计数（:62）。线程不穿越 fork，ForkMixin 钩子（:457）在子进程重建线程池。吞吐闸门：一个 worker 下载后同分片全命中缓存。

## 5. 关键设计决策

1. **工厂+`__restore_key__` 双协议**：格式差异压进工厂三方法；恢复键是嵌套元组，每层前缀类名与索引（`src/megatron/energon/flavors/base_dataset.py:418`），恢复时逐层断言再剥——局部保证，全局成立。
2. **EPath 存储抽象**：file:// 与裸路径归一 DEFAULT_PROFILE；dss:// 强制 NVDATASET_CACHE_DIR（`src/megatron/energon/epathlib/epath.py:84`）；`__getstate__` 不序列化 fs 防凭据泄漏（:105）；map_epath（`src/megatron/energon/epathlib/mapped_array.py:176`）按本地 mmap/远端 seek-read/先拷本地三择一。
3. **blend 配方双模式**：RecipeBlend 权重随机抽样（`src/megatron/energon/recipe/recipe.py:433`）与 RecipeBlendEpochized 重复数精确配比（:543）；对应 DATASET_WEIGHT（吞吐友好）与 SAMPLE_REPETITIONS（epoch 精确）两种装配（`src/megatron/energon/task_encoder/base.py:810`）。
4. **FeistelPermutation**（`src/megatron/energon/rng.py:31`）：8 轮 Feistel 网络+SplitMix64（:23），2^k 域双射后 cycle-walking 收回——O(1) 内存均匀洗牌，多 worker 各取不相交切片即等价全局（<8 轮有偏差，:37）。
5. **stateless 装饰器**（`src/megatron/energon/task_encoder/base.py:126`）：编码函数用随机性时进出各保存/恢复全局 RNG，样本可独立重放；WorkerRng 自实现多项式采样规避 torch 2.7 torch.multinomial 变更（`src/megatron/energon/rng.py:143`）。
6. **错误分级与溯源**：SkipSample（跳样本）→ SampleException（ErrorContext 跟踪连续失败超容差升级，`src/megatron/energon/errors.py:51`）→ FatalSampleError（终止），恢复期默认 reraise（`src/megatron/energon/worker.py:67`）；SourceInfo 随 Lazy get() 自动 attach（`src/megatron/energon/cache/file_cache_pool.py:49`），报错直达物理文件。

## 6. 测试与质量体系

17 个 test 文件三支柱：test_dataset.py（2216 行全链路+四 CLI 命令）、test_dataset_det.py 确定性专项（`tests/test_dataset_det.py:233` 起：determinism/跨 rank 恢复/样本不变性）、test_recipe.py（2016 行配方确定性）。内置 S3 模拟器让远端语义可离线回归；CI 七条 workflow+justfile；AGENTS.md+.agents/skills 表明本仓即 agent 协作开发样板。

## 7. 新人上手路径（按 15 步 tour 精选 9 步）

1. **总览与样本基因**：README+`__init__.py` → edataclass/errors/source_info，建立样本模型心智。
2. **统一路径**：epath.py+mapped_array.py，跑通本地与 msc:// 差异。
3. **协议骨架**：base_dataset 四抽象+resolver，确立"一切皆工厂"。
4. **准备期**：跟 energon prepare 走一遍 .nv-meta 产物。
5. **主力格式**：itar+base_webdataset，理解"tar 不解包随机访问"。
6. **包装器乐高**：从 base.py 父类读起，精读 blend/packing/batch。
7. **最后一跳**：TaskEncoder 四阶段与装配表，写自己的子类（多数用户只需这步）。
8. **checkpoint 之道**：SavableDataLoader 类 docstring（`src/megatron/energon/savable_loader.py:633`）→_store_checkpoint。
9. **验证面收尾**：跑 test_dataset_det.py，读 justfile 与 PR 模板。

## 8. 常见坑与勘误（源码甄别，读码/改动前必看）

1. **retry_stream 重试分支疑似丢数据**：`src/megatron/energon/retry_stream.py:44` 的 read() 把多次重试的读累计进 buf，却返回最后一次的 res 而非 buf（:52）——短读后再次循环丢先前累积字节。
2. **packing_dataset 恢复键双重剥取**：`src/megatron/energon/wrappers/packing_dataset.py:371`、:375、:383 三处同一赋值连写两遍，疑似编辑残留；当前等于剥两层键，层数对不上时恢复走错。
3. **tar_patcher 死代码引用不存在属性**：_evaluate_pax_header（`src/megatron/energon/flavors/webdataset/tar_patcher.py:632`）与 _skip_payload（:654）全仓无调用（实走 numba 版 :309），且 :650 引用的 result.issues 在 TarScanResult（:44，仅两字段）上不存在。
4. **merge.py cv2 分支不可达**：`src/megatron/energon/transforms/merge.py:159` 先 raise NotImplementedError()，:161-163 的 import cv2/warpAffine 永不执行。
5. **typed_converter._isinstance_deep 误用 get_args(val)**：`src/megatron/energon/typed_converter.py:1145` 起，Literal/list/tuple/dict 四分支（:1150 等）全对**值**取 typing.get_args(val) 而非对**类型** tp_chk 取参。
6. **MixDataset 幽灵引用**：`src/megatron/energon/task_encoder/loader.py:129`、:200、:255 三处 docstring 引用不存在的 megatron.energon.MixDataset；实为 BlendDataset（`src/megatron/energon/task_encoder/base.py:870`）与 MixBatchDataset。
7. **11 个 flavor 专用 Webdataset 类全弃用**：TextWebdataset（`src/megatron/energon/flavors/text.py:20`）、ImageWebdataset（image.py:22）、CaptioningWebdataset（captioning.py:25）等，构造即 warn_deprecated，新数据集用 StandardWebdatasetFactory。
8. **webdataset/config.py 名不副实**：仅剩 split_name_re/skip_meta_re 两个正则（`src/megatron/energon/flavors/webdataset/config.py:8`），其余全转 deprecated 兼容层。
9. **METADATASET=RECIPE 枚举别名**：`src/megatron/energon/flavors/dataset_type.py:15` 里 METADATASET 值就是 "recipe"，旧名保留同值别名。
10. **wrappers.SkipSample 是弃用别名**：`src/megatron/energon/wrappers/skip.py:9` 继承自 megatron.energon.SkipSample（errors.py:13），构造即 FutureWarning。
11. **copy_to_local 是 map_epath 参数**：`docs/source/internals/epath_storage.md:29` 提到的 copy_to_local 是 EPath.map()/map_epath 的开关参数（`src/megatron/energon/epathlib/mapped_array.py:182`）。
12. **通行坑**：worker_config 必须传数据集而非 loader（`src/megatron/energon/loader.py:104` 传了只报警不生效）；BlendDataset 要求权重>0 且每 worker 至少一源有样本（`src/megatron/energon/wrappers/blend_dataset.py:68`），小数据集+多 worker 即 RuntimeError；dss:// 未设 NVDATASET_CACHE_DIR 即断言失败。
