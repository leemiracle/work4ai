> 标题：LongMemEval 桥接离线集成测试——哨兵防泄漏与 monkeypatch 工艺 · 源文件：tests/test_longmemeval_jev.py（139 行）· 图谱标签：test / integration / offline / longmemeval / caching（图谱度数 in=7 / out=25）

## 角色定位

第 30 篇适配器 `memory/longmemeval_jev.py` 的专属验收套件。文件头一句话规格（tests/test_longmemeval_jev.py:1）："Offline LongMemEval integration checks; no providers or model downloads"——不用 OPENAI_API_KEY、不下载 embedding 模型、不发任何网络请求，在 CI 的 ubuntu 与 macos 双腿（.github/workflows/ci.yml:15、29）上验证 Jev 分支的核心承诺：金标隔离、缓存内容身份、日期诚实、与巨型 harness 的委托关系。

它的方法论招牌是**哨兵防泄漏**：fixture 把金标答案与金标会话 ID 故意填成 `GOLD_ONLY_SENTINEL` / `GOLD_SESSION_SENTINEL`（tests/test_longmemeval_jev.py:27），然后在答题路径上断言这些哨兵串绝不出现在发给 LLM 的 prompt 里（tests/test_longmemeval_jev.py:101）。适配器 docstring 声称 "gold answers never enter construction or retrieval"（memory/longmemeval_jev.py:35），本套件把这句口号变成可执行断言。

## 内部结构

两个 fixture 加七个测试，按被测面分组：

- **fixture `question`（tests/test_longmemeval_jev.py:19-28）**：两段会话故意乱序——日期晚的 "later"（05-30）排在 "earlier"（05-20）前面（tests/test_longmemeval_jev.py:21-25），专门考验 build 的会话排序；消息里埋相对时间词 "yesterday"；question_type 给 temporal-reasoning。`LongMemQuestion` 九字段构造顺序与 jev_mem/datasets/longmemeval.py:32-40 的 dataclass 一致，haystack_sessions 收尾。
- **fixture `memory`（tests/test_longmemeval_jev.py:31-42）**：离线化的核心。`offline_builder`（tests/test_longmemeval_jev.py:33-37）用 MockEncoder（128 维确定性词哈希嵌入，memory/mock_encoder.py:7-8）+ NumpyVectorDB + `llm_backend=None` 的 TRG 组装 MemoryBuilder 且 `llm_enabled=False`；`monkeypatch.setattr(adapter, "MemoryBuilder", offline_builder)`（tests/test_longmemeval_jev.py:38）打在**适配器模块的全局名**上——适配器 build 里正是引用这个名字（memory/longmemeval_jev.py:68），签名用 `**kwargs` 吞掉 llm_model/embedding_model 两个真参数。config 开 `jev_mock=True`（tests/test_longmemeval_jev.py:39）让决策层走 JevClient mock。yield 后 close（tests/test_longmemeval_jev.py:42）。
- **写路径保真（tests/test_longmemeval_jev.py:45-54）**：build 后三节点、图/向量库计数一致（tests/test_longmemeval_jev.py:48）；节点顺序 `["earlier","later","later"]` 证明乱序会话被日期重排（tests/test_longmemeval_jev.py:49）；later 两消息共享会话时间戳、speaker 角色保留（tests/test_longmemeval_jev.py:50-51）；"yesterday" 被解析成 normalized "29 May 2023"——锚定**消息所属会话**的 05-30 而非今天（tests/test_longmemeval_jev.py:52）；timing 字段落地（tests/test_longmemeval_jev.py:53-54）。
- **缓存身份三连（tests/test_longmemeval_jev.py:57-87）**：改金标答案/金标会话/问题文本 → 仍缓存命中（tests/test_longmemeval_jev.py:61-63）——金标不进 manifest 的**正向证明**；`rebuild=True` 重建后节点 ID 全新且与旧集不相交（tests/test_longmemeval_jev.py:66-69）；改 haystack 一个字 → 缓存目录换新（tests/test_longmemeval_jev.py:70-74）。失效维度参数化打点：会话日期、session_id、消息 role、config 的 relation_threshold 任何一个变动都换 manifest（tests/test_longmemeval_jev.py:77-87）。
- **答题隔离（tests/test_longmemeval_jev.py:90-105）**：monkeypatch `engine.query` 只回单个指定节点（tests/test_longmemeval_jev.py:92-94）；completion 函数做 prompt 间谍（tests/test_longmemeval_jev.py:95-98）；断言两个金标哨兵不在 prompt、未被检索的 "earlier" 会话原文不在 prompt、被检索的证据文本与 question_date 在 prompt（tests/test_longmemeval_jev.py:101-103）；retrieved_session_ids 只含命中会话（tests/test_longmemeval_jev.py:104）；计时不变式 query_seconds ≥ retrieval_seconds ≥ 0（tests/test_longmemeval_jev.py:105）。
- **真检索引擎离线冒烟（tests/test_longmemeval_jev.py:108-113）**：不 mock query，真跑 engine.query——anchor_nodes 非空、metadata 里 controller 为 "jev-mem"、jev_calls 不超 maximum_jev_calls 预算（tests/test_longmemeval_jev.py:110-113）。MockEncoder 的词哈希嵌入足以让关键词路线命中，证明共享检索栈在零 provider 下可组装可运行。
- **日期解析（tests/test_longmemeval_jev.py:116-120）**：空串得 None、ISO 带 Z 解析为 naive `datetime(2023,5,30,12)`、垃圾串抛 "Unsupported LongMemEval date"——钉死 parse_date 不发明"今天"。
- **harness 委托（tests/test_longmemeval_jev.py:123-139）**：`ChunkedLongMemEvalTester.__new__` 跳过 `__init__`（tests/test_longmemeval_jev.py:126）——绕开构造器里 OPENAI_API_KEY 硬检查（jev_mem/benchmarks/longmemeval.py:64-66）与惰性 import 副作用；手工填五个属性、把 baseline 两方法换成探针 stub（tests/test_longmemeval_jev.py:127-133）；跑 `test_questions` 后断言：结果 correct、memory_timing 在场当且仅当走 Jev 分支、baseline 构建只在无 jev 时被调（tests/test_longmemeval_jev.py:134-137）、且 harness 用完把 builder 关干净（tests/test_longmemeval_jev.py:138-139）。

## 外部连接

import（tests/test_longmemeval_jev.py:10-16）：load_longmemeval 三数据类（根垫片 sys.modules 转发到 jev_mem/datasets/longmemeval，load_longmemeval.py:1-3）；adapter 整模块；JevMemConfig；MemoryBuilder/MockEncoder/QueryContext/TemporalResonanceGraphMemory/NumpyVectorDB——离线件全家桶。延迟 import（tests/test_longmemeval_jev.py:125）：test_longmemeval_chunked 垫片→jev_mem/benchmarks/longmemeval 的 ChunkedLongMemEvalTester。monkeypatch 三锚点：adapter.MemoryBuilder（38）、memory.engine.query（94）、tester 实例方法（132-133）。对位关系：本套件的每条断言都能映射回 memory/longmemeval_jev.py 的具体行为段（第 30 篇），并与 harness jev 分支 jev_mem/benchmarks/longmemeval.py:2052-2054 形成三方闭环。图谱报 in=7/out=25，fan-in 主要来自共享测试基建与图谱对 fixture 复用的统计口径，以 grep 实测为准。

## 数据流

fixture 装配流：JevMemConfig(jev_mock=True) → adapter.LongMemEvalJevMemory →（build 触发）被替换的 offline_builder → MockEncoder TRG + llm_enabled=False 的 MemoryBuilder → 真 QueryEngine 挂 mock JevClient。测试数据流两路：写路径一路断言图结构（节点数/顺序/属性/时间戳）；答题路径一路拦截 prompt 文本做内容审计。harness 测试里数据从 question 流经被 stub 的 evaluate_lenient 直接给满分，验证的是**分派与收尾**而非评分。缓存测试通过 deepcopy 改字段→重算 manifest→比对缓存目录，全程不触碰网络与真实嵌入。

## 设计决策

**哨兵法是防泄漏测试的最小工艺**。不需要理解 prompt 模板内部结构，只要金标值是全局唯一字符串，"不出现在 prompt"就是一条完备的端到端断言；同一手法顺带证明未检索会话的原文也不泄漏（tests/test_longmemeval_jev.py:102）——比"检查检索函数输入"更接近威胁模型。

**两层 mock 策略显式分层**：MemoryBuilder 整个换掉（重基建，离线化），engine.query 按需换掉（轻行为，隔离变量）——答题隔离测试若用真检索，"哪些证据进了 prompt"就依赖检索质量而非隔离性质。真引擎冒烟测试（108-113）补上第三层：确认 mock 基建下真栈仍可跑，三层合起来既隔离又防 mock 失真。

**`__new__` 直造实例是绕重型构造器的标准姿势**：harness 构造器要 API key、要惰性 import、要装 LLMController（jev_mem/benchmarks/longmemeval.py:58-70），测试只关心 test_questions 的三分派逻辑，就只填它真正读的五个属性（tests/test_longmemeval_jev.py:127-129）。代价是**属性契约隐式化**——harness 未来新增被 test_questions 读取的属性，本测试不会红，属于用窄接口换零依赖的既定取舍。

**缝隙两条**：其一，缓存测试证明"金标不影响缓存身份"，但金标在**构建产物**层面的零痕迹（例如 audit 日志不含金标）未覆盖；其二，MockEncoder 的哈希嵌入让向量检索路线退化为词面命中，temporal_references 断言（tests/test_longmemeval_jev.py:52）依赖 TemporalParser 的确定性而非嵌入质量——嵌入相关行为（如向量维度不匹配的防御）不在本套件射程内。

## 新人提示

先读两个 fixture（tests/test_longmemeval_jev.py:19-42）看懂离线化手术怎么做，再按 45→57→90 的顺序读三组核心测试，最后读 123-139 的 harness 委托。跑法：`python -m pytest tests/test_longmemeval_jev.py -q`，纯离线，秒级完成。

四个坑：一，改适配器 build 的 MemoryBuilder 调用签名时记得 offline_builder 的 `**kwargs` 会静默吞掉任何新参数——fixture 不会替你发现参数没传到（tests/test_longmemeval_jev.py:33-37）；二，`__new__` 造的 tester 与真实构造器的属性集是**人工同步**的，harness 加属性要回来补 stub（tests/test_longmemeval_jev.py:127-129）；三，缓存失效测试（77-87）新增字段请照抄三行式模式（deepcopy→setattr→断言 manifest 变化），别真跑两次 build——那会拖慢套件；四，想加新题型行为测试时，fixture 的 question_type 是自由文本（datasets 侧是 str 无枚举校验），但适配器只特判 "multi-session"（memory/longmemeval_jev.py:117），新类型默认走 answer_top_k，测试预期要对着这个分支写。
