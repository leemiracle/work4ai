# examples/basic_agent.py 精讲——框架诞生前的手搓原型：三个运行时缺陷与 AI Studio 复制考古

## 一、角色定位

`examples/basic_agent.py`（250 行）是仓里**信息密度最高的示例**，也是最诚实的考古现场：它完全绕过 `mlx_use.Agent`/`Controller`/`Registry` 框架，手搓了一个最小 agent 循环——启动 Notes 应用 → `MacUITreeBuilder` 采 UI 树 → 拼自然语言 prompt → `llm.invoke` → `json.loads` 解析动作 → 直调 `click`/`type_into` 执行。这基本就是本项目的"创世代码"：框架层的每一步（消息管理、结构化输出校验、动作注册）都能在这里找到未抽象的前身。目标也带着作者指纹——在备忘录里创建名为 **'Ofir folder'** 的文件夹。

但它是**三处带伤出厂**的代码：一个 import 期就炸的未定义变量、一个传给 `build_tree` 的不存在的参数、一个少传必需参数的 `click` 调用。作为"跑不起来的示例"，它反而精确标注了底层 API 演进的时间差——示例写于旧接口时代，接口后来变了，示例没人回头修。

## 二、内部结构

**头部（L1-17）**：L1 的 `# --- START OF FILE examples/basic_agent.py ---` 是工具拼接文件的边界标记（同款标记在 `print_app_tree.py` L1-2 出现且文件名误写，见第六节）；L6 `import Cocoa` 直连 pyobjc；L7-8 构造 Gemini 客户端；L10-11 从 mlx_use 只取三个原语——`click`/`type_into`/`MacUITreeBuilder`，零框架依赖。**L17 是第一颗雷**：`ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(GEMINI_API_KEY))`——`GEMINI_API_KEY` 在全文件无定义无导入（L16 注释只说 "Replace with your actual Gemini API key"，却没给赋值语句），**模块加载即 NameError**，后面 233 行代码实际永远执行不到。

**等待就绪（L25-46）**：`wait_for_app_ready` 轮询激活应用——L35 `app.activateWithOptions_(Cocoa.NSApplicationActivateIgnoringOtherApps)` 是 pyobjc 经典调用；L29-33 的 `if not app: continue` 与 L34 的 `if app:` 互补成一对（走到 L34 时必为真），逻辑冗余但无害。

**手搓状态机（L49-72）**：`FolderCreationState` 三态机——未点 New Folder / 已点未输入 / 已输入。`get_context`（L55-61）按状态生成给 LLM 的阶段提示（"去找 New Folder 按钮"/"文本框已出现，输入文件夹名"）；`update`（L63-72）按动作名+元素信息推进状态。注意 L70 判定的动作名是 `'type'`，而底层函数名是 `type_into`——LLM 协议名与实现名是两套词汇，靠 prompt 约定对齐。

**主循环（L75-246）**：启动应用（L77-81 `NSWorkspace.launchApplication_`）→ 按 bundle id `com.apple.Notes` 扫 runningApplications 找 PID（L88-96）→ 等就绪 → 10 步循环（L108-110）：**L116 是第二颗雷**——`builder.build_tree(notes_app.processIdentifier(), notification_callback=notification_handler)`，而 `build_tree` 真实签名是 `(self, pid: Optional[int] = None)`（tree.py L258），**TypeError**；L20-22 的 `notification_handler` 属于更早的接口版本。拿树后 `get_clickable_elements_string()`（L122）转可交互元素清单；L125 注入状态机上下文；L127-184 是 57 行内嵌 prompt——教模型 click/type 两动作、JSON 响应格式，内嵌 UI 树。**L186 `llm.invoke(prompt)`** 纯同步；L193-195 手工剥 markdown 围栏——正是框架层 `AgentOutput` 结构化输出要解决的痛点；L197 `json.loads`；L202-220 分派——**L206 是第三颗雷**：`click(element_to_click)` 只传一参，而 `mac/actions.py` L43 签名是 `click(element, action: str)` 双必选参，**TypeError**；type 分支（L210-218）调 `type_into(element, text)` 参数吻合（actions.py L62 第三参有默认值）。L224 `state.update` 重复调用（L207/L218 已调过）；L232-235 以字符串包含 `'Ofir folder'` 判定目标达成；L237 sleep(1) 等 UI 稳定；L244-246 finally `builder.cleanup()`。

## 三、外部连接

- **mlx_use/mac/tree.py**：`MacUITreeBuilder` 与 `build_tree(pid)`（L258）——示例唯一重度依赖；L204 直取私有 `builder._element_cache` 做 index→元素映射，这个私有缓存正是框架层 `requires_mac_builder` 注入机制的雏形。
- **mlx_use/mac/actions.py**：`click(element, action)`（L43）/`type_into(element, text, submit=False)`（L62）/`perform_action`（L19）三个原语；示例的调用姿势暴露了 click 签名演进（曾有一参版本）。
- **与框架版对照**：`examples/lunch_notes.py` 用 `Agent`+`Controller` 完成同一个"Notes 建文件夹"任务——本示例的框架化重写版，两者对读最能看清抽象的价值。
- **examples/print_app_tree.py**：同款拼接标记头（L1-2，且文件名误写成 basic_agent.py）；其 L13 `from mlx_use.agent.views import ActionModel` 依赖 agent/views.py L12 的"顺路命名空间"（详见 agent-views.md 第六节）。
- **上游关系**：无对应物——macOS-use 原创的 Mac 自动化原型，非 browser-use 平移件。

## 四、数据流

单步循环的数据变换链：PID →（build_tree：AXUIElement 递归遍历）→ `MacElementNode` 树 →（get_clickable_elements_string）→ 带高亮 index 的文本清单 →（f-string 拼进 prompt + 状态机上下文）→ 单条长字符串 →（Gemini）→ 响应文本 →（剥围栏 + json.loads）→ `{"action": ..., "parameters": {...}}` →（查 `_element_cache`）→ `MacElementNode` →（click/type_into：AXUIAction press/setValue）→ 布尔成败 → 状态机推进 + 下一步。与框架版对照，缺的正是三样：历史消息管理（每步都是无记忆的单轮）、结构化校验（json 失败仅打印，L226-227）、多动作步（每步只执行一个动作）。状态机 `FolderCreationState` 就是"记忆"的手工替代品。

## 五、设计决策与取舍

- **无框架直写的教学价值**：把 agent 的本质（树→prompt→LLM→动作→反馈）裸露到 250 行里，每一步都可单步调试——读它比读框架更能建立心智模型；代价是三处接口漂移无人修复，示例从"入门"变成了"陷阱"。
- **状态机外置而非靠 LLM 记忆**：单轮无记忆调用下，用 Python 状态机给每步注入"你现在处于哪个阶段"，是对模型记忆不可靠的工程补丁——框架版用 message_manager 历史替代了它。
- **同步 llm.invoke + asyncio 主循环混用**：LLM 调用阻塞事件循环，但对单 agent 单任务场景无所谓；框架版改 async 全链。
- **目标达成检测用字符串包含**（L232）：'Ofir folder' 出现在 UI 树文本即成功——简单到不会出错，也简单到会被同名前缀骗过（'Ofir folder 2' 也命中）。

## 六、新人提示（坑与勘误）

1. **三缺陷的爆发次序**：L17 import 期 NameError（先炸）→ 修好后 L116 每步 build_tree TypeError → 再修后 L206 click 调用 TypeError。**修复示例 = 补 `GEMINI_API_KEY = os.getenv(...)` + 删 `notification_callback` 参数 + 给 click 补第二参（如 `'press'`）**。不修的话此文件只能当阅读材料。
2. **prompt 里的 AI Studio 复制痕迹**：L144/L160/L169/L180 的 "Use code with caution."、L145 的 "Python"、L169/L181 的 "Json" 是从 Gemini AI Studio 复制 prompt 时把 UI 按钮文字一起拷进来的化石——它们会原样发给模型，轻度浪费 token 且污染指令边界。
3. **`notification_callback` 不是幽灵参数**：L20-22 的 handler 证明早期 `build_tree` 确实计划支持辅助功能通知回调（AXObserver 方向），接口简化后被删——示例是唯一物证。图谱摘要称其为"传不存在的参数"准确，但"为什么会有"的答案在接口演进史里。
4. **click 的第二参语义**：`click(element, action)` 的 `action` 是要执行的 AX 动作名（框架层 `ClickElementAction` 有对应 action 字段，controller/service.py L75-79 注册的 `click_element(index, action, ...)` 透传）——不是布尔也不是坐标。
5. **L1 拼接标记的对照组**：`print_app_tree.py` L1-2 是 `# print_app_tree.py` + `# --- START OF FILE examples/basic_agent.py ---` 两行——工具批量拼接文件时头部模板串了行，证明这批 examples 曾整体过一遍机器手。
6. **别学 `_element_cache` 直取**：L204/L213 直捅私有属性，框架内已有正规通道（requires_mac_builder 注入 + `_element_cache` 查询封装在 controller 动作里）。
7. **目标检测的边界**：L232 的包含判断会把 'Ofir folder 2'、历史邮件里的 'Ofir folder' 全判成功——按需换成精确匹配或元素角色校验。
