> 标题：LoCoMo 数据集加载——基准数据的唯一入口 · 源文件：jev_mem/datasets/locomo.py（246 行）· 图谱标签：基准与数据集层

## 角色定位

基准与数据集层的底座：把 LoCoMo 原始 JSON 解析成带类型的 dataclass 树，供评测全链消费。纯标准库实现（jev_mem/datasets/locomo.py:1-6：json/os/dataclasses/datetime/pathlib），不碰 LLM、不碰网络，是整个仓库最干净的叶子模块之一。

**同名文件勘误（新人第一坑）**：仓里有两个 locomo.py——本文件是数据加载层（jev_mem/datasets/locomo.py），另一个是 benchmark 编排 runner（jev_mem/benchmarks/locomo.py，精讲 12）。runner 在 jev_mem/benchmarks/locomo.py:29 导入本模块的 `load_locomo_dataset`（:475 调用），方向是 runner 依赖 loader、反之零依赖。仓库根的 load_dataset.py:3 是兼容垫片，其 docstring 明言 "use jev_mem.datasets.locomo instead"——老入口只剩转发。

## 内部结构

- 七个 dataclass（jev_mem/datasets/locomo.py:8-57）定义全仓数据词汇表：
  - `QA`（8-21）：question/answer/evidence/category/adversarial_answer，唯一带行为的成员是 `final_answer` property（16-21）——category 为五（对抗题）时返回 adversarial_answer，否则 answer
  - `Turn`（23-27）speaker/dia_id/text；`Session`（29-33）；`Conversation`（35-39）双说话人加 session 映射；`EventSummary`（41-43）；`Observation`（45-47）；聚合根 `LoCoMoSample`（49-57）
- `parse_session`（59-77）：含图轮次的 caption 融合——`[Image: blip_caption]` 前缀拼 text（63-70），多模态轮降维成纯文本
- `parse_conversation`（79-95）：遍历 session_N 键（82-84），日期取兄弟键 session_N_date_time（85），空 session 跳过（88-89）
- `load_locomo_dataset`（97-202）：存在性检查（110-111）、json 加载（113-114）、逐样本解析主循环（121-193）——其中嵌着逐 QA 的图片证据预扫描（127-140）、QA 构造（145-152）、四类子结构装配（164-170）、统计累加与打印（186-188）；收尾全量统计块（195-200）
- `get_dataset_statistics`（204-227）：程序化统计接口，纯聚合
- `main`（229-242）冒烟入口：默认加载 data/locomo10.json（230），逐 session 只打第一轮（236-239 的 break 位置）

## 外部连接

零仓内 import（1-6 纯标准库）——图谱里 fanOut 为零的数据层叶节点。被引关系（grep 实测）：jev_mem/benchmarks/locomo.py:29（评测主入口）、scripts/evaluate_anchor_recall.py:28（锚点召回研究）、utils/utils.py:53（一次导入五个类型）、memory/test_harness.py:20（LoCoMoSample 类型标注）、load_dataset.py:3（兼容垫片）、tests/test_project_layout.py:16 与 24（布局契约测试钉死模块路径与 QA 类型）、tests/test_public_release.py:151 与 153（用 examples/locomo_synthetic.json 做发布冒烟）。注意 memory/test_harness.py 这个 memory/ 下的文件反向依赖 jev_mem/datasets——数据类型是跨子系统的公共语言。

## 数据流

raw JSON（benchmark 用 --dataset 传入，冒烟默认 data/locomo10.json）→ `load_locomo_dataset` → `List[LoCoMoSample]` → 消费方拿走三样东西：对话轮（构建记忆的原料）、qa 列表（评测题目）、evidence dia_id（召回率对账，见 test_harness 的 evidence_recall）。对抗题语义在出口处收口：所有正经消费方都取 `qa.final_answer`（memory/test_harness.py:329、335、408、475、482、554、578 一致使用），property（16-21）是陷阱答案换入的唯一关卡。evidence 的形状是 "session:turn" 冒号串（131-133 拆分），图片证据预扫描就是拿 turn 部分去对话里 suffix 匹配（137）。统计只走 print（186-200），返回值里不带——要程序化统计用 get_dataset_statistics（204-227）。

## 设计决策

**final_answer 用 property 而非加载期归一**（16-21）是本文件最好的一笔：原始字段全部保真（分析对抗题仍能看到陷阱答案本体），消费方一行 property 拿到安全值；配合 test_harness 全线使用 final_answer，category 五的陷阱在评测口径里零泄漏。反面是纪律依赖——谁直接读 .answer 谁踩坑，仓内目前无违例。

**批判三处**。其一，图片证据预扫描（127-140）是纯为打印而生的重活：has_image_evidence 只用来累加两个计数器（142-143、182-183），从不落进 QA 对象，最终只出现在 print 行（188、197）——四层嵌套（QA×evidence×session×turn）全量扫描，换来的仅是加载时控制台噪音；且匹配用 `dia_id.endswith(turn_id)`（137），turn 部分为 "2" 时会误命中 "...12" 结尾的轮次，后缀匹配的松紧度从未校准；找到命中后 break 只跳出最内层 turn 循环（140），外层继续空转。其二，print 当日志用（156-157、160-161、186-192）：库代码里 print+re-raise 的错误处理，进度与错误混在 stdout，无法静音无法分级。其三，空数据集即崩：len(samples) 作除数（198）与 min/max 空序列（199-200）在空文件或全过滤场景分别抛 ZeroDivisionError 与 ValueError——对固定的十样本数据集无所谓，接自定义切片就会翻车。

**宽松与严格不一致**：session_summary 走防御性 .get（170），event_summary/observation 却硬下标（166、168）——上游 schema 少字段时前者静默空 dict、后者 KeyError，行为分裂。sample_id 用枚举序号字符串（173），原始标注 ID 被丢弃，跨数据集对账时无锚。

## 新人提示

先读 8-57 的 dataclass 块——七个类就是全仓评测代码的公共词汇表，QA.final_answer（16-21）是唯一需要记住行为的地方；然后跳到 parse_conversation（79-95）理解 session_N/session_N_date_time 的扁平 schema 约定，这是自制数据集必须遵守的格式。加载一行即得：`from jev_mem.datasets.locomo import load_locomo_dataset`；控制台会刷一堆统计（186-200），那是预期行为不是错误。想做 judge 重评之类的轻量任务只要 QA 对——抱歉，load_locomo_dataset 没有 only_qa 选项，你仍要付全量对话解析加图片扫描的成本（127-140）。最小可跑 schema 样本看 examples/locomo_synthetic.json（tests/test_public_release.py:153 在用），照着造数据最快。最后对齐口径：本文讲数据加载层，评测编排请看精讲 12（jev_mem/benchmarks/locomo.py），两个同名文件别混。
