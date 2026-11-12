# browser.py — 单一 CDP 会话的浏览器控制：原子观察、新鲜度守卫、几何执行

## 一、角色定位

browser.py 是 agent 与真实 Chrome 之间的唯一通道，docstring（browser.py:1）点明两大主张：观察/执行都走 **one CDP session**（不每步起子进程），动作只作用于**被观测到的节点**。它下层依赖 browser-harness 的 `ensure_daemon` 与 `cdp`（browser.py:9-10），上层被 agent.py 持有（agent.py:19）。文件内嵌 snapshot.js 全文作为注入脚本（browser.py:13），把"读页面"变成一次 `Runtime.evaluate` 的原子操作——README 的"One browser call per snapshot"实现在此，实测 CDP 调用从 1092 降到 101（docs/performance.md）。

## 二、内部结构

**模块级常量（browser.py:13-14）**：READ_STATE 在 import 时就把同目录 snapshot.js 读成字符串；MARKER 则把整个 IIFE 再包一层只取 `.marker` 的新 IIFE——意味着"查新鲜度"其实是**重跑完整快照再比对语义指纹**，不是廉价读取。**StalePage（browser.py:16-17）**：ValueError 子类，语义是"这条决策已不再指向被观察的那页"。

**Browser 类（browser.py:20-112）**：

- `__init__`（browser.py:21-33）：ensure_daemon 拉起 harness 守护进程 → `Target.createTarget` 开后台标签页 → `attachToTarget(flatten=True)` 拿会话 ID → 固定视口 1120×780（browser.py:25）→ **焦点仿真**（browser.py:27，让后台标签页的 rAF/动画不被节流，又不抢占用户正在看的标签）→ 导航目标 URL → 15 秒 deadline 轮询 `document.readyState`（20ms 间隔，browser.py:29-33）。
- `evaluate`（browser.py:38-42）：对 exceptionDetails 一律转 StalePage——文档在求值期间被导航销毁是最常见的失效方式。
- `observe`（browser.py:44-86）：分两段。第一段处理 `after_input`（browser.py:45-76）：若上一步是 click/fill，先注入一段 Promise 等页面"稳定"——普通交互等 2 个 rAF 或最多 50ms，combobox 等可见的 autocomplete option、上限 200ms（browser.py:53-67）；这样下次观察时建议项已经出现，不用为此多花一次预测。此段只读且发生在动作已记账之后，被导航打断也只静默放过（browser.py:47、75-76）。第二段是正式观察（browser.py:77-85）：调 browser_operation 的 observe 分支，遇 StalePage 最多重试 10 次、每次 20ms，仍失败抛"Page did not settle"。
- `fresh`（browser.py:88-98）：**双档新鲜度**。click/select 动作走专用守卫——取 `window.__jevFast` 的 pageKey() 与 guard(node) 二元组，与观察时记录的 page_key/guards 比对（browser.py:93-97，guards 键是 str(node) 因为 JSON 序列化把数字键转成了字符串）；其余（DONE 判定、fill 前置等）走 MARKER 全量语义比对（browser.py:98）。`type(node) is not int` 同时挡掉了 bool（browser.py:91-92）。
- `act`（browser.py:100-107）：执行前再过一次 fresh（含文本生成之后的复查，见 agent.py:116 注释），wait 动作睡 100ms（browser.py:103-104），然后委托 browser_operation，并把非 wait 动作记入 after_input 供下次 observe 做稳定等待（browser.py:106）。
- `close`（browser.py:109-112）：关标签页并置空 target。

**模块级 fingerprint（browser.py:115-117）**：对 url/text/actions/scroll 四键做 sha256（json sort_keys 保证稳定序），刻意排除 screenshot——纯视觉变化不算页面变化（tests/test_agent.py:270-276 锁定）。

**browser_operation（browser.py:120-194）**——观察与执行的原子原语：

- observe 分支尾部（browser.py:188-194）：一次 evaluate 执行 READ_STATE 全文得 info；info 为 None 说明正在导航，抛 StalePage；算 fingerprint；可选截 jpeg quality=72（browser.py:193）。
- act 分支（browser.py:135-186）：scroll 用 `Input.dispatchMouseEvent(mouseWheel)` 派发固定点 (550,650) 的滚轮（browser.py:138-139）；wait 直接跳过返回。click/fill/select 共用一段目标解析 JS（browser.py:144-160）：节点必须是 int 型观测 ID（browser.py:141-142，注释强调"never model-generated selectors"），再过**六重执行前校验**——isConnected、非 disabled/aria-disabled/inert、checkVisibility（含透明度）、fill 目标非只读、几何在视口内、`elementFromPoint` 命中测试确认未被遮挡（browser.py:146-151）。select 在此直接设值并派发 input+change 事件（browser.py:152-158）。校验不过时分两类报错：select 抛 RuntimeError（可能已部分生效，禁止重试，browser.py:130-131、162-163），其余抛 StalePage 让上层重观察（browser.py:164）。click 在元素**当前几何中心**合成 mousePressed/mouseReleased（browser.py:165-168）——动画位移后的按钮照样点得到，scripts/check_guards.py:24 的"moving target"断言验证的就是这一点。fill 先合成 ctrl/meta+A 全选（darwin 用 modifiers=4，其余 2，browser.py:170-184），再 `Input.insertText` 插入文本（browser.py:185），语义是"整体替换"而非追加。

## 三、外部连接

import 只有四个：hashlib/json/sys/time 标准库加 browser_harness 的 admin 与 helpers（browser.py:3-10）。被 agent.py:7 导入（Browser、StalePage 两名）；`__init__.py:4` re-export Browser；tests/test_agent.py:12 导入 StalePage/browser_operation/fingerprint 做离线契约测试；scripts/check_guards.py:5 用真浏览器（data: URL 本地页面）回归 fresh() 的 9 类 DOM 突变判定。snapshot.js 虽是独立文件，运行时以字符串形态内嵌于本文件（browser.py:13、144-160、188），window.__jevFast 缓存由它建立。

## 四、数据流

进：URL 字符串（构造）；act 的动作对象（snapshot.js 产出的 {id,kind,node,label,value...}）与可选 text。出：observe 返回完整观察字典——url/title/w/h/text/scroll/actions(≤250条)/marker/page_key/guards/omitted_actions/fingerprint/screenshot(base64)。actions 里每个元素的 node 字段是页内 WeakMap 分配的稳定整数 ID，act 就拿这个 ID 从 `__jevFast.nodes` Map 取回真实 DOM 节点（browser.py:145）。marker 与 page_key/guards 是两套指纹：前者全量语义（url/滚动/视口/标题/正文/动作语义/表单值），后者供 click/select 的廉价定向复查。

## 五、设计决策与取舍

1. **语义新鲜度优于 DOM 变异计数**：不订阅 MutationObserver，而是比对"意义"（值/状态/标签/近邻上下文）；无关的屏外文本或视觉动画不会误触发重预测（check_guards.py:29-31 验证）。2. **几何永远在输入前一刻解析**：快照里的 rect 只用于展示，点击坐标执行时现算（browser.py:149），把动画问题从"重新预测"降级为"重取坐标"。3. **变异绝不重试**：select 中断抛 RuntimeError 而非 StalePage（browser.py:130-131），因为 change 事件可能已触发，重试等于二次变更。4. **观察与执行共用一个原子原语**：browser_operation 一个函数两分支，保证"读"与"写"对文档状态的假设一致。5. **焦点仿真而非切前台**（browser.py:27）：后台标签页保持渲染能力又不打扰用户，代价是隐式依赖 CDP 的 emulation 支持。6. **稳定等待只在交互后做且严格限幅**（50/200ms），用极小的确定性延迟换取"下一次观察就有建议项"，避免为等待单花一次模型调用。

## 六、新人提示

- MARKER 检查不是轻量操作：它重跑整个 snapshot IIFE，只是丢弃除 marker 外的全部产出；不要在热路径滥用 fresh() 的无动作档。
- guards 的键是字符串数字（`str(node)`，browser.py:97），而 snapshot.js 里 guards 是数字键（snapshot.js:94）——JSON 序列化改键型，比对两侧必须显式对齐。
- observe 的 10 次重试只捕 StalePage；RuntimeError 会立即上抛，这是"中断的 select 不可重试"在观察层的对应物。
- evaluate 对所有 exceptionDetails 一律报"Document changed during evaluation"（browser.py:40-41），但异常原因未必是导航——把它理解为"求值失败=页面可能变了"的保守策略即可。
- 截图默认 quality=72 jpeg（browser.py:193），库调用默认不开截图（agent.py:21 只有 record_dir 或显式 screenshots=True 才开）。
- 图谱 hub 对本文件"单一 CDP 会话、原子观察、combo 等待、六重校验"的概括与源码一致；核对无出入。
