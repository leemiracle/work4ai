# 隐界 Wiki 角色管理平台完成计划

## Summary

- 目标：把角色创建、读取、编辑、逻辑修改、删除 / 恢复全部收口到 `apps/wiki`，所有写操作走 wiki 版本、差异、审核、巡查、回滚、保护、封禁流程，不再做传统后台 CRUD。
- 用户口径：仅登录用户可提交；采用 Wikipedia 原版风格；删除采用软删除归档。
- 调研依据：Wikipedia 页面保护 / 待审变更、用户等级、删除流程、新页巡查、最近修改巡查、MediaWiki stable/current 版本、观察列表与编辑冲突机制。

## Key Changes

- 后端治理模型：
  - `CharacterPage.currentRevisionId` 作为稳定版本；新增 / 使用 `latestRevisionId` 表示最新提交版本，形成 stable/current 双版本语义。
  - 所有角色写入只能通过 `WikiEditService`：创建、档案编辑、recipe 逻辑编辑、软删除、恢复、回滚。
  - 权限矩阵固定为：`newcomer`、`autoconfirmed`、`patroller`、`admin`；保留 4 天 + 10 个 approved edit 的自动确认规则。
  - Wikipedia 风格审核：新手提交进入 pending；自动确认用户的普通内容编辑可直接生效但进入最近修改巡查；创建、删除、恢复、角色逻辑高风险改动必须待审，patroller/admin 可直接生效。
  - 页面保护采用 `reviewPolicy=open|pending_changes` + `protectionLevel=none|semi|full`：半保护拒绝 newcomer 编辑，完全保护仅 admin 可编辑，pending changes 下未确认改动默认不进入稳定版本。

- API / 类型：
  - 扩展 `GET /api/wiki/pages/:id?view=stable|current`：游客默认 stable；登录用户可看 current / pending；响应增加 `stableRevision`、`latestRevision`、`pendingRevisions`、`visibleContent`、`viewMode`。
  - 扩展 `POST /api/wiki/pages/:id/edits`：继续支持 `contentSnapshot`、`recipeSnapshot`、`baseRevisionId`、`editSummary`、`isMinor`，服务端按变更路径计算 `riskLevel` 和是否待审。
  - 扩展 `POST /api/wiki/pages/:id/delete-request` / `restore-request`：body 必填 `reason`，写入 lifecycle revision 和审核 metadata。
  - 扩展 `GET /api/wiki/pending-reviews`：支持 `operation`、`riskLevel`、`revisionKind`、`limit` 过滤。
  - 扩展 `PATCH /api/wiki/pages/:id/protection`：支持同时设置 `reviewPolicy`、`protectionLevel`、`expiresAt`、`reason`，保护日志保持可查。

## Implementation Order

1. 保存计划文件，确认当前 git 状态后开始。
2. 后端先完成实体字段、类型契约、审核策略、stable/current 查询、生命周期 metadata、保护策略和服务层路径。
3. 前端复用现有 `character-page.tsx` 的逻辑编辑器，用于创建和编辑两处。
4. 重做 pending review / recent changes / history 的 diff 展示和筛选，不新增独立后台 CRUD 页面。
5. 更新 `AGENTS.md` 的实体、路由、页面说明；执行最小验证；最后提交 commit。

## Test Plan

- 后端最小验证：覆盖 `newcomer` 编辑 pending、`autoconfirmed` 普通编辑直发并待巡查、高风险 recipe 待审、patroller 审核发布、软删除 / 恢复不删除 `CharacterEntity`。
- 前端验证：`pnpm --filter @yinjie/wiki typecheck` 和 `pnpm --filter @yinjie/wiki build`。
- 后端验证：`pnpm --filter api test -- wiki`；若没有可复用 wiki spec，则新增一个聚焦 `WikiEditService/WikiReviewService` 的最小 spec。
- 手工冒烟：注册首个 admin、注册普通用户、创建角色、提交逻辑编辑、审核通过、查看 stable/current、申请删除、恢复、回滚。

## Assumptions

- 不开放匿名编辑；游客只读。
- 删除不硬删角色、消息、收益或引用，只做 wiki 词条归档和前台隐藏。
- 角色逻辑影响运行时行为，因此即使采用 Wikipedia 原版风格，也默认按高风险变更处理，非 patroller/admin 需先审核。
- 不引入 MediaWiki；在现有 NestJS / TypeORM / React 架构内复刻核心治理逻辑。
