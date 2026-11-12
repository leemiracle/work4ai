# 11 · 测试矩阵五路：从契约一致性到 e2e，以及 test_deepagents.py 为何 2686 行

## 角色定位

`tests/` 是质量体系的分层金字塔，五条主路各管一层：**`adapter_contract/`**（4 文件）验契约本体——test_agent_config/test_agent_execution/test_health_contract 校验归一化模型与生命周期语义，test_dependency_boundary 守依赖边界；**`adapters/`**（30 文件约 2 万行）是每适配器单元层，全部 fake SDK 注入跑在无 harness 环境；**`python/`**（34 文件）测 SDK/runtime 本体（test_runtime.py、test_typed_config.py、test_installed_adapter_discovery.py、harbor 桥八件套等）；**`integrations/`**（5 文件）测 Harbor 桥横切面（runner/skills/mcp/telemetry/credentials + test_relay_scope_leak.py）；**`e2e/`**（26 文件）是显式 opt-in 真 harness 冒烟。辅路还有 collector（4）、scripts（15）、docs（2）、examples（2）、_utils（7）与 fixtures（九个夹具环境：alternate/claude/default/file-config-agent/hermes-shim-agent/nooa/nooa_bench/openshell_echo 等）。conftest.py 的 `restore_environ` autouse 夹具（tests/conftest.py:44-60）先兜底：测试动过的环境变量一律还原、新增一律删除——大量适配器靠环境变量传凭证。

## 内部结构

**adapters/ 体量排行直接反映适配器复杂度**：test_deepagents.py 2686 行 > test_codex_adapter.py 2506 > test_claude_adapter.py 2166 > test_adapaters_common_utils.py 1978（common 层最大）> test_nooa_adapter.py 1875 > test_openclaw.py 1822 > test_hermes_adapter.py 1659 > test_external_nat_adapter.py 1503 > test_adapters_common_lifecycle.py 967。头部破千行不是冗余，是每适配器要单测的**归一化矩阵**本身大：模型选择、MCP transport 翻译、工具策略、usage 归一、生命周期错误码，每条路径独立成用例。

**test_deepagents.py 为何 2686 行（92 测试）——三个放大器叠加**：

1. **fake SDK 层自成体系**。docstring 说明立场："stub deepagents/langchain/langgraph SDKs 使测试无需真 harness；真 SDK 由 opt-in 集成测试锻炼"（tests/adapters/test_deepagents.py:5-11）。`fake_sdks` 夹具（test_deepagents.py:157-304，约 150 行）mock 出 create_deep_agent/chat_openai/init_chat_model/fs_backend/local_shell_backend 全家并带录制器断言构造 kwargs；`fake_relay`（test_deepagents.py:346-467）stub nemo_relay plugin + deepagents 集成；`make_payload`（test_deepagents.py:306）是 payload 工厂；更妙的是"局部转真"开关——`use_real_langgraph`（test_deepagents.py:468）与 `use_real_deepagents`（test_deepagents.py:483）用 `monkeypatch.delitem(sys.modules, ...)` 摘掉指定假模块让真包解析，于是 `test_real_langgraph_async_checkpointer`（test_deepagents.py:2007）能在假环境里嵌真 checkpointer。
2. **遥测双失败域的排列组合**。deepagents 适配器把"agent 失败"与"记录失败"分成两个域（adapter 的 TurnOutcome），测试必须穷举组合：`test_relay_scope_teardown_failure_keeps_the_invocation_completed`（:909）、`test_relay_plugin_teardown_failure_keeps_the_invocation_completed`（:944）、quarantine 家族 `test_a_dirty_scope_stack_quarantines_telemetry_for_later_turns`（:972，docstring 写透动机"turn 1 留下的 scope 对 turn 2 仍 current，否则它嵌在陈旧 scope 下还自报干净"）、`test_quarantine_survives_a_stop_and_restart`（:1073）、`test_an_unreadable_scope_handle_counts_as_dirty`（:1128）直到 `test_teardown_and_artifact_faults_are_both_reported`（:1263）。仅遥测块（约 :632-1500）就吃掉近 900 行。
3. **策略面广**：local_shell backend 安全组合（必须 workspace + 显式 execute 策略，:1683-1811 五个测试）、工具门禁 middleware（:1954-2005）、usage 回放只计本回合（:2111）、subgraphs 流（:2234）、持久 runtime 复用编译图与 checkpointer（:2153）。

**e2e 层的 opt-in 协议**：`RUN_FABRIC_DEEPAGENTS_INTEGRATION=1 NVIDIA_API_KEY=... pytest tests/e2e/test_deepagents.py`（tests/e2e/test_deepagents.py:5-7），`pytest.importorskip("deepagents")`（e2e :35）跳过未装环境，模型端点指向本地 api_server mock（e2e :36-38）。e2e 也分层：每适配器 test_<name>.py + test_<name>_checks.py 健康专测（test_openclaw_checks.py 563 行、test_codex_checks.py 235 行）+ 横切 test_checks.py（292 行）/test_swebench_style.py。

## 外部连接

测试矩阵锚定三层外部契约：`adapter-contract/python/` 的模型（adapters 层直接 import `nemo_fabric_adapter_contract.models` 断言 AgentRunResult 形状，test_deepagents.py:26-40）；描述符 JSON 文件（`test_descriptor_declares_supported_normalized_config` test_deepagents.py:52 直接读 `deepagents.fabric-adapter.json` 断言 `system_instruction_modes == ["replace"]` 与 `runtime.max_turns` 在 accepts——描述符与实现互相锁定）；fixtures/ 九个夹具环境（hermes-shim-agent 含自己的 23 行迷你 adapter.py 充当"最小适配器被测方"，tests/fixtures/hermes-shim-agent/adapters/hermes-shim/adapter.py）。conftest 会话级夹具 `requires_harbor`（conftest.py:32）/`requires_hermes_agent`（conftest.py:39）用 import 探测决定跳过，integrations 层缺包不红。

## 数据流

典型单元流：make_payload 造 lifecycle payload（base_dir 指 tmp_path）→ fake_sdks 已 monkeypatch 掉 SDK import → 直接 `adapter.DeepAgentsRuntime()` 调 start/invoke/stop → 断言 `result_view(result)`（test_deepagents.py:121 把 AgentRunResult 转可比 dict）与录制器捕获的构造 kwargs。集成链反向：e2e 起真 runtime（`async with await Fabric().start_runtime(config, base_dir=tmp_path)`，e2e test_deepagents.py:50-52），invoke 两次验多轮连续性，再 `assert_atof_model`（e2e :26 从 _utils.utils 引入）核对 Relay ATOF 工件——测试穿透到落盘遥测。

## 设计决策

1. **假 SDK 而非真子进程**：adapters 层 30 文件全 mock——CI 无需装 16 个 harness（多为商业 CLI），且能断言"适配器给 SDK 传了什么"而不仅"结果对不对"。
2. **描述符即断言对象**：把 JSON 描述符当被测代码读（test_deepagents.py:52），契约文档漂移在测试层爆掉。
3. **quarantine 语义测到病态级**：连"scope handle 不可读"（:1128）、"干净解栈不误伤"（:1143）都有专测——遥测可信度被当产品特性。
4. **opt-in e2e 物理分目录**：默认 pytest 跑不了 e2e（需环境变量+真 harness+key），保证本地 `pytest tests/adapters` 永绿。
5. **每适配器双文件**（test_x.py + e2e/test_x_checks.py）：健康检查（live/active/ready 三级）单独立 e2e，只有真 harness 才暴露真实探针行为。

## 新人提示

跑测试先 `uv run pytest tests/adapters/test_deepagents.py -x` 感受节奏；读大文件别顺序读，先 `grep -n "^async def test\|^def test"` 列 92 用例再按主题跳（遥测 :632-1500 / backend :1583-1811 / MCP :1870-1953 / usage :2068-2180）。写新适配器测试照抄 deepagents 三夹具骨架（fake_sdks/make_payload/fake_relay）能省半天。conftest 的 `restore_environ` 是 autouse——测试里 set 的环境变量出函数即失效，跨测试传态走 fixture 返回值。改适配器行为先找"keeps_the_invocation_completed"型测试，它们是最易破坏的语义合同。`.agents/skills/python-tests` 维护者技能有完整测试命令集。
