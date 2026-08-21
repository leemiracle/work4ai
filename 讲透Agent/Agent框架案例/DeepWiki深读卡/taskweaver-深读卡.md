# taskweaver 深读卡 —— 微软 code-first 数据分析 Agent：把用户请求译为有状态会话中执行的 Python 代码

> **定位**：TaskWeaver 是微软的 code-first Agent 框架，将用户请求转成 Python 代码片段并协调插件完成数据分析任务。核心差异化：同时保留 chat history 与 code execution history（含内存中的 DataFrame 等富数据结构），跨轮有状态。论文背书：*TaskWeaver: A Code-First Agent Framework*（arXiv:2311.17541，2023-11，微软 19 人团队）。
> **本地**：`repos/taskweaver`（microsoft/TaskWeaver）｜**深读**：deepwiki 19 子页归档 `deepwiki/taskweaver/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 用户层 | CLI / WebUI / Library / Docker 四种接入 | `chat/console/chat.py`, `playground/UI/app.py` |
| 会话层 | round 驱动的有状态会话 + 事件流 | `Session`, `SessionEventEmitter`, `PostEventProxy` |
| 规划层 | 任务分解与多角色编排 | `Planner`, `planner_prompt.yaml` |
| 记忆层 | 双历史 + 结构化附件 + 压缩/经验 | `Post`, `Round`, `Attachment`(init_plan/plan/execution_result…), `RoundCompressor`, `Experience` |
| 执行层 | 代码生成-验证-执行闭环 | `CodeGenerator`, `CodeVerification`, `CodeExecutor` |
| 执行环境 | IPython kernel 本地/容器隔离 | CES：`Environment`, `kernel/launcher.py`, `manager/sub_proc.py` |
| 工具层 | 插件注册与嵌入选择 | `PluginEntry`, `PluginRegistry`, `PluginSelector`, `Plugin` 基类 |
| 基础设施 | 多 LLM 后端门面 + 可观测 | `LLMApi`(openai/anthropic/ollama/qwen/zhipuai…), `tracing.py` |

## 二、核心机制

1. **Code-First + 双历史有状态会话**（Overview / Code Interpreter）：用户请求被译成 Python 代码在 IPython Kernel 中执行，变量与 DataFrame 在会话内存中跨轮存活——区别于只记文本历史的同类框架，把"代码"当作 Agent 间通信媒介；执行结果经 `execution_result`/`code_error` Attachment 回流 Planner。
2. **Planner 中枢辐射式多角色编排**（Planner / External Roles）：Planner 产出 `init_plan→plan→current_plan_step` 附件做任务分解与进度展示，所有角色（CodeInterpreter、ImageReader 等外部 Role）只经 Planner 通信（`Post.send_to` 路由）；LLM 流式输出由 PostTranslator 边解析 JSON 边发事件，实现打字机式计划/代码展示。
3. **嵌入向量自动选插件**（Plugin System）：插件 = YAML spec（签名+示例）+ Python impl 双文件；`PluginSelector` 用 embedding 相似度 top-k 挑选相关插件注入代码生成 prompt，而非全量塞入——早期"RAG 选工具"实践；`plugin_only` 变体则直接映射为 function calling 工具，另有 CLI-only 变体执行 shell 命令。
4. **AST 白名单 + 容器隔离双层安全**（Code Interpreter / Code Execution Service）：执行前 `FunctionCallValidator` 做 AST 级模块/函数/变量白名单校验与 Jupyter magic 命令分离，失败触发 `format_code_correction_message()` 自纠错重试（`max_retry_count`）；执行时 CES 默认在 Docker 容器内启动 IPython kernel 实现进程级隔离。

## 三、与讲透系列的对位

| TaskWeaver 概念 | 讲透系列对应概念 |
|---|---|
| 代码生成→验证→执行→错误重试闭环 | 讲透Agent：ReAct 循环（行动-观察-修正） |
| PluginSelector embedding top-k 选插件 | 工具调用：RAG 式工具检索 |
| Post/Round 双历史 + Round 压缩 + Experience 注入 | 记忆机制 / 上下文工程 / 自进化（经验沉淀） |
| Planner 中枢、全部 Role 经其转发 | 讲透多Agent协作：编排模式（hub-and-spoke） |
| FunctionCallValidator AST 门禁 + CES 容器 | 安全沙盒 |

## 四、关键入口

```python
taskweaver/session/session.py                # Session：round 驱动会话中枢，按 send_to 路由 Post 到各 Role
taskweaver/planner/planner.py                # Planner 角色：任务分解 init_plan/plan，调度 CodeInterpreter 与外部 Role
taskweaver/code_interpreter/code_interpreter/code_generator.py  # LLM 代码生成：插件签名+Experience+压缩历史注入 prompt
taskweaver/code_interpreter/code_executor.py # 执行生命周期：load_plugin → execute_code → 产物(image/chart/file)落盘
taskweaver/code_interpreter/code_verification.py  # AST + FunctionCallValidator：模块/函数/变量白名单门禁
taskweaver/memory/plugin.py                  # PluginEntry/PluginSpec/PluginRegistry/PluginSelector 全家（嵌入选插件）
taskweaver/ces/kernel/launcher.py            # CES：IPython kernel 启动，local/container 双模式隔离执行
taskweaver/llm/__init__.py                   # LLMApi 门面：openai/anthropic/ollama/qwen/zhipuai 多后端统一接口
```

## 五、深读子页地图（19 页精选 5）

1. **Code Interpreter**（L2354）— 核心引擎：生成→验证→执行→重试全管线与三个变体（全量/PluginOnly/CLIOnly）对比
2. **Plugin System**（L3616）— 最完整的扩展机制：YAML+impl 双文件、embedding 自动选择、plugin_only function calling
3. **Memory and Communication System**（L1843）— Post/Round/Attachment 双历史、Round 压缩、Experience 经验学习
4. **Code Execution Service**（L3080）— CES 内幕：IPython kernel 启动、Docker 容器安全、magic 命令注入
5. **Session Management**（L1467）— round 制消息路由、PostEventProxy 流式事件与 WebUI 会话管理

## 六、与"我们"的关系（一句话）

它是把"代码即行动空间"做成工程闭环（生成-验证-沙盒执行-重试-经验沉淀）的微软级参考实现，学 ReAct 代码执行、RAG 式工具选择与 AST+容器双层沙盒，这一仓足够。

---
生成：2026-08-21 · deepwiki 19 页全归档
