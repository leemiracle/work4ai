# 09 Checkpoint 体系：dist_checkpointing 全家桶与转换器插件群

## 一、角色定位

权重持久化两条平行战线。**运行时线** `megatron/core/dist_checkpointing/`（4030 行）是训练循环的保存/加载引擎：以 ShardedTensor 为中心的"逻辑分片声明"式分布式检查点，天然支持改 TP/PP/EP 重排加载。**离线线** `tools/checkpoint/`（近 9000 行）是格式转换器工厂：HF↔mcore、LLaVA/Mixtral 特化、加权合并、DSA→Mamba 重映射，靠 loader/saver 插件协议拼装；dist_checkpoint_io.py、gpt_checkpoint_interop.py 做桥接。

## 二、内部结构

**运行时核心 serialization.py**：入口 `load`（serialization.py:74）与 `save`（:339），docstring 即协议书——load 五步（公共态→factories→LocalNonPersistent→ShardedObjects→ShardedBase），save 七步（rank 0 写 common.pt、分片按策略落盘、写 metadata.json）。默认策略由 :58/:63 给出，后端默认 torch_dist。

**分片对象模型 mapping.py**：`ShardedBase`（:30）抽象根；`ShardedTensor`（:48）声明"全局张量的本地一片"（replica_id 与 pre/post offset 映射）；`ShardedObject`（:324）表达非张量对象；`ShardedTensorFactory`（:402）+`apply_factories`（:447）支持自定义对象拆成底层分片再重组；`LocalNonpersistentObject`（:306）标记不落盘。优化器态由 optimizer.py 用这些原语描述成可重排布局（DistributedOptimizer 五种参数态布局见 08 篇）。

**策略层 strategies/**：`MCoreMetadata`（torch.py:91）/`MCoreSavePlan`（:98）扩展 PyTorch DCP 元数据；`MCoreSavePlanner(DefaultSavePlanner)`（:406）与 `MCoreLoadPlanner(DefaultLoadPlanner)`（:495）挂在 torch.distributed.checkpoint 上；`TorchDistSaveShardedStrategy`（:600）/`TorchDistLoadShardedStrategy`（:840）承载配置。fully_parallel.py 的 `FullyParallelSaveStrategyWrapper`（:46）/`FullyParallelLoadStrategyWrapper`（:163）把保存负载也按 DP 切片；checkpointable.py 的 `CheckpointableShardedTensor`（:15）服务延迟物化。外围 validation.py（611 行完整性校验）、exchange_utils.py、tensor_aware_state_dict.py、gpt_checkpoint_interop.py。

**转换器总线 convert.py（168 行）**：`load_plugin`（:90）按 `loader_<name>`/`saver_<name>` 优先、裸名兜底 `importlib.import_module`（:93），按 `add_arguments` 存在性判活（:103-104）。执行模型是**双进程队列流水线**：saver 起子进程（:155），loader 在主进程（:160），`mp.Queue(maxsize=...)`（默认 50，:125）背压。消息协议在头注释（:26-88）完整定义：Metadata Namespace → embeddings/每层/final norm/lm head 顺序 dict → "done"；loader 发 "exit" 表失败。

**loader/saver 模板方法基类**：`MegatronCheckpointLoaderBase`（loader_base.py:10）的 `load()`（:396）是八步模板方法（解析参数→校验→选 provider→初始化环境→算 vocab→构元数据→load_model_shards→发队列），子类只覆写 `build_sys_argv`/`import_model_provider`/`_maybe_parse_additional_megatron_args`（:34，checkpoint 参数回填主参数）。最凶一手在 `parse_megatron_args`（:39）：**直接覆写 `sys.argv`**（:56）再调 Megatron parse_args——复用训练参数系统的全部代价集中于此。`load_model_shards`（:181）用 fake process group 逐 TP rank 换身份、逐 VP rank 重建模型再 load_checkpoint，在单进程里"演"出任意并行度。saver 侧对称：`MegatronCheckpointSaverBase`（saver_base.py:15）→ `MegatronCheckpointSaverLLM`（saver_core.py:33）→ `save_checkpoint`（:63）队列消费循环。

**特化插件族**：`MegatronCheckpointLoaderLLaVA`（loader_llava.py:32）三钩子全覆写（:41/:54/:96）；Mixtral 走 `loader_mixtral_hf.py`（:343）；保存侧 `MegatronCheckpointSaverLLaVA`（saver_llava.py:44）与独立类 `HFCheckpointSaverLLaVA`（saver_hf_llava.py:32）。两把重炮：`weighted_merge.py`（2188 行加权合并）与 `gpt_hybrid_conversion.py`（901 行 GPT↔hybrid 转换，配套 hybrid_conversion.py 与 remap_gpt_dsa_to_mamba.py 的 DSA→Mamba 重映射）；`checkpoint_inspector.py`（1534 行）离线检视。

**schema 四类体系**：mcore 侧 `ModelSchema`（schema_base.py:8，构造期硬断言 8 个必备键 ：14-24）→ `CoreSchema`（schema_core.py:17）→ 三个特化 `CoreLocalSchema`（:52）/`CoreTESchema`（:76）/`CoreMoETESchema`（:101，按 `num_experts // ep_size` 算本地专家）。注意 CoreMoETESchema 直接继承 CoreSchema 而非 CoreTESchema——名字像孙类实为兄弟。HF 侧 `HFSchema`（schema_hf.py:8）→ `HFLMSchema`（:25）/`HFInternViTSchema`（:58）/`HFSiglipSchema`（:94）/`HFRADIOSchema`（:129），`set/set_layer` 把逻辑名翻成 HF state_dict 键（swiglu 切换 gate_proj/fc1 命名）。

## 三、外部连接

运行时线被 `megatron/training/checkpointing.py` 每个保存/加载边界调用；optimizer.py 的分片声明让检查点与优化器布局解耦——08 篇 `checkpoint_fully_reshardable_formats` 成立的前提。strategies/torch.py 站在 PyTorch DCP DefaultSavePlanner 肩上。转换器线反向 import 训练侧（`from megatron.training.arguments import parse_args`，loader_base.py:48），`--megatron-path` 支持指向另一棵 Megatron 源码树（:44）——同一工具可在不同版本间搬权重。

## 四、数据流

训练保存：模型/优化器 `sharded_state_dict()`（含分片声明）→ `save()` 分流 factories→ShardedBase→普通对象进 common.pt（rank 0）→张量按策略协商去重（replica_id 决定谁写）→metadata.json。加载：目标布局的声明当"取货单"→planner 把全局切片映射到本 rank→`load()` 校验完整性后填充。转换：`--loader loader_core --saver saver_hf_llava` → convert.py 反射插件 → loader 聚合任意并行旧检查点回完整张量 → 队列按协议发 saver → saver 按 schema 逐层 set/set_layer 写目标格式。全程单机双进程，无需真实分布式环境。

## 五、设计决策

1. **声明式分片而非过程式搬运**：ShardedTensor 携带全局形状与本地偏移，保存/加载只对声明做规划——改并行度加载不需要专门工具，是整个体系最值钱的性质。
2. **站在 PyTorch DCP 上做子类**：继承 DefaultSavePlanner 而非自造轮子，只在元数据与去重策略处特化。
3. **插件用"命名约定+反射"而非注册表**：文件名即插件名，加新格式零改动总线。
4. **双进程队列而非函数调用**：loader/saver 天然并行，队列 maxsize 流控；代价是协议必须顺序严格，头注释 60 行协议文档是真正的接口契约。
5. **复用训练参数系统的代价显式化**：覆写 sys.argv（loader_base.py:56）很难看但避免两套参数 schema；模板方法把 hack 限制在基类一处。
6. **schema 是数据不是代码**：新旧两世界各一张键映射表，转换逻辑通用——加新模型多半只是加一张表。

## 六、新人提示

- 排查"加载后缺/多张量"先看 `StrictHandling`（serialization.py:79 默认 ASSUME_OK_UNEXPECTED），再跑 validation.py 校验，别急着怀疑文件。
- 写新插件：文件名必须 loader_/saver_ 前缀（或裸名模块），必须导出 add_arguments 与 load/save_checkpoint；消息顺序必须遵守 convert.py 头注释协议，乱序在对端 name 校验时炸（--no-checking 可跳过但别生产用）。
- `--loader core` 与旧值 `mcore` 等价（convert.py:134-139 自动迁移）。
- loader_llava 的 `_maybe_parse_additional_megatron_args`（:54）演示 checkpoint 独有参数注入 margs——子类定制首选钩子。
- 转大模型先 `print_memory_usage`（utils.py 工具，loader_base.py:7 导入）：单进程聚合全部 TP/PP 分片，内存按完整模型算。
- hybrid/DSA→Mamba 转换是近期新增线，改动频繁，用前核对 examples/ 对应脚本版本。
