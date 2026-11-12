# 01 · FastAPI 后端核心：main / router / create_app / 信封 / DI 容器

## 角色定位

`backend/app/main.py` 是后端唯一装配入口：`scripts/start.sh:83` 用 `uvicorn app.main:app` 拉起，import 该模块即完成 DataFlow core 初始化、11 个注册表装配、路由聚合、CORS、MCP 挂载与前端静态托管。它几乎不含业务逻辑——业务在 `app/api/v1/endpoints/` 的 11 个端点模块与 `app/services/` 注册表里。配套三件套各司其职：`router.py` 聚合路由；`envelope.py`/`errors.py`/`handlers.py` 统一响应信封与错误语义；`core/container.py` 提供全局 DI 单例。

## 内部结构

`main.py` 顺序逐行可查：L17 先建模块级 `app = FastAPI()`；L23-48 工厂 `create_app()` 依次 `setup_dataflow_core()`（L24）→ `container.init()`（L25）→ 新建 FastAPI 挂 `api_v1` 到 `/api/v1`（L26-27）→ CORS 只放行 localhost（L28-35）→ 装异常处理器（L38）→ 挂 MCP（L41，注释钉版"必须在 StaticFiles catch-all 之前"）→ 有 `frontend/dist` 则 StaticFiles 挂 `/`（L43-46）；L50 `app = create_app()` 把 L17 实例整个覆盖；L52-58 注册 `/ui/{path}` SPA 兜底；L61-69 startup 钩子刷新算子缓存。`router.py:16-26` 把 datasets/operators/tasks/pipelines/prompts/serving/text2sql（双 router）/preferences/agent/json_schemas 共 12 个子路由挂进一个 `APIRouter`。`handlers.py` 装四个异常处理器（ApiError L22、RequestValidationError L34、StarletteHTTPException L50、兜底 Exception L66），全部返回 HTTP 200 + 信封体；唯独 `/mcp` 开头路径豁免（L12-17）——JSON-RPC over SSE 不能被信封包住，否则 Cursor 这类客户端校验直接失败。`container.py` 的 `AppContainer`（L3）开 11 个槽位（L8-18），`init()`（L20）全部延迟导入再实例化——docstring 自述动机：解决"module 里全局初始化时各 Registry 实例化顺序不可控"。

## 外部连接

向上：`dataflow_setup.py` 用同解释器跑 `python -m dataflow.cli init`（docstring 钉版：open-data-flow 1.0.10 刻意没有 `dataflow.__main__`），且拒绝向非空残缺目录合并。`container.init()` L34-39 按 `config.py:54-56` 的 `_DATAFLOW_EXTENSIONS` 白名单动态加载扩展；L41-42 检测 Ray worker，worker 进程跳过数据集扫描。向下：`mcp_server.py:53` 把 FastApiMCP 挂 `/mcp`，L31-52 白名单只暴露约 20 个安全操作；`envelope.py` 的 `ApiResponse`（L6-11）是全仓响应契约，前端 `model.js` 生成层照抄。

## 数据流

普通请求：浏览器 → CORS → `/api/v1/xxx` → 端点从 `container` 取注册表 → 正常路径 `resp.ok()` 返回信封；异常路径抛 `ApiError` 家族（`errors.py`：NotFound 40401、Conflict 40901）→ handlers 捕获 → HTTP 200 + `success=false` + 业务码 + `meta.http_status` 记录"本应返回的状态码"，前端只看 `res.code` 分支（`App.vue:41`）。启动流：import main → create_app → 注册表装配 → startup 钩子 dump `data/ops.{lang}.json`。

## 设计决策（含批判）

- **一切错误返回 HTTP 200**：`handlers.py:31` 注释直言"无论什么错误，都返回 200"。单用户本地工具（CLAUDE.md 钉版：无鉴权无多租户）下简化了前端处理，但牺牲 HTTP 语义，网关无法靠状态码报警。
- **业务码三套并存（契约漂移）**：`envelope.py:8` 默认 `code=0`；`resp.py` 的 `ok()` 却填 200；errors 用 1/40401。前端判 `res.code === 200` 依赖 `ok()` 实现细节——若改回 0，语言/主题恢复静默失效。
- **勘误·L17 死实例**：L17 的 `app = FastAPI()` 注定被 L50 覆盖，期间无任何引用；L1/L11 还重复 import 两次 FastAPI。`create_app()` 无幂等保护——每调一次重跑 setup+`container.init()` 全量重建（二次调用半初始化：旧容器引用与新容器脱钩）。
- **勘误·L36-37 变量遮蔽**：`create_app()` 内重算 `DIST_DIR`/`INDEX_FILE`，与 L19-20 模块级同值，纯冗余。
- **推断·spa_fallback 可能不可达**：`/ui/{path}`（L52）注册晚于 L46 的 StaticFiles 挂载 `/`；Starlette 先注册先匹配，`/ui/*` 先落 StaticFiles。机制推断，未实测。

## 新人提示

读后端先读 main.py → container.py → handlers.py（合计不足 200 行），全景即有。改端点记住响应必须走 `resp.ok()` 或抛 `ApiError`；新服务必须挂进 `AppContainer` 并在 `init()` 实例化（CLAUDE.md 明令禁止绕过容器的全局单例）。`/mcp` 信封豁免是硬约束，动 handlers 别删 protocol path 判断。测试复用 `from app.main import app`，别反复调 `create_app()`。
