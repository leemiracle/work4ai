# mac/actions.py —— 动作原子层：四个函数把意图砸进 AX API

## 一、角色定位

`mlx_use/mac/actions.py`（140 行）是最底层的执行原子库，只有四个模块级函数：`perform_action`（通用 AX 动作执行）、`click`（带白名单的按压）、`type_into`（设值+可选提交）、`right_click`/`scroll`（菜单与滚动）。它对上完全无知——不知道 Agent、不知道 LLM、不知道步骤——只认 `MacElementNode`（element.py 的 dataclass）和 macOS Accessibility API。Controller 的七个注册动作（controller/service.py:37-265）里凡是碰 UI 的，最终都坍缩到这四个函数上。

文件头第 1 行的 `# --- START OF FILE mac_use/mac/actions.py ---` 注释与 tree.py 头部的拼接残骸同源——它就是那次拼接导出事件中"被嵌进 tree.py"的那个文件的正文，只是自己的标记行没被删掉。

## 二、内部结构

**`perform_action(element, action)`（actions.py:19-41）**：唯一真正调 `AXUIElementPerformAction` 的地方（actions.py:32）。前置两道闸：`element._element`（原始 AXUIElement 引用）非空（actions.py:22-24），且 `action in element.actions`（actions.py:27-30）——`element.actions` 是 element.py 的 property，从 `attributes['actions']` 取，而该属性只有 tree.py:157-158 在动作列表非空时才写入。返回值判 `result == 0`（kAXErrorSuccess）。异常整体兜底返回 False，**这个库永不抛错，只说谎成功与否**。

**`click(element, action)`（actions.py:43-60）**：签名是**双参数**——element 之外还要指定用哪种 AX 动作来"点击"。三道闸：引用非空（actions.py:45-47）、`element.enabled`（actions.py:50-52）、动作在白名单 `['AXPress','AXClick','AXOpen','AXConfirm','AXShowMenu']`（actions.py:55-58），最后转调 `perform_action`（actions.py:60）。

**`type_into(element, text, submit=False)`（actions.py:62-99）**：先建 `NSString`（actions.py:75），`AXUIElementSetAttributeValue` 直接写 `kAXValueAttribute`（actions.py:76）。submit=True 时查 `element.actions` 走提交链：优先 `AXConfirm`，退化 `AXPress`（actions.py:85-93），都没有则报错。

**`right_click(element)`（actions.py:101-117）**：有 `AXShowMenu` 就执行它（actions.py:113-114）；否则回退普通 `click(element)`（actions.py:117）——见坑 2。

**`scroll(element, direction)`（actions.py:119-140）**：方向映射表 left/right/up/down → `AXScrollXxxByPage`（actions.py:124-129），仅支持按页滚动，目标元素 actions 里要有对应滚动动作（actions.py:136-137）。

## 三、外部连接

- **controller/service.py**：`click/type_into/right_click/scroll` 四个直接 import（controller/service.py:21），七个注册动作中四个 UI 动作全部下沉到这里。
- **context.py**：import 了 `click/type_into`（context.py:24）但调用签名错误（见坑 2），且该模块本身不可导入。
- **element.py**：强耦合的三件 property——`actions`/`enabled`/`_element`。`enabled` 的缺省是 True（element.py `attributes.get('enabled', True)`），tree.py:178-180 只有在 `AXEnabled` 属性存在时才写入真实值——**"没查到"和"确实启用"在下游不可区分**。
- **tree.py**：`_element` 与 `actions` 两个属性的供给方（tree.py:154,157-158）；tree.py 头部还嵌着本文件的拼接副本。

## 四、数据流

一次点击的完整旅程：LLM 输出 `{"click_element": {"index": 17, "action": "AXPress"}}` → Controller 闭包查 `_element_cache[17]` 得 `MacElementNode`（controller/service.py:83-84）→ enabled 检查（controller/service.py:86）→ `click(node, 'AXPress')` → 白名单 → `perform_action` → `AXUIElementPerformAction(node._element, 'AXPress')`（actions.py:32）→ AXError 0/非0 → bool 一路向上折返回 `ActionResult`。注意 `action` 参数的语义链：tree 阶段 `AXUIElementCopyActionNames` 采集每个元素的动作列表进 prompt（element.py 序列化时 `actions="AXPress"` 展示），LLM 看着清单挑动作名传回来——**模型的"选择"被限制在元素真实支持的动作集合内**，这是 prompt 与动作层之间最精巧的闭环（prompts.py:62 明确教了这条规则）。

## 五、设计决策与取舍

- **`type_into` 是"设值"不是"打字"**：`AXUIElementSetAttributeValue` 直接改 value 属性，不产生键盘事件。对 Notes 的文本框这通常够用；但对依赖 keydown/keydown 监听、自动补全、输入法组合态的控件（浏览器页面、终端模拟器、代码编辑器），值会"凭空出现"而应用毫无反应。这是速度（一次调用 vs 逐键 CGEvent）换语义保真度的典型取舍——真要模拟键盘得走 Quartz CGEventTap，本仓库没做。
- **错误即 False 的谎言协议**：所有函数 catch-all 返回 False，上层只能看到"失败"看不到"为什么"。Controller 层再包一层 try/except 转成 `ActionResult(error=...)`，最终模型收到的是布尔语义+固定文案。调试体验差，但保证了 agent 循环永不被底层异常打断——与 agent/service.py 的容错哲学一致。
- **双闸 enabled 检查**：actions.py:50-52 与 controller/service.py:86 各查一次 `element.enabled`——防御性重复，成本为零（同一个 property 读同一个 dict）。

## 六、新人提示（坑与勘误）

1. **`click` 的 action 参数，全仓三处调用缺参**：正确用法只有 controller/service.py:91 的 `click(element_to_click, action)`。错误三连：① actions.py:117（right_click 的回退分支 `click(element)`——**库内部自踩**，一旦走到回退路径就是 TypeError，且被 perform_action 之外的调用栈直接抛出）；② context.py:158（死模块里的死调用）；③ examples/basic_agent.py:206（早期手写 agent 的活化石调用）。根因是 `click` 后来加了 `action` 参数，调用方没同步。
2. **死导入两个**（actions.py:10-11）：`kAXConfirmAction` 与 `AXUIElementCopyActionNames` 进了 import 却从未使用——代码里提交用字符串 `'AXConfirm'`（actions.py:88），动作名采集在 tree.py 而非此处。pyobjc 导入无副作用，纯粹是噪音。
3. **right_click 的回退是自爆路径**：actions.py:116-117 的意图是"没有菜单动作就当普通点击"，但如坑 1 所述单参调用必炸——且 `perform_action` 不包这层，异常会穿透到 Controller 的 try（controller/service.py:106-109）变成泛化 error 文案，真实原因被吞。
4. **白名单与交互集不对称**：click 白名单含 `AXClick`/`AXOpen`（actions.py:55），但 tree.py:56-65 的 `INTERACTIVE_ACTIONS` 不含它们——意味着支持 AXClick/AXOpen 的元素可能根本没被编号进交互列表，白名单里的这两个动作实际无从触发。
5. **`NSString.stringWithString_(text)`**（actions.py:75）：pyobjc 通常能自动桥接 Python str，显式包 NSString 是防御写法，无害但说明作者遇到过桥接边界问题（含 NUL 字符或非 UTF-8 序列的文本）。
6. **本文件也是拼接受害者兼加害者**：自己的标记注释没删（actions.py:1），同时自己的头部副本被嵌在 tree.py:4-15——读 tree.py 时看到的 `import Cocoa`/`NSString` 那段，就是从这里复印的。

（行号锚：actions.py:1,10-11,19-41,22-24,27-30,32,43-60,45-52,55-58,60,62-99,75,76,85-93,88,101-117,113-117,119-140,124-129,136-137；controller/service.py:21,37-265,83-84,86,91,106-109；context.py:24,158；tree.py:56-65,154,157-158,178-180；examples/basic_agent.py:206；prompts.py:62）
