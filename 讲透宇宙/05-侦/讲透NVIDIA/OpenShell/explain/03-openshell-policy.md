# 03 · openshell-policy：策略语言的解析、校验与原子合并

## 一、角色定位

`openshell-policy` 是授权语言的中枢：crates 文档（crates/openshell-policy/src/lib.rs:4-9）自述"提供策略 YAML↔protobuf 双向转换"，并明确分工——**规范表示与有界解析器住在 `openshell-policy-schema`，本 crate 负责把它适配到运行时 protobuf 模型，并拥有"运行时相关"的校验**。gateway 在 CreateSandbox/ApproveDraftChunk 时用它做安全校验；沙箱侧经它拿默认策略；监督器把 OPA 数据喂进来之前也靠它统一口径。四个子模块各司其职：`compose`（provider 层合成）、`l7_validate`（端点语义）、`merge`（审批合并，6931 行巨物）、`ambiguity`（端点选择器冲突），加 `middleware`（网络中间件 JSON 校验，crates/openshell-policy/src/lib.rs:12-22）。

## 二、内部结构

**双向转换**：`parse_sandbox_policy`（crates/openshell-policy/src/lib.rs:856）从 YAML 字符串到 proto 类型，`serialize_sandbox_policy`（:875）反向，`sandbox_policy_to_json_value`（:888）产出 OPA 可直接消费的 JSON（这是 rego 引擎的数据源），`load_sandbox_policy`（:940）处理 CLI 路径覆盖。别名层（crates/openshell-policy/src/lib.rs:60-71）把 schema crate 的 `PolicyDocument as PolicyFile` 等改名保持可读。

**保底策略**：`restrictive_default_policy`（crates/openshell-policy/src/lib.rs:971-996）是无策略沙箱的兜底——文件系统只读 `/bin /usr /lib /proc /dev/urandom /etc /var/log`、可写仅 `/tmp /dev/null`、landlock best_effort、**`network_policies: HashMap::new()`（:991）即封死全部网络（文档注释 crates/openshell-policy/src/lib.rs:969"blocks all network access"）**。`ensure_sandbox_process_identity`（:1001）补默认 `sandbox` 用户/组——但注释（:998-1000）点明 Docker/Podman 保留"省略"以回落 OCI `Config.User`，其他驱动在校验前填充。

**安全校验**：`validate_sandbox_policy`（crates/openshell-policy/src/lib.rs:1345）总入口；核心在 `validate_filesystem_paths`（:1357-1397+），四条铁律对应 `PolicyViolation`（:1023）的变体：路径必须绝对（:1376-1380 RelativePath）、不得含 `..` 父遍历（:1381-1388 PathTraversal）、read_write 不得指向文件系统根——连续斜杠 trim 后为空即违规（:1391-1397 OverlyBroadPath）、总量受限（`MAX_FILESYSTEM_PATHS = 256`，:1016；单条 `MAX_PATH_LENGTH = 4096`，:1019）。注释（:1351-1356）还要求把违规里的路径值在可信工具外展示时脱敏。`validate_and_canonicalize_sandbox_policy`（:1873）是"校验+规范化"复合出口，gateway 与 merge 都走它。

**merge.rs（6931 行，真正的千行巨物）**：审批链的执行者。入口 `merge_policy`（merge.rs:1000-1030）三段式：先 `validate_and_canonicalize` 输入策略；循环应用 `PolicyMergeOp`（:222-247，六种操作：AddRule/RemoveEndpoint/RemoveRule/AddDenyRules/AddAllowRules/RemoveBinary）；末尾再次校验合并结果。**原子性靠"merged 私有"实现**——注释（merge.rs:1012-1015）："merged 在所有操作成功前保持私有，失败即原子回退，且不允许后面的坏操作替换前面操作的错误"。三类反馈类型：`PolicyMergeError`（:381，含 InvalidInputPolicy/InvalidMergedPolicy 等）、`PolicyMergeWarning`（:250，如 ExistingProtocolRetained）、`PolicyMergeResult`（:690，policy+warnings+changed）。`canonicalize_advisor_add_rule`（:30-145）是防"建议降质"的关键：拒绝事件只报 (host,port,binary)，若目标已有唯一端点契约，就改写建议为**保留既有契约**而非新开一个通用 L4 端点（:21-28 注释解释：新开泛 L4 会丢检查元数据并制造歧义）；观察到的**新**二进制单独放一条 advisor 标记的规则，使它无法继承 exact-host 私有地址信任。provider 规则名以 `_provider_` 前缀隔离（compose.rs:8），`is_provider_rule_name` 判定、`strip_provider_rule_names`（compose.rs:45）剥离、`compose_effective_policy`（compose.rs:59）把 provider 层叠进有效策略。文件里 `#[cfg(test)]` 从 2401 行起——**4531 行（65%）是测试**，这是它 6931 行的真正构成。

**歧义检测**：`ambiguity.rs` 的 `EndpointAmbiguity`（ambiguity.rs:16-30）成对报告"能授权同一请求但策略派生行为不一致"的端点（端口重叠 + 元数据冲突），供网关在审批前拦下会打架的规则。`l7_validate.rs` 补端点语义：`validate_l7_endpoint_semantics`（l7_validate.rs:243）校验 tls/enforcement/access 组合，`agent_authored_transport_rejection`（:138）拒绝 agent 自署名的传输层配置。

## 三、外部连接

上游依赖 `openshell-policy-schema`（授权表示与有界解析）、`openshell-core`（proto 类型、mcp 版本工具、CONTAINER_POLICY_PATH）。下游：gateway/server（CreateSandbox 校验、ApproveDraftChunk 走 merge_policy）、sandbox supervisor（CONTAINER_POLICY_PATH 探测默认策略，crates/openshell-policy/src/lib.rs:962 还保留 navigator 时代的旧路径 `/etc/navigator/policy.yaml` 兼容）、supervisor-network 的 OPA 引擎（消费 to_json_value 的输出）。

## 四、数据流

YAML/schema → parse → ProtoSandboxPolicy → validate（安全违规清单）→ 存储分发；拒绝事件 → SubmitPolicyAnalysis 生成建议 chunk → 管理员批准 → merge_policy(base, ops)（六种操作、原子应用、无新检查冲突断言 merge.rs:1021 `ensure_no_new_inspection_conflicts`）→ 新 policy version → sandbox_policy_to_json_value → OPA 数据。

## 五、设计决策

1. **schema 与校验分家**：可解析性（有界、拒未知字段）归 policy-schema；运行时语义（路径安全、landlock 值、进程身份）归本 crate——授权语言的两半各有把关人。
2. **合并原子性不靠事务靠作用域**：中间态变量私有 + 首尾双校验，失败零残留。
3. **建议不降质**：advisor 规则改写保留既有检查契约，新二进制隔离成独立规则防信任继承。
4. **默认策略封网**：无策略 ≠ 宽松，restrictive_default 的空 network_policies 是安全底线。

## 六、新人提示

- "千行巨物"merge.rs 三分之二是测试（2401 行起）；读逻辑只看前 2400 行，别被行号吓退。
- `validate_filesystem_paths` 同时服务"类型化策略"与"原始 OPA data"两条入口（:1351 注释）——改它要跑两边测试。
- read_write 根路径判定用 `trim_end_matches('/')` 后判空（:1393），`///` 也算根；别只拦 `/`。
- LEGACY_CONTAINER_POLICY_PATH（crates/openshell-policy/src/lib.rs:961）暴露了前世：项目由 navigator 改名 openshell，旧镜像的策略路径仍在兼容。
- PolicyMergeWarning 不是错误：审批 UI 必须展示（如"保留既有协议"），静默吞掉会让管理员误判合并结果。
