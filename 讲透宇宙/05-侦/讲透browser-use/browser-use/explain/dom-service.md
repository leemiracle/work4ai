# browser_use/dom/service.py 精讲——DOM 树构建：三树合一的感知引擎

## 一、角色定位

`browser_use/dom/service.py`（1245 行）定义 `DomService`（L45）——把活页面变成模型可读文本的感知引擎。Agent 每步看到的"Interactive elements 列表"源头在这里：并行发起多路 CDP 请求拿三棵树（DOMSnapshot 快照、DOM.getDocument 全量树、Accessibility 无障碍树），融合成 `EnhancedDOMTreeNode` 增强树，再交序列化器产出 `SerializedDOMState` 与 `selector_map`（元素索引→节点映射，动作寻址基础）。类 docstring L51 留着 TODO："currently we start a new websocket connection PER STEP"——每步新建连接的已知债务。

## 二、内部结构

**构造参数即策略**（L56-72）：`cross_origin_iframes`（默认关——L977 注释自嘲 "hacky way to disable"）、`paint_order_filtering`、`max_iframes`（默认 100）、`max_iframe_depth`（默认 5）、`viewport_threshold`（默认 1000px）。`__aexit__` 空操作（L77-78，session 自管缓存）。

**核心方法 `_get_all_trees`（L403-700）**——单次采集的全部 CDP 交互：

1. **就绪探测**（L407-412）：`document.readyState` 一次 evaluate，失败静默。
2. **iframe 滚动位置采集**（L417-454）：注入 JS 遍历 iframe 读 scrollTop/scrollLeft，跨域在 JS 内 catch。
3. **JS 点击监听器探测**（L456-567）：最精巧的一段。用 `includeCommandLineAPI: true` 打开 DevTools 专属 `getEventListeners()`（L502），全元素扫描找带 click/mousedown/pointerdown 监听器的元素。三重自保护：页面超 10000 元素放弃（L477-479）、命中超 100 个返回哨兵值跳过解析（L489-491、L508-511）、`DOM.describeNode` 换 backendNodeId 按 20 个一批限并发（L546-552，注释解释：describeNode 触发 target/session 簿记，几十个并发能饿死截图等其他 CDP 请求）。最后 `Runtime.releaseObject` 防泄漏（L556-562）。
4. **四路并行 CDP 请求**（L589-598）：snapshot / dom_tree / ax_tree / device_pixel_ratio 同时发出，`asyncio.wait(timeout=10.0)`；超时或失败的逐个重试一轮（短超时 2.0s，L622-623），再不行**区别对待**——AX 树失败降级为空节点集继续（L641-642，注释 L629-632：AX 只是增强，snapshot+DOM 仍可用，不该陪葬），其余失败才抛 TimeoutError（L653-654）。
5. **iframe 爆炸防护**（L667-674）：snapshot 文档数超 `max_iframes` 截断并 WARNING。

产出打包 `TargetAllTrees`（L688-700），带完整 `cdp_timing` 分解。

**get_dom_tree（L703-1110）**：三树融合为增强树。签名里的递归状态参数暴露递归本质：`iframe_depth` 防无限嵌套、`visited_cross_origin_targets` 防环、`initial_total_frame_offset` 累积 iframe 坐标偏移（iframe 内元素坐标加外层偏移才是绝对坐标）。内部 `_construct_enhanced_node`（L759）逐节点挂 snapshot 数据、AX 属性、可见性。**跨域 iframe 递归**（L973-1034）只在 `cross_origin_iframes` 开启时走：iframe 可见 + 两边都 ≥10px（L37、L40-42）才递归进对应 target；`all_frames` 惰性获取（L1011-1013，真遇到才拉 frame 树）；frameId 缺失退回按 src URL 匹配（L1018-1031，注释举例 HubSpot 弹窗这类动态注入 iframe 的兜底）。

**get_serialized_dom_tree（L1111-1165）**：对外主入口。get_dom_tree（all_frames=None 惰性）→ `DOMTreeSerializer(...).serialize_accessible_elements()`（L1140-1142）→ 返回 `(serialized_dom_state, enhanced_dom_tree_root, timing_info)`。计时偏执级：分项计时之外还算"未追踪开销"（tracked 与 total 差值，超 0.1ms 才记，L1150-1153）——性能回归排查产物。

**detect_pagination_buttons（L1167-1245）**：静态方法，从 selector_map 识别分页按钮。四组模式词表（next/prev/first/last，L1188-1191）五语支持（英/西/法/德/荷）；`«`/`»` 歧义符号只作兜底、词信号优先（L1186-1187）；纯数字 1-2 位且 role 是 button/link 识别为页码（L1230）；还探测 disabled。翻页任务靠它免于每页肉眼找"下一页"。

**隐藏元素统计（L80-192）**：`_count_hidden_elements_in_iframes` 收集 iframe 内"被 viewport 阈值藏起来（非 CSS 隐藏）"的可交互元素，每 iframe 上限 10 条，每条带 tag/标签/距离几页（L128）——变成给 LLM 的"往下滚 3 页有个按钮"提示。判隐藏的关键区分在 L87-103：先确认不可见，再排除 display:none/visibility:hidden/opacity≤0 的 CSS 隐藏——**只有"位置在视口外"的才"滚动能救"，CSS 藏的滚了也白滚**。

## 三、外部连接

- **唯一消费者是 DOMWatchdog**（`browser/watchdogs/dom_watchdog.py` L558 实例化 DomService）：BrowserSession 派发 `BrowserStateRequestEvent` → DOMWatchdog 调 `get_serialized_dom_tree` → 结果进 `BrowserStateSummary.dom_state`。DomService 不被 Agent/Tools 直接调——感知也走总线。
- **序列化下游**：`dom/serializer/serializer.py` 的 `DOMTreeSerializer.serialize_accessible_elements`（L114）产出 selector_map；`dom/views.py` L936 `SerializedDOMState.llm_representation()`（L943）渲染模型文本——prompts.py L252 调用的正是它。
- **上游依赖**：cdp-use 的 `DOMSnapshot.captureSnapshot`（含 paintOrder/DOMRects，L571-580）、`DOM.getDocument(depth=-1, pierce=True)`（L582-585，pierce 穿透 shadow DOM）、`Accessibility.getFullAXTree`。
- **配置来源**：BrowserProfile 的 max_iframes/max_iframe_depth/cross_origin_iframes/paint_order_filtering（文件头注释 L32 明说配置化）。

## 四、数据流

一步感知的完整链条：CDP 四路并行 + 两路预处理（iframe 滚动、JS 监听器）→ `TargetAllTrees` → get_dom_tree 三树融合（backendNodeId 对齐、AX name/role 挂载、shadow root 展开、跨域 iframe 递归）→ `EnhancedDOMTreeNode` 树 → 隐藏元素统计回填 → `DOMTreeSerializer` 过滤+编号 → `SerializedDOMState`（`_root` + `selector_map: {index: node}`）。此后两条消费线：模型侧 `llm_representation()` 渲染带索引的元素清单；执行侧 Agent 的 click/input 拿 index 查 `selector_map`（BrowserSession.get_element_by_index）找 backendNodeId 发 CDP 命令。**索引是感知与执行的共同货币**。

## 五、设计决策与取舍

1. **三树融合而非单树**：DOMSnapshot 给布局/paintOrder/bounds（语义弱）、DOM.getDocument 给结构层级（无样式）、AX 树给语义名与角色（可能失败）。互补且任一失败不致命——AX 显式降级（L629-642）是冗余观体现。
2. **并发加严控**：CDP 请求并行（10s+2s 两轮超时），但 describeNode 批 20、监听器上限 100——对远程 CDP 连接脆弱性的敬畏（L456-459 注释直言无界 gather 会让会话显得卡死）。
3. **iframe 双闸**：数量（max_iframes 截文档）+ 深度（断递归），防百级 iframe 爆内存。
4. **可见性区分"滚得回"与"真隐藏"**：视口外的值得提示（滚动可救），CSS 隐藏不提示——L87-103 分开两类。
5. **计时内建**：每阶段 ms 级 timing 且算未追踪开销。

## 六、新人提示（坑/勘误）

- **`llm_representation` 不在本文件**：在 `dom/views.py` L943（SerializedDOMState 方法）；本文件只建树。搜错文件是新人常见迷路点。
- **`cross_origin_iframes` 默认 False**：跨域 iframe（支付弹窗、嵌入式登录）默认看不到——"为什么 agent 看不到 reCAPTCHA iframe"类问题第一查点。
- **每步新建 WebSocket**：docstring L51 的 TODO 是已知性能债；高频调用要有开销意识。
- **selector_map 索引每步都可能变**：页面一变编号重排。这就是 Tools 层动作先 `get_element_by_index` 查证、找不到就回"页面可能变了"（tools/service.py L785-789）的原因。
- **`_JS_CLICK_LISTENER_OVERFLOW` 哨兵是字符串**：`'__browser_use_too_many_click_listeners__'`（L36）经 `%r` 注进 JS 传回（L490、L508），别当异常处理。
- **iframe 坐标是累积偏移**：嵌套 iframe 元素 bounds 已含外层偏移，自行解析坐标别重复加。
