# 05 · storage 与数据卫道士——六条继承链、坏行隔离与训练数据校验

## 角色定位

`utils/storage.py` 是数据面唯一事实源：算子之间不直接传 DataFrame，中间结果一律经 storage 的 step 链落介质（内存/文件/ClickHouse）。图谱中它有 268 条入边，全仓被引最多；`jsonl_reader.py` 与 `training_data.py` 是挂靠其侧的两名"数据卫道士"——前者隔离脏 JSONL 行，后者做训练数据结构校验。

## 内部结构

`DataFlowStorage` ABC（`storage.py:15`）约定三个抽象方法 `get_keys_from_dataframe`/`read`/`write`（`storage.py:19-36`）与调试用 `__repr__`（`storage.py:39-69`）。六个子类构成继承链：`LazyFileStorage`（`storage.py:71`）内存缓冲+原子落盘（临时文件+`os.replace`，`storage.py:391-409`），退出/信号钩子兜底 flush（`storage.py:180-204`）；`DummyStorage`（`storage.py:432`）最小桩；`FileStorage`（`storage.py:477`）即写即落盘，`step()` 返回浅拷贝共享 DataFrame 防 OOM（`storage.py:562-564`）；`MyScaleDBStorage`（`storage.py:795`）走 ClickHouse 连接池（`storage.py:749-761`）与 `sys:`/`user:` 字段前缀协议（`storage.py:764-769`）；`BatchedFileStorage`（`storage.py:974`）继承 FileStorage、限 jsonl/csv（`storage.py:991-992`），`iter_batches` 切批（`storage.py:1041-1064`），runner 注入 `_active_batch` 后 read 旁路返回当前帧（`storage.py:1012-1013`），写文件首批 `w` 后续 `a`（`storage.py:1109-1116`）；`StreamBatchedFileStorage`（`storage.py:1123`）改流式，get_keys 只读首行表头（`storage.py:1137-1163`），`iter_chunks` 走 chunksize 分块（`storage.py:1228-1243`）。

## 外部连接

上游消费：`Pipeline.py:11` import 并在编译期 assert（`Pipeline.py:74`）；checkpoint 深度依赖其内部协议 `first_entry_file_name`/`cache_type`/`_get_cache_file_path`（`pipeline_checkpoint.py:106-146`）。`jsonl_reader.py` 被 storage 单点引用（`storage.py:13`），图谱另有 record_execution/record_ledger 等三处直用。`training_data.py` 出边仅 json 标准库（`training_data.py:5`）——真零仓内依赖，却被 8 个结构评测/生成算子反向依赖。

## 数据流

`step()` 把 `operator_step` 从 -1 递增（`storage.py:546`），read 按 step 找内存缓冲→源文件→缓存文件，write 永远写 step+1 的文件（`storage.py:722`）；step 0 源可为本地文件或 `hf:`/`ms:` 远程数据集（`storage.py:637-663`）。脏数据路径：`JSONLReadPolicy.bind` 把 policy 绑死单源并防 ledger 与源/缓存同名（`jsonl_reader.py:28-35`）；`inspect` 全量扫描产出 keys 并原子写错误台账（`jsonl_reader.py:70-107`）；`iter_chunks` 给每批附 `dataflow_source_locations` 行级溯源（`jsonl_reader.py:122-123`）；身份指纹（ino/size/mtime）防扫描中文件被偷换（`jsonl_reader.py:37-40`）。校验路径：`TrainingDataError` 带 field+code 稳定错误码（`training_data.py:10-16`）；`validate_messages` 单轮严格 profile（`training_data.py:31-57`）；`validate_conversation` 是完整状态机——pending/returned 集合管 tool_call 与 tool 响应一一配对、必须以 assistant 非空回答收尾（`training_data.py:111-173`）。

## 设计决策

"算子间只传 storage 引用、数据经介质中转"使每步天然可断点、可审计、可重跑，是 checkpoint 体系的地基；批式与流式共用同一 runner 契约（`storage.py:1042-1048`）。批判：`clean_surrogates`（无效 Unicode 清洗）在三个类里各复制一份（`storage.py:330`、`storage.py:678`、`storage.py:1071`）；`FileStorage` 非原子写，docstring 自认中断可能留半文件（`storage.py:537-540`）——正因如此 checkpoint 只信自己的 fsync+truncate 协议（`pipeline_checkpoint.py:257-283`）；六链职责有交叠，LazyFileStorage 与 FileStorage 几乎是平行双实现。

## 新人提示

先 `storage.step()` 再读写，否则 ValueError（`storage.py:553-555`）；step 0 永不落写（`storage.py:372-380`）。批式续跑游标文件在 cache_path 下 `{prefix}_last_success_step.txt`。选型口诀：小数据 FileStorage、要崩溃安全走 BatchedFileStorage+checkpoint_dir、超大 JSONL 用 Stream 变体+JSONLReadPolicy。写训练数据算子直接复用 training_data.py 校验器，别自拼正则——tool_calls 配对规则比看上去复杂得多。
