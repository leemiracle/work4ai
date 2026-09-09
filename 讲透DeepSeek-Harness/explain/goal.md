# goal/src/index.ts — GoalService：可审计的目标域服务

> 原文件：[`packages/goal/goal/src/index.ts`](../../../explore/deepseek-ai/deepseek-harness/packages/goal/goal/src/index.ts)（629 行）

## 角色定位

`GoalService` 把"目标"从 agent 内存里的一个变量提升为**同会话的目标域**：事件溯源的状态、compare-and-set（CAS）语义的变更动词、进程内的 continuation 激活。目标在这里是可审计、可重放、可与远程客户端共享的一等会话数据，而不是运行时的私有状态。

它与 dsh-session 的关系是"域服务挂靠会话投影"的标准范本：goal 状态作为会话的一个投影（projection key `'goal'`）随日志重放，服务本身只提供变更动词与激活机制。读懂这个文件，等于读懂了"如何在事件溯源会话上再开一个业务域"的仓库标准做法。

## 内部结构

**七个 CAS 变更动词**：`create` / `edit` / `pause` / `resume` / `complete` / `block` / `clear`。每个动词都是 compare-and-set：请求携带前置预期（当前状态/版本），服务检查日志折叠出的现值，匹配才落事件，否则显式失败——并发变更不丢更新、不静默覆盖。

**fold 与服务分离**：`fold.ts` 的 `applyGoalEvent` 是纯折叠函数——给定旧状态与一个 goal 事件，产出新状态。它不依赖 Cordis 上下文，持久层重放、恢复路径与在线服务共用同一份语义。`domain.ts`/`runtime.ts`/`types.ts` 分别承载领域对象、运行时与类型，入口把它们再导出为包的公共面。

**版本与引用**：`GOAL_CHANGE_VERSION` 标记目标变更结构的版本；`goalChangeRef` 产出对一次目标变更的稳定引用，供事件间互指。

**远程暴露**：服务继承 `TypertRemoteService`（配合 `@Remote` 装饰器的远程协议基类），goal 的读写经 Typert 远程命名空间对 Host API 暴露——远程面与进程内面共享同一服务实例与同一份 CAS 语义，不存在"远程另走一套"。

**wire schema**：zod schema 定义在线格式，远程边界处校验。

七个动词之间的迁移关系值得展开：`create` 建立初始目标，`edit` 修改内容，`pause`/`resume` 在暂停与进行之间切换，`complete` 与 `block` 分别以"完成"与"受阻"收束，`clear` 清空整个域——动词集合就是状态机的边集，服务逐条检查"当前状态是否允许这条边"。continuation 激活是进程内语义：等待特定变更的等待者（比如挂起中的后续动作）在事件落账后被唤醒，不经轮询。包入口同时是桶文件，`types/domain/runtime/fold` 的公共面经这里再导出；zod wire schema 保证远程载荷形状——进程内调用与远程调用校验强度不同，正是"同进程边界信任类型、线边界才校验"这条仓库规则的落地。

## 外部连接

会话侧：`dsh-session-projection` 的投影机制，键 `'goal'`——恢复会话时 goal 状态从日志重放而来，无需独立存储。协议侧：`dsh-typert-protocol` 的 `TypertRemoteService`/`Remote`/`RemoteError`，目标数据经 session-controller 汇聚的远程面到达客户端。消费侧：agent 在回合中读取目标状态驱动行为；goal 变更事件进入会话日志后，同样受"model-visible ⟺ logged"约束——目标变化是模型可见输入，必须以事件形态存在。包内依赖：`domain.ts`、`fold.ts`、`runtime.ts`、`types.ts` 四个模块。

## 数据流

在线路径：变更请求（本地调用或远程解码）→ CAS 前置检查（用 fold 出的现值比对）→ 通过则 goal 变更事件 append 进会话日志 → `applyGoalEvent` fold 更新投影状态 → continuation 激活（进程内等待该变更的等待者被唤醒）→ 通知发布。恢复路径：会话重放时逐事件 fold，goal 投影自然重建。远程路径：请求经 Typert 解码与 zod 校验 → 走同一条在线路径 → 结果编码回传。

## 设计决策

**CAS 而非自由写**：目标的状态迁移（创建→暂停→恢复→完成/阻断→清空）天然是状态机。CAS 把"非法迁移"与"并发冲突"都变成显式失败，而不是靠事后对账。七个动词就是状态机的全部合法边——想加第八种迁移，先回答"这是不是既有动词能表达的"。

**fold 独立于服务**：折叠逻辑不持有上下文、不做 IO，测试无需启动 Cordis；持久层与恢复层复用它，保证"在线算的"与"重放算的"是同一个结果。

**目标走会话日志**：与仓库不变式对齐——凡是模型要看见的，都得能从日志重建。目标显然属于模型要看见的。

**远程与进程内同源**：TypertRemoteService 的继承让远程调用直接落进服务方法，避免"远程门面转述本地语义"造成的第二真相源。

**版本常量克制**：只在目标事件结构真正变化时才动 `GOAL_CHANGE_VERSION`，与 session 侧版本哲学一致。

## 新人提示

先读 `fold.ts` 再读本文件：折叠函数读完，状态机就在脑子里了，服务主体只是"检查+落账+激活"的壳。理解 CAS 语义最快的方式是看测试里的失败用例——非法迁移与过期前置各长什么样。动这个词表（比如想加 `archive`）之前，先确认没有既有动词能组合表达，仓库规则"每个公开操作要有当前消费者证据"会要求你拿出真实需求。排查"目标状态不对"时记住唯一重建方式是重放 fold——直接查内存状态是徒劳的，日志才是答案；`goalChangeRef` 则是跨事件追溯一次变更的入口。调试 continuation 不触发时，先确认等待者注册的进程还活着——激活是进程内语义，跨进程不存在；再查 CAS 前置是否真的匹配，被拒绝的变更不会唤醒任何人。
