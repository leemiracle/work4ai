# Mycel ONBOARDING · 新人入门指南

>图谱基线 `4ec5a4d5`（3168n/6913e/15 层 15 步）；锚均核实。

## 1. 一句话定位

Mycel 是 OpenDCAI org 的 **agent 工作台平台**：FastAPI 后端 + React 双 SPA（frontend/app 主工作台+frontend/monitor 观测台）+ Supabase/PostgREST 存储面 + 五家 sandbox provider（local/agentbay/docker/e2b/daytona），支撑多 agent 社交。

**双名并存是第一道门槛**：前身代号 **LEON** 与产品名 **Mycel** 同活——环境变量全线 `LEON_*`，模型虚拟名 `leon:mini`（config/defaults/models.json:4），docker 沙箱 id 前缀 `leon-`（sandbox/providers/docker.py:100），内核类就叫 `LeonAgent`（core/runtime/agent.py:92）；部署却用 `MYCEL_RUNTIME_PROFILE`（cli-minimal/compose.yml:57）。只 grep "Mycel" 漏一半代码，grep "leon" 才是全息入口。

## 2. 心智模型

**profile 二态装配**：`create_app`（backend/web/app_factory.py:13）二选一——`COMMUNICATION` 四组通信路由（:22,33-36）vs `FULL` 16 组含 monitor（:58-73），一份代码两种形态。

**LeonAgent 是心脏**：`_build_middleware_stack`（agent.py:973-976）固定序组装 SpillBuffer→Monitor→PromptCaching→Memory→Steering→ToolRunner（caching 仅 Anthropic）；QueryLoop（core/runtime/loop.py:292）驱动多轮模型-工具循环。

**ToolRunner 权限三态**：core/runtime/runner.py:45 按七级来源（userSettings→…→session，permissions.py:6-14）求 allow/deny/ask，以 `ToolResultEnvelope` 统一四态产出（runner.py:186-193）——权限拒绝不是异常是正常信封。

**Storage 三层**：contracts.py（808 行）是契约唯一来源；container.py:36 `_REPO_REGISTRY` 34 项是唯一装配表，懒加载 supabase 31+sqlite 7 实现。

**ids→sandboxes 考古**：身份列已迁 `sandbox_runtime_id`，测试与前端双钉死（坑①）——理解"沙箱即运行时身份"，三域命名就通了。

## 3. 代码地图（图谱 15 层）

| 层 | 域 | 要点 |
|---|---|---|
| 0 | 工程底盘 | pre-commit/六 workflows/双 compose/check_backend_layout |
| 1 | 后端入口 | main.py:1-13→create_app；app_entrypoint 端口解析（双进程共用） |
| 2 | Web 路由 | routers 十三模块 + chat 族（chats_router.py:26），22+ 端点 |
| 3 | Monitor 观测 | 挂 `/api/monitor`（monitor/app/main.py:13）+ 十二用例 |
| 4 | Sandbox/Threads | 最大子系统：SandboxManager（manager.py:249）+五 provider+threads 编排 |
| 5 | 身份社交 | identity 七件套 + hub + library |
| 6 | Agents 内核 | LeonAgent/QueryLoop/middleware 六族/mcp_gateway/fork |
| 7 | 工具族与 Eval | core/tools 七族 + eval/ 评测 |
| 8 | Storage | contracts 契约源；_REPO_REGISTRY 34 项；47 表六域 |
| 9 | Messaging/Protocols | service.py 投递路由；信封 v1 解耦两层 |
| 10 | 主 SPA | Vite+Zustand 四 store+SSE 流；components 101 个 |
| 11 | Monitor SPA | 独立 vite 工程，对接 `/api/monitor` |
| 12 | 测试金字塔 | Unit 223 文件；Integration 7；yatu 14 中文剧本 |
| 13 | Docs/Config | docs/en+zh 各八篇 .mdx；三对 loader；agents/ 四 .md |
| 14 | Typings | 六个 .pyi 补齐 mypy |

## 4. 核心链路走读：一次 agent 会话的旅程

1. **chat 进站**：POST `/api/chats`（chats_router.py:184）→ `make_chat_delivery_fn`（backend/threads/chat_adapters/chat_inlet.py:12）进投递管线。
2. **thread 编排**：`start_agent_run`（run/entrypoints.py:21）拉起执行流；`run_stream_loop`（stream_loop.py:26）转事件流。
3. **agent loop**：一线程一 LeonAgent（pool/registry.py:49）；`QueryLoop.query`（loop.py:341）驱动循环——流式工具调用、重叠执行、检查点水合。
4. **ToolRunner 裁决**：过七级三态；deny→`tool_permission_denied`、ask→权限请求（runner.py:186-193），allow 才执行。
5. **sandbox 执行**：工具后端 `self._sandbox.fs()`（agent.py:981）；SandboxManager（sandbox/manager.py:249）管线程绑定、卷挂载 `leon-volume-{id}`（manager.py:325）、空闲回收；docker 起 `leon-` 容器（docker.py:100）。
6. **storage 落盘**：经 StorageContainer（storage/container.py:74）写 Supabase/SQLite；`apersist_state`（loop.py:724）收口。

主读线：**routers→chat_inlet→run/→LeonAgent→QueryLoop→ToolRunner→SandboxManager→StorageContainer**。

## 5. 运行与调试

**最小本地栈 cli-minimal（唯一本地通信 profile）**：README 明言"not the full Mycel platform"（cli-minimal/README.md:3）。五服务（compose.yml:2-48）= postgres + schema-init + postgrest + gateway（`/rest/v1/*`）+ mycel-backend（`communication`，:57）：

```bash
python3 deploy/cli-minimal/generate-env.py > deploy/cli-minimal/.env   # JWT 自签（generate-env.py:27）
docker compose --env-file deploy/cli-minimal/.env -f deploy/cli-minimal/compose.yml up  # 8042→8900（:55）
```

**provider 装配**：local 零容器常驻；其余四家按配置经 `init_providers_and_managers`（backend/sandboxes/inventory.py）装配进程级单例。

**monitor 三级端口回退**：后端独立进程默认 8011（backend/monitor/app/main.py:19）；前端 env→worktree→回退主 backend，而主 backend 又是 env→worktree→8001 三级（monitor-ports.ts:13-25）。

**e2e 陷阱**：workflow（每日 02:00，e2e.yml:13）列的 7 个 pytest 路径全不在所指位置（:35-42）——本地用 tests/Integration/ 与 tests/yatu/。

## 6. 已知坑（动手前必读）

**① sessions→sandboxes 迁移，两层钉棺材**。后端三测试锁死 `sandbox_runtime_id`——create/get 返回它（tests/Unit/storage/test_chat_session_row_contract.py:4-34）、PRAGMA 必含该列（:36-60）。前端 monitor：contract 测试 readFileSync 断言旧 token 不存在，且**被禁 token 拼接构造防自 grep**——`["leon","runtime"].join("-")+"-"`（monitor 的 SandboxesPage.tsx:40 与同目录 .contract.test.js:9-11、ResourcesPage.contract.test.js:16-33 同法禁 session 族）。**grep "leon-runtime" 零命中不是没有，是设计如此**。

**② e2e workflow 幽灵测试**：e2e.yml:35-42 七路径在 tests/ 根全不存在——仅 daytona_e2e 与 summary_persistence 活在 tests/Integration/，其余五个消失；缺文件必 collection error，定时 e2e 必炸。

**③ README 幽灵文件群（双语同病）**：config/defaults/README.md:9-14 的 `agents/*.json` 与 `model_mapping.json` 不存在（实为 .md）；:66-71 的 `leon:fast` 等六名与 models.json 实际四名 mini/medium/large/max 脱节；README.md:200 与 README.zh.md:196 双链不存在的 CONTRIBUTING.md。

**④ @@@port-precedence 注释与实码相反**：backend/web/main.py:11 注释宣称 worktree 最高，但 `resolve_app_port`（backend/bootstrap/app_entrypoint.py:19-37）实码**先环境变量**（:20）**再 worktree**（:22-33）——真实序 `LEON_BACKEND_PORT > PORT > worktree > 8001`。钉反的 @@@ 注释比没有更危险。

**⑤ enrich_from_runtime 整除均摊丢余数**：eval/tracer.py:86 把聚合 usage `// n` 均摊（:107-112），余数丢、六项独立取整；成本均摊却浮点除（:114-116）无此问题。

**⑥ .env.example 死配置**：frontend/app/.env.example:1-2 的 `VITE_SUPABASE_URL/ANON_KEY` 在 src/ 零引用；根 .env.example:9 `MODEL_NAME`、:18 `LANGSMITH_API_KEY` 无消费者。

**⑦ pre-commit `|| true` 宽松门禁**：.pre-commit-config.yaml:12（eslint）与 :19（tsc）entry 皆 `bash -c '... || true'`——前端 lint/类型错误永远退出 0（ruff 是真闸）。

**⑧ idle_reaper 占位+monkey-patch 读法**：idle_reaper.py:5-6 的 `IDLE_REAPER_INTERVAL_SEC = 0` 与 `init_providers_and_managers = None` **是占位非 bug**——真值由 lifespan 启动注入（lifespan.py:177-187，:185 写入 config.py:7 的 30 秒），避免 pool 反向 import web；单读该文件会误判忙轮询。

另有 Firecrawl 子串过滤（firecrawl.py:50-54）、eval 场景目录缺失（runner.py:224）、`is_error` 误判（runner.py:147），详见 explain/12。

## 7. 上游与生态

**Supabase/PostgREST**：31 仓储经 PostgREST session 保真（storage/providers/supabase/_query.py:17-22）；cli-minimal 用裸 postgres+postgrest+nginx 复刻同一 REST 面；大 IN 查询可触发 502（sandbox_monitor_repo.py:242）。

**langchain-anthropic 猴补丁**：上游 >= 1.0 流式丢 message_start 的 input_tokens，本仓 monitor/usage_patches.py:1-9 钉版补丁恢复 v0.2.4 行为，agent.py:89 导入即应用——升级前先看补丁是否仍需要。

**OpenDCAI org**：Mycel 与 DataFlow 同 org，agent 平台线主体仓；docs 双语可参考但默认落后实码一个版本（坑③）。

## 8. 学习路径

**第一遍（tour 15 步）**：1-3 建形态 → 4-6 啃内核（LeonAgent/QueryLoop/ToolRunner+工具族）→ 7-9 执行与社交 → 10-11 观测存储 → 12-15 外围。

**第二遍（explain 12 篇配读）**：01 配步骤 1-2、02 配 4-5、03 配 7、04 配 8-9、05 配 11、06 配 13-14（坑①考古）、07 配 10、08 配 6、09 配 12、10 配第 5 节、11 配 15、12 配第 6 节。

**动手建议**：首贡献从修文档坑入手（③④）；改目录先跑 check_backend_layout 并 grep workflows；跑通 cli-minimal 再用 fakes 写单测；任何 .md 与代码冲突**永远信代码**。
