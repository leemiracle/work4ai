# 讲透 Tai-e

[pascal-lab/Tai-e](https://github.com/pascal-lab/Tai-e)（太阿）——南京大学 pascal-lab 出品的**现代 Java 静态分析框架**（ISSTA 2023 论文 *"Tai-e: A Developer-Friendly Static Analysis Framework for Java by Harnessing the Good Designs of Classics"*）。汲取 Soot/WALA/Doop/SpotBugs 四大经典的设计精华并做速度与精度优化：输入字节码/源码 → World 类层次 → 自研三地址码 IR → 指针分析（on-the-fly call graph）→ 污点分析/缺陷检测。本地仓 `/usr-data/data1/repos/Tai-e`（master `8f22e4196925c21e`，2026-09-19 快照，src/main/java 758 文件）。

## 产物

| 目录 | 内容 |
|---|---|
| [deepwiki/](deepwiki/INDEX.md) | DeepWiki 全量 34/34 页（9 章 + 25 子页，2026-10-12 经官方 MCP 端点 `mcp.deepwiki.com/mcp` 抓取，覆盖率 100%，全文 592K 字符；每页带源文件清单可对账） |
| [onboarding/](onboarding/ONBOARDING.md) | ONBOARDING.md 8 节（5969 字/33 行号锚点；14 层架构总览+核心数据流+扩展点地图+2 周上手路线） |
| [explain/](explain) | 12 篇精讲（六节结构：角色定位/内部结构/外部连接/数据流/设计决策/新人提示；共 57480 字 493 个行号锚点，全部实读源码取证） |

## 知识图谱（understand-anything）

- 位置：仓内 `.understand-anything/knowledge-graph.json`（**2723 节点 / 9073 边 / 14 层 / 16 步导览**，validator 0 issues）
- 基线：fingerprints 1044 文件（commit `8f22e4196925c21e`），支持增量更新
- 边分布：imports 5780 / contains 1679 / exports 812 / inherits 206 / configures 184 / tested_by 150 / implements 138 / documents 67
- 14 层：util 基础设施 → language 类型系统 → IR → IR 后端 → 前端翻译+World → 分析基座 → 程序图+数据流 → pta 核心 → pta 插件+工具箱 → 污点+规则库 → 缺陷检查 → Android → 测试 → 入口+工程
- 台账：`.understand-anything/DISPATCH-LEDGER.md`（48 批全程记录）

## explain 篇目（tour 16 步 → 12 篇选材）

| # | 篇 | 主线 |
|---|---|---|
| 01 | main-entry-config | Main CLI → Configs → AnalysisManager 按 Plan 执行 |
| 02 | world-hierarchy | World 单例门面 + WorldBuilder + JClass 类模型 |
| 03 | ir-data-model | 三地址码 Stmt/Exp/Var + 双 visitor 枢纽 |
| 04 | frontend-translate | 字节码→IR：MethodIRBuilder/VarManager/栈机变量提升 |
| 05 | soot-world-loading | Soot 适配层与双前端路线（soot vs 直翻） |
| 06 | cfg-icfg-callgraph | CFG 四族边 + DefaultICFG + on-the-fly call graph |
| 07 | dataflow-solver | WorkList/InterSolver 与五元组框架 |
| 08 | pta-default-solver | **DefaultSolver 927 行主循环（全书心脏）** |
| 09 | pta-plugin-system | Plugin 钩子/CompositePlugin/SolverHolder |
| 10 | pta-advanced-plugins | invokedynamic lambda 边 + 反射四 model |
| 11 | zipper-mahjong-scaler | pascal-lab 三篇 OOPSLA 论文落地 |
| 12 | taint-analysis | 三 handler + YAML 规则库（含配置勘误钉版） |

## 本轮勘误账（DeepWiki 未覆盖，explain 12 收录）

1. **OgnlUtil.yml/TextParseUtil.yml 用单数 `sink` key**，解析器只读复数 `sinks` → 两个 OGNL sink 配置被静默忽略
2. java-io.yml 重复条目 + `PrintWrite` 笔误（应 PrintWriter，静默 warn 忽略）；HttpCookie type 与返回类型脱节
3. 上游拼写错误：`apahce-commons` 目录名、`spel-inejction` 目录名、`RAEDME.adoc` 文件名、Category.yml 签名缺逗号
4. MultiStringsSourceArgumentsProvider 错误信息里的 `@MultiStringsValueSource` 笔误

## 快速入口（按问题找页）

- **想懂整体**：deepwiki [1-overview](deepwiki/1-overview.md) → onboarding §1-3
- **写一个分析 pass**：onboarding §5 + explain 01
- **调指针分析**：explain 08（DefaultSolver）→ 09（插件体系）→ 03（IR 模型）
- **做污点检测**：explain 12 + deepwiki [4.1-4.3](deepwiki/4-taint-analysis.md)
- **懂 Java 静态分析设计**：explain 05/06/07（Soot 借鉴/程序图/数据流）
