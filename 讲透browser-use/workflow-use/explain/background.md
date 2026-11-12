# extension/src/entrypoints/background.ts — 浏览器录制后台：从用户操作到语义工作流

> 源文件：`extension/src/entrypoints/background.ts`（851 行）
> 勘误：任务书原路径 `extension/src/core/background.ts` 不存在，实际位于 `src/entrypoints/`（WXT 框架的标准后台入口）。

## 一、角色定位

这是 Chrome 扩展的 **service worker**（WXT `defineBackground` 包裹，L28），录制链路的浏览器端枢纽：内容脚本捕获的用户操作（点击/输入/按键/滚动/导航）与 rrweb DOM 快照事件在这里汇聚成步骤序列，实时转换为**语义工作流**（target_text 锚定），POST 给本机 Python 录制服务（`http://127.0.0.1:7331/event`，L41——接收端是 `recorder/service.py` 的 uvicorn，recorder/service.py:178）。它同时管理录制开关状态并向三类消费者广播：所有 tab 的内容脚本（SET_RECORDING_STATUS）、侧边面板 UI（recording_status_updated）、Python 服务器（RECORDING_STARTED/STOPPED/WORKFLOW_UPDATE）。

## 二、内部结构

- **三层内存态**（L29-39）：`sessionLogs: {tabId: StoredEvent[]}` 原始事件仓（L30）、`tabInfo` 补 URL/标题（L33）、`recentUserInteractions` 记录最后用户交互时间戳——导航过滤的依据（L36）。**没有持久化**（L800-801 注释掉了 storage 方案），service worker 被杀即丢数据。
- **状态开关**：`isRecordingEnabled = true`（L38，注意注释写"Default to disabled (OFF)"与代码相反，属过期注释）；`lastWorkflowHash` 做去重缓存（L39）。
- **工具函数**：`calculateSHA256`（L44，SubtleCrypto 摘要）、`sendEventToServer`（L56，fetch POST，失败仅 warn 不重试不缓冲，L63-68）、`generateStepDescription`（L72，六类步骤的描述文案，scroll 返回 null）。
- **转换核心**：`broadcastWorkflowDataUpdate`（L92）与 `convertStoredEventsToSteps`（L299）。
- **事件入口三组**：tab 生命周期监听（L251-293）、`chrome.runtime.onMessage` 统一消息路由（L532-798）、DEV 自动开侧栏（L816-850）。

## 三、外部连接

上游：内容脚本发来的 `CUSTOM_CLICK/INPUT/SELECT/KEY_EVENT` 与 `RRWEB_EVENT`（类型清单 L536-541）、侧栏的 `START/STOP_RECORDING`、`GET_RECORDING_DATA`、`ADD_EXTRACTION_STEP`（L661/647/706）、新 tab 的 `REQUEST_RECORDING_STATUS`（L783）。类型依赖 `../lib/types`、`../lib/workflow-types`、`../lib/message-bus-types`（L3-26）。下游：`chrome.tabs.captureVisibleTab` 截图（L618）、Python 录制服务（7331 端口，与仓内 `recorder/` 模块构成跨语言闭环）。

## 四、数据流

事件入库（`storeEvent` 闭包，L559）：校验 tabId → 填 tabInfo → 自定义事件刷新 `recentUserInteractions`（L574-577）→ **导航过滤**：rrweb 的 Meta/FullSnapshot 带 href 时，只有"会话首事件或从未交互过"才入库，交互后的导航一律过滤（注释：always filter post-interaction navigation，L585-602）——用户点按钮导致的跳转不该重复记录为 navigation 步骤。自定义事件先截图（jpeg quality 75，L618-621）再入库，截图失败降级入库（L627）。

事件→步骤（`convertStoredEventsToSteps`，L299）：click 事件四字段齐全才收（L307-312），**targetText 优先**；cssSelector 只在 radio/checkbox/`role="radio"`/`role="checkbox"`/button 这类复杂交互元素时附带（L329-337）——语义优先、选择器点穴的录制策略。input 事件支持合并：与上一步同 tab/URL/frameUrl/xpath/elementTag 即视为同一输入框的连续击键，只更新 value/时间戳/截图（L360-374），且拿到 targetText 后删除 cssSelector（L379）——这就是打字过程不爆炸成 N 步的原因。rrweb 只取 `IncrementalSource.Scroll`（L446-448，同 targetId 的连续滚动合并，L459-469）与 Meta/FullSnapshot 的导航；extract 步骤要求 url+extractionGoal（L499）。

步骤→工作流（`broadcastWorkflowDataUpdate`，L92）：跨 tab 汇总按时间排序（L94-99）→ 每步删除 7 个内部字段（timestamp/tabId/frameUrl/xpath/elementTag/elementText/screenshot，L114-120）→ **targetText 改名 target_text**（无则显式 null，L134-140）对齐 Python 端 schema → 产出双格式：`semanticWorkflowData` 发服务器、`uiWorkflowData` 留原字段给 UI（L149-166）→ SHA-256 对 allSteps 摘要，与 lastWorkflowHash 相同则跳过发送（L168-179）→ `WORKFLOW_UPDATE` 事件 POST（L183-188）。每次入库都触发一次全量重算（L240/L611）——录制期内是 O(N²) 的总工作量，靠 hash 去重挡住网络侧。

## 五、设计决策与取舍

- **录制端语义化前移**：target_text 在浏览器侧就定形（而非事后 Python 侧转换），并按元素类型有条件保留 cssSelector——复杂控件的选择器在语义执行器里有专门处理路径（radio 值匹配等），留着是给兜底的。
- **导航去重的交互时间戳法**（L585-602）简单有效：副作用跳转必然紧跟交互。缺陷是刷新（F5）也会被过滤——首事件豁免只保护第一次加载。
- **双格式输出**（L149-166）避免 UI 与服务器互相迁就：服务器要蛇形命名+瘦字段，UI 要原驼峰+截图，各自一份。
- **POST 即忘**（L56-69）：服务器不在线只 warn，事件不重放——录制数据仍在内存，下次任何事件触发时会带全量 WORKFLOW_UPDATE 补发，等效最终一致。
- **START_RECORDING 清空一切**（L664-670）：三张表全清，语义是"新会话"而非"继续"，也顺带废除了独立的 CLEAR_RECORDING_DATA 消息（L791 注释记录了这次删减）。
- **sync/async 消息通道纪律**：`isAsync` 标志位贯穿 onMessage（L533/660/774/797），异步 sendResponse 必须返回 true 保持通道——Chrome MV3 最常见的坑，这里处理得很规范。

## 六、新人提示（坑/勘误）

1. **注释与代码相反**：L38 注释"Default to disabled (OFF)"而初值是 `true`——背景脚本一加载就处于录制态（内容脚本注入后即可上报）。真实开关由侧栏 START/STOP 控制。
2. **无持久化**：MV3 service worker 随时可能被回收，长时间录制中途 worker 重启会丢 `sessionLogs`；L800-801 的 storage 方案被有意搁置。
3. `CUSTOM_SELECT_EVENT` 在 customEventTypes 清单里（L539）会入库，但 `convertStoredEventsToSteps` 没有对应 case（L515-517 注释承认 TODO）——下拉选择静默丢失，是已知缺口。
4. input 合并条件要求 frameUrl 严格相等（L365），跨 iframe 的同字段输入不会合并——行为正确但排查"为什么没合并"时先查 frameUrl。
5. 端口 7331 硬编码（L41）且为明文 HTTP localhost；Python 侧未启动时每个事件都会 console.warn 刷屏。
6. DEV 模式 onInstalled 自动开侧栏（L816-845）依赖 `chrome.sidePanel.open` 通常要求用户手势，注释自认"might fail"——生产路径走 action 图标点击开面板（L848-850）。
