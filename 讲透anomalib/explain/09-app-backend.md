# 09 · anomalib Studio 后端（application/backend/）

## 一、角色定位

`application/backend/` 是 anomalib 库的"产品化外壳"：把 `src/anomalib` 的 Engine、模型注册表、OpenVINO 推理器包装成多用户 FastAPI REST 服务（图谱 app-backend 层，166 节点）。分层教科书式：`api/endpoints/`（17 个路由）→ `services/`（20 个业务）→ `repositories/`（SQLModel CRUD），外加 `workers/` 进程与 `core/scheduler.py:20` 多进程调度。目标：让用户"上传图片 → 选模型训练 → 实时看结果"全程不写 Python。依赖单向：后端 import `anomalib.*`，库对 application 零依赖。

## 二、内部结构

**main.py:38（102 行，入口）**：L38-43 `FastAPI(lifespan=lifespan)`；L59-76 依次挂 15 个路由（project/job/media/model/pipeline/source/sink/trainable_model/snapshot/system/video/stream 等）。L68-69 被注释的 `webrtc_router` 注明"connectivity issues: revisit"——WebRTC 是未启用功能。L81-88 检测静态目录存在则挂 `/static`（Docker 形态）；L91-96 按平台选 uvloop/asyncio 后 `uvicorn.run("main:app")`；L100-101 强制 spawn，L10-11 `mp.freeze_support()` 是 PyInstaller 桌面 sidecar 守护。

**api/dependencies/dependencies.py:40（179 行，装配点）**：L40-42 `get_scheduler` 从 `request.app.state.scheduler` 取全局调度器——跨进程原语（reload 事件、共享内存指标）都由 lifespan 放进 app.state。L45-47 `get_model_service` 注入 `scheduler.mp_model_reload_event`，是"API 改模型 → 推理 worker 立刻重载"的通信底座。L50/L67/L79 三处 `@lru_cache` 表明 Metrics/Configuration/PipelineService 是进程级单例。L104-124 `is_valid_uuid/get_uuid` 把非法 ID 统一转 400，派生 8 个 `get_*_id` 校验依赖；L167-169 `get_device_name` 顺手转大写（OpenVINO 要求）。

**api/endpoints/model_endpoints.py:19（120 行）**：前缀 `/api/projects/{project_id}/models`（L18-22）。四个端点：GET 列表（L25-33 分页）、GET 单模型（L36-46 查无抛 ResourceNotFoundException）、`POST /{model_id}:predict`（L49-74 冒号动作风格，上传图经 `MediaRestValidator` 校验，缓存挂 `request.app.state.active_models`，L69 注释）、DELETE（L77-92 连产物删）与 `POST /{model_id}:export`（L95-120 返回 zip）。

**services/training_service.py:50（430 行，最重）**：`train_pending_job`（L49-69）从 job 队列领任务；`_run_training_job`（L72-181）先 `TrainJobPayload.model_validate`（L77），再用 `DatasetSnapshotService.use_snapshot_as_folder` 把快照解成临时目录（L124），训练本体丢 `asyncio.to_thread(cls._train_model, ...)`（L127）保事件循环。`_train_model`（L196-333）是调用库的完整示范：L240-246 构造 `Folder` 数据模块（val_split_mode=SYNTHETIC）；L249-260 `get_model` + 自定义 `Evaluator`；L264-266 XPU 走 `SingleXPUStrategy`；L273-283 构造 `Engine`（挂进度回调与 `EarlyStopping(monitor="pixel_AUROC", patience=5)`）；L287 `engine.fit`；L286/L304-307 固定 `ExportType.OPENVINO` 导出；L315-323 把 model.xml/bin/ckpt 搬进仓库。`_sync_progress_with_db`（L377-413）0.5s 轮询 job，发现 CANCELED 即 set `cancel_training_event`（L394-397）；L415-430 `abort_orphan_jobs` 启停时清孤儿任务。

**workers/inference.py:33（301 行，常驻推理进程）**：`InferenceWorker`（L33）持帧队列/预测队列/reload 事件。`run_loop`（L251-301）：L263 取帧 → L269 处理 reload → L276 直通模式（pipeline 激活未 running 时原图转发，L72-75）→ L287-288 推理入队。`_model_refresh_daemon`（L87-113）每 5 秒（L59）刷新活跃模型；`_handle_model_reload`（L115-153）事件驱动重载并驱逐缓存（L128）；`_process_frame_with_model`（L209-242）渲染叠加图装进 `StreamData.inference_data`。

**repositories/base.py:19（191 行）**：`BaseRepository[ModelType, SchemaType]`（L19，PEP 695 泛型）约定 `to_schema/from_schema` 抽象 mapper（L26-33）；`_get_filter_query`（L41-56）合并 base_filters；`ProjectBaseRepository`（L184-191）只覆写 `base_filters = {"project_id": ...}`——一行实现项目隔离，8 个子仓库自动继承"只见本项目数据"。

**api/endpoints/trainable_models_endpoints.py:21（76 行）**：`_load_model_metadata`（L20-60，lru_cache）读 `core/model_metadata.yaml`；L44 用 `list_models(case="snake")` 交叉验证，YAML 有而库无的模型告警剔除（L52-54）；L58 推荐优先排序。给前端训练对话框供货。

## 三、外部连接（图谱边证据）

main.py 有 16 条 imports 边指向全部 endpoints，是层内入度之王；create_openapi.py、exception_handlers.py 与 9 个测试文件反向 import 它。training_service 的 imports 边横跨两仓：6 条指向 `src/anomalib` 的 data/deploy/engine，8 条指向后端仓库——"应用↔库"边界上最宽的单点。dependencies.py 带 7 条 tested_by 边；repositories/base.py 被 8 个 repo import 成扇形；trainable_models_endpoints 带 `configures: model_metadata.yaml` 边。

## 四、数据流

训练流：前端 POST `/api/jobs:train` → JobService 落库 pending → TrainingWorker 进程（MAX_CONCURRENT_TRAINING=1）轮询领走 → 解快照 → 线程内 Engine.fit → OPENVINO 导出 → 产物入库、状态 COMPLETED，进度由 `_sync_progress_with_db` 回写。推理流：视频源 worker 推帧进 `frame_queue` → InferenceWorker → `ModelService.predict_image`（model_service.py L276，命中 `cached_models` 免加载，L283-291）→ 预测帧进 `pred_queue` → stream 端点分发前端。API 单图推理同走 ModelService，缓存挂 app.state；指标走共享内存（dependencies.py L53），推理进程写、metrics 端点读。

## 五、设计决策

1. **进程隔离而非线程**：训练/推理/流加载独立 spawn 进程避免 GIL 互踩；单训练内部又用 `asyncio.to_thread`——注释明说是单并发训练的权宜（L45-46）。
2. **数据库当消息总线**：job 状态/进度全落库，取消靠轮询（L394），不引入消息队列，代价是 0.5s 粒度延迟。
3. **缓存三件套**：模型对象缓存在调用方，服务无状态；metadata 与服务实例 lru_cache——热路径零重复加载。
4. **项目隔离下推仓储基类**：multi-tenant 约束由 `base_filters` 一处收口，不在每个端点重复。
5. **训练产物固定 OpenVINO**：`ExportType.OPENVINO` 硬编码（L286），推理服务只认它（model_service.py L258 否则 NotImplementedError）。

## 六、新人提示（含勘误）

- **图谱勘误一**：图谱摘要称 training_service"在子进程里跑完整训练"——源码是 `asyncio.to_thread`（L127）跑**线程**；"进程"指外层 TrainingWorker（workers/training.py），两层别混。
- **图谱勘误二**：predict 的模型缓存不在 ModelService 里，而在 `request.app.state.active_models`（L69），在 service 里找缓存初始化会扑空。
- WebRTC 三件套齐全但 L68-69 被禁用；dependencies.py L162-174 的 `get_webrtc_manager` 等目前是死代码，勿照其理解主流程。
- main.py L45-47 `_ = exception_handlers` 防 import 被格式化删除——"导入即副作用注册"，实现去 exception_handlers.py 找。
- 调训练先看三处：job 表 message、TensorBoard 路径、`train-workspace-{model.id}` 临时目录是否被 finally 清掉（L329-333）。新端点模板：抄 trainable_models_endpoints 的 Router+prefix，服务经 dependencies 注入，仓储继承 ProjectBaseRepository。

---
**自检**：总字符（不含换行）4946 / 去空格字符 4620；行号锚 46 个（main.py×6、dependencies.py×9、model_endpoints×6、training_service×13、inference.py×8、base.py×5、trainable_models×5 等，均经源文件核实；另补 file:line 路径锚 8 处——main.py:38、dependencies.py:40、model_endpoints.py:19、training_service.py:50、inference.py:33、repositories/base.py:19、trainable_models_endpoints.py:21、core/scheduler.py:20，均 grep -n 实证）。
