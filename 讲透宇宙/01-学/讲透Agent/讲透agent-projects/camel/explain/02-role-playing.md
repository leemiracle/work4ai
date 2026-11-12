# 02 RolePlaying 双智能体范式：camel/societies/role_playing.py

## 1. 角色定位

RolePlaying 是 camel 的起家范式——2023 年 CAMEL 论文的"角色扮演式智能体合作"（AI Society inception prompting）在此落地，文件位于 `camel/societies/role_playing.py`（注意：不在 `camel/agents/` 下，属 societies 层；选题清单中"camel/agents/role_playing.py"的路径与源码不符，以源码为准）。它只做一件事：把两个 ChatAgent 组装成"user 出题、assistant 解题"的自驱动对话对，外层只需循环调 step 就能得到无需人类介入的多轮协作。853 行的体量与 6239 行的 Workforce 形成鲜明对照：这是框架里"最小可用的多智能体范式"，也是 Workforce 中 RolePlayingWorker 复用的内核。

## 2. 内部结构

`class RolePlaying`（role_playing.py:36）本身不是 agent，而是编排器。构造函数（role_playing.py:92）按固定顺序组装流水线：

1. `_init_specified_task_prompt`（role_playing.py:214）：默认 `with_task_specify=True`，先烧一次 LLM 调用把简短 task_prompt 扩写成具体任务描述；
2. `_init_planned_task_prompt`（role_playing.py:264）：可选 task planner 进一步拆解（默认关）；
3. `_get_sys_message_info`（role_playing.py:298）：按 task_type（默认 AI_SOCIETY）从 SystemMessageGenerator 取角色系统提示；
4. `_init_agents`（role_playing.py:356）：构建 assistant_agent 与 user_agent 两个 ChatAgent——user_agent 是关键设计，它不是人类输入通道，而是被 LLM 驱动的"任务指令模拟器"；
5. `_init_critic`（role_playing.py:466）：`with_critic_in_the_loop=True` 时，critic_role_name 为 "human" 则接 Human 交互代理（role_playing.py:491），否则建 CriticAgent 对多候选消息做裁决。

构造期也支持直接传入现成的 `assistant_agent`/`user_agent`（此时系统提示取自 agent 本身且不允许为 None）。对话推进面：`init_chat`（role_playing.py:548）重置双 agent 并生成开场消息，默认开场白是硬编码的 "Now start to give me instructions one by one. Only reply with Instruction and Input."（role_playing.py:566）；`step`（role_playing.py:631）/`astep`（role_playing.py:711）推进一轮；`clone`（role_playing.py:787）复制整套配置支撑多进程实验。

## 3. 外部连接

- 向内依赖 camel.agents 的 ChatAgent、CriticAgent、TaskSpecifyAgent、TaskPlannerAgent，全部经包 barrel 取用。
- 提示词侧接 camel.prompts 的 SystemMessageGenerator 与 TextPrompt 模板族——task_type 换成 CODE/MISALIGNMENT 等即切换整套系统提示。
- `model` 参数是全局兜底：传入后若 agent 专属 kwargs 未指定模型则统一覆盖（构造函数开头即打 warning，role_playing.py:119）。
- Human（camel.human）在 critic 位提供真人介入点，是这套纯自动范式里唯一的交互出口。
- 被 Workforce 消费：add_role_playing_worker（workforce.py:3019）把整套双 agent 对话封装成 workforce 的一个 Worker 节点。

## 4. 数据流

step 的输入是一个 assistant 角色的消息（通常来自上一轮返回或 init_chat），流程严格"user 先行"：`user_agent.step(assistant_msg)` 让 user 模拟器生成下一条任务指令 → `_reduce_message_options`（role_playing.py:516）把候选消息收敛为单条（无 critic 且消息数>1 时直接 ValueError；有 critic 则走 `critic.reduce_step`）→ 多响应模式下调用方负责补记记忆（role_playing.py:675 的注释钉版：ChatAgent.step 只在单消息返回时自动入记忆，n>1 时由本类在 `_reduce_message_options` 选定后调 `record_message`，判定函数是 `_is_multi_response`（role_playing.py:838），检查 model_config_dict 里 n>1）→ `assistant_agent.step(user_msg)` 执行任务产出回复 → 同样 reduce+补记 → 返回 `(assistant_response, user_response)` 二元组，各自携带 msgs/terminated/info。任何一方 terminated 时返回"半空"元组：未完成方 msgs 为空但 info 保留，调用方据 terminated 决定停或续。

## 5. 设计决策

1. **user-agent-first 顺序**：step 先驱动 user 再驱动 assistant，保证每轮 assistant 拿到的都是新鲜指令——这是论文"inception prompting"的可执行形态，也是新人最容易接反的方向。
2. **多响应裁决收口在一处**：n>1 的多候选消息必须收敛为单条才能续轮，RolePlaying 把该职责显式放在 `_reduce_message_options`，并在 critic 缺席时用异常拒绝多消息——宁可炸也不静默取第一条。
3. **记忆补记责任反转**：多响应时 ChatAgent 不自动写记忆，由 RolePlaying 选定后补记（role_playing.py:675），避免全部 n 条候选污染对话史。
4. **构造即全链初始化**：task specify 默认开意味着构造函数本身就有 LLM 调用与网络依赖——做单元测试必须 mock 或显式关 `with_task_specify`。
5. **async 是镜像而非内核**：astep 与 step 逐行同构，没有共享的异步内核，与 ChatAgent 的选择一致。

## 6. 新人提示

- **日志被压制**：本文件用裸 `logging.getLogger(__name__)` 且强制 `setLevel(logging.WARNING)`（role_playing.py:32），与全仓 camel.logger.get_logger 风格分裂——调试时 INFO 级流程日志全部被吞，想看轮次细节得自行改级或挂外部 handler。
- **默认构造会打真实 API**：with_task_specify=True 的扩写调用在 `__init__` 里同步发生，CI/离线环境必炸。
- **terminated 的半返回语义**：`msgs=[]` 不等于出错，先查 terminated 与 info 再决定重试。
- **开场白角色是 assistant**：init_chat 返回的消息以 assistant 身份进入 user_agent，别把角色名当成真实 speaker。
- **critic 只在多候选时有戏**：单消息路径 critic 完全不参与；想让 critic 每轮评审，需在 agent 配置里把 n 调大。
- **clone 后是浅共享模型配置**：多进程跑实验时 clone+with_memory=False 是标准姿势，但模型后端的 client 连接是否复用取决于后端实现，压测前先确认。
