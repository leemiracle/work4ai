# 07 · 元素查询与作用域对账：query/pipeline.py 与 scope.py

## ① 角色定位

元素查询（FindElement）是所有元素级操作（click/type_text 等）的前置基建：给定 display reference 或语义路径，解析出当前仍活着的 native binding 并捕获其子树 facts。本篇讲 `computer_use_engine/interaction/query/pipeline.py`（195 行）、`scope.py`（100 行）与 `instances/` 实例解析三件套。

它回答的核心问题只有一个：**"上次读屏看到的那个元素/窗口，现在还在吗？在哪个作用域下？"**——GUI Agent 最易出幻觉处。query 线把问题拆成预算层（30 秒 Scope + 原生 lease）与对账层（modal 关闭后的上下文重定位）。注意包名映射：import 全写 `computer_use.interaction.query.*`，文件实居 `computer_use_engine/interaction/query/`。

## ② 内部结构

`FindElementPipeline`（pipeline.py:101）是五段 `Sequence`（:131-165），数据模型两个 frozen dataclass（model.py:20-50）：`FindPlan`（request + state + target + remaining）与 `FindLease`（plan + `OperationLease[Binding]` + selected + tree）。

1. **prepare_element_lookup**（passes/prepare_element_lookup.py:32-37）：请求与 handle 的 query_root/AppState 配对，契约 `Effect.RESOURCE`（:43）。直读 `controller._query_root`（pipeline.py:136），配注释 "The pipeline shares retained bindings with their owning service"（:134-135）——服务与 pipeline 有意共享绑定。
2. **Scope("LookupCallScope")**（pipeline.py:119-122）：`port.calls.claim(30000)` 领 30 秒共享预算。claim 实现 `native/lifecycle.py:86-119`：预算限 1..120000ms（lifecycle.py:88）、拒绝 retired 与并发 busy、绑定 owner task（:95）。
3. **AppScopeReconciliation**（pipeline.py:37-69）：作用域对账（见下）。
4. **Scope("LookupNativeScope")**（pipeline.py:124-129）：`calls.operation(window_binding(target), remaining)` 开原生读租约，内部 `begin_read(target, budget)`（lifecycle.py:195）换 token；退出强制 `port.finish` 清理（lifecycle.py:215），清理不确定即 retired。
5. **find_element + FindFacts**：`resolve_path` 按 token 与剩余预算解析路径（passes/find_element.py:31-38，`Effect.QUERY`）；`FindFacts`（pipeline.py:72-98）用同一租约收集选中子树 facts；**build_lookup_snapshot**（passes/build_lookup_snapshot.py:31-47）构造 ElementSnapshot 并显式 `result["source"]["ref"] = None`（:46）——"lookup has not published a number for this result"，查询结果未发布 display number。

**app_context 对账（scope.py:42-100）**：触发谓词（pipeline.py:145-149）要求 selection/observation 非空且 `plan.target == plan.state.observation.target`——目标确来自上次观察。目标即固定工作根则直接返回（scope.py:70-71）；否则重新 `_discover` 取活跃 surface（:74-77）；目录有 `stopReasons` 或任何 surface `parentState == "unknown"`（:78-81）→ `refuse("observation_incomplete")`，证据不全宁可拒绝。核心循环（:86-95）从 target.surface 沿旧观察的 modal 父链（每级须 `modal is True 且 parentState == "known"`）向 active surface 回溯，`seen` 防环；surface 仍在当前目录、不在旧记录、父链断裂统统 `refuse("stale_target")`。终点校验（:96-99）：回溯窗口须与 `replace(previous_window, surface=surface)` 同一 binding，resumed 窗口丢失查询根也拒绝。`refuse()`（:30-39）构造的错误带 `effect="none"` 与 `next="read this App again before continuing; no input was sent"`——把"没发输入"说死。

**instances/ 实例解析**：`instances/scope.py`（329 行）是身份守卫——`validate_session`（:34-60）查 retired 与固定身份；`require_identity`（:63-87）区分"身份不存在/已退役"（stale_target）与"membership 未确认"（observation_incomplete）；`adopt`（:104-166）目录刷新后重算成员归属；`refresh`/`resolve`（:169-272）同样 `claim(30000)`（:190）。`instances/pipeline.py` 的 `ApplicationDiscoveryPipeline.run()`（:40-90）按根窗口发布公共整数引用，`nativeReadIsolation` 能力下退回 AX 枚举，注释明确 "This is still a directory query, never recursive tree capture"（:64-66）。

## ③ 外部连接

- **上游**：`QueryPipeline`（pipeline.py:168-183）是 SessionController 入口，请求由 `client/computer.py` 的 `UI.element()` 发出（computer.py:140-148）。
- **下游**：`FindFacts` 复用 `read/acquisition/facts` 的 `FactCollectionPipeline`（pipeline.py:85）；ElementSnapshot 是 write 线路径解析输入。
- **横向**：scope.py import 目录服务 `select_surface`（scope.py:16），query 与 read 在目录服务上汇合。

## ④ 数据流

```
FindElement (owner + path + timeout_ms)
  │ prepare_element_lookup → FindPlan{request, state, target}
  │ Scope(claim 30000ms) → remaining 注入
  │ AppScopeReconciliation → app_context：刷新目录 → 沿 modal 父链回溯 → 新 target 或 refuse
  │ Scope(operation lease)：begin_read → token
  │     ├─ find_element：resolve_path(...) → selected
  │     └─ FindFacts：collect(read, node=selected.node) → tree
  └ build_lookup_snapshot → ElementSnapshot（source.ref=None）
```

预算单调递减共享：`remaining()` 每次重算 `deadline - now`（lifecycle.py:98-102），归零抛 `TimeoutError`；租约退出前再调一次 `remaining()` 确认读未超时（lifecycle.py:207-208）。

## ⑤ 设计决策与权衡

**为何固定 30 秒而非调用方指定？** query 与实例刷新统一 `claim(30000)`（pipeline.py:121 等），read 主链却用请求自带 `timeout_ms`（08 篇）。元素查询是"操作前校验"，时限由引擎兜底防模型占死预算；claim 硬上限 120000ms（lifecycle.py:88）。

**对账为何放 query 而非 read？** 谓词精确限定"target 恰来自上次 observation"（pipeline.py:148），只在幻觉高危场景重对账；read 本身天然重新发现目录。对账做成 FindPlan→FindPlan 恒等变换（:66），无侵入插在两个 Scope 之间。

**宁可拒绝不可猜**：四个 refuse 出口全落 `observation_incomplete`/`stale_target` 两码且带 `next`。代价是偶发误拒，收益是掐断"对消失的 modal 输入"类最难排查的事故。

**TYPE_CHECKING 两极与同步禁区**：文件头块（pipeline.py:27-34）外尾部还有一串（:186-195），最后一个干脆是 `if TYPE_CHECKING: pass`（:194-195）——批量生成的 import 残留；instances/scope.py:326-329 同款。两个 Node 的 `_run` 直接 `raise TypeError("Scope reconciliation requires arun()")`（pipeline.py:68-69）：需原生租约的节点禁同步，是 Pass 双轨（`run()` 走 `_sync` 拒绝 awaitable，core.py:251-262）在 Node 层的对应物。

## ⑥ 新人提示与坑

1. **阶段间全传 frozen dataclass**：用 `replace()` 造新值；`FindPlan.remaining` 初始 None（model.py:33），Scope 外访问不报错，传给 `resolve_path` 前必须已进 claim。
2. **下划线访问（`_discover`/`_selection`/`_query_root`）是协议的一部分**：重构 SessionController 时十余处调用要一起动。
3. **build_lookup_snapshot 的 `next(...)` 无默认值**（build_lookup_snapshot.py:38-44）：selected.node 不在 tree.refs 抛 StopIteration 而非业务错。
4. **refuse 的 `effect="none"` 只对查询成立**：write 线同款错误带真实 effect（11 篇）。
