# 08 · agent-sandbox CRD + validation.yaml + secrets.yaml：类型层、契约层、凭据层

> 仓库：NVIDIA/AI-Factory-Operations-Agent（AFOA，Mosaic 栈的 OpenClaw 运维 agent）
> 主文件：`helm/mosaic-stack/crds/agent-sandbox.yaml`（3999 行）、`templates/validation.yaml`（342 行）、`templates/secrets.yaml`（66 行）
> 协同文件：`templates/agent-sandbox-controller.yaml`（114 行，CRD 的消费方）

## 一、角色定位

这三个文件分别是 chart 的**类型层、契约层、凭据层**，各自回答一个问题：

- `agent-sandbox.yaml`：集群里的"沙箱工作负载"长什么样？它是 vendored 的上游 CRD——`sandboxes.agents.x-k8s.io`，版权头写明 `Copyright 2025 The Kubernetes Authors`（`agent-sandbox.yaml:1`），由 controller-gen v0.19.0 生成（`agent-sandbox.yaml:9`）。AFOA 不修改它，只随 chart 分发；OpenShell 的沙箱创建（见第 07 篇的 openshell create 包装脚本）间接消费这套 API。
- `validation.yaml`：342 行**零资源输出**的 fail-fast 校验集——整个文件没有一个 `kind:`，全部是 `{{- if ... }}{{- fail "..." }}` 对（`validation.yaml:4-6` 起）。它在 `helm install/upgrade` 渲染期就把非法配置拦死，错误以 Helm 报错形态出现，而不是等 Pod 起不来再猜。
- `secrets.yaml`：三个运行时凭据 Secret（OpenClaw gateway token、诊断 agent 双 key、iraop API key），核心是一条"**显式值 → 既有值 → 随机生成**"的三层 default 链，保证升级幂等。

## 二、内部结构

### CRD：spec 四键 + status 五键 + scale 子资源

3999 行里 3900 多行是 `openAPIV3Schema` 的完整 JSON Schema 树（`agent-sandbox.yaml:24-3991`），spec 顶层只有四键：`podTemplate`（必填，`agent-sandbox.yaml:3936-3938`）、`replicas`、`shutdownTime`、`volumeClaimTemplates`——本质是"一个 StatefulSet 的 pod 模板 + 生命周期 + 存储"的最小化投影。status 侧五键：conditions（标准 K8s 条件数组，reason 带 `^[A-Za-z]([A-Za-z0-9_,:]*[A-Za-z0-9_])?$` 模式约束，`agent-sandbox.yaml:3954-3957`）、replicas（必填）、selector、service、serviceFQDN（`agent-sandbox.yaml:3940-3988`）——controller 把它创建的 Service 名与 FQDN 回写进 status，agent 拿 serviceFQDN 即可直连沙箱。

subresources 是点睛之笔（`agent-sandbox.yaml:3994-3998`）：`scale` 子资源把 `specReplicasPath: .spec.replicas`、`statusReplicasPath: .status.replicas`、`labelSelectorPath: .status.selector` 接通标准 HPA/`kubectl scale` 协议——沙箱作为 CRD 天然获得水平伸缩语义，不需要任何额外 API。

### controller：极简三件套

`agent-sandbox-controller.yaml` 在独立的 `agent-sandbox-system` Namespace 装 StatefulSet（`agent-sandbox-controller.yaml:52-73`），镜像钉 `registry.k8s.io/agent-sandbox/agent-sandbox-controller:v0.1.0`（`:73`）。ClusterRole 三组权限恰好对应 reconcile 三资源：核心组的 PVC/pod/service（`:80-93`）、CR 组的 sandboxes（`:94-105`）、以及 status 子资源（`:106-113`）。装不装由 `agentSandbox.install` 值控制且**默认 true**（`agent-sandbox-controller.yaml:5-8`）——CRD 与 controller 一起进，不拆散。

### validation.yaml：按域分段的 342 行契约

逐段清点 fail 条款：

- **llm 域**：mode 枚举 external/vllm（`validation.yaml:4-6`）；vllm 模式下 profile 只许 super-1gpu/ultra-4gpu（`:64-66`）、gpuCount/replicaCount ≥1（`:67-72`）、**`distributed` 键存在即报"已移除"**（`:73-75`，把废弃配置变成显式错误而不是静默忽略）、tensorParallelSize 必须等于 gpuCount（`:76-78`）；external 模式强制 baseUrl/model（`:55-62`）。
- **Slack/审批域**：启用即须 existingSecret + 非空 allowedUserIds（`:10-15`）；editUserIds 是三重约束——必须 Slack 启用（`:16-18`）、必须 edit 模块启用（`:19-21`）、每个审批人必须在 allowedUserIds 里（`:22-26`）。
- **Slurm/BCM 联动域**：backend=bcm 需要 BCM MCP 在位（`:38-40`）；BCM 取证必须 ssh-adapter 模式（`:41-43`）且 noCmshUser=false（`:44-46`）；vanilla Slurm 必须开证据采集器（`:47-49`）。**跨域一致性**在此成型：第 07 篇 openclaw.yaml 装配 bcm extension 用的同一个 `mosaic-stack.bcmEnabled` 判定，这里先一步把它约束住。
- **managed/external MCP 全 schema 校验**（`:83-212`）：130 行最长的段——server 名必须 DNS-1123 且 ≤30 字符（`:86-88`）、image digest 必须 `sha256:` 64 位十六进制（`:98-100`）、OAuth 启用时 port 须 <65535（`:105-107`）且 tokenUrl 必须无凭据无查询串的 HTTPS（`:108-110`）、同一 header 不许同时是字面值和 secret（`:157-159`）、toolPolicy.defaultAccess 只许 view/edit（`:164-166`）、externalMcpServers 的 URL 只许 HTTPS 或 `*.svc.cluster.local` 的 HTTP（`:187-189`）。这段与第 10 篇 mcp-oauth-proxy 的 HTTPS-only 校验（`mcp-oauth-proxy.mjs:10`）遥相呼应——**安装期与运行期各拦一道**。
- **模块依赖域**：terminal 依赖 ui+execution+kubernetes+local 集群四件（`:213-227`）；clusters 依赖 ui+execution 且至少一个 BCM/K8s 目标（`:228-254`）；edit 依赖 execution、hitl 需要 ui 或 Slack 审批人、**至少配一个后端**（`:312-314`）；diagnostics 依赖 diagnosticAgent+bcm 模块+bcmMcp 启用+ssh-adapter 四连（`:331-342`）。
- **edit.ssh 主机表逐项正则**：alias/address/user/port 四个字段各有独立 regex 与范围（`:296-310`），timeoutMs ≥1000、maxOutputBytes ≥1024（`:289-294`）。

值得注意的元设计：**这是一份"不可能配置错"清单**——所有 fail 消息都以 values 路径开头（如 `managedMcpServers.servers.%s.image.digest must be a sha256 digest`），报错即文档。342 行不产出任何资源，Helm 会把它渲染成空文档，成本只有渲染期的几毫秒。

### secrets.yaml：三层 default 链与幂等

66 行三段 Secret，每段同一骨架。以 OpenClaw gateway token 为例（`secrets.yaml:4-21`）：

```
lookup "v1" "Secret" .Release.Namespace .Values.openclaw.secrets.name   # 先查集群里已有的
→ $existingToken = 既有 Secret 里的 OPENCLAW_GATEWAY_TOKEN (b64dec)      # secrets.yaml:5-9
→ $gatewayToken = .Values 显式值 | default $existingToken | default (randAlphaNum 48)  # :10
```

三层语义：装机方显式指定 > 集群里已存在的值 > 首次安装随机生成。关键是第二层——`randAlphaNum` 每次 upgrade 都会产出新值，若没有 lookup 兜底，**每次升级 gateway token 都会换**，所有持有旧 token 的客户端全部失效。lookup 把"已生成过"变成事实上的第四种来源，这就是升级幂等。诊断 agent 段同构且更复杂：API_KEY 与 BCM_WEBHOOK_TOKEN 双 key 各自独立走链（`secrets.yaml:23-33`），并把 API_KEY 组装成 `AGENT_API_KEYS` JSON（`:43`）——一个 Secret 同时喂诊断服务端（校验调用方）与 OpenClaw（作为调用方）。research 段额外携带 NVIDIA_API_KEY/NVIDIA_CHAT_API_KEY 两个外部凭据（`:62-63`），注意它们的值直接来自 values（`:328-329` 的 validation 只在 create=true 时要求 nvidiaApiKey 非空）——**chart 生成的 Secret 里只有内部 token 是随机的，外部 API key 永远是装机方提供的明文入参**。

## 三、外部连接

- CRD ↔ OpenShell：`openclaw.yaml:381-468` 装配的 openshell CLI 在 Pod 内创建 Sandbox 资源，controller（`agent-sandbox-controller.yaml:75-113` 的 RBAC 恰好是它要 watch/patch 的面）负责把 CR 翻译成 pod+service+PVC。
- validation ↔ 消费模板：validation.yaml 里每条 fail 都对应某个模板的条件块（如 `:76-78` TP=gpuCount 对应 `vllm.yaml:50` 的 `--tensor-parallel-size` 注入；`:277-291` ssh 字段约束对应 `openclaw.yaml:165-172` 的装配）。改模板新增 values 时，这里必须补对应条款——chart 的"行为契约"由测试（第 12 篇）和这份校验双保险。
- secrets ↔ 消费方：`openclaw.yaml:525-529` 引用 OPENCLAW_GATEWAY_TOKEN、`:627-633` 引用 DIAGNOSTIC_AGENT_API_KEY、`:634-640` 引用 IRAOP_API_KEY——三段 Secret 的 key 名与消费点一一对应，改名要两边同步。
- 旁支：`runai-validation.yaml` 是同模式的域专项版（RunAI 托管 MCP 的四条 fail），`storage-validation.yaml`（tests/deployment/）则是专用 values 层叠而非校验。

## 四、数据流

**安装期**：`helm install` → validation.yaml 全量 fail 检查（任何一条不过即中止，集群零改动）→ CRD 先于模板应用（helm 对 crds/ 目录的内置次序）→ secrets.yaml 的 lookup 首次返回空 → randAlphaNum 生成 token 写入 Secret → controller StatefulSet 起，开始 watch sandboxes。

**升级期**：validation 用新 values 重新全量检查 → secrets lookup 命中既有 Secret → token 保持不变 → Deployment 因 checksum 注解滚动（见第 07 篇）。CRD 本身因 crds/ 目录的"不覆盖"策略**不会自动升级**——上游改 schema 时需要手动 `kubectl apply` 或删 CRD 重装，这是 vendored CRD 的已知代价。

## 五、设计决策

- **fail-fast 放渲染期而非 NOTES/启动期**：错误出现在 `helm install` 的 stderr 里、带着 values 路径，比"Pod CrashLoop 后翻日志"早一个数量级。342 行的投入换来的是安装支持的断崖式下降。
- **lookup 幂等链优于 `helm lookup 禁用` 论**：很多人担心 lookup 在 `helm template`/CI 干跑时返回空导致 diff 不稳，这里的取舍是运行时幂等优先——干跑时 token 显示为生成值，属可接受噪声。
- **CRD 整包 vendored 而非引用**：上游 kubernetes-sigs/agent-sandbox 的 controller 与 CRD 版本耦合（v0.1.0 配对），拆开引用反而引入版本漂移风险；代价是上游更新要手动同步。
- **Secret 不用 `data` 用 `stringData`**（`secrets.yaml:18`）：值在渲染产物里是明文、由 API server 编码——省掉模板里到处 b64enc，代价是 `helm get manifest` 能看到 token。对内网运维栈这是务实取舍。

## 六、新人提示

- 给 values 加新开关时，先问三件事：validation.yaml 要不要加条款？哪个模板的哪个条件块消费它？chart-render.test.mjs（第 12 篇）要不要加断言？三处齐了才算改完。
- `helm template` 干跑会看到 secrets.yaml 渲染出随机 token——那是 randAlphaNum 的产物，**不要**把干跑输出直接 apply。
- 查 Sandbox 沙箱状态用 `kubectl get sandbox -o wide`：status 里的 serviceFQDN（`agent-sandbox.yaml:3984-3985`）就是 agent 该连的地址。
- ⚠️ 甄别记录：任务简报"CRD 3999 行 / validation 342 行 fail-fast 契约全集 / secrets 三层 default 链幂等"与源码逐项吻合（wc -l 实测 3999/342/66）。补充核实：validation.yaml 不含 `required` 调用，全部是 `fail` 函数；`required` 形态的 fail-fast 在 seed ConfigMap（`openclaw-seed-configmap.yaml:12`）与 ingress 模板。图谱 summary 与源码一致。

（行号锚基于当前工作树源码逐条核实。）
