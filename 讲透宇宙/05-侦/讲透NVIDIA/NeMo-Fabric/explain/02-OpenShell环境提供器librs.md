# 02 · OpenShell 环境提供器：为什么 lib.rs 有 3397 行

> 仓库：NVIDIA/NeMo-Fabric @ 86f86882 · environment-providers/openshell · 全仓最大单文件剖析

## 一、角色定位

OpenShell 是 NeMo Fabric 的**进程级沙箱执行面参考实现**——唯一内置的 environment provider。lib.rs:4-10 模块文档钉边界："服务私有 JSON/stdio 请求，通过 OpenShell gateway 创建、附加、检视、执行与释放沙箱；操作前验证沙箱身份与策略；提供有界沙箱 exec；**agent 运行时状态不归本提供器管**"。

与 fabric-core 是标准 client/server 配对：fabric-core 侧 crates/fabric-core/src/runtime/openshell.rs（1000 行，OpenShellRuntimeAdapter）是**调用方协调器**——模块文档（openshell.rs:4-9）明确分工："宿主把配置投影为任务局部配置、经提供器发命令、校验响应、追踪绑定与不确定操作、收集工件；gateway 与沙箱操作归提供器，任务 runtime server 与 harness 适配器在沙箱内执行"。

为什么 3397 行？拆开即答案：**主体约 2200 行 + 内联测试约 1200 行（37 个 test，L2200 起 tests 模块）**。主体容纳完整协议解析、七操作分发、沙箱身份验证、gateway 封装、错误分类——"自带全部校验与测试的单文件协议服务器"。

## 二、内部结构（带行号）

**常量防线（L27-34）**：PROTOCOL_VERSION `fabric.environment-provider.v1alpha1`（L27）是握手版本；MAX_REQUEST_BYTES 1 MiB（L28）、MAX_EXEC_OUTPUT_BYTES 3 MiB（L29）、ready 60s（L30）/delete 30s（L31）/exec 30s（L32）/gateway 30s（L33）四类默认超时，MAX_OPERATION_TIMEOUT_SECONDS 600s（L34）封顶。

**沙箱命名（L36-43）**：generated_sandbox_name 对 environment_id 做 SHA-256 取前 8 字节成 `nf-{:016x}`。注释解释约束："OpenShell 0.1.2 把 DNS 可路由沙箱名限制 19 字节，environment ID 保留在 label 用于调和时的精确身份校验"。

**stdio 主循环（L78-128）**：serve_stdio()（L78）委托泛型 serve（L83-128）——循环读一行 JSON、handle_request 处理、写回+flush，单行 NDJSON 风格。read_request_frame（L136-169）是手写流式读取器，返回三态 RequestFrame（EndOfInput/Data/Oversized，L130-134）：超限时增量 consume 不丢弃整个流，最终回 `request_too_large`（L94-98）——恶意大请求既不 OOM 也不失联。

**操作模型（L1195-1263）**：ProviderRequest 携带 protocol_version/request_id，flatten 内嵌七分支 ProviderOperation（L1204：RuntimeCommand/CollectArtifacts/Prepare/Attach/Inspect/Exec/Release）；handle_request（L171）→handle_operation（L192）两级分发。TaskCommand（L1245-1263）四分支 Check/Start/Invoke/Stop——与 fabric-core 的 task_command.rs（76 行）同一命令集，deny_unknown_fields 严格模式：适配器生命周期指令经宿主→提供器→沙箱内 runtime server 三跳。

**身份验证双闸（L1728-1778）**：SandboxBinding::from_environment 校验 provider 必须 "openshell"（L1734）、workspace/artifacts 绝对路径无反斜杠无 `..`（L1740-1749）、connection 必须带 sandbox_id/sandbox_name（L1754-1763）；verify()（L1767）每操作前比对快照——沙箱名解析到不同 id 即报 `sandbox_identity_changed`，防替换劫持。

**镜像钉版（L1691-1713）**：validate_pinned_image 只接受 `sha256:<64hex>` 本地 ID 或 `repo@sha256:<64hex>` OCI digest——浮动 tag 一律拒绝。

**Gateway 封装（L1793-2186）**：GatewayStatus/GatewayHealth 健康态（L1793-1803）；SdkGatewayFactory/SdkGateway（L1918/L1933）包装 openshell_sdk 客户端，Gateway trait 抽象使测试可注入假 gateway（37 个测试能跑全靠它）；map_sdk_error（L2186）+grpc_error_code（L2190）把 tonic gRPC 错误译进 ProviderError。

**工件脚本（read_artifacts.py，94 行）**：沙箱内一次性执行——模块文档钉限制：只读 root 下常规文件、不跟 symlink、**16 文件/单 256 KiB/总 512 KiB**（L16-18）；O_PATH|O_DIRECTORY|O_NOFOLLOW 逐级打开（L20-25）；返回 JSON 字节由宿主拷贝，"持久任务 runtime server 不参与"。

**入口薄壳（main.rs 25 行）**：只收 `serve --stdio`（main.rs:11-15），其余退出码 2；宿主 SDK 按需拉起本进程。

## 三、外部连接

- **上游调用方**：fabric-core OpenShellRuntimeAdapter（runtime/openshell.rs:21）持全局 BINDINGS 注册表（L38-40 LazyLock Mutex 双层 BTreeMap），按 gateway+workspace+sandbox_id 组 resource_key（L43-58）追踪绑定。
- **下游**：openshell_sdk（OpenShellClient/proto），经 gRPC/tonic 连 OpenShell gateway。
- **沙箱内对端**：runtime_server（SDK 命令桥，第 5 篇）收 TaskCommand 驱动 harness 适配器。
- **协议版本对**：提供器侧 `fabric.environment-provider.v1alpha1`（L27）与南向 `fabric.adapter/v1alpha2`（fabric-core adapter_contract.rs:10）是两条独立版本线。

## 四、数据流

以 Invoke 为例：宿主把 Invoke 命令装进 ProviderRequest 写到提供器 stdin → serve 读行（L91）→ 校验协议版本与请求 id → SandboxBinding 重建身份（L1734）→ SdkGateway 沙箱内执行（gateway 30s 超时）→ 沙箱内 runtime server 跑适配器 invoke → 响应沿 stdout 单行 JSON 回宿主 → decode_sdk_command_response（L363）校验 → RunResult 回消费者。Exec 分支（L1219-1235）：command 数组+workdir+env+stdin+超时，输出截 3 MiB。CollectArtifacts（L1213）触发 read_artifacts.py。

## 五、设计决策

1. **单文件巨石是刻意的**：提供器是独立部署的安全边界进程，协议/校验/gateway/错误收进一个 lib.rs 可整体审计；1200 行内联测试与实现同文件，改协议必须同步改测试。
2. **身份验证先于一切**：每操作先重建 SandboxBinding 再 verify（L1728-1778），开销换沙箱替换攻击免疫。
3. **超时矩阵全覆盖**：五级超时（L30-34）保证任何路径卡死都有上限。
4. **流式防炸**：三态读取器（L130-169）让超大请求不 OOM 且能继续回错误。
5. **工件读取用一次性脚本**：与 runtime server 解耦，沙箱内无需为收集工件开常驻端口——攻击面更小，配额硬编码在脚本内。

## 六、新人提示

- 先读 L78-128 主循环+L1195-1263 两个枚举即得协议全景；L2200 后的测试是最佳用法示例库。
- "沙箱行为怪"先查 verify()（L1767）与 ProviderError code——`sandbox_identity_changed` 通常意味 gateway 侧沙箱被重建。
- validate_pinned_image（L1691）是硬规则：本地镜像 `sha256:<id>`、远端 `repo@sha256:<digest>`，别写 `:latest`。
- 宿主侧对应物在 runtime/openshell.rs:38-40 BINDINGS——"宿主认为沙箱里有什么"读那边，"沙箱实际是什么"读本文件。
- 收集大工件失败先查 read_artifacts.py 的 16/256K/512K 限额（L16-18）。
