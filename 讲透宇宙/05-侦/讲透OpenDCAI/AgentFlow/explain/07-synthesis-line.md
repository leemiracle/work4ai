# 07 · synthesis QA 合成线：从种子到多跳问答的装配链

> 所属仓库：OpenDCAI/AgentFlow（图谱 909 节点/1857 边）。本篇覆盖 `synthesis/` 包全量 + `sandbox/result_formatter.py` 格式化层，是 AgentFlow"造数据"的另一半——rollout 线跑评测，synthesis 线造训练/评测用的 QA 数据。

## 一、角色定位

synthesis 线回答的问题是：**给定一个种子（一段 PDF 大纲、一个 CSV 目录、一个起始实体），如何自动造出"需要多跳推理才能回答"的 QA 对？**

它的思路不是让 LLM 直接编题（那样答案容易飘），而是先让一个探索型 Agent 在沙箱里真实地跑工具（搜文档、跑 Python、点 UI），把走过的路径存成**轨迹树**，再从树里挑出高质量路径，最后基于"真实观察到的证据"合成问题。答案 grounded 在观察里，问题被强制要求不含答案文本（防捷径）。

包结构一眼看全：

- `synthesis/pipeline.py`（283 行）——主编排，`SynthesisPipeline` 类
- `synthesis/core/`——七件套：`config.py`（SynthesisConfig dataclass）、`models.py`（TrajectoryNode/Trajectory/SynthesizedQA 三个数据类）、`worker.py`（SandboxWorker 沙箱适配器）、`sampler.py`（TrajectorySampler 树采样）、`selector.py`（TrajectorySelector 轨迹选择）、`synthesizer.py`（QASynthesizer 问答合成）、`utils.py`（OpenAI 客户端+XML/JSON 解析+重试）
- `synthesis/api.py`（85 行）——`load_config/load_seeds/synthesize` 三函数轻量门面
- `configs/synthesis/`——八个场景配置（doc/doc_ds/ds/GUI/rag/text2sql/web/web_rag）

## 二、内部结构

### 装配链：pipeline.py L42-93

构造函数 `SynthesisPipeline.__init__`（pipeline.py:42-64）做三件事：校验配置（pipeline.py:51-53 调 `config.validate()`，缺 model_name/api_key/base_url 直接抛 ValueError）、建输出目录、初始化两个 JSONL 文件句柄路径（pipeline.py:59-60：`synthesized_qa.jsonl` 与 `trajectories.jsonl`）。

真正的装配发生在 `run_async`（pipeline.py:66）：

1. **worker**（pipeline.py:79）——`SandboxWorker(self.config, worker_id="main_worker")`，沙箱适配器；
2. **启动**（pipeline.py:85）——`await worker.start(create_sessions=False)`，注意 `create_sessions=False`：会话创建被刻意推迟到每个 seed 的 setup（pipeline.py:84 注释"Defer session creation to per-seed setup to avoid a short-lived initial session"），避免起一个马上就要重建的短命会话；
3. **三大组件**（pipeline.py:91-93）——`TrajectorySampler(worker, config)` / `TrajectorySelector(config)` / `QASynthesizer(config)`，一行一个，全部无状态构造。

之后进入逐 seed 主循环（pipeline.py:96-191），每颗种子四步：

- **会话隔离**（pipeline.py:110-143）：先 `list_sessions()` 探测现存会话，对每个 `resource_type` 以 `custom_name = f"{resource_type}_{source_id}"`（pipeline.py:139）重建——已存在则 `reinitialize`，否则 `create_session`。这保证 seed 之间不串数据（比如上颗 seed 写进 RAG 知识库的干扰文档不会泄漏到下一颗）；
- **Step 1 采样**（pipeline.py:147）：`sampler.sample_trajectory_tree(seed_content, seed_kwargs)` 返回整棵节点树；
- **Step 2 选择**（pipeline.py:155-161）：`selector.select_trajectories(nodes, root_id, ...)` 从树里挑至多 `max_selected_traj` 条根到叶路径；
- **Step 3 合成**（pipeline.py:170-176）：逐条轨迹调 `synthesizer.synthesize_qa(trajectory, qa_idx)`，失败的轨迹只打警告跳过；
- **落盘**（pipeline.py:179-185）：QA 对与轨迹各自**追加写** JSONL——中途崩了已产出的数据不丢。

### 四大组件内幕

**SandboxWorker**（synthesis/core/worker.py:18-128）是 sandbox 包的薄适配层：构造时把 config 的六个沙箱参数（server_url/worker_id/auto_start/config_path/timeout/warmup_resources）灌进 `Sandbox` 门面类（worker.py:27-34）。`execute_tool`（worker.py:101-110）纯转发 `self.sandbox.execute()`；`execute_tool_sync`（worker.py:112-124）是个小机巧：检测到已有事件循环时借 `ThreadPoolExecutor` 起新线程跑 `asyncio.run`，否则直接跑。细节：worker.py:75-76 对 `bdb.BdbQuit`（断点调试退出）做了特殊透传，不打日志不吞异常——给插 pdb 调试的人留的活口。

**TrajectorySampler**（synthesis/core/sampler.py:20-374）是全包最重的组件。树探索逻辑在 `_explore_node`（sampler.py:96-110）：深度未过 `depth_threshold` 时每节点开 `branching_factor` 个孩子，过了就只开 1 个（sampler.py:102），兄弟节点用 `asyncio.gather(..., return_exceptions=True)` 并发探索（sampler.py:110）。每个孩子的动作用 `<intent>/<tool_name>/<parameters>` XML 协议从 LLM 生成（sampler.py:165-204，解析器在 utils.py:61-97），执行结果经 `format_tool_result` 格式化成干净字符串再存进节点的 observation（sampler.py:213-218）。

采样质量的两道防线：

- **动作签名去重**（sampler.py:320-355）：`tool_name(规范化参数JSON)` 做签名，参数里超 160 字符的字符串折叠成 `md5` 指纹（sampler.py:334-347），同 seed 内重复动作直接丢弃（sampler.py:191-193）；
- **已探索清单注入**（sampler.py:357-374）：最近 40 条签名格式化进 prompt，明令"You MUST propose a NEW action... Repeating any of them is strictly forbidden"（sampler.py:283-285），早期动作被省略但仍在禁止之列（sampler.py:370-372）。

**TrajectorySelector**（synthesis/core/selector.py:12-171）纯 Python 无 LLM 参与。流程：找全部叶子（selector.py:40）→ 过滤深度不足 `min_depth` 的（selector.py:44）→ 回溯建根到叶路径（selector.py:67-82）→ 百分制评分排序（selector.py:148-171：**深度 40 分**（`min(len(path)/5, 1)*40`）+ **信息量 30 分**（路径平均观察长度做 min-max 归一）+ **多样性 30 分**（路径覆盖的工具种类占可用工具比例））→ 贪心选 top-k，与已选路径做 **Jaccard 相似度**检查，超过 `path_similarity_threshold`（默认 0.7）的跳过（selector.py:123-131）。

**QASynthesizer**（synthesis/core/synthesizer.py:15-228）负责最后的出题。prompt 里写死了六条出题军规（synthesizer.py:163-174）：答案必须是具体事实、禁问 How/Why、**问题不得含答案文本**（anti-shortcut）、问题不超过 2 句、**必须 ≥3 跳**、答案 ≤1 句无废话。产出必须是 JSON（`response_format={"type": "json_object"}`，synthesizer.py:44），且 `reasoning_steps` 至少 3 步（synthesizer.py:89-90）。代码侧还有两道验收（不合规就重试，最多 3 次，temperature 每次 +0.1，synthesizer.py:43）：答案泄漏检查 `_answer_leaks_into_question`（synthesizer.py:115-121，归一化后判断 answer 是否出现在 question 里）和冗长检查 `_question_too_verbose`（synthesizer.py:123-129，>85 英文词或 >500 字符拒收）。**失败原因会回注进下一轮 prompt**（synthesizer.py:190-196"[Regeneration Required - Previous Output Rejected]"），这是很漂亮的自我修正回路。

### 格式化层：result_formatter 九类 + 异常体系

sampler 拿到的原始工具响应是 `{code, message, data, meta}` 信封（result_formatter.py:23-35），`format_tool_result`（result_formatter.py:867-887）负责拆信封提取 agent 可读文本。继承结构：

- **ToolResult 基类**（result_formatter.py:111-154）：ABC，抽象方法 `to_str(verbose)`；`success` 从 metadata 来（由顶层 `code==0` 推出，result_formatter.py:770）；
- **九个具体类**：BashResult（result_formatter.py:161，成功只回 stdout）、CodeExecutionResult（result_formatter.py:226，带内存/耗时 verbose）、VMResult（result_formatter.py:291，只留 accessibility_tree 滤掉截图）、BrowserResult（result_formatter.py:314，按 image_path/url/text 三形态分支）、WebSearchResult（result_formatter.py:366）、RAGSearchResult（result_formatter.py:422，官方钦定的"标准模板"）、VisitResult（result_formatter.py:479，warning 追加）、DocResult（result_formatter.py:545，doc:/ds: 六种前缀共用）、SQLResult（result_formatter.py:578，按 list_databases/get_schema/execute 三态分别渲染）；
- **ResultFormatter 工厂**（result_formatter.py:702-860）：先按工具名精确匹配（result_formatter.py:785-801），再退到 `resource_type` 或工具名前缀查 `FORMATTER_MAP`（六键：bash/code/browser/vm/doc/ds，result_formatter.py:720-727），查不到抛 ValueError 并提示用 `register_formatter`（result_formatter.py:840-860）注册——"没有通用兜底格式化器"是刻意的（result_formatter.py:16）。

异常体系在 sandbox/sandbox.py：`SandboxError` 基类（sandbox.py:126）+ 三个子类 `SandboxConnectionError`（sandbox.py:131）/`SandboxServerStartError`（sandbox.py:136）/`SandboxSessionError`（sandbox.py:141），分别对应连接失败、自动拉起服务失败、会话操作失败三种处置路径。加上 result_formatter 的九个 ToolResult 子类，这就是图谱里"12 条 inherits 边"的来处。

### config 八场景（configs/synthesis/）

| 配置 | 工具 | max_depth/branching | resource | 特色 |
|---|---|---|---|---|
| doc_config.json | doc-search, doc-read | 20/2 | 无 | 强调跨页证据+视觉元素 |
| doc_ds_config.json | doc 两件+ds 三件 | 20/2 | 无 | 文档+数据混合探索 |
| ds_config.json | ds_inspect_data, ds_read_csv, ds_run_python | 20/2 | 无 | 唯一用 `${OPENAI_API_KEY}/${OPENAI_API_URL}` 的（其余走 OpenRouter） |
| GUI_config.json | vm- 十四件 | 10/1 | vm | `sandbox_auto_start: false`（GUI 沙箱需手工起）；seeds/sandbox 路径双断链（见下） |
| rag_config.json | rag-search | 10/2 | rag（top_k=10） | 默认配置最接近文档示例 |
| text2sql_config.json | sql:list_databases, sql:get_schema, sql:execute | 4/1 | sql | 含 `/path/to/` 占位符；`target_qa_count` 字段实际不生效 |
| web_config.json | web-search, web-visit | 50/2 | 无 | 最深探索 |
| web_rag_config.json | rag+web 三件 | 50/2 | 无 | 混合检索 |

八场景同构：换工具清单、换 prompt tips、换深度参数，装配链一行不改——这是本线最核心的扩展方式。

## 三、外部连接

- **向下游 sandbox 包**：worker.py:13 `from sandbox import Sandbox`；sampler.py:11 `from sandbox import format_tool_result`；sampler.py:17 `from sandbox.tool_schemas import get_tool_schemas`——工具 schema 不在 synthesis 里维护，统一从 sandbox/tool_schemas 取。
- **向 rollout 线**：产出的 `synthesized_qa.jsonl` 就是 benchmark/infer 线的燃料（configs/infer 四场景消费的 seeds 与 QA 同构）；轨迹数据可供训练侧蒸馏。
- **向 LLM 供应商**：utils.py:12-17 `create_openai_client` 走 OpenAI 兼容协议，base_url 可指 OpenRouter（`${OPENROUTER_API_KEY}`）或任意兼容端点。
- **上游 seeds**：五域种子（seeds/doc|ds|GUI|rag|web），见第 10 篇。

## 四、数据流

一颗种子的完整旅程：

```
seeds.jsonl 一行 {content, kwargs}
  → generate_source_id (pipeline.py:33-36, md5前8位) → "src_0001_ab12cd34"
  → 会话重建 custom_name=rag_src_0001_ab12cd34 (pipeline.py:139)
  → sampler: root(intent="Initialize exploration") → _explore_node 并发分叉
      每节点: LLM→<intent><tool_name><parameters> → worker.execute_tool
             → sandbox HTTP → format_tool_result → observation 存节点
  → 节点树 Dict[node_id→TrajectoryNode]
  → selector: 叶子→路径→(40深度+30信息+30多样性)评分→Jaccard去重→top-k Trajectory
  → synthesizer: 每条 Trajectory → LLM(JSON模式) → 验收(防泄漏/防冗长/≥3跳)
             → 失败原因回注重试×3 → SynthesizedQA
  → 追加写 results/ds_synthesized_qa/{synthesized_qa,trajectories}.jsonl
```

注意两条异步通道并存：整条 pipeline 是 async（sampler 内部 gather 并发），但 selector/synthesizer 是同步函数（utils.py:100-115 的 `chat_completion` 是同步阻塞版）——只有采样阶段吃并发红利，出题阶段串行。对以采样为主要成本的场景（web max_depth=50）这是对的取舍。

## 五、设计决策（含批判）

**做得好的**：①证据先行——答案必须 grounded 在工具观察里，从机制上压幻觉；②三重防捷径（prompt 军规+代码泄漏检查+reasoning_steps≥3），比单靠 prompt 可靠；③失败原因回注重试（synthesizer.py:190-196）是教科书级的 self-correction；④追加写 JSONL 天然断点友好；⑤result_formatter"每工具一 formatter、无兜底"的设计逼着新工具作者想清楚 agent 该看到什么。

**要批判的**：

1. **output_dir 参数是骗局**（pipeline.py:45-47）：`__init__` 收了 `output_dir` 参数，但 L45 无条件覆写为 `<仓根>/results/ds_synthesized_qa`。于是 main() 里 `--output-dir`/`config.output_dir`/`OUTPUT_DIR` 环境变量的三级解析链（pipeline.py:250）全部白算，api.py:81 同样白算；八个配置里写的 `results/doc`、`results/text2sql` 等各不相同 output_dir **全部无效**——所有场景的产出混进同一个目录。看起来是某次"聚合输出"改动把参数路径焊死了，但签名和解析链没清理。
2. **docstring 承诺过头**：result_formatter.py:56-65 声称支持 RAGBatchSearchResult/RAGStatsResult/SessionResult/InitResult/BatchExecuteResult 五类，代码里一个都没有——`rag:batch_search` 会落进 FORMATTER_MAP 查无（MAP 只有六键）直接 ValueError（result_formatter.py:810-816）。文档与实现差一档。
3. **config 静默吞字段**：SynthesisConfig.from_dict 用 `valid_fields` 过滤未知键（config.py:68-69），text2sql_config.json 的 `target_qa_count: 100` 就这样无声消失——用户以为设了目标量，实际毫无效果，连 warning 都没有。
4. **GUI 配置双断链**：GUI_config.json 的 `seeds_file: "seeds/vm/seeds.jsonl"` 指向不存在的目录（实际是 `seeds/GUI/`），`sandbox_config_path: "configs/sandbox-server/vm_config.json"` 同样不存在（实际是 `GUI_config.json`）——vm→GUI 改名只改了一半。doc_ds_config.json 的 `configs/server/doc_ds_sandbox.json` 中 `configs/server` 整个目录不存在。text2sql 两处 `/path/to/AgentFlow/` 占位符。
5. **doc_ds 的种子借用**：doc_ds_config.json 的 `seeds_file` 指向 `seeds/web/seeds.jsonl`——混合场景拿 web 域的种子，疑似调试遗留。

## 六、新人提示

- 跑最小闭环：`python synthesis/pipeline.py --config configs/synthesis/rag_config.json`（rag 是默认参数最全的场景）；GUI 场景必须先手工起沙箱（auto_start=false）。
- 找输出别看配置里的 output_dir，直接去 `<仓根>/results/ds_synthesized_qa/`。
- 调 prompt 行为改两处：探索风格在 config 的 `sampling_tips`，出题风格在 `synthesis_tips`+`qa_examples`（都是 config 透传进 prompt 的，不用改代码）。
- 加新工具域的三步：sandbox 侧注册工具+schema → result_formatter 加 formatter 类 → 复制一份 config 改工具清单。前两步漏了任何一步都会在采样期 ValueError。
- 读代码顺序建议：pipeline.py 主循环 → selector.py（最短）→ sampler.py（最长，重点 _explore_node 与 _action_signature）→ synthesizer.py。models.py 三个 dataclass 五分钟可过。
- 排查"为什么这颗 seed 一题没出"：看 stdout 三类警告——"No trajectories sampled"（采样空）、"too similar ... skipping"（路径全撞车，可调低 path_similarity_threshold）、"Synthesis failed after 3 attempts"（出题验收三连拒，看前一行给的 Last reason）。
