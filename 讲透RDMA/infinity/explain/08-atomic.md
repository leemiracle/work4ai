# 08 Atomic——8 字节原子槽：原子性在网卡，不在 CPU

> 源文件：`src/infinity/memory/Atomic.h`（44 行）/ `src/infinity/memory/Atomic.cpp`（51 行）

## ① 角色定位

Atomic 处于 L07（Atomic.h:21），Region 继承树的第二片叶子，全库最小也最"专"的内存类：一个 `uint64_t` 成员，按 8 字节注册成 MR，唯一的存在理由是**给远端网卡当原子操作的落点**。它同时扮演两个方向的角色——**远端槽**：server 侧 `new Atomic(context)` 再 `createRegionToken()`（Region.cpp:21-23）铸出凭证，经握手送到 client，成为 `qp->compareAndSwap(token,...)`/`fetchAndAdd(token,...)` 的 destination；**本地落点**：client 侧另持一个 Atomic 作 previousValue，网卡执行原子操作后把**旧值 DMA 回来**填进它（QueuePair.cpp:502-504/:549-551）——原值获取零 CPU 参与。一句话定位：CPU 侧它只是普通内存，网卡侧它是对端可远程原子触达的 8 字节窗口。README.md:3 的 "one-sided (read/write/atomic)" 中 atomic 一词的内存端基础设施就是它。

## ② 内部结构

全类四成员五方法（Atomic.h:25-36）：构造（只要 context）、虚析构、`getValue()`/`setValueNonAtomic()`，外加 protected 的 `uint64_t value`（Atomic.h:36）。没有所有权标志（对照 Buffer.h:35-36）——因为 Atomic **永远自注册**：data 直接指向自己的成员（Atomic.cpp:23），MR 永远自己建自己销，不存在 Buffer 那三种所有权模式，析构无条件 `ibv_dereg_mr`（Atomic.cpp:44-48）。`sizeInBytes = sizeof(uint64_t) = 8`（Atomic.cpp:19）是 verbs 原子操作的天然粒度——IB 的 CMP_AND_SWP/FETCH_AND_ADD 只认 8 字节对齐的 64 位槽，这是这个类"长成这样"的物理约束。

## ③ 外部连接

**依赖**：Context 的 PD 做注册（Atomic.cpp:25）；继承 Region 取得凭证铸造能力。**被谁用**：①QueuePair 原子组四重载（QueuePair.h:136-141），CAS/FAD 各分全量版（收 `Atomic* previousValue`）与便捷版；便捷版自动用 `context->defaultAtomic`（QueuePair.cpp:529/:533）；②Context 构造时预建 `defaultAtomic` 公共槽（Context.cpp:72，Context.h:88），与 defaultRequestToken 并列。**opcode 落点**：IBV_WR_ATOMIC_CMP_AND_SWP（QueuePair.cpp:510）与 IBV_WR_ATOMIC_FETCH_AND_ADD（:557），wr.atomic 填 remote_addr/rkey 取自 destination token（:515-516/:562-563），compare/swap 或加数填 :517-518/:564。与组1 05 篇的互引：原子组同样走"reset+setRegion+wr_id=token"统一模板，只是 SGE 的 addr/lkey 取自 previousValue 而非业务 Buffer。

## ④ 数据流

**构造**（Atomic.cpp:16-29）：填 context/size/type 标签（:18-20，RegionType::ATOMIC）→ `value=0`（:22）→ **`data = &value`**（:23，把成员地址当缓冲区首址）→ `ibv_reg_mr` 四权限注册（:25-26）：`LOCAL_WRITE | REMOTE_ATOMIC | REMOTE_READ | REMOTE_WRITE`。两个要害：其一，REMOTE_ATOMIC 是全库内存层**唯一**出现处——Buffer 与 RegisteredMemory 都刻意不给（Buffer.cpp:33-34，组1 02 篇），原子槽与普通内存的权限隔离在注册那一刻就完成了；其二，**这里没有 INFINITY_ASSERT 检查注册返回值**（对照 Buffer.cpp:35）——注册失败拿到 NULL MR 后续静默崩，连开断言都救不了。

**读值/写值**（Atomic.cpp:31-41）：`getValue()` 裸读、`setValueNonAtomic()` 裸写——方法名诚实得很：**没有 volatile、没有 atomic、没有任何栅栏**，就是普通 load/store。远端改了这个槽，本 CPU 只能在"恰好转过来看一眼"时发现；不存在失效通知，更不存在回调。

**端到端原子链**（跨三机件）：server：`Atomic *a = new Atomic(ctx); a->createRegionToken();` → token 随握手过网（read-write-send.cpp:60 的 memcpy 通道）；client：`qp->fetchAndAdd(remoteToken, 1, &rt); rt.waitUntilCompleted();` → 网卡在 server 内存上原子加一并把旧值 DMA 回本地 previousValue 的 8 字节（QueuePair.cpp:548-551）→ `previousValue->getValue()` 读到的就是 fetch 回的原值。server CPU 全程不知情——这就是"原子性在网卡"的字面意思。

## ⑤ 设计决策

**原子语义完全外包给网卡**：库不在 CPU 侧做任何同步（getValue 连 volatile 都不给，Atomic.cpp:31-35）。这是 RDMA 无等待同步的正统打法——锁、计数器、屏障都做成"远端 CAS/FAD 序列"，代价是本端读自己槽位的时效没有保证，而收益是远端零参与、无扩展瓶颈。

**权限隔离用注册权限位实现**：四权限注册（Atomic.cpp:25-26）+ Buffer/RegisteredMemory 三权限（无 REMOTE_ATOMIC）构成双向护栏——普通内存远程 CAS 会被网卡按 rkey 权限拒收。想让一块大内存里多个字可原子？做不到也不该做：每 8 字节一个 Atomic 就是一个独立 MR，注册开销按槽计——**计数器架构应该少而精，不是数组**。

**previousValue 复用 Atomic 而非 Buffer**：落点只需要 8 字节+lkey，复用 Atomic 顺手就有了；副作用是便捷重载全局共享 defaultAtomic（QueuePair.cpp:529/:533），多线程并发用便捷版会互踩落点（组1 05 篇坑②钉版：须自带 previousValue）。

**在途深度=1 的隐形天花板**：activate 硬编码 `max_rd_atomic=1`（QueuePair.cpp:98/:116，组1 05 篇）——单个 QP 同时只有 1 个在途原子操作，高并发原子流会在这里排队，调优须改源码重编。

## ⑥ 新人提示

上手顺序：先读 Atomic.cpp:16-29 的 20 行构造（重点盯 :23 的 data=&value 与 :25 的权限位），再对照 QueuePair.cpp:489-530 的 CAS 实现看 destination/previousValue 各自的流向。四个坑：①**别用 getValue() 自旋等远端写入**——没有 volatile，编译器完全可能把循环值缓存进寄存器；正确做法是靠 RequestToken 的完成事件或独立的计数协议；②便捷 CAS/FAD 共享 defaultAtomic，多线程必带 previousValue；③对 Atomic 铸 offset 版 token 要小心：`createRegionToken(offset)`（Region.cpp:25-27）不保证 8 字节对齐语义，奇数 offset 的 token 交给网卡原子操作是对齐违例；④Atomic 没有 resize/没有外部内存版——要 N 个计数器就 N 个对象，各自注册。验收自测：向同伴说清 destination token 与 previousValue 分别在通信的哪一端、旧值走哪条路回来。
