# 05 · policy 引擎与策略预设

对象：`src/lib/policy/index.ts`（2981 行，全仓最大单文件）、`nemoclaw-blueprint/policies/presets/`（25 个内置预设）、`src/lib/policy/trusted-private-endpoints.ts`（端点白名单能力）。

## 角色定位

策略是 NemoClaw 安全模型的数据面：一份 YAML `network_policies` 文档定义沙箱可出网的主机/端口/二进制，OpenShell 据此执行。`policy/index.ts` 是这份文档的唯一写手——preset 加载、合并、移除、并发编辑 rebase、基线排除、npm 兼容都在这一个文件里；25 个预设 YAML 是"审核过的开网配方"（github/npm/pypi/huggingface/brave/tavily/local-inference/personal-open-internet 等）；trusted-private-endpoints 则把"允许内网端点"做成进程内能力令牌而非字符串参数。

## 内部结构

引擎分四层。**加载层**：`listPresets`（index.ts:138）合并两个来源——中央预设目录（`PRESETS_DIR` :83 指向 blueprint）与 messaging 通道预设（`src/lib/messaging/channels/<channel>/policy/`）；`loadPresetForSandbox`（:406）四级回落：通道预设→内置预设→自定义预设的 live 内容；自定义预设键名强制 `nemoclaw_custom__` 前缀做命名空间隔离（:285-300）；未配置对应通道时通道预设要剥掉凭据绑定（`stripMessagingCredentialBindings` :191）。**变更层**：`PolicyMutationContext` 三函数族——`inspectPolicyMutationContext`（:761）/`preparePolicyMutationContext`（:798）/`recheckPolicyMutationContext`（:813）在每次写前后建立并复核观察上下文。**提交层**：`setPolicyDocument`（:1047）最多 `POLICY_RECONCILE_ATTEMPTS=5` 轮（:963）提交-读回-验证；并发冲突走 `rebasePolicyDocumentOntoConcurrentEdit`（:1015）三向合并：requested 等于 original 则采纳 external 的外部改动，external 等于 original 则采纳 requested，两边都改且相等采纳 requested，对象则递归合并，真冲突记入 conflicts 并让 external 胜出（`mergeConcurrentPolicyValue` :971-1013）。**兼容层**：OpenClaw npm 双键 `npm_registry`（baseline）与 `npm_yarn`（preset）（:1416-1417）——OpenShell 0.0.106 起拒绝 TLS/L7 元数据不一致的重叠端点选择器，所以 preset 激活期间用审核过的 full-access L4 端点元数据临时替换重叠的 baseline 端点、但保留 OpenClaw-only 的二进制域（:1500 注释）；`normalizePersonalOpenInternetPolicy`（:1278）要求保留键 `personal_open_internet` 与审核版深相等否则拒绝合成。

## 外部连接

82 个图谱连接使它成为"policy 引擎与策略资产"层的枢纽：动作面 `actions/sandbox/policy-channel.ts`（2437 行 CLI 层）与其 14 个专项测试（drift/baseline/conflict/lock/scope-disclosure 等）；`mcp-bridge-policy.ts` 让 MCP 桥重建时复用策略渲染；sibling 模块 `baseline-exclusion.ts`（保护键判定 :41）、`preset-provenance.ts`（来源分类 :24）、`preset-ownership.ts`、`preset-scope-render.ts`、`tiers.ts` 组成引擎的资产语义；`host-redaction.ts` 保证日志不泄主机名。预设资产被 CLAUDE.md 列为规范添加路径（"Adding a network policy preset"）。

## 数据流

应用一条预设：YAML 读入（上限 `MAX_PRESET_FILE_BYTES=10MB` :88）→ `getPresetEndpoints`（:467）用 `host:` 行正则抽出端点清单做"将要打开什么"预览 → `mergePresetIntoPolicy`（:1199）把 preset 条目合入当前策略 → `setPolicyDocument` 提交 → OpenShell 校验拒绝则带 `policySetFailure`（:907）退出 → 成功则 `verifyAppliedPolicyDocument`（:918）读回比对 → `confirmAppliedPolicySetSubmission`（:849）落定。白名单数据流：命令想放行内网端点时，先经 `findUntrustedPrivatePolicyEndpointHost`（trusted-private-endpoints.ts:161）找未授权私网主机，再由 `validateTrustedPrivatePinnedContent`（:56）校验 pin 只挂在精确端点上（出现 `allowed_ips` 即拒），校验通过才发 `TrustedPrivatePolicyPinCapability`——一个带 unique symbol 品牌的不可伪造令牌（:27-31，存 WeakMap），后续 API 只认令牌不认字符串。

## 设计决策

①**乐观并发+三向合并**：策略可被 agent 在沙箱内自改，引擎不锁整个文档而是 rebase 五轮，外部编辑优先保住用户侧改动。②**保留键防伪造**：`personal_open_internet`、`npm_yarn` 是保留键（:1421-1424），自定义 preset 不得占用，personal 键内容必须与审核版深相等（:1304-1308）。③**messaging 预设只开网不建桥**：通道 preset 仅开 provider API 出网，桥与配对在 onboard 时接线——单独 apply 会"开了防火墙却没有运行中的桥"（#1691，:462-473）。④**验证警告承载运维知识**：jira 预设的警告（:495-511）连"curl 空响应与被拦截不可区分，用 body 可见的 API 探测"这种坑都写进了产品文案。⑤**能力令牌化**：私网信任是进程内 WeakMap 令牌而非布尔参数，杜绝远端调用方传参自授。⑥**nonFatal 逃生门**：生命周期代码必须用 nonFatal 让失败回到自己的补偿逻辑，而非被 `process.exit` 抢走回滚机会（:1040-1046 doc，#9206）。

## 新人提示

加预设就是往 `nemoclaw-blueprint/policies/presets/` 放 YAML 并过 `preset-allowed-ips.test.ts` 等资产测试，不动 index.ts。读引擎建议顺序：加载层（:138-460）→ 提交环（:1047 起，抓住 context 三函数与 5 轮重试）→ 最后才是 npm 兼容这种历史包袱区（:1416 之后）。测试入口 `remove-preset-fail-closed.test.ts` 锁死"移除失败必须保守"的语义；`policy-apply-finality.test.ts` 锁提交终态。改三向合并前先写冲突用例——`mergeConcurrentPolicyValue` 的四个分支各有语义，错一个就会静默丢外部编辑。
