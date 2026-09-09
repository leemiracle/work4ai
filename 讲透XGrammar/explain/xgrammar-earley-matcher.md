# xgrammar-earley-matcher — 运行时校验与掩码生成（earley_parser.cc / grammar_matcher.cc）

## 角色定位

这对文件是**推理期核心**（cpp-runtime 层）：每个生成的 token 都经过它们。`earley_parser.{h,cc}`（802+1272 行）实现 Complete/Predict/Scan 三操作的 Earley 解析器——per-rule FSM 管规则内字符匹配，Earley 管规则间栈式调度（递归引用无法平面 FSM 化）；`grammar_matcher.cc`（2774 行）封装完整推理语义：逐 token 接受/回滚、产出下一 token 位掩码、投机解码草稿树、预算强制、捕获组、jump-forward。Python 侧 GrammarMatcher/BatchGrammarMatcher 是轻壳。

## 内部结构

**ParserState**（earley_parser.h）是全库最核心的数据结构之一：五元组 `(rule_id, sequence_id, element_id, sub_element_id, active_temperature_rule_id)` 加预算字段（budget_deadline / char_budget_deadline / repeat_count / rule_start_pos），压缩表达"语法推导当前位置"。它同时是 mask 缓存的键（StateHashForCache 忽略位置字段）——同一语法位置在不同上下文共享同一份预计算掩码。

**EarleyParser** 把状态分三类管理（头部注释引 Wikipedia 伪代码）：scanable（可扫描下一字符，存进按输入位置分行的 `scanable_state_history_` 历史栈）、predictable（进按 rule_id 索引的 completable 表）、completable。推进一字节 = Scan 当前行 + 级联 Predict/Complete 到不动点；回退 = `PopLastStates(n)` 弹历史栈行尾。推理期扩展：FSM 状态标志懒缓存、nullable 规则表、预算截止判定、UTF-8 码点计数历史、捕获事件历史（与状态栈逐行对齐，回滚自动撤销）。

**GrammarMatcher::Impl** 公共面：`AcceptToken`（先在 trial 副本上试推再真接受，失败状态不变）、`AcceptString`、`FillNextTokenBitmask(DLTensor*, index)`、`RollbackTokens(n)`、`AcceptStopToken`/`IsTerminated`、`GetCaptures`、`FindJumpForwardString`（贪心找下一必经字面量）。内部关键：`FillBitmaskForStates` 遍历当前 scanable 状态查预计算掩码，uncertain 用 lookahead/父状态实时消解后写入 DLTensor；token/字符预算强制（迭代到不动点）；投机解码 `TraverseDraftTreeRecursive` 是 DFS——根节点算掩码，子节点 AcceptToken 试探，成功则填掩码并下钻，超时剪枝。批量版走线程池。

## 外部连接

上游消费 CompiledGrammar::Impl（语法+FSM+mask 缓存）与 TokenizerInfo（sorted vocab/trie 范围）；`earley_parser.h` 同时被 grammar_compiler.cc 复用做编译期预计算。下游：bitmask 由 kernels 层套到 logits；Python 侧 matcher.py 直连；DLTensor 接口让掩码直接写进 torch tensor 内存。

## 数据流

一步典型生成循环：① 上一 token 采样得 tid；② `AcceptToken(tid)`——按解码字节逐个 Advance+Complete 级联；③ `FillNextTokenBitmask(mask, 0)`——遍历所有 scanable 状态查预计算掩码，多状态按位 OR 合并（任一路径允许即允许），uncertain 用当前栈上下文现场消解，写入 mask；④ 引擎把 mask 套上 logits 采样下一 token。回滚：RollbackTokens 弹状态栈 n 行（捕获/字符计数历史同步弹回）；fork 整栈复制。

## 设计决策

- **选 Earley 而非 LL/LR**：语法引导生成要求任意 CFG（用户 EBNF 可能左递归、二义），LL/LR 只覆盖真子集还要处理表冲突；Earley 天然容纳且支持部分匹配。最坏 O(n³)，但约束生成串短、重活已被 FSM 化+预计算搬走，Earley 只处理规则栈调度这层薄壳。
- **状态压缩进 int32 五元组**：语法位置可哈希、可比较、可做缓存键——掩码预计算因此可行。
- **trial-then-accept**：先副本试推失败不动真状态——强异常安全。
- **历史栈对齐设计**：scanable 状态、捕获事件、字符计数三套历史逐行对齐，PopLastStates 一次弹三表——回滚正确性由结构保证。
- **编译期/运行期同引擎**：mask 预计算类继承 EarleyParser，杜绝语义漂移。

## 新人提示

先读 earley_parser.h 头部 310 行（三类状态管理+ParserState 注释），对照 Wikipedia Earley 伪代码；再读 grammar_matcher.cc 的 AcceptToken（约 1203 行）与 FillNextTokenBitmask（约 1645 行）。调试用 `debug_print=True`。测试抄 test_grammar_matcher_basic.py 的 generate+accept+check 模式。FillNextTokenBitmask 的 index 是批内下标不是 token id。改预算逻辑跑 test_max_chars.py 与 test_speculative_decoding.py 回归。
