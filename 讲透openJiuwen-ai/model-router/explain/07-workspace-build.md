# 07 · Cargo workspace 构建体系：五成员、maturin 与类型桩

## ① 角色定位

这个仓是「Rust 内核 + Python 门面」的双语言工程，两半的接缝全部由构建体系承担：根 `Cargo.toml` 是 virtual workspace（无 `[package]`），五个 crate 各管一层（protocol→state→algorithms→runtime→py）；`pyproject.toml` 把最上层的 `crates/py` 交给 maturin 编成原生扩展 `_openjiuwen`；`typings/` 与 `python/openjiuwen/_openjiuwen.pyi` 负责让 Pyright/Pylance 在没有编译产物时也能跳转。**`.pyd`（Windows）/`.so`（Linux）不在仓里**——克隆下来只有类型桩 `_openjiuwen.pyi` 代表它的存在，真身要靠 `maturin develop` 现场编译，这是新人第一个要建立的认知。

workspace 在 `Cargo.toml:3-9` 列出五成员，而 `Cargo.toml:10-15` 的 `default-members` 只有前四个。这一行排除 `crates/py` 的意义：**`cargo build`/`cargo test` 默认不碰 PyO3 绑定**。绑定层依赖 `pyo3` 且产出 cdylib，需要 Python 解释器环境配合才有意义；把纯 Rust 内核的日常构建与 Python 侧解耦，CI 里可以只跑内核测试而不装 Python 工具链。`pyo3` 版本钉在 0.23 且带 `abi3-py38`（`Cargo.toml:30`）——abi3 稳定 ABI 让一个扩展兼容 3.8+ 全部 CPython，与 `pyproject.toml:9` 的 `requires-python = ">=3.8"` 严格对齐。

## ② 内部结构

**maturin 桥**：`pyproject.toml:1-3` 声明 `build-backend = "maturin"`（>=1.7,<2），`[tool.maturin]` 四件套（`pyproject.toml:21-25`）是整个接缝的坐标：`manifest-path = "crates/py/Cargo.toml"` 指回 Rust 侧、`python-source = "python"` 指向纯 Python 包目录、`module-name = "openjiuwen._openjiuwen"` 决定扩展落在包内、`features = ["extension-module"]` 打开 cdylib 编译开关。

**crates/py 的双重身份**：`crates/py/Cargo.toml:9-11` 写 `crate-type = ["cdylib", "rlib"]`，同一个 crate 既要编成 Python 扩展（cdylib）又要作为普通库被 Rust 测试引用（rlib）。`crates/py/Cargo.toml:13-15` 定义 feature `extension-module`，转发到 `pyo3/extension-module`。

**build.rs 的开关判断**：`crates/py/build.rs:5-10` 读环境变量 `CARGO_FEATURE_EXTENSION_MODULE` 判断当前构建是否在产扩展；`:12-16` 只有为真时才调用 `pyo3_build_config::add_extension_module_link_args()` 加 cdylib 链接参数。注释写明原因：同一 crate 的 rlib 构建**不得**收到这些链接 flag——没有这个判断，rust-analyzer 或 `cargo check` 走的非扩展构建会被污染。

**链接器兜底**：`.cargo/config.toml:1-4` 是开发机环境补丁——stable-x86_64-pc-windows-gnu 工具链下 PATH 里的 LLVM-MinGW gcc 缺 libgcc，`rustflags = ["-C", "link-self-contained=yes"]` 强制走 rustup 自带 self-contained 链接器。这是本仓开发环境为 Windows 的直接物证。

**类型桩双份**：`python/openjiuwen/_openjiuwen.pyi` 200 余行手写桩，首行注释点破分工——Pylance/Pyright 靠它跳转，运行时仍加载 `.pyd`。`pyproject.toml:31-36` 与 `pyrightconfig.json` 都设 `stubPath = "typings"`，后者还把 `typeCheckingMode` 定为 basic（`pyrightconfig.json:6`）。`typings/pytest/__init__.pyi:3-8` 给 `importorskip` 补了签名——类型检查环境不必装 pytest。

## ③ 外部连接

- **向 Rust 内核**：`crates/py/Cargo.toml:18-22` 依赖四个 workspace crate，版本经 `Cargo.toml:23-27` 的 path 依赖统一。
- **向 pytest**：`pyproject.toml:27-29` 设 `testpaths = ["tests"]` + `pythonpath = ["python"]`——测试**不装包**直接 import 源码树的 `openjiuwen`；`tests/conftest.py:7-8` 再把 `python/` 插到 `sys.path` 最前，注释明说是防 site-packages 旧 wheel 挡住本地改动。扩展本体仍需 `maturin develop` 编进该目录。
- **向可选依赖**：`pyproject.toml:11-19` 两个 extra：`x-router`（torch>=2.0+transformers>=5.0，分类器用）、`x-router-bandit`（numpy>=1.24，BanditStore 向量化用）。注释特意写明「缺 extra 只能跑启发式模式，且必须显式 `enabled = false`，省略 `[x-router.classifier_model]` 段是错误而非回退」。
- **向 Rust 集成测试**：`crates/runtime/Cargo.toml:33-34` 用 `[[test]]` 把仓库根的 `tests/react_agent.rs` 挂到 runtime crate 名下——根目录不是 package，测试文件必须由某成员认领才进 `cargo test`。

## ④ 数据流

一次完整构建-使用链：`maturin develop` 读 `pyproject.toml` → 转发编译 `crates/py`（带 extension-module feature）→ `build.rs:13-15` 注入链接参数 → 产出 `_openjiuwen.abi3.so/.pyd` 落进 `python/openjiuwen/` → 运行时 `import openjiuwen` 经 `python/openjiuwen/__init__.py:75` 加载它；同时 IDE 读同目录 `.pyi` 桩提供补全。另一臂：`cargo test`（default-members）跑纯 Rust 内核 + react_agent 集成测试，全程不触发 PyO3。双臂各走各的，唯一共享的是 workspace.dependencies 里的版本钉版。

## ⑤ 设计决策与权衡

1. **default-members 排除 py 是「按消费者分割」而非「按依赖分割」**：五个成员的依赖是线性叠的，但消费者有两类（Rust 工程师 / Python 宿主），构建入口按消费者分账。
2. **手写 .pyi 而非 pyo3 自动生桩**：pyo3 生态有 `pyo3-stub-gen` 类工具，本仓选择手写——桩是 API 文档的一部分（如 `_openjiuwen.pyi:116` 的 `Decision = ModelSelection` 别名、`:199-202` 四个 outcome 字符串常量），与 `lib.rs:141-145` 的模块注册一一对应，人肉维护反而强制每次改 API 都过一遍桩。
3. **abi3-py38 牺牲部分新 API 换一版多平台**：0.23+abi3 组合放弃了 free-threaded 等新特性，换来免多版本轮转，对一个路由库是正确取舍。
4. **`.cargo/config.toml` 入仓**：通常机器特定配置不进版本库，这里入仓说明团队统一 Windows-gnu 开发环境，代价是 Linux 贡献者需要确认该配置无副作用（实际只作用于 windows-gnu target，无害）。

## ⑥ 新人提示与坑

- **clone 后 `import openjiuwen` 报 ImportError 是正常的**：`python/openjiuwen/__init__.py:94-95` 把扩展加载失败静默降级（NativeRouter=None），真正报错在用到 Router 时（`python/openjiuwen/__init__.py:117-123` 提示 `maturin develop`）。别以为是装错了。
- **改了 Rust 代码 Python 侧行为没变**：九成是忘了重新 `maturin develop`，conftest 优先源码树也救不了没编译的扩展。
- **`cargo build` 看不到 crates/py 的错误**：它在 default-members 之外，要么 `cargo build -p openjiuwen`，要么走 maturin。
- **README 目录树漏了 `config/stage_router.toml`**（已知勘误）：仓库里真实存在四份 config（edge/cloud/stage_router/x-router-example），stage_router 配套的 `algo-stage_router` feature 在 `crates/runtime/Cargo.toml:10-17` 的默认 feature 列表里开启，按 README 目录树找文件会扑空。
- **pyright 报 pytest 缺失**：确认 `stubPath = "typings"` 生效（两处配置都可能被 IDE 本地设置覆盖）。
