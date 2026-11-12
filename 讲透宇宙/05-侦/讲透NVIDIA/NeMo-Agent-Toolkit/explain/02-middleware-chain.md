# 02 中间件体系：洋葱圈协议与 security 防线复用

## 一、角色定位

NAT 把工作流里的可调用单元（工具函数、LLM、workflow）都视为"函数"，中间件是套在函数外的可组合包装。源码定位见 `middleware.py:17-20`："Middleware works like middleware in web frameworks"——Web 洋葱圈向 agent 编排域的移植。它承载全部横切关注点（缓存/熔断/超时/日志/HITL/动态拦截/security 攻防）；函数本体纯粹，横切能力在 `builder/function.py:133` 装配成链。

## 二、内部结构

### 协议层 middleware.py

`FunctionMiddlewareContext`（`middleware.py:46`，frozen dataclass）存被包装函数静态元数据；`InvocationAction`（`middleware.py:73`）是意图枚举，仅 SKIP（L83）；`InvocationContext`（`middleware.py:87`）统一 pre/post 两阶段——frozen 组 original_*（L103-106）与 mutable 组 modified_*/output/action（L109-112）。`Middleware(ABC)`（`middleware.py:118`）三个抽象成员 `enabled`（L157）/`pre_invoke`（L163）/`post_invoke`（L192），外加默认直通的 `middleware_invoke`（L237）与 `middleware_stream`（L273）。

### 编排层

`FunctionMiddleware`（`function_middleware.py:48`）给默认实现（enabled 恒 True，L94）。骨架 `function_middleware_invoke()`（L149）：构造上下文（L177）→ pre_invoke（L187）→ `action==SKIP` 短路返回 None（L191）→ `is_final` 不再下传（L195）→ `call_next`（L199）→ post_invoke（L202）。流式版（L208）：pre 开流前一次（L251），post 逐 chunk（L263），`ctx.output is None` 是压制哨兵（L273）。`FunctionMiddlewareChain`（L277）组装洋葱圈：`build_single()`（L303）/`build_stream()`（L334）从 `reversed()` 逐层闭包（L316），第一环最外层，禁用环由框架跳过（L318）。`validate_middleware()`（L367）守门：同实例去重（L384）、final 至多一个且在链尾（L395）。

### 实现层：六族与 security

- cache：`CacheMiddleware`（`cache_middleware.py:48`），构造 `is_final=True`（L93）——全库唯一默认 final，命中即终结整链；覆写 L169；配置 `cache_middleware_config.py:24`。
- circuit_breaker：`circuit_breaker_middleware.py:64`，状态机 L45。
- dynamic：`DynamicFunctionMiddleware`（`dynamic_function_middleware.py:42`），构造带 `builder`（L48），是"持有 builder 的枢纽族"：`_discover_and_register_*` 系列（L131/L367）运行时发现并拦截其他组件，`_should_intercept_*` 谓词（L431）选择性挂链。
- hitl：`HITLMiddleware`（`hitl_middleware.py:29`），含抽象回调（L48）；`pre_invoke`（L84）配了 prompt（`hitl_middleware_config.py:31`）时向人类发问。
- logging：`logging_middleware.py:26`；timeout：`timeout_middleware.py:34`（覆写 L46）；`common.py` 仅 `TargetLocation`（`common.py:19`，INPUT/OUTPUT）。
**勘误**：任务书"六族均为实现+config+register 三件套"与源码不符。`middleware/register.py:18-22` 只导入五族 register；`hitl/` 无 register.py，HITLMiddleware 不进 YAML 注册体系，核心包内仅测试实例化（`test_hitl_middleware.py:46`），是供继承的抽象层；examples/HITL 把审批做成普通函数（`hitl_approval_tool.py:32`）供 agent 循环调用（`retry_react_agent.py:167`）。

security 三线复用中间件形态：defense 基类 `DefenseMiddleware(FunctionMiddleware)`（`defense_middleware.py:122`，`is_final=False` 于 L158）四件套——PII（`defense_middleware_pii.py:66`，post_invoke L239）、输出验证器（`defense_middleware_output_verifier.py:70`）、预校验器（`defense_middleware_pre_tool_verifier.py:93`，拦截 `raise ValueError` 于 L363）、内容守卫（`defense_middleware_content_guard.py:61`）；red_teaming（`red_teaming_middleware.py:48`）以 `target_location`（`red_teaming_middleware_config.py:83`）消费 TargetLocation；guardrails 见 `nemo_guardrails_middleware.py:57`。

## 三、外部连接

- **builder/function.py 是唯一装配点**：`configure_middleware()`（L133）构造 Context（L146）、Chain（L153）、`build_single/build_stream`（L155）；无中间件回退裸函数（L200）；FunctionGroup 组级 middleware 下放全员（L508-509）。
- **YAML 体系**：顶层 `middleware: dict`（`data_models/config.py:284`）定义命名中间件，函数/组按名引用（`data_models/function.py:39-41`）；样例 `config-with-defenses.yml:50` 与 L22。
- **注册机制**：`register_workflow.py:337` 把配置类型登记进 `GlobalTypeRegistry`（`type_registry.py:1423`），register.py 挂接见 `cache/register.py:22`。
- **eval/inventory**：scenario 可附加中间件（`red-teaming-with-defenses.yml:69`）；`WorkflowInventory`（`workflow_inventory.py:124`）为发现协议词汇表。

## 四、数据流

以 retail 链（PII 挂输出侧）一次单输出调用为例：装配期 `builder/function.py:145` 打印链序，`build_single` 反向闭包使先配置者包最外层；每环经委托层（`function_middleware.py:130-136`）进入编排，pre 阶段 PII 因配在输出侧放行（`defense_middleware_pii.py:248`）；`call_next`（L199）逐环穿透到工具本体——任何环改写的 `modified_args` 即内层实参；输出回程逐环过 post_invoke，PII 在此改写 output，red_teaming 注入攻击 payload。短路两条：pre 阶段 `action=SKIP`（`hitl_middleware.py:62`）全跳过返回 None；final 链头（cache 命中）不穿透。流式则 pre 一次、post 每 chunk 一次，被置 None 的 chunk 静默消失。

## 五、设计决策

1. **frozen original + mutable modified 双轨**（`middleware.py:103-112`）：original 不可变供审计，修改只写 modified。
2. **意图挂 context 而非返回哨兵**：SKIP 是字段不是特殊返回值（L74-81），钩子返回值语义单一；代价是枚举仅一个成员。
3. **None 双重语义**：单次调用 SKIP 短路返回 None（L191）；流式 post 置 None 是 chunk 压制（L273）。
4. **final 强约束**（`function_middleware.py:393-401`）：final 即"可选替换执行者"；cache 是唯一默认 final（L93）。
5. **双层 invoke 委托 + enabled 框架检查**：通用 `middleware_invoke` 默认转调 `function_middleware_invoke`（L130-136），族只覆写后者；enabled 在 build 时过滤（L318）。
6. **DynamicFunctionMiddleware 是权限枢纽而非功能**：持有 builder 即持有组件世界（L48），circuit_breaker/logging/timeout/hitl/guardrails 皆从它派生；cache/defense/red_teaming 无 builder。
7. **安全防线复用中间件而非另造层**：pre/post 恰对应"进前拦/出后查"（INPUT 走 pre、OUTPUT 走 post，`defense_middleware_pii.py:248` 即此映射）。

## 六、新人提示

- 先读 `builder/function.py:133` 装配现场，链行为 90% 由装配逻辑而非协议层决定；链序错在 validate（L367）当场抛错。
- 自定义中间件最小路径：继承 FunctionMiddleware 实现 enabled/pre/post（默认见 `function_middleware.py:94`），YAML 化仿 `cache/register.py:22` 并在 `middleware/register.py:18-22` 追加导入；"替函数做决定"则覆写 `function_middleware_invoke`（样例 `cache_middleware.py:169`）。
- 继承 HITLMiddleware 须实现两个抽象回调（`hitl_middleware.py:48`），且不走 register 通道（见勘误）。
- 流式中间件慎用 None：置 `ctx.output = None` 会吞 chunk（L273），要输出 None 值就包一层。
