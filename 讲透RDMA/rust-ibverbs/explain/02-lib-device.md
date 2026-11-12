# 02 · ibverbs/src/lib.rs + device.rs：crate 门面与设备发现

> 源码：`ibverbs/src/lib.rs`（403 行）+ `ibverbs/src/device.rs`（390 行）｜行号锚全源码核实

## ① 角色定位

用户触达 crate 的第一站。`lib.rs` 三职：**全库文档门面**（约 195 行 crate 级 doc）、**flag newtype 宏工厂**（`flags_newtype!`，lib.rs:204-295）、**扁平命名空间出口**（mod 声明 lib.rs:297-305 + `pub use xxx::*` lib.rs:316-324——用户永远写 `ibverbs::Context`）。`device.rs` 是最短的生产者-消费者链：`devices()` → `DeviceList` → `Device` → `open()` 交棒 Context；它也是全库唯一**不持有 verbs 句柄所有权**的资源层（设备数组由 `ibv_get_device_list` 分配）。

## ② 内部结构

**lib.rs**

- crate 文档即契约清单：快速上手示例（lib.rs:19-66 走通 devices→open→cq→pd→qp→handshake→poll 全链）、线程安全（lib.rs:126-150，含 `MLX5_SINGLE_THREADED=1` 撤销 Sync 的警告）、资源清理（lib.rs:152-158："drop panics rather than silently leak"）、fork 语义（lib.rs:160-165：Linux 5.13 起无需 ibv_fork_init，但子进程 drop 会毁父进程资源）。
- `flags_newtype!`（lib.rs:204-295）：为全库十余种 flag 类型生成统一表面——关联常量、`empty/contains`、位运算、**按名打印的 Debug**（未命名位以十六进制余数显示，lib.rs:269-274）、与 ffi bitfield 的无损互转（`From` 双向，lib.rs:283-293）。内嵌测试 `test_flags_newtype`（lib.rs:337-402）以 AccessFlags 为代表全量验一遍：未知位存活（lib.rs:371-373）、ffi 往返（lib.rs:395-401）。
- 逃生舱：`pub use ffi`（lib.rs:335）转卖 sys crate，用户不需单独依赖 ibverbs-sys 也不会版本失配。

**device.rs**

- `devices()`（device.rs:14-24）：一行 FFI `ibv_get_device_list(&mut n)` 包成 `Result<DeviceList>`，null 经 `nonnull` 翻成 `Error::GetDeviceList`。
- `DeviceList`（device.rs:28-32）：裸数组指针+长度。`unsafe impl Sync/Send`（device.rs:34-35）；**Drop 调 `ibv_free_device_list`**（device.rs:37-41）——RAII 从这里开始。`iter()`（device.rs:50）、`len/is_empty`（device.rs:55-62）、`get`（device.rs:65）、`IntoIterator for &DeviceList`（device.rs:70-76）。
- `DeviceListIter`（device.rs:79-92）：包 `slice::Iter`，`ExactSizeIterator`。
- `Device<'devlist>`（device.rs:103）：**单字段借用结构**——`&'devlist *mut ffi::ibv_device`，生命周期钉死在父列表上；`compile_fail,E0277`（device.rs:99-102）证明不能凭空造 Device。
- `Guid`（device.rs:125-151）：`#[repr(transparent)]` 包 `[u8;8]`，**按线上序存字节**——`from_be64`（device.rs:146）把 `__be64` 内存字节原样拷贝而非解释为整数（小端机上直接当 u64 会反转）；`oui()` 取前 24 位厂商号（device.rs:133）；`Display` 按 ibv_devinfo 惯例渲染四组冒号十六进制（device.rs:153-164）。
- `Device` 方法族：`open()`（device.rs:198）直通 `Context::with_device`；`name()` 返回 `Option<&CStr>`，文档列八家厂商前缀 mlx5/bnxt_re/cxgb4/efa/hns/irdma/rxe/siw（device.rs:225）；`guid()` 以全零为保留值判错（device.rs:245）；`index()` -1 时 `Error::DeviceIndexUnavailable`（device.rs:260）；`transport_type()` 直读字段转枚举，**RoCE 汇报为 Ib**（device.rs:273，RoCE 是以太网上的 IB 传输）；`as_raw()` 逃生舱（device.rs:282）。
- `TransportType`（device.rs:288-331）：`non_exhaustive` 六变体，`From` 未知值落 Unknown（device.rs:314 的 `_` 分支）。

## ③ 外部连接（图谱节点）

| 节点 | 关系 |
|---|---|
| `function:device.rs:devices` | 全库入口；examples 全部示例首行调用（loopback.rs:10 等） |
| `class:DeviceList`/`DeviceListIter`/`Device` | Device 借列表存活；`Device::open` 是去 context.rs 的唯一通道 |
| `class:Guid` | 被 context.rs 复用：`DeviceAttr::node_guid`（context.rs:1111）、QueuePairEndpoint 的 gid 字段 |
| `class:TransportType` | 与 qp.rs:72 的 Transport 标记**正交**：前者设备物理传输，后者 QP 服务类型 |
| `file:ibverbs/src/lib.rs` | mod 顺序（lib.rs:297-305）即 onboard ③ 的"阅读顺序"；`pub use ffi`（lib.rs:335）挂接 sys 层 |

## ④ 数据流：devices() 到 Context 的交接

```
devices() ──ibv_get_device_list──▶ DeviceList(裸数组, n)
   │ iter()                        │ Drop: ibv_free_device_list
   ▼                               ▼
Device<'devlist> ──name/guid/index/transport_type──▶ 选择判据
   └─.open() ──▶ Context::with_device [context.rs:62] ── ibv_open_device + async_fd 置非阻塞
```

三个走读细节：① **`open` 不真打开设备**（device.rs:191-193 文档钉版，onboard ⑧第 9 条）：设备早被内核低层驱动打开、可同时服务其他代码；此动词只**建用户态上下文**，故同一 Device 多次 open 不冲突。② **迭代器是借用而非拷贝**：`as_slice()`（device.rs:45-47）用 `from_raw_parts` 在裸数组上现造切片，`'devlist` 全程跟踪。③ **Guid 双测试**（device.rs:333-357）：`guid_from_be64_keeps_wire_order` 用真机样例 `0002:c903:00a0:7c8e`（Mellanox OUI）验线上序保真——Debug 输出能直接对上 `ibv_devinfo` 的原因。

## ⑤ 设计决策

1. **`devices()` 是函数不是关联方法**：没有"全局对象"抽象，对齐 C API 的进程级设备表。
2. **Device 用生命周期而非句柄包装保护**：`ibv_device` 只是查询句柄，复制无意义——借用 + compile_fail 把"Device 不能脱离列表"讲成类型故事而非运行时检查。
3. **flags_newtype! 集中在门面**：flag 类型散布 mr/pd/qp/completion 四文件，宏放 lib.rs 保证"改一处表面、全库一致"，测试只写一份。
4. **扁平重导出 + `deny(missing_docs)`**（lib.rs:196）：公开物全在 `ibverbs::` 一级且有文档——API 表面小而平，贴合"ibverbs 就是 verbs 的 Rust 拼写"。
5. **TransportType 的 From 带 `_ => Unknown` 兜底**：与 sys 层 NewType 策略呼应——内核枚举永远可能超前于头文件。

## ⑥ 新人提示

- 第一件事跑 `cargo run --example devinfo`（走完本篇全部 API）；无硬件则 `rdma link add rxe0 type rxe netdev <网卡>` 造 Soft-RoCE。
- **DeviceList 必须活着**才能用 Device——常见坑：把 Device 存下来再 drop 列表；借用检查器会拦（E0505/E0597），懂 `'devlist` 即秒读报错。
- name 机器内唯一、fabric 内不唯一（device.rs:206-210）；跨机器认设备用 guid（device.rs:234），换 PCI 槽位 name 会变。
- Debug 里的十六进制余数（`AccessFlags(0x40000000)` 形态，lib.rs:376-391）是未命名位——内核比你头文件新，不是 bug。
- DeviceList/Device 声明 Sync+Send（device.rs:34/104-105）：`ibv_get_device_name` 等查询线程安全（lib.rs:126-128 引 RDMAmojo）。

---
*explain 组1 · 2026-11-12｜锚全部核对自 82e8e65c 源码*
