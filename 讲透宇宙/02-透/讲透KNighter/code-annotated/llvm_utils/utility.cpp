/* =============================================================================
 * 【模块定位】论文点名的 9 个 utility functions 的实现体（llvm_utils/utility.h
 *   的 .cpp 侧，论文 §4 "9 such utility functions"，速查卡"关键资产与代码映射"）。
 *   纯 CSA/AST API 薄封装：常量求值、约束推断符号上界、数组/字符串长度、
 *   表达式→MemRegion、AST 上下搜索（模板实现在 .h）、已知解引用函数表、
 *   源码文本匹配。
 *
 * 【论文映射】§3.1.2 Pattern→Plan 阶段把本文件的签名+实现全文注入
 *   pattern2plan/plan2checker 提示词（prompt_template/knowledge/utility.md，
 *   即速查卡"utility 函数签名清单"），LLM 据此在 plan 里决定复用哪些原语；
 *   §3.1.3 合成的 checker.cpp 直接 #include 调用。
 *
 * 【管线角色】scripts/setup_llvm.py 把本文件拷到 $LLVM_DIR/clang/lib/
 *   StaticAnalyzer/Checkers/utility.cpp（.h 拷到 clang/include/.../Checkers/），
 *   与 Clang 源码树内编译单元平级参与构建，被各 plugin 的 libXXXPlugin.so 链接。
 *
 * 【关键坑】① 两处剥隐式节点 API 不同：getArraySizeFromExpr 用 IgnoreImplicit()
 *   （剥所有隐式节点，含 ImplicitCastExpr），getStringSize 用 IgnoreImpCasts()
 *   （只剥隐式 cast）——本文件按原样保留，勿"统一"；② DerefTable 是启发式
 *   小表（作者注明 illustrative，可扩充），判据是"函数名精确匹配"，别名/内联
 *   场景不在内——这正是论文失败模式里"编译器内联 strcpy/memset 导致回调拦截
 *   不到"的一处根源；③ getStringSize 的 APInt 固定 32 位宽（大字面量理论溢出，
 *   实际无碍）。
 * ========================================================================== */
// 安装路径即 include 路径：setup_llvm.py 拷到 clang/lib/StaticAnalyzer/Checkers/ 后，
// 从 clang/include/clang/StaticAnalyzer/Checkers/utility.h 解析（utility ⑤-⑨ 的声明）
#include "clang/StaticAnalyzer/Checkers/utility.h"

// utility ①实现：常量表达式求值为整数
// EvaluateAsInt 是 Clang AST 的编译期常量折叠入口（需 ASTContext 提供类型/目标平台信息）
bool EvaluateExprToInt(llvm::APSInt &EvalRes, const Expr *expr, CheckerContext &C) {
  Expr::EvalResult ExprRes;  // 求值结果容器（还可能携带溢出/副作用标志）
  if (expr->EvaluateAsInt(ExprRes, C.getASTContext())) {  // 成功=true 且 Val 是整型
    EvalRes = ExprRes.Val.getInt();  // 取出 APSInt 写给出参
    return true;
  }
  return false;  // 非常量（含运行期值）——调用方应改走符号约束（utility ②）
}

// utility ②实现：用路径约束推断符号最大值
// State->getConstraintManager() 拿到当前约束管理器，getSymMaxVal 查询"在此状态下
// Sym 还可能多大"——如 if (a <= 10) 之后对 a 的查询应得 10
const llvm::APSInt *inferSymbolMaxVal(SymbolRef Sym, CheckerContext &C) {
  ProgramStateRef State = C.getState();  // 当前 ExplodedNode 携带的 ProgramState（约束都存在这里）
  const llvm::APSInt *maxVal = State->getConstraintManager().getSymMaxVal(State, Sym);  // 约束求解：Sym 的上确界
  return maxVal;  // 约束不足以定界时为 nullptr（调用方判空后再用于溢出判断）
}

// utility ③实现：从数组名表达式提取定长数组大小
// 链式 dyn_cast 逐层剥洋葱：隐式节点→DeclRefExpr→VarDecl→ConstantArrayType
bool getArraySizeFromExpr(llvm::APInt &ArraySize, const Expr *E) {
  if (const DeclRefExpr *DRE = dyn_cast<DeclRefExpr>(E->IgnoreImplicit())) {  // 剥掉 ImplicitCastExpr（数组名外常包 lvalue-to-rvalue 隐式转换）后须是变量引用
    if (const VarDecl *VD = dyn_cast<VarDecl>(DRE->getDecl())) {  // 引用的声明须是变量（排除函数/枚举等）
      QualType QT = VD->getType();  // 变量类型
      if (const ConstantArrayType *ArrayType = dyn_cast<ConstantArrayType>(QT.getTypePtr())) {  // 须是编译期定长数组（char buf[64]）；VLA/指针/数组形参退化都到不了这里
        ArraySize = ArrayType->getSize();  // 定长尺寸（APInt）
        return true;
      }
    }
  }
  return false;  // 任一层不匹配即失败
}

// utility ④实现：字符串字面量长度
// 与 ③ 的差别：这里用 IgnoreImpCasts()（只剥隐式 cast），StringLiteral 外层同样
// 只包 ImplicitCastExpr，两种剥法对本用例等价——保留原实现差异，勿"顺手统一"
bool getStringSize(llvm::APInt &StringSize, const Expr *E) {
  if (const auto *SL = dyn_cast<StringLiteral>(E->IgnoreImpCasts())) {  // 剥隐式 cast 后须是字符串字面量
    StringSize = llvm::APInt(32, SL->getLength());  // 32 位宽 APInt 装"不含结尾 '\0' 的字符数"
    return true;
  }
  return false;  // 非字面量（数组变量/指针）不处理
}

// utility ⑤实现：表达式 → MemRegion（论文点名的代表函数）
// getSVal(E, LCtx) 在当前栈帧对表达式求 SVal（符号执行里的"值"抽象）；
// getAsRegion() 当该 SVal 是个指向内存区域的定位值（loc）时取出 MemRegion，
// 否则（未知值/常量）返回 null——MemRegion 即 CSA 内存模型的"一块内存"，
// 可作 REGISTER_MAP_WITH_PROGRAMSTATE 挂的 map 的 key
const MemRegion* getMemRegionFromExpr(const Expr* E, CheckerContext &C) {
  ProgramStateRef State = C.getState();  // 当前节点状态
  return State->getSVal(E, C.getLocationContext()).getAsRegion();  // 表达式求值→定位值→区域，一步到位
}

// 已知解引用函数表的条目结构（utility ⑧ 的数据源）
struct KnownDerefFunction {
  const char *Name;                    ///< The function name.  ← 原注释（保留）：被精确匹配的 C 函数名
  llvm::SmallVector<unsigned, 4> Params; ///< The parameter indices that get dereferenced.  ← 原注释（保留）：会被解引用的 0-based 参数下标集合（SmallVector 4 是栈上小容量优化）
};

// This is just an illustrative list. Expand as needed.
// ↑ 原注释（保留）。中文说明：启发式函数表——判"把空指针传给这些函数的这些参数
//   位必然崩"。作者明示可按目标代码库扩充（Linux 内核可加 copy_from_user 等）。
const KnownDerefFunction DerefTable[] = {
    // String functions
    // ↑ 原分组注释（保留）。各条目 0-based 下标：dest=0、src=1
    {"strcpy",  {0, 1}},  // char *strcpy(char *dest, const char *src);  ← dest/src 都被解引用
    {"strcat",  {0, 1}},  // char *strcat(char *dest, const char *src);  ← 同上
    {"strcmp",  {0, 1}},  // int strcmp(const char *s1, const char *s2);  ← 读两个串
    {"strlen",  {0}},     // size_t strlen(const char *s);  ← 只读 s 一个
    {"strncpy", {0, 1}},  // char *strncpy(char *dest, const char *src, size_t n);  ← dest/src（n 本身不解引用）
    {"strncat", {0, 1}},  // char *strncat(char *dest, const char *src, size_t n);  ← 同上

    // Memory functions
    // ↑ 原分组注释（保留）
    {"memcpy",  {0, 1}},  // void *memcpy(void *dest, const void *src, size_t n);  ← dest/src 都被解引用
    {"memmove", {0, 1}},  // void *memmove(void *dest, const void *src, size_t n);  ← 同上
    {"memcmp",  {0, 1}},  // int memcmp(const void *s1, const void *s2, size_t n);  ← 读两块内存
    {"memset",  {0}},     // void *memset(void *s, int c, size_t n);  ← 只写 s（c/n 是标量）

    // Formatted output
    // ↑ 原分组注释（保留）。注意 snprintf 的 format 是 2 号参数（0=str 缓冲, 1=size）
    {"snprintf", {0, 2}}, // int snprintf(char *str, size_t size, const char *format, ...);  ← str 缓冲 + format 串被解引用
    {"sprintf",  {0, 1}}, // int sprintf(char *str, const char *format, ...);  ← str + format

    // Some user-defined or custom system functions
    // ↑ 原分组注释（保留）。内核 target 定制条目
    {"_dev_err",  {2}},    // dev_err(dev, fmt, ptr) -> assume param #2 is dereferenced.  ← 原注释保留；Linux 内核打印函数，启发式假设变参区的指针参数（2 号）会被 %s/%p 打印解引用
    // Add more as you see fit ...
};

// utility ⑧实现：查表判定"该调用会解引用哪些参数"
// 与 ⑨ 的分工：⑧ 是"调用点语义表"（谁解引用），⑤ 是"值→区域"（跟踪谁）；
// null-ptr checker 把两者串起来：PossibleNullPtrMap 里的空区域流进 ⑧ 命中的参数位 → 报警
bool functionKnownToDeref(const CallEvent &Call,
                                 llvm::SmallVectorImpl<unsigned> &DerefParams) {
  if (const IdentifierInfo *ID = Call.getCalleeIdentifier()) {  // 取被调函数名标识；间接调用（函数指针）/内联后无标识符时为 null
    StringRef FnName = ID->getName();  // 拿到裸函数名字符串

    for (const auto &Entry : DerefTable) {  // 线性扫表（表小无所谓；精确名匹配，不做原型比对）
      if (FnName == Entry.Name) {
        // We found the function in our table, copy its param indices
        DerefParams.append(Entry.Params.begin(), Entry.Params.end());  // 命中：把该函数的解引用参数下标集追加给调用方
        return true;
      }
    }
  }
  return false;  // 不在表内（含取不到名字的情况）——不判定为"必然解引用"
}

// utility ⑨实现：表达式源码文本含指定名字？（文本级启发式）
// 走 Lexer 从 SourceRange 抽源码原文再做子串匹配——比 AST 精确匹配宽（宏名、
// 变量名混排都能命中），适合识别 unlikely(x)/IS_ERR(x) 这类宏空检查（§3.2
// refinement 让 checker 学会"宏检查合法"时就靠这类判别）
bool ExprHasName(const Expr *E, StringRef Name, CheckerContext &C) {
  if (!E)
    return false;  // 空表达式直接 false（doc 承诺的契约）

  // Use const reference since getSourceManager() returns a const SourceManager.
  // ↑ 原注释（保留）
  const SourceManager &SM = C.getSourceManager();  // 源码管理器：字节偏移↔文件/行列 的映射
  const LangOptions &LangOpts = C.getLangOpts();  // 语言选项（影响 Lexer 的 token 化行为）
  // Retrieve the source text corresponding to the expression.
  // ↑ 原注释（保留）。getTokenRange 取"token 精确范围"（含最后一个 token 的完整
  //   拼写，而非字符级半截），再由 Lexer 还原这段源码文本
  CharSourceRange Range = CharSourceRange::getTokenRange(E->getSourceRange());
  StringRef ExprText = Lexer::getSourceText(Range, SM, LangOpts);  // 抽出的源码子串（跨行/宏展开场景可能不完整，属该启发式的已知局限）

  // Check if the extracted text contains the specified name.
  // ↑ 原注释（保留）。子串匹配（非整词），"unlikely" 也会命中 "my_unlikely"——宽松但够用
  return ExprText.contains(Name);
}
