# 08 · P2P 机内通道：src/transport/p2p.cc

## 一、角色定位

`src/transport/p2p.cc`（1516 行）实现 `p2pTransport`——传输表第一位（transport.cc:15-20）的机内互联：同机 GPU 经 NVLink/P2P 直接读写对方显存。它回答三个问题：**能不能直连**（`p2pCanConnect`）、**用什么形态连**（DIRECT/IPC/CUMEM/INTERMEDIATE 四型，p2p.cc:19-24）、**素材怎么交换与映射**（CUDA IPC 句柄或 cuMem shareable handle）。框架层经 canConnect 选中后，setup/connect/free 三段式由本文件完成；GPU kernel 通过它布置的 `connInfo->buffs/head/tail`（device.h:136-159）与 NCCL_P2P_READ/WRITE 标志（device.h:123-124）直接搬数据——p2p 是唯一几乎无 proxy 参与数据面的传输（CE memcpy 模式例外）。

## 二、内部结构

### 1. 连接可行性：p2pCanConnect（p2p.cc:129）

五道闸门依次判：①拓扑层 `ncclTopoCheckP2p` 给可达性与中转 rank（p2p.cc:136），需中转且开 memcpy 时直接放弃（p2p.cc:139-142）；②非 cross-clique 时若 `ncclTopoCheckNet` 认为走网络更好则让贤（p2p.cc:145-152）；③同 host 才继续（p2p.cc:154）；④把 peer 的 PCI busId 翻译成本进程可见 cudaDev（`busIdToCudaDev`，p2p.cc:107——CUDA_VISIBLE_DEVICES 会改编号必须按 busId 对齐；CUDA 10.1+ 隐形设备放行，p2p.cc:163-165）；⑤`cudaDeviceCanAccessPeer` 硬件判定（p2p.cc:178），同卡多 rank 恒可（p2p.cc:175-177）。最后是 legacy IPC 探测并缓存（p2p.cc:186-204，WSL workaround）。MNNVL cross-clique 直连优先，因为 peer 不在本 rank 拓扑里（p2p.cc:144）。

### 2. 四种通道形态

`p2pGetInfo`（p2p.cc:337）问拓扑"Ampere+ 且 NVLink 相连则默认 P2P Read"（注释 p2p.cc:340-342），`NCCL_P2P_READ_ENABLE`（默认 -2=自动，p2p.cc:331）可覆盖；CE memcpy 模式强制 write（p2p.cc:402），CollNet 的 scatter-reduce 连接（connIndex 1）也强制 write（p2p.cc:407-408）。setup 时定型（p2pSendSetup:393 / p2pRecvSetup:474）：

- **P2P_DIRECT**：同进程（`P2P_SAME_PID` 宏，p2p.cc:334）且未禁 direct 且非 memcpy（p2p.cc:418）——直接用对方指针，零句柄交换。
- **P2P_CUMEM**：`ncclCuMemEnable()` 时走 cuMem 虚拟内存 API（p2p.cc:424），MNNVL 也在此路径。
- **P2P_IPC**：legacy `cudaIpcGetMemHandle/cudaIpcOpenMemHandle`（p2p.cc:250-256/322）。
- **P2P_INTERMEDIATE**：拓扑需要中转 GPU 时，素材指向中转 rank（p2p.cc:439-444）。

连接素材 `p2pConnectInfo`（p2p.cc:38-44）塞进 256B 的 ncclConnect，static_assert 保证不超（p2p.cc:45）。

### 3. 句柄分配与导入

- `ncclP2pAllocateShareableBuffer`（p2p.cc:223）：cuMem 路径 `ncclCuMemAlloc`+`cuMemExportToShareableHandle`（p2p.cc:231-240），POSIX fd 句柄不导出而内嵌原生 handle 留待 UDS 转换（p2p.cc:235-238），refcount>0 时多次 retain 挂引用（p2p.cc:241-244）；legacy 路径 cudaMalloc+cudaIpcGetMemHandle。
- `ncclP2pImportShareableBuffer`（p2p.cc:267）：按 granularity 对齐尺寸（p2p.cc:283-284）；POSIX fd 句柄先经 proxy UDS 通道传来（`ncclProxyClientGetFdBlocking`，p2p.cc:291-295）；再 `cuMemAddressReserve+cuMemMap+cuMemSetAccess` 三步映射远端内存（p2p.cc:299-309）并 `ncclMemTrackImportFromPeer` 记账（p2p.cc:315-316）。
- `p2pMap`（p2p.cc:349）按进程关系分流：同进程异卡 `cudaDeviceEnablePeerAccess`（p2p.cc:355-362），cuMem 下还要映射对方 memHandle 抬引用防"peer 先退出显存悬空"（p2p.cc:363-373，注释明言此动机）；异进程走上面的 Import。

### 4. setup/connect 成对逻辑

`p2pSendSetup` 计算发送侧尺寸：`sizeof(ncclSendMem)`，P2P Read 时把 SIMPLE 缓冲**拼在 sendMem 尾部**（p2p.cc:411-414）并对齐 CUDA_IPC_MIN；随后 `ncclProxyConnect`+`ncclProxyMsgSetup` 让 proxy 分配共享 buffer 回传 p2pBuff（p2p.cc:457-466）。`p2pRecvSetup` 对应地：Read 模式 recv 侧**不含** SIMPLE 缓冲（p2p.cc:492-494）——数据由接收方从对端拉。connect 阶段完成指针配对（p2pSendConnect:540 / p2pRecvConnect:583）：

```
send 侧: tail = &远端recvMem.tail   head = &本地sendMem.head  [p2p.cc:572-573]
recv 侧: tail = &本地recvMem.tail   head = &远端sendMem.head  [p2p.cc:602-604]
```

双方**各写本地、读远端**，NVLink 双向对称；`ptrExchange/redOpArgExchange`（device.h:146-147）支持 zero-copy 直传指针与算子参数。Read 模式的 SIMPLE 缓冲镜像布局见 p2p.cc:551-559/612-615。free 链（p2pSendFree:624 / p2pRecvFree:653）区分 cuMem（sameProcess→ncclCuMemFreeAddr，否则 ncclCudaFree）与 legacy（cudaIpcCloseMemHandle）。

### 5. CE memcpy 模式（dev op 的旁路）

`P2P_USE_CUDA_MEMCPY=1` 时（p2p.cc:122）`initCeOperation`（p2p.cc:1500）动态挂上 proxyConnect/proxyProgress：proxy 建 CE 专用缓冲、SHM 段与事件（p2pSendProxySetup:685、p2pSendProxyConnect:751），数据面改为 GPU→ceDevBuff→proxy `cudaMemcpyAsync(D2D)`→对端 recvFifo，事件完成再推 SHM tail（p2pSendProxyProgress:844，memcpy 在 p2p.cc:875-877、tail 在 p2p.cc:889）。SM 零参与、全由 copy engine 搬——dev op 的 CE 旁路。

### 6. 用户 buffer 的 IPC 注册

`ipcRegisterBuffer`（p2p.cc:1015）服务 zero-copy 直通用户显存：已有注册记录则复用（p2p.cc:1064-1072）；否则 `cuMemRetainAllocationHandle` 拿句柄，失败回退 legacy IPC（p2p.cc:1113-1118）；跨 VA 段走多段注册（p2p.cc:904，`cuMemGetAddressRange` 逐段导出，超 8192 段放弃，p2p.cc:104/949）。句柄经 `ncclProxyMsgRegister` 送到对端 proxy，由 `p2pProxyRegister`（p2p.cc:1347）map 后返回远端地址 rmtRegAddr（p2p.cc:1165-1167），地址表再异步拷进 GPU（p2p.cc:1209-1216）；collective 返回地址数组、send/recv 返回单地址（p2p.cc:1225-1231，remote addr 由 ncclDevWorkP2p 设备结构携带）。注销沿 `p2pProxyDeregister`（p2p.cc:1468）+ proxyMemHandleQueue 回收。

## 三、外部连接

include：comm/graph/shmutils/p2p/transport/mem_manager/shm 等（p2p.cc:8-17）。被调：`p2pCanConnect` 由 transport.cc:33 选择循环调用（表序第一位）；`ncclIpcLocalRegisterBuffer/ncclIpcGraphRegisterBuffer` 被 register/sendrecv_reg.cc:37/41 与 coll_reg.cc:271-283 调用；`ncclP2pUsesMemcpy`（p2p.cc:1513）供注册路径判断。依赖：topo 层 `ncclTopoCheckP2p/ncclTopoCheckNet`（p2p.cc:136/147）、proxy 通道与 UDS fd 传递（p2p.cc:291）、mem_manager 记账、device.h 的 READ/WRITE 标志与 send/recvMem 布局。CUDA API 双轨贯穿全文：legacy（cudaIpc*）与 cuMem。

## 四、数据流

```
p2pCanConnect 五闸 → p2pTransport 胜出                    [p2p.cc:129]
p2pSendSetup/p2pRecvSetup:
  定型 DIRECT|CUMEM|IPC|INTERMEDIATE, 定 read/write       [p2p.cc:418-444]
  → proxy: ncclP2pAllocateShareableBuffer(分配+导出句柄)  [p2p.cc:223]
  → ncclConnect 素材经 bootstrap 交换(transport.cc:191)
p2pSendConnect/p2pRecvConnect:
  p2pMap: 同进程 peerAccess / 异进程 ImportShareableBuffer [p2p.cc:349/267]
  → connInfo{buffs[], head/tail 交叉配对, flags=READ|WRITE}
  → cudaMemcpy 刷入 devPeers(GPU 可见)
运行期(write): 发送 kernel 写远端 recvMem buff + 推本地 head
               接收 kernel 轮询远端 head, 消费后推本地 tail
运行期(read):  接收 kernel 从远端 sendMem SIMPLE 尾部拉数据
销毁: p2pSendFree/p2pRecvFree(cuMem or cudaIpcClose)
```

## 五、设计决策

1. **四形态一套代码**：DIRECT/IPC/CUMEM/INTERMEDIATE 差异压缩到 setup 定型+p2pMap 分流两处，connect 之后完全同构——新增内存 API 只动分配/导入两个函数。
2. **Read/Write 可选而非硬编码**：Ampere 后 NVLink 读效率与写相近且省一次中转，默认按拓扑自动选（p2p.cc:340-342），环境变量留逃生门；CollNet scatter-reduce 强制 write（p2p.cc:407-408）体现"策略在算法层、机制在传输层"。
3. **SIMPLE 缓冲随 Read 迁移**：Read 模式把大块 SIMPLE 缓冲放发送侧（p2p.cc:411-414）、接收侧省掉（p2p.cc:492-494），显存按数据所有权分配。
4. **cuMem 优先、legacy 兜底的渐进栈**：cuMemEnable 分支覆盖新硬件（MNNVL/GB200），legacy cudaIpc 路径保留兼容（WSL/旧驱动），注册失败还有"cuMem 导出失败重试 legacy"的降级链（p2p.cc:1113-1118）。
5. **引用计数保生命周期**：同进程映射对方 handle 抬引用（p2p.cc:363-373）、proxyMemHandleQueue 队列化注销——"peer 先死"是常态，防悬空优先于防泄漏。

## 六、新人提示

- 日志定位通道形态：`NCCL_DEBUG=INFO,NCCL_DEBUG_SUBSYS=INIT` 的 `via P2P/direct|IPC|CUMEM|indirect/N` 行（p2p.cc:420-443），`/read` 后缀表示 Read 模式。
- 怀疑 P2P 被误判：依次查 `NCCL_P2P_DISABLE`、`NCCL_P2P_LEVEL`、CUDA_VISIBLE_DEVICES（busIdToCudaDev 映射失败会静默放弃，p2p.cc:160-171）。
- `NCCL_P2P_USE_CUDA_MEMCPY=1` 是 SM 短缺场景的实验开关（proxy+copy engine 数据面），生产慎用——它禁用 intermediate 形态（p2p.cc:139-142）。
- zero-copy 注册失败的高频原因：用户 buffer 跨多个 VA 段且超 8192 段上限（p2p.cc:949-956）、或 legacy IPC 不支持该分配（cuMemRetainAllocationHandle 失败且 LEGACY_CUDA_REGISTER=0，p2p.cc:1113-1115）——日志 grep "failed to IPC register"（p2p.cc:1244）。
- 改 p2pConnectInfo 结构必须同步检查 static_assert（p2p.cc:45）：它是塞在 256B ncclConnect 里的 wire 结构，多机两端 NCCL 版本不同时会静默错位。
