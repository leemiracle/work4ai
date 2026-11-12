# 09 · Hopper provider 深讲（IDA 适配器带过）

## 角色定位

本篇选 Hopper 深讲——仓内证据面最大：`src/hopper/` 24 文件、1132 行 Python 桥 `bridge/hopper_bridge.py`、宿主层 LinuxHopper/MacHopper、自托管 CI。IDA 是薄适配器（连外部既有 IDA MCP server），在外部连接带过。Hopper 是"寄生式"架构：REA 不自建引擎，而是用 Hopper 官方 CLI 的 `--python` 选项把桥脚本注入 Hopper 进程内，桥再开 Unix socket 服务 REA。`HopperProvider implements AnalysisProviderCandidate`（`src/hopper/HopperProvider.ts:44`）。

## 内部结构

探测三问：`inspectAvailability` 只认 darwin/linux 且 launcher `accessSync(X_OK)`（`HopperProvider.ts:78`）；`inspectTargetSupport` 拒绝非 executable/database，DOS MZ/COM 显式让位 Ghidra 16 位适配器（`HopperProvider.ts:117`）；profile 不支持时返回"永远失败"的 client 而非抛异常（`HopperProvider.ts:150`）。`createClient`（`HopperProvider.ts:145`）是装配重心：解析 `prepared_image`（FAT 源验证的 thin slice）→推导 loader args→构造 HopperClient+HopperApplicationLauncher，桥脚本路径由 `import.meta.url` 相对定位（`HopperProvider.ts:217`）；Linux 切 `launchMode: "verified_linux_demo"`（`HopperProvider.ts:220`）。execute 包装三件事：regex 搜索走独立 `HopperRegexSearch`（`HopperProvider.ts:238`）、`address_to_file_offset` 映射回原文件偏移（`HopperProvider.ts:244`）、按能力表注入 limitations（`HopperProvider.ts:254`）。

Python 桥运行在 Hopper 专属线程（docstring 明言移到 worker 会死锁，`hopper_bridge.py:1`）。`_bind_session_document` 用 realpath 匹配目标并处理 Hopper 重建 wrapper 的句柄相等性（`hopper_bridge.py:102`）；`EXHAUSTIVE_ANALYSIS_METHODS` 先过 `backgroundProcessActive` 完成门（`hopper_bridge.py:137`）；批量改名先验证全部目的地再统一应用——"后一个地址畸形不能丢弃前面的变更"（`hopper_bridge.py:967`）；`_run` 起 0600、`listen(1)` 单客户端 socket（`hopper_bridge.py:1117`）。

## 外部连接

请求鉴权 `hmac.compare_digest` 对比注入的 REA_TOKEN（`hopper_bridge.py:1036`）；错误归四类且不泄露传输凭据（`hopper_bridge.py:1094`）。宿主层 `BridgeLauncher.ts` 是进程边界：Hopper helper 内部发 AppleScript `activate`，文档承认可能抢前台且无法在受支持启动方式内抑制（`BridgeLauncher.ts:108`）；启动前取 `HopperTargetLease` 防并发（`BridgeLauncher.ts:134`），启动后写 0600 ownership.json（`BridgeLauncher.ts:236`）。Linux 侧 `LinuxHopper.ts` 钉死外部效果：下载前缀与 6.4.2 demo 三包哈希硬编码（`LinuxHopper.ts:12`、`LinuxHopper.ts:23`），下载前披露 URL/字节数/命令（`LinuxHopper.ts:54`）。IDA 对比：`IdaMcpConnection.ts:110` 用 MCP SDK 以 stdio 或 StreamableHTTP 连上游，遇 `output_truncated` 直接拒绝建立观察（`IdaMcpConnection.ts:52`），stdio 强制 `IDA_MCP_MAX_WORKERS=1`（`IdaMcpConnection.ts:121`）。

## 数据流

BinaryTarget→探测→launcher 写 bootstrap（注入 REA_SOCKET/REA_TOKEN）→`hopper --analysis -Y <bootstrap> --executable <target>`（`BridgeLauncher.ts:190`）→桥绑定 session document→单连接 NDJSON 循环（`hopper_bridge.py:1009`）→health 握手回 runId（`HopperClient.ts:382` 校验）→`callTool` 串行执行（`HopperClient.ts:403`）→包装 `AnalysisExecution`→close 发 shutdown；桥按 `REA_OWNS_PROCESS_LIFETIME` 决定关文档或留给进程清理（`hopper_bridge.py:733`）。

## 设计决策

核心权衡"不做引擎做合同"：只调 Hopper 公开 Python API，能力缺失抛 `CapabilityUnavailableError` 而非退化实现。所有权诚实分层——REA 只拥有 launcher 助手的进程组，不宣称拥有 macOS LaunchServices 可能复用的 GUI 进程（`BridgeLauncher.ts:115`）。改名后主动失效搜索/伪代码缓存保证读回一致。Linux demo 模式是明示妥协：钉版+哈希换可控运行环境。

## 新人提示

桥内一切在 Hopper 线程串行执行，勿加并发；`BAD_ADDRESSES`（-1/0xFFFFFFFFFFFFFFFF/None）是 Hopper 哨兵值，地址解析必须过滤；符号名超 1024 个 UTF-16 单元被截断，桥以此常量预校验（`hopper_bridge.py:16`）。TS 新增方法要同步改 `EXHAUSTIVE_ANALYSIS_METHODS` 与能力表。真实行为只有 `npm run verify:hopper` 验证（`real-hopper.yml:35`），vitest 里全是 fake。
