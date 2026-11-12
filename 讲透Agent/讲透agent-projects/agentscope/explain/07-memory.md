# 07 memory 记忆系统：working/long-term 双轨与 Mem0·ReMe 适配

（锚相对 `src/agentscope/`；文件首次出现用全路径，后文用唯一短名，行号均经源码核实）

## 1. 角色定位

memory 子包是 agentscope 的记忆中枢，双轨制设计：**working memory**（短期记忆，对话上下文仓库，`_working_memory/`）与 **long-term memory**（跨会话知识库，`_long_term_memory/`），在 `memory/__init__.py:4` 与 `memory/__init__.py:10` 分别导出，共 10 个公开类。working 轨三实现（InMemory/Redis/SQLAlchemy）回答"当前对话放哪"；long-term 轨（Mem0/ReMe 三兄弟）回答"跨会话记什么"。两轨都挂 module 子包的 `StateModule`，天然接入 session 持久化。

## 2. 内部结构

**working 轨**：`MemoryBase`（`memory/_working_memory/_base.py:11`）持压缩摘要状态 `_compressed_summary`（`_base.py:18`，经 register_state 可序列化），抽象五件套 `add`/`delete`/`get_memory`（`_base.py:104`）/`size`/`clear`。核心机制是 **mark**：每条消息挂多个字符串标签，`get_memory` 按 `mark`/`exclude_mark` 过滤。`InMemoryMemory` 用 `list[tuple[Msg, list[str]]]` 存储（`memory/_working_memory/_in_memory_memory.py:17`）；`AsyncSQLAlchemyMemory` 内置 MessageTable，主键为 user-session-msg 复合串；`RedisMemory` 用 `marks_index` Set 追踪标签（`_redis_memory.py:31`）并周期刷新会话 TTL。

**long-term 轨**：`LongTermMemoryBase` 设计**双接口**——开发者用的 `record`/`retrieve`，与 agent 主动调用的工具函数 `record_to_memory`/`retrieve_from_memory`（`memory/_long_term_memory/_long_term_memory_base.py:48` 与 `:69`）。Mem0 适配层动态构造配置类绕开 mem0 的 provider 硬校验（`_mem0_long_term_memory.py:30`），用 `AgentScopeLLM`/`AgentScopeEmbedding` 适配器（`_mem0_utils.py:133`/`:284`）与 `_EventLoopManager` 跨事件循环桥复用 agentscope 模型。ReMe 侧（`_reme_long_term_memory_base.py:77`）是全包唯一带 `ABCMeta` 的基类。

## 3. 外部连接

ReActAgent 是最大消费者：构造时接 `long_term_memory`（`agent/_react_agent.py:286`），按 `long_term_memory_mode` 分流 static/agent 控制，agent_control 把两个长期记忆方法注册为工具（`agent/_react_agent.py:304`）。回复前 static 模式检索并注入 `<long_term_memory>` 包裹的 Msg（`agent/_react_agent.py:889`），回复后把 working memory 全量 record 进长期库（`agent/_react_agent.py:529`）。working memory 每次 prompt 组装都经 `get_memory` 进 formatter。formatter/pipeline/session 以 Msg 为介质间接依赖本包。

## 4. 数据流

working 主环：Msg 进 `add(memories, marks)` → 按 `msg.id` 去重（`_in_memory_memory.py:130`）→ `deepcopy` 入库（`_in_memory_memory.py:135`）→ `get_memory` 过滤 → 有压缩摘要则伪装成 user Msg 前置（`_in_memory_memory.py:81`）→ formatter 转 API 方言。压缩流：达阈值后取未标 COMPRESSED 的消息 → LLM 生成摘要 → `update_compressed_summary` → 老消息打 COMPRESSED mark。long-term 流：agent 工具以 `thinking+content` 描述性入库；检索按 keywords 取回文本注入上下文。

## 5. 设计决策

①**mark 而非分区**：一条消息可同时属多个逻辑组（压缩组+轮次组），增删经 `update_messages_mark` 完成，避免"搬移消息"式重写。②**摘要伪装 user 消息**：压缩摘要与普通消息同存储同通道，下游 formatter 零改动。③**双接口分层**：工具函数文档即提示词，开发者接口保持纯数据语义。④**适配器接 Mem0**：继承其配置类覆盖 validate_config、不动上游——外部记忆框架集成的标准姿势。

## 6. 新人提示

- 坑 1（必验）：`MemoryBase`/`LongTermMemoryBase` 用 `@abstractmethod` 却**没有 ABCMeta**（两者类声明均为纯 class）——装饰纯文档化，子类漏实现不报错，调用时静默返回 None；对照 `_reme_long_term_memory_base.py:77` 的 `metaclass=ABCMeta` 才是正规写法。
- 坑 2：`InMemoryMemory.add` 默认按 `msg.id` 去重，同一 Msg 重复 add 被静默吞掉，重放场景须 `allow_duplicates=True`（`_in_memory_memory.py:97`）。
- 坑 3：每次 add 对 msg 与 marks 各 `deepcopy`（`_in_memory_memory.py:135`），长对话内存翻倍，正确性优先的取舍。
- 坑 4：SQLAlchemy 版外键挂 SessionTable（`_sqlalchemy_memory.py:55`），必须与 session 子系统共库，否则外键悬空。
- 坑 5：Mem0/ReMe 是 optional 依赖（pyproject `mem0ai`/`reme` extra），import 失败的错误信息自带安装指引，别误当框架 bug。
