# 05 · HITL 交互链 + OAuth redirect/popup 双模式

## 角色定位

两条「打断聊天流」的机制共享同一个入口（system_interaction_message）却分道扬镳：HITL（human-in-the-loop）是 agent 主动要人回答问题/做选择，模态强制回应；OAuth consent 是后端要求登录，浏览器跳转或弹窗完成认证后**无缝续发被打断的消息**。后者是全仓状态机最复杂的特性——跨页面导航后的消息恢复与防循环守卫都在这。

## 内部结构

**HITL 链**：入站 interaction 消息在 `Chat.tsx:893-895` 调 openModal 打开 InteractionModal（`ChatInteractionMessage.tsx:35`）。模态支持四种 input_type：text（textarea+必填校验，`ChatInteractionMessage.tsx:184-204`）、binary_choice（按钮组，`ChatInteractionMessage.tsx:206-224`）、radio（单选，`ChatInteractionMessage.tsx:226-260`）、notification——**不开模态**，走 toast.custom 常驻通知（`ChatInteractionMessage.tsx:138-164`）。倒计时：timeout>0 时 setInterval 每秒递减（`ChatInteractionMessage.tsx:61-83`），剩余 ≤20% 变红（`ChatInteractionMessage.tsx:8` 阈值 + `ChatInteractionMessage.tsx:173-182`），归零 toast 报错并关模态（`ChatInteractionMessage.tsx:85-91`），提交前 isTimedOut 双保险（`ChatInteractionMessage.tsx:105-112`）。回答回传：`handleUserInteraction` 组 user_interaction_message 帧，带新 uuid + 原 thread_id/parent_id（`Chat.tsx:297-331`）。

**OAuth 模式选择**：`getOAuthMode` 读 NEXT_PUBLIC_NAT_OAUTH_MODE，redirect 默认/popup 可选（`const.ts:24-25`）；偏好帧在 WS onopen 即发（`Chat.tsx:514`，构造器 `const.ts:30-36`）。

**popup 模式**（`Chat.tsx:611-633`）：window.open 刻意**不带** noopener/noreferrer——带了会返回 null 拿不到句柄、无法在认证完成后关窗（`Chat.tsx:614-620` 注释）；完成消息监听器以 `event.source !== popup` 为信任边界（`Chat.tsx:625-632`）——因为 NAT 取消页从第三方 origin 以 targetOrigin '*' postMessage，origin 检查不可用，**窗口身份才是正确的信任锚**；收到 AUTH_CANCELLED 置 oauthPopupCancelledRef 阻止后续自动弹（`Chat.tsx:629-631`）。

**redirect 模式**（`Chat.tsx:634-642`）：跳转前 `persistOAuthPendingMessage` 把触发消息+会话 id 存 sessionStorage（`Chat.tsx:594-603`）并置 `oauth_redirect_initiated` 标记（`Chat.tsx:640`）。

**取消守卫（防循环核心）**：页面加载 effect 检测「刚从 redirect 回来但 URL 无 oauth_auth_completed」（`Chat.tsx:350-368`）→ 置 `oauth_redirect_cancelled` + 无 pending 消息时 toast 提示（`Chat.tsx:360-367`）；自动重连 effect 见到该标记就不连接（`Chat.tsx:370-377`）——否则「重连→预检认证失败→又 redirect」无限循环；只有用户显式发消息才清标记（`Chat.tsx:964-967`）。

**恢复链**：resume effect 读 pending 键（`Chat.tsx:1594-1597`），有 oauth_auth_completed 查询参数则清 URL（`Chat.tsx:1603-1608`）并消耗键（`Chat.tsx:1612-1613`）；完成时先确保 WS 已连再重发，且按「末条是否 assistant」精确删 1 或 2 条（`Chat.tsx:1646-1654`）——预检认证场景无 assistant 气泡，无条件删 2 会误杀上一轮回复；取消时在聊天流里落一条 'Authorization cancelled.' 助手消息（`Chat.tsx:1616-1635`）。

## 外部连接

上游协议：interaction 消息来自 types/websocket.ts 的 SystemInteractionMessage（`types/websocket.ts:38-49`），consent 判型 `types/websocket.ts:137-144`，URL 三级回退 `types/websocket.ts:224-237`；URL 安全校验 `utils/security/oauth-validation.ts:6-29`（失败拒绝打开，`Chat.tsx:823-831`）。配套测试 `__tests__/components/Chat.websocket.test.tsx` 断言偏好帧与 onopen 发送逐字一致，`__tests__/components/InteractionModal.test.tsx` 覆盖四类渲染/必填/超时/OAuth 弹窗并发队列。

## 数据流

HITL：agent 发 interaction → 模态 → 用户作答 → user_interaction_message 帧（thread_id/parent_id 回传对齐后端会话树）。OAuth：user_message 触发 consent → 校验 URL → redirect 跳转（消息暂存）→ IdP → NAT 成功页（跨 origin，无法读 sessionStorage）→ 带 `oauth_auth_completed` 回 UI → 清 URL → 恢复消息重发 → 原对话继续。

## 设计决策

①HITL **刻意不给 Cancel/背景点击关闭**（`ChatInteractionMessage.tsx:166-167` 的遮罩无 onClick）——workflow 在等人，逃避回答只会卡死流程；②偏好帧**单一事实源**放 const.ts 而非 Chat 内联，生产与测试共享帧形状；③取消守卫拆两层（页面加载检测 + 重连拦截），因为预检认证时没有 pending 消息可依赖（`Chat.tsx:346-349` 注释言明）。

## 新人提示

改 OAuth 流先画状态图：oauth_redirect_initiated（跳转前）→ oauth_auth_completed（URL 回传）→ oauth_redirect_cancelled（取消守卫）→ handleSend 清守卫，四个 sessionStorage/URL 键一个都不能漏；popup 关闭依赖持有句柄，任何「顺手加 noopener」的 PR 都会打断认证完成回调；HITL 新 input_type 在 `ChatInteractionMessage.tsx:184-260` 加渲染分支外，还要检查后端约定（input_type 字符串双端一致）。
