# A-29 `simular-ai/Agent-S`（12.2K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\simular-ai__Agent-S
> Python ｜ GUI Agent 框架（S1→S2→S2.5→S3 四代同仓）｜ 名字里的 "S" 曾指 Self-evolving（经验学习），当前 S3 主打 OSWorld 72.60%

## 1. 架构总览（目录地图）

- `gui_agents/s1/` — 初代：`core/AgentS.py`（Manager-Executor 层级 + episodic/narrative 记忆更新）、`core/Knowledge.py`（KnowledgeBase：embedding 检索 + Perplexica 网络知识 + LLM 融合）、`aci/`（各平台 Agent-Computer Interface）
- `gui_agents/s2/` — DAG 化层级：`agents/agent_s.py`（AgentS2 主控，记忆更新逻辑与 S1 同构）、`agents/manager.py`（任务级经验检索注入）、`agents/worker.py`（子任务级经验检索注入）、`memory/procedural_memory.py`（**名为记忆实为静态 prompt 库**）
- `gui_agents/s2_5/` — 扁平化：Worker 单层、**无任何记忆**（`agents/agent_s.py:48-72`，类注释 "uses no hierarchy for less inference time"）
- `gui_agents/s3/` — 当前旗舰：`agents/worker.py` + `agents/code_agent.py`（程序化执行）、`bbon/behavior_narrator.py` + `comparative_judge.py`（Behavior Best-of-N）、`memory/procedural_memory.py`（仍是静态 prompt）
- `evaluation_sets/`、`osworld_setup/`、`integrations/` — OSWorld/WindowsAgentArena 评测脚手架

## 2. 记忆机制深读（核心发现：记忆随版本演进被逐步移除）

### 2.1 写入/抽取管线（仅 S1/S2 有）
- **episodic 记忆**：子任务执行中 `subtask_trajectory` 以固定分隔符逐段累积 plan（`gui_agents/s1/core/AgentS.py:335-380`）；子任务完成时取轨迹首段（"Task:
{query}

Subtask: ...
Subtask Instruction: ..."）作 key，LLM 用 `SUBTASK_SUMMARIZATION_PROMPT` 把轨迹蒸馏成"正确计划 + grounded actions"存入 `episodic_memory.json`（`s1/core/AgentS.py:339-359`、写入侧 `s2/agents/agent_s.py:364-404`）
- **经验抽象（关键设计）**：summarization prompt 强制把 `agent.click("The menu button in the top row", 1)` 中的描述串替换为 `element1_description` 占位符——把具体坐标/描述泛化成可跨任务复用的模板（`s2/memory/procedural_memory.py:179-183`）；且"只准引用轨迹中实际出现的动作，不得发明"（`procedural_memory.py:184`）
- **narrative 记忆**：整任务结束时以 search_query 为 key，`TASK_SUMMARIZATION_PROMPT` 总结"成功计划（保留用过的热键）/ 失败原因 + 给 agent 的可执行建议（禁止空泛建议如 Implement Error Handling）"存 `narrative_memory.json`（`s1/core/AgentS.py:300-319`、prompt `s2/memory/procedural_memory.py:118-132`）
- **网络知识（S1/S2 的 RAG 路）**：`formulate_query` 由 a11y 树生成搜索问题（缓存到 formulate_query.json，`s1/core/Knowledge.py:77-113`），`_search` 走 LLM 内部知识或 Perplexica，结果缓存 `{engine}_rag_knowledge.json`（`Knowledge.py:115-152`）

### 2.2 存储后端与数据模型
- **纯 JSON 文件**，按平台分目录：`{local_kb_path}/{platform}/episodic_memory.json`、`narrative_memory.json`、`embeddings.pkl`（pickle 缓存 embedding）、`formulate_query.json`、`*_rag_knowledge.json`（`s1/core/Knowledge.py:42-50,79-81,119-121`）；读写工具 `load_knowledge_base`/`load_embeddings`（`s1/utils/common_utils.py:840-858`）
- schema 极简：`{key_text: summarized_experience_text}` 平 dict；key 即检索 embedding 的文本——**检索索引和存储 key 是同一段自然语言**
- 所谓 "PROCEDURAL_MEMORY" 是运行时用 `inspect` 遍历 ACI 类的 `is_agent_action` 方法签名 + docstring 动态拼装的系统提示（`s2/memory/procedural_memory.py:20-31`）——静态"如何操作电脑"的技能说明书，非习得记忆

### 2.3 检索策略
- OpenAI embedding + sklearn `cosine_similarity` 全量暴力扫，**只取 top-1**（若最近邻是查询自身则取次近，`idx = 1 if keys[sorted_indices[0]] == instruction else 0`，`s1/core/Knowledge.py:181-188`、episodic 同构 `Knowledge.py:217-224`）
- 无混合检索、无重排、无 top-k；embedding 惰性计算并 pickle 缓存（`Knowledge.py:162-179`）

### 2.4 遗忘·整合·演化
- **无遗忘**：JSON 只增不减，key 去重靠字符串精确匹配（`agent_s.py:392`）
- 融合靠 LLM：`knowledge_fusion` 把 web 知识 + 相似任务经验 + a11y 树交给 LLM 判断"经验是否真有用"再整合成编号列表（`s1/core/Knowledge.py:226-250`）
- 反思机制（运行时，非持久）：`REFLECTION_ON_TRAJECTORY` 检测动作循环（"look out for cycles of actions continually repeated"），只反馈"偏航/正常"不指定动作（`s2/memory/procedural_memory.py:104-116`）
- **S2.5→S3 的"演化"是删记忆**：S2.5 Worker 无 knowledge_base 字段（`s2_5/agents/worker.py:18-55`）；S3 仅有静态 procedural prompt（`s3/memory/procedural_memory.py:13-117`，全目录 grep 无 episodic/narrative 引用）——S3 用 **bBoN**（rollout 后 BehaviorNarrator 叙述行为 + ComparativeJudge 挑最优，`s3/bbon/behavior_narrator.py:19-34`）替代了跨任务经验积累，用推理期算力换训练期记忆

### 2.5 注入上下文的方式
- Worker 在 t=0 检索 episodic 经验拼进 instruction："You may refer to some similar subtask experience if you think they are useful. {...}"（`s2/agents/worker.py:116-146`）；注入前有 "dirty fix" 正则把经验中的 `(123` 元素 id 替换成 `(element_description` 以适配新界面（`worker.py:129-136`）
- Manager 检索 narrative 经验 + web 知识，融合后追加 "You may refer to some retrieved knowledge..."（`s2/agents/manager.py:129-164`）
- 无 token 预算；轨迹截断只靠 `max_trajectory_length` 张截图滑动窗口（`worker.py:95-96`）

## 3. 关键代码摘录

**摘录 1：经验的占位符泛化（`gui_agents/s2/memory/procedural_memory.py:179-184`）**
```python
2.	Description Replacement in Grounded Actions:
    When summarizing grounded actions, the agent.click() and agent.drag_and_drop() grounded actions take a description string as an argument.
    Replace these description strings with placeholders like \"element1_description\", \"element2_description\", etc., while maintaining the total number of parameters.
    For example, agent.click(\"The menu button in the top row\", 1) should be converted into agent.click(\"element1_description\", 1)
...
3.	Only generate grounded actions that are explicitly present in the trajectory. Do not introduce any grounded actions that do not exist in the trajectory.
```

**摘录 2：top-1 余弦检索 + 自匹配跳过（`gui_agents/s1/core/Knowledge.py:181-188`）**
```python
similarities = cosine_similarity(
    instruction_embedding, np.vstack(candidate_embeddings)
)[0]
sorted_indices = np.argsort(similarities)[::-1]

keys = list(knowledge_base.keys())
idx = 1 if keys[sorted_indices[0]] == instruction else 0
return keys[sorted_indices[idx]], knowledge_base[keys[sorted_indices[idx]]]
```

**摘录 3：episodic 记忆写入（`gui_agents/s1/core/AgentS.py:339-359`）**
```python
subtask_key = subtask_trajectory.split(
    "\n----------------------\n\nPlan:\n"
)[0]
try:
    subtask_path = os.path.join(
        self.local_kb_path, self.platform, "episodic_memory.json"
    )
    kb = json.load(open(subtask_path))
except:
    kb = {}
if subtask_key not in kb.keys():
    subtask_summarization = self.planner.summarize_episode(
        subtask_trajectory
    )
    kb[subtask_key] = subtask_summarization
```

**摘录 4：经验注入的 id→description 适配 hack（`gui_agents/s2/agents/worker.py:129-136`）**
```python
# Dirty fix to replace id with element description during subtask retrieval
pattern = r"\(\d+"
retrieved_subtask_experience = re.sub(
    pattern, "(element_description", retrieved_subtask_experience
)
retrieved_subtask_experience = retrieved_subtask_experience.replace(
    "_id", "_description"
)
```

**摘录 5：静态"程序性记忆"= API 签名拼装（`gui_agents/s2/memory/procedural_memory.py:20-31`）**
```python
for attr_name in dir(agent_class):
    if attr_name in skipped_actions:
        continue
    attr = getattr(agent_class, attr_name)
    if callable(attr) and hasattr(attr, "is_agent_action"):
        # Use inspect to get the full function signature
        signature = inspect.signature(attr)
        procedural_memory += f"""
def {attr_name}{signature}:
'''{attr.__doc__}'''
    """
```

## 4. 基准/评测声明（反虚荣视角）
- README 宣称：OSWorld **72.60%**（bBoN）"First to Surpass Human Performance"、单 S3 69.9%/66%（README.md:6,62-63,95）；WindowsAgentArena 56.6%（3 rollouts 选优，README.md:97）——数字 **[自封]** 但有 arXiv 论文（2510.02250）+ 仓库内 osworld_setup/evaluation_sets harness，OSWorld 榜单可外部核验 **[部分第三方可核]**
- 注意口径：72.60% 是 **bBoN 多 rollout 选优**的结果，单次执行 66-69.9%；"超越人类（72%）"对比的是 OSWorld 论文里的人类基线 **[口径需谨慎]**
- 记忆系统对得分的贡献在 S3 上不存在（S3 无记忆）——早期论文中"experience learning"提升声明属于 S1/S2 时代 **[与当前版本脱钩]**

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量）
1. **经验占位符泛化**：总结动作序列时把具体元素描述替换成 `element1_description` 占位符，让 episodic 经验成为可跨界面迁移的"动作模板"而非死记坐标——GUI/浏览器 agent 记忆抽象的正确姿势（`procedural_memory.py:179-183`）
2. **失败经验的可执行化**：narrative 总结强制"建议必须可通过 agent 动作完成、禁止空泛建议"——负面记忆的价值密度设计（`procedural_memory.py:130-131`）
3. **双粒度记忆分层**：narrative（整任务计划级，Manager 用）vs episodic（子任务动作级，Worker 用），对应层级注入（`manager.py:129-164` vs `worker.py:116-146`）
4. **检索自匹配跳过 trick**：`idx = 1 if top1 == instruction else 0` 一行处理"查到自己"（`Knowledge.py:187`）
5. **反向教训（最重要）**：S2.5/S3 靠删记忆+加推理（反思、bBoN）反而涨分——说明弱记忆（top-1 暴力检索、无遗忘、无质量门）可能不如没有；记忆系统必须证明其增量超过检索噪声的代价

## 6. 局限与风险
- 记忆工程质量原始：纯 JSON 全量加载、pickle 缓存、裸 `except:` 吞异常（`Knowledge.py:85-86,123-127`）、无并发保护、无容量上限——只适合论文实验规模
- 检索仅 top-1 余弦，无阈值兜底——不相关经验也会被注入（"if you think they are useful" 全靠 LLM 自辨）
- key 即轨迹原文前缀，换个措辞的同任务无法命中（无规范化）
- "procedural memory" 命名误导：实为静态 API 文档 prompt，非习得技能
- 用户问的 "Agentarium"：**全仓库 grep 无任何匹配，不存在该组件** [未在代码中出现]；deepwiki 的 S3 目录也未提及——疑为与其他项目混淆或谣传
- S1/S2 记忆代码仍在仓库但已被当前版本弃用——读者按 README 跑 S3 时记忆系统根本不生效

## 7. 一句话对比 mem0
mem0 把对话事实做成向量卡片随取随用；Agent-S 的记忆是把"操作电脑的成败轨迹"蒸馏成带占位符的动作模板按任务相似度注入——但最有警示价值的反差是：它的最新 SOTA 版本干脆放弃了记忆，用推理期 best-of-N 换掉了积累期经验库。
