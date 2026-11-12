# 04 · openshell-prover：Z3 驱动的 containment 证明器与渗出能力注册表

## 一、角色定位

`openshell-prover` 把"这条策略会不会放走数据"变成可判定的形式问题。crate 文档（crates/openshell-prover/src/lib.rs:4-8）一句话讲清方法论：**把沙箱策略、二进制能力、凭据作用域编码为 Z3 SMT 约束，然后跑可达性查询检测数据渗出路径与写绕过**。它有两条腿：`queries.rs` 的四类风险发现（服务网关的审批增量门），和 `containment.rs` 的边界包含检查（候选策略必须落在边界策略之内）。`prove()`（crates/openshell-prover/src/lib.rs:38-76）串起全流程：parse_policy → 加载凭据集与二进制注册表 → build_model → run_all_queries → 可选 accepted-risks 抵扣 → 渲染报告；退出码约定 ：32-34——`Ok(0)` 无发现（或全部被接受）、`Ok(1)` 存在未接受发现。

## 二、内部结构

**四类发现是封闭集**（queries.rs:11-34 文档 + crates/openshell-prover/src/finding.rs:29-32 常量）：①`link_local_reach`——任何可达 `169.254.0.0/16` 或 `fe80::/10` 的路径，**无条件发射**（云元数据端点即凭据，可达即风险）；②`l7_bypass_credentialed`——L7 代理无法检查其线上协议的二进制（git-remote-https/ssh/nc）获得对"凭据在作用域内主机"的可达；③`credential_reach_expansion`——二进制新获得此前不可达的 (host,port) 凭据化访问；④`capability_expansion`——在已有凭据化访问的 (binary,host,port) 上新增 HTTP 方法。输出**只有类别没有严重度**（crates/openshell-prover/src/lib.rs:213 注释"categorical, not severity-graded"）；"新不新"由网关的 finding_delta 决定，自动批准门=无新发现。入口 `run_all_queries`（queries.rs:271），`check_credential_safety`（:76）承载主体逻辑。`model.rs` 的 `build_model`（:386）铸造 Z3 模型，`can_write_to_endpoint`（:285）/`can_exfil_via_endpoint`（:329）是两类核心谓词。

**渗出能力注册表**（registry.rs）：`EMBEDDED_REGISTRY`（registry.rs:16）用 `include_dir!` 在编译期嵌入 `registry/` 目录，九个二进制档案：claude/curl/gh/git/nc/node/python3/ssh/wget。`BinaryCapability`（:113-122）六字段，安全语义最重的三个：`can_exfiltrate`（:119）、`exfil_mechanism`、`can_construct_http`。`get_or_unknown`（:168-189）体现**保守默认**：精确匹配→glob 匹配→都失败就返回"未知描述符"，其中 `can_exfiltrate: true, can_construct_http: true`（:185-187）——**没见过的二进制按最危险处理**。`bypasses_l7()`（:126-128）聚合协议级标记。

**claude CLI 被建模为渗出源**是注册表最生动的样本（registry/binaries/claude.yaml）：`binary: /usr/local/bin/claude`（:4）；协议表两条（:6-20），其中 `http-via-tools`（:13-16）描述直白——"Claude can make HTTP requests via tool use (Bash, WebFetch)"，带 get/post/put 三个 action（post/put 标 type: write）；`spawns` 列表（:21-27）把 node/python3.13/git/curl/ssh/nc 全列为子进程——即模型承认 agent CLI 可以借壳任何危险工具；`can_exfiltrate: true`（:28）+ 机制说明（:29）"可通过工具调用、API 请求或派生子进程读取文件并发送内容"。注意其两条协议 `bypasses_l7: false`（:10/:16）——Claude 的流量本身可被 L7 检查，真正的风险敞口是 spawn 链；对比 git/ssh/nc 档案里的 `bypasses_l7: true` 才触发第②类发现。testdata/policy.yaml:46 的 `- { path: /usr/local/bin/claude }` 让回归测试复现该场景。

**containment.rs（3486 行）——"健全而刻意收窄"的包含检查**：文档（containment.rs:4-13）三个关键词：sound（不漏报）、deliberately narrow（只覆盖能证明的子集）、**fails closed**（超出支持模型即 Unsupported，绝不猜）。入口 `check_within_boundary(boundary, candidate, options)`（:377-382）回答"候选策略的每个建模动作是否都被边界策略允许"。`CheckResult` 四态封闭契约（:342-347）：Within/Exceeds（带反例 `ExceedsEvidence`）/Unsupported（带 ReasonCode）/Inconclusive——注释要求**授权方只接受 Within**（:13）。`check_within_boundary_inner`（:397-459）的次序本身就是安全审计：先预检+校验支持域（含 workdir 符号 `<OCI_WORKDIR>` 未解析即 Unsupported :410-412），先跑 `execution::check`（:413，exec 权限差集，Exceeds 即短路），边界==候选直接 Within（:417-419），再 `check_filesystem`（:420，:1393 定义），最后**双遍求解网络**（:425-443）：`binary_identity_required=false/true` 各跑一遍 Z3，第二遍前若候选二进制路径存在符号链接歧义则 Unsupported（ReasonCode::UnresolvedBinaryPath）——宁可不给证明也不给假证明。有界性硬上限常量群（:36-45）：MAX_RULES=1024、MAX_ENDPOINTS=4096、MAX_PORT_ENTRIES=65536、MAX_PATTERN_BYTES=4KB、MAX_TOTAL_PATTERN_BYTES=1MB——防策略本身成为 DoS 载荷。`SymbolicAction`（:357-367）是全息符号动作：binary/ancestor_binary/host/port/layer/method/path/ip/trusted_gateway 九维，配合 `ip.rs`（IP 范围推理）与 `execution.rs`（exec 检查）两个子模块。

**凭据与豁免**：credentials.rs 定义凭据档案（name/type/scopes），`load_credential_set_embedded` 与注册表同源；accepted_risks.rs 的 `AcceptedRisk`（:43）+ `apply_accepted_risks`（:98）实现"已知风险登记抵扣"——被接受的发现从报告中剔除，让增量门只看新面。

## 三、外部连接

上游：z3 crate（求解器）、openshell-policy-schema（canonical 授权表示）。下游：`openshell-server/src/grpc/policy.rs` 消费四类发现做 finding_delta 与自动批准（queries.rs:33-34 点名）；`openshell-prover-cli` 提供命令行入口；testdata 提供 policy/credentials 回归夹具。注册表可被 `registry_dir` 文件系统覆盖（crates/openshell-prover/src/lib.rs:47-59），嵌入版是默认真源。

## 四、数据流

策略 YAML + 凭据 YAML + 二进制注册表 → Z3 约束模型 → 四类可达性查询 → findings（含路径反例）→ accepted-risks 抵扣 → 报告/退出码；网关侧：老策略 findings 做 baseline → 新策略 findings 求差集 → 零新发现放行自动批准，否则转人工 chunk 审批。

## 五、设计决策

1. **类别化而非分级化**：四类封闭集合+无严重度，把"多严重"的判断还给网关 delta 与人——证明器只管"是不是新渗出面"。
2. **未知即高危**：注册表 miss 落到 can_exfiltrate=true 的保守描述符，白名单文化的反面是黑名单默认。
3. **fail closed 的形式化**：Unsupported/Inconclusive 是一等结果，授权只认 Within——证明器的能力边界成为系统安全边界的一部分。
4. **agent CLI 一等公民建模**：claude 档案承认"工具调用+spawn"是独立渗出机制，比把它当普通 https 客户端诚实得多。

## 六、新人提示

- 勘误：说"claude 的协议 bypasses_l7"是错的——它两条协议都是 false；触发第②类发现的是 git/ssh/nc，claude 的风险经由 spawns 链与 can_exfiltrate 传导。
- 四类发现互斥性靠网关抑制（capability_expansion 若同时出现在 credential_reach_expansion delta 则被压掉，queries.rs:31-34），prover 本身可能双发。
- containment 与 queries 是两套独立模型（containment.rs:5-6 明言独立于 legacy proposal-risk model），别混用名词。
- `get_or_unknown` 的 glob 档案（registry 里 `*` 模式）先于 unknown 兜底生效，自定义注册表时注意顺序语义。
- 退出码 1 是"有未接受发现"，不是程序错误；CI 里别把它当 crash 处理。
