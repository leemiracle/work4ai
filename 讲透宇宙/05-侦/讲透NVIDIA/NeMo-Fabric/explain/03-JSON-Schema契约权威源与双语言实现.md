# 03 · JSON Schema 契约权威源与双语言实现

> 仓库：NVIDIA/NeMo-Fabric @ 86f86882 · schemas/ + adapter-contract/{python,typescript}

## 一、角色定位

NeMo Fabric 的核心架构命题是"**一份契约，三种语言投影**"。schemas/ 是契约权威快照：adapter-contract/ 11 个（南向适配器面）+ sdk/ 16 个（北向消费者面）= 27 个 JSON Schema，与 fabric-core schema.rs:86 的 `SchemaName::ALL: [Self; 27]` 一一对应。图谱的 27 条 defines_schema 边正是"生成器→快照文件"。

纪律写在 schemas/SCHEMA.md:8-10：**文件由 Rust core 类型生成，非手编**。生成入口 schema.rs:266 `write_schema_snapshots`——改 Rust 类型→重新生成→三语言投影（TS 类型/Python dataclass/rustdoc）必须同一提交内更新（SCHEMA.md:13-15："update each applicable language binding and its parity tests in the same change"）。

两个语言实现刻意不同：**TypeScript 机器生成**（generated/*.ts 文件头钉版 "Do not edit it directly; run `npm run generate` instead"），**Python 手写维护**（33 个 dataclass 对照 Rust schema 人工对齐，SCHEMA.md:11-12）——全仓最值得琢磨的非对称设计。

## 二、内部结构（带行号）

### 权威源

- schemas/adapter-contract/ 11 个：adapter-descriptor、adapter-target-descriptor、agent-config、agent-run-request/result、adapter-check-request/result、openai-stream-invocation/record、runtime-context、adapter-invocation（SCHEMA.md:31-42 目录树）。sdk/ 16 个：agent、run-plan、run-result、fabric-event、environment-handle 等。
- SCHEMA.md:46-48 钉语义链："FabricConfig 是消费者意图的北向源；规划产出 CapabilityPlan 作为路由证据；把所选 descriptor 接受的字段投影进 AgentConfig——南向适配器输入的权威形态"。
- 生成器四函数：schema.rs:220 generate_schema、:253 generate_all_schemas（BTreeMap 稳定序）、:261 generate_schema_json、:266 write_schema_snapshots 按 relative_path 分目录落盘。

### TypeScript 侧

- scripts/generate.mjs:21 引 json-schema-to-typescript 的 compile；:24 锁源目录 `schemas/adapter-contract`；:26 `--check` 模式供 CI 字节级比对（:112-131 Buffer.equals，stale 即报"Run `npm run generate` and commit the result"）。
- schemaSpecs（:34-60）定义 8 个投影：adapter-descriptor/adapter-target-descriptor 带自定义 project、agent-run-result 带自定义 generate、其余直译。
- :65-70 transportSchemaNames 白名单显式排除三个传输 schema——"它们是规范南向契约但不属于零依赖 TS 模型包"，排除显式化而非静默跳过。
- 双保险：projection-guards.mjs:6-32 `assertRunResultConditionals` 用 isDeepStrictEqual 钉死 AgentRunResult 的 if/then 条件（failed→error 必填、succeeded→error 为 null）；`assertAdapterSchemaInventory`（:42-53）钉死 schema 清单——新增文件必须显式进投影清单。
- 产物：src/generated/ 8 个 .ts（agent-config.ts 367 行最大）+ src/json.ts（19 行 JsonValue 递归类型）+ src/version.ts（8 行，从 schema 的 contract_version.const 提取，generate.mjs:85-91 requireString 校验）。index.ts:14-19 re-export 全部 generated；:22-42 用索引类型从生成物派生 AdapterKind/InstructionMode/AgentRunStatus 等别名——手写层只做导出整形不复制形状。
- test/stable.test.ts（248 行）用 @ts-expect-error 做编译期契约测试：:46-52 验证已删除的 health level "operational" 不被接受、AdapterCheckResult 保留 required null 字段；:55-60 四条不变式——passing 结果 reason_code 必须 null、observed_at 不许 null、非 passing 必须带 reason。

### Python 侧（零依赖，pyproject.toml:27 dependencies=[]）

- models.py 706 行 33 类：ContractModel 基类（models.py:73）是根——__pydantic_config__ ClassVar（:78-81，extra="forbid"+allow_inf_nan=False，**只在可选 TypeAdapter 用时生效，基包不 import pydantic**，注释 :77-78 钉版）；__post_init__ 先 validate_dataclass 再 _validate（:83-85）；__setattr__ 拦截每次赋值（:86-103）——decode、验证失败回滚旧值再 raise，**构造后改字段也绕不过校验**。from_mapping/to_mapping（:112-122）是线格式出入口。
- 类型体系：AgentContractBlock（:198）是 AgentConfig 树 17 个配置块公共基（带 extensions）；AgentRunRequest（:518）/AgentRunError（:535）/AgentArtifact（:566，_validate_artifact_path :547）/AgentUsage（:583）/AgentRunResult（:605）；StrEnum 家族 AgentRunStatus（:526）/ControlLocation（:621）；MCP 认证双形态 McpOAuth2Config（:319）/McpServiceAccountConfig（:382）。
- codec.py 311 行手写往返：decode_dataclass（:88）按 type hints 解码；_decode_value（:173）约 120 行递归处理 Optional/Literal/Union/枚举/列表/映射；错误带字段路径（ContractValidationError :34 继承 ValueError）；encode_dataclass（:157）反向。
- pydantic_support.py 42 行可选桥：type_adapter（:11）/extension_schema（:17）/set_pydantic_extensions（:25）——方向永远 Pydantic→dataclass，不反向。

## 三、外部连接

- **上游**：fabric-core 27 个公开类型（schema.rs SchemaName）——一切 schema 的源头。
- **下游**：TS 9 适配器 import `nemo-fabric-adapter-contract`（adapters/typescript/common/package.json 依赖）；Python 10 适配器 import `nemo_fabric_adapter_contract`；TS 适配器包捆绑规范 schema 供 ajv 运行时校验（SCHEMA.md:61-64）。
- **版本锚**：adapter-descriptor 的 contract_version.const 经 generate.mjs:85-91 进 version.ts，与 fabric-core adapter_contract.rs:10 的 `"fabric.adapter/v1alpha2"` 同值；stable.test.ts:27 用它构造合法 descriptor。
- Python SDK 的 types.py/models.py 是 sdk/ 组 schema 的消费投影（北向），与 adapter-contract（南向）分属两组。

## 四、数据流

**发布流**：Rust 类型变更 → write_schema_snapshots 刷新 schemas/ → CI 跑 generate.mjs --check 字节比对 → stable.test.ts+projection-guards 验不变式 → Python 人工改 models.py 对齐 → parity 测试同行提交。

**运行时流（TS）**：descriptor JSON → generated 类型约束 → ajv 用包内规范 schema 验证实例 → 契约对象进出适配器。

**运行时流（Python）**：宿主 stdin JSON → ContractModel.from_mapping → decode_dataclass 逐字段解码（错误带路径）→ 适配器操作类型化对象 → to_mapping → stdout 回宿主。Pydantic 用户在边界外用 type_adapter 预验证，进契约世界后一律 dataclass。

## 五、设计决策

1. **TS 生成、Python 手写的非对称**：TS 的 json-schema-to-typescript 生态成熟可字节级校验；Python 想要 slots+kw_only+深度校验语义，生成器达不到故手写+测试对齐。代价是 Python 侧同步负担高——SCHEMA.md 把它写成流程纪律。
2. **零依赖是硬约束**：Pydantic 通过 ClassVar 配置+可选桥实现"兼容而不依赖"——适配器作者不必为 dataclass 包拖进 pydantic 全家桶。
3. **不变式测试优于快照**：stable.test.ts 断言"错误用法必须编译失败"，projection-guards 钉条件结构——测语义不测形状，重构容错高。
4. **清单守卫防静默漂移**：assertAdapterSchemaInventory 让"新增 schema 忘了投影"从静默缺失变显式报错。
5. **显式排除优于隐式过滤**：transportSchemaNames 白名单+注释，边界一目了然。

## 六、新人提示

- 改契约的正确顺序：先改 fabric-core Rust 类型→生成快照→`npm run generate`→手动对齐 Python models.py→一个提交。颠倒必出 parity 告警。
- 看不懂 AgentRunResult 的 required null 字段，读 stable.test.ts:55-60 四条 @ts-expect-error——契约语义的最佳文档。
- Python 解码错误看 ContractValidationError 的 path（codec.py:34 起），直接对应 JSON 嵌套位置。
- 南北向之分：AgentConfig 是南向投影、FabricConfig 只在北向——对照 SCHEMA.md:46-48 + agent_config.rs 的 project_agent_config。
- 27 个 schema 与 SchemaName::ALL（schema.rs:86-113）顺序一致，文件名由 schema.rs:149 filename() 决定。
