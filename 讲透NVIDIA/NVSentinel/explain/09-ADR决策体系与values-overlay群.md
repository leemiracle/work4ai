# 09 · ADR 决策体系与 Helm values overlay 群

## 一、角色定位

NVSentinel（K8s GPU 集群自主 SRE 平台）配置由两个平面构成：`docs/designs/` 的 ADR 体系管"为什么这么设计"，`distros/kubernetes/nvsentinel/` umbrella chart 的 values overlay 群管"部署处于什么状态"。ADR 不是死档案：ADR-050 策略样例就是 `values-npd-gpu-services.yaml` 的蓝本，ADR-055 直接点名子 chart 与 Helm 开关。

实测（修正任务书两处）：`docs/designs/` 63 个 md = 61 篇编号 ADR（缺 057/060/061 合法）+ README + template；overlay **23 个**而非 24，tilt 族 **10 个**而非 9——多出 values-tilt-mongodb-tls-disabled-percona.yaml，与另三个变体构成"标准/Percona × TLS 开/关"2×2 矩阵。

## 二、内部结构

### ADR 体系：编号、模板、索引

编号规则（README）：文件名与文内 `# ADR-NNN:` 标题一致；"取下一空闲号，**绝不复用编号**——即使原记录已撤销"（README.md:9）；编号分配制不连续、空洞是常态。每篇遵循 template.md 九节骨架，被否决方案须写明理由。

索引 59 行，瑕疵有二：**双 055 撞号**——`055-nvcre-certification-monitor.md`（README.md:71 收录）与 `055-pod-drain-policies.md`（055-pod-drain-policies.md:18）后者未入索引，违反 README.md:9 铁律，"ADR-055"引用从此歧义；**索引漏收 050**——README.md:66 收 049 后直跳 051，而 050 有 overlay 落地。

### Chart.yaml：22 依赖的 condition 矩阵

22 个依赖各绑一个 condition 键，21 个走 `global.<组件>.enabled`，唯一例外 postgresql 的非 global `postgresql.enabled`（Chart.yaml:30）。charts/ 恰 22 个子目录但目录名≠chart 名：`charts/k8s-datastore/` 声明 `name: k8sdatastore-crds`，是 ADR-027 的纯 CRD 载荷；platform-connectors 本体由 umbrella templates/ 直渲染。

### 主面板与 overlay 分类学

values.yaml global 块 22 个开关默认仅 4 个为真、全是观测类：gpuHealthMonitor（values.yaml:318-319）、syslogHealthMonitor/labeler/metadataCollector（values.yaml:337-342），动作组件全关。

23 个 overlay 逐个打开归为五族：**策略类 5**（values-remediation 修复链总闸 / values-npd-remediation NPD 通用条件 / values-npd-gpu-services ADR-050 GPU 服务 / values-nvcre 验证线 / values-preflight-kube 原生 gang scheduling）；**存储类 4**（values-postgresql.yaml:22 切 provider；DocDB/Cosmos/Atlas 三变体共享"mongodbStore 关+URI 走 Secret"骨架，差异仅在 CA：DocDB 挂私有 CA，Cosmos/Atlas 用公共 CA）；**环境类 3**（aicr-uat/aws/gcp 三份 UAT 全家桶）；**开发类 10**（tilt 族：4592 行主配置 + 9 变体）；**参考类 1**（values-full.yaml 2520 行参考文档）。

## 三、外部连接

**ADR→overlay 引用网络实测仅三篇**（grep 全 designs）：ADR-050 点名 `values-npd-remediation.yaml` 为策略载体；ADR-053 链接它并说明 NPD 策略故意不入 KOM 默认值——本仓不拥有 NPD 安装（053-npd-checks-integration.md:121-124）；ADR-039 列出需同步文件。其余 58 篇靠命名约定与 Implementation 节语义维系。

由此修正任务书："ADR-054/055 nvcre → values-nvcre.yaml"不成立——实测该文件 `nvcreCertificationMonitor` 零出现，它开的是 `global.lifecycleManager.enabled` 与 `fault-quarantine.validation.enabled`（values-nvcre.yaml:39-41），即 ADR-049 验证线；ADR-055 组件开关另行开启（055-nvcre-certification-monitor.md:31-32）。ADR-054 是组件内置指标，不落任何 overlay。

修复链血统：fault-quarantine←ADR-003、node-drainer←ADR-004/041、fault-remediation←ADR-009、janitor/janitor-provider←ADR-017 与 ADR-028（values-remediation.yaml:75 `provider: "generic"` 即其落地）。上游另接 NPD（不安装不配置，values-npd-remediation.yaml:19）、NVCRE、云托管库。umbrella 下 `policies/` 是 SBOM/SLSA 镜像准入策略，与 KOM 的 policies 同名不同物。

## 四、数据流：values-npd-remediation.yaml 完整键路径

**两层键路径**：`global.kubernetesObjectMonitor.enabled: true`（values-npd-remediation.yaml:43-44）点亮 KOM 依赖（Chart.yaml:67-69）后，`kubernetes-object-monitor.policies` 4 条策略才有消费者。每条三段式：`resource` 固定 watch core/v1 Node；`predicate.expression` CEL 匹配，如 NPDXfsShutdown 要求 `c.type == "XfsShutdown" && c.status != "False"`（values-npd-remediation.yaml:80-82）；`healthEvent` 分型：isFatal + `recommendedAction: REPLACE_VM` + errorCode。

**列表替换语义**：Helm 对列表整体替换不逐项合并，故两个 NPD overlay 都把 KOM 默认策略 ReplaceNotReadyNode（charts/kubernetes-object-monitor/values.yaml:40）抄回列表头（values-npd-remediation.yaml:48）以免被冲掉。

**分层组合**：此 overlay 只产事件，需与 values-remediation 叠加（values-npd-remediation.yaml:24-30）。叠加后链路：NPD 检测→永久 Node Condition→KOM 按 CEL 匹配→HealthEvent 到 platform-connector→fault-quarantine cordon+taint（REPLACE_VM 带 `drainOverrides.skip: true` 跳排水，values-npd-remediation.yaml:67-68）→fault-remediation 渲染维护 CR→janitor 执行。

GPU 服务线分型更细：FabricManagerDown/Flapping→`RESTART_BM`、NotInstalled→`CONTACT_SUPPORT`（无单元可重启）、PersistencedDown→非致命，分型来自 ADR-050 check inventory 表（050-gpu-system-services-npd-checks.md:83-86）。**文档与落地有差异**：ADR-050 样例 predicate 匹配 type+status+reason 三元组（050-gpu-system-services-npd-checks.md:283-286），落地版只匹配 type+status（values-npd-gpu-services.yaml:74-76）——更宽松，任何来源置 True 都触发。ADR 是蓝图、overlay 是事实。

## 五、设计决策

**ADR 只追加不改写**：README 明言决策推理"几乎无法仅从代码恢复"；取代决策保留原件、新记录声明取代；禁止改写旧记录。

**渐进信任模型**：默认只观测、动作全关。values-remediation.yaml:18-19：信任报告再叠修复层。能 cordon/驱逐/重启节点的系统默认必须只读。

**NPD 策略 opt-in**（ADR-053/050）：CSP 预装 NPD 各异、操作员可能已有修复规则；启用无对应 NPD 配置的策略是"安全但惰性"。

**单条件 monitor 拆四文件**：ADR-050——每配置文件实例化独立 monitor、状态只携带自身条件切片；四条件共用一个 monitor 的话，NPD 重启后首批发布把未探测条件按默认值广播、破坏恢复语义（050-gpu-system-services-npd-checks.md:395-406）。

**治理瑕疵如实记**：双 055 违反自家铁律；055-pod-drain 与 063 同线（063 是其增量扩展非 supersede），撞号让"ADR-055 的 pod drain 策略"永久歧义。索引漏收使 README 索引不可信。

**存储 overlay 的 CA 分型**：Cosmos/Atlas 置空 caSecretName 与 clientCertMountPath 防证书轮询循环——ADR-002 的 datastore 抽象在 overlay 层表达环境差异。

## 六、新人提示

1. **找决策先 ls 再读索引**：索引漏收 050 与 055-pod-drain，双 055 只收其一，`ls docs/designs/*.md` 才是全集。
2. **写新 ADR**：拷 template.md 骨架取下一空闲号（当前 064）；别填 057/060/061，空洞制度允许。
3. **动含列表值的 overlay 前先想合并**：带 `policies:` 的 overlay 整体替换，合并靠手工（头注释有指引）。
4. **遍历开关记两个例外**：postgresql 的 condition 不带 global 前缀（Chart.yaml:30）；k8sdatastore-crds 的 chart 名与目录名 k8s-datastore 不一致。
5. **叠加顺序即优先级**：后 `-f` 覆盖前一个同键；npd 与存储 overlay 键无交集可任意序；tilt 族以 values-tilt.yaml 为底。
6. **干跑验证**：只想看 KOM 反应不修节点，按 values-npd-remediation.yaml 文件头给策略 healthEvent 加 `processingStrategy: STORE_ONLY`。
