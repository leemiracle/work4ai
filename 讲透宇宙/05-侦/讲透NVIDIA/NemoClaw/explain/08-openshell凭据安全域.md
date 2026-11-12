# 08 · OpenShell 凭据安全域（子进程凭据审计基线 / dcode-wrapper 谓词族 / SSRF 双 BlockList）

## 一、角色定位

本篇覆盖 NemoClaw 凭据防线的三件独立武器：**①审计基线链**——`src/lib/actions/sandbox/openshell-child-visible-credentials.v*.json` 五个版本（v0.0.72/85/99/101/116）逐版本归档"OpenShell 子进程环境里哪些键以原值可见、哪些被重写、哪些是运行时控制面"；**②形状谓词族**——`agents/langchain-deepagents-code/dcode-wrapper.sh`（实测 1079 行）把"什么算秘密"做成可组合的 bash 谓词；**③SSRF 双 BlockList**——`src/lib/private-networks.ts` 与 `src/lib/security/mcp-url-target.ts` 分别在 URL 校验与 MCP 目标边界拦截私网/翻译前缀。三者共同回答：沙箱里的 agent 到底能看见什么、能把请求发到哪。

## 二、内部结构

**审计基线**：v0.0.116 基线（143 行）顶层分四桶——`rawChildValueKeys` 8 个（`:48`，如 GCP_PROJECT_ID/GOOSE_PROVIDER——原值可见但不含秘密）、`rewrittenChildValueKeys` 3 个（`:58`，GCE_METADATA_HOST/GCE_METADATA_IP/METADATA_SERVER_DETECTION——元数据服务防御性重写）、`runtimeControlKeys` 52 个（`:63`，BASH_ENV/IFS/LD_*/代理变量等运行时行为面）、`runtimeControlPrefixes` 24 个（`:117`，DEEPAGENTS_/HERMES_/NEMOCLAW_/GRPC_ 等前缀族）。**审计协议本身在演进**：v0.0.72/85/99 只有 9 个顶层字段，`generation` 块（方法名+逐源文件 sha256 证据）是 v0.0.101 才加入的——`v0.0.116.json:15` 的 `"method": "openshell-static-config-and-child-env-source-review-v1"` 即协议名（静态配置评审+子进程环境源评审），`upstreamSourceEvidence`（`:16`）为 OpenShell 三个 rust 源文件记录 gitObjectId+sha256 双锚，`nemoclawSources`（`:9`）同样钉住 NemoClaw 侧三个消费文件。方法名即审计协议——基线怎么来的、凭什么可信，全部写进数据本身。

**消费端**：`src/lib/actions/sandbox/mcp-bridge-validation.ts:30` 直接 import v0.0.116 基线；`:48` 导出 `MCP_CREDENTIAL_BOUNDARY_OPENSHELL_VERSION` 作为边界版本闸（版本不符抛专用错误并指引安装对应 OpenShell）；`:162-172` 把三桶构建成 Set/前缀数组做环境分类。同文件 `:36-37` 定义 OpenShell revisioned 凭据名两种正则：`^v[0-9]+_[A-Za-z0-9_]+$`（版本化）与 `^s[a-f0-9]{64}_[A-Za-z0-9_]+$`（sha256 稳定名）——占位符命名本身就是凭据代际协议。

**谓词族**（dcode-wrapper.sh）：核心 `is_secret_shaped_value`（`:283`）不看变量名只看值形状，一个函数串起十余个正则族：OpenAI/Anthropic `sk-proj-/sk-ant-` 与 `sk-` 长串（`:289-294`）、NVIDIA `nvapi-/nvcf-`+`ghp_/hf_/glpat-/gsk_/pypi-/tvly-`（`:295-297`）、`github_pat_`（`:298-299`）、Slack `xox[bpas]-`（`:300-302`）、AWS `A(K|S)IA[A-Z0-9]{16}`（`:306-308`）、Discord bot token 与 JWT 三段式（`:309-314`）、Linear `lsv2_`（`:322-324`）。可组合子谓词：`has_private_key_block_shape`（`:179`）、`has_bearer_secret_shape`（`:165`）、`has_context_secret_shape`（`:155`）、`has_non_slack_secret_shape`（`:192`）；上下文侧 `has_credential_name_context`（`:330`）按变量名兜底，`is_managed_token_value_for_name`（`:233`）放行 NemoClaw 自管 token，`is_openshell_env_placeholder_for_name`（`:438`）校验占位符与名字配对。拒绝出口 `refuse_secret_env/refuse_dynamic_env/refuse_invalid_openshell_placeholder/refuse_auth_store_credentials`（`:485/:493/:501/:509`）与总闸 `assert_no_secret_runtime_env`（`:516`）、`assert_no_secret_env_file`（`:551`）、`assert_no_auth_store_credentials`（`:632`）逐层设卡。脚本开局 `unset BASH_ENV ENV OPENAI_PROXY`（`:14`）并清 `NEMOCLAW_DCODE_AUTO_APPROVAL*`（`:15-18`）——自身先消毒再谈检查。

**SSRF 双 BlockList**：`mcp-url-target.ts:16` 自建 `blockedMcpTargets`，IPv4 侧 18 个网段（`:18-36`，含 100.64/10 CGNAT、169.254/16 链路本地元数据、192.0.2/24 文档段）；IPv6 侧除常规保留段外显式列 **NAT64 `64:ff9b::/96`（`:45`）与 `64:ff9b:1::/48`（`:46`）、6to4 `2002::/16`（`:54`）**，且 `:43-44` 注释指出废弃的 IPv4-compatible 编码（`::7f00:1`）能骗过纯 IPv6 检查故 `::/96` 也封。`private-networks.ts` 则从 `nemoclaw-blueprint/private-networks.yaml` 加载规范 CIDR 集，首用时建 `node:net BlockList` 并 memoize（`:4-7,41-57`）；`:80-83` 注释钉版两条 BlockList 语义：**IPv4-mapped IPv6（::ffff:a.b.c.d）BlockList 自动匹配 IPv4 规则无需显式条目；NAT64/6to4 因 BlockList 不抽取内嵌 IPv4，必须按前缀显式写进 YAML**——这就是"同一威胁两张表"的分工原因。`isLoopbackHostname`（`:137`）把 loopback 从私网语义中拆出（`:124-135` 注释：127.0.0.1 只达本机服务，不是 LAN/元数据枢轴，宿主侧 Ollama/vLLM 探测合法放行）。

## 三、外部连接

基线上游是 OpenShell rust 源（google_cloud.rs/provider_credentials.rs/secrets.rs），下游四消费者含 `hermes-portable-build-context.ts` 与 mcp-bridge-validation；升级 OpenShell 版本必须新增基线文件并切换 import。谓词族服务 dcode（Deep Agents Code）启动器，与 MCP 桥的 `resolveCredentialEnv`（mcp-bridge-validation 内）共用"值不落盘、只传名字"的约定。`private-networks.ts:26` 的 `host.openshell.internal` 桥名同时被 `mcp-url-target.ts:7-9` 的别名集（host.docker.internal/host.containers.internal）镜像，端口约束（http + 1024-65535 + 无 userinfo/search，`private-networks.ts:105-122`）是唯一放行的"私网式"目标。

## 四、数据流

OpenShell 发版 → 人工按 method 协议评审三个 rust 源 + NemoClaw 三个消费文件 → 产出带 sha256 证据链的新基线 JSON → mcp-bridge-validation 构建分类集 → 沙箱创建/凭据发布时环境变量逐键归桶（原值放行/重写/剔除）→ dcode-wrapper 启动时谓词族二次把关（名字上下文+值形状+占位符配对三通道）。URL 侧：用户输入先过 `isPrivateHostname`（含保留名+IP 字面量），DNS 解析后过窄口径 `isPrivateIp`，MCP 目标另过 `blockedMcpTargets`。

## 五、设计决策

1. **基线按上游版本归档而非就地更新**——五份 JSON 并存使任意历史沙箱的凭据面可审计、可回放。
2. **信任锚是证据不是声明**：v0.0.101 起逐文件 sha256，防止"评审过了"变成口说无凭。
3. **形状检测组合化**：单谓词各自可测，新 token 形状只加一个分支；误放行风险由 `is_managed_token_value_for_name` 白名单对冲。
4. **BlockList 语义差异写进注释即规范**：auto-match vs 前缀显式，靠 YAML 单一事实源消除两表漂移。
5. **loopback 单列**是"安全边界要贴威胁语义、不贴地址分类"的教科书案例。

## 六、新人提示

给 OpenShell 升版本时的检查单：新增 `openshell-child-visible-credentials.v<新版本>.json`（带 generation 证据块）→ 改 `mcp-bridge-validation.ts:30` 的 import → 版本闸报错文案自动跟随。读 dcode-wrapper 从 `:283` 向两端展开（子谓词在前、refuse 出口在后）。SSRF 排查先分清调用点在 pre-DNS（hostname 接口）还是 post-DNS（ip 接口），别混用。图谱注意：两份 BlockList 数据分属 TS 内嵌数组与 YAML 外部文件，imports 边看不到 YAML 依赖，得靠 `NETWORKS_FILE` 路径常量（`private-networks.ts:24`）追。
