# scripts/rea.mjs：npm bin 入口的三模式分发器

## 角色定位

`scripts/rea.mjs` 是 rea-agents 包唯一可执行入口：package.json 把 `rea` 与 `rea-agents` 都指向它（package.json:33-36）。它是纯 JavaScript（.mjs），不参与 TS 编译，职责极克制——在加载任何构建产物之前，按命令行参数决定启动哪套运行时。注释道破核心约束：必须先路由生产 MCP 再 import Incur，因为 `mcp add` 等注册辅助归 Incur，而 stdio 工具目录只允许 `dist/main.js` 服务（scripts/rea.mjs:7-8）。图谱中它 fan-out=1（只读 package.json），却被 26 个节点引为入口锚点。

## 内部结构

文件仅 93 行，三组构件：

- **参数与版本预解析**：`process.argv.slice(2)` 取参后，用 `import(..., { with: { type: "json" } })` 导入 package.json，把版本写进 `process.env.REA_PACKAGE_VERSION`（scripts/rea.mjs:9-13），下游无需重复读包清单。
- **模式判定**：`isMcpMode` 要求恰好一个参数且为 `--mcp` 或 `mcp`（scripts/rea.mjs:14-15）；`isMcpDoctorMode` 是 `mcp doctor` 二级命令（scripts/rea.mjs:16）；其余全落 CLI 模式。
- **运行时预检**：三种模式各声明必需的 dist 文件——MCP 只要 `dist/main.js`，doctor 追加 `dist/mcpDoctor.js`，CLI 要 `dist/cli.js`、`dist/cliOutput.js`、`dist/cli/streamedJsonOutput.js`（scripts/rea.mjs:18-22）。`compiledRuntimeExists` 逐个 `access()`，只有 ENOENT 返回 false，其他异常原样抛出（scripts/rea.mjs:74-93）。

## 外部连接

三条分支全是动态 import：MCP 模式加载 `dist/main.js` 的 `runEntrypoint`（scripts/rea.mjs:29-31）；doctor 模式加载 `dist/mcpDoctor.js` 的 `runProductionMcpDoctorCli`，并传 `dispatcherPath`（rea.mjs 自身路径）与 `packageRoot` 供诊断定位（scripts/rea.mjs:32-39）；CLI 模式加载 `createCli`、`createStreamedCliJsonOutput` 与 cliOutput 的四个校验/渲染函数（scripts/rea.mjs:41-49）。刻意不用顶层 import——静态 import 会在参数路由前拖入全部运行时，破坏加载隔离。

## 数据流

输入是原始 argv，输出是进程副作用。CLI 模式流最完整：`validateCliOutputArguments` 校验输出参数，失败打印错误并置 exitCode=1（scripts/rea.mjs:50-53）；通过后构造流式 JSON 输出对象接管 stdout（scripts/rea.mjs:56-57），再 `createCli(...).serve(args, {...})` 执行命令。命令的文本输出经 `sanitizeCliOutput` 清洗后写 stdout 并置 `wroteOutput`（scripts/rea.mjs:64-66）；已被 JSON 通道处理且失败时改写 stderr（scripts/rea.mjs:59-63）；全程无输出则兜底打印 `renderEmptyFilteredCliOutput`（scripts/rea.mjs:69-70），防止 `--json` 过滤器静默吞掉一切时用户毫无察觉。

## 设计决策

- **预检优于晚失败**：dist 缺失时给出可操作修复指引（`npm ci && npm run build:cached` 或重装）并置 exitCode=1（scripts/rea.mjs:24-28），而不是让 import 抛生涩的 `ERR_MODULE_NOT_FOUND`——MCP 场景下用户只看到客户端里的模糊失败，这段 stderr 是唯一线索。
- **ENOENT 与其他 IO 错误分流**：权限错误不该被误报为"未构建"（scripts/rea.mjs:86-93）。
- **shebang + ESM**：`#!/usr/bin/env node`（scripts/rea.mjs:1），Node 要求 `^22.19.0 || ^24.11.0 || >=26.0.0`（package.json），因为用到了 import attributes 语法。

## 新人提示

改它时记住它**永远跑在未构建/半构建环境**：新增运行时文件必须同步登记进对应模式的 `runtimeFiles`，否则装完包就报 "compiled runtime is missing"。不要加业务逻辑——顶层一旦 import TS 产物，"先路由后加载"的次序就被破坏，`rea --mcp` 会错误启动 CLI 框架。`isMcpMode` 用 `args.length === 1` 严格匹配，`rea --mcp --foo` 掉进 CLI 模式是有意的（CLI 要自己报告未知参数），别顺手放宽。调试安装问题先手工跑 `node scripts/rea.mjs mcp` 确认走的分支。
