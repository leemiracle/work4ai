# Xinference 新人入职文档（ONBOARDING）

> 基于代码图谱（2785 节点 / 5826 边 / 14 层 / 16 步导览）与源码抽查（commit `b3de260`，2026-09-03）生成。行号锚均从源码核实。

## 1. 这是什么项目

Xinference 是 Xorbits（Xprobe）开源的**规模化推理平台**（scale-up inference platform，Apache-2.0 许可）。一句话定位：把"下载模型 → 选引擎 → 加载 → 服务化 → 多机扩展 → 监控告警"整条链路变成统一 RESTful API + CLI + Web UI 的平台产品。它自己不写推理 kernel，而是把 vLLM、SGLang、Transformers、llama.cpp、MLX、LMDeploy 六大 LLM 引擎以及数十个多模态引擎，包在统一的模型抽象与集群管理之下。

四条主线能力：

- **八模态统一管理**：LLM、embedding、rerank、image（含 19 个 OCR 模型簇）、audio（TTS/ASR 二十余家引擎）、video、world（世界模型）、flexible，全部走同一套注册表（`llm_family.json` 内置 163 个 LLM 家族）与同一组生命周期 API。
- **多引擎矩阵**：同一个模型（如 Qwen）可按环境落在不同引擎上——启动时用 `check_lib` 探测本机依赖 + `match` 匹配规格，自动选出可用的引擎类；用户也可显式指定 `model_engine`。
- **三种交互面**：RESTful API（`restful_api.py` 3832 行、88 方法，OpenAI 兼容端点全家 + Anthropic Messages 端点 + SSE 流式）、Python SDK（`client/` 同步/异步双客户端）、Web UI（`frontend/` Next.js 静态导出，随 wheel 分发）。
- **分布式集群**：supervisor-worker 两级进程拓扑，基于 Xorbits 自家的 **xoscar** actor 框架；单机模式只是"supervisor+worker 合体"的特例。进阶设施还有独立 Token Router 服务（token 计数与准入路由）和跨节点 KV cache 转移（Xavier）。

对新人最需要建立的第一印象：**这不是一个推理引擎，而是一个"引擎联邦"的管理层**。你会发现仓库里 90% 的代码在回答三个问题——模型从哪来（注册/下载/缓存）、放到哪去（调度/设备/venv 隔离）、请求怎么流（REST → actor → 引擎 → 流式回传）。

## 2. 十分钟架构

集群由三类 actor 构成，全部继承 `xoscar.StatelessActor`：

```mermaid
flowchart TB
    subgraph 客户端
        CLI["CLI<br/>deploy/cmdline.py (click)"]
        SDK["Python SDK<br/>client/restful/"]
        WEB["Web UI<br/>frontend/ Next.js"]
        ROUTER["Token Router<br/>router/ 独立进程"]
    end
    subgraph 服务面
        API["RESTfulAPI<br/>api/restful_api.py:332 (3832 行/88 方法)<br/>+ routers/ 12 子路由"]
        AUTH["OAuth2<br/>api/oauth2/advanced/<br/>auth_service/oidc/audit/rate_limiter"]
    end
    subgraph Actor 集群（xoscar）
        SUP["SupervisorActor<br/>core/supervisor.py:223 (7120 行)<br/>worker 注册/心跳对账/launch 编排/副本扩缩"]
        WORK["WorkerActor × N<br/>core/worker.py:797 (6248 行)<br/>设备分配/venv→下载→子进程加载"]
        MODEL["ModelActor × 副本数<br/>core/model.py:205 (1424 行)<br/>无状态包裹模型:限流/批处理/OOM 自毁/Xavier"]
    end
    subgraph 引擎层
        ENGINES["LLM 六引擎: vLLM/SGLang/Transformers/llama.cpp/MLX/LMDeploy<br/>多模态: OCR×19 / TTS·ASR×20+ / SD·diffusers / hy_world"]
        XAVIER["Xavier KV 转移<br/>vllm/xavier/ 12 文件<br/>BlockTracker + TransferActor"]
    end
    CLI --> API
    SDK --> API
    WEB --> API
    ROUTER -->|数据面代理| API
    API --> AUTH
    API --> SUP
    SUP -->|launch_builtin_model supervisor.py:2839| WORK
    SUP -->|心跳/死亡对账 _handle_dead_worker:584| WORK
    WORK -->|子进程 sub_pool| MODEL
    MODEL --> ENGINES
    MODEL -.->|xavier_config 注入| XAVIER
```

几个关键机制点（后文第 4 节深读）：

1. **进程拓扑**：`xinference-local` = supervisor+worker 同进程；`xinference-supervisor` / `xinference-worker` 拆开部署（`pyproject.toml:78-85` 共定义 8 个 console 入口，deploy/ 下每个入口都是薄壳——`router.py`/`router_agent.py` 仅 8 行）。
2. **模型在子进程中运行**：WorkerActor 收到 launch 后走 venv 准备 → 下载缓存 → 在独立 sub_pool 进程里创建 ModelActor 包裹模型实例；好处是引擎崩溃不拖垮 worker，OOM 时 ModelActor 直接 `os._exit(1)` 让 xoscar 重建子进程池（`core/model.py:601-612` 有长注释解释为何不能用 `sys.exit`）。
3. **REST 层只做转发**：`restful_api.py` 不碰模型，全部经 actor ref 调 supervisor；OAuth2 子树（`api/oauth2/advanced/`）提供企业级认证/审计/限流，是独立可插拔层。

十分钟自测三问：①一条 `POST /v1/chat/completions` 从哪个类进、最终落在哪个 Actor 的哪个方法？②为什么同一个模型名在不同机器上可能跑在不同引擎上（提示：`check_lib` + `match`）？③模型进程 OOM 后集群如何自愈（提示：`os._exit(1)` + 子进程池重建）？答不上来的，跟着第 5 节路线走一遍就有答案。

## 3. 目录地图（按图谱 14 层归组）

图谱把全仓切成 14 层，按"读代码时的心智分组"归成 9 组：

| 组 | 图谱层 | 目录 | 要点 |
|---|---|---|---|
| 工程骨架 | L01 | `pyproject.toml`、`build_backend.py`、`build_web.py`、`.github/` | in-tree PEP 517 构建后端：打包前校验内置模型元数据、构建 Web UI、写 `_commit.py`（40 位 SHA 供 `/v1/cluster/version`）；`.git_archival.txt` 让 sdist 无 git 也能推版本 |
| 公共底座 | L02 | `xinference/types.py`、`constants.py`、`device_utils.py`、`client/` | pydantic 公共模型 + 设备探测（fanIn 100 的 `types.py` 是全仓依赖顶点）；`client/` 是用户 SDK |
| 服务面 | L03 | `xinference/api/` | `restful_api.py` 主体 + `routers/` 12 个模态子路由 + `oauth2/advanced/` 账户体系 |
| 集群控制面 | L04 | `xinference/core/`、`xinference/deploy/` | 三 Actor 巨型模块（supervisor 7120 / worker 6248 / model 1424 行）+ launch_strategy、download_task_store、virtual_env_manager、metrics/otel 等支撑件 + 进程启动入口 |
| 模型抽象 | L05 | `xinference/model/core.py`、`model/llm/llm_family.py` | 八模态工厂分发 + 家族注册表（`llm_family.json` 163 家族 35565 行） |
| 引擎矩阵 | L06–L09 | `model/llm/{vllm,sglang,transformers,llama_cpp,mlx,lmdeploy}/`、`model/embedding/`、`model/rerank/`、`model/image/`、`model/audio/`、`model/video/`、`model/world/`、`model/flexible/` | LLM 六引擎 + multimodal 16 特化 + tool_parsers 15 家；OCR 19 文件；TTS/ASR 20+ 引擎单文件直放 `audio/` 根下 |
| 调度运行时 | L10 | `model/scheduler/`、`model/batch.py`、`model/cache_manager.py`、`model/llm/vllm/xavier/` | 引擎无关的连续批处理骨架 + Xavier 跨节点 KV 转移（12 文件 1884 行） |
| 路由与 tokenizer | L11 | `xinference/router/` | 独立 Token Router 服务（19 文件 4224 行）+ DeepSeek-V4 估算器与随仓 tokenizer 资产包 |
| 部署与可观测 | L12–L13 | `xinference/deploy/docker/`、`monitor/` | Dockerfile×2 + compose 五场景（cpu/distributed/airgap/byo-wheels/默认）+ pypiserver 离线分发；monitor/ 七套 Grafana 面板 ×4 语言 + 四语告警规则 + filebeat |

另有 L14 测试层（157+ 测试文件）横跨各模态 `tests/` 目录，`xinference/thirdparty/`（21 个 vendored 包共 812 个 py 文件）挂在引擎矩阵之下，详见第 7 节。

阅读优先级建议：先 `deploy/` → `api/restful_api.py` 的路由注册段 → `core/` 三 Actor，再按兴趣下钻引擎或调度。`model/` 下的 `utils.py`（fanOut 101）和 `core/utils.py`（fanOut 54）是公共工具汇点，查工具函数先看这里。

## 4. 核心子系统深读

### 4.1 supervisor-worker-model 三 Actor 模型

三份巨型模块构成集群骨架，全部基于 xoscar（Xorbits 自家 actor 框架，模型跑在独立子进程池中）：

- **SupervisorActor**（`core/supervisor.py:223`，7120 行）——控制面大脑。`launch_builtin_model`（L2839）是模型上线的总编排口：先做模态归一（audio/world 模态先 resolve 引擎名，L2869-2878），再校验部署形态——local 部署静默忽略 `n_worker>1`（L2880-2883）；`replica_config`（逐副本钉 worker）与分片启动、legacy `worker_ip/gpu_idx` 参数互斥（L2885-2897）；`n_worker>1` 走 `_launch_builtin_sharded_model` 分布式分片路径（L2899+）。worker 健康靠心跳 + 反向通道双路探测，`_handle_dead_worker`（L584）统一处理三种死亡（心跳超时/反向通道死/优雅注销），`_check_dead_nodes`（L4237）在独立线程里周期巡检。
- **WorkerActor**（`core/worker.py:797`，6248 行）——数据面执行者。`launch_builtin_model`（L4129）串起 venv 准备 → 下载 → 子进程加载全流程。venv 有性能标记：`.xinference_setup_done` marker 文件 + `_venv_setup_done` 进程级缓存（L145-151）保证同包集 venv 只全量装配一次。虚拟环境用 xoscar 的 `VirtualEnvManager`（L135），模型依赖冲突靠它隔离。
- **launch 支撑件**（图谱 step-06，cluster 的运维内脏）：`launch_strategy.py`（137 行）`select_worker` 按负载评分择优落位（L90-91 以负载总和为 score 选最闲 worker）；`launch_history_store.py` 历史回放；`download_task_store.py`（204 行）+ `progress_tracker.py` 管下载进度与暂停恢复；`cache_tracker.py`（159 行）对账已缓存模型；`status_guard.py` 守护模型状态迁移合法性（注册中→就绪→出错的单向门闸）。
- **ModelActor**（`core/model.py:205`，1424 行，`xo.StatelessActor + CancelMixin`）——运行时包裹层，无状态地包住任意模型实例：`request_limits` 限流（默认 `inf`，L281）；`allow_batch` 决定是否加模型级互斥锁（L286-288）；labels 体系带 model_type/engine/quantization/gpu_index 供 Prometheus 打点（L303-315）。

**必读注释**：`core/model.py:555-612` 的 OOM 自毁逻辑。OOM 时先设重入门闸（`_oom_handling`，同步批处理路径下 OOM 线程不会 await 协程，可能重入），向 worker 上报状态（5 秒超时），尽力 `stop()` 回收，最后 **必须 `os._exit(1)` 而非 `sys.exit(1)`**——`sys.exit` 只抛 `SystemExit`，会被 xoscar `_ErrorProcessor.__exit__` 无条件吞掉，进程活着、returncode 不变，`monitor_sub_pools` 永远认为它活着，`recover_sub_pool` 永不触发。这一段是理解"模型崩溃如何自愈"的钥匙。

### 4.2 八模态注册与 `create_model_instance` 分发

`model/core.py:20-145` 的 `create_model_instance` 是**全部模型的世界入口**：按 `model_type` 字符串分发到 llm/embedding/image/rerank/audio/video/world/flexible 八个模态工厂（LLM 分支 L55，其余依次到 L139）。两个细节：所有模态工厂的 import 都写在函数体内（懒加载，防循环依赖）；非 LLM 模态统一弹出 `enable_thinking`/`trust_remote_code` 等仅对 LLM 有意义的参数（L52-53、L70-71 等）。

以 LLM 为例看注册三件套（`model/llm/`）：

1. **家族表**：`llm_family.json` 内置 163 个家族（35565 行），每条含 `model_name/model_specs/model_ability/context_length/virtualenv` 等字段；用户自定义家族落 `~/.xinference/v2/llm/`（`register_custom_model`，`llm/__init__.py:132+`），按 `updated_at` 时间戳智能合并，同名取最新。
2. **引擎探测**：抽象基类 `LLM`（`core.py:47`）定义 `check_lib`（L75，探测引擎依赖是否可 import）与 `match`（L190 = `check_lib` + `match_json` 两步）。`_install()`（`llm/__init__.py:249-274`）把六引擎的模型类填进 `SUPPORTED_ENGINES` 字典，再经 `generate_engine_config_by_model_family`（`llm/__init__.py:75-129`）对每个 spec 遍历所有引擎类调 `cls.match()`，把命中的 `llm_class` 登记进 `LLM_ENGINES[model_name][engine]`——这张表就是 REST 层引擎查询与启动校验的底账。
3. **实例化**：`create_llm_model_instance`（`llm/core.py:324-427`）——`match_llm` 查家族 → `check_engine_by_spec_parameters`（`llm_family.py:640`，从 `LLM_ENGINES` 按 name/format/size/quantization 四元组取出引擎类；venv 模式走 L672 的 with_virtual_env 变体）→ `LLMCacheManager.cache()` 下载/命中缓存（L383）→ 可选 MTP 投机解码 drafter 下载（L389-401，引擎不支持则直接 ValueError）→ LoRA `peft_model` 按 `__init__` 签名注入（L409-424，引擎不支持 LoRA 时警告降级）。

audio 模态是同一范式的变体：`engine_family.py` 的 `AudioEngineModel` 基类提供 `required_libs + check_lib + match`，具体引擎用多继承组装（如 `engine.py:112` 的 `TransformersWhisperAudioModel(WhisperModel, AudioEngineModel)`），16 个引擎类集中在 `engine.py`。

### 4.3 LLM 六引擎矩阵与懒加载

六大引擎目录：`vllm/`、`sglang/`、`transformers/`、`llama_cpp/`、`mlx/`（Apple Silicon 专用）、`lmdeploy/`。职责边界：

- `transformers/core.py` 是通用 PyTorch 兜底路径，`transformers/multimodal/` 下 16 个视觉/音频多模态特化（qwen2_vl/glm4v/intern_vl/deepseek_vl2/ovis2/minicpm…），文本特化（gpt_oss/chatglm/gemma4/ling3）与 tensorizer 加速平级放置。
- `vllm/` 最厚：`core.py` 适配 + `distributed_executor.py` 双代分布式执行器 + `patches/` 对 vLLM 的热补丁 + `xavier/` 整个子系统。
- **懒加载是全仓纪律**：六引擎的重依赖 import 全部压在 `_install()` 等函数体内——`llm_family.py` 只声明空的 `VLLM_CLASSES: List[Type[LLM]] = []` 等容器，import 引擎 core 模块的动作推迟到真正需要注册时。这样装不起 vLLM 的机器照样能起服务、注册 llama.cpp 模型。`model/core.py` 的八模态工厂 import、`create_llm_model_instance` 内的 `LLMCacheManager` import 同理。
- **输出解析层**：`tool_parsers/` 15 家方言解析器（qwen/deepseek r1→v4 五代/glm4→glm5/kimi_k3/llama3/gemma/minimax 两代…）把各家工具调用语法归一为标准格式；`reasoning_parser.py` 解析思考链（Kimi-K3 有专门分支，`llm/core.py:216`）；`harmony.py` 对齐 gpt-oss 的 Harmony 模板。

### 4.4 连续批处理与 Xavier KV 转移

**引擎无关批处理骨架**（供 transformers 类引擎用，vLLM/SGLang 自带批处理）：`model/batch.py` 的 `BatchMixin` 用 `asyncio.Queue` 攒请求，按 `batch_size`/`batch_interval`（常量 `XINFERENCE_BATCH_SIZE/INTERVAL`）聚合后一次性调引擎，包装在 xoscar 的 `_ExtensibleWrapper` 上；处理器崩溃时 `_on_process_batch_done`（L73）把排队 future 全部置异常，避免请求悬死。`model/scheduler/core.py` 定义四个流式哨兵常量（`XINFERENCE_STREAMING_DONE_FLAG` 等）与 `AbortRequestMessage`——跨进程流式协议靠字符串哨兵而非通道关闭来收尾。`scheduler/batch.py`/`request.py` 是批状态机与请求抽象。

**Xavier 跨节点 KV cache 转移**（`model/llm/vllm/xavier/`，12 文件 1884 行）解决"多副本部署下，请求路由到新副本要重算整段 prompt"的问题：

- `scheduler.py:40` 的 `XavierScheduler(Scheduler)` 直接继承 vLLM 调度器，在 `__init__` 里把 `BlockSpaceManager.get_block_space_manager_class` 猴补成 `XavierBlockManager`（L59），后续调度全走定制块管理。
- 调度时通过 `xo.actor_ref` 找两个全局 actor：`VLLMBlockTracker`（`block_tracker.py:20`）维护 `hash → (rank, block_id)` 双向索引，各副本把已算 KV 块的 hash 注册上来，`unavailable_ranks` 集合把恢复中的节点摘除（L67-72）；`TransferActor`（`transfer.py`）异步拉取远端块。
- 容错：`seq_group.force_calculation` 标记传输出错的组，强制本地重算退出 Xavier 流程（`scheduler.py:107-108`）。ModelActor 侧通过 `xavier_config` 注入（`core/model.py:266,323`），销毁时联动清理 TransferActor（model.py:218-226）。

### 4.5 Token Router 与 tokenizer 资产线

`xinference/router/` 是**独立部署的 token 计数与准入路由进程**（自己的 console 入口 `xinference-router`，与推理集群分进程）：`service.py`（127 行）双模式引导——托管模式经 RouterControlPlaneClient 拉配置、独立模式读 YAML；`app.py`（970 行）组装 ASGI；请求路径 admission 准入 → classifier 分类 → `tokenization_worker.py` 计数 → `sse.py` 流式转发 → `backend.py` 回 Xinference 集群。core 侧有配套治理四件套：`core/router_orchestration.py`/`router_registry.py`/`router_scheduler.py`/`router_assignment_store.py`；REST 层的 Token Router 数据面代理在 `restful_api.py:673-681`（httpx AsyncClient 连接池）。

token 计数的**资产化**是这条线的精髓（`router/tokenizer.py`）：`DeepSeekV4TokenEstimator`（L98，类注释明言 "Mirror Xinference's DeepSeek-V4 chat rendering before routing"）必须精确复刻主服务端的 chat 渲染——消息归一化（L40，多模态 content 列表折叠为文本，Phase-1 只支持纯文本）、tools 注入（L64，并进 system 消息）、thinking 三层开关（L76 的 chat_template_kwargs + enable_thinking 归一）→ `encoding_dsv4.py` 的 `encode_messages`（`importlib` 动态加载并校验可调用性，L27-37）→ HF `tokenizers` 计数 → 产出 `TokenBudget` dataclass（L19：prompt/output/reserve/total/enable_thinking 六字段）。tokenizer 文件本体随仓分发于 `router/tokenizer_assets/deepseek_v4_flash_0731/`（含 LICENSE/SOURCE.json 溯源），`tokenizer_asset.py` 负责资产定位。计数差一个 token 就可能把放行请求错路由到容量不足的副本，所以"镜像渲染语义"是这条代码线的第一正确性约束。

## 5. 新人第一周路线（16 步导览 → 5 天）

图谱 16 步 tour 已按依赖关系排序，压缩成 5 天计划：

**Day 1 跑起来 + 看骨架**（tour step-01/02）：装最小依赖 `pip install -e .`（不装任何引擎 extras），`xinference-local` 起单机服务，浏览器开 Web UI（默认 9997 端口）；对照读 `pyproject.toml` 的 8 个 console 入口、`build_backend.py`（打包时做哪三件事）、`deploy/cmdline.py` 的 click 命令组与 `deploy/local.py`（187 行，看清 supervisor+worker 如何在同进程合体）。

**Day 2 服务面**（step-03/04）：`restful_api.py` 只看三段——`RESTfulAPI.__init__` 的路由注册（L411 起）、OpenAI 兼容端点如何转发到 actor、Token Router 数据面代理（L673）；然后跳进 `routers/` 任选一个模态路由（建议 `llm.py`）看参数模型，注意 `dependencies.py` 的注入约定：API 实例由 `RESTfulAPI.serve()` 挂到 `app.state.api`，handler 经 `Depends(get_api)` 拿到，supervisor ref 再在 handler 内 `await api._get_supervisor_ref()` 按需获取。OAuth2 层按需：`oauth2/advanced/auth_service.py` 的认证主流程，其余（oidc/audit/rate_limiter/migrate）当黑盒。

**Day 3 集群骨架**（step-05/06）：精读 `core/model.py` 全文（1424 行，一天读得完）——重点 OOM 自毁段（L555-612）与 `__pre_destroy__` 显存回收（L208-257，注释引用 issue #5156）；supervisor/worker 两份巨型模块不必通读，按调用链走一条：`launch_builtin_model`（supervisor.py:2839 → worker.py:4129）追到 `create_model_instance`（model/core.py:20），画出一次模型上线经过的每个函数。

**Day 4 模型与引擎**（step-07/08/09/10/11）：吃透 4.2 节的注册三件套；用 `xinference engine <model_name>` 命令（cmdline.py:1588）查几个模型的可用引擎，对照 `LLM_ENGINES` 的生成逻辑；tool_parsers 挑 qwen 和 deepseek_v4 两家读，理解方言归一；多模态引擎按兴趣各挑一个（OCR 建议 `deepseek_ocr.py`，音频建议 `engine.py` 的多继承模式）。

**Day 5 深水区**（step-12~16）：scheduler+Xavier（4.4 节路线）、Token Router（4.5 节路线）二选一精读，另一个浏览；`monitor/` 面板 JSON 不用细读，搞清七套面板各监控什么、为什么 ×4 语言；`deploy/docker/` 看 airgap 场景如何离线组装。收尾自查：能否向别人讲清"一条 chat 请求从 REST 到 GPU 再流式回来"的完整路径？讲不清就回到 Day 3 的调用链。

## 6. 构建与测试

**构建链**（`pyproject.toml` + 根级脚本）：PEP 517 in-tree 后端 `build_backend.py` 包装 setuptools.build_meta，在每次 wheel/sdist/editable 构建前做三件事——校验内置模型元数据合法性、跑 `build_web.py` 构建 Next.js 前端并静态导出到 `xinference/ui/web/dist`（`NO_WEB_UI=1` 可跳过）、把 40 位 git SHA 写进 `xinference/_commit.py`（`/v1/cluster/version` 的数据源；无 git 元数据时回退 `.git_archival.txt` 展开值）。版本号走 setuptools_scm 动态推导。20+ 个 optional extras 按引擎（vllm/sglang/transformers/mlx/llama_cpp/intel/musa）与模态（embedding/rerank/image/video/audio）切分——**平台本体几乎零重依赖，一切重物都可选**。

**测试**：202 个 test 文件（图谱 L14 统计 157 个 pytest 文件 + 辅助），最大特点是**大量 skip 因资源成本**——`pytest.mark.skip(reason="Cost too many resources.")` 在 llm/audio 等重型测试里出现 10 处，真正跑大模型的测试默认跳过；`test_llm_model.py:403` 还有 compute capability ≥8.0（Ampere）的 GPU 条件跳过。根 `conftest.py` 在 CI 环境关健康检查（`GITHUB_ACTIONS` → `XINFERENCE_DISABLE_HEALTH_CHECK=1`）。本地跑：`pytest xinference/model/llm/tests/test_llm_family.py` 等注册表测试零 GPU 零下载，新人第一次提 PR 前跑这个最划算。

**CI**（`.github/workflows/`）：`python.yaml` 主线——一组零依赖的纯逻辑测试用 `pytest --noconftest`（L58-59），MacOS 专门跑 MLX 组（L341-344），GPU 组用 `--ignore test_llm_model.py` 裁剪并按"每家族一次冷启动"分组跑（L498 注释解释了这是避免资源竞争而非环境抖动）；`release.yaml`/`docker-cd.yaml` 管发布，`pr_auto_run_gen_docs.yaml` 校验文档生成。

**性能基准**：`benchmark/` 仓根目录自带 `benchmark_serving.py`（服务化吞吐）、`benchmark_latency.py`、`benchmark_embedding.py`/`benchmark_rerank.py` 与通用 `benchmark_runner.py`，配套 extras（`pyproject.toml:294`）——评估引擎矩阵改动对吞吐/首 token 延迟的影响时，先用这套脚本拉基线再动代码。

## 7. 设计哲学与坑

**哲学一：懒加载是防循环依赖的生命线，也是安装友好性的卖点。** `llm_family.py` 顶层只有空容器（`VLLM_CLASSES: List[Type[LLM]] = []`），引擎类的 import 压进 `_install()` 函数体（`llm/__init__.py:249-255`）；`model/core.py:35-43` 八模态工厂的 import 同理。新人最易犯的错：为图方便把引擎 import 提升到模块顶层——轻则未装 vLLM 的环境直接 ImportError 起不来服务，重则 core↔model↔engine 三层互相 import 成环。**加 import 前先问：这个符号能不能在调用点再 import？**

**哲学二：model_spec 双消费。** `llm_family.json` 的同一份 `model_specs` 被两条路径消费——注册期 `generate_engine_config_by_model_family` 用它生成 `LLM_ENGINES` 查询表（REST 的 engine 查询、启动校验都查这张表），实例化期 `create_llm_model_instance` 又回头查同表取 `llm_class`。改 spec 结构时必须同时核对两条路径，还有 venv 变体 `check_engine_by_spec_parameters_with_virtual_env`（含引擎标记收集与 fallback 选择逻辑，`llm_family.py:703-720` 按 ability 倾向 multi/chat 类名）共三处。

**哲学三：监控全家桶的四语言变体是维护税。** `monitor/` 七套面板（overview/gpu-resources/host-resources/llm-slo/model-load/security-audit/token-router）每套 en/zh-CN/ja/ko 四份 JSON，告警规则 `rules*.yml` 同样四语。**改一个面板查询语句要同步改四份文件**，漏改会造成语言间数据口径漂移——这是图谱 L13 层 57 个文件的主成因。

**坑一：thirdparty/ 是 vendored 代码不是自家代码。** `xinference/thirdparty/` 收容 21 个上游包共 812 个 py 文件（indextts 205、ace_step_1_5 110、fish_speech 92、melo 56、cosyvoice 47…），多为音频/视觉引擎的 fork 定制版。它们**不遵循本仓代码规范、不接收本仓重构**，修 bug 优先考虑升上游；其中 navidc_ocr 还以 `vllm.general_plugins` 入口注册进 vLLM（`pyproject.toml:87-88`）。搜索代码时记得排除此目录，否则 812 个文件会淹没结果。

**坑二：崩溃自愈依赖 xoscar 进程语义。** `os._exit(1)` vs `sys.exit(1)`（4.1 节）之外，`__pre_destroy__` 的显存回收注释（`core/model.py:228-235`）值得读：pytorch 系模型没有 stop()/close()，不显式 `del + empty_cache` 显存要等子进程退出才释放，会把下个模型的 subpool 挤崩（issue #5156）——跨引擎资源回收的"补丁感"很强，改引擎加载路径时别顺手删这些看似冗余的清理。

**坑三：信任边界内建于注册表。** `_install()` 给内置家族打 `is_builtin=True` 后才允许 trust_remote_code，用户下载/自定义模型保持 gated（`llm/__init__.py:282-286` 注释明言 CWE-94）。给家族表加字段时别破坏这个标记链。

**坑四：模态差异靠参数清洗抹平。** `create_model_instance` 对非 LLM 模态弹 `enable_thinking`、对非 vLLM embedding 弹 `trust_remote_code`（L52-53、L70-71）——新增公共参数时记得在各模态分支里决定它的去留，否则会以 `Unrecognized keyword arguments` 拒启动（`llm/core.py:71-72`）。

**哲学四：Web UI 离线分发。** 前端 Next.js 静态导出直接打进 wheel（`ui/web/dist`），生产部署不需要 Node——代价是**改前端必须重跑构建**，`pip install -e .` 开发模式下 UI 可能是陈旧的；调 UI 时记住 `NO_WEB_UI=1` 与 `build_web.py` 两个开关。

**哲学五：发行版可插拔扩展引擎。** `_install()` 末尾调 `_run_engine_registration_hooks(MODEL_TYPE_LLM, SUPPORTED_ENGINES)`（`llm/__init__.py:274`，钩子定义在包顶层 `engine_hooks.py`）——私有化发行版（如国产芯片适配）可以在六内置引擎之外追加自家引擎类而不动主仓代码；同理 pyproject 的 `vllm.general_plugins` 入口让 vendored 的 navidc_ocr 注册进 vLLM 插件体系。读懂这两个扩展点，就能判断"该改主仓还是该写插件"。

## 8. 深入索引

**图谱资产**（`~/ai/inference/.understand-anything/`）：

- `knowledge-graph.json`——全量图谱（2785 节点/5826 边），节点 id 形如 `file:xinference/core/supervisor.py`、`class:AudioEngineModel`，可按 id 精确定位；
- `onboard-input.json`——本文档的输入（14 层分层 + 16 步 tour + 30 个 hub 节点带摘要），想看某层的完整代表文件清单直接查 `layers[].representativeNodes`；
- `fingerprints.json`——文件指纹基线，支持增量更新图谱。

**30 个 hub 节点**（改这些文件影响面最大，code review 时重点看）：`types.py`（fanIn 100）、`model/utils.py`（fanIn 99/fanOut 101）、`constants.py`（fanIn 71）、`llm_family.py`（41/36）、`device_utils.py`（37）、`restful_api.py`（27/49）、`core/utils.py`（20/54）；类节点：`AudioEngineModel`（fanIn 18）、`PytorchMultiModalModel`（15）、`ToolParser`（15）、`ChatModelMixin`（14）。

**grep 词表**（按调查意图分组）：

| 意图 | grep 词 |
|---|---|
| 模型上线全链路 | `launch_builtin_model`、`create_model_instance`、`launch_model_as_sub_process` |
| 引擎匹配 | `SUPPORTED_ENGINES`、`LLM_ENGINES`、`check_engine_by_spec_parameters`、`check_lib`、`match_json` |
| 生命周期/自愈 | `_handle_dead_worker`、`_check_dead_nodes`、`_oom_handling`、`recover_sub_pool`、`__pre_destroy__` |
| 隔离环境 | `VirtualEnvManager`、`.xinference_setup_done`、`build_subpool_envs` |
| 批处理/流式 | `BatchMixin`、`_process_batch`、`XINFERENCE_STREAMING_DONE_FLAG`、`allow_batch` |
| Xavier | `XavierScheduler`、`VLLMBlockTracker`、`TransferActor`、`force_calculation`、`hash_block_tokens` |
| Token Router | `DeepSeekV4TokenEstimator`、`TokenBudget`、`encode_messages`、`RouterControlPlaneClient` |
| 平台扩展点 | `_run_engine_registration_hooks`、`vllm.general_plugins`、`is_builtin` |

**后续阅读**：`doc/` 实官方文档源（含集群部署与 FAQ）；`README.md` 的功能矩阵与 `benchmark/` 的性能口径可作对外沟通素材。遇到行为不符直觉时，先查 `xinference/constants.py`（71 个文件依赖它）里的环境变量开关，再查 `core/status_guard.py` 的状态迁移合法性规则。
