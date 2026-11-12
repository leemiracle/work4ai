# src/domain/ 领域地基：result.ts 与 evidence.ts

## 角色定位

src/domain/ 是纯领域层（约 150 个文件，无 IO、无框架依赖），其中两个文件是"地基中的地基"。`result.ts` 仅 10 行，却是全仓被引用最多的模块——图谱 fan-in=259（fan-out=11），src 下 211 个文件 import 它：`Result<T,E>` 判别联合是所有边界（config 解析、provider 调用、会话 open）的错误通道。`evidence.ts` fan-in=234、fan-out=36，107 个 src 文件直接 import：它定义 REA 的立身之本——"每次成功观测都是一条可验证的 Evidence 记录"。二者合成一个工程信条：错误是值、结论是带哈希的不可变事实。

## 内部结构

**result.ts** 三导出打天下：联合类型 `{ok:true;value:T} | {ok:false;error:E}`（src/domain/result.ts:2-4）与构造器 `ok`（result.ts:7）、`err`（result.ts:10），全字段 `readonly` 防篡改。

**evidence.ts** 四段：

- **schema 族**：`providerSchema`（id/name/version，evidence.ts:26-30）；`subjectSchema` 带 24 值 format 枚举（evidence.ts:31-62）；`evidenceLocationSchema` 是 5 分支 discriminatedUnion——address/address-range/artifact-path/file-offset/file-offset-range（evidence.ts:65-79）；权威五级与 isolation 四档（evidence.ts:81-94）。
- **主 schema**：`evidenceBaseSchema` `.strict()` 十五字段，含 `evidence_id: prefixedDigestSchema("ev")`、confidence 三档（observed/derived/inferred）、limitations/locations/evidence_links（evidence.ts:96-113）；envelope 版追加可选 analysis_profile 并 `superRefine` 强制其 provider 与顶层 provider 三字段全等（evidence.ts:116-141）。
- **不可变层**：模块级 `WeakMap<object, Evidence>` 登记冻结快照（evidence.ts:154），`isImmutableEvidence` 靠成员查询 O(1) 判定（evidence.ts:260-261）。
- **工厂与校验**：`semanticProjection` 剔除 subject 的 name/local_path 等展示字段（evidence.ts:202-226）；`computeEvidenceId` 对投影做 canonical digest（evidence.ts:229-230）；`parseEvidence` 重算哈希比对 evidence_id，不符即抛（evidence.ts:233-253）；`createEvidence` 与生成器版 `createImmutableEvidenceSteps` 服务协同计算（evidence.ts:270-312）。

## 外部连接

result.ts 消费者横跨 config（parseConfig 返回 `Result`，src/config/parseConfig.ts:38）、组合根、hopper/ghidra/ida 适配器与全部 server 层。evidence.ts 三条主链：① server 层每个工具 handler 用 `createEvidence` 产记录入账（src/server/registerOfficialTools.ts:14）；② EvidenceMcpServer 在传输层截获超大结果也造 Evidence 保底（src/server/EvidenceMcpServer.ts:17）；③ 持久化侧 evidenceBundle 以 `evidenceRecordSchema` 为线格式。上游只依赖 jsonValue/canonicalDigest/digests 等同层模块（src/domain/evidence.ts:1-23）。

## 数据流

生产侧：provider 返回观测 → `normalizeEvidenceObservation` 组装 semantic 对象并补默认值——predicate_type 默认 "rea.analysis"（evidence.ts:346）、confidence 默认 "observed"、authority 默认 "shipped-artifact"（evidence.ts:351-352）、无目标时强制注入一条 subject 不可用 limitation（evidence.ts:354-362）→ 先按有无 profile 选分支 schema parse，避免 union 双遍克隆（evidence.ts:366-372）→ 以占位 `ev_000...0` 解析后仅替换 evidence_id，避免整载荷二次克隆（evidence.ts:380-388）。消费侧：外部输入走 `parseEvidence`，哈希复验把"语法合法但语义被篡改"的记录拒之门外（evidence.ts:248-251）。

## 设计决策

- **ID 即完整性校验**：evidence_id 是语义投影的 `ev_` 前缀 SHA-256（evidence.ts:229-230），字段改动即 ID 失配——防"持久化后悄悄改记录"的程序错误。投影刻意排除 name/local_path（evidence.ts:202-226），文件改名不改变证据身份。
- **双层 union 的性能注释**：两处注释（evidence.ts:239-245 与 366-372）解释为何先探测 analysis_profile 再选 schema——zod union 会为失败分支克隆整个 normalized_result，"先看信封再看载荷"是实测出的优化。
- **不可变性可验证**：不止冻结，还"记住哪些对象验证过"（WeakMap），信任链无需递归重验。
- **错误走 Result、数据走 schema**：domain 层从不 throw 业务错误。

## 新人提示

给 Evidence 加字段必须同时动四处：evidenceBaseSchema、`semanticProjection`（决定它是否参与身份哈希——展示性字段要排除，否则无害重命名会让历史 ID 全失效）、工厂默认值、evidenceBundle 导入导出测试。`parseEvidence` 的哈希校验意味着**测试 Evidence 必须经 createEvidence 生成**，硬编 ID 必挂。confidence/authority 是产品承诺：observed 只能用于工具真看到的，推断标 inferred。result.ts 别加 helper（连 map/flatMap 都没有是有意的——逼调用方显式分派 ok 分支）。
