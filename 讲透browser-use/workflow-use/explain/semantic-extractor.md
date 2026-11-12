# workflow/semantic_extractor.py — 语义提取臂：可见文本到确定性选择器

> 源文件：`workflows/workflow_use/workflow/semantic_extractor.py`（1097 行）

## 一、角色定位

`SemanticExtractor`（L14）是"零 AI 执行"路线的感知端：把当前页面上的可交互元素抽取出来，建立 **可见文本 → 确定性选择器** 的映射（`extract_semantic_mapping`，L816），并提供按文本找元素的匹配服务（`find_element_by_text` L867 / `find_element_by_hierarchy` L1019）。它的存在动机写在类 docstring 里：CSS 选择器脆弱，LLM 每步调用昂贵；用"人眼看到的文字"做锚点，配多级选择器兜底，两端都占。

上游是 `SemanticWorkflowExecutor`（每步执行前调用它建映射），下游消费它的 mapping 做 index 定位或选择器回退。整个模块**不调用任何 LLM**，全部是 DOM 注入 + 纯 Python 字符串匹配。

## 二、内部结构

- **类型识别与编号**：`_get_element_type_and_id`（L24）把元素归入 7 类（input/button/select/textarea/a/radio/checkbox）——ARIA role 优先于标签（L32-35），input 再按 type 细分 radio/checkbox（L37-40），未知标签兜底为 input（L52）；编号 `f'{type}_{n}'`（L55-56），计数器由 `_reset_counters`（L20）每次提取前重置。
- **文本来源优先级**：`_get_element_text`（L67）按 label_text → text_content → placeholder → title → aria_label → value → name → id 八级链取第一个非空（L70-79）。
- **去重机制**：`_handle_duplicate_text`（L161）对重复文本依次尝试层级上下文（`_get_hierarchical_context` L107）、坐标 `at x,y`、id/name/class（取前两个 class，L189-191）、最后是纯数字后缀 `(2)`（L200-204）。
- **DOM 抽取引擎**：`extract_interactive_elements`（L206）内嵌一段约 560 行的 JS（L212-775），经 `page.evaluate(js_code, debug_mode)`（L778）执行后 JSON 解析（L783）。
- **匹配器**：`find_element_by_text` 五策略瀑布 + `find_element_by_hierarchy` 带上下文提示的加权匹配。

## 三、外部连接

- 依赖极简：`aiofiles`（L6，仅 debug 落盘用）、`re`、标准 logging；`Page` 类型只在 `TYPE_CHECKING` 下导入（L8-9），运行时零 browser-use 依赖——这是个可独立单测的纯逻辑模块（除 evaluate 外）。
- JS 内的选择器清单（L226-246）覆盖标准控件、ARIA role 全家桶、日历/日期选择器、下拉菜单、`data-testid/cy/qa`，甚至**机票/预订站点专有选择器**（`.flight-option`、`.book-now`、`[data-flight]` 等，L244-245）——后者暴露了这个项目的目标场景。

## 四、数据流

一次 `extract_semantic_mapping(page)`：

1. 重置计数器（L821）→ `extract_interactive_elements` 拿原始元素列表（L824）；
2. JS 侧先 `querySelectorAll(interactiveSelectors)`（L252），逐元素：跳过隐藏元素（宽高为 0 / visibility:hidden / display:none，L650-653）；生成三层选择器——`css_selector`（有 id 用 `#id`，否则标签+data 属性+name+type，L664-685）、`hierarchical_selector`（`safeGetDOMPath` 最多 5 层、遇 id 短路，L476-512）、`fallback_selector`（裸标签名，L725）；文本回退链 textContent → aria-label → title → placeholder（L695-704）；
3. JS 侧每个元素还携带 widget 检测（`safeGetWidgetType` L260：calendar/dropdown/booking/form/action/generic 六类）、日历上下文（departure/return 识别，L327-335）、**表格标签提取**（`safeGetLabelText` L514：label[for] → 最近 label → 前兄弟 → 前一个 td/th 且文本 <50 字符、去尾冒号，L540-553）、兄弟位置、坐标；
4. Python 侧逐元素定型（L831）、取文本（L834）、无文本则用占位符 `[Button]`/`[Input Field - text]` 等（L87-105）、去重（L841），最终 mapping 值含 selectors/hierarchical/fallback/text_xpath 四级选择器加 `deterministic_id`、`original_text`、`label_text`（L856 注释强调 input 匹配靠它）等内部字段（L845-861）。

匹配阶段（`find_element_by_text`）五策略依次降级：①大小写不敏感精确匹配（L874-878）；②目标形如 id/name（去 `_`/`-` 后全字母数字，L881）时直接查选择器串里的 `#xxx`/`[name=]`/`[id=]`（L885-889）；③解析 `Submit (in Contact Form)` 式括号上下文，全匹配 1.0 分、container/dom_path 命中 0.8 分（L893-925）；④模糊匹配：双向子串长度比 + 对 original_text 同样计算 + 词集 Jaccard 与重叠率，阈值 0.3（L927-982）；⑤camelCase/snake_case 拆词 70% 命中（L984-1014）。

## 五、设计决策与取舍

- **选择器四层冗余**：css_selector 会因一次改版失效，hierarchical_selector、fallback_selector（裸标签）、text_xpath（`//tag[contains(text(), ...)]`，L726）逐级兜底——执行端拿到的是"一篮子"而非单点。
- **JS 全防御式编程**：所有辅助函数都 try-catch 包裹（safe* 前缀族），单个元素抽取失败只 errorCount++ 不中断整页（L749-756）——爬陌生页面的工程现实。
- **debug_mode 硬编码 False**（L210）：打开后会把 debugLog 与 stats 用 aiofiles 落盘（L790-791），文件名用事件循环时间戳；这是排障后门而非产品功能。
- **匹配分数体系是手调的**：0.3 模糊阈值（L975）、0.5 层级阈值（L1090）、70% 拆词率（L1005）、base×0.7 + context×0.3 权重（L1081）——没有学习成分，全部经验值，改前先跑回归。
- **evaluate 返回值双形态兼容**：`json.loads(result_str) if isinstance(result_str, str) else result_str`（L783）——不同浏览器内核对 evaluate 返回的处理不一致。
- **失败返回空列表而非抛错**（L814）：上游语义执行器把"找不到"当作可恢复状态走下一级策略，本模块不做政策决定。

## 六、新人提示（坑/勘误）

1. **映射的 key 不是纯页面文本**：重复文本会被自动加后缀（`(in 父容器)`、`(at 120,340)`、`(2)`），精确匹配策略能吃到这些 key，但直接拿页面原文查 mapping 可能 miss——匹配请走 `find_element_by_text` 而非 `mapping[text]`。
2. **text_xpath 有注入风险**：elementText 直接拼进 `contains(text(), "...")`（L726），文本含双引号会产出非法 XPath，消费方需自 行处理异常。
3. `_get_hierarchical_context` 的 parent_text 截断到 50 字符（47+`...`，L115-117），容器文本取前 5 个词（JS L440-441）——上下文信息是有损压缩的。
4. 计数器是实例状态且在 `extract_semantic_mapping` 开头才重置（L821）：直接调用 `extract_interactive_elements` 不重置，`deterministic_id` 会跨页累计——单测时容易踩。
5. 航班/预订专用选择器（L244-245）与 widget 三类特判（calendar/dropdown/booking）说明这套抽取器在旅行预订场景上调过——别的领域遇到识别不准先看 `safeGetWidgetType` 的 className 关键词表（L271-289）。
6. L788 有重复的 `import json`（L781 已导入），无害但表明 debug 分支久未走。
