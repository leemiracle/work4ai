# 03 · FastAPI 后端：入口、路由、二十件服务与适配层

## 角色定位

`fastapi_app/` 是平台的 HTTP 网关与业务编排层：向下把 dataflow_agent 的 18 个工作流图（06 篇）包装成 REST 端点，向上为前端（01/02 篇）提供 `/api/v1/*` 全部接口，并独揽三件横切事——API key 校验、配额计费、按端点限流。它自己不做 AI：所有生成逻辑都委托 services，services 再委托工作流图。理解本层的关键是三条组织线：**routers（HTTP 壳）→ services（业务编排）→ workflow_adapters（图调用粘合）**，外加一个 5332 行的例外。

## 内部结构

**应用工厂（main.py 144 行）**：`create_app()`（main.py:61）按序组装 CORS（allow_origins 来自逗号分隔配置，含 `*` 时自动关 credentials，main.py:73-84）→ `APIKeyMiddleware`（main.py:88）→ 19 个业务 router 全部挂 `/api/v1` 前缀（main.py:91-139）→ 静态挂载 `/outputs`（main.py:131-136，产物直读通道）→ `/health`。启动前有两段全局副作用：`.env` 加载（main.py:10-16）与**运行时 tmpdir 重定向**——把 TMPDIR/TEMP/TMP 全部改指 `outputs/system/tmp`（main.py:20-35），避免容器内 /tmp 污染与跨进程不可见。

**APIKeyMiddleware 三合一（middleware/api_key.py 456 行）**：`dispatch`（api_key.py:328）对命中 `_should_check_api_key` 的路径执行三级检查：①X-API-Key 头（query 参数 `x_api_key` 兜底，api_key.py:374-377）与 settings 对账；②`_resolve_user` 解析 Supabase Bearer 用户（api_key.py:391）；③按端点查限流规则表——`/api/v1/paper2figure/generate` 12 次/300s、`pdf2ppt` 8 次/300s、写操作全局 120 次/60s 等（api_key.py:73-84），再叠加服务端配额检查。这是"贵工作流执行前的最后闸门"（api_key.py:6-7 注释自述）。

**routers 与 get_service 延迟导入模式**：19 个 router 文件是纯 HTTP 壳——参数校验、鉴权上下文、调 service、包响应。典型如 paper2ppt.py 的三个 provider（paper2ppt.py:33-47）：

```python
def get_service() -> Paper2PPTService:
    from fastapi_app.services.paper2ppt_service import Paper2PPTService
    return Paper2PPTService()
```

`from` 写在函数体内、每次 `Depends(get_service)` 现造实例。两个动机：①**启动加速与循环依赖规避**——service 模块普遍重（拉起 LLM client、torch 相关工具），顶层 import 会拖慢冷启动并容易与 router 形成环；②**无状态请求作用域**——service 实例不落单例，请求间零共享。kb.py 是反面样本：它不走 service 层，2800+ 行 router 里直接混着上传、notebook、chat、zip 打包等业务（kb.py:36-58 一路 import 到 fitz/docx/pptx），是"路由即业务"的历史堆积。

**services 20 件**（services/ 目录 20 个 .py）：按职责分四类——①转换线编排（paper2ppt/paper2poster/paper2video/paper2citation/paper2drawio/image2ppt/image2drawio/pdf2ppt/image_playground/kb_deepresearch/kb_report/paper2any）；②计费双闸（billing_service 575 行 + guest_quota_service 76 行）；③平台设施（managed_api_service 免费模式凭据解析、onlyoffice_file_service 在线编辑、supabase_admin_service service_role 客户端）；④**巨类 paper2ppt_frontend_service.py：5332 行单文件、`class Paper2PPTFrontendService`（L154）106 个方法**（正则精确计数）。方法名剖面可见其责任堆叠：公开入口仅 `generate_slides/export_slides/review_slide/upload_asset` 四个（加上 `__init__`），其余 100+ 全是 `_` 私有帮手——从 `_call_llm_json/_extract_json_object` 的 LLM 解析，到 `_load_mineru_context` 的文档上下文，到 `_normalize_table_data/_slugify` 的杂务，ReAct 逐页生成、审阅、HTML/CSS 沙箱、canvas schema 双协议、12 模板布局、信号量限流全在一个类里。

**计费双 TTL 与双闸**：`billing_service.BillingService` 维护进程内配额缓存 `_quota_cache`（billing_service.py:33，threading.Lock 保护），**双 TTL 语义**：`BILLING_QUOTA_CACHE_TTL_SECONDS`（fresh 期直接用，L50-51）+ `BILLING_QUOTA_STALE_TTL_SECONDS`（stale 期先用旧值再后台刷新，L53-54）——典型的 stale-while-revalidate，避免 Supabase 抖动打穿配额查询。扣费核心 `consume_workflow`（billing_service.py:358）向 `points_ledger` 插账，**以 event_key 幂等**（先查 `points_ledger` 已有 event_key 即跳过，billing_service.py:389），余额查 `points_balance`（billing_service.py:272）——retry 风暴下不重复扣点。guest_quota_service 则是 SQLite 单文件兜底：`guest_usage(guest_id, usage_date)` 表按日累计（guest_quota_service.py:32-45），为匿名/未注册流量提供本地配额（前端已注明 guest 模式移除、仅向后兼容保留）。

**schemas.py 44 个 Pydantic 模型**（664 行）：请求/响应契约单仓管理——Paper2PPTRequest、DeepResearchRequest/Response、KBReportRequest/Response 等（kb.py:18 直接引用），44 个 `class ...(BaseModel)` 精确计数。前端 ts 类型与此没有生成链，是手工对齐。

**rebuttal 12-agent 三件套（rebuttal_service.py 2108 行）**：审稿回复线的业务核心。**12 个 Agent 类顺序流水**（rebuttal_service.py:203-753）：ReviewCheckAgent（审稿意见格式校验 L203）→ PaperSummaryAgent（论文总结 L282）→ IssueExtractorAgent/IssueExtractorCheckAgent（问题抽取+自校 L318/L360）→ PaperSearchAgent（文献检索 L405）→ ReferenceFilterAgent/ReferenceAnalyzeAgent（引文过滤/分析 L468/L514）→ StrategyGenAgent/StrategyReviewAgent/StrategyHumanAgent（策略生成/审/人审 L560/L605/L652）→ RebuttalDraftAgent/RebuttalFinalAgent（草稿/终稿 L704/L753）。每个 Agent 把输入输出落盘为 `agent-{name}_{input|output}.txt`（如 L229-241），配 LogCollector（L108）与 QuestionState/SessionState（L151/L180）状态对象——"三件套"= 输入落盘 + LLM 调用 + 输出落盘的可审计范式。

**workflow_adapters 10 件**：9 个 `wa_*` 线适配器（paper2ppt/paper2poster/paper2video/paper2citation/paper2figure/pdf2ppt/kb_deepresearch/kb_report）+ `heavy_workflow_subprocess`（重工作流子进程隔离）。另有 `workflow_adapters_old.py` **509 行全注释死代码存档**——非注释非空行数 0（grep 精确实证），文件头保留"参考 gradio_app 封装逻辑"的考古说明，是上游 DataFlow gradio 时代的遗迹。

## 外部连接

- **前端**：01/02 篇全部 `backendFetch` 端点在此落地；X-API-Key + Bearer 双头由 APIKeyMiddleware 消化。
- **dataflow_agent**：services 经 `run_workflow`（kb.py:22）或 wa_* 适配器进入 06 篇的 wf_* 图；state.py 的 13 套 Request/State dataclass 直接被 router 引用（kb.py:18）。
- **Supabase**：billing 写 points_ledger/points_balance/usage_records；supabase_admin_service 提供 service_role 客户端；dependencies/auth.py 解析用户。
- **静态产物**：`/outputs` 挂载直读（main.py:131-136），前端 normalizeBackendAssetUrl 与 secureAssetService 围绕它工作。
- **子进程隔离**：heavy_workflow_subprocess + script/ 下的 heavy_worker，把重图放到独立进程池，防 GIL/显存拖垮 API 进程。

## 数据流

一次典型生成请求：前端 POST → CORS → APIKeyMiddleware.dispatch：API key 对账 → 限流规则表 → `_resolve_user` → 配额预检（billing 缓存命中则免查 Supabase）→ router handler：Pydantic 校验 → `Depends(get_service)` 现场造 service → service 编排（拉 outline、逐页调 agent、写 outputs/）→ `consume_workflow` 扣点（event_key 幂等）→ 响应包 `_to_outputs_url` 产物路径 → 前端拿 URL 直读 `/outputs`。同步窗口 `_SYNC_SUBMISSION_WINDOW_SECONDS = 20`（paper2ppt.py:31）：20 秒内能完成就走同步响应，否则转任务态（paper2ppt_task_service + 前端轮询）。

## 设计决策（含批判）

1. **get_service 延迟导入是双刃剑**：换来冷启动快与循环依赖豁免，代价是**每请求重建 service**——若 service `__init__` 里做重活（读配置、建 client）会乘以 QPS；当前实现因 init 轻而可接受，但没有任何机制阻止后人往 init 里塞重物，且 import 错误从"启动即炸"推迟到"首请求才炸"。
2. **paper2ppt_frontend_service 巨类是全仓最大技术债**：5332 行/106 方法远超人类审阅单元，`_normalize_*` 系列就有十余个，改动必生回归；它没有分层为"协议解析/LLM 客户端/资产管线/导出"四个模块，是因为 ReAct 循环把四者拧在了一起。新人勿试一次性重构，只能切片蚕食。
3. **kb.py 直连业务破坏三层约定**：19 个 router 里 18 个走 service，唯独 kb 把文件处理/解压/notebook/解析全内联，2800+ 行 router 文件本身已是味道；新增 kb 功能应学 kb_deepresearch_service 的拆法。
4. **计费幂等 event_key 设计正确且必要**：前端 retry + 网络重发场景下，points_ledger 的 event_key 去重（billing_service.py:389）是唯一防线；但缓存失效靠 `_invalidate_cached_quota`（L85）显式调用，漏调一处就会读到旧余额——一致性窗口内可能超扣/少扣，属已知取舍。
5. **双 TTL stale-while-revalidate 对单体部署合理**：多副本横向扩展时进程内缓存各自为政，余额视图会分叉；当前 docker-compose 单 backend 无碍，扩容前需换成集中缓存。
6. **509 行全注释的 old 适配器应删除而非存档**：git 历史已尽保存职责，留它在源码树只会污染 grep 与图谱；同类问题在 06 篇的 deprecated wf_* 会再现。
7. **限流规则表硬编码在中间件**（api_key.py:73-84）：调额度要改代码发版；与 config/pricing.yaml 的计费配置双轨，运维心智分裂。
8. **X-API-Key 可走 query 参数**（api_key.py:377）：为某些不支持自定义头的客户端留的口子，但 query 会进访问日志——泄露面比 header 大，宜收紧。

## 新人提示

- 加新端点的标准姿势：schemas.py 加 Request/Response → services/ 新建 service 类 → routers/ 新文件 `APIRouter` + `get_service` 延迟导入 → main.py include_router。别学 kb.py 的内联写法。
- 调试鉴权失败先分三段：401 无 X-API-Key（前端没走 backendFetch）/ 403 用户解析失败（Supabase token 过期）/ 429 限流或配额（看 middleware 日志与 points_balance）。
- 产物路径统一用 `utils._to_outputs_url`/`resolve_outputs_path` 转换，别手拼 `/outputs/` 前缀——Windows/容器路径差异与安全校验都在 utils 里。
- 改 rebuttal 流程先读 12 个 Agent 的 input/output 落盘文件（outputs 下的 agent-*_input.txt），那是免费的执行轨迹日志。
- 想知道某请求会不会被限流，直接查 api_key.py:73-84 的规则表：bucket 名是限流域，同 bucket 共享计数。
