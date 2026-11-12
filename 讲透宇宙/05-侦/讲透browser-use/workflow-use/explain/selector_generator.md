# selector_generator.py 精讲——多策略选择器生成器（healing 自愈子系统的确定性定位核心）

## ① 角色定位

`workflows/workflow_use/healing/selector_generator.py`（630 行）是 healing 自愈子系统里**把"录制时抓到的元素快照"翻译成"执行时可回放的定位策略"**的唯一组件。它不依赖 LLM、不依赖浏览器，是纯函数式确定性代码：输入 `element_data` 字典（tag/text/attributes/xpath 等），输出按优先级排序的 `SelectorStrategy` 列表。

存在意义写在模块 docstring（L1-6）：为页面元素生成多重回退定位策略，**降低对 AI 定位的依赖，让工作流更确定性**。在 healing 服务链路中，LLM 负责语义理解（动作是什么），本模块负责机械定位（元素在哪）——LLM 决定"点击文本为 Submit 的按钮"后，具体怎么找到按钮由这里的策略列表逐条尝试。

图谱属 L06「healing 自愈子系统」，是 `service.py`（WorkflowGenerationService）在录制回放数据落地时调用的底层工具（service.py L15 导入、L79 实例化、L664 调用 `generate_strategies_dict`）。

## ② 内部结构

### SelectorStrategy 数据类（L18-44）

```python
@dataclass
class SelectorStrategy:
    type: str      # 策略类型：'text_exact', 'role_text', 'aria_label', 'xpath' 等
    value: str     # 选择器值或匹配文本
    priority: int  # 越小越先尝试（1 最高）
    metadata: Dict[str, Any] = field(default_factory=dict)
```

带 `to_dict`/`from_dict`（L27-44）支持 JSON 序列化——策略列表最终嵌入工作流定义持久化，执行期反序列化逐条匹配。

### SelectorGenerator 类（L47-630）

构造参数三个（L67-82）：`enable_xpath_optimization`、`max_xpath_alternatives=2`（含绝对 XPath 兜底，2 = 1 优化 + 1 绝对）、`max_total_strategies=2`（**全部类型合计最多 2 条**）。

主入口 `generate_strategies`（L84-290）按固定顺序生成 8 类语义策略：

| 策略 | 行号 | priority | 触发条件 |
|---|---|---|---|
| text_exact | L118-127 | 1 | 有可见文本 |
| role_text | L129-139 | 2 | 能推断 role 且有文本 |
| aria_label | L141-150 | 3 | attributes 含 aria-label |
| placeholder | L152-161 | 4 | 含 placeholder |
| title | L163-172 | 5 | 含 title |
| alt_text | L174-183 | 6 | 含 alt |
| text_fuzzy | L185-194 | 7 | 文本长度 >3，阈值 0.8 |
| xpath | L196-280 | 2-10 动态 | 兜底，`_calculate_xpath_priority` 计算 |

XPath 分支（L196-280）最复杂：优化开启且有绝对 XPath 时，调 `XPathOptimizer.optimize_xpath`（L212-214）生成多条健壮候选，逐条算优先级并标注 `strategy` 名（id-based/table-anchored/text-contains 等，`_determine_xpath_strategy` L541-590 判定）；优化抛异常则降级到 `_generate_xpath`（L243-255）。

辅助方法：`_infer_role`（L292-337，role 属性优先，否则 tag→role 映射表 + input type 特判 L328-335）、`_generate_xpath`（L339-399，按 id > name > data-* > aria-label > placeholder > contains(text()) 的 **elif 链**取第一个命中）、`_generate_css_selector`（L401-454）、`_escape_xpath_value`（L456-475，单双引号混合用 `concat()` 拼接的经典转义）、`_calculate_xpath_priority`（L481-539，绝对 10 → id/name/data 2 → aria 3 → table/form 锚定 4 → class 6 → 裸文本 7 → 多重位置谓词 8 → 默认 5）、`generate_strategies_dict`（L592-603）、`get_summary`（L605-630，只展示前 5 条）。

## ③ 外部连接

- **上游依赖**：唯一 import 是 `workflow_use.healing.xpath_optimizer.XPathOptimizer`（L12），构造时按开关注入（L82），负责把脆弱绝对 XPath 改写成锚定 id/table/form 的相对路径。
- **唯一消费者**：`healing/service.py`。L79-84 实例化显式传 `max_total_strategies=2`；L664 在逐个处理录制交互元素时调 `generate_strategies_dict(element_data)`，结果写回 `element_data['selector_strategies']`（L666），随 element_text_map 传给下游确定性转换器，最终嵌入工作流定义。
- **输入来源**：element_data 由 service.py 从 DOM 快照对象组装（tag_name/text/xpath/css_selector/attributes），xpath 字段做 `x_path`/`xpath` 双属性名兼容。
- **下游隐含契约**：执行期语义匹配器按 `type` 字段分派（text_exact 全等、text_fuzzy 按 metadata.threshold=0.8、xpath 直接查询），metadata.tag/role 用于缩窄候选集。

## ④ 数据流

单次调用流水线：

1. **拆包**（L114-116）：tag 转小写、text 去首尾空白、attrs 取字典。
2. **语义策略生成**（L118-194）：7 类顺序追加，独立判断存在性；fuzzy 额外带 `threshold: 0.8`。
3. **XPath 策略生成**（L196-280）：优化路径产出 0-2 条 `optimized: True` 策略；L221 跳过逻辑——若某条恰等于绝对 XPath 且非最后一条则跳过（避免中间重复，末位绝对路径保留兜底）。
4. **排序**（L283）：`strategies.sort(key=lambda s: s.priority)`。Python 稳定排序保证同优先级保持插入序——语义策略先入列，priority=2 的 role_text 排在同为 2 的 id 型 XPath 之前。
5. **截断**（L286-288）：超出 `max_total_strategies` 砍低优先级尾部。默认 2 意味着典型输出是「text_exact + 一条最优 XPath」。

## ⑤ 设计决策与取舍

**语义优先于结构**。text_exact 给 priority 1，超过 ID 型 XPath（2）——录制场景里可见文本（"Sign in"）通常比 DOM 结构更能扛页面改版；ID 若是框架自动生成（React `:R1:`、CSS-in-JS 哈希类名），稳定性反而差。这是针对"录制→回放隔一段时间"场景的经验取舍。

**docstring 的可靠性排序与实现不一致（勘误）**。类 docstring（L54-64）声称顺序是「1. ID selectors (most stable) 2. Data attributes 3. Name...」共 10 级，但实际第一条是 text_exact，且**不存在独立的 id/data/name 语义策略**——它们只在 `_generate_xpath`（L363-376）和 `_generate_css_selector` 内部作为构件出现。docstring 描述的是早期版本设计，重构后没同步。

**elif 互斥的属性选择**。`_generate_xpath` L363-389 只选**一个**最强属性（命中 id 就不看 name）——单条件 XPath 更短可读，代价是 id 失效时不退 name（回退靠多策略列表整体，而非单条内部）。

**默认 max_total_strategies=2 是激进瘦身**。最多 8 类砍到 2 条，动机是工作流定义的 token 体积（策略进 LLM 上下文与持久化 JSON），service.py L79-84 显式传 2 印证有意为之；代价是丢弃 fuzzy、aria 等中间层回退。

**异常静默降级**。优化失败只 `logger.debug`（L244）后退回简单生成；`_generate_xpath`/`_generate_css_selector` 全程 try/except 返 None（L397/L452）——本环节永不抛异常，保证录制链路不被打断。

## ⑥ 新人提示（坑/勘误）

1. **`_generate_css_selector` 是死代码**：L401-454 完整实现（含 id 冒号/点号转义 L423），但全仓无调用者——element_data 的 `css_selector` 字段读进来后从未用于生成策略。别以为输出里有 css 类型策略。
2. **`base_priority = 3` 是死变量**（L218）：注释说 "Priority starts at 3"，赋值后循环内实际用 `_calculate_xpath_priority` 的返回值，该变量从未被读取。
3. **priority 数字越小越优先**，与直觉相反；`_calculate_xpath_priority` 返回 1-10，绝对 XPath 恒为 10（L494-496），且 `xpath.startswith('/html/body')` 强制视为绝对（L495）——即使优化器返回的是相对路径。
4. **text_fuzzy 的 `len(text) > 3`**（L186）：短文本不生成模糊策略（短串模糊匹配误报率高）。调阈值时记得这是字符数。
5. **`type` 值是跨进程契约**（录制端生成、执行端消费、测试断言），改名会让存量工作流定义里的策略失去匹配器；新增类型须同步执行端分派。
6. **`_infer_role` 的 role 属性直接透传**（L304-305）：不校验合法性，页面写错 role 会把错值带进 metadata——匹配端按 ARIA 规范枚举会对不上。
7. **同优先级顺序依赖稳定排序**：priority=2 有 role_text 与 id 型 XPath 两个来源，顺序由插入序决定（语义先于 XPath）；改成非稳定比较会让回退顺序悄悄变化。
8. **get_summary 只展示前 5 条**（L625），调试长策略列表别被它骗了——不是全量日志。
