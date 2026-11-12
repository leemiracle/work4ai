# 10 · mdltlc：MDL Transform Language 编译器与 Coco/R→递归下降双解析器

## 1. 角色定位

`src/prod/bin/mdltlc/` 是 **MDLTL（MDL Transform Language）命令行编译器**（mdltlc.h:39 自述"The MDLTL command line compiler application"）。MDLTL 是 MDL distiller 的规则语言：形如 `pattern --> replacement` 的 DAG 重写规则，用于把任意 MDL 材质"蒸馏"成目标格式（如简化 BSDF 集合）。真实用例钉版：`src/shaders/plugin/mdl_distiller/dist_rules.mdltl:30` 起就是 `rules Reduce_1_4_to_1_3_rules topdown { fresnel_factor(ior,k,base) --> bsdf_tint(...); ... }`——同目录的 dist_rules_generated.cpp 即 mdltlc `--generate` 的产物，被 mdl_distiller 插件在运行时按策略应用。命令行选项里 `--plugin` 已是"legacy option, ignored"（mdltlc.cpp:74），编译器本体负责 mdltl→AST→DAG 规则→C++ 源码全链。本篇主角 `mdltlc_parser_rd.cpp`（1908 行）是**手写递归下降解析器**，头文件明言其使命："intentionally used in parallel with the Coco/R parser while the transition is in progress"（mdltlc_parser_rd.h:12-14）——它是 Coco/R 生成解析器（mdltlc_parser_coco.cpp）的替换候补，当前两者**双跑并比对 AST**。

## 2. 内部结构

三层经典布局。**词法**：`Token_kind` 枚举 84 个 token（mdltlc_parser_rd.cpp:44 起——除 ident/字面量/运算符外还有语言关键字 TK_BOTTOMUP/TK_TOPDOWN/TK_RULES/TK_MATCH/TK_POSTCOND/TK_DEADRULE 等）；`Token` struct 携带 line/column（:110）；`Scanner` 类（:206）手写扫描：`next()`（:221）先跳空白注释，再按首字符分派——标识符分支连 `::` 也吞进 ident（:244 的 `c==':' && peek(1)==':'` 判断，MDLTL 标识符允许限定名），数字/字符串/运算符各有专门扫描，错误就地 set_error（:609）。**语法**：`Parser` 类（:632）LA(1) 递归下降，构造时从 Compilation_unit 取表达式/类型/值/规则四个工厂与符号表（:643-648）；`parse()`（:652）顶层循环吃 `TK_RULES` 块直至 EOF。核心产生式链：`parse_rules()`（:753）= `rules <ident> <strategy> { imports* rule* postcond? }`，strategy 二选一 STRAT_BOTTOMUP/STRAT_TOPDOWN（与 mdltlc.atg:194-196 的文法一致）；`parse_rule()`（:836）的完整形状是 `node --> expr [repeat_rules|skip_recursion] [if|maybe guard] [where bindings] [debug_name] [debug_print]* [deadrule]? ;`——`-->` 是 TK_MAPSTO（:841-842），result code 区分"循环应用"与"剪递归"（:849-853），deadrule 标记死规则（:901-903）；`parse_where()`（:951）解析 where 绑定，临时名靠 `m_gensym_counter` 生成（:1126/:1886）；postcond 是独立的三层布尔表达式解析器（or :1796 → and :1815 → primary :1834）。入口 `mdltlc_parse_rd()`（:1891）是文件末尾的唯一公开函数。**文法母本**：mdltlc.atg 是 Coco/R 属性文法，`mdltlc = { rules }`（:174），rules 产生式带语义动作建 Ruleset（:180-192）。

## 3. 外部连接

- **Coco/R 双子**：mdltlc_parser_coco.cpp 由 mdltlc.atg + Parser.frame/Scanner.frame 生成；rd 解析器手写对应物。Compilation_unit::compile（mdltlc_compilation_unit.cpp:213）先跑 coco（:231），成功后**再建一个 comparison_unit 跑 rd**（:245-261），最后 `mdltlc_compare_asts()` 逐节点比对（:275）。
- **AST 基建复用 MDL 编译器**：Rule/Ruleset 挂在 `mi::mdl::Ast_list_element` 上（mdltlc_rules.h:104/:246），分配器、符号表、工厂模式全部来自 `mdl/compiler/compilercore`（mdltlc_compiler.cpp:28-29）——mdltlc 与 MDL 编译器同一套地基。
- **语义层**：mdltlc_analysis.cpp（类型检查）/mdltlc_types.cpp/mdltlc_values.cpp/mdltlc_exprs.cpp 是 AST 的配套语义模块；mdltlc_std_module.cpp 提供内建环境。
- **下游消费者**：codegen（mdltlc_codegen.cpp）+ gen_mdltl_enum_names.py；产物规则喂给 `generator_dag_distiller_plugin_api`（src/mdl/codegenerators/generator_dag/）与 mdl_distiller 插件；示例侧 examples/mdl_sdk/distilling_target/distilling_target_plugin_rules.mdltl 教用户写自己的规则。
- **测试**：test_parser.cpp:129 与 test_basics.cpp:231 直接调 `mdltlc_parse_rd()`，绕过 coco 对照单独测 rd。

## 4. 数据流

一次 `mdltlc file.mdltl` 编译：Mdltlc::run（mdltlc.cpp:105）解析选项 → 读源码进 string（Compilation_unit::compile :214-221 逐字符 slurp）→ **双解析**：coco 先建 AST（主结果），rd 在影子单元再建一棵（:261）→ `mdltlc_compare_asts` 比对，rd 失败或 AST 不一致都变成编译错误（:263-281，错误信息明写"hand-written MDLTL parser failed on input accepted by Coco/R"）→ 语义分析与类型推断 → codegen 生成 .h/.cpp（--generate 默认关）。运行时方向：distiller 拿到材质 DAG，按 Ruleset::Strategy 自顶向下或自底向上遍历，模式匹配 rule 左侧，命中则用右侧+where 绑定替换（dist_rules.mdltl:31-32 的 fresnel_factor→bsdf_tint 即典型替换），repeat_rules 控制是否循环到不动点。

## 5. 设计决策

- **双解析器并行验证**（本文件存在的理由）：Coco/R 是生成物、改文法容易但难加复杂语义动作；rd 手写、可演进。当前架构让每次编译都免费跑一致性测试——rd 在 coco 接受的输入上失败即 bug，两树不一致即 bug。代价是每份输入双倍解析成本，纯为迁移期保险。
- **`::` 进标识符 token**（:250）：MDLTL 模式里的限定名（`math::clamp`）作为单 token 处理，简化了文法层，但要求 Scanner 做 lookahead(1)——手写词法的典型权衡。
- **错误即位置**：Token 自带 line/column，Scanner/Parser 全部 set_error 带位置（:285-288 等），与 mdltlc_locations.h 的 Location 体系对接——编译器级错误报告是硬需求。
- **result code / deadrule 留在语法层**：repeat_rules/skip_recursion/deadrule（:849-853/:901）不是注释性花活而是 Rule 的一等字段（mdltlc_rules.h:113-121 枚举），distiller 据此控制重写循环与死规则统计。
- **AST 复用而非自立门户**：直接继承 mi::mdl 列表元素与工厂体系，mdltlc 与 MDL 主编译器共享内存管理/符号表语义——省一套基建也绑定版本。
- **`--plugin` 选项保留但 ignored**（mdltlc.cpp:74）：CLI 兼容旧脚本的诚实降级。

## 6. 新人提示

- 读本文先看 mdltlc.atg（文法即文档），再对照 rd 解析器各 parse_* 函数——每个产生式在 atg 里都有对应行（rules :180 ↔ parse_rules :753）。
- **改文法必须三处同步**：mdltlc.atg（重新生成 coco）、mdltlc_parser_rd.cpp、mdltlc_ast_compare.cpp——否则编译直接报 AST 不一致，这是双解析器机制的自我保护。
- rd 解析器单独测试入口在 test_parser.cpp:129，调它可绕开 coco 对照快速验证改动。
- debug_name/debug_print（:882-899）是规则调试通道，distiller 报告里能按名字定位命中的规则，排查"为什么我的规则没触发"从这入手。
- Scanner 的 ident 扫描吞 `:`（:256-258），意味着 `a:b` 也是合法标识符文本——写关键字判断时记得 keyword_kind 只匹配整词。
- 想理解 distiller 全貌，从 dist_rules.mdltl 正着读（模式即文档），再回看 Ruleset::Strategy 两个策略对改写顺序的影响。
- mdltlc 与 src/mdl/distiller（运行时）是两个目录：前者编译规则、后者应用规则，别混。
