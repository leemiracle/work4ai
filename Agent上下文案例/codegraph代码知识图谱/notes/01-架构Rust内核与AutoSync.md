# 01 · 架构：Rust 内核、SQLite 与三层 Auto-Sync

> 出处：上游 README（2026-08 版）+ 文档站 guides。文档级审计，逐条标注。

## 1. 总体数据流

```
源码 ──Rust kernel 解析──▶ 符号/边 ──▶ SQLite（.codegraph/codegraph.db + FTS5 全文索引）
                                        │
agent ◀──MCP（codegraph serve --mcp）────┘
   ▲
   └── watcher（原生 OS 事件）→ debounce(2s) → 增量 sync（只重算变更文件）
```

四个阶段：**Extraction（Rust 内核）→ Storage（SQLite+FTS5）→ Resolution（调用→定义、import→文件、继承、框架模式、跨语言桥接）→ Auto-Sync**。

## 2. Rust 内核：三个工程决策

1. **字节级等价验收**（README "Built for speed"）：20 语言在编译代码中解析（每文件只跨一次 FFI 边界）；每种语言只有在真实仓库上产出的图与参考（portable）引擎 **byte-for-byte 一致**后才允许走原生路径；无预编译二进制的平台/语法错误文件**逐文件自动回退**，保证"同一个图，两条路径"。
2. **机器自适应**：worker 池/解析池/缓存按**真实核数**（容器 cgroup 感知——VPS 只给 2 核就按 2 核配）与实测可用 RAM 定尺寸。性能锚点（README 实测）：
   - Swift 编译器仓库（27k 文件）全量索引 ~100s；单文件改后 re-sync ~4s；
   - Linux 内核（70k 文件 / 2M 符号 / 6.4M 关系）在 2核/6GB VPS <12 分钟（对比"RAM-first 设计在 1% 前就 OOM"）；
   - 单文件保存：watcher 300ms 触发，同步 ~0.3–0.4s 工作量；比"最快竞品的 re-index-on-change"在 31 仓库/30 语言基准上快 2–7×，且**差距随仓库变大而拉大**（竞品成本 ∝ 仓库，codegraph 成本 ∝ 变更）。
3. **不编译、自包含**：bundle 自带运行时，无 native build、无需 Node（npm 安装也可）。这是它 66k★ 的可安装性基础。

## 3. 图里有什么：超越"符号表"的三层边

| 层 | 内容 | 例子 |
|---|---|---|
| 符号层 | 函数/类/方法节点 + verbatim 源码 | `codegraph_node` 返回带行号源码（同 Read 输出形状） |
| 关系层 | 调用边（含 **dynamic-dispatch hop**——grep 跟不到的虚调用）、import、继承 | `codegraph_callers/callees/impact`（blast radius） |
| 领域层 | **17 框架路由**（Django/Flask/FastAPI/Express/NestJS/Laravel/Drupal/Rails/Spring/Play/Gin/Axum/ASP.NET/Vapor/React Router/Vue/Nuxt/Astro…）：`route` 节点 → handler 的 references 边 | 查 handler 的 callers 能看到绑定它的 URL |
| 桥接层 | 跨语言闭环：Swift↔ObjC（@objc 桥接规则+Cocoa 介词前缀）、RN legacy bridge/TurboModules、native→JS 事件通道、Expo Modules DSL、Fabric/Paper 视图组件 | 每条桥在小/中/大真实仓库验证（Charts/realm-swift/Wikipedia-iOS、react-native-firebase、expo SDK…） |

**关键诚实设计**：桥接边全部打 `provenance:'heuristic'` + `metadata.synthesizedBy`（如 `swift-objc-bridge`、`rn-event-channel`）——推测出来的边**自称推测**，不与解析出的边混淆。覆盖率也诚实分语言报告：TS/JS 95.8%、Python 100%、Go 96.6%、Rust 86.7%、Liquid 73.8%；反射重的框架（Django 74.1%）明说是静态分析上限。

## 4. Auto-Sync 三层：把"索引会过期"变成显式信号

| 层 | 机制 | 为什么存在 |
|---|---|---|
| ① watcher + debounce | FSEvents/inotify/ReadDirectoryChangesW，默认 2000ms（`CODEGRAPH_WATCH_DEBOUNCE_MS` 可调，clamp [100ms,60s]），编辑风暴合并为一次 sync | agent 边写边查，索引必须跟上 |
| ② 过期横幅 | debounce 窗口内，若 MCP 响应引用了 pending 文件 → 响应前置 `⚠️` 点名该文件并指示 agent 直接 `Read`；未引用的 pending 文件显示为小 footer。已在 Claude Code 验证（agent 会说 "Reading the file directly for the live content"） | **索引沉默地错 = agent 自信地错**；宁可降级也不撒谎 |
| ③ 连接时对账 | MCP server（重）连接时先跑 `(size, mtime)` + content-hash 对账，吸收 server 不在时的外部改动（git pull、别的编辑器） | 补上"无守护进程时段"的洞 |

`codegraph status` 随时可见 `### Pending sync:` 段。手动 `sync` 仅用于 watcher 被禁（沙箱 / `CODEGRAPH_NO_DAEMON=1`）或脚本场景。

> 与 dsh 案例的"model-visible ⟺ logged"对照：dsh 用运行时断言保证"账本不说谎"；codegraph 用横幅保证"索引不说谎"——同一设计哲学（**fail-loud 而非 fail-silent**）在两个层的落地。

## 5. Agent 接线面：一个工具主义

- **MCP 默认单工具** `codegraph_explore`：一次调用返回相关符号 verbatim 源码 + 符号间调用路径 + blast radius 摘要。README 明说这是实测结论："一个强工具比一堆窄工具更能引导 agent"。其余 7 个（node/search/callers/callees/impact/files/status）默认不列出，`CODEGRAPH_MCP_TOOLS=explore,node,search` 按需开。
- **覆盖 9 类 agent**：Claude Code、Cursor、Codex CLI、opencode、Hermes Agent、Gemini CLI、Antigravity IDE、Kiro、GitHub Copilot（vscode/cli/jetbrains 三入口）。`codegraph install` 自动写 MCP 配置 + 在 `CLAUDE.md`/`AGENTS.md`/`GEMINI.md` 写 marker-fenced 指令段（教 subagent 用 CLI 等价命令）；`uninstall` 干净逆装。
- **使用指引随 initialize 下发**（`src/mcp/server-instructions.ts`）：核心是"直接用图回答结构性问题，不要再用 grep 复核"——防止 agent 退回 R1 习惯把索引变纯开销。还明确引导"不要把探索委派给文件阅读 subagent"（否则 subagent 照样读文件，图白建）。
- **CLI 等价面**：`query/node/files/callers/callees/impact/affected`（`affected` 可接 `git diff --name-only | codegraph affected --stdin` 做受影响测试选择，深度默认 5）。

## 6. 配置与边界

- 零配置默认：跳过 node_modules/dist/.next/Pods 等 + `.gitignore` 内容（非 git 项目也生效）+ >1MB 文件；`codegraph.json` 支持 `exclude/include/extensions`（自定义扩展名映射，如 `.dota_lua → lua`）。
- 已知边界（README Troubleshooting 诚实列出）：网络盘/WSL2 `/mnt` 上 SQLite WAL 失效需移本地盘；Windows/WSL 共享 checkout 需 `CODEGRAPH_DIR` 分开索引；跨项目查询传 `projectPath` 可查任意已索引项目。

→ 下一篇：[02-基准方法论与诚实披露](02-基准方法论与诚实披露.md)
