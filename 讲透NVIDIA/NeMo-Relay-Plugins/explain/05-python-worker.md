# 05 · worker.py：六钩子 Python worker 范式与测试防线

> 路径约定：裸 `:N` 锚均指最近的全路径锚所属文件；所有行号经源码实证。

## 角色定位

575 行的 worker.py 是插件著作文档同款 grpc-v1 worker（docstring 明示，`plugins/example-python-grpc-worker-plugin/nemo_relay_python_grpc_worker_example/worker.py:4`）：从一份显式配置安装全部安全注册面。与 explain/04 逐钩子对应，差异仅在进程形态——Relay 按 `load.runtime="python"` + `entrypoint="nemo_relay_python_grpc_worker_example.worker:main"`（`plugins/example-python-grpc-worker-plugin/relay-plugin.toml:30-31`）拉起独立进程经 gRPC 通信。它是写 Python 插件的唯一模板。

## 内部结构

**配置双表**：DEFAULT_CONFIG（`plugins/example-python-grpc-worker-plugin/nemo_relay_python_grpc_worker_example/worker.py:33-54`）给六组配置完整默认值；`GROUP_FIELDS`（`:56-71`）是各组允许字段白名单——校验与归一化共用同一份真值；`normalized_config`（`:485-497`）做默认值+用户覆盖的组级合并。

**类骨架**：`ExamplePythonWorker(WorkerPlugin)`（`:74`）声明 plugin_id 与单组件限制（`:77-78`）。`validate` 委托模块级 `validate_config`（`plugins/example-python-grpc-worker-plugin/nemo_relay_python_grpc_worker_example/worker.py:358-482`）：未知字段 Error（`:366-371`）、布尔/整数/字符串数组逐路径类型检查（`:397-460`）、kinds 须命中枚举（`:433-449`）、mode 只许 observe/enforce（`:472-481`）。`register`（`:85-120`）先复跑校验并拒绝带 Error 的配置（`:86-91`），再按开关装配四组注册。

**六钩子装配**（主体）：

1. 注册管控（`:100-112`）：按前缀拦截其他注册。
2. 观测 `_register_observation`（`plugins/example-python-grpc-worker-plugin/nemo_relay_python_grpc_worker_example/worker.py:122-196`）：事件元数据注入器（`:126-129`）、订阅者（`:131-136`）、事件/工具/LLM 三类九个脱敏守卫（`:138-170` + 批量注册 `:172-196`）——LLM 请求侧 codec decode→redact→encode 往返（`:156-164`）。
3. 请求 `_register_requests`（`plugins/example-python-grpc-worker-plugin/nemo_relay_python_grpc_worker_example/worker.py:198-275`）：工具策略守卫（`:211-214`）、工具请求打标（`:216-224`）、LLM 模型黑名单（`:226-231`）、LLM 请求拦截（`:233-262`）——`LlmRequestInterceptOutcome` 同打包请求改写+pending_marks+optimization_contributions（`:251-262`）。
4. 运行时 `_register_runtime`（`:277-294`）：包装工具执行拦截发 runtime 事件。
5. 执行 `_register_execution`（`plugins/example-python-grpc-worker-plugin/nemo_relay_python_grpc_worker_example/worker.py:296-355`）：工具注解保留上游结果（`:301-322`）、`repeat_downstream` 用 `asyncio.gather(..., return_exceptions=True)` 并发重调取首个成功（`:324-334`）、流式逐 chunk 惰性打标（`:336-345`）。
6. 生命周期辅助 `_emit_runtime_events`（`plugins/example-python-grpc-worker-plugin/nemo_relay_python_grpc_worker_example/worker.py:500-524`）：push/pop scope 的 try/except 保证失败也关 scope（`:506-516`），隔离 scope 栈用完即弃（`:517-524`）。

`main`（`plugins/example-python-grpc-worker-plugin/nemo_relay_python_grpc_worker_example/worker.py:559-571`）是 entrypoint 真身：非 Windows 直接 `serve_plugin`；Windows 先 `SIG_IGN` 屏蔽 Ctrl+C（`:565-571`）——控制台信号是进程树级的，worker 须等 Relay 经 gRPC 下发关闭。

## 外部连接

- **SDK**：`nemo_relay_plugin` 的 WorkerPlugin/PluginContext/各 Outcome 类型（`plugins/example-python-grpc-worker-plugin/nemo_relay_python_grpc_worker_example/worker.py:15-31`）。
- **构建三阶段**：`plugins/example-python-grpc-worker-plugin/tasks.py`——build 用 `uv sync --locked + uv build`（`:16-34`）、test 用 `uv run --locked pytest`（`:37-56`）、package 拷源码包+锁文件+schema+LICENSE 进 bundle（`:59-78`）。
- **manifest 契约**：worker_protocol=grpc-v1（`plugins/example-python-grpc-worker-plugin/relay-plugin.toml:12`），`integrity.sha256` 钉住 worker.py 本身哈希（`:27-28`）——改一行必须重打包。
- **平台面**：`plugins/example-python-grpc-worker-plugin/release.toml:8` 只声明 linux-x86_64/linux-arm64/windows-x86_64/macos-arm64 四平台（无 musl/arm64 Windows）；`[relay]` 钉测试宿主 sha（`:46`）。
- **对照实现**：Rust worker（`plugins/example-rust-grpc-worker-plugin/src/lib.rs`，446 行）逐钩子对应。

## 数据流

Relay 读 manifest → 验 sha256 → 建 Python 环境 → 起 `main` → `serve_plugin` 进 gRPC 循环 → validate/配置 → register 装配钩子。一次工具调用：请求脱敏 → 策略守卫 → 请求拦截打标 → 执行拦截（注解+pending mark）→ 响应脱敏；LLM 调用同构外加流式通道；runtime 事件反向流回 Relay。

## 设计决策

1. **校验先于一切**：register 入口重跑 validate 并抛首个 Error（`:86-91`）——堵住"跳过 validate 直接 register"的半装配路径。
2. **回调闭包化、注册点集中**：钩子是捕获配置的局部函数（`:211-231`），注册点集中三段（`:172-196`/`:264-275`/`:347-355`）——审阅一眼看全注册面。
3. **Windows 信号语义显式化**（`:565-571`）：测试 `test_windows_worker_leaves_shutdown_to_relay`（`plugins/example-python-grpc-worker-plugin/tests/test_worker.py:259`）与 Unix 对照（`:286`）锁死该行为。
4. **失败也要关 scope**（`:506-516`）：异常路径 pop 带 failed 标记，pop 自身失败吞掉保原异常——可观测性不破坏正确性。
5. **未知字段 Error**（`:366-371`）：与 native 示例的 Warning 取舍相反（explain/04 决策 6）；worker 跨进程更难调试，宁严勿松。
6. **测试即契约**：manifest 哈希与源码绑定（`plugins/example-python-grpc-worker-plugin/tests/test_worker.py:93`）、协议版本（`:101`）、entrypoint 真能 serve（`:243`）、注册面全量（`:298`）、流式惰性（`:596`）——manifest/入口/钩子三层原子覆盖。

## 新人提示

- **测试规模口径**：`test_worker.py` 共 36 个测试函数（`:93-596`），两处 `parametrize`（`:153-154` 三参数、`:204-214` 三案例）展开后 40 个收集项；任务书"37 测试"与源码不符，以源码为准。
- 改 worker.py 任何一行都要重新生成 bundle——manifest 哈希测试（`:93`）立刻红。
- `example` fixture 从插件项目根 fresh import（`:35-53`）——新 worker 测试沿用。
- 配置 schema 与 GROUP_FIELDS 必须同步演化，`test_schema_declares_only_supported_groups`（`:107`）守线。
- gRPC 导入是每个声明平台必须装的隐式契约（`plugins/example-python-grpc-worker-plugin/tests/test_worker.py:26` noqa 注释）。
