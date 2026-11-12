# 06 · security_model 与 multitenancy：三模式矩阵和多租户部署样板

> 文件：`docs/security_model.md`（74 行）、`docs/multitenancy.md`（41 行）
> 样例：`docs/examples/multitenancy/{tenant-values,tenant-reader,operator-values}.yaml`

## 一、角色定位

如果说前五篇讲的是安全机制的"实现"，这两份文档是"宪法"——它们把散在 automation-context/policy/runner 里的代码决策收拢成可向运维者承诺的模型。`security_model.md:3` 一句话立纲："AI Factory Operations Agent separates observation from mutation at the tool, credential, and session layers"（在工具、凭据、会话三层分离观察与变更），紧跟着泼冷水："**Model instructions improve tool selection, but they are not a security boundary**"——模型指令只能改善工具选择，不是安全边界。这句话是全仓的密码：AGENTS.md 里所有纪律（第 5 篇）都只是行为引导，真正的边界永远是代码层的三重闸（策略校验、凭据注入、RBAC）。

`multitenancy.md` 则回答"多人共用怎么办"：答案是**不做**单实例多用户授权，而是 operator 与 tenant 各起独立 Helm release（`multitenancy.md:3`：各自独立 UI 登录、agent 状态、审计存储、凭据）。两份文档一纵一横：前者定义单实例内的权限模型，后者定义实例间的隔离拓扑。

## 二、内部结构

### 三模式矩阵：View / Edit / Auto

`security_model.md:11-15` 的矩阵是全文核心，三行分别回答"只读工具/沙箱执行与远程诊断/基础设施变更"三类操作：

| 模式 | 只读工具 | 沙箱与远程诊断 | 基础设施变更 |
| --- | --- | --- | --- |
| View | 自动 | 自动 | 阻断 |
| Edit | 自动 | 自动 | `hitl=true` 时需审批 |
| Auto | 自动 | 自动 | 用户接受警告后免审批执行 |

四条矩阵外的钉子：

1. **默认无 Edit**：`modules.edit.enabled` 默认 false，此时"不安装 edit Kubernetes 凭据、BCM admin 工具、remote SSH 工具"（`security_model.md:7`）——工具根本不在册，不是"在册但被拦"。
2. **Edit 开了也从 View 起步**：每个新交互会话仍默认 View，模式逐会话选择（`security_model.md:9`）。
3. **自动化会话恒 View**：定时巡检与告警触发的会话"不能被改成 Edit 或 Auto"（`security_model.md:17`）——代码锚是 `automation-context.ts:6` 的 `AUTOMATION_SESSION` 正则与 `:190-196` 的恒 false 判定。
4. **Auto 的警告不是执行机制**：警告只是用户确认（user acknowledgement），真正的约束仍是"服务端会话状态、工具验证器、Kubernetes RBAC、BCM 凭据、SSH 主机表、审计记录继续生效"（`security_model.md:63`）——UI 上的"我知道了"不放松任何一层。

**矩阵的代码对应**（这是文档与前三篇的接榫处）：三模式状态机在 `automation-context.ts:148-152`（sessionAccessMode 非法值回落 view——默认安全侧）；矩阵执行在 `automation-guard/index.ts:62-102` 的 `session-access` 策略——`toolRequiresEdit` 判变更（`:70`），自动化或 `contextAllowsMutation` 为假则 block（`:76-79`），Edit+HITL 且非 Auto 转 `requireApproval`（`:95-100`，timeoutBehavior deny=**fail closed**）；Edit 的"须 HITL"与 Auto 的"免审批先警告"分别落在各插件的 hitl 配置默认值（`bcm/index.ts:148`、`remote-ssh/index.ts:34`、`kubernetes/index.ts:42`，三者默认 `hitl !== false` 即 true）。Slack 通道的双名单（`security_model.md:19`）：`allowedUserIds` 是消息白名单，`editUserIds` 更窄——**Edit 用户自批自销**（自己发起、自己按 allow/deny 按钮），代码锚 `automation-guard/index.ts:47-49`（senderId 在 editUserIds 内才给 edit 模式）与 slack-approval 的决策者校验。

### 分域边界：Kubernetes、BCM、诊断 SSH

- **Kubernetes**（`security_model.md:25-31`）：读侧 ServiceAccount 的 ClusterRole 只给 get/list/watch；admin 默认 ClusterRole 限定 8 类资源的 create/delete/patch/update + pods/exec 的 create，可用 `existingClusterRole` 替换（`:29`——管理员自定义实际行政范围）；**"Auto bypasses approval, not RBAC or request validation"**（`:31`）——Auto 只免人审，不免权限与校验。
- **BCM**（`security_model.md:33-40`）：只读身份与管理身份分离，`bcm_execute_cmsh` "never requests approval"（`:37`）；admin/note 写工具仅在 BCM edit 开启时装载，"blocked in View, approval-gated in Edit, automatic in Auto"（`:38`）；BCM 自身的 profile 凭据保持权威（`:40`）。
- **诊断与 SSH**（`security_model.md:42-57`）：本地 exec 在 OpenShell 沙箱内，"会话守卫不解析、不白名单沙箱命令"（`:44`——沙箱边界由 OpenShell 强制，两套机制不混）；View 可跑的白名单诊断由 `diagnostic-policy.ts` 逐参数校验（`:46`）；SSH 四约束（`:50-55`）：主机是装机定义的别名、身份材料来自 Helm 配置与 Secret、不接受选项与身份覆盖、命令以受验 argv 而非任意 shell 程序传输。最清醒的一句在 `:57`："**Read-only execution is not a confidentiality boundary**"——只读不是保密边界，诊断命令能读其 OS/SSH 身份允许的一切，运维者必须配最小权限身份。

### 审批与审计（`security_model.md:59-70`）

审批的三个属性：范围仅一次操作、不改会话模式（`:61`）；拒绝/过期/审批服务不可用一律 fail closed（`:61`）；审批≠成功（与 AGENTS.md:39 呼应）。审计四条（`:65-70`）：自动化会话拒一切变更工具；本地命令不属远程白名单管辖；**工具调用、审批、拒绝、结果全部入审计流**（对应第 1 篇的双台账）；Secrets 保持为 K8s Secret、只挂载进需要的工作负载，"不经 prompt 传递、不提交进 values"（`:70`）。

最后一段 Operator Responsibility（`:72-74`）把责任交还运维：开 Edit 前审查生成的 RBAC、自定义 ClusterRole、BCM profiles、SSH 主机表、挂载凭据、UI 访问面；Auto 只给"可信到无需逐操作审查"的用户。

### multitenancy：两实例、两种世界观

`multitenancy.md` 的核心表（`:7-10`）：operator 问"哪些节点不健康"（集群健康/硬件清单/网络/系统遥测），tenant 问"我的作业为什么 pending"（自己的作业/Pod/事件/日志）。**职责按受众切分，而不是按技术栈**——同一个 K8s 集群，两套实例看两个世界。

样例三件套的模块矩阵对比（租户 `tenant-values.yaml:14-26` vs 操作员 `operator-values.yaml:14-26`）：

- **共同开**：ui/execution/kubernetes；
- **tenant 关**：observability/grafana/bcm/slurm/diagnostics/research/terminal/clusters/**edit 全关**；
- **operator 加开**：observability/grafana/bcm/clusters（edit 也关——样例本身是只读运维形态）；
- **凭据路由**：tenant 的 kubernetes 段 `defaultCluster: tenant-a`、`local.enabled: false`、集群表走 `kubeconfigSecretRef: tenant-a-kubeconfig`（`tenant-values.yaml:29-37`）——本地集群读取器整体关闭，只认外部注入的租户 kubeconfig；operator 则 `local.enabled: true`（`operator-values.yaml:29-30`）。

`tenant-reader.yaml` 是租户侧最小 RBAC 三件套：ServiceAccount（**`automountServiceAccountToken: false`**，`:6`——不用集群内身份）、Role 两条规则——core 组的 pods/pods/log/events 与 batch 组的 jobs/cronjobs，**verbs 一律 get/list/watch**（`:13-19`）、RoleBinding 绑定（`:21-33`）。整个文件没有一个写动词。

两条安全警告（`multitenancy.md:37-41`）值得原文级铭记：其一，"**The chart's default Kubernetes reader is cluster-wide, even when installed in a tenant namespace; keep it disabled for tenants**"（`:39`）——chart 默认读取器是集群级的，装在租户命名空间里也一样能看到全集群，租户必须关掉默认读取器（这正是 tenant-values 里 `local.enabled:false` 的原因）；其二，"**These are separate deployments, not per-user authorization in a shared UI**"（`:41`）——这是部署级隔离，不是共享 UI 里的按用户授权；namespace 分离不构成隔离，须认证 ingress 与网络策略（`:41`）；管理员与运行时控制器仍受信，互相不信任的租户要用独立集群或 VM。

交接验收（`multitenancy.md:39`）：拿租户 kubeconfig 验证 `tenant-a` 内作业与日志可读、其他命名空间/节点/Secrets/作业变更全拒——**边界要用实测证伪，不能靠配置推断**。

## 三、外部连接

- **上游代码**：三模式矩阵的每一格都能落到 `automation-context.ts` 的判定函数（见上）；`modules.edit.*` values 经 chart 模板同时驱动插件注册（`kubernetes/index.ts:205` 的 `if (settings.editEnabled)`）与 AGENTS.md 渲染分支（`AGENTS.md:29`）——**配置、代码、提示词三处在同一开关下联动**。
- **multitenancy 样例 → kubernetes 插件**：图谱 configures 边 `tenant-values.yaml → kubernetes/index.ts`——租户 values 的 clusters 表就是 `resolveCluster`（`kubernetes/policy.ts:128-143`）注册表的数据源。
- **bcm.md / installation.md**：operator-values 的 bcm 段（`operator-values.yaml:38-42`：mode ssh-adapter + headHost + hostSshKeySecretName）展开在 `docs/bcm.md`（无 K8s 的 BCM 头节点经 SSH 适配）。
- **第 5 篇的 AGENTS.md:33**：三模式的 agent 侧行为纪律（View 解释方案不动手、Edit 立即调工具触发审批 UI、Auto 直接执行）与本篇矩阵逐格对应。

## 四、数据流

一次多租户部署的权限装配流：

```
operator 侧：
  helm upgrade --install mosaic-operator ... -f operator-values.yaml -n mosaic-operator
  → 模块 ui/execution/kubernetes/observability/grafana/bcm/clusters 开
  → AGENTS.md 渲染：edit=false → "Read-only Mode" 节
  → 凭据：mosaic-grafana-auth(basic) + bcm-host-ssh-key(ssh 私钥) 两个 Secret

tenant 侧：
  kubectl apply -f tenant-reader.yaml -n tenant-a     ← Role 仅 get/list/watch
  制作 kubeconfig（引用该 SA）→ Secret tenant-a-kubeconfig -n mosaic-tenant-a
  helm upgrade --install mosaic-tenant-a ... -f tenant-values.yaml -n mosaic-tenant-a
  → local 集群读取器关闭；run_kubectl 只见 resolveCluster 注册的 tenant-a
  → agent 每次只读调用：kubectlArgv 注入租户 kubeconfig → RBAC 兜底
```

租户实例里的 agent 即便被提示注入诱导"看看别的命名空间"，三层都会拦：策略层（run_kubectl 白名单不含 namespaces 跨查的动机也无法传凭据旗）、凭据层（kubeconfig 由代码注入）、RBAC 层（Role 只授权 tenant-a 的 get/list/watch）——这正是"模型指令不是安全边界"的正面示范。

## 五、设计决策

1. **承诺写在文档、强制写在代码**。文档矩阵若没有 `automation-guard/index.ts:62-102` 的策略兜底就是空文；本仓的纪律是每个安全断言双向可溯——文档找得到代码锚，代码注释引用文档语义。
2. **默认缺装（absent by default）而非默认拦截**。edit 关闭时工具不装载（`security_model.md:7`）——攻击面直接不存在，而不是存在但守着。"能拆掉的门比锁着的门更安全。"
3. **Auto 的警告是 UX 不是边界**（`security_model.md:63`）：把"用户确认知情"与"权限强制"分层，警告可以换肤，强制层不动。
4. **租户隔离选部署级而非授权级**：单实例按用户授权要解决共享 UI 的会话隔离、审计归属、凭据路由三大难题；两个 release 天然各管各的。代价是多实例运维——AFOA 明确认为这代价更便宜。
5. **默认读取器集群级是个坑，样例负责显式填坑**：tenant-values 的 `local.enabled:false` 不是可选项而是必选项，文档用加粗警告+验收步骤双保险（`multitenancy.md:39`）——知道坑还不够，要给出可执行的验证。

## 六、新人提示

- 读 `security_model.md` 的正确顺序：先 `:3` 的三层分离命题 → `:11-15` 矩阵 → `:31` 的 RBAC 权威句 → `:57` 的保密边界句，四句撑起全文；其余是分域展开。
- 评估"要不要开 Edit/Auto"时逐项过 `:72-74` 的清单（RBAC/ClusterRole/BCM profiles/SSH 主机表/挂载凭据/UI 访问面）——开 Edit 是扩张授权面，不是打开开关。
- tenant-values.yaml 几乎每个 `enabled: false` 都是一次安全决策的化石：observability 关（不该看全局指标）、bcm 关（不该碰硬件）、clusters 关（不该发现别的集群）——裁模块就是裁视野。
- `automountServiceAccountToken: false`（`tenant-reader.yaml:6`）常被漏抄：租户 kubeconfig 是外部注入的身份，Pod 内不需要自动挂载集群令牌，挂着反而多一条泄漏路径。
- ⚠️ 甄别记录：任务简报"Edit 须 HITL/Auto 免审批先警告"与 `security_model.md:14-15` 逐字吻合；"tenant-reader 仅 get/list/watch"与 `tenant-reader.yaml:16,19` 一致；"operator/tenant 模块矩阵"经两份 values 逐行核实（共同开 ui/execution/kubernetes，tenant 全关基础设施模块）。图谱 summary 与源码/文档无冲突。

（行号锚基于当前工作树源码逐条核实。）
