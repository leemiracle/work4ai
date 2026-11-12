# vide ONBOARDING（图谱 @ e44d7f0f，2026-10-12）

> 源：图谱精简输入（3191 节点/11 层/16 步 tour）。

## 1. 项目是什么 / 为什么存在

vide 是南京大学 PASCAL 组开源的 Verilog/SystemVerilog 编程 IDE（root package `vide` v1.3.0-beta.1），主打"让硬件设计拥有软件级流畅度"：精准补全、实时诊断（含端口宽度告警）、自动重构与语义高亮。它复刻 rust-analyzer 范式——Salsa 增量查询数据库（RootDb）+ VFS + 多层 HIR；语法分析经 slang-sys FFI 绑定 slang C++ 库（vendored 于 `third_party/slang`），格式化借力 Verible。交付三形态：VS Code 扩展、Zed 扩展、WASM playground（`crates/vide-lsp-wasm`）。

| 维度 | 取值 |
|---|---|
| 语言域 | SystemVerilog / Verilog-2005 + vide.toml manifest 编辑器特性 |
| 范式 | rust-analyzer 式 LSP：Salsa tracked query + 不可变 snapshot 并发 |
| 解析底座 | slang（C++）via crates/slang-sys（cxx-build + generate_ast.py 生成绑定） |
| 增量内核 | db 阶梯 SourceDb→PreprocDb→HirDefDb→TyDb→RootDb + parse LRU |
| 交付端 | VS Code 桌面/Web、Zed、WASM playground（6 目标矩阵交叉编译） |

## 2. 仓库布局与 crate 地图（11 层依赖树，自底向上）

1. **Salsa 基础设施层**：base-db 定义 SourceDb；vfs 内存文件系统（`crates/vfs/src/lib.rs`）；utils 工具（line_index/text_edit）。
2. **工程模型与用户配置层**：project-model 发现 TOML 工作区；workspace-model 划分 source root；user-config 定义 vide.json 契约。
3. **slang FFI 绑定层**：slang-sys 绑定解析树/诊断/trace（facts.rs 事实表；wrapper.cpp 1876 行）。
4. **语法与预处理展开层**：syntax 门面（`crates/syntax/src/lib.rs` 度 154 全仓第一）；preproc 建模型；preproc-expand 增量展开。
5. **HIR 定义层**：hir-def 的 item_tree/owner/scope/body/pathres（名字解析 1494 行）。
6. **HIR 类型与语义层**：hir-ty 类型推断；hir-semantics 门面转发 to_def。
7. **IDE 功能层**：crates/ide 聚合 RootDb，补全/诊断/引用/重命名全在此。
8. **LSP server 主程序层**：global_state.rs 状态机、qihe.rs 外部分析器、lsp_ext/to_proto.rs 编码。
9. **编辑器扩展与 WASM 层**：editors/vscode/src/extension.ts、editors/vscode/src/browser/worker-runtime.ts、editors/zed。
10. **CI/CD 与构建层**：ci.yml、build-artifacts.yml（6 目标交叉编译）、xtask。
11. **工作区根配置与文档层**：根 Cargo.toml（18 成员）、rustfmt.toml、双语文 README。

## 3. 架构总览：一条请求的旅程

以 `textDocument/completion` 为例（tour 第 13 步）：

```
编辑器 keystroke (JSON-RPC)
 ▼ src/global_state/event_loop.rs   Event{LSP|任务|VFS变更}
 ▼ handlers/request/completion.rs   在只读 GlobalStateSnapshot 上查询
 ▼ crates/ide/src/analysis.rs       AnalysisSnapshot：43 个查询方法
 │   （换快照前经 ide/db/apply_change.rs 取消旧查询）
 ▼ completion/context.rs   caret 快照 + ExpectedSyntax
 ▼ completion/request.rs   期望语法→15 种 CompletionProvider
 ▼ completion/engine{,plan,candidate}.rs   分派/排序/去重
 │   查询链 SourceDb→PreprocDb(解析+宏展开 LRU)→HirDefDb→TyDb
 ▼ src/lsp_ext/to_proto.rs  编码 CompletionItem[] 回包
```

写路径：didChange 经 text_document/mem_docs 进 VFS，process_changes 合并去重、失效诊断，publisher.rs 增量推送；读走快照、写走主循环（vide-lsp-runtime/router.rs 并发模型）。

## 4. 核心子系统深入

### 4.1 增量编译内核：Salsa 阶梯与 RootDb

db trait "底座窄、上层宽"：`base-db/src/source_db.rs` 管源文本与 source root，change.rs 以 durability 原子写回，`preproc-expand/src/db.rs`（约 1500 行）加 parse LRU 与宏展开 trace 索引，顶层 `ide/src/db/root_db.rs` 聚合全部 trait。增量三件套：apply_change.rs 取消旧查询并等快照释放；CancellationToken 派生子 token 原子取消；semantic_index.rs 增量维护引用索引（build.rs 849 行）。

### 4.2 预处理展开：preproc / preproc-expand

slang-sys/preproc.rs 定义 trace 的 FFI 安全模型（宏 Id、include 边、token origin）；preproc/source/model.rs 建定义/引用/include 图；preproc-expand 映射进 salsa——compilation_plan.rs 规划 include 与 buffer 装配，macro_file.rs 用 MacroCallId 定位宏调用，macro_file/source_map.rs 做 map_up/map_down 换算（宏内导航/rename），reference_index.rs 建 MacroReferenceIndex；展开文件经 HirFileId 统一寻址。

### 4.3 HIR 三层：hir-def → hir-ty → hir-semantics

hir-def 下沉：item_tree.rs 压轻量签名索引，lower.rs 贯穿下沉并收集诊断（diagnostics.rs 1319 行），owner.rs 的 OwnerTable 登记模块/class/checker/generate 容器，scope.rs（1993 行）建作用域，body.rs 维护 HIR↔syntax 映射，pathres.rs 按 phase 解析名字。hir-ty/src/infer.rs 按 DefKind 穷举定义类型并归一化为语义 Ty——端口宽度告警源头。hir-semantics/src/semantics.rs 复刻 Semantics 门面，source_to_def.rs 桥接"语法节点→HIR 定义"。

### 4.4 completion engine

completion/context.rs 合成词法与语法上下文，request.rs 映射 15 种 CompletionProvider，engine/plan.rs 分派（expr/member/port_list/keywords/snippets/system 等），candidate.rs 以 CandidateRank 排序、CandidateIdentity 去重；关键词事实来自 slang-sys/facts.rs 的 is_possible_* 谓词。92 个 insta 快照（engine/snapshots/）锚定候选。

## 5. 关键文件 Top 榜（度数 Top15）

| # | 文件 | 度 | 为什么重要 |
|---|---|---|---|
| 1 | crates/syntax/src/lib.rs | 154 | 语法门面，引用最密 |
| 2 | crates/preproc-expand/src/db.rs | 129 | PreprocDb 中枢 |
| 3 | crates/vfs/src/lib.rs | 108 | 统一文件视图 |
| 4 | crates/utils/src/text_edit.rs | 104 | 原子编辑/偏移映射 |
| 5 | crates/ide/src/verilog_2005.rs | 104 | 特性矩阵测试 |
| 6 | crates/hir-def/src/lib.rs | 104 | hir-def 根 |
| 7 | crates/utils/src/line_index.rs | 102 | 行列换算 SIMD |
| 8 | crates/preproc-expand/src/macro_file.rs | 92 | 宏文件与溯源 |
| 9 | crates/ide/src/semantic_index.rs | 88 | 引用索引 |
| 10 | crates/ide/src/lib.rs | 88 | ide 声明入口 |
| 11 | crates/hir-def/src/owner.rs | 76 | OwnerTable |
| 12 | crates/ide/src/manifest.rs | 73 | manifest 特性 |
| 13 | crates/slang-sys/src/facts.rs | 72 | 补全事实源 |
| 14 | crates/ide/src/module_resolution.rs | 70 | 模块名消歧 |
| 15 | crates/hir-def/src/body.rs | 70 | 过程体 HIR |

## 6. 导览路线（16 步 tour 串成学习路径）

1. 读 README 与根 Cargo.toml，建 crate 地图。
2. main.rs 进 global_state.rs 事件循环。
3. 文档同步：text_document→mem_docs→process_changes→vfs。
4. 工程发现：config.rs 与 project/workspace/user-config。
5. Salsa 底座：base-db 的 source_db/change 与 root_db。
6. slang FFI：slang-sys 的 build.rs、generate_ast.py、syntax。
7. syntax 门面：lib、slang_ext、token_at_offset。
8. 预处理：slang-sys/preproc→preproc/model→preproc-expand/db。
9. HIR lowering：item_tree→lower→owner→scope→body→pathres。
10. 类型推断：hir-ty 的 ty→infer→db。
11. Semantics：semantics 与 source_to_def。
12. ide 门面：analysis、navigation_target、render。
13. 补全全旅程：completion→context→request→engine→candidate。
14. 其余特性：diagnostics、references、rename、code_action。
15. 增量内核：apply_change、cancellation、semantic_index。
16. 分发：vide-lsp-wasm、browser.rs、editors、ci.yml。

## 7. 构建与测试

```bash
cargo build -p vide      # LSP server（nightly-2026-05-24 钉版）
cargo test               # 全 workspace
cargo test -p vide_ide   # IDE 层含补全快照
cargo xtask check-config-artifacts / check-schemas  # 生成物校验
cargo xtask server / vscode                          # 构建产物
```

- **CI（ci.yml）**：fmt、xtask 校验、slang 绑定再生成校验、clippy -D warnings；三 OS 矩阵测试 + VS Code npm test。
- **分发（build-artifacts.yml）**：6 目标矩阵（zigbuild 交叉编译）产出二进制与 VSIX；release.yml 校验三处版本一致。
- **snapshot 模式**：insta 1.46——engine/tests.rs 用 `insta::assert_debug_snapshot!` 锚定候选于 engine/snapshots/*.snap（92 个）；src/tests.rs（57 个助手）spawn 测试服务器，tests/diagnostics.rs 最大（29 测试）。

## 8. 新人上手建议

**先读**：README.md → 第 3 节数据流图 → `crates/ide/src/db/root_db.rs` → 补全链路五文件。**再改**：从小 provider 或 code_action/handlers.rs（24 个 handler 静态注册表）入手。**验证**：`cargo test -p vide_ide` + insta 快照；LSP 行为用 src/tests.rs 助手写集成测试。

三条常见任务路径：
1. **加补全候选**：context 判定上下文 → request 挂 provider → engine 实现 → 加 fixture 接受快照。
2. **加诊断**：语法/语义归 slang（preproc-expand/db.rs 透出）；lowering 诊断加 hir-def/diagnostics.rs；自研 provider 加 ide/diagnostics.rs → src/tests/diagnostics.rs 加用例。
3. **改宏行为**：slang-sys/preproc.rs → preproc/source/model.rs → preproc-expand 三件（compilation_plan/macro_file/reference_index）→ 用 macro_file/tests.rs 与 hir-semantics 的 TestDb 验证。
