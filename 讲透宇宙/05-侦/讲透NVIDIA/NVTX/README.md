# 讲透 NVTX（NVIDIA Tools Extension Library）

> 上游 NVIDIA/NVTX @ commit b20b676e62e09621bc8dddc62e5596908c104d06（2026-11-09 分析）
> 本地仓 /usr-data/data2/repos/agent-repos/NVIDIA/NVTX · DeepWiki 抓取 2026-10-26

## 全链状态表

| 阶段 | 产物 | 状态 |
|---|---|---|
| DeepWiki | `deepwiki/`（22 页，266,533 字符，TRUE_100） | ✅ 2026-10-26 |
| understand 图谱 | 仓内 `.understand-anything/knowledge-graph.json`（467 节点/505 边/12 层/14 步导览，validator 0 issues，fingerprints 730 文件 @b20b676e） | ✅ 2026-11-09 |
| onboarding | `onboarding/ONBOARDING.md`（8 节，40+ 行号锚全源码复核） | ✅ |
| explain | `explain/` 4 篇（nvtx3 头族/nvtxDetail 扩展机制/Rust+Python 绑定/NVTXW+sample-injection，每篇 12+ 锚） | ✅ |

图谱分层：L01 根与构建（4）/L02 CI 矩阵（19）/L03 C 核心 API 头（13）/L04 nvtxDetail 实现层（4）/L05 Rust crate（16）/L06 Python 绑定（5）/L07 Python 测试（5）/L08 C/C++ 测试（31）/L09 sample-injection（15）/L10-L11 Doxygen 双站（80+65）/L12 文档入口（3）。

## 勘误清单（图谱/常识表述 vs 源码实证）

1. **C 头族 35 个，图谱仅收录 17 个**：磁盘 `c/include/nvtx3/` = 14 个公共 API 头 + 21 个 nvtxDetail 头；图谱 17 个文件节点 = 13 个公共头（缺 `nvToolsExtPayloadHelper.h`，238 行）+ `nvtxExtImpl.h` + 3 个 `_v1` 实现头。**nvtxDetail 的 18 个实现头全部未入图**——含注入机制核心 `nvtxInitDefs.h`（595 行）/`nvtxInit.h`（499 行）/`nvtxImplCore.h`（432 行）/`nvtxImpl.h`（464 行）/`nvtxTypes.h`（318 行）。L04"扩展实现层 files=4"实为 4/22。
2. **三个 `_v1` 实现头零函数实体（宏展开无静态实体）**：`nvtxExtImplCounters_v1.h`/`Mem_v1`/`Payload_v1` 的函数体全部由 `NVTX_EXT_IMPL` 宏族以 fn_name 参数展开生成（`nvtxExtImpl.h:94-106` 状态机），无静态可寻址函数符号——tree-sitter 提取 0 属预期，非分析缺陷。
3. **Rust "mod sys" 错解**：`sys` 不是 crate 内部模块——`rust/src/lib.rs:197` 为 `pub use nvtx_sys as sys`，指向独立 workspace 成员 `crates/nvtx-sys`（`rust/Cargo.toml:5,22`，其 `src/lib.rs` 699 行 FFI 绑定未入图）。且 `rust/src` 实际 31 个 .rs，图谱仅 17：`domain/` 子模块 9 个（category/identifier×4/ranges/registered_string/resource/sync）只入了 `pthread.rs` 一个，`common/message.rs`/`test_utils.rs` 及 6 个 examples 均缺席。
4. **Doxygen 页数映射失真**：图谱 80（C）+65（C++）=145 页；磁盘 `docs/doxygen/` 106 页 + `docs/doxygen-cpp/` 63 页 = 169 页（C 站缺 26 页 dir_*/辅助导航页；C++ 站 65 节点含非 html）。另有**第三站 `docs/python/` 14 页 Python 文档站 + `docs/index.html` 整站未入图**。
5. **Python 层图谱只见 barrel、漏实现主体**：`python/src/nvtx` 磁盘 8 个 py（含 `writer.py` 64 行——NVTXW 后端事后写出、`colors.py`、`__main__.py` 54 行 `python -m nvtx` 运行器）+ `_lib/` 5 个 .pyx 共 **4417 行 Cython**（lib 1212/counters 804/writer 2185/time 127/profiler 89）全部未入图。"Cython 双后端"的准确表述：`_lib/__init__.py` 导出 `Domain`/`DummyDomain` **双态域**（工具未附着降级空操作），以及实时标注（`nvtx.py` annotate）vs 事后写出（`writer.py`+nsys_writer）双用途。
6. **17 个声明头的"函数"多为 A/W 宏声明**：`nvToolsExtCuda.h`/`CudaRt.h`/`OpenCL.h`/`Sync.h`/语义头四件套（49/55/68/140 行）的 API 全部经宏生成 A/W 双编码声明，tree-sitter 每头仅提得 1-4 个实体；语义头实为纯类型定义头（每头恰 1 个结构体）。
7. **CI 事实核对**：`.gitlab-ci.yml`（619 行）= 3 模板（`.core-template:2`/`.python-template:18`/`.rust-template:38`）+ **56 个具名 job**（脚本实证，非估算）；job 名含括号与空格需引号包裹。GitHub Actions 14 workflow，`core.yml`（479 行）为最大者。

## 阅读路径

- 快速上手：`onboarding/ONBOARDING.md` 第一节（四代实现总表）→ `explain/01`（C/C++ 头族）
- 机制深潜：`explain/02`（五态扩展槽位）→ `explain/04`（sample-injection Payload 解码）
- 语言绑定：`explain/03`（Rust workspace 双轨 + Python Cython 承重）
- DeepWiki 对照：`deepwiki/INDEX.md`（22 页，C API/Payload/Sync/CI 主题）
