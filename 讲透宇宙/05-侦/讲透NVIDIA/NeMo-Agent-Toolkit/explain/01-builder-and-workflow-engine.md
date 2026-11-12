# 01 Builder 与 Workflow 引擎：NAT 的装配线

覆盖 `nat/builder/{builder,workflow_builder,workflow}.py`、`nat/cli/type_registry.py`、`nat/runtime/loader.py`（均在 packages/nvidia_nat_core 下）。

## 一、角色定位

这组文件是 NAT 的"依赖注入容器 + 装配线"。YAML 变成可运行 agent 的全链路在这里：`load_config` 读 YAML 并校验（loader.py:69）→ `WorkflowBuilder.from_config`（workflow_builder.py:1612）按依赖拓扑序把 LLM、工具、中间件逐个实例化 → `build()`（workflow_builder.py:450）产出 `Workflow`（workflow.py:39）→ `Workflow.run()`（workflow.py:100）交给 runtime 的 `Runner`（runner.py:52）。"哪种 config 对应哪个构建函数"的目录由 `GlobalTypeRegistry`（type_registry.py:1423）全进程维护。一句话：registry 是菜单，builder 是厨房，Workflow 是端出来的菜。

## 二、内部结构

**Builder 抽象（builder.py:75）**是纯接口层，895 行几乎全是 `@abstractmethod` 供给方法，按组件类型成对出现：`add_function`（builder.py:102）、`get_tools`（builder.py:230，按 LLM 框架包装）、`add_llm`（builder.py:258）、`add_memory_client`（builder.py:450）、`add_middleware`（builder.py:747），另有微调 `add_trainer`（builder.py:558）与 test-time compute `add_ttc_strategy`（builder.py:679）。每个 add/get 都伴 `get_*_config`，config 与实例双轨可查。文件尾 `EvalBuilder`（builder.py:796）是评测专用接口，由 `WorkflowEvalBuilderBase`（workflow_builder.py:1619）组合。ContextVar `_current_builder_context`（builder.py:72）+ `Builder.current()`（builder.py:78）让任何构建函数内都能取当前 builder——插件代码只收 config 参数却拿得到全局供给的秘密在此。

**WorkflowBuilder 实现（workflow_builder.py:319）**。构造时 registry 缺省取 `GlobalTypeRegistry.get()`（workflow_builder.py:327）。内部状态是 13 个 `Configured*` 字典（ConfiguredFunction :115、ConfiguredLLM :127 等），dataclass 把 config 和 instance 捆在一起——双轨记录使 `build()` 既能导出完整 Config 又能复用实例。生命周期靠 `async with`：`__aenter__`（workflow_builder.py:366）装 logging 与 telemetry exporter，组件上下文统一压进 `AsyncExitStack`。核心装配 `_build_function_impl`（workflow_builder.py:226）四步：registry 查 registration → 探测框架（:252）→ `enter_async_context(build_fn(...))`（:255）→ 归一化返回值为 `Function` 并挂 middleware。`populate_builder`（workflow_builder.py:1408）是 config 驱动主循环：`build_dependency_sequence`（component_utils.py:280，:1418 调用）算拓扑序，按 ComponentGroup 分派到各 add_*，per-user 组件跳过留给懒构建（:1455），`set_workflow`（:1518）装入口，`_validate_dependencies`（:1531）校验共享组件不得依赖 per-user 组件。

**Workflow（workflow.py:39）**是产出物：持 entry_fn、组件实例字典、`ExporterManager`（workflow.py:70）和一份 `contextvars.copy_context()` 快照（workflow.py:80）——serve 场景 HTTP 请求跑在与构建期不同的 async 上下文，需恢复构建期 ContextVar。`from_entry_fn`（workflow.py:133）动态生成携带泛型 schema 的子类。

**GlobalTypeRegistry（type_registry.py:1423）**：类级单例（type_registry.py:1425）包装 `TypeRegistry`（type_registry.py:455），按族存取 `register_function`/`get_function`（type_registry.py:727/737）、`register_llm_provider`（:836）、`register_llm_client`（:878）、`register_tool_wrapper`（:1112）等。最妙在文件尾（type_registry.py:1448）：每次注册变化触发 `Config.rebuild_annotations()`，pydantic Config 动态长出新组件字段——registry 与 config schema 活联动，不是两份手工同步清单。

**插件发现（loader.py）**：`discover_entrypoints`（loader.py:128）扫 `nat.plugins` 等 entry point 组；`discover_and_register_plugins`（loader.py:175）逐个 `entry_point.load()`，import 副作用完成注册。

## 三、外部连接

向上依赖 `nat.data_models.*` 的 pydantic config 类与 component_utils 拓扑排序；向下被 `load_workflow`（loader.py:97）消费，front_ends、eval、data_flywheel（经 `add_telemetry_exporter` :1387 注册）都建在 Workflow 之上。`ChildBuilder`（child_builder.py:64）是依赖追踪代理：`ChildBuilder.use` 包住每次构建（workflow_builder.py:607），覆写 get_* 把消费记入 `FunctionDependencies`，退出时恢复原 ContextVar（child_builder.py:375）。

## 四、数据流

一次 `nat run/serve`：YAML → `load_config`（loader.py:69）→ `from_config`（loader.py:115）→ `populate_builder` 按拓扑序逐组件 resolve（LLM 先于引用它的 agent）→ `build()`（workflow_builder.py:450）：收集 function group 展开的 included functions（:485）、组装 Config、`Workflow.from_entry_fn`（:543）→ 运行期 `Workflow.run(msg)` → `Runner`。调用方三种取结果姿势：`result()`（runner.py:160）、`result_stream()`（runner.py:258）、`result_with_steps()`（workflow.py:116，内部 `pull_intermediate` workflow.py:120 抓中间步骤流——eval 收集轨迹正走此通道）。

## 五、设计决策

1. **config 驱动 + 拓扑构建**：YAML 只做声明，实例化顺序由依赖图决定，不写初始化代码。
2. **add/get 与 wrapper 分离**：LLM 只实例化一次，各 agent 按自己的 `LLMFrameworkEnum` 取包装客户端（get_llm :869 经 `get_llm_client` :879 查 wrapper 注册表）；工具同理（get_tool :832）。一套底座适配多框架，是 NAT 支撑十余个 agent 框架包的机制基础。
3. **AsyncExitStack 统一生命周期**：组件 build_fn 都是 async context manager，退出即清理。
4. **profiler 钩子可选注入**：`detect_llm_frameworks_in_build_fn` 在 workflow_builder.py:93-102 是 try-import，真身在独立包 `nvidia_nat_profiler`（utils.py:36，源码级扫描 build_fn 引用哪些 LLMFrameworkEnum 并递归追 helper；`chain_wrapped_build_fn` 真身 framework_wrapper.py:198）。未装 profiler 时 workflow_builder.py:98 的 stub 返回空表、透传原 build_fn。勘误：任务书把 workflow_builder.py:98 当钩子本体，实际那只是 ImportError 降级 stub。
5. **输出通道**：Workflow schema 只有 streaming/single 两条输出通道（workflow.py:83/88）；任务书"三种输出形态（streaming/single）"与源码不符，更准确是第四节的三种取结果姿势。
6. **ContextVar 快照**（workflow.py:80）：为 serve 场景跨 async 上下文保真。

## 六、新人提示

上手顺序：先通读 builder.py:75 接口面，再精读 `_build_function_impl`（workflow_builder.py:226）即懂 80% 装配机制，然后跑通任一 example。坑：① 忘 `async with WorkflowBuilder()` 直接用，`_get_exit_stack`（workflow_builder.py:579）会明确报错；② 函数组工具名用 `__` 分隔（function.py:407），旧配置的 `.` 是 legacy 兼容（function.py:410）；③ 自定义组件 build_fn 必须是 async context manager 且返回 Function/FunctionInfo/裸函数之一（workflow_builder.py:260-268 归一化）；④ 组件注册靠 import 副作用，registry 变更实时改写 Config 字段（type_registry.py:1448），"config 不认识我的类型"先查 entry point 是否被 load。
