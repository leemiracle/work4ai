# 06 · Automation 流水线——clearml/automation/controller.py（5634 行）

## ① 角色定位

controller.py 定义 `PipelineController`：**DAG 流水线编排器**。类 docstring（controller.py:43-49）一锤定音：流水线=步骤 DAG，每步是一个克隆的 Task（或从函数创建的 Task），控制器监控到完成；**流水线本身也是一个 Task**（pipeline controller Task），可本地跑也可投递到 clearml-agent 的 services 队列。下半部 `PipelineDecorator`（controller.py:3981）提供 `@pipeline`/`@component` 函数式 API——图谱 inherits 边证实它**继承**而非组合 PipelineController。同目录 scheduler.py（HPO 调度）、trigger.py 都围绕这个生态。

## ② 内部结构

**类常量（controller.py:59-85）**：`_tag="pipeline"`、步骤标签前缀 `pipe:`、**参数引用宏正则** `_step_pattern=r"\${[^}]*}"`（controller.py:62）、状态 artifact 名 `pipeline_state`、幂等指纹 runtime 属性 `_pipeline_hash`、三个节拍——plot 更新 5 分钟/进度 10 秒/节点监控 5 分钟（controller.py:71-73）。

**`Node` 内部类（controller.py:94，@attrs）**：DAG 节点即数据对象——`name`/`base_task_id`（克隆模板）/`task_factory_func`（函数建 Task）/`parents`（上游表=DAG 边）/`parameters`/`task_overrides`/`executed`（实际 Task ID）/`job`（ClearmlJob 对象）/三组 `monitor_*` 上卷配置/`cache_executed_step`。`continue_behaviour` 是私有传输 dict，`__attrs_post_init__`（controller.py:197）展开成 `continue_on_fail`/`continue_on_abort`/`skip_children_on_fail`/`skip_children_on_abort` 四 bool（controller.py:176-192）。

**命令式 API**：`__init__`（controller.py:223，pool_frequency 默认 0.2 分钟）；`add_step`（controller.py:486）/`add_function_step`（controller.py:774）建 DAG；`start`（controller.py:1055）/`start_locally`（controller.py:1130）；`wait`（controller.py:1380）、`is_successful`（controller.py:1415）；类方法 `create`/`clone`/`enqueue`/`get`（controller.py:1594/1692/1749/1809）把流水线当实体管理。

**序列化与幂等**：`_serialize_pipeline_task`（controller.py:2091）是本地/远程分水岭——本地运行时把 DAG JSON 写进 Task 配置对象（`Pipeline` 节）、参数摊平进 Args 区、`_get_task_hash`（controller.py:2198）算指纹写 runtime 属性；`_serialize`/`_deserialize`（controller.py:2235/2252）双向转换。

**执行引擎**：`_daemon`（controller.py:3356）主循环独立线程，`ThreadPool(16)`（controller.py:3360）并发发射；循环体检测完成、失败重试（`_call_retries_callback` controller.py:3205→`_relaunch_node` controller.py:2855）、超时中止（controller.py:3397）、失败级联（controller.py:3391-3397）。`_launch_node`（controller.py:2873）：解析 `${step}` 宏 → 构造 `ClearmlJob`（automation/job.py:516）带 `parameter_override`/`parent=流水线Task.id`/`pipe:` 标签 → `node.job.launch()`（controller.py:2971）。**宏引擎** `_parse_step_ref`（controller.py:3516）把 `"${step1.parameters.Args/param}"` 替换为上游实际值，可递归进 dict/list/tuple。**上卷** `_monitor_node`（controller.py:3572）把步骤 Task 的标量/artifact/输出模型**引用复制**到流水线 Task（controller.py:3621-3660）；`_update_execution_plot`（controller.py:2973）与 `_update_dag_state_artifact`（controller.py:3321）负责 UI。

**装饰器 API**：`component`（controller.py:4474）39 个参数（return_values/cache/packages/parents/execution_queue/monitor_*/retry_on_failure/docker...）；`pipeline`（controller.py:4975），`pipeline_execution_queue` 默认 `"services"`（controller.py:5001）；`_component_launch`（controller.py:5386）把组件函数源码+自动 requirements（走 08 篇 pigar）打包成远程 Task；`run_locally`（controller.py:5343）/`debug_pipeline`（controller.py:5355）。

## ③ 外部连接（图谱证据）

图谱 25 条边：controller.py imports job.py（ClearmlJob）、populate.py、proxy_object.py、主 task.py；被 `automation/__init__.py`、scheduler.py、**pipeline_from_decorator.py** 反向导入——最后这个是关键：services 队列拉起流水线 Task 后由它从序列化配置重建 PipelineDecorator 并驱动执行。inherits 边：`PipelineDecorator→PipelineController`（controller.py:3981）。`_create_task_from_function`（controller.py:1940）依赖 utilities 的 CreateFromFunction。

## ④ 数据流

定义期（本地）：add_step×N 或 @component → DAG 内存结构 → `start()` → 序列化写 controller Task → 投 services 队列。执行期（远程 agent）：pipeline_from_decorator 入口 → `_deserialize` 重建 DAG → `_daemon` 循环：入度清零节点 → `_launch_node`（宏展开→克隆→enqueue）→ 轮询 is_stopped → 完成后 `node.executed=task_id` 解锁下游 → `_monitor_node` 上卷 → 状态写 `pipeline_state` artifact+执行图 → 全终态 → 流水线 Task 置 completed/failed。函数式流水线另有 `_update_eager_generated_steps`（controller.py:4300）处理运行期动态产生的步骤。

## ⑤ 设计决策

1. **Pipeline-as-Task**：控制器自身是 Task，天然获得远程执行/重试/UI/状态持久化——恢复不需要额外存储，状态全在 Task 配置对象与 runtime 属性里。
2. **步骤=克隆 Task+哈希幂等**：`_get_task_hash` 使 `cache=True` 步骤跨运行复用，即"流水线缓存"的全部基础。
3. **`${step}` 宏延迟解析**：发射瞬间才查上游实际值，声明序与执行序解耦。
4. **上卷而非重报**：指标/工件/模型以引用复制挂到流水线 Task，不重复上传。
5. **双 API 一套内核**：装饰器是命令式的语法糖+函数源码序列化，继承保证行为一致。
6. **失败语义四开关**：continue_on_fail/abort × skip_children_on_fail/abort，比全局 abort_on_failure 细一级。

## ⑥ 新人提示（含勘误）

- **勘误 1**：`PipelineDecorator` **继承** `PipelineController`（controller.py:3981，图谱 inherits 边），不是组合——装饰器实例可直接用全套命令式方法。
- **勘误 2**：`pool_frequency` 单位是**分钟**默认 0.2（=12 秒，controller.py:226）；`_monitor_node_interval` 是 5 分钟（controller.py:73）——"指标上卷慢"的答案在这。
- **勘误 3**：`pipeline_execution_queue` 默认 `"services"`（controller.py:5001）；想本地跑控制器逻辑须显式传 `None` 或 `run_locally`（controller.py:5343）——默认把整条流水线逻辑送去远程。
- `Node.executed` 三态：None（未跑）/task_id 字符串（终态）/False（被 skip_children 策略跳过）（controller.py:3391-3397），判空前想清语义。
- `@component` 的 `return_values` 默认 `("return_object",)`（controller.py:4480），不写照样存 artifact。
- 步骤名不许叫 `pipeline`（`_reserved_pipeline_names`，controller.py:68）。

---
**自检报告**：不计空格字符 4654；汉字 819+英文词 338；行号锚 45 个全部 grep -n 核实（正文标注 controller.py:43-5386 与 job.py:516 等）。
