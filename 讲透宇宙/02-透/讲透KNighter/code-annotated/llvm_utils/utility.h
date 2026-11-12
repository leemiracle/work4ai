/* =============================================================================
 * 【模块定位】KNighter 论文点名的 9 个 utility functions 的声明头（论文 §4
 *   "9 such utility functions"，速查卡"关键资产与代码映射"条目）。它们封装 CSA
 *   底层常用操作（常量求值/约束推断/区域提取/数组与字符串长度/AST 上下搜索/
 *   已知解引用函数表/源码文本匹配），让 LLM 合成 checker 时只需"填空调用"，而
 *   不必从零实现底层 CSA 代码——这是把 validity 从 8 提到 12、语法错误从 52 降到
 *   28 的关键设计（论文 §3.1.2 消融）。
 *
 * 【论文映射】两处消费：① §3.1.2 Pattern→Plan 阶段——这 9 个函数的签名与实现
 *   通过 prompt_template/knowledge/utility.md 注入 pattern2plan / plan2checker
 *   提示词（仓库另有 *-no-utility.md 消融对照模板）；② §3.1.3 Plan→Checker
 *   阶段——合成出的 checker.cpp 直接 #include "clang/StaticAnalyzer/Checkers/
 *   utility.h" 调用（即下方第 1 个 #include 的路径）。
 *
 * 【管线角色】scripts/setup_llvm.py 把本文件拷到 $LLVM_DIR/clang/include/clang/
 *   StaticAnalyzer/Checkers/utility.h（utility.cpp 拷到 clang/lib/StaticAnalyzer/
 *   Checkers/），使所有合成 checker 与官方 checker 平级编译，无需改 LLVM 构建
 *   脚本即可被 plugin 链接到。下游：src/tests/clang-{correct,incorrect,v8}.cpp
 *   三个示例 checker + 全部 LLM 合成 checker。
 *
 * 【CSA 背景】CSA（Clang Static Analyzer）是路径敏感符号执行引擎：沿 ExplodedGraph
 *   展开，节点=ProgramPoint+ProgramState；checker 通过 REGISTER_MAP_WITH_
 *   PROGRAMSTATE 宏在 ProgramState 上挂自定义 map，并在 checkPostCall 等回调里
 *   被事件驱动地调用。本文件全部函数都是给这类 checker 用的"原语库"。
 *
 * 【关键坑】getMemRegionFromExpr 有两条使用约束（原注释已声明）：勿传裸
 *   DeclRefExpr（getSVal 语义不合适）、调用前勿自行 IgnoreImplicit()（内部会按
 *   需求处理隐式节点）——LLM 生成的调用必须遵守，否则语义漂移。
 * ========================================================================== */
/* include guard：宏名与安装位置（clang/lib/.../Checkers/）对应的 LLVM 命名惯例 */
#ifndef LLVM_CLANG_LIB_STATICANALYZER_CHECKERS_UTILITY_H
#define LLVM_CLANG_LIB_STATICANALYZER_CHECKERS_UTILITY_H

/* ---- 头文件组：9 个 utility 全部构建在这些 CSA/AST API 之上 ----
 * CheckerContext    —— checker 回调的一站式上下文（getState/getSVal/addTransition 等）
 * APSIntType        —— 任意精度整数 APSInt 的符号/宽度类别工具
 * ProgramStateTrait —— REGISTER_MAP_WITH_PROGRAMSTATE 宏所在头
 * SymbolManager     —— 符号管理器与 SymbolRef（约束推断的输入）
 * Checker           —— checker 基类模板（Checker<check::...>）
 * BugType           —— bug 类别对象（报警时用）
 * CallEvent         —— 函数调用事件的统一抽象（PostCall/PreCall 回调的实参）
 * ParentMapContext / ParentMap —— AST 父节点映射（向上搜索要用）
 * Expr              —— 表达式 AST 节点基类 */
#include "clang/StaticAnalyzer/Core/PathSensitive/CheckerContext.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/APSIntType.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/ProgramStateTrait.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/SymbolManager.h"
#include "clang/StaticAnalyzer/Core/Checker.h"
#include "clang/StaticAnalyzer/Core/BugReporter/BugType.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/CallEvent.h"
#include "clang/AST/ParentMapContext.h"
#include "clang/AST/ParentMap.h"
#include "clang/AST/Expr.h"


// ↑ using-directive：把 clang / ento（staticanalyzer 核心命名空间）整个引入，
//   utility.cpp 与所有 checker 源文件都依赖它裸用 Expr/CheckerContext/SVal 等名——
//   这也是 create_plugin.py 生成的 opaq 壳插件能直接编译这些名字的前置条件
//   （头文件里的 using 会传导给所有 include 者；工程上属反模式但论文代码从简）。
using namespace clang;                 // AST 层：Decl/Expr/Stmt/APInt 等全部类型
using namespace ento;                  // CSA 引擎层：CheckerContext/SVal/ProgramState 等


// utility ①（编号对应论文 §4 的 9 个函数清单）
// Evaluate the expression to int type, and store the evaluated result in EvalRes
// Return true if this evaluation succeed.
// Only works for constant values
// ↑ 原注释（保留）。中文说明：AST 层常量折叠（EvaluateAsInt），不走符号执行，
//   只对编译期可求值的常量表达式生效——整数溢出类 checker 拿边界常量用。
// 参数：EvalRes 出参（任意精度整数）；expr 待求值表达式；C 提供ASTContext
// 返回：bool 是否成功
bool EvaluateExprToInt(llvm::APSInt& EvalRes, const Expr *expr, CheckerContext &C);


// utility ②：符号最大值推断——CSA 约束求解入口
// Return the maximal possible value for a given symbol
// Using existing constraints to infer the maximal value
// For example, the maximal value of 'a' may be 10 after the statement "if (a <= 10)"
// ↑ 原注释（保留）。中文说明：把"符号执行到目前为止累积的路径约束"交给
//   ConstraintManager，推断 Sym 能取到的最大值（如 `if (a <= 10)` 之后 a 的
//   max=10）。溢出/越界 checker 判"最坏情形"的核心原语。
// 参数：Sym 待推断的符号；C 取当前 ProgramState
// 返回：APSInt 指针（约束不足以定界时可能为 null，调用方须判空）
const llvm::APSInt* inferSymbolMaxVal(SymbolRef Sym, CheckerContext &C);


// utility ③：数组长度提取
// Get the array size from an expression, and store the result in ArraySize
// Return true if the size is successfully retrieved
// The expression should be the DeclRefExpr of the array
// ↑ 原注释（保留）。中文说明：只认"数组变量的 DeclRefExpr + ConstantArrayType
//   定长声明"（如 char buf[64]），VLA/指针/退化的形参都拿不到——越界 checker
//   求缓冲区容量用。
// 参数：ArraySize 出参；E 数组名表达式
// 返回：bool 是否成功
bool getArraySizeFromExpr(llvm::APInt& ArraySize, const Expr *E);


// utility ④：字符串字面量长度提取
// Get the string size from an expression, and store the result in StringSize
// Return true if the size if successfully retrieved
// ↑ 原注释（保留，"if"为原仓 typo 保留不改）。中文说明：对 StringLiteral 取
//   getLength()（不含结尾 '\0'），配 32 位宽 APInt——缓冲区溢出类 checker
//   （strcpy 定长 buf）算"源串多长"用。
// 参数：StringSize 出参；E 字符串字面量表达式
// 返回：bool 是否成功
bool getStringSize(llvm::APInt& StringSize, const Expr *E);

// utility ⑤：表达式 → MemRegion——论文点名的代表函数（速查卡引用）
// Get the MemRegion from an expression
// For example, it will return the corresponding MemRegion of the variable "a" given expression of "a"
// Do not pass DeclRefExpr as the parameter!
// Dynamic won't be used in this function, so do not perform IgnoreImplicit() before invoking this function!
// ↑ 原注释（保留，两条调用约束）。中文说明：把 AST 表达式经 getSVal 求值映射到
//   CSA 内存模型（MemRegion 是符号执行里"一块内存"的抽象，作 ProgramState map
//   的 key）。checkPostCall 里把"kmalloc 返回值"变成可跟踪的堆区域就是它。
// 参数：E 表达式；C 提供当前 ProgramState 与 LocationContext
// 返回：MemRegion 指针，求不出区域时为 null
const MemRegion* getMemRegionFromExpr(const Expr* E, CheckerContext &C);


// utility ⑥：沿 ParentMap 向上找第一个 T 类型祖先节点（模板必须实现在头文件里）
// Going upward in an AST tree, and find the Stmt of specific type
// ↑ 原注释（保留）。典型用法：拿到解引用表达式后向上找它所在的 IfStmt/
//   CompoundStmt，判断"这个解引用是否已被某个分支条件保护"。
// 参数：S 起点；T 目标 Stmt 类型（模板参）；C 提供 LocationContext→ParentMap
// 返回：首个 T 类型祖先，到根仍无则 nullptr
template <typename T>
const T* findSpecificTypeInParents(const Stmt *S, CheckerContext &C) {
  if (!S) return nullptr;  // 空起点防御
  while (!dyn_cast<T>(S)) {  // 当前节点还不是 T 类型就继续向上（dyn_cast 失败返回 null）
    S = C.getLocationContext()->getParentMap().getParent(S);  // 经 ParentMap 取 AST 父节点；ParentMap 需要当前栈帧 LocationContext 才能构造
    if (!S) return nullptr;  // 走到 AST 根仍未命中——放弃
  }
  return dyn_cast<T>(S);  // 跳出循环时 S 必是 T 类型，dyn_cast 必成功
}


// utility ⑦：向下 DFS 找第一个 T 类型后代节点
// Going downward in an AST tree, and find the Stmt of secific type
// Only return one of the statements if there are many
// ↑ 原注释（保留，"secific"为原仓 typo 保留）。中文说明：深度优先遍历子树，
//   命中即返回；兄弟间顺序按 Stmt::children() 的 AST 孩子顺序——多个命中时
//   只回最先遇到的一个，调用方不能假设唯一。
// 参数：S 起点；T 目标类型（模板参）
// 返回：首个 T 类型后代，无则 nullptr
template <typename T>
const T* findSpecificTypeInChildren(const Stmt *S) {
  if (!S) return nullptr;  // 空起点防御
  if (dyn_cast<T>(S)) return dyn_cast<T>(S);  // 起点自身即命中（顺手短路，不进递归）
  for (const Stmt *SubStmt: S->children()) {  // 逐孩子 DFS（children() 是 Stmt 的统一子节点接口）
    if (dyn_cast<T>(SubStmt))  // 孩子直接命中
      return dyn_cast<T>(SubStmt);
    const T* RetVal = findSpecificTypeInChildren<T>(SubStmt);  // 否则递归下探
    if (RetVal) return RetVal;  // 子树命中即层层回传
  }
  return nullptr;  // 整棵子树无 T 类型节点
}

// utility ⑧：已知"必然解引用指针参数"的函数表查询（原 doc 注释保留在下方）
/// \brief Determines if the given call is to a function known to dereference
///        certain pointer parameters.
///
/// This function looks up the call's callee name in a known table of functions
/// that definitely dereference one or more of their pointer parameters. If the
/// function is found, it appends the 0-based parameter indices that are dereferenced
/// into \p DerefParams and returns \c true. Otherwise, it returns \c false.
///
/// \param[in] Call        The function call to examine.
/// \param[out] DerefParams
///     A list of parameter indices that the function is known to dereference.
///
/// \return \c true if the function is found in the known-dereference table,
///         \c false otherwise.
// ↑ 原英文 doc 注释（保留）。中文说明：null-ptr checker 的关键判定原语——
//   "这个调用点会解引用哪些参数"。空指针传给 strcpy/memcpy 等必然崩，所以
//   PossibleNullPtrMap 里挂着的空指针若流进这些参数位即报警。
bool functionKnownToDeref(const CallEvent &Call,
                                 llvm::SmallVectorImpl<unsigned> &DerefParams);

// utility ⑨：源码文本级名字匹配（原 doc 注释保留在下方）
/// \brief Determines if the source text of an expression contains a specified name.
///
/// This function retrieves the source text corresponding to the provided expression
/// and checks whether that text contains the given \p Name. It leverages Clang's Lexer
/// utilities to extract the text from the expression's source range. If the expression is
/// null, the function returns \c false.
///
/// \param[in] E The expression to inspect.
/// \param[in] Name The name (or substring) to search for within the expression's source text.
/// \param[in] C The checker context, used to access the source manager and language options.
///
/// \return \c true if the expression's source text contains \p Name; otherwise, \c false.
// ↑ 原英文 doc 注释（保留）。中文说明：文本级启发式（非语义级）——最典型的用途是
//   识别宏调用，如 refinement 阶段 LLM 学会"unlikely(p) 是合法的空检查"后，
//   用它判空检查表达式文本里是否含 "unlikely"（论文 §3.2）。
bool ExprHasName(const Expr *E, StringRef Name, CheckerContext &C);

#endif
