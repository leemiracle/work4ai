# scope/src/index.ts — dsh-scope：作用域原语与事件路由的根

> 原文件：[`packages/core/scope/src/index.ts`](../../../explore/deepseek-ai/deepseek-harness/packages/core/scope/src/index.ts)（204 行）

## 角色定位

`dsh-scope` 是整个 harness 的作用域地基：它把 Cordis 上下文（Context）打上一个**不透明的 scope 标签**，并在此基础上提供两条贯穿全仓库的语义——**注册视图沿父链向下继承**（子作用域能看见祖先注册的东西）与**事件准入沿父链向上延展**（祖先的监听器能收到后代作用域的事件）。工具的分层遮蔽（scoped 工具盖住全局工具）、子代理组合的观察（一个常驻组合监听它下面每个 agent 的事件）、会话与目标事件的路由，全都建立在这 204 行之上。

它是个零业务依赖的纯原语包：只 import Cordis 的 `Context`/`Fiber`，其余全是本包的 `store.ts` 类型再导出。读透它，后面读 tools、subagent、goal 时关于"作用域"的一切疑问都会消失。

## 内部结构

**核心类型与标签**：`ScopeKey = object`——任何对象都能当键，相等性就是对象身份，无法伪造。`kScope` 是模块内 Symbol，`createScope` 把它写进派生的 Context。`Scoped<T>` 用 `declare const ScopedBrand: unique symbol` 做成品牌类型：一个"路由型事件接收器"，类型参数只记录主体类型供派发检查，不暴露主体的任何属性——事件负载才携带真正的主体。

**两张 WeakMap**：`carrierKeys`（事件载体 → 其路由键，`undefined` 键值用于区分"无键载体"与"非载体"）与 `scopeParents`（键 → 父键）。注释里有一句关键的话：**一张关系表同时驱动两个方向的嵌套语义**——注册视图向下（`ScopedLayers`）、事件准入向上（`scopeTarget`）。

**父链写入与检查**：`linkScopeParent` 沿 parent 链向上遍历，途中撞见自身就抛"会成环"错误；`bindScopeParent(key, parent)` 是一次性绑定——已有父键再绑直接抛错，重绑的唯一途径是它返回的 `ScopeParentBinding.rebind`，而这个 binding 只交给最初的绑定者。`scopeParentOf`/`scopeChainOf` 分别读单亲与全链（nearest-first）。

**Scope 与 createScope**：`createScope(ctx, key, options?)` 先按需绑父，然后 `ctx.plugin(scope)` 用一个共享的 no-op 插件铸造 fiber，`fiber.ctx.extend({ [kScope]: key })` 得到打标后的 scoped context。返回的 `Scope` 含三个成员：`ctx`（注册入口）、`rawDispose`（精确的 Cordis disposer，供有序组合 effect 使用）、`dispose()`（幂等共享同一个 Promise，内部 `quiesceFiber` 会在 dispose 之后继续排空 `fiber.inertia`，保证异步拆卸真正静止）。

**scopeOf 与 scopeTarget**：`scopeOf(ctx)` 读上下文最近继承的标签。`scopeTarget(base, key)` 是路由的心脏——它构造一个保留了 `base` 原有 Cordis filter 的载体，其 filter 逻辑为：先过 base filter；监听器上下文**未打标则全局准入**；打标则当且仅当标签等于派发键或其任一祖先时准入。标签在派发键**之下**则被排除——事件只向上流，永不向下。`isScopeCarrier`/`carrierKeyOf` 提供载体判定与键读取。

## 外部连接

图谱上本文件被 `store.ts`（`ScopedLayers`/`NamedEntries`/`AnonymousEntries`——分层注册存储）依赖，那是注册视图向下继承的数据结构落点。再往外，`core/tools` 的 scoped 注册与遮蔽、`subagent` 的子组合隔离、goal/session 的事件定向派发，都是 `createScope` + `scopeTarget` 这对原语的组合应用。文件头注释点名的典型场景：一个 standing composition（常驻组合）通过祖先键观察其下组合的每一个 agent 的事件——这正是"事件向上"语义的用途本身。

## 数据流

建立期：`createScope(ctx, key, { parent })` → 绑父（环检查）→ 铸 fiber → 打标 ctx。注册期：经 scoped ctx 注册的工具进入 `ScopedLayers`，读取时沿父链向下看层（子看见全部祖先层，同名时近层遮蔽远层）。派发期：事件发到 `scopeTarget(base, key)` 载体 → 载体 filter 逐一检查监听器 ctx 的 tag：无标签放行；有标签则查 `scopeChainOf(key)` 是否包含该标签 → 命中者收到事件。拆卸期：`dispose()` 共享排空 Promise，fiber 连同其注册一起消失。

## 设计决策

**不透明 object 键**：scope 身份 = 对象身份，天然防伪，与仓库"跨边界 id 一律品牌化（`Branded<B>`）、禁止裸 string"的立场同源——能被 `===` 比较的东西就不能被内容伪造。

**一张表两个方向**：注册向下与事件向上共用 `scopeParents`，而不是分别维护两套结构。好处是不存在"继承关系与冒泡关系不一致"这类状态——它们定义上就是同一条链的两种走法。

**一次性绑定 + 特权 rebind**：祖先关系不可被任意后来者挪动。`rebind` 的 JSDoc 写明了前置契约：仅当旧父之下没有保留任何产物时才可重链（blank-session recompose 场景），且"本关系看不到 session 记录了什么"，所以契约由持有者自律遵守。这是典型的"把不可静态保证的契约写在唯一入口的文档上"。

**WeakMap 承载关系**：键与载体都可被垃圾回收，作用域元数据不产生泄漏。

**fail-loud 的环检查**：所有链消费者（`scopeChainOf`、filter 遍历）都向根走，环意味着死循环，因此在唯一的写入点（bind/rebind 共用 `linkScopeParent`）就拒绝。

## 新人提示

读这个文件前先在纸上画一条父子链，把两条口诀写在旁边：**"注册向下、事件向上"**。排查"为什么我的监听器收到了别家作用域的事件"时，第一反应应该是查监听器 ctx 的 tag 是否落在派发键的祖先链上，而不是怀疑业务代码；排查"为什么看不见某层注册"时反过来查父链方向。两个工程细节值得记住：拆卸一律用 `Scope.dispose()`（幂等且会排空 fiber 惯性），只有嵌进有序组合 effect 时才碰 `rawDispose`；`scopeTarget` 的"未打标监听器全局准入"意味着全局调试监听器不需要懂任何作用域——这是刻意留给观察者的便利通道。
