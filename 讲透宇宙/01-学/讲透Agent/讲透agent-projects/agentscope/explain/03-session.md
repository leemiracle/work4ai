# 03 session 会话持久化：SessionBase 与多智能体状态协调

## 1. 角色定位

session 子系统回答的问题是"整场多智能体会话如何存档/恢复"。`src/agentscope/session/_session_base.py` 定义协议，`_json_session.py` 与 `_redis_session.py` 给出文件与 Redis 两个实现。最重要的实证结论先说：grep 全 src 目录，`save_session_state`/`load_session_state` 除 session 包自身外**零消费者**——核心框架不自动持久化，协调完全下放给应用层：你在入口处手动 `await session.load_session_state(session_id=..., agent1=agent1, ...)`、出口处手动 save。这是设计而非缺陷（examples 里 werewolves、a2a_server、planning_agent 等全这么用），也意味着"忘记 save 就丢档"是常态风险。

## 2. 内部结构

**SessionBase**（`src/agentscope/session/_session_base.py:8`）薄到只有两个 `@abstractmethod` 异步方法：`save_session_state`（`_session_base.py:12`）与 `load_session_state`（`_session_base.py:30`）。精髓全在签名：`**state_modules_mapping: StateModule`——把"多个带状态模块"作为关键字可变参数收进来，名字即存档键。注意它引用 StateModule 仅作类型注解、自身并不继承（类图上 SessionBase 不是 StateModule），且没有 ABCMeta 兜底，忘实现子类方法不会在实例化时报错。`allow_not_exist` 让"首次运行无档可加载"合法化。

**JSONSession**（`src/agentscope/session/_json_session.py:12`）：`_get_save_path` 规定文件名规则——有 user_id 时 `{user_id}_{session_id}.json`，否则 `{session_id}.json`（`_json_session.py:42`），目录自动 `makedirs`。save 时对每个模块调 `state_dict()` 组成大 dict（`_json_session.py:63`），`aiofiles` 异步写盘、`errors="surrogatepass"` 容忍奇怪字符（`_json_session.py:68`）。load 侧的关键语义是**部分加载**：只回填存档里存在的键（`_json_session.py:113`），存档缺谁不报错；文件不存在时按 `allow_not_exist` 决定跳过还是 raise（`_json_session.py:120`）。

**RedisSession**（`src/agentscope/session/_redis_session.py:17`）：key 模式 `user_id:{user_id}:session:{session_id}:state`（`_redis_session.py:20`），支持 `key_prefix` 隔离多环境、`key_ttl` 滑动过期。redis 依赖是惰性导入，缺包时给出 pip 安装提示（`_redis_session.py:61`）。save 用 `SET ... ex`（`_redis_session.py:125`）；load 用 `GETEX` 原子地"读+续期"（`_redis_session.py:152`）——读档动作本身会刷新 TTL，这是滑动会话的标准姿势。实现了 `__aenter__/__aexit__` 自动关连接。

## 3. 外部连接

session 站在整个状态体系的出口端。上游是 `StateModule`（`src/agentscope/module/_state_module.py:20`）：`__setattr__` 拦截把类型为 StateModule 的属性自动登记进 `_module_dict`（`_state_module.py:29`），`state_dict()` 递归收集子模块+显式注册的标量属性（`_state_module.py:49`）。由于 `AgentBase` 继承 StateModule，一个 ReActAgent 的 memory、toolkit、long_term_memory 等子模块全部自动进入序列化树；ReActAgent 自己还显式 `register_state("name")` 与 `("_sys_prompt")` 两个标量。 toolkit 的 state_dict 只存激活工具组（`_toolkit.py:965`），所以"存档-换代码-恢复"时工具函数本体不在档里、靠代码重建，档只恢复"哪些组激活"。真实消费模式见 `examples/game/werewolves/main.py:109`：`await session.load_session_state(session_id=..., **{player.name: player for player in players})`——九个 agent 一行收编。

## 4. 数据流

恢复一场九人狼人杀：构造 `JSONSession(save_dir="./checkpoints")` → load 逐模块 `load_state_dict` → 每个 player 的嵌套状态树（sys_prompt、memory 消息流、toolkit 激活组）被递归写回 → 游戏照跑（存档无关运行时）→ 出口 `save_session_state` 把九棵状态树 `json.dumps` 进一个文件。Redis 版同理，只是目的地换成带 TTL 的 key。注意流向是"应用层显式调"：框架内没有任何钩子替你触发 save。

## 5. 设计决策

用 `**kwargs` 而非 list 传模块，让存档键=参数名，调用处自文档且免维护注册表。部分加载语义配合"代码定义结构、存档只填数据"，使跨版本恢复尽量宽容——新加的模块在旧档缺失时保持默认。JSON/Redis 双实现的差异刻意保持极小（同样的 state_dict→json.dumps 管线），自定义后端（如 examples 的 SQLiteSession）只需继承两个方法。选择手动 save 而非自动 checkpoint，避免了每轮回复的写放大，把持久化时机留给最懂业务的调用方。

## 6. 新人提示

- 最大的坑是"以为框架会自动存档"：src 内零调用点，必须应用层显式调 save/load（见 `examples/game/werewolves/main.py:117` 的收尾 save）。
- `SessionBase` 无 ABCMeta：自定义 session 忘实现方法要到真正调用时才 NotImplementedError/静默空跑（`@abstractmethod` 在无 ABCMeta 元类时不具强制力）。
- JSONSession 的 user_id 拼进文件名而非目录：user_id 含路径分隔符会写出意外路径，外部输入需自行校验。
- 存档不含可调用对象：Toolkit 的 state_dict 只返回激活组名清单，恢复前必须先注册同名工具函数，否则"激活了一个不存在的组"。
- `load_state_dict` 默认 `strict=True`：状态树里多出的键在档中缺失会 KeyError，调参改名属性=旧档不再可整体加载，需 strict=False 或做迁移。
- 与 ONBOARDING 第 6 节"状态即 state_dict"互补：那边讲 StateModule 拦截机制，本文讲它在 session 出口的收口方式与部分加载语义。

自报：03-session.md｜约 3290 字符（不计空格）｜锚 20 个
