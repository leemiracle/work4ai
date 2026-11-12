# 09 · nooa 适配器与 Harbor 基准群：Dockerfile→适配器的 deploys 边体系

## 角色定位

nooa 适配器是 Fabric 接 NVIDIA 实验室 OO Agents 的双面门面：`adapters/python/nooa/src/nemo_fabric_adapters/nooa/adapter.py`（700 行）跑通用 `InteractiveAgent` 目标，`bench_adapter.py`（403 行）专跑基准用 `BenchAgent`。与 07/08 篇"包一个成熟 harness"不同，nooa 的目标 agent 是**用户经 `workflow.entrypoint.ref` 注册的 Python 工厂**——适配器只定义鸭子类型协议。它俩与 `examples/harbor/` 基准群（calculator/nooa_bench/swebench）构成评估链：Harbor（任务容器/验证/reward/重试）→ FabricAgent（宿主侧组 FabricConfig）→ 容器内 Fabric runner → 适配器 → 目标 agent。README 写死分工："FabricAgent 和 FabricConfig 构造跑在宿主进程；pinned 包、适配器发现、harness 执行、workspace 与 verifier 跑在隔离任务容器内"（examples/harbor/README.md）。

## 内部结构

**adapter.py 是注册协议的执行者**。入口常量 `WORKFLOW_FACTORY_KIND = "interactive_agent_factory"`（adapter.py:38）规定 entrypoint.kind；`_load_factory`（adapter.py:109）解析 `package.module:factory` 形态 ref，逐段 `isidentifier()` 校验后动态加载。工厂收到 `InteractiveAgentBuildContext`（adapter.py:44-56，frozen dataclass：config/models/system_instruction/settings/skill_paths/runtime_id/base_dir/workspace/artifact_root），返回裸 agent 或 `InteractiveAgentTarget`（adapter.py:59-65，可选 `close` 清理与 `continue_after` 续跑谓词）。协议校验 `_validate_agent`（adapter.py:343-360）点名七个必须可调用成员：`agent.handle`、`event_manager.on`、`queue_manager.channels/get_channel/race/shutdown`——纯鸭子类型，目标框架零继承接入。调度核心 `dispatch`（adapter.py:429-455）是 OO Agents 标准唤醒环：文本放进 `user_messages` 通道（adapter.py:434）→ `await queue_manager.race()`（adapter.py:436）→ 排空所有通道 → `await agent.handle(notification)`（adapter.py:445）→ `_reason` 校验返回值必须是 `DONE/NEED_INPUT/GET_USER_INPUT/WAIT` 之一且带非空 explanation（adapter.py:39-40、418-426）→ `WAIT` 续环，终态经 `continue_after` 谓词决定续跑（adapter.py:448-455）。MCP 走 agent 自带 skills registry：`_mcp_registry`（adapter.py:164-177）探测 `agent.skills.register/activate` 后，`MCPManager.create_stdio_server/create_url_server` 建 server、`registry.register("mcp.<name>", tool)` 登记、`activate(registered)` 一次激活（adapter.py:239-292）。invoke 用 `event_manager.on("AgentMessage", capture)` 收集助手消息（adapter.py:620），输出经 `_with_telemetry`（adapter.py:494）附 Relay 遥测块（degraded/quarantine_cause 语义与 deepagents 同款）。

**bench_adapter.py 是每调用一实例的变体**。`BenchRuntime`（bench_adapter.py:193）start 只缓存 BenchAgent 工厂类（bench_adapter.py:222-224）、模型资源与 workspace；每次 invoke 现场 `self._bench_agent_factory(llm=...)` 新建（bench_adapter.py:287），组 `{"user_message", "working_dir", "instructions"}` 输入（bench_adapter.py:301-306），调私有 `agent._run_evaluation(task_input)`（bench_adapter.py:315），token 用量经 `start_task_tokens/get_task_tokens` 对（bench_adapter.py:308-316）。生命周期坑写在注释："BenchAgent 为每个任务创建替换 shell，先关旧 shell 免得持久 runtime 泄漏"（bench_adapter.py:311-313，`_close_shell` invoke 前后各一次）。

**Harbor 三任务的 Dockerfile 即 deploys 边**。calculator 镜像（examples/harbor/calculator/task/environment/Dockerfile）从 `python:3.14-slim` 起步，三层安装对应三种集成风格：`COPY --from=node:24.16.0-bookworm-slim` + `npm install --global openclaw@2026.9.4`（Node 面）、rustup 工具链（Pi 构建面）、一串 `pip install -e` 装 `adapter-contract/python`、`sdk/python/nemo-fabric-runtime`、`adapters/python/{common,claude,codex,openclaw}` 与 `nemo-fabric[claude,openclaw]`（Python 面）。任务规范 task.toml 声明 Harbor schema 1.3：verifier 120s/agent 900s/2CPU/4GB。nooa_bench 镜像（nooa_bench/task/environment/Dockerfile）换 `python:3.12-slim-bookworm` + 本地 wheelhouse + `nemo-fabric-adapters-nooa[full]`，并以一行 import 自检钉住链路，最后 `useradd --uid 10001 fabric` 降权。真 SWE-Bench 镜像（nooa_bench/swebench/Dockerfile）直接 `FROM swebench/sweb.eval.x86_64.django_1776_django-13741:latest` 叠 uv + wheelhouse。

## 外部连接

calculator 的零凭证冒烟路径用"最简适配器"作对照：`fabric/adapters/scripted/scripted.fabric-adapter.json` 声明 `adapter_kind: "process"` + `runner: {command: "python3", script: "run.py"}`——不走模块加载而走子进程。`run.py` 47-61 行手写 stdin JSONL 循环应答 start/invoke/stop，invoke 直接覆写 `/app/calculator.py` 修 bug（run.py:24-31），证明契约最小实现不到 60 行。宿主侧桥 FabricAgent 的 README 映射表把每个 Harbor 输入钉到 FabricConfig 字段：`--ak fabric_adapter_id` → `harness.adapter_id`、`--model` → `models.default`、`--skill` → `skills.paths`；凭证规则同表写明——`fabric_model_api_key_env` 必须配 `--ae` 注入，桥主动拒绝 `MODEL_DSN` 这类 Harbor 无法脱敏的名字。

## 数据流

一次 nooa_bench 基准跑：宿主 `harbor run --path examples/harbor/nooa_bench/task --agent nemo_fabric.integrations.harbor:FabricAgent --ak fabric_adapter_id=nvidia.fabric.nooa.bench-agent ...`（nooa_bench/README.md）→ 容器内 runner 反序列化 FabricConfig → `Fabric.run()` 以任务本地 base_dir 解析适配器与资产 → BenchRuntime start 建模型 → invoke 经 RelayTelemetry 包裹（bench_adapter.py:338-342）→ verifier 跑 `task/tests/verify.py` 出 reward。calculator 的 scripted 流全程无 LLM：同一 task 换 `--ak fabric_adapter_id` 即切五种跑法——任务与验证器固定，实验只改命名输入，证据可归因（README 原话"each experiment changes only the named Harbor input"）。

## 设计决策

1. **鸭子协议优于基类**：nooa 不发布抽象基类，七成员可调用探测（adapter.py:343）让任意框架零改动接入，代价是错误只能在 start 期暴露。
2. **bench 与通用分家**：InteractiveAgent 是持久会话，BenchAgent 是一次性评估器（每 invoke 重建+关 shell），两种生命周期分开两个 Runtime 而非塞开关。
3. **wheel 先行**：`prepare.sh` 以 Maturin+Zig 构建 manylinux 2.17 wheel 进 wheelhouse，解耦宿主 glibc 与 Python 3.12 Debian 镜像。
4. **容器内自检**：Dockerfile 的 import 行让构建期即验证"适配器+harness+relay 版本兼容"。
5. **降权运行**：uid 10001 非 root，与 Harbor 沙盒姿态一致。

## 新人提示

跑例子按 calculator→nooa_bench→swebench 顺序（README 三行表格即此建议）。读代码先看 scripted/run.py 理解契约最小面，再读 adapter.py 的 dispatch 环（429 行起）。`prepare.sh` 产出的 wheel 落在 git 忽略的 vendor 目录，克隆后必须先跑脚本再 build 镜像。别混淆两个 adapter_id：`nvidia.fabric.nooa`（通用）与 `nvidia.fabric.nooa.bench-agent`（基准），用错得到描述符不匹配错误。测试对应 `tests/adapters/test_nooa_adapter.py`（1875 行）、`test_nooa_bench_adapter.py`（431 行）、`test_nooa_relay_compat.py`，e2e 侧 `tests/e2e/test_nooa_bench_harbor.py` 与 `test_harbor_swebench_task.py`。
