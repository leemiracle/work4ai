<!-- source: knowledge-graph tour step | files: bridge/ghidra/ReaGhidraBridge.java, src/ghidra/GhidraClient.ts, src/hopper/HopperProvider.ts, src/ida/IdaMcpConnection.ts -->
# 08 · 反汇编三巨头：Ghidra/Hopper/IDA 的三种接入姿势

### 1. 角色定位

分析 Provider 层与 Bridge 层在反汇编领域交汇出三家老牌 provider（深度注册表 v6.5 已扩为四家：hopper/ghidra/ida/**kuna**，`src/composition/binary.ts:32`，kuna 见 09 篇），各代表一种建立信任的方式：Ghidra 是**全资私有会话**——REA 启动、认证、监督、销毁整个 JVM；Hopper 是**候选式寄生**——探测宿主可执行的 Hopper 再注入自身；IDA 是 bring-your-own——用户自备 ida-pro-mcp，REA 只做 MCP 客户端。三者收敛到同一契约 `AnalysisProviderCandidate`（`src/application/AnalysisProvider.ts:285`）：绑目标前可问可用性、目标支持、分析 profile，外加 v6.5 的 pending 资源问询（`:294-296`）。

### 2. 内部结构

**GhidraClient：会话所有者。**（`src/ghidra/GhidraClient.ts:97`）`start()`（`:222`）幂等化（`#hasOwnedResources` 判重，`:644`），启动序列：私有运行时目录→端点分配→目标快照准入→生成 32 字节 bearer token（`:732`）→launcher 拉起 JVM→ping 握手；token 进诊断脱敏（`:1025`）。请求走 `GhidraRequestQueue`——"FIFO that admits one Ghidra Program request at a time"（`src/ghidra/GhidraRequestQueue.ts:38`），因桥单连接单线程；响应由 `GhidraResponseBuffer` 切行后按 id 配对（`src/ghidra/GhidraResponseBuffer.ts:7`）。

**ReaGhidraBridge.java：对端 4892 行单类+sidecar 群。** `run()`（`bridge/ghidra/ReaGhidraBridge.java:184`）读会话描述符后 POSIX 立即删除（`:197`，bearer 只活一次）；核对 Ghidra 版本（`:216`）与导入字节 SHA-256（`:220`，constantTimeEquals 防时序泄露，定义 `:4790`）；`end(true)` 提前结束脚本自带事务（`:232`），让后续编辑各自拥有可即时回滚的外层事务。31 项能力硬编码于 `CAPABILITIES`（`:142`），ping/shutdown 在 switch 前处理（`:393`/`:419`），其余经 28 路 case 分派（`:430`）；鉴权 token 常量时间比较（`:4681`）；注释拒绝未配对 UTF-16 代理对（`:1529`）、写回再转义孤立代理对（`:4823`）。pcode 值流设 3000 操作/64 输入/12000 边上限（`:121-123`）并回报 truncated 与遗漏计数（`:1674-1705`）。v6.5 增量在 sidecar：`ReaGhidraApplySeeds`（151 行，配 TS 侧 `GhidraAnalysisSeeds.ts` 285 行）注入分析种子、`NoReturnFix`（123 行）/`MipsSoftFloat`（176 行）修正 no-return 与 MIPS 软浮点、`PrepareRaw`/`PrepareCom`/`AnalysisOptions`/`BundleActivator` 补备料与挂载；语言面由 `GhidraLanguageCatalog.ts`（209 行）+Mips/Psp/Riscv/PowerPc/RawBinary/Pe 六族 Profile 铺开（.NET NativeAOT 扩展平移至 bridge/nativeaot/，4 个 Java 文件 361 行）。

**HopperProvider：候选装配器。** 只认 darwin/linux 且 launcher `accessSync(X_OK)`（`src/hopper/HopperProvider.ts:82`）；DOS MZ/COM 显式让位 Ghidra 16 位适配器（`:158`）。`createClient`（`:181`）先对 profile 的 `prepared_image` 做 zod 校验（`:200-204`），失败返回"永远失败"的 client 而非抛异常（`:206-221`）；Linux 切 `verified_linux_demo`（`:259`）；`execute` 三条旁路——regex 改道 `HopperRegexSearch`（`:272`）、`address_to_file_offset` 映回原始 FAT 偏移（`:318`）、thin slice 注入 limitations 声明身份指向原文件（`:291`）。setup 侧 v6.5 支持下载安装：`HOPPER_DOWNLOAD_BYTES` 上限 100,000,000 字节（`src/application/HopperDownload.ts:2`）+ ReleaseFeed 与 Mac/Linux Publisher。

**IdaMcpConnection：薄 MCP 客户端。** 工厂 `createIdaMcpConnection`（`src/ida/IdaMcpConnection.ts:339`）含 `command` 走 stdio 否则 StreamableHTTP（`:417-438`）。`decodeIdaToolResult` 统一解包，`output_truncated` 为真直接抛 `AnalysisProtocolError` 拒绝建立观察（`:106-110`）——截断预览宁可不要；凭据剥除移到 `IdaDiagnosticRedactor`（authorization/cookie，`src/ida/IdaDiagnosticRedactor.ts:154-164`）；stdio 强制 `IDA_MCP_MAX_WORKERS=1`（`:432`）。新增 `IdaNativeProtocol.ts`（native MCP 输出 zod 契约）、`IdaCallGraph.ts`、`IdaBusyHealth.ts`。

### 3. 外部连接

共同上游是应用层契约（`AnalysisProvider.ts:285`）与核心 `AnalysisError` 错误族。Ghidra 被 `GhidraProvider` 经可注入 `clientFactory` 默认装配（`src/ghidra/GhidraProvider.ts:88`）。IDA 同构：`IdaProvider` 注入 `connectionFactory`（`src/ida/IdaProvider.ts:45`），`IdaSessionClient` 将工具目录与 profile 对账——legacy 十工具与 modern 清单（`src/ida/IdaSessionClient.ts:53-65`）缺一即抛错（`:523-530`），headless 专属操作另有门（`:249-260`）。进程基础设施 Ghidra/Hopper 共享（`PrivateRuntimeRoot`+`ProviderProcessSupervisor`）。Hopper 桥脚本用 `import.meta.url` 定位（`HopperProvider.ts:255`），已迁到 bridge 根（`bridge/hopper_bridge.py` 1181 行，`:1028` 服务 NDJSON、`:1148-1153` chmod 0600 单客户端 socket）；与 Ghidra `-postScript`+`-readOnly`（`src/ghidra/GhidraLauncher.ts:728`、`:672`）互为镜像。

### 4. 数据流

以 Ghidra `analyze_function` 为例：MCP 工具→`callTool`（`src/ghidra/GhidraClient.ts:356`）先确保 `start()`——launcher 写描述符并拉起 JVM→Java 绑定 socket 并 chmod `rw-------`（`bridge/ghidra/ReaGhidraBridge.java:266`）→TS 握手 ping，拒绝 `analysis_timed_out`（`src/ghidra/GhidraClientStartup.ts:51`）→请求入队→队首后写一行 `{id,token,method,params}`→Java readLine 鉴权分派到 `analyzeFunction`（`:1533`）：解析 procedure→扫指令→反编译→组装伪代码/汇编/引用/`native_api` 边界（`:1594`/`:2243`）与 pcode 值流→`writeSuccess` 回一行 JSON→buffer 切行、router 配对。关闭时先发 10s 超时 `shutdown` 并校验回执（`GhidraClient.ts:86`、`:911-930`）。IDA 同流更短；Hopper 多一道 bootstrap 注入。

### 5. 设计决策

**为什么自造行式协议？** 自有桥是单客户端、单目标、短命会话：unix socket 文件权限+随机 token+常量时间比较即完整认证面；把 MCP SDK 拖进 JVM/Python 宿主只会扩大攻击面。**mutation 权威绑定 transport** 是最漂亮的取舍：Windows 只有回环 TCP（无文件权限护城河），故 mutation 与扩展在非 unix-socket 上直接禁用（`ReaGhidraBridge.java:504-510`），读写权限由传输介质而非代码分支决定，TS 侧用 `expectedReadOnly` 对账（`GhidraClient.ts:863`）。**注释回写自带验证**：提交前逐字段比对读回值，不符抛 `annotation_readback_mismatch`（`:1460-1469`）。**诚实失败三例**：IDA 拒绝截断输出、Ghidra 拒绝超时分析、Hopper 畸形 profile 返回永久失败 client（`HopperProvider.ts:206-221`）——宁无观察不坏观察。**注入缝隙**贯穿：platform/clientFactory/connectionFactory 全部默认参可注入（`HopperProvider.ts:56`、`IdaProvider.ts:45`），测试无需真实引擎。**sidecar 化扩展**：桥主类只留协议骨架，语言修正/种子/选项拆成独立 Java 小类随桥源分发，新架构不必碰主类。

### 6. 新人提示

先读候选接口（`AnalysisProvider.ts:285`），再按 Ghidra→Hopper→IDA 由厚到薄读 provider。易错点：Java 桥 `requireObject`/`requireKeys` 是**全键集合相等**（`ReaGhidraBridge.java:4691-4702`），多传一个字段即拒——调试时别往 params 塞调试键；描述符生命周期分平台（POSIX 读后即删 `:197`、Windows 保留到关闭）；地址有 REA 专属编码（space+offset），解析在 `:4512`。测试入口：`GhidraProvider.behavior.test.ts`、`HopperProvider.test.ts`、`IdaMcpConnection.test.ts`；真实行为只有 `npm run verify:*` 可验（ghidra 有 10 个架构变体），vitest 全是 fake。加新能力要同步四处：Java `CAPABILITIES`（`:142`）、TS operation union、zod schema、能力描述表。
