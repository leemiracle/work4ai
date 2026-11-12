# RAG-Anything 新人上手指南（ONBOARDING）

> 基于代码图谱（commit 2cd2b332）撰写，关键论断经源码行号抽验核实。

## 1. 这是什么系统

RAG-Anything 是 HKUDS 开源的**多模态文档 RAG 框架**（24.5k★，v1.4.5，`raganything/__init__.py:80`），定位「基于 LightRAG 的 All-in-One 多模态 RAG」。它是 LightRAG 的姊妹仓：LightRAG 解决「文本→知识图谱→检索」，RAG-Anything 补「**任意格式文档→多模态内容块→图谱索引**」的前半段——PDF/Office/图片/HTML/音频/视频统一解析，图表公式交视觉模型描述后与文本一起进 LightRAG 知识图谱，实现模态感知检索（README 五阶段：文档解析→多模态内容处理→分析引擎→知识图谱索引→模态感知检索）。

核心 API 极简：`RAGAnything`/`RAGAnythingConfig`/`Parser` 无条件导出，其余能力（音视频处理器、resilience、callbacks、prompt 切换）全走 try/except ImportError 特性门控，并以 `globals()` 检查动态扩展 `__all__`（`__init__.py:91-139`）——轻量安装也能跑通主链路。

## 2. 总体架构：14 层堆栈

三层域：**产品域（L1-9）→ 质量域（L10-12 测试三梯队 78 文件：解析契约 21/状态机查询 31/其余 26）→ 工程域（L13 构建与 CI；L14 docs+examples 13 个+reproduce 复现）**。产品域：

- **L1 门面**：双语 README（英 1403 行/中 1357 行）+ SECURITY.md（仅 1.4.x+ 修安全，禁公开 issue 报漏洞）。
- **L2 主类**：`@dataclass` 组合 `RAGAnything(QueryMixin, ProcessorMixin, BatchMixin)`（`raganything.py:63-64`）；`config.py` 约 20 字段经 `default_factory=get_env_value` 在**实例化时**读环境（`config.py:18-35`）。
- **L3 处理引擎**：`processor.py`（2677 行）+ `base.py` DocStatus 枚举（`base.py:4-12`）+ `parse_options.py`。
- **L4 解析中枢**：`parser.py`（3726 行，全仓最大）+ `mineru_content.py`。
- **L5 处理器族**：六个 `BaseModalProcessor` 子类（第 4 节）。
- **L6 工具**：`utils.py`（分离/页码回放）、`image_signature.py`（魔数识别）、`asset_urls.py`、`enhanced_markdown.py`（沙箱 MD→PDF）、`omml_extractor.py`（OMML→LaTeX）。
- **L7 批处理**：`batch_parser.py`（ThreadPoolExecutor）+ `batch.py`。
- **L8 韧性**：`resilience.py`（retry/熔断）+ `callbacks.py`（发布-订阅旁路）+ `document_context.py`（contextvars 隔离，`document_context.py:3,8`）。
- **L9 prompt 双语**：`prompt.py` 约 40 键 + `prompt_manager.py` 运行时切换 + `prompts_zh.py`。

## 3. 核心数据流：一份 PDF 从摄入到检索

以 `process_document_complete`（`processor.py:1985`）为主线：

1. **解析**：`parse_document` 分发。MinerU 调 `mineru -p ... -o ...` CLI 产 `*_content_list_v2.json`，`mineru_content.py` 把按页结构**拍平**为扁平内容块（精确 stem > 作用域 legacy > 共享 v2 优先级矩阵）。Office 先经 LibreOffice 转 PDF（`parser.py:19`：MinerU 2.0 起不内置）；文本/Markdown 直解析、**禁止 PDF 往返**。
2. **缓存判定**：以内容 SHA-256 指纹+配置键为身份（`processor.py:73,116`），**内容指纹优先于 mtime**。
3. **内容分离**：`separate_content_with_page_map`（`utils.py:237`）拆文本流与多模态条目并建页面区间表。
4. **文本入库**：文本交 LightRAG `ainsert`；管线忙时只入队不处理，`_wait_for_text_processing`（`processor.py:193`）轮询等待——历史回归点（曾提前写 HANDLING 致 PENDING 文档被踢出队列、文本永不分块）。
5. **页码回填**：`replay_chunk_spans`（`utils.py:459`）按 LightRAG 同款 chunk 几何参数**回放**分块位置映射回源页——几何推导而非文本搜索。
6. **多模态处理**：type-aware 批处理分发六处理器；图表公式带周边文本上下文（ContextExtractor）交 VLM 描述，稳健 JSON 解析+正则兜底抽实体，chunk 与实体落 LightRAG。
7. **状态簿记**：doc_status 全程更新；音视频路由为单条 media 条目（字节变化改 doc_id）。

8. **检索**：`aquery` 委托 LightRAG（local/global/mix）；`aquery_with_multimodal` 先 LLM 分析相关模态描述化增强，再对图像路径正则捕获（`query.py:689`）→ 白名单校验（须在 working_dir/parser_output_dir 下，`query.py:729-742`）→ base64 → VLM 消息。缓存键以文件 sha256 指纹区分同名文件（`query.py:41,103`）。

## 4. 关键子系统深读

**parser.py（3726 行）**：`Parser` 基类（`parser.py:359`）→ `MineruParser`(:1395)/`DoclingParser`(:2454)/`PaddleOCRParser`(:3108)。MinerU 版本门控是重头戏：`_MINERU_REQUIREMENT = "mineru[core]>=3.4.1,<4"`（`parser.py:77`）、`_MINERU_FIRST_UNSUPPORTED_MAJOR = 4`（:79）、`_MINERU_LAST_SUPPORTED_PYTHON = (3, 13)`（:83）——MinerU 4.0 改子命令式 CLI 且只产 Markdown，诊断链由 43 用例 `test_mineru_version_support.py` 钉死。中文 PDF 用 STSong-Light CID 字体（`parser.py:817`）。自定义解析器可进程内注册（重名拒绝/名称归一化）。

**modalprocessors 六继承**：`BaseModalProcessor`（`modalprocessors.py:383`）派生 Image(:923)/Table(:1161)/Equation(:1360)/Generic(:1550) + `AudioModalProcessor`（`modalprocessors_audio.py:47`，faster-whisper 转写+token 分窗）+ `VideoModalProcessor`（`modalprocessors_video.py:74`，双通道：SceneDetect 关键帧交 VLM+音轨 whisper）。失败 fallback 须保持三元组返回契约（历史 bug：返二元组致 ValueError 掩盖失败）。

**主类三 Mixin**：Query（查询+缓存）/Processor（解析+入库+状态）/Batch（批量）组合进 dataclass；惰性初始化以 `asyncio.Lock` 串行化（`raganything.py:121-122`）。

**resilience 熔断**：动机 issue #172（网络瞬时故障卡死 process_document_complete，`resilience.py:7`）。`CircuitBreaker`（:229）用 **generation 代数检查**（:271,323）丢弃迟到旧恢复周期结果，配套测试以冻结时间+Event 编排交错时序。

## 5. 设计决策与取舍

- **依赖极简+锁定**：核心依赖仅 4 项（pyproject.toml:25-32）——`lightrag-hku<1.5`（新版 role_llm_funcs 不兼容）、`mineru[core]>=3.4.1,<4`（带 py3.14 marker）、huggingface_hub、tqdm；七组可选依赖按需装。
- **特性门控 barrel**：可选能力全走 ImportError 门控，装得少不炸包。
- **contextvars 并发隔离**：`document_context.py` 为共享 processor 提供操作级隔离，并发摄取多文档时上下文不互相污染。
- **配置实例化时读环境**：default_factory 使每个 config 实例独立捕获构造时刻的环境（`test_config_environment.py` 守护）。
- **共享白名单防口径漂移**：`parse_options.py` 的 `PARSER_CACHE_KWARGS`（:12）被 processor 缓存与 batch_parser 增量 manifest 共用，`test_parse_options.py:8` 以 `is` 断言同一对象。
- **半桩半真测试范式**：大量测试以 `spec_from_file_location` 单独加载真模块绕开重依赖，甚至 ast 提取单方法体 exec（`test_multimodal_concurrency.py`）——重依赖仓的标志性手法。
- **函数体延迟 import**：测试体在 lightrag 可用时才执行；`prompts_zh` 惰性导入。
- **三层并发模型**（docs/batch_processing.md:276-314）：解析 worker × `max_parallel_insert` × `llm_model_max_async` 独立且**相乘**，视频场景达 `max_parallel_insert²`（:314）——调参须三层一起看。

## 6. 已知问题与坑

- **omml_extractor 零生产消费者**：573 行单测全绿的 OMML→LaTeX 转换器，包内仅 docstring 自引用，无生产调用（grep 实证）。
- **issue 模板 LightRAG 残留**：`bug_report.yml:36-38,52` 仍用「LightRAG Config Used / LightRAG Version」字段，系姊妹仓移植后未改名。
- **公网 URL 仅 MinerU 路径**：`attach_public_media_urls` 全仓唯一调用点在 `parser.py:2060`（MineruParser 类内），Docling/PaddleOCR 条目不享受映射。
- **README 中文版缺节**：缺英文版「Troubleshooting」「Public media URLs」两个 H3 与「PaddleOCR Parser」H4 小节（H2-H4 计 42 vs 39），中文用户排障需回看英文版。
- **排队语义曾破坏文本索引**：旧版提前写状态把文档踢出队列（test_queued_text_insert 钉死）；重跑已处理文档曾卡 HANDLING（test_rerun_completed_status）。
- **离线陷阱**：tiktoken 首次联网下载令离线初始化失败，须先跑 `scripts/create_tiktoken_cache.py` 且 `.env` 在 **import lightrag 之前**加载（docs/offline_setup.md）。

## 7. 新人上手路径（对应 tour 前 6 步）

1. **读 README**：五阶段算法+8 示例建全局图景；中文读者补看英文版缺的三节。

2. **主类**：从 `raganything.py:63` 三 Mixin 切入，跑 `examples/raganything_example.py`（注入→处理→查询全链）。
3. **Processor**：吃透 `processor.py` 的缓存指纹、doc_status 生命周期、排队语义——理解全仓状态机的关键。
4. **解析器**：三实现+版本门控；换 Docling 只需 `RAGAnythingConfig(parser="docling")`；HTML 仅 Docling 支持。
5. **多模态处理器**：四处理器+ContextExtractor；`examples/modalprocessors_example.py` 演示绕过解析直用。
6. **工具族**：`utils.py` 分离与页码回放、`image_signature.py` 魔数安全、`enhanced_markdown.py` 沙箱（v1.4.0 起摄入**不再** MD→PDF，只产排版成品）。

之后按需深入批处理/韧性/prompt 双语/测试（Step 7-12）。

## 8. 与 LightRAG 的分工关系

两仓同出 HKUDS，工程基建互为移植源（issue 模板即证据）。分工：**LightRAG 是检索与图谱引擎**——文本插入、实体/关系抽取、分块、local/global/mix 查询、存储后端抽象；**RAG-Anything 是多模态摄入层**——解析、模态识别、VLM 描述、内容组织，最终写进 LightRAG 实例（可自带已初始化实例，见示例 6）。依赖严格单向：RAG-Anything → lightrag-hku，锁定 `<1.5`。查询侧 `aquery` 直接委托，仅多模态增强是自有增量。可理解为「LightRAG 的多模态前置放大器」：图谱与检索全复用，只补文档理解这一段。

---

*基于代码图谱（751 节点/1332 边/14 层/14 步导览）撰写；行号锚 29 处全部源码核实（commit 2cd2b332）。*
