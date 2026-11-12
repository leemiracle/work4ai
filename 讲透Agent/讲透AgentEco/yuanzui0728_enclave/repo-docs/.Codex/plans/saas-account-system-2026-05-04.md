# 隐界 SaaS 账号与订阅体系实施规划（基于现有代码补齐闭环）

## Summary
- 不重做 `apps/cloud-api` 里已经存在的 `users / subscription / invite / cloud-config` 基建；本次重点是把它们和 `apps/app`、`api`、`apps/cloud-console` 真正串成完整 SaaS 闭环。
- SaaS v1 口径固定为：`1 个云账号 = 1 个云世界`、手机号验证码登录、7 天试用、49.9/月 / 139.9/季 / 499/年、邀请成功送邀请人 30 天、会员到期仅禁 AI 能力、支付先走手动开通。
- 生产环境收口为云登录入口；本地世界仅保留开发/内部环境。老用户补建 SaaS 账号时，默认补送 30 天迁移会员。

## Key Changes
### 1. Cloud API 与 Contracts
- 以现有 `cloud_users / subscription_plans / user_subscriptions / invite_* / cloud_configs` 为准，不再重建模型；只补齐缺口。
- 统一云后台管理路由前缀到 `/admin/cloud/*`，把当前新加的 `cloud/admin/*` 控制器改到与现有 `cloud-console` 一致；客户端接口仍保持 `/cloud/me/*`，服务间接口保持 `/cloud/internal/*`。
- 在 `packages/contracts` 增加完整 SaaS 客户端方法：
  - 客户端：`getMyCloudProfile`、`getMySubscription`、`getMyInviteSummary`、`redeemInvite`、`createCheckout`
  - 管理端：`listCloudUsers`、`getCloudUser`、`grantSubscription`、`banUser`、`unbanUser`、`listSubscriptionPlans`、`upsertSubscriptionPlan`、`listCloudConfigs`、`upsertCloudConfig`、`listInviteRedemptions`、`rejectInviteRedemption`
- 改造 `packages/contracts/src/client.ts` 的请求错误模型，新增结构化 `ApiRequestError`，保留 `statusCode / errorCode / message / meta / requestId`，不能再只抛纯字符串 `Error(message)`。
- 在 cloud-api 强制执行账号状态：
  - `banned` 用户禁止验证码登录后继续解析世界、禁止访问 `cloud/me/*`
  - `archived` 视为不可继续使用的停用账号
- 增加一个幂等的老用户补建脚本/命令：从现有 `CloudWorld.phone` 回填缺失的 `cloud_users`、邀请码，并发放 30 天迁移会员；使用现有 `admin_grant` source，统一 note 标记，不新增订阅 source。
- 补齐世界实例环境注入：`CLOUD_OWNER_PHONE`、`CLOUD_API_BASE_URL`、`CLOUD_SERVICE_TOKEN` 在云端 provision/resume 世界时写入实例环境，作为 World API 订阅回查唯一来源。

### 2. 主 App 账号层与会话层
- 新增独立 `cloud-session-store`，保存云端 access token、expiresAt、phone、profile 摘要；不要复用 `world-owner-store` 或仅靠 `runtime-config`。
- 存储策略固定：
  - iOS / Android 用现有 `native-secure-storage`
  - Web / Desktop 用独立持久化存储
- 重写启动链路：
  - `splash-page.tsx` 先校验 cloud session，再决定是否允许自动回到云世界
  - 若 session 缺失或过期，清空 `runtime-config` 里的云世界连接信息和 `world-owner-store`，强制回 `/welcome`
- `welcome-page.tsx` 继续沿用现有手机号登录链路，但补上：
  - `?invite=` 持久化
  - `inviteCode + deviceFingerprint` 透传验证
  - 登录成功后保存 cloud session
  - 生产环境隐藏本地世界入口，开发/内部环境通过构建开关保留
- 新增登出能力：从资料/设置页清除 cloud session、world runtime config、world owner store，并回到欢迎页。
- 新增统一会员页，路由固定为 `/profile/subscription`：
  - 显示手机号、会员状态、到期时间、当前套餐
  - 显示后台配置的月/季/年套餐价格与文案
  - 显示邀请码、邀请链接、累计奖励、最近邀请记录
  - 点击续费仅走手动 checkout 提示与运营联系方式
- 在 `profile-page.tsx` / `profile-settings-page.tsx` 增加“会员中心”“退出登录”入口。

### 3. World API AI 权限拦截
- `api/src/modules/subscription/` 已有本地草稿，实施时以它为起点审核并接入，不盲目重写。
- 在 `api/src/app.module.ts` 注册 `SubscriptionModule`，在 `AiModule` 注入 `SubscriptionService`，注册全局 `SubscriptionExpiredFilter`。
- `ai-orchestrator.service.ts` 的 11 个 AI 公开入口全部首行调用 `assertCanUseAi(feature)`；只拦 AI，不拦历史浏览和普通非 AI 页面读取。
- WebSocket 不再只下发纯文本错误：
  - 扩展 `packages/contracts/src/ws.ts` 的 `ChatErrorPayload`，支持 `code` 和 `meta`
  - 继续复用现有 `error` 事件，不新增新事件名
  - 前台聊天 hook 收到 `SUBSCRIPTION_EXPIRED` 时，直接打开统一到期弹窗
- HTTP 侧也统一使用 `ApiRequestError` 里的 `code/meta` 打开同一弹窗，保证 REST / WS 两条链路表现一致。
- 到期弹窗 CTA 固定跳 `/profile/subscription`。

### 4. Cloud Console 后台
- 在 `apps/cloud-console` 新增 5 个 SaaS 页面：`Users`、`User Detail`、`Plans`、`Configs`、`Invite Audit`。
- `Users`：手机号、账号状态、订阅状态、到期时间、邀请人、关联世界状态，支持筛选和分页。
- `User Detail`：订阅历史、邀请历史、关联世界链接，支持手动赠送会员、封禁/解封。
- `Plans`：管理 trial / monthly / quarterly / yearly / invite_reward 的价格、时长、启用状态、公开购买状态、排序、文案。
- `Configs`：管理 `trial.* / invite.* / feature.* / copy.* / app.publicBaseUrl`。
- `Invite Audit`：查看兑换记录、IP/设备指纹风控信息、撤销奖励。
- 手动支付 v1 不新增支付网关、不做回调编排；后台“赠送订阅”就是实际履约入口。

### 5. Migration 与文档
- 结构变更落地时同步更新 `AGENTS.md` 的路由、模块、实体、接口清单。
- 实施开始时把本规划落盘到 `.Codex/plans/saas-account-system-2026-05-04.md`。
- 推荐实施顺序：
  1. contracts + cloud-api 路由/错误模型对齐
  2. App cloud session 与登录启动链路
  3. World API AI 拦截接入
  4. Cloud Console 用户/订阅/配置页面
  5. 老用户 backfill 与生产 SaaS 开关切换

## Test Plan
- Cloud API：
  - 验证码登录自动创建 `cloud_user`、发 7 天 trial
  - 新用户带邀请码时邀请人立即 +30 天
  - 同 IP / 同设备连续注册命中风控后记录为 rejected
  - banned 用户无法继续登录/解析世界
  - `/admin/cloud/users`、`/admin/cloud/subscription-plans`、`/admin/cloud/configs`、`/admin/cloud/invites/redemptions` 全部可用
  - 老用户 backfill 可重复执行且不重复发放迁移权益
- 主 App：
  - 有效 cloud session 重启后仍可进入云世界
  - cloud session 过期后重启会被送回 `/welcome`
  - 生产环境看不到本地世界入口
  - `/profile/subscription` 能正确显示后台改过的价格、文案、邀请信息
  - 登出后清空世界入口与账号态
- World API：
  - 文本、图片、音频三类 AI 各抽一条链路验证 402 `SUBSCRIPTION_EXPIRED`
  - websocket 聊天触发到期时收到结构化 error payload，并弹出会员到期弹窗
- Cloud Console：
  - 用户筛选、赠送会员、封禁/解封、套餐编辑、配置编辑、邀请撤销全部跑通
- 全链路验收：
  - 老用户 backfill 30 天会员 -> 登录成功 -> AI 可用 -> 后台改到期 -> 仍能查看历史但 AI 被拦截 -> 打开会员页 -> 后台赠送续期 -> AI 恢复 -> 邀请新用户 -> 邀请人再得 30 天

## Assumptions
- 一个云账号仍然只绑定一个云世界；本期不做多世界、多租户后台。
- 会员到期只禁 AI 能力，不禁历史浏览；不改变现有世界实例生命周期策略。
- 支付首期仅手动开通，不接微信支付/支付宝，也不新增订单中心。
- 老用户迁移权益固定为一次性 30 天，使用现有 `admin_grant` 能力承载。
- 生产环境云入口收口，本地模式仅保留给开发/内部使用。
