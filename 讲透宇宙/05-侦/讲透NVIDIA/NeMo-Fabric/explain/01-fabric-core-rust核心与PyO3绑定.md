# 01 · fabric-core Rust 核心与 PyO3 绑定

> 仓库：NVIDIA/NeMo-Fabric @ 86f86882（v0.6.0） · 行号锚全部源码核实

## 一、角色定位

`crates/fabric-core` 是整个 NeMo Fabric 生态的**语言中立内核**。"一份版本化契约、三种语言投影"——Python SDK、TS 适配器、JSON Schema 全部是这份 Rust 内核的同构翻译。lib.rs:6-19 声明 14 个子模块（adapter_contract/agent_config/agent_execution/check/config/doctor/environment/error/resource_snapshot/runtime/schema/system_stats/task_command/time），lib.rs:21-73 的 `pub use` 一次性扇出上百个公共类型，构成下游唯一导入面。

workspace 层面，Cargo.toml:4-12 组四成员（fabric-core/fabric-cli/fabric-python/environment-providers/openshell），版本 0.6.0（Cargo.toml:22）、edition 2024（:23）。文件规模"两大三中"：config.rs 7535 行与 runtime.rs 6629 行占核心 22320 行近三分之二，check.rs 1721/environment.rs 1526/resource_snapshot.rs 1289 次之，schema.rs 704/agent_config.rs 518/agent_execution.rs 470/error.rs 422/system_stats.rs 385 收尾，外加 system_stats/（cgroup.rs 788+sampling.rs 802）与 runtime/openshell.rs 1000 行（runtime.rs:40 `mod openshell`）。

## 二、内部结构（带行号）

**契约元数据**：adapter_contract.rs:10 定义 `ADAPTER_CONTRACT_VERSION = "fabric.adapter/v1alpha2"`——南向契约线格式版本，跨进程握手都比对它。AdapterExtensionPoint 枚举列 18 个可扩展块（adapter_contract.rs:17-54），ALL 常量数组（:57）供 descriptor 校验遍历。

**配置树**：config.rs:32 的 `FabricConfig` 是北向根，16 个顶层字段（schema_version/metadata/harness/workflow/discovery/models/instructions/runtime/environment/tools/skills/mcp/telemetry/system_stats/relay），:76-78 的 `extensions` 用 `#[serde(default, flatten)]` 收容"本版本尚未识别的加性字段"——契约前向兼容的关键。AdapterDescriptor（:324）声明适配器身份/runner/接受字段；解析链 load_adapter_descriptor（:1856）→ resolve_run_plan_from_config（:2399，_with_adapter_directories 变体 :2412 供 PyO3 注入安装发现目录）→ inspect_adapter_config（:2441，只查元数据不探测可执行位置）→ resolve_diagnostic_plan（:2492，doctor 用）。

**运行时引擎**：私有 trait RuntimeAdapter（runtime.rs:840）抽象 start/invoke/invoke_openai_stream/stop 四动作，双实现：LocalHostAdapter（:860，本地子进程宿主；LocalAdapterHost 持 child/stdin/responses channel，:877-879 注释钉死"适配器启动值只留内存，绝不进序列化 handle 或 plan"）与 OpenShell 后端。公开 API 函数族：run_plan（:900，start→invoke→stop 一锤子）/prepare_environment（:931）/prepare_service（:984）/start_runtime_with_service（:994）/release_service（:1034）/start_runtime（:1195）/invoke_runtime（:1208）/invoke_openai_stream（:1269）。三类 handle EnvironmentHandle（:342）/RuntimeHandle（:372）/ServiceHandle（:421）都是可序列化值对象，跨进程传递无状态负担。

**健康检查**：check.rs 五枚举层（CheckLevel/CheckStage/CheckOutcome/CheckReason，:40-125）+ CheckReport（:407）；check_service（:765）/check_environment（:897）两入口，HMAC 健康码验证+本地 TCP 探测。

**错误模型**：error.rs 单枚举 41 变体（thiserror），从 :18 ResolveBaseDirectory 到 :416 ParseJson 覆盖全部失败面。

**Schema 导出**：schema.rs:26 SchemaName 枚举 27 项，:86 `ALL: [Self; 27]`，:266 write_schema_snapshots 落盘 schemas/——SCHEMA.md:9-10 钉版"由 Rust 类型生成非手编"。

## 三、外部连接

- **PyO3 绑定**：fabric-python/src/lib.rs:4 声明"Python native bindings"；#[pymodule] _native（lib.rs:353-385）注册 19 函数+3 异常；全部数据交换走 JSON 字符串（lib.rs:567-601 的 parse_config/parse_run_plan 等 9 个反序列化函数）。
- **fabric-cli**：plan/doctor/run 命令直接调 core 的 resolve/inspect 函数族。
- **Python SDK**：_native.pyi 为 20 函数提供类型桩；client.py:57 动态 import，失败降级。
- **OpenShell 提供器**：environment-providers/openshell 独立二进制与 core 的 runtime/openshell.rs 调用侧配对。

## 四、数据流

北向 run_config 为例：Python 传 config_json → fabric-python lib.rs:110 run_config 反序列化 → resolve_context（lib.rs:409）定 base_dir 与描述符目录（data_path/share/nemo-fabric，:425）→ core 产出 RunPlan → run_plan（runtime.rs:900）内部 start→invoke→stop → RunResult 序列化回传。

所有绑定函数用 `py.detach(...)` 包裹重活（lib.rs:60 等十几处）——释放 GIL。ADAPTER_PYTHON 环境变量（lib.rs:41）可指定适配器专用解释器，query_python_data_path_with_timeout（:449-522）子进程查询 sysconfig，5s 超时（:42）+10ms 轮询（:43）超时即 kill——内嵌测试 :533 用死循环脚本验证。

## 五、设计决策

1. **JSON 边界而非对象边界**：绑定不暴露 Rust 对象，全部 JSON 往返（to_json 用 to_string_pretty，lib.rs:387-392）。牺牲序列化开销，换绑定层零类型耦合——Rust 演进不需同步改 PyO3 签名，schema 快照即接口文档。
2. **错误按语义映射**：to_py_error（lib.rs:394-407）把 host_timeout 映射 PyTimeoutError、资源观测双错误映射专用异常（lib.rs:22-39 pyo3::create_exception!）——Python 侧可按异常类型精确重试。
3. **flattened extensions**：未知字段以 JSON 值透传给声明支持它的适配器，旧核心读新配置不报错。
4. **handle 可序列化但密钥不序列化**：敏感值只存 LocalAdapterHost 内存（runtime.rs:877-879 注释）。
5. **schema 校验留在 Rust**：Cargo.toml:30-35 注释解释——schemars 只生成不校验，委托 Python 会破坏语言中立边界，jsonschema 0.49 是"有正确诊断的最窄选项"。

## 六、新人提示

- 读码顺序：lib.rs（模块地图）→ adapter_contract.rs（100 行最快全景）→ runtime.rs:840 trait → config.rs FabricConfig → 再钻两大文件实现。
- config.rs/runtime.rs 前半是"契约区"（struct 密集），后半是"过程区"，按需读。
- doctor（doctor.rs 777 行+doctor_plan）是"配置为什么解析失败"的调试捷径。
- OpenShell 后端从 runtime.rs:40 进 runtime/openshell.rs（1000 行），再对照提供器侧 lib.rs（3397 行，见第 2 篇）。
- 41 个错误变体（error.rs）是排障字典：错误信息 stage/code 与变体一一对应，先在 error.rs 找变体再看触发点，比全文搜索快。
