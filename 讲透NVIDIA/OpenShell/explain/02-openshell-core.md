# 02 · openshell-core：全仓共享的底座库

## 一、角色定位

`openshell-core` 是 workspace 里 38 个 crate 的公共底座。`src/lib.rs` 用 46 个 `pub mod` 声明（crates/openshell-core/src/lib.rs:12-59，其中 `external_driver_socket` 仅 unix、`oauth` 仅 feature 门控）铺开全部职责面：proto 生成码门面、配置、错误、策略数据模型、JWT/OIDC、遥测、路径、网络工具……除了 `openshell-policy` 这类独立 crate，几乎所有组件都直接依赖它。它自己是"哑"库——不含任何二进制入口，只提供被各方引用的类型与转换。crate 文档（crates/openshell-core/src/lib.rs:4-10）自述四件套：协议缓冲定义与生成代码、配置管理、公共错误类型、构建版本元数据。

## 二、内部结构

**proto 门面**（src/proto/mod.rs，201 行）：`mod generated`（crates/openshell-core/src/proto/mod.rs:17-18）通过 `include!(concat!(env!("OUT_DIR"), "/openshell.rs"))` 吸入 tonic/prost 生成码，再用 `pub use self::generated::openshell::v1 as openshell`（crates/openshell-core/src/proto/mod.rs:21）对外只有一个名字空间。四个子包 re-export 各归其位：`datamodel`（:31）、`sandbox`（:35）、`compute`（:39）、`extension`（:43）。最精巧的是 `pub mod v1` 别名层（crates/openshell-core/src/proto/mod.rs:27-29）：嵌套包对根包 `openshell.v1` 的引用可能被生成为 `super::super::v1::*`，别名让这条路径永远可达——这是 prost 生成器的已知怪癖的工程兜底。`credentials`（crates/openshell-core/src/proto/mod.rs:56-58）单独 include 另一份生成文件。整个模块挂满 `#[allow(clippy::all, ...)]`（crates/openshell-core/src/proto/mod.rs:9-17），生成码不背 lint 债。

**策略数据模型**（src/policy.rs，236 行）：`SandboxPolicy`（crates/openshell-core/src/policy.rs:15-21）五字段——version/filesystem/network/landlock/process，是策略的"运行时视图"（区别于 openshell-policy 的授权态 YAML 视图）。两个默认值即安全立场：`NetworkPolicy::default()` 直接 `NetworkMode::Block`（crates/openshell-core/src/policy.rs:51-58），`NetworkMode` 枚举（:60-66）默认变体就是 Block；`FilesystemPolicy::default()` 默认 `include_workdir: true`（:35-43）。最关键的转换在 `TryFrom<ProtoSandboxPolicy>`（:112-138）：**proto 里的网络策略字段被无条件覆盖为 `NetworkMode::Proxy`**（:116-121，注释直言"集群模式下永远走代理网络，让 OPA 评估全部出站"）——proto 端点里的 allow 语义在这里被降格为"必须过代理受检"。`LANDLOCK_COMPATIBILITY_VALUES`（:99）是 landlock 兼容模式的单一真源，YAML 解析、proto→运行时转换、网关校验三方共享，防止合法值集合漂移。

**错误线**（src/error.rs，140 行）：`Error` 枚举（crates/openshell-core/src/error.rs:14-68）七个变体（Config/Io/Tls/Transport/Execution/Process/Timeout），每个都带 `#[diagnostic(code(openshell::*))]`（miette 诊断码），配五个命名构造器（:72-104）。`ComputeDriverError`（:112-128）是另一条线：所有计算驱动（docker/k8s/podman/vm/mxc）把后端错误映射成 AlreadyExists/NotFound/InvalidArgument/Precondition/Message 五类，再经 `From<ComputeDriverError> for tonic::Status`（:130-140）翻译成 gRPC 状态码——驱动差异止步于此，网关只见标准状态。

**配置**（src/config.rs，1653 行）：`Config`（crates/openshell-core/src/config.rs:165）聚合计算驱动/凭据驱动/服务路由；`PolicyValidationFailureMode`（:52）决定策略校验失败时是拒绝还是放行观察；`GatewayJwtConfig`（:796）的 `token_ttl()`（:816）与 `sandbox_token_ttl()`（:823）分别控制用户与沙箱 token 的 TTL。`resolve_supervisor_image_tag`（:124）处理监督器镜像 tag 的多候选回退。

**跨组件事件**（src/denial.rs）：`DenialEvent`（denial.rs:14-32）由网络代理（L4/L7 拒绝）与旁路监视器（绕过代理的直连尝试）共同产出；它放在 core 是刻意的——两个监督器叶子（supervisor-network 与 supervisor-process）都要产出它，又不能互相依赖（denial.rs:7-12 注释）。`denial_stage` 五个值（:28）：connect/forward/ssrf/l7/bypass。

**版本与描述符**：`VERSION`（crates/openshell-core/src/lib.rs:81-84）优先取 `OPENSHELL_GIT_VERSION` 环境注入（build.rs 从 git 元数据算出，Docker/CI 无 .git 时回落 `CARGO_PKG_VERSION`）；`FILE_DESCRIPTOR_SET`（crates/openshell-core/src/lib.rs:90-95）把全套 proto 的 FileDescriptorSet 编进二进制，server 测试靠它枚举全部 RPC 验证 `#[rpc_auth]` 覆盖率。

## 三、外部连接

上游：tonic/prost（OUT_DIR 生成码）、miette/thiserror。下游消费者几乎全覆盖：openshell-server/gateway（Config+错误+proto）、openshell-sandbox（policy.rs 的 SandboxPolicy 是 boundary_exec 的执行依据）、openshell-supervisor-network（denial.rs 的 DenialEvent、endpoint_status、mcp 版本工具）、openshell-policy（core::proto 类型与 container_paths 的 CONTAINER_POLICY_PATH）。

## 四、数据流

proto/*.proto --tonic_build--> OUT_DIR 生成码 --> proto/mod.rs 门面 --> 各 crate `use openshell_core::proto::X`；策略流：YAML（openshell-policy 解析）→ ProtoSandboxPolicy（存储/传输）→ core::policy::SandboxPolicy（沙箱运行时，TryFrom 强制 Proxy）；错误流：驱动后端错误 → ComputeDriverError → tonic::Status → gRPC 客户端。

## 五、设计决策

1. **proto 门面单一出口**：生成码的路径怪癖（super::super）被 alias 层吸收，业务代码永远 `openshell_core::proto::SandboxPolicy`。
2. **默认即拒绝**：NetworkMode 默认 Block；运行时转换再把 proto 的 allow 语义强制改写为 Proxy 受检——"允许"必须经过"可检查"。
3. **错误双轨**：通用 Error（人读，带诊断码）与 ComputeDriverError（机器读，映射 gRPC 码）分离，各服务各取所需。
4. **共享类型下沉但不引入依赖**：DenialEvent 放 core 是为了打破两个监督器叶子间的循环依赖。

## 六、新人提示

- 别被 `policy.rs` 名字骗了：它只是运行时视图，策略的解析/校验/合并在 `openshell-policy`，授权态规范表示在 `openshell-policy-schema`——三个"policy"各管一段。
- `TryFrom<ProtoSandboxPolicy>` 会**丢弃** proto 里的网络模式并强制 Proxy（crates/openshell-core/src/policy.rs:116-121）；如果你在单机 docker 路径上调试"为什么 endpoint 的 enforcement 不生效"，先看这条转换。
- `Error::Timeout` 没有载荷字段（crates/openshell-core/src/error.rs:65-67），超时上下文要靠 tracing 补。
- lib.rs 顶部 46 个 mod 是"文档式目录"：找功能先扫这里，比全仓 grep 快。
- `FILE_DESCRIPTOR_SET` 是 `include_bytes!` 进二进制的（crates/openshell-core/src/lib.rs:95），改 proto 后要重编 core 才能被 server 测试看到。
