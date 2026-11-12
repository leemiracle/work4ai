# 01 · compilercore_analysis.cpp —— MDL 编译器的语义分析心脏

> 文件：`src/mdl/compiler/compilercore/compilercore_analysis.cpp`（19019 行，图谱 143 子节点，编译器核心线第一大文件）
> 配套头：`src/mdl/compiler/compilercore/compilercore_analysis.h`（`class Analysis` 声明于 L104，`class NT_analysis` 声明于 L894）

## 1. 角色定位

MDL 编译器前端分三步：词法/语法解析（产出 AST）→ **语义分析（本文件）** → 代码生成。本文件实现的是中间那一步：拿到 parser 吐出的语法合法但"含义未定"的 AST，把每个名字绑定到 Definition、给每个表达式定类型、解析所有重载、做常量折叠、校验语言规则（禁止递归、参数类型限制），并收集全部编译错误与警告。它在 `mi::mdl` 命名空间（L68-69）内——后续一切 DAG 代码生成、蒸馏、JIT 都建立在它产出的语义完整的 `Module`（definition table + messages）之上。

文件里其实有两层类：基类 `Analysis`（错误报告、名字查找、限定名解析等通用工具）与派生类 `NT_analysis`（name/type analysis，真正遍历 AST 的 pass）。调用方是 `compilercore_modules.cpp:357` 的 `NT_analysis nt_analysis(m_compiler, *this, *ctx, cache);`——模块加载器在解析完成后立即构造它跑分析。

## 2. 内部结构

匿名命名空间里的辅助类（按行号）：

- `Default_initializer_modifier`（L993）：clone 声明时重写默认参数初始化器，处理导入模块时的惰性求值。
- `Let_temporary_modifier`（L2016）：clone 时把 let 表达式转成 temporary。
- `Imported_module_cache`（L2113）：实现 `IModule_cache`，缓存已加载的被 import 模块，防止循环 import 重复编译。
- `Levenshtein_matcher`（L2798）：编辑距离拼写建议器，"did you mean" 功能的实现基础。
- `Parameter_modifier`（L3964，MDL_FINAL）：clone 函数时重写参数。
- `Reference_replace`（L17803）：文件尾部的 `Module_visitor`，把对延迟导入实体的引用替换成正式导入后的新 Definition。

`Analysis` 基类方法群（实现在 L2187-3416 + L5575-5782）：

- `import_definition`（L2187）/`get_import_location`（L2200）：导入实体的 Definition 改写与位置追溯。
- `error`（L2419）/`error_strict`（L2457）/`warning`（L2470）/`add_note`（L2494）：四级消息体系；错误码表在 compilercore_errors.h，`MESSAGE_CLASS = 'C'`（头文件 L182）标记编译器类消息。
- `get_lvalue_base`（L2534）/`get_result_type`（L2584）：左值链与函数结果类型推导。
- 内嵌类 `Const_fold_expression`：实现 `IConst_foldHandler` 四回调——`exception`（L2606，常量折叠越界/除零转错误）、`lookup`（L2668，查常量变量值）、`evaluate_intrinsic_function`（L2685，求值内建函数）。
- `find_best_match`（L2980）：用 Levenshtein_matcher 给未命中名字挑最近候选。
- `find_definition_for_qualified_name`（L3038）：`::a::b::c` 限定名沿 scope 链解析，名字查找总入口。
- `is_const_expression`（L3222）/`is_const_array_size`（L3398）/`qualify_type`（L3416）：常量性与 const/uniform/varying 限定。

配套注册表：`Operator_lookup_cache`（L3486，操作符重载查找缓存）、`Auto_imports`（L3517，弱导入自动补登记表）。

`NT_analysis`（L3550 起构造，`public Analysis, ICallgraph_scc_visitor` 双继承——头文件 L894）方法群分四组：

**声明处理（enter/declare）**：`enter_builtin_constants`（L3676）/`enter_builtin_annotations`（L3690）/`enter_builtin_categories`（L3803）/`enter_stdlib_constants`（L3857）先灌内建符号；`load_module_to_import`（L4429，处理 `::` 绝对名、namespace 别名、MDL 1.6 起废除的 weak import L4465-4477）；`import_entity`（L5057）；`declare_function`（L6757）/`declare_material`（L7675）/`declare_material_preset`（L8096）。

**visitor 派发**：约 20 个 `pre_visit(IDeclaration_*)` 重载接管每种声明节点——import L12232、constant L12322、annotation L12575、type_enum L12848、parameter L13366、function L13435 等；表达式侧 `post_visit(IExpression*)` 群在 L14354-15124。

**类型/重载核心**：`find_implicit_conversion`（L9041）→`create_type_conversion_call`（L9058）→`convert_to_type_implicit`（L9103）/`convert_to_type_explicit`（L9141）；`resolve_overload`（L9840，评分制主战场，L9904-9910 的 3/2/1 打分：精确匹配 +3、可隐式转换 +2、需显式转换 +1）；`find_overload`（L10239）与 `is_more_specific`（L9469）/`kill_less_specific`（L9516）决胜；`bind_array_type`（L9608）绑定 deferred 数组尺寸；`calc_mdl_versions`（L9387）定模块版本。

**收尾校验**：`handle_known_annotation`（L15775）、`check_enable_if_condition`（L16476）、`handle_cast_expression`（L17018）、`update_call_graph`（L17312）、`process_scc`（L17393，报 RECURSION_CALL_NOT_ALLOWED 并打印递归链 L17407-17419）、`check_called_functions`（L17430）。

## 3. 外部连接

include 三层（L33-59）：公共接口 `<mi/mdl/mdl_expressions.h>` 等；compilercore 同伴 `compilercore_def_table.h`（Definition 表）、`compilercore_builder.h`（Module 构造器）、`compilercore_errors.h`、`compilercore_factories.h`。上游 caller 是 `compilercore_modules.cpp`（模块加载流水线）；产物 `Module` 被 `compilercore_optimizer.cpp` 与下游 generator_dag、distiller 消费。SCC 检测走 `ICallgraph_scc_visitor` 接口。

## 4. 数据流

输入：parser 的 AST（`IDeclaration_*` 树）+ `Module_cache`（被 import 模块）。变换：① 内建符号灌表（L3676-3857）→ ② 逐声明 `pre_visit` 建 Definition 与 scope（含 import 改写 L4429）→ ③ 表达式 `post_visit` 做类型检查、隐式转换插入（L9103 在表达式树上原地改写为 `IExpression_call` 转换节点）、常量折叠（Const_fold_expression）、重载裁决（L9840）→ ④ call graph 构建 + SCC 遍历拒绝递归（L17312-17427）→ ⑤ 未用函数/材质警告（`check_used_function` L17349）。输出：语义完整的 `Module`（Definition 表带类型/flags/常量值）+ `Messages_impl` 错误列表。

## 5. 设计决策

- **visitor 双相（pre/post）而非单趟递归**：声明必须先于表达式可见（前向引用），pre_visit 建 skeleton、post_visit 填语义，是符号表两遍法的标准落地；对比单趟手写递归下降，可维护性高得多。
- **错误恢复而非 fail-fast**：`IType_error`（L9877 跳过坏候选）与 error Definition（L3211）让编译器在报错后继续收集更多错误——编译器 UX 优于一次性失败。
- **评分制重载**（L9904-9910）：3/2/1 三档分数 + `is_more_specific` 决胜，比 C++ 的 partial ordering 简单且可解释，与 MDL"小语言"定位匹配。
- **SCC 禁递归**：MDL 是无递归语言，编译期拒绝（L17393）而非运行时栈检查，保证后端可以安全做 aggressive inline 与 DAG 化。
- **Levenshtein 建议**（L2798）：拼写错误的修复体验，开源编译器（rustc 同款思路）的标配。

## 6. 新人提示

- 调试入口：`dump_enable_positions`（L46）+ dump_ast；错误码语义查 compilercore_errors.h，'C' 区分编译器/后端消息。
- `pre_visit` 返回 false 可剪枝整个子树（annotation block 即此模式）。
- 改重载规则先读 L9884-9957：`min_params`、named args、preset（L9851 `m_preset_overload`）三态都要兼顾。
- import 语义坑：MDL 1.6 前的 weak import（L4465）决定找不到模块是错误还是静默；namespace 别名可指绝对路径（L4453-4463）。
- 相关文件：compilercore_def_table.h（Definition）、compilercore_builder.h（Module 构造）、下游 generator_dag_generated_dag.cpp（本系列第 3 篇）。
