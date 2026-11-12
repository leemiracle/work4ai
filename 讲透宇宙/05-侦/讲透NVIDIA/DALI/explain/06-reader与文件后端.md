# 06 · reader 与文件后端：DataReader 模板基类、loader/parser 家族与 FileStream 多后端

## 角色定位

图谱 L08「数据读取与文件后端」（141 节点/124 文件）是数据入口子系统：operators/reader 一侧是"reader 算子=DataReader 模板基类+loader 家族+parser 家族"三层；dali/util 一侧是 FileStream 多后端文件抽象（本地 mmap/std/odirect、S3/GCS 云、GDS 直存）与格式工具（numpy/fits/image/ocv/nvml）。分工哲学一句话：reader_op.h 用约 500 行模板重基类把 loader 生命周期与 DALI 管线执行模型（prefetch/epoch）解耦（NOTES batch-15），Loader 只回答"第 i 个样本怎么读"，文件怎么打开全交给 util 层。

## 内部结构

`DataReader`（reader_op.h:55-57，template<Backend, LoadTarget>）在构造时读 prefetch_queue_depth 参数（:64）并建环形预取队列（:66）；预取循环带 NVTX DomainTimeRange 标注（:94），支持 loader checkpoint 快照 SaveLoaderSnapshot/LoaderStateSnapshot 序列化往返（reader_op.h:103/126-138）；独立预取线程 PrefetchWorker 由互斥锁保护启停（:141-163）。`Loader` 基类（loader.h:67）管分片与游标：ctor 从 options 取 shard_id/num_shards/stick_to_shard（:84-88）并校验（:98）；两阶段初始化的注释写明原因——重写的 PrepareMetadata 不能在基类构造期虚派发（loader.h:112-116）；epoch 耗尽判定看 shards_ 前端游标（:148-153）；跨 shard 补齐到满 batch 的规则在 :208-215（returned_sample_counter_ 与 num_samples(num_shards_, Size()) 对齐，保证每 epoch 样本/批数一致）；纯虚三件套 ReadSample（:355）/PrepareMetadataImpl（:411）/Reset(wrap_to_shard)（:419），取样路径按条件选 ReadSample(*tensor_ptr) 或 Skip() 并推进计数（:248-254/:321-326/:443）。FileLoader（file_loader.h:43-45）是通用骨架：file_filter 参数（:49）→ file_discovery_opts_（:63），并强制 shuffle_after_epoch 与 stick_to_shard 互斥（:94-99）。Parser 层极薄：`Parser<ParseTarget>` 只有纯虚 Parse(data, SampleWorkspace*)（parser.h:29-40），TFRecordParser 读 feature_names/features 对（tfrecord_parser.h:35-47）并校验 CRC（:54）。文件后端单入口 `FileStream::Open`（file.cc:35）：s3://→S3FileStream、gs://→GCSFileStream（各带编译期开关 AWSSDK_ENABLED/GCS_ENABLED 与 ClientManager 单例，file.cc:37-52）；本地剥 file:// 前缀后按 Options{read_ahead,use_mmap,use_odirect}（file.h:76-80）三选一 MmapedFileStream/ODirectFileStream/StdFileStream（file.cc:64-70）。FileStream 基类（file.h:31）带 RAII MappingReserver 管理 mmap 配额（file.h:33-70）；URI 解析用 string_view 零拷贝切 scheme（uri.h:28-88）。构建侧的 dummy 占位家族也在这层语境里：dali/kernels/dummy.cu 是空文件，头注释明示用意——老 CMake 在 CMAKE_CUDA_RESOLVE_DEVICE_SYMBOLS=ON 时仍用 Clang 链接，此文件强制走 NVCC 以完成 separable compilation 的 device linking（kernels/dummy.cu:15-18，NOTES batch-56）；同族还有 dali/core/dummy.cc（对齐 thread_local 符号的链接期 workaround，NOTES batch-39）与 pipeline/util/python_function/test 各处的 dummy.cc——全仓共 9 个 dummy 文件，都是链接器属性占位。

## 外部连接

上游：executor/pipeline 调度 reader 的预取（DataReader 继承 Operator<Backend>），checkpoint 体系直接挂 LoaderStateSnapshot。文件后端被全部 loader 共用：FileLoader/COCO/WebDataset/numpy/recordio/fits 都开 FileStream；GDS 路径的 CUFileStream 同样是 FileStream 子类（接 L03 篇）。云发现走 discover_files_{s3,gcs}.cc 与 s3/gcs_filesystem.cc；webdataset 的 tar 访问经 libtar 封装（tar_utils.h:18 include，:31 注释"通过给定 FileStream 访问 .tar"）；nvml_wrap.cc 是 dlopen 弱依赖范式样板（nvml_wrap.cc:35-41 两次 dlopen，符号缓存 mutex+unordered_map :80-81，NOTES batch-78）。GPU 直读支线：numpy_reader_gpu_op+numpy_loader_gpu 与 fits_reader_gpu_op 把文件读成设备张量。

## 数据流

一次迭代：reader op 构造 → Loader 两阶段初始化（PrepareMetadata 扫目录/索引，FileLoader 经 discover_files 列文件）→ PrefetchWorker 线程循环 ReadIndexedSample：游标有效则 ReadSample、否则 Skip，样本入 prefetched_batch_queue_ → 管线拉取 → Parser.Parse 把原始字节拆成 (image, label) 等结构 → 下游解码算子。epoch 结束 Reset(wrap_to_shard) 回卷游标，可选 shuffle_after_epoch。

## 设计决策

1. 三层解耦（DataReader 管执行/Loader 管样本/Parser 管格式）：新增数据源只需 Loader+Parser，预取/分片/checkpoint 全部继承。
2. 两阶段初始化是对 C++ 虚函数构造期语义的显式妥协（loader.h:112-116 注释自证）。
3. 分片补齐策略在基类实现：多 shard 每 epoch 样本数一致比"精确均分"更重要（loader.h:208-215）。
4. 单 URI 入口+编译期云开关：s3/gcs 支持不绑架默认构建，报错文案直接指路（file.cc:41/50）。
5. MappingReserver RAII：mmap 句柄是全进程配额（vm.max_map_count），预取越深越要先预约（file.h:33-70）。
6. dummy 占位家族：用空翻译单元控制链接器行为（NVCC device link/thread_local 对齐），是"构建系统没法表达的事放进源码树"的样板。

## 新人提示

加新 reader 的固定四步：写 Loader 子类（实现 ReadSample/Reset/PrepareMetadataImpl）→ 视情况写 Parser → 用 DataReader 模板实例化 op 并 DALI_SCHEMA 注册 → 抄 file_reader_op.cc 骨架。IO 问题断点在 file.cc:35（所有路径都过这里）；云存储报"not built with ... support"是编译开关问题不是路径问题。分片行为对拍用 reader_op_test.cc 与 filesystem_test.cc；mmap 相关问题先看 MappingReserver 是否把配额占满。看懂 dummy.* 别当死代码——动 CMake 链接配置前先确认这些占位还有没有用（kernels/dummy.cu 注释对应的老 CMake 行为）。查预取卡顿优先 DomainTimeRange 的 NVTX 记录（reader_op.h:94）。
