# 03 Region——已注册内存的统一视图：继承树的根与凭证的铸造口

> 源文件：`src/infinity/memory/Region.h`（60 行）/ `src/infinity/memory/Region.cpp`（63 行）

## ① 角色定位

Region 处于 L04，是整个内存抽象体系的根：把"一段已注册、可进 verbs 工作请求的内存"抽象成统一接口——data 指针、size、ibv_mr 句柄、RegionType 标签，外加地址/lkey/rkey 访问器。QueuePair 的通信原语在类型层面只认 Region 的两个具体子类（Buffer/Atomic）与它们铸造的 RegionToken；Context 的 friend 列表也按 Region 体系放行（Context.h:52-55）。它还是**凭证铸造口**：createRegionToken 三重载是把本端内存变成远端可寻址凭证的唯一入口（Region.cpp:21-31）。没有 Region，QueuePair 的签名将被迫各写一套 Buffer/Atomic 特化——统一视图就是为消除这种重复。

## ② 内部结构

**继承体系**：Region（Region.h:23，虚析构 :27）← Buffer（Buffer.h:19，普通消息内存）与 Atomic（Atomic.h:21，8 字节原子槽）。RegionType 枚举 BUFFER/ATOMIC/UNKNOWN（RegionType.h:15）给子类贴标签。

**公共接口两层**：

- 凭证铸造：createRegionToken() / (offset) / (offset, size) 三重载（Region.h:29-31）——全量快照 / offset 起剩余区间 / offset 起定长区间；
- 七访问器（Region.h:35-41）：getMemoryRegionType/getSizeInBytes/getRemainingSizeInBytes(offset)/getAddress/getAddressWithOffset(offset)/getLocalKey/getRemoteKey。

**protected 成员**（Region.h:45-52）：context/memoryRegionType/ibvMemoryRegion/data/sizeInBytes 五元组由子类构造时填好，基类只读。Region 自身**没有构造函数**：无公开构造路径，事实上是抽象基类的轻量做法（protected 成员+虚析构，没用纯虚函数）。

## ③ 外部连接

**被谁调用**：QueuePair 全部 17 个操作重载的 buffer 参数类型是 Buffer*（QueuePair.h:95-110），内部经 Region 接口取 getAddress/getLocalKey/getRemainingSizeInBytes（QueuePair.cpp:166-170）；RequestToken 持有 Region* 回指操作的本地内存（RequestToken.h:29-30）；Context::postReceiveBuffer 同样经 Buffer→Region 取三件套（Context.cpp:110-112）。

**依赖谁**：forward-declare RegionToken（Region.h:21）并在 .cpp 引 RegionToken.h 铸凭证；context 成员指回 Context（Region.h:45）。图谱中 Region.h 出边到 RegionType.h/Context.h，入边来自 Buffer.h/Atomic.h/QueuePair.h/RequestToken.h——内存线枢纽节点。小勘误：Region.cpp:9 include 了 Buffer.h，但实现体（仅 Region 自身与 RegionToken 符号）零引用 Buffer——冗余 include 残留，阅读时别据此以为基类反向依赖子类。

## ④ 数据流

**createRegionToken 三重载**（Region.cpp:21-31）：以全量重载为例（:21-23），把五访问器取出的值连同 this 指针一并 `new RegionToken(...)`。offset 重载换算 getRemainingSizeInBytes(offset)（= sizeInBytes−offset，:41-43）与 getAddressWithOffset(offset)（= data+offset，:49-51）；定长重载直接用传入 size。**凭证是快照不是引用**：铸造后 Region 再 resize，旧 token 不会跟着变（Buffer::resize 会换 ibv_mr，Buffer.cpp:103-104，旧 token 的 rkey 即告失效——真实的悬挂风险点）。

**钥匙访问器**（Region.cpp:53-59）：getLocalKey/getRemoteKey 直读 `ibvMemoryRegion->lkey/rkey`——本端发工作请求用 lkey，远端寻址用 rkey，两把钥匙统一出口。

**地址口径**：getAddress 返回 uint64_t 而非 void*（:45-47），因为该值最终要填进 wr.rdma.remote_addr（QueuePair.cpp:270）——地址即数值。

## ⑤ 设计决策

**极简基类**：Region 不做任何注册动作（注册在子类构造里），只提供读取面与铸造面。Buffer/Atomic 两种截然不同的内存（堆块 vs 成员 uint64_t）共享同一套通信签名；代价是成员全 protected 靠子类自觉初始化，漏初始化无编译期防护。

**三重载覆盖三种授权粒度**：全量授权、尾段授权（offset 起剩余）、定长窗口授权——"最小授权"直接内建在铸造口，远端拿到 token 只能触达快照圈定的区间（QP 侧再用 getRemainingSizeInBytes 断言复核，QueuePair.cpp:273）。

**getRemainingSizeInBytes 无下界检查**（Region.cpp:41-43）：offset 大于 size 时无符号下溢成天文数字，上层断言默认编译下被编译掉（Debug.h:21-24）形同虚设——健壮性寄望调用者自律，性能库常见取舍。

**RegionType 随凭证远行**：枚举进 RegionToken 跨机传输（read-write-send.cpp:60），让对端知道内存用途类别；UNKNOWN 专供按字节重建的默认构造（RegionToken.cpp:16）。

## ⑥ 新人提示

上手顺序：先读 Region.h 的 25 行类声明建立成员心智图，再对照 Buffer.cpp:22-70 与 Atomic.cpp:16-29 看两个子类怎么填五元组，最后跟 createRegionToken 一行行走进 RegionToken。三个坑：①token 是铸造瞬间的快照——之后对 Buffer 调 resize 或 delete，旧 token 变废纸，务必重新铸造并重新握手；②别直接 new Region——没有公开构造，也没有任何理由绕过 Buffer/Atomic；③`getRemainingSizeInBytes` 的下溢在默认编译下静默通过，传 offset 前自己保证 offset<size。验收自测：不看书默写五元组成员名与七访问器签名。
