# @yinjie/analytics

共享前端埋点 SDK。在 `apps/app` / `apps/wiki` / `apps/site` 中初始化一次即可。

## 使用

```ts
import { init, track, trackPageView } from "@yinjie/analytics";

init({
  appId: "app",                              // "app" | "site" | "wiki"
  endpoint: "https://api.example.com/telemetry/events/batch",
  userIdProvider: () => useStore.getState().user?.id ?? null,
  release: import.meta.env.VITE_APP_VERSION,
  // 可选：
  // flushIntervalMs: 5000,
  // maxBatchSize: 30,
  // apiCallSampleRate: 1.0,
  // debug: false,
});

// 业务关键动作
track("login_success", { method: "phone" });
track("moment_published", { hasMedia: true });

// 路由切换时的 PV（如未启用 auto-page-view 时手动调用）
trackPageView("/feed");
```

Next.js 营销站使用 `'use client'` 的 Provider：

```tsx
import { AnalyticsProvider } from "@yinjie/analytics/next";

<AnalyticsProvider appId="site" endpoint="...">
  {children}
</AnalyticsProvider>
```

## 自动采集

`init()` 默认开启：

| 事件 | 触发时机 |
|---|---|
| `session_start` | init 后立即上报 |
| `session_end` | `pagehide` / `beforeunload`，附带 `durationMs`（仅累计可见时长） |
| `page_view` | init 时一次 + `history.pushState/replaceState/popstate` 之后 |
| `frontend_error` | `window.onerror`，stack 截断 2000 字符 |
| `unhandled_rejection` | `window.unhandledrejection` |
| `white_screen` | init 后 5s 检测到 root 容器空 |
| `performance` | FCP / LCP / TTFB / DCL 合并为单条事件 |
| `api_call` | 通过 `@yinjie/contracts` 的 `setApiCallObserver`，自动捕获每次 `request<T>` 的 `{method, path, status, durationMs, ok, errorCode}` |

可通过 `init({ enableAutoCapture, enableAutoPageView, enableContractsBridge })` 关闭其中任一项。

## 上报通道

- 内存批量队列；触发时机：定时（默认 5s）、批次满（默认 30）、`visibilitychange:hidden`、`pagehide`、`beforeunload`。
- 隐藏/卸载优先 `navigator.sendBeacon`；失败回落 `fetch` keepalive；主动 flush 用 `fetch` + 5s 超时 + 2 次指数退避重试。
- 最终失败的批次写入 `localStorage["yinjie_telemetry_pending"]`（封顶 50 条 / 64KB），下次 init 时回放。
- SDK 永不抛错，永不阻塞调用方。

## 标识

- `anonId`：localStorage `yinjie_anon_id`，`crypto.randomUUID()` 生成，跨会话稳定。
- `sessionId`：每次 init 一个，浏览器关闭即失效。
- `userId`：每次 track 时通过 `userIdProvider()` 即时读取，登录前为空，登录后自动开始携带，无需手动 `identify()`。

## 与 contracts 的耦合点

`packages/contracts/src/client.ts` 暴露 `setApiCallObserver(fn)`。SDK 在 init 时用动态 import 注册一个 observer；observer 内 try/catch 包裹，绝不影响业务调用。`endpoint` 自身的 path 前缀会被过滤以避免上报循环。

## 不做什么

- 不发送 PII（电话号、邮箱不会自动上报；如需 props 中带，调用方自行决定）。
- 不缓存事件超过 50 条（避免 localStorage 占用）。
- 不做客户端聚合 — 全部明细发到后端。
