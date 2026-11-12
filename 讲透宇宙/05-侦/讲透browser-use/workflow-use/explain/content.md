# content.ts 精讲——扩展内容脚本（rrweb DOM 录制 + 语义事件采集双通道）

## ① 角色定位

`extension/src/entrypoints/content.ts`（1075 行）是浏览器扩展注入到**每个网页**的录制探头，属图谱 L11「extension 录制采集链路」核心节点（54 节点大文件）。它同时跑两套采集：

- **rrweb 增量快照流**（`rrweb.record`，L122-198）：录 DOM 结构演化，产出 `RRWEB_EVENT`——"页面上发生了什么"的原始底片；
- **8 个自定义捕获监听器**（L206-213，click/input/change/keydown/mouseover/mouseout/focus/blur 全 capture 阶段挂 document）：在真实交互上叠加语义提取，产出 `CUSTOM_CLICK_EVENT`/`CUSTOM_INPUT_EVENT`/`CUSTOM_SELECT_EVENT`/`CUSTOM_KEY_EVENT`——"每步意味着什么"的语义注解。

双通道是 workflow-use 录制架构的基石：rrweb 保证回放完整性，自定义事件保证步骤的语义可定位性（targetText/xpath/cssSelector/semanticInfo 一应俱全）。两者都经 `chrome.runtime.sendMessage` 发给 background.ts（消费 case 在其 L304/349/419/443）。注入面 `matches: ["<all_urls>"]`（L1006）全站生效。

## ② 内部结构

**模块状态**（L4-9）：`stopRecording`（rrweb 停止句柄）、`isRecordingActive`（本地开关）、滚动防抖三件套 + `DEBOUNCE_MS = 500`。

**选择器工具**：`getXPath`（L12-38）——有 id 直接 `id("xxx")`（L13-15），否则递归统计同名兄弟生成 `div[2]/span[1]` 式位置路径；`getEnhancedCSSSelector`（L68-113）——tag + 合法类名（正则过滤任意类，L75-80）+ `SAFE_ATTRIBUTES` 白名单 24 属性（L43-66，含 data-testid/data-qa/data-cy 测试锚点）。

**录制控制**：`startRecorder`（L115-215）幂等启动 + 挂 8 监听器；`stopRecorder`（L217-237）停 rrweb + 卸监听。

**语义提取**：`extractSemanticInfo`（L240-554，315 行巨型函数）——radio/checkbox 走专门管线（L248-426）：option 文本四级策略（label[for] L258-264 → 父 label L267-272 → 前后兄弟短文本 L275-299 → value 属性 L302-308）、组名上溯找 fieldset legend 或通用 label（L316-347）、按 name 收集全组选项（L350-380），拼 `"Marital Status: Married"` 式 labelText（L384-390）；非 radio 走五级 label 瀑布（L427-517）。产出 12 字段 semanticInfo（L535-553）。

**事件处理器**：`handleCustomClick`（L557-645，含 `shouldSkipClickEvent` 三条过滤 L649-675 与 checkbox/radio checked 状态捕获 L603-619）；`handleInput`（L689-730，密码打码）；`handleSelectChange`（L734-782，含全选项列表）；`handleKeydown`（L803-859，12 键白名单 L787-801 + CmdOrCtrl 组合）。

**高亮 overlay**：mouseover 绿框（L867-931，zIndex 2147483000）+ focus 红框（L943-994，zIndex 2147483100 叠上层），`pointerEvents: "none"` 不挡交互。

**入口 `main`**（L1007-1074）：监听 `SET_RECORDING_STATUS` 同步开关（L1010-1018）、加载时主动 `REQUEST_RECORDING_STATUS` 对齐初始态（L1026-1046）、`beforeunload` 兜底清理（L1049-1062）。

## ③ 外部连接

- **下行（生产）**：五类消息发往 background.ts——RRWEB_EVENT 直接透传（L190）、CUSTOM_* 带语义 payload；background 把它们翻译成工作流步骤草稿，CUSTOM_SELECT_EVENT 在其 L516-518 注释标注"未来映射 SelectStep"。
- **上行（控制）**：background 广播 `SET_RECORDING_STATUS`（background.ts L201）切换录制；content script 注入时主动询问初始态（L1026）——解决"新开标签页/刷新后 content script 重生而 background 状态未变"的同步问题。
- **依赖**：`rrweb` + `@rrweb/types`（L1-2）、`chrome.runtime` 消息通道、WXT 的 `defineContentScript`（隐式全局）。
- **数据契约消费者**：payload 里的 xpath/cssSelector/semanticInfo 最终被 Python 端（healing 的 selector_generator/deterministic_converter）消费——`selector_strategies` 的生成源头就是这里的 element 数据。

## ④ 数据流

以"点击一个提交按钮"为例：

1. 捕获阶段 click 监听先于页面处理器触发（L206 capture=true），`handleCustomClick` 拿到 target。
2. `getXPath` 生成位置路径；`extractSemanticInfo` 提取 labelText（button 自身 textContent 优先，L431-441）。
3. `targetText` 组装（L569-589）：button 类优先 textContent→ariaLabel→value→title；其它元素 labelText→textContent→placeholder→ariaLabel→name→id。
4. `shouldSkipClickEvent` 过滤冗余（隐藏 radio 常与可见元素同时触发，L655）。
5. clickData 组包（L621-636）：timestamp + **双 URL**（`document.location.href` 主页面 vs `window.location.href` 所在 frame，L623-624）+ 双选择器 + elementState + semanticInfo + radioButtonInfo。
6. sendMessage 到 background，与并行 rrweb 增量流汇合。滚动事件特殊流水线（L126-187）：坐标取整（L135-139）→ 方向反转立即发（L148-167，改向是语义边界）→ 同向 500ms 防抖合并（L174-187）。rrweb 侧 `checkoutEveryNms: 10000 / checkoutEveryNth: 200`（L196-197）定期全量快照防增量漂移。

## ⑤ 设计决策与取舍

**双通道而非纯 rrweb**：rrweb 快照有 DOM 缺意图（不知道点的是"提交"还是"取消"）；纯自定义事件有意图缺页面演化。并行采集让 background 交叉对齐——语义事件定步骤，rrweb 流提供上下文与回放。代价是消息量翻倍与两流时序对齐问题。

**监听器 capture 阶段 + 永久挂载**（L206-213）：capture 先于页面 stopPropagation 保证不漏；录制开关只由 handler 内 `isRecordingActive` 判断（L558/L690 等）而非动态挂卸——避免状态切换瞬间丢事件，代价是非录制期也有少量调用开销。

**语义提取放在内容脚本而非 Python 端**：label 关联、radio 组结构是 **DOM 活体查询**（label[for]、closest('label')），离开页面上下文无法还原——提取必须现场做。315 行的 extractSemanticInfo 是对真实表单世界脏乱差的全面妥协。

**隐私双保险**：rrweb 层 `maskInputOptions: {password: true}`（L193-195）+ handleInput 手动替换 `"********"`（L715）——两条通道都不过密码明文。

**高亮 overlay 即建即毁**（L873-877）：每次 mouseover 移除旧 div 新建——实现简单、无位置残留，代价是高频鼠标移动下的 DOM churn（零交互干扰）。

## ⑥ 新人提示（坑/勘误）

1. **L202 赋错函数（真 bug）**：`(window as any).rrwebStop = stopRecorder`——把**模块自己的 stopRecorder 函数**挂上去，而 rrweb 返回的原生句柄是局部变量 `stopRecording`。外部调 `window.rrwebStop()` 实际走模块包装（多走日志与状态重置路径），rrweb 原生 stop 从未暴露。全仓无其它 rrwebStop 消费者，属潜伏笔误。
2. **L97 的 no-op 替换（真 bug）**：`attrValue.replace(/"/g, '"')` 把双引号替换成它自己——转义意图（应为 `\\"`）从未生效。靠 L98 兜底（含引号/空格值改用 `*=` 包含匹配）掩盖了语法断裂风险，但值含 `]` 或 `="` 时选择器仍可能失配。
3. **L394 向 DOM 元素挂 `_radioButtonInfo`**：把数据挂在元素实例上——SPA 复用 DOM 节点时旧 radio 信息可能残留到不相关元素（L533 读取时不校验新鲜度）。
4. **shouldSkipClickEvent 的 L667-672 与 L655 条件重叠**：第三条（display:none 且无 targetText 的 radio）几乎是第一条（不可见 radio）的子集——isElementVisible 查四个条件（L678-684），style.display 只是其一；三条过滤实为两条半。
5. **keydown 不捕 Alt/Shift 组合**：L822 注释自认"可按需扩展"——录制含 Alt 快捷键的工作流会静默丢步骤。
6. **getXPath 的 `id("xxx")` 函数式语法**（L14）不是通用 XPath：`document.evaluate` 支持，但 Python 端部分求值器不认 `id()` 函数——跨语言消费该 xpath 时注意转成 `//*[@id="xxx"]`。
7. **handleInput 每次击键都发事件**：没有防抖（对比滚动的 500ms）——input 一个 20 字词产生 20 条 CUSTOM_INPUT_EVENT，去重责任全在 background 端。
8. **beforeunload 清理在 bfcache 恢复时不重挂**（L1049-1062）：页面从 bfcache 恢复不触发重新注入，监听器已移除而 rrweb 句柄状态未知——移动端 Safari 录制断流排查从这里入手。
