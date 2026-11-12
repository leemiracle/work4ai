# snapshot.js — 注入页面的原子 DOM 快照 IIFE：稳定节点身份、动作枚举、双层新鲜度指纹

## 一、角色定位

snapshot.js 是一个 107 行的 IIFE，被 browser.py 在 import 时整体读成字符串（browser.py:13），随后以 `Runtime.evaluate` 注入目标页面执行——它是"观察"这个动词的全部实现。browser.py:12 的注释点题：**原子地读取可见内容与控件，并保留真实 DOM 节点身份**。它在架构中位于数据链最底端：页面 DOM →（本脚本）→ 结构化观察字典 →（model.action_space）→ 元素表 →（TypeSafe）→ 决策。"模型只能从被观测枚举里选"的安全模型根基就在这里——没有 selector 直通车，只有脚本分配的整数节点 ID。

## 二、内部结构

**缓存与节点身份（snapshot.js:2-8）**。入口先判 `document.body`，导航间隙返回 null（snapshot.js:2，browser.py:189-190 将其转成 StalePage）。核心是 `window.__jevFast` 缓存（snapshot.js:3）：`ids` 是 element→id 的 **WeakMap**（节点被 GC 自动消失），`nodes` 是 id→element 的 Map（执行时按 id 取回活引用），`next` 是递增计数器。identity()（snapshot.js:4-7）给每个元素分配单调递增 ID——**ID 由代码拥有、随 WeakMap 生命周期存续，不是 CDP backendNodeId**（docs/design.md 明确勘误过）。每次快照先剪掉已断连引用（snapshot.js:8）；导航即换新 window，缓存自然重置。

**过滤谓词（snapshot.js:9-11）**。safe 排除 password/file/hidden 三种 input（snapshot.js:9，密码值永不上报，scripts/check_guards.py:107 有断言）；visible 要求无 aria-hidden/inert 祖先且通过 checkVisibility（含透明度与 visibility CSS，snapshot.js:10-11）。

**可访问名 name()（snapshot.js:12-23）**。一条 `||` 短路链实现降级命名：aria-labelledby 引用（递归、seen 防环）→ aria-label → label 元素文本 → button/submit/reset 的 value → alt → 非 INPUT 的子文本节点拼接（跳过 aria-hidden 子树）→ title → placeholder。这不是完整 accessible-name 规范（design.md 如实承认），但覆盖常见 HTML/ARIA。

**角色与选择器（snapshot.js:24-27、28-43）**。14 个 ARIA 角色白名单（button/link/checkbox/radio/switch/tab/menuitem/menuitemradio/option/gridcell/combobox/textbox/searchbox/spinbutton，snapshot.js:24-25）；selector 串是这些 `[role=...]` 加上 `a[href],button,input,textarea,select,summary,[contenteditable="true"]`（snapshot.js:26-27）。role()（snapshot.js:28-43）先认显式 role，再按标签映射：BUTTON/SUMMARY→button、A→link、SELECT→combobox、TEXTAREA/可编辑→textbox；INPUT 按类型细分（checkbox/radio 原样、button/submit/reset/image→button、search→searchbox、number→spinbutton、text/email/url/tel→textbox），其余 null 出局。

**两套指纹（snapshot.js:44-54）**。pageKey()（snapshot.js:44-46）返回七元组：timeOrigin/URL/scroll/视口四值外加**全部安全表单域的状态数组**（[identity,value,checked,selectedIndex,disabled,readOnly]）。guard()（snapshot.js:47-54）是单元素指纹：未连接或不可见返回 null；scope 取最近的 form/dialog/article/li/tr 等容器（snapshot.js:49），返回 13 元组（identity/role/name/value/checked/selectedIndex/readOnly/disabled/aria 三态/selected/href）加 **scope.innerText 截断 6000 字符**——"目标 + 近邻上下文"的语义画像。两套指纹分别服务 browser.fresh 的 click/select 专用档（browser.py:93-97）。

**动作枚举（snapshot.js:55-81）**。遍历 selector 命中元素，过滤 safe/visible/非 disabled/无 aria-disabled 祖先（snapshot.js:57）；矩形有尺寸且中心在视口内才入选（snapshot.js:58-59）——**屏外元素不进动作空间**；内含按钮的 gridcell 跳过避免双计（snapshot.js:60）。base 条目携带 node/role/label/rect（snapshot.js:61-62），aria 的 checked/selected/expanded 与 checkbox/radio 真实状态并入（snapshot.js:63-67）。分叉：SELECT 为每个未选中且未禁用的 option 生成一条 select 动作，label 是"字段 → 选项"复合形式并记录 current_value（snapshot.js:68-71）；其余元素先判 editable（非只读且角色是 textbox/searchbox/spinbutton，或 INPUT/TEXTAREA 型 combobox，snapshot.js:73-75），可编辑的产出 fill + click **成对动作**（click 冠"Open"前缀，用于唤起日历/建议列表，snapshot.js:78-79）。value 提取规则在 snapshot.js:76-77。

**可见文本采集（snapshot.js:82-92）**。TreeWalker 遍历文本节点，总长封顶 6000；跳过 script/style/noscript/template 与不可见父级（snapshot.js:86）；Range.getBoundingClientRect 逐节点判可见（snapshot.js:87-88）——**发给模型的是视口内真实可见的文本**，屏外正文与页脚不占上下文。

**汇总与截断（snapshot.js:93-106）**。先对全部动作节点算 guards（snapshot.js:94）、生成去 rect 的 semantics（snapshot.js:95-96），组成 marker 十元组：timeOrigin/URL/滚动/视口/标题/正文/动作语义/**page_key[6] 即表单状态数组**（snapshot.js:97-98）；**然后**才把 actions 截到 250 条（snapshot.js:99-100）、按序编 `e1..eN`（snapshot.js:101），被截数量记入 omitted_actions。尾部按滚动位置追加 scroll_down/scroll_up（±560px，snapshot.js:102-103）与 wait（snapshot.js:104）。返回 url/title/w/h/text/scroll/actions/marker/page_key/guards/omitted_actions（snapshot.js:105-106）。

## 三、外部连接

单向被消费：browser.py:13 读文件为 READ_STATE；browser.py:14 的 MARKER 把它包一层只取 marker；browser.py:51 的稳定等待脚本访问 `__jevFast.nodes`；browser.py:94-95 的 fresh 专用档调 `pageKey()/guard()`；browser.py:145 的执行解析同样经 `nodes.get(id)` 取回真实节点。scripts/check_guards.py 用真浏览器回归其判定；`node --check jev_ultrafast/snapshot.js` 是 README 开发命令之一。

## 四、数据流

进：无参数——纯读当前 document 与 window 缓存，零网络。出：单个可 JSON 化对象（经 CDP returnByValue 回传）。两条关键通道：① 节点身份——node 整数 ID 随 actions 下发，Python 侧原样带回，经 Map 取回 DOM 引用，"所点即所见"；② 指纹——marker（全量语义）与 page_key/guards（定向）随观察返回，供 fresh 比对。JSON 序列化会把 guards 数字键变字符串，browser.py:97 因此用 `str(node)` 对齐。

## 五、设计决策与取舍

1. **WeakMap+Map 双结构**：ids 弱引用不阻止 GC，nodes 强引用保证可执行性，配 L8 剪枝，身份生命周期与文档一致。2. **语义先于几何**：快照只记语义（rect 仅展示用），几何永远在输入前一刻解析（browser.py:149），动画位移无需重新预测。3. **截断顺序有讲究**：guards/semantics/marker 在截到 250 **之前**计算——新鲜度比对覆盖全部候选，被截断的候选本就不可选，两边自洽。4. **fill/click 成对暴露**："打开日历/建议"与"输入文本"各自成可选项，供策略层（questions.py:6 的三步日期规则）执行。5. **不做完整 accessible-name 算法**：承认边界（shadow DOM/frames/canvas 均不支持），换取 107 行可审计性。

## 六、新人提示

- 节点 ID 是**每文档**的：导航后重置，替换元素（outerHTML 重建）拿到新 ID——fresh 专用档因此必判 stale（check_guards.py:41 的"replaced node"用例）。
- 脚本每次执行都重跑整个枚举（MARKER 档也一样），"廉价 fresh"只是省了 Python 侧的对象组装，DOM 遍历成本仍在。
- password 在 safe 谓词出局（snapshot.js:9），但 combobox 型 input 的 innerText 会被采集（snapshot.js:77）——敏感内容若在可见文本里仍进上下文；scroll 动作按滚动位置条件生成（scrollY>0 才有 scroll_up），别假设上下滚恒在。
- marker 含表单状态数组（page_key[6]），**用户手敲一个字符都会让终态判定 stale**——这是 DONE 前必复查新鲜度的原因之一（agent.py:94）。
- 图谱 hub 对本文件"稳定递增 id、select 按未选项展开、双层指纹"的概括与源码一致；核对无出入。
