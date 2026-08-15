# A-13 `activeloopai/deeplake`（9.2K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\activeloopai__deeplake
> C++/Python（pybind11 单向绑定）｜ Apache-2.0 ｜ 一句话定位：面向 AI 数据湖的列式存储 + TQL 查询引擎（"Database for all AI data"），本仓库为 4.x 重写版——Python 层只是薄壳，核心全部在 C++。

## 1. 架构总览（目录地图，标出核心目录的职责）

```
python/deeplake/     Python API 薄壳：全部 re-export 自编译扩展 _deeplake（pybind11）
  __init__.pyi       类型存根：Dataset/Column/Branch/Tag/Version/query() 等 ~170 符号
  storage.pyi        云存储 Reader/Writer 抽象（s3/gcs/azure/filesystem）
  schemas.pyi        TextEmbeddings / COCOImages 预置 schema 模板
  types.pyi / tql.pyi / core.pyi   类型/查询/内核存根
cpp/                 C++ 核心（本仓真正的实现）
  deeplake_core/     存储格式层：chunk 策略、datafile 格式、索引类型、类型系统
  deeplake/          逻辑 schema（column_definition/schema/column_datafiles_info）
  deeplake_api/      对外 C++ API：dataset/branch/tag/history/log_entry/replay_log
  heimdall/          列/行读视图层（column/row/dataset_view，惰性迭代）
  bifrost/           列流式读取（column_streamer/async_prefetcher）
  tql/               TQL 查询语言执行器（SQL 方言，基于 hyrise sql-parser）
  query_core/        查询中间表示（expr/top_k_search_info/search_config）
  icm/               自研基础库：JSON/trie(roaring)/schema_field/shape
  nd/                N 维数组内核（40+ array 实现：lazy/strided/transformed...）
  storage/           存储抽象（reader/writer/provider_base）
  codecs/            压缩编解码（compression.hpp）
  deeplake_pg/       Postgres 变体；vcpkg/ C++ 依赖管理；async/ 自研 promise/future
```

关键事实：`python/deeplake/core.py:1-3`、`python/deeplake/storage.py:1-3`、`python/deeplake/schemas.py:1-7` 全部只有一行 `from ._deeplake.xxx import *`——Python 侧无任何业务逻辑，读源码必须进 `cpp/`。`.pyi` 存根是理解 API 面的最佳入口（带完整 docstring 与示例）。

## 2. 记忆机制深读（本笔记核心）

DeepLake 不是 Agent 记忆系统，而是"Agent 数据运行时"：它提供记忆系统底座所需的存储格式、向量/全文索引、SQL 级检索与版本控制。以下按"作为记忆底座"的视角深读。

### 2.1 写入/抽取管线（谁触发、schema 是什么）

- 写入由应用侧显式驱动，无任何 LLM 抽取管线——抽取是上层（LangChain/记忆框架）的事：
  - 建列：`ds.add_column(name, dtype)`；写行：`ds.append({...})`。
  - Column 读写支持单条/区间/索引列表三种寻址（`python/deeplake/__init__.pyi:1401-1436` ColumnView.__getitem__ docstring）。
  - 异步写：`set_async(slice(0,32), new_labels)` 返回 FutureVoid，`commit_async()` 不阻塞（__init__.pyi:310-348）。
- 预置"Agent 记忆 schema"：`python/deeplake/schemas.pyi:11-58` `TextEmbeddings(embedding_size, quantize)`，字段为：
  - `id(uint64)` / `chunk_index(uint16)` / `document_id(uint64)` / `date_created(uint64)` / `text_chunk(text)` / `embedding(float32[n])`——即一个标准 RAG 分块表。
  - `quantize=True` 时"slightly decrease accuracy while greatly increasing query speed"（schemas.pyi:35）。
  - schema 可自由增删改：`schema["text_embed"] = schema.pop("embedding"); schema["author"] = types.Text()`（schemas.pyi:45-56）。
  - `schemas.pyi:60-131` `COCOImages` 同理（图像+边界框+嵌入多模态记忆表）。
- 元数据即时持久化：`python/deeplake/__init__.pyi:551-604` Metadata 类，"Changes are persisted immediately without requiring commit()"——与数据行的 commit 语义分离；典型用法 `ds["images"].metadata["mean"] = [...]` 存预处理统计。
- 版本化写入（`cpp/deeplake_api/dataset.hpp`）：
  - `commit(message)`（:188）、`refresh()`（:193）、`has_uncommitted_changes()`（:211）。
  - 私有成员 `auto_commit_timer_id_` / `last_commit_time_`（:236-237）+ `setup_auto_commit()`（:230）表明存在定时 auto-commit。
  - 异步操作日志：`log_queue_` / `pending_log_writes_` / `log_operation(name, args)`（:240-242）+ `start_logging()`（:249）。
  - 日志条目结构（`cpp/deeplake_api/log_entry.hpp:12-18`）：`{session_id, timestamp(μs), operation, args}`，写路径用 `icm::json`、读路径用 `icm::const_json`（:17）——回放/审计底座。

### 2.2 存储后端与数据模型（chunk engine 深读）

**Chunk 切分策略**（`cpp/deeplake_core/chunk_strategy.hpp`）：
- 两种策略：按行数 `num_rows_chunk_strategy`（:20-51）与按字节 `num_bytes_chunk_strategy`（:53-110）。
- 字节策略默认 **8MB**：`num_bytes_ = 8'000'000L`（:109）；`default_strategy()/default_strategy_for_type()` 对一切类型一律返回 `num_bytes(8'000'000)`（:133-141）。
- 行数估算靠随机采样：`get_single_row_estimated_bytes` 最多随机抽 100 行，用 `dtype_bytes × volume` 求均值再除出每 chunk 行数（:84-106）——对可变长记忆条目比固定行数更稳。

**Datafile 格式族**（`cpp/deeplake_core/chunk_format_definition.hpp` + `datafile_format.hpp`）：
- `datafile_format` 是四格式 variant：`chunk_datafile_format`（v1）、`chunk_datafile_format_v2`、`video_datafile_format`、`chunk_datafile_sequence_format`（datafile_format.hpp:110-115）。
- 工厂入口 `datafile_format::chunk_v1/chunk/video`（datafile_format.hpp:21-31）。
- 每个 chunk 格式持有四级参数：`type_ + chunk_compression_ + sample_compression_ + is_sequence_`（chunk_format_definition.hpp:62-114）——**chunk 级与 sample 级压缩解耦**。
- 压缩率是按 dtype+压缩组合"算"出来的：`compression_ratio()` 调 `impl::calculate_compression_ratio(dtype, sample_compression_, chunk_compression_)`（chunk_format_definition.hpp:102-105）；v2 格式恒为 1.0（:192-195）。
- video 格式硬编码 `return 20.f; // this is a guess based on some articles and chatgpt :D`（:279）——罕见的工程坦诚。
- 列→物理文件映射（`cpp/deeplake/column_datafiles_info.hpp:8-24`）：
  - `insert_datafile_info{filename, offset_start, offset_end}`：新数据追加到新文件。
  - `update_datafile_info{filename, offsets[]}`：**更新不重写整个 chunk，只记录 offsets 补丁文件**。
  - `dataset.hpp:200-201` 的 `get_datafiles()/get_datafiles_report()` 可审计每列物理布局。
- datafile 头（`cpp/deeplake_core/datafile_header.hpp:8-12`）：`{storage::resource_meta meta_, nd::header_info hinfo_}`——物理资源元数据与数组头解耦。

**存储抽象**（`python/deeplake/storage.pyi:26-67`）：
- `Reader`：字节区间读 `get(path, start_bytes, end_bytes)`（:32-34）、异步变体、`length/list/list_iter/list_dirs/subdir`、pickle 支持（`__getstate__/__setstate__`，:30-31）。
- `Writer`：`set/set_async/remove/remove_directory/subdir`（:57-61）。
- 全局并发控制：`concurrency()/set_concurrency(num_threads)`（:90-120）。

**读路径**：`cpp/heimdall/column.hpp:7-21` column 接口只有 `update_row/update_rows/set_metadata/create_index/drop_index`——读写同一对象；`cpp/bifrost/column_streamer.hpp` + `async_prefetcher.hpp` 提供训练循环式流读与预取。

### 2.3 检索策略（TQL + 六种索引）

- 检索入口是 TQL（Tensor Query Language），SQL 方言（`python/deeplake/__init__.pyi:644-755` query() docstring）：
  - 向量：`ORDER BY COSINE_SIMILARITY(vector, ARRAY[...]) DESC`（__init__.pyi:713-717）。
  - 文本：`ORDER BY BM25_SIMILARITY(text, 'machine learning') DESC`（:726-730）。
  - 过滤：`WHERE train_split='train' AND confidence>0.9 AND label IN ('cat','dog')`（:736-742）。
  - 跨数据集 JOIN（:747-753）、MAXSIM（ColPali 多向量，:661）。
  - 参数化批查询：`prepare_query('...WHERE category = ?').run_batch([["active"],["inactive"]])`（:612-642）。
  - `explain_query()` 输出查询计划（:837-866）。
- 执行器（`cpp/tql/executor.hpp:26-108`）：
  - 持有 `hsql::SelectStatement`（hyrise sql-parser，:16-20）与 `heimdall::dataset_view_ptr`，全异步 `async::promise` 管线。
  - 集合运算 UNION/INTERSECT/DIFFERENCE（:91-95）。
  - **查询结果缓存** `query_cache_`：`map<pair<query_string, params>, dataset_view_ptr>`（:107）。
  - 并行度控制 `get/set_max_num_parallel_queries`（:110-111）。
- Top-K 检索中间表示（`cpp/query_core/top_k_search_info.hpp:17-39`）：`{filter_expr, order_expr, k, order_type, search_config}`；批参数版 `top_k_binary_function_search_info` 带 sample 回调（:41-66）。
- 相关 IR 辅件（cpp/query_core/ 目录）：`inverted_index_search_info` / `text_search_info` 分别承载倒排与文本检索的参数面，`search_config.hpp` 为查询配置对象——三种检索路径在 IR 层就已分叉。
- 索引六种，按列创建（`python/deeplake/__init__.pyi:1678-1760` Column.create_index）：
  - `Inverted`（关键词，配 CONTAINS）/ `BM25` / `Exact`（文本与数值）。
  - `Clustered`（嵌入聚类索引，默认）/ `ClusteredQuantized`（量化聚类，"faster, slight accuracy loss"）。
  - `PooledQuantized`（2D token 级嵌入矩阵，配 MAXSIM，即 ColBERT 式迟交互；示例 :1752-1758）。
  - 嵌入索引实现钉在 `cpp/deeplake_core/embedding_index_type.hpp:17-25`：`type::{clustered, clustered_quantized}` + `quantization_type::{none, binary_quantized}`。
- 统计辅助查询计划：`python/deeplake/__init__.pyi:1283-1342` `ColumnStatistics`：min/max、n_distinct、null_frac、most_common_vals/freqs（PG 风格 MCV）、avg_width——`has_statistics/has_mcv/has_numeric_stats` 谓词暗示统计可缺席。

### 2.4 遗忘·整合·演化

- 无 decay/merge/TTL 语义；演化靠 **Git 式版本控制**：
  - branch：`create_branch(name)` / `create_branch(name, version)`（dataset.hpp:92-93）；merge（:96）；`CannotDeleteMainBranchError`（__init__.pyi:28）。
  - tag：`tag(name, version, message)`（dataset.hpp:100）。
  - version/history：`cpp/deeplake_api/version.hpp:26-54`，commit 含**双时间戳**——用户机器时钟（:36-40 注释 "The epoch time the user's machine had when committing"）与存储时钟（:41）。
  - `rebuild_branch` 重建损坏分支（dataset.hpp:130-136，自认"internal dangerous operation...changes the branch ID"）。
  - 只读侧 `checkout(version)`（read_only_dataset.hpp:37）+ `refresh()`（dataset.hpp:193）。
- 操作回放：`cpp/deeplake_api/replay_log.hpp` 存在 + `log_entry.hpp:36-45` 可从 JSON 反序列化——会话级写入日志可重放，是记忆操作审计的底座。

### 2.5 注入上下文的方式（与 Agent 记忆的衔接点）

- 无 prompt 拼装——它是库不是框架。衔接点有三：
  1. **schema 模板**：`TextEmbeddings`（schemas.pyi:11）直接给出 RAG 记忆表骨架，含 chunk_index/document_id 外键式字段。
  2. **TQL 即记忆查询语言**：一次 `deeplake.query()` 可跨 `mem://`/`tmp://`/`s3://` 数据集做向量+BM25 混合检索并 JOIN 元数据。
  3. **训练循环直连**：查询结果 `DatasetView` 可直接 `.pytorch()`（__init__.pyi:720-721）。
- `mem://`（纯内存）与 `tmp://` 路径贯穿全部 docstring 示例（__init__.pyi:196-199、237-239、627-631）——进程内 Agent 记忆与云端数据湖同一 API。
- 异步原语面向管线：`Future.result()/is_completed()/cancel()` + `await`（__init__.pyi:172-303），适合 Agent 主循环不阻塞地预取记忆。

## 3. 关键代码摘录

**① chunk 字节策略默认 8MB + 随机采样估行宽**（`cpp/deeplake_core/chunk_strategy.hpp:84-109`）：
```cpp
int64_t get_single_row_estimated_bytes(const std::ranges::range auto& rows) const
{
    ASSERT(!rows.empty());
    auto sample_count = std::min<std::size_t>(100, rows.size());
    auto& random_number_generator = base::random_engine();
    std::uniform_int_distribution<std::size_t> indices(0, rows.size() - 1);
    int64_t sum = 0;  std::size_t count = 0;
    for (std::size_t i = 0; i < sample_count; ++i) {
        const auto index = indices(random_number_generator);
        const auto volume = rows[index].volume();
        if (volume != 0) { sum += nd::dtype_bytes(rows[index].dtype()) * volume; ++count; }
    }
    if (count > 0) { return sum / count; }
    return nd::dtype_bytes(rows[0].dtype());
}
...
int64_t num_bytes_ = 8'000'000L;
```

**② datafile 格式 variant**（`cpp/deeplake_core/datafile_format.hpp:110-115`）：
```cpp
using data_type = std::variant<std::monostate,
                               chunk_datafile_format,
                               chunk_datafile_format_v2,
                               video_datafile_format,
                               chunk_datafile_sequence_format>;
```

**③ 列物理布局：插入/更新文件补丁模型**（`cpp/deeplake/column_datafiles_info.hpp:8-24`）：
```cpp
struct column_datafiles_info {
    struct insert_datafile_info { std::string filename; int64_t offset_start; int64_t offset_end; };
    struct update_datafile_info { std::string filename; std::vector<int64_t> offsets; };
    std::vector<insert_datafile_info> insert_datafiles;
    std::vector<update_datafile_info> update_datafiles;
};
```

**④ TQL 执行器持有查询缓存与集合运算**（`cpp/tql/executor.hpp:91-107`）：
```cpp
heimdall::dataset_view_ptr union_(...); intersect_(...); difference_(...);
async::promise<heimdall::dataset_view_ptr> apply_order(...);
...
std::map<std::pair<std::string, icm::string_map<>>, heimdall::dataset_view_ptr> query_cache_;
```

**⑤ Agent 记忆 schema 模板签名**（`python/deeplake/schemas.pyi:11-21`）：
```python
def TextEmbeddings(embedding_size: int, quantize: bool = False) -> dict[...]:
    """A schema for storing embedded text from documents.
    This schema includes the following fields:
    - id (uint64), chunk_index (uint16), document_id (uint64),
      date_created (uint64), text_chunk (text),
      embedding (dtype=float32, size=embedding_size)
    """
```

## 4. 基准/评测声明（反虚荣视角）

- README 仅在对比 WebDatasets 时做定性声明"nearly identical streaming speeds... superior random access and shuffling"（README.md:155）[自封][不可复现]，无脚本或数据集。
- 代码内唯一"数字"是 video 压缩率 20x 的注释自嘲（chunk_format_definition.hpp:279 `// this is a guess based on some articles and chatgpt :D`）[自封/玩笑]。
- 无 benchmark 目录、无 eval harness（Taskfile.yml 为构建任务）。
- 可复现性评注：
  - .pyi 存根内嵌大量 `<!-- test-context -->` 可执行示例（如 __init__.pyi:193-202、233-241），疑似供文档测试/CI 使用——API 行为有测试锚，但性能无。
  - ColumnStatistics（__init__.pyi:1283-1342）提供了自查数据分布的手段，用户可自建基准但仓库不提供。

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量）

1. **chunk 级 vs sample 级双压缩轴**（chunk_format_definition.hpp:22-28）：
   - 记忆系统存"文本块+向量"混合负载时，可为不同模态选不同压缩，而非整条记录一个策略。
   - 压缩率按 dtype×压缩组合预先可算（:102-105），写入前即可估存储成本。
2. **更新即补丁文件**（column_datafiles_info.hpp:16-20）：
   - 记忆改写（update memory）不重写 chunk，只追加 offsets 补丁。
   - append-only 心智同样适用于记忆演化日志，天然保留历史。
3. **TQL 把"向量+全文+元数据过滤+JOIN"压进一种 SQL**（__init__.pyi:648-664）：
   - Agent 记忆查询若仍靠多个 SDK 拼装，不如给一层声明式语言。
   - MAXSIM 直接支持多向量迟交互（ColBERT 式）记忆。
   - 参数化批查询 prepare_query().run_batch() 适合记忆批量评估/回放。
4. **版本控制作为记忆演化的原语**：
   - branch/merge/tag/version + 双时间戳 commit（version.hpp:36-41）——记忆回滚与 A/B 对比实验的现成模型。
   - auto-commit 定时器（dataset.hpp:230-237）是"边跑边存档"的参考。
   - 操作日志 log_entry + replay_log 支撑审计与重放（log_entry.hpp:12-46）。
5. **8MB 字节 chunk + 采样估行宽**（chunk_strategy.hpp:84-109）：
   - 对可变长记忆条目（对话片段、文档块）比固定行数 chunk 更稳。
   - 避免一条超长记忆打爆单 chunk。
6. **PG 风格列统计（MCV/n_distinct）暴露给查询计划**（__init__.pyi:1283-1342）：
   - 记忆库做混合检索时，列统计可决定走倒排还是扫描。

## 6. 局限与风险

- **双刃的 C++ 单体**：
  - Python 层不可调试（全部逻辑在编译扩展内），二次开发门槛高。
  - 4.x 重写后与旧版 3.x 生态（LangChain deeplake vector store 等）API 断裂。
- 并发写语义不透明：
  - merge 语义未在头文件暴露冲突解决细节。
  - 多 Agent 并发写同一记忆库的合并行为不可见（仅 rebuild_branch 兜底）。
- 索引黑盒：
  - Clustered 的聚类参数等未在 API 存根暴露（仅 IndexBuildConfig 类型名）。
  - 量化索引的召回损失无量化口径（docstring 只说 "slight accuracy loss"）。
- 生命周期缺失：无遗忘/衰减/TTL，记忆治理完全甩给上层。
- 统计可缺席：schema 演化后旧列统计可能缺失（has_statistics 谓词暗示）。
- 社区门槛：自研基础库（icm/nd/async）规模庞大，贡献者上手成本高。

## 7. 一句话对比 mem0

mem0 给的是"LLM 抽取+更新+检索"的记忆逻辑层，deeplake 给的是记忆逻辑层脚下的存储引擎层——chunk 格式、六种索引、TQL 与 Git 式版本控制；它不做任何记忆决策，却把 mem0 需要外购的底座（向量库+对象存储+版本化）做成了一体。

## 8. 附录：关键文件钉版地图（按本笔记论据源）

**Python API 面（.pyi 存根 = 事实文档）**
- `python/deeplake/__init__.pyi:12-170`：全部导出符号表（可当索引用）
- `python/deeplake/__init__.pyi:172-416`：Future/FutureVoid 异步原语
- `python/deeplake/__init__.pyi:612-755`：prepare_query/query/query_async/explain_query
- `python/deeplake/__init__.pyi:1283-1342`：ColumnStatistics（MCV/n_distinct/null_frac）
- `python/deeplake/__init__.pyi:1678-1841`：create_index/drop_index 六种索引全文档
- `python/deeplake/storage.pyi:26-120`：Reader/Writer/concurrency
- `python/deeplake/schemas.pyi:11-131`：TextEmbeddings / COCOImages 模板
- `python/deeplake/core.py:1-3` / `storage.py:1-3` / `schemas.py:1-7`：薄壳证明

**C++ 存储格式层（chunk engine）**
- `cpp/deeplake_core/chunk_strategy.hpp:20-51`：按行数策略
- `cpp/deeplake_core/chunk_strategy.hpp:53-110`：按字节策略（默认 8MB、采样估算）
- `cpp/deeplake_core/chunk_strategy.hpp:133-141`：default_strategy 恒 8MB
- `cpp/deeplake_core/chunk_format_definition.hpp:19-60`：chunk_format_definition（双压缩轴）
- `cpp/deeplake_core/chunk_format_definition.hpp:62-201`：v1/v2/sequence 三种 chunk 格式
- `cpp/deeplake_core/chunk_format_definition.hpp:241-287`：video 格式（20x 玩笑注释在 :279）
- `cpp/deeplake_core/datafile_format.hpp:16-116`：格式工厂与 variant
- `cpp/deeplake_core/datafile_header.hpp:8-12`：datafile 头
- `cpp/deeplake_core/embedding_index_type.hpp:12-80`：嵌入索引类型（clustered/quantized）

**C++ 查询层**
- `cpp/tql/executor.hpp:26-111`：执行器、集合运算、query_cache_、并行度
- `cpp/query_core/top_k_search_info.hpp:17-66`：Top-K IR 与批参数变体
- `cpp/query_core/`（目录）：expr/functor/group_statement/inverted_index_search_info/text_search_info/search_config

**C++ 基础库（只读关键件）**
- `cpp/icm/trie.hpp` + `cpp/icm/roaring.hpp`：倒排/BM25 索引的底层结构（trie 词项 + roaring 位图 postings）
- `cpp/nd/impl/`（目录 40+ 数组实现）：lazy/strided/transformed 数组支撑零拷贝列视图
- `cpp/async/promise.hpp`：全引擎异步原语（Python Future 的来源）
- `cpp/storage/reader.hpp / writer.hpp / provider_base.hpp`：多云 provider 抽象
- `cpp/deeplake_pg/`：Postgres 后端变体（与文件/对象存储后端并列）
- `cpp/bifrost/column_streamer.hpp / async_prefetcher.hpp`：流式读与预取（训练循环入口）

**C++ API 与版本控制**
- `cpp/deeplake_api/dataset.hpp:180-249`：commit/refresh/auto-commit/log_operation
- `cpp/deeplake_api/log_entry.hpp:12-46`：操作日志条目与序列化
- `cpp/deeplake_api/version.hpp:26-54`：双时间戳 version
- `cpp/deeplake_api/read_only_dataset.hpp:33-98`：checkout 只读面
- `cpp/deeplake/column_datafiles_info.hpp:8-24`：列物理布局（插入/更新补丁）
- `cpp/heimdall/column.hpp:7-21`：列写接口（update_row/create_index）
