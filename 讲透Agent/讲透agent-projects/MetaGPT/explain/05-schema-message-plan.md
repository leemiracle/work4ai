# 05 Message/Document/Plan schema：metagpt/schema.py

## 一、角色定位

schema.py（976 行）是全仓数据宪法：Message（消息总线上的信封）、Document/Documents（文件抽象）、Task/TaskResult/Plan（任务与计划）、MessageQueue/SerializationMixin（容器与序列化）全在这一个文件里。MetaGPT 的 agent 间通信没有任何魔法，只有 Message 的三个路由字段；Plan 则是 plan_and_act 策略与 RoleZero 命令协议（Plan.finish_current_task 等）共用的数据面。**选题勘误**：任务书写的 "metagpt/schema.py+plan.py" 与源码不符——本仓无 metagpt/plan.py，Plan 类内嵌在 schema.py:495；独立文件只有 strategy/planner.py 的 Planner（策略层壳，goal/working_memory 包装 + 命令透传），di/write_plan.py 的 docstring 写 "@File : plan.py"（:4，NOTES-DIGEST 284 命名漂移条目）是历史迁移痕迹。

## 二、内部结构（行号锚）

**Message（schema.py:232-421）**：
- schema.py:232-243 字段七件套：id/content/instruct_content/role/cause_by/sent_from/send_to；metadata dict 存附加信息。
- schema.py:241 send_to 默认 `{MESSAGE_ROUTE_TO_ALL}`（const.py:81 的 `"<all>"`）——默认广播。
- schema.py:266-269 `check_cause_by`：**cause_by 缺省自动填 UserRequirement 的类全名字符串**——这是"每个 Message 必有生产者标签"的强制约束，也是 _watch 路由能成立的前提。
- schema.py:276-283 send_to 校验与序列化（set↔list 互转）。
- schema.py:251-263 `check_instruct_content`：反序列化时按 {"class","mapping"/"module","value"} 动态重建 pydantic 模型——跨进程恢复结构化输出的机关。
- schema.py:305-315 `__setattr__`：对 cause_by/sent_from/send_to 三键强制 any_to_str(_set) 归一化——**直接赋值 Action 类也会自动变字符串**，路由键永不脏类型。
- schema.py:412-417 is_user_message/is_ai_message。
- schema.py:439-454 AIMessage：role 锁 assistant；:448-451 with_agent 把发送者名字写进 metadata[AGENT]（MGXEnv 的 move_message_info_to_content 靠它溯源）。

**Document（schema.py:138-192）**：root_path/filename/content 三字段；:168-192 异步 load 类方法（含 project_path 相对化）；__str__ 直接返回 content（:166-170）。

**Task/TaskResult（schema.py:456-477）**：task_id/dependent_task_ids 依赖表 + instruction/code/result/is_success/is_finished/assignee；:474-477 update_task_result 是追加式拼接（code/result 用 "\n" 连接）。

**Plan（schema.py:484-651）**：
- schema.py:486-492 `@register_tool(include_functions=[append_task/reset_task/replace_task/finish_current_task])`——**Plan 四方法被注册为工具命令**，RoleZero 的 thinking_command 协议直接调它们（NOTES-DIGEST 356：命令协议的数据面）。
- schema.py:495-503 字段：goal/context/tasks/task_map/current_task_id。
- schema.py:505-523 `_topological_sort`：DFS 后序遍历排依赖；:511-517 visit 闭包的 visited 集合同时充当"处理中"与"已处理"两种状态（灰黑不分）。
- schema.py:582 `# FIXME: if LLM generates cyclic tasks, this will result in infinite recursion`——**无环检测缺失是作者自认的**（NOTES-DIGEST 352）：LLM 产出 A 依赖 B、B 依赖 A 时 visit 无限递归直接爆栈，没有友好报错。
- schema.py:640-651 `_update_current_task`：current_task_id 指向第一个未完成任务；:651 TaskReporter().report 上报任务态。

## 三、外部连接

Message 被全仓引用：Role._observe 的过滤条件（role.py:410-412）、Environment.publish_message 的投递（base_env.py:175）、Memory 存储、RAG 的 rag_key。instruct_content 的动态类重建连接 actions/action_outcls_registry。Plan 的消费双线：Role._plan_and_act（role.py:472-496，Planner 包装 Plan）与 RoleZero 命令解析（finish_current_task 在 special_tool_commands 特权路径）。Document 是 document_store 与 repo_parser 的底层载体。

## 四、数据流

消息一生：构造 `AIMessage(content=..., cause_by=WritePRD, sent_from=PM实例)` ——__setattr__/field_validator 把动作类与角色实例归一成字符串 → publish 到 env → 路由进下游 buffer → 入 memory → 拼进 prompt（to_dict 只取 role+content，:332-334）→ 下游 _act 产新 Message。计划一生：WritePlan 动作产 Task 列表 → Plan.add_tasks 拓扑排序（schema.py:524-564，公共前缀合并策略）→ current_task 逐个执行 → finish_current_task 置 is_finished 并滚动 current_task_id → TaskReporter 每步上报。

## 五、设计决策

- **路由即数据**：不做中心路由器，路由信息（cause_by 生产者、send_to 收件人）内嵌消息体，环境只做模式匹配——这让消息可序列化、可重放、可跨进程（Team.deserialize 恢复的正是这些信封）。
- **默认广播 + 双向兜底**：send_to 默认 `<all>`（schema.py:241），cause_by 默认 UserRequirement（:266-269）——两个默认值合谋保证了"最朴素的消息也能被订阅 UserRequirement 的角色接收"，新手 demo 无需懂路由就能跑通。
- **结构化输出的序列化协议**：instruct_content 不是存对象引用而是 {class, mapping, value} 三元组（:297-303 ser_instruct_content），配合 check_instruct_content 的动态重建——ActionNode 动态类因此可跨进程存活，代价是依赖 action_outcls_registry 注册表找类。
- **Plan 无环检测的缺失是层级问题**：依赖图来自 LLM 输出（write_plan），信任边界上没做校验；正确修法是 visit 加 in_stack 灰名单，FIXME 挂在 reset_task 而非 _topological_sort 本身，说明作者把锅记在了 LLM 生成端。
- **__setattr__ 归一化（:305-315）是防御性亮点**：pydantic v2 下覆盖 __setattr__ 需小心绕过校验器，此处只对三个路由键做字符串化，其余透传 super()——路由键类型安全由此闭环。

## 六、新人提示

1. 调路由问题打印 `msg.cause_by / msg.send_to / role.rc.watch / role.addresses` 四元组（都是字符串）对齐即可，九成问题在这里。
2. 手动构造 Message 给角色喂数据时，记得 cause_by 决定谁理它；不填默认 UserRequirement。
3. Plan 的 tasks 顺序即拓扑序，别自行 sort 打乱；加任务用 append_task/replace_task 命令而非直接改列表（会绕过 task_map 与 current_task_id 维护）。
4. 给 dependent_task_ids 填依赖时确保引用存在且无环——_topological_sort 对悬空 id 会 KeyError（task_map[task_id] 直接索引），对环会无限递归。
5. 序列化自定义 instruct_content 子类必须能被 import_class 找到（走 module 路径），否则反序列化 KeyError。
