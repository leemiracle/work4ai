# Telemetry Module

客户端埋点上报 + 异步聚合 + Admin 查询。三层结构与 `revenue-sharing/` 保持一致。

## 文件

| 文件 | 作用 |
|---|---|
| `telemetry-public.controller.ts` | `POST /telemetry/events/batch`，无 JWT，前端用 sendBeacon/fetch keepalive 调用。 |
| `telemetry-admin.controller.ts` | `GET /admin/cloud/telemetry/*`，AdminGuard，云控制台用。 |
| `telemetry.service.ts` | 入库 + 限流 + IP 哈希 + 所有 Admin 查询的 SQL。 |
| `telemetry-aggregator.service.ts` | 每小时把 `client_telemetry_events` 滚动到 `client_telemetry_daily`。 |
| `telemetry.dto.ts` | class-validator DTO（appId、eventType、单批 100 条上限、单事件 props 32KB）。 |

## 数据表

- `client_telemetry_events`（原始）：单条事件的不可变记录，按 `(appId, eventName, occurredAt)`、`(appId, eventType, occurredAt)`、`sessionId`、`(userId, occurredAt)` 建索引。`ipHash` = sha256(`ip` + 当日盐).slice(0,16)，每天换盐，不可反推。
- `client_telemetry_daily`（汇总）：按 `(date, appId, eventName)` 主键的日级 rollup。`apiP50Ms`/`apiP95Ms`/`apiSuccessRate` 仅对 `eventName='api_call'` 计算，其余事件类型保持 NULL。

## 限流

`TelemetryService.allowBucket` 在内存中按 `(appId, ipHash)` 维护一个 200 events/min 的 token bucket，超额返回 `{accepted:0, rejected:N}`，不返 429（避免暴露指纹）。重启后桶清空，可接受。

## 时间格式注意事项

TypeORM + better-sqlite3 把 datetime 列写成 `YYYY-MM-DD HH:MM:SS.SSS`（空格分隔），不是 ISO 的 `T`/`Z`。所以：

- 跨天范围比较：用 `>= 'YYYY-MM-DD HH:MM:SS.SSS'` 字符串比较（`startOfRange()` 已处理）。
- 单天聚合：用 `substr(occurredAt, 1, 10) = :date`（`telemetry-aggregator.service.ts` 已处理）。

如果改用 PostgreSQL，需要回到 `>= ISO`。

## 调优建议

- 默认 `apiCallSampleRate = 1.0`。生产中事件量增大时，前端 SDK 调到 0.3–0.5；error/business 仍保持 1.0。
- 当 `client_telemetry_events` 单日条数超过 ~1M 时，考虑把 p50/p95 从 ORDER BY OFFSET 改成桶直方图（每条 api_call 写入桶，daily 表存桶）。
- 原始表保留期：现在没有 GC，按需要可加 cron 任务删除 `createdAt < now - 90 days` 的行。

## 查询接口速查

```
GET  /admin/cloud/telemetry/overview?range=7d&appId=app
GET  /admin/cloud/telemetry/timeseries?eventName=page_view&range=7d&groupBy=appId
GET  /admin/cloud/telemetry/top-events?range=7d
GET  /admin/cloud/telemetry/funnel?steps=page_view,login_success,pay_checkout_success&range=7d
GET  /admin/cloud/telemetry/api-health?range=7d
GET  /admin/cloud/telemetry/errors?range=7d
```

均支持 `appId=app|site|wiki` 可选参数。
