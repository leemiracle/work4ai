# 03 · Rust crate 与 Python 绑定：两代安全封装

## 角色定位
Rust（`rust/src/lib.rs`，474 行）与 Python（`python/src/nvtx/nvtx.py`，485 行）是 NVTX 的两代语言绑定，目标一致：把 C 联合体语义的属性槽位封装成各自语言的惯用类型系统。Rust 侧额外支持 no_std 嵌入式场景，Python 侧额外提供 numpy dtype→结构化负载的自动 schema。

## 内部结构
**Rust 是 cargo workspace**：安全 crate `nvtx` + 原始 FFI crate `nvtx-sys`（`crates/nvtx-sys/src/lib.rs`，699 行；`rust/Cargo.toml:5` workspace members、`rust/Cargo.toml:22` path 依赖、版本 2.0.0）。注意 `sys` 不是内部 mod——`rust/src/lib.rs:197` 是 `pub use nvtx_sys as sys` 外部 crate 别名（图谱曾误读为 mod，已修正）。三级 feature 档：std/alloc/core-only（`rust/Cargo.toml:88-90` 的 std→alloc→nvtx-sys/std 特性链），`lib.rs` 定义 `TypeValueEncodable` trait 作为值→载荷槽位的编码协议。

核心 `rust/src/domain.rs`（1070 行）条件编译双轨：std 档 `HashMap`+`std::sync::Mutex`（`rust/src/domain.rs:25-27`），no_std+alloc 档 `BTreeMap`+`spin::Mutex`（`rust/src/domain.rs:14,23`）；注册字符串/类别缓存在 `rust/src/domain.rs:268-269`。值类型族：`str.rs`（ASCII CString/UTF-16 WideCString 双编码+`StrError` 内嵌 NUL 定位）、`color.rs`（u32 位段 ARGB+CSS 颜色名）、`payload.rs`（泛型负载）、`category.rs`（原子计数器分配 id）、`ranges.rs`（`Range`/`LocalRange` 双 RAII）、`cuda.rs`/`cuda_runtime.rs`（句柄枚举→`nvtxNameCu*`/`nvtxNameCuda*`）。线程标识 `domain/identifier/pthread.rs:10` 用 `cfg(not(target_os = "macos"))` 排除 barrier/spinlock（`:21-24`）。生态件 `rust/src/tracing.rs:54` `NvtxLayer` 实现 tracing_subscriber `Layer`（`impl:99`，`on_enter:143`/`on_exit:165`，字段经 `NvtxVisitor:188` 记为 payload）。

**Python 的实现主体在 Cython**：`_lib/` 五个 .pyx 共 4417 行（`lib.pyx` 1212/`counters.pyx` 804/`writer.pyx` 2185/`time.pyx` 127/`profiler.pyx` 89），`_lib/__init__.py` 导出 `Domain` 与 `DummyDomain`/`dummy_domain` 双态域（工具未附着降级空操作）。纯 Python 层：`nvtx.py` 的 `annotate` 上下文管理器/装饰器、`get_domain:141`（`@lru_cache:136` 缓存）、`mark:256`/`push_range:309`/`pop_range:366`/`start_range:381`/`end_range:441`（自动类型推导）、`numpy_dtype:55`、`enabled:454`；支撑 `_dtype_validation.py`/`_metadata.py`（dtype→schema 元数据+缓存键）。

## 外部连接
Rust 全部 FFI 落在 nvtx-sys 一处，`native_types.rs` 再从 nvtx_sys/libc 转发 CUDA 句柄与 pthread 原语。Python `nvtx.py` 之下是 `_lib` Cython 扩展直调 C API；顶层 `writer.py`（64 行，docstring `:19-29`）则反向把**预先采集**的事件经 NVTXW 后端写出（Nsight Systems nsys_writer 集成），`__main__.py`（54 行）提供 `python -m nvtx` 的 cProfile 式 Profile 运行器。测试对照：Rust `rust.yml` CI 五 job（含 msrv 1.77 与全 feature no_std check）；Python `tests/conftest.py`（992 行）`build_injection:83` 现场编译 mock 注入库、`NvtxEventsReader:361` ctypes 镜像读事件流、常量手工镜像（`COUNTER_FLAG_LIMIT_MIN:47`/`MAX:48`）防生产 schema 错误。

## 数据流
Rust：builder（`EventAttributesBuilder`）→ `encode()` 按默认编码打包进属性槽位 → nvtx-sys FFI 调 C API → nvtxDetail 槽位机制决定转发/降级。域内注册字符串先查缓存（`rust/src/domain.rs:268`），未命中才调 `nvtxDomainRegisterStringA` 并缓存句柄。Python：`annotate`/事件函数推导值类型 → `_lib` Cython 层构造属性 → 同一 C 路径；numpy 数组走 `_metadata` 的 schema 注册路径（`nvtx.py:55`）。

## 设计决策
- Rust **缓存前置**：注册字符串/类别在域内缓存，把"每次标注查句柄"降为 map 命中——但全局域拒绝跨域注册字符串（`lib.rs` 的 `strip_registered_message_for_global_context` 防护），语义安全优先。
- **双轨条件编译**而非 feature 门控两套文件：同一 `domain.rs` 双 map/Mutex 实现，避免代码分叉。
- Python **Cython 承重**：热路径（属性构造、push/pop）全在 .pyx，纯 Python 层只做装饰器语义与类型推导。
- `DummyDomain` 双态：未附着时同 API 零异常零开销，测试无需 mock 即可跑语义。

## 新人提示
Rust 侧从 `category.rs`（内嵌单测）入手最快；改 `domain.rs` 缓存记得两条编译轨都要 `cargo check --no-default-features`。Python 侧先读 `test_basic.py` 对照 `conftest.py` 的 verify_* 断言族理解事件如何被逐字段核对；`test_payloads.py` 全部测试在 `if np is not None:` 条件块内（无 numpy 自动跳过）。写集成时优先 `annotate` 装饰器，需要跨线程区间才用 `start_range/end_range` 句柄模式。
