# 07 · Python 适配器三雄：openclaw / codex / deepagents 的同一契约三种集成风格

## 角色定位

Python 适配器群是南向契约在 Python 生态的三种落地形态：**openclaw 是"进程管理器"**——拉起外部 OpenClaw Gateway 子进程、探活、再经回环 HTTP 对话（`adapters/python/openclaw/.../openclaw/adapter.py`，1743 行）；**codex 是"SDK 嵌入者"**——经 `openai_codex` 官方 SDK 驱动 app-server 与 thread（`adapters/python/codex/.../codex/adapter.py`，1725 行）；**deepagents 是"库编译者"**——进程内 import `deepagents`/`langchain` 编译 LangGraph 图并持久化 checkpoint（`adapters/python/deepagents/.../deepagents/adapter.py`，1347 行）。三者实现同一三方法生命周期 start/invoke/stop，文件尾同为 `lifecycle.serve(XxxRuntime, config_loader=AgentConfig.from_mapping)`（openclaw adapter.py:1738、codex adapter.py:1720、deepagents adapter.py:137）。

## 内部结构

**openclaw（进程管理风格）**：常量区钉死唯一受支持版本 `SUPPORTED_OPENCLAW_VERSIONS = frozenset({"2026.9.4"})`（adapter.py:52）与端口派生跨度 `MAX_DERIVED_PORT_OFFSET = 110`（adapter.py:54）。`OpenClawRuntime.start`（adapter.py:995）链路：正则验版本（adapter.py:61）→ 选端口并预检 base 与 base+2（`_select_port` adapter.py:346，浏览器控制端口派生在 base+2）→ `secrets.token_urlsafe(48)` 一次性 token（adapter.py:1049）→ 临时目录写 `openclaw.json` chmod 0o600（adapter.py:1052-1065）→ `config validate --json` 预检（adapter.py:1080）→ 拉子进程装父死亡信号 `setpriv --pdeathsig SIGTERM`（adapter.py:638-654，沙箱禁 capability 时优雅退化）→ `_wait_started` 轮询 `/startupz`（adapter.py:1525）。运行期 `_monitor_gateway`（adapter.py:1406）每 2 秒探活，连续 3 次失败（adapter.py:48）记 gateway 故障。服务化是 openclaw 独有第三形态：prepare/attach/connect 三操作（adapter.py:1006-1018），跨进程凭证经 `_write_service_connection`（adapter.py:731）以 0o600 原子写 JSON。

**codex（SDK 嵌入风格）**：`CodexRuntime`（adapter.py:1329）持有一个 `AsyncCodex` 客户端与一个 thread。start（adapter.py:1349）构建 `CodexConfig`（`sdk_config` adapter.py:894，含 `FABRIC_TEST_CODEX_BIN` 测试钩子）、备 Relay 网关（adapter.py:774）、对 openai provider 用临时 `CODEX_HOME` + `client.login_api_key`（adapter.py:1379-1400）隔离凭证、经 `_register_skill_roots`（adapter.py:321）发底层 `skills/extraRoots/set` 请求注入 Fabric skill 路径——注释明言 pinned SDK 未包装此请求，保留兼容缝。invoke 走 `_invoke_thread`（adapter.py:1212）：`thread.turn()` + `handle.run()`，超时先 5 秒 `_interrupt_turn`（adapter.py:1162）。OAuth MCP 登录甚至开浏览器：`_open_authorization_url`（adapter.py:79）刻意用可取消子进程包 `webbrowser.open`。

**deepagents（库编译风格）**：start（adapter.py:632）直接 `create_deep_agent`（adapter.py:691）建图，配 `AsyncSqliteSaver` checkpointer（adapter.py:416，路径按 runtime_id 的 sha256 命名 adapter.py:410-413）。工具策略用 `ToolGateMiddleware`（adapter.py:86）在 LangChain middleware 层拦 tool call（adapter.py:105），子代理被同策略包裹（`_gated_subagents` adapter.py:571）。

## 外部连接

三者的"外部"语义迥异：openclaw 连**本机子进程+回环 HTTP**（`httpx.AsyncClient` http2=true trust_env=false，adapter.py:1127-1141，URL 锁 `http://127.0.0.1:{port}`）；codex 连 **SDK 管的 app-server JSON-RPC**，health 甚至下钻私有链 `client._client._sync._proc` 做 `process.poll()`（adapter.py:1458-1461）；deepagents **无外部进程**——模型经 `ChatOpenAI`/`init_chat_model` 出网（adapter.py:195-266），图执行全在本进程。共享公共层 `nemo_fabric_adapters.common`（lifecycle/instructions/utils）。MCP 归一同源不同译：openclaw 翻成 `streamable-http` 产 `toolFilter`（adapter.py:409-450）；codex 产 `mcp_servers` 原生键（adapter.py:206）；deepagents 走 `MultiServerMCPClient` 直接换工具（adapter.py:348-356）。

## 数据流

入口统一为 lifecycle JSON（config + runtime_context），输入 `AgentRunRequest`，输出 `AgentRunResult`。差异在中段：openclaw 拼 OpenAI Chat Completions 体 POST `/v1/chat/completions`（adapter.py:558），受 Fabric 截止时间约束 `asyncio.timeout_at(lifecycle.invocation_deadline(context))`（adapter.py:1587）；codex 的 usage 归一最讲究——`_normalize_usage`（adapter.py:1052）对**线程累计总量做差分**而非取末次响应；deepagents 因 checkpointer 回放历史，usage 必须**只聚合本回合 updates 增量**（`invoke_compiled_agent` adapter.py:990 的 stream_mode `["updates","values"]` + subgraphs=True；`_dedup_messages` adapter.py:1234 按 message id 去重防子图重复计数）。

## 设计决策

1. **attach 不可验证即拒绝**：openclaw `_validate_attach_config`（adapter.py:100）把 base_url/tools/mcp/skills 等部署方字段全列 unsupported——宁拒绝不假装。Telegram `apiRoot` 的 HTTP 必须字面回环 IP（adapter.py:224-264）。
2. **环境变量白名单继承**：codex `INHERITED_ENV_NAMES`（adapter.py:107-139）只放约 30 个名字，子环境其余置空（adapter.py:638）；并强制 `CODEX_INTERNAL_ORIGINATOR_OVERRIDE = "codex_python_sdk"`（adapter.py:660）防身份继承产生非法 initialize metadata。
3. **passthrough 白名单**：deepagents `FABRIC_OWNED_AGENT_KEYS`（adapter.py:51-61）禁调用方覆盖 model/tools/backend，`DEEPAGENTS_PASSTHROUGH_KEYS`（adapter.py:65）只放行 JSON 可序列化的 subagents/interrupt_on，未知键报错不静默丢（adapter.py:533-538）。
4. **遥测污染隔离**：deepagents 独有 quarantine——Relay scope 栈被早先回合弄脏后，后续回合跳过请求 scope 打 `_QUARANTINE_NOTE`（adapter.py:72-76）；`_scope_top_unchanged`（adapter.py:1079）以哨兵 `_UNREADABLE`（adapter.py:79）保证检查不因 Relay 改名失效。
5. **本地 shell 否决权**：deepagents `resolve_backend`（adapter.py:269）要求 local_shell 必须有 workspace 且显式 execute 策略（adapter.py:457-462），默认 `FilesystemBackend(virtual_mode=True)`（adapter.py:303）把 agent 关进 workspace。

## 新人提示

阅读顺序建议 deepagents → codex → openclaw（复杂度递增）。先抓共同骨架：Runtime 三方法 + `main()` serve，错误全走 `lifecycle.LifecycleError(code, message, metadata=...)` 且 code 带 harness 前缀；invoke 前都有 runtime_id 匹配检查（openclaw adapter.py:1568、codex adapter.py:1575、deepagents adapter.py:741），这是契约级约定。三处最易抄错：openclaw 的双端口预检、codex 的差分 usage、deepagents 的回放去重。测试对应 `tests/adapters/test_openclaw.py`（1822 行）、`test_codex_adapter.py`（2506 行）、`test_deepagents.py`（2686 行），全部 fake SDK 注入。
