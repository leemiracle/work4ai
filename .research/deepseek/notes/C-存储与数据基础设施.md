# DeepSeek 存储与数据基础设施三仓研究笔记（3FS / smallpond / open-infra-index）

> 研究型代码考古笔记。基础目录：`C:\workspace\work4ai\.tools\deepseek-repos\`。
> 诚实约束：所有数字均来自本仓库实际读到的文件（README / docs/design_notes.md / docs/metrics.md / deploy/README.md / 源码头文件）。任务提示中的 "batch load / file insight 运维工具" 与 "DPDK 使用" 在本仓库中**未找到对应物**，下文如实说明，不编造。

---

## 0. 三仓总览

| 仓库 | 语言/规模 | 一句话定位 |
|---|---|---|
| 3FS (Fire-Flyer File System) | C++/Rust，src/ 下 313 个 .cc + 509 个 .h，全仓 1288 文件 | 面向 AI 训练/推理负载的高性能分布式文件系统：解耦架构 + CRAQ 强一致 + RDMA/SSD 全带宽利用 |
| smallpond | Python（60 个 .py），MIT | 基于 DuckDB + 3FS 的轻量分布式数据处理框架：无常驻服务、PB 级数据 |
| open-infra-index | Markdown 索引 | DeepSeek 开源 infra 的总索引：开源周 Day1-6 全景 + 两篇系统论文 + 推理系统披露数据 |

三者关系：3FS 是存储底座（Day 5 "Thruster for All DeepSeek Data Access"）；smallpond 是 3FS 之上的数据处理层（GraySort 即二者联合跑出的成绩）；open-infra-index 把 3FS/smallpond 放进 DeepEP/DeepGEMM/FlashMLA 等全套 infra 版图。

---

## 1. 3FS（Fire-Flyer File System，2025-02 开源周 Day 5）

### 1.1 定位一句话
用"解耦（disaggregated）架构 + CRAQ 链式复制 + 无状态元数据 + RDMA 直达"榨干数千块 SSD 与数百存储节点的聚合带宽，让上层应用以 locality-oblivious 方式共享存储，同时保留文件系统语义（来源：`README.md`、`docs/design_notes.md`）。

### 1.2 四组件架构（`docs/design_notes.md` §Design and implementation）
1. **cluster manager（mgmtd）**：所有服务向其心跳；处理成员变更、分发集群配置。多实例部署选主，主故障自动提升。生产环境配置存在与文件元数据同一个事务 KV（FoundationDB）里以减少依赖。
2. **metadata service（meta）**：实现文件系统语义，**无状态**——元数据全部存 FoundationDB（SSI 可序列化快照隔离事务），客户端可连任意实例，实例挂了自动切换。
3. **storage service（storage）**：每服务管理若干本地 SSD，提供 chunk store 接口，实现 CRAQ（Chain Replication with Apportioned Queries）保证强一致。
4. **client**：FUSE 客户端（低门槛）+ native 客户端（性能关键路径，异步零拷贝 USRBIO）。
全组件跑在同一张 RDMA 网（InfiniBand 或 RoCE）上。

### 1.3 关键数字（全部来自实际读到的文件）
- **峰值吞吐**：180 存储节点（每节点 2×200Gbps IB + 16×14TiB NVMe SSD），500+ 客户端节点（各 1×200Gbps IB）读压测，**聚合读吞吐 ~6.6 TiB/s**，且带训练背景流量（`README.md` §Performance 1）。
- **GraySort**：25 存储节点（2 NUMA 域/节点、每 NUMA 一个存储服务、2×400Gbps NIC）+ 50 计算节点（2 NUMA、192 物理核、2.2 TiB 内存、1×200Gbps NIC），**110.5 TiB 数据、8192 分区、30 分 14 秒排完 = 平均 3.66 TiB/min**（`README.md` §Performance 2）。
- **KVCache**：单客户端节点（1×400Gbps NIC）读吞吐**峰值 40 GiB/s**；同期 GC 删除 IOPS 见 `docs/images/kvcache_gc_iops.png`（`README.md` §Performance 3）。
- **FUSE 天花板**：实测 FUSE 只能处理 ~**400K 次/秒的 4KiB 读**，再加并发因自旋锁争用不升反降（`docs/design_notes.md` §Limitations of FUSE，perf 定位到内核态自旋锁）。
- **生产条带**：stripe size = **200**；小文件链数提示从 16 起步、每扩一次翻倍（`docs/design_notes.md` §Dynamic file attributes）。
- **测试集群部署参数**（`deploy/README.md`）：6 节点，chunk size 1MiB（init-cluster 参数 1048576）、stripe 16；存储盘 XFS 格式化挂载、`fs.aio-max-nr=67108864`；数据放置 5 节点 × 16 SSD × 每 SSD 6 target，3 副本。

### 1.4 核心机制（文件路径 + 类/函数）

**A. CRAQ 链式复制（`docs/design_notes.md` §Data replication + §Data placement）**
- 写请求发 head，沿链传播；**写全部、读任意**（write-all-read-any），读流量均匀分摊到链上所有 target——这是全闪存系统榨干读带宽的关键。
- 每个 chunk 存两个版本：committed（v）与 pending（u=v+1），版本号单调递增；tail 提交后 ack 沿链回传。
- 与教科书 CRAQ 的差异：**不做 tail 版本查询**。读到 committed/pending 并存时返回特殊状态码，客户端稍候重试或发 relaxed read 读 pending 版本（`docs/design_notes.md` 读流程第 2 步）。
- 链表（chain table）带版本号，只有 primary cluster manager 能改；可建多张链表隔离批处理/在线业务（target 与 SSD 互斥）。
- 源码：`src/storage/service/StorageService.h`（`class StorageService : public serde::ServiceWrapper`，batchRead/write/update/queryLastChunk/truncateChunks/removeChunks/syncStart/syncDone 等协程接口，`CoTryTask<WriteRsp> write(...)`）；转发/更新可靠性在 `src/storage/service/ReliableForwarding.cc`、`ReliableUpdate.cc`。

**B. 故障检测与恢复（`docs/design_notes.md` §Failure detection/§Data recovery）**
- 心跳即租约：T 秒无心跳判失败；服务侧 T/2 秒联系不上 manager 自杀退出。
- target 双状态机：**public state**（serving/syncing/waiting/lastsrv/offline，随链表广播）+ **local state**（up-to-date/online/offline，仅在 manager 内存）；manager 周期性按状态转移表扫描每条链更新 public state；offline target 移到链尾；发现自己是 lastsrv/offline 立即退出（防脑裂/网络分区）。
- 恢复 = 前驱向后继持续发 **full-chunk-replace 写** + dump-chunkmeta 元数据比对（按链版本号与 committed 版本号决定哪些 chunk 要传/删）；sync-done 后回 up-to-date。恢复与正常流量重叠。
- 源码：`src/storage/sync/ResyncWorker.cc`、`src/storage/worker/{DumpWorker,CheckWorker,SyncMetaKvWorker,PunchHoleWorker,AllocateWorker}`。

**C. 元数据：FoundationDB 事务 KV（`docs/design_notes.md` §File metadata store + `src/meta/`）**
- inode：全局唯一 64 位单调 ID；key = `"INOD" + inode id`（小端编码让 inode 均匀散布到多个 FDB 节点）；value 按类型（文件含 length/chunk size/链表选择范围/shuffle seed；目录含父 inode id 与子目录默认 layout；symlink 含目标路径）。目录项 key = `"DENT" + 父 inode id + entry name`，天然连续 key range → range scan 高效 readdir。
- 写事务靠 FDB 冲突检测集 + 自动重试，使多个 meta 服务并行仍保持一致。
- 不追踪只读 fd（训练任务开海量文件，省元数据负载）；写打开的 fd 记 file session，删除延迟到全部 fd 关闭；客户端每 **5 秒**上报写文件最大写位置，元数据侧用 inode id 的 rendezvous hash 把长度更新分摊到不同 meta 服务。
- 源码：`src/meta/store/Inode.h`（`class Inode`，`packKey/snapshotLoad/store/loadAncestors` 等 `CoTryTask` 方法，`snapshotLoad` 不加入读冲突集）、`src/meta/store/DirEntry.h`、`src/meta/components/SessionManager.h`、`src/meta/components/GcManager.h`（GC 条目格式 `prefix-timestamp-inode`）、`src/meta/components/ChainAllocator.h`（建文件时 round-robin 选连续链 + 随机 seed shuffle 保证均衡）、`src/meta/ops/`（Open/Remove/Rename/Mkdirs 等操作，均走 FDB 事务）。
- KV 抽象：`src/common/kv/IKVEngine.h` + `src/fdb/FDBKVEngine.h`、`HybridKvEngine.h`（FDB/内存 KV 可切换，供测试）、`src/kv/{RocksDBStore,LevelDBStore,MemDBStore}`。

**D. chunk 存储引擎（两代实现并存，均实读到）**
- 旧 C++ 版（`docs/design_notes.md` §Chunks and the metadata + `src/storage/store/ChunkEngine.cc`）：每 SSD = 固定数量数据文件 + RocksDB 元数据 + 内存 hashmap 缓存；COW 写（新分配块→读旧块→应用更新→写新块→RocksDB WriteBatch 原子提交）；物理块 **64KiB–64MiB 共 11 档**，每档一个资源池、每池 **256 个物理文件**，位图管理，回收块优先复用，耗尽时 `fallocate()` 一次性再扩 256 块以减少碎片；append 有 in-place 优化。
- 新 **Rust 版**（`src/storage/chunk_engine/`，`Cargo.toml` + `src/lib.rs`，workspace 见根 `Cargo.toml`）：
  - Allocator/MetaStore 两分：内存先分配、后持久化（失败丢失无影响）；回收先落盘再改内存，`Arc<ChunkPos>` 引用计数保证并发读写/删除无冲突。
  - 层级：chunk(64KB/512KB/4MB) → group(256 chunks，即 16MB/128MB/1GB) → file(~120GB≈960 groups) → disk(30TB=每档 256 files) → node(10–20 盘)；**单机可支撑 ~12 亿 chunk、~500 万 group**（`chunk_engine/README.md`）。
  - 256-bit bitset（4×uint64）+ `__builtin_ctz` 快速找空位；`allocate_thread` 维持 active_groups 水位、`compact_thread` 周期迁移整 group 回收空间。
  - MetaStore 三映射：chunk_id→meta（derse 序列化）、group_id→state（RocksDB MergeOp 原子更新）、chunk_pos→chunk_id（compaction 用）。

**E. 客户端：FUSE + USRBIO 异步零拷贝（`src/lib/api/UsrbIo.md` + `src/fuse/`）**
- native client 内嵌在 FUSE daemon 中：元数据操作仍走 POSIX（open/close/stat），I/O 走共享内存 API。
- **Iov**：大块用户↔FUSE 共享内存，IB 内存注册由 FUSE 进程统一管理；**Ior**：io_uring 式小环形队列，用户入队、FUSE 出队，`io_depth` 控制成批下发（多批并行）；fd 需 `hf3fs_reg_fd` 注册。核心函数：`hf3fs_iorcreate4 / hf3fs_iovcreate / hf3fs_prep_io / hf3fs_submit_ios / hf3fs_wait_for_ios`（`src/lib/api/hf3fs_usrbio.h`，实现于 `src/lib/api/UsrbIo.cc`）。
- FUSE 侧实现：`src/fuse/IoRing.h`（`class IoRing`）、`IovTable.h`、`PioV.h`（`class PioV`：把用户读写聚合成 chunk 级批量 I/O，`addRead/addWrite/executeRead/executeWrite/chunkIo`）、`FuseApplication.h`（`class FuseApplication : public ApplicationBase`）；`FuseConfig.h` 关键热更配置：`batch_io_coros=128`、`rdma_buf_pool_size=1024`、`max_readahead=16_MB`、`io_jobq_size=1024` 等。
- 客户端读写路径：`src/client/storage/StorageClientImpl.cc`（批量读）+ `TargetSelection.h`（读 target 选择策略：LoadBalance/RoundRobin/Random/Tail/Head/Manual，支持 traffic zone 隔离）+ `UpdateChannelAllocator.h`（写通道号分配，storage 服务按 channel id 去重 update 去重幂等）。
- RDMA 栈：`src/common/net/`（`Transport/TransportPool/IOWorker/EventLoop/RDMAControl` 等，IB socket 封装）；**未发现 DPDK 代码**——网络层以 InfiniBand verbs/RoCE 为主。

**F. 数据放置 = 整数规划问题（`deploy/data_placement/`）**
- 恢复期流量均衡被形式化为 **balanced incomplete block design（BIBD）**，用 **Pyomo 建模 + HiGHS 求解器**求最优链表（`deploy/data_placement/README.md`：v_5-b_10-r_6-k_3-λ_2 解，min_peer_traffic=max_peer_traffic=1.5 完全均衡）；`gen_chain_table.py` 生成 create_target / upload-chains / upload-chain-table 的 admin_cli 命令序列。
- 设计洞察：朴素链表下 A 盘故障其读流量全部压到链上另两副本 → B/C 立刻饱和；让 A 与其余每块 SSD 都配对过，故障流量被 1/(N-1) 摊薄。

**G. 运维与可观测**
- **admin_cli**（`src/client/admin/`，60+ 命令，每命令一文件）：init-cluster / user-add / create-targets / upload-chains / upload-chain-table / list-chains / list-targets / dump-chains / dump-inodes / dump-chunk-meta / find-orphaned-chunks / offline-target / remove-chunks / prune-session / set-config（配置统一由 mgmtd 管理热更）/ read-bench 等。
- **回收站体系**：`hf3fs_utils/`（hf3fs_cli：`rmtree --expire [1h|3h|8h|1d|3d|7d]` 把目录移入 `/{mountpoint}/trash/{user}`，可恢复）+ Rust 写的 `src/client/trash_cleaner/`（周期清理过期回收站）。
- **监控**：各服务埋点 → monitor_collector → **ClickHouse**（表 `3fs.counters` / `3fs.distributions`；四种 recorder：value/count/distribution/latency，见 `docs/metrics.md`，示例 `fuse.write.latency`、`storage.chunk_engine.copy_on_write_times`、`storage.target_state` 等 80+ 指标）。
- **基准工具**：`benchmarks/fio_usrbio/`（fio 外置引擎插件 hf3fs_usrbio.so，支持 batch 参数）；`benchmarks/storage_bench/StorageBench.cc`（存储服务直连压测）。
- Python 客户端：`hf3fs/`（`hf3fs_py_usrbio` 的 Client 封装：open/preadv/pwritev/walk/scandir/BinaryFile，支持多挂载点与 token）+ `hf3fs_fuse/`。
- 未找到名为 "batch load" 或 "file insight" 的工具（任务提示与仓库实际不符，实际对应物为 admin_cli 批处理命令集与 fio/storage_bench 基准）。

### 1.5 源码模块地图（`src/` 实测目录树 + 职责；括号为 .cc/.h 文件数）
```
src/
├── common/        (242) 基础库（相当于其他系统的 foundation 层）
│   ├── app/     ApplicationBase/OnePhaseApplication/TwoPhaseApplication/ConfigManager——服务生命周期与配置热更框架
│   ├── net/     Transport/TransportPool/IOWorker/EventLoop/RDMAControl/ThreadPoolGroup——自研 RDMA(verbs) 网络栈
│   ├── kv/      IKVEngine/ITransaction/WithTransaction/KeyPrefix——KV 引擎抽象（FDB/RocksDB/LevelDB/MemDB 可插拔）
│   ├── utils/   Coroutine(C++20 协程)/CoroutinesPool/PriorityCoroutinePool/RobinHood/LruCache/Shuffle 等 150+ 工具
│   ├── monitor/ ValueRecorder/CountRecorder/DistributionRecorder/LatencyRecorder 指标
│   ├── serde/   序列化 + ServiceWrapper 服务框架（RDMA 上跑的 RPC）
│   └── logging/
├── core/          (32)  mgmtd/meta/storage 共用的基础组件（README："base component of mgmtd, meta, storage"）
├── fbs/           (56)  FlatBuffers 生成的 schema（storage/meta/mgmt 协议结构）
├── fdb/           (13)  FoundationDB 接入：FDBContext/FDBTransaction/HybridKvEngine（FDB↔内存 KV 切换）
├── kv/            (9)   RocksDBStore/LevelDBStore/MemDBStore 通用 KV 实现
├── mgmtd/         (98)  集群管理器：链表/节点/target 状态机、选主、配置分发（MgmtdServer.h 等）
├── meta/          (55)  元数据服务：store/(Inode,DirEntry,MetaStore,FileSession) + ops/(Open,Remove,Rename…)
│                       + components/(ChainAllocator,SessionManager,GcManager) + event/(Scan)
├── storage/       (59)  存储服务：
│   ├── service/  StorageServer/StorageService/StorageOperator/ReliableForwarding/ReliableUpdate/TargetMap
│   ├── store/    ChunkEngine(C++版)/ChunkFileStore/ChunkReplica/StorageTarget(s)
│   ├── chunk_engine/  ★Rust 重写的 chunk 引擎（alloc/core/file/meta/types，cxx 桥接）
│   ├── aio/     AioReadWorker/BatchReadJob（libaio 批量读）
│   ├── sync/    ResyncWorker（故障恢复数据同步）
│   └── worker/  Allocate/Check/Dump/PunchHole/SyncMetaKv 后台 worker
├── client/        (178) 客户端库：
│   ├── core/CoreClient.h、meta/MetaClient、mgmtd/MgmtdClient+RoutingInfo（路由信息缓存）
│   ├── storage/  StorageClientImpl/StorageMessenger/TargetSelection/UpdateChannelAllocator
│   ├── admin/    admin_cli 全部命令
│   └── trash_cleaner/ ★Rust 回收站清理器
├── fuse/          (24)  FUSE 客户端：FuseApplication/FuseOps/IoRing/IovTable/PioV
├── lib/           (11)  对外 API 库：api/(hf3fs_usrbio.h, UsrbIo.cc, fuse.h)、py/(pybind11 绑定 hf3fs_py_usrbio)、
│                       rs/(hf3fs-usrbio-sys Rust FFI)
├── analytics/     (7)   结构化 trace（SerdeObjectReader/Writer/SchemaBuilder）
├── monitor_collector/(7) 指标收集服务（TCP 收集→ClickHouse）
├── memory/ (9) migration/ (5) simple_example/ (5) stubs/ (14) tools/ (6，admin/set-layout 工具)
```
Rust workspace（根 `Cargo.toml`）：`src/client/trash_cleaner`、`src/storage/chunk_engine`、`src/lib/rs/hf3fs-usrbio-sys`；rust-version 1.85，release-cmake profile 开 LTO。

### 1.6 工程亮点
1. **协议形式化验证**：`specs/` 用微软 **P 语言**对 CRAQ/DataStorage 建模并跑模型检查（`specs/README.md`：tcOneClientWriteNoFailure/tcTwoClientsWriteWithFailures 等 10 组测试全 pass，RunTests.ps1 汇总）——分布式一致性协议用专用形式化工具验证，罕见的工程投入。
2. **C++/Rust 混合演进**：chunk 引擎与回收站清理器用 Rust 重写，cxx/cbindgs 桥接进 CMake 构建；同仓维护 C++/Rust 双实现。
3. **编译器兼容性当作集群协议对待**：`std::shuffle` 在 g++10/g++11 行为不同会导致二进制不兼容，故 CMake 强制 `-DSHUFFLE_METHOD=g++10|g++11|stdshuffle` 锁死洗牌算法（`README.md` + 根 `CMakeLists.txt`）。
4. **测试规模**：`tests/` 153 个 gtest .cc（net/RDMA echo、serde、FDB 事务、chunk engine、meta ops、mgmtd cluster 全覆盖），配 gtest-parallel 并行跑。
5. **配置集中治理**：所有服务/客户端 `*_main.toml` 由 mgmtd 统一管理，admin_cli `set-config` + `hot-update-config` 热更新；launcher/app 双层 toml 分离部署态与运行态。
6. **CI**（`.github/workflows/build.yml`）：self-hosted runner，clang-14 + RelWithDebInfo + FDB 7.1.61 client + libfuse 3.16.2 源码编译，cargo build --release 先行。
7. **部署物**：systemd unit（`deploy/systemd/`）+ docker 构建镜像（TencentOS-4 / OpenCloudOS-9 专用 build 镜像）；依赖列表覆盖 Ubuntu 20.04/22.04、openEuler、OpenCloudOS/TencentOS——多国产 OS 适配痕迹。
8. **监控选型**：不用 Prometheus 而用 **ClickHouse** 存全量指标（counters/distributions 双表，latency 以 ns 记录出 P90/P99）。

### 1.7 work4ai 输入
- **讲透分布式AI系统**：3FS 是"存算分离 + RDMA 一跳直达"的完整参考实现——CRAQ 读写任何副本 vs Quorum 的带宽对比、链表 BIBD 放置、双状态机故障恢复、租约式心跳，全是可展开的教案；KVCache on 3FS 是"推理系统离线化缓存"的关键一环（与 open-infra-index Day 6 的 56.3% 磁盘 KV cache 命中率互证）。
- **讲透GPU与系统级（讲透GPU与系统级库）**：USRBIO = 用户态 io_uring 思想搬到分布式 FS（Iov/Ior 对照 SQ/CQ）；FUSE 内核瓶颈的 400K IOPS 实测数字是"内核旁路"动机的最佳案例；RDMA verbs 封装（`common/net/`）与 IB 内存注册管理可作系统编程教材。
- **讲透数据 / database-systems**：元数据建模（INOD/DENT key 设计、小端打散、range scan readdir）是"在 KV 上造文件系统"的经典范式；HybridKvEngine 的可插拔 KV 抽象、FDB SSI 事务冲突检测，是分布式事务的落地样本；chunk 引擎两级位图分配器 + RocksDB WriteBatch 原子性 = 存储引擎分配器设计范例。
- **工程化手册库**：P 语言形式化验证协议、Pyomo+HiGHS 把运维问题变成整数规划、SHUFFLE_METHOD 兼容性治理、mgmtd 集中配置热更、ClickHouse 指标体系、admin_cli 60+ 命令的运维面设计——都是可直接进手册的实践条目。

---

## 2. smallpond（2025-02 开源周 Day 5 配套）

### 2.1 定位一句话
构建在 DuckDB（单机执行引擎）与 3FS（共享存储）之上的轻量分布式数据处理框架：无常驻服务、任务级断点续跑、PB 级扩展（`README.md`）。

### 2.2 架构与核心机制（文件路径 + 类/函数）
- **双层 API**（`docs/source/api.rst`）：
  - 高层 DataFrame API（动态构图）→ **Ray** 做调度后端（`smallpond/dataframe.py`：`Session.read_parquet/read_csv/read_json/from_pandas/from_arrow`、`partial_sql(query, *inputs)`（`{0}/{1}` 占位符逐分区执行）、`DataFrame.repartition(n, by_row=, hash_by=)`、`write_parquet/write_parquet_lazy`、`Session.wait`）。
  - 低层 API（静态构图）→ 内置调度器（`smallpond/logical/node.py`：DataSourceNode/DataSetPartitionNode/SqlEngineNode/LogicalPlan；`smallpond/execution/driver.py`：Driver 命令行直跑），性能优化与配置更丰富，两者正在合并。
- **执行层任务类型**（`smallpond/execution/task.py`，34 个 class）：DataSourceTask / SqlEngineTask / HashPartitionTask（DuckDB 版与 Arrow 版双实现）/ PythonScriptTask / ArrowStreamTask（含 batch 级 checkpoint）/ ProjectionTask / DataSinkTask / RootTask / ExecutionPlan 等。
- **DuckDB 调优固定动作**（`execution/task.py` ExecSqlQueryMixin）：`SET threads TO {effective_cpu_count}`、`memory_limit`（含超发系数 cpu_overcommit_ratio/memory_overcommit_ratio）、`temp_directory`、`enable_object_cache=true`、`arrow_large_buffer_size=true`、`preserve_insertion_order=false`、`max_expression_depth=10000`——逐任务精细限额。
- **无服务架构 + 文件系统即消息队列**（`docs/source/internals.rst` + `execution/workqueue.py`）：data_root 下 `job_time.job_id/` 一目录一作业（config pickle/log/queue/output/staging/temp）；scheduler 与 worker 间通信用 **WorkQueueOnFilesystem**（队列落盘）；失败恢复为任务级 checkpoint（`staging/completed_tasks`、`started_tasks`），ArrowBatchTask 支持批级。
- **内存工程**（`session.py`）：Ray worker `LD_PRELOAD` 可选 jemalloc/mimalloc，`MALLOC_CONF: percpu_arena:percpu,background_thread:true,dirty_decay_ms:10000,lg_tcache_max:16`，并钉死 `ARROW_IO_THREADS=2/OMP_NUM_THREADS=2/POLARS_MAX_THREADS=2` 防线程超发。
- **平台抽象**（`platform/base.py`、`platform/mpi.py`）：默认本地 subprocess 起作业；检测到 `mpirun` 则用 MPI 平台拉起多节点 worker——集群接入只需实现 Platform 接口。
- **可观测**：自动起 Prometheus(8080)+Grafana(8122)，Ray Dashboard(8008)；后台线程每 60s dump graph.png 与 timeline（`session.py._dump_periodically`，按 worker/按节点两版 timeline）。
- **GraySort 实现**（`benchmarks/gray_sort_benchmark.py`）：两阶段——① `generate_records` 用 gensort 产记录，Arrow compute 切 key 前 2 字节做 big-endian uint16 bucket（bucket_nbits=12）；② 按 bucket shuffle（ShuffleNode）后 in-partition 排序（sort_engine 默认 polars，写 500MB IO 块）；全部中间数据落 3FS。
- **数据集层**（`logical/dataset.py`）：ParquetDataSet/CsvDataSet/JsonDataSet，`functools.lru_cache` 缓存按文件/按行/按大小三种分区方案；Parquet row group 参数集中治理（`common.py`：DEFAULT_ROW_GROUP_SIZE=122880、MAX_ROW_GROUP_BYTES=2GB、MAX_PARQUET_FILE_BYTES=8GB）。
- **io 层**（`io/filesystem.py`）：识别 `/hf3fs` 挂载点路径并对 3FS 文件做专门删除处理；cloudpickle+zstandard 序列化对象。**未发现 S3/OSS 对象存储支持代码**（任务提示中的"对象存储支持"未在当前版本实读到）。

### 2.3 工程亮点
- "轻"到极致：无常驻服务、无常驻元数据——作业状态全部是文件系统里的目录与 pickle，删目录即清理。
- DuckDB 每任务资源限额 + 双超发系数（CPU/内存）与 NUMA 绑定（bind_numa_node）选项。
- 故障注入意识：`common.py` 定义 `InjectedFault` 异常类型；`pytest_running()` 判断测试环境改变行为（如强制 checkpoint）。

### 2.4 互相关系
- 读写全走 3FS（FUSE 挂载点 `/hf3fs`），GraySort 成绩（3.66 TiB/min）即 smallpond(计算) + 3FS(存储) + RDMA(网络) 的联合测量；3FS README 的 GraySort 一节反向引用 smallpond。
- 与 Spark/Ray 的分工（`docs/source/getstarted.rst` 明示）：调度借用 Ray Core，存储去 3FS，smallpond 只做"数据集抽象 + DuckDB 执行 + 断点恢复"这一薄层——定位是补全 3FS 生态的数据准备（data preparation）环节，对应 3FS README "Diverse Workloads → Data Preparation"。

### 2.5 work4ai 输入
- **讲透数据 / database-systems**："DuckDB 嵌入式引擎 + 文件系统消息队列 + 任务级 checkpoint"是现代轻量湖仓（lakehouse-lite）的极简参考实现；HashPartition 的 DuckDB/Arrow 双实现适合讲"shuffle 该用 SQL 引擎还是列存内核"。
- **讲透分布式AI系统**：训练数据预处理管线的真实形态（正是 3FS 四大负载之首）；Ray 作为通用任务底座的用法边界。
- **工程化手册库**：LD_PRELOAD 分配器调优、MALLOC_CONF 参数、每分钟 graph/timeline 自动 dump、平台抽象接入模式，均可入册。

---

## 3. open-infra-index（DeepSeek 开源 infra 总索引）

### 3.1 定位一句话
DeepSeek 基础设施开源的官方索引与叙事线：把 FlashMLA→DeepEP→DeepGEMM→DualPipe/EPLB→3FS/smallpond 串成"开源周"，并补上两篇系统论文与推理系统经营数据（`README.md`）。

### 3.2 内容清单与组织方式（全部实读）
- **时间线组织**（README 分节）：
  - 202505 ISCA25 Industry Track：Insights into DeepSeek-V3（arXiv 2505.09343，硬件-架构协同的 scaling 反思）。
  - 202504：The Path to Open-Sourcing the DeepSeek Inference Engine——坦诚放弃整体开源内部推理引擎（基于一年前 vLLM fork、耦合内部集群管理、维护带宽不足），改为"抽取独立组件库 + 向现有开源项目贡献优化"，并承诺新模型发布前同步推理工程实现 Day-0 支持。
  - 202502 开源周 Day1–6：Day1 **FlashMLA**（Hopper MLA 解码 kernel，paged KV block 64，H800 上 memory-bound 3000 GB/s / BF16 580 TFLOPS）；Day2 **DeepEP**（首个开源 MoE EP 通信库：NVLink+RDMA、训练高吞吐/解码低延迟两套 kernel、原生 FP8）；Day3 **DeepGEMM**（FP8 GEMM，Hopper 1350+ TFLOPS，JIT 编译，核心 ~300 行）；Day4 **DualPipe**（双向流水线计算通信重叠）+ **EPLB**（专家并行负载均衡）+ **profile-data**（V3/R1 计算通信重叠剖析数据）；Day5 **3FS**（6.6 TiB/s、3.66 TiB/min、40+ GiB/s KVCache）+ **smallpond**；Day6 推理系统总览。
  - 2024 SC24：Fire-Flyer AI-HPC 论文（软硬件协同的深度学习成本设计，arXiv 2408.14158）。
- **Day 6 推理系统披露**（`202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md`，关键数字）：
  - PD 分离 + 跨节点 EP：Prefill 单元 4 节点（Routed Expert EP32 / MLA+Shared DP32，每 GPU 9 路由专家+1 共享）；Decode 单元 18 节点（EP144/DP144，每 GPU 2 路由专家+1 共享），32 个冗余路由专家。
  - 通信隐藏：prefill 双微批交替（dual-batch overlap）；decode 把 attention 拆两步、**5 级流水**无缝重叠。
  - 三层负载均衡器：prefill LB（core-attention 计算均衡 + dispatch 发送均衡）、decode LB（KVCache 用量均衡 + 请求数均衡）、expert LB（最小化最大 dispatch 接收负载）。
  - 经营数据（2025-02-27~28 24h）：V3+R1 峰值占用 **278 节点**、均值 226.75 节点（每节点 8×H800）；日成本 **$87,072**（$2/GPU·h 假设）；输入 608B tokens（**56.3% 命中磁盘 KV cache**——即 3FS）、输出 168B tokens；每 H800 节点平均 **73.7k tokens/s 输入 / 14.8k tokens/s 输出**；若按 R1 定价理论日收入 $562,027，**成本利润率 545%**（实际收入远低于此，含免费 Web/App 与夜间折扣）。日夜潮汐：白天全节点推理、夜间缩容转训练/研究。

### 3.3 工程亮点（索引本身的组织法）
- 用"一天一仓"的节奏把互相依赖的组件（kernel→通信→GEMM→并行策略→存储）按依赖倒序开源，每仓配性能数字与"production battle-tested"背书——开源叙事工程化的样本。
- LPLB/TileKernels 等新仓未列入本地该 README 读到的正文（该版本 README 止于上述内容）；本地克隆中 DeepEP/DeepGEMM/FlashMLA/DualPipe/EPLB/profile-data 均为独立仓库存在。

### 3.4 work4ai 输入
- **讲透分布式AI系统**：Day 6 是罕见的"推理系统经营学"一手数据（利润率、命中率、潮汐调度），EP32/EP144 双并行度、5 级 decode 流水可直接做成图解教案；与 3FS KVCache 40 GiB/s 互为印证。
- **讲透GPU与系统级**：FlashMLA/DeepGEMM/DeepEP 的数字（3000 GB/s、580 TFLOPS、1350+ FP8 TFLOPS）是 kernel 层上限的锚点，连接本系列其他笔记。
- **工程化手册库**："放弃整体开源、改为组件化贡献"的决策分析（代码库分叉/基础设施耦合/维护带宽三因）是开源策略管理的好案例。

---

## 4. 三仓联动图谱

```
Day6 推理系统 (EP144 decode, KVCache 56.3% 命中)
        │ 磁盘 KV cache / 数据集 / checkpoint
        ▼
3FS (CRAQ 链复制, 6.6 TiB/s, FDB 元数据, USRBIO)
        │ FUSE 挂载 /hf3fs                      ┌─ GraySort 3.66 TiB/min (50+25 节点)
        ▼                                       │
smallpond (DuckDB+Ray, 任务级 checkpoint) ──────┘
        │ 数据准备产物（目录/Parquet）
        ▼
训练/推理负载 (V3/R1, FlashMLA/DeepGEMM/DeepEP…)
```

open-infra-index 是这张图的目录页：SC24 Fire-Flyer AI-HPC 论文给出"为什么需要这套存储"（万卡集群成本设计），Day 6 给出"这套存储在推理侧的回报"（56.3% 缓存命中率、545% 理论利润率）。

---

## 5. 覆盖度与未读到清单（诚实声明）
- 已实读：3FS 全部 README/docs/deploy/data_placement/specs/README、configs 清单、src 目录树与 ~15 个关键头文件/源文件；smallpond 全部 docs + 5 个核心模块源码 + benchmark 脚本头部；open-infra-index 全部 3 个 md。
- 未读到/未找到：3FS 仓库内 .cc 实现体的大部分函数体细节（仅选择性深读头文件与关键类）；"batch load / file insight" 工具、DPDK、smallpond 对象存储支持——**在本地克隆中未发现**，若上游新版本加入需另行确认；3FS docs/images 下图片未逐张查看（数字取自 README 文字）。
