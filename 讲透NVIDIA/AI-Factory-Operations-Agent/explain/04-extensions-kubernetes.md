# 04 · extensions/kubernetes：双级 kubectl 工具与四条相对导入

> 文件：`helm/mosaic-stack/files/openclaw-seed/extensions/kubernetes/{index,policy,runner}.ts`（248+143+88 行）
> 图谱注：scanner 曾把 .ts 标 infra 全盲，本目录 4 条 imports 边为建图时人工核实补录

## 一、角色定位

kubernetes 插件把"读集群"与"改集群"拆成**两个工具、两份凭据、两条校验链**：

- `run_kubectl`（`kubernetes/index.ts:167-203`）：只读，白名单命令，**任何模式都不需要审批**；
- `run_kubectl_admin`（`kubernetes/index.ts:205-246`）：仅在 `editEnabled=true` 时注册，接受**精确 argv**（含 exec 进 Pod），Edit 模式审批、Auto 模式免审。

这就是 `docs/security_model.md:25` 所说"Read and write operations use separate tools and Kubernetes credentials"的代码形态。读侧凭据是 chart 的只读 ServiceAccount（RBAC 只给 get/list/watch，`security_model.md:27`），写侧是独立的 admin 凭据（默认 ClusterRole 限定资源类型，`security_model.md:29`）——**模式切换不改变凭据，凭据才是边界的地基**。

### 四条相对导入：目录内的真实依赖网

图谱建图时 scanner 对 .ts 文件的 import 提取全盲（标 infra），本目录 4 条 imports 边是人工读源码补录的，它们全部从 `index.ts` 发出（`kubernetes/index.ts:5-20`）：

1. `index.ts:5-9` → `../automation-context.ts`：导入 `contextSkipsApproval`/`requestIdentityApproval`/`sessionAccessExtension`——审批判定与模式判定全部来自单一事实源；
2. `index.ts:10` → `../mutation-ledger.ts`：导入 `runMutationOnce`——admin 请求的幂等台账；
3. `index.ts:11-19` → `./policy.ts`：导入 6 个校验函数与 2 个类型——策略层；
4. `index.ts:20` → `./runner.ts`：导入 `runKubectl`/`toolResult`——执行层。

注意 `policy.ts` 与 `runner.ts` 之间**没有边**：policy 只依赖 `node:crypto`（`policy.ts:4`），runner 只依赖 `node:child_process`（`runner.ts:4`），两者由 index.ts 编排——策略与执行互不感知，这是可以独立单测（`tests/kubernetes-policy.test.mjs` 与 `tests/kubernetes-runner.test.mjs` 各测一边）的结构性原因。

## 二、内部结构

### index.ts：策略挂载与双工具注册

`kubernetes-access` 可信策略（`kubernetes/index.ts:118-165`）先拦 **exec 回退**：`isKubectlExecFallback` 识别在通用 `exec` 工具里夹带 kubectl 的尝试（命令串或数组逐参匹配 `kubectl`/`kubectl.real`，`kubernetes/policy.ts:83-88`），直接 block 并明说"Do not retry with exec"（`index.ts:122-127`）——这是对"绕道跑 kubectl"的显式封堵，与 AGENTS.md:70 的行为纪律（"Never use general exec to run... kubectl"）形成代码+提示词双保险。

然后分工具：`run_kubectl` 过 `validateKubectlReadRequest`（`:129-131`）；`run_kubectl_admin` 过 `validateKubectlAdminRequest`，再按 `hitl`/Auto 决定审批（`:133-157`）——审批卡片由 `formatKubectlApproval` 生成（集群名 + 引号转义的完整命令 + **stdin 原文展示**，`policy.ts:32-42`；stdin 必须展示原文，因为脚本内容就是变更本体）。

`executeRequest`（`index.ts:61-108`）是执行编排：`resolveCluster` 路由集群（`:68`）；**变更请求走 `runMutationOnce`，只读直接执行**（`:79-86`）；台账 target 记 `集群名:命令`、args 只记 `{args, stdinSha256}`（`:83-84`）——stdin 原文不进台账，只留 sha256 摘要（摘要生成在 `policy.ts:114`），既保幂等判定又不把脚本全文复制进第二份持久化文件。

### policy.ts：三张表与四个校验函数

- `READ_ONLY_COMMANDS`（`policy.ts:6-8`）：10 个只读首词——api-resources/api-versions/auth/cluster-info/describe/explain/get/logs/top/version。
- `FORBIDDEN_FLAGS`（`policy.ts:9-13`）：16 个禁用长旗——**全是凭据与目标覆盖类**（--kubeconfig/--server/--token/--as/--password/--client-key/--insecure-skip-tls-verify 等）+ `--raw`；另有短旗 `-s`（`:14`）。这些旗在本插件里非法，因为**集群与身份必须由装机者选定**（`security_model.md:28`："Credential overrides remain blocked so the installer-selected cluster and identity stay authoritative"）。
- 三个正则：`SECRET_RESOURCE`（`:15`，secrets 单复数）拦 Secret 读取；`KUBECTL_COMMAND`（`:16`，含 kubectl.real 变体）供 exec 回退检测；`SHELL_SYNTAX`（`:17`，`[;&|`$<>]`）在非 admin 路径拦 shell 元字符。

`validateArgs`（`policy.ts:53-74`）的层次值得细读：数组边界（≤64、每参 ≤4096、禁控制字符）→ 非 admin 拒 shell 语法（`:60`）→ **flag 检查只查 `--` 之前**（`:63-64`——exec 的 `--` 之后是容器内命令，不是 kubectl 客户端参数，查它既越权又会误杀）→ Secret 检查豁免 `auth can-i`（`:69-72`——权限自检"我能不能读 Secret"本身合法）。

`validateKubectlReadRequest`（`:90-97`）三连：首词白名单、`auth` 只准 `can-i`（`:94`）、`cluster-info` 拒 `dump`（`:95`——dump 会把整集群配置倾倒出来）。`validateKubectlAdminRequest`（`:99-116`）放开 shell 语法与 Secret（admin 本来就要写 Secret/跑脚本），但**凭据覆盖 flag 仍拒**；exec+stdin 时 `-i`/`--stdin` 必须在 `--` 之前（`:102-108`），错误消息明示 "no command was executed"——策略层在执行前拦截。

### runner.ts：注入式凭据与统一结果

`kubectlArgv`（`runner.ts:6-18`）把 `--kubeconfig` 钉在参数最前——与 FORBIDDEN_FLAGS 拒绝用户传入的同名旗构成双保险：**凭据由代码注入，用户参数只能跟在后面**（kubectl 后出现的同名旗会覆盖前者，所以"拒绝用户传"+“代码先注入”必须同时成立）。`--server`/`--tls-server-name` 可选注入（`:14-15`）支持外部集群的地址固定。

`runKubectl`（`runner.ts:20-74`）：`KUBECONFIG` 环境变量注入（`:32`）、`shell:false`（`:33`）、stdin 按需 pipe 并 `end(stdin)`（`:34,66`）、输出限额 SIGKILL（`:55-62`）、超时 SIGKILL（`:69-72`）、**kubeconfig 路径脱敏**（`:50-51`——错误消息里的路径替换成 `<kubeconfig>`）。

`toolResult`（`runner.ts:76-88`）统一结果包装：首块是命令行 + 结构化 JSON，stdout/stderr 各自非空才附加块；`isError` 三判据——blocked / previousStatus failed / exitCode 非 0（`:84-85`）——**重放一个上次失败的请求也算 isError**，模型能感知到"这不是这次执行的错"。

### resolveCluster：多集群路由

`resolveCluster`（`policy.ts:128-143`）：未指定用 `defaultCluster`（默认 "local"，`index.ts:37`）；名字必须在 `clusters` 注册表内（`:138`）；配置兼容字符串（kubeconfig 路径）与对象（kubeconfig+server+tlsServerName）两形态（`:141`）。registry 由 chart 的 `mosaic-stack.kubernetesClusters` helper 归一（`templates/_helpers.tpl`），外部集群凭据走 kubeconfigSecretRef（`docs/examples/multitenancy/tenant-values.yaml:33-37` 即一例）。

## 三、外部连接

- **上游共享件**：automation-context（审批/模式）、mutation-ledger（幂等）——与 remote-ssh/bcm/automation-guard 同源，见第 1 篇。
- **插件清单**：`kubernetes/openclaw.plugin.json` 声明 tools 契约与 trustedToolPolicies（图谱 configures 边指向 index.ts）。
- **测试矩阵**：`tests/kubernetes-policy.test.mjs`（238 行，直接 import policy.ts 六个导出）、`tests/kubernetes-runner.test.mjs`（临时目录级 kubectl 假可执行验证）、`tests/kubernetes-kind-e2e.sh` + `kubernetes-kind-client-e2e.ts`（双集群 Kind E2E：local 与 external 两个集群，验证只读走 run_kubectl、变更走 admin 全链）。
- **行为层**：AGENTS.md:72 规定每次 Kubernetes 读都走 `run_kubectl` 并带 cluster 字段、验证返回的 cluster 与请求一致；:74 规定 `/k8s` 前缀路由；TOOLS.md:14-16 复述"run_kubectl 恒只读、恒免审批"。
- **values 链**：`docs/examples/multitenancy/tenant-values.yaml`（图谱 configures 边）→ `modules.kubernetes.enabled` + `kubernetes.clusters[].kubeconfigSecretRef` → `_helpers.tpl` 归一 → 插件配置。

## 四、数据流

Edit 模式下"给 ns mosaic 的 deployment 打标签"：

```
run_kubectl_admin {cluster:"local", args:["label","deploy","api","tier=gold","-n","mosaic"]}
  → kubernetes-access 策略：
      isKubectlExecFallback? 否（toolName 对）
      validateKubectlAdminRequest：argv 边界 ✓、-- 前无禁旗 ✓、无 stdin
      hitl=true + 非 Auto → formatKubectlApproval 生成卡片（命令全文）
      → requireApproval（timeoutBehavior: deny）
  → 批准 → executeRequest：
      resolveCluster("local") → {kubeconfig: "/var/run/.../reader-admin"}
      runMutationOnce 领号（args + 无 stdinSha256）
      runKubectl("/tools/kubectl",
        ["--kubeconfig",cfg,"label","deploy","api","tier=gold","-n","mosaic"],
        {env:{...process.env, KUBECONFIG:cfg}, shell:false})
  → {code, stdout, stderr}（kubeconfig 已脱敏）
  → toolResult（isError 由 code!==0 判）→ 台账终态 completed/failed
```

重放同一 toolCallId：领号阶段命中已有记录，直接返回 `{replayed:true, previousStatus}`（`index.ts:87-95`），**不再 spawn 进程**——网络抖动下的重试不会把标签打两遍（label 恰好幂等，但 delete/scale 不是）。

## 五、设计决策

1. **读/写分工具而非分参数**。一个带 `--dry-run` 旗的统一工具要复杂得多的策略；两个工具让"读侧零审批"成为结构属性：`run_kubectl` 的注册与审批逻辑根本不相连。
2. **凭据注入与凭据拒绝成对出现**（runner.ts:12-16 注入 + policy.ts:9-13 拒绝）。只注入不拒绝，用户旗会覆盖注入值；只拒绝不注入，凭据就要从环境泄漏。两者必须同批落地。
3. **`--` 语义感知的 flag 检查**（policy.ts:63-64）：exec 场景把参数空间切成"kubectl 客户端段"与"容器命令段"，只对前者执行客户端 flag 策略——不理解这个语义边界的实现会误杀合法 exec 命令。
4. **stdin 原文进审批卡片、只进摘要进台账**（policy.ts:32-42 vs index.ts:84）：审批人需要看全文才能批准；台账需要的是幂等性与可追溯性，不需要第二份全文。同一数据的两种消费者，两种表示。
5. **exec 回退检测放在 kubernetes 策略而不是 exec 工具**（index.ts:122-127）：只有这里知道"哪些 exec 参数是绕道"，exec 工具本身是通用沙箱，不该懂 kubernetes 语义。

## 六、新人提示

- 加新的只读命令 = 改 `READ_ONLY_COMMANDS`（policy.ts:6-8）+ 补 policy 测试；但先确认 RBAC 侧 ServiceAccount 真的有对应资源的 get/list/watch——**策略白名单是 RBAC 之上的二次限制，不是替代**（`security_model.md:31`："Auto bypasses approval, not RBAC"）。
- `validateKubectlArgs`（policy.ts:118-120）是 `validateKubectlReadRequest` 的纯 args 出口，供策略层预检复用——别在校验链里绕开它单写一份。
- 排查"为什么我的 admin 命令没跑"：按顺序查三态——策略 block（返回 blocked:true）、审批 deny/timeout（blockReason 有文案）、台账 replayed（返回 previousStatus）。三者的返回结构不同，看 `executed`/`replayed` 字段即可分辨。
- ⚠️ 甄别记录：任务简报的"双级工具"与"4 条相对导入手补"均与源码核实一致（`index.ts:5-20` 四个 import 语句逐条对应图谱四条 imports 边）；FORBIDDEN_FLAGS 源码为 **16 个长旗 + 1 个短旗 -s**（policy.ts:9-14 逐项清点），图谱 summary 的"18 个"应为合计口径差异，本文按源码分列。

（行号锚基于当前工作树源码逐条核实。）
