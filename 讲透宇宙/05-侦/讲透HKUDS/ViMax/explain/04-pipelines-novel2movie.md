# 04 · pipelines/novel2movie_pipeline.py — Novel2Movie 两阶段管线

> 源文件：`pipelines/novel2movie_pipeline.py`（**实测 1010 行**，任务书说 950——以源码为准）。行号锚均从源码核实（commit fd4b72e7）。

## 1. 角色定位

novel2movie_pipeline.py 承载三条管线中最难的一条：**长篇小说 → 分场景视频**。难点在"长"——几十万字的小说无法塞进任何上下文窗口，且角色在不同事件/场景里有不同名字与状态。本文件的解法是把任务拆成**两阶段**（对应 agent 的两个工具调用）：`plan_text_artifacts`（:73-309）做纯文本规划——压缩小说、抽取事件、对每个事件用 FAISS+reranker 检索原文相关片段、写剧本化场景、三层合并角色（场景级→事件级→小说级）；`render_video_artifacts`（:312-477）做纯渲染——基于已有规划产物生成角色立绘并逐场景委托 Script2VideoPipeline 出片。两阶段各自可断点续跑、中间产物全落盘，agent 可以在两阶段之间停下来让用户审阅。

文件第 1 行是一句刺眼的 `# TODO: NOT IMPLEMENTED YET`（:1）——它标记的是**文件尾部那套遗留单体 `__call__`**（:479-996，Step 1-7 的 emoji 打印版一体化实现），而非两阶段方法本身。生产路径只用 plan/render 两个方法（vimax_adapters.py:304,386 分别调用）；`__call__` 是被两阶段重构取代的前身，读架构时跳过即可。

## 2. 内部结构

**`__init__`（:47-70）——十个注入依赖，零内部构造**：novel_compressor / event_extractor / embeddings / rerank_model / scene_extractor / global_information_planner（五个 LLM/生成 agent）、image_generator、rewriter（提示词改写器）、script2video_pipeline（渲染委托对象）、working_dir。全靠 vimax_adapters 的两个工厂组装（:626-644 计划态、:647-665 渲染态）——本文件自身不 import 任何 agent 类，是纯粹的编排层。注意**计划态**注入的是 dummy：`image_generator=dummy`、`script2video_pipeline=dummy`（vimax_adapters.py:640,642，_UnavailableGenerator，:37-42 调即抛错），保证规划阶段绝不可能偷偷触发渲染。

**`plan_text_artifacts`（:73-309）——六步规划，每步带断点续跑与进度事件**：

1. **存原文并分块**（:89-99）：novel.txt 落盘，`novel_compressor.split()` 切块，每块存 `novel_chunk_N.txt`。
2. **压缩**（:101-128）：逐块检查 `novel_chunk_N_compressed.txt` 是否已存在（:106-107），已压缩的跳过——断点续跑第一例；未完成的用 `Semaphore(5)` 并发压缩（:111-115）；最后 `aggregate` 合并成 novel_compressed.txt（:126，同样先查缓存）。
3. **事件抽取**（:130-151）：`while` 循环让 event_extractor 产出"下一个事件"（:144-147），直到 LLM 打出 `is_last` 标记（interfaces/event.py:11）。每个事件立即落盘 event_N.json（:148-150），崩了重启从盘上 JSON 续抽（:134-141 预载）。循环顶部有**防呆帽** `_ensure_extraction_cap`（:143）：模型永不打 is_last 时最多抽 50 个事件（:1001）。
4. **RAG 检索原文片段**（:153-204）：知识库不是压缩文而是**原文**——`CacheBackedEmbeddings`（本地文件缓存 embedding，sha256 键，:158-163）包住远程 embeddings，`RecursiveCharacterTextSplitter(512/128)` 切块（:164），FAISS 建库（:166）。对每个事件的每个 process_chain 描述：FAISS 召回 top-10（:173）→ reranker 精排（:177）→ 分数 ≥0.7 累加计分（:179-180）。结果以 `chunk_N-score_X.XX.txt` 落盘（:201-203）——**分数编码在文件名里**，续跑直接解析文件名还原（:188-194），零索引文件。并发 `Semaphore(10)`（:184）。
5. **场景抽取**（:206-249）：scene_extractor 结合 relevant_chunks 逐场景生成剧本化 Scene（:225-240），is_last 终止 + 每事件 30 场封顶（:230,:1002）。已有场景预载（:213-221），未完成事件并发 8（:243）。
6. **角色三层合并**（:251-301）：场景级先在事件内合并成 `CharacterInEvent`（:257-267，并发 8），再**串行**折叠进小说级 `CharacterInNovel`（:293-298）——串行是必然：每步依赖上一步的全量角色表。novel_level 续跑从 `novel_characters_after_event_N.json` 的最大 N 续起（:284-292）。

返回压缩小说/事件/场景/小说级角色四件套（:304-309）。

**`render_video_artifacts`（:312-477）——三步渲染**：

1. **前置校验**（:334-339）：events/scenes/characters 三类目录缺一即 RuntimeError"run vimax_novel_planning first"——**依赖声明靠目录存在性**，与 vimax_adapters 的 checklist 判定（vimax_adapters.py:825-830）双保险。随后从盘上重载全部规划产物（:341-384）——本方法不信任内存状态，永远从持久化产物出发。
2. **角色立绘两代**（:386-440）：先按小说级角色的 static_features 生成"基础立绘"（512x512 白底全身正面像，:396-400，并发 5）；再沿 `CharacterInNovel.active_events → CharacterInEvent.active_scenes → Scene.characters` 三层索引（:429-437）遍历每个角色在每个场景的出场，用基础立绘作参考图 + dynamic_features 改写生成"场景立绘"（:417-423，并发 3）；角色不可见或无动态特征时直接**拷贝**基础立绘（:414-416）。prompt 经 `self.rewriter`（:421）——agent 路径下是 _IdentityRewriter 直通（vimax_adapters.py:602-604），留作换提示词方言的扩展点。
3. **逐场景出片**（:442-469）：双重 for 循环**串行**调用 `self.script2video_pipeline(...)`（:459-467）——注意 :449 直接改写共享实例的 `working_dir`（`self.script2video_pipeline.working_dir = scene_video_dir`），串行循环里安全，但这个副作用意味着该实例不能并发复用。

**遗留单体 `__call__`（:479-996）**：Step 1-7 全内联 + emoji 打印（:484 起），与两阶段方法功能重叠但有代差——:976 硬编码 `style = "realistic movie style"` 无视入参、:979-989 的 character_registry 是裸列表结构（新版是 `{"portrait": {...}}` 字典，:450-457）、Step 4 复用 Step 3 的 tasks 列表未清空（:738-742，潜在双重 await 隐患）。无人调用的遗留代码，别把它当真相。

**模块尾部（:999-1010）**：两个全局帽 `MAX_EXTRACTED_EVENTS=50`、`MAX_SCENES_PER_EVENT=30`（:1001-1002）与 `_ensure_extraction_cap`（:1005-1010），注释（:999-1000）写得明白：is_last 只由 LLM 断言，永不打的模型不能无限烧 token。

## 3. 外部连接

**依赖上游**：interfaces 的五个 Pydantic 模型——Event（interfaces/event.py:6，process_chain :22/is_last :11）、Scene（interfaces/scene.py:7，is_last :12）、CharacterInScene/InEvent/InNovel（interfaces/character.py:8/50/77，三层各带 identifier_in_* 与 active_scenes/active_events 索引字段 :59/:86）；langchain 检索栈（CacheBackedEmbeddings/LocalFileStore :10-11、RecursiveCharacterTextSplitter :12、FAISS :13）；utils/text.safe_path_component（:25，角色名转安全文件名）；shutil（:4，拷贝立绘）。死 import 四件：yaml（:5）、importlib（:7）、PIL.Image（:14）、tenacity.retry（:23）——全文件零调用，历史残留。

**被依赖下游**：
- vimax_adapters.py:21 import；`_build_novel_pipeline`（:626-644）为 `vimax_novel_planning` 工具造计划态实例（:304 消费）；`_build_novel_render_pipeline`（:647-665）为 `vimax_render_video` 的 novel 分支造渲染态实例（:384 消费，注入真 Script2VideoPipeline）。
- 测试：tests/test_novel2video_adapter.py:17,144 用假组件构造管线、:157-158 直接 patch 本模块命名空间里的 `CacheBackedEmbeddings.from_bytes_store` 与 `FAISS.from_texts`（FAISS 是重依赖，测试必须挡掉）；tests/test_hang_guards.py:18 直测 `_ensure_extraction_cap`。

## 4. 数据流：一次 agent 发起的小说改编全路径

用户在 TUI 粘贴一章小说：

1. 模型调 `vimax_novel_planning` 工具 → vimax_adapters.py:304 `_build_novel_pipeline(novel_dir)` 组计划态管线 → :305-317 `plan_text_artifacts(novel_text, progress=...)`，每步经 `_pipeline_progress` 转成 tool_progress 事件穿透到前端。
2. 压缩：若上次会话崩在第 7 块，:106-107 的存在性检查让 0-6 块秒过，只压缩剩余块（Semaphore 5 并发）——**这是"断点续跑"的实现本质：每步先读盘、后干活**。
3. 事件抽取逐个落盘；RAG 检索给每个事件找回原文血肉（压缩文定骨架、原文供细节，这是"先压后检"的信息保真设计）。
4. 角色三层合并完成，模型拿到 `{"missing": [], "ready_for_scene_render": false}` 的 ToolResult（vimax_adapters.py:330-338）——规划态明确不渲染。
5. 用户说"开始出片"→ 模型调 `vimax_render_video` → adapters :382-402 判定 novel_mode_ready → `_build_novel_render_pipeline` 造渲染态 → `render_video_artifacts(style, progress)`：校验目录 → 基础/场景立绘（image_generator 此时是真的）→ 逐场景把 scene.script + 立绘 registry 交给 Script2VideoPipeline（分镜→关键帧→镜头视频→拼接，见 04 姊妹篇）。
6. 返回 `scene_videos_dir`（:472-477），vimax_adapters.py:387-402 把它写进 ToolResult 与 render_status.json——novel 模式**没有整片拼接**，产物是每个场景一个视频目录（final_video_path 为 None，vimax_adapters.py:395）。

## 5. 设计决策

- **两阶段拆分是 agent 交互的产物**：单体 `__call__` 一口气跑完几十分钟，agent 无法在中途检查/改稿；拆开后 `vimax_novel_planning` 与 `vimax_render_video` 之间天然形成一个"人类审阅点"，且 render 阶段崩了不必重做规划（LLM token 大头在规划）。
- **断点续跑用"文件存在即跳过"而非状态数据库**：每个中间产物自带语义化文件名（chunk_N_compressed / event_N / chunk_i-score_X），恢复=重扫目录。分数编码进文件名（:191,:202）是朴素但零索引文件的妙招；代价是文件名解析成了隐性协议，改名即破坏兼容。
- **防呆帽（:999-1010）承认 LLM 不可靠**：is_last 是模型承诺，50/30 的硬帽是工程兜底——"trust but cap"。
- **知识库用原文而非压缩文**（:165 vs :95）：压缩是为了塞进抽取 prompt，检索是为了保真细节——两种上下文策略各司其职，这是本管线对"长文本信息损失"的核心应对。
- **角色三层模型（scene/event/novel）+ active_events/active_scenes 映射**：让"同一角色在 30 个场景有 30 张立绘"变成可索引的遍历（:429-437）而非全量搜索。遗留代码里作者自己都吐槽过遍历查找（:943,946 的 TODO 注释），新版用映射+下标索引修复了大半。
- **novel 模式不出整片**：每场景独立视频目录，拼接留给用户/后续工具——多场景长片的整体节奏控制本就是开放问题，不硬做。
- **并发度分级**：压缩 5、检索 10、场景抽取 8、基础立绘 5、场景立绘 3、出片 1（串行）——大致按"调用成本与供应商限流压力"递减，与 tools/render_backend.py 的 RPM 限流互为表里。

## 6. 新人提示

- **别动遗留 `__call__`**（:479-996）：它是带 TODO 的死代码，且内部有 tasks 复用（:738-742）与硬编码 style（:976）等已知问题；需要改行为时改两阶段方法。同理，:1 的 TODO 指的是它，不是整个文件"没实现"。
- 四个死 import（yaml/importlib/Image/retry，:5,:7,:14,:23）别顺手"清理"出 PR——留着无害，删了要过全部测试；但新增代码也别学它（本文件 import 卫生差是历史包袱）。
- `render_video_artifacts` 会**改写**共享 script2video_pipeline 实例的 working_dir（:449）——若你想并行化 :445 的双重循环，必须先给每个 scene 克隆一个 pipeline 实例，否则目录互相踩踏。
- 文件名协议（`-score_`、`event_N.json`、`novel_characters_after_event_N.json`）被三处消费：本文件续跑、vimax_adapters 的 `artifact_checklist`、web 前端产物树。改名=三处连锁改，先 grep。
- 检索阈值 0.7 与 top-10 都是经验值（:173,:179）：调低阈值召回更多原文但噪声变多，会直接改变场景剧本的"细节密度"。
- 测试本管线必须 patch `CacheBackedEmbeddings.from_bytes_store` 与 `FAISS.from_texts`（test_novel2video_adapter.py:157-158 的现成写法）——否则单测会真调 embedding API 或因缺 faiss-cpu 失败。
- `_ensure_extraction_cap` 的错误信息会原样冒泡给模型（经 adapters 的异常包装）——模型看到"cap: 50"后通常会收敛并补 is_last，这是个有用的自然语言反馈回路，改文案时保住这个语义。
