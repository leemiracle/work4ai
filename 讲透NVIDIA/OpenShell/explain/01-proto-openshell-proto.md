# 01 · proto/openshell.proto：82 个 RPC 的安全契约面

## 一、角色定位

`proto/openshell.proto`（3805 行）是整个 OpenShell 系统的"接口宪法"。全仓 38 个 Rust crate 里唯一一处把"谁能调用什么"说清楚的地方：单个 `service OpenShell`（openshell.proto:23）声明了 **82 个 rpc**，配合 **232 个 message + 20 个 enum**，把沙箱生命周期、监督器会话、凭据刷新、策略审批四条安全线全部钉死在跨语言的 protobuf 里。Go/Python/TS SDK 与 Rust 端共享同一份编译产物，谁也别想"实现里偷偷改语义"。文件头注释（openshell.proto:15-22）明确了资源模型的所有权：`Sandbox`/`SandboxSpec`/`SandboxStatus`/`SandboxPhase` 是网关拥有的公共类型，内部 compute driver 不得直接导入或返回——驱动观察值必须先由网关翻译成公共资源再持久化/返回。

## 二、内部结构

**授权元数据内嵌在方法选项里**，这是本文件最重要的结构决策。`options.proto:26-29` 用 `extend google.protobuf.MethodOptions` 扩展了字段号 50000 的 `authorization`，类型 `AuthorizationRule`（options.proto:12-24）含 `auth_mode`/`workspace_role`/`global_role`/`scope` 四字段。auth_mode 只有四个合法值（options.proto:13）：`bearer`（用户 OIDC）、`sandbox`（沙箱监督器 JWT）、`peer`（网关副本之间）、`dual`（两者皆可）、外加 `unauthenticated`。每个 rpc 无一例外都带这个 option——`openshell-core` 的 `FILE_DESCRIPTOR_SET`（crates/openshell-core/src/lib.rs:95）让 server 测试能枚举全部 RPC 校验覆盖率，82/82 缺一不可。分档示例：Health 匿名（:25-29）；GetGatewayInfo 要求 `global_role: platform_admin`（:39-45）；CreateSandbox 要求 `scope: sandbox:write + workspace_role: user`（:48-54）。

**沙箱生命周期**：CreateSandbox（:48）→ GetSandbox/ListSandboxes（:74/:83）→ Stop/Start（:181/:190）→ Delete（:172）。状态归一化在 `SandboxStatus`（:1160）：`phase`（:1170）由网关推导而非透传驱动条件；`current_policy_version`（:1172）在沙箱上报策略加载完成时更新；`main_process_instance_id`（:1175）用于拒绝重启后的陈旧退出上报；`restart_count`/`next_restart_time`（:1190/:1192）承载崩溃循环退避。`SandboxPhase` 枚举（:1217-1232）九个相位 + `reserved 10`（:1229-1231）——注意 `SANDBOX_PHASE_RESTARTING` 已被显式保留废弃，客户端不要期待它回来。

**凭据双闸**：`IssueSandboxToken`（:732）把 K8s 投影 ServiceAccount JWT 换成网关铸造、绑定沙箱 UUID 的 JWT（K8s 路径专用；单机驱动在 create 流程里直接拿 JWT，从不调这个 RPC，见 :727-731 注释）。`RefreshSandboxToken`（:744）的注释（:738-743）是安全设计的教科书：旧 token 到自身过期前仍有效（部署应保持短 TTL 限制重放窗口）；监督器在 token 生命周期的 ~80% 处由后台任务刷新；**新 token 只缓存在内存里，磁盘上的 bootstrap 文件刻意不回写**。

**策略审批闭环**（:639-725 一整节）：沙箱侧 `SubmitPolicyAnalysis`（:644，auth_mode: sandbox）提交拒绝摘要+建议块；人侧 `ApproveDraftChunk`（:661，要求 `config:write + workspace_role: admin`）合并进活跃策略；`ApproveAllDraftChunks`（:681）批量放行但**跳过带安全标记的 chunk（除非强制）**；`EditDraftChunk`（:691）支持在批准前收窄（注释例：narrow allowed_ips）；`UndoDraftChunk`（:700）反向撤销已合并规则；`GetDraftHistory`（:719）留痕。提案方只允许"sandbox"身份、批准方只允许"admin"身份，攻防两侧权限刻意分离。

**监督器会话与字节中继**：`ConnectSupervisor`（:552）是双向流，监督器启动即挂上、终身保持；`SupervisorMessage`/`GatewayMessage`（:2973/:2983）各只含 5 个 oneof payload（hello/heartbeat/relay 开关等）。原始字节走独立的 `RelayStream`（:584）——与 ConnectSupervisor 同一条 TCP+TLS+HTTP/2 连接上的新 HTTP/2 流，**无新 TLS 握手、无反向 HTTP CONNECT**（:582-583 注释）。`RelayOpen`（:3054）由网关下发 channel_id，`TcpRelayTarget`（:3071）Phase 1 只接受环回地址（:3072 注释）。多副本网关间还有 `peer` 模式的 `PeerRelay`（:597）转发。

## 三、外部连接

上游被 `datamodel.proto`/`sandbox.proto`/`options.proto` import（:8-13）；下游由 `openshell-core/src/proto/mod.rs` 生成 Rust 侧（crates/openshell-core/src/proto/mod.rs:17-21），server 的 `#[rpc_authz]` 宏消费 AuthorizationRule 生成方法级授权表；`secret` 字段选项（options.proto:33-35）禁止敏感字段穿过通用拦截器边界。BeginRootfsTarStaging（:64-71）体现了"不信任客户端路径"的设计：网关返回一次性 token + 绝对路径，客户端**从不自己命名文件系统路径**。

## 四、数据流

用户带 bearer token 调 CRUD → 网关查 AuthorizationRule → 驱动观察 → 网关翻译成公共 SandboxStatus 返回；沙箱内监督器带 sandbox JWT 维持 ConnectSupervisor + 在 80% TTL 刷新 token；拒绝事件经 SubmitPolicyAnalysis 上行 → 人工 ApproveDraftChunk/EditDraftChunk 收窄后合并 → 新 policy version 经 SandboxStatus.current_policy_version 回流。

## 五、设计决策

1. **授权进 proto 而非代码注释**：schema 即执行依据，跨语言 SDK 免二次实现；82 rpc 全覆盖可被测试枚举验证。
2. **拒绝默认**：资源型 rpc 全部要 scope+role；peer/sandbox/dual 三种机器身份与人类 bearer 分离。
3. **生命周期归一化**：客户端只读 SandboxPhase，不解读原始平台条件——把异构后端差异关在网关内。
4. **reserved 字段纪律**：`reserved 2`（SessionAccepted:3008）、`reserved 10`（SandboxPhase:1229）防止字段号复用造成的语义漂移。

## 六、新人提示

- 任务书里"252 定义"实测为 232 message + 20 enum = 252 顶层类型（加 1 个 service 共 253），以 `grep -c` 为准。
- `SANDBOX_PHASE_RESTARTING` 已删除并 reserved，别在客户端 switch 里写它。
- IssueSandboxToken 请求体是空的（:822 `message IssueSandboxTokenRequest {}`）——身份完全来自请求头里的 K8s 投影 JWT，别往 body 里塞字段。
- RefreshSandboxToken 不是撤销：旧 token 到期前并行有效，安全上限由 TTL 决定。
- RelayStream 复用同一连接是刻意为之（省握手+免反向 CONNECT），不要"优化"成新建连接。
