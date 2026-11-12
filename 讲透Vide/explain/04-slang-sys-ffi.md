# 04 · slang FFI：把 C++ 解析器请进 Rust（crates/slang-sys）

## 角色定位

vide 不重写 SystemVerilog 解析器，而是把业界最完整的开源解析器 slang（C++，位于 `third_party/slang` 子模块）以静态库形式链接进 Rust 二进制。`crates/slang-sys` 就是这座桥：`build.rs` 负责「编 slang + 生成 Rust 定义 + 编 cxx 桥 + 配置链接」四段流水线，`src/` 下的 wrapper.cpp/ffi.rs 对定义桥两侧，各 `*.rs` 模块把 CXX 生成的原始 API 包装成符合 Rust 习惯的类型。这是全仓唯一涉及 C++ 的 crate，也是 WASM 通道（vide-lsp-wasm）能整体编译进 Emscripten 的关键前提。与 bindgen 全自动方案不同，这里混合了三种手法：**Python 脚本生成枚举/AST 绑定、CXX bridge 定义共享类型、手写 wrapper.cpp 补齐不透明接口**。

## 内部结构

**build.rs（455 行）** 顶部常量即地图：L8 `SLANG_SOURCE_DIR = "../../third_party/slang"`，L21-27 列出三组桥文件——`FFI_FILES`（compilation/diagnostic/syntax 三份 `ffi.rs`）、`WRAPPER_HEADERS` 与 `WRAPPER_FILES`（对应的 wrapper.h/cpp）。`main()`（L29-56）按四阶段执行并各自计时（`log_phase` L58-60）：`generate_rust_defs` → `build_slang` → `build_cxx_bridge` → `setup_linking`。

`generate_rust_defs`（L194-252）并行跑五个 Python 生成器（L197-231 的表：syntax_kind/token_kind/trivia_kind/diagnostic/ast），输入是 slang 源码树的 `syntax.txt`、`tokenkinds.txt`、`diagnostics.txt` 与 `Diagnostics.h` 头，输出到 `OUT_DIR` 的 .rs 文件——**slang 升级时枚举与 AST 访问器自动跟上**，而不是手写几千行绑定。

`build_slang`（L254-347）用 cmake crate 编静态库。缓存目录按「target × 环境指纹 × profile」三维隔离：L92-95 build_dir 拼入 target，L109-142 `cmake_cache_key` 把 CC/CXX/CMAKE_GENERATOR/toolchain 等环境变量排序后算 FNV-1a hash（L131 注释言明这只是缓存命名空间不是安全边界）——避免不同 toolchain 共享 CMake 缓存的脏状态。L293-303 关闭 slang 的测试/工具/pylib 与 mimalloc，L305-313 是 Emscripten 专属分支（`-fwasm-exceptions`、`CMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY`），L334-344 修复 cmake-rs 在 MSVC Release 下丢失 /O2 的问题。

`build_cxx_bridge`（L349-396）是 CXX 的主场：L357-368 从 `DEP_CXXBRIDGE1_HEADER` 找到 cxx.h 并复制进 `target/slang-sys/clangd/include`（给 clangd 提供跳转用的头文件聚合点，L394-395 还递归复制 cxxbridge 与 slang 安装头）；L375 `cxx_build::bridges(ffi_files)` 解析三份 ffi.rs 里的 `#[cxx::bridge]`，L376-383 把 wrapper.cpp 一并编进 `slang_sys_bridge` 静态库，C++20 标准（L385-389）。`setup_linking`（L416-428）输出 cargo 指令：L422 `cargo:rustc-link-lib=static:-bundle=svlang`（`-bundle` 让静态库直接并入 crate，无需传递链接）、L423 链接 fmt，Windows 下补 Advapi32。`setup_rerun_triggers`（L430-455）声明重编译触发器：build.rs、slang 源码树、脚本、全部桥文件与三个环境变量。

**src 侧**：`lib.rs` L1-19 声明 compilation/diagnostic/facts/preproc/source_buffer/syntax/token/value 八个模块并转售核心类型。`syntax/ffi.rs` L9 是 `#[cxx::bridge(namespace = "slang_sys::syntax")]`——桥类型全部落在该命名空间；L11-122 是一整套 `RawTrace*` 纯数据结构（RawTrace/RawTraceEvent/RawTraceToken/RawTraceTokenOrigin/RawTraceEmittedToken），把 slang 预处理器的 trace 事件**按值**搬进 Rust，没有生命周期纠缠。`wrapper.h`（L12-20）只留一个 `to_std_strings` 辅助函数把 `rust::Vec<rust::String>` 转 `std::vector<std::string>`。

## 外部连接

包装层以 `syntax/tree.rs` 为例：`SyntaxTree`（L24-28）持 `SharedPtr<ffi::SyntaxTree>`（CXX 共享指针，树拥有全部节点内存——注释警告借出的 SyntaxNode 不得活过树）+ `Arc<OnceLock<Trace>>` 惰性 trace 缓存。`parse_with_options`（L95-116）把十几参数（predefines/include_paths/include_buffers/expand_includes/collect_expected_syntax/expected_syntax_offset）展平传给 `ffi::parse_syntax_tree`；两种入口 `from_text_with_options`（guess=true，猜测根节点）与 `from_file_in_memory*`（guess=false，保持 COMPILATION_UNIT 根，L119-145——注释强调这是 HIR 与语义索引的 file-root 契约）。`root()`（L162-166）经 `ffi::syntax_tree_root` 取根。下游消费方是 `crates/syntax`（门面，见第 5 篇）与 `preproc-expand`。`syntax.rs` 内嵌的测试（L26 `rust_calls_upstream_slang_parser` 起）是验证桥活性的最快入口。

## 数据流

以一次解析为例：Rust 侧 `SyntaxTree::from_file_in_memory_with_options_and_trace(text, name, path, &options)`（tree.rs L136-145）→ 展平参数调 C++ 桥函数 `parse_syntax_tree`（L102-115）→ wrapper.cpp 组装 slang 的 SourceManager/PreprocessorOptions（用 `include_buffers` 注册内存中的 include 文件，使未保存的 .svh 也能被 `include`）→ slang 返回 `SharedPtr<SyntaxTree>` → Rust 包成 `SyntaxTree`，trace 单独拉回成 `crate::preproc::Trace`。之后 `tree.root()` 返回的 `SyntaxNode` 是借用树的结构句柄，遍历（`elem_preorder`/`children`）与取值（`kind()`/`range()`/`value_text()`）全部经 ffi.rs 声明的 extern 函数落到 C++。构建期数据流则是：`cargo build` → rerun 触发器命中 → build.rs 四阶段 → `OUT_DIR` 的生成 .rs 被 `syntax/syntax_kind.rs`（仅 4 行，include 生成物）等挂载 → cxxbridge 宏生成 Rust/C++ 双侧胶水 → 最终二进制静态包含 svlang。

## 设计决策

**为什么 CXX bridge 而非纯 bindgen？** slang 的 SyntaxTree 是不透明复杂对象，bindgen 直出 API 会暴露 C++ 模板与所有权细节。CXX 让两侧共享一组手工声明的窄接口（RawTrace 结构按值传递、SharedPtr 管理树所有权），Rust 侧永远只见干净类型。代价是每个新接口都要写桥声明——所以大量面（AST 访问器、诊断码）改由 Python 生成器从 slang 的权威数据文件产出，手写面控制在最小。

**为什么按值搬运 trace？** 预处理 trace 要进 Salsa 体系（被多个查询长期持有），若借 C++ 引用则生命周期无法表达。RawTrace 系列（ffi.rs L11-122）用 String/Vec 全量拷贝，一次解析的 token/事件量可控，换来的解耦远超拷贝成本。

**为什么 `expected_syntax_offset` 单独成参数？** tree.rs L46-48 注释：补全元数据只服务光标处一次查询，绝不让它污染权威编译树——见第 6 篇 parser_expected_syntax 的 cursor-scoped parse。

**为什么要 clangd include 聚合目录？** 桥代码是 Rust/C++ 混写，IDE 补全两侧都要好；build.rs L365-368 把 cxx.h 与 slang 头复制到固定位置，clangd 的 compile_flags 只要指一处。

## 新人提示

1. 首次构建失败九成是子模块没拉：build.rs L71-76 会 panic 提示 `git submodule update --init`。
2. 改 ffi.rs 后若链接报 undefined symbol，检查 wrapper.cpp 是否实现了新声明的 extern 块，且文件在 build.rs L26-27 的 WRAPPER_FILES 清单里。
3. slang 升级流程：更新子模块 → 五个生成器自动跟 → 跑 `crates/slang-sys` 测试（syntax.rs L26-325 十余个用例覆盖遍历/诊断/trace）；注意 diagnostics.txt 与 Diagnostics.h 的参数布局变化（ide/diagnostics.rs 对 `args[0]` 的位置假设有注释钉版）。
4. CMake 缓存诡异时删 `target/slang-sys/<target>/<hash>/`；hash 换了自然重配，不要手改缓存。
5. WASM 构建走 `EMSCRIPTEN_CMAKE_TOOLCHAIN_FILE` + emscripten 分支（build.rs L259、L305-313），本地调试别混用同一 target 目录。
