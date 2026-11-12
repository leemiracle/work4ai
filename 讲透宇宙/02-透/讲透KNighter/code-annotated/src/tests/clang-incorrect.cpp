/* =============================================================================
 * 【模块定位】"应编译失败"的示例 checker：clang-correct.cpp 的注错镜像——与
 *   正例逐行同源，仅故意注入两处编译错误，作为 Syntax Repair（论文 §3.1.3
 *   Implementation + Syntax Repair，速查卡"编译失败则 repair agent 依编译错误
 *   修复，最多 maxAttempts=5 次"）的测试夹具。
 *
 * 【两处注入错误（与 correct 的 diff 仅此两行）】
 *   ① 下方 checkPostCall 的 kzalloc 分支：`Callee->getName() = "kzalloc"`
 *     ——把 == 误写成 =（对 getName() 返回的临时对象赋值）→ 编译错；
 *   ② 同分支内：`MR->getRegion()`——MemRegion 根本没有 getRegion() 成员
 *     （正确写法是 getBaseRegion()）→ 编译错。
 *   两处都典型模拟 LLM 生成 checker 的常见语法/API 幻觉形态，供 repair agent
 *   拿真实编译器报错（error: lvalue required / no member named 'getRegion'）
 *   练修复。
 *
 * 【论文映射】§3.1.3 的 repair 闭环单测缩影：test_backend.py::
 *   test_build_checker_incorrect 用本文件断言 build_checker 返回非 0（编译必挂，
 *   验证 csa.py 能正确捕获编译失败）；test_repair_checker 把本文件喂给
 *   repair_checker（src/checker_repair.py，提示词 prompt_template/repair.md，
 *   对应论文 repair agent），断言 LLM 修成可编译版本。
 *
 * 【管线角色】上游：csa.py::build_checker（编译应失败并留下编译日志）；
 *   下游：src/tests/test_backend.py 两个用例。业务逻辑注释与 clang-correct.cpp
 *   保持同构（两文件 diff 即"哪里错了"的教学对照）。
 * ========================================================================== */
// ---- CSA checker 标准头组（与 clang-correct.cpp 一致）----
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
#include "llvm/Support/raw_ostream.h"
// 论文 9 个 utility functions 头（getMemRegionFromExpr 在下方被调用）
#include "clang/StaticAnalyzer/Checkers/utility.h"

#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/AST/StmtVisitor.h"

using namespace clang;
using namespace ento;
using namespace taint;

// Program state map to track uninitialized memory regions
// ↑ 原注释（保留）。脏内存表：key=MemRegion，value=是否未初始化（kmalloc=true/kzalloc=false）
REGISTER_MAP_WITH_PROGRAMSTATE(UninitMemoryMap, const MemRegion *, bool)
// Program state map to track pointer aliasing
// ↑ 原注释（保留）。别名表（本示例声明未使用，演示宏写法）
REGISTER_MAP_WITH_PROGRAMSTATE(PtrAliasMap, const MemRegion*, const MemRegion*)

namespace {

// 与 correct 相同的三回调订阅（PostCall/PreCall/Location）
class SAGenTestChecker : public Checker<check::PostCall, check::PreCall, check::Location> {
   mutable std::unique_ptr<BugType> BT;

   public:
      SAGenTestChecker() : BT(new BugType(this, "Kernel Information Leak")) {}

      void checkPostCall(const CallEvent &Call, CheckerContext &C) const;
      void checkPreCall(const CallEvent &Call, CheckerContext &C) const;
      void checkLocation(SVal Loc, bool isLoad, const Stmt *S, CheckerContext &C) const;

   private:
      void reportInfoLeak(const MemRegion *MR, CheckerContext &C) const;
};

// ===== checkPostCall：kmalloc/kzalloc 分支打标（注入错误①②都在 kzalloc 分支）=====
void SAGenTestChecker::checkPostCall(const CallEvent &Call, CheckerContext &C) const {
  ProgramStateRef State = C.getState();
  const IdentifierInfo *Callee = Call.getCalleeIdentifier();
  if (!Callee)
    return;

  if (Callee->getName() == "kmalloc") {  // 此分支与 correct 完全相同（对照：这里用的是 ==）
    // Track kmalloc allocations, mark memory as uninitialized
    // ↑ 原注释（保留）
    const Expr *expr = Call.getOriginExpr();
    if (!expr)
      return;

    const CallExpr *CE = dyn_cast<CallExpr>(expr);
    if (!CE)
      return;

    const MemRegion *MR = getMemRegionFromExpr(CE, C);
    if (!MR)
      return;

    MR = MR->getBaseRegion();
    if (!MR)
      return;
    State = State->set<UninitMemoryMap>(MR, true);
    C.addTransition(State);
  } else if (Callee->getName() = "kzalloc") {  // 【注入错误①】== 误写为 =（对 getName() 的临时返回值赋值，编译错）——repair agent 应依报错改回 ==
    // Track kzalloc allocations, which zero-initialize memory
    // ↑ 原注释（保留）
    const Expr *expr = Call.getOriginExpr();
    if (!expr)
      return;

    const CallExpr *CE = dyn_cast<CallExpr>(expr);
    if (!CE)
      return;

    const MemRegion *MR = getMemRegionFromExpr(CE, C);
    if (!MR)
      return;

    MR = MR->getRegion();  // 【注入错误②】MemRegion 无 getRegion() 成员（正确=getBaseRegion()，见上方 kmalloc 分支），编译错——模拟 LLM 的 API 幻觉
    if (!MR)
      return;
    State = State->set<UninitMemoryMap>(MR, false);
    C.addTransition(State);
  }
}

// ===== checkPreCall：copy_to_user 前查脏标记（与 correct 完全相同）=====
void SAGenTestChecker::checkPreCall(const CallEvent &Call, CheckerContext &C) const {
  ProgramStateRef State = C.getState();
  const IdentifierInfo *Callee = Call.getCalleeIdentifier();
  if (!Callee)
    return;

  // Check for copy_to_user(user_dst, kernel_src, size)
  // ↑ 原注释（保留）
  if (Callee->getName() == "copy_to_user") {
    SVal Arg1 = Call.getArgSVal(1);
    const MemRegion *MR = Arg1.getAsRegion();
    if (!MR)
      return;

    MR = MR->getBaseRegion();
    if (!MR)
      return;
    const bool *Uninit = State->get<UninitMemoryMap>(MR);
    if (Uninit && *Uninit) {
      reportInfoLeak(MR, C);
    }
  }
}

// ===== checkLocation：空实现（与 correct 相同）=====
void SAGenTestChecker::checkLocation(SVal Loc, bool isLoad, const Stmt *S, CheckerContext &C) const {

}

// ===== 报警三步曲（与 correct 相同）=====
void SAGenTestChecker::reportInfoLeak(const MemRegion *MR, CheckerContext &C) const {
  ExplodedNode *N = C.generateNonFatalErrorNode();
  if (!N)
    return;

  auto report = std::make_unique<PathSensitiveBugReport>(
      *BT, "Potential kernel information leak due to uninitialized kmalloc memory being copied to user space", N);
  C.emitReport(std::move(report));
}

} // end anonymous namespace

// 注册入口与 API 版本串（与 correct 相同；编译错误在上方函数体，注册段本身无误）
extern "C" void clang_registerCheckers(CheckerRegistry &registry) {
  registry.addChecker<SAGenTestChecker>(
      "custom.SAGenTestChecker",
      "Detects kernel information leaks by uninitialized kmalloc memory being copied to user space",
      "");
}

extern "C" const char clang_analyzerAPIVersionString[] =
    CLANG_ANALYZER_API_VERSION_STRING;
