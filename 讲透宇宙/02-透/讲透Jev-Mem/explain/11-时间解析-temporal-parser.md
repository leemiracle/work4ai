> 标题：时间解析——TemporalParser 精讲 · 源文件：memory/temporal_parser.py（427 行）· 图谱标签：记忆存储与检索子系统 / 叶子模块（零项目内依赖）

## 角色定位

Jev-Mem 的时间语义层：把口语时间表达（"yesterday""last Monday""three weeks ago"）变成可比较的 `datetime`，或带精度标签的归一化文本。文件头（memory/temporal_parser.py:4-6）自述三大职责：相对日期、绝对日期、归一。

为何独立成文件？LoCoMo 这类长程基准里时间信息有两种形态：utterance 里的相对时间（"I moved here last year"——不锚定说话时刻永远不知是哪年）和 question 里的混合时间（"What did Mel do in June 2023?"）。`query_engine` 的时序题型打分（query_engine.py:1504-1570）、`memory_builder` 建图时的 dates_mentioned 属性、`answer_formatter` 的答案归一，全依赖这里的原语。它是干净的叶子模块——只 import re/logging/datetime（temporal_parser.py:9-12），被六个模块共享。

## 内部结构

单类 `TemporalParser`（memory/temporal_parser.py:16）：

**构造期词表**（temporal_parser.py:21-43）：`relative_patterns`（temporal_parser.py:24-37）——12 个表达到 lambda 的映射，`'last month'` 按 30 天近似（temporal_parser.py:32）；`weekday_names`（temporal_parser.py:40-43）。

**解析组**：`parse_session_timestamp`（temporal_parser.py:45）多格式解析——temporal_parser.py:59-65 专门处理 LoComo 特有的 `"1:56 pm on 8 May, 2023"`，temporal_parser.py:68-77 八种格式瀑布，全部失败返回 `datetime.now()`（temporal_parser.py:88，永不抛异常）；`extract_temporal_reference`（temporal_parser.py:90）单引用抽取，三级优先：相对→星期→绝对（temporal_parser.py:104-116）；`_extract_weekday_reference`（temporal_parser.py:120）处理 "last/previous Monday" 等，days_back 回退算法在 temporal_parser.py:143-147，为 0 强制 7 即"上周同一天"；`_extract_absolute_date`（temporal_parser.py:160）四级正则瀑布：DD Month YYYY / Month DD, YYYY / Month YYYY / 裸年份（temporal_parser.py:171-197）；`extract_all_dates`（temporal_parser.py:206）多时间抽取返回 (原文, datetime) 列表。

**归一组**：`describe_references`（temporal_parser.py:247）是本文件最精细的方法——单个大正则（temporal_parser.py:260-266）匹配 yesterday/this past week/last fri/three weekends ago 全形态，逐匹配分类归一：日偏移查表、星期缩写容错、数量词映射（temporal_parser.py:257-281）、月份用 `divmod` 做日历进退（temporal_parser.py:300）；输出带 original/normalized/precision/anchor_date 四字段（temporal_parser.py:311-312）。docstring（temporal_parser.py:248-252）钉死哲学："Anchor relative expressions without inventing finer event precision"。`normalize_date_format`（temporal_parser.py:315）输出 `D Month YYYY` 无前导零格式。

**查询辅助组**：`calculate_duration`（temporal_parser.py:334，人话时长分档）、`is_temporal_question`（temporal_parser.py:371，14 个时序关键词）、`extract_time_constraints`（temporal_parser.py:391，把 "last week"/"yesterday" 翻成 start_date/end_date 区间，421-425 用 min/max）。

## 外部连接

import 只有 re/logging/datetime/typing（temporal_parser.py:9-12）——零项目内依赖，图谱叶子节点。被引（grep 实证 6 文件）：`memory_builder.py`（建图期抽 dates_mentioned）、`answer_formatter.py`（答案归一）、`jev_mem_policies.py`、`jev_mem_retrieval.py`、`longmemeval_jev.py`、`tests/test_jev_mem.py`。注意 `query_engine.py` **不直接** import 它——那边自带 `extract_date_from_question`（query_engine.py:475-506）等简化版，两处能力部分重叠，是历史演化痕迹。

## 数据流

**建图期**（memory_builder 驱动）：utterance `"I watched that movie last Friday with Jon"` 带会话基准时间 2023-05-10（周三）→`extract_temporal_reference`（temporal_parser.py:90）：相对不中→星期引用命中，回退算法算得 2023-05-05（temporal_parser.py:133-147）；或 `extract_all_dates`（temporal_parser.py:206）拿全部提及，以 dates_mentioned 属性挂上事件节点（memory_builder.py:395 回填）。query_engine 的 `find_nodes_by_date_range`（query_engine.py:508）与 `resolve_relative_temporal_reference`（query_engine.py:544）日后靠这个属性做 ±2 天召回与 10/15 分加成。

**查询期**：问题 `"What did Mel start learning two months ago?"` 基准 2023-07-01→`describe_references`（temporal_parser.py:247）：正则命中→count=2、unit='month'（temporal_parser.py:287-290）→日历运算（temporal_parser.py:300）得 normalized="May 2023"、precision='month'→返回四字段 dict。

**约束抽取**：`extract_time_constraints("anything from last week?", ref)`（temporal_parser.py:391）→命中 temporal_parser.py:406-408→`{'start_date': ref-7d, 'end_date': ref}`，可直接当遍历时间窗。**会话时间戳**：LoComo 的 `"1:56 pm on 8 May, 2023"` 经专用分支（temporal_parser.py:60-65）解析为 2023-05-08——数据集特化的活化石。

## 设计决策

**精度不造假原则**（temporal_parser.py:248-252）是灵魂，也是它比朴素 dateparser 更适合记忆系统的原因："last week" 归一成 "The week before 10 May 2023"（temporal_parser.py:306-308）而非随便挑一天。记忆问答里错误的具体日期比诚意的模糊区间危害大——答错日期直接判错，答"那一周"还能对上宽松匹配。对比旧路径把 'last month' 折算成 base-30d（temporal_parser.py:32），`describe_references` 月份走真日历（temporal_parser.py:300），两条路径的精度差就是本模块的进化史。

**永不抛异常的解析**：`parse_session_timestamp` 全链 try 兜到 `datetime.now()`（temporal_parser.py:85-88），每级正则都包 try。批处理管线上一条脏数据不该炸整个建图；代价是错误被静默吞掉，解析失败与时间缺失不可区分，排查靠 temporal_parser.py:86 的 warning。

**lambda 词表驱动**（temporal_parser.py:24-37）：加新模式零逻辑改动。但 30 天/365 天是粗粒度近似——2 月里的 "last month" 会算错月份；`describe_references` 修正了这点，旧路径仍用近似版，并存是技术债。**正则瀑布而非 NLP 模型**：零模型依赖、微秒级、完全确定；代价是覆盖面有限——"a fortnight ago"、中文时间表达不在射程。对 LoCoMo（英文规整）够用，泛化要上 dateparser 或 LLM 抽取。

## 新人提示

先读 `describe_references`（temporal_parser.py:247），对照 docstring 的"不发明精度"看 temporal_parser.py:300-309 分档处理；再读 `extract_temporal_reference`（temporal_parser.py:90）三级优先链理解旧路径。

四个常见误解：以为解析结果是精确日期——precision 字段（day/week/month/year）才是真相，week/month 档的 normalized 是描述性文本不是 ISO 日期（temporal_parser.py:305-308）；以为 'last month' 是日历月——relative_patterns 路径按 30 天近似（temporal_parser.py:32），只有 describe_references 走真日历（temporal_parser.py:300），入口不同结果不同；以为解析失败会报错——`parse_session_timestamp` 返回 `datetime.now()`（temporal_parser.py:88），坏数据伪装成"现在"，排查时间错乱先查这里；以为 query_engine 的时间处理调了本模块——没有，query_engine.py:475-506 自带简化版日期抽取，改本文件不影响那边，两处要同步改。
