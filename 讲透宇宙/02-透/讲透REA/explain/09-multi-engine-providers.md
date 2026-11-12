<!-- source: knowledge-graph tour step | files: src/composition/binary.ts, src/kuna/KunaProvider.ts, src/application/AnalysisProvider.ts, src/dotnet/ManagedStaticProvider.ts, src/android/JadxProvider.ts, src/native/NativeMacOSProvider.ts, src/evm/EvmoleInterfaceProvider.ts, src/firmware/FirmwareProvider.ts -->

# 09 · 多域引擎接入：从五路 provider 到三轨道版图

### 角色定位

v6.1.0 时本篇讲"五路 provider 同构"；v6.5.0 多域接入长成三轨道版图——src/ 新增 19 个顶层子系统（约 120 文件/3.3 万行），全部复用同一骨架：不可信引擎与字节输入关进 0700 私有工作区、prlimit 资源限制、`Result<T, AnalysisError>` 投影稳定 code/category。三条轨道接入深度不同：

1. **深度 provider 轨**：可被 binary session 选中。注册表只有四席 `[hopper, ghidra, ida, kuna]`（src/composition/binary.ts:32），kuna 是 v6.5 唯一新增深度 provider。
2. **领域 Port+契约轨（主流新轨道）**：`application/<area>/<Area>Port.ts` 端口 + `contracts/<area>/` 契约族 + `composition/<area>.ts` 薄装配，不进注册表，属 artifact/observation 型——adb/apktool/captures/pcap/flutter/frida/go/jeb/rust/signals/sqlite/wasm/electron 十四族。
3. **RE 工具直通轨**：gdb/rizin/objdump/cutter 是 caller-supplied 命令/会话通道，只有工具契约、无 provider 抽象（docs/reverse-engineering-tools.md:3）。

契约本体没膨胀：`AnalysisOperation` 六成员不变（AnalysisProvider.ts:36-42）；`AnalysisExecution` 新增 relationshipCoverage/referencesTruncated/selectorOrigin（:32、:52-59）——诚实字段下沉契约。

### 内部结构

**深度轨 kuna**：src/kuna/ 24 文件 6288 行，新子系统之最。KunaProvider.ts:54 `implements AnalysisProviderCandidate`。kuna 是 Noelo-Lab 的 Apache-2.0 反编译器、单个可执行文件（docs/kuna-provider.md:3）；BYO 铁律——REA 不下载/安装/更新（KunaRelease.ts:8），`REA_KUNA_COMMAND` 指定绝对路径，`--version` 对照 `KUNA_VERIFIED_VERSION = "1.833"`（KunaRelease.ts:2），其他版本在 doctor/profile 标 unverified 而非拒绝。

**Port 轨**：端口是小接口——AdbDeviceAnalysisPort/ApktoolResourceAnalysisPort/WasmArtifactPort/JebAnalysisPort/GoBinaryPort/RustBinaryPort/SqliteDatabasePort/ElectronFusePort/FridaInstrumentationPort（17-136 行）；PacketCapturePort/SignalRecordingPort 定义在各自 Service 内（PacketCaptureService.ts:27）。代表 provider：AdbProvider.ts:564、ApktoolProvider.ts:340、PcapProvider.ts:131、JebProvider.ts:105（BYO JEB MCP）、GoBinaryProvider.ts:173、RustBinaryProvider.ts:40、FlutterBuildProvider.ts:334、SigrokRecordingProvider.ts:67、TsharkCaptureProvider.ts:68（二者 :133/:137-150 各配 REA_*_COMMAND+prlimit）、WabtArtifactProvider.ts:46（:109 REA_WABT_BIN_DIRECTORY）、ElectronFuseProvider.ts:45、SqliteDatabaseProvider.ts:60。

**直通轨**：GdbSessionManager.ts 2240 行 GDB/MI 持久会话（:532 `REA_GDB_COMMAND ?? "gdb"`）；RizinDebugSessionManager.ts 1590 行（inferior_tty :284+/proc 验证）；ObjdumpCommand.ts:11 只做 argv 构造、被 composition/reverseEngineering.ts:24 消费；Cutter 桥=bridge/cutter/rea_bridge.py（816 行）+CutterBridgeClient.ts（:23 只许 127.0.0.1、:25 token≥20、:834-844 HMAC 握手证明）。frida 特殊：optionalDependencies frida@17.23.2（package.json:393-394），FridaInstrumentationManager.ts 1507 行，fridaToolContracts 9 个 MCP 工具。

**原五路现状（锚已全重核）**：ManagedStaticProvider.ts:50 零进程，:110-114 admission sha256 不符抛 EvidenceIntegrityError；NativeMacOSProvider.ts:101（#dispatch :459、三路 capture :594-611、"disappearing target" :751、isNonzeroUnsignedObservation :1013），新增 PE 资源族 pe/PeResourcesProvider.ts:22；JadxProvider.ts:279（#tail/#retained/#idle :280-283、会话键 JSON.stringify :422），Java 桥 ReaJadxBridge.java 368 行；EvmoleInterfaceProvider.ts:145（:70 z.literal("0.9.3")、三 phase :201、Linux x64 :208），新增 SolidityMetadata.ts（cborg 解 CBOR）；FirmwareProvider.ts:105（regions→binwalk 否则 unblob :229、--version 准入 :271、limitations :96）。

### 外部连接

深度轨唯一生产入口 createBinarySession（binary.ts:20-38）：四 provider 进 `AnalysisProviderRegistry`；auxiliary 声明（auxiliaryAnalysisProviders.ts:19，Native :38-40、Managed :47-49）经 LazyAnalysisProvider 懒挂。Managed 独占通道 createManagedBinarySession 空 registry 只挂它（binary.ts:42-45）。Port 轨装配在 composition/<area>.ts 薄文件，被 CLI（src/cli/ 50 个平铺命令文件）与 server（createServer.ts 919 行、36 个 register*Tools）双侧消费——firmware :320、pcap :348、adb :367。契约树 contracts/ 扩到 17 子目录、36 个工具组（toolContracts.ts:39-76 spread 聚合）。私有工作区底座 PrivateRuntimeRoot 移至 src/process/PrivateRuntimeRoot.ts:45；filesystem/（OwnedFileHandle/StableFileHash）被 kuna/jeb/adb 复用作所有权句柄。

### 数据流

kuna 会话模型（新深度轨代表，四步）：

1. **admission**：定位 BYO 命令+`--version` 验证；非 1.833 版本产出 unverified 观察而非错误。
2. **项目导出**：后台 `kuna decompile-project --jobs 1` 在目标私有副本上建导出（KunaProjectCache.ts:76，`--jobs 1` 是 reference 答案，导出缓存在 REA 拥有的 KunaProjectExport）。
3. **伪代码/库存**：单函数 `kuna decompile --addr`（KunaSessionClient.ts:1063）；函数/字符串走 `kuna functions/strings --json` inventory（KunaCommand.ts:38，~210 字节/函数预算放行至 60 万函数）。
4. **产 Evidence**：result/limitations/locations 经 createAnalysisExecution（AnalysisProvider.ts:81）原子化，analysis profile 记录 kuna 版本验证态。

### 设计决策

**BYO 纪律**。所有外部引擎 caller-supplied，统一 `REA_<TOOL>_COMMAND` env；Linux 上 captures/signals 还强制 util-linux prlimit（TsharkCaptureProvider.ts:137、SigrokRecordingProvider.ts:133）——捕获面越大，资源边界越要先钉死。

**清理所有权**（v6.5 新原则）。AnalysisProviderCandidate 增 hasPendingOwnedResources()/closeOwnedResources()（AnalysisProvider.ts:294-296）；AnalysisError 增 cleanupIncomplete/cleanupResources（analysisErrorBase.ts:68-69）+ domain/analysisErrorCleanup.ts。Jadx 旧的粘性 `#cleanupFailure` 演化为 `#pendingCleanup` 记账（JadxProvider.ts:352-363）：清理失败被保留、经 owner 再解决，而非静默成功——AGENTS.md 钉为 owner 原则。

**诚实字段**。referencesTruncated 三态：true=报告了截断、false=显式报告无截断、缺失=不作完整度声明；relationshipCoverage 是 provider 对 caller/callee 观测的自评覆盖——"没报告"不等于"没截断"。

**零引擎纯解析五族**。go/rust/flutter/electron/sqlite 不 spawn 任何外部进程：Go ELF/Mach-O/PE 三镜像解析（GoElfImage/GoMachoImage/GoPeImage）、cargo-auditable 内嵌依赖图（RustAuditableReader）、Dart VM snapshot hash、Electron fuse 位、SQLite 用 Node 原生 node:sqlite（SqliteDatabaseInspection.ts:1，SqliteDatabaseWorkerExecution.ts worker 隔离）——能静态解析就不引入新供应链面。

### 新人提示

上手：AnalysisProvider.ts 契约（六 operation+三诚实字段）→ kuna（新深度轨样本）→ 任选 Port 轨一族（推荐 sqlite：零 BYO 依赖）→ gdb/cutter 直通轨。易错点：①注册表只有四席，新领域默认走 Port 轨，别硬挤深度轨；②kuna 非 1.833 不是错误而是 unverified 观察；③Evmole 仍只支持 Linux x64（EvmoleInterfaceProvider.ts:208），worker exit 76 是 EFBIG 哨兵、须同时核对单字节 "F" marker（EvmoleRelease.ts:8、EvmoleInterfaceProvider.ts:478）；④PrivateRuntimeRoot 已搬到 src/process/，老路径引用失效。
