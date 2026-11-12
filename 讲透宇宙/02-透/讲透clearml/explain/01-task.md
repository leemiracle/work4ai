# clearml/task.py — Task 门面：SDK 公共 API 的总入口

## ① 角色定位

`clearml/task.py`（5711 行）是 ClearML SDK 的门面层：用户脚本 `import clearml; task = clearml.Task.init(...)` 触发的一切都从这里开始。它把"实验"（experiment）抽象为一个 `Task` 对象——超参、日志、指标、模型、artifacts 全部挂在这个对象上，最终落到 ClearML Server 可视化/复现。

它的角色是**编排者而非实现者**：真正的脏活（repo 捕获、脚本分析、指标上报、模型管理）全部委托给 `backend_interface`、`binding`、`backend_api` 三大下层。图谱把它归入 **SDK Public API 层（8 节点）**，是整个仓库唯一面向终端用户的巨型门面——文件级入边 20 条（`clearml/__init__.py:3` 直接 `from .task import Task` 重导出），出边 63 条铺向全仓。类定义 `class Task(_Task)`（task.py:152）中的 `_Task` 即 `backend_interface/task/task.py` 的同名基类（task.py:60 导入），门面继承实现层的模式由此定型。

## ② 内部结构

**单例保护与类状态**。`__init__`（task.py:237）要求传入私有哨兵 `__create_protection`，否则直接抛 `UsageError`（task.py:245）——禁止用户手工构造，只能走 `init/create/get_task` 三个工厂。类属性大量使用 `deferred_config`（task.py:210-212），如 `__task_id_reuse_time_window_in_hours`（24h 复用窗口）、`__detect_repo_async`、`__default_output_uri`，惰性求值避免配置未就绪时取值。

**`Task.init`（task.py:280）——最长也最重要的方法**，约 640 行，完整生命周期分六步：
1. **已存在检查**：若 `__main_task` 已有且参数不一致，`verify_defaults_match` 抛错（task.py:524-537）；子进程场景则修复 hooks 后直接返回（task.py:543-581）。
2. **分布式判定**：`__get_master_id_task_id()`（task.py:587）让 torch DDP 非 0 rank 进程不建新任务，改拿锚点 task id。
3. **本地/远程分叉**：`deferred_init=True` 时包成 `FutureTaskCaller` 后台线程执行，完成回调里才落 `Task.__main_task = x`（task.py:634）；正常路径调 `_create_dev_task`（task.py:4403）创建/复用任务对象，随后 `Task.__main_task = task`（task.py:740）。
4. **框架自动绑定**：`should_connect()` 逐级解嵌套字典开关，依次 patch hydra/joblib/matplotlib/tensorflow/pytorch/xgboost 等 13 个框架（task.py:773-806）；并 `PatchOsFork.patch_fork(task)`（task.py:752）让 fork 出的子进程继承上报。
5. **资源监控 + 随机种子 + 参数捕获**：`ResourceMonitor` 按 `development.worker.*` 配置启动（task.py:822 起）；`make_deterministic` 固化种子（task.py:860）；argparse/jsonargparse/click/fire 四类 CLI 捕获在 task.py:863 起的 `auto_connect_arg_parser` 块。
6. **收尾**：`_dev_mode_setup_worker()`（task.py:904）、`BackgroundMonitor.start_all`（task.py:915）、`_set_startup_info()`（task.py:918）。

**`_create_dev_task`（task.py:4403）**是 dev 模式复用逻辑核心：项目/任务名缺省时用 `ScriptInfo.get` 从仓库名和入口文件名兜底（task.py:4409）；24h 窗口内查上次同 (project,name,type) 的任务 id（task.py:5468 `__get_last_used_task_id`，窗口校验在 task.py:5519），可复用则 reset+`_clear_task` 清空重写，published/closed/archived/已有输出模型的一律不复用（task.py:4525-4536）；`continue_last_task` 则改为 reload+`mark_started(force=True)` 续训。最后也兜底设置 `Task.__main_task = task`（task.py:4553）。

**其他关键成员**（全部行号锚实测）：`current_task`（task.py:265）、`create`（task.py:1295，手动建任务、不自动记录、离线模式直接拒绝）、`get_task`（task.py:1428）、`get_tasks`（task.py:1516，docstring 明言"只返回最近 500 条"，更老的用 `query_tasks`；tags 过滤支持 `__$all/__$not/__$or` 三算子）、`clone`（task.py:1806）、`set_packages`（task.py:2149）、`get_logger`（task.py:2500）、`mark_started`（task.py:2728）、`close`（task.py:2816）、`set_base_docker`（task.py:3524）、`execute_remotely`（task.py:3595，本地脚本转队列入参即停止）、`create_function_task`（task.py:3691，pipeline 子任务）、`import_offline_session`（task.py:4059，离线会话回灌）。退出路径 `_at_exit`（task.py:4998）→ `__shutdown`：先标 stopped 防僵尸 running，再按信号/异常判定 failed/completed。

## ③ 外部连接（图谱边证据）

图谱 `file:clearml/task.py` 出边 63 条，方向即依赖：向下 `backend_interface/task/{__init__,args,populate,log,models}`、`backend_interface/{base,logger,model,routers}`、`backend_api/session/session.py`、`backend_api/services/__init__`、`binding/absl_bind.py` 等 framework patch 全家桶；入边 20 条是消费方：`automation/{controller,job,monitor,optimization,scheduler,trigger}`（pipeline/HPO 全走 Task 门面）、`logger.py`、`model.py`、`router/endpoint_telemetry.py`、`binding/{environ_bind,hydra_bind}`、`hyperdatasets/data_view.py`。一进一出构成"门面居中、四通八达"的星形拓扑。

## ④ 数据流

`Task.init` → `_create_dev_task` →（本地）`_create_dev_task` 内 `task.started()` + `ScriptInfo.get` 捕获 repo/diff/requirements → `_edit(script=...)` 写回服务端；随后运行期所有事件走 `get_logger()`（task.py:2500）→ `Logger` → `Metrics/Reporter` 后台线程批量 POST 到 events 服务；atexit 时 `_at_exit` 冲刷缓冲、改状态、关 worker。远程模式（agent 执行）则 `running_remotely()` 为真，init 走 task.py:727-749 分支：直接按 `get_remote_task_id()` 附着既有任务并 `task.started()`，超参从服务端拉回覆盖本地（后续 set_parameters 被过滤），实现"UI 改参 → 远程生效"。

## ⑤ 设计决策

1. **门面+受保护构造**：把 5000 行 API 收敛为一个类，靠私有哨兵防误用，比抽象工厂更直白。
2. **dev 任务复用而非新建**：24h 窗口内同名任务覆盖重写（task.py:5519），避免 UI 被调试垃圾任务淹没——这是 ClearML 最具辨识度也最易被误解的产品决策。
3. **进程级单例 + fork 补丁**：`__main_task` 类级单例配合 `PatchOsFork`，让 multiprocessing 子进程也能正确上报而不重复建任务。
4. **框架绑定全在 init 内联完成**：13 个 patch 按字典开关惰性挂载，用户零配置获得自动记录，代价是 init 膨胀成 640 行巨石——可读性换开箱即用。

## ⑥ 新人提示（含勘误）

- **勘误 1**：`Task.init` 默认**不会**每次运行新建任务——`reuse_last_task_id=True` 时 24h 内复用并清空旧任务（日志会打 "overwriting (reusing) task id=..."，task.py:4574 区域）。要强制新建传 `reuse_last_task_id=False`。
- **勘误 2**：`Task.get_tasks` 只返回最近 500 条（task.py:1516 docstring 原文），要深翻历史用 `Task.query_tasks`。
- **勘误 3**：`Task.create` 永远新建且不自动记录（"This method **always** creates a new Task"，task.py:1324），与 `init` 语义相反；离线模式下调 create 直接 `UsageError`。
- `_at_exit` 在 fork 子进程里会因 `BackgroundMonitor.set_at_exit_state(True)` 走降级路径（task.py:5006-5008），子进程只冲 stdout 不碰事件 API——排查"子进程日志丢了"先看这里。
- 阅读顺序建议：先 152-300（类骨架）→ 4403-4600（dev 复用）→ 740-920（init 尾部装配线），最后啃 280-740 的参数文档。

---
自检：不计空格字符 4617、含空格 4953、行号锚去重 44 处（task.py 为主，另有 __init__.py:3 一处；范围锚含 210-212/524-537/543-581/773-806/4525-4536），全部经 grep -n/源码逐条核实。
