# 02 · example-plugin：skill / tool / rail 三组件教科书

## 一、角色定位

`plugins/example-plugin/` 是 JiuwenSwarm 官方参考插件，全仓两个在架插件之一。它的使命不是提供多有用的能力，而是**用一个极小的真实场景（文本字数统计 + 会话轮次记录）演示插件包三类能力组件的标准写法**：skill 指导（教智能体"怎么做"）、tool 执行（给智能体"新手"）、rail 监听（在执行过程"旁路观察"）。README 第一句就自我定位（`plugins/example-plugin/README.md:3`）："在一个插件包内同时演示 skill / tool / rail 三类能力组件的标准写法……所有代码保持最小可读，供插件开发者照抄结构。"init.py 模板的 README 也指名"参考 plugins/example-plugin/README.md"（`templates/plugin-template/README.md:16`）——它是新插件的活范本。

它同时是工具链的测试基准：validate.py 的 L0/L1/L2 三层校验、hot_load_worker 的真 import 验证、tests/plugins 的行为测试，都以它为首个全绿样本（`plugins/example-plugin/README.md:47` 明言本包必须通过 `validate.py --only example-plugin` 三层校验）。

## 二、内部结构

一个标准插件包五件套——manifest.json + README.md + skills/ + tools/ + rails/：

**manifest.json（84 行）是包的单一声明入口**。头部元信息：`id: example-plugin`（L4）、中文名与一句话描述（L5-6）、双语 `display_name/display_description`（L7-14）、`category: Engineering`（L15）、`source: local`（L16）。面向 Hub 详情页的三组展示字段：`default_init_input`（L18-21，首次对话提示）、三个双语 `tags`（L22-35）、三条 `quick_inputs`（L36-49）。最关键的是三段组件声明，结构各不相同：

- **skills 段**（L50-55）：`{"dir": "./skills/usage-report", "mode": "all"}`——按**目录**声明，`mode: all` 表示包内所有智能体都装载该技能；
- **tools 段**（L56-69）：按 **file + class** 定位（`tools/word_count_tool.py` 的 `WordCountTool`），并带双语 `display_name/display_description`（L60-68）；
- **rails 段**（L70-83）：同样 file + class（`rails/turn_counter_rail.py` 的 `TurnCounterRail`），也带双语展示字段。

三段声明方式的差异映射三类组件的本性：skill 是目录制（一个 SKILL.md 入口可挂附属文件），tool/rail 是类定制（加载器按 file+class 反射导入）。

**三个组件文件各自极简**：

1. `tools/word_count_tool.py`（70 行）：`WordCountTool(Tool)`（L16）构造函数里用 `ToolCard` 声明 id/name `word_count`（L22-23）、description（L24-28）、JSON Schema 参数 `text` 必填（L29-38）。`invoke()`（L42-56）纯函数式统计四个指标：`characters`/`characters_no_spaces`/`words`/`lines`（L50-56）；缺参时返回 `success: False` + 中文错误（L44-48），**不抛异常**。`stream()` 直接 yield 一次 invoke 结果（L58-59）。`_extract_text()`（L61-69）兼容 dict 与对象两种入参形态。
2. `rails/turn_counter_rail.py`（41 行）：`TurnCounterRail(DeepAgentRail)`（L17），内存计数器 `_invoke_count`（L23），`init/uninit` 挂载/摘除 agent 引用（L25-29），`before_invoke` 自增（L35-36），`after_invoke` 空实现（L38-40）。暴露 `invoke_count` 只读 property（L31-33）。
3. `skills/usage-report/SKILL.md`（34 行）：frontmatter `name: usage-report` + description（L1-4），正文三节——目标（"统计结果必须来自 word_count 工具的真实返回值，禁止自行估算"，L12）、四步工作流（L15-29，含固定报告模板 L22-29）、验收标准（"数值与工具返回值完全一致""不引入臆造字段"，L31-34）。

## 三、外部连接

- **openjiuwen SDK 两个基类**：tool 侧 `from openjiuwen.core.foundation.tool import Tool, ToolCard`（`word_count_tool.py:13`），rail 侧 `from openjiuwen.harness.rails.base import DeepAgentRail`（`turn_counter_rail.py:14`）。这两行是插件与宿主框架的全部耦合面——插件不 import 任何其他宿主模块。
- **SKILL.md → tool 的语义引用**：skill 工作流第 2 步"调用 word_count 工具，入参 text"（`SKILL.md:18`），同时 tool 的 description 也反向声明"需配合 usage-report skill 使用"（`word_count_tool.py:27`）——这是**纯文本互相引用**，无 import 边，靠 description 语义让模型自己建立关联。
- **rail 注释指向规范**：`turn_counter_rail.py:39` 注释"需要汇总/落盘的场景参见 docs/plugin-spec.md 的 Rail 规范"。
- **测试线**：`tests/plugins/example-plugin/test_example_plugin.py` 用 `pytest.importorskip("openjiuwen")`（L17）实现"无 SDK 整体跳过"，`importlib.util.spec_from_file_location` 按文件路径直接加载模块（L24-28）——不经包导入，模拟宿主热加载的真实路径。六个测试覆盖：计数正确性（L41-50）、多行多词（L53-57）、缺参降级（L60-64）、isinstance 真 Tool（L67-71）、rail 计数（L74-84，用 `SimpleNamespace` 伪造 ctx）、**钩子必须真覆盖基类**（L87-94）。
- **工具链**：validate.py L0 校验 manifest 声明与磁盘文件一一对应，L2 热加载真 import 本包两个 py；catalog.py 把本包登记进 catalog.json。

## 四、数据流

以 manifest 的 `default_init_input`（L18-21）"统计这段文本的字数并生成使用报告"为例，一次完整请求的三组件接力：

1. **skill 触发**：宿主按 manifest skills 段（L50-55）装载 usage-report 技能，SKILL.md 的 description（"当用户要求统计一段文本的字数……时使用本技能"，`SKILL.md:3`）参与路由匹配，命中后工作流指导进入上下文。
2. **tool 调用**：智能体按工作流第 2 步发起 `word_count` 工具调用，入参 `{"text": "你好，世界！……"}`。SDK 将请求派发到 `WordCountTool.invoke()`（`word_count_tool.py:42`）：`_extract_text` 取参（L43）→ `splitlines()` 数行（L49）→ 返回四指标 dict（L50-56）。
3. **结果裁决**：工作流第 3 步检查返回值（`SKILL.md:19`）——`success=false` 停止并向用户说明；`success=true` 按固定模板（L22-29）填入 `{characters}` 等占位符输出报告。验收标准要求四项数值与工具返回**完全一致**（L33），杜绝模型自行算数。
4. **rail 旁路计数**：整条链路的每一轮智能体 invoke，`TurnCounterRail.before_invoke` 都被宿主钩子机制调用一次（`turn_counter_rail.py:35-36`），计数器自增。它不读输入、不改输出、不参与内容生成——README 的组件协作图（`README.md:26`）明确标注 rail 是"旁路"。用户问"这个会话聊了几轮"时（manifest quick_inputs 第 2 条，L42-44），智能体读取 `invoke_count` 回答。

关键点：**数据流的主干是 skill→tool 的顺序编排，rail 是横向切面**。skill 与 tool 之间没有函数调用关系，编排权在模型手里——skill 用自然语言写"第 2 步调用 word_count"，模型遵照执行；这是 agent 插件体系与传统插件体系（宿主回调接口）的本质区别。

## 五、设计决策与权衡

1. **场景刻意选小**：字数统计 70 行、轮次计数 41 行、skill 34 行——三组件加起来不到 150 行，让读者一次看全三类骨架而不被业务逻辑淹没。官方教科书的标准做法（对照 web-to-markdown 342 行单 tool，深度留给"真实可用"示范）。
2. **tool 纯函数式**（docstring L6："无文件写入、无外部依赖、无运行时对象注入"）：好处是可测（测试直接 `asyncio.run(tool.invoke(...))`，`test_example_plugin.py:43`）、可并发、热加载无清理负担。代价是状态无处安放——有状态需求全部推向 rail（本包的轮次计数就是示范"状态放哪"）。
3. **rail 状态只留内存**：`turn_counter_rail.py:6-7` docstring 明言"仅在内存中累计调用轮次，不做文件写入、不注入 prompt"。这是刻意的最小化：rail 模板规范要求"内部状态路径统一使用 get_workspace()，禁止写包内路径"（`rail_template.py:7-8`），示例索性不落盘，把落盘场景留给规范文档。
4. **错误返回而非异常**：`invoke` 一切失败路径都返回 `{"success": False, "error": ...}`（`word_count_tool.py:44-48`），让模型能读到中文错误信息并向用户转述。若抛异常，宿主只能给模型一个 traceback 片段——错误消息本身成为 prompt 的一部分，这是 agent tool 设计的重要范式。
5. **manifest 双语三处重复**：`default_init_input` 必须与 `quick_inputs[0]` 完全相同（模板注释钉死），display_name 与 name 语义重复、display_description 与 description 重复。冗余是 Hub 渲染层（详情页 vs 列表页 vs 首次对话）各自取数的代价，由 L0 校验保证一致性。
6. **`_extract_text` 兼容对象入参**（`word_count_tool.py:63-66`）：dict 与 attr 双形态。SDK 的 inputs 是 dict，但宿主某些路径传对象——示例宁可多写 7 行也演示这个防御性写法，新人照抄可避开一类真实坑。

## 六、新人提示与坑

1. **SKILL.md 的 description 决定触发**：`SKILL.md:3` 那句"做什么 + 何时用"是模型判断何时启用技能的唯一依据。写得太泛（"文本处理技能"）会永不触发或乱触发——模板注释也强调"触发机制依赖这句话"（`templates/plugin-template/components/SKILL.md:3`）。
2. **rail 钩子必须是真实现**：`test_example_plugin.py:87-94` 用 `getattr(type(rail), hook) is not base_impl` 断言钩子真的覆盖了基类——docstring（L88）说明"否则热加载会拒绝"。只写 `def before_invoke(self, ctx): return None` 语义上等于没写（rail 模板 L36-37 恰好就是这个样子，需要改成有实际行为的实现）。
3. **skill 目录名 = frontmatter name**：manifest skills 段声明的是 `./skills/usage-report` 目录（L52），加载器进目录找 SKILL.md，frontmatter `name: usage-report`（L2）必须与目录名一致，L0 校验查这个对应。
4. **测试无 SDK 自动跳过**：`importorskip`（`test_example_plugin.py:17`）意味着本地没装 openjiuwen 时这六个测试静默 skip——别被"全绿"迷惑，CI 的 hot-load 节点才负责真跑（L5 注释）。
5. **counter 与报告的数字来源**：skill 明令"禁止自行估算"（`SKILL.md:12`）——这是对模型幻觉的直接防御。写自己的 skill 时，"结果必须来自工具返回值"这类硬约束值得照抄。
6. **manifest 组件声明的路径格式不统一**：skills 段 `dir` 带 `./` 前缀（L52），tools/rails 段 `file` 不带（L58,72）。这是规范原文的写法，照抄即可，别"修正"成一致——L0 按原样校验。
7. **图谱视角**：本包与 web-to-markdown 之间零依赖，两插件互不可见；组件间唯一"连接"是 manifest 声明 + SKILL.md 的文本引用。分析插件协作时先读 manifest 三段声明，再看 SKILL.md 里的工具名引用链。
