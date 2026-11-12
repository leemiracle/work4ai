# 01 · ibverbs-sys：FFI 裸绑定层与版本兼容 shim

> 源码：`ibverbs-sys/src/lib.rs`（614 行，下文简称 **sys lib.rs**）+ `ibverbs-sys/build.rs`｜行号锚全源码核实
>
> **勘误（任务书甄别）**：所指 `ibverbs-sys/src/verbs.rs` 不存在（src/ 仅 lib.rs）。所谓 "verbs.rs" 的内容——shim 分发函数、`ibv_wc` 手写结构——全部位于 sys lib.rs，本文按实际文件论述。

## ① 角色定位

`ibverbs-sys` 是双 crate 架构的底座：**把 rdma-core 的 C 头机械翻译成 Rust 声明**，不做安全加工。三块拼成：① bindgen 产物 include（sys lib.rs:5，构建期生成）；② 手写 `ibv_wc`（sys lib.rs:10-227，bindgen 被 `blocklist_type("ibv_wc")` 显式排除 build.rs:167）；③ 版本兼容 shim（sys lib.rs:229-613，重实现 verbs.h 里的 `static inline`——没有导出符号，bindgen 天生看不见，sys lib.rs:229-233 注释）。上层 `ibverbs` 以 `ffi::*` 引用（重命名见 ibverbs/Cargo.toml:38）；安全层能做"零成本薄壳"，前提是本层把 C 世界原样摆好。

## ② 内部结构

**sys lib.rs 三分区**：

- **`ibv_wc` 工作完成结构**（sys lib.rs:10-52）：字段与 verbs.h 逐一对齐，前五私有、后八公开。访问器（sys lib.rs:54-185）把 man page 契约编码成方法：`wr_id()`（:57）、`len()`（:71，UD 收包含 40 字节 GRH 的口径写进文档）、`is_valid()`（:80）、`error()`（:158，返回 `(status, vendor_err)`，25 种状态码语义全文搬运）、`opcode()`（:169）、`imm_data()`（:178——仅成功且 `IBV_WC_WITH_IMM` 置位时返回，并做 `u32::from_be` 网络序翻转）。
- **编译期布局断言**（sys lib.rs:190-207）：`const _` 块断言 48 字节总长、8 字节对齐、13 字段逐个偏移（wr_id@0、status@8、wc_flags@36……），补上 bindgen 对生成结构的等价检查。`Default`（sys lib.rs:209-227）以 `GENERAL_ERR` 起始，避免误当成功。
- **shim 函数群**：见④。

**build.rs 生成管线**：

- `VENDORED_HEADERS`（build.rs:8-30）11 对映射，把 git submodule `vendor/rdma-core` 的头摆成"已安装 rdma-core"目录形态。`vendored_include_dir()`（build.rs:35-57）拷贝保留 mtime 使 rerun-if-changed 精确；submodule 未初始化则提示 `git submodule update --init`（build.rs:37-41）；也可 `RDMA_CORE_INCLUDE_DIR` 指系统头（build.rs:89-96）。
- **wrapper.h 不是磁盘文件**：内存构造的字符串——verbs.h 加按 feature 追加的 efadv.h/mlx5dv.h/rdma_cma.h（build.rs:105-114），经 `header_contents`（build.rs:118）喂给 bindgen。build.rs:100-104 注释解释必须单一翻译单元：bindgen 把第一之后的输入当 `-include` 先读，谁先定义 include guard 谁遮蔽别人。
- **allowlist 与枚举策略**：`ibv_.*`/`_ibv_.*` 白名单（build.rs:129-131），特批 `verbs_context`（shim 摸 op 表，build.rs:134）与内核枚举 `ib_uverbs_advise_mr_.*`（build.rs:137）。18 个 bitmask 枚举走 `bitfield_enum`（build.rs:139-156），其余一律 NewType（build.rs:160-163）——注释言明：内核和 provider 会回传头文件没命名的值，newtype 容纳任意值而不产生非法枚举。

## ③ 外部连接（图谱节点）

| 节点 | 连接 |
|---|---|
| `file:ibverbs-sys/src/lib.rs` | 被安全层全部模块以 `ffi::*` 消费（12 条 depends_on 为图谱手补——onboard ⑧第 2 条） |
| `class:ibv_wc` | 被 completion.rs 的 WorkCompletion 包装 |
| `function:___ibv_query_port`、`function:ibv_create_qp_ex` | 分别被 context.rs:404、qp.rs:805 调用 |
| `file:ibverbs-sys/build.rs` + `function:vendored_include_dir`、`function:main` | 构建链；feature 透传链接 libefa/libmlx5/librdmacm（build.rs:62-77） |
| `file:ibverbs-sys/tests/miri_verbs_get_ctx.rs` | Miri 专属测试，`cargo +nightly miri test` 才编译 |

## ④ 数据流：shim 分发的两条路径

**路径 A：扩展 op 表（`verbs_get_ctx_op!`，sys lib.rs:248-273）**。`___ibv_query_port`、`ibv_create_cq_ex`、`ibv_create_qp_ex`、`ibv_advise_mr`、`ibv_query_rt_values_ex`、`ibv_query_device_ex` 六个 inline 动词靠嵌在 `verbs_context` 里的 op 表分发。宏四步（注释 sys lib.rs:238-247）：① 查 `abi_compat` 全 1——非扩展上下文**连前面内存都不可读**；② 从 context 指针向后读 `sz`（运行时结构大小紧贴 context 之前）；③ 新 op 在 `verbs_context` **头部追加**（"grows up"，sys lib.rs:244），运行时库结构可能比 vendored 的小，`sz >= size_of::<verbs_context>() - offset_of!(op)` 判槽位可达；④ 可达才 `context.sub(back)` 倒退读函数指针，否则 None。

消费方各有姿势：`___ibv_query_port`（sys lib.rs:314-333）拿不到 op 回退 compat 符号并先清零结构；`ibv_create_cq_ex`（:357-370）`set_errno(EOPNOTSUPP)` 返回 null；`ibv_create_qp_ex`（:400-416）有捷径——comp_mask 恰为 `IBV_QP_INIT_ATTR_PD` 时直转 legacy `ibv_create_qp`（前缀偏移断言 :374-387）；`ibv_query_device_ex`（:477-505）把 provider 返回的 EOPNOTSUPP/ENOSYS 也视为没真实现，清零回退 legacy。

**路径 B：legacy op 表直取（sys lib.rs:507-583）**。`ibv_poll_cq`（:525）、`ibv_req_notify_cq`（:542）、`ibv_post_recv`（:559）、`ibv_post_srq_recv`（:577）走 `ibv_context.ops` 旧表——libibverbs 把它**填满**（缺的 op 用 EOPNOTSUPP 桩顶替，每个建 CQ 的 provider 必实现 poll_cq），故无需可用性检查，一行 `(*(*cq).context).ops.poll_cq.unwrap()`（:530）完事。这段是**数据面热路径**，qp.rs 的 submit/post_recv 每次都经过。

**errno 跨架构钉版**（sys lib.rs:277-298）：MIPS 上 ENOSYS=89/EOPNOTSUPP=122、SPARC 90/45、其余 38/95——shim 报错必须与 C inline 全架构一致，`const` 按 `cfg!` 分派。`set_errno`（sys lib.rs:341-346）经 `safe fn __errno_location` 拿线程 errno 槽（glibc/musl 均暴露，无参恒返回调用线程槽位故标 safe）。

**Miri 测试**（tests/miri_verbs_get_ctx.rs:1-12 文档）：vendored v65 头 45 个 op 槽，老运行时 v39..v58 只 39 槽、v59..v61 42、v62/v63 43——**vendored 结构起点可能落在 provider 分配之外**。测试按各代槽位数 calloc 假 provider，验证分发永不越界（普通 cargo test 跳过，onboard ⑧第 10 条）。

## ⑤ 设计决策

1. **手写 ibv_wc 而非 bindgen**：私有字段强制走访问器（`imm_data()` 的网络序翻转不可能被忘）、`Default` 不再全零（零 status 恰是 SUCCESS）、man page 契约钉在调用点；48 字节断言兜住 repr 正确性。
2. **NewType 枚举兜住"未来的值"**：C 枚举由内核/provider 回填、头文件永远滞后；newtype 使任意回传值合法，安全层再以 `Unknown(u32)` 吸收（见 context.rs 的 PortState）。
3. **shim 忠实复刻 C inline 的错误面**：包括"返回 null 前先设 errno"细节（sys lib.rs:336-337），让上层 EOPNOTSUPP→`Error::Unsupported`（error.rs:31）归一对真硬件与 Soft-RoCE 一视同仁。
4. **bindgen 锁定 rust_target 1.85/edition 2024**（build.rs:125-127）：产物不随构建机工具链漂移，与 Bazel 构建一致——sys MSRV 的来源。
5. **vendor 头而非依赖系统包**：构建只需 libclang（链接仍需 .so）；版本由 submodule 钉住（vendored 基线 v65，Miri 测试头注释），绑定与 shim 偏移推理在同一代头上成立。

## ⑥ 新人提示

- 先读两段注释：sys lib.rs:229-247（为什么有 shim）与 :507-512（为什么那四个不需要检查）——分发设计的钥匙。
- 改 VENDORED_HEADERS 或 allowlist 后须 `cargo clean`，rerun-if-changed 只盯头文件与 build.rs。
- `ibv_create_qp_ex` 的 comp_mask 捷径（sys lib.rs:405-407）：provider 没实现扩展 op 也能建带 PD 位的 QP——安全层 lib.rs:108-113 宣称"需要扩展 verbs"的底气之一。
- Miri 复跑：`cargo +nightly miri test -p ibverbs-sys --test miri_verbs_get_ctx`。
- op 指针上的 `unwrap()` 安全**仅当指针来自合法 context**——这些函数保持 unsafe fn 的全部理由。

---
*explain 组1 · 2026-11-12｜锚全部核对自 82e8e65c 源码*
