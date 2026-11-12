# 09 RoleZero 与经验池：命令驱动角色与两套"经验"的真相

## 1. 角色定位

RoleZero（`metagpt/roles/di/role_zero.py:55`，`class RoleZero(Role)`）是 MetaGPT 对"最小角色框架"的答案：不再为每个动作写 Action 子类，而是让 LLM 直接输出命令 JSON（Plan.finish_current_task/Editor.edit_file_by_replace/Terminal.run_command...），角色本体只剩 think→parse→execute 循环。它是 DataInterpreter 系（DataAnalyst、MGX 各管理角色）的共同基类，也是全仓"经验机制"最密集的一条线——但这里并存两套完全不同的"经验"，极易混淆：`metagpt/strategy/experience_retriever.py` 的静态 few-shot 注入器，与 `metagpt/exp_pool/` 的运行时经验池。

## 2. 内部结构

角色主体 491 行：`special_tool_commands`（role_zero.py:77，Plan.finish_current_task/end/Terminal.run_command/RoleZero.ask_human 四命令）走独立执行路径不产消息；`exclusive_tool_commands`（L80-85，Editor 四命令）多条出现只留首条防重复编辑；`_think`（L198）先探测回复语言（L211），`_act`（L280）经 `parse_commands`（L284）解析命令流。经验接线三件套在 L15-17 一次导入：`exp_cache` 装饰器（exp_pool/decorator.py:29）、`RoleZeroContextBuilder`（context_builders/role_zero.py:10）、`RoleZeroSerializer`（serializers/role_zero.py:10）；L91 `experience_retriever` 字段默认 `DummyExpRetriever()`。L267 用 `@exp_cache(context_builder=..., serializer=...)` 包住 LLM 调用实现经验读写复用。

## 3. 外部连接

经验池管理器 `exp_pool/manager.py:18` 的 ExperienceManager：storage 属性延迟构造 BM25 或 Chroma 引擎（`_create_bm25_storage` L145、`_create_chroma_storage` L191），写入即 `storage.persist`（L91）；对 rag 模块三处函数体内 try-import，未装依赖时 import exp_pool 不报错、真用到 storage 才 raise ImportError。长期记忆 `memory/role_zero_memory.py:24` 的 RoleZeroLongTermMemory 同样在 `_resolve_rag_engine`（L46-56）里 try-import `SimpleEngine`，失败即提示安装 rag 模块——经验与记忆两条线都硬依赖 rag 子系统。命令解析 `utils/role_zero_utils.py:98` 的 `parse_commands` 服务 LaTeX 转义修复与状态抽取；prompts/di/role_zero.py 提供命令语法与 few-shot。

## 4. 数据流

调用链：用户需求 → RoleZero._think 组上下文（memory_k=200 条历史，L97）→ exp_cache 命中则注入相似经验 → LLM 输出命令 JSON → parse_commands 三元组（commands, ok, command_rsp）→ 命令分派（special/exclusive/普通）→ Editor/Terminal/Browser 执行 → 结果回写 memory → `RoleZeroContextBuilder` 取最新经验、`RoleZeroSerializer.serialize_req` 过滤后入库。静态经验线独立旁路：experience_retriever.retrieve(context) 的返回串直接拼进 system prompt。

## 5. 设计决策

先钉最大勘误：**experience_retriever.py 1243 行约三分之二是 few-shot 示例字符串常量，"检索"全是关键词静态匹配**。`DummyExpRetriever`（L13）`return self.EXAMPLE` 且 `EXAMPLE: str = ""`——默认返回空串等于关经验；`SimpleExpRetriever`（L651）无条件返回 `TL_EXAMPLE`（L471-648，TeamLeader 7 个完整命令流示例）；`KeywordExpRetriever`（L658）靠 `"deploy" in context.lower()`/`"issue"`/`"https:"` 这类子串判断在 DEPLOY/FIX_ISSUE/WEB_SCRAPING 三个常量间切换，注释掉的 task 分支可见未完成。没有向量检索、没有数据库——所谓"经验检索器"是 prompt 工程的类语法糖。真检索在 exp_pool，但有两处暗坑：其一 `query_exps`（manager.py:94）的 tag 过滤与精确匹配都是 RAG 取回后在内存里做的（L112 留 `TODO: filter by metadata`），而 `DEFAULT_SIMILARITY_TOP_K = 2`（exp_pool/schema.py:11）——先截断后过滤，tag 命中的经验可能已被 top_k=2 卡掉；其二 `_create_bm25_storage` 新建路径会塞一条 `Experience(req="req", resp="resp")` 占位经验建索引（L172），假数据从此进检索池。第三处：`RoleZeroSerializer._is_useful_content`（serializers/role_zero.py:48）只保留内容含 `"Command Editor.read executed: file_path"` 的消息、其余全丢——为压 embedding 长度的激进过滤，后果是 RoleZero 经验池里只有文件读取记录，对话与命令输出一概不存。另有小笔误：`parse_commands` 签名声明返回 `Tuple[list[dict], bool]`（role_zero_utils.py:98），实际 L144 返回 `(commands, True, command_rsp)` 三元组。

## 6. 新人提示

想给 RoleZero 喂经验有三档：改 DummyExpRetriever 的 EXAMPLE（最快）、换 KeywordExpRetriever（按需求关键词挑模板）、开 exp_pool（真语义检索但记得调大 top_k 并清洗占位经验）。读 experience_retriever.py 直接跳到 L471 以后的常量区，前 650 行类定义信息量很低。调"为什么经验没生效"按顺序查：role_zero.py:91 默认是否还是 Dummy、exp_pool 是否 persist、serializer 是否把你的消息全过滤了。扩展新命令照 exclusive_tool_commands 模式登记，避免 LLM 连发编辑命令互相覆盖。长期记忆接 rag 的两个 try-import 点（manager.py 与 role_zero_memory.py:46）决定了最小安装跑不起来这两条线，报 ImportError 先查 rag 依赖而非代码 bug。
