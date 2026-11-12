# NVIDIA NemoClaw ONBOARDING

> 图谱基线：14199 节点 / 31394 边 / 16 层 / 16 步 tour / validator 0 issues / fingerprints 4071 文件 @ `ccf68dae`（2026-11-07 分析）。
> 本文行号锚全部从源码 `ccf68dae` 实核；仓内巨石文件行数（1178/1176/818/2298/2981/2423/1706/1267/847/1103/586/2077/2558/1018/3910/2508）均经 `wc -l` 复核。

---

## 1. 项目定位：OpenShell 沙箱之上的 agent 运维参考栈

NemoClaw 是 NVIDIA 开源的 **agent 工具生态参考栈**（OpenClaw 系命名），README.md:12 一句话钉死定位："open source reference stack for running supported AI agents more safely inside NVIDIA OpenShell sandboxes"。它不是 agent 本身，而是把三类 always-on agent——**OpenClaw（默认）/ Hermes / LangChain Deep Agents Code**——装进 NVIDIA OpenShell 沙箱并安全运维的整条工具链。三条产品主线：

1. **sandbox 编排**：`nemoclaw onboard` 引导式安装 → GPU 沙箱创建（docker-gpu-patch 路由）→ 生命周期（start/stop/snapshot/rebuild）。
2. **受管推理（managed inference）**：vLLM 双站（DGX Station）受管集群、NIM/Ollama/llama.cpp 宿主本地推理、profile 化的受管启动契约。
3. **维护者自动化**：maintainer 22 个 + contributor 6 个技能目录与 68 个 `.dsh` 顶层工具，把 triage/E2E/release 全流程机械化——这是一个"用 agent 维护 agent 基础设施"的仓库。

形态是 **TS 单体仓，4969 文件（fingerprints 基线 4071 个维护文件）**：根 `package.json`（name `nemoclaw` v0.1.0）声明四个 bin——`nemoclaw`（主 CLI）、`nemohermes`（Hermes 别名线）、`nemo-deepagents`（同主 CLI 换名）与 `nemoclaw-acp`/`nemoclaw-blueprint-runner`（dist 产物入口）。README.md:15-20 列出三种受支持 agent；README.md:36-38 的 express install 默认装 OpenClaw，`n` 进交互可选 Hermes/Deep Agents Code。仓级治理文件成对出现：`AGENTS.md`（19 节 AI 协作指南）与 `CLAUDE.md` 同构维护，`SECURITY.md`/`CONTRIBUTING.md`/`WRITING.md` 齐备——AI 代理是这个仓的一等公民协作者。

**边界钉版**（避免新人误解）：
- OpenShell（NVIDIA 另一仓，Rust）才是**沙箱与网关的运行时**；NemoClaw 是编排/策略/推理配置的**外部权威**，通过 CLI 子进程和 docker 驱动它。
- 策略领域 NemoClaw 只做"读取/组合增量/提交/验证存活"，OpenShell 才是策略唯一持久事实源（见 §5）。
- `nemoclaw/` 子目录是装进 OpenClaw 内的插件子包（`/nemoclaw` TUI 斜杠命令），与主 CLI 是两个 npm 工程（.agents/references/development.md:15）。

---

## 2. 架构总览：16 层地图（src/lib 域目录 × 外围资产双维）

图谱把 4969 文件切成 16 层，本质是两个维度：**L01-L14 是 src/lib 的功能域**（沿依赖方向从门面到集成），**L15-L16 是外围资产**（agent 协作资产与构建工程）。

| 层 | 主题 | 规模 | 关键内容 |
|---|---|---|---|
| L01 | 门面与 CLI 命令域 | 325 文件 | bin/ 双入口、src/commands oclif 命令树（106 个 `extends NemoClawCommand`）、src/lib/actions 非 sandbox 动作 |
| L02 | sandbox 核心域与 GPU 创建流 | 229 | run-attempt 1178 行、docker-gpu-patch 三段式、dockerfile-patch 系、base-image 解析族 |
| L03 | gateway 所有权与生命周期 | 157 | gateway-* 40 余 + docker-driver-gateway-* 40 余、gateway-ownership 529 行（#6576） |
| L04 | rebuild 子系统与断点续跑 | 166 | rebuild-pipeline 1176 + journal 818 + resume/checkpoint 群 + state/sandbox.ts 3910 行（全仓最大文件） |
| L05 | sandbox 运维动作域 | 223 | connect/destroy/doctor/exec/logs/snapshot(18)/sessions(18)/warmup 等 |
| L06 | MCP 桥与工具发现运行时 | 199 | mcp-bridge-* 76 文件三 adapter + tools/mcp-tool-discovery-runtime 独立构建 |
| L07 | onboard 编排主干与 preflight 就绪域 | 201 | preflight.ts 2298 行巨石、corporate-ca 四件、readiness 域 |
| L08 | policy 引擎与策略资产 | 111 | policy/index.ts 2981 行（全仓最大策略件）+ tiers.yaml + 25 个 preset YAML |
| L09 | inference 推理域与 vLLM 双站受管集群 | 412 | serving/ 56 文件、vllm-station-cluster 1706、nim.ts 1343 |
| L10 | runtime-provider 契约与受管工作负载状态机 | 402 | contract 847/registry 1103/activation 586 + machine/ onboard FSM |
| L11 | 核心工具箱与状态注册表 | 257 | core 工具箱、state/registry.ts 1018、onboard-session 2558 |
| L12 | 消息域 | 267 | channels/ 135 渠道实现 + applier/compiler/hooks/manifest |
| L13 | openshell 适配器与凭据安全域 | 263 | adapters/openshell 124 文件 + 凭据审计五版本演进链 |
| L14 | agent 集成与 hermes 补丁群 | 257 | agents/hermes 72 文件含 12 个 patch-*.py + 外部 agent 配方仓 |
| L15 | 双技能体系与 .dsh 工具 | 236 | .agents/skills 31 目录 + .dsh/tools 68 工具目录 |
| L16 | nemoclaw 插件子包、配置资产与构建工程群 | 400 | Dockerfile 2508 行 32 阶段、managed-inference 配置体系、npm-cache-seed 78 tgz、ci/ 23 预算文件 |

**双语言栈**（.agents/references/development.md:62-71）：`bin/` 是刻意保留的 CommonJS 启动器（`nemoclaw.js` 启动编译产物 `dist/`），主实现 `src/lib/` 全 TypeScript ESM 编译进 dist；`nemoclaw/` 插件独立 tsconfig 分域（blueprint/shared/security/commands）；`test/` 用 ESM。仓内还有大量非 TS 资产：`agents/hermes` 的 Python 补丁群与防御式 bash（start.sh）、Dockerfile 内嵌的 Python 探针、`.agents/skills` 与 `.dsh/tools` 的 markdown/shell 工具——**这是 TS 为主、五语言混编的单体**。

**依赖主干**（图谱 fanIn 最高的枢纽）：`src/lib/state/registry.ts`（沙箱注册表门面，fanIn 263）与 `src/lib/state/onboard-session.ts`（会话核心 2558 行，fanIn 198）是全局状态双枢纽；`src/lib/runner.ts`（子进程执行核心 465 行，fanIn 117）统一一切 spawn；`src/lib/agent/defs.ts`（agent 定义加载，fanIn 155）是三 agent 适配的元数据源。理解"注册表→会话→动作→适配器"这条链就看懂了大半个仓。

**最大文件榜**（新人别从这些下手，但要知道它们在哪）：`src/lib/state/sandbox.ts` 3910 行（备份/恢复，safeTarExtract 三重防线）> `src/lib/policy/index.ts` 2981 > `src/lib/onboard/managed-startup/profile.ts` 2423 > `src/lib/onboard/runtime-provider/docker-llama-cpp-managed-lifecycle.ts` 2077 > `src/lib/inference/vllm-station-cluster.ts` 1706。

---

## 3. sandbox 核心与 GPU 创建流：run-attempt 1178 行 + rebuild 双巨石

### 3.1 创建流四段：intent → plan → launch → finalization

沙箱创建的入口链在 `src/lib/onboard/` 根：`sandbox-create-plan.ts`（意图物化为计划）→ `sandbox-create-launch.ts`（发射）→ `sandbox-gpu-create.ts`/`sandbox-gpu-create-flow.ts`（GPU 全流程编排）→ `created-sandbox-finalization.ts`（收尾，重度依赖注入：CreatedSandboxCompletionDeps 声明数十个可替换协作函数）。心脏是 **`sandbox-gpu-create-run-attempt.ts`（1178 行）**，批甄别笔记对它的概括值得原文引用："创建身份的完整闭环：nonce 标签注入→创建→观察 ID→settle→发布等待→就绪身份复核→效应前验证——每个阶段失败都有分类与恢复路径"。关键函数行号锚：

- `resolveCreateAttemptNonce`（:216）——用 `node:crypto` 的 `randomBytes`（:4 import）生成创建尝试 nonce，注入 OpenShell 标签；
- `probeExactOpenShellSandboxId`（:148）——精确沙箱 ID 探测，:542 注释钉版"nonce 作为身份查询不可用时的持久恢复证据"；:703 注释"retry until one strict nonce-owned row is available"（严格 nonce 拥有的行才可用，防串沙箱）；
- `waitForCreatedOpenShellSandboxPublication`（:246）——发布等待；
- `restartInterruptedFinalHandoff`（:352）/`acknowledgeInterruptedFinalHandoff`（:378）——中断的最终交接可重启/确认（创建被打断后的断点续接）；
- `createSandboxGpuCreateAttemptRunner`（:410）——总 runner 工厂。

镜像侧的信任边界在 `src/lib/sandbox-base-image.ts`（632 行）：:156-157 解析 `image@sha256:...` 形式的 digest 钉扎，:159-161 处理 Docker 把 manifest-list digest 归一为平台 manifest digest 的情况（优先本地证明，离线回退调用方精确 ref）。蓝图侧钉版规则见仓根 CLAUDE.md "Blueprint Image Pins"：`blueprint.yaml` 的 `digest` 与 `components.sandbox.image` 必须同 SHA-256 同步更新，`test/onboarding/validate-blueprint.test.ts` 拒绝可变 tag。

### 3.2 docker-gpu-patch 三段式：给 OpenShell 容器补 GPU 路由

OpenShell 原生创建路径当年不带 GPU 直通，NemoClaw 用**克隆-重建-回滚**三段式过渡（`docker-gpu-patch-finalize.ts` 头注释自认这是 workaround，首选修复在 OpenShell 侧，并列出移除条件）：

- `docker-gpu-patch.ts`（605 行）——家族门面，re-export 54 个符号；`classifyDockerGpuPatchFailure` 在 :238/:300/:338 被三处调用，按快照+模式分类九种失败；
- `docker-gpu-patch-clone.ts`（790 行）——核心工程：把 OpenShell 创建的容器**逐字段复制成显式 docker run**，每个 inspect 字段有对应转换函数；OCI 身份元数据（uid/gid/image-user）经 env 传递并验证；
- `docker-gpu-patch-recreate.ts`（456 行）/`docker-gpu-patch-rollback.ts`（141 行）/`docker-gpu-patch-diagnostics.ts`（367 行）——重建、回滚与诊断闭环。

配 `dockerfile-patch.ts` 系按需注入 Dockerfile 补丁：corporate-ca（企业 CA）、extra-agents、hermes-context、reasoning、security、preserved-env 六类。

### 3.3 rebuild 子系统："容器可换、状态可重放"

`src/lib/actions/sandbox/` 的 rebuild-* 群（90 余文件）实现资产保护性重建。**`rebuild-pipeline.ts`（1176 行）**是总管线：`rebuildSandbox` facade（:122）在 MCP 生命周期锁内串行化类型化 phase 管线，`rebuildSandboxUnlocked`（:188）才是主体，六相调用点全可锚定——preflight :213 → backup :517 → destroy :841 → recreate :1017 → restore :749 → post-restore 验证 :759（恢复分支的重跑在 :1054/:1092）。

**`rebuild-recreate-journal.ts`（818 行）**是断点续跑的账本：`recordRebuildRecoveryBackup`（:290）写恢复记录、`readRebuildRecoveryRoute`（:425）读路由权威、`fingerprintRebuildRecreateTargetIntent`（:581）做意图指纹（:625-627 注释保留 version-1 指纹与更强指纹不兼容的兼容性边界）、`assertRebuildRecoverySource`（:642）重验权威——恢复记录无 recorded gateway authority 则拒绝（:445/:487 两处报错文本钉死这一纪律）。:232 "file authority is invalid" 是恢复文件本身的权威校验。

真正的状态搬运在 `src/lib/state/sandbox.ts`（3910 行，全仓最大文件）：manifest 驱动的备份/恢复（:4-10 头注释——用 agent manifest 的 state_dirs/configPaths 决定备份什么，从而对任何 agent 类型通用；备份剥离凭据走 credential-filter），批笔记钉版其 `safeTarExtract` 是"validate/audit/reject 三重防线"（符号链接/硬链接审计）。onboard 侧配套 `onboard-recreate-journal.ts`、`state/onboard-checkpoint.ts` 与 resume-*/checkpoint-*/cancel-rollback 群，构成"容器可换、状态可重放"的完整闭环。

---

## 4. gateway 所有权与事故模型：#6576 双权威 + preflight 巨石

### 4.1 #6576 双权威事故：ownership 529 行纯函数修复

这是全仓最好的"事故驱动架构"教材。**`gateway-ownership.ts`（529 行）**头注释（:4-27）把事故讲透：外部监督者（如平台镜像自带的 gateway 服务）拥有进程，而 NemoClaw 静默回退去启动 standalone gateway——**两层都认为自己拥有同一端口**，一个替换活监听器、另一个重启它，宿主留下持久 bind 冲突且无权威属主（:13-17）。修复原则（:18-19）：外部监督模式**永不许 standalone 回退**——要么 attach+校验，要么失败。

所有权模型三要素（全部纯函数，先决策后执行）：

1. **属主解析序**：`GatewayOwnerSource = "declared" | "packaged-service" | "standalone"`（:57）。`resolveGatewayOwner`（:141-167）：有声明（declared，:152）则声明即权威；否则回历史行为——有包管服务（packaged canonical service）用包管（:163），否则 NemoClaw 自己管 standalone（:163）——但属主现在是**显式的**而非由先跑到的代码路径隐式决定。
2. **外部监督判定**：`isExternallySupervised`（:171-172）。
3. **效果闸门**：`assertGuardLifecycleEffect`（:222-238）——每个生命周期效果前对已声明属主做守卫，外部监督属主下任何替换（包括 standalone 回退）直接报错，:238 错误文案给出修复路径（"declare mode nemoclaw-managed 把生命周期交还 NemoClaw"）。

同一事故的防御纵深散布全仓：`onboard.ts:1158`（外部/提供商拥有的 gateway 绕过 Docker 效果）、`preflight-gateway-sequence.ts:12`（属主由调用方先行解析一次）与 :62（该序列把 #6576 回归变成可端到端测试的保证）、`gateway-recovery.test.ts:333/355`（外部监督下任何恢复分支不得启动 gateway；NemoClaw 自有时恢复正常）。销毁权威另立：`gateway-teardown-authority.ts`（:5-10 头注释——rebuild/teardown/forward recovery 用精确目标权威解析；credentials add/reset 等在变更 provider 前必须重载权威），:92/:109 对持久化会话不可读/损坏/schema 版本不支持各自拒绝并指明恢复路径。

配套的 `docker-driver-gateway-*` 族 40 余文件承载 service/env/jwt-bundle/local-tls/port-listener/runtime-marker/cutover/config-auth；`gateway-binding.ts`（fanIn 59）做每端口命名迁移（历史进程级单例 `nemoclaw` → per-port `nemoclaw-<port>`，默认端口保留旧名兼容磁盘状态）与受管状态根目录 marker 防未受信注入。

### 4.2 preflight.ts 2298 行：59 函数的宿主全量评估

`src/lib/onboard/preflight.ts` 是 onboard 前的宿主体检巨石（2298 行、59 个函数，全函数 opts 依赖注入故全可测）：

- **`assessHost`（:599）**——宿主全量评估入口：WSL/容器运行时/包管理器/GPU/CDI/cgroup/资源；docker info 解析器族 `parseDockerStorageDriver`（:372）/`parseDockerUsesContainerdSnapshotter`（:383）/`parseDockerNvidiaRuntimeAvailable`（:391）/`parseDockerInfoCpus`（:403）/`parseDockerInfoMemTotalBytes`（:417）；资源判定 `isDockerUnderProvisioned`（:447）+ `checkContainerRuntimeResources`（:468）。
- **端口探测**——`probePortAvailability`（:906）与 `checkPortAvailable`（:966）：lsof 主路径（:983 `lsof -i :p -sTCP:LISTEN -P -n`），空输出不权威时升级 sudo -n lsof（:1005），:994 报出占用进程名+PID。
- **DNS 三探测**——`dnsProbeName`（:1673）、`probeContainerDns`（:1736，容器内 DNS）、`probeHostDns`（:2062，宿主 DNS；:1976 注释明说容器探测只证明 docker 网络层）、`isFatalContainerDnsProbeFailure`（:1955）/`isFatalHostDnsProbeFailure`（:2162）分级致命性。
- **环境治理**——`getMemoryInfo`（:1027）、`ensureSwap`（:1206）、`ensureProbeImageCached`（:1404，探测镜像缓存）、`isDockerDaemonUnreachable`（:1468）。

外圈配套：`fatal-runtime-preflight.ts`（致命运行时预检）、`preflight-docker-authority-conflict.ts`/`preflight-ubuntu-2604.ts`/`preflight-podman-compat.ts`（平台特判）、`corporate-ca.ts` 企业 CA 四件、`readiness-wait.ts`、`overlayfs-auto-fix.ts`、`src/lib/readiness/gateway.ts`+`sanitize.ts`。

---

## 5. policy 引擎与凭据安全：2981 行最大文件 + 五版本审计链

### 5.1 policy/index.ts 2981 行：OpenShell 是唯一持久事实源

`src/lib/policy/index.ts`（2981 行，全仓最大文件，fanIn 54 / fanOut 148）是策略引擎核心。README 钉版的原则在此落地：**OpenShell 是沙箱策略唯一持久事实源，NemoClaw 只做读取/组合增量/提交/验证存活**——所以这个引擎管的是"变更上下文"而非"策略存储"。关键锚点：

- **变更上下文三段式**：`inspectPolicyMutationContext`（:761，读前快照）→ 外部提交 → `recheckPolicyMutationContext`（:813，重检并发编辑）；`rejectFinalPolicySetSubmission`（:836）与 `confirmAppliedPolicySetSubmission`（:849）、`verifyAppliedPolicyDocument`（:918）管提交终态验证。
- **并发编辑 rebase**：`rebasePolicyDocumentOntoConcurrentEdit`（:1015）在 `setPolicyDocument`（:1047）内被调用（:1154），冲突非空即拒绝（:1160-1168）——多人/多代理同时改策略不会静默覆盖。
- **OpenClaw npm 兼容层**（:1430-1520）：`npmCompatibilityEntry`（:1430 附近）把较宽的 npm preset 与 reviewed 基线的 GET-only endpoints 组合，基线重复 selector（:1462）、无效 selector（:1456）、基线漂移（:1536-1538 "differs from the reviewed baseline"）全被拒绝——兼容层的铁律是**基线只能收紧不能放宽**。

层级与资产分离：`src/lib/policy/tiers.ts` 运行时读 `nemoclaw-blueprint/policies/tiers.yaml`（:17 起 tiers 节）——**restricted**（:18，仅基础沙箱，无三方网络）/ **balanced**（:23，开发工具+包管理+模型下载）/ **open**（:33）/ **personal**（:53）/ **open** / **personal**（personal 用单一 L4 宽授权替换 80/443 端口策略，文件头注释钉版）。preset 资产落 `nemoclaw-blueprint/policies/presets/` 25 个 YAML（github/npm/pypi/huggingface/claude-code/gmail/jira/nous-* 系等）。配套 `preset-provenance.ts`（openclaw/hermes 基线归属推断）、`preset-ownership`（防覆盖他人条目）、`host-redaction`、`trusted-private-endpoints`、actions 侧 `policy-channel` 域与 `exec-policy-hint.ts`（只读探针，不写策略）。

### 5.2 openshell 子进程凭据审计：五版本演进链 v0.0.72→116

`src/lib/actions/sandbox/` 下五个 JSON 契约夹具是**凭据治理的演进实证**：`openshell-child-visible-credentials.v0.0.72/.85/.99/.101/.116.json`。结构演进本身讲了一个收紧的故事——

- v0.0.72：只有 `sources`（OpenShell 侧上游源文件：google_cloud.rs/provider_credentials.rs）+ `rawChildValueKeys`（子进程原始可见键：GCP_PROJECT_ID/GOOSE_PROVIDER/ANTHROPIC_VERTEX_PROJECT_ID 等）+ `rewrittenChildValueKeys`（被改写的键如 GCE_METADATA_HOST）；
- v0.0.85/99：`sources` 增加 secrets.rs（上游凭据面扩大，审计跟着扩）；
- v0.0.101/116：新增 `generation` 块——`method: "openshell-static-config-and-child-env-source-review-v1"` + `upstreamSourceEvidence`（每条源文件带 gitObjectId）——**审计协议本身被版本化**，方法名即协议。

对应行为契约冻结在 `src/lib/onboard/compatible-endpoint-smoke.ts:66-74`：`OPEN_SHELL_DIRECT_POLICY_DENIAL_CONTRACT = { httpStatus: 403, error: "policy_denied", method: "POST", host: "host.openshell.internal", path: "/v1/chat/completions" }`——直连网关必须被策略拒绝，:478-487 的冒烟脚本逐字段断言该拒绝，:625-626 把契约版本与 HTTP 状态写进证据输出。**含义**：agent 永远不能绕过 policy 直连网关端口，403+policy_denied 是唯一合法响应。

宿主侧配套：`src/lib/runner.ts` 一切 spawn 走 `buildSubprocessEnv`（:29 import，:151/:232/:345 三处装配）——子进程**不继承完整父 env**，凭据按 allowlist 显式注入，runCapture 输出经 redact 消毒后返回；`src/lib/credentials/store.ts`（fanIn 70）头注释钉版"OpenShell gateway 才是凭证的 system of record，本模块一切不落盘"，只做 KNOWN_CREDENTIAL_ENV_KEYS 白名单投影与作用域覆盖解析；`src/lib/security/credential-env.ts` 以字面正则副本嵌入已审查产物、pin 脚本强制逐字一致（禁止运行时 import 未审查代码）；`src/lib/security/redact.ts`（330 行，fanIn 53）提供全文/独立秘密/URL 三级脱敏。测试侧 `gateway-domain.ts` 对齐 `test/fixtures/openshell-status-errors-v0.0.99.json`——OpenShell 结构化状态错误 kind 全量可用后应移除文本解析器（源码注释自记技术债）。

---

## 6. 受管推理域：vLLM 双站 + profile 2423 行 + runtime-provider 契约

### 6.1 serving 面：受管集群发现与适配器注册表

`src/lib/inference/serving/`（56 文件）是受管推理的门面：

- **`managed-cluster-discovery-production.ts`（1267 行）**——生产实现，安全姿态全仓最严：SSH 传输三重校验——`SAFE_SSH_KEY_TYPE_PATTERN`（:51）白名单密钥类型；解析 `ssh -G` 有效配置（:673）并断言 `stricthostkeychecking` 为 yes/true（:704）；known_hosts 逐文件查证（:762 `ssh-keygen -F`），最终探测命令统一走 `strictManagedVllmSshTransportArgs()`（:790）。
- **`adapter-registry.ts`**——三适配器注册表，版本化 ref 全部钉死：`vllm.managed-cluster/v1`（:21）、`vllm.host-local/v1`（:23）、`llama-cpp.host-local/v1`（:27）三族 materializer/lifecycle/receipt ref（:21-29），schema 常量 `nemoclaw.nvidia.com/managed-cluster-vllm-plan/v1`（:97）；:363-377 逐字段验证（host-local vLLM 必须 backend vllm + 显式选择 host-local materializer + 有效 declarative direct-install policy）。
- **`managed-cluster-discovery.ts`**——拓扑发现：/30 直连 rail 对端计算与 CX7 200Gbps 带宽/MTU 校验。
- 配套 `resolver.ts`、`vllm-station-runtime-receipt.ts`（363 行，运行时回执）、`runtime-receipt` 735 行域件、openai-validation-session、openrouter/bedrock adapter、`endpoint-ssrf-preflight.ts`。

### 6.2 vLLM 双站集群：GB300 选择与 rail 匹配

**`vllm-station-cluster.ts`（1706 行）**管理 DGX Station 双站（dual-Station）受管 vLLM：

- :431 起内嵌 Python `rail_inventory()` 探针（在目标机上枚举 GPU rail）——TS 编排 + Python 探针的混合模式；
- :731 "dual-Station connectivity requires exactly two rail requests"（双站连接必须恰好两条 rail 请求）；
- :1179 `/\bGB300\b/i` 从混合 GPU 池中筛 GB300；:1184 `ConnectX[- ]?8|\bCX-?8\b` 匹配 CX8 rail；:1186-1190 对 rdmaDevice/netdev/pciAddress/macAddress/uverbsDevice 五维去重防脏数据；:1201-1204 逐 rail 校验（含全零 MAC 拒绝）。
- 同族 `vllm-station-lifecycle-lock.ts`（launch contract 标签化 schema 迁移 + legacy head cutover 三阶段 prepare/rollback/finalize）、`vllm-station-runtime-receipt.ts`；`vllm-models.ts` 从编译期 JSON 目录装配模型清单；`nim.ts`（1343 行）管 NIM 容器（detectGpu 含 CUDA proof、spark/station/n1x/jetson 平台分类、NGC 登录、manifest digest 选择）。

### 6.3 受管启动契约：profile.ts 2423 行的"有界 schema"

`src/lib/onboard/managed-startup/profile.ts`（2423 行，63 个校验函数）是**受管启动的 profile 契约**：`MANAGED_STARTUP_PROFILE_MAX_BYTES = 64 * 1024`（:20，base64 后上限 :23-24）——schema 有界是硬约束；字段级上限 MAX_IDENTIFIER_BYTES 256 / MAX_MODEL_BYTES 1024 / MAX_URL_BYTES 2048（:26-28）。内容四大清单：能力表（:366-379 六维冻结：inferenceApis/dashboardModes/inputModalities/webSearchProviders/toolGateways/tuningFields）、供品清单、**延迟运行时输入**（:640 `deferredRuntimeInput`，:650-668 明说哪些运行时输入被刻意排除在 secret-free v1 profile 之外）、清理义务。63 个校验函数覆盖凭据形状检测/URL 凭据材料/受权 messaging 字段。**设计哲学**：受管工作负载向宿主申报能力与义务，宿主按契约验证后放行——把信任问题变成 schema 问题。

### 6.4 runtime-provider 契约/注册表/激活：可替换运行时的接缝

`src/lib/onboard/runtime-provider/` 三件套 + 引擎：

- **`contract.ts`（847 行，fanIn 90）**——类型全集：五个版本常量（:22-26，bundle/snapshot/preflight-schema/bootstrap/bootstrap-plan）；能力面类型家族 gateway/workload/lifecycle/mutation/snapshot/bootstrap/containerEngine/hostLocalInference（:28-46 起，如 `RuntimeProviderMutationOperation` :32、`RuntimeProviderContainerEngineOperation` :40）；`normalizeRuntimeProviderIdentity`（:48）。
- **`registry.ts`（1103 行，41 函数）**——逐字段验证 + 权威断言：:677（containerEngine 不得在没有 host-local-inference 权威下暴露 NVIDIA container proof）、:817-818（mutation authority 不支持该操作即拒）、:840-880（回执权威——provider 必须能证明拥有 recorded workload receipt，"could not prove ownership" :875 / "rejected the durable workload receipt" :880——畸形或 legacy 回执不能变相授权删除）。
- **`activation.ts`（586 行）**——激活白名单十维常量族（:20-61）：AGENTS/PLATFORMS/ROOT_MODES（仅 rootless）/ACCELERATION_MODES（cpu、nvidia-cdi）/INFERENCE_SERVICES（ollama、nim、vllm）/JOURNEYS/HOST_AUTHORITIES/TRANSPORTS/ENGINE_SCOPES。
- **`docker-llama-cpp-managed-lifecycle.ts`（2077 行）**——docker 驱动的 llama.cpp 受管生命周期引擎；`docker-operation-authority.ts` 把 docker 可执行身份 sha256 固定。

目标架构在 `src/lib/onboard/machine/`（126 文件）：onboard 状态机（`core-flow-phases.ts`、`handlers/provider-inference.ts` 964 行主函数、**`handlers/sandbox.ts`（2627 行）的 `SandboxStateFlow`（:615）**——:785 `decideSandboxResume` 编排创建/复用/重建三路决策，:845-847 凭据变更时强制先验证 messaging credentials 再 mutation）。

---

## 7. 双技能体系与 hermes：技能出方法，工具出动作

### 7.1 .agents/skills 31 目录：maintainer 22 + contributor 6 + 双导览

`.agents/skills/` 是仓内 AI 协作技能的标准宿主（`.claude/skills` 是指向它的 symlink，`skills/nemoclaw-user-guide/` 另有面向终端用户的一份）：

- **maintainer 22 个**（`nemoclaw-maintainer-*`）：triage / 值班三联 morning·day·evening / e2e / fix-e2e-failures / audit-e2e-assertions（CLAUDE.md 钉版为 E2E 分诊第一入口）/ policies / runtime-provider / security-code-review / release-notes / pr-comparator / cut-release-tag / validate-launchable / verify-stale / classify-ci-failure / analyze-ci-performance / analyze-pr-value-stream / cross-issue-sweep / normalize-title-tags / find-review-pr / refactor-docs。
- **contributor 6 个**：onboard（checkout 设置）/ plan-issue / implement-issue / create-pr / update-dependencies / update-docs——贡献生命周期每阶段唯一 owner（CLAUDE.md "Agent Skills" 节钉版）。
- **双导览**：`nemoclaw-skills-guide`（选技能用）与 `nemoclaw-user-guide`（终端用户文档路由）+ `_shared/`（git-github-hard-stop、pr-follow-up、documentation-writing-review 等公共契约）。

标准结构 = `SKILL.md` 入口 + `references/repo-policy·relationship-rules` 参考文件（机器可读的 label-taxonomy.json 与人类可读的 .md 双面并存）。安装由 `src/lib/skill-install.ts` 落位。技能写作受仓根 CLAUDE.md 约束：描述短而具体、条件化程序放 references、完成判据留在入口、保持 harness 无关（陈述所需能力与可观察结果，不指定工具名）。

### 7.2 .dsh/tools 68 个顶层工具：PR·CI·E2E 全流程机械化

`.dsh/tools/` 下 68 个工具目录（含 README.md/AGENTS.md 则 70 项）是技能的动作手足——**技能出方法，工具出动作**。覆盖 PR 全周期（`create_nemoclaw_pr`/`review_nemoclaw_pull_requests`/`merge_nemoclaw_pull_request`/`restack_pr_chain`）、E2E 观诊（`monitor_nemoclaw_e2e_run_group`/`e2e_root_cause_correlator`）、CI 证据（`github_actions_run_diff`/`inspect_gh_job_log`/`wait_for_nemoclaw_pr_check`）、底层执行器（`run_targeted_vitest`/`refresh_locked_npm_cache_seed`/`prepare_isolated_pr_worktree`——注意有单复数两个 worktree 工具）。审查自动化自成闭环：`audit_nemoclaw_request_changes`/`dismiss_nemoclaw_pr_reviews`/`carry_nemoclaw_cached_review_recommendations`/`finalize_nemoclaw_cached_reviews` 把"缓存审查建议→批量处置"机械化。

### 7.3 agents/hermes：12 个 patch-*.py 补丁群

`agents/hermes/`（72 文件）是 Hermes 运行时的集成与改造现场。12 个 `patch-*.py`（+1 个 `patch-langfuse-credentials.mts`）各带完整设计文档式头注释，代表案例：

- **`patch-gateway-process-identity.py`**——教 pinned Hermes gateway matcher 认识 NemoClaw 改名的入口（NemoClaw 装 `/usr/local/bin/hermes` 包装器、真入口移到 `hermes.real`，而上游只认 basename `hermes`/`hermes.exe`，导致 `hermes status` 在网关运行中报停止，#7804 见 :17）；补丁只改 entry-token allowlist，子命令语法不动，"无其他进程因此可见为 gateway"；头注释明记移除条件（上游改按内容/配置解析入口后删除）。
- **监督模式双补丁**：`patch-external-supervisor-recovery.py` + `patch-external-supervisor-restart.py`——与 §4 的 gateway 外部监督模型呼应，把外部监督语义注入 Hermes 恢复路径。
- **cron 治理双补丁**：`patch-cron-execution-runtime.py` + `patch-cron-restore-drain.py`。
- **细节修复**：`patch-hermes-sqlite-temp-store.py`（SQLite 临时存储）、`patch-mcp-http-proxy.py`（MCP 走 HTTP 代理）、`patch-profile-policy-defaults.py`、`patch-session-list-preview.py`、`patch-auxiliary-token-limit.py`、`patch-discord-recovery-permissions.py`、`patch-langfuse-credentials.mts`。

周边资产：`start.sh`（防御式 bash 典范——ensure/repair 函数全部幂等可重入，恢复用文件标记+PID 追踪跨信号存活）；`migrate-dashboard-state.py`（same_file 身份校验+预算控制+可恢复迁移记录三保险）；宿主侧 `src/lib/hermes-tool-gateway-broker.ts`（sleep 用 Atomics.wait 防忙等；控制客户端是内嵌源码字符串经 `--input-type=commonjs --eval` 执行，宿主进程不持有 socket；matrix/runtime-credentials/control-contract 被哈希校验）。外部 agent 配方仓同层：`agents/langchain-deepagents-code/`(33)/`agents/pi`(14)/`agents/openclaw`(7)。

### 7.4 MCP 桥：三 adapter + TOCTOU 补偿

`src/lib/actions/sandbox/mcp-bridge-*`（76 文件）把外部 MCP server 桥进沙箱内 agent：hermes/openclaw/deepagents 三家 adapter（`mcp-bridge-adapter-hermes.ts`/`-openclaw.ts`/`-deepagents*.ts` 8 文件）+ 全生命周期（add/remove/update/restart/migration/destroy-preflight/resolution-probe/policy-render）。契约中枢 `mcp-bridge-contracts.ts`：`MCP_BRIDGE_POLICY_SOURCE = "generated:nemoclaw-mcp-bridge"`（:6）、`McpBridgeError`（:8）、:35 "必须不留下任何 agent/OpenShell 状态的持久 NemoClaw 副本"。最值得读的是 **`mcp-bridge-provider-mutation.ts` 头注释（:4-14）——TOCTOU 补偿的完整设计文档**：OpenShell v0.0.99 服务端有 resource-version CAS，但 `provider update` 不接受调用方期望版本，另一客户端可在预检与变更间竞争；对策三重——随机 provider 名 + MCP 生命周期锁 + 不可变身份后检（credential shape/resource version 强制后检），非零变更结果一律 fail closed，"永不从后续 resource-version 增长推断成功"；注释明记待 OpenShell 暴露 CAS 后移除。消息域策略按 agent 双文件：`src/lib/messaging/channels/policy.ts` 的 `CHANNELS_ROOT`（:32）+ `POLICY_FILE_BY_AGENT`（:33-36，仅 openclaw/hermes 两种）+ :92 的路径拼接。

---

## 8. 新人上手：命令继承体系、二进制种子甄别与阅读路线

### 8.1 NemoClawCommand 继承体系：oclif 命令树的组织方式

`src/commands/` 的 106 个命令类全部 `extends NemoClawCommand`（`src/lib/cli/nemoclaw-oclif-command.ts`，265 行，fanIn 107）。基类覆写 oclif 的 `_run` 模板方法（:107）注入跨命令生命周期：portable host fence 的 read（:112-113）/deny（:117-118）两档策略、removed-immutability 迁移边界、Hermes portable 支持断言、sandbox 生命周期锁（:125 `resolveLifecycleSandboxName`）；收尾统一 `failWithLines`（:250，多行错误）与 `applyExitResult`（:255，统一退出码）。命令侧范例 `src/commands/onboard.ts`：:14 类声明、:21 `buildOnboardFlags({ includeEvents: true })` 统一 flags 供给（定义在 `src/lib/onboard/command-support.ts`）、:26-29 `--events jsonl`（:26 判定）走动态 import 包裹事件流——**flags 定义与事件流是集中治理的，命令类只做薄壳**。命令树按域展开：根命令 onboard/launch/status/doctor/setup/use/update + 子域 sandbox/（agent/channels/hosts）、credentials/、tunnel/、agents/、config/、inference/、profiles/、internal/。

### 8.2 二进制种子与生成物甄别

`tools/mcp-tool-discovery-runtime/npm-cache-seed/` 收 78 个 vendored tgz 作**离线供应链种子**（含 chai 5.2.3/6.2.2 双版本并存可见版本策略；大 tarball 以 `.tgz.part-00N` 分片入 git，`.gitattributes` 保证 text=auto 不转换）。新人甄别要点：同目录 `reviewed-runtime-bundle/*.bundle` **不是二进制**——是 esbuild 文本产物（.gitattributes 标记 -diff/linguist-generated），结构提取为空属正常；扫描器/图谱对 tgz 与 .bundle 的"空提取"不是 bug。种子刷新由 `.dsh/tools/refresh_locked_npm_cache_seed` 闭环。`tools/mcp-tool-discovery-runtime/` 本身是独立构建的 MCP 工具发现运行时（@modelcontextprotocol/sdk 1.30.0），有自己的 package.json/npm 缓存，别当主仓代码读。

### 8.3 Dockerfile 2508 行 32 阶段：供应链审查即构建

根 `Dockerfile` 是多阶段构建的极端形态：32 个 FROM / 31 个命名阶段。第一段就是供应链审查——:14 `FROM scratch AS reviewed-npm-archive`（npm 12 归档先审后用）；:16 基础镜像 digest 钉扎（`node:24.18.1-trixie-slim@sha256:ac39e4...`）；:31 `FROM npm12 AS builder`；随后按 payload 拆阶段：mcp-tool-discovery-runtime（:61）、wechat-npm-archives（:70）、codex-acp 双架构归档（:76/:80/:84）、openclaw-managed-messaging-npm-common-archives 五段（:147-519，每段约 93 行 npm 归档）与平台分流（:581/:593/:605）、openclaw payload 四件（:651/:665/:671/:687）、最终 `FROM ${BASE_IMAGE} AS openclaw-system`（:710）。外部 tarball ADD 一律带 sha256/sha512 checksum。`Dockerfile.base` 是三段式底座（SHELL 设 pipefail 防 bash 静默吞错）。`ci/` 23 个预算/例外 JSON 把架构约束变成 CI 硬闸：source-architecture-budget（源架构预算）、e2e-assertion-budget、platform-matrix、npm-audit-exceptions、coverage-threshold-cli/plugin（覆盖率棘轮——新代码不得降低 CLI/plugin 覆盖率）、dockerfile-growth-exceptions（例外文件体例=PR 号+精确上限+审批链接+移除条件）。

### 8.4 阅读路线（建议 5 步）

1. **门面（半天）**：README.md → `.agents/references/development.md`（:9-31 架构表 + :62-104 关键决策）→ `package.json` scripts → `src/commands/onboard.ts`（17-30 行）看命令薄壳模式。
2. **所有权先行（1 天）**：`gateway-ownership.ts` 全文 529 行精读（先读 :4-27 事故叙述）——它是全仓"先决策后执行"范式的最佳样本；顺带 `preflight-gateway-sequence.ts`。
3. **创建流（1-2 天）**：t02 tour 顺序——`sandbox-create-plan.ts` → `sandbox-gpu-create-run-attempt.ts`（重点 :148-410）→ `docker-gpu-patch.ts` 门面 → `created-sandbox-finalization.ts`；再进 rebuild（`rebuild-pipeline.ts` :122-188 读锁与相序）。
4. **安全域（1 天）**：`policy/index.ts` 读 :761-918 变更上下文三段式 + tiers.yaml；`compatible-endpoint-smoke.ts:66-74` 拒绝契约；`runner.ts`+`subprocess-env.ts`+`credentials/store.ts` 凭据链。
5. **按角色选深入**：推理方向走 §6（serving/ → vllm-station → profile.ts）；agent 集成走 §7（hermes 补丁群是最好的"上游约束下的工程"教材）；维护者直接用 `.agents/skills/nemoclaw-contributor-onboard` 技能 + `npm run dev:setup` / `dev:doctor`。

**上手命令**（development.md Quick Reference）：`npm run dev:setup`（checkout 设置）、`npm run test:changed`（验证变更）、`npm run validate:pr`（PR diff 验证）、`cd nemoclaw && npm run build`（插件）。注意根 `npm install` 触发 prek git hooks（hooks 失败先查 `core.hooksPath`）；`nemoclaw/` 子目录是独立 npm 工程；`.claude/skills -> ../.agents/skills` 两个路径同一内容。

**新人三大心智模型**：① **权威显式化**——gateway/policy/destroy/receipt 处处是"先解析权威、再断言、后执行"，遇到冲突宁可失败不回退；② **过渡方案自觉**——docker-gpu-patch、mcp-bridge TOCTOU 补偿、hermes 补丁群都自带移除条件注释，读注释比读代码快；③ **一切可注入**——巨石文件（preflight 59 函数、finalization deps）全函数 opts 依赖注入，测试即文档。
