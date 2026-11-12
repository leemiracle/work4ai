# browser_use/actor/page.py — 页面对象与动作执行

## ① 角色定位

actor/ 包的自我定位写在 `__init__.py` 开头："A Playwright-like library built on top of CDP"——一个绕开 Playwright、直接架在 Chrome DevTools Protocol 上的高层操作库。page.py 是这个包的门面类：`Page`（page.py:42）代表一个 CDP target（注释明说"tab or iframe"，页签和跨域 iframe 都算），把裸的 CDP 命令包装成 Playwright 味道的方法：goto、reload、screenshot、press、evaluate、go_back。它与 element.py（Element/mouse.py（Mouse）构成"actor 三件套"，服务两类用户：一是 BrowserSession 自己（get_current_page 等工厂方法返回 Page 实例），二是 integrations/openai 与 anthropic 的 browser-use 工具集成（page.py 文件头的 import 可见两处直接消费）。它还带一组"AI METHODS"（page.py:407 起）：用 LLM 按自然语言找元素、抽结构化内容，是库内少有的"自带 prompt"的地方。

## ② 内部结构

构造极简（page.py:45-54）：持有 browser_session、target_id、可选 session_id 和 llm，全部惰性。`_ensure_session`（page.py:56）是核心机关——CDP 的 flat session 模式下，对某 target 操作必须先 `Target.attachToTarget`（flatten=True）拿 sessionId，随后并发 enable 四个域：Page/DOM/Runtime/Network（page.py:66-71）。所有方法第一步都过它，做到"首次访问自动挂载"。方法可分四组：

- **导航组**：goto（page.py:324，Page.navigate，errorText 非空即抛 RuntimeError）、navigate 别名（page.py:333）、go_back/go_forward（page.py:337/359）走 Page.getNavigationHistory + navigateToHistoryEntry 的两步式历史导航，越界（currentIndex≤0 或到尾）直接抛错。
- **输入组**：press（page.py:221）与 hold_key（page.py:240）。press 有双通道设计：单字符或 Enter/Tab/Space 走事件总线的 SendKeysEvent（让 watchdog 统一处理），其余命名键（F1-F12、方向键等有 vk_code 的）直发 Input.dispatchKeyEvent keyDown/keyUp（page.py:226-234）。hold_key 实现修饰键按住语义：别名归一（cmd→Meta 等，page.py:247-259）、modifier_bits 位掩码（Alt=1/Control=2/Meta=4/Shift=8，page.py:261）、逐键 keyDown、sleep(duration)、finally 里逆序 keyUp 且吞掉首个释放异常保后续释放（page.py:277-290），注释明确"不做 auto-repeat"。
- **求值组**：evaluate（page.py:106）强制代码必须是箭头函数（否则 ValueError，page.py:123），拼成 `((...args)=>{...})(json_args)` 后 Runtime.evaluate（returnByValue+awaitPromise，page.py:139），结果一律转字符串返回。`_fix_javascript_string`（page.py:164）做保守清洗：只剥外层引号包裹、只修"明显是 Python 转义残留"的 `\"`。
- **AI 组**：get_element_by_prompt（page.py:414）先取 DOM 树、DOMTreeSerializer 序列化出 llm_representation，配一段内置 system prompt（描述 `[index]<type>text</type>` 格式）让 LLM 返回 ElementResponse(element_highlight_index)，再查 selector_map 还原成 Element（page.py:486-494）；must_ 版本找不到就抛 ValueError（page.py:496）。extract_content（page.py:507）复用与 tools/service.py 同一套 markdown 抽取器（`_extract_clean_markdown`，page.py:572），以 120 秒超时调 LLM 产出 pydantic 结构化结果。

辅助设施：screenshot（page.py:195，jpeg 支持 quality、clip 需正值校验）、set_viewport_size（page.py:292，Emulation.setDeviceMetricsOverride）、get_target_info/get_url/get_title（page.py:308-322）、get_elements_by_css_selector（page.py:382，注意它要把 DOM.querySelector 返回的 nodeId 逐个 describeNode 换成 backendNodeId 才能构造 Element）。

## ③ 外部连接

Page 与 BrowserSession 是双向咬合：Page 持有 session 引用取 cdp_client 与 event_bus；session.py 反过来在 get_current_page/must_get_current_page/get_pages/close_page 等处 import Page（session.py:1372/1383/1398/1433，全部标注"避免循环导入"的函数内延迟 import）。DOM 侧依赖 DomService 与 DOMTreeSerializer（page.py:11-12）；LLM 侧只依赖 base.BaseChatModel 协议，具体供应商无关；键盘细节委托给 actor/utils.get_key_info（page.py:10）。integrations/openai/browser_use.py:19 与 integrations/anthropic/browser_use.py:33 直接 import Page 作为其工具集的操作载体。cdp_use 是底层 CDP 客户端库，所有 `self._client.send.XXX` 调用最终落到它。

## ④ 数据流

以 press("PageDown") 为例：get_key_info 解析出 code+vk_code → 命名键分支直发两次 dispatchKeyEvent（keyDown/keyUp）→ 不经事件总线、不等 watchdog。而 press("a") 走另一条路：event_bus.dispatch(SendKeysEvent) → DefaultActionWatchdog.on_SendKeysEvent 接住 → 由 watchdog 决定逐字符 keyDown/char/keyUp 三连发。两条路径的分工是"Page 能独立完成的快路径"与"需要全局策略（敏感信息脱敏日志、组合键归一）的慢路径"。AI 找元素的数据流是同步闭环：DOM 树（EnhancedDOMTreeNode）→ 序列化文本 → LLM 一个 index → selector_map[index] 拿 DOMTreeNode → `cdp_client_for_node` 换到该节点所属 frame 的 CDP session → Element(backend_node_id)（page.py:493-494）。跨域 iframe 场景全程靠 target_id/session_id 的自动路由对开发者透明。

## ⑤ 设计决策与取舍

一是**flat session 惰性挂载**：不在构造时 attach，首次操作才 attach+enable 四域，构造 Page（如 get_pages 列出全部页签）零 CDP 开销。二是**双通道键盘输入**：文本类输入统一走事件总线（获得脱敏日志与归一化），命名键直发 CDP 保 vk_code 精确——注释（page.py:225）直说这是为了"Preserve named CDP keys that the text-oriented SendKeys action does not recognize"。三是**evaluate 强制箭头函数**：消除"传表达式还是函数体"的歧义，配合 args JSON 化杜绝注入。四是**返回值一律字符串**（page.py:150-162）：牺牲类型保真换调用方简单，对象 JSON 化、标量 str()。五是 extract_content 复用 tools/service 的抽取器（page.py:525 注释"same method as in tools/service.py"）而非另写一套，保证 CLI/MCP/actor 三处抽取结果一致。六是 go_back/go_forward 用历史表导航而非 Page.back 命令——CDP 没有可靠的原生 back，历史表方案还能精确越界检测。

## ⑥ 新人提示（坑/勘误）

- **Page ≠ 浏览器 tab**：它是 CDP target，一个跨域 iframe 也是合法的 Page（page.py:43 注释），target_id 语义比"tabId"宽。
- **evaluate 不接受普通函数声明或表达式**：必须 `(...)=>` 开头（page.py:123），传 function(){} 或裸表达式直接 ValueError；`_fix_javascript_string` 的清洗刻意保守，复杂的引号问题它不救。
- **press 的例外清单会变**：'Enter','Tab','Space' 三个名字键走 SendKeysEvent（page.py:227），其余 vk 命名键直发 CDP；改这里的行为要同步看 watchdog 的 on_SendKeysEvent。
- **hold_key 只接受修饰键组合**：非末位键不在 modifier_bits 里就抛 ValueError（page.py:262-263），"按住字母 a 三秒"这种需求它不支持。
- **get_element_by_prompt 找不到返回 None 而不抛错**（page.py:486），LLM 返回的 index 不在 selector_map 也归为 None；需要强失败用 must_get_element_by_prompt。
- **get_elements_by_css_selector 是 N+1 查询**：每个命中节点都要单独 describeNode 换 backendNodeId（page.py:398-403），大结果集慢是结构性的。
- extract_content 的 120 秒超时（page.py:560）把一切异常都折成 RuntimeError（page.py:569-570），原始错误类型丢失，排障时要知道这层包裹。
