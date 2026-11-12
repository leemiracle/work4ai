# xgrammar-fsm — 状态机族：构建、确定化与最小化（fsm.cc / fsm_builder.cc）

## 角色定位

这对文件构成 **cpp-compiler 层的自动机引擎**。`fsm.cc`（1996 行）定义 FSM 完整数据结构与四个核心算法（epsilon 化简、等价状态合并、NFA→DFA 确定化、DFA 最小化）；`fsm_builder.cc`（1797 行）名字易误导——它不是通用 builder，而是**正则表达式→FSM 的编译器**外加 tag trigger 的 trie FSM 构建，服务 GrammarFSMBuilder 对 kRegex 叶子的编译与 kTagDispatch 触发串的自动机化。两者合答一个问题：怎么把字符级约束变成运行期 O(1) 转移的可查表结构。

## 内部结构

**fsm.h/cc 类型族**：边结构 `FSMEdge{min, max, target}` 极紧凑——`min>=0` 是字符范围边 `[min,max]`，`min<0` 是七种特殊边：kEpsilon（ε 转移）、kRuleRef（规则引用，max 存 rule_id）、kEOS（接受 EOS）、kRepeatRef（重复引用，aux 存 `[rule_id, lower, upper]`，该状态仅此一条出边）、kToken/kExcludeToken（token 集合边/补集边，aux 存 `[count, id...]`）。容器两套：`FSM` 用 `vector<vector<FSMEdge>>` 邻接表（构建期可变），`CompactFSM` 用 `Compact2DArray`（CSR 式紧凑布局，运行期缓存友好），`ToCompact()` 转换；共享 `FSMImplBase<ContainerType>` 模板基类，Advance/GetEpsilonClosure 等算法只写一遍。外面包 FSMWithStartEnd / CompactFSMWithStartEnd 记录起止状态。

**四个算法**（fsm.cc）：`SimplifyEpsilon`——两条并查集合并规则消 ε 边（"a 仅一条 ε 出边且 a 非终止或 b 终止则并"、"a→ε→b 且 b 入度 1 则并"），保持接受语义；`MergeEquivalentStates`——出入边等价类合并；`ToDFA`——子集构造，字符范围边切成不交区间分桶，ε 闭包合并状态集，超 `max_num_states` 即报错防爆炸；`MinimizeDFA`——Moore 式分区细化，先按终止/非终止二分，工作队列用前驱边反复切细到不动点，最后 RebuildWithMapping 重编号。

**fsm_builder.cc 三块**：① RegexIR（正则解析中间表示，含字符类 `[...]` 解析、`\d\w\s` 类逃逸、大小写折叠、区间归一）；② `AddPackedUTF8RangeEdges`——Unicode 码点区间展开成 UTF-8 字节序列边（`CodepointToPackedUTF8` 打包比较，一个码点区间对应多条不同长度前缀的字节路径），多字节正确性的关键；③ TrieFSMBuilderImpl——为 tag trigger 串集合建 trie FSM 并 AddBackEdges（Aho-Corasick 式失配回边），多模式并行匹配。

## 外部连接

上游 GrammarFSMBuilderImpl 对每条规则调用这里编译成 FSMWithStartEnd；kRegex/kSubstring 叶子在 FSM 构建期走 `Regex()` 编译入口（失败返回错误而非抛异常）。下游产物存进 `per_rule_fsms` 与 `complete_fsm`，被 earley_parser（运行期 Advance）和 grammar_compiler（枚举 scanable 状态）消费；`suffix_automata.cc` 是姊妹件，把 kSubstring（子串约束）编译成后缀自动机。`tests/cpp/test_fsm.cc`、`test_fsm_builder.cc` 直接守护本对文件。

## 数据流

以 `rule ::= ("a" [0-9])+` 为例：GrammarFSMBuilder 遍历规则体——字节串 "a" 变两个状态一条范围边，字符类变一条范围边，`+` 用自环表达 → 得到的 NFA 先 SimplifyEpsilon 折叠 ε 链 → ToDFA 确定化（同字符至多一个目标）→ MinimizeDFA 压状态数 → ToCompact 转 CSR 存进 `per_rule_fsms[rule_id]`。运行期 `CompactFSM::Advance(state, byte)` 就是查一行有序边数组，O(d) 出结果。

## 设计决策

- **七种特殊边而不是预处理掉**：规则引用边表达"引用而未内联"的递归结构（真递归交给 Earley）；token 边直接支持 kToken/kExcludeToken；EOS 边统一"何时允许停止"语义。
- **状态数上限贯穿所有算法**：病态正则（嵌套量词）会让 DFA 指数爆炸，超限优雅降级。
- **双容器（FSM/CompactFSM）**：构建期可变、运行期紧凑，模板基类零重复；CSR 化后转移 cache miss 极少。
- **UTF-8 packed 边展开而非运行期解码**：多字节成本一次付清在编译期，运行期只见字节流。
- **trie+回边做多模式触发**：tag dispatch 要同时盯多个 begin/end 串，AC 自动机一遍扫描全搞定，配合"第二字符起确定接受" bitset 二次切片。

## 新人提示

先读 `fsm.h` 的 FSMEdge 注释块（边类型编码是理解一切的钥匙）；拿 `test_fsm.cc` 小用例纸上手推 ToDFA/MinimizeDFA。kRepeatRef 的"单出边不变式"违反它运行期会算错重复计数。改 SimplifyEpsilon 小心接受状态合并条件（注释写明为何"a 终止且 b 非终止不能并"）。正则支持范围看 RegexIR 枚举，别假设与 Python `re` 全兼容。所有算法带 max_num_states，新代码路径记得传。
