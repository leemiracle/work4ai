# REA v6.1.0 → v6.5.0 变化事实底稿（2026-10-16 文档同步用）

> 基线 commit `441813c0`（v6.1.0，2026-10-09 快照）→ HEAD `1bd5c5c8`（v6.5.0，2026-10-16）。
> 期间 1845 个提交、3656 文件变更（+951,858/−60,583）、src/ 1283→1969 文件。
> 本文件是 ONBOARDING/explain/README 同步的单一事实源；所有条目经源码/git 实证。

## 0. 版本与规模速查

| 项 | v6.1.0 | v6.5.0 |
|---|---|---|
| 版本 | 6.1.0 | 6.5.0（npm 包 rea-agents） |
| 全仓 tracked 文件 | 2246 | 4030 |
| src/ 文件 | 1283 | 1969 |
| src/ 顶层目录 | 20 | 43（新 23 个） |
| src/domain/ 文件 | 409 | 608（子目录 8→22） |
| npm scripts | ~138 | 209（+73/−2） |
| 仓根 README 语言镜像 | 16 个 README*.md | 1 个（19 语言镜像迁 docs/readme/） |

## 1. 新增分析子系统（src/ 新顶层目录 19 个实质子系统，~120 文件/3.3 万行）

| 目录 | 规模(文件/行) | 职责 | 关键锚点 | 引擎依赖 | 接入方式 |
|---|---|---|---|---|---|
| adb | 11/3782 | Android 设备检视+文件/包传输 | AdbProvider.ts:564;AdbShellOutput.ts:100 | BYO adb | Port(adb/AdbDeviceAnalysisPort)+契约 contracts/adb/ |
| apktool | 8/1461 | 解码 Android 资源表+二进制 manifest | ApktoolProvider.ts:340;REA_APKTOOL_COMMAND | BYO apktool | Port+契约 |
| captures | 3/694 | 已存 capture 选定协议字段检视 | TsharkCaptureProvider.ts:68 implements PacketCapturePort;:137 REA_TSHARK_COMMAND(+prlimit) | BYO tshark | Port+契约 contracts/captures/ |
| cutter | 2/1103 | Cutter(Rizin GUI)桥接会话 | CutterBridgeService.ts:36;CutterBridgeClient.ts(zod 校验 127.0.0.1+token) | BYO Cutter GUI；桥=bridge/cutter/rea_bridge.py(816 行) | 工具契约 contracts/cutterToolContracts.ts，非 provider |
| electron | 4/1003 | Electron fuse 位纯解析(inspect_electron_fuses) | ElectronFuseProvider.ts:45 implements ElectronFusePort | 纯 Node | Port+契约 |
| filesystem | 7/612 | 所有权句柄/stable hash/staged 输出共享基建 | OwnedFileHandle.ts/StableFileHash.ts/OwnedDirectoryHandle.ts | 纯 Node | 非 provider，被 kuna/jeb/adb 复用 |
| flutter | 8/2661 | APK 识别 Flutter 构建事实(Dart VM snapshot hash/build-id) | FlutterBuildProvider.ts:334;DartElf.ts | 纯 Node | 契约 contracts/flutter/ |
| frida | 2/1588 | 动态插桩：设备/进程发现、attach/spawn、脚本注入 | FridaInstrumentationManager.ts:104(1507 行)；frida-bindings.d.ts | **optionalDependencies frida@17.23.2**(Node 绑定) | Port+契约 contracts/fridaToolContracts.ts(8 个 MCP 工具) |
| gdb | 1/2240 | GDB/MI 持久调试会话(Linux only) | GdbSessionManager.ts(:1024 spawn "gdb") | BYO gdb | 工具契约 contracts/gdbToolContracts.ts |
| go | 7/1878 | Go 二进制内嵌构建元数据(ELF/Mach-O/PE) | GoBinaryProvider.ts:173 implements GoBinaryPort;GoElfImage/GoMachoImage/GoPeImage | 纯 Node | Port+契约 contracts/go/ |
| jeb | 6/859 | JEB 项目/单元/反编译检视 | JebProvider.ts:105 implements JebAnalysisPort;JebMcpConnection.ts | BYO JEB 自带 MCP server(默认 127.0.0.1:8425/mcp,REA_JEB_MCP_URL) | Port+契约 contracts/jeb/ |
| **kuna** | **24/6288 最大** | Kuna 反编译器深度 provider | KunaProvider.ts:54 implements AnalysisProviderCandidate | BYO kuna 可执行文件(REA_KUNA_COMMAND,验证版本 1.833) | **深度 provider**(见下) |
| objdump | 1/26 | GNU objdump argv 构造 | ObjdumpCommand.ts:11 | BYO objdump | 命令构造器，被 composition/reverseEngineering.ts 消费 |
| pcap | 8/1793 | pcap/pcapng 摘要(地址/DNS/SNI/协议栈) | PcapProvider.ts:131;REA_TSHARK_COMMAND/REA_CAPINFOS_COMMAND | BYO Wireshark 4.x tshark+capinfos | 契约 contracts/pcap/ |
| rizin | 2/1607 | rizin 一次性命令+持久调试会话(Linux,inferior_tty+/proc 验证) | RizinDebugSessionManager.ts:242(1590 行)；RizinCommand.ts | BYO rizin | 工具契约 contracts/rizinDebugToolContracts.ts |
| rust | 4/843 | cargo-auditable 内嵌依赖图纯解析 | RustBinaryProvider.ts:40 implements RustBinaryPort;RustAuditableReader.ts | 纯 Node | Port+契约 contracts/rust/ |
| signals | 2/612 | sigrok 录制解码 | SigrokRecordingProvider.ts:67 implements SignalRecordingPort;:133 REA_SIGROK_COMMAND | BYO sigrok-cli 0.7.2+(Linux+prlimit) | Port+契约 contracts/signals/ |
| sqlite | 8/1859 | SQLite 快照检视，**零外部安装** | SqliteDatabaseProvider.ts:60 implements SqliteDatabasePort;SqliteDatabaseWorkerExecution.ts:106(worker 隔离) | Node 24.15+/26 原生 node:sqlite DatabaseSync.limits | Port+契约 contracts/sqlite/ |
| wasm | 12/1390 | 离线 WASM 产物检视(不执行) | WabtArtifactProvider.ts:46 implements WasmArtifactPort;:109 REA_WABT_BIN_DIRECTORY(wabt@1.0.42) | BYO WABT 1.0.42(spawn wasm-objdump) | Port+契约 contracts/wasm/(接口对比 spec 2356→WasmInterfaceComparisonService.ts) |

**kuna 身份**：非内部代号。Noelo-Lab 开源 Apache-2.0 反编译器，单个 kuna 可执行文件
（docs/kuna-provider.md:3）。BYO（绝不下载/安装/捆绑），版本 1.833 验证，其他版本在
doctor/profile 标 unverified。会话模型：后台 kuna decompile-project 在目标私有副本上建
导出（KunaProjectCache/KunaProjectExport），伪代码 kuna decompile --addr，函数/字符串
kuna functions/strings --json inventory。

**三条接入轨道**：
1. 深度 AnalysisProvider（可被 open_binary 选中）：注册表仅 4 个——`[hopper, ghidra, ida, kuna]`
   （src/composition/binary.ts:19-26）。**kuna 是唯一新增深度 provider**。
2. 领域 Port+工具契约（主流新轨道）：三层结构——application/<area>/<Area>Port.ts 端口
   （PacketCapturePort/SignalRecordingPort/WasmArtifactPort/JebAnalysisPort/GoBinaryPort/
   RustBinaryPort/SqliteDatabasePort/ElectronFusePort/AdbDeviceAnalysisPort/
   ApktoolResourceAnalysisPort/FridaInstrumentationPort）+ contracts/<area>/ 契约族（15+ 新
   文件）+ composition/<area>.ts 薄装配（6-58 行）。不进 Registry，属 artifact/observation 型。
3. RE 工具直通：gdb/rizin/objdump/cutter 是 caller-supplied 命令/会话通道
   （docs/reverse-engineering-tools.md:3），仅工具契约无 provider 抽象。
   配置门面统一 REA_<TOOL>_COMMAND env 模式，captures/signals 带 prlimit。
   **零引擎纯解析五族：go/rust/flutter/electron/sqlite**。

## 1b. 既有 provider 大变化

- **ghidra（+13385/−1056，60 文件，最大增量）**：ReaGhidraBridge.java 3404→**4892 行**；
  新 6 个 Java sidecar：BundleActivator/AnalysisOptions/**ApplySeeds**(151,配 GhidraAnalysisSeeds.ts
  285)/NoReturnFix(123)/MipsSoftFloat(176)/PrepareRaw；新语言/架构配置族
  GhidraLanguageCatalog.ts(209)+Mips/Psp/Riscv/PowerPc/RawBinary/Pe Profile（新文档
  ghidra-mips/ppc/psp/riscv/raw-binary）；nativeaot 扩展平移至 bridge/nativeaot/。
- **ida（+8504，31 文件）**：新 IdaNativeProtocol.ts（native MCP 输出 zod 契约）、IdaCallGraph.ts、
  IdaBusyHealth.ts、IdaDiagnosticRedactor/Writer（诊断脱敏链）。
- **dotnet（+8782，44 文件）**：Managed* 快照解码族大扩（ManagedSnapshot/ManagedMethodSpecs/
  ManagedUserStrings/ManagedTypeNames/ManagedMemberPointers 等 11+ 新文件）。
- **android**：ReaJadxBridge.java 256→368 行；新 JadxDoctor.ts、JadxWorkspaceRoot.ts。
- **native（+7637，51 文件）**：新 PE 资源解析（pe/PeResourcesProvider/PeResourceParser/
  PeResourceLayout）、pwntools 解码器+460 行、MachoArchitectureSelection、machoUuid。
- **hopper**：新 HopperMacPublisher.ts+HopperDownload.ts(100MB 上限)+HopperReleaseFeed+
  LinuxHopperPublisher——setup 支持下载/安装 Hopper（原仅 Linux 官方包）。
- **evm**：新 SolidityMetadata.ts（CBOR metadata，docs/specs/solidity/cbor-metadata/）。
- **firmware**：FirmwareProvider(+284)/FirmwarePublication(+343)/FirmwareReports(+272) 扩展。
- **AnalysisOperation 联合无新成员**（src/application/AnalysisProvider.ts:36-42 六成员不变）；
  真变化：AnalysisExecution 新增 relationshipCoverage/referencesTruncated/selectorOrigin（:32,:52-59）；
  AnalysisProviderCandidate 新增 hasPendingOwnedResources()/closeOwnedResources()（:294-296，
  对应"清理所有权"系列提交）。

## 2. 契约层与入口面（explorer B 实测，jiti 运行时取数）

- **TOOL_CONTRACTS：19 group → 36 group；工具总数 138 → 207**（jiti 实测）。
  `src/contracts/toolContracts.ts:39-76` 只做 spread 聚合；contracts 目录 7→**17 子目录 /
  88 个 .ts**。36 group 顺序：OFFICIAL, ENHANCED, NATIVE, BINARY_DIAGNOSTICS, ANALYSIS_VIEW,
  ARTIFACT, EVM, GO, RUST, WASM, SQLITE, CAPTURE, SIGNAL, MANAGED, ANDROID, APKTOOL, PCAP,
  FLUTTER, JEB, ADB, FIRMWARE, MANAGED_WORKFLOW, BROWSER_PROVIDER, ELECTRON,
  JAVASCRIPT_RUNTIME_OBSERVATION, APPLICATION, WEB_SCRIPT, WEB_RUNTIME, WEB_NETWORK_CAPTURE,
  JAVASCRIPT_RECOVERY, SESSION, CUTTER, REVERSE_ENGINEERING, GDB, RIZIN_DEBUG, FRIDA。
  大 group 规模：OFFICIAL 38 / SESSION 21 / ADB 24 / ANDROID 43 / GDB 45 / GO 45 / CAPTURE 36
  / FIRMWARE 34 / FLUTTER 34 / JEB 34 / CUTTER 26 / APKTOOL 27 / APPLICATION 28 / ARTIFACT 99 量级。
  MCP_PROMPTS = 6 条（src/contracts/promptContracts.ts）。
- **PUBLISHED_TOOL_NAME_FLOOR 已不存在**：toolContracts.test.ts（238 行）在 b71a591a6
  （2026-10-09 "test: consolidate redundant assertions into boundary workflows"）整体删除，
  无替代 floor 清单——改为 tests/boundary/ 行为化断言（tests/boundary/mcp/serverIdentity.test.ts:114-118
  校验 CATALOG_IDENTITY.counts）。
- **toolEffects 8→10 维**：新增 executesForeignCode（0b7fc40ee，#1904）与 mutatesDevice
  （4a4ae9b2b，#1359 Frida）。10 键：mutatesTarget/mutatesSession/writesFilesystem/
  launchesProcess/accessesNetwork/changesUiState/mayDiscardData/executesForeignCode/
  mutatesDevice/idempotent。
- **compactInputSchema.ts（新增）**：MCP input schema 压缩呈现。开关
  REA_MCP_INPUT_SCHEMA_PROFILE=full|compact（src/config/mcpInputSchemaProfile.ts:8-35），
  compact 预算 13 KiB（Kimi/Moonshot 单工具 schema 上限 ~13.7KB，issue #1484）；
  输出带 presentation: "inline"|"reduced"；createServer.ts:339 注入；b3389a5b0 数组 items
  用 {type:[六种JSON类型],items:{}} 万能 schema 保嵌套值。
- **CLI**：命令注册器 23→**38 组**（src/cli.ts:99-136）；CLI_COMMAND_NAMES 94→**153**
  （+59/−2）；CLI_COMMAND_TOOL_ALIASES 9→**19 组/20 条**（src/cliCommandNames.ts:166-187）；
  src/cli/commands/ 不存在——50 个文件平铺在 src/cli/（adbCommands/fridaCommands/
  cutterCommands/pcapCommands/goCommands/rustCommands/sqliteCommands/wasmCommands…）。
  新命令族：frida list-frida-devices/list-frida-processes/instrument-with-frida；rizin
  execute-rizin-command/debug-with-rizin；gdb debug-with-gdb；cutter list-cutter-sessions/
  cutter-command；objdump inspect-with-objdump/list-objdump-architectures；wasm
  inspect-wasm-artifact/compare-wasm-interfaces；go inspect-go-binary；rust
  inspect-rust-binary；sqlite inspect-sqlite-database；pcap inspect-pcap-client/
  inspect-pcap-capture；adb 24 条；jeb 4 条；project-harmony-application-graph。
  删除：comment、compare-bundles。
- **MCP server**：createServer.ts 919 行；CreateServerOptions 可注入依赖 23→**35 项**
  （:149-186）；register*Tools( 调用 19→**36**；src/server/register*Tools.ts 共 **36 个文件**
  （registerAdbTools/…/registerFridaTools/registerGdbTools/registerRizinDebugTools/
  registerWasmTools/registerGoTools/registerRustTools/registerSqliteTools/
  registerPcapTools/registerCutterTools/registerRecordedCrashTools…）。
- **setup 客户端 14→25**（src/application/SupportedClients.ts:486-700）：原 14 全保留
  （claude_code/claude_desktop/codex/cursor/gemini_cli/windsurf/devin/opencode/antigravity/
  copilot_cli/commandcode/vscode/grok_build/grok_bot），新增 11：qwen_code/kimi/trae/
  workbuddy/omp/pi/hermes/qoder/droid(Factory Droid)/zcode/dsh(DeepSeek Harness)（:578-688）；
  format 枚举扩 omp/pi/kimi/hermes/zcode/zcode_fallback/dsh（:48-64），新字段
  geminiSettings/zcodeFallbackPath/msixPackage/quitBeforeSetup/skillPath。
- **package.json**：CHANGELOG 6.2.0/6.3.0=2026-10-09、6.4.0=10-11、6.5.0=10-13；
  dependencies 32→40（新增 @xmldom/xmldom/cborg/openpgp/saxes/stream-chain/stream-json/
  tokenx/yaml）；optionalDependencies 新增 frida 17.23.2；devDependencies 18→23。
- **README 语言镜像**：19 个镜像未删，整体迁 docs/readme/（cbe769b50，2026-10-13，
  #2165），README.md:3-4 保留语言链接（zh/zh-TW/ja/ko/tr/ru/vi/th/de/es/fr/uk/pl/pt-BR/
  ar/fa/id/it/el，旧 16→现 19）；website/locales/ 另有 20 个站点语言目录。

## 3. domain 层（explorer D 已回）

- 409→608 文件；子目录 8→22，新增 14：adb(2)、**analysisView(31，最大新子域，
  统一"分析视图"投影层：androidPackageView/binaryLayoutView/machoView/dartAotView/
  evmInterfaceView/javascriptApplicationView 等)**、apktool(1)、captures(2)、electron(2)、
  flutter(1)、go(1)、harmony(1)、jeb(1)、pcap(2)、rust(1)、signals(4)、sqlite(1)、wasm(2)。
- 错误 tag 27 个**一字未改**（src/domain/analysisErrorBase.ts:5-34）；核心错误类 10 个同名未变。
  AnalysisError 本体新增 diagnostics 字段、cleanupIncomplete/cleanupResources（:81-82）；
  新文件 src/domain/analysisErrorCleanup.ts（近期 cleanup 归属治理提交链：
  3ed925e54/1bd5c5c87/6e74704f9/ca7ee018b）。
- javascript/ 子树 126→214 文件（+88，单子域扩张冠军）；javascriptApplicationGraph.ts
  499→656 行仍是高连接度核心；新增 electronStaticAnalysis* 8 文件、electronActiveObservation、
  javascriptApplicationChangeGraph 等。
- **evidenceEnvelope 已废除（v6.2 breaking，必改）**：旧 `{result, evidence_id, evidence}`
  包装移除，Evidence-producing 工具把完整 Evidence 直接放进 structuredContent 与 JSON text；
  `value = evidence.normalized_result`（docs/migration-6.2.md:7-24）。
- 三分扩展为四分措辞："observations, derivations, inferences, unknowns"（AGENTS.md:3）；
  evidenceAuthoritySchema 五枚举 shipped-artifact/controlled-replay/historical-reference/
  external-service/analyst-inference（src/domain/evidence.ts:109-115）。
- Every Evidence 必填 analysis_profile（observed profile 对象或 null），参与 Evidence
  身份（migration-6.2.md:50-55）。
- residual unknown 机制健在：src/domain/residualUnknown.ts（414 行，ResidualUnknown/
  UnknownStatus/RecordUnknownInput/UpdateUnknownInput，:123,244,266,284）。
- provenance 是横向原则（AGENTS.md:3 "Preserve Evidence provenance"），落点散布
  artifactGraph/hopperValues/browserNetworkEvidence/artifactInventorySnapshot 等。

## 4. v6.2 其余 breaking（migration-6.2.md，文档必改点）

- binary_session 结果删顶层 provider/providers 别名 → 读 analysis_provider_binding/
  analysis_provider_candidates（migration-6.2.md:57-61）。
- 快照要求 workflow_entries + 每个 cached query 的 profile-bound Evidence；import 拒绝
  不完整绑定（:68-82）。
- Artifact inventory：nodes 表内容身份（artifact_id/sha256/format），per-path 角色/权限
  移到 occurrences[]（artifact_kind/artifact_format/executable）（:84-101）。
- 进程捕获不再转换 legacy v3；必须显式 executable identity + event_journal（:103-112）。
- filesystem effects 可报 status:"unknown"+reason（:114-116）；一次性分析可报
  cleanup_incomplete 而非静默成功（:118-125）。
- JS presence 三态 present/absent/unknown-coverage；property_path 是完整段数组或 null（:127-137）。
- 函数比较维度状态收敛为 unchanged/changed/unknown，truncated 移除（:139-143）。
- symlink target_state unreadable/unknown 要求 target:null，外部目标用观测绝对路径（:145-153）。

## 5. bridge 层（explorer D 已回）

- 24→32 文件（+4224/−452 行）。
- ReaGhidraBridge.java **3404→4892 行**；能力 case 26→28 个。
- hopper_bridge.py 1181 行；native/rea_lldb_tracer.py 917 行（+新 test 442 行）；
  process/ProcessRunTokenReader.swift 339 行（本轮 +110）；mitmproxy/capture.py 384；
  pwntools/ layout_impl 314 + recorded_crash_impl 168 + decoder_runtime 59；
  pwndbg/core_context.py 101；android/ReaJadxBridge.java 368。
- **新增两座桥**：bridge/cutter/rea_bridge.py（816 行，Cutter/Rizin）；
  bridge/nativeaot/（5 个 Java 文件共 1177 行，.NET NativeAOT 的 Ghidra 扩展）。
- ghidra/ 其余：MipsSoftFloat(176)/NoReturnFix(123)/ApplySeeds(151)/Extensions(113)/PrepareRaw。

## 6. 测试/质量基建（explorer C 已回）

- vitest **11→12 project**（+cli-boundary；清单外置 scripts/lib/test-projects.mjs:6-76）；
  新增 vitest.reverse-tools.config.ts（36 测试文件，13 个"逆向工具"源文件的专用覆盖/
  突变基座）与 vitest.reverse-tools-semantics.config.ts（3 文件走 processOwnershipRunner）。
- **Stryker 突变测试全新**：stryker.config.mjs（vitest runner+related+perTest）+
  stryker.semantics.config.mjs（command runner，专突变超时/进程语义）+
  scripts/lib/reverse-tools-mutation-targets.mjs（TS AST 方法级 mutate 区间）+
  tsconfig.reverse-tools-mutation.json；入口 test:mutation:reverse-tools；CI mutation.yml。
- tests/：boundary 315→730、acceptance 15→102、conformance 59→106（目录 17→18，+psp）、
  fixtures 127→204；新增 tests/ciTestSequencer.ts（CI 历史耗时排序）。
- **CI：ci.yml 14→20 job**；workflow 17→30（新 ci-full-pr/ci-timings/mutation/pr-readiness/
  pr-title/release-recovery/sqlite-runtime/ghidra-bridge-sources/real-cutter/real-go-binary/
  real-packet-capture/real-signal-recording/real-termux）。
- scripts/lib 73→126；新 scripts/ci/（28 文件自研 CI 编排库）与 scripts/fixtures/。
- npm verify:* 约 **45 个**（ghidra 10 个架构变体、AI client 8 个、wasm/solidity/go/pcap/
  harmony/flutter/jeb/cutter/kuna/adb/apktool/frida…）。
- 新根目录合规三件套：licenses/（19 项第三方许可证，Ghidra 12.1.4/frida-17.23.2 等）+
  THIRD_PARTY_NOTICES.md + DISCLAIMER.md（合法分析用途声明）；licenses:generate/check
  已挂 docs:check:built。
- tsconfig.frida-verification.json：2 文件独立 noEmit 工程，验证 Frida 绑定声明
  （npm run verify:frida:bindings）。
- experiments/analysis-efficiency/（77 文件）：分析效率实验区（完整投递 vs 摘要/分页/
  选择式投递的字节与成本对比，跟踪 issue #2016）。

## 7. 规范与文档（explorer D 已回）

- **AGENTS.md 整体改写**（147 行 diff）："dependencies flow inward" 原则在（新表述：
  domain semantics and contracts → provider adapters → shared application workflows →
  CLI/MCP adapters）。新增三块：Product and Authority（fail-closed integration）、
  Architecture and Cleanup（**owner 原则**："Give each interpretation and resource a
  clear owner"、"Retain ownership of resources whose cleanup failed"）、Performance
  （优化次序：agent tokens/context > 分析时间 > CPU/内存）。细节外移 CONTRIBUTING.md。
- **CONTRIBUTING.md 重构**：新增 Contribution scope（含 Fail-closed integration :149）、
  PR ownership/readiness、Maintainer release checklist；Node 钉版不再写死句子，引用
  .nvmrc（24.18.0）+ packageManager（npm@11.16.0）——实际版本未变。
- **ADR 机制废弃**：docs/adr/（0001/0002/0003+README）全删，改为 docs/specs/ 的
  spec/plan/tasks/verification 四件套（现有 2356-wasm-interface-comparison、
  solidity/cbor-metadata 两组）。**ONBOARDING §8 引用的 adr/0001 已失效**。
- docs/ 新增 27 篇：adb-device-analysis/apktool-resource-analysis/client-configuration/
  client-verification/electron-fuses/flutter-analysis/frida-instrumentation/ghidra-provider/
  ghidra-mips|ppc|psp|riscv/go-binaries/harmony-analysis/http3-capture-lab/jeb-analysis/
  kuna-provider/migration-6.2/packet-captures/pcap-analysis/raw-binary/
  reconstruction-coverage/reverse-engineering-tools/rust-binaries/signal-recordings/
  sqlite-databases/wasm-artifacts。
- 仓根 19 语言 README 迁 docs/readme/；website/（Cloudflare 部署）+ docs/.vitepress
  （VitePress 文档站）双站并存，website/ +340K 行。
- **skill-src/ 已不存在** → 迁 .agents/skills/reverse-engineer-anything/（SKILL.md +
  references/ 5 篇：android-applications/evidence-workflows/javascript-applications/
  native-and-artifacts/runtime-observation）；skills/ 仍是 ignored 构建产物；
  scripts/verify-repository-skill.mjs 守卫。.agents/skills/ 还有 rea-tool-design/
  rea-changelog-update/rea-ci-tests-audit 等仓库自有 agent 技能。

## 8. DeepWiki 上游（已重抓 2026-10-16）

47/47 页 100%（10 章 + 37 子页，610,319 字符）。新增 4 页：4.6 调试器与动态插桩、
4.7 新 provider（kuna/jeb/wasm/evm/flutter/go/rust）、6.5 Web 网络捕获与脚本导出、
8.4 分析效率实验。旧快照归档 deepwiki-v6.1-archive/。

## 9. 文档更新最要紧口径（B 实测 + G4 勘误）

工具 138→207 · CLI 命令 94→153 · 客户端 14→25 · 副作用 8→10 维；
"19 group 单文件"表述作废（36 group 目录树）；PUBLISHED_TOOL_NAME_FLOOR 一节删除，
改述 CATALOG_IDENTITY 计数闸（tests/boundary/mcp/serverIdentity.test.ts:114-118）。

**⚠ 勘误（G4 改稿代理逐锚核实推翻下列初稿数字，主会话已独立复核）**：
1. 深度 provider 注册表锚：binary.ts **:32**（`[hopper, ghidra, ida, kuna]` 数组字面量；
   createBinarySession 在 :20-38）——初稿 "binary.ts:19-26" 作废。
2. PacketCapturePort/SignalRecordingPort **非独立 Port 文件**——分别定义在
   PacketCaptureService.ts:27 / SignalRecordingService.ts 内；独立 <Area>Port.ts 文件只覆盖部分域。
3. frida MCP 工具 **9 个**（list_frida_devices/list_frida_processes/start_frida_session/
   load_frida_script/resume_frida_session/unload_frida_script/frida_session_status/
   close_frida_session/instrument_with_frida）——"8 个"作废。
4. ci.yml **27 个 job**（YAML 解析实测：apple-artifacts/binary_layout/browser/build/changes/
   conformance-fixtures/docs/evm/ghidra_bridge/javascript_recovery/nativeaot/package-e2e/
   reconstruction-readiness/recorded_crash/required/reverse-tools-quality/sqlite-runtime/static/
   test/test-shard/test-source/web_network/web_runtime/web_source_map/website/windows-curated/
   windows-native-build）——"14→20"作废（ explorer C 漏计 path-gated job）。
5. package.json `verify:*` scripts **99 个**——"约 45"作废（C 只数了部分子集）。
6. gdb spawn "gdb" 在 GdbSessionManager.ts **:574**（REA_GDB_COMMAND 默认 :532）。
7. AnalysisProvider 接口 :174-186→**:229**、createAnalysisExecution :45-68→**:81**（旧文档漂移）。
8. conformance 目录"59→106"与 boundary"315→730"系不同计数口径（.test.ts vs 全部 .ts；
   boundary .test.ts 实数 716）；Jadx 粘性 `#cleanupFailure` 机制已被 v6.5 owner 化清理取代
   （JadxProvider.ts:352-363 `#pendingCleanup` + analysisErrorCleanup.ts）。

**⚠ 勘误二（G1 组 01/02/04 逐锚核实）**：
9. CreateServerOptions 可选字段实数 **34**（:149-184）——初稿 35 作废；optionalFeatures 12→**15** 项。
10. **src/config.ts barrel 已删除**——配置解析改 src/config/ 目录直 import（main.ts:10）。
11. **src/main/reload.ts 与 SIGHUP 热重载已删除**；sanitizeCliOutput 不存在——实为 resultOutput
    过滤+SIGPIPE 守卫（退出码 141，rea.mjs:18,119-129）；MCP 入口迁移 dist/main.js→dist/mcp/main.js（rea.mjs:59）。
12. **contractSnapshot.test.ts 已删除**（与 toolContracts.test.ts 同批断言合并）；toolResult.ts
    重构为 ToolResultDelivery 类（:47）。

**⚠ 勘误三（G3 组 06/07/08 逐锚核实）**：
13. bridge/nativeaot/ 实为 **4 个 Java 文件共 361 行**（Directory 70/Extension 183/
    MethodConventions 38/TypeMetadata 70）——初稿"5 文件 1177 行"作废（explorer D 把
    extensions 目录下的旧布局与 gradle 配置误并入）。
14. hopper_bridge.py 已从 bridge/hopper/ 迁至 **bridge/ 根**（1181 行）。
15. ReaGhidraBridge 能力精确口径：CAPABILITIES 31 项（:142），ping/shutdown 在 switch 前处理
    （:393/:419），其余 **28 路 case**（:430）。
16. PrivateRuntimeRoot POSIX 侧改为 **mkdtemp 原子 owner-only**（proof 串 posix-mkdtemp-owner-only，
    :27-36/:70-75）——"mkdtemp+chmod 0700+失败回滚"旧机制作废；DirectAnalysisTool 19→20 值
    （新增 search_bytes）；IdaMcpConnection 类改 createIdaMcpConnection 工厂（:339）。

**⚠ 勘误四（G2 组 03/05/11 逐锚核实）**：
17. analysisErrorCore.ts 实为 **193 行**（底稿"96→181 行"中的 181 系 analysisErrorBase.ts 行数，混淆）。
18. evidenceAuthoritySchema 五枚举在 evidence.ts **:108-114**（非 :109-115）。
19. compact schema 的 env 读取在 createServer.ts **:620-627**（compactPresentationForMcpInputSchemaProfile
    调用 :626）+ createMcpServer :256/:276 传参——":339 注入"不是注入点；mcpInputSchemaProfile.ts
    共 46 行（预算 :11/enum :13/parse :29）。
20. TOOL_EFFECTS 实数**恰 207 条**（与 TOOL_CONTRACTS 严格同集）；契约第 10 字段 returnsTargetContent
    + TARGET_CONTENT_FREE_TOOLS 白名单（底稿未提）；ANALYSIS_RESOURCE_KINDS 四种→五种；
    binaryTarget 大改（ExecutableMetadata 六分支/dos-mz/dos-com/FAT 迁 apple/machoContainer.ts/
    elfArchitecture 放行七种）；mcpDoctor/catalogIdentity 已上移 src/ 顶层；
    parseEvidence 篡改行为= zod issue 拒绝（非抛 TypeError）；EvidenceLedger 移 investigation/。
