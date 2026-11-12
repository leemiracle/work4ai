# 04 · modalprocessors.py —— 模态处理器六继承家族与 ContextVar 并发隔离

> 源码：`raganything/modalprocessors.py`（1710 行，commit 2cd2b332）+ 姊妹文件 `modalprocessors_audio.py`/`modalprocessors_video.py` + 并发隔离底座 `document_context.py`（39 行）。

## 1. 角色定位

多模态内容块的「翻译官」：接收解析器产出的 image/table/equation 条目，调 VLM/LLM 生成带上下文的描述，把描述+实体写进 LightRAG 图谱与向量存储。家族是**一个基类六个子类**：`BaseModalProcessor`（`modalprocessors.py:383`）在本文件派生 Image（:923）/Table（:1161）/Equation（:1360）/Generic（:1550）；`AudioModalProcessor`（`modalprocessors_audio.py:47`）与 `VideoModalProcessor`（`modalprocessors_video.py:74`）因重依赖独立成文件、惰性加载。文件前 382 行还有 `ContextConfig`（:55）与 `ContextExtractor`（:70）两个公共件，为每个条目捞周边文本上下文。**ONBOARDING「六继承家族」口径**：非六类都定义在本文件，而是 4+2 分布三文件、同宗 `BaseModalProcessor`。

## 2. 内部结构

**（a）ContextExtractor（前 382 行）**。`extract_context`（:83）按格式分派：MinerU 内容列表（:135，再分页级 :154/块级 :194）、dict 源（:261）、纯文本（:288）、text_chunks（:302），末统一 `_truncate_context`（:331）按 token 预算裁剪。它决定图表描述的「视野」——窗口/标题题注/过滤类型全由 `ContextConfig` 控制。

**（b）BaseModalProcessor（:383-922）**。构造器（:386-431）做「LightRAG 内脏移植」：直接拿走 `text_chunks`（:403）、三个向量库（:404-406）、`knowledge_graph_inst`（:407）、embedding/llm 函数（:410-411）、`llm_response_cache`（:417）、`tokenizer`（:418），并用 `_build_global_config()` 快照全局配置（:412-416）——处理器写图谱与 LightRAG 本体同一套参数。两个核心抽象：`generate_description_only`（:477，批处理阶段 1：只产描述+实体）与 `generate_chunk_sections`（:500，**1→N 泛化**：默认单 section :524-533，长音频/视频分窗时覆写——audio 覆写于 `modalprocessors_audio.py:298`）。统一入库出口 `_create_entity_and_chunk`（:557）返回**三元组**——fallback 曾返二元组、解包 ValueError 反过来掩盖真实失败，故所有 except 分支必须维持三元组（Image 的 fallback 见 :1109-1119）。

**（c）稳健 JSON 解析链（:640-820）**。VLM 输出不保证合法 JSON，五级防线：剥思考标签（:640）→ `_robust_json_parse`（:663）→ 抽候选（:689）→ 修引号（:745,:759）→ `_extract_fields_with_regex` 正则兜底（:774）。这 180 行是「LLM 输出工程」教科书。

**（d）四个子类**同构：`generate_description_only`（组 prompt 调 `modal_caption_func`+`_parse_response`）→ `process_multimodal_content`（描述+chunk 模板组装→`_create_entity_and_chunk`）→ 各自 `_parse_*_response`。差异在输入：Image 有 base64 编码（:941）走真视觉模型、chunk 模板带 captions/footnotes/section_path/neighbor_text（:1081-1097）；Table 吃 HTML 表格体；Equation 走 LaTeX（文件头 `_restore_latex_escapes` :41 防转义破坏）；Generic 兜底任何未知模态。`_parse_response` 给实体名拼类型后缀 `name (type)`（:1139-1141），同名不同类不冲突。

**（e）音视频姊妹文件**。Audio（`modalprocessors_audio.py:47`）：whisper **属性级惰性加载**（:111-129），模型/设备/精度可配（:77-93），依赖探测只用 `find_spec`（:42-44）；`generate_chunk_sections` 覆写为按 token 预算分窗（:298，window_meta 带 start/end/part/total）。Video（:74）：双通道=视觉（`_detect_scenes` :180+关键帧交 VLM，注意 `CAP_PROP_POS_FRAMES` 定位吸附最近关键帧 :231）+音轨复用 Audio；`audio_processor` 是**共享注入参数**（:116，docstring :134，惰性兜底自建 :151-166）——主类注册时传同一实例（`raganything.py:291`），全进程一份 whisper。

## 3. 外部连接（对齐图谱边）

- → `lightrag` 最强边：五类存储+两函数+tokenizer+global_config 全取自 LightRAG（:403-418）；写图谱经 processor.py 的 type-aware 工具族。
- → `document_context.py`：`set_content_source`（:433-446）与 `_get_context_for_item`（:448-460）经 `set/get_document_source` 接 ContextVar 层。
- → `prompt.py`：`PROMPTS["image_chunk"]` 等 chunk 模板（:1091）。
- ← `raganything.py`：`_initialize_processors` 注册六类+共享 ContextExtractor（`raganything.py:222-303`）；← `processor.py` 批/逐条两路分发。
- → 重依赖（惰性）：PIL、faster-whisper（audio）、scenedetect+moviepy+opencv（video）。

## 4. 数据流

单个图表条目的旅程：processor 分发 → `_get_context_for_item`（:448）先查 ContextVar 覆盖、无则用实例默认源，ContextExtractor 按页/块坐标捞周边文本 → `generate_description_only` 组 prompt 交 `modal_caption_func` → 五级 JSON 防线解析出 description+entity_info → `process_multimodal_content` 用 chunk 模板拼最终文本 → `_create_entity_and_chunk`（:557）算 `chunk-` 前缀哈希 id（:565）、按 `batch_mode`（:1061）决定是否立即抽关系 → 返回三元组。批处理两阶段：先全量 `generate_description_only`，后统一实体抽取入库。

**并发隔离**（`document_context.py`）：`_sources` 是 ContextVar（:8），`@document_context` 装饰摄入入口（processor.py:2179）设空 dict、退出 reset（:13-24）；`set_document_source` 写入时**复制快照而非原地改**（:32-33 注释：子任务继承的是快照，绝不变异继承来的映射）。效果：同一 processor 实例并发处理 A/B 两文档，各自任务树看到各自 content_source；直用 processor（examples 路线）时 ContextVar 为空、优雅回落实例属性（:443-445）。

## 5. 设计决策

- **处理器不 own 存储只租用**：直接引用 LightRAG 内脏而非另建连接，多模态实体与文本实体同图谱同命名空间——「模态感知检索」成立的前提。
- **ContextVar 而非实例状态**：六实例服务全仓，实例级 content_source 并发下互相污染；ContextVar 以任务树为界隔离，直用场景零成本回落。
- **1→N 的 generate_chunk_sections 泛化**：长转写/多场景需求倒逼出的抽象——默认 1 段保四老子类不变，新子类只覆写一处（:507-513 docstring 自述动机）。
- **五级 JSON 防线宁可慢不可断**：fence/思考前缀/单引号/截断各有专门修复，正则兜底保证总能提出实体三字段。
- **fallback 保三元组契约**：失败路径产降级实体（类型+内容前 100 字摘要，:1112-1118）而非抛异常——单条失败不阻塞整文档。
- **音视频拆文件+属性级惰性**：import 期零重依赖，探测与首次加载分离。

## 6. 新人提示

1. 写新处理器：继承 `BaseModalProcessor`，实现 `generate_description_only`（必选）与 `_parse_*_response`，多段输出再覆写 `generate_chunk_sections`；**任何 except 分支返回值必须维持三元组**。
2. 排查「图表描述没有上下文」：确认摄入走了 `process_document_complete`（会 `set_content_source`）；直用 processor 要手动喂 content_source 或接受空上下文。
3. `modal_caption_func` 分配规则在主类：image/video 优先视觉模型，table/equation/generic 用文本 LLM（`raganything.py:238,282`）——表格走视觉模型需自己改注册逻辑。
4. 长音频拆窗后实体名带 Part 编号，检索命中多段时按 start/end 时间戳重组。
5. 视频 seek 精度受关键帧吸附影响（`modalprocessors_video.py:231`），帧级对齐别指望 OpenCV 帧号连续。
