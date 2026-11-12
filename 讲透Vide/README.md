# 讲透 Vide

[pascal-lab/vide](https://github.com/pascal-lab/vide)——南京大学 PASCAL Research Group 开源的 **Verilog/SystemVerilog Coding IDE**（MIT）。目标是让硬件设计拥有软件级流畅度：精确补全/注释诊断/自动重构/语义高亮等十余项传统硬件 IDE 缺失的分析能力。架构 = rust-analyzer 范式在 HDL 上的复刻：Rust workspace 多 crate（`base-db`/`vfs`/`project-model`/`syntax`/`slang-sys`/`preproc`/`hir-def`/`hir-semantics`/`hir-ty`/`ide`/`vide-lsp-runtime`/`vide-lsp-wasm`），Salsa 增量查询数据库（RootDb）+ VFS + HIR 三层 IR；前端解析/诊断复用 [MikePopoloski/slang](https://github.com/MikePopoloski/slang)（SystemVerilog 编译器，非着色语言同名物），格式化可选调 Verible。交付面：LSP server + VS Code/Zed 扩展 + WASM 浏览器 Playground + 官网文档站。本地仓 `/usr-data/data1/repos/vide`（commit `e44d7f0f`，2026-10-12 快照，master）。

## 产物

| 目录 | 内容 |
|---|---|
| [deepwiki/](deepwiki/INDEX.md) | DeepWiki 全量 **47 页**（11 章 + 36 子页，375K 字符，2026-10-12 经官方 MCP 端点抓取，**覆盖率 100%**，对账见 [deepwiki/_coverage-check.md](deepwiki/_coverage-check.md)） |
| [onboarding/](onboarding/ONBOARDING.md) | ONBOARDING.md 8 节 5980 字（11 层 crate 地图 + 请求旅程数据流图 + 度数 Top15 + 16 步导览 + 三条任务路径；31 个路径引用独立复核） |
| [explain/](explain/) | 12 篇重要文件/子系统精讲（六节结构：角色定位/内部结构/外部连接/数据流/设计决策/新人提示；行号实证 22+3 处独立抽验全命中，每篇 ~4700 不计空格字符） |

## 知识图谱（understand-anything）

- 位置：仓内 `.understand-anything/knowledge-graph.json`（**3191 节点 / 6490 边 / 11 层 / 16 步 tour**，校验 0 issues，13 孤儿警告均为 CI step/dotfile/tmLanguage 良性外围件）
- 基线：fingerprints 549 文件 @`e44d7f0f`，支持增量更新
- 覆盖：549 文件全分析（37 批，裁 866：website/third_party/374 快照/324 Verilog 测试语料）；549/549 零缺失零重复对账
- 层次（自底向上）：base-infra(38) → project-config(14) → slang-ffi(38) → syntax-preproc(88) → hir-def(58) → hir-ty-semantics(18) → ide(119) → lsp-server(64) → editors-wasm(83) → ci-build(18) → workspace-root(11)
- 派发台账/RUNBOOK：`.understand-anything/DISPATCH-LEDGER.md`（37 批全程）

## explain 篇目（tour 主线 12 篇）

| # | 篇 | 主线 |
|---|---|---|
| 01 | lsp-entry-main-loop | src/main.rs 入口 + GlobalState 事件循环 |
| 02 | vfs-lib | VFS：编辑器文本进入分析世界 |
| 03 | base-db-rootdb | Salsa 增量底座与 RootDb trait 聚合 |
| 04 | slang-sys-ffi | C++ 解析器进 Rust（cxx/build.rs 所有权协议） |
| 05 | syntax-facade | 统一语法树门面（度数全仓第一 154） |
| 06 | preproc-macro-expand | 预处理模型与宏增量展开（MacroFileId 虚拟文件） |
| 07 | hir-def-lowering | HIR lowering：语法树的去语法化 |
| 08 | hir-ty-infer | 类型推断（端口宽度告警源头） |
| 09 | hir-semantics | 面向消费方的 Semantics 门面 |
| 10 | completion-engine | 补全引擎 |
| 11 | semantic-index-diagnostics | 语义索引（增量维护+取消）与诊断 |
| 12 | wasm-editor-distribution | WASM 分发 + VS Code/Zed 接入 |

## 快速入口（按问题找页）

- **想懂整体**：onboarding §1-3；deepwiki `1-overview` → `2-architecture-overview`
- **增量编译内核**：explain 03 + onboarding §4.1；deepwiki `2.2-incremental-database-salsa-rootdb`
- **加一个 IDE 功能**：explain 10/11；deepwiki 5 章对应子页；onboarding §8 任务路径
- **LSP 请求链路**：explain 01；deepwiki `6.1-globalstate-and-main-loop`
- **宏/预处理**：explain 06；deepwiki 2 章 VFS + 8 页 preproc 相关
- **测试怎么跑**：onboarding §7；explain 11（verilog_2005.rs≈IDE 行为规格）

## 本轮钉版（流水线新知，2026-10-12）

- **scanner Rust 盲区量化**：batchImportData 对跨 crate `use` 几乎全空（37 批 scanner 仅 ~150 条 vs 子代理补扫 ~2400 条，占最终 imports 边 80%+）。**派发模板内嵌 crate 名→路径对照表是决定性资产**，已随 `pipeline-bin/understand/rust_use_rescan.py` 固化（含 vide 版 CRATE_MAP 模板）。
- **Rust 解析四坑**：①源文件带 U+FEFF BOM 会吞首行 `use`（须 utf-8-sig 读取）；②`super::` 解析 dirname 已消掉本模块段，第一次 super 不再上溯（差一修正）；③`src/foo.rs` 与 `src/foo/` 并存时模块解析目录优先；④`pub(in crate::x) mod` 受限声明需正则放宽 `[^)]*`。
- **merge 前缀错位**：子代理发 `file:package.json` 类边而节点实为 `config:` 前缀（7 条 drop）——终图谱前手工核对 dangling 清单并按前缀修复回补。
- **edition 2024 uniform paths**：bare 首段解析到当前模块子模块（`pub use tables::…`）；build.rs 是独立编译单元需单独处理。
