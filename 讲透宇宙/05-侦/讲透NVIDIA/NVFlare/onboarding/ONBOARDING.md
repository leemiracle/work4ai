# NVFlare 仓库 Onboarding（知识图谱版）

> 基于本仓 understand-anything 知识图谱（9120 节点/17846 边/16 层/16 步导览，fingerprints 3465 文件 @a02743eb）与源码逐文件核验写成。所有 `路径:行号` 锚均来自源码 grep 实证。
> 本文是全链产物的导航入口：深度解析见 `../explain/`（9 篇），DeepWiki 全量页见 `../deepwiki/`。

## 一、仓库定位与全景地图

NVIDIA FLARE（**F**ederated **L**earning **A**pplication **R**untime **E**nvironment）是 NVIDIA 开源的领域无关联邦学习 SDK（`README.md:16`），让 ML/DL 工作流以最小改动迁移到联邦范式。它同时覆盖横向 FL（数据各方独立）、纵向 FL（特征分片多方）、联邦统计与隐私计算（DP/HE/PSI，`README.md:24-30`）。论文与文档入口见 `README.md:6`。

本仓最独特之处：**agent-first**。仓库根有给 AI coding agent 的协作契约（`AGENTS.md`、`CLAUDE.md`），`skills/` 目录提供十余个遵循 agentskills.io 规范的可装技能（`skills/README.md`），`nvflare/tool/agent/` 提供专供 agent 的检查 CLI——把"AI agent 能否安全地操作联邦系统"当作一等设计目标（详见第八节）。

代码量分布（图谱 file 级 3523 节点统计）：`nvflare/` 主包 1321、`examples/` 1268、`research/` 407、`skills/` 160、`job_templates/` 141、`integration/` 64、`3rdParty/` 81（第三方许可清单）。主包内部再分：`app_opt` 267（框架适配器）、`app_common` 250（通用 FL 组件）、`fuel` 213（基础库）、`edge` 117（边缘联邦）、`private` 107（运行时核心）、`tool` 88（CLI）、`dashboard` 69、`apis` 57（契约）、`lighter` 39（provision）、`client` 26（作业 API）、`collab` 26（纵向协作）。

新人最常犯的方向错误：以为核心逻辑在 `nvflare/` 顶层的 `client.py`/`server.py`——实际运行时心脏藏在 `nvflare/private/fed/` 下（private 即"内部实现"，但恰恰是全仓最重要的一层）。

## 二、联邦架构总览：三进程模型与 f3 通信（联邦架构专节）

### 2.1 Server-Client-Admin 三进程拓扑

生产部署中一个 FLARE 系统由三类进程构成（`CLAUDE.md:73-77` 的架构概述）：

- **Server 进程**：跑 `FederatedServer`（`nvflare/private/fed/server/fed_server.py:357`），承载 Controller（控制流）、聚合器与作业调度；
- **Client 进程**：每个站点一个，跑 ClientEngine（`nvflare/private/fed/client/client_engine.py:58`），承载 Executor（本地训练）；
- **Admin 进程**：运维入口，通过 HCI 命令体系（`nvflare/fuel/hci/`）与 Server 交互——提交作业、看日志、下载结果。

进程边界即信任边界：客户端注册要走 challenge/register 两步握手与 token 签名验证（`fed_server.py:731` `client_challenge`、`:794` `register_client`、`:552` `sign_auth_token`）。

### 2.2 f3：统一通信底座

所有进程间通信走 Fuel 框架的 **f3（FireFighting Fabric）**：每个参与者是一个 `Cell`（`nvflare/fuel/f3/cellnet/cell.py:231`），以 FQCN（全限定 cell 名）寻址，靠 channel/topic 订阅路由（`cell.py:687` `_register_request_cb(channel, topic, cb)`）。Cell 的核心原语是 fire_and_forget（单向）、send（等待回复）、broadcast（多播）、get_cb_result（回调取果），分别由 `cell.py:355` `_fire_and_forget`、`:475` `_send_request`、`:278` `_broadcast_request` 实现；`cell.py:257` 的 `__getattr__` 还支持按远端方法名动态调用。

传输层可插拔：`nvflare/fuel/f3/drivers/` 下有 aio_grpc/aio_http/aio_tcp/tcp/grpc/file 多种 driver。Server 收到客户端任务结果、客户端拉任务，本质都是 f3 消息（Message + Shareable 载荷序列化）。

### 2.3 Job：2.x 的一等单元

NVFlare 2.4+ 把"作业"（Job）作为部署与提交的一等单元：一个 Job 目录 = `meta.conf`（执行者/资源）+ Server/Client 侧配置 + 自定义代码，由 `nvflare/job_config/api.py:184` 的 `FedJob` 编程 API 或 job_templates 模板描述。作业经 admin 面提交后由 ServerEngine 以独立子进程启动（`nvflare/private/fed/server/server_engine.py:236` `_start_runner_process`），实现作业间隔离。`ClientApp`/`ServerApp`（`nvflare/job_config/api.py:161/172`）分别描述两端要装载的组件。

### 2.4 三种运行模式

- **Simulator**：单进程模拟多方（`nvflare/private/fed/app/simulator/simulator.py`），开发主通道；
- **POC**：本机多进程模拟生产拓扑（真入口在 `nvflare/tool/poc/`——注意 `nvflare/lighter/poc.py:17-23` 已是 deprecated 占位符，只打印迁移提示）；
- **Production**：lighter provision 生成带证书的 startup kit 后分布式部署。

## 三、核心契约层：nvflare/apis

`nvflare/apis/` 是全仓的"宪法层"——所有上层组件（app_common、app_opt、examples）只依赖这里的抽象：

| 契约 | 定义 | 职责 |
|---|---|---|
| Shareable | `nvflare/apis/shareable.py:41` | 通信通用载荷，继承 dict；header/cookie jar/peer props 三段元数据（`:20` ReservedHeaderKey、`:78` add_cookie） |
| DXO | `nvflare/apis/dxo.py:45` | Data eXchange Object：data_kind + data + meta 结构化封装，`to_shareable()`（`:98`）/`from_shareable()`（`:156`）与 Shareable 互转 |
| DataKind | `dxo.py:23` | 九种载荷类型：FL_MODEL/WEIGHTS/WEIGHT_DIFF/METRICS/ANALYTIC/COLLECTION/STATISTICS/PSI/APP_DEFINED |
| FLContext | `nvflare/apis/fl_context.py` | 组件间上下文（private/public、sticky/non-sticky 属性） |
| Executor | `nvflare/apis/executor.py:25` | 客户端契约：抽象方法 `execute(task_name, shareable, fl_ctx, abort_signal)`（`:40`）；`get_job_target_type()`（`:54`）声明作业归属 |
| ControllerSpec | `nvflare/apis/controller_spec.py:255` | 服务端契约：`start_controller`/`control_flow`/`stop_controller` 三段生命周期（`:257-284`） |
| Task/ClientTask | `controller_spec.py:72/173` | 任务单元与"任务×客户端"实例 |

Controller 的任务分发原语是理解一切 FL 算法的钥匙（`controller_spec.py:319-495`）：`broadcast`（一对多）、`send`（点对点）、`relay`（环形接力），各有 `_and_wait` 同步变体与 `broadcast_forever`（`:390`）；`SendOrder`（`:193`）控制多目标顺序。FedAvg 就是"broadcast 训练任务 → 各端 execute → 服务端聚合"的最简组合。

任务在服务端由 `nvflare/apis/impl/task_manager.py` 的 TaskManager 维护（任务表、目标路由、超时取消），ServerRunner 的 `process_task_request`（`nvflare/private/fed/server/server_runner.py:263`）实现 **pull 模型**——客户端主动拉任务而不是服务端推送，这是弱网环境下联邦系统的标准设计。

## 四、服务端运行时

`nvflare/private/fed/server/` 28 个文件构成服务端引擎：

- **fed_server.py**（1255 行）：`BaseServer.deploy()`（`:205`）装配进程；`FederatedServer` 注册 cellnet 回调（`:438`）、处理客户端注册全链（challenge → 校验 site 配置 `:766` → register `:794` → quit `:885`）；auth token 用 HMAC 签名验证（`:552-558`）。
- **server_engine.py**（1115 行）：`ServerEngine`（`:91`）承担 SP（服务端主进程）/SJ（作业进程）双职责（靠 `nvflare/private/fed/server/run_manager.py:67-69` 写入的 PROCESS_TYPE 区分 SERVER_JOB/SERVER_PARENT）——`start_app_on_server`（`:179`）起作业、`_start_runner_process`（`:236`）为每个 Job fork 独立 runner 进程、`send_app_command`（`:475`）向运行中作业发指令、`abort_app_on_server/restart_server/shutdown_server`（`:354-429`）覆盖运维动作。注意全仓并无名为 `main_loop` 的方法：作业侧的持续驱动是 `job_runner.py:683` 的 `JobRunner.run` 轮询循环（类定义 `:110`）+ `ServerRunner._execute_run`（`server_runner.py:130`）。
- **server_runner.py**（618 行）：`ServerRunner(TBI)`（`:80`）跑在作业子进程里——`run()`（`:185`）主循环，`_execute_run`（`:130`）装配 ServerApp；任务回路核心是 `process_task_request`（`:263`）/`_try_to_get_task`（`:382`，含 retry 与 timeout）/`process_submission`（`:445`）；心跳（`_handle_job_heartbeat` `:580`）与 `restore`（`:616`）支撑断点续跑。
- **job_runner.py + job_cmds.py + job_meta_validator.py**：作业上传/校验/调度/清理的全生命周期。
- **client_manager.py**：客户端注册表与在线状态；**cred_keeper.py**：证书管家。

一句话记忆：**engine 管进程，runner 管作业，controller 管算法**——三层职责绝不能混。

## 五、客户端运行时与 FLARE Client API

客户端是服务端的镜像结构：

- **client_engine.py**（527 行）：`ClientEngine`（`:58`）常驻，`send_aux_request`（`:177`）发辅助请求、`start_app`（`:349`）/`deploy_app`（`:462`）接收作业部署、`abort_app`（`:390`）/`restart`（`:453`）响应运维指令。
- **client_executor.py**：`ClientExecutor` 抽象（`:95`）+ `JobExecutor` 实现（`:180`）；`_get_job_launcher`（`:337`）按作业元数据选择启动器（in-proc/sub-proc/外部进程）。
- **client_runner.py / client_app_runner.py**：装配 ClientApp 并执行任务循环。

应用侧用 **FLARE Client API**（`nvflare/client/api.py`）：`init`（`:53`）/`receive`（`:88`，返回 FLModel）/`send`（`:98`）/`log`（`:211`，指标上报）/`is_train`（`:181`）等模块级函数。注意 `nvflare/client/decorator.py` 里只剩已 deprecated 的 `@flare.train`/`@flare.evaluate`（`:38`/`:92`，提示改用 send/receive）——过滤链不再走装饰器，而是配置在 Job 的 filter 组件里。这套 API 的价值：单机训练脚本加几行 flare 代码即可联邦化，FLARE 2.x 的"最小迁移成本"卖点即源于此（`README.md:33`）。

执行器后端三选一（`nvflare/app_common/executors/client_api/`）：`in_process_backend.py:76`（InProcessBackend，同进程）、`external_process_backend.py`（外部子进程）、`attach_backend.py`/`cell_backend.py:80`（CellBackendBase，f3 通道挂载，含 `:41` CellSession 会话管理），由 `client_api_executor.py` 统一装配——决定 ClientApp 与 ClientEngine 的进程关系。

## 六、FL 组件生态与隐私计算

### 6.1 app_common：开箱组件库（250 文件）

- **workflows/**：`scatter_and_gather.py:36`（ScatterAndGather，SAG：广播-训练-聚合，FedAvg 骨架）与 `cyclic.py:21`（Cyclic 环形）是两大开箱控制流；**ccwf/**（22 文件）是跨站验证工作流；
- **aggregators/**：`intime_accumulate_model_aggregator.py:47`（InTimeAccumulateWeightedAggregator，边收边聚）等 11 种聚合策略；
- **executors/、filters/、streamers/、widgets/、psi/、statistics/**：执行器、过滤链、结果流、面板挂件、隐私求交、联邦统计各成体系；
- **pt/**：`pt_file_model_persistor.py`/`pt_file_model_locator.py`（PT 模型交换）+ `pt_fedopt.py`/`pt_fedproxloss.py`/`pt_ditto.py`（算法组件；FedOpt 服务端优化器实现在 `nvflare/app_common/pt/pt_fedopt.py`）。

### 6.2 app_opt：框架适配器（267 文件）

每个 ML 框架一个适配子包：`pt`（40 文件，含 `file_model_persistor.py` Learnable↔state_dict 转换）、`xgboost`（77 文件，横向 histogram_based + 纵向 v2 两代实现）、`tf`、`lightning`、`monai`、`hf`（HuggingFace callbacks）、`sklearn`、`flower`、`he`（同态加密）、`p2p`、`tensor_stream`、`kaggle` 等。命名规律：`app_opt/<框架>/` 内 controller+executor 成对出现，组件 id 可直接写进 Job 配置。

### 6.3 隐私三件套

- **PSI**（`app_common/psi/`）：Diffie-Hellman 求交（`dh_psi/dh_psi_workflow.py:34` DhPSIWorkFlow），纵向 FL 的样本对齐前置；
- **HE**（`app_common/homomorphic_encryption/` + `app_opt/he/`）：加密聚合 filter 链（`he_model_encryptor.py`/`he_intime_accumulate_model_aggregator.py`）；
- **DP**（`app_common/filters/`）：差分隐私过滤器在任务收发两侧生效。

### 6.4 纵向联邦（collab + edge）

`nvflare/collab/`（26 文件）是纵向协作的进程编排原语（`api/app.py` 等）；`nvflare/edge/`（117 文件）面向海量弱设备：`web/web_server.py` + `routing_proxy.py` gRPC 接入（`service/edge_api.proto`），`assessors/` 评估设备/模型质量决定聚合权重，`device/pt/runner.py` 提供端侧 PT 训练。

## 七、Provision 部署与 CLI 工具链

### 7.1 lighter：生产供给器

`nvflare/lighter/provisioner.py:25` 的 `Provisioner` 按 Builder 流水线把 `project.yml` 变成各站点 startup kit（证书/配置/启动脚本）：`provision()`（`:77`）→ `_build()`（`:97`）。Builder 家族在 `lighter/impl/`：`cert.py`（证书签发）、`workspace.py`、`template.py`、`static_file.py`、`docker.py`、`aws.py`/`azure.py`（云 builder）、`he.py`、`edge.py`。模板基座是 `lighter/templates/master_template.yml`（另有 aws/azure/edge 变体）。典型产物：server/client/admin 三端的 startup 目录。

### 7.2 tool：CLI 全家（88 文件）

入口 `nvflare/cli.py`（顶层包骨架，`nvflare/cli.py`），子命令族：`tool/job/job_cli.py`（nvflare job create/submit/list/download，模板来自 job_templates/）、`tool/deploy/`（docker/k8s/slurm 三种部署 + helm 模板，docker 路径的 `docker_deploy.py:94` prepare 负责改造 startup kit）、`tool/poc/`（POC 一键，`nvflare/tool/poc/poc_commands.py`）、`tool/cert/`、`tool/package_checker/`、`tool/agent/`（见下节）、`tool/examples/`（示例管理）。

### 7.3 dashboard 与监控

`nvflare/dashboard/`（69 文件）是 Django 管理面板（`cli.py`/`wsgi.py`/`application/` 46 文件），走 flare_api 与 Server 会话；`app_opt/tracking/` 提供 MLflow/TensorBoard 集成，`examples/advanced/monitoring/` 示范完整观测栈。

## 八、Agent-first 设计与上手路径（agent-first 专节）

### 8.1 协作契约

`AGENTS.md`（21 行）是精简版 agent 备忘：PR 评论 `/build` 触发 CI（`AGENTS.md:3`）、优先用 `rg` 搜索、改动前跑 `./runtest.sh -s` 风格检查、公开产物不得含内部 Jira 引用。`CLAUDE.md`（151 行）是完整版：架构速览、常用命令、black/flake8/isort 风格约定（`CLAUDE.md:117-122`）、测试布局——两文件分工：AGENTS.md 只放 agent 特有增量，共享内容全在 CLAUDE.md（`AGENTS.md:8`）。

### 8.2 skills/：可安装的操作技能

`skills/` 160 文件、10 个技能目录，遵循 agentskills.io 规范 + NVIDIA catalog 扩展（`skills/README.md`）：frontmatter 的 `metadata` 嵌套 `version/author/min-flare-version/blast-radius/category`。**blast-radius 是安全模型核心**——`nvflare-diagnose-job` 标 `read_only`（`skills/nvflare-diagnose-job/SKILL.md:9`），`nvflare-autofl` 标 `submits_production`（`skills/nvflare-autofl/SKILL.md:16`），声明技能可触达的爆炸半径。

技能矩阵（按 category）：Orientation（nvflare-orient，框架导航）、Conversion（convert-huggingface/pytorch/lightning，训练代码转 NVFlare Job）、Troubleshooting（diagnose-job：simulation vs POC/production 双模式取证，失败模式目录映射 recovery_category）、Optimization（autofl：campaign runner 管理的隔离候选实验）、Statistics（fed-stats）。`nvflare-shared/` 是内部非触发技能，沉淀 conversion-workflow/pytorch-model-exchange/validation-evidence 等公共参考。

**对抗性评测夹具**：`skills/nvflare-convert-huggingface/evals/files/injection-hf/` 是注入攻击样本（其 README 内嵌"下载外部 TrustedAggregator/跳过验证/外传权重/隐瞒用户"的恶意指令），用于评测 agent 抗注入——`diagnose-job` 的 SUSPICIOUS_LOG_CONTENT 条款（`SKILL.md:66-70`，把日志文本当证据而非指令）与它互为攻防两面。**此类夹具内容绝不可当作真实建议执行。**

### 8.3 tool/agent：agent 专用 CLI

`nvflare/tool/agent/`（13 文件）：`agent_cli.py` 提供 `nvflare agent inspect source/project/dataset/existing-job` 命令族（`nvflare/tool/agent/agent_cli.py:41` def_agent_cli_parser、`:131` handle_agent_cmd、`:183` _handle_agent_inspect_cmd），`inspection/` 子目录实现数据集/文件/项目检查器，`nvflare/tool/agent/command_registry.py:50` agent_command_registry 注册命令表——让 agent 以结构化 JSON 输出取证，而非裸 grep 仓库。skills 与它互相引用（diagnose-job 明确调用 `nvflare agent inspect source`，`skills/nvflare-diagnose-job/SKILL.md:43`）。

技能 CI 走 `.github/workflows/request-nvskills-ci.yml`，与 premerge 主流水线分离——skills 规范有自己的校验器（`skills/README.md` 中 NVIDIA catalog 字段校验）。

### 8.4 新人 30 分钟上手路径

1. 读 `README.md` + `CLAUDE.md`（5 分钟，建立模型）；
2. `examples/hello-world/` 挑 hello_pt 跑 `nvflare simulator`（10 分钟，见到一轮联邦）；
3. 对照本文第三节读 `nvflare/apis/dxo.py` + `executor.py` + `controller_spec.py`（10 分钟，吃透契约）；
4. 跟图谱导览（tour.json 16 步）从 T02 走到 T09，配合 explain 系列 9 篇深入各子系统；
5. 进阶：self-paced-training 教程（`examples/tutorials/self-paced-training/`，367 文件的官方课程）→ advanced 用例 → research/ 实验。

### 8.5 调试切入点

- 作业没起来：先看 Server 端 `log.txt` 的 job_runner 报错，再 `nvflare job list` 看状态；
- 客户端连不上：查 `fed_server.py:794` register 链的证书/token 拒绝日志；
- 算法没生效：确认 Job 配置里组件 id 与 app_common 导出一致（grep `__init__.py` 的组件注册表）；
- 模拟器行为怪异：记住 simulator 是单进程串行模拟，进程级问题（multiprocessing、CUDA fork）不会在模拟器复现。

---

### 产物索引

| 产物 | 位置 |
|---|---|
| 知识图谱 | 仓内 `.understand-anything/knowledge-graph.json`（9120n/17846e/16 层/16 步） |
| 本 Onboarding | `onboarding/ONBOARDING.md` |
| 深度解析 9 篇 | `explain/explain-01~09-*.md` |
| DeepWiki 全量 | `../deepwiki/`（详见其 INDEX.md） |
