# 01 · DemandLoader 按需加载：mapOrRequest 缺页模型与 PagingSystem 引擎

## 角色定位

DemandLoading 是 OTK 的主库（`DemandLoading/DemandLoading/`，75 文件）：让 OptiX 渲染器只加载视线真正命中的纹理 tile，用几百 MB 显存装下 TB 级数据集。机制核心是"device 发起、host 服务"的缺页模型——与 OS 虚拟内存同构，但缺页陷阱由 kernel 主动调用触发而非硬件异常。

## 内部结构

公开接口 `DemandLoading/DemandLoading/include/OptiXToolkit/DemandLoading/DemandLoader.h:33`（class DemandLoader 抽象基类，25 方法）：资源创建族 createTexture（`DemandLoader.h:42`）/createUdimTexture（`:48`）/createResource（`:58`，任意资源回调版）；页管理 invalidatePage（`:61`）/loadTextureTiles（`:64`）/unloadTextureTiles（`:67`）/setPageTableEntry（`:74`）/replaceTexture（`:77`）/initTexture（`:85`）。实现中枢 `DemandLoading/DemandLoading/src/DemandLoaderImpl.cpp`（659 行）：构造 `DemandLoaderImpl.cpp:124`（聚合选项与分页系统），createTexture `:159` 挂 ImageSource，makeTextureOrVariant `:235` 构造 DemandTextureImpl，migrateTextureTiles `:334` 纹理迁移，replaceTexture `:346` 热替换。

分页引擎 `DemandLoading/DemandLoading/src/PagingSystem.cpp`（473 行）：构造 `PagingSystem.cpp:27`（`:38-39` 建初始 pushMappings FutureEvent）；pullRequests（`PagingSystem.cpp:94`）异步拉取 device 侧缺页位图；processRequests（`:143`）在拷贝完成后消费（`:71` 注释说明回调链）；updateLruThreshold（`:55`）按返回/请求 stale 页与中位 LRU 值自适应调驱逐阈值；eviction 在 `:184-186` 按 maxStagedPages 分批 stage。设备侧协议 `DemandLoading/DemandLoading/include/OptiXToolkit/DemandLoading/Paging.h` 全 `__device__` 内联原语：lruInc（`Paging.h:16`，半字节 LRU 计数）、atomicSetBit（`:24`）/atomicUnsetBit（`:32`）/checkBitSet（`:41`）、半字节原子组（`:48-69`）。PageTableManager 管 64 位页表区间（backed/unbacked 分配）；LRU.h 定驱逐策略；Options.h 是贯穿 host/device 的配置 POD。核心数据契约 `DemandLoading/DemandLoading/include/OptiXToolkit/DemandLoading/DeviceContext.h`：StalePage（`DeviceContext.h:18`）/PageMapping（`:26`）/struct DeviceContext（`:34`）；同步票据 `Ticket.h:17`（class Ticket）。

## 外部连接

向下依赖 Memory 库的 MemoryPool/SyncVector（传输缓冲与页表驻留内存）；向上暴露 include/ 22 个公开头（DemandTexture.h 纹理句柄族、SparseTextureDevices.h 探测稀疏纹理支持设备、TextureSampler.h 采样器编址）；数据面接 ImageSource 族（`DemandLoading/ImageSource/include/OptiXToolkit/ImageSource/ImageSource.h:73` readTile 供 tile 内容）；纹理物理层接 `DemandLoading/DemandLoading/src/Textures/SparseTexture.cpp:248`（mapTile，cuSparseArray 异步映射）与 `:262`（fillTile）。示例层经 `examples/OTKAppBase/include/OptiXToolkit/OTKAppBase/OTKApp.h` 聚合使用。

## 数据流

一次纹理缺页：device kernel 采样 miss → 调 Paging 协议置请求位（`Paging.h:24` 原子位操作）→ host launch 循环 pullRequests（`PagingSystem.cpp:94`）拷回位图 → processRequests（`:143`）解码缺页页号 → RequestQueue 入队 → ThreadPoolRequestProcessor 线程池执行 ResourceRequestHandler::fillRequest → ImageSource readTile 读像素 → 写传输缓冲 → pushMappings 把物理页映射写回 device 页表 → `SparseTexture.cpp:248` mapTile 绑定进稀疏纹理 → kernel 下一 launch 命中。驱逐：LRU 半字节计数（`Paging.h:16`）超阈值（updateLruThreshold 自适应）→ 旧页 unmap 进 StalePage（`DeviceContext.h:18`）列表 → 显存回收给新页。

## 设计决策

①**mapOrRequest 双语义**——kernel 首访返回"未映射"并记请求、host 补映射后重访命中，一帧内多次访问零额外成本；②**LRU 计数压到半字节**（`Paging.h:48` atomicAddHalfByte）——device 内存预算下页元数据极致压缩，代价是计数饱和需中位数校准（`PagingSystem.cpp:55`）；③**staged eviction 分批**（`PagingSystem.cpp:184`）——映射推送与驱逐交错限流，避免一次性大同步卡帧；④**纹理/任意资源双轨**——createResource（`DemandLoader.h:58`）回调式让几何/材质复用同一引擎（`DemandLoading/DemandGeometry/src/ProxyInstances.cpp` 与 DemandMaterial 即此路）。

## 新人提示

读码顺序：`DemandLoading/DemandLoading/README.md` 机制 → `DemandLoader.h:33` 接口 → `DemandLoaderImpl.cpp:159` createTexture → `PagingSystem.cpp:94`/`:143` 拉取-处理对。调试"纹理黑块"先分三问：请求置位了吗（Paging.h 位图）、host 读到 tile 了吗（TestRequestHandlerLogging 可复现）、映射推回了吗（TestPagingSystem/TestPagingSystemKernels）。无 GPU 环境用 `Testing/include/OptiXToolkit/Testing/MockOptix.h:44` 的 mock 跑 TestDemandLoader/TestDemandPageLoader。页表相关改动先读 TestPageTableManager——64 位区间边界是历史 bug 高发区。
