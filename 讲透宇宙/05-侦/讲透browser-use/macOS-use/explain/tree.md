# mac/tree.py —— AX 树构建器：整个系统的感知层

## 一、角色定位

`mlx_use/mac/tree.py` 的 `MacUITreeBuilder` 是 macOS-use 的眼睛。每个 agent step，`Agent` 拿着上一步的 pid 调 `build_tree(pid)`（agent/service.py:205），它通过 macOS Accessibility API 把目标 App 的主窗口递归展开成一棵 `MacElementNode` 树，并做三件关键的事：给可交互元素编号（`highlight_index`）、把编号到节点的映射存进 `_element_cache`（动作寻址的地址簿）、把上下文文本节点也标记出来。没有这个文件，"LLM 看到的世界"和"Controller 点击的对象"就无法对接。

它也是考古信息最密的文件：文件头嵌着上游拼接残骸，中部有永假比较，observer 被 stub 成恒真——层层都是演化化石。

## 二、内部结构

**文件头的拼接残留（tree.py:1-41）**：第 1 行是 `# --- START OF FILE mac_use/mac/tree.py ---`，第 4 行又出现 `# --- START OF FILE mac_use/mac/actions.py ---`——某次"多文件拼接导出"的产物被整段粘成了 tree.py 的开头。于是前 41 行里有：actions.py 的全套 import（tree.py:5-15）、重复的 `import Cocoa`（tree.py:8,16）、两个 `logger = logging.getLogger(__name__)`（tree.py:14,41）、然后才是 tree.py 本体的 import（tree.py:18-39）。功能上无害，但 `asyncio`（tree.py:2）、`objc`（tree.py:17）、`AXError` 等（tree.py:19-29）与 CFRunLoop 三件套（tree.py:37）在本文件内均无消费者。

**常量与状态（`__init__`，tree.py:46-73）**：`max_depth=30`/`max_children=250` 双限幅；`INTERACTIVE_ACTIONS`（tree.py:56-65，AXPress/AXShowMenu/AXIncrement/AXDecrement/AXConfirm/AXCancel/AXRaise/AXSetValue）与 `SCROLL_ACTIONS`（tree.py:68-73）两套动作白名单——这是"什么算可交互"的权威定义。

**属性读取 `_get_attribute`（tree.py:79-93）**：三参 `AXUIElementCopyAttributeValue(element, attribute, None)`，error 分流：`kAXErrorSuccess` 返回值、`kAXErrorAttributeUnsupported` 静默 None、其他错误也 None（注释掉的 debug 日志说明作者刻意降噪）。`_get_actions`（tree.py:95-105）用 `AXUIElementCopyActionNames` 取元素支持的动作列表。

**交互判定 `_is_interactive`（tree.py:107-126）**：有动作才有资格；`AXTextField` 要 AXSetValue 且 `AXEnabled` 为真（tree.py:117-119）；`AXButton/AXLink` 要 AXPress 且启用（tree.py:122-124）；其余命中两套白名单即算（tree.py:126）。

**递归核心 `_process_element`（tree.py:128-227）**：先 `str(element)` 做去重键查 `_processed_elements`（tree.py:130-135，防 AX 共享子树死循环）；取 role/actions，建 `MacElementNode` 并把原始 AXUIElement 引用挂到 `node._element`（tree.py:154）；采集 title/value/description/enabled/position/size/subrole 七类属性（tree.py:161-186）；算 `is_context`（AXStaticText/只读 AXTextField 且父级可见，tree.py:189-191）；可交互的领号进 cache（tree.py:196-199），上下文元素进 `ctx_` 前缀键（tree.py:200-203）；最后递归子元素，深度与宽度超限只记 error 不中断（tree.py:206-221）。

**生命周期（tree.py:229-256）**：`cleanup` 清 cache/processed/pid 并强排 gc；`reset_state` 是 cleanup 的温和版。

**入口 `build_tree（tree.py:258-353）**：清缓存 → pid 空则抛 ValueError（tree.py:266-268，agent 首步的"还没开 App"信号）→ `ps -p` 验活（tree.py:276-284）→ observer stub（见坑 3）→ `AXUIElementCreateApplication` 建 app 引用（tree.py:291）→ 读 role 测权限（`kAXErrorAPIDisabled` 提示开辅助功能，tree.py:294-300；-25204 连接失效则清 pid，tree.py:301-306）→ 建 root、取主窗口（`kAXMainWindowAttribute`，tree.py:319），失败降级取 `AXWindows[0]`（tree.py:322-336）→ 主窗口节点挂到 root（tree.py:338-342）。

## 三、外部连接

- **agent/service.py**：唯一消费者，每步 build_tree + 序列化进 prompt（序列化在 element.py）。
- **controller/service.py**：动作执行时按 int index 查 `_element_cache`（controller/service.py:54/83/119/148）——cache 是树与动作层的接头。
- **element.py**：`MacElementNode` 定义 + `get_clickable_elements_string`（`[index][:]<role attrs> [interactive]` 格式）。

## 四、数据流

`pid → AXUIElementCreateApplication → app_ref → (权限探测) → main_window_ref → _process_element 递归 → root 树`。递归产出双通道：树本体（序列化进 prompt）与 `_element_cache`（int→node，动作层寻址）。**编号从 0 重新起算**（tree.py:264），prompt 里的 `[17]` 只在"本轮刚建的这棵树"内有效——这解释了为什么 Agent 必须每步重建树，也是动态 UI 场景下模型用错旧 index 的根因。

## 五、设计决策与取舍

- **每步全量重建 vs 增量**：`_processed_elements`/`reset_state` 的存在说明曾有复用树的想法，但 build_tree 开头无条件清空（tree.py:262-264）宣判了轮询制的胜利——正确性优先，AX 遍历本就是毫秒级。
- **`str(element)` 当元素标识**（tree.py:130）：pyobjc repr 含对象地址，去重效果依赖 repr 稳定性；至少防住了真正的环。
- **双限幅 + 只警告**：max_children 超限仍处理前 250 个（tree.py:213），"Some elements will not be processed" 日志是排查"元素找不到"的第一现场。
- **主窗口单窗口假设**：无主窗口时取窗口列表第一个（tree.py:329），多窗口 App 的其余窗口全部不可见。

## 六、新人提示（坑与勘误）

1. **永假比较 + 元组返回（tree.py:320-321）**：`error, main_window_ref = AXUIElementCopyAttributeValue(...)` 之后 `if error == '-25212': return None, "Window not found"`。`error` 是 AXError 整数，与字符串 `'-25212'` 比较恒为 False——该分支永不触发，是死代码；但一旦有人"修好"比较（改成 `error == -25212`），`return None, "Window not found"` 会返回元组，调用方 `root.get_clickable_elements_string()`（agent/service.py:207）立刻 AttributeError。**两层 bug 叠加，修复时必须一起改**。有趣的呼应：prompts.py:82 明明教了模型"遇到 -25212 就重新 open_app"——说明这个错误码真实出现过，prompt 记住了教训，代码分支却从未生效。
2. **observer 是恒真 stub（tree.py:75-77）**：`_setup_observer` 只 `return True`，`_observers` 字典（tree.py:49）从未写入，tree.py:37 的 CFRunLoop 导入随之死亡。感知模型已从事件驱动降级为轮询，函数壳留着只是不想改调用点（tree.py:286）。
3. **`is_visible` 语义污染（tree.py:178-180）**：`node.is_visible = bool(is_enabled)`——把"是否启用"写进"是否可见"字段。element.py 里两个字段并存展示，读树代码时极易被骗：此仓库中 is_visible 实际承载的是 enabled 语义。
4. **`_element_cache` 是混类型字典**：int 键（可交互元素）与 `'ctx_' + repr` 字符串键（上下文元素）共居一 dict（tree.py:198,202）。动作层 `index in cache` 的 int 查询天然不会撞到 ctx 键，但任何"遍历 cache"的代码都要先做键类型分诊。
5. **`ps -p` 阻塞事件循环（tree.py:275-277）**：`subprocess.run` 是同步调用，在 async build_tree 里每步执行一次——小停顿，但严格的 asyncio 项目里这是反模式。
6. **权限错误是运行时第一坑**：`kAXErrorAPIDisabled`（tree.py:299-300）对应"系统设置里没给辅助功能权限"，几乎每个新环境第一次跑都会撞；返回 None 后 agent 端表现为 state 永远是开场白。
7. **上游包名化石**：头部注释 `mac_use/...`（tree.py:1,4）与 import `mlx_use.mac.element`（tree.py:39）并存——重命名迁移只改了 import，注释原样保留。

（行号锚：tree.py:1-4,14-41,46-73,75-77,79-105,107-126,128-227,229-256,258-353,294-306,320-321；agent/service.py:205,207；controller/service.py:54,83,119,148；prompts.py:82）
