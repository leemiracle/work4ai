# variable_identifier.py 精讲——变量识别器（录制值 → 参数化占位符的三级检测流水线）

## ① 角色定位

`workflows/workflow_use/workflow/variable_identifier.py`（527 行）解决的问题：录制时你填了 `john@example.com`，回放时想换人怎么办？本模块扫描工作流里所有 input 步骤的**字面值**，判断哪些「每次都会变」（邮箱/电话/姓名/卡号……），把 `{var_name}` 占位符替换进去并生成配套 input_schema（含 default 回退值）——把一次性操作录像改造成可参数化复用的工作流。

图谱属 L04「变量系统线」，三条消费线：healing 的 `service.py`（L121-122 调模块级便利函数）、recorder 的 `semantic_converter.py`（L260 读 variable_config 的 min_confidence）、`variable_config.py` 六套预设（阈值 0.4-0.85 分级）。docstring 自称 "AI-Powered"（L2），但实现是纯正则 + 关键词 + 启发式——名字与实现的第一个落差。

## ② 内部结构

三个类型构件 + 主类 + 便利函数：

- **VariableType**（L18-31）：11 种枚举（string/email/phone/number/boolean/url/date/credit_card/ssn/zip_code/password）。
- **VariableCandidate**（L34-45）：value/variable_name/variable_type/confidence(0-1)/context/suggested_default/description/required。
- **VariableIdentifier**（L48-508），三个类级常量定调检测能力：
  - `PATTERNS`（L60-69）：8 种类型正则（EMAIL L61、PHONE 支持 `+()-.` 分隔 L62、URL/ZIP/SSN/卡号/日期双序/数字）。
  - `VARIABLE_KEYWORDS`（L72-101）：28 个上下文关键词→类型映射。
  - `STATIC_VALUES`（L104-118）：永不参数化黑名单（true/false/yes/no/on/off/1/0/submit/cancel/ok）。

方法四组：**主入口** `identify_variables_in_workflow`（L132-186，遍历 steps、替换占位符、生成 schema、写 metadata）；**三级检测** `identify_variable`（L188-253）编排 `_detect_by_pattern`（L255-262，置信 0.95）→ `_detect_by_context`（L264-304，置信 0.85/0.75）→ `_looks_dynamic`（L306-324，置信 0.5）；**命名** `_generate_variable_name`（L326-346，上下文优先+类型兜底表）、`_normalize_variable_name`（L361-384，剥 input-/txt- 前缀、特殊字符转下划线、数字开头加 field_）、`_ensure_unique_variable_name`（L386-399，`_2`/`_3` 递增）；**辅助** `_extract_step_context`（L401-431）、`_generate_description`（L433-443）、`_generate_input_schema`（L445-504）、`_is_variable_placeholder`（L506-508）。

模块级便利函数（L512-527）与类方法同名 `identify_variables_in_workflow`——无状态转发；图谱中为避免节点 ID 冲突仅模块级版本建节点。

## ③ 外部连接

- **上游**：healing `service.py` L121-122（`min_confidence=self.pattern_variable_confidence`，源自 variable_config 预设）与 recorder `semantic_converter.py`。输入是 deterministic_converter 产出的工作流 dict（input 步骤带 value/target_text/description）。
- **下游**：`{var_name}` 占位符由执行引擎的变量注入机制运行时解析；`_generate_input_schema` 产出对齐 `WorkflowInputSchemaDefinition`——注释 L448 明言 schema 只支持 string/number/bool 三型，11 种细分类型经 type_mapping（L449-461）压扁 + format_mapping（L464-473）保留细节。
- **metadata 契约**：L183-184 写 `variables_auto_identified: True` 与 `identified_variable_count`，下游（UI/存储层）据此识别"参数化过的工作流"。

## ④ 数据流

input 步骤 `{'type':'input','value':'john@example.com','target_text':'Email'}` 的处理：

1. **占位符检查**（L152-153）：值已是 `{xxx}` 则跳过（幂等，重跑不二次包装）。
2. **上下文提取**（L156→L401）：从 semanticInfo（labelText/placeholder/ariaLabel/name/id/textContent）、target_text、description、cssSelector 正则抠 name/id（L424-429）攒 context。
3. **三级检测**（L159→L188）：正则 EMAIL 命中 → 置信 0.95、变量名取 context 的 `email` 或类型兜底（L335），confidence≥0.95 时 suggested_default 留 None（L218）；正则不中走关键词——combined_hints 拼六路 context（L267-281），'email' in hints → 置信 0.85 + suggested_default=value；再不中走启发式——`_looks_dynamic` 数混合大小写/含数字/含特殊字符/长度>10 四指标，**≥2 项才算动态**（L323-324）→ 置信 0.5。
4. **阈值过滤与替换**（L161-169）：confidence ≥ min_confidence 才收——默认 0.6 下 Stage 3（0.5）**必然被拒**。去重后 `steps[i]['value'] = '{email}'`（L166）。
5. **schema 生成**（L177-178→L445）：`{'name':'email','type':'string','required':True,'format':'email','default':'john@example.com'}`——default 永远有值（无 suggested_default 时 L498-500 回退原始 value），零输入也能跑。

## ⑤ 设计决策与取舍

**三级瀑布对应三种证据强度**：正则（值本身形态）> 关键词（字段标签语义）> 启发式（"看起来动态"）。置信 0.95/0.85/0.5 与 min_confidence（预设 0.4-0.85）组合出可调的激进程度——保守 preset 0.85 只收正则命中，激进 preset 0.4 连启发式候选都收。

**default 永远兜底**（L494-500）是关键产品决策：参数化工作流必须向后兼容——不填参数就按录制原值跑。代价是敏感值（密码/卡号）原值也进 schema 持久化，安全上是双刃剑。

**值替换与 schema 同源**：同一次扫描里值变占位符、schema 记 default，原子绑定——不存在"占位符无 schema 定义"的中间态。

**检测保守偏向**：STATIC_VALUES 把 '1'/'0' 判静态、len<2 放弃（L200）、常见虚词白名单（L312）——宁可漏识别（工作流仍可跑）不可误识别（错替换破坏语义）。

## ⑥ 新人提示（坑/勘误）

1. **L296 是不可达死代码（任务书点名甄别）**：`_detect_by_context` 的 L294-302 "name 字段附加检查"永远走不到。该块条件 `any(term in combined_hints for term in ['name','full name','given name','surname','family name'])` 中**每个 term 都含子串 'name'**（'surname'=sur+'name'），条件为真 ⟹ `'name' in combined_hints` ⟹ L284 的关键词循环早已用 `'name'` 键（L80）命中并 return。整块连同 0.75 置信分支都是死代码；L299 `if var_name and 'name' in var_name` 的静默跳过也从未生效。
2. **浅拷贝副作用 bug**（L142）：`workflow_data.copy()` 只拷顶层——L166 改的 step dict 与调用方共享引用，**返回"新"工作流的同时污染传入的 workflow_data**。调用方若还要用原对象会拿到已替换的值。
3. **`use_llm` 是空参数**：L120-129 存进 self 后零读取，variable_config 有个 preset 传 True 实际无效果（docstring L126 自认 "future enhancement"）。
4. **BOOLEAN 是幽灵类型**（L25）：PATTERNS 与 VARIABLE_KEYWORDS 都无产出路径，type_mapping L460 的映射走不到；`required` 恒为 True（L220/L235/L250），schema 无 False 可能。
5. **L218 条件恒假**：pattern 置信固定 0.95（L259），`confidence < 0.95` 严格小于永不成立——pattern 路径永远不设 suggested_default，靠 L498-500 兜底。"高置信不带默认"的意图从未实现。
6. **`_seen_variables` 跨调用累积**（L130）：实例复用时第二个工作流同名变量被错误编号（email→email_2）。模块级便利函数每次新建实例（L526）躲开了此坑，直接复用实例的调用方会踩。
7. **context 键名与消费者错位**（L410）：`key.lower().replace('text','')` 把 labelText→label（对）但 textContent→content、ariaLabel→aria——而 hints 只认六键（L267-279），'content'/'aria' 提取了从不参与检测。
8. **PHONE 正则尾段 `{4,6}`**（L62）放行 11-13 位连续数字，纯数字长串（如订单号）可能先被 PHONE 捕获而非 NUMBER——正则按 PATTERNS 插入序先到先得（L257）。
