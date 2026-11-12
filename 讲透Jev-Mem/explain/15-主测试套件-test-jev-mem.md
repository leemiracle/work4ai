> 标题：Jev-Mem 主测试套件——全链路不变量宪法精讲 · 源文件：tests/test_jev_mem.py（874 行）· 图谱标签：test / integration / invariants · file 度数 95 = 全图谱度数冠军（图谱记 58 个测试函数，实为 54 测试 + 4 夹具，以 grep 实读为准）

## 角色定位

Jev-Mem 的宪法测试：54 个测试函数（`def test_` 实数）加 11 处 `parametrize` 展开约百用例，唯一贯穿"写入→决策→图构建→检索→停止→答案→持久化"全链路。其余测试文件按层切分（tests/test_backend_cache.py 等），只有它做端到端不变量断言——这也是全图谱度数冠军（file 节点 95 度）的由来：顶层 import 横跨十二模块，54+4 个函数级节点全挂其下。

硬前提：test_jev_mem.py:9 `from typesafe_sdk import Choice, Noul` 依赖私有 SDK（Jev 决策服务，协议见 jev_client.py:1-4），test_jev_mem.py:6 `import httpx2 as httpx` 依赖 site-packages 的 httpx 分叉——本机缺 typesafe_sdk 时 pytest collection 直接报错（实测），`-k` 无法逃生；为装 SDK 的 CI 设计。

## 内部结构

**夹具层**（test_jev_mem.py:23-49）：`fixture_answers` 是 mock 决策基线——Noul 默认 0.9、Choice 走 choice_fixture（representation 类选 merge 其余 unknown）、redundancy/contradiction/obsolete/causal 等关系命题一律置零、stopping 强制"证据不足需继续"；`make_builder` 组装全离线栈——JevMemConfig(jev_mock=True)+MockEncoder+NumpyVectorDB+llm_enabled=False，零网络零真 LLM；另有 `add_memories`/`engine_for` 工厂。

**九族测试**：

- 写路径与准入：拒绝零副作用——encoder.encode 钉成 pytest.fail，三空断言（test_jev_mem.py:52-59）；准入+多标签类型共享单次 Jev 请求（test_jev_mem.py:521-531）；默认写保留短句重复句（test_jev_mem.py:534-554）；LoCoMo 每轮保留带溯源且禁用 LLM 抽取（test_jev_mem.py:349-360、557-572）。
- 图结构：四类 LinkType 边共存且方向与判定一致（test_jev_mem.py:62-81）；相似不得推因果、且不向 Jev 发 timestamp 类问题（test_jev_mem.py:84-94）；无时间戳时 MAGMA 顺序与 Jev 别名关系仍成立（test_jev_mem.py:97-108）；增量时间边与批处理规则逐边等价（test_jev_mem.py:583-600，count×dated 参数化）；时间边插入失败整体回滚（test_jev_mem.py:603-617）。
- 预算与停止：候选集有界且关系分批（test_jev_mem.py:111-119）；图预算守恒，(2,3) 用例专测 minimum 钳制（test_jev_mem.py:122-129，对应 jev_mem_policies.py:170-173）；检索五项上限且 llm_calls 必须为零（test_jev_mem.py:132-150）；调用预算与截止双约束（test_jev_mem.py:179-188）；证据充分遍历前停、矛盾阻止收敛（test_jev_mem.py:153-176）。
- wire 协议：MockTransport 假 /v1/systemone——wire 格式、429 重试、二次命中 cache（test_jev_mem.py:208-224）；畸形概率不缓存不崩溃（test_jev_mem.py:227-237）；401/422 不重试且 fail-closed（test_jev_mem.py:240-248）；混合问题逐字段断言、缓存副本不可篡改（test_jev_mem.py:419-458）；key 优先级、非法 choice 拒收、重试计预算与大 Retry-After 不越 deadline（test_jev_mem.py:461-518）。
- 巩固：矛盾留痕 CONTRADICTS 边而非破坏性合并、二次巩固幂等（test_jev_mem.py:265-279）；摘要只在 Jev 批准后生成且不递归（test_jev_mem.py:282-293）；只接受受支持动作（test_jev_mem.py:637-652）。
- 持久化：save/load 与 FAISS 往返保真（test_jev_mem.py:191-205、374-388）；旧 schema 拒复用（test_jev_mem.py:620-634）；显式 load/rebuild 语义（test_jev_mem.py:655-689）；reuse 读调写拒（test_jev_mem.py:747-762）；sys1mem 历史键迁移（test_jev_mem.py:849-874）。
- 检索与格式化：关键词排序用全倒排且确定（test_jev_mem.py:720-731）；检索参数与诊断（test_jev_mem.py:734-744）；稀有事件词压过人名（test_jev_mem.py:824-837）；答案清洗保义、多跳上下文保 speaker/dia_id、时间上下文保邻接（test_jev_mem.py:692-721、807-821）。
- 时间语义：九组相对时间锚定断言，含 2024 闰年锚 yesterday→29 February 2024（test_jev_mem.py:765-782）；无锚返回空（test_jev_mem.py:785-791）；写路径标注只 enrich 属性不改观察时间戳（test_jev_mem.py:794-804）；node_state 分离 observation 与事件时间（test_jev_mem.py:840-846）。

另有审计无凭据（test_jev_mem.py:296-307）、图回滚向量（test_jev_mem.py:310-318）、配置校验、编码器重排、System Two 证据限定、CLI 先验证后入库等单点（test_jev_mem.py:321-416）。

## 外部连接

顶层 import（test_jev_mem.py:1-20）：httpx2（test_jev_mem.py:6）、typesafe_sdk 的 Choice/Noul（test_jev_mem.py:9）、memory 九模块（graph_db/jev_client/jev_questions/jev_mem_config/jev_mem_policies 等图→决策→检索栈）。局部导入拉进 main.JevMemSystem（test_jev_mem.py:393 与 410）等更远依赖。最特殊一条：`from test_fixed_memory import validate_reuse_memory`（test_jev_mem.py:621 与 748）——test_fixed_memory.py 是仓根九行 sys.modules 垫片，转发到 jev_mem/benchmarks/locomo，实际拿到 locomo.py:38 的 validate_reuse_memory。被引：无人 import（测试叶子）；度数 95 全来自 fan-out 与挂载节点。

## 数据流

典型写侧测试：`make_builder` 注入 mock 决策函数（签名 `(operation, state, questions) -> dict`）→ `builder.build(...)` 写入 → 断言图/向量/索引三件套 → `engine_for(builder).query(...)` → 断言 `context.metadata`（停止原因、边数等）。协议族反向流：MockTransport 假服务器 → JevClient(transport=...) → 断言请求体与重试/缓存行为。全链零网络零真 LLM 零磁盘污染。mock 里还能反向观察 Jev 收到的问题集（test_jev_mem.py:86-88 与 113-115）——"没问不该问的问题"本身是被测行为（test_jev_mem.py:94、100）。

## 设计决策

**mock 协议即文档**：fixture_answers 的默认值编码了策略语义——关系命题默认零 → 不建关系边；stopping 三缺一 → 强制继续。读夹具比读 policies 更快理解决策语义，代价是改动全体联动。

**"钉死不该发生"的负向断言**：pytest.fail 被当 monkeypatch 替身值用在 encode、jev.evaluate、extract_event、assess_observation、summarizer 等七处（test_jev_mem.py:55、260 与 367、352-353、544 与 560、273 与 650）。配合消融开关互不掩盖的验证（test_jev_mem.py:251-262），这是防"关掉 A 被 B 兜底"的手段——ablation flag 可信度由这里背书。

**事务性与边界精选**：图插入失败回滚向量（test_jev_mem.py:310-318）与时间边失败回滚节点（test_jev_mem.py:603-617）都构造 add_link 抛异常断言不留半成品；参数化打边界——(2,3) 打 minimum 钳制（jev_mem_policies.py:172-173）、闰年锚打日历语义（test_jev_mem.py:766-767）。

**跨模块垫片依赖是隐藏耦合**：test_jev_mem.py:621 与 748 经仓根垫片借用 locomo benchmark 的校验函数——重构 locomo.py:38 的函数名会静默炸掉这里的测试。

**环境门槛即筛选**：typesafe_sdk 缺失使整文件 collection error（本机实测）——套件核心之一就是与真实 SDK 的 wire 合同（test_jev_mem.py:208-518 十个测试全在打这条线）。图谱口径差：图谱 summary 写 58 个测试函数，grep 实读 54 个测试 def + 4 个夹具 def（test_jev_mem.py:23、35、43、48）。

## 新人提示

先读 test_jev_mem.py:23-49 夹具四件套再读任何测试——不理解 mock 签名与默认值，每个测试都要回来看。按需检索：改写路径跑 52-119 与 583-617；改协议跑 208-248 与 419-518；改检索与预算跑 111-188 与 720-837；改持久化跑 191-205、620-689、747-762、849-874（均指本文件行号）。temporal 合同即 test_jev_mem.py:765-846 五个测试。

三个坑：本机跑 pytest 报 ModuleNotFoundError typesafe_sdk 是预期——先确认环境再怀疑代码；测试失败优先怀疑 mock 语义漂移（fixture_answers 键名与 memory/jev_questions.py 的问题 ID 字符串耦合）；不要把 make_builder 复用于生产——jev_mock=True 是评测替身配置。
