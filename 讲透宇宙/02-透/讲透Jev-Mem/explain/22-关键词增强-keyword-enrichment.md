> 标题：关键词增强——embedding 前置的检索助推器 · 源文件：memory/keyword_enrichment.py（269 行）· 图谱标签：记忆存储与检索子系统

## 角色定位

记忆存储与检索子系统里最小的"信号放大器"：在文本送去 embedding 之前，抽取关键词并拼接到原文/查询后，让向量更偏向人名、年份、日期、时间这类稀疏但决定性的 token。本质是穷人版词权重——embedding 模型会把罕见实体稀释进句向量，写入侧与查询侧各做一次关键词后缀增强（memory/keyword_enrichment.py:161 与 208），两边对称，检索余弦相似度才吃得到这份增强。纯文本处理，无 LLM、无网络，标准库正则加 Counter 搞定全部。

它在仓内有三个消费点、全部是热路径：写入侧 memory/trg_memory.py:185 的 enrich_content（建节点时增强内容）、查询侧 memory/trg_memory.py:249 与 memory/query_engine.py:1166 的 enrich_query（编码查询前增强问题）。注意它**没进** memory/__init__.py 的导出表（grep 实测无 keyword 条目），是子系统的内部模块。

## 内部结构

- `KeywordEnricher`（memory/keyword_enrichment.py:14）唯一类，构造器只初始化停用词表（17-30）：约八十个英文虚词代词，'her' 在字面量里写了两遍（24-25，set 自去重无实害，但暴露手抄清单出身）。
- `extract_keywords`（32-90）：一条顺序管线，按优先级依次喂入——首字母大写的人名/地名序列（49-53，负向后行断言排除句首大写词，只取前五个）；年份（55-56）；十二个月名（58-59，IGNORECASE）；日期与时间模式（61-65）；词频 top 内容词（67-75）；top 双词短语（77-80）；最后保序去重（82-88）并截断到 max_keywords（90，默认十五个）。
- `extract_bigrams`（92-116）：小写 `[a-z]+` 分词（103），两侧都非停用词且长于二字符（107-109），下划线连接成伪词（110），Counter 取 top（115-116）。
- `enrich_content`（118-165）：先抽关键词，再并入 metadata——entities 前五个（134-139）、topic 词（141-145）、speaker（147-150）、semantic_facts 每条前两词取三条（152-157）；有关键词则追加 `[KEYWORDS: ...]` 后缀、截前十五个（159-161），无则原样返回（162-163）。
- `enrich_query`（167-208）：限额十个（180）；实体优先排序（197-206）；最多追加八个词（206）；空格拼接（208）。
- 文件尾是内嵌手工演示 `test_enrichment`（210-268）与 `__main__` 入口（269-270）——生产模块兼职演示脚本；pytest.ini 的 testpaths 限定 tests/，此函数不会被误收集。

## 外部连接

import 仅 re/logging/typing/collections（7-10），零仓内依赖，是子系统里的叶子工具。被引关系（grep 实测）：memory/trg_memory.py:38 导入、:96 实例化、:185 调 enrich_content、:249 调 enrich_query；memory/query_engine.py:18 导入、:51 实例化、:1166 调 enrich_query。测试目录零引用——无单元测试，唯一的验证手段是内嵌演示脚本。图谱把它归入记忆存储与检索子系统层，与 trg_memory/query_engine 同簇，fanIn 二与 fanOut 零（与实测口径一致）。

## 数据流

写入侧：MemoryBuilder 产出抽取结果 → trg_memory 建节点时调 `enrich_content(extraction.content_narrative, metadata)`（memory/trg_memory.py:185-192），metadata 里带 entities/keywords/speaker/topic 四个键 → 增强串（原文加 `[KEYWORDS: ...]` 后缀）送 encoder 编码（trg_memory.py:195-197）→ 向量入库。查询侧两条：trg 的 query 入口 enrich_query 后编码（trg_memory.py:249-251）；query_engine 的图遍历入口同样先 enrich_query 再编码（query_engine.py:1166-1167）。两侧不对称地共享同一套抽取逻辑——内容侧带 metadata 合并（134-157），查询侧只有纯文本抽取（180-206），这是合理的设计差：查询没有结构化元数据可用。

一处实锤口径分裂在写入侧：trg_memory.py:189 传入了 `'keywords': extraction.keywords`，但 enrich_content 的 metadata 合并只认 entities/topic/speaker/semantic_facts 四个键（memory/keyword_enrichment.py:134-157）——上游精心抽取的 keywords 字段被静默丢弃，白传了。

## 设计决策

**后缀而非前缀**（159-161）：`[KEYWORDS: ...]` 拼在原文之后，叙事文本仍占据字符串头部，embedding 对开头的敏感度不被稀释；双方词（content 与 query）共享同一批 token，余弦相似度自然上抬。

**抽取优先级即领域知识**：人名最优先且排除句首大写（49），年月日时各给两个名额（55-65）——这正是 LoCoMo 长程对话记忆的查询分布（"X 什么时候搬的家"、"Y 在哪年养的狗"）。代价是所有配额都硬编码（前五人名、前二月名、top 三短语、查询侧八词），没有配置通道，调参要改源码。

**批判四处**。其一，月名正则 IGNORECASE（58-59）会把情态动词 "may" 当 May 收进关键词，且月名直通 extend、绕过了停用词表（'may' 明明在表内，21 行）——高频情态词就此混入每个含 may 的句子。其二，全部正则都是拉丁字母位（`[A-Z][a-z]+`、`[a-z]+`，49/67/103）——中日韩文本抽不出任何关键词，增强静默变 no-op；对英文基准完美、对多语言场景是隐形天花板。其三，`enrich_query` 里的 question_type 推导（183-187）算完即弃，后续从未使用——预留未用的死代码。其四，仓内停用词表不止这一份：query_engine.py:1162-1164 内联了另一套仅十字的过滤表，两套口径并存，改停用词时极易漏改。

**值得肯定**：双词短语下划线连接成伪词（110）提升了 "adoption_agencies" 这类短语的匹配精度；保序去重（82-88）保证高优先级信号不被低优先级重复挤掉；内容侧十五与查询侧十的限额差（90 与 180）贴合两侧文本长度差。

## 新人提示

最快的手感来自跑内嵌演示：`python3 memory/keyword_enrichment.py`（269-270），看五条示例查询的增强前后对照（254-267），比读十遍代码都快。改 metadata 合并逻辑时记住两头都要动：keyword_enrichment.py:134-157 加新键，trg_memory.py:185-192 的调用方同步传键——keywords 键被丢弃就是只改了一头的存量事故。想让系统支持中文，改的不是加停用词：49/55/61/64/67/103 六处正则全要重写，工作量等于换一个 extractor。排查"检索召回差"时，先打印 enrich_query 的输出（208 行返回值）确认关键词确实抽到了——人名没被大写正则捕获（49）是最常见失因，尤其句首人名被 lookbehind 排除之后。最后，这模块在每个写节点与每次查询上都跑，纯正则加计数，成本相对 embedding 调用可忽略，不必做性能优化。
