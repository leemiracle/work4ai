# DataFlow ONBOARDING（新工程师入门指南）

> 图谱 1252 节点/3743 边/14 层 · commit 7d7ff715 · v1.0.13（dataflow/version.py:1）· 行号锚经源码核实

## 1. 一句话定位

DataFlow 是 OpenDCAI org 的数据为中心 AI 主仓（PyPI 包名 open-dataflow）：为 LLM 训练提供**数据生成、清洗、评测**一站式能力的开源系统。核心抽象 operator+pipeline+LLM serving，200+ 算子按 14 域组织、Registry 插件化注册；入口覆盖 `dataflow` CLI 七组子命令、Gradio WebUI 与 statics/ 下 53 条官方流水线。用户：构造/治理训练数据的工程师与贡献算子的开发者。README.md:128 自述 SIGMOD 2027 论文与 ICML 2025/LIC 2025 双冠军。

## 2. 心智模型：三契约 + Registry + Pipeline

200+ 算子全是同一范式实例化，先立骨架：

- **OperatorABC**（dataflow/core/operator.py:5）：唯一抽象方法 `run()`，202 个算子类的共同祖先；`get_operator` 工厂（operator.py:17）按名实例化。
- **PromptABC/DIYPromptABC + prompt_restrict**（dataflow/core/prompt.py:6/12/28）：装饰器注入 ALLOWED_PROMPTS 白名单并构造时校验 prompt_template 类型——LLM 算子提示词守门机制。
- **LLMServingABC**（dataflow/core/llm_serving.py:5）：`generate_from_input/start_serving/cleanup` 三方法，模型来源对算子透明。

**插件机制**：算子文件头 `@OPERATOR_REGISTRY.register()`（operators/core_text/generate/prompted_generator.py:10）注册；Registry（dataflow/utils/registry.py:34）+LazyLoader（registry.py:261）+各域 `__init__.py` TYPE_CHECKING 块懒加载，import 不拖重依赖。

**Pipeline 编排**：PipelineABC（dataflow/pipeline/Pipeline.py:19）`compile()`（Pipeline.py:44）把算子属性包成 AutoOP 代理（dataflow/wrapper/auto_op.py:38）、按 input_/output_ 键前缀建依赖图校验；数据统一走 DataFlowStorage（dataflow/utils/storage.py:15）。

骨架一句话：**算子吃 DataFrame 行产新列/新行；pipeline 串联算子；storage 落盘；serving 供脑**。

## 3. 代码地图（14 层 layers）

- **L01 配置文档**：README 双语 45 节、pyproject（CLI 入口+15 extras）、pytest.ini、Dockerfile（cuda12.4.1）。
- **L02 core**：三契约+WrapperABC+logger/version。
- **L03 general_text**（约 50 算子）：三类去重、语言/blocklist 过滤、PII 匿名化、BLEU/CIDEr/Task2Vec/Vendi 评估。
- **L04 text_sft(24)+text_pt(15)**：Alpagasus/DEITA 评分、FineWeb-Edu/Qurating/困惑度/教材质量；eval 与 filter 同名成对。
- **L05 core_text(19，README 最小示例在此)+reasoning(19 数学题合成与答案过滤)+conversations(BUTTON 函数调用)**。
- **L06 code(20，双向生成+python_executor 沙箱)+text2sql(SQL 合成/难度分类/真库执行验证)**。
- **L07 knowledge_cleaning(MinerU 三模式 PDF→MD→分块→清洗→多跳 QA)+agentic_rag(原子/深度/宽度 QA+QAF1)**。
- **L08 垂直域**：chemistry（SMILES）、pdf2vqa、core_speech、core_vision。
- **L09 prompts 模板库**：与算子配套（text2sql.py 1681 行 9 类、agenticrag.py 31 类）。
- **L10 serving**：11 后端（API/vLLM/SGLang/VLM/LiteLLM/VertexAI/Perspective/LightRAG/LALM/嵌入）。
- **L11 引擎 utils**：storage 六实现、pipeline_runner 断点续跑、pipeline_checkpoint 事务、training_data 状态机、rayorch 并行。
- **L12 入口**：cli.py Typer 七子命令+cli_funcs（pdf2model/text2model 训练管线）+webui。
- **L13 statics/pipelines**：api/cpu/gpu 三档 53 官方 pipeline+playground。
- **L14 scaffold+example**：cookiecutter 模板+各域最小输入数据（pipeline_math_short.json 被 5 条流水线引用）。

## 4. 核心链路走读：一条数据的旅程

多数流水线直接 `python xxx_pipeline.py` 跑：

1. **入口**：`__main__` 实例化普通类调 `forward()`（statics/pipelines/api_pipelines/agentic_rag_pipeline.py:39-52 最短样本）；CLI 则从 dataflow/cli.py:19 的 Typer app 进七子命令，实现委托 cli_funcs。
2. **存储**：FileStorage（dataflow/utils/storage.py:477）指向首输入文件与 cache 目录；算子跑完 `storage.step()`（storage.py:562）切到带前缀新 jsonl（中间结果链即审计轨迹）。
3. **算子**：PromptedGenerator.run（prompted_generator.py:58）：`storage.read('dataframe')` 读全量 → 拼 prompt → `llm_serving.generate_from_input` 批量生成 → 数量对齐校验 → 写回 output_key 列。
4. **模型**：APILLMServing_request（dataflow/serving/api_llm_serving_request.py:21、:345）线程池打 OpenAI 兼容端点，每请求经 _bounded_api_worker 可杀子进程重试；换后端算子零改动。
5. **引擎**：继承 PipelineABC 的先 `compile()` 键校验（Pipeline.py:44），run_compiled_pipeline（dataflow/utils/pipeline_runner.py:168）分批执行；本地 JSONL/CSV 自动启用事务 checkpoint（pipeline_checkpoint.py）断点续跑。

## 5. 运行与调试

**安装**（README.md:287-295）：`pip install uv && uv pip install open-dataflow`；GPU 加 `[vllm]` extra，另有 15 个 extras 按域加装；Docker 用仓根 Dockerfile。

**第一条流水线**（statics/pipelines/api_pipelines/README.md）：`export DF_API_KEY=...` → `dataflow init` 复制 statics 资产到 cwd（cli_funcs/cli_init.py:18-35）→ 改 llm_serving/storage 参数 → `python reasoning_pipeline.py`。无 key 可跑 cpu_pipelines/reasoning_pipeline.py（零 LLM）；`dataflow webui`（README.md:382）可视化构建。

**加自定义算子**：`dataflow init repo` 走 cookiecutter（statics/scaffold/cookiecutter.json），模板 my_prompted_generator.py 演示标准写法，跑 test_registed_op.py 验证注册增量。

**调试**：`dataflow env` 环境报告；`get_logger`（dataflow/logger.py）统一日志；draw_graph 导出键依赖图。

## 6. 已知坑与断链（全部源码实证，阅读前必看）

1. **幽灵模块 `dataflow.operators.generate`**：目录不存在（operators/ 下 14 域无 generate）但 3 处引用——webui/kbcleaning_tools.py:1 一次导入 4 个旧类名（CorpusTextSplitterBatch 等）必 ImportError，**Gradio 知识清洗链断裂**；.github/ISSUE_TEMPLATE/2-ask-for-help.yaml:44 与 scaffold 模板内同名文件:44 示例同病。正解见 cli_text.py:211-213 从 knowledge_cleaning 导新名 `as` 别名；FileOrURLToMarkdownConverter 三模式在 mineru_operators.py:200/325/493。
2. **53 个 pipeline 仅 7 个真继承 PipelineABC**（benchmark_eval type3-6 等；BatchedPipelineABC 继承 0）——其余"普通类+__main__"直跑，compile 键校验用不上；读 pipeline 先看 __init__/forward。
3. **text2model Step1 断链**：cli_text.py:390 取 merge_json_jsonl.py，该脚本全仓不存在（statics/ 只有 pipelines/playground/scaffold），`dataflow text2model train` 第一步必失败。
4. **serving/__init__.py:1-15 导出 11 后端但漏 FlashRAGServing** → agentic_rag_multihop_core_pipeline.py:12 导入必 ImportError；手动 `from dataflow.serving.flash_rag_serving import ...` 可绕。
5. **lite_llm_serving.py:22 与 :25 连续两个 `def start_serving`**：内容相同的合并残留，后者覆盖前者，非 IDE 幻觉。
6. **LazyLoader 体系致 IDE 跳转失灵**（设计非 bug）：TYPE_CHECKING 块只是类型声明、运行时被伪模块替换。技巧：开 operators/<域>/__init__.py 的 TYPE_CHECKING 块看全量目录，按路径直接开实现。
7. **配置漂移**：pytest.ini ignore 的 test_ragkbcleaning.py 与 test/general_text.py 已不存在，norecursedirs 又排除 dataflow 包；pyproject.toml:13 `requires-python=">=3.7"` 与 README.md:280"Python>=3.10"矛盾——按 3.10+ 备环境（pyarrow==20.0.0 即其钉版）。

## 7. 上游与生态

OpenDCAI org 关系仓三层：**分发层** DataFlow-Ecosystem（README.md:141）下 DataFlow-MM 等域扩展仓，用脚手架同款协议接入；**产品层** DataFlow-WebUI（cli_funcs/cli_webui.py 运行时从其 Release 下载后端）；**训练层** DataFlex 是 pdf2model 可选后端（dataflex_pdf2model_launcher.py，规避 Qwen2.5-VL 批次崩溃）；DataMind/gugu 等构成数据-模型闭环。文档交叉：同级 `deepwiki/` 已抓取 DeepWiki 102 页，10.4/10.5 章与本指南第 5 节互补；docs/ 另有训练数据准备与韧性 JSONL 两份指南。

## 8. 学习路径（新人 7 天）

图谱 tour 15 步即现成参观路线，配同级 `explain/` 精讲：

- **D1-2 地基**：tour step-01~04（README→三契约→registry→最小算子），配 explain/01-core-operator.md、02-core-prompt-serving.md；跑通一条 cpu_pipeline。
- **D3 算子域巡礼**：step-05~09 按需选域——清洗读 general_text（minhash 去重/task2vec），数学读 reasoning+prompts/reasoning/math.py（难度锚定与双题融合），指令数据读 text_sft 三连；配 explain/09/10。
- **D4 生产线**：step-10~11（code 沙箱、text2sql 真库验证、knowledge_cleaning 四步链）。
- **D5 引擎**：step-12~13，精读 compile 与 checkpoint，中断验证断点续跑。
- **D6 入口与贡献**：step-14~15，`dataflow init repo` 写一个算子，对照 REVIEW.md 审查清单自检（上游 PR 验收标准）；配 explain/07、08。
- **D7 实战**：真实需求落 pipeline，先查 L03/L04 现成算子；绕开坑 1 WebUI 断链（走别名导入）。

> 全程提醒：本仓 IDE 跳转基本不可用（坑 6），"开 __init__ 看目录、按路径开文件看实现"。
