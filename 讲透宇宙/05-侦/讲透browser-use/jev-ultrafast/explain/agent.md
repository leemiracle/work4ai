# agent.py — 完整的 agent 循环：类型化选择、可观测状态、有界执行

## 一、角色定位

agent.py 是 jev-ultrafast 的心脏，全仓 174 行写完了一个浏览器 agent 的全部循环逻辑。文件 docstring（agent.py:1）一句话立宪：typed choices（决策是受限枚举）、observable state（状态全量可读）、bounded execution（执行有硬预算）。它在架构中处于承上启下的位置：向下持有 Browser 实例（agent.py:19）负责浏览器观察与执行，向内调用 model.py 的 choose/field_text 做决策与文本生成，向上被 demo.py 的 HTTP 命令分发器（demo.py:54、demo.py:66）和 examples/flights.py、examples/run.py 直接消费。README 里"Read the loop"链接指向的就是这个文件——读懂它等于读懂整个项目的运行时语义。

## 二、内部结构

**构造与首次观察（agent.py:13-44）**。`__init__(url, goals, *, record_dir=None, screenshots=False)` 先把 goals 归一化为单个 task 字符串（str 直接 strip，list 用换行拼接，agent.py:14），空任务直接抛 ValueError（agent.py:16）。随后创建 Browser 并立刻做首次 observe（agent.py:23）；这次观察若失败，先 close 浏览器再向上抛异常（agent.py:24-26），不留僵尸标签页。核心状态全部收进一个 14 键的裸字典 state（agent.py:27-41）：browser/goal/page/decision/history/status/plan/plan_index/decisions/text_calls/elapsed_ms/started_at/record。screenshots 参数有个隐式规则：只要给了 record_dir 就自动开启截图（agent.py:21），首帧以 `000000.jpg` 落盘（agent.py:44）。

**snapshot()（agent.py:46-50）**。对外快照 = state 剥掉 browser 句柄，再附上 `action_space(page["actions"])[0]` 生成的 elements 元素表——这就是 README 里"numbered element table"的数据来源。

**command()——唯一的状态推进入口（agent.py:52-161）**，三个子命令：

- `tick`（agent.py:55-64）：predict + act 的复合步。若中途抛 StalePage，则丢弃决策、status 拉回 ready、重新观察并返回快照——这是"导航打断预测"的标准恢复路径，tests/test_agent.py:315-320 锁定了"恢复时不执行任何动作"。
- `predict`（agent.py:65-85）：先做四道闸——浏览器存活检查（agent.py:66-67）、计时器懒启动（agent.py:68-69）、页面新鲜度复查不新鲜就重观察（agent.py:70-71）、终态拒绝（done/blocked 后再预测报错，agent.py:73-74）。随后是**模型调用预算**：decisions 数组长度达到 `MAX_STEPS * 2` 即 120 次封顶（agent.py:75-76）。真正决策只有一行 `choose(page, goal, history)`（agent.py:77），结果连同 fingerprint 与耗时记入 decisions 账本（agent.py:78-84）。
- `act`（agent.py:86-158）：执行分支，顺序是全文最值得精读的部分。① fingerprint 闸：调用方回传的 fingerprint 必须等于当前 page 的 fingerprint（agent.py:88-89）；② **决策一次性消费**——在任何变更或模型调用之前先把 state["decision"] 置 None（agent.py:90-91），注释明言"A retry cannot double-click"；③ DONE/BLOCKED 终态处理，落定前还要再查一次新鲜度，plan_index 在 DONE 时翻为 1（agent.py:93-100）；④ **动作预算**：history 满 60 条即置 blocked 并抛错（agent.py:102-104）；⑤ fill 分支：先复查新鲜度（agent.py:107-108），再组 field_context，若 pending_text 三元组的上下文键与本次完全一致则复用已生成文本，否则调 field_text 并记入 text_calls（agent.py:109-115）；⑥ 委托 browser.act 执行（agent.py:117，browser 会在输入前最后一刻再查一次新鲜度）；⑦ **先记账后观察**（agent.py:120-141）：history 条目含 18 个字段（step/action/kind/choice/probability/confidence/latency_ms/text/text_helper/operation/target/page_changed/url/usage/executed_ms/elapsed_ms 等），观察若被导航打断，已执行的动作也不会丢（tests/test_agent.py:221-227）；⑧ 观察后回填 page_changed 与最新 url（agent.py:144-148）；⑨ 录帧以耗时毫秒命名（agent.py:149-152）；⑩ **无进展熔断**：最近 3 步全部 page_changed 为 False 且 kind 不是 wait，则置 blocked（agent.py:153-158）。

**run() 与生命周期（agent.py:163-174）**：run 是生成器，每 tick 一次 yield 一个快照，status 进入 done/blocked 停止；close 配合 `__enter__/__exit__` 支持官方 README 的 with 用法。

## 三、外部连接

依赖面极窄：从 .browser 导入 Browser 与 StalePage（agent.py:7），从 .model 导入 action_space/choose/field_context/field_text 四个函数（agent.py:8），从 .questions 导入 MAX_STEPS（agent.py:9）。上游消费者有 demo.py（reset 时构造、command 透传）、examples/flights.py:48（`Agent(URL, GOALS)`）、examples/run.py、tests/test_agent.py:162（用 `Agent.__new__` 绕过构造直接装配 state，实现零浏览器离线测试）。被 `__init__.py:3` re-export 为包级 API。

## 四、数据流

输入：一个 URL 字符串 + 一段自然语言 goal（或 goal 列表）。内部：state["page"] 是 browser.observe 返回的完整观察（url/title/text/actions/fingerprint/screenshot...）；state["decision"] 是 choose 返回的决策对象（choice/operation/target/probabilities/confidence/usage/latency_ms...）。输出：snapshot() 返回可 JSON 化的状态字典；history 每条是一步的完整审计记录，text_calls 单独记录文本助手的每次调用（模型名、延迟、产出值）。demo.py 的 response_state（demo.py:32-34）把这个快照直接推给浏览器前端。

## 五、设计决策与取舍

1. **决策先消费再执行**（agent.py:91）：把"取走决策"放在一切副作用之前，天然杜绝重试双击/双填，这是比事务回滚更便宜的正确性方案。2. **双预算制**：120 次模型调用（agent.py:75）+ 60 次浏览器动作（agent.py:102），两个稀缺资源分别设限，text_calls 不占预算但受 pending_text 缓存约束。3. **记账先于观察**（agent.py:120）：观察可能因导航失败，但已执行的浏览器副作用不可撤回，账本必须先落。4. **pending_text 以整个 context 元组为缓存键**（agent.py:110-114）：页面文本一变缓存即失效（tests/test_agent.py:202-211 验证），保证复用绝不污染新语境。5. **熔断豁免 wait**（agent.py:156）：等待不改变页面是常态，不应误杀加载中的任务。6. **不用异常做控制流回滚**：StalePage 走恢复路径，ValueError/RuntimeError 一律上抛，由 demo 层转成给用户的错误消息。

## 六、新人提示

- **plan/plan_index 是单任务残留**：plan 恒为 `[task]` 单元素（agent.py:17），plan_index 只在 DONE 时从 0 变 1（agent.py:98），别误以为存在多目标规划机制。
- state 是裸 dict 而非 dataclass，demo.py:62 会直接往里塞 scenario 键——扩字段零成本但也零 schema 保护。
- act 的 fingerprint 来自调用方 body（agent.py:88），demo 前端必须原样回传快照里的 fingerprint，否则永远过不了闸。
- predict 的 started_at 懒启动意味着 reset 后第一次 GET /api/state 的 elapsed_ms 是 0，计时从第一次 predict 才开始（agent.py:68-69）。
- tick 只捕 StalePage；select 执行中断抛的 RuntimeError（browser.py:130-131）不会被 tick 吞掉，会一路传到 demo 变 4xx/5xx，需要用户 reset——这是刻意设计（变异永不自动重试）。
- 图谱 hub 对本文件的描述（三段式协议、StalePage 防护、双重预算、无进展熔断）与源码逐条核对一致，无出入。
