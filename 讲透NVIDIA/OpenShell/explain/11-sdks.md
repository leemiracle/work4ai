# 11 · SDK 三语言：Go / TypeScript / Python 的客户端面差异

## 一、角色定位

OpenShell 对外暴露四张客户端脸：**Rust `openshell-sdk`**（crates/openshell-sdk，内部基石，被 CLI/TUI 复用并经 napi-rs 打成 npm 包 `@openshell/sdk`）、**Go**（sdk/go）、**TypeScript**（sdk/typescript，npm 名 `@nvidia/openshell-sdk`）、**Python**（python/openshell）。三家"外部"SDK 定位一致——把 82 个 RPC 的 proto 契约包装成各自语言的惯用 API——但成熟度与取舍差异显著：Go 最全（12 个域子客户端 + 全内存 fake），Python 聚焦沙箱与凭据（单文件 2443 行手写 client），TypeScript 走 Connect 栈最薄。TS client.ts:5-9 的注释把谱系说破：scoped client"**mirroring the Python SDK**"，组织模型"mirroring the CLI's noun-verb model"——三家刻意对齐概念而非互相移植代码。

## 二、内部结构

**Go（约 4.3 万行，其中一半是生成码）**。`sdk/go/proto/openshellv1/` 生成码 20377+3457 行；手写面 `openshell/v1/` 按 client-go 子客户端模式拆域：client.go:19-31 的 `ClientInterface` 列全 12 个访问器（Sandboxes/SandboxTemplates/Providers/Services/Exec/Files/Health/SSH/TCP/Config/Policy/Workspaces）。三个特色层：`internal/converter/`（proto↔公共类型转换，sandbox.go 576 行+policy.go+network_policy.go——"Proto-generated types never appear in the public API"，sdk/go/openshell/v1/doc.go:10 的硬承诺）；`fake/`（sandbox.go 847 行全内存测试替身，deep copy 防别名，fake/sandbox.go:24-25）；doc.go 466 行的包级使用文档。分页是惰性 Pager：List 只构造不请求，NextPage 才打 RPC（sdk/go/openshell/v1/doc.go:40）。Watch 支持 `StopOnTerminal`（Ready/Error 自动关 channel，sdk/go/openshell/v1/doc.go:86-92）。

**TypeScript（手写约 3000 行）**。`client.ts`（1848 行）是 OpenShellClient 组合 SandboxClient/SandboxTemplateClient，gateway 域调用（health）留顶层；`transport.ts`（145 行）管 h2c/TLS/mTLS/拦截器；`errors.ts`（113 行）错误分类；`oidc.ts`（208 行）client credentials。技术栈 @connectrpc/connect + @bufbuild/protobuf（client.ts:18）。最别致的是**手维护枚举镜像**：proto 生成的是 protoc-gen-es 数字枚举，SDK 对外暴露小写字面量联合类型（`SandboxPhaseName = 'unspecified'|'provisioning'|...`，client.ts:77），注释明说"deliberately duplicated by hand, not generated"（client.ts:68-75）——靠 exhaustive Record 编译错误 + client.test.ts 的 drift 测试双保险防两边失同步。

**Python（手写 2700+ 行）**。`sandbox.py`（2443 行）单体：SandboxClient/SandboxTemplateClient/WorkspaceClient + Pager。Pager 带防御性预算：`_PAGER_MAX_CONSUMED_TOKENS=10_000` 与 1MiB token 历史字节上限（sandbox.py:34-35），重复 continuation token 直接抛 SandboxError（:93）——防服务端分页 bug 把客户端拖进死循环。`errors.py` 的 `GatewayError` 直接继承 `grpc.RpcError`（:32），`from_grpc_error`（:111）做翻译，`_error_mapping_channel`（sandbox.py:42 引入）是错误映射的旁路通道。`_proto/` 是生成 stub（`from ._proto import openshell_pb2_grpc`）。

**Rust 基石**。crates/openshell-sdk/src/lib.rs:4-25 两层：`OpenShellClient`（策展 MVP 面）+ `raw` 模块（直接暴露生成的 tonic client，覆盖 provider/policy/logs/settings/SSH/forwarding——"策封面没跟上的 RPC 走 raw"）。自有传输栈：TLS 物料、请求拦截器、OIDC 刷新、Cloudflare Access 隧道代理（edge_tunnel.rs）。

## 三、外部连接

全部 SDK 指向同一网关 gRPC 面（proto/openshell.proto 的 `openshell.v1.OpenShell` 服务，TLS 走 mTLS 客户端证书——TS transport.ts:24-27 注明"默认本地网关（Docker/VM/Homebrew/Linux 包）**要求**客户端证书"）。认证三式互通：静态 token、OIDC bearer（Go auth.go/auth_refresh.go、TS oidc.ts、Python ClientCredentialsAuth）、Cloudflare Access edge（TS 明说隧道 sidecar 是语言无关的 127.0.0.1 进程，header 模式直连够用时不必起）。Go/TS 的生成码来源 buf（仓根 buf.yaml + proto/）；Python 走 grpcio 生成。Rust 的 tonic 生成在 openshell-core。

## 四、数据流

以"创建并等就绪"为例（三家同构）：`Client(Config{地址+认证})` → 建传输（Go grpc.ClientConn；TS createGrpcTransport + 拦截器挂 OIDC/CF 头；Python grpc.secure_channel + TlsConfig）→ 域客户端组装请求（Go converter 把公共 SandboxSpec 转 proto；TS 直接用 MessageInitShape 生成类型；Python 手拼 openshell_pb2 消息）→ CreateSandbox RPC → WaitReady 轮询/Watch 流（Go StopOnTerminal 自动收尾；TS poll 循环在 scoped client 内）→ 错误路径统一翻译（Go errors.go IsNotFound；TS fromConnect→SdkError+errorCode；Python from_grpc_error→GatewayError）。分页契约三家一致：continuation token 惰性翻页，Go/TS Pager 薄封装，Python 多一层 token 预算防线。

## 五、设计决策

1. **"proto 类型不出公共 API"的梯度执行**：Go 最严格（converter 层 1000+ 行专职隔离）；TS 折中——复杂消息（SandboxResources 等）直接 re-export 生成类型（client.ts:52 注释"Re-export these rather than re-curating parallel surfaces"），枚举则手造镜像换 DX；Python 全手写无生成类型泄漏。三个答案对应三种语言的生态预期。
2. **错误翻译下沉到传输层**：三家都在 client 内统一拦 gRPC 错误翻译成语义错误（not_found/aborted…），调用方写业务分支不碰RpcError 细节——与 server 端 persistence_error_to_status（ABORTED 引导重试）首尾呼应。
3. **测试替身是一等公民**（Go fake 全内存、TS client.test.ts 2109 行比实现还长、Python sandbox_test.py 3027 行）——SDK 的契约稳定性靠行为测试钉住而非类型。
4. **Rust raw 逃生舱模式**：策封面永远可以落后，raw 保证能力不缺失——四张脸里只有 Rust 同时给"惯用"与"全量"两层。

## 六、新人提示

- **别在 TS 里找枚举生成对应物**：`SandboxPhaseName` 等联合类型是手维护的，proto 枚举一变必须同步改联合+NAME 映射，否则 drift 测试红。
- **Python Pager 的 token 预算不是可调配置**：是硬编码常量（sandbox.py:34-35），撞上限说明服务端分页坏了，先查网关不是调 SDK。
- **Go 的 `internal/converter` 是包路径隔离**：外部包 import 不到，新加域记得同时写 converter 双向转换与 fake 实现，漏 fake 会让下游测试编不过。
- **mTLS 是本地默认**：TS 之外两家同样要求 clientCert——连接报"需要客户端证书"先查 Config 是否带证书材料，不是网关坏了。
- **`@openshell/sdk` 与 `@nvidia/openshell-sdk` 是两个包**：前者 napi-rs 包 Rust 原生绑定，后者纯 TS——npm 搜索时别拿错。
- Cloudflare Access 的 WebSocket 隧道不在任何 SDK 里（TS transport.ts:4-7 明说），是独立 sidecar 进程。
