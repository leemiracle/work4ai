# OpenShell 新人导读（ONBOARDING）

> 基于仓库知识图谱（commit `76cfd0e31d5e1633db7ccd86ad9023ef7a2461b2`，2026-10-01）与源码逐项核实生成。
> 图谱规模：7661 节点 / 17189 边 / 16 层 / 16 步导览，分析文件 1195 个。
> 所有路径与行号均经源码验证；「设计文档 vs 现实」差距清单见文末。

## 1. 一句话定位

OpenShell 是 NVIDIA 开源的**自主 AI agent 安全外壳与监督器**：给跑着 LLM agent 的舰队提供"安全且私有的运行时"。它不是又一个沙箱工具，而是四件事的合体——

1. **沙箱生命周期管理**：从 create/start/stop/delete 到 exec/端口转发/SSH 会话，五种计算后端（microVM、Kubernetes、Podman、Docker、Windows MXC）一种接缝；
2. **策略证明**：agent 改策略不是直接生效，而是先过 Z3 形式化包含性（containment）检查——"新策略是否仍被边界策略包住"；
3. **L7 出站监督默认拒绝**：沙箱内 agent 的每一条出站连接都要过内嵌 OPA 策略评估与 HTTP/MCP/GraphQL/WebSocket/JSON-RPC 逐协议检查，没有显式 allow 就是 deny；
4. **OCSF 遥测与凭据供应**：一切监督行为落为 OCSF 1.8.0 标准安全事件；真实凭据（NVIDIA/OpenAI/AWS/Vertex 等 18 家 provider）只活在网关侧，沙箱拿到的永远是按 token grant 注入的短命材料。

工程形态是单仓多语言：Rust workspace 38 个 crate（edition 2024）+ Python/TypeScript/Go 三语言官方 SDK，外加 proto/ 契约层与 buf 工具链。README 的自我定位很直白："built agent-first"（AGENTS.md）——这个仓库本身就是用 coding agent 协作开发的，`.agents/skills/` 下 18 组工作流技能与 `.claude/.opencode` 的审查代理是一等公民。

## 2. 仓库全貌

全仓磁盘文件约 2100 个（不含 .git），图谱分析范围 1195 个（裁掉测试快照与生成产物类）。目录按依赖方向自上而下：

```
proto/                  跨语言契约源头（12 个 .proto；openshell.proto 一个文件 82 个 rpc）
├─ openshell.proto      网关主服务：沙箱全生命周期/模板/provider/凭据/policy/watch
├─ datamodel.proto      WorkspaceSelector/ObjectMeta/Workspace 等共享模型
├─ sandbox.proto        SandboxPolicy/NetworkEndpoint(25+ 字段)/L7 规则
├─ compute_driver.proto credential_driver.proto   驱动扩展契约
└─ options.proto        AuthorizationRule：按方法声明鉴权要求的自定义 option

crates/                 38 个 Rust crate（AGENTS.md 有权威架构总表）
├─ 共享底座：openshell-core(46 子模块) bootstrap binary-identity extension-core
├─ 策略线：openshell-policy policy-schema providers(18 家 provider 档案解析)
├─ 隔离线：isolation-interface sandbox sandbox-backend（RFC 0012 三层）
├─ 驱动群：driver-{vm,docker,podman,kubernetes,mxc} vfio + 凭据 driver-{vault,db-credstore,kubernetes-secrets}
├─ 数据平面：supervisor supervisor-network supervisor-process supervisor-middleware{,-builtins}
├─ 控制平面：server server-macros gateway gateway-interceptors
├─ 证明与一致性：prover prover-cli conformance conformance-cli
├─ 遥测：ocsf otel otel-test-support
└─ 人机入口：cli tui sdk（sdk 经 napi-rs 发布为 @openshell/sdk）

sdk/go/                 最完整语言 SDK（215 个 .go：types/converter/fake 全内存替身）
sdk/typescript/         @nvidia/openshell-sdk（protoc-gen-es 生成 stub）
python/openshell/       Python SDK（sandbox.py 2443 行 23 类）
providers/              18 份 LLM 提供商网关 YAML 档案（nvidia/openai/anthropic/aws...）
rfc/                    架构决策记录 0001-0014（0007/0008 编号空缺）
docs/                   fern 文档站 59 个 .mdx；telemetry/ 遥测设计评审纪要
tasks/ + scripts/       mise 任务编排（tasks/*.toml 按域拆分）与发布/CI 脚本
e2e/                    python/rust/docker/gpu/kubernetes/mcp-conformance 六线 E2E
deploy/                 docker/helm/kube/deb/rpm/sbom/man 全形态部署
.agents/skills/ + skills/ + .claude/ + .opencode/   agent 协作层
```

图谱 16 层把这套结构切成清晰的依赖梯度（L01 仓根治理 → L02 proto 契约 → L03 核心库 → L04 策略 → L05 隔离 → L06 驱动群 → L07 遥测 → L08 控制平面 → L09 网关监督器 → L10 证明器 → L11 CLI/TUI → L12-13 四语言 SDK → L14 任务脚本 → L15 RFC → L16 agent 协作层）。读依赖方向永远是"上层引用下层"：proto 是一切的源头，openshell-core 是被引用最多的 crate（lib.rs fanIn=138，全仓第一 hub），SDK 层 Go 的 types 包一族 fanIn≈97-99 是第二集团——语言绑定把契约面复制到了每个生态。

三个容易低估的目录：`providers/*.yaml` 不是配置示例而是 providers crate 的"声明式 profile 数据模型"的实例（profiles.rs 7995 行 + 939 行校验器消费它们）；`rfc/` 不是历史档案馆，0005/0012/0014 三个 RFC 仍处于 review 状态、直接描述在途工程；`.agents/skills/` 的 sync-agent-infra 技能维护着一张"工作流变更→须检查哪些文档"的地图，改协作流程前必读。

## 3. 核心架构：安全模型如何分层落地

OpenShell 的安全模型可以概括为一条"策略流水线 + 两个执行平面"。

**策略流水线（YAML → 证明 → 执行）**：

1. **编写**：开发者/agent 写声明式策略 YAML。`openshell-policy-schema` 用 ParseLimits 资源上限做**有界解析**，未知字段直接拒绝（防 YAML 炸弹与拼写漂移），并做词法路径归一化；
2. **校验**：`openshell-policy` 做 YAML↔protobuf 双向转换与安全校验——路径穿越、过宽路径、TLD 通配（如允许 `*.com`）、身份合法性；`merge.rs`（6931 行）实现 PolicyMergeOp 原子变更序列，agent 的增量策略修订（增删规则/端点/二进制）在这里合并成有效策略；
3. **存储**：openshell-server 的 persistence 层以版本化 protobuf 存策略修订与 draft chunk（storage_proto.rs），SQLite/Postgres 双后端 enum dispatch；
4. **证明**：`openshell-prover` 把"候选策略相对边界策略的包含性"交给 Z3 符号求解（containment.rs 3486 行），四态结果 Within/Exceeds/Unsupported/Inconclusive——**超出支持模型即 fail-closed**，宁可拒判不放行；已接受风险用 accepted_risks 显式折叠；
5. **执行**：策略随沙箱创建下发，沙箱内监督器持续经 gRPC 轮询热重载（supervisor/src/lib.rs 的 policy poll loop）。

**两个执行平面**：

- **控制平面**（openshell-server + gateway 二进制）：82 个 rpc 的 gRPC API、OIDC/sandbox JWT/mTLS 三路认证、`#[rpc_authz]` 宏生成的方法级授权常量表、CAS 乐观并发存储、watch 游标。gateway main.rs 只有 10 行——它做的事是"把五种计算驱动注册进 server CLI 再启动"；
- **数据平面**（sandbox + supervisor 系，全部跑在沙箱内）：`openshell-sandbox` 是无特权（capability-free）工作负载边界，启动即做运行时资格鉴定（seccomp notify 回路、Landlock ABI、DNS 中继绑定、socket 虚拟化探针），不合格直接 fail-fast；`openshell-supervisor-network` 是出站守门人——HTTP CONNECT 代理主体 proxy.rs（14996 行，该 crate 最大文件；全仓之最其实是 server 的 grpc/policy.rs，23492 行）先问内嵌 OPA（regorus 封装）策略可否放行，再决定是否进 L7 协议检查与凭据注入。

**沙箱五驱动一种接缝**：vm/docker/podman/kubernetes（Linux，gateway/src/lib.rs 的 install_in_tree_compute_drivers 按优先级注册）+ mxc（Windows-only，u16::MAX 优先级注册；同时给另外四个驱动名装 UnsupportedWindowsFactory stub，让 Windows 上的报错是明确的"不支持"而非缺驱动）。驱动只负责"造容器/造 VM/造 Pod"，隔离语义统一由 RFC 0012 的 isolation-interface 契约约束——attach → Bound → confirm → Ready → start_agent → Running，trait 链上每个状态转移都以 `self: Box<Self>` 按值消费前一状态（contract.rs:17），**顺序即安全属性**：没确认过边界就不能起 agent。

**网关默认拒绝路由**：L7 层（l7/mod.rs 的 validate_l7_policies，500 行静态校验）对 REST/GraphQL/JSON-RPC/MCP 规则做全量校验后，运行时逐请求匹配——没有命中 allow 规则的一切出站默认拒绝，且不可检查（uninspectable）的流量在 fail_closed 配置下同样拒绝。凭据守卫按"端点必须与 token grant 指定的 host:port 匹配"二次核验，防止拿 A 服务的 token 打 B 服务（proxy.rs 有专门的 endpoint mismatch 类型化拒绝测试）。

## 4. 关键模块深读（7 个）

### 4.1 openshell-core：一切组件的共享底座

lib.rs 声明 46 个子模块（proto 生成代码门面、配置、错误、策略域模型、sandbox 会话、凭据、遥测），fanIn=138 全仓第一——改这里等于动全身。两个值得记住的细节：`src/proto/mod.rs` 以 `include!(concat!(env!("OUT_DIR"), "/openshell.rs"))` 引入 build.rs 用 vendored protoc + tonic_prost_build 生成的代码，并顺带产出 FileDescriptorSet 供 server 运行时枚举 RPC 做 handler 穷尽性测试；`src/paths.rs` 是全仓唯一的 XDG 目录解析点（config/state/data 三分），敏感文件统一走属主-only 权限助手。`sandbox_session.rs` 的 SandboxSessionId 是"一次运行期启动"的强身份：同一持久启动的重试复用同值、后续启动换新值——监督侧对账沙箱世代就靠它。

### 4.2 策略线：policy-schema / policy / merge.rs

三级分工：policy-schema 刻意只依赖 5 个 crate（miette/serde/serde_json/serde_yml/thiserror），钉死规范表示与解析语义；policy 负责与 protobuf 互转和安全校验；server 侧的 merge.rs 把 agent 的原子变更序列（PolicyMergeOp）折叠成有效策略。安全校验的三板斧——路径穿越、过宽路径、TLD 通配——都在 policy crate 的 lib.rs 导出面上。MCP 检查契约冲突防护与 advisor 观测规则的规范化改写（canonicalize_advisor_add_rule）也在这条线上：agent 观测到的"建议规则"不能直接进策略，必须先规范化再走覆盖判定（policy_covers_rule）。

### 4.3 isolation-interface + openshell-sandbox：RFC 0012 落地

contract.rs（1075 行）是跨模块的类型库：IsolationBackend → BoundBoundary → ReadyBoundary → RunningBoundary 的 trait 链、边界确认体系（OuterFenceGuarantees/BoundaryConfirmation）、网络中介类型（PendingTcpOpen/PendingDnsQuery）。openshell-sandbox 的 main.rs（2040 行）是沙箱内二进制：启动先跑 qualify_runtime() 逐项验证 seccomp notify 回路、Landlock ABI、DNS 中继、socket 虚拟化（还带 capability-probe 独立子命令做 Phase 0 探测），不合格 fail-fast；process.rs 的 pre_exec 里完成 setsid/TIOCSCTTY 并强制 Landlock+seccomp。注意它还有 copy-self/bootstrap/seed-workspace 三个自举子命令——init container 直接调二进制自身完成自我拷贝，不依赖 sh/cp。

### 4.4 supervisor-network：出站守门人

三个大件：`opa.rs` 内嵌 regorus（OPA 兼容）引擎，每个 CONNECT 请求都查询，支持策略代际（PolicyGenerationGuard）热重载，引擎不可用即 fail-closed；`proxy.rs`（14996 行）是透明 TCP 捕获 + 显式 CONNECT + 转发 HTTP 三路径的代理主体，做目标校验、凭据端点不匹配检测、OCSF 全量允许/拒绝事件；`l7/` 目录按协议分 provider（REST/GraphQL/JSON-RPC/MCP/WebSocket），l7/mod.rs 的 validate_l7_policies 做 500 行静态校验，middleware.rs 定义 fail_closed/fail_open 链语义。AWS SigV4 请求签名（sigv4.rs 585 行）也在这条线上：代理剥掉沙箱客户端的占位 Authorization 头、用真实凭据重签，沙箱永远见不到密钥。

### 4.5 openshell-prover：形式化策略检查

prove() 流水线：parse_policy → 加载凭据集与二进制能力注册表 → build_model（Z3）→ run_all_queries → apply_accepted_risks → 渲染报告。两个设计点：registry.rs 用 `include_dir!` 把 registry/ 目录（git/curl/gh 等二进制能力 YAML）编译期内嵌，未注册二进制回退到保守描述符（can_exfiltrate=true 宁可错报）；containment 只做"刻意收窄"的可靠模型——REST 方法/路径、L4 目标、符号 IP 范围，超出即 Unsupported，绝不猜。prover-cli 是独立二进制 openshell-prover，退出码即结论（0=通过、1=有未接受 findings、3=不支持的策略面），测试覆盖到 FIFO 非阻塞拒收、内嵌 NUL 拒收这类输入卫生细节。

### 4.6 openshell-server：分布式控制平面

grpc/ 目录（mod.rs + 16 个 handler 子模块）承载 82 个 rpc 的分派；auth/ 子系统 16 个模块实现认证器链（OIDC/peer/sandbox_jwt）与 Principal 四分类（User/Sandbox/Peer/Anonymous）；persistence/mod.rs 的 Store 是 Postgres/Sqlite 的 enum dispatch，CAS 乐观并发 + keyset 分页 + 跨对象分布式变更锁。server-macros 的 #[rpc_authz] 属性宏读方法上的 #[rpc_auth] 标注生成 MethodAuth 常量表——鉴权要求声明在 proto（options.proto 的 AuthorizationRule）与 handler（宏）两处对齐。迁移用 sqlx::migrate! 编译期嵌入 migrations/{postgres,sqlite}/ 目录。

### 4.7 gateway + driver-docker：组合与最重驱动

gateway crate 的 lib.rs 就是"驱动装配车间"：Linux 按 feature 开关注册 kubernetes/podman/docker/vm（vm 优先级 u16::MAX），Windows 注册 mxc 并给其余四个名字装明确的 Unsupported 工厂。driver-docker 的 lib.rs（6586 行）是最重的单驱动实现：sandbox 生命周期、镜像拉取与运行时二进制提取、GPU CDI 设备解析、passwd/group 工作负载身份解析、事件轮询与快照调和、AppArmor/挂载/卷。对照着 driver-mxc 的 policy_map/map.rs 读很有收获——MXC 表达不了的策略（端口/协议/L7/二进制 scope）全部显式记 loss，并用 Pattern C 把文件系统交给 MXC、完整网络策略保留给 host CONNECT 代理，"能力有损翻译"是被显式建模的，不是静默降级。

## 5. 数据流走读：一条 agent 命令的完整旅程

以 `openshell sandbox create --image … -- claude-code` 为例（涉及文件均经源码核实）：

1. **CLI 入口**（crates/openshell-cli/src/main.rs，7052 行单文件）：clap 解析 17+ 子命令之一 Sandbox::Create，先经 src/tls.rs 的 TlsOptions 装配 gRPC 通道（edge token/OIDC 刷新/mTLS 三选一，insecure 走显式 danger 模块）；实现主体在 src/run.rs（8455 行）——create 的 781 行编排含 rootfs tar 分阶段上传与 git 感知 upload；
2. **网关认证与授权**：请求进 openshell-server 的 grpc 分派，auth/ 认证器链产出 Principal（人类用户走 OIDC，沙箱监督器走网关铸造的 sandbox JWT，网关节点走 Peer）；#[rpc_authz] 生成的 MethodAuth 常量表按 proto options.proto 声明的 auth_mode/workspace_role 做方法级授权，再过 workspace_authz 工作区层；
3. **控制平面编排**（grpc/sandbox.rs）：ServerState 取 compute driver（gateway 装配好的注册表按优先级选出），校验 spec、写持久化（Store CAS）、生成 staging token；
4. **驱动造沙箱**（以 driver-docker 为例）：拉镜像、提取 openshell-sandbox/supervisor 运行时二进制、解析 GPU CDI 设备、把 supervisor bundle（boundary.json/tls 材料等引导材料）暂存进容器，启动控制进程；
5. **边界协议握手**（sandbox-backend/src/boundary_protocol.rs）：supervisor 与沙箱在单一互认证连接的 gRPC 流内交换长度定界 JSON 帧——驱动只选传输（Unix socket/TCP/vsock），进程生命周期与认证消息全由这层版本化协议承担；
6. **资格鉴定 fail-fast**（openshell-sandbox/src/main.rs）：沙箱二进制启动先 qualify_runtime() 逐项验证内核原语（seccomp notify 往返、Landlock ABI 版本、DNS 中继绑定、socket 虚拟化），任何一项不合格直接退出并输出 JSON 报告；
7. **监督器双角色**（openshell-supervisor/src/main.rs）：SupervisorRole::IsolationBackend 走 run_sandbox（attach 隔离后端 → Bound → confirm → Ready → start_agent），NetworkProxy 走 run_network_proxy；两者都装配 OCSF 双层日志（stderr 简写 + /var/log JSONL + 日志推送）；
8. **agent 进程落地**（openshell-sandbox/src/process.rs）：ProcessHandle::spawn_impl 组装 PTY/管道双形态，pre_exec 里 setsid/TIOCSCTTY/剥离监督者环境变量、注入 TLS 与供应商环境，随后强制 Landlock 规则集 + seccomp 过滤器——agent 从第一行代码起就在围栏里；
9. **出站流量**（supervisor-network/src/proxy.rs）：agent 的 HTTPS 请求进 CONNECT 代理 → opa.rs 查策略（Rego，热重载）→ 允许则继续 L7 协议检查（l7/）与凭据注入（token grant / SigV4 重签）→ 拒绝则记 OCSF 网络活动事件（含 default-deny 引擎标记）；活动/拒绝聚合计数由 supervisor 的聚合器循环上报网关；
10. **策略热重载与审计**：supervisor 的 policy poll loop 持续拉取网关策略变更，代际守卫保证切换原子；一切决策落 OCSF 事件（JSONL）与 OTLP trace，供事后审计与 prover 的 accepted_risks 对账。

一句话总结这条链：**契约（proto）定义形状，控制平面（server）管状态，驱动（driver）造围栏，沙箱（sandbox）验内核原语，监督器（supervisor）管放行，遥测（ocsf）留全证**。

## 6. 设计决策与取舍

- **fail-closed 是全仓第一哲学**。不是口号而是代码分布：身份归因在 entrypoint_pid==0 时 fail closed（supervisor-network/src/identity_source.rs:113）；OPA 引擎不可读/策略不可解析即拒（crates/openshell-supervisor-network/src/run.rs:359）；L7 不可检查流量在 fail_closed 链下拒绝（l7/middleware.rs）；prover 超出支持模型返回 Unsupported 而非放行；未注册二进制的描述符 can_exfiltrate=true 宁可错报。读代码时凡是遇到"不认识/读不到/超限"分支，默认行为几乎都是拒。
- **编译期嵌入换取单二进制自包含**。三处代表：prover 的 registry.rs 用 `include_dir!` 内嵌二进制能力档案（运行时可用目录覆盖）；core 与 server 的 proto 生成代码用 `include!(OUT_DIR)` 引入（storage_proto.rs 还 include_bytes! 了 FileDescriptorSet）；OCSF vendored 官方 JSON Schema 内嵌供测试校验。代价是改这些资源要重编译，收益是发布产物无外部依赖、供应链面更小。
- **typestate 式生命周期**。isolation-interface 没有 typestate 字样，但 contract.rs:17 明写"Each transition consumes the prior state by value (`self: Box<Self>`)"——Bound→Ready→Running 的状态在类型与所有权双重意义上线性流动，编译期就消灭"跳过确认直接起 agent"这类状态机 bug。
- **proto 单一来源纪律**。buf.yaml 声明双模块（proto/ 与 crates/openshell-server/proto 私有存储格式分离）；lint STANDARD + breaking FILE 策略；tasks/scripts/check_proto_compatibility.py 按 git tag 推断发布 train，minor 增量才允许 breaking——0.x 阶段的兼容性门禁是脚本化而非口头约定。
- **Windows 的显式收缩**。mxc 驱动整个 crate 非 Windows 目标编译为空 stub 保 Linux 构建绿色（driver-mxc/src/lib.rs），Windows 上另外四个驱动名注册 UnsupportedWindowsFactory——"明确不支持"优先于"静默缺失"。mxc 的 policy_map 把能力损失（loss）记成显式字段而非静默丢弃，是"诚实降级"的范本。
- **双持久化的 enum dispatch**。Store 直接是 Postgres/Sqlite 的 enum 而非 trait object——方法调用静态分派、测试两边都要过，避免"只测了一边后端"的漂移。迁移文件 sqlx::migrate! 编译期嵌入，启动即校验。
- **大文件与小模块的张力**。cli/run.rs 8455 行、proxy.rs 14996 行、merge.rs 6931 行——本项目不追"每文件 300 行"教条，而是以"一个内聚职责一个文件"划界（run.rs 是全部 CLI 命令实现、proxy.rs 是完整代理状态机），配合 workspace 级 clippy pedantic+nursery 纪律控制质量。

## 7. 已知坑与勘误（新人别踩）

以下全部经源码逐项核实（ls/grep/wc 实证，非转述）：

1. **`.claude/agent-memory/principal-engineer-reviewer/MEMORY.md` 已过时**：第 5 行仍写 `crates/openshell-server/src/grpc.rs`——该文件早已不存在，现在是 grpc/ 目录（mod.rs + 16 个 handler 子模块）；第 11 行的 `crates/openshell-sandbox/src/grpc_client.rs` 同样不存在（ls 实证）。审查代理的跨会话记忆落后于重构，引用它给的路径前先 ls。
2. **RFC 0005 的 nftables 零实现**：RFC 0005（state: review）多处描述"nftables bypass enforcement / nftables LOG parsing / inet filter table"，current-shape.md 甚至标注为"current main"行为；但全仓 .rs 无任何 nftables 操纵代码，仅有的 "nftables" 字符串在 OCSF 事件标签（shorthand.rs:644 的 `FirewallRule::new("bypass-detect", "nftables")`）与文档里。设计文档超前于实现，读 RFC 时先 grep 对应 crate。
3. **`openshell/sigv4` 中间件是纯规划**：RFC 0009 明确定位 SigV4 为"restricted built-in `HttpRequest/post_credentials` hook"且属"possible future extensions/follow-up design work"；当前唯一内建中间件是 `openshell/regex`（supervisor-middleware-builtins/src/lib.rs:39 的 match 只有两臂）。**注意区分**：作为 provider profile `credential_signing: sigv4` 的代理侧签名是已实现且带 localstack E2E 的（supervisor-network/src/sigv4.rs 585 行 + tests/sigv4_localstack.rs）——"sigv4"一词在中间件语境是规划、在凭据签名语境是现实。
4. **vendored OCSF schema 有 404 占位 stub**：`crates/openshell-ocsf/schemas/ocsf/v1.8.0/objects/connection_info.json`（与 v1.7.0 同名文件）内容是 `{"error": "Object connection_info not found"}`——抓取脚本当年把 404 响应存成了文件。依赖 schema 目录"非空即有效"的校验会踩坑。
5. **v1.7.0 schema 快照零代码引用**：validation/schema.rs 只加载 v1.8.0 路径；"降级到 1.7.0"由 format/downgrade.rs 的代码逻辑（字段剥离 + unmapped.downgraded_from 标记）完成，不消费 v1.7.0 schema 目录。整个 v1.7.0 目录是遗留快照，可视为死重。
6. **Go 版本三个口径**：`sdk/go/go.mod` 语言版本 `go 1.25.13`；`sdk/go/README.md:319` 与 `docs/sdk/go.mdx:17` 写 "Go 1.25.13 or later"；`mise.toml:28` 的 Go 工具链钉在 `1.26.7`。语义上不矛盾（最低语言版本 vs 开发工具链），但三个数字并存容易让人怀疑哪个是权威——以 go.mod 为准。
7. **TESTING.md 死引用**：TESTING.md:232 引用 `deploy/docker/Dockerfile.images`，该文件不存在（deploy/docker/ 下只有 Dockerfile.ci/gateway/sandbox/supervisor 与 cross-build.sh）；另 TESTING.md 的 harness 模块表漏列了实际存在的 cli.rs 与 host_process.rs（e2e/rust/src/harness/ 实有 9 个模块）。
8. **CI.md 死锚点**：CI.md:413 链接 `AGENTS.md#vouch-system`，但 AGENTS.md 全文无 "vouch"——vouch 体系实际在 CONTRIBUTING.md:23-32（AI 生成贡献泛滥所以首 PR 须真人背书）。
9. **update-docs 技能名与目录名不一致**：目录是 `.agents/skills/update-docs/`，SKILL.md front matter 的 name 却是 `update-docs-from-commits`。按名字查找技能两处都要试。
10. **数据库迁移编号跳 002/003**：migrations/{postgres,sqlite}/ 只有 001、004-008，002/003 从未存在（sqlx::migrate! 按文件名顺序执行不要求连续，但"补编号"前必须知道这个空档不是遗漏）。同理 rfc/ 编号跳过 0007/0008，rfc/README.md 的状态机里没有"编号回收"概念。
11. **CI 是镜像触发制**（CI.md）：NVIDIA 自托管 runner 跑的是 copy-pr-bot 镜像到 `pull-request/<N>` 分支后的 push 事件，不是原生 PR 事件——外部贡献者 PR 不自动跑 CI，需 `/ok to test <SHA>` 人工放行，这解释了为什么 PR 上看不到常规的 checks 树。

## 8. 上手路径：前三天阅读顺序（对照 16 步 tour）

**第一天——定位与契约（tour overview → proto）**：README.md 的四支柱定位 → AGENTS.md 的 38 crate 架构总表（本仓最高密度的地图，比任何文档都全）→ GOVERNANCE.md（六价值观与"AI agent 不得担任 Maintainer"）→ proto/README.md 的 API 设计约定（实体引用命名/workspace_scope/每 RPC 专用消息）→ proto/openshell.proto 通读 82 个 rpc 的服务面。环境：mise（mise.toml 钉了 rust 1.95.0 / go 1.26.7 / python 3.14.5），`mise run test` 起步。

**第二天——安全模型纵深（tour policy → isolation → drivers）**：policy-schema/src/lib.rs 的有界解析 → policy/src/lib.rs 与 merge.rs 的策略合并 → isolation-interface/src/contract.rs 的生命周期契约（对照 RFC 0012）→ openshell-sandbox/src/main.rs 的资格鉴定 → gateway/src/lib.rs 的五驱动注册 → 任选 driver-docker/src/lib.rs 或 driver-mxc/src/policy_map/map.rs 读"策略如何落到具体后端"。下午跑 `openshell-prover` CLI 对 providers/ 目录任一 YAML 做一次包含性检查，看退出码与报告（prover-cli/tests/cli.rs 的 21 项黑盒测试就是行为说明书）。

**第三天——数据平面与协作（tour gateway → supervisor → prover → conformance → cli-tui → sdk → tasks-rfc → agent-collab）**：supervisor-network/src/proxy.rs 挑 CONNECT 主路径读 → l7/mod.rs 的静态校验 → opa.rs 热重载 → ocsf/src/events/base_event.rs 的事件底座 → conformance/src/lib.rs 看跨驱动一致性如何定义 → rfc/0001（核心架构三组件）、0002（agent 驱动策略管理——理解"为什么策略要走 draft/审批/prover"）、0014（发布稳定性）→ 最后读 .agents/skills/build-from-issue/SKILL.md 理解"授权语义分层"（直接指令只授权所请求阶段），再看 CONTRIBUTING.md 的 vouch 体系。动手题：用 skills/openshell-cli 技能（或直接 CLI）起一个 docker 网关、创建最小策略沙箱、观察 OCSF 拒绝事件。

阅读心法：这个仓库**先契约后实现**（改任何 API 先过 proto 与 buf breaking）、**先 RFC 后大改**（rfc/README.md 规定重大变更先开 issue）、**文档与代码同步是技能化纪律**（sync-agent-infra 的维护地图）。动手验证：`cargo test -p openshell-policy -p openshell-policy-schema` 单 crate 起测最快；改 proto 后 `mise run` 里的 proto 兼容检查会拦你。

## 附：勘误与设计文档 vs 现实差距清单

| # | 文档/记忆主张 | 现实（源码实证） | 影响与处置 |
|---|---|---|---|
| 1 | MEMORY.md:5 `crates/openshell-server/src/grpc.rs` | 已拆为 grpc/ 目录（mod.rs + auth_rpc/mutation_replay/policy/provider/sandbox/service/workspace 等 16 子模块）；MEMORY.md:11 的 sandbox/src/grpc_client.rs 也不存在 | 引用审查代理记忆的路径前先 ls；该记忆文件需人工刷新 |
| 2 | RFC 0005（review）"nftables bypass enforcement / LOG parsing"为现状 | 全仓零 nftables Rust 实现；仅 OCSF 事件标签字符串（shorthand.rs:644）与 podman 文档提及 | RFC 属前瞻设计；以 RFC 评估现状会高估 L4 层能力 |
| 3 | RFC 0009 提及内建中间件 `openshell/sigv4` | 未实现；内建仅 `openshell/regex`（middleware-builtins crates/openshell-supervisor-middleware-builtins/src/lib.rs:39）。但 provider `credential_signing: sigv4` 已实现（sigv4.rs 585 行 + localstack E2E） | 两个"sigv4"语境勿混：中间件=规划，凭据签名=现实 |
| 4 | vendored OCSF schema 目录完整可用 | v1.8.0 与 v1.7.0 的 objects/connection_info.json 均为 `{"error": "Object connection_info not found"}` 404 stub | 别拿"文件存在"当 schema 有效；校验测试可能被 stub 误导 |
| 5 | 内嵌 v1.7.0 schema 支撑降级 | validation/schema.rs 只引用 v1.8.0；降级由 format/downgrade.rs 代码逻辑完成，v1.7.0 目录零引用 | v1.7.0 目录是死重；清理或留作历史快照均可 |
| 6 | Go 版本权威口径 | go.mod=1.25.13（语言下限）/ sdk README+docs=1.25.13 or later / mise.toml=1.26.7（工具链） | 以 go.mod 为准；三数字并存是最低版本与工具链之别 |
| 7 | TESTING.md:232 `deploy/docker/Dockerfile.images` | 文件不存在（目录仅 Dockerfile.ci/gateway/sandbox/supervisor） | GPU E2E 文档引用死路径；harness 模块表也漏 cli/host_process 两模块 |
| 8 | CI.md:413 `AGENTS.md#vouch-system` | AGENTS.md 无 vouch 内容；实际在 CONTRIBUTING.md:23-32 | 死锚点；vouch 政策本身有效 |
| 9 | `.agents/skills/update-docs/` 技能名 | SKILL.md name 字段为 `update-docs-from-commits`，与目录名不一致 | 按名检索/路由技能时两处都试 |
| 10 | 迁移编号连续隐含 | migrations/{postgres,sqlite}/ 为 001、004-008，002/003 从未存在；rfc/ 亦跳 0007/0008 | 非遗漏勿"补号"；新迁移取下一可用号（009）即可 |
| 11 | RFC 状态即实现状态 | 0005/0012/0014 均为 review 态在途工程；0014 定义 alpha 出口标准（三轨发布 + C01-C07 conformance 认证） | 读 RFC 先看 front matter 的 state 字段 |

——完——
