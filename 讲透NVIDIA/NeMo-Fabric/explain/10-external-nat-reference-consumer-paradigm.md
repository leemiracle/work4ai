# 10 · external/nat 参考适配器与 consumer 范式：第三方接入的样板间

## 角色定位

`external/` 是给第三方适配器作者的"样板间"——README 开宗明义："source-only reference adapters，行使公开适配器契约而不成为 bundled 适配器；不发布 wheel、不进 bundled 或 installed-adapter discovery；打包与发现是从契约中分离的关注点"（external/README.md）。唯一住户 nat（NeMo Agent Toolkit）参考：`external/nat/src/nemo_fabric_adapters/nat/adapter.py`（973 行）+ 描述符 `nat.fabric-adapter.json` + 两个 target 描述符（targets/calculator.fabric-target.json 等）+ 三个可跑示例（examples/calculator.py 等）。它示范 bundled 适配器刻意不做的形态：**目标由 target 注册、组件经入口点安装、流式经 schema 探测**。互为表里的是 `examples/langgraph_custom_agent/` 的 consumer/adapter/agent 三分目录——教你从消费者侧接自定义 agent。

## 内部结构

**配置翻译层是主体**。`build_nat_config_mapping`（adapter.py:619-628）把 typed AgentConfig 编译成 NAT 内存配置 dict，四个子编译器各有铁律：`_nat_workflow`（adapter.py:95-130）要求 `entrypoint.kind == "factory"` 且 ref 必须是 `fabric.agent.react`（常量 adapter.py:36），用户 settings 写 `_type` 被拒（adapter.py:119-124），翻译侧才注入 `workflow["_type"] = "react_agent"`（adapter.py:127）；`_nat_llms`（adapter.py:187-225）把 provider `nvidia` 映射为 NAT 的 `nim`（adapter.py:179-184），并拦截 `RESERVED_MODEL_SETTINGS`（adapter.py:44-56 九键）防调用方替换归一化模型字段；`_nat_tool_component`（adapter.py:133-153）把 `tools.definitions.<name>` 的 `ref` 变成组件 `_type`——README 强调"没有 Python callable 穿越配置契约"，自定义函数必须打包成已安装 NAT 组件经 ref 选择；`_apply_system_instruction`（adapter.py:232-259）只接受 `mode="append"`，映射进 react_agent 的 `additional_instructions`，与 settings 同名键冲突报错。最讲究的是 MCP 与工具策略合成：`_mcp_group`（adapter.py:329-363）把每个 MCP server 变成 `_type: mcp_client` 的 function group，注释点破 NAT 约束"include 与 exclude 不能共存——非空 allowlist 在互斥 blocklist 施加后本就是有效暴露集"（adapter.py:357-359）；空 allowlist 意味零工具暴露，`_apply_mcp_servers`（adapter.py:366-402）顺手从 workflow `tool_names` 摘除防既有引用复活。组内成员选择用 `__` 分隔符语法（adapter.py:37，`_group_member_identity` adapter.py:405-411）：`tools.enabled` 写 `group__member` 即只放行组内特定工具，`_apply_enabled_tools`（adapter.py:470-525）为选择器克隆 group 改写 include，`_apply_blocked_tools`（adapter.py:552-569）对组成员增补 exclude 或 include 耗尽时整组摘除。

**运行时层薄如纸**。`NatRuntime`（adapter.py:715）start 经 `build_nat_config`（adapter.py:631-651）先 `discover_and_register_plugins(PluginTypes.CONFIG_OBJECT)` 再 `Config.model_validate`（adapter.py:640-644）——让 NAT 自己的插件体系验证翻译结果；随后一个 `AsyncExitStack` 管 `WorkflowBuilder.from_config` 与 `SessionManager.create(shared_builder=...)`（adapter.py:756-763）。invoke 每次 `sessions.session(**kwargs)` 开会话、`session.run(input, runtime_type=RUN_OR_SERVE)` 进 runner、`await runner.result()`（adapter.py:797-802）。流式是第二入口 `invoke_openai_stream`（adapter.py:830-950）：先探测 `get_workflow_streaming_output_schema()`，只有声明 `ChatResponseChunk`（adapter.py:845-848）才走 `runner.result_stream(to_type=ChatResponseChunk)` 单次消费（adapter.py:880），逐 chunk `to_jsonable_python` 后 `emit(serialized)` 并拼接 choice 0 的 `delta.content`（adapter.py:904-914）；schema 不符先于开会话报 `nat_openai_stream_unsupported_schema`（adapter.py:859-863）。

## 外部连接

`nat.fabric-adapter.json` 是描述符范本：`contract_version: fabric.adapter/v1alpha2`、`adapter_kind: python`、`target_types: ["workflow"]`、`runner.module`、`tool_definition_schema` 用 JSON Schema 声明 kind/ref/settings 三键（settings 禁 `_type`）、`capabilities` 四布尔里只有 `streaming: true`——README 自述"第一版参考不声称取消、服务或热更新支持"。target 描述符（targets/calculator.fabric-target.json）是另一方向：`id: nvidia.examples.nat.calculator` 绑定 adapter_id，`spec.entrypoint` 固定 factory/fabric.agent.react，`settings_schema` 要求消费者提供 `llm_name`。consumer 侧连接在示例里最直观：`examples/calculator.py` 的 `build_config()` 用 `DiscoveryConfig(local_paths=[...])` 指向 external/nat 目录 + `WorkflowConfig(target_id="nvidia.examples.nat.calculator", settings={"llm_name": "default"})`（calculator.py:43-49）。langgraph_custom_agent 的 consumer/config.py 同构：`DiscoveryConfig(local_paths=[DESCRIPTOR_DIRECTORY])` + `HarnessConfig(adapter_id="nvidia.fabric.example.langgraph.email-phishing", resolution="preinstalled")`（config.py:53-56），模型/指令/Relay 全 typed Pydantic。

## 数据流

完整翻译链：`FabricConfig.workflow.target_id` → planning 解析 target 描述符 → `AgentConfig.workflow.{entrypoint,settings}` + `tools.definitions` → adapter.start 编译 NAT 内存配置 → `Config.model_validate` → WorkflowBuilder/SessionManager 常驻 → invoke 的 request.context 三键（user_id/conversation_id/user_message_id，`_session_kwargs` adapter.py:654-673，缺省 user_message_id 取 runtime request_id）映射 NAT 会话身份 → result 经 `to_jsonable_python(serialize_unknown=False)` 序列化（adapter.py:815-818），非 JSON 结果单独报 `nat_result_not_json_serializable`（adapter.py:824-827）。流式终值是拼接串非末 chunk（adapter.py:950）。

## 设计决策

1. **描述符即合同**：能力边界（capabilities）、接受字段（config.accepts）、工具定义形状全写进 JSON 描述符，runtime 只是履约——planning 期能凭描述符拒绝不支持的配置而不必启动适配器。
2. **归一化字段主权**：settings/model/tool 三处保留字拦截（`_type`、RESERVED_MODEL_SETTINGS）贯彻同一原则——Fabric 拥有可移植字段，调用方只在空白处填空。
3. **schema 探测代替版本分支**：流式支持与否看输出 schema 是否 ChatResponseChunk 而非 NAT 版本号（README："checks the schema rather than branching on a workflow name"），1.7.0/1.8.0 通吃。
4. **参考与产品分居**：external/ 不进包不进 discovery；langgraph_custom_agent 把 consumer/adapter/agent 三责任物理分目录，agent/ 的 graph.py 零 Fabric import。
5. **append-only 指令**：react_agent 无原生替换缝就拒绝 replace，宁窄勿假。

## 新人提示

把 nat 当"如何写第三方适配器"教材读：先读 `nat.fabric-adapter.json` 与 README 字段映射表（models→llms、definitions→functions/function_groups、mcp→mcp_client 组），再顺 `build_nat_config_mapping` 一条链到底。跑起来只需 `external/nat/examples/calculator.py` 加 NVIDIA_API_KEY。`__` 组成员选择语法易被忽略，却是 MCP 工具粒度管控关键。对照阅读：bundled 侧 deepagents（07 篇）用 middleware 门禁解决同类问题，nat 用配置改写 include/exclude——同一契约两种工具策略哲学。测试在 `tests/adapters/test_external_nat_adapter.py`（1503 行），e2e 依赖已装 `nat` 包。
