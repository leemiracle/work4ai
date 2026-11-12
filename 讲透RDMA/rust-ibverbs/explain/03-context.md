# 03 · context.rs：Context、Arc 共享与异步事件

> 源码：`ibverbs/src/context.rs`（1554 行，安全层第二大文件）｜行号锚全源码核实

## ① 角色定位

`Context` 是 **verbs 世界的根句柄**：一个设备一次用户态会话。所有资源（PD/CQ/comp channel）从它派生，所有查询动词（设备能力、端口属性、GID 表、硬件时钟）挂在它身上。它也是**共享策略第一现场**：内部是 `Arc<ContextInner>`（context.rs:44），克隆即共享、最后一个引用负责 close——onboard ⑥2 钉版的三策略（Context 用 Arc、SRQ 用 `Arc<SharedReceiveQueueInner>`（srq.rs:45）、**MR 不共享**）中 Context 是最纯一档。文件后半（context.rs:456-1243）是一排查询结果类型化包装（Mtu/PortState/PortSpeed/PortWidth/LinkLayer/PhysicalState/DeviceAttr/PortAttr），把 C 端裸枚举翻译成带 `Unknown` 兜底的安全类型。

## ② 内部结构

```
Context (derive Clone, context.rs:43)
 └─ inner: Arc<ContextInner>            context.rs:44
     ├─ ctx: *mut ffi::ibv_context
     └─ Drop → ibv_close_device          context.rs:24-32
```

方法五组：**构造**——`with_device`（context.rs:62，被 Device::open 调）、`shared`（context.rs:80，rdmacm 专用：按设备地址的 Weak 缓存 :84-95）；**派生**——`create_cq`（:125，返回 builder）、`create_comp_channel`（:142）、`alloc_pd`（:230-236）；**异步事件**——`async_fd`（:149，返回 `BorrowedFd`，open 时已置非阻塞 :71）、`poll_async_event`（:169）、`wait_async_event`（:203）；**查询**——`gid_table`（:248）、`routable_gid`（:292）、`query_gid`（:306）、`num_comp_vectors`（:330）、`query_device`（:347）、`query_device_ex`（:372）、`query_port`（:400）、`query_rt_values_ex`（:436）、内部 `rd_atomic_limits`（:354）；**逃生舱** `as_raw`（:419）。

配套：`AsyncEvent<'ctx>`（context.rs:488）、`AsyncEventType`（:607，22 具名变体+`Unknown(u32)`）、`HcaClock`（:740，wrapping Sub :749-757）、三个 Attr 结构（DeviceAttr :1107 / DeviceAttrEx :1165 / PortAttr :1249，全部 `Deref` 到 ffi 结构保住全字段可达）。

## ③ 外部连接（图谱节点）

| 节点 | 关系 |
|---|---|
| `class:Context` | 被 device.rs:199 创建；被 pd.rs:48 反向持有（ProtectionDomainInner.ctx）——**父句柄由子资源保活**从 PD 开始 |
| `function:with_device`/`function:shared` | 前者接 Device::open，后者专供 rdmacm 的 ConnectionManager |
| `function:poll_async_event`/`function:wait_async_event` | examples/event_loop.rs 主循环驱动力；SrqLimitReached（context.rs:644）是 srq.rs 水位机制的消费者 |
| `function:gid_table`/`function:query_gid` | 供 pd.rs:182 的端口查询链与 qp.rs:1178 的 endpoint() 取 GID |
| `function:query_port` | **经 sys 层 shim `___ibv_query_port`**（context.rs:404 调用，实现在 sys lib.rs:314）——为拿 `active_speed_ex` 等扩展字段不走 compat 符号 |
| `function:query_rt_values_ex` | 同名 sys shim（sys lib.rs:452）消费方；HcaClock 与 completion.rs 完成时间戳对表 |
| `class:PortAttr`/`class:Mtu` 等 | pd.rs:417 的 require_active 消费 PortState；qp.rs:537 消费 active_mtu；Display 输出 C 头文件名（context.rs:694-720） |

## ④ 数据流：三条关键方法走读

**1. open 与失败自愈（context.rs:62-73）**。`nonnull(ibv_open_device)` 成功后立刻把 async_fd 设非阻塞——失败则局部 `context` 随 `?` 返回 drop，Arc 归零触发 `ibv_close_device` 把半开设备关回去（context.rs:69-71 注释明言）。RAII 管构造失败的标准姿势。

**2. 异步事件的"读即 ack"（context.rs:169-191）**。常规 C 写法 get→用→ack 三步，但 libibverbs 会**阻塞销毁**事件所指的 QP/CQ/SRQ 直到 ack（context.rs:182-184）——攥着事件不放（或泄漏）能把对象 Drop 永久挂死。本 crate 的解法：读到事件先在 ack 前抢救 `qp_num`（`event_qp_num` context.rs:578-597，QP 类事件在指针仍有效时解引用），然后**立刻 ack**，`AsyncEvent` 只剩纯数据。`wait_async_event`（context.rs:203-217）循环等 fd 可读再 poll，并处理"fd 可读但事件被别线程抢走"的竞态（context.rs:211-213）。

**3. routable_gid 挑选链（context.rs:457-465 + 测试 context.rs:1396-1426）**。GID 表非每条可路由：`on_port → filter(RoceV2) → find(is_ipv4_mapped)`，退到"任意 RoCEv2"，再退"端口第一条"（IB 的 index 0 总可路由；RoCE v1 只通同网段）。测试用 7 条混合表验证选中 5、截断后选 1、IB 表选 0 三分支（context.rs:1416-1425）——把网络运维知识（RoCE v2 over IPv4 才可跨网段）编码进 API 的范例，loopback.rs:23-27 直接消费。

查询组 buf 细节：`gid_table` 先 query_device 拿端口数、逐端口累加 `gid_tbl_len` 定容量（context.rs:251-255）再调 `_ibv_query_gid_table`（下划线开头的导出符号 :258）；`query_port` 走 shim 拿全尺寸结构（:402-404 注释：compat 符号会把 `port_cap_flags2/active_speed_ex` 留零）；`query_rt_values_ex` 把 C ABI 塞在 `timespec` 里的**原始 tick 计数**折叠回 u64（:445-452，mlx5 把整个计数器放 tv_nsec）。

## ⑤ 设计决策

1. **Clone = Arc 克隆**（context.rs:39-40 文档"cheap (reference counted)"）：子资源各持克隆（PD 的 ctx、CQ builder 的 `self.clone()` context.rs:126），形成引用计数保活链——Context 生命周期由最长下游资源决定，最后关灯。
2. **`shared` 只服务 rdmacm**（context.rs:75-80）：按设备地址键控+Weak。注释点明以地址为键的安全性：context 持设备引用，条目还能 upgrade 时地址不会被复用。普通用户无需感知——每次 open 就是新 Context。
3. **异步事件牺牲存储换解放**：提前 ack 使 `AsyncEvent` 不能再携带对象指针——只留数值 `qp_num`，原始 `element` 联合体经 `as_raw()` 暴露但要求"只在仍持 wrapper 时解引用"（context.rs:543-551）；`'ctx` 生命周期只是文档性的（context.rs:493-495 注释自认可去）。
4. **查询包装 Deref + as_raw 双轨**：新类型既给常用字段类型化方法（`fw_ver()` 处理内嵌 C 字符串 context.rs:1122-1126），又 Deref 到 ffi 让冷门字段照常可达——不在"安全"与"全功能"间二选一。
5. **non_exhaustive + Unknown(u32) 贯穿**（PortState context.rs:843、PortSpeed context.rs:900……）：与 sys 层 NewType 策略（01 篇⑤2）同一防线两层。

## ⑥ 新人提示

- **Clone 语义对照**（onboard ⑥2 考点）：`Context` 克隆=共享 ibv_context；`ProtectionDomain`（pd.rs:68-71）同样 Arc 共享；`SharedReceiveQueue`（srq.rs:44-46）共享给多 QP；**`MemoryRegion` 无 Clone**（05 篇）。记忆钩子：**句柄类共享、缓冲类独占**。
- `query_port` 结果别长缓存：端口属性会被子网管理器/硬件改（context.rs:393-394），每用每查。
- `wait_async_event(None)` 无限等待，且 `DeviceFatal` 后**不再有任何事件**（context.rs:626-629）——事件循环要为此终止态设计逃生（event_loop.rs 演示）。
- `num_comp_vectors`（context.rs:330）是 `set_comp_vector` 上界；忙 CQ 摊向量=摊 CPU 中断（context.rs:327-329）。
- `HcaClock` 相减 wrapping（context.rs:749-757 + 测试 context.rs:1429-1435）：窄时钟（ionic 48 位）先 `& mask` 再比较；跨一个回绕会大小倒置。
- fork 警告（lib.rs:160-165）：子进程 drop 继承的 Context 会替父进程 close 设备——子进程要么 exec 要么不 drop。

---
*explain 组1 · 2026-11-12｜锚全部核对自 82e8e65c 源码*
