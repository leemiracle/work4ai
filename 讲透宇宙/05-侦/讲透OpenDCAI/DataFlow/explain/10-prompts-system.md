# 10 · dataflow/prompts/：提示词体系

## 一、角色定位

`dataflow/prompts/` 是全仓 LLM 提示词的集中营：所有算子对模型说的话都以 `PromptABC` 子类的形式住在这里，与算子逻辑（operators/）物理分离。这带来一个关键约束机制——算子通过 `@prompt_restrict` 装饰器声明自己只接受哪几个提示词类，传错类型在实例化瞬间就抛 TypeError（core/prompt.py:57-72），而不是等到生成出垃圾数据才被发现。目录组织与 operators 域分组镜像对应：10 个顶层文件（agenticrag/text2sql/text2qa/func_call/general_text/code/kbcleaning/chemistry/core_text/pdf2vqa）加两个子包（reasoning/ 含 diy/general/math，model_evaluation/）。实际注册进 `PROMPT_REGISTRY` 的 PromptABC 子类共 **99 个**（按文件分布：agenticrag.py 31、func_call.py 11、general_text.py 11、text2sql.py 9、reasoning/math.py 9、text2qa.py 7、code.py 6、其余各 1-3），其中 agenticrag 一家占近三分之一，因为它的合成流水线每一段（标识符抽取→结论→问题→清洗→作答→评分）各配一个专用 prompt。

## 二、内部结构

**基类极简**（core/prompt.py:7-20）：`PromptABC` 只有 `build_prompt()` 一个抛 NotImplementedError 的方法；`DIYPromptABC` 是留给用户自定义提示词的逃生门——`prompt_restrict` 白名单检查对 DIY 子类永远放行（core/prompt.py:62），官方类与用户扩展的二分法由此建立。

**每个 Prompt 类的形态**以 `Phi4QAGeneratorPrompt`（prompts/general_text.py:12-27）为典型：`@PROMPT_REGISTRY.register()` 装饰 + `__init__` 存配置 + `build_prompt()` 把参数 format 进模板字符串。复杂些的（如 func_call 的 BUTTON 七级联）拆 `build_system_prompt`/`build_prompt` 两段。reasoning/math.py 里的三个 Fusion prompt（Parallel/Sequential/Condition，被 fusion 生成器 L6 导入）展示了"同一任务多策略变体"的组织方式。

**注册表复用 operators 的 Registry 机制**（utils/registry.py），prompt 与算子共享同一套懒加载基建；顶层 `prompts/__init__.py` 只有一行 `from .reasoning import *`，其余文件靠注册表按需发现。

## 三、外部连接

消费方向：operators 各算子 `__init__` 的 `prompt_template` 参数接收 prompt 实例（如 ReasoningQuestionFusionGenerator 的 L24 类型注解四选一）；`prompt_restrict` 与算子基类的 `ALLOWED_PROMPTS`（core/operator.py:8）构成双重声明——前者运行时强制，后者类型注解暴露。DIY 通道意味着用户可以继承 `DIYPromptABC` 写自己的提示词注入任何算子，这是"算子固定、提示词可换"插件化的全部基础。

## 四、数据流

Prompt 对象在算子实例化时创建一次（fusion 生成器 L31-33：`prompt_template is None` 则落默认 Parallel 变体），run 时对 DataFrame 每行调 `build_prompt(行字段值)` 拼出 user prompt 列表，连同 `build_system_prompt()` 一起喂 `llm_serving.generate_from_input`（fusion L92-106）——prompt 层是纯函数式的字符串工厂，无状态、不碰 storage。

## 五、设计决策（含批判）

**提示词外置集中管理是正确决策**：改一句话不用动算子代码，评审 prompt 版本时只看一个目录。`prompt_restrict` 的签名绑定检查（`sig.bind_partial`，core/prompt.py:51）能同时捕获位置/关键字两种传参的错误类型，工程质量高。

批判与勘误（三处甄别全部源码实证）：

1. **fusion 生成器 L93 的 enumerate/zip 解包 bug**（operators/reasoning/generate/reasoning_question_fusion_generator.py:93）：`[self.prompts.build_prompt(p1,p2) for p1,p2 in enumerate(zip(problem_1, problem_2))]`——zip 已产出值对，再套 enumerate 后解包得到的是 `p1=整数下标, p2=(值1, 值2) 元组`，build_prompt 实际收到 `(0, ("题A", "题B"))`。正确写法是去掉 enumerate。这个算子当前产出的 prompt 内容必然错乱。同文件还有两处化石：L61 第二个 `elif lang == "en"` 永不可达（与 L50 重复，内部描述还停留在旧的 eval_stage 参数时代）；`_validate_dataframe`（L73-83）检查 `self.input_key`，但 run() 从未设置该属性（只设 input_problem_1/2，L101），一旦被调用必 AttributeError。
2. **phi4qa L83 output_key 硬编码失效**（operators/text_pt/generate/phi4qa_generator.py:83）：run 签名接受 `output_key` 参数并存入 self（L55-56），但写回时 `dataframe['generated_content'] = generated_outputs` 用死列名，返回值却是 `output_key`（L87）——用户传自定义 output_key 时，下游按返回值读列必 KeyError。附带一个对齐隐患：L67-71 跳过空 raw_content 行不进 llm_inputs，L83 却把 (可能更短的) generated_outputs 直接赋给全量 DataFrame 列，行数不等时 pandas 直接报错或错位。
3. **general_text.py 三处重复 import**：L3-4 与 L8-9 完全重复导入 `PROMPT_REGISTRY` 和 `PromptABC`（中间只隔一段 docstring），L77 与 L79 重复 `import textwrap`——合并文件时未清理的痕迹，无害但暴露了该文件由多个文件拼接的出身。

## 六、新人提示

写新算子的顺序建议：先在 prompts/ 对应域文件里定义 Prompt 类并注册，再在算子侧 `@prompt_restrict(YourPrompt)` 挂白名单，最后跑一次传错类型的实例化测试确认 TypeError 通路。两个易踩坑：① `prompt_restrict` 装饰的是类，必须放在 `@OPERATOR_REGISTRY.register()` 之外层且在类定义前（fusion 生成器 L13-19 的顺序是范本）；② 别学 phi4qa 把列名写死——output_key 进了签名就要用在赋值处。审读 prompt 模板时注意 `{content}` 之外的裸花括号会撞 format 的占位符解析。
