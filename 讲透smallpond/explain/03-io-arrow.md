# smallpond/io/arrow.py 精讲——Parquet 与 3FS 之间的 IO 核心

> 原文件：`smallpond/smallpond/io/arrow.py`（368 行）

## 一、角色定位

arrow.py 是 smallpond 所有列存数据的进出咽喉：把 parquet 文件（通常躺在 3FS 挂载上）读成 Arrow 流/表、把内存里的 Arrow Table 切成合适数量的 parquet 文件写回去。它不关心调度与计划，只解决三件纯 IO 问题：**怎么切（RowRange）、怎么保证 PB 级不溢出（large 类型）、怎么并行（线程池分治）**。GraySort 110.5TiB/30min 的成绩背后，读写路径的每一个字节都经过这里。

## 二、内部结构

- **RowRange dataclass**：`path/data_size/file_num_rows/begin/end` 五字段，派生 `num_rows` 与 `estimated_data_size`（按文件字节数比例折算行区间字节数）；`take(num_rows)` 从头部截取并前移自身 begin（破坏性操作）；`partition_by_rows()` 静态方法把一组 RowRange 均分成 n 份（每份按剩余均分公式 `(num_rows + k - 1) // k` 取整）。
- **类型层**：`convert_type_to_large` 递归地把 string/binary 及 List/Struct/Map 容器内的同类型换成 large 版本；`convert_types_to_large_string`/`cast_columns_to_large_string` 作用在 schema/table 上。
- **读路径四层**：`_iter_record_batches`（单文件内按 batch 与目标区间的交集 slice）→ `_iter_record_batches_from_files`（跨文件缓冲拼接，batch_size 与 max_batch_byte_size 双闸门，`combine_buffered_batches` 用 `combine_chunks().to_batches()` 重切齐整）→ `build_batch_reader_from_files`（首文件读 schema，包成 `arrow.RecordBatchReader.from_batches`）→ `read_parquet_files_into_table`。
- **并行层**：`load_from_parquet_files` 用 ThreadPoolExecutor（默认 max_workers=16）+ `split_into_rows` 均分文件，各线程独立读表后 `arrow.concat_tables`。
- **写路径**：`parquet_write_table`（本地写时 `open(..., buffering=32*MB)` 大缓冲）；`dump_to_parquet_files`（自适应行组 + 按总字节定文件数 + 线程池并行写）。

## 三、外部连接

最大用户是 logical/dataset.py：ParquetDataSet 的 `to_batch_reader()/to_arrow_table()` 直接转调这里的读函数；CsvDataSet/JsonDataSet 等在产出 parquet 中间件后也走同一出口。执行侧被 task.py 的 ArrowStreamTask、HashPartitionArrowTask、DataSinkTask 调用做中间数据落盘。`filesystem: fsspec.AbstractFileSystem` 参数是通往 3FS 的门：上层传入 hf3fs 的 fsspec 实现后，所有 `unstrip_protocol` 分支生效；不传则纯本地路径。常量 `DEFAULT_BATCH_SIZE/MAX_PARQUET_FILE_BYTES/DEFAULT_ROW_GROUP_*` 来自 smallpond/common.py。

## 四、数据流

读：`paths_or_ranges`（整文件路径或 RowRange 列表）→ `parquet.ParquetFile(path, buffer_size=16MB)` → `iter_batches(batch_size, columns, use_threads=False)` 顺序吐 batch → 与 `[offset, offset+length)` 求交集裁剪 → `cast_columns_to_large_string` → 缓冲到目标尺寸统一吐出 → RecordBatchReader 零拷贝流（下游 UDF 按批消费）。

写：arrow Table → 强转 large 类型 → `avg_row_size = nbytes // num_rows` → `row_group_size = min(row_group_bytes // avg_row_size, row_group_size)` 自适应 → `table.to_batches(max_chunksize=row_group_size)` → 文件数 = `max(ceil(nbytes / MAX_PARQUET_FILE_BYTES), num_workers)` → `split_into_rows` 均分 batch 进文件 → 并行 `parquet_write_table`（`write_batch_size` 与 `data_page_size` 均按行组大小 1/8 折算）。空表有专门分支：warning 后写一个 0 行 parquet 保住 schema。

## 五、设计决策

- **强制 large_string/large_binary**：源码注释直指 ARROW-17828——Arrow 32 位偏移在单列 2GB 处溢出。PB 级数据下这不是理论风险，是必炸的墙；在 IO 层一次性递归转换，让上层永远只见 large 类型。
- **RowRange 而非文件级切分**：按行区间（而非整文件）描述数据片，`partition_by_rows` 才能做到"按行数均分负载"——EvenlyDistributedPartitionNode 的 by_rows 模式正建立在这上面。
- **文件间并行、文件内串行**：`use_threads=False` 关掉 pyarrow 内部多线程，并行度放在 ThreadPoolExecutor 对多文件的分治上——海量小文件场景下避免线程争抢反而更稳。
- **行组自适应**：先按平均行字节把 row_group_bytes 换算成行数上限，再与行数上限取小——兼顾压缩率（大行组）与谓词下推过滤并发（小行组），与 DuckDB 官方 parquet tips 的建议一一对应。
- **写缓冲显式放大**：32MB Python 层缓冲 + 16MB pyarrow buffer_size，针对高延迟分布式文件系统（3FS）减少小 IO 往返。

## 六、新人提示

`take()` 与 `partition_by_rows()` 有修改/深拷贝语义，注释里都有 NOTE，链式调用前想清楚所有权。排"某文件缺列"问题时直接抄 `_read_schema_from_file` 报错信息里给的 duckdb 查询（它能列出目录下所有缺列文件）。在 3FS 上调优时优先看两个数：MAX_PARQUET_FILE_BYTES 决定文件粒度，行组参数决定下游扫描并发。`load_from_parquet_files` 的 max_workers=16 是软上限（min(文件数, 16)），小文件多时可考虑调大。

fsspec 适配注意两点：所有函数对 `filesystem` 参数只做 `unstrip_protocol(path)` 一层处理，因此传入的 fsspec 实例必须自行缓存连接（hf3fs 的 fsspec 包装即如此）；同一函数里本地路径与带协议路径不可混用（要么全走 filesystem 分支，要么全走裸路径）。`_iter_record_batches` 的 `use_threads=False` 是刻意选择——若单文件巨大且文件数少，可在调用层换 `parquet.ParquetFile.read` 全量路径再自行分批，但常规分布式场景维持现状即可。
