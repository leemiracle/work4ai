# 08 · KV Cache V1/V2 双体系：块管理传统派与三层存储新架构

## 一、角色定位

KV cache 管理是推理引擎的"内存操作系统"：决定哪些前缀可复用、哪些页可驱逐、容量不够时挡谁。TensorRT-LLM 里这是**两套并存的完整体系**（图谱实证：V1 侧 21 节点、V2 侧 110 节点）：V1 = `cpp/tensorrt_llm/batch_manager/kvCacheManager.cpp`（4647 行、163 处成员函数定义）+ 头文件 `cpp/include/tensorrt_llm/batch_manager/kvCacheManager.h`（2754 行），经典的块管理+基数树复用；V2 = `cpp/tensorrt_llm/batch_manager/kv_cache_manager_v2/`（31 文件的新目录），GPU/Host/Disk 三层存储、页级生命周期、跨层迁移。二者不是版本替换关系——Python 侧 `pyexecutor/_util.py` 按特性开关选择 V1 或 V2 管理器（`resolved_kv_cache_manager_is_v2` 等函数，图谱 fn 节点实证）。

## 二、内部结构

**V1 的骨架全在头文件里**：`KVCacheBlock`（kvCacheManager.h:387，只存元数据不存指针的 cache block）、`KVCacheBlockPool`（:784）、`WindowBlockManager`（:866，滑窗注意力专用——每个窗口一个实例，各自携带 dtype，使不同层组可混布不同精度池）、`BlockManager`（:1502）、`KVCacheManager`（:2292，`friend class KVCacheManagerBindings` 供 nanobind 暴露）。两条专用分支：`LinearAttentionMetadata`（:146）承载 Mamba 类线性注意力的状态缓存快照（statesSnapshotInterval 必须是 tokensPerBlock 整数倍，:194 校验）；`GenerationRequest`（:595）持有每请求的块映射。cpp 侧四个构造重载（kvCacheManager.cpp:3208/3226/3246/3289）对应统一/逐层 head 数、有无 stream 的组合。

**V2 是围绕"页"重建的**。核心文件分工：`kvCache.cpp`（2819 行）一请求一 `KvCache` 对象，生命周期三段式 `activate`（:216）/`suspend`（:564）/`resume`（:260）；`storageManager.cpp`（1964 行）管槽位与迁移，`CacheLevelManager`（storageManager.cpp:103）= "one storage level (GPU/Host/Disk) + its eviction controller"（storageManager.h:95），`submitMigrationBatch`（storageManager.cpp:579）是跨层迁移核心——按优先级排页、成批调度拷贝，`forceEvict`/`adjustCacheLevel`/`shrinkPoolGroup`/`expandPoolGroup` 构成配额操作面。外围件：`evictionController`（驱逐策略）、`coldPageCodec`（冷页压缩）、`cudaVirtMem`（虚拟内存映射）、`copyEngine`+`batchedPageCopy.cu`（拷贝执行）、`lifeCycleRegistry`（SSM/普通 KV 混布的生命周期登记）、`eventManager`（对外事件）、`introspection`（自省）。

**BlockRadixTree 是复用索引**（blockRadixTree.cpp 1004 行 + 头文件）：`class BlockRadixTree`（blockRadixTree.h:355）以前缀树组织已缓存块。块键 `BlockKey` 是 SHA-256 摘要——头文件用一段 SECURITY INVARIANT（blockRadixTree.h:67-79）钉死红线：哈希必须保持密码学抗碰撞且 ≥256 位，因为基数树是全局共享的跨请求/跨租户索引，前缀匹配纯靠摘要相等、**不复核底层 token**，攻击者可影响哈希输入（token、用户提供的 cache_salt、多模态字节）；换成 xxHash 或截断都会造成静默跨请求污染/泄漏。哈希实现走 `SHA256AutoDetect`（blockRadixTree.cpp:87，按 x86/arm SHANI 分派），事件侧另有 `v2_sha256`/`v2_sha256_64` 两档算法名（eventManager.cpp:93/97）。

## 三、外部连接

Python 双镜像：`tensorrt_llm/_torch/pyexecutor/kv_cache/kv_cache_manager_v2.py`（5921 行巨类，图谱口径约 150 方法，同时是 SWA/全注意力/静态 cache 三路容量估算纯函数库 + host tier 自动配额计算）；`tensorrt_llm/runtime/kv_cache_manager_v2/__init__.pyi`（685 行）对应 C++ V2 的 nanobind 绑定全量存根。上层消费者是 pyexecutor 的 resource_manager 与注意力后端（fp4_mla/cache_manager.py 甚至双继承 KVCacheManagerV2 做组合式特化）；下层对接 L07 的迁移/传输线（transfer.py 的 KVRegionExtractorV1、KVCachePageTable）。`ReuseScope`（loraId+salt，blockRadixTree.h:37）把 LoRA 前缀隔离接入复用命名空间。

## 四、数据流

冷启动一条请求：scheduler 申请 → V2 侧 `KvCache` 构造（kvCache.cpp:55，带 ReuseScope 与可选 `BlockRadixTree::ReuseMatch`）→ `activate` 入 GPU 层 → 前缀树查命中块标记复用。容量吃紧：evictionController 挑牺牲页 → `submitMigrationBatch` 降级到 Host/Disk（或直接 evict）。解码暂停（如 disagg 迁走、请求挂起）→ `suspend`；恢复时走 `resume`（kvCache.cpp:260）：先设 stream（:265-270），过 `maxUtilForResume` 利用率闸门（:278），`mNeverResumed` 首恢复标志控制增量循环语义（:299/:311 注释明言 delta 循环在 `_never_resumed` 之外），SSM 生命周期或有 partial 页时延迟恢复（:343-344）——这是一个 250 行的函数（260→510，下一函数 prefetch 在 :512），跨 GPU/Host/Disk 三层逐页编排恢复顺序，是 V2 最重路径。

## 五、设计决策

① **V1/V2 并存而非替换**：V2 面向分层存储与页级生命周期（长上下文、offload、disagg 场景），V1 仍是大量特性开关的稳态路径——迁移按特性矩阵逐项点亮，`_util.py` 的选择函数就是裁定点。② **WindowBlockManager 每窗口一实例**而非集中式：滑窗的 out-of-window 块回收（detachFrontBlock）天然按窗口独立计数（kvCacheManager.h:774），避免全局锁。③ **密码学哈希做键不是过度设计**：见 SECURITY INVARIANT——隔离性完全押在摘要碰撞阻力上，这是"安全属性由数据结构选择承载"的教科书写法。④ **buddy/页式分层 + MigrationRecorder 回调**（storageManager.h:48-49）：迁移、drop 都是注入的记录函数，事件流与存储逻辑解耦，eventManager 才能对外做 kv 事件订阅。

## 六、新人提示

先读 kvCacheManager.h 的类清单（按本文行号跳读），V1 全貌一小时可建。V2 入口顺序：storageManager.h 的 CacheLevelManager 注释 → kvCache.cpp 的 resume → blockRadixTree.h 的安全注释。三个易错点：改哈希算法前先重读 blockRadixTree.h:67 的红线（不能换非密码学哈希/不能截断）；V2 的"页"与 V1 的"块"不是一回事，文档混用时要看上下文；pyi 存根与 C++ 签名须同步改，漏改只会在运行时暴露。容量估算改动要三处对齐：C++ config、Python kv_cache_manager_v2.py、pyi。
