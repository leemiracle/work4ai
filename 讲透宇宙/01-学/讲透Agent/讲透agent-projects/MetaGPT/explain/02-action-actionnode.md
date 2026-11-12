# 02 Action 与 ActionNode 体系：metagpt/actions/

## 一、角色定位

actions/ 目录是 MetaGPT 的"动作层"：Action 是最小执行单元（一次 LLM 调用或一段逻辑），ActionNode 则是结构化输出引擎——把"让模型填一张带类型标注的表"变成可校验的 pydantic 动态模型。两者关系：Action 是壳（携带 llm/prefix/context），ActionNode 是 schema 与解析内核；`_an` 后缀的文件（write_prd_an.py、design_api_an.py）都是"用 ActionNode 重写的 Action"。目录里还沉淀了三层历史：早期自由文本 Action（write_code.py）、ActionNode 结构化代（*_an.py）、以及 RoleZero 命令代（di/ 子包），三代并存。

## 二、内部结构（行号锚）

**Action 基类**（actions/action.py）：
- action.py:34 `class Action(SerializationMixin, ContextMixin, BaseModel)`；:36-40 i_context 联合类型（CodingContext/RunCodeContext 等五种上下文形态）。
- action.py:46-54 `_update_private_llm`（model_validator）：llm_name_or_type 命中 ModelsConfig 时整体换 LLM 实例——按动作级配模型的机制点。
- action.py:70-75 `_init_with_instruction`：传 `instruction=` 关键字即自动包一个 schema="raw" 的 ActionNode，免写子类。
- action.py:98-105 `_run_action_node`：有 node 时 run 自动降级为 node.fill；:107-110 run 基类抛 NotImplementedError，子类必须覆写。
- action.py:83-85 `set_prefix`：prefix 同时写 llm.system_prompt 与 node.llm。

**ActionNode**（actions/action_node.py，876 行）：
- action_node.py:135-172 类头与 __init__：key/expected_type/instruction/example/content/children 六元组，prevs/nexts 支撑 ActionGraph。
- action_node.py:214-217 `from_children`：常量树组装的标准姿势（父节点 key + 子节点列表）。
- action_node.py:250 `create_model_class`：用 pydantic create_model 把 children mapping 动态生成模型类做类型校验，@register_action_outcls（:249）同时登记进注册表供反序列化找类。
- action_node.py:428-452 `_aask_v1`：schema=="json" 走 llm_output_postprocess（:441-444），否则 markdown 解析 OutputParser.parse_data_with_mapping（:446）。
- action_node.py:597-650 `fill`：入口分发——CODE_FILL/XML_FILL/SINGLE_FILL 三特殊模式（:626-639），strgy="simple" 一次填整树（:642），"complex" 逐子节点填再合并（:644-650）。
- action_node.py:706-711 auto_review 的 `_AN_REVIEW` 动态类、:798 `_AN_REVISE`：审阅-修订闭环。

**常量树范式**（actions/write_prd_an.py）：
- write_prd_an.py:14-18 `LANGUAGE = ActionNode(key="Language", expected_type=str, instruction=..., example="en_us")`——每个字段一个模块级常量；文件尾 `WRITE_PRD_NODE = ActionNode.from_children("WritePRD", NODES)`、`REFINED_PRD_NODE = ...` 组装成树（另见 REFINED_NODES 列表）。

## 三、外部连接

上游唯一消费者是 Role：set_actions→_init_action 注入 context/llm/prefix（role.py:229-233），_think 选中后 `_act` 调 todo.run（role.py:383）。下游：ActionNode 依赖 utils/repair_llm_raw_output 的修复闭环（经 provider/postprocess/llm_output_postprocess.py:12 分发到 BasePostProcessPlugin）；exp_pool 的 @exp_cache 与 ActionNodeSerializer 挂在 fill 链上（action_node.py:27-28 引入）。ActionType 枚举（actions/__init__.py:34-52）与 roles/ 的 _watch 字符串互通——watch 集合存的就是动作类名字符串。

## 四、数据流

典型 ActionNode 流：Role._act → Action.run → 检测到 node → `_run_action_node` 把 history 反转拼成 context → `node.fill(req, llm, schema)` → simple_fill 内 compile 生成带格式示例的 prompt（SIMPLE_TEMPLATE，action_node.py:66-77）→ llm.aask → _aask_v1 → llm_output_postprocess 四步修复（大小写/标签缺失/提取/JSON 修复）→ create_model_class 生成的类校验字段类型 → instruct_content（BaseModel 实例）与 content（原文）双双返回 → Role 包装成 AIMessage。失败路径：校验不过则 auto_review 产评论、auto_revise 带 `_AN_REVISE` schema 重问。

## 五、设计决策与勘误（证据锚）

- **WRTIE_CODE 拼写（勘误）**：actions/__init__.py:38 `WRTIE_CODE = WriteCode`——枚举成员名拼错且已固化，上游qa_engineer 等处引用它做 watch 匹配，改拼写等于换协议。
- **write_code_an_draft.py 是死代码草稿（勘误，NOTES-DIGEST 284）**：文件头 :4 `@File : write_review.py` 复制漂移；:557 `WRITE_CODE_NODE = ActionNode.from_children("WRITE_REVIEW_NODE", ...)` 变量名与节点键不一致；:576 `class WriteCodeAN(Action)` 的 docstring 还写着 "Write a code review"（:577）；:584-587 自带 `async def main()` 与 `asyncio.run`——全仓 grep 零消费方，是留存的结构化实验场，读它学模式可以，别当生产链路。
- **ArgumentsParingAction 拼写（勘误）**：actions/skill_action.py:24 类名 "Paring" 应为 Parsing，上方 :22 还挂着 `# TOTEST` 注释；其 run（:43-54）+ parse_arguments（:56 起，文本前缀切片法解析 `skill_name(args)`）服务于 Assistant 角色的技能调用（assistant.py:111）。
- **markdown 类型注解必须用 typing.List**：action_node.py:7-9 NOTE 明言——内置 list 在 markdown 提取时拿不到类型信息，这是常量树里 List[str] 遍布的原因。
- **三代并存的历史包袱**：WriteCode（write_code.py:88）返回 CodingContext 而非 ActionNode，与 _an 系并存使"动作输出形态"没有统一契约，消费方需 isinstance 三分支（role.py:384-394）。

## 六、新人提示

1. 写新 Action：只需继承 Action、实现 run；要结构化输出就定义模块级 ActionNode 常量列表 + from_children，再在 run 里 node.fill(req=context, llm=self.llm, schema="json")，照抄 write_prd_an.py 的骨架。
2. 排查"模型输出解析失败"先看 config 的 repair_llm_output 开关（默认 False，见 config2.py:75），修不动输出时优先改 instruction/example 而不是加修复正则。
3. instruction 是每个节点的"字段说明书"，质量直接决定填充率；example 会进 few-shot，类型必须与 expected_type 严格一致。
4. ActionType 枚举只是索引目录，新增动作不必注册它——真正生效的路由键是类名字符串（any_to_str）。
5. 涉及 _an 文件时先 grep 消费方：部分 _an 文件（如 write_code_an_draft.py）早已脱离主链。
