# A-27 `EvoAgentX/EvoAgentX`（3.2K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\EvoAgentX__EvoAgentX
> Python ｜ 自进化 Agent 工作流生态：自然语言目标 → 自动生成多 agent 工作流 → 基准评测 → 7 种进化算法迭代优化（TextGrad/MIPRO/AFlow/EvoPrompt/SEW/MAP-Elites）

## 1. 架构总览（目录地图）

- `evoagentx/workflow/` — 工作流核心：`workflow_graph.py`（`WorkFlowNode`:49、`WorkFlowGraph`:585，1800+ 行 Pydantic 大模型）、`workflow.py`（执行引擎，带 `workflow_id`/`version` 字段，`workflow/workflow.py:40-41`）、`workflow_generator.py:20`（目标→工作流自动构建）、`workflow_manager.py:416`（任务/action 双层调度）
- `evoagentx/optimizers/` — **进化引擎**（本仓灵魂）：`aflow_optimizer.py`（AFlow 式图进化，文件头致谢 MetaGPT MIT，`optimizers/aflow_optimizer.py:1`）、`evoprompt_optimizer.py`（prompt 种群进化）、`map_elites_optimizer.py`（质量多样性归档）、`sew_optimizer.py`（自研 SEW）、`textgrad_optimizer.py`、`mipro_optimizer.py` + `engine/`（通用参数寻优引擎）
- `evoagentx/memory/` — agent 级记忆：`long_term_memory.py`（RAG 消息库）、`memory_manager.py`（LLM 管家）、`context_manager.py`
- `evoagentx/agents/long_term_memory_agent.py` — MemoryAgent 封装
- `evoagentx/storages/` — 持久层：`db_stores/sqlite.py`（默认 sqlite，`storages_config.py:12`）+ 向量库（faiss/chroma/qdrant）+ 图库（neo4j）
- `Wonderful_workflow_corpus/` — 精选工作流语料库（travel/tetris/arxiv_daily/invest 等，各含 `workflow.json`+`tools.json`），即可复用的"工作流记忆"种子库

## 2. 记忆机制深读（双形态记忆）

### 2.1 形态一：agent 级消息记忆（写入/抽取管线）
- **MemoryAgent.chat 流程**（`agents/long_term_memory_agent.py:330-352`）：检索 top_k=3 → `create_conversation_message` 把检索结果拼进 context → LLM 生成 → 回答写回记忆（`long_term_memory_agent.py:84-114`）；`interactive_chat` 每轮结束 `handle_memory_flush` 刷新索引保证下轮可检（`long_term_memory_agent.py:442-446`）
- **写入决策**：`MemoryManager.handle_memory(action="add")` 先组装 `{action, memory_id, message}` 输入，再交 `_prompt_llm_for_memory_operation` 用 LLM 裁决 add/update/delete（`memory/memory_manager.py:98-116`、`memory_manager.py:35-56`）；prompt 是 `MANAGER_PROMPT`（`prompts/memory/manager.py:1-54`）——按 exact content match 判重、要求返回 JSON 数组、异常时回退原始输入直写（`memory_manager.py:54-56`）
- **去重**：`LongTermMemory.add` 对每条消息算 **sha256(content)**，撞哈希则复用旧 memory_id 跳过写入（`memory/long_term_memory.py:88-114`）——纯精确去重，无语义合并
- **数据模型**：Message→Chunk 转换时 metadata 携带 `wf_goal/wf_task/wf_task_desc/next_actions/action` 等**工作流上下文字段**（`long_term_memory.py:36-59`）——记忆条目天然带"哪条工作流哪步产生"的溯源标签

### 2.2 存储后端与数据模型（形态一）
- `LongTermMemory` = `StorageHandler`（默认 SQLite 表 `memory`，含 content_hash 列）+ `RAGEngine`（faiss/chroma/qdrant 可配）双层（`long_term_memory.py:16-34`）；corpus_id 即会话/用户命名空间（`default_corpus_id`），session 作用域每次 uuid4、global 作用域稳定 id（`long_term_memory_agent.py:380-389`）
- save/load 走 `rag_engine.save(table=self.memory_table)` 落库（`long_term_memory.py:270-276`）

### 2.3 检索策略（形态一）
- 纯向量 RAG：`search_async` 构造 `Query(query_str, top_k, metadata_filters)` 交 `rag_engine.query_async`（`long_term_memory.py:232-257`）；无关键词路、无重排、无 RRF——检索深度明显弱于 ReMe/mem0，metadata_filters 是唯一过滤手段

### 2.4 形态二（核心）：工作流即记忆——进化式存储·变异·复用
- **存储**：工作流是带 `workflow_id` + `version` 的可序列化 JSON 模块（`workflow/workflow.py:40-41`；`WorkFlowGraph.save_module`，`workflow_graph.py:1783`）；`Wonderful_workflow_corpus/*/workflow.json` 展示 schema：goal + nodes[]（每 node 含 name/inputs/outputs/reason/agents[]，agent 内嵌完整 prompt）——工作流的"基因型"就是这份 JSON
- **变异-选择循环（AFlow 路线）**：每轮从历史 top-4 轮按混合概率分布（softmax×α + uniform×λ）轮盘选父本（`utils/aflow_utils/data_utils.py:80-129`）→ 读父本 graph.py+prompt.py → 拼装"经验+算子描述+日志"进化 prompt → LLM 输出 XML 格式 modification+新 graph 代码（`optimizers/aflow_optimizer.py:185-215`）→ 写入 `round_N/` 目录 → 验证集 5 次评估 → 写 `experience.json`（`aflow_optimizer.py:255-268`）
- **经验（episodic 记忆）**：每轮落盘 `experience.json = {father node, modification, before, after, succeed}`（`utils/aflow_utils/experience_utils.py:85-92`），聚合树按父节点分形成 success/failure 两枝（`experience_utils.py:14-48`）；下轮变异 prompt 注入经验文本——**失败项标注 "Absolutely prohibit {modification}"（防重蹈覆辙），成功项同样标 "Absolutely prohibit"（防原地踏步）**（`experience_utils.py:58-70`，两处字面相同，疑似沿袭 AFlow 原版措辞）；`check_modification` 还在代码层硬性拒绝与历史重复的 modification（`experience_utils.py:72-83`、`aflow_optimizer.py:210-211` 的 while True 循环）
- **种群级进化（EvoPrompt/MAP-Elites 路线）**：`evoprompt_optimizer.py` 维护 `node_populations: Dict[str, List[str]]` 每 workflow 节点一个 prompt 种群，排名淘汰 "Best/Survivor/Eliminated"（`optimizers/evoprompt_optimizer.py:95,166-178`），组合采样生成候选（`evoprompt_optimizer.py:471-506`）；`map_elites_optimizer.py` 用 archive{cell: ArchiveEntry(cfg, fitness)} 质量多样性存档，随机选父 + `_mutate_cfg` 变异 + 分数占优才入档（`map_elites_optimizer.py:74-92`）
- **SEW 变异算子**：`SimplePromptBreeder` 支持 zero-order（随机 thinking_style 生成超变异 prompt）与 first-order（固定 mutation_prompts 池）（`sew_optimizer.py:603-653`）；工作流可在 python/yaml/code/core/bpmn 五种表示间转换后交 LLM 变异（`sew_optimizer.py:20-65`）；主循环每 N 步评估、收敛即停、**最终从快照恢复历史最优图**（`sew_optimizer.py:688-711`）
- **复用**：优化出的工作流经 `save_module/from_file` 落盘为 JSON 模块跨项目复用（`workflow/action_graph.py:60-85`）

### 2.5 注入上下文的方式
- 形态一：检索结果直接拼进 `Context: {context}\n\nUser: {prompt}` 模板（`long_term_memory_agent.py:37`、`long_term_memory_agent.py:432`）；无 token 预算控制
- 形态二：经验文本整体注入优化 prompt（`aflow_optimizer.py:193-199`）；`Environment.update_task_execution_history` 在执行期维护任务历史供调度器参考（`workflow/environment.py:56`）

## 3. 关键代码摘录

**摘录 1：AFlow 经验注入——成败皆禁（`evoagentx/utils/aflow_utils/experience_utils.py:58-70`）**
```python
def format_experience(self, processed_experience, sample_round):
    experience_data = processed_experience.get(sample_round)
    if experience_data:
        experience = f"Original Score: {experience_data['score']}\n"
        experience += "These are some conclusions drawn from experience:\n\n"
        for key, value in experience_data["failure"].items():
            experience += f"-Absolutely prohibit {value['modification']} (Score: {value['score']})\n"
        for key, value in experience_data["success"].items():
            experience += f"-Absolutely prohibit {value['modification']} \n"
```

**摘录 2：sha256 精确去重（`evoagentx/memory/long_term_memory.py:99-109`）**
```python
for msg, memory_id in zip(messages, memory_ids):
    content_hash = hashlib.sha256(str(msg.content).encode()).hexdigest()
    if content_hash in existing_hashes:
        logger.info(f"Duplicate message found (hash): {msg.content[:50]}...")
        existing_id = next(
            (r["memory_id"] for r in self.storage_handler.load(...) if r.get("content_hash") == content_hash), None)
        if existing_id:
            final_memory_ids.append(existing_id)
            continue
```

**摘录 3：MAP-Elites 归档占优替换（`evoagentx/optimizers/map_elites_optimizer.py:74-92`）**
```python
parent = random.choice(list(archive.values()))
cfg = self._mutate_cfg(parent.cfg)
...
metrics, fitness = self._evaluate(output)
if existing is None or fitness > existing.fitness:
    entry = ArchiveEntry(cfg=cfg, fitness=fitness, metrics=metrics, cell=cell)
    ...
    if best_entry is None or entry.fitness > best_entry.fitness:
```

**摘录 4：AFlow 经验落盘 schema（`evoagentx/utils/aflow_utils/experience_utils.py:85-99`）**
```python
def create_experience_data(self, sample, modification):
    return {
        "father node": sample["round"],
        "modification": modification,
        "before": sample["score"],
        "after": None,
        "succeed": None,
    }

def update_experience(self, directory, experience, avg_score):
    experience["after"] = avg_score
    experience["succeed"] = bool(avg_score > experience["before"])
    save_json(experience, os.path.join(directory, "experience.json"), ...)
```

**摘录 5：记忆条目携带工作流溯源元数据（`evoagentx/memory/long_term_memory.py:38-52`）**
```python
metadata = ChunkMetadata(
    corpus_id=self.default_corpus_id,
    memory_id=memory_id,
    timestamp=message.timestamp,
    action=message.action,
    wf_goal=message.wf_goal,
    ...
    wf_task=message.wf_task,
    wf_task_desc=message.wf_task_desc,
    message_id=message.message_id,
)
```

## 4. 基准/评测声明（反虚荣视角）
- 内置 benchmark 覆盖 GSM8K/HotpotQA/MBPP/HumanEval/LiveCodeBench/BBH/NQ/WorfBench（`evoagentx/benchmark/*.py`），优化器原生对接 benchmark——评测是**框架一等公民**而非事后贴数
- README 主打框架能力，性能数字引用自对应论文（AFlow/SEW 等），非本仓自测 **[第三方论文数字，本仓提供复现 harness]**；SEW 论文数字未在 README 内复核 **[需查论文]**

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量）
1. **工作流即基因型、经验即表现型**：把"程序性记忆"做成可版本化 JSON（workflow_id+version），进化过程本身就是记忆写入——记忆的"深度加工"由选择压力（验证集分数）驱动而非 LLM 自评（`workflow/workflow.py:40-41` + `aflow_optimizer.py:255-268`）
2. **负面经验显式记忆 + 双重防重复**：prompt 层 "Absolutely prohibit" + 代码层 `check_modification` 硬校验，确保变异不重蹈历史覆辙（`experience_utils.py:58-83`）——失败经验的记忆价值高于成功经验，这是对 mem0 "只记事实" 的补集
3. **进化算法族谱可插拔**：同一 WorkFlowGraph 底座上跑 6+ 种优化器（轮盘选择/种群淘汰/QD 归档/文本梯度），等于给"记忆演化"提供了算法选择器（`optimizers/__init__.py`）
4. **记忆条目内嵌工作流溯源字段**（wf_goal/wf_task/next_actions）——记忆天然带"产生情境"标签，比 mem0 的 user_id/agent_id 分维度更细（`long_term_memory.py:38-52`）
5. **Wonderful_workflow_corpus 种子库**：预置高质量工作流作为进化起点，冷启动问题的一种工程解

## 6. 局限与风险
- 形态一（消息记忆）非常薄：无语义合并（仅 sha256 精确去重）、无遗忘、纯向量单路检索、LLM 管家 JSON 解析脆弱（`memory_manager.py:46` 手工剥 ```json  fencing）——相比 mem0 是玩具级
- AFlow 变异对象是**可执行 Python 代码**（graph.py），LLM 生成代码直接 load 执行（`graph_utils.py:43-53`），存在任意代码执行风险，无沙箱
- 成功经验也标 "Absolutely prohibit" 的措辞与语义意图（防停滞）不符，是 AFlow 原版 bug 的沿袭，LLM 实际可能被误导（`experience_utils.py:64-66`）
- 进化成本高：AFlow 默认 max_rounds=20 × validation 5 次 × 全数据集评估（`aflow_optimizer.py:61-65`），无成本预算控制
- `asyncio.run` 在同步方法内部嵌套调用（`long_term_memory.py:168,200,262`），与 MemoryAgent 的 `asyncio.create_task` 后台写（`long_term_memory_agent.py:213,220`）混用，事件循环管理脆弱

## 7. 一句话对比 mem0
mem0 记"是什么"（事实性陈述句），EvoAgentX 记"怎么做"（可执行工作流基因 + 成败经验树），用验证集分数当遗忘曲线——用进化算法替代 LLM 自评来做记忆的存留裁决。
