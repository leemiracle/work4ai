> 标题：会话分段器——EpisodeSegmenter 精讲 · 源文件：memory/episode_segmenter.py（331 行）· 图谱标签：记忆构建子系统 / 流式语义分段（Episode 层的诞生地）

## 角色定位

Jev-Mem 的"情节切分器"：把逐条涌入的 turn 流式聚成语义完整的 Episode，供 memory_builder 建图。模块头（memory/episode_segmenter.py:1-6）自述基于 Nemori 的 episode segmentation 思路做语义边界检测。它在 TRG 图里承担"从对话到情节"的第一级抽象：Event 由单 turn 抽取，Episode 由本模块决定哪几条 turn 同属一件事。

为何要这层？LoCoMo 多跳题常横跨多轮同主题对话，Event 粒度太碎、Session 太粗，Episode 是检索的中间锚点。触发是流式的：每来一条 turn 判断"话题是否断了"，断了就把缓冲区打包成 Episode——无需预拿全量对话。

## 内部结构

四个类，各司其职：

**Episode**（memory/episode_segmenter.py:14-28）：@dataclass 情节单元——title/content（LLM 摘要）、original_messages、participants、起止时间戳、boundary_reason（审计字段）、metadata，episode_id 默认取创建时刻的时间戳浮点数（memory/episode_segmenter.py:28）。

**MessageBuffer**（memory/episode_segmenter.py:30-69）：定长缓冲区。add 对 dict/对象两种输入归一化（memory/episode_segmenter.py:38-53），is_full 判满（memory/episode_segmenter.py:59-61），get_messages 返回浅拷贝防篡改（memory/episode_segmenter.py:67-69）。

**BoundaryDetector**（memory/episode_segmenter.py:71-184）：两级判定器。`detect_boundary`（memory/episode_segmenter.py:80-96）先走快路径——显式信号命中直接返回 confidence 1.0（memory/episode_segmenter.py:88-91）；缓冲不足两条拒绝语义判定（memory/episode_segmenter.py:93）。快路径 `_check_explicit_signals`（memory/episode_segmenter.py:98-126）看两类信号：跨日（两条 timestamp 的 `.date()` 不同即切，memory/episode_segmenter.py:111-115）与六个话题标记词（by the way 等，memory/episode_segmenter.py:117-124）。慢路径 `_semantic_boundary_check`（memory/episode_segmenter.py:128-184）取缓冲最后五条拼上下文（memory/episode_segmenter.py:139-142），要 LLM 返回 is_boundary/reason/confidence 三键 JSON（memory/episode_segmenter.py:144-163），temperature 0.0（memory/episode_segmenter.py:166-170）；**置信闸门**在 0.7——LLM 说切但置信不足仍不切（memory/episode_segmenter.py:177-180）；异常一律返回"不切"（memory/episode_segmenter.py:182-184）。

**EpisodeSegmenter**（memory/episode_segmenter.py:186-331）：编排器。构造时解包 `llm_controller.llm` 兼容两种注入（memory/episode_segmenter.py:198），默认十条/两条（memory/episode_segmenter.py:190）。核心 `process_turn`（memory/episode_segmenter.py:205-241）顺序是灵魂：**先判边界再加新 turn**——缓冲满强制切（memory/episode_segmenter.py:220-222），否则 detector 判（memory/episode_segmenter.py:224-230）；确认切且条数达标才打包并清缓冲（memory/episode_segmenter.py:232-236），新 turn 入缓冲起下一段（memory/episode_segmenter.py:239）——边界 turn 归下一段，与"从此翻篇"直觉一致。收尾：flush_remaining 打包尾巴（memory/episode_segmenter.py:243-252），finalize 是别名（memory/episode_segmenter.py:254-258）。`create_episode`（memory/episode_segmenter.py:260-295）聚合参与者、调 `_generate_title_and_summary` 出标题摘要（memory/episode_segmenter.py:277）、取时间戳 min/max 为起止（memory/episode_segmenter.py:280-282）。摘要失败降级为首行截断当标题、前两百字符当摘要（memory/episode_segmenter.py:322-327）。

## 外部连接

对内只有标准库依赖（json/logging/dataclass/datetime/typing）——图谱干净叶子。唯一上游是 memory_builder：import 于 memory/memory_builder.py:21；构造于 memory/memory_builder.py:104-110，且**覆写两个默认参**——max_buffer_size 压到五、min_episode_size 压到一条（段更碎，换更细检索锚点）；生产驱动点是逐 turn 的 process_turn（memory/memory_builder.py:1242）与会话末的 finalize（memory/memory_builder.py:1252）。下游出口：episode.episode_id 直接充当图节点 ID（memory/memory_builder.py:517 的 EpisodeNode 构造），随后双向建链——EPISODE CONTAINS EVENT 正向、EVENT PART_OF EPISODE 反向（memory/memory_builder.py:1045-1067）。另经 memory/__init__.py:23 懒加载表导出；图谱 fanIn 与 grep 一致，无口径差。

## 数据流

建图期全程在线（memory_builder.build_dataset 内）：turn 到来 → memory_builder 先做 Event 抽取入图，再把 turn_data（speaker/text/timestamp/dia_id/entities/topic/dates_mentioned 七键，memory/memory_builder.py:1232-1240）喂给 process_turn → 快路径查标记词，慢路径拼五条上下文问 LLM"是不是话题转折"→ 判切则 create_episode：LLM 生成标题加摘要 → Episode 被 create_episode_node 落成 EpisodeNode → episode_buffer_events 攒的 event_id 逐个建 CONTAINS/PART_OF 双向链 → 缓冲清空，新 turn 起段。会话循环结束调 finalize 兜住尾段（memory/memory_builder.py:1251-1255）。查询期受益是间接的：query_engine 沿 PART_OF 下钻到事件、沿 CONTAINS 聚合，answer_formatter 按 Episode 摘要整段输出。

## 设计决策

**先判后加的顺序语义**（memory/episode_segmenter.py:215-241）是最重要的一条：边界 turn 永远开启新段而非闭合旧段，保证话题纯净。**两级判定**把便宜规则（跨日、标记词）放在贵的 LLM 前，显式信号免 LLM 调用；**置信闸门加异常保守化**（memory/episode_segmenter.py:177-184）共同确立"宁可长段不误切"——切错伤多跳检索，长段只是摘要略泛，代价不对称。**对话级容错降级**（memory/episode_segmenter.py:322-327）保证摘要失败时情节仍成立（截断原文顶上），分段不因模型故障中断建图。

批判性发现一条主坑加两条次坑。**主坑：跨日快路径在生产接线下是死的。** `_check_explicit_signals` 依赖 timestamp 对象有 `.date()` 方法（memory/episode_segmenter.py:112-113），但 memory_builder 喂进来的 timestamp 是 `isoformat()` 字符串（memory/memory_builder.py:1235）——字符串没有 `.date`，hasattr 守卫把两边判 None，日期变更永远不触发边界，快路径只剩六个标记词在工作；且 create_episode 的起止 min/max（memory/episode_segmenter.py:280-282）是在对 ISO 字符串做字典序比较——ISO 字典序恰与时间序一致故侥幸正确，属巧合非设计。**次坑一**：episode_id 用创建时刻墙钟（memory/episode_segmenter.py:28）而非对话时间或内容哈希，同微秒建两段会撞 ID。**次坑二**：每条 turn 一次边界 LLM 调用加每段一次摘要调用，成本 O(turns)——数百 turn 的样本上这是建图期 LLM 开销大头，且与 max_buffer_size 无关（缓冲满只省摘要不省判定）。

## 新人提示

先读 process_turn（memory/episode_segmenter.py:205-241）理解"先判后加"；再读 detect_boundary 两级结构与置信闸门（memory/episode_segmenter.py:80-96、177-180）。

四个常见误解：以为分段参数是类默认的十条/两条——生产是覆写后的五条/一条（memory_builder.py:104-110），调参改那边；以为跨天必切——该路径真实数据上是死代码（memory_builder.py:1235 与 episode_segmenter.py:112-114 类型错配），只有标记词和 LLM 判定在切；以为 min_episode_size 不满足时缓冲清空——不会，turn 继续累积（memory/episode_segmenter.py:232-239），这一刀推迟；以为摘要失败该段作废——截断原文顶上、照常入图（memory/episode_segmenter.py:322-327），首行截断式 title 就是降级指纹。
