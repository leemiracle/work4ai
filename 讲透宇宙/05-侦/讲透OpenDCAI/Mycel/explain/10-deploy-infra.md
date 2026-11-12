# 10 · 部署基建：compose 档位与发布链

## 角色定位

Mycel 的部署面由三块拼成：**根 docker-compose.yml**（生产全栈形态：backend+frontend 两服务）、**deploy/cli-minimal/**（CLI 用户本地通信后端，一 Compose 拉起五服务迷你栈）、**.github/workflows 的 deploy 双中心**（deploy.yml 生产 + deploy-staging.yml 预发，皆驱动 Coolify API）。deploy/README.md:3-4 开宗明义：这个目录"不是完整生产部署系统"，只是"仓内可拥有、可当产品契约的 compose 档位"。cli-minimal 是**唯一**的仓内本地通信栈——旧的 local-communication 档位连同其 fork schema 已被移除并被测试钉死（见 11 篇）。

## 内部结构

**deploy/cli-minimal/compose.yml 五服务**（compose.yml:1-69）：
1. `postgres`（:2-13）— postgres:15-alpine，pg_isready 健康检查，数据卷 mycel-cli-minimal-postgres；
2. `schema-init`（:15-28）— 一次性服务 `restart: "no"`，依赖 postgres healthy，跑 `scripts/apply_app_schema.py --prepare-supabase-roles --database-url ...` 铺正式 app schema（不是 fork）；
3. `postgrest`（:30-39）— v12.2.8，依赖 schema-init `service_completed_successfully`（:33-34，严格的初始化完成门槛），`PGRST_DB_SCHEMAS: identity,chat,agent,container,library,observability`（:37）暴露 Supabase 风格 REST 面，`PGRST_JWT_SECRET` 必填；
4. `gateway`（:41-46）— nginx:1.27-alpine 挂 rest-gateway.conf，薄网关只转 `/rest/v1/*`（测试钉死不含 gotrue/studio/realtime/storage/analytics/kong，test_cli_minimal_deploy.py:79-83）；
5. `mycel-backend`（:48-66）— 唯一对外端口 `${MYCEL_BIND_HOST:-127.0.0.1}:${MYCEL_PORT:-8042}:8900`（:55，默认只绑回环），环境变量把五件套 Supabase 凭据全部 `:?required` 硬校验。

**generate-env.py（凭据生成器）**：只有 `SUPABASE_JWT_SECRET` 是随机的（`secrets.token_urlsafe(48)`，generate-env.py:37）；`SUPABASE_ANON_KEY` 与 `LEON_SUPABASE_SERVICE_ROLE_KEY` 是**真 JWT**——`jwt.encode({"role": ..., "iss": "mycel-cli-minimal", ...}, secret, HS256)`（:25-27，:43-44），PostgREST 拿同一 secret 验签即可识别角色。测试要求能被 `jwt.decode` 解回 role 声明（test_cli_minimal_deploy.py:108-112）。`MYCEL_PORT` 从 --public-url 解析（:12-22）。

**工厂注入机制**：compose 里 `LEON_SUPABASE_CLIENT_FACTORY=backend.identity.auth.supabase_runtime:create_supabase_client`（compose.yml:59）是**module:function 字符串注入**——storage/runtime.py:218-228 读该变量，`_load_factory`（:231-245）按冒号切分、importlib 动态导入、getattr 取函数、校验 callable；`_ensure_supabase_client`（:248-253）再校验返回物必须暴露 `table(name)` API。storage/runtime.py:21 还把这个变量当特性探针（`bool(os.getenv(...))`）。这样 storage 层不 import 任何 identity 代码，依赖倒置靠环境变量完成。

**运行档位**：`RuntimeProfile` 只有 FULL/COMMUNICATION 两值（runtime_profile.py:7-10），cli-minimal 的 backend 跑 `MYCEL_RUNTIME_PROFILE=communication`（compose.yml:57）裁剪成通信后端；非法值直接 RuntimeError 列出合法集（:16-18）。

**根 compose**（docker-compose.yml:1-33）：backend+frontend 两服务，@@@staging-leon-home-volume（:10-12）把 `/root/.leon` 挂命名卷——models/members/sandboxes 运行时状态必须活过容器替换，否则每次部署冷启动空仓；接入外部网络 `supabase_default`（:30-33），Supabase 本体由运维侧管理。

## 外部连接

deploy.yml（24 行）极简：两条 curl 打 Coolify API 分别部署生产 backend/frontend（deploy.yml:16-23，COOLIFY_BACKEND_PROD_UUID/FRONTEND_PROD_UUID）。deploy-staging.yml（151 行）重得多：解析目标 ref → PATCH Coolify 应用指向 staging stack 分支 → 触发部署 → 轮询 deployment 状态（:84-89）→ 校验 Coolify 应用契约（:105-108）→ **拉 https://app.staging.mycel.nextmind.space/openapi.json 验 OpenAPI 契约**（:118-122）→ PR 评论贴 staging URL（:141）。另 docker.yml 构建镜像、feishu-notify.yml 飞书通知、e2e.yml 每日 02:00 UTC 定时+手动跑端到端。

## 数据流

CLI 用户路径：`generate-env.py > .env` → `docker compose up` → schema-init 铺库建角色 → postgrest 起在 3000、gateway 8000 → mycel-backend 以 communication 档启动，storage 层经工厂注入拿 supabase client，REST 走 SUPABASE_INTERNAL_URL=gateway:8000 内联，外部 cel CLI 打 MYCEL_PUBLIC_URL。生产路径：合并到 main → deploy.yml 触发 Coolify 拉镜像部署双服务；PR → deploy-staging.yml 起预发栈 → OpenAPI 契约校验通过才在 PR 报可测 URL。

## 设计决策（含批判）

- **五个 `:?required` 环境变量**：缺一个 compose 直接拒起，比运行时才炸的配置债好得多；代价是新手第一次 up 的门槛高。
- **真 JWT 而非占位串**：本地栈与云端 Supabase 的鉴权语义完全同构，本地能跑通的生产 token 逻辑不用改；但也意味着 .env 文件本身就是敏感凭据，README:41 提醒 "Keep this file local"。
- **字符串工厂注入**：解耦彻底（storage 零 identity 依赖），可注入任意测试替身；批判点是部署正确性依赖一个拼对的字符串——typo 只在运行时爆 `Failed to import`。
- **e2e workflow 滞后（坑）**：e2e.yml:32-39 引用 7 个测试路径，其中 **4 个全仓不存在**（tests/test_e2e_providers.py、test_sandbox_e2e.py、test_e2e_backend_api.py、test_p3_e2e.py），另外 3 个实际在 tests/Integration/ 与 tests/Unit/sandbox/ 子目录。pytest 以显式路径收集，幽灵路径必报 collection error——这条每日定时任务在当前树上是**必炸**状态，说明 tests/ 目录重组后没人同步 workflow。

## 新人提示

1. 本地起栈先跑 generate-env.py，别手写 .env——ANON_KEY 必须 HS256 签出来，随机字符串过不了 PostgREST 验签。
2. 排查 backend 起不来先查五件套环境变量是否齐（compose 报错信息会点名缺谁），再查工厂字符串是否 import 得到。
3. 改测试目录结构后，记得 grep .github/workflows/ 里的 tests/ 路径——e2e.yml 的四个幽灵路径就是反例。
4. 想加 deploy/full 档位：README:26-29 明说这需要独立架构决策（会成为公开的自托管契约），别顺手加。
