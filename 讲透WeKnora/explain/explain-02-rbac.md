# explain-02 · internal/middleware/rbac.go — 四级角色 RBAC 守卫族

```
文件路径: internal/middleware/rbac.go
行数:     336 行，注释约占六成
所属层:   服务启动层（layer:api，中间件）
一句话:   Gin 中间件形态的租户 RBAC 执行点：四级角色下限、创建者豁免、平台管理员通道，外加灰度开关与懒查询。
```

## 一、角色定位

权限模型是租户内四级角色阶梯 Owner(40)/Admin(30)/Contributor(20)/Viewer(10)（数值在 types/tenant_member.go:36-46，HasPermission 即等级比较）。auth 中间件认证后把角色写进 context，本文件负责**授权执行**：把放行规则收敛成四个 middleware 工厂，路由层按端点挑选。核心矛盾：RBAC 是后上线功能，必须不清空存量部署就能灰度开启。

## 二、内部结构

**类型与哨兵**：ErrResourceNotFound（L24）、ErrOwnershipForbidden（L262）转发自 access 包；CreatorLookup（L46）是核心抽象——从 gin.Context 解析资源创建者 ID 的闭包，注释写死四态返回契约。

**四个守卫**：
1. RequireRole（L68-112）：角色下限闸。API-key 短路（L75-78，交给 APIKeyGate）→角色达标放行→跨租户超管放行（L84）→灰度关闭则记日志放行（L89-95）→否则审计+403（L103）。
2. RequireRoleOrSystemAdmin（L123-132）：角色下限+平台管理员白名单。
3. RequireSystemAdmin（L148-187）：平台级闸，**不受灰度开关控制**（L144 注释明言开关绝不能把平台端点降级成人人可调）；API key 仅 platform 策略可复用（L155-168）。
4. RequireOwnershipOrRole（L214-249）："角色达标**或**创建者"二选一，L199-213 列 8 步决策序，委托纯函数 access.CheckOwnershipOrRole，按 err 三分支收尾：放行/403/503。

**辅助**：rbacEnforcementEnabled（L256）读灰度开关；EvaluateOwnershipOrRole（L269）同决策的 handler 适配器；warnOnNilConfig（L326）用 sync.Once 对 nil config 发一次性告警——nil 会让 enforcement 永久关闭。

## 三、外部连接

import 仅 5 个：application/access（决策内核）、config、logger、types、gin。被 import：internal/router/rbac.go（13 处，L196-212 四档角色小包装、L449-465 ownership 包装）。协作：上游靠 auth 写 context；拒绝经 AuditServiceFromContext 落审计表。

## 四、数据流

"Contributor 改别人的智能体"：PUT /agent/:id→auth 写角色→RequireOwnershipOrRole(Admin, agentCreator, cfg)→20<30 且非超管→灰度关闭则标记 EnforcementSkipped 放行（**lookup 不执行，零 DB 开销**）；开启则查库取 creatorID→非 caller→审计+403。若 :id 不存在则故意放行，让 handler 返回自己的 404（L226-230），避免把"URL 写错"伪装成"权限不足"。

## 五、设计决策

**灰度安全的懒查询**：L202-205 注释点明 enforcement 关闭期 lookup 永不被调用——dormant 窗口热路径零 DB 往返，观察模式才能长期挂。**fail-closed 缺省**：角色缺失时缺省 Viewer（caller.go:17）。**错误语义保真**：403/404/503 严格区分，配 1 分钟滑窗去重审计（L99-102）。可批判处：守卫同时吃 cfg 又从 context 拿身份，测试须两处构造；双入口共享决策序，改一处须同步另一处文档。

## 六、新人提示

- 先读注释：决策序与契约全在 doc comment，代码是注释的直译。
- "403 还是 404"是刻意区分，别"顺手修复"not-found 放行。
- API key 走 APIKeyGate 通道，本文件一律短路。
- 排查"为何没拦住"：先查 EnableRBAC 与启动日志 nil config 告警。
- 延伸阅读：DeepWiki 3.5-security-and-multi-tenancy、12.1-organization-management。
