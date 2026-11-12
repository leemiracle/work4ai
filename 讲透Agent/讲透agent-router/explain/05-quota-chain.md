# 05 · QuotaPolicy 全链：token 配额如何从 CRD 变成 Envoy 限流

## 一、角色定位

quota 是"按 token 用量限流"：不数请求数，数 LLM 消耗的 token，超额回 429。链路四层：QuotaPolicy CRD → controller 翻成 ratelimit 配置推给 xDS runner → extensionserver 在 Envoy 插限流过滤器与 descriptor 动作 → 外部 ratelimit 服务执行（token 计算见 06 篇）。两个前置事实：**QuotaPolicy 只在 v1alpha1**（api/v1alpha1/quota_policy.go:26，v1beta1 无对应物，仍是 alpha）；extensionserver 注入时直接 list QuotaPolicy（quota_ratelimit.go:137），不走 reconciler 缓存。

## 二、内部结构

**CRD（api/v1alpha1/quota_policy.go）**：TargetRefs 只许引用 AIServiceBackend（:46 CEL），跨命名空间需 ReferenceGrant。配额两层：ServiceQuota（:55）与 PerModelQuotas（:65；:90 要求匹配 BackendRef 的 ModelNameOverride）。QuotaDefinition（:99）= CostExpression（CEL，缺省 total_tokens）+ DefaultBucket + BucketRules；QuotaRule（:142）按 header 分桶，ShadowMode（:161）只记账不执行。QuotaValue（:171）= limit+duration，枚举七选一（:176）。:52 的 TODO 明言 ServiceQuota 的 descriptor 尚未设置——生效的是 per-model 线。

**controller（controller/quota_policy.go）**：`QuotaPolicyController`（:35）持 runner 与 configCache。`syncQuotaPolicy`（:155）：解析 TargetRefs（:161 先验 ReferenceGrant 再读后端）、`BuildRateLimitConfigs`（:196）、锁内更新缓存并重推 xDS（:207 防乱序）。合并 `getMergedConfigsLocked`（:295）：按名排序，同路径冲突字母序在前者优先（:290），`MergeDescriptors`（merge.go:16）按 Key+Value 递归合并，domain 固定 `ai-gateway-quota`。装配在 controller.go:255。

**ratelimit translator（translator.go）**：descriptor 树三层：backend_name（值 `{namespace}/{name}`，:55）→ model_name_override（:33）→ bucket 键（:74）。`BuildRateLimitConfigs`（:94）每后端建树，`buildPerModelDescriptorKeyed`（:210）产出 ComparableKey（:43）供跨 policy 合并。`quotaValueToPolicy`（:392）把 QuotaValue 变成 RequestsPerUnit/Unit——**token 配额被表示为"每窗口请求数"，差额由 hits_addend 扣（06 篇）**。

**xDS runner（runner.go）**：`Runner`（:39）内嵌 SnapshotCache，`Start`（:60）在 18002（:33）起 ADS gRPC，`UpdateConfigs`（:93）版本自增后 `SetSnapshot`（:123）。

**extensionserver 注入（quota_ratelimit.go）**：`maybeInjectQuotaRateLimiting`（:64）：list QuotaPolicy（:137）→ ReferenceGrant 过滤（:148）→ 建 backend→policies 映射（:187）→ 补 ratelimit cluster（:208）→ `patchRoutesWithQuotaRateLimits`（:343）给命中路由打 TypedPerFilterConfig（:578）→ 只给有配额路由的 listener 插限流过滤器（:245；名带后缀防撞，:48）。descriptor 动作从动态元数据取 backend/model（:718）；请求时 hits_addend 恒 0（:787），扣费在 stream-done 动作（:777 读 quota_cost 格式串）。

## 三、外部连接

- **controller/gateway.go**：把 CostExpression 注入 LLMRequestCosts（gateway.go:1172 的 quota_cost 键），05/06 的接缝。
- **extproc**：写 backend/model/quota_cost 进动态元数据（processor_impl.go:1053），供 descriptor 与 hits_addend 读。
- **Envoy ratelimit filter**：gRPC 到 cluster，FailureModeDeny 可配（:320）。
- **ReferenceGrant**：两层校验（:161 与 :168）。

## 四、数据流

配额生效循环：apply QuotaPolicy → reconciler 翻 descriptor 树、合并、推 xDS 快照（ratelimit 热更配额表）→ 通知路由重算（:137）→ extensionserver 下次 PostTranslateModify 插 filter、打 per-route 动作 → Envoy 收新 xDS。请求侧：请求时 filter 查 descriptor（hits_addend 0 只判旧账）；流结束后 extproc 把 cost 写进 quota_cost，stream-done 动作扣费（06 篇）。超额回 429。

## 五、设计决策

1. **token 限额复用请求数机制**：RequestsPerUnit 语义不变，用 hits_addend 把 token 数当"次数"扣——无需改 Envoy；代价是本请求的量流结束才入账（先消费后记账）。
2. **双通道一致性**：reconciler 推 xDS、extensionserver 注 filter，两边都读 apiserver，靠同一 ReferenceGrant 对齐；改配额语义须同时动两处。
3. **确定性合并**：policy 排序+ComparableKey 语义合并（translator.go:43），多 policy 命中同桶不抖动。
4. **过滤名后缀防撞**：quota filter 名带后缀（quota_ratelimit.go:48），与 Envoy Gateway 原生限流共存。

## 六、新人提示

排查：QuotaPolicy status → ratelimit 收到快照没（runner 日志 numConfigs）→ listener 有无 filter（config dump）→ 路由 TypedPerFilterConfig → 06 篇的 quota_cost 是否写出。测试：quota_policy_test.go、ratelimit/translator 表驱动、tests/e2e quota 场景。坑：modelName 必须等于 ModelNameOverride（quota_policy.go:90），写原始模型名静默不生效。
