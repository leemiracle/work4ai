# 08 · PyO3 桥：crates/py/src/ 跨语言接缝的三层分工

## ① 角色定位

`crates/py/src/` 是整个系统唯一的 Rust→Python 通道，模块头一句话定调（`lib.rs:1-4`）：「薄门面：类型转换 + 同步调用；路由逻辑全部在 Rust 内核」。四个主文件各司其职：lib.rs（147 行）注册模块与 Router 门面，types.rs（788 行）定义 16 个 `#[pyclass]` 协议类型，convert.rs（904 行）做双向转换与校验，adapter.rs（94 行）做 Python 算法→Rust `AlgorithmProvider` 的**反向**绑定；state_adapter.rs/error.rs 对位处理状态与错误。一条铁律贯穿三层：**边界处校验一次、内核零信任重算**——畸形输入在 convert 层就被 `ValueError` 拦下，进内核的已是干净协议类型。（本篇锚点 lib.rs/types.rs/convert.rs/adapter.rs 均指 `crates/py/src/` 下同名文件。）

## ② 内部结构

**lib.rs——模块表面**：`PyRouter`（`lib.rs:41-44`）包一个 Rust `Router`，暴露五个方法。`from_config`（`lib.rs:49-54`）签名 `(config, *, state=None)`，config 收 path 字符串**或** dict（便于配置中心注入）；`route`（`lib.rs:66-76`）收 RouteRequest 或 dict，返回 `PyModelSelection`——注释明言这是 Decision 的投影；`report`（`lib.rs:80-84`）走与 Rust 侧 `Router::try_report` 相同的校验入口，非法反馈抛 ValueError 且不写 state。装配逻辑在 `assemble`（`lib.rs:96-114`）：算法解析**先查 Python 注册表再查 Rust registry**（`lib.rs:100-103`），state 解析同样三路（用户传入 > Python 注册 > 内核按 profile 建）。`#[pymodule]`（`lib.rs:121-147`）注册 16 个类 + 2 个注册函数，并用 `m.add("Decision", m.getattr("ModelSelection")?)`（`lib.rs:141`）造别名，`lib.rs:142-145` 导出 OK/OVERFLOW/UNAVAILABLE/REJECTED 四个字符串常量。

**types.rs——协议类型镜像**：每个类型都是「Py 壳 + native()/from_native() 或 From 双向实现」三件套。两种风格并存：小类型（ToolCall/Message/RoutingKey 等）直接展开字段并实现 `From`（如 `types.rs:29-45`）；带不变量的类型包 `inner` 私有字段+getter 暴露（`PyRetrievedItem` `types.rs:280-284`、`PyExtension` `types.rs:567-571`）。构造即校验：`PyRetrievedItem::new` 拒绝非有限 score（`types.rs:291-295`）并对 data 走 `extract_json` 配额检查（`types.rs:296-307`）。最复杂的是 `PyFeedback`（`types.rs:525-787`）：typed 构造器（`:602-635`）兼容旧字段与 `call=` 新表达且互斥——注释（`:611-612`）解释为何用 `None` 哨兵而非默认值比较：显式 `outcome="ok"` / `latency_ms=0` 不能被误判成未提供。`Feedback.ok` classmethod（`types.rs:645-684`）从 decision 对象/dict 提取 route_id，把「拿 decision 直接造反馈」的宿主常见写法做成一步。

**convert.rs——边界校验场**：`extract_json`（`convert.rs:24-111`）手写 Python 对象→协议 Value 的递归走查，内嵌 `charge`（`:28-48`）按字节/深度/元素数三重配额计费——注释强调计费顺序与 `protocol::Value::validate_inner` 严格一致：字符串按 UTF-8 字节计、其余节点 8 字节。`extract_feedback`（`:162-279`）对 dict 做字段白名单（`:173-194` 未知字段直接报错）并统一「call 与旧字段互斥」判定（`:224-259`）。`unsigned_integer`（`:146-153`）显式拒绝 bool——Python 里 `True` 是 int 子类，不挡会把延迟写成 1ms。`extract_request`/`extract_hint`/`extract_decision`（`:459-492`/`494-523`/`599-655`）都遵循「typed 对象 > dict > duck-typing 属性」降级链，hint 额外接受裸字符串当 cache_affinity（`:504-509`）。文件尾部 `profile_from_obj`/`profile_from_dict`（`:798-854`，中文注释）把 path/dict 配置解析成 `RouterProfile`——注意 `:852` 的 `evolving: Vec::new()`：dict 路径暂不支持 evolving，TOML 路径才有。

**adapter.rs——反向桥**：`py_algorithms()`（`adapter.rs:14-17`）用 `OnceLock<Mutex<HashMap>>` 维护进程级 Python 算法注册表。`PyAlgorithmAdapter::decide`（`adapter.rs:35-55`）在 `Python::with_gil` 里把请求/上下文转成 Py 对象，调 Python 的 `decide` 方法，再把返回值经 `extract_decision` 转回——其中 `adapter.rs:47-51` 用**错误消息字符串匹配**把 Python 侧的 "no available target" 翻译回 `RouterError::NoTarget`，这是桥上少数的按文本约定点。`register_algorithm`（`adapter.rs:67-93`）做 duck-typing 校验（有 decide 方法、name 非空且不叫 "unnamed"），类或实例都收——`convert::as_instance`（`convert.rs:897-903`）对类 `call0()` 实例化，实例原样返回。

## ③ 外部连接

向上：`python/openjiuwen/__init__.py:75-93` 是 `_openjiuwen` 的唯一正式消费者，重导出全部类型；`_openjiuwen.pyi` 是它的静态影子。向下：依赖 `openjiuwen_runtime::{registry, KvCacheCoordinator, Router}` 与 `openjiuwen_state::StateProvider`（`lib.rs:17-19`）。横向 KV 缓存协调走 `PyKvCoordinator`（`lib.rs:29-39`）——Rust trait 回调里 `Python::with_gil` 调 Python 闭包，错误被 `let _ =` 吞掉（回调失败不该打断路由）。`register_algorithm` 被 Python 门面 `bind_register` 接住（见 09 篇），形成「Python 类定义 → Rust 槽位」闭环。

## ④ 数据流

一次 `router.route(request, hint)` 的跨边界往返：Python dict/对象进 `route` → `extract_request`/`extract_hint`（`lib.rs:72-73`）转成协议类型（dict 路径里 metadata 缺省时从顶层 session_id/agent_id 兜底，`convert.rs:472-478`）→ Rust `Router::route` 全速决策（无 GIL）→ `Decision` 经 `PyModelSelection::from_decision`（`types.rs:505-513`）投影成四字段 Py 对象返回。反馈臂：宿主拿 selection 造 `Feedback.ok(...)` → `report` → `extract_feedback` 校验 → `Router::try_report`。反向臂（Python 算法）：Rust decide_loop 每请求调 `PyAlgorithmAdapter::decide` → GIL 区内一次完整的 Py 对象进出（`adapter.rs:36-54`）。

## ⑤ 设计决策与权衡

1. **投影而非全量导出**：`route` 只返回 `ModelSelection` 四字段（`lib.rs:64-65` 注释），Decision 的其余内部信息不跨边界——跨语言面越窄，桩越稳，`.pyi` 才能手写维护。
2. **两层宽容 + 一层严格**：对宿主输入（request/hint/feedback）宽容降级多形态，对**数据内容**（JSON 深度/字节、未知字段、非有限数）严格拒绝。宿主写法多样是现实，数据格式漂移是 bug。
3. **GIL 只圈回调不圈决策**：主路径决策在纯 Rust 侧跑（无 GIL），只有 Python 算法/回调进 `with_gil`。5 路内置算法同构 stub 的现状下（已知勘误），未来真算法进来时 Python 侧不是瓶颈假设。
4. **错误翻译靠 `to_py`/`feedback_error` 单点**：Rust 错误统一转 Python 异常类型在 `error.rs`/`convert.rs:20-22`，Python 侧看到的就是干净的 ValueError/TypeError，不需要认识 Rust 错误枚举。
5. **字符串匹配翻译 NoTarget（`adapter.rs:47-51`）**：省了一个跨语言错误协议，代价是 Python 算法作者必须一字不差地抛 "no available target" 文本——脆约定换薄桥，量级小时可接受。

## ⑥ 新人提示与坑

- **`.pyi` 与 `lib.rs` 是手工同步对**：给 `PyRouter` 加方法要同时改 `pymodule` 注册（`lib.rs:122-147`）、`_openjiuwen.pyi:186-194`，漏一处 IDE 补全就与运行时脱节。
- **Feedback 的 None 语义**：`outcome=None` 与 `outcome="ok"` 不同、`latency_ms=0` 与缺省不同（`types.rs:611-615` 注释），宿主代码别用 `if not latency_ms` 这类判定。
- **dict 配置进不了 evolving 段**（`convert.rs:852`）——需要 evolving 就走 TOML 路径。
- **bool 会被延迟字段拒收**：`unsigned_integer` 的检查（`convert.rs:147-151`）是有意为之，`latency_ms=True` 是 bug 不是 1。
- **Python 算法抛错文本即协议**：想让 Rust 侧正确识别「无可用目标」，必须精确抛含 "no available target" 的异常（`adapter.rs:47-50`）。
