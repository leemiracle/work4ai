# 08 · Ghidra 双端协作：GhidraClient 与 ReaGhidraBridge.java

## 角色定位

Ghidra provider 是跨语言对等双端：TS 侧 `src/ghidra/GhidraClient.ts:65` 拥有并监督一个私有 headless Ghidra JVM；Java 侧 `bridge/ghidra/ReaGhidraBridge.java:101` 是打包进 npm 的单类 3400 行 `HeadlessScript`，在 JVM 内只暴露行式 JSON 协议。`GhidraProvider`（`src/ghidra/GhidraProvider.ts:55`）做安装探测与目标支持判定。图谱给 Java 桥标 fan-out 88（Ghidra API import 面）。

## 内部结构

Java 桥 `CAPABILITIES` 硬编码 28 个方法（`ReaGhidraBridge.java:121`），`handleRequest` switch 是唯一分派点（`ReaGhidraBridge.java:351`）。`run()` 序列（`ReaGhidraBridge.java:160`）：读会话描述符→POSIX 立即删除描述符文件（consume-and-delete，`ReaGhidraBridge.java:172`）→校验版本（`ReaGhidraBridge.java:185`）→`constantTimeEquals` 比对导入字节 sha256（`ReaGhidraBridge.java:188`）→`end(true)` 提前结束脚本自带事务，让每次编辑拥有可回滚的真实外层事务（`ReaGhidraBridge.java:198`）。传输双轨：POSIX Unix socket 且 chmod `rw-------`（`ReaGhidraBridge.java:229`）；Windows 回环 TCP，端口文件原子发布（`ReaGhidraBridge.java:242`）。鉴权：请求 token 经 `MessageDigest.isEqual` 常时比较（`ReaGhidraBridge.java:3204`），JSON 键集严格相等（`ReaGhidraBridge.java:3219`）。唯一写操作 `annotateNativeFunction` 在显式事务内写后读回验证，不符即抛错回滚（`ReaGhidraBridge.java:1016`、`ReaGhidraBridge.java:1061`）；Windows P0 拒绝该方法（`ReaGhidraBridge.java:377`）。

TS 侧组合件分层：`GhidraWire`（编码）→`GhidraRequestQueue`（串行）→行缓冲→按 id 路由的 `GhidraResponseRouter`（`GhidraClient.ts:111`）。`#startWithin`：私有运行时根→端点分配→目标快照准入（`GhidraClient.ts:329`）→32 字节随机 token（`GhidraClient.ts:348`）→launcher 启 JVM（`GhidraClient.ts:352`）→握手（`GhidraClient.ts:389`）。`callTool` 一律先进串行队列（`GhidraClient.ts:210`）。

## 外部连接

Java 桥只 import Ghidra 公开 API 与 Gson（`ReaGhidraBridge.java:46`），协议即契约。TS 侧依赖 `process/` 三件套（`GhidraClient.ts:8`），被 `GhidraProviderClient.ts` 包成应用层 AnalysisClient，汇入 `composition/binary.ts` 注册表。真实引擎断言由 `scripts/verify-real-ghidra-assertions.mjs` 在 CI 验证。

## 数据流

BinaryTarget→`GhidraProvider.createClient`（`GhidraProvider.ts:186`）→目标字节复制为私有快照，targetSha256 携带到 Java 再比对→工具调用经队列编码为 `{id,token,method,params}` 单行 JSON→Java 分派→`writeResponse` 回写（Gson 不转义代理对，桥内手工补 `\u` 保无损 UTF-8，`ReaGhidraBridge.java:3344`）→router 命中 pending promise→包装 `AnalysisExecution`。close 先发 `shutdown` 校验确认帧（`GhidraClient.ts:484`），再等进程退出、删运行时根。

## 设计决策

防御三处：①历史 token 全留集合，诊断输出统一 `#redactAuthentication` 替换 `[REDACTED]`（`GhidraClient.ts:568`）；②清理 fail closed——JVM 未死时强删目录会被活 JVM 重建文件，`incomplete` 时保留 supervisor 与文件供重试并抛错（`GhidraClient.ts:527`）；③pcode 规模上限定死（`ReaGhidraBridge.java:102`），regex 栈耗尽转可操作错误。握手含 `read_only`/`analysis_timed_out`（`ReaGhidraBridge.java:414`），TS 侧校验 runId/版本/digest/sha 一致（`GhidraClient.ts:428`）——两端互不信任。

## 新人提示

改协议必须两端同步：CAPABILITIES 数组、switch、`GhidraSessionValues.ts` 解析 schema 三处对齐。`start()` 的 startPromise 记账有竞态注释，改动前先读（`GhidraClient.ts:150`）。Windows 差异（P0 只读/回环 TCP/DACL）在 provider 能力表分派（`GhidraProvider.ts:70`），勿在 client 写平台分支。vitest 全用 fixture，勿启真 JVM。
