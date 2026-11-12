# 08 · 任务与执行线：从 task_registry 到 Ray worker

## 角色定位

这条线回答一个问题：用户（或 agent）在画布上点了"执行"之后发生了什么。三个文件构成执行链的骨架——`backend/app/services/task_registry.py`（588 行）是任务账本，负责 task_id 生成、状态落盘、查询与终止；`backend/app/services/ray_pipeline_executor.py`（1089 行）是执行引擎，用 Ray 把 pipeline 扔进独立 worker 进程跑；`backend/app/services/dataflow_engine.py`（988 行）是"翻译官"，把 WebUI 的 pipeline 配置（含哈希化的 serving/database 引用）解码成 DataFlow core 能吃的运行时对象。HTTP 入口在 `api/v1/endpoints/tasks.py`：同步执行 L206、异步执行 L282、kill L319。

## 内部结构

**task_registry：一个 JSON 文件的全部生命周期。** 存储就是 `backend/data/task_registry.json`（config.py L22），`_ensure`（L21-41）在损坏时备份成 `.broken.<时间戳>` 再重建。`_generate_task_id`（L54-59）用 `pandas.Timestamp.now() + os.urandom(8)` 拼串取 MD5 前 12 位。`update`（L115-151）带状态自动时间戳：进 `running` 补 `started_at`，进终态补 `finished_at`（L139-145）。查询侧的 `get_execution_result`（L318-426）值得细看：它不只读账本，还直接读 `dataflow_cache_step{N}.jsonl` 缓存文件做采样预览（L372），当前 step 文件不存在时回退读上一步（L379-380）——UI 上的"样本数据"就是从这里来的。

**start_execution_async 的双 task_id 不一致（已知 bug）。** L428-508 的执行流里 task_id 被生成了两次：L461 `task_id = self._generate_task_id()` 生成第一个 ID；L464-472 构造 task_data 时把它填进 `meta.task_id`；随后 L473 `container.task_registry.create(task_data)`——而 `create()` 内部（L94）会**再生成一个新 ID** 覆盖 `task["id"]`；L474 `task_id = task["id"]` 把局部变量改写成第二个 ID，后续的 initial_result、Ray 提交、返回值全用第二个。结果：落盘任务记录里 `id` 与 `meta.task_id` 指向两个不同的孤儿哈希，第一个 ID 纯属浪费，任何依赖 `meta.task_id` 做关联的消费者都会对不上号。修法是删掉 L461 让 meta 填 `task["id"]`，或让 create 接受外部 ID。

**kill_execution：先杀后落盘，防"诈尸"写文件。** L510-588 的顺序是刻意的：L541 先 `ray_executor.kill_execution(task_id)` 物理切断 worker 进程，L543-558 才把 `cancelled` 状态写回磁盘。L539-540 的注释原文说得很清楚："先 Kill 进程，后改状态。这样即使 Kill 之后 worker 还有最后一丝余力想写文件，也会因为进程被切断而停止"。反过来做（先标 cancelled 再杀）会有竞态：worker 在标记之后、被杀之前完成一轮状态回写，把 cancelled 覆盖回 running。它还同步把 `operators_detail` 里 running/initializing 的算子改为 cancelled（L550-554），让 UI 立即停表；即使整个流程抛异常，L568-585 的兜底分支也保证状态仍然落盘。

**ray_pipeline_executor：单并发执行器。** `RayPipelineExecutor`（L808）默认 `max_concurrency=1`（L814、L1089 全局单例），`_ensure_initialized`（L827-846）懒初始化 `ray.init(num_cpus=1, ignore_reinit_error=True)`。核心是 `@staticmethod @ray.remote`（L848-849）装饰的 `_execute_pipeline_remote`（L850-970）。task_registry 两处**函数体内延迟导入** `from app.services.ray_pipeline_executor import ray_executor`（L443、L520）——因为 executor 头部就 `import ray`（L7），模块级导入会把 Ray 拖进每个 import task_registry 的进程（包括跑单测的进程）。

**Ray worker 里的重建世界。** remote 函数运行在全新进程，L875-881 把 json/os/importlib/datetime/logger/settings/DataFlowEngine 全部重新导入一遍；L882-887 逐个 `importlib.import_module(ext)` 加载 DataFlow 扩展模块（operator 插件注册靠它）；L890 设 `RAY_WORKER=1` 环境变量自标识；L895-898 `os.chdir(settings.BASE_DIR)` 对齐工作目录——后面那十几行 logger.info 逐项打印目录存在性（L900-921），是踩过"worker 里相对路径全错"的坑之后留下的诊断痕迹。之后 L926-935 把任务标 running，L938 调真正的 `dataflow_pipeline_execute`，L941-949 把结果合并写回账本文件。

**dataflow_pipeline_execute：算子装配 + compile 预检 + 顺序执行。** L162-806。装配阶段逐算子解析 init/run 两桶参数（`llm_serving`/`embedding_serving`/`database_manager`/`prompt_template` 四类特殊参数各有专门分支，L345-465），动态代码参数（lambda/def 字符串）在 L458-459 直接 `eval`。L550-579 的 **compile key 预检**是这条线最重要的质量闸：用实例化好的算子跑一遍与官方 `pipeline.compile()` 等价的 key 校验，任何算子的 `input_*` key 不在"数据集列 + 上游产出"集合里就在执行前中止——"能跑通的才跑"，而不是跑到第三个算子才崩。预检自身崩溃时兜底跳过（L558-561），不让检查器成为新故障点。

**conftest 的 .yaml 谎言。** `backend/tests/conftest.py` L13 给临时账本起名 `test_task_registry.yaml`，但 TaskRegistry 读写全是 `json.dump`/`json.load`（task_registry.py L49-52）——后缀是 YAML、内容是 JSON。无害但误导：新人按后缀猜格式、或未来有人真给 `.yaml` 接了 YAML 解析器，测试会当场翻车。

**dataflow_engine.decode_hashed_arguments。** L274-422 静态方法，把 pipeline 配置里的 ID 引用展开成运行时描述：input_dataset 变成 FileStorage 配置（L312-318，缓存路径 `BASE_DIR/cache_local/{task_id}_output`，前缀 `dataflow_cache_step`——正是 get_execution_result 读的那些文件）；serving/database 引用填进 `serving_map`/`embedding_serving_map`/`db_manager_map`，Ray worker 拿到后在远端重建实例（executor L397-425）。`init_serving_instance`（engine L181-250）有个安全细节：api_key 不进 params，而是写入环境变量 `DF_API_KEY_{serving_id}`（L233），DataFlow core 从环境读。

## 外部连接

上游三个入口：tasks.py 的三个端点（同步执行走 `start_execution` + `DataFlowEngine.run` 的同步路径；异步走 `start_execution_async` + Ray；kill 走 `kill_execution`）。MCP 白名单里挂着的 `execute_pipeline`/`execute_pipeline_async`/`get_execution_status`/`get_task_result` 四个工具最终都落到这里。下游是 DataFlow core（open-dataflow 包，OPERATOR_REGISTRY/PROMPT_REGISTRY/FileStorage/PipelineABC）与前端任务面板（轮询 status 端点渲染 operators_detail 的算子粒度进度）。

## 数据流

异步执行一次的完整时序：`POST /api/v1/tasks/execute-async` → `start_execution_async`：create 任务记录 → 写 queued 初始态 → `decode_hashed_arguments` 预解码 → `ray_executor.submit_execution`（L972-1021，`future` 存进 `_task_refs` 字典供 kill 用，立即返回）→ Ray worker 起进程：重导世界 → chdir → 标 running → `dataflow_pipeline_execute`：装配算子（参数特殊分支 + coerce）→ compile 预检 → 逐算子执行（每步写 `dataflow_cache_step{N}.jsonl`，`update_execution_status`/`add_log` 两个闭包 L184/L207 实时回写账本）→ worker 把最终结果 merge 回账本。前端轮询 `get_execution_status` 读账本渲染进度；下载/预览读缓存 jsonl。

## 设计决策（含批判）

**JSON 文件当账本而非 SQLite**——与"单用户本地工具"定位一致，人类可直接查看。批判：每次 `update` 都是全量读-改-写整个文件（L126-149），任务多了每次轮询都重读全文件；主进程与 Ray worker 同时写同一文件没有文件锁，靠"worker 只在首尾写、主进程只在 kill 时写"的时序约定避免冲突——约定而非机制。

**max_concurrency=1**——诚实承认 DataFlow 算子多数不是并发安全的，排队比死锁好。批判：没有队列实现，第二个任务只是被 Ray 的资源调度自然阻塞，用户侧看不出"排队中"与"卡死"的区别。

**compile 预检兜底跳过**——检查器不能成为故障点，正确。批判：跳过意味着预检失败时坏 pipeline 又回到"跑到一半才崩"的旧世界，日志里只有一行 warning，没有计数或告警通道。

**eval 动态代码**（executor L458-459）——WebUI 本地工具场景下可接受（用户 eval 的是自己的代码），但若照 run.sh 的安全叙事（"无认证 + pipeline 执行 = 任意代码执行"）审视，这个 eval 是该叙事的具体落点：pipeline 配置里的 `lambda` 字符串会被原样执行。

## 新人提示

1. 排查"任务卡在某状态"先读 `backend/data/task_registry.json`：`status`、`operators_detail` 各算子状态、`logs` 数组都在一个文件里，比加打印快。
2. 改任务状态机时记住写入方有三家：主进程 update、Ray worker 首尾两次写、kill 的强制覆盖。任何新写入路径都要考虑与 worker 回写的竞态——kill 的"先杀后写"顺序是范本。
3. 跑单测不需要 Ray：conftest 的 task_registry fixture 只测账本 CRUD；涉及 executor 的逻辑都在 remote 函数里，本地单测覆盖不到，改动后要真起一次异步执行验证。
4. `get_execution_result` 的 `step` 语义是"算子索引"，文件名 `dataflow_cache_step{N}.jsonl` 与 operators_detail 里的 `index` 字段对齐；step 文件不存在回退 step-1 的分支（L379-380）说明执行中读"当前步"经常拿到的是上一步的完整产物——预览面板显示旧数据通常是这个原因，不是 bug。
