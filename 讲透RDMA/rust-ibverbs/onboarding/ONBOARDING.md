# rust-ibverbs 新人导览（ONBOARDING）

> jonhoo/rust-ibverbs @ 82e8e65c（v0.9.2）｜图谱 273 节点/451 边/14 层/16 步 tour｜行号锚全源码核实（2026-11-12）

## ① 项目定位：ibverbs 的 Rust 安全封装

RDMA 数据路径零系统调用、零拷贝、微秒延迟；Linux 用户态标准接口 libibverbs 的 verbs C API 裸指针遍布、错误走 errno、资源生命周期全靠手工配对，写错即内核态崩溃。rust-ibverbs 是它的**安全 Rust 封装**，双 crate：`ibverbs-sys`（bindgen 裸绑定，`ibverbs-sys/src/lib.rs:5` include! 产物）+ `ibverbs`（安全层）。三条承诺（README.md:1-20）：零系统调用零拷贝数据面；**传输规则编码进类型系统**——UD 不带地址句柄、UD 上设 RC 超时等非法组合直接编译错（qp.rs:29-71 五个 compile_fail 文档测试）；**RAII 全覆盖**——每种资源 Drop 都调对应 destroy 动词。错误归一（`Error::Unsupported` 抹平 EOPNOTSUPP 等 errno，error.rs:31）让 Soft-RoCE 与真硬件代码同构。零成本：安全层只是所有权薄壳，数据面直落 FFI；`SendBatch`（qp.rs:1517）一次门铃提交整批（qp.rs:1607）。

## ② 快速上手

系统装 `libibverbs-dev`；无硬件用 Soft-RoCE：`rdma link add rxe0 type rxe netdev <网卡>`（README.md:186）。`cargo add ibverbs`（feature：rdmacm/mlx5/efa）。

```rust
let ctx = ibverbs::devices()?.iter().next().expect("no device").open()?; // README.md:21
let mut mr = ctx.alloc_pd()?.allocate(4096, ibverbs::AccessFlags::PERMISSIVE)?;
```

`devices()`（device.rs:14）返回 DeviceList（Drop 调 `ibv_free_device_list`，:37-41）。先 `cargo run --example devinfo` 确认环境，再跑 loopback（第④节）。

## ③ 架构总览：14 层

| 层 | 内容 | 代表锚 |
|---|---|---|
| L01/L02 | README 门面；CI 四 workflow + configure-ci.sh | README.md、.github/workflows/ |
| L03/L04 | Cargo 清单（`ffi` 重命名、feature 透传）；Bazel 替代构建 | ibverbs/Cargo.toml:38 |
| L05 | **FFI 绑定**：vendored 头 bindgen+ibv_wc 访问器+版本 shim+Miri | ibverbs-sys/src/lib.rs |
| L06 | **安全层门面与错误**：flags_newtype!、扁平重导出、统一 Error | lib.rs:204、error.rs:26 |
| L07/L08 | 设备与上下文；保护域与内存注册 | device.rs:14、pd.rs:69、mr.rs:87 |
| L09 | **队列对数据面**（qp.rs 3519 行全库最大）+ SRQ | qp.rs:477、srq.rs:44 |
| L10 | 完成与寻址：CQ/25 种 WC 状态码；GID/AH | completion.rs:1072、address.rs |
| L11/L12 | 硬件扩展（EFA SRD、mlx5 dmabuf）；rdmacm 连接管理 | efa.rs:45、rdmacm.rs:1604 |
| L13/L14 | 六个示例；集成测试矩阵（2619+1464 行，#[ignore]） | ibverbs/examples/、ibverbs/tests/ |

记忆钩子：L05 是 C 的世界，L06-L10 是 Rust 的世界，L11-L12 厂商扩展，L13-L14 证明层；安全层 mod 声明顺序（lib.rs:297-305）即阅读顺序。

## ④ 核心链路：examples/loopback.rs 全链

74 行走完最短闭环：①`devices()`（loopback.rs:10）→`.open()`（:15）②`ctx.create_cq(16).build()`（:18，builder 在 context.rs:125，build 在 completion.rs:321）+`alloc_pd()`（:19，context.rs:230）③`ctx.routable_gid(1)`（:23，context.rs:292）挑可路由 GID④`pd.create_qp::<Rc>(&cq,&cq,1)`（:29，pd.rs:174）产 `QueuePairBuilder<Rc>`（qp.rs:477），`.set_gid_index()`（qp.rs:600）后 `.build()`（:895）产 `PreparedQueuePair`（:1033）；create_qp 此刻即查端口并要求 ACTIVE（pd.rs:182-183）⑤`endpoint()`（:38，qp.rs:1175）打包 `QueuePairEndpoint`（:1076）交换后 `handshake(endpoint)`（:39，qp.rs:1364）自动走完 Reset→Init→RTR→RTS 状态机（qp.rs:134）⑥`pd.allocate(16, PERMISSIVE)`（:41，pd.rs:255）⑦先收后发：`qp.post_recv([RecvRequest::new(2,&[mr.slice(..8)])])`（:46，qp.rs:2710）→`start_send()`（:47，:2751）→`batch.op().signaled().send(1,&[mr.slice(8..)])`（:48，send 在 :1669）→`submit()`（:49，:1607 单次门铃）⑧`cq.poll()`（:54，completion.rs:1117）→`next()`（:55，:1039）→`wc.ok()`（:56，completion.rs:749 把失败 WC 翻成 WcError），按 `wc.wr_id()`（:742）分派并校验字节（:66）。unsafe 仅 post_recv/submit——批量描述符由用户构造，无法静态穷尽校验。

## ⑤ 关键模块深讲

**RAII 所有权链**：`Context`（context.rs:43）内是 `Arc<ContextInner>`（:44，Drop 关设备）；`ProtectionDomain`（pd.rs:69）可 clone 共享；子资源反向持有父 PD——MR 的 `MemoryRegionInner._pd`（mr.rs:59-60）、SRQ 的 `_inner._pd`（srq.rs:6）——**父对象由类型系统自动延寿**。

**MemoryRegion<O> 泛型所有权**（mr.rs:87）：`O` 是缓冲所有者——`allocate` 产 `MemoryRegion<Box<[u8]>>`，`register_from_raw`（pd.rs:295）产 `MemoryRegion<()>`，`register_dmabuf`（pd.rs:327）注册 DMA-BUF。两字段 ManuallyDrop（mr.rs:90-91），Drop 顺序手工编排：**先 dereg 后释放缓冲**；dereg 失败 panic 并故意泄漏缓冲（mr.rs:84-86）——设备可能仍持 DMA 引用，宁漏不炸。`slice()`（mr.rs:160）借出带 lkey 的 `LocalMemorySlice`（:198）；`remote()`（:134）产可序列化 `RemoteMemorySlice`（:261）——远端 rkey+地址即单边操作的"指针"。

**Qp/Srq 队列族**（qp.rs）：sealed `Transport` trait（qp.rs:72）+ 标记 `Connected`（:76）/`Reliable`（:81）/`Datagram`（:85）+ Rc/Uc/Ud（:92/:97/:106）与 EFA 的 Srd（efa.rs:45）。能力约束落在签名：`set_timeout` 要求 `T: Reliable`（qp.rs:945）、`handshake` 要求 `T: Connected`（:1364）、UD 走 `activate(qkey)`（:1225）、`batch.to(ah,..)` 要求 `T: Datagram`（:1564）。`SendBatch`（:1517）**Drop 即 abort**（:1621-1626）：未 submit 的批次调 wr_abort；submit 用 forget 跳过。`SendOp`（:1640）修饰符链完必须以 opcode 收尾。SRQ（srq.rs:44）以 `Arc<SharedReceiveQueueInner>`（:45）跨 QP 共享，`set_limit`/`set_max_wr`（:101/:118）在线调水位，`post_recv`（:170）同为 unsafe。

**mlx5 加速路径**（feature 门控）：`register_dmabuf_data_direct`（mlx5.rs:34）把 GPU 显存注册为 data-direct MR（网卡直访显存绕过主机内存）；`mlx5_data_direct_sysfs_path`（:91）查关联设备；tests/mlx5.rs 验证非 mlx5 硬件上被正确拒绝。

## ⑥ 设计决策

1. **`ffi = { package = "ibverbs-sys" }` 重命名**（ibverbs/Cargo.toml:38）：全库以 `ffi::ibv_*` 引用，贴 C 原文；Bazel 侧 `ibverbs/BUILD.bazel` 同名 alias 复刻同一约定。
2. **共享资源三策略**（勘误：任务书所称 `Arc<RawIbvMr>` 源码中不存在）：Context 用 `Arc<ContextInner>`（context.rs:44，子资源各持克隆）；SRQ 用 `Arc<SharedReceiveQueueInner>`（srq.rs:45，跨线程 clone 给多 QP）；**MR 不共享**——泛型所有权 `MemoryRegion<O>`（mr.rs:87）+ ManuallyDrop 顺序 Drop。三种策略各匹配 verbs 语义。
3. **raw 指针边界收敛**：每类资源有 `as_raw()` 逃生舱口（device.rs:282、pd.rs:86、mr.rs:128）；`register_from_raw`（pd.rs:295）收外部裸指针以 unsafe+断言收口。公开 unsafe 仅三个数据面动词。
4. **sys 层版本 shim**（ibverbs-sys/src/lib.rs:230-546）：`ibv_create_cq_ex` 等在 verbs.h 是 C inline，bindgen 看不见，手工重实现 ops 表分发（ibv_poll_cq :525）；旧运行时槽位缺失返回 EOPNOTSUPP 与 C 对齐；Miri 测试构造 v39..v63 假 provider 验证分发不越界。
5. **错误模型集中**（error.rs:26）：`#[non_exhaustive]` enum 携带 errno+操作名；`operation()` 返回 `&'static &'static str` 让 Error 保持两 word（error.rs:33），热路径零分配。

## ⑦ 新人学习路径（16 步 tour）

- 第 1 天·理解承诺：step-01 README 与根 Cargo.toml → step-02 安全层门面与 ffi 重命名 → step-03/04 sys 层（头布局、shim、Miri）。
- 第 2 天·跑通：step-06 devices/devinfo → step-10 loopback 对照第④节 + doorbell_batching 看批处理收益 → step-05 error.rs。
- 第 3-5 天·深潜：step-07 Context/CompletionChannel + event_loop → step-08 PD/MR（重点 slice 与 RemoteMemorySlice 序列化）→ step-09 通读 qp.rs（Transport 类型系统与 SendBatch Drop 语义是核心考点）。
- 第 2 周·扩展与验证：step-11 address/efa → step-12 mlx5 → step-13 rdmacm 免握手 → step-14 集成测试矩阵（查 API 行为先看 tests/loopback.rs）→ step-15/16 CI 与 Bazel。

练习：①改两条 wr_id 各发一次；②换 UD 体会编译错；③批量 8 条对比逐条提交。

## ⑧ 已知坑与勘误

图谱侧（引用批回执计数先问口径）：1. merge 的 `tested_by` 以 basename 判定测试归属，对 Rust `tests/` 目录全盲，18 条手补；2. scanner 漏跨 crate `use crate::{重导出}` 10 条；FFI 全走 `ffi::*` 被当外部包滤掉，12 条 depends_on 手补（L03"12 条边"根因）；3. `Arc<RawIbvMr>` 不存在（见⑥勘误）。

源码/使用侧：4. **edition 2024 uniform paths**（ibverbs/Cargo.toml:4，MSRV 1.85 由 sys 继承）：`use ffi::...` 直指依赖 crate，老工具链报错。5. **集成测试默认 #[ignore]**：CI 现场 modprobe rdma_rxe 起 Soft-RoCE 才跑；本地 `cargo test -- --ignored` 且先造 rxe。6. **SendBatch 忘 submit 会 abort 整批**（qp.rs:1621）：hns owner-doorbell 在 opcode 返回时可能已执行请求（:1599），别当回滚用。7. **dereg 失败 panic 并泄漏缓冲**（mr.rs:84-86）：生产环境须接 unwind。8. **EFA 特例**：SRD 每请求必产完成，EFA 拒绝 unsignaled/solicited（qp.rs:102-105）。9. **`Device::open` 不真打开设备**（device.rs:191-193）：设备由内核驱动打开，只建用户态上下文。10. **Miri 测试栈**：miri_verbs_get_ctx.rs 只在 `cargo +nightly miri test` 下跑，普通 cargo test 跳过。

---
*understand-anything onboarding 子代理，2026-11-12｜图谱 commit 82e8e65c｜86 锚全源码核实*
