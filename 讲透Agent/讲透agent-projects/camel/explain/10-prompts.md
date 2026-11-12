# 10 提示词体系：camel/prompts/

## 1. 角色定位

prompts 包是 camel 全部内置提示词的沉淀层，三层堆叠：底层 `TextPrompt`/`CodePrompt`（str 子类 + 关键字模板语义）；中层 12 个 `XxxPromptTemplateDict`（按 TaskType 分类的提示词字典，如 AI Society/Misalignment/Translation）；顶层两个聚合器——`TaskPromptTemplateDict`（TaskType→模板字典的二级映射）与 `PromptTemplateGenerator`（统一取用门面，prompt_templates.py:22）。角色清晰分工：camel/societies/role_playing.py:47-63 与 generators.py 经 Generator 取系统提示词，十几个 task agent（search/knowledge_graph/role_assignment 等）也各自定义 PromptTemplateDict 供 ChatAgent 装配。这个包把"提示词即代码"做到极致：所有模板是类体顶层的 TextPrompt 常量，可拼接、可 format、可直接被静态分析。

## 2. 内部结构

**TextPrompt（camel/prompts/base.py:92）**是 str 的直接子类，靠两个机制获得模板能力：`key_words` property 走 `get_prompt_template_key_words`（camel/prompts/base.py:105，函数体内延迟 import）提取 `{var}` 占位符集合；覆写 `format`（camel/prompts/base.py:109-124）先为全部未提供的占位符生成 `{'{key}': '{key}'}` 默认值——**部分格式化**：`TextPrompt("Hello {name}, {task}").format(name="X")` 后 `{task}` 原样保留，可分步填充。**CodePrompt（:128）**在其上加 `code_type`：因 str 不可变，用 `__new__`（camel/prompts/base.py:136-149）把 code_type 存实例属性；`execute`（camel/prompts/base.py:168）直接桥接 interpreters——不传 interpreter 时默认 `SubprocessInterpreter().run(self, self._code_type)`（:196），这就是 prompts→interpreters 的依赖边。

**`@wrap_prompt_functions`（camel/prompts/base.py:72）**是全包最重的元编程：类定义完成后遍历 `dir(cls)`，把每个 routine 方法包进 `return_prompt_wrapper`（camel/prompts/base.py:24）——返回值是 str 就转成本类实例、是 tuple 就逐项转换（:52-63）。TextPrompt 与 CodePrompt（camel/prompts/base.py:127）各装饰一次，而 CodePrompt 继承 TextPrompt，父类方法在父类装饰时已包一层、子类再装饰时 dir() 里同名方法又被包一次——双次包装（图谱钉版），行为靠 isinstance 短路不出错但栈深翻倍。

**TextPromptDict（camel/prompts/base.py:205）**是 `Dict[Any, TextPrompt]` 子类，其 `EMBODIMENT_PROMPT`（camel/prompts/base.py:208）在类体顶层调用 `get_system_information()`（camel.utils，:19 导入）拼系统信息——**import camel.prompts.base 即采集 OS/platform 信息**，属导入期副作用（图谱钉版）。12 个任务模板字典同构：类体常量 + `__init__` 里 update({RoleType.X: self.YYY})（如 ai_society.py:124-125 挂 ASSISTANT/USER 两个角色键）。

**TaskPromptTemplateDict（task_prompt_template.py:48）的基类是 `Dict[Any, TextPromptDict]` 而非 TextPromptDict**——它是二级聚合器：`__init__` 一口气实例化 12 个任务模板字典挂到 TaskType 键上（task_prompt_template.py:60-75）。与一级字典不在同一抽象层级（图谱勘误：对其发 inherits→TextPromptDict 边是错的）。

## 3. 外部连接

- **PromptTemplateGenerator（prompt_templates.py:22）**是唯一推荐入口：`get_system_prompt(task_type, role_type)` 按 TaskType 拿字典再按 RoleType 取键；`get_generate_tasks_prompt`/`get_task_specify_prompt`（:97/:111）服务任务生成线。role_playing.py 四处调用（:47/:52/:57/:63）。
- **types.RoleType/TaskType**：模板字典的键空间全在这里（EMBODIMENT/ASSISTANT/USER/Critic...），枚举即提示词索引。
- **interpreters**：CodePrompt.execute 的默认执行通路（camel/prompts/base.py:196）。
- **generators.py（GeneratorMixin）**：ai_society 的 GENERATE_ASSISTANTS/USERS/TASKS 三模板（ai_society.py:42-58）是 RoleNameGenerator/TaskGenerator 的弹药库，消费 data/ 下的角色 txt（apps/agents/agents.py:413-414）。
- **agents 包**：task_agent/search_agent 等每个自带 `<X>PromptTemplateDict`，与 prompts 包的 12 个共享同一模式但按 agent 命名空间存放。

## 4. 数据流

典型角色扮演链：`RolePlaying(task_type, task_prompt)` → 构造期 `PromptTemplateGenerator().get_system_prompt(task_type, role)` → `TaskPromptTemplateDict[task_type]` 取一级字典 → `[role_type]` 取 TextPrompt → agent 的 system_message 由模板 `.format(task=task_prompt)` 填充。任务生成链：GeneratorMixin 用 GENERATE_TASKS 模板 format(assistant_role=..., user_role=...) 让 LLM 列任务。拼接复用链（本包最特色的复用方式）：`MisalignmentPromptTemplateDict.ASSISTANT_PROMPT = DAN_PROMPT + AISocietyPromptTemplateDict.ASSISTANT_PROMPT`（misalignment.py:73-74）——DAN 越狱前缀直接串接 AI Society 的完整系统提示；`RoleDescriptionPromptTemplateDict` 同款手法（role_description_prompt_template.py:43-44），但注意两者继承目标不同：前者直接继承 TextPromptDict（:25），后者直接继承 AISocietyPromptTemplateDict（:22）从而免费获得全部生成类提示词。

## 5. 设计决策

1. **提示词用 str 子类而非 dataclass/string 常量**：换来三件事——可拼接（DAN+ASSISTANT 组合拳）、format 部分填充、key_words 自省；代价是 @wrap_prompt_functions 的全方法隐式包装与双次装饰的栈深，且任何返回 str 的方法都会被静默转成 prompt 对象（行为 surprises）。
2. **类体常量 + 类体拼接的"提示词继承"**：模板复用不靠方法调用而靠类体顶层字符串相加——静态可见、grep 友好；但拼接发生在 import 期，改 AISociety 的 ASSISTANT_PROMPT 会静默改变 Misalignment/RoleDescription 的成品，跨文件追踪必须沿拼接表达式走。
3. **二级聚合器不继承一级字典**：TaskPromptTemplateDict 用组合（Dict 值类型是 TextPromptDict）保持层级清晰，代价是取提示词要走两级索引——Generator 封装了这层琐碎。
4. **EMBODIMENT_PROMPT 的导入期采集**：系统信息在 import 时固化进类常量——同进程内不会刷新；也让"为什么 import camel 就读 /etc/os-release"这类困惑有了解释（get_system_information 的副作用）。
5. **12 任务字典全量实例化**：TaskPromptTemplateDict.__init__ 无条件构造全部 12 个，无懒加载——启动成本一次性付清，换 取用零分支。

## 6. 新人提示

- **别按文件名找"生成器"**：真正干活的是 prompt_templates.py 的 PromptTemplateGenerator；task_prompt_template.py 只有聚合字典。
- **format 的部分填充是特性不是 bug**：调试时看到输出里残留 `{task}` 先查是否漏传参，而不是怀疑模板损坏；`key_words` 可以列出一个模板全部占位符。
- **加新 TaskType 的三步**：types/enums.py 加枚举 → prompts/ 下新建 XxxPromptTemplateDict（记得 `__init__` 挂 RoleType 键）→ task_prompt_template.py 的 update 里补一行；漏第三步 Generator 静默取不到。
- **"dan_prompt" 自定义键**：misalignment 字典额外把 DAN_PROMPT 挂进字典本体（RoleType 键空间外的自定义键），取用方需知晓这个非角色键。
- **CodePrompt.execute 默认落本机子进程**（camel/prompts/base.py:196）：不传 interpreter 就是 SubprocessInterpreter 直跑，CI 里对不受信代码调用前先想清楚（interpreters 篇的安全谱系在此适用）。
