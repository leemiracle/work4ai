# 03 · RAG 评测链：synthetic_data_generator → llm_answer_generator → Ragas/judge 双评测

> 覆盖 `RAG/tools/evaluation/`（synthetic_data_generator / rag_evaluator / notebooks / docker-compose.yaml / compose.env）与姊妹篇 `RAG/tools/observability/`。

## 一、角色定位

评测链是主线六端点契约的**第一个第三方消费者**：不 import 任何 chain-server 代码，纯 HTTP 黑盒打被测服务，因此能评测任何实现 /documents、/generate、/search 的系统。三段流水：**合成数据段**（无标注文档 → LLM 生成 QA 黄金标准）、**填答段**（文档喂给被测 RAG，逐题收集系统答案与检索上下文）、**评测段**（Ragas 六指标或 LLM-as-a-Judge Likert 双路线）。四个 notebook（`notebooks/01_synthetic_data_generation.ipynb`→`02_filling_RAG_outputs_for_Evaluation`→`03_eval_ragas`→`04_Human_Like_RAG_Evaluation`）是同流水线的交互版，`results/qna.json` 是产物样例。

## 二、内部结构

**合成数据生成器**（`synthetic_data_generator/data_generator.py`，96 行）：`generate_synthetic_data`（data_generator.py:43）默认 chunk 3000/overlap 100（data_generator.py:46）、`ai-mixtral-8x7b-instruct, temperature 0.2, max_tokens 300`（data_generator.py:47）。Mistral 风格 `[INST]<<SYS>>...<</SYS>>` 提示模板（data_generator.py:25-33），系统提示只要求"two very good question answer pairs... strictly in a json format with keys [\"question\",\"answer\"]"（data_generator.py:34-38）。流程：os.listdir 取全部文件（data_generator.py:55）→ UnstructuredFileLoader（data_generator.py:66-67）→ RecursiveCharacterTextSplitter 分块（data_generator.py:68-69）→ 逐块 `llm.invoke`（data_generator.py:73）→ **正则抽取** `"question":\s*"([^"]*)"`/`"answer":...`（data_generator.py:74-77）→ 数量相等才逐对入库（data_generator.py:78）。输出四键 `question/ground_truth_answer/ground_truth_context/document`（data_generator.py:80-86）——**上下文与答案同源同块**，是 context_recall 的黄金标准。解析失败只 log 不中断（data_generator.py:88-92 双层 try）。CLI 仅 `--docs`/`--gd_output` 两参（main.py:29-34）。

**填答生成器**（`rag_evaluator/llm_answer_generator.py`，128 行）：`generate_answers`（llm_answer_generator.py:58）先把 PDF 全部 POST /documents 摄取（llm_answer_generator.py:70-72，非 PDF 只提示不上传 llm_answer_generator.py:53-54）。逐题双请求：流式 POST /generate 剥 SSE 前缀 `raw_resp[6:]`（llm_answer_generator.py:102，与 playground 同款私有协议）把 content 累进 `generated_answer`（llm_answer_generator.py:105-106）；POST /search 拿 top-1 chunk 存 `retrieved_context`（llm_answer_generator.py:113-119）。生成参数 `use_knowledge_base: True, temperature: 0.2, max_tokens: 256`（llm_answer_generator.py:63）——低温短上限，评测要稳定。失败以占位串/空串落盘不中断（llm_answer_generator.py:111/122）——**坏样本保留可审计**。

**评测器**（`rag_evaluator/evaluator.py`，236 行）：
- `eval_ragas`（evaluator.py:97）：ChatNVIDIA 包 LangchainLLMWrapper、`NVIDIAEmbeddings(model="ai-embed-qa-4")` 包 LangchainEmbeddingsWrapper（evaluator.py:113-116）→ 四列 Dataset（evaluator.py:132-138）→ `ragas.evaluate` 六指标 answer_similarity/faithfulness/context_precision/context_relevancy/answer_relevancy/context_recall（evaluator.py:144-151）。
- 聚合分 = faithfulness、context_relevancy、answer_relevancy、context_recall 的**调和平均**（`calculate_ragas_score`，evaluator.py:92-94；总体分同算法 evaluator.py:156-158）——短板即崩盘，对应"检索/忠实/相关/召回"四个独立失效面。结果双写 parquet+json（evaluator.py:153-160）。
- `eval_llm_judge`（evaluator.py:165）：双示例 few-shot 模板（女王之死问答好坏各一，evaluator.py:35-81），要求 `{"Rating":1-5,"Explanation":...}`；逐题收集（evaluator.py:191-207），0 分改 1、空值剔除取均值（evaluator.py:214-217）。

**编排与部署**：`rag_evaluator/main.py` argparse 暴露 `--base_url/--generate_answer/--evaluate/--docs/--ga_input/--ga_output/--ev_input/--ev_result/--metrics/--judge_llm_model`，`--metrics` 可选 ragas|judge_llm。compose 起两容器（docker-compose.yaml）：`synthetic_data_generator`（`--docs /data_dir --gd_output /result_dir/qna.json`）与 `rag_evaluator`（全参数，`--metrics ${METRICS:-ragas}`），挂 `DATASET_DIRECTORY→/data_dir`、`RESULT_DIRECTORY→/result_dir`，同 `nvidia-rag` 网络直连 chain-server；`compose.env` 给 `BASE_URL="chain-server:8081"` 等默认。

**观测姊妹篇**（`RAG/tools/observability/docker-compose.yaml`）：otel-collector-contrib 0.102.0 + jaeger all-in-one 1.52 + cassandra 4.0 + jaeger-cassandra-schema——评测量化"质量"，观测定位"哪段慢/错"。

## 三、外部连接

被测系统：chain-server 六端点（BASE_URL 指向任意同契约实现）。LLM：合成/填答/评测共用 `NVIDIA_API_KEY` 走 build.nvidia.com。数据进出：文档目录 → qna.json（合成）→ eval.json（填答）→ result.json/.parquet（评分）三段文件链落 RESULT_DIRECTORY。上游依赖 ragas/datasets 等在各自 requirements.txt；两个生成器是**独立构建目录**（Dockerfile 以 `DIRECTORY_NAME` 参数区分）。

## 四、数据流

```
原始PDF ──(解析→分块→mixtral生成→正则抽对)──▶ qna.json
   │                                            │
   └──(POST /documents 摄取)──▶ 被测RAG ◀──逐题 /generate──┘
                                    └──逐题 /search──▶ eval.json
                            (question/generated_answer/retrieved_context/ground_truth_*)
eval.json ──ragas 六指标──▶ result.parquet + result.json（调和平均 ragas_score）
        └──LLM judge 双示例 few-shot──▶ ratings 均分
```

关键约定：**同一批文档先合成再摄取**——ground_truth_context 与检索库同源，context_recall 才有意义；第三方 QA 集需自带 ground_truth_context。

## 五、设计决策

1. **黑盒 HTTP 契约而非 SDK 复用**：换"可评测任何兼容实现"的通用性，代价是复刻 SSE 解析（raw_resp[6:]）。
2. **正则抽取而非 JSON 解析**（data_generator.py:74-77）：围栏/trailing comma 也能抽出对子，鲁棒优先。
3. **调和平均聚合**（evaluator.py:92-94）：RAG 是串联系统，指标不可互补。
4. **失败样本显式保留**（llm_answer_generator.py:111/122）：占位答案可审计。
5. **三段中间文件可独立重跑**（GENERATE_ANSWERS=False 跳填答直评测）：省 LLM 费用。

## 六、新人提示

- **judge 路线两处源码级缺陷，用前必修**：其一，evaluator.py:204 读 `response_body["Explanantion"]`——键名拼写错（提示词要求 "Explanation"，evaluator.py:52/66），守规矩 LLM 返回正确键即 KeyError 被 except 吞掉、rating 记 None（evaluator.py:208-210），评分静默大量丢失；其二，evaluator.py:171-179 构造的 llm_params（含 `--judge_llm_model`）没接进 evaluator.py:181 的裸 `ChatNVIDIA()`——**换 judge 模型的参数实际不生效**。compose 默认 `${METRICS:-ragas}` 恰好绕开；要用 judge 先修两处。
- 默认值冲突以 compose 为准：main.py `--metrics` 默认 judge_llm，compose/compose.env 均 ragas。
- `retrieved_context` 只取 top-1（llm_answer_generator.py:64/119）——评的是"第一名命中"，评 top-k 需改这两处。
- 合成上限由 mixtral+max_tokens 300 决定（data_generator.py:47），复杂推理 QA 偏浅；换模型改函数默认参数。
- 与观测配合：先 Ragas 定位低分维度（faithfulness 低=编造），再开 ENABLE_TRACING 看检索了什么。
- 甄别条款：行号锚在 commit `203b0de` 核实；"Explanantion" 错键与 llm_params 未接线为源码实证非推测；notebook 与脚本双轨以脚本为准。
