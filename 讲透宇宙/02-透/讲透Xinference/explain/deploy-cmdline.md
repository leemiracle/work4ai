# deploy/cmdline.py — CLI 入口与 xinference-local 启动链精讲

> 仓库 `/data/usershare/ai/inference`（包 `xinference/`），文件 1876 行。

## 一、角色定位

图谱 11 层架构中属 **layer:deploy 部署层**（tour 第 2 步「CLI 启动链」起点）。`pyproject.toml` L77-85 的 console_scripts 有 4 个映射到本文件：`xinference`→`cli`、`xinference-local`→`local`、`xinference-supervisor`→`supervisor`、`xinference-worker`→`worker`。双重身份：**进程启动器**（把 CLI 进程变成集群一部分）与**运维客户端**（其余约 15 个子命令经 `RESTfulClient` 走 HTTP）。图谱显示它无 inbound imports——纯叶子入口。

## 二、内部结构

- **启动组**：`cli`（L165，裸 `xinference` 发 DeprecationWarning）、`local`（L220）、`supervisor`（L267）、`worker`（L333）、公共执行体 `start_local_cluster`（L98）。
- **运维组**：`model_launch`（L932，30+ click 选项）、`model_list`（L1163）、`model_terminate`（L1312）、`register_model`（L400）、`stop_cluster`（L1848）等。
- **工具组**：`model_chat`/`model_generate`（L1449/L1350，手写 REPL）、`get_stored_token`（L82，读 sha256(endpoint) 命名的 token 文件）。

## 三、外部连接

下游：`deploy/utils.py`、`RESTfulClient`。**延迟 import 是关键设计**：三个启动 main 均在函数体内 import（L108/L276/L344），使 `xinference --help` 不加载 torch/xoscar。被依赖方仅 entry points 与 `conftest.py`。

## 四、数据流

**`xinference-local` 从命令到可服务**：

1. entry point→`local()`（L220，默认 port 9997）→`start_local_cluster()`（L98）：`initialize_system_settings`（L107）→日志 dictConfig→`deploy/local.py::main`。
2. `main`（L153）：`set_start_method("spawn")`（L163，注释钉版：CUDA 可能已在 xoscar virtualenv 初始化，fork 会炸）→**端口双轨**：对外 9997，内部 `supervisor_address` 用 `get_next_port()` 随机（L165）。
3. `run_in_subprocess`（L123）：spawn daemon 子进程+Pipe，父进程 poll 等 `READY`（L139-144）。
4. 子进程 `_start_local_cluster`（L42）：`create_worker_actor_pool`（deploy/utils.py L1016，`xo.create_actor_pool(n_process=0, auto_recover="process")`）→`xo.create_actor(SupervisorActor)`（L64-66）→`start_worker_components`（deploy/worker.py L30，创建 WorkerActor）→`await pool.join()`。
5. 父进程 `health_check`（deploy/utils.py L1027，轮询 `supervisor_ref.get_status()`）→`restful_api.run`（L180）：`RESTfulAPI` 经 `xo.actor_ref(uid="supervisor")` 连回 actor 世界（restful_api.py L638），起 uvicorn。

单机/分布式同构：`xinference-supervisor` 走 `deploy/supervisor.py::main`（同款结构但不建 worker）；`xinference-worker` 先用 `RESTfulClient._get_supervisor_internal_address()`（L361）查内部地址再启动。

**一次 `xinference launch`**：`model_launch`（L932）解析选项+`ctx.args` 透传（L961-978）→强制 `wait_ready=False`（L1085）→POST `/v1/models`→`RESTfulAPI.launch_model`（restful_api.py L1151）→supervisor 的 `launch_builtin_model`；CLI 侧 tqdm 轮询 `get_launch_model_progress`（L1119-1129），Ctrl+C 可 `cancel_launch_model`（L1140）。

## 五、设计决策

- **运维命令纯 HTTP 化**：非启动子命令都是 REST 客户端，鉴权统一、零 actor 耦合。
- **双进程结构**：uvicorn 在主进程、actor pool 在 daemon 子进程，互不连坐；Pipe READY+health_check 双保险。
- **wait_ready=False+进度轮询**：大模型加载可达数十分钟，不能占住 HTTP 连接。
- **兼容包袱显式管理**：DeprecationWarning、`--model_path` 旧写法兼容（L970-977）。

## 六、新人提示

- 切入点：`local()`→`start_local_cluster()`→`deploy/local.py` 的 `main`/`_start_local_cluster`，40 行读完启动骨架。
- 易错点：①日志里 actor 地址端口随机，与 CLI `--port` 不同，别拿 9997 去 `xo.actor_ref`；②`ctx.args` 必须 `--key value` 成对（L963）；③stream=True 的 chat/generate 是 asyncio 手写循环，TODO（L1362）说明 RESTfulClient 尚不支持逐字流式；④`n_gpu` 有 "auto"/"none"/int 三态（L1028）。
- 相关测试：`xinference/conftest.py`；冒烟：`xinference-local --log-level DEBUG` 后 `curl localhost:9997/v1/cluster/info`。
