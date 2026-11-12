# 01 Role 角色基座：metagpt/roles/role.py

## 一、角色定位

Role 是 MetaGPT 全部智能体的唯一基类（role.py:125 `class Role(BaseRole, SerializationMixin, ContextMixin, BaseModel)`）。仓库里从经典 SOP 的 ProductManager/Architect 到 RoleZero 命令驱动系的 TeamLeader/Engineer2，全部继承这一棵类树。它把"一个 agent"固化为四个正交维度：身份（name/profile/goal/constraints 四字段拼出 system prompt）、动作（actions 列表）、注意力（watch 订阅集合）、运行时上下文（rc: RoleContext）。理解了 Role 就理解了 MetaGPT "消息驱动 + SOP"的全部底层：agent 之间不直接调用，只通过 Message 的 cause_by/send_to 两个字段完成路由。

## 二、内部结构（行号锚）

- role.py:92-123 `RoleContext`：运行时态全部收拢在此（env/msg_buffer/memory/working_memory/state/todo/watch/react_mode）。state=-1 表示初始或终止态（:106 注释）。
- role.py:161-164 `validate_role_extra`（mode="after" 的 model_validator）→ :166-180 `_process_role_extra`：构造收口处，做三件事——is_human 时换 HumanProvider（:169-170）、给 llm 挂 system_prompt 与 cost_manager（:173-174）、默认 `_watch([UserRequirement])`（:177）。
- role.py:182-191 `todo` property 与 `set_todo`：set_todo 时把 context 注入 action（:189-190），这是 Action 拿到配置的暗道。
- role.py:210-214 `check_addresses`：地址默认为 `{类全名字符串, name}`——人名路由的注册点。
- role.py:284-288 `_watch`：把 Action 类转成 `any_to_str` 字符串集合存入 rc.watch；:290-291 `is_watch` 是查询侧。
- role.py:302-306 `_set_state`：state 与 todo 联动，state>=0 时 todo=actions[state]。
- role.py:340-379 `_think`：单动作直通（:342-346）；recovered 恢复（:348-351）；BY_ORDER 顺序步进（:353-357）；多动作走 STATE_TEMPLATE 让 LLM 选状态号（:359-378），非法回答兜底为 -1（:371-373）。
- role.py:381-397 `_act`：执行 rc.todo.run(history)，按返回类型包装成 AIMessage（:384-394）并写回 memory（:395）。
- role.py:399-427 `_observe`：从私有 msg_buffer.pop_all() 取消息（:406），按 `n.cause_by in self.rc.watch or self.name in n.send_to` 过滤（:410-412），只把感兴趣的消息入 memory（:418）。
- role.py:429-446 `publish_message`：`<self>` 标签展开（:433-437）、发给自己则 put_message 短路（:438-440）、否则交给 env 广播（:446）。
- role.py:454-470 `_react` 与 :472-496 `_plan_and_act`：两种执行策略，入口在 :512-523 `react()`（结束时 :520 重置 state=-1）。
- role.py:529-554 `run`：observe→react→publish 的总循环，`role_raise_decorator`（:529）负责异常上报。
- role.py:556-559 `is_idle`：三条件判闲，Environment 轮询靠它收敛。

## 三、外部连接

上游：Team.hire→Environment.add_roles→role.set_env（role.py:308-316），set_env 会重挂 addresses、重刷 system_prompt 与 actions。下游：`_act` 调 Action.run、`_plan_and_act` 调 strategy/planner 的 Planner（role.py:47 引入）。横向：Memory 双实例（memory 持久 + working_memory 工作区）；`extract_state_value_from_output` 来自 utils/repair_llm_raw_output（role.py:49，:368 消费）。路由常量在 const.py:77-83（MESSAGE_ROUTE_FROM/TO/CAUSE_BY/TO_ALL/TO_SELF）。

## 四、数据流

一轮完整循环：环境投递 Message 进 role.rc.msg_buffer（put_message，role.py:448-452）→ `_observe` 过滤出 news（cause_by 命中 watch 或 send_to 命中自己名字）→ news 入 memory → `react` 选策略 → `_think` 决定 todo → `_act` 用 history 调 LLM → 产出的 AIMessage（cause_by=todo 动作类名）publish 回环境 → 下游角色的 watch 集合若含该动作类名即被激活。cause_by 是生产者标签、watch 是订阅者过滤器，两者都是 `any_to_str(Action类)` 的字符串，构成发布-订阅总线。

## 五、设计决策

- **订阅制而非广播制**：默认 watch=[UserRequirement]（:177），不显式 _watch 的角色只对用户需求起反应，SOP 依赖各角色显式声明关注上游产物（如 Architect watch WritePRD）。
- **pydantic v2 上的多继承缝合**：model_config `extra="allow"`（:128）让角色可用 kwargs 传 watch 等任意配置；两个 model_validator（:161、:210）承担了传统 __init__ 的工作。
- **人名常量路由陷阱（勘误，NOTES-DIGEST 298/337 交叉）**：环境按 member_addrs 找收件人，地址含类名字符串与英文人名两套 key（role.py:213）。MGXEnv 硬编码 `TEAMLEADER_NAME = "Mike"`（const.py:161；mgx_env.py:28 `tl = self.get_role(TEAMLEADER_NAME)`）——给 TeamLeader 改 name 会直接 KeyError/None，人名是协议的一部分而非装饰。
- **死代码警示（勘误）**：role.py:318-321 的 `name` property 返回 `self._setting.name`，但 pydantic v2 元类在类创建时删除与字段同名的 property（实测类 __dict__ 无 name 键），该 property 永不生效——读源码时勿被它带偏。

## 六、新人提示

1. 读源码顺序：RoleContext → run → _observe → _think/_act → publish_message，跳过三个模板常量（:51-79）。
2. `test_message`/with_message 只该用于测试（文件头 :17-18 注明），正常流转必须走 publish/put。
3. 想让角色响应某动作，改 `_watch([...])`；想让消息直达某角色，send_to 填它的 name 或类名字符串，别改 Environment。
4. debug 时先看 `_observe` 的 news 是否为空（"no news. waiting." :545）——九成"角色不干活"是 watch 没配上 cause_by。
5. 人名（Mike/Alice 等）出现在 const.py 就是路由 key，重命名前先 grep 全部 get_role 消费点。
