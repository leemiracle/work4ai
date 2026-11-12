# 09 · 凭证轮换与跨命名空间治理：rotators、tokenprovider 与 ReferenceGrant 防线

## 一、角色定位

云厂商凭证是短命的：AWS STS、Azure Entra、GCP Workload Identity Federation 换来的 token 通常一小时过期。本篇讲控制面如何让数据面永远握着有效凭证——backend_security_policy.go 按类型选轮换器，rotators/ 负责"取新凭证→写回 Secret"，tokenprovider/ 抽象 OIDC token 获取；另一半是跨命名空间治理：referencegrant.go 把 Gateway API ReferenceGrant 变成所有跨 ns 引用（后端/Secret/InferencePool/QuotaPolicy）的唯一授权通道。存在理由：轮换是安全合规硬需求，跨 ns 边界是多租户攻防面。

## 二、内部结构

**BSP reconciler**：Reconcile（backend_security_policy.go:80）→ reconcile（backend_security_policy.go:103）四步：finalizer（backend_security_policy.go:104，删除经 syncBackendSecurityPolicy :368 向受影响 backend/InferencePool 发事件传播）；requiresRotation 判定（backend_security_policy.go:108：APIKey 类不轮换）；AWS 无 file 无 OIDC 则跳过（backend_security_policy.go:114，注释：让 IRSA/Pod Identity 默认链接管）；rotateCredential（backend_security_policy.go:160）按类型构造：AWS OIDC（:164）、Azure 双路 OIDC/client-secret（:176，scope 固定 cognitiveservices :47，clientSecretRef 也过 grant :199）、GCP 三路 WIF/file/ADC（:225，ADC 让路 extproc :271）；轮换后给生成 Secret 补 ownerReference（backend_security_policy.go:288）。executeRotation（backend_security_policy.go:310）统一节拍：读上轮到期→过期则 Rotate→requeue 到"新到期-5 分钟"（:323），失败 1 分钟重试（:311）；preRotationWindow 固定 5 分钟（backend_security_policy.go:51）。

**Rotator 接口（rotators/common.go:24）**：IsExpired/GetPreRotationTime/Rotate 三方法。到期时间存 Secret 注解 `rotators/expiration-time`（common.go:19）——状态载体即存储，controller 重启零损失；生成 Secret 命名 `ai-eg-bsp-<名>`（common.go:75，前缀 :21）。

**三个 rotator**：AWSOIDCRotator.Rotate（aws_oidc_rotator.go:146）= OIDC token→STS AssumeRoleWithWebIdentity（aws_oidc_rotator.go:197）→三元组写成 AWS credentials 文件格式塞 Secret（populateSecretWithAwsIdentity aws_oidc_rotator.go:129，profile 固定 default :132）；构造器支持 `AI_GATEWAY_STS_PROXY_URL` 出网代理（aws_oidc_rotator.go:78）。azureTokenRotator.Rotate（azure_token_rotator.go:89）provider 直取，Secret 键 azureAccessToken（azure_token_rotator.go:24）。gcpOIDCTokenRotator 最长链：OIDC→GCP STS 交换（exchangeJWTForSTSToken gcp_oidc_token_rotator.go:268，调用 :192）→可选 SA impersonation（gcp_oidc_token_rotator.go:206）→写 Secret 连同 region/project（populateInSecret :234）；Rotate 注释 :171 写明四步。

**tokenprovider**：TokenExpiry 统一 token+到期（tokenprovider/token_provider.go:19）；NewOidcTokenProvider（oidc_token_provider.go:45）做 OIDC 发现（issuer/token_endpoint 校验 :67）；GetToken（oidc_token_provider.go:97）先验跨 ns client secret（:102：无 validator 时跨 ns 一律拒绝）。

**跨 ns 校验器（referencegrant.go:30）**：validateReference（referencegrant.go:171）同 ns 放行（:182），跨 ns 用字段索引查 grant（:186，索引建在 controller.go:385）；ReferenceNotPermittedError（referencegrant.go:36）的 Error() 文案（:46）把"谁引用谁、去哪建什么 grant"写得能直接抄进工单；isReferenceGrantValid（referencegrant.go:216）拒绝正在删除的 grant（:227 注释：finalizer 窗口内也必须视为已收回）；matchesTo 省略 name 即通配（referencegrant.go:297）。四个薄入口：AIServiceBackend（referencegrant.go:80）、QuotaPolicy（:93，导出版 :108 供 extensionserver 复用）、InferencePool（:130）、Secret（:157）。

**联动控制器**：ReferenceGrantController（referencegrant_controller.go:55）创建/更新/删除都按 grant 所在 ns 全量重触发（triggerAffectedReconciles :84 注释：grant 收窄后失去授权的对象不再被新 spec 描述，必须按 ns 反查）；删除经 finalizer 保证"授权收回"先于对象消失（referencegrant_controller.go:69）。secretController（secret.go:48）watch 任意 Secret，双索引反查引用它的 BSP（secret.go:66）与 MCPRoute（secret.go:81）并发事件——APIKey 轮换/更换无需用户动作。

## 三、外部连接

- **gateway.go 总装**：getBSPSecretRefData（gateway.go:1042）读静态凭证走同一 validator；bspToFilterAPIBackendAuth 读轮换产物（Azure gateway.go:970、GCP :992），token 内联进 filterconfig。
- **extproc/backendauth**：数据面只消费最终 token，不知道轮换存在。
- **状态回写**：updateBackendSecurityPolicyStatus（backend_security_policy.go:408）RetryOnConflict 写 Accepted/NotAccepted。

## 四、数据流

轮换循环：apply 带 OIDCExchangeToken 的 BSP → 构 rotator → GetPreRotationTime 读 `ai-eg-bsp-*` 注解（首跑 NotFound 视为零值即立刻轮换）→ Rotate：OIDC token→厂商交换→upsert Secret+注解到期→补 ownerRef → requeue 到到期前 5 分钟 → sync 向下游发事件 → 08 篇总装内联 token → Pod 滚动/watcher 拾取。跨 ns 拒绝流：route 引别 ns 后端且无 grant → 总装剔除该后端并记日志（gateway.go:504）→ grant 补上后 ReferenceGrantController 全量重触发，后端自动回归。

## 五、设计决策

1. **到期时间存 Secret 注解**：无内存状态、重启/leader 漂移无损；注解被改坏只会误触发一次轮换，可接受。
2. **默认链显式让路**：AWS/GCP 什么都不配时不轮换（backend_security_policy.go:114、gateway.go:942 注释连"IRSA 为何不能拒 fallback"都写了）——不配置是合法且推荐的形态。
3. **索引与读路径同构**：Secret watch 索引（controller.go:500）与 backendSecurityPolicySecretRef（controller.go:524）共用解析，OIDC 型按 BSP 自身建键，两视图不漂移。
4. **fail-closed 删除语义**：grant 删除在 finalizer 窗口即视为无授权（referencegrant.go:227），收敛快于放行。
5. **错误即文档**：ReferenceNotPermittedError 教用户建 grant；rotator 日志带 policy/类型/剩余分钟（backend_security_policy.go:326）。

## 六、新人提示

加新厂商：CRD 加类型（07 篇）→ backend_security_policy.go 分支 → rotators/ 实现三方法 → gateway.go:908 加消费分支。测试 backend_security_policy_test.go、rotators/*_test.go（mock STS/token provider）、referencegrant_test.go。排障：BSP status → `ai-eg-bsp-*` Secret 注解时间与键内容 → rotator 日志。坑三处：OIDC client secret 跨 ns 也要 grant（oidc_token_provider.go:102）；Azure 必须 clientSecretRef/OIDC 二选一（CEL backendsecurity_policy.go:236）；手删 `ai-eg-bsp-*` Secret 会立刻触发全新轮换（NotFound 视为过期），排障时是特性不是事故。
