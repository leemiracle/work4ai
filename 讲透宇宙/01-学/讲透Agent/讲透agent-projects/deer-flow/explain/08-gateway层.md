# 08 · Gateway 层：双进程架构里的 REST 门面

## 角色定位

`backend/app/gateway/` 是 DeerFlow 双进程架构中的"管理面"进程。整个系统跑两个 Python 服务：LangGraph Server（2024 端口，agent 运行时）与 Gateway API（8001 端口，REST 服务）。Gateway 不执行任何 agent 循环，它只负责模型查询、MCP/skills 配置管理、记忆读写、上传转换、artifacts 下载、自定义 agent 增删——这些"控制面"操作被从 LangGraph 进程剥离出来，让运行时进程保持纯粹的图执行。nginx（2026 端口）做统一入口分流：`/api/langgraph/*` 转发 LangGraph，其余 `/api/*` 落到 Gateway。

`app.py` 是全进程装配点：`create_app()` 工厂（`app.py:72`）构造 FastAPI 实例、挂 9 个 router（`app.py:153-177`）、注册 `/health`（`app.py:179-186`），模块级 `app = create_app()`（`app.py:192`）供 uvicorn 以 `app.gateway.app:app` 引用——Makefile 的 stop 目标正是按这个进程签名 pkill 的。

## 内部结构

目录极扁平：`app.py`（193 行）+ `config.py`（30 行）+ `routers/` 九个路由模块共 1844 行。路由按资源切分：

- **agents.py（383 行，最大）**：自定义 agent 的 CRUD。创建端点 `@router.post`（`agents.py:165`）写 config.json 与 `SOUL.md`（`agents.py:209`），中途失败用 `shutil.rmtree(agent_dir)` 回滚半成品目录（`agents.py:222`）；SOUL.md 是 agent 人格与行为约束文件，仅详情接口返回（`agents.py:27`）。
- **skills.py（438 行）**：含 `.skill` ZIP 安装全链路（详见 10 篇）。
- **memory.py / mcp.py / models.py / uploads.py / artifacts.py / suggestions.py / channels.py**：各占一个资源面。channels.py 最小（52 行），只有状态查询与单渠道重启两个端点。
- **`routers/__init__.py` 只有 3 行**：`from . import artifacts, mcp, models, skills, suggestions, uploads`（`routers/__init__.py:1`）——重导出 6 个，而磁盘实际有 9 个路由模块（agents/channels/memory 未列入 `__all__`，`routers/__init__.py:3`）。app.py 绕过 `__all__` 直接按子模块名导入（`app.py:8-18`），所以功能无恙，但这份 6 模块清单是 router 家族扩张（agents/channels/memory 后加）留下的旧代快照。

文档计数漂移值得钉版：backend/CLAUDE.md 结构树注释写 "routers/ # 6 route modules"、其 Router 表列了 7 个（Models/MCP/Skills/Memory/Uploads/Artifacts/Suggestions，无 agents/channels）、磁盘实数 9 个——同一份"最权威文档"内部三方不一致，以磁盘为准。

自有配置 `gateway/config.py` 走环境变量而非 config.yaml：`GatewayConfig`（`config.py:6`）仅 host/port/cors_origins 三字段，`GATEWAY_PORT` 缺省 8001（`config.py:24`），惰性单例（`config.py:17`）。

## 外部连接

**对 harness 单向依赖。** Gateway 属 App 层，只准 `import deerflow` 不许反向——这条边界由 `tests/test_harness_boundary.py` 在 CI 强制。典型形态如 `models.py:4` 的 `from deerflow.config import get_app_config`：经 config 包的 barrel 而非直连子模块路径，全仓 14 处同款导入之一。

**lifespan 的两次跨层延迟导入。** 启动序列（`app.py:31-69`）先 `get_app_config()` 做配置预检（`app.py:37`），失败即 RuntimeError 拒绝起服；随后在函数体内 `from app.channels.service import start_channel_service`（`app.py:53`）拉起 IM 渠道服务——失败仅 `logger.exception` 不抛（`app.py:57-58`），未配置 IM 通道的部署照常工作。这两处函数体内导入造成图谱 scanner 的系统性盲区：批分析阶段 gateway 相关 14 个文件中 8 个 `batchImportData` 为空数组（app→channels 与跨层延迟导入全部漏采），依赖边靠子代理逐文件源码重扫补齐。

**MCP 的"进程外缓存"约定。** `PUT /api/mcp/config`（`mcp.py:98`）把配置写回 extensions_config.json（`mcp.py:156` 的 json.dump），但**刻意不重置 MCP 工具缓存**——`mcp.py:160-161` 注释明示：LangGraph 是独立进程，靠 mtime 检测文件变化自动重建工具集。Gateway 侧只做 `reload_extensions_config()` 自更新（同文件尾段）。这是双进程架构下"写文件即通信"的典型协议。

## 数据流

以一次文件上传为例串起全链：前端 POST `/api/threads/{id}/uploads` → `upload_files`（`uploads.py:41`）→ 文件名经 `Path(file.filename).name` 归一化拒绝穿越（`uploads.py:74`）→ 落盘到线程目录 → 若沙箱非本地，经 `sandbox.update_file(virtual_path, content)` 同步进运行时容器视图（`uploads.py:90`，markdown 转换产物同样走 `uploads.py:111`）。删除端点先 `resolve().relative_to` 校验目标仍在线程 uploads 目录内（`uploads.py:185`）。

下载侧 artifacts 的两个防御点：`is_text_file_by_content` 读前 8KB 探 null 字节判定文本/二进制（`artifacts.py:17-27`，`b"\x00" not in chunk`），决定 inline 渲染还是强制下载；文件名按 RFC 5987 编码进 `Content-Disposition`（`artifacts.py:143-147`），中文文件名在浏览器侧不乱码。

## 设计决策

**① lifespan 而非模块级副作用。** 渠道启停全部收进 `lifespan` 上下文（`app.py:31`），shutdown 对称调用 `stop_channel_service`（`app.py:64-66`）——比起在 import 时起线程，这保证 uvicorn 优雅退出不遗留 WebSocket 连接。

**② CORS 外包给 nginx。** `app.py:149` 注释 "CORS is handled by nginx"：本地 serve 模式 nginx 也在线（scripts/serve.sh），GatewayConfig 虽有 cors_origins 字段却无中间件消费——字段是预留位而非生效配置，读代码时别被它误导。

**③ 控制面/数据面分离的代价自觉。** Gateway 明确不碰 MCP 工具（`app.py:46-49` 三行注释把"为什么不在这儿初始化"写成了 mini-ADR）。代价是配置生效延迟：PUT 之后要等 LangGraph 下次 mtime 轮询。收益是 Gateway 重启、崩溃都不影响进行中的 agent 会话。

**④ 请求模型即 OpenAPI 文档。** mcp.py 用 44 行 pydantic 模型描述 OAuth 全部字段（`mcp.py:15-31`，含 `refresh_skew_seconds` 默认 60s 等），端点 docstring 内嵌 JSON 示例（`mcp.py:124-135`）——`/docs` 页面因此可直接当接口手册用。

## 新人提示

- 加新端点的路径是"建 routers/xxx.py + 在 app.py 补 include_router"，**别忘 `routers/__init__.py` 已经三文件掉队的前车之鉴**：要么顺手把新模块加进 `__all__`，要么全仓统一改成 app.py 直连子模块。
- 调试渠道问题先打 `GET /api/channels/`（`channels.py:26-34`）：`service_running=false` 意味着 lifespan 阶段就没起来，去 Gateway 日志找 startup 时的 exception 行，而不是怀疑平台凭证。
- agents.py 的回滚语义（`:222`）只在"目录已建、写文件中途失败"触发；创建成功后的删除走 `:379` 的显式端点。测试覆盖时注意区分这两条路径。
- 看到上传后 agent "看不到文件"，优先查 `uploads.py:90` 的 `sandbox.update_file` 是否执行——本地沙箱与容器沙箱的可见性机制不同，前者靠路径映射天然可见，后者必须显式同步。
- 本地起服调试无需 nginx：`make gateway` 直连 8001 即可，但 CORS 语义与生产不同（无中间件、无同源收口），前端联调时记得走 2026 端口。
