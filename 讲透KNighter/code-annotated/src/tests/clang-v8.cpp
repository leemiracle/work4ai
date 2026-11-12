/* =============================================================================
 * 【模块定位】V8 目标（Google Chromium 的 JavaScript 引擎；fork 增量，上游 PR
 *   #14 / commit 6788ff97 "implement run_checker for v8"）的示例 checker：检测
 *   "for 循环在边界检查之前就解引用循环指针"的越界读模式——典型形态
 *   `for (int x = *p; p != end; ++p)`（init 里 *p 先解引用，边界条件后判）与
 *   `for (...; ...; *++p)`（inc 里先加再解引用）。
 *
 * 【论文映射】论文 Generability 讨论的跨目标扩展实证：Linux 之外的目标（V8/
 *   Chromium）换目标不换管线——差分验证（§3.1.4）与 checker 形态照旧。本文件
 *   是 test_backend.py::test_evaluate_v8 的夹具：连同 commit_v8.txt 的 V8 patch
 *   跑 csa.py::_validate_checker_v8，期望 (TP,TN)=(1,1)——buggy 版本报 1 警告、
 *   patched 版本 0 警告。
 *
 * 【与 Linux 示例（clang-correct.cpp）的本质差异】不走路径敏感 ExplodedGraph
 *   回调（checkPostCall 等），而是订阅 check::ASTCodeBody——每个函数体一次的
 *   AST 遍历风格（类 clang-tidy），配 BasicBugReport（非路径敏感报告，无
 *   ErrorNode/trace path）。收益：V8 这种超大目标上扫描快，也不依赖 CSA 对 V8
 *   特有容器/内存分配的建模；代价：无跨语句路径推理。这演示了论文框架的另一
 *   种 checker 形态（论文统计里"非路径敏感"那部分合成 checker 的样例形态）。
 *
 * 【管线角色】上游：csa.py::build_checker（编译为 plugin）+
 *   _replace_checker_name_in_code 改名（SAGenTestChecker 为占位基名）；下游：
 *   src/targets/ 的 v8 target 与 test_backend.py::test_evaluate_v8。
 *
 * 【关键坑】① debugLog 每次落 /tmp/v8_checker_debug.log 且同步写 llvm::errs()
 *   ——V8 管线调试期产物，正式全库扫描会有 IO 开销（stderr 刷屏）；② 三个
 *   mutable 计数器（函数数/循环数/bug 数）依赖 CSA 分析单线程，非线程安全；
 *   ③ ObjCMethodDecl 取名分支对 V8 是死代码（V8 无 ObjC），保留通用性；
 *   ④ containsDerefOfVar 用 IgnoreParenImpCasts（只剥隐式转换）而
 *   containsDerefOfPreIncVar 用 IgnoreParenCasts（剥全部 cast 含显式）——两处
 *   剥法不一致，按原样保留；⑤ 注册名/类名 SAGenTestChecker 是 csa.py 改名锚点。
 * ========================================================================== */
// ---- CSA checker 头组（ASTCodeBody 形态：Checker/CheckerRegistry/BugReporter + AST 层）----
#include "clang/StaticAnalyzer/Core/BugReporter/BugReporter.h"
#include "clang/StaticAnalyzer/Core/BugReporter/BugType.h"
#include "clang/StaticAnalyzer/Checkers/Taint.h"
#include "clang/StaticAnalyzer/Core/Checker.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/CallEvent.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/CheckerContext.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/Environment.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/ProgramState.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/ProgramStateTrait.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/SymExpr.h"
#include "clang/StaticAnalyzer/Frontend/CheckerRegistry.h"
// AST 遍历头（本 checker 真正消费的层：ForStmt/Expr/ASTContext）
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/AST/StmtVisitor.h"
#include "llvm/Support/raw_ostream.h"
// 论文 9 个 utility functions 头（本 checker 实际未调用 utility——演示 AST
// 形态 checker 可独立于 utility 库；保留 include 以维持标准头组）
#include "clang/StaticAnalyzer/Checkers/utility.h"
#include "clang/AST/Expr.h"
#include "clang/AST/Stmt.h"
#include "clang/AST/ASTContext.h"
#include <memory>
#include <fstream>

using namespace clang;
using namespace ento;
using namespace taint;

// Debug logging helper
// ↑ 原注释（保留）。中文说明：V8 管线调试辅助——每次调用追加写
//   /tmp/v8_checker_debug.log（跨调用累积，便于事后还原分析轨迹）并同步打
//   stderr（llvm::errs() 是 LLVM 的非缓冲错误流，立即可见）
static void debugLog(const std::string &msg) {
  std::ofstream logFile("/tmp/v8_checker_debug.log", std::ios::app);  // 追加模式打开日志文件（首跑自动创建）
  if (logFile.is_open()) {  // 打开成功才写（权限/磁盘问题不致命）
    logFile << "[SAGenTestChecker] " << msg << std::endl;  // 带前缀写一行并 flush（endl 换行+刷新）
    logFile.close();
  }
  // Also output to llvm::errs() for immediate visibility
  // ↑ 原注释（保留）
  llvm::errs() << "[SAGenTestChecker DEBUG] " << msg << "\n";  // 双通道：stderr 即时观察，文件持久留档
}

namespace {

// ASTCodeBody 形态 checker：模板参数只订阅 check::ASTCodeBody（每个函数/方法体
// 编译完时回调一次，签名是 (Decl*, AnalysisManager&, BugReporter&)——注意没有
// CheckerContext，因为这不是路径敏感回调，不走 ExplodedGraph）
class SAGenTestChecker : public Checker<check::ASTCodeBody> {
   mutable std::unique_ptr<BugType> BT;  // bug 类别（回调是 const 成员，故 mutable）
   mutable int totalFunctionsAnalyzed = 0;  // 统计：已分析函数数（仅用于调试汇总；mutable 同上）
   mutable int totalForLoopsFound = 0;  // 统计：遇到的 for 循环数
   mutable int totalBugsFound = 0;  // 统计：报出的 bug 数

   public:
      // BugType 三参构造：所属 checker / bug 名 / 类别 "Memory safety"（诊断里分组显示）
      SAGenTestChecker() : BT(new BugType(this, "For-loop pre-check dereference", "Memory safety")) {
        debugLog("SAGenTestChecker initialized");  // plugin 加载即打点（验证注册链路通）
      }

      // 析构打汇总——跑完一轮从日志直接读出 函数数/循环数/bug 数（V8 调试期验收手段）
      ~SAGenTestChecker() {
        debugLog("SAGenTestChecker destroyed - Functions: " + std::to_string(totalFunctionsAnalyzed) + 
                 ", Loops: " + std::to_string(totalForLoopsFound) + 
                 ", Bugs: " + std::to_string(totalBugsFound));
      }

      void checkASTCodeBody(const Decl *D, AnalysisManager &Mgr, BugReporter &BR) const;  // 主回调：函数体入口

   private:

      // Helpers
      // ↑ 原注释（保留）。三个判定原语 + 两个遍历入口：
      const VarDecl *getLoopPtrFromCondition(const Expr *Cond) const;  // 从循环条件提取被比较的指针变量
      bool containsDerefOfVar(const Expr *E, const VarDecl *VD, const UnaryOperator *&DerefUO) const;  // 子树内是否含 *p（输出解引用节点）
      bool containsDerefOfPreIncVar(const Expr *E, const VarDecl *VD, const UnaryOperator *&DerefUO) const;  // 子树内是否含 *++p（前加后解引用）

      void analyzeForStmt(const ForStmt *FS, AnalysisManager &Mgr, BugReporter &BR, const std::string &funcName) const;  // 单个 for 的完整判定+报警
      void traverseStmt(const Stmt *S, AnalysisManager &Mgr, BugReporter &BR, const std::string &funcName) const;  // 递归找 ForStmt
};

// 边界比较运算白名单：<,<=,>,>=,!=（排除 ==）——相等比较一般不是"指针遍历到
// 边界"的写法，只有关系/不等运算才构成"p 走向 end"的边界检查语义
static bool isRelOrNe(BinaryOperatorKind Op) {
  return Op == BO_LT || Op == BO_LE || Op == BO_GT || Op == BO_GE || Op == BO_NE;
}

// 从 for 循环条件里提取"参与边界比较的指针变量"
// 三步走：剥括号/隐式转换 → 须是二元运算 → 运算符在白名单内，然后在左右操作数里找指针型变量
const VarDecl *SAGenTestChecker::getLoopPtrFromCondition(const Expr *Cond) const {
  if (!Cond) {  // for(;;) 无条件循环——无边界可判
    debugLog("  - Condition is null");
    return nullptr;
  }

  const Expr *E = Cond->IgnoreParenImpCasts();  // 剥掉括号与隐式 cast，露出真实运算符
  const auto *BO = dyn_cast<BinaryOperator>(E);  // 须是二元运算（a<b / a!=b 等）
  if (!BO) {
    debugLog("  - Condition is not a binary operator");
    return nullptr;
  }

  if (!isRelOrNe(BO->getOpcode())) {  // 白名单过滤（== 等被拒）
    debugLog("  - Binary operator is not relational/ne");
    return nullptr;
  }

  // lambda：从单个操作数提取"指针型变量声明"（Operand→剥转换→DeclRefExpr→VarDecl→判指针类型）
  auto GetPtrVar = [](const Expr *Operand) -> const VarDecl * {
    Operand = Operand ? Operand->IgnoreParenImpCasts() : nullptr;  // 空安全：null 操作数先归一成 nullptr
    if (!Operand)
      return nullptr;
    if (const auto *DRE = dyn_cast<DeclRefExpr>(Operand)) {  // 须是"变量名"引用（非常量/表达式）
      if (const auto *VD = dyn_cast<VarDecl>(DRE->getDecl())) {  // 引用的须是变量声明
        if (VD->getType()->isPointerType()) {  // 且类型是指针——本 checker 只跟踪指针遍历（i<int n 的整数循环不感兴趣）
          debugLog("    Found pointer variable: " + VD->getNameAsString());
          return VD;  // 命中：这就是"循环指针"
        }
      }
    }
    return nullptr;
  };

  if (const VarDecl *L = GetPtrVar(BO->getLHS()))  // 先看左操作数（p < end 的 p）
    return L;
  if (const VarDecl *R = GetPtrVar(BO->getRHS()))  // 左边不是指针再看右边（end > p 的 p）
    return R;

  debugLog("  - No pointer variable found in condition");  // 条件里没有指针变量：非目标模式
  return nullptr;
}

// 子树内是否含 *p（对指定变量 VD 的一元解引用）？命中时经出参 DerefUO 返回该节点
// （供后续报警定位到精确的解引用表达式）
bool SAGenTestChecker::containsDerefOfVar(const Expr *E, const VarDecl *VD,
                                          const UnaryOperator *&DerefUO) const {
  if (!E || !VD)  // 参数防御
    return false;

  if (const auto *UO = dyn_cast<UnaryOperator>(E)) {  // 当前节点是一元运算？
    if (UO->getOpcode() == UO_Deref) {  // 且是解引用（*p）？
      const Expr *Sub = UO->getSubExpr()->IgnoreParenImpCasts();  // 剥掉 * 里的括号/隐式转换，露出操作数
      if (const auto *DRE = dyn_cast<DeclRefExpr>(Sub)) {  // 操作数须是变量名（*p[0]、*(f()) 等复杂形态不匹配）
        if (DRE->getDecl() == VD) {  // 且正是循环指针变量本身（指针比较用 Decl* 恒等）
          DerefUO = UO;  // 出参：命中节点（报警位置）
          debugLog("    Found dereference of " + VD->getNameAsString());
          return true;
        }
      }
    }
  }

  // Recurse into children
  // ↑ 原注释（保留）。当前节点不匹配→DFS 所有子表达式（复合条件/逗号表达式都能搜到）
  for (const Stmt *Child : E->children()) {
    if (const auto *CE = dyn_cast_or_null<Expr>(Child)) {  // 孩子可能是非 Expr 的 Stmt（罕见），dyn_cast_or_null 双防
      if (containsDerefOfVar(CE, VD, DerefUO))  // 命中即短路返回
        return true;
    }
  }
  return false;  // 整棵子树无 *p
}

// 子树内是否含 *++p（前自增后解引用——for 的 inc 段典型写法）？
// 与上一个 helper 的差别：* 的操作数不是裸变量，而是 ++p（UO_PreInc 套 DeclRefExpr）
bool SAGenTestChecker::containsDerefOfPreIncVar(const Expr *E, const VarDecl *VD,
                                                const UnaryOperator *&DerefUO) const {
  if (!E || !VD)
    return false;

  if (const auto *UO = dyn_cast<UnaryOperator>(E)) {  // 外层一元运算
    if (UO->getOpcode() == UO_Deref) {  // 是解引用
      const Expr *Sub = UO->getSubExpr()->IgnoreParenCasts();  // 注意：这里用 IgnoreParenCasts（剥全部 cast 含显式），与前 helper 的 IgnoreParenImpCasts 不一致——按原样保留
      if (const auto *UO2 = dyn_cast<UnaryOperator>(Sub)) {  // 内层须还是一元运算
        if (UO2->getOpcode() == UO_PreInc) {  // 且是前自增 ++p
          const Expr *Inner = UO2->getSubExpr()->IgnoreParenCasts();  // 再剥一层拿 ++ 的操作数
          if (const auto *DRE = dyn_cast<DeclRefExpr>(Inner)) {  // 须是变量名
            if (DRE->getDecl() == VD) {  // 且正是循环指针
              DerefUO = UO;  // 出参：最外层解引用节点（报警位置）
              debugLog("    Found dereference of pre-incremented " + VD->getNameAsString());
              return true;
            }
          }
        }
      }
    }
  }

  // Recurse into children
  // ↑ 原注释（保留）。同样 DFS 下探
  for (const Stmt *Child : E->children()) {
    if (const auto *CE = dyn_cast_or_null<Expr>(Child)) {
      if (containsDerefOfPreIncVar(CE, VD, DerefUO))
        return true;
    }
  }
  return false;
}

// 单个 for 语句的完整判定与报警：条件里有指针变量 PtrVD 时，检查 init 段是否
// 已对它解引用（边界还没判就先 *p → 越界读）、inc 段是否是 *++p（同性质）
void SAGenTestChecker::analyzeForStmt(const ForStmt *FS, AnalysisManager &Mgr, BugReporter &BR, 
                                      const std::string &funcName) const {
  if (!FS)
    return;

  totalForLoopsFound++;  // 计数（析构时汇总）
  debugLog("  Analyzing for-loop #" + std::to_string(totalForLoopsFound) + " in function: " + funcName);

  const Expr *Cond = FS->getCond();  // for(init; cond; inc) 的条件段
  const VarDecl *PtrVD = getLoopPtrFromCondition(Cond);  // 提取循环指针（内部含白名单过滤）
  if (!PtrVD) {  // 无指针变量→非目标模式，跳过
    debugLog("  - No pointer variable in loop condition, skipping");
    return;
  }

  debugLog("  - Found pointer variable in condition: " + PtrVD->getNameAsString());

  // Check initializer
  // ↑ 原注释（保留）。init 段两形态：DeclStmt（声明并初始化，可含多个声明）或裸表达式
  const Stmt *Init = FS->getInit();  // init 段（可能为空）
  if (Init) {
    debugLog("  - Checking initializer");
    const UnaryOperator *DerefUO = nullptr;  // 解引用节点出参（报警定位用）

    if (const auto *DS = dyn_cast<DeclStmt>(Init)) {  // 形态①：声明语句 for(int x = *p; ...)
      for (const Decl *D : DS->decls()) {  // 一条 DeclStmt 可含多个声明（int a=..., b=*p;）逐个查
        if (const auto *VD = dyn_cast<VarDecl>(D)) {  // 只关心变量声明
          const Expr *InitE = VD->getInit();  // 该变量的初始化表达式
          if (InitE && containsDerefOfVar(InitE, PtrVD, DerefUO)) {  // 初始化里解引用了循环指针→命中：边界检查之前就 *p
            totalBugsFound++;
            debugLog("  *** BUG FOUND #" + std::to_string(totalBugsFound) + 
                    " in initializer: dereference before bound check");
            // BasicBugReport：非路径敏感报告（ASTCodeBody 形态没有 ExplodedNode），
            // 位置用 PathDiagnosticLocation::createBegin 精确到解引用表达式起始；
            // DerefUO 为 null 时兜底定位到整条 init 语句
            auto R = std::make_unique<BasicBugReport>(
                *BT,
                "Dereference in for-loop initializer occurs before bound check; possible out-of-bounds read.",
                DerefUO ? PathDiagnosticLocation::createBegin(DerefUO, BR.getSourceManager(), nullptr)
                        : PathDiagnosticLocation::createBegin(Init, BR.getSourceManager(), nullptr));
            if (DerefUO)
              R->addRange(DerefUO->getSourceRange());  // 诊断里高亮 *p 的源码范围
            BR.emitReport(std::move(R));  // 提交报告（BugReporter 直发，不经 CheckerContext）
          }
        }
      }
    } else if (const auto *IE = dyn_cast<Expr>(Init)) {  // 形态②：裸表达式 init（x = *p; 少见写法）
      if (containsDerefOfVar(IE, PtrVD, DerefUO)) {  // 同一判定
        totalBugsFound++;
        debugLog("  *** BUG FOUND #" + std::to_string(totalBugsFound) + 
                " in initializer expr: dereference before bound check");
        auto R = std::make_unique<BasicBugReport>(  // 报警（同上，兜底定位点换成该表达式）
            *BT,
            "Dereference in for-loop initializer occurs before bound check; possible out-of-bounds read.",
            DerefUO ? PathDiagnosticLocation::createBegin(DerefUO, BR.getSourceManager(), nullptr)
                    : PathDiagnosticLocation::createBegin(IE, BR.getSourceManager(), nullptr));
        if (DerefUO)
          R->addRange(DerefUO->getSourceRange());
        BR.emitReport(std::move(R));
      }
    }
  }

  // Check increment
  // ↑ 原注释（保留）。inc 段查 *++p 形态：自增越过边界与解引用同拍发生，边界保护失效
  const Expr *Inc = FS->getInc();  // inc 段（可能为空）
  if (Inc) {
    debugLog("  - Checking increment");
    const UnaryOperator *DerefUO = nullptr;
    if (containsDerefOfPreIncVar(Inc, PtrVD, DerefUO)) {  // 命中 *++p
      totalBugsFound++;
      debugLog("  *** BUG FOUND #" + std::to_string(totalBugsFound) + 
              " in increment: dereference of pre-incremented iterator");
      auto R = std::make_unique<BasicBugReport>(  // 报警（消息与 init 段不同，明说前自增迭代器）
          *BT,
          "Dereference of pre-incremented iterator in for-loop increment occurs before bound check; possible out-of-bounds read.",
          DerefUO ? PathDiagnosticLocation::createBegin(DerefUO, BR.getSourceManager(), nullptr)
                  : PathDiagnosticLocation::createBegin(Inc, BR.getSourceManager(), nullptr));
      if (DerefUO)
        R->addRange(DerefUO->getSourceRange());
      BR.emitReport(std::move(R));
    }
  }
}

// 递归遍历语句树，遇到 ForStmt 就交给 analyzeForStmt（手写递归而非
// RecursiveASTVisitor——只需要 ForStmt 一种节点，最小遍历开销）
void SAGenTestChecker::traverseStmt(const Stmt *S, AnalysisManager &Mgr, BugReporter &BR, 
                                    const std::string &funcName) const {
  if (!S)
    return;

  if (const auto *FS = dyn_cast<ForStmt>(S))  // 命中 for 语句
    analyzeForStmt(FS, Mgr, BR, funcName);  // 判定+报警

  for (const Stmt *Child : S->children()) {  // 继续下探所有子语句（嵌套 for 也会被逐层捕获）
    if (Child)
      traverseStmt(Child, Mgr, BR, funcName);
  }
}

// 主回调：每个函数/方法体编译完成时被调一次（ASTCodeBody 事件）
// 形态与路径敏感回调的对比：参数是 AnalysisManager&/BugReporter&（无 CheckerContext），
// 说明本 checker 完全工作在 AST 层，不进 ExplodedGraph
void SAGenTestChecker::checkASTCodeBody(const Decl *D, AnalysisManager &Mgr, BugReporter &BR) const {
  if (!D)
    return;

  totalFunctionsAnalyzed++;  // 函数计数
  // ↑ 原文件本行与下一行之间是一个仅含两个空白的行（原样保留在下方）
  
  std::string funcName = "unknown";  // 日志用函数名；取不到名字时保持 "unknown"  // 函数名（仅用于日志；取不到时保持 unknown）
  if (const auto *FD = dyn_cast<FunctionDecl>(D)) {  // 普通函数/方法（V8 的主体）
    funcName = FD->getNameAsString();
  } else if (const auto *MD = dyn_cast<ObjCMethodDecl>(D)) {  // ObjC 方法——对 V8 是死代码，保留通用性
    funcName = MD->getNameAsString();
  }
  
  debugLog("Analyzing function #" + std::to_string(totalFunctionsAnalyzed) + ": " + funcName);

  const Stmt *Body = D->getBody();  // 函数体（纯声明无体时为 null）
  if (!Body) {
    debugLog("  - No body found");
    return;
  }

  traverseStmt(Body, Mgr, BR, funcName);  // 入口遍历
}

} // end anonymous namespace

// 注册入口：加载 plugin 时打一条日志验证链路，再注册 checker（名字用于
// -analyzer-checker= 过滤；描述即 bug pattern 的人类可读版）
extern "C" void clang_registerCheckers(CheckerRegistry &registry) {
  debugLog("=== Registering SAGenTestChecker ===");
  registry.addChecker<SAGenTestChecker>(
      "custom.SAGenTestChecker",
      "Detect dereference in for-loop init/increment before the loop bound check",
      "");
}

// plugin ABI 版本协商串（.exports 导出的第二个符号）
extern "C" const char clang_analyzerAPIVersionString[] =
    CLANG_ANALYZER_API_VERSION_STRING;