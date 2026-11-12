<!-- source: knowledge-graph tour step | files: src/domain/result.ts, src/domain/jsonValue.ts, src/domain/analysisErrorCore.ts, src/domain/binaryTarget.ts -->

# EXPLAIN 5 · 领域模型地基：Result、有界 JSON、十类错误与无 I/O 头解析

### 1. 角色定位

domain 层仍是 REA 14 层分层中最大的一层（v6.5 达 608 个 .ts/22 个子目录，v6.1 为 409/8），本篇四文件是被依赖最深的"词汇表子层"：不执行分析，却定义上层全部 Provider、工作流与 MCP 出口的语言。`src/domain/result.ts` 是 10 行期望式错误通道，grep 实测 src+tools **363 文件** import（v6.1 为 211）；`src/domain/jsonValue.ts` 是跨边界 JSON 值契约（src 内 210 文件消费）；`src/domain/analysisErrorCore.ts` 是 provider 中立失败分类法；`src/domain/binaryTarget.ts` 无 I/O 解析可执行头。存在理由：TS 缺期望式失败通道，MCP 出口需要秘密安全且可投影的错误，"ELF arm64 还是托管 PE DLL"须在选 Provider 前有中立答案。

### 2. 内部结构

**result.ts：类型即产品。** `Result<T,E>` 是 readonly 判别联合（src/domain/result.ts:2），构造器 `ok`/`err` 用 `never` 反向参数化（:7）。无 map/chain 帮手——调用方 `if (r.ok)` 收窄，刻意最小。

**jsonValue.ts：有界校验+认证缓存。** `MAX_JSON_DEPTH=1000` 挡递归爆栈（src/domain/jsonValue.ts:6）；`jsonValueValidationSteps` generator 用显式 pending 栈迭代遍历、每 4096 节点 yield（:31,:49）。对象检查已重写为手工 descriptor 审计：数组须稠密无 accessor（:71-78），对象须普通原型（:80-82），`Reflect.ownKeys` 逐键拒 accessor（:83-91），**Proxy 直接拒绝**（:60-61）；只有 `freezeJsonSnapshot` 认证过的不可变根才进 WeakMap 校验缓存（:19,:34-43）。出口 `jsonValueSchema`（:128-133）pipe 后接 `preserveJsonValue` 递归重建、剥掉原型 setter（:97）；`_zod.toJSONSchema = () => ({})` 摘除递归段；新增对象边界 `jsonObjectSchema`（:143）。

**analysisErrorCore.ts：十个失败类+清理语义。** 核心错误类 10 个同名未变（96→193 行）。`ANALYSIS_RESOURCE_KINDS` 从四种资源扩为五种——新增 transport/capacity（src/domain/analysisErrorCore.ts:24-30）；`AnalysisInputIssue`（:70-84）仍是 Secret-safe 纠错元数据（path+六值 reason，guidance 由 schema 作者显式写）；`systemCode` 只收 `"EACCES"|"EPERM"`（:172）；多类新增 `remediationAction` 恢复指引（:11,:35）。基座 `AnalysisError`（analysisErrorBase.ts，181 行）27 个 tag **一字未改**（:4-32），但本体新增 `diagnostics`/`capturedOutput`/`cleanup`/`cleanupIncomplete`/`cleanupResources` 五字段（:65-69）——传 cleanup 即 cleanupIncomplete=true（:81-82）；`retainSecondaryFailure`（:93-108）把后续失败并进原错误不替换类型，`resolveCleanup`（:111-114）只在资源方确认重试成功后清标记；新文件 `analysisErrorCleanup.ts` 的 `analysisErrorWithCleanupFailure`（:6）合并双方资源清单并写双错误诊断（:29-41）。

**binaryTarget.ts：magic 分派纯函数。** `ExecutableMetadata`（src/domain/binaryTarget.ts:21-64）六分支判别联合：ELF mips/riscv/powerpc 三族各带 `ElfFamilyMetadata`（elfClass/byteOrder/type/flags，:22-39），通用 mach-o/elf/dos-mz/dos-com 分支，PE 分支新增原始 `peMachine`（:55）与 `codeView` PDB 记录（:63）。入口 `parseExecutableHeader`（:70-90）按 ELF→MZ→thin Mach-O→FAT 分派，否则 `err("unsupported binary format")`（:90）；签名增加 `fileSize`/`mzWindowsHeaderSignature` 参数支撑**有界二次补读**——FAT 表解析移入 `apple/machoContainer.ts`（MAX_FAT_ARCHITECTURES=128，machoContainer.ts:50；四态判定含 needs-data），不够读返回 needs-data 由属主补字节；无宿主兼容切片直接失败不猜（binaryTarget.ts:152）。MZ 分支先 `observeMzWindowsHeader`，NE/LE/LX 旧格式拒绝（:276），纯 DOS 镜像产出 dos-mz（:280-288）。`parsePeRecord`（:296）从 COFF characteristics 判 executableRole（0x0002 缺失=非可执行、0x2000=DLL，:327-331）；`peManagedStatus`（:503-530）交叉校验 optional-header magic 与架构，CLI 目录非零即 managed。`elfArchitecture` 放行七种（新增 mips/powerpc/riscv，:546-566）。

### 3. 外部连接

`result.ts` 是全仓最热的边：`src/hopper/protocol.ts`、`src/native/NativeMacOSProvider.ts` 等以其为返回词形；`jsonValue.ts` 是证据入关口，投影层把 `partialObservation` parse 成 JSON 才进 details（src/domain/analysisErrorProjection.ts:72-77）。错误体系三层：基座 27 个稳定 tag（src/domain/analysisErrorBase.ts:4-32）→ 投影 `STATIC_ERROR_CODES`（:193-217）映稳定 code（并集仍 20 个，新增 cleanup_incomplete/revision_conflict）→ `src/server/toolResult.ts` 的 `ToolResultDelivery` 消费成 MCP 错误负载（toolResult.ts:46,:100）。闭环：响应超预算时反向构造 `AnalysisResourceConstraintError`（toolResult.ts:181），错误类在出口被当资源治理工具复用。`binaryTarget.ts` 唯一生产消费者 `BinaryTargetResolver.ts`：读 4096 前缀（:302,:460），MZ 重定位表超界二次补读（:495），产出汇入 `BinaryTarget` 联合（binaryTargetTypes.ts:139）。

### 4. 数据流

成功支路：调用者给路径 → Resolver 读 4096 前缀（FAT/MZ 需要时按 needs-data 补读）→ `parseExecutableHeader` 产出 `ExecutableMetadata` → 与 path/sha256 组装成 `BinaryTarget` → 选 Provider。失败支路同走 domain 词汇：解析失败处 `err(new AnalysisInputError(operation, {cause}, [issue]))`（真实示例 src/native/NativeCallObservation.ts:56）→ `Result` 逐层上浮不解包 → 出口投影 tag 映射 `invalid_request`（src/domain/analysisErrorProjection.ts:197）。清理支路（新）：provider 清理失败被包成带资源清单的错误，投影为 cleanup_incomplete 而非静默成功。

### 5. 设计决策

**手写 10 行 Result 不引第三方**：全仓最深依赖必须零包。**generator 而非一次性循环**：4096 步一个让出点使深 JSON 校验可调度（同法 src/domain/immutableJson.ts:70）。**WeakMap 只认认证根**：模块私有 WeakSet 密封（src/domain/immutableJson.ts:3），jsonValue 缓存同样只收认证快照——Object.freeze 伪造不了身份。**头解析无 I/O 且有界**：纯函数+fileSize 参数让"不够读"成为显式 needs-data 而非异常（fixture 可 20 字节拼最小 ELF 头，src/domain/binaryTarget.fixture.ts:2）；FAT 无宿主切片时失败优于猜测。**错误投影穷尽**：`as const satisfies` 强制每个非特化 tag 有 code（src/domain/analysisErrorProjection.ts:216-217）。**超预算转错误而非截断**：源码明言分析结果未被截断（src/server/toolResult.ts:186）——伪装成功会污染 Evidence 语义。**清理失败保留所有权**（新）：AGENTS.md owner 原则落地——清理失败的资源保持 owned，`AnalysisCapabilityUnavailableError.retryable` 在 cleanupIncomplete 时强制 false（src/domain/analysisErrorCore.ts:134）。

### 6. 新人提示

上手顺序：result.ts → jsonValue.ts 连读 immutableJson.ts → analysisErrorCore.ts 配 analysisErrorBase.ts 与 analysisErrorCleanup.ts → binaryTarget.ts 配 dosMz.ts（e_lfanew 判定 src/domain/dosMz.ts:27-32：短 DOS 头 0x3c 处可能是重定位数据，须签名确认）。测试入口 `npx vitest run src/domain/binaryTarget.test.ts`，值得读的边界用例：DOS 镜像不误读 e_lfanew（src/domain/binaryTarget.test.ts:7）、PE application/DLL/managed/非可执行四分（:36）、FAT 按宿主选切片且无兼容即拒（:95,:124）。易错点：①新增错误类三处同步——类内 `_tag`、基座 tag 数组、投影 STATIC_ERROR_CODES；②`AnalysisInputIssue.message` 别塞调用方原文；③`jsonValueSchema` transform 会深克隆，大 payload 先 `freezeJsonSnapshot` 认证才吃缓存；④PE characteristics 判序先 0x0002 再 0x2000，反了会把非可执行标成 application；⑤带 cleanup 的错误别在清理确认前吞掉。
