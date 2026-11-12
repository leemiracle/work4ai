# 03 · rollout 主循环：懒加载路由、AgentRunner 与四场景评测

## 角色定位

`rollout/` 是 AgentFlow 的**评测驱动层**：拿一个 benchmark（doc/ds/rag/web 四场景）+ 一个模型端点 + 一份工具清单，跑多轮 agent 循环、落轨迹、算分。它与 sandbox 是「驾驶员与车」的关系——rollout 只管发 ExecuteRequest 和收响应，工具执行的脏活全在 sandbox 服务端。这层的三个看点：包级 `__getattr__` 懒加载路由（重依赖隔离的核心手法）、`SyncAgentRunner` 的组合式同步包装、evaluator 对 DocDancer 官方评分脚本的 importlib 动态挂载。

## 内部结构

**懒加载路由（仓内 7 处先例的总纲）**。rollout 的两个 `__getattr__` 是入口：

- `rollout/__init__.py` L65-78：立即导出轻量符号（RolloutConfig、七个数据模型、Evaluator 等，L37-58），`AgentRunner/SyncAgentRunner/RolloutPipeline/rollout/quick_rollout` 五个重符号全部按名延迟 import；
- `rollout/core/__init__.py` L29-32：只懒加载 runner 一对类，L28 注释直说原因——「requires sandbox which has heavy dependencies」。sandbox 链上拖着 desktop_env/vLLM/Faiss 等巨物，`import rollout` 若触发它们，纯配置场景（比如只想调 `load_config`）会被拖进数秒甚至失败的 import。

仓内同类手法共 7 处，构成一套完整的懒加载谱系：① rollout/__init__ `__getattr__`；② rollout/core/__init__ `__getattr__`；③ DocDancer 线 mineru_vl_utils/__init__.py L21 的 `__lazy_attrs__` 表驱动 `__getattr__`（PEP 562）；④ sandbox/__init__.py L74-79 的 try/except ImportError 可选导入（backend 模块缺席时静默降级）；⑤⑥⑦ config_loader.py 的三处函数内延迟 import——L314-316（`from .app import HTTPServiceServer` + `BackendConfig`，注释明示「Lazy import to avoid circular dependencies」）与 L381（`from .backends.tools import get_all_api_tools`）。三种形态各有分工：`__getattr__` 管「符号按需出现」、try/except 管「可选依赖缺席不崩」、函数内 import 管「打破循环导入/推迟重模块」。config_loader 若顶层 import app，会与 app.py L51-53 反向 import core/routes 形成 import 环。

**AgentRunner 主循环**（core/runner.py，381 行）。`__init__`（L37）只建 OpenAI client 与状态位；`start()`（L59）依次：建 `Sandbox` 门面（L68-75，server_url/auto_start/config_path/timeout/warmup 五参全由 RolloutConfig 注入）→ 为 `resource_types` 逐个建会话（L81-92，resource_configs 从 config 的 resource_init_configs 取 content）→ `_load_tool_schemas`（L129-142）把本地六域+MCP schema 经 `convert_tool_schema_to_openai` 翻成 function calling 格式。`run_task`（L144）组装 system+user 消息进 `_run_conversation`（L223）——主循环本体：`while turn_count < max_turns`（L243），每轮 `async_chat_completion` 带 tools 调 LLM（L248-254）；有 tool_calls 则**每轮只执行第一个**（L271 切片 `[:1]`，串行语义），结果经 `format_tool_result_for_message` 压成 tool 消息回填（L294-305）；无 tool_calls 即最终答案，`extract_final_answer` 抽取返回（L310-313）；打满轮数则倒序找最后一条非空 assistant 消息兜底（L316-323）。`_execute_tool`（L325）把 task.kwargs 合并进参数（L342-343）——这是 seed_path 之类种子参数进入 doc/ds 工具的通道。L103-104 有一处 `bdb.BdbQuit` 例外重抛：调试器退出信号不被「启动失败」分支吞掉，罕见的调试友好细节。

**SyncAgentRunner**（L353-380）：教科书式组合委托——持有一个 AgentRunner（L357），`_run_async`（L359-365）每次新建事件循环跑完即关，start/stop/run_task 三方法纯转发，`__enter__/__exit__` 挂上下文管理。它不继承、不复制状态，同步世界（pipeline、脚本）与异步内核之间只隔这一层薄壳。

**evaluator**（core/evaluator.py，725 行）。`Evaluator.evaluate`（L67）聚合各任务得分；`_get_metric_fn`（L172）按配置名分发到 exact_match/f1/contains/numeric/similarity/llm_judgement 等内置指标，另有三个外部对接指标：`_docbench_lasj`（L329，LLM 判官）、`_mmlongbench_doc_lasj`（L413，读 DocDancer eval 目录的 LasJ prompt）、`_mmlongbench_doc_f1`（L504）——最后这个最有代表性：内部函数 `_load_eval_score`（L507-527）以 `Path(__file__).parents[2]` 定位仓根，找 `projects/DocDancer/eval/eval_score.py`，先 `sys.path.insert`（L519-520）再 `importlib.util.spec_from_file_location` + `exec_module`（L522-524）拿到官方 `eval_score` 函数——**评分口径直接复用 DocDancer 官方实现而非重写**。答案抽取 `_extract_answer`（L562）用 gpt-4o-mini（默认，L574）按 `prompt_for_answer_extraction.md` 抽取，响应按 `Extracted answer:`/`Answer format:` 两标记切分（L606-615），格式归一化映射 Int/Float/Str/List（L620）后调 `eval_score(ground_truth, pred_ans, answer_format)`（L626）。

**四 benchmark 场景**（configs/infer/）：`doc_infer.json`（doc_search/doc_read 两工具，MMLongBench-Doc_LasJ 评测，独立 evaluator 端点）、`ds_infer.json`（ds 三件套，exact_match，sandbox_auto_start + ds_config.json）、`rag_infer.json`（rag_search）、`web_infer.json`。四份配置同构：model/api、max_turns、available_tools、system_prompt、evaluation_metric、data_path、输出目录。`RolloutPipeline`（pipeline.py L36）串起 load_benchmark（L91）→ run_async（L118，内分 _run_sequential L215/_run_parallel L227）→ 落盘；`api.py` 提供 `rollout`/`quick_rollout` 两个糖函数。

## 外部连接

依赖面：sandbox 包（Sandbox 门面+tool_schemas，runner.py L15 注释「Import sandbox components directly to avoid server module dependencies」）、openai SDK、DocDancer 官方脚本与 prompt。被依赖面：synthesis 线复用同一 runner 思路造轨迹；projects/BrowseComp-V3 的 run_rollout.py 是同模式的 web 场景变体。数据面：benchmark/*.jsonl 任务、seeds/ 种子参数、infer_results/ 输出。注意 runner 消费的 `Sandbox` 默认配置（sandbox/sandbox.py L47-91 DEFAULT_SERVER_CONFIG）引用了 bash/browser/code_executor 三个 backend_class，而 resources/ 目录只有 vm/rag/mcp 三个实现——config_loader L354-355 只打 error 日志不中断，但意味着默认配置含三条必然失败的死条目，实际靠 configs/sandbox-server/*.json 覆盖。

## 数据流

单任务全流：benchmark.jsonl 一行 → BenchmarkItem → runner 建 Sandbox 会话 → system_prompt+question 进 LLM → tool_call → Sandbox.execute（HTTP 到 sandbox server）→ 工具结果回填消息 → 循环至无 tool_calls → final_answer → TaskResult（含 Trajectory：messages/tool_calls/turns）→ Evaluator 按指标打分 → summary+trajectory 落盘 infer_results/<场景>/。doc 场景的种子参数流：seed.jsonl kwargs → task.kwargs → _execute_tool 合并 → 工具内 kwargs.get("seed_path")。

## 设计决策（含批判）

- **`__getattr__` 而非全量延迟**：轻符号立即可用、重符号按需加载，比「全部 lazy」少了使用摩擦，比「全部 eager」少了 import 成本。代价是 IDE 跳转与静态分析对延迟符号半盲。
- **每轮只执行首个 tool_call**（L271）：牺牲并行换取轨迹确定性与上下文一致性（后一工具可见前一工具结果），对评测公平性是对的；对追求吞吐的部署场景是明显瓶颈。
- **SyncAgentRunner 每调用新建事件循环**（L361）：简单安全（无循环复用冲突），但高频调用下循环创建开销可见——好在 rollout 粒度是「任务」不是「请求」，可接受。
- **importlib 挂载官方评分脚本**：口径权威、随上游更新；但 exec_module 绕过包管理，脚本内顶层副作用无隔离，且路径硬绑仓内相对位置（parents[2]），仓外安装即断。eval_score.py 内部还有 `eval()` 反序列化（见 06 篇），风险在此被间接放大。
- **evaluator 与 runner 同进程**：评测强依赖 LLM 抽取答案（gpt-4o-mini），评测端点配置错误会让「跑分」悄悄变成「全 0」——doc_infer.json 里 evaluator 三字段与主模型端点分开配置，是刻意的解耦。

## 新人提示

1. 想快速理解主循环，只读 runner.py 的 `_run_conversation`（L223-323）一百行即可，其余都是装配。
2. 加新评测指标：evaluator.py 加 `_xxx` 方法 → `_get_metric_fn` 的映射表补一行 → 配置 evaluation_metric 改名。内置指标零外部依赖，官方对接指标记得检查 projects/ 路径存在性。
3. 调试「import rollout 卡住/报错」时，先怀疑懒加载边界被打破——任何在包级 import sandbox 重链的新代码都会破坏 L65-78 的设计前提。
4. 四份 infer 配置是最佳的配置模板来源：新场景从最像的一份拷起，改 available_tools 与 evaluation_metric 通常就够了。
