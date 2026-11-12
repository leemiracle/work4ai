# 02 · core/prompt.py 与 core/llm_serving.py——提示词与推理引擎的基座

## 角色定位

这两个文件是 DataFlow"生成侧"的双基座：`prompt.py` 定义提示词的模板抽象（PromptABC），`llm_serving.py` 定义推理后端的引擎抽象（LLMServingABC）。所有 LLM 类算子的构造函数都同时注入这两者——模板负责"把 DataFrame 行拼成 prompt 文本"，引擎负责"把 prompt 列表变成模型输出"。最终图谱中 `core/prompt.py` 有 69 条入边，是 core 包被引用最广的文件；`llm_serving.py` 经 `core/__init__.py:2` 导出，并被 `LLM_SERVING_CLASSES` 类型别名（`core/__init__.py:9`）用于 Pipeline 的后端探测（`Pipeline.py:69`）。

## 内部结构

`prompt.py` 三件套：`PromptABC`（`prompt.py:6-10`）只有 `build_prompt` 抛 NotImplementedError；`DIYPromptABC`（`prompt.py:12-16`）是空壳子类，语义通道=用户自定义模板；核心是 `prompt_restrict` 装饰器（`prompt.py:28-78`）——装饰时 `setattr` 类属性 `ALLOWED_PROMPTS`（`prompt.py:34`），包一层 `new_init` 绑定实参后取 `prompt_template`，`isinstance(pt, cls.ALLOWED_PROMPTS)` 不在白名单且非 DIY 子类就抛带完整允许清单的 TypeError（`prompt.py:56-67`），并回写 `__annotations__` 暴露 Union 类型（`prompt.py:74-75`）。文件尾带 `__main__` 自测块（`prompt.py:81-107`）。`llm_serving.py` 的 `LLMServingABC`（`llm_serving.py:5`）声明三抽象方法：`generate_from_input`（`llm_serving.py:8-14`）、`start_serving`（`llm_serving.py:16-21`）、`cleanup`（`llm_serving.py:23-28`），外加可选 `load_model`（`llm_serving.py:30-35`）。注意 `start_serving` 的 docstring 写的是"Cleanup the generator"（`llm_serving.py:18-20`）——复制粘贴残留，实际语义是"启动服务"。

## 外部连接

`prompts/` 包按领域拆成 13 个模块文件，实测 98 个 `PromptABC` 子类（grep `^class \w+\(PromptABC\)`；任务书写 71 个，以源码现况为准），DIY 子类 0 个，全部挂 `@PROMPT_REGISTRY.register()`（如 `prompts/core_text.py:6-7`）。运行时消费以直接 import 为主——`PROMPT_REGISTRY`（`registry.py:259`）的 `.get()` 在主代码零调用（仅脚手架测试用），注册更多是"可发现性"而非查找路径。算子侧标准接线见 `format_str_prompted_generator.py:9-12`：同时 import 装饰器、serving 基类与具体 prompt 类。

## 数据流

以 `FormatStrPromptedGenerator` 为样例（`format_str_prompted_generator.py:45-62`）：`storage.read('dataframe')` 取整表 → 逐行按 `input_keys` 抽字段 → `prompt_template.build_prompt(need_fields, **key_dict)` 渲染 prompt（`format_str_prompted_generator.py:53`；`FormatStrPrompt` 用字符串替换实现，缺字段按 `on_missing` 抛 KeyError 或补空串，`prompts/core_text.py:22-27`）→ 交给 `llm_serving.generate_from_input(user_inputs, system_prompt, json_schema)`（`format_str_prompted_generator.py:58`）→ 输出整列写回 `dataframe[output_key]` 并 `storage.write`（`format_str_prompted_generator.py:60-62`）。

## 设计决策

模板与引擎分离、在算子构造器汇合，是典型的策略模式：同一算子换 prompt 即换任务，换 serving 即换模型，互不感知。白名单校验放装饰器而非基类，对 98 个存量 prompt 零侵入、可逐算子渐进收紧。批判有二：其一，运行时 isinstance 只拦"传错对象类型"，拦不住"模板字段与 input_keys 不匹配"——这类错误要拖到 `build_prompt` 才炸（`prompts/core_text.py:23-26`）；其二，ABC 签名与实现已经漂移——各后端 `generate_from_input` 普遍加了 `json_schema` 扩展参（`api_llm_serving_request.py:348`），基类声明（`llm_serving.py:9`）没有，靠鸭子类型兜底。

## 新人提示

自定义 prompt 继承 `DIYPromptABC` 即可被任何算子接受，这是设计特性不是后门。新 prompt 类记得挂 `@PROMPT_REGISTRY.register()`，运行时直接 import 即用。新 serving 后端的三个抽象方法必须全实现，否则实例化直接 TypeError；`python -m dataflow.core.prompt` 可跑自测验证装饰器行为。排查"Invalid prompt_template type"报错时，看报错里列出的允许清单（`prompt.py:62-67`）比看文档快。
