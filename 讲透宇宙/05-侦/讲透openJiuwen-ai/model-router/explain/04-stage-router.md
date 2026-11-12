# 04 · crates/algorithms/src/stage_router/mod.rs：唯一真实算法（与五个同构 stub 的真相）

## 一、角色定位：Rust 内核里唯一"动真格"的决策逻辑

先钉一条必须写明的勘误：**仓里名叫"路由算法"的 Rust 实现有六个，但只有 stage_router 是真实算法；另外五个（weighted / ensemble / rule_cascade / signal / passthrough）是同构 stub。** 证据链：`test_algo/routing/weighted.rs:5` 注释"骨架阶段退化为直通，权重表后续注入"；ensemble、rule_cascade、signal 三个文件的 doc 注释逐字相同（"骨架阶段退化为直通"），且 `decide` 函数体与 passthrough 完全一致——都是 `ctx.targets.without(&request.exclusions)` 后 `available.first()`（如 `weighted.rs:14-15`、`rule_cascade.rs:14-15`）。唯一区别是 `name()` 返回值和 reasoning 字符串里的算法名。passthrough 本身是"真身"（它的语义就是选第一个），其余四个是**占位注册项**——为了证明 registry 的多算法分派机制而存在。

于是 `stage_router/mod.rs`（688 行，全仓最大单文件）承担了全部真实智能：一个**无状态的阶段感知路由器**，通过分析编码代理（coding agent）的对话历史，判断当前处于"简单任务/收尾阶段"还是"高难任务/救火阶段"，在 efficient 与 capable 两档模型间切换。它的模块注释（`mod.rs:162`）自称"Stateless default Stage Router: efficient-first and signal-only fall-open"——两个关键词：默认选便宜档（efficient-first），信号不足时敞开回落到便宜档（fall-open）。

设计原型与 Switchyard 一脉相承（`decision.rs:1` 提及 Decision 字段与 Switchyard 同构），这是 Anthropic 的 context-engineering 路由思想在 Rust 里的独立实现。

## 二、内部结构：一张两级决策的流水线

### 入口 decide（mod.rs:170-195）

```rust
let efficient = ctx.targets.first().ok_or(RouterError::NoTarget)?;
let Some(capable) = ctx.targets.models.get(1) else {
    return Ok(Decision::answer(efficient, "stage_router: only available target"));
};
```

**位置即语义**：第一个目标是高效模型、第二个是能力模型——这是与配置的硬约定（`config/stage_router.toml:1-2` 注释"第一个目标是高效模型，第二个目标是能力模型"，models 顺序 `["efficient-model", "capable-model"]`）。只有单目标时直接选它（L172-176）。

然后是三步纯函数管线：`observe_history(request, DEFAULT_POLICY)` 产出快照 → `assess_stage(&snapshot, DEFAULT_POLICY)` 产出评估 → 按 tier 映射到模型名，reasoning 携带 `source={basis} score={:.3} confidence={:.3}`（L186-194）。

### 观察器 observe_history（L365-417）

一次遍历 `request.messages`，收集五个信号：

- **conversation_depth**：非 system/developer 的消息计数（L372-374 有测试钉死：`system_and_developer_messages_do_not_inflate_depth`，L665-679）。
- **context_was_compacted**：任何消息内容含 `"session is being continued"`（COMPACTION_MARKER，L12）即置位（L375-378）——上下文被压缩过意味着会话已长到失控，是需要强模型的硬信号。
- **recent_results**：最近 `history_window=3`（DEFAULT_POLICY，L21-25）条 tool 角色消息的文本内容，用 `retain_latest` 滑窗维护（L380-386、L419-427）。
- **recent_operations**：最近 3 次 assistant 的工具调用分类（L387-395）。
- 汇总：`failure_pressure` 取窗内**最大**失败权重（L398-401，不是求和——一次 critical 就够）；`clean_test_run` 是 any 判定（L402-404）。

### 失败签名表 FAILURE_SIGNATURES（L32-96）

10 组字面量子串匹配（先 `to_ascii_lowercase` 再 `contains`，L445-452 的 `failure_weight`），三档权重：CRITICAL=1.0（out of memory / connection refused）、HARD=0.7（traceback / importerror / command not found / assertionerror / valueerror / syntaxerror / timeout / filenotfound）、SOFT=0.3（exit code 1 等非零退出）。匹配英文错误文本——这是为英文工具链生态写的签名表，中文错误信息会漏检（潜在坑）。

### 工具分类词表（L98-160）

`operation_kind`（L454-485）把 ToolCall 分为 Write/Edit/Read/Plan/Other 五类：先按工具名精确匹配（WRITE_TOOLS 是 write/create_file/new_file/write_file 一组，L107；EDIT_TOOLS 七个别名，L98-106），SHELL_TOOLS（bash/shell 等，L110-116）命中后再按 `command` 字段的**前缀子串**二次分类（SHELL_WRITE 的 `cat >`/`<< 'eof'` heredoc 系列，L117-131；SHELL_EDIT 的 `sed -i`/`perl -i` 系列，L132-142；SHELL_READ 的 `cat /`/`grep ` 系列，L143-146）。这套词表覆盖了主流编码代理工具命名（Edit/MultiEdit/TodoWrite/Bash...），是整个算法里最"经验密集"的资产。

### 评估器 assess_stage（L324-363）：两级短路 + 证据打分

1. **安全覆写**（L325-332）：`requires_capable_model` = 压缩过 或 failure_pressure ≥ 1.0（L243-245）→ 直接 Capable，basis=override，confidence=1.0。
2. **已验证完成**（L333-340）：`represents_completed_work` = 干净测试通过 + 有产出（writes+edits>0） + 零失败压力（L247-249）→ 直接 Efficient，basis=tests_passed。
3. **证据打分**（L342-363）：四维 EvidenceVector（L252-258）——`failure`（压力值）、`stalled`（深会话+零产出+非调查中）、`investigation`（深会话+零产出+调查中，即只读不写）、`delivery_ratio`（产出/总操作）。合成公式（L275-279）：

$$\text{score} = \tanh\big(5.0 \times 0.10 \times (\frac{failure}{0.7} + stalled + investigation - delivery\_ratio)\big)$$

   confidence = |score|。confidence ≥ floor(0.5) 时：score > 0 → Capable（麻烦多），否则 Efficient（交付顺畅）；confidence 不足 → fall_open 选 Efficient。

tanh 把无界证据压到 (-1,1)，SCORE_GAIN×EVIDENCE_WEIGHT = 0.5 的缩放让"单一维度满值"恰好到 tanh(0.5)≈0.46——**单一证据不足以越过 0.5 的置信门槛**，必须两维以上叠加才升级，这是内建的保守性。

### 测试结果判定（L491-532）

`is_clean_test_result` 的精妙在否定条件的分层：命中通过短语（" passed"/"test result: ok"/"✓ " 等，L147-158）且不含失败字面量（"✗"/"fatal:"，L159）且**没有紧邻数字的失败关键词**（L498-514 的 `has_counted_failure`：找 "failed" 前面紧贴的数字，`count_immediately_before` 反向收集连续 ASCII 数字，L516-532）。于是 "25 passed in 1.2s" 干净、"2 failed, 5 passed" 不干净、"8 passed; 0 failed" 干净（零失败仍算干净，测试 L641-643 钉死）。

### 测试覆盖（L579-687）

12 个单测覆盖了每条决策路径：空历史 fall_open、critical 覆写、压缩覆写、相关错误+探索升级、测试通过后降档、失败不触发 tests_passed、滑窗纪律、深度不掺水、单目标兜底。这套测试就是算法的行为规格书。

## 三、外部连接

- **上游**：`mod.rs:1-5` 只引入 std 的 VecDeque 与 protocol 的五个类型 + 本 crate 的 `AlgorithmProvider, RouteContext`。零第三方依赖、零 state 依赖——它的全部输入就是 request.messages 与 ctx.targets。
- **注册**：`runtime/src/registry.rs:20-21`，`"stage_router"` 名字挂在 `#[cfg(feature = "algo-stage_router")]` 下（algorithms/Cargo.toml:14-22 与 runtime/Cargo.toml:21-22 透传，默认全家桶里都开）。
- **装配**：`Router::from_profile` → `registry::create_algorithm("stage_router")`；`router.rs:364-380` 的测试 `stage_router_assembles_from_profile` 完整走了一遍 TOML → Router → route 链路。
- **被消费的语义约定**：`decide_loop` 给它的 `ctx.targets` 已剔除 exclusions——若 capable 被状态排除，列表塌缩成单元素，L172-176 的单目标分支接住，退化为永远选 efficient。
- **对位关系**：Python 侧 x-router 是它的同类（真实算法），但走 Python 注册表（py/lib.rs:100-103 Python 优先）；五个 stub 的 Python 同名版本在 `python/openjiuwen/test_algo/`（cost_aware.py 等，供 Python 侧对照实验）。

## 四、数据流：一条真实轨迹

编码代理第 N 轮请求，messages 含：user 任务 → assistant 调 Bash(`sed -i ...`) → tool 返回 "Traceback (most recent call last)..." → assistant 调 Read → tool 返回文件内容 ×8 轮深度：

1. `observe_history`：depth=10（≥ stall_depth 8）；recent_results 窗口 = [traceback 文本, 文件内容, ...]，traceback 命中 HARD=0.7 → failure_pressure=0.7；recent_operations 窗口 = [Edit(sed -i), Read]，activity={edits:1, reads:1}；
2. `assess_stage`：无压缩、压力 <1.0 → 不覆写；无干净测试 → 不是 completed_work；进证据打分：failure=0.7, stalled=0（有产出）, investigation=0（depth 够但 production≠0）, delivery_ratio=1/2 → combined = 0.7/0.7 + 0 + 0 - 0.5 = 0.5 → score=tanh(0.5·0.5·2)=tanh(0.5)≈0.462 < 0.5 → fall_open 选 efficient；
3. 若再来一次 timeout（0.7）叠加上一轮：窗口最大压力仍 0.7，但若同时零产出深会话 → stalled=1 加入 → combined=1+1=2 → score=tanh(1.0)≈0.762 ≥ 0.5 → Capable，reasoning=`source=dimensions score=0.762 confidence=0.762`。

整个判定只消费 messages 文本与工具名——不调模型、不看 state、不记历史，每次路由从请求自带的上下文独立推断。

## 五、设计决策与权衡

**为什么无状态？** 严格贴合算法槽的纯函数契约：同样的对话历史永远得到同样的档位。代价是它看不到"上一轮路由选了谁、效果如何"——那是 state 层与反馈闭环的职责。它事实上把"状态"外包给了对话本身：messages 就是编码代理最完整的状态载体，何必再造一份。

**为什么 fall-open 到 efficient 而不是 capable？** 成本不对称：错选 cheap 的代价是一次可能平庸的回答 + 宿主重试升级；错选 expensive 的代价是每一轮都贵。安全覆写通道（压缩/critical）保证了真正的危险场景不会漏——fall-open 只在"证据不足"时发生，不是"出事时"。

**为什么 failure 取 max 不取 sum？**（L398-401）一次 critical（1.0）就该触发覆写；求和会让三条 SOFT(0.3×3=0.9) 虚增压力。窗口语义是"最近发生过什么级别的事"，不是"累计多惨"。

**为什么签名表用子串不用正则/模型？** 零依赖、可审计、O(n·m) 可预测。错检（用户消息里恰好含 "valueerror:"）的后果有限——最多升一档；漏检（非英文错误）同理只降质。这是与 x-router 路线（本地 0.6B 分类器）的鲜明对照：**词表路由 vs 模型路由**，本仓两条路线并存。

**砍掉了什么？** 无 per-session 记忆、无成本/延迟输入（TargetSet 只有名字没有价格表）、硬编码 DEFAULT_POLICY（`StagePolicy` 结构已抽象出 window/floor/stall_depth 三参，但没有接配置——为未来 TOML 化留的口）。

## 六、新人提示与坑

1. **五个 stub 别当真**：weighted/ensemble/rule_cascade/signal 的 reasoning 字符串自带坦白（"stub, falls back to first target"，`weighted.rs:17-19`）。读仓或写文档时别被名字骗去分析"权重策略"——不存在。test_algo/mod.rs:1-4 说它们是"与 Python test_algo 包同名同功能的骨架实现"，磁盘保留、按 feature 可裁。
2. **目标顺序是协议的一部分**：stage_router.toml 的 models 顺序错了，算法静默选错档——没有任何运行时校验第一个必须是 efficient。
3. **签名表英文中心**：中文/本地化错误输出（"内存不足"）不命中任何签名，failure_pressure 恒 0。给中文宿主用要扩表。
4. **`contains` 的子串陷阱**：`"not found\n"` 带 `\n`（L55）是为了避开 "command not found" 已被更高档捕获的歧义；改词表时注意这些精心挑选的边界。
5. **depth 计数包含 tool 消息**：L372-374 只排除 system/developer，tool 结果一条算一条——长工具输出会加速触达 stall_depth，这是有意的（长会话本身是复杂度信号）。
6. **policy 不可配**：`history_window=3 / floor=0.5 / stall_depth=8` 写死在 `DEFAULT_POLICY`（L21-25）。想调参要么改代码重编译，要么 fork 本文件——`StagePolicy` 的存在暗示了配置化的意图，但尚未接线。
