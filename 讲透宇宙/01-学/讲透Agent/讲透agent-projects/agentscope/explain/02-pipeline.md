# 02 pipeline 编排：sequential/fanout/msg_hub 三件套

## 1. 角色定位

pipeline 子系统只有三个小文件，却是多智能体协作的全部语法：`src/agentscope/pipeline/_functional.py` 提供三个裸函数原语（串行、扇出、流式打印调度），`src/agentscope/pipeline/_class.py` 把前两个包装成可复用的类，`src/agentscope/pipeline/_msghub.py` 用异步上下文管理器实现"一组智能体互相听见"。它刻意不做图引擎——没有节点边、没有状态机，控制流就是普通的 await 链。命名勘误：目录里没有 `_pipeline_base.py`，也没有 `parallayer`，并发原语的真名是 `fanout_pipeline`（`_functional.py:47`）；继承链上的"基类"其实是 `TruncatedFormatterBase` 所在 formatter 家族之外的一个平行约定——pipeline 无基类，全靠鸭子类型（`__call__`）。

## 2. 内部结构

**sequential_pipeline**（`src/agentscope/pipeline/_functional.py:10`）：全部实现是三行——`for agent in agents: msg = await agent(msg)`（`_functional.py:42`），前一个的输出作为后一个的输入，返回末位输出。注意它不 deepcopy 消息：Msg 对象按引用流动，上游 agent 后续再改同名消息会影响下游已入账的记忆。

**fanout_pipeline**（`_functional.py:47`）：`enable_gather=True` 时对每个 agent `asyncio.create_task(agent(deepcopy(msg)))` 再 gather（`_functional.py:96`）；False 则退化为顺序执行。与 sequential 的关键差异是这里每次都 `deepcopy(msg)`——N 个 agent 各拿一份副本，防止并发读写同一 Msg；返回值永远是 `list[Msg]`（顺序=agents 顺序，gather 保序）。

**stream_printing_messages**（`_functional.py:107`）：最精巧的一个。它不编排 agent，而是"旁听"：给参与 agents 统一挂一条消息队列（`_functional.py:163` 处 `set_msg_queue_enabled(True, queue)`），把用户传入的任意协程（比如一个 sequential_pipeline 调用）包成 task（`_functional.py:166`），task 完成时通过 done_callback 向队列投递 `"[END]"` 哨兵（`_functional.py:171`），主循环逐条 yield 队列里的 (msg, is_last) 直到收到哨兵（`_functional.py:180`）；收尾还检查 `task.exception()` 并原样重抛（`_functional.py:190`）——保证流式打印不会吞掉业务异常。docstring 特意强调 is_last 是"流式消息的最后一个 chunk"而非"agent 的最后一条消息"。

**类式包装**（`src/agentscope/pipeline/_class.py`）：`SequentialPipeline`（`_class.py:10`）与 `FanoutPipeline`（`_class.py:43`）只做一件事——构造期固化 agents 与参数，`__call__` 委托对应函数（`_class.py:37`）。存在价值是可复用、可作为对象传递（比如塞进另一个 pipeline 当"宏"）。

**MsgHub**（`src/agentscope/pipeline/_msghub.py:14`）：入场时 `_reset_subscriber` 让每个参与者的 `_subscribers[hub名]` 指向其余全员（`_msghub.py:89`，底层是 `AgentBase.reset_subscribers`，它会排除自己）；可选 announcement 公告随 `__aenter__` 广播（`_msghub.py:78`）；出场 `__aexit__` 按本 hub 名撤销订阅（`_msghub.py:87`）。运行期可 `add`/`delete` 增删成员，每次变更后整体重置订阅。手动 `broadcast` 就是逐个 `await agent.observe(msg)`（`_msghub.py:138`）；`set_auto_broadcast` 关掉自动广播后 hub 退化为纯手动广播器。

## 3. 外部连接

`_functional.py` 只 import `AgentBase`/`Msg`/`AudioBlock`，对 agent 的全部要求是可 `await` 调用——所以 pipeline 的真实耦合点是 `AgentBase.__call__` 的 finally 广播（`src/agentscope/agent/_agent_base.py:461`）：MsgHub 的自动广播正是靠每个 agent 回复后在 finally 里遍历 `_subscribers` 调它们的 `observe` 实现的。消费侧：examples 的对话流水线普遍 `async for msg, last in stream_printing_messages(...)` 做实时 UI；`_chat_room.py` 是第四个文件，为直播聊天室场景服务，不属编排核心。

## 4. 数据流

三智能体圆桌一轮：`async with MsgHub([a1,a2,a3], announcement=开场词):` → 入场互相订阅+公告 observe → `await a1(topic)` → a1 的 `__call__` → reply 完成 → finally 广播给 a2/a3 的 observe（各自 memory.add）→ `await a2()` 同理 → `await a3()` → 出场撤销订阅。若外面再套 `stream_printing_messages([a1,a2,a3], 圆桌协程)`，则每个 agent 内部 `self.print(msg)` 时消息进队列，被调度器逐条 yield 给 UI，圆桌协程结束触发 `[END]`。扇出场景：`fanout_pipeline([专家1,专家2,专家3], 同一问题)` 三任务并发，各自 deepcopy 的消息互不干扰，gather 后按入参顺序收齐三份答案。

## 5. 设计决策

"函数原语 + 薄类包装"双层 API：函数版适合一次性拼装，类版适合复用与预配参，两者共享同一实现避免分叉。fanout 用 deepcopy 换并发安全、sequential 不拷贝换零开销，是按共享度做的取舍。MsgHub 用"订阅表+名字隔离"而不是共享 memory：不同 hub 可叠加、同名互不干扰，且 agent 的记忆仍归自己所有，`observe` 进的是各自记忆——这让"听见过"与"说过"在序列化时天然可持久化。stream_printing_messages 用队列+哨兵而非回调，是 asyncio 里最朴素的生成器桥接，代价是每条消息经一次队列调度。

## 6. 新人提示

- 目录名对不上直觉：没有 `_pipeline_base.py`；老教程里的 `parallayer`/`MsgHub` 旧 API 在本仓已重构为 `fanout_pipeline` 与 async 上下文管理器版 MsgHub（`__aenter__` 而非 `enter()`）。
- `stream_printing_messages` 的第二个布尔是"该流式消息的最后 chunk"（见其 docstring 的 note），一个 agent 一轮会产出多个 True，别拿它当"回合结束"。
- MsgHub 是 async 上下文管理器：忘记 `async with` 直接构造不会有任何订阅生效；嵌套 hub 时外层退出只撤销自己名字的订阅。
- `add`/`delete` 之后必须经过 `_reset_subscriber`（源码内已自动调用），若你绕过 API 手改 participants，订阅表不会更新。
- sequential 不拷贝消息：如果下游 agent 会原地改 Msg（如改 metadata），考虑自己 deepcopy。
- 与 ONBOARDING 4.3 节互补：那边一句话带过三个原语，本文给出哨兵机制、deepcopy 差异与订阅表生命周期。

自报：02-pipeline.md｜约 3580 字符（不计空格）｜锚 19 个
