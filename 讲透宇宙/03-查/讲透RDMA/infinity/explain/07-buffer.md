# 07 Buffer——Region 的通用内存载体：三种所有权从构造走到注销

> 源文件：`src/infinity/memory/Buffer.h`（44 行）/ `src/infinity/memory/Buffer.cpp`（113 行）

## ① 角色定位

Buffer 处于 L06（Buffer.h:19），是 Region 继承树上最大的一片叶子，也是用户 90% 时间打交道的类：它把"申请一段内存→注册成 MR→交给 QueuePair 收发"压缩成一行 `new Buffer(context, size)`。两个示例里所有通信内存都是 Buffer（read-write-send.cpp:51/:55/:78-79，send-performance.cpp:60/:96/:113-114）。与三角分工对齐：**Region 是接口与凭证铸造口**（03 篇），**RegisteredMemory 是注册容器**（02 篇），**Buffer 是带所有权的通用载体**——自己管 malloc、自己管 ibv_reg_mr、析构时按两个标志决定还什么。QueuePair 全部 17 个操作重载的本地内存参数类型都是 `Buffer*`（QueuePair.h:95-110），Buffer 因此是"能进工作请求的内存"的默认具体形态。

## ② 内部结构

类面极小（Buffer.h:23-31）：三个构造 + 析构 + `getData()` + `resize()`，**没有任何自有数据访问的复杂性——复杂度全在构造的所有权语义上**。自有成员仅两个布尔（Buffer.h:35-36）：`memoryRegistered`（析构要不要 ibv_dereg_mr）与 `memoryAllocated`（要不要 free）——2 bit 编码出三种所有权模式。其余五个字段（context/memoryRegionType/ibvMemoryRegion/data/sizeInBytes）全部继承自 Region 的 protected 五元组（Region.h:45-52），由构造函数直接填。Buffer.cpp:17 本地定义 `MIN(a,b)` 宏，服务 resize 的拷贝量计算。

## ③ 外部连接

**依赖**：Context 的 PD（`ibv_reg_mr` 挂靠，Buffer.cpp:33/:63）；`Configuration::PAGE_SIZE` 提供对齐粒度（Buffer.cpp:28→Configuration.h:43）；Debug.h 四处断言（Buffer.cpp:29/:35/:65/:108）。**被谁用**：QueuePair 的 send/write/read 以 Buffer 取 addr/lkey（组1 05 篇模板第②步）；Context::postReceiveBuffer 经 Region 接口取三件套挂 SRQ（组1 01 篇，Context.cpp:110-112）；视图构造消费 RegisteredMemory 的 ibv_mr（Buffer.cpp:48-49）。小勘误（组1 钉版）：Region.cpp:9 include 了 Buffer.h 但实现零引用——冗余残留，别据此以为基类反向依赖子类。图谱中 Buffer.h 出边到 Region.h/Context.h/RegisteredMemory.h，入边来自 QueuePair.h 与两示例——内存线中段枢纽。

## ④ 数据流

**构造一：库内分配+注册**（Buffer.cpp:22-40）：`posix_memalign` 按 4096 页对齐分配（:28，对齐利于 NIC pin 页）→ 断言分配成功（:29）→ `memset` 清零（:31）→ `ibv_reg_mr` 以三权限注册（:33-34，`REMOTE_WRITE | LOCAL_WRITE | REMOTE_READ`，**无 REMOTE_ATOMIC**——那是 Atomic 的专属权限，Atomic.cpp:25-26）→ 置双标志 true（:37-38）。这段与 RegisteredMemory 的分配构造（RegisteredMemory.cpp:20-34）几乎逐行相同——Buffer 没有委托而是复制粘贴，两个类各自持一份"posix_memalign+reg_mr"样板。

**构造二：RegisteredMemory 视图**（Buffer.cpp:42-54）：`data = memory->getData() + offset`（:48），`ibvMemoryRegion = memory->getRegion()`（:49）直接复用大块注册的 ibv_mr，双标志 false（:51-52）——零成本切片，这是"一次注册、多视图"池化模式的落点。注意 :48 对 offset **不做任何越界检查**：offset 超出父块大小不会报错，只会得到一个指向父块之外的 Buffer，后续注册键与地址全部"合法地"错误。

**构造三：注册外部内存**（Buffer.cpp:56-70）：调用者给裸指针，Buffer 只注册不分配（:63-64），`memoryAllocated=false, memoryRegistered=true`（:67-68）——生命周期归你，注册归我。

**析构**（Buffer.cpp:72-81）：严格按标志逆序——先 dereg（:74-76）后 free（:77-79）；视图模式两者皆跳过。

**resize**（Buffer.cpp:87-110）：唯一非平凡方法。先记住 `uint32_t oldSize = this->sizeInBytes`（:90——**uint64 截断成 uint32，>4GB buffer 的旧长度直接错**）；`newData==NULL` 时原地复用（:92-94）；新旧指针不同则 `memcpy` 拷 MIN 交集（:96-99）；仅当 `memoryRegistered` 才走 dereg+重新注册（:101-106，权限位原样重放）；视图 Buffer 走 :108 断言拒绝。

## ⑤ 设计决策

**2 bit 所有权标志代替继承**：三种模式没有拆成三个类，靠构造函数填标志+析构/resize 查标志——对比"每种所有权一个子类"的教科书做法，这里用最平的结构换最少的概念数；代价是 resize 只认自注册（:108）这一隐含契约。

**resize 重注册=钥匙换发**：Buffer.cpp:102-104 销毁旧 ibv_mr 再注册新的，lkey/rkey 必然改变——所有先前 `createRegionToken`（Region.cpp:21-31）铸出的旧 token 立即作废，且**没有任何机制通知你**。这与 03 篇"token 是快照不是引用"的钉版结论互为因果。

**权限位写死且不含原子**：三权限覆盖 read/write 场景，与 RegisteredMemory 完全一致（组1 02 篇）——远端 CAS 被网卡按权限拒收是有意的安全默认：原子操作只该落在 Atomic 的 8 字节槽上。

**getData() 是唯一的新增读取面**（Buffer.cpp:83-85）：把 Region::getAddress 的 uint64 数值重新包回 `void*`，服务"往 buffer 里填/读内容"的直觉写法——地址即数值（ verbs 口径）与地址即指针（用户口径）在此各取所需。

## ⑥ 新人提示

上手顺序：先读 Buffer.h 的 30 行类声明建立"三构造+两标志"心智表，再对照 Buffer.cpp:22-70 看三种所有权怎么填五元组，最后单精读 resize。四个坑：①**原地扩容是堆溢出**——resize 传大 newSize 且 newData=NULL 时只重新注册不重新分配（:92-106），新尺寸越过原分配边界即 UB，增长必须自己 malloc 新块传进来；②视图构造的 offset 不查父块边界（:42-54），越界静默通过；③resize 拒绝视图 Buffer 的断言（:108）默认编译下被编译掉（Debug.h:21-24）——实际行为是"拷贝了数据但一切照旧"的静默 no-op；④oldSize 的 uint32 截断（:90）让 >4GB buffer 的 resize 拷贝量算错。验收自测：不看书默写三构造对应的两标志真值表，并说出 resize 后旧 RegionToken 为什么作废。
