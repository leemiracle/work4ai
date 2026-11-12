# 02 · mm 内存资源体系与 GDS 直存通道

## 角色定位

图谱 L03 层（51 节点）由两半组成：`dali/core/mm`+`include/dali/core/mm` 是 pmr 风格内存资源体系——注释自述"follows the interface of C++17 polymorphic memory resource ... extends them by the CUDA stream support"（memory_resource.h:28-29），接口从 libcu++ 演化（NOTES-DIGEST batch-79 甄别）；cufile 系+gds_mem 是 GPU Direct Storage 直存读通道。这层是 DALI 显存与 pinned 内存策略底座：Tensor/TensorList 分配、kernels 暂存、Python 侧 pinned buffer 都落到这里的默认资源。**注意三处分布**：cufile 代码散在 `dali/util`（CUFileStream 抽象+StdCUFileStream）、`dali/operators/reader`（GDSAllocator/GDSStagingEngine+CUFileLoader）、`dali/core`（dynlink_cufile 装载）三处，跨目录检索 cufile 必看全三处。

## 内部结构

资源接口按 memory_kind 分型：`host/pinned/device/managed` 资源别名（memory_resource.h:46-47），流序版本 `async_memory_resource = stream_ordered_memory_resource`（memory_resource.h:53-57）。资源可组合成链：pool_resource（pool_resource.h:89-90，FreeList+LockType 模板参，get/put 剩余切分 :134/185）、binning_resource（binning_resource.h:44/137 按尺寸分桶）、async_pool_resource（async_pool.h:44，per-stream 释放队列与事件挂起释放 :248/276）、cuda_vm_resource（cuda_vm_resource.h:44）。cu_vm.h 封装虚拟内存 API：CUMemAddressRange 保留地址段（cu_vm.h:83，保留≠分配，需 cuMemMap+cuMemSetAccess 生效，:120-132）、CUMem 物理句柄（:177）、IsSupported 探测（:63）。

全局装配在 default_resources.cc：单例 `DefaultResources`（:41）经 `g_resources` 宏访问（:128）；`MMEnv`（:138）读四个开关——DALI_USE_DEVICE_MEM_POOL（:153）/DALI_USE_VMM（:156）/DALI_USE_PINNED_MEM_POOL（:159）默认全开，DALI_USE_CUDA_MALLOC_ASYNC（:162）默认关。设备资源三级决策（CreateDefaultDeviceResource，:231）：cudaMallocAsync 直通（:236，CUDA>=11.2 门控）→ VMM 路径 async_pool_resource<device, cuda_vm_resource>（:249-255）→ 兜底 cudaMalloc 上游套 async_pool_resource<device, pool_resource<device, coalescing_free_tree, spinlock>>（:257-263）。pinned 同构（:267-274）。

GDS 侧：gds_mem.h 定义 4096 对齐常量（kGDSAlignment，gds_mem.h:34）、`GDSAllocator`（:37）、move-only `GDSStagingBuffer`（:80，析构 assert"必须归还引擎"）与 `GDSStagingEngine`（:114）。gds_mem.cc 里 chunk 尺寸裁剪 4096~16M（GetGDSChunkSizeEnv，gds_mem.cc:32/50）、缓冲注册 cuFileBufRegister（:69）、`GDSRegisteredResource`（:84）与 `GDSMemoryPool`（:141，对齐抬到 chunk 尺寸 :147-158）。util 侧 `CUFileStream` 是抽象基类（cufile.h:28），接口 ReadGPU/ReadAtGPU（cufile.h:50/58，注释说明 cuFile 要"注册缓冲基址+偏移"语义）；工厂 Open 剥 file:// 前缀并拒绝 mmap（cufile.cc:24-32）。

## 外部连接

上游：CUDA runtime/VMM API 与 dlopen 的 libcufile。dynlink_cufile.cc 是弱依赖范式样板（与 nvml_wrap 同型，NOTES batch-78）：先 dlopen libcufile.so.0 再退 libcufile.so（dynlink_cufile.cc:29-35），失败打印 conda 提示（:40），`CufileLoadSymbol` 惰性解析（:53）。cufile_helper.h 的 `CUFileDriverScope`（:37）带两处同款注释"cuFileDriverOpen in some versions can close stdin"（:41/:65）——SDK bug workaround；RAII `CUFileHandle` 持有 fd（缓冲 IO）与 fdd（直读 IO）双描述符（cufile_helper.h:86-118）。符号可见性由 libdali_core.map.in 控制：cufile.h 符号默认可见会连带导出 DALI 包装，map 显式 `local: cuFile*` 隐藏（libdali_core.map.in:4-6）。下游：L07 Tensor/TensorList 分配走 GetDefaultResource；kernels 的 dynamic_scratchpad 从资源借内存；CUFileLoader（cufile_loader.h:33）继承 FileLoader<GPUBackend, Target, CUFileStream>，析构注释写明注销顺序坑——缓冲须在 cuFileDriver 关闭前 Deregister（cufile_loader.h:40-49）。

## 数据流

分配路径：算子请求 → GetDefaultResource<kind> → async_pool 先查 per-stream 空闲块（事件未触发则挂 pending_free）→ miss 落 pool_resource 的 coalescing_free_tree → 仍 miss 打到上游 cudaMalloc/VMM 映射；释放分同步（立即回池）与流序（事件完成后回收）两路。GDS 读路径：CUFileLoader 打开文件 → GDSAllocator 分配已注册设备块 → cuFileRead 直入显存（跳过 host 中转）→ 不规则样本由 GDSStagingEngine 经 kernels/common/scatter_gather（gds_mem.h:32 include）从规则 chunk 搬到目标张量；ODirectFileStream 是无 GDS 时的 CPU 对照路径（O_RDONLY|O_DIRECT，odirect_file.cc:65，pread 定位读 :104）。

## 设计决策

1. 选 pmr 而非裸 allocator：资源自由组合成"池→上游→CUDA API"链，default_resources 三级决策是组合力的直接展示；代价是模板链深、报错难读。
2. cuFile 一律 dlopen：GDS 可选，无库环境须能跑（惰性解析+探测 cuFileIsSymbolAvailable，dynlink_cufile.cc:57）。
3. 单行 .inl 宏接力：dynlink_cufile.inl 整文件只有 `#undef cuFileDriverClose`，语义靠包含点还原——tree-sitter 零提取（NOTES batch-55），图谱节点靠人工甄别。
4. 环境变量逃生门：四级开关每级可关，等价运行期 A/B 旋钮（default_resources.cc:153-163）。
5. GDSStagingBuffer 用类型系统锁生命周期：move-only+析构 assert，把"忘记归还"从泄漏变成崩溃（gds_mem.h:80-91）。
6. 4096~16M chunk 约束来自 cuFile 注册块对齐要求（gds_mem.cc:50）。

## 新人提示

排查显存问题先动环境变量：DALI_USE_DEVICE_MEM_POOL=0 关池直连 cudaMalloc，对比即可定位池碎片还是驱动问题；DALI_USE_VMM=0 在老驱动上绕开 VMM。查 cuFile 链路记住三处分布（util/reader/core），只 grep 一个目录必漏。cufile_helper.h:41 的"close stdin"注释值得精读——某些 cuFile 版本 DriverOpen 会误关 fd 0，DALI 用 scope guard 护住。行为语义测试在 dali/core/mm/*_test.cc（pool/binning/async/cuda_vm 各有专测）与 gds_mem_test.cu；调试直读 vs 缓冲路径先分清 fd 还是 fdd（cufile_helper.h:115-118）。
