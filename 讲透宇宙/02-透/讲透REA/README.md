# 讲透 REA

[morluto/rea](https://github.com/morluto/rea)——REA "Reverse Engineer Anything"：统一逆向工程 **MCP server + CLI**（TypeScript monorepo + turbo + vitest）。让终端用户和 AI agent 在无源码前提下检查原生二进制（Hopper/Ghidra/IDA/Kuna）、JavaScript/Electron 应用、.NET 程序集、网站、EVM 字节码、Android APK 与固件，并给出带 Evidence 的结论（observation/derivation/inference/unknown 四分 + canonical digest + 可追溯 artifact）。本地仓 `/usr-data/data1/reverse/rea`（npm 包 `rea-agents` **v6.5.0**，commit `1bd5c5c8`，2026-10-16 快照）。

## v6.5.0 大版本同步（2026-10-16）

自首轮知识库（v6.1.0 @ `441813c0`，2026-10-09）以来 **1845 个提交、3656 文件变更（+95 万行）**，本目录四件套已全部同步：

- **能力面大扩容**：MCP 工具 **138→207**（契约 group 19→**36**，目录化）；CLI 命令 **94→153**；新增 19 个分析子系统（约 120 文件/3.3 万行）——**kuna 第四深度 provider**（注册表 `[hopper, ghidra, ida, kuna]`）、Frida 动态插桩（9 工具）、GDB/Rizin 持久调试会话、Cutter GUI 桥、SQLite（零引擎 node:sqlite）、pcap/pcapng、sigrok 信号、WASM（WABT）、Go/Rust/Flutter/Electron fuse 纯解析、adb/apktool/JEB；setup 客户端 **14→25**（+Qwen/Kimi/Trae/Droid/DeepSeek Harness 等 11 家）
- **契约与 Evidence breaking（v6.2）**：evidenceEnvelope 包装废除（Evidence 直入 structuredContent）、analysis_profile 必填参与身份、快照绑定收紧、函数比较 truncated 移除——升级必读 `docs/migration-6.2.md`
- **质量基建升级**：vitest 11→12 project + reverse-tools 双配置、**Stryker 突变测试**（AST 方法级 targets）、CI 14→**27 job** / workflow 17→30、`verify:*` 99 个、合规三件套（licenses/THIRD_PARTY_NOTICES/DISCLAIMER）
- **规范演进**：ADR 废除 → `docs/specs/` 四件套；`skill-src/` → `.agents/skills/`；AGENTS.md 新增 Product and Authority / Architecture and Cleanup（owner 原则）/ Performance 三章；副作用模型 8→**10 维**（executesForeignCode/mutatesDevice）；19 语言 README 迁 `docs/readme/`
- 变化事实底稿（每条带 file:line 实证）：[_sync-facts-v6.5.md](_sync-facts-v6.5.md)

## 产物

| 目录 | 内容 |
|---|---|
| [deepwiki/](deepwiki/INDEX.md) | DeepWiki 全量 **47 页**中文索引 + 英文原文（10 章 + 37 子页，2026-10-16 经官方 MCP 端点重抓，覆盖率 100%；新增 4.6 调试器与动态插桩 / 4.7 新 provider / 6.5 Web 网络捕获 / 8.4 分析效率实验；v6.1 快照 43 页归档 `deepwiki-v6.1-archive/`） |
| [onboarding/](onboarding/ONBOARDING.md) | ONBOARDING.md 8 节，**2026-10-16 同步至 v6.5.0**（中文字 6118——较首轮 4380 增加 v6.5 增量段落；图谱层表/度数仍标注 @441813c0 基线） |
| [explain/](explain) | 12 篇重要文件/子系统精讲（六节结构：角色定位/内部结构/外部连接/数据流/设计决策/新人提示；行号实证，**2026-10-16 全部复核更新至 v6.5.0**） |

## 知识图谱（understand-anything）

- 位置：仓内 `.understand-anything/knowledge-graph.json`（**7060 节点 / 16505 边 / 14 层 / 14 步导览**，校验 0 issues）
- 基线：fingerprints 2214 文件（commit `441813c0`，v6.1.0）——**早于 v6.5.0 大扩容，节点/边/层统计已滞后**（src/ 现为 1969 文件），增量重建待做；文档中的层表与度数均已标注"@基线"
- 派发台账/RUNBOOK：`.understand-anything/DISPATCH-LEDGER.md`

## explain 篇目（tour 14 步 → 12 篇选材）

| # | 篇 | 主线 |
|---|---|---|
| 01 | cli-entry-dispatch | 入口三分派：MCP stdio / mcp doctor / CLI |
| 02 | composition-config | 组合根 + zod 配置管道（+新子系统薄装配） |
| 03 | tool-contracts | 契约总账：36 group 目录树 + 10 维副作用 + compact schema |
| 04 | mcp-server-assembly | 契约→SDK registerTool 薄翻译层（34 项注入/36 注册器） |
| 05 | domain-model | Evidence/Result/错误三级体系（evidenceEnvelope 已废除） |
| 06 | application-session | BinarySession 代际并发 + DirectAnalysis（快照绑定收紧） |
| 07 | process-sandbox | owned process：令牌验证 + fail-closed 清理（owner 原则） |
| 08 | disassembler-trio | Ghidra/Hopper/IDA 三巨头接入姿势（桥 4892 行） |
| 09 | multi-engine-providers | 五路专用引擎 → 三轨道版图（+kuna/19 新子系统） |
| 10 | browser-js-graph | CDP 观测 × 静态应用图对账（+web 三契约族） |
| 11 | evidence-ledger | 证据体系与完成账本（四分法/analysis_profile/provenance） |
| 12 | testing-verification | vitest 12 project + reverse-tools + Stryker + CI 20 job |

## 快速入口（按问题找页）

- **想懂整体**：deepwiki 1-rea-overview → 2-architecture；onboarding §3（14 层依赖树 + 度数 Top 榜）
- **加一个 MCP 工具**：explain 03 + 04；deepwiki 2.3 contracts；onboarding §8
- **加一个分析 provider**：explain 08（三巨头）+ 09（三轨道版图）；onboarding §5；deepwiki 4 章（4.6 调试器/4.7 新 provider）
- **证据/可信机制**：explain 11；deepwiki 7.1-7.2；`docs/migration-6.2.md`（v6.2 breaking）
- **进程沙箱与清理**：explain 07；deepwiki 7.3
- **测试怎么跑**：explain 12；deepwiki 8 章；docs/testing.md（"test paths do not establish depth"）
- **JS/Electron/网站分析**：explain 10；deepwiki 6 章（6.5 网络捕获）
- **调试器/动态插桩（新）**：deepwiki 4.6；docs/frida-instrumentation.md、docs/reverse-engineering-tools.md
- **v6.1→v6.5 迁移**：`_sync-facts-v6.5.md`（事实底稿）+ docs/migration-6.2.md

## 本轮钉版（流水线新知）

**2026-10-16 同步轮**：
- **大版本文档同步的编排模式**：4 个并行 explorer（providers/契约入口/测试基建/domain+bridge）产出带 file:line 锚的事实清单 → 汇成单一事实底稿 `_sync-facts-v6.5.md`（供所有后续改稿代理复用）→ 主会话亲改 README+ONBOARDING、代理改 explain → 机械判据终验。explorer B 用 **jiti 运行时 import 真模块数工具数**（vitest 因 rolldown binding 不可跑时的替代取数法）。
- **代理自报数字不可信的又一轮实证**：旧文档"29 个能力/60 余项依赖/24 组注册器"多处被实测推翻（26→28 case、23→38 组、依赖 34 项）；连初版 explorer 底稿也被改稿代理推翻 8+4 处（ci.yml 20→27 job、verify 45→99、frida 8→9、CreateServerOptions 35→34、binary.ts:19-26→:32 等）——凡数字必带命令输出，逐锚核实条款是决定性防线。
- **DeepWiki MCP 通道二次验证**：重抓 43→47 页 100% 一次过；上游新增页与仓内大版本对齐（可作为"上游 wiki 是否跟进"的探测手段）；wiki_full.md 体量可能不升反降（610K vs 691K）——上游内容重组，非抓取缺陷。

**2026-10-09 首轮**：
- DeepWiki 新通道：官方 MCP 端点 `mcp.deepwiki.com/mcp` stateless 直连（网页盾未解）——`read_wiki_structure` + `read_wiki_contents`（~700KB，SSE 分帧拼接）。工具 `pipeline-bin/deepwiki/dw_fetch_mcp.py`。
- 双会话协同：`_CLAIM.md` 占位协议 + 台账公告栏；死亡会话按「读 RUNBOOK→盘上产物盘点→断点续派」零损失接管。
- explain 完成判据外部化：字数 2500-4800（不计空格）+ 行号锚 ≥10 + 六节 `###` 结构；主会话独立复跑判据而非采信自报。
- onboarding 字数双口径：中文字数为主、总字符为辅（引用密度极高的大仓）。
