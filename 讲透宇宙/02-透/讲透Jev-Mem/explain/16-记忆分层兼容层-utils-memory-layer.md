> 标题：记忆分层兼容层——utils/memory_layer.py 精讲 · 源文件：utils/memory_layer.py（801 行）· 图谱标签：记忆系统公共底座 / LLM 客户端工厂 + 遗留 Agentic 记忆系统（半休眠）

## 角色定位

全仓唯一的 LLM 客户端工厂，兼一份从 Agentic Memory 范式项目整体搬入的遗留记忆系统。grep 全仓实证：四个消费方（memory/memory_builder.py:53、memory/trg_memory.py:42、jev_mem/benchmarks/locomo.py:73、jev_mem/benchmarks/longmemeval.py:32）**全部只 import `LLMController` 一个名字**——MemoryNote、HybridRetriever、SimpleEmbeddingRetriever、AgenticMemorySystem 仓内零外部引用。801 行里真正在生产上跑的只有工厂加两个后端约 120 行，其余六百多行是被 TRG 图记忆取代的"祖先器官"。上半部（LLM 控制器族）是活的公共底座；下半部（MemoryNote 起的记忆进化系统）是一套自给自足的平行记忆系统，只在 `__main__` 自测里被唤醒。

## 内部结构

**可选依赖旗标区**（utils/memory_layer.py:14-48）：六个 try-import 各设 `*_AVAILABLE` 常量，但除 `NLTK_AVAILABLE` 在 simple_tokenize（utils/memory_layer.py:51）被消费外，其余五个设完即弃——类里裸用 BM25Okapi（utils/memory_layer.py:373）、SentenceTransformer（utils/memory_layer.py:311），缺库不是降级而是 AttributeError。

**LLM 控制器族**（活代码核心）：`BaseLLMController` 只声明 `get_completion(self, prompt)`（utils/memory_layer.py:57-61）；`OpenAIController`（utils/memory_layer.py:63-119）建 client（utils/memory_layer.py:72，支持 OPENAI_BASE_URL 环境变量），每次调用把 usage 三元组追加入账（utils/memory_layer.py:98-101），`get_token_stats` 出五项统计（utils/memory_layer.py:105-119）；`OllamaController`（utils/memory_layer.py:121-166）走 litellm 的 `ollama_chat/{model}` 前缀（utils/memory_layer.py:155-162），异常时按 json_schema 逐属性合成空响应兜底（utils/memory_layer.py:139-151、164-166）。工厂类 `LLMController`（utils/memory_layer.py:168-179）按 backend 分发，非法值 ValueError。

**MemoryNote 记忆单元**（utils/memory_layer.py:181-299）：构造时若 llm_controller 在且 keywords/context/category/tags 任缺，就地触发 `analyze_content` 抽元数据（utils/memory_layer.py:200-205）——LLM 调用藏在构造函数里；analyze 用 strict json_schema prompt 抽三件套（utils/memory_layer.py:256-282）。

**检索器双胞胎**：`HybridRetriever`（utils/memory_layer.py:301-438）BM25+语义双通道、alpha 线性混合（utils/memory_layer.py:433）、pickle+numpy 双文件持久化（utils/memory_layer.py:318-357）；`SimpleEmbeddingRetriever`（utils/memory_layer.py:440-545）纯语义单通道，content+元数据拼检索文档（utils/memory_layer.py:539-541）。

**AgenticMemorySystem**（utils/memory_layer.py:547-759）：门面类。`add_note`（utils/memory_layer.py:592-603）建 note→进化判定→入 retriever，进化计数每满 evo_threshold 触发 `consolidate_memories` 全量重建检索器（utils/memory_layer.py:599-602、605-621）。`process_memory`（utils/memory_layer.py:623-723）拿 5 近邻拼进化 prompt（模板 utils/memory_layer.py:558-588，schema 629-675），LLM 判 should_evolve 后执行 strengthen（连接并入 links，utils/memory_layer.py:698-702）或 update_neighbor（按序改写邻居 context/tags，utils/memory_layer.py:703-722）。`run_tests`（utils/memory_layer.py:761-799）是 `__main__` 自测入口。

## 外部连接

对内依赖只有 `memory.local_device.local_model_device`（utils/memory_layer.py:4，用于 utils/memory_layer.py:311、449 的设备选择）。对外被引四处（grep 实证）：memory_builder 构造器内裸 import（memory/memory_builder.py:53）；trg_memory 用 try/except 包裹并设 LLM_AVAILABLE 降级（memory/trg_memory.py:41-46）；locomo score-only 内延迟 import（jev_mem/benchmarks/locomo.py:73）；longmemeval 顶层 import（jev_mem/benchmarks/longmemeval.py:32）。**口径差**：图谱 fanOut 标整个文件"被 4 模块依赖"，实测只有 LLMController 被用；其余公共类是"导出无人 import"的悬挂面。

## 数据流

**生产流（活的半边）**：MemoryBuilder 构造期 `LLMController(llm_backend, llm_model, api_key)`（memory_builder.py:53）→ 实例传给 AnswerFormatter、EpisodeSegmenter 的 BoundaryDetector（episode_segmenter.py:77 解包 `.llm`）、Evaluator/LLMJudge → 各处统一调 `controller.llm.get_completion(prompt, response_format, temperature)`，token 账本沿途累积。

**遗留流（休眠的半边）**：`add_note` → MemoryNote 构造内 analyze_content 抽元数据 → `process_memory` 取 5 近邻 → 进化 prompt 交 LLM → strengthen 写 links、update_neighbor 改邻居 → 计数到阈值全量 consolidate。这条链用自己的存储与检索器，与 TRG 图、FAISS 零接触——两套体系互不往来，正是"分层兼容"的字面写照。

## 设计决策

**工厂+策略双后端**（utils/memory_layer.py:168-179）是本层被留下的真实理由：切 openai/ollama 只改一个字符串，base_url 环境变量（utils/memory_layer.py:72）让第三方端点零代码接入。**Ollama 空响应合成**（utils/memory_layer.py:139-151、164-166）是刻意的静默容错：小模型常吐不出合法 JSON，与其炸管线不如按 schema 造一个"全空但结构合法"的返回——代价是失败被吞掉，只能靠空返回值察觉。**strict json_schema prompt**（utils/memory_layer.py:256-282、629-675）是全仓 LLM 调用纪律；**token 记账**（utils/memory_layer.py:74-78、105-119）留一手成本数据。

批判性地看，休眠半边有一串实锤隐患：`HybridRetriever.add_document` 增量路径三处断裂——`self.bm25.add_document` 在 BM25Okapi 上不存在（utils/memory_layer.py:405）、`torch.cat` 的 torch 未 import 必 NameError（utils/memory_layer.py:411）、张量与 numpy 混接（utils/memory_layer.py:407-411）；`analyze_content` 外层 except 引用可能未赋值的 `response`（utils/memory_layer.py:291-293），内层裸 `except:` 把原始字符串当 dict 返回（utils/memory_layer.py:284-287），下游 `analysis["keywords"]` 随之 TypeError；`links` 标注 Dict 实按 list 用（utils/memory_layer.py:187、209、701）；`find_related_memories` 标注 List[MemoryNote] 实返 (str, list) 元组（utils/memory_layer.py:725-736），`run_tests` 还按旧接口取 `.content`（utils/memory_layer.py:788-797），今天跑必崩。这些不影响生产（无人调用），但说明休眠代码没有测试护栏会自腐。

## 新人提示

先读 168-179 的工厂与两个 Controller 的 get_completion——唯一需稳定维护的公共接口；MemoryNote 之后是"考古区"，改动前先 grep 确认无外部引用。

四个常见误解：以为这是主记忆系统的实现层——不是，主系统是 memory/trg_memory.py 的 TRG 图，AgenticMemorySystem 是未被采用的平行方案；以为 `*_AVAILABLE` 旗标控制了降级——没有，五个旗标设完即弃，缺库照样炸（utils/memory_layer.py:14-48 对照 373/311）；以为 get_completion 签名与基类一致——OpenAIController 要求 response_format 必传（utils/memory_layer.py:82 对照 59），按基类签名裸调会 TypeError；以为 Ollama 后端失败会报错——它返回合成空 JSON（utils/memory_layer.py:164-166），排查"元数据全空"先查这里。
