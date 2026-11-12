# 02 · flavors 家族：格式工厂与 ICP 接口契约协议

## 角色定位

`flavors/` 是 Energon 的格式层：把 WebDataset 目录、jsonl/binidx 单文件、manifest 数据集统一变成 `SavableDataset`。贯穿全族的核心是 **ICP（接口契约协议）**——用 `runtime_checkable Protocol` 把"一个数据格式必须会什么"写成两份机器可查契约，而非继承树：

1. 工厂侧 `DatasetFactoryProvider`（dataset_factory_resolver.py:15）：三个 classmethod——`detect_path`/`get_original_shards`（原始分片清单）/`from_path`（实例化工厂），实现后用 `@register_dataset_factory_provider`（:124）挂进探测链。
2. 读取器侧 `common/reader.py` 四级阶梯：`IndexedSampleReader`（:15，整数随机访问）→ `SamplePartReader`（:29，加部件枚举）→ `PartFileReader`（:46，字符串 key 取部件）→ `SamplePartFileReader`（:60，组合）。tar/jsonl/binidx 读取器都向这组 Protocol 对齐，上层不关心物理格式。

## 内部结构

- `dataset_type.py`：枚举（:13）与判定链 `get_dataset_type`（:27）——yaml 即 recipe（:23），否则问 resolver，再查 `.nv-meta/index.sqlite` 判 FILESYSTEM（:38），不中则 INVALID。
- `dataset_factory_resolver.py`：单例（:148）持优先级表，FIRST=0/SINGLE_FILE=100/MANIFEST=200（:26），bisect 插入（:54）线性探测（:61）；`get` 失败报"忘了 prepare"引导（:86）。
- `base_manifest_dataset.py`：webdataset 系 provider，`detect_path` 靠 `.nv-meta/.info.json|.yaml`（:38）；`from_path`（:53）默认读 `dataset.yaml`+train（:69），`default_type=StandardWebdatasetFactory`（:82）让 yaml 不写类名也行。
- `webdataset/` 工厂链：`StandardWebdatasetFactory`（standard_webdataset.py:15）收 `sample_type` 并断言子类（:60），向下 DefaultDecoder（自动解码）→DefaultGeneric→Base。
- 单文件双兄弟：jsonl 的 `CrudeJsonlDatasetFactory`（crude_jsonl_dataset.py:26，Default 子类 :117 注册、:122 只认 `.jsonl`、:70 断言索引一致）与 binidx 的 Megatron-LM 词表格式（binidx_dataset.py:26，:104 注册）。
- `crude.py`：`CrudeSample` 是裸 dict（:10）；`CrudeWebdataset`（:14）强制 sample_loader 恒等（:48）且禁用户传（:42）。

## 外部连接

- 上游入口 `get_dataset_from_config`（dataset_config.py:49）：path→resolver.get()（:84）→tags 合并→类型断言（:99）。
- yaml→对象靠 `typed_converter.JsonParser`（dataset_config.py:18）：`sample_type: {__module__, __class__}` 由它反序列化成类喂给工厂。
- `base_indexed_dataset.build`（base_indexed_dataset.py:141）是工厂与运行时交界：part_filter→filter index→`shard_workers` 分片→`_build_reader`（:163）→`DatasetSampler`（:170）→`MapDataset`（:178）。
- `recipe/` 与 `task_encoder/` 都消费工厂；11 个旧味觉类仍从 `flavors/__init__.py` 导出保兼容；产出的 SavableDataset 交给 loader（见 01 篇）。

## 数据流

典型 WebDataset 目录实例化：`/data/xxx` → 判 MANIFEST_DATASET → `from_path` 读 `.nv-meta/dataset.yaml` → JsonParser 反序列化（顶层无 `__class__` 落默认工厂，`sample_type.__class__` 决定样本 dataclass，CrudeSample 即 crude 模式）→ `ShardListMeta.from_config`（base_manifest_dataset.py:112）展开 split 分片 → `build()` 产出 `MapDataset(DatasetSampler(reader))`。

读取器契约在此生效：`DatasetSampler` 只依赖整数访问契约，四种 reader 可无缝互换；`get_original_shards`（crude_jsonl_dataset.py:39 用偏移索引数样本）供 recipe 层做权重对账。

## 设计决策

- **ICP 用 Protocol 而非基类**：`@runtime_checkable` 让 isinstance 动态验约（reader.py:14），第三方格式不必 import 内部基类树；注册表收敛接入点（resolver.py:124），自定义 provider 优先级 0 压过内置。
- **11 个 deprecated 味觉类的来龙去脉**：旧 API 在 dataset.yaml 顶层写 `__module__/__class__` 指向 TextWebdataset 等 11 个"格式即类"包装（text.py:20、captioning.py:25 等各一）；新 API 把样本类型下沉为 `sample_type` 字段、顶层统一工厂。旧类没删，变成"构造即告警"的壳——告警文本（captioning.py:29-37）就是转换说明书（删顶层 __module__/__class__、改写 sample_type 两行、其余保留），warn_deprecated 是统一入口。
- **模块级兼容层**：deprecated.py:22 的 `DEPRECATED_MODULES` 记录 14 个旧模块的符号迁移，`_DeprecatedModuleFinder`（:286）挂 `sys.meta_path`，旧 import 可用但发警告——比删符号温和。
- **Crude 哲学**：解码推迟到用户 cooker，样本原始字段直出（crude.py:48 恒等加载），适合字段不稳定的数据湖。
- **单文件走旁路索引**：jsonl 偏移索引与 binidx 头给 O(1) 随机访问；:70 的一致性断言把"索引陈旧"提前为构造期报错。

## 新人提示

1. 接新格式只写三方法+装饰器（参考 crude_jsonl_dataset.py:117）；读取器对齐 `SamplePartFileReader` 即可。
2. 改样本类型只动 `sample_type.__class__`；旧数据集顶层 `__class__: TextWebdataset` 按告警迁移。
3. "Path does not contain .nv-meta"报错先跑 prepare 生成 manifest（:96 有引导文案）。
4. 调试用 `get_dataset_type(path)` 看路径被认成哪类；`index.sqlite` 存在是 FILESYSTEM 型标志。
5. 自定义 sample_type 必须是 `Sample` 子类（standard_webdataset.py:60 断言），字段名即文件后缀的 field_map 默认约定。
6. `get_original_shards` 绕过 filter/subset 返回源顺序全量（resolver.py:68），对账时勿与运行口径混用。
