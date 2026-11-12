# 06 · nemo/retriever-synthetic-data-generation：检索器合成数据管线的抽象族

> 覆盖 `nemo/retriever-synthetic-data-generation/`（`nemo_retriever_sdg/` 十文件 1200 行 + `scripts/run_pipeline.py` + `scripts/conf/` 三配置）。核心是五个 ABC 组成的组装式管线：**Processor / QAGenerator / Filter / Analyzer / Evaluator**，全部围绕一个 `Corpus` 数据类型流转。

## 一、角色定位

回答的问题：**"没有人工标注的语料，怎么造出能训练/评测检索器的合成 QA 数据，并量化'合成数据值多少'？"** 与 `RAG/tools/evaluation/`（第 3 篇）相邻但哲学相反：那边黑盒 HTTP 打服务评 **RAG 应用**；这边白盒数据变换评 **embedding 检索模型**，全程不依赖部署服务。方法论：SQuAD 语料进 → LLM 生成合成问题 → 双重过滤（简单度/可答性）→ 改写增难 → BEIR 框架打分 → original vs synthetic 对比报告——输出直接可跑 BEIR 的 DenseRetrievalExactSearch，检索社区标准协议。

## 二、内部结构

**数据底座 `Corpus`**（`dataset.py`）：`@dataclass Corpus: data: dict`（dataset.py:29-30）——薄到只有一个字典，但格式严格：`data[].paragraphs[0].context/document_id/title/qas[]`，qa 带 `synthetic: true` 与 `answer_start: -1` 生成式标记（dataset.py:46-66 docstring 即格式规范）。三入口：`load_data` 分派 squad/rawdoc（dataset.py:31-36）；`load_rawdoc` 逐行 JSONL 装配空 qas 段（dataset.py:78-94）——**无标注原始语料一等公民**。三出口：`to_json`（dataset.py:97）/`to_csv`（dataset.py:102）/`to_beir`（dataset.py:118）——BEIR 三件套 corpus.jsonl（dataset.py:217）、queries.jsonl（dataset.py:219）、qrels/test.tsv（dataset.py:223）。

**五个抽象族**（每 ABC 配 Dummy，管线可空转）：

1. **Processor**（processor.py:18-22）：`process(corpus)->corpus` 前后处理钩子。真实实现两枚：`ParaphraseQuestionRewriter`（rewriter.py:18）只改写 `synthetic: true` 的问题（rewriter.py:35-45），提示词要求"更短、更难、降低与原文词汇重叠"（rewriter.py:74-79）；`DivergenceCalculator`（calculator.py:23）给每题算 PINC 词汇发散度（1-n-gram 交集比，calculator.py:40-58）——**组件间通过给 qa 字典加字段传递结果**。
2. **QAGenerator**（qa_generator.py:41）：`SimpleQAGenerator`（qa_generator.py:53）默认 `mistralai/mixtral-8x7b-instruct-v0.1` + `integrate.api.nvidia.com/v1`（qa_generator.py:54-55，OpenAI SDK 兼容直连）；`generate()` 流式拼 delta（qa_generator.py:144-148）；`parse_response` 是**字符串手术**——`split("Question")[1:]` 再 `split("Answer")`（qa_generator.py:166-168），逐对配 `get_random_hash()`（qa_generator.py:34，secrets+SHA256）与 `synthetic: true`（qa_generator.py:177-183）。`generate_qa_pairs`（qa_generator.py:162-209）内置**断点续跑**：生成文件逐行载入并用 `assert context ==` 对账（qa_generator.py:173-176）——LLM 贵且慢，缓存对账是刚需。
3. **Filter**（filter.py:28-30）：语义是**给 qa 加分不改成员**（删减由容器统一）。容器 `Filters.apply_filters`（filter.py:37-63）两段式：全部 filter 先各写 `{prefix}__keep` 字段，再按"任一否决即剔除"聚合出 corpus_all/corpus_filtered 双输出（filter.py:49-62）——**全 filter 全样本先评分后聚合**（注释自认计算贵 filter.py:40）。`EasinessFilter`（filter.py:65）双后端：HF SentenceTransformer 本地（filter.py:73-76）或 NIM 嵌入分批算相似度（filter.py:78-88、104-110）；`AnswerabilityFilter`（filter.py:195）LLM-as-a-Judge 按 `criterion_N == "Y"` 判留（filter.py:249-253），解析失败记 None 不硬删（filter.py:256-258）。
4. **Analyzer**（analyzer.py:32）：`analyze(corpus)->Report`；`Report` 支持 `+` 合并（analyzer.py:23-30）。`QuestionLengthAnalyzer`（analyzer.py:43）与 `LexicalDivergenceAnalyzer`（analyzer.py:60）都做 original vs synthetic 双组 `describe()` 对比——**一切分析以"合成组相对原始组"为基准**。
5. **Evaluator**（evaluator.py:28）：`BEIREvaluator`（evaluator.py:38）用 `GenericDataLoader(split="test")`（evaluator.py:77-79）→ 每候选模型 `DRES(SentenceBERT(model_name))`（evaluator.py:84）→ `retriever.evaluate` 得 ndcg/map/recall/precision（evaluator.py:88-91）→ recall5 对比表 CSV（evaluator.py:98-104）与逐题 top-5 命中标志（`__get_topk_rel_doc_flags`，evaluator.py:49-74，多模型交叉表 evaluator.py:121-131）。**最终答案的形态：换合成数据后各检索模型的 Recall@5 动了多少。**

**编排器 `scripts/run_pipeline.py`**（OmegaConf+hydra instantiate）：main()（run_pipeline.py:24）把 pre_processors/qa_generator/post_processors/filters/analyzers 全 `instantiate(...)`（run_pipeline.py:35-60），顺序 load→pre→generate→post→apply_filters（run_pipeline.py:73-77）→ 双语料写 SQuAD+BEIR 四目录（run_pipeline.py:83-90）→ analyzers 合并报告 `report__{all,filtered}.json`（run_pipeline.py:93-98）→ 可选 BEIREvaluator 双语料评测（run_pipeline.py:101-119）。**输出目录已存在即 ValueError**（run_pipeline.py:26）——绝不覆盖上一次实验。三配置 `config.yaml/config-nq.yaml/config-fiqa.yaml` 对应 NQ 与 FiQA-2018 两基准。

## 三、外部连接

LLM：mixtral（生成）+ 可配 judge（AnswerabilityFilter），走 OpenAI 兼容端点。嵌入：EasinessFilter 双通道（HF 本地或 NIM filter.py:78-88）；评测侧本地 SentenceBERT（evaluator.py:84）。BEIR 生态：DRES/GenericDataLoader/EvaluateRetrieval——输出即 BEIR 输入，可与排行榜语境互读。NLTK：PINC 的 n-gram（calculator.py:48-49）。同仓邻居：`nemo/Evaluator/`（LLM-as-a-Judge 微服务化 + Live Evaluation compose 带 nemo-postgresql）与 `nemo/NeMo-Data-Designer/`（托管合成数据设计）是同一主线的另两种形态——本目录是**纯库形态**（无 compose 无服务）。

## 四、数据流

```
squad json 或 rawdoc.jsonl
  │ load_data(dataset.py:31) → Corpus
  ▼ pre_processors（可挂 DivergenceCalculator 加 lexical_divergence 字段 calculator.py:37-47）
  ▼ SimpleQAGenerator（mixtral 逐段生成→split 解析→qa+=synthetic 标记 qa_generator.py:162）
  ▼ post_processors（可挂 Rewriter 增难 rewriter.py:35）
  ▼ Filters.apply_filters（Easiness/Answerability 各写 __keep → 双语料 filter.py:37）
  ├─→ squad/synthetic_data__{all,filtered}.json + beir/{all,filtered}/{original,synthetic}/
  ▼ Analyzers → report__{all,filtered}.json（original vs synthetic describe 对比）
  ▼ BEIREvaluator → 每模型 ndcg/map/recall/precision + recall5 对比 CSV（evaluator.py:98-104）
```

一次实验目录=全部产物：数据（双格式双语料）、分析（report×2）、评测（eval/{all,filtered}/）三族文件，可复现可对比。

## 五、设计决策

1. **评分与删除分离**（filter.py:37-63）：Filter 只写 keep 字段、容器统一聚合——多 filter 否决逻辑可组合可审计（每个 qa 留有被谁否决的痕迹），代价是全量深拷贝两份（filter.py:46-47 注释自认 just in case）。
2. **字符串手术而非结构化输出**（qa_generator.py:166-168，对照第 3 篇 data_generator.py:74-77）：一脉相承的宽容解析；今天可换 response_format/json_mode 但宽容性下降。
3. **断点续跑一等公民**（qa_generator.py:169-180）：逐行 append + context 对齐 assert，中断恢复零重复调用。
4. **original/synthetic × all/filtered 双正交轴**：报告与评测都沿两轴展开（evaluator.py:98-104 recall5 表两列）——"过滤有效吗"与"合成够好吗"同时可答。
5. **Dummy 全家桶**（processor.py:25 / qa_generator.py:48 / analyzer.py:38 / verifier.py:19）：任一环可置空做消融——`verifier.py` 甚至**只有 Dummy**（24 行），验证环节是预留空位。
6. **实验目录不可变**（run_pipeline.py:26-27）：宁报错不静默覆盖——对照实验完整性优先于便利。

## 六、新人提示

- 阅读顺序：dataset.py（29-66 docstring 是最好的格式文档）→ run_pipeline.py（90 行看完全编排）→ filter.py:37-63（聚合机制）→ qa_generator.py:162-209（断点续跑）→ evaluator.py（BEIR 协议）→ 任一 config.yaml 对照理解 instantiate。
- 最小实验：config 里 filters/analyzers 全指 Dummy、max_examples=3——**零 LLM 成本验证管线形状**，再逐步开真件。
- **源码级小缺陷**：`EasinessFilter` 走 NIM 分支且配置缺 `truncate` 时赋值写成 `self.trunacte = "NONE"`（filter.py:83，拼写错），而调用读 `self.truncate`（filter.py:160）——该场景 AttributeError；配置显式给 truncate 即可绕开。
- `paragraphs[0]` 硬索引（filter.py:94/207 等）假定每段单段落——多段落 SQuAD 变体需先拆分。
- 调新数据集：copy config-nq.yaml 改 input_file/output_dir，`model_names` 换候选 embedding 模型；`beir/` 目录产物可直接当检索器训练语料。
- 甄别条款：行号锚在 commit `203b0de` 源码核实；`trunacte` 拼写错（filter.py:83）与 verifier 仅 Dummy（verifier.py:19）为源码实证；"五个 ABC"按文件实证（rewriter/calculator 复用 Processor 接口非独立 ABC）；与 RAG/tools/evaluation 的边界（检索器评测 vs RAG 应用评测）按两目录 README 与代码形态归纳。
