# 09 · operators/：域分组算子地图

## 一、角色定位

`dataflow/operators/` 是 DataFlow 的功能心脏：数据清洗/合成/评测的全部能力都以"算子"形式住在这里。目录按**数据形态/领域**切成 14 个域包，每个域内部再按**处理阶段**分四类子目录——`eval`（打分标注）、`filter`（按分筛除）、`generate`（LLM 合成新数据）、`refine`（确定性文本修正）。所有算子继承 `OperatorABC`（core/operator.py:5-15），只需实现一个抽象 `run()`；构造时自带 `ALLOWED_PROMPTS` 元组（core/operator.py:8）限定该算子可绑定的提示词类型。规模分布：general_text 53 个 py 文件居首，text_sft 26、code/text_pt/reasoning/core_text 各约 20、text2sql 13、knowledge_cleaning/conversations 9、pdf2vqa 6、agentic_rag 5、chemistry 3、core_vision/core_speech 各 2。

## 二、内部结构

**发现机制三件套**：① 域包 `__init__.py` 统一用 TYPE_CHECKING + LazyLoader 双轨（text_pt/__init__.py:3-32）——静态检查期可见全部算子符号，运行时 `generate_import_structure_from_type_checking`（utils/registry.py:13-29）用 ast 解析出符号→文件映射后把整个包替换为懒加载代理，import 开销近零；② 全局 `OPERATOR_REGISTRY` 提供 `@register()` 装饰器与按名 `get()`（utils/registry.py:82-134，miss 时逐模块 `getattr` 兜底再抛 KeyError）；③ 顶层 `operators/__init__.py` 的四行再导出全部被注释停用——发现权完全收归注册表。

**各域代表算子**（结合图谱批产物 summary）：

- **general_text**（通用文本质检，无 generate）：filter 线最豪华——五种去重器并立（hash/minhash/simhash/ngramhash/sem，分别对应精确/MinHash-LSH/64 位指纹/n-gram 集合/BERT 语义）；`rule_based_filter.py` 一个文件装 20 个纯规则过滤器；eval 线有 BLEU/CIDEr（自包含 vendored 实现）、BERTScore、VendiScore、task2vec 数据集多样性；refine 线 19 个小修士（HTML 实体/emoji/停用词/SymSpell 拼写等）。
- **core_text**（核心生成底座）：9 个生成器是全仓合成能力的母体——prompted/chunked/format_str 生成器、text2qa 种子与多跳 QA、bench 答案生成、embedding、LightRAG 检索；eval 线的 `unified_bench_dataset_evaluator.py`（1455 行）以 eval_type×metric_type 二维分发覆盖 6 类评测形态，自带 loglikelihood/PPL 打分。
- **text_sft**（SFT 数据产线）：eval 与 filter 一一镜像（deita 质量/复杂度、alpagasus、instag、treeinstruct、superfiltering、rm 偏好），全是论文同名方法落地；generate 线 condor/alpaca_messages/qa_messages 把数据转 messages 格式。
- **text_pt**（预训练语料质检）：fineweb_edu/debertav3/perplexity/qurating/textbook/pair_qual 七套打分器+同名 filter——一条 FineWeb-Edu 风格的 PT 数据筛选拷贝线。
- **reasoning**：数学推理专列——问题类别/难度/可解性三评估、答案七过滤（含 `\boxed{}` 格式检查、math_verify 符号比对、LLM 裁判）、QwenMathEval 风格答案抽取。
- **knowledge_cleaning**：RAG 知识库专列且只有 generate——KBC 分块/清洗/多跳 QA（单条+批量双变体）、MinerU 三模式文档转 Markdown、数学教材 PDF 题目抽取。
- **conversations**：函数调用对话合成（BUTTON 自底向上七级联生成器）+ ShareGPT 结构校验；**code**：8 评估+8 过滤+4 生成，含进程隔离沙箱执行器 python_executor；**text2sql**：七种 SQL 生成变体（含 CoT 投票）；**agentic_rag**：原子/深度/宽度 QA 三合成器；**chemistry/core_vision/core_speech/pdf2vqa**：各 1-5 个专项算子的小域。

## 三、外部连接

算子向上被两层消费：`dataflow/pipeline/`（Python API 流水线，SequentialPipeline 逐算子串 storage）和 webui 的 DynamicOperatorSystem（operator_pipeline.py:56-65 反射注册表生成表单）。向下依赖三根支柱：`LLMServingABC`（core/llm_serving.py，算子只认接口不认实现，vllm/api/sglang 可换）、`FileStorage`（utils/storage.py，`storage.step()` 滚动落盘）、`dataflow/prompts/`（71 个 PromptABC 子类按域对号）。eval↔filter 是仓内最强耦合模式：filter 普遍实例化同名 SampleEvaluator 打分再按区间筛（如 code_doc_quality_filter.py 委托 CodeDocumentQualitySampleEvaluator）。

## 四、数据流

单个算子的标准节拍：`run(storage)` → storage 读上一步 DataFrame → 逐行/逐批计算（打分列、新数据列或布尔标记）→ 写回 storage 形成下一步缓存。数据集级评估器（DatasetEvaluator，如 vendi_dataset_evaluator）不产出行级列而是返回汇总指标；流水线里 filter 删行、evaluator 加列、generator 加行加列、refiner 原位改写——四种足迹互不冲突，靠 FileStorage 的 step 计数串联成链。

## 五、设计决策（含批判）

**"域×阶段"正交分组是本仓最清晰的架构决策**：新算子该放哪、找算子去哪读，两条坐标一夹即定位；eval/filter 成对设计让"先标注后筛除"可拆开跑（只看分布不删数据），这对数据勘探非常友好。LazyLoader 三件套解决了 200+ 算子全量 import 必炸的问题。

批判三点：① `code_score_filter.py` 源码 TODO 自注"应移入 general filter"——通用数值分数过滤被错放在 code 域，域边界已有腐蚀；② general_text/filter/__init__.py 整文件 60 行全是注释掉的旧注册代码，注释里的 `cur_path` 仍指向已不存在的 `dataflow/operators/filter/` 旧路径，是重构未清理的化石；③ 命名不对称：general_text 是唯一没有 generate 的文本大域（生成能力被抽到 core_text），新人极易在此迷路——"general"其实是"质检工具箱"而非"通用"。

## 六、新人提示

入门三步：① 读 core/operator.py:5-15（29 行）确立"算子=实现 run() 的类"心智；② 读 text_pt/__init__.py 全文（32 行）掌握 LazyLoader 模板——加新算子就是在此文件 TYPE_CHECKING 块加一行 import；③ 从 `lowercase_refiner.py` 这类最小算子读起，再到 general_text/filter 体会 evaluator 委托模式。选算子时记住 eval 先行：先跑 evaluator 看分数分布，再定 filter 阈值，比盲设阈值后重来省一轮全量计算。
