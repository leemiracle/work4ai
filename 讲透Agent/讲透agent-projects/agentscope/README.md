# agentscope（agentscope-ai/agentscope，34.8k★）全链知识库

阿里通义多智能体框架。本地仓 `/usr-data/data2/repos/agent-repos/agent-projects/agentscope`（commit f5e4d380 时锚定）。

## 全链状态表

| 环节 | 状态 | 产物 |
|---|---|---|
| DeepWiki | ✅ TRUE_100（2026-10-29 轮） | `deepwiki/` |
| understand 图谱 | ✅ 557n/1554e/16层/15步tour · validator 0 issues · fingerprints 568@f5e4d380 | 仓内 `.understand-anything/knowledge-graph.json` |
| ONBOARDING | ✅ 5990 字符（不计空格）/55 锚/8 节 | `onboarding/ONBOARDING.md` |
| explain | ✅ 12 篇 49,130 字符/229 锚（2026-11-01） | `explain/01-12` |
| 锚终验 | ✅ 主会话独立抽验 16 锚：15 好/0 坏/1 语义消歧（realtime/_base.py 按篇主题归位） | — |

字数口径=不计空格总字符（SB3 轮钉版双轨口径）。explain 六节结构：角色定位/内部结构/外部连接/数据流/设计决策/新人提示。

## 图谱口径钉版（2026-10-31 wave#2）

- 44 批 568 文件中 **62% 为 examples/docs/tests junk**（354 文件）——采用**跳批处置**：只分析 15 个纯 SRC 批（src 全 204 文件+根 6 文件），26 junk 批不派，3 个误派 junk 产物（b5/b14/b16/b17）隔离 `intermediate/quarantine-junk/`。等效于裁剪 re-prepare，省 29 批。
- 验收：fileNodes 210/210 与 SRC 批文件集精确对齐、junk 残留 0。

## 勘误精选（全部源码行号实证）

1. **Gemini realtime 把 api_key 明文拼进 websocket URL**（`realtime/_gemini_realtime_model.py:32/85`）——日志泄漏风险，对照 OpenAI/DashScope 走 header
2. **`agentscope.tune` 顶层 API 已废弃**——`tune/__init__.py:4` 硬 `raise ImportError` 非软提示；trinity-rft 不在任何 pyproject extra
3. **`rrag/` 是空目录**——实际检索包是 `rag/`；re-rank 无独立模块，重排在消费端 `agent/_react_agent.py:981`
4. **仓内 `agentscope.a2a` 与 pip 包 `a2a-sdk` 顶层模块同名碰撞**；resolver 用 `@abstractmethod` 但未继承 ABCMeta（`a2a/_base.py:12/18`）抽象性运行时不强制；nacos 导入根是 `v2.nacos.*`（nacos-sdk-python≥3.0）
5. **DashScope `tool_choice="required"` 被静默降级 `auto`**（`_dashscope_model.py:230`）
6. **`call_tool_function` 永不抛异常**——错误转文本进模型上下文（工具契约=返回 ToolResponse 的函数，无 _tool_base.py）
7. **session 在 src 内零消费者**——持久化协调完全下放应用层（grep 实证）
8. **TextReader docstring 虚标 chunk overlap**（`rag/_reader/_text_reader.py:14`，实现零 overlap）；`Document.id` "unique" 注释失实（chunk 间共享 doc_id）
9. **Msg.to_dict 丢 invocation_id**（round-trip 缺陷）；`has_content_blocks` Literal 漏 "thinking"
10. **MCP 有状态客户端 LIFO 关闭**（`mcp/_http_stateful_client.py:24`）；dashscope TTS `dashscope.api_key=` 进程级全局赋值（`tts/_dashscope_cosyvoice_realtime_tts_model.py:103`）

## 与 DeepWiki 的关系

DeepWiki 快照含第 7/8 章（后端服务与 Web UI）对应上游完整仓；本地仓 `src/` 不含该部分（onboard 第 8 节已标注）。explain 系列比 DeepWiki 快照深一个版本代（源码逐行锚定）。
