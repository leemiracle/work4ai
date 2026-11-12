/* =============================================================================
 * 【模块定位】"应编译成功"的示例 checker（金标准样例）：检测 Linux 内核信息泄露
 *   ——kmalloc 分配的未初始化内存未经写入就经 copy_to_user 拷给用户态。
 *   路径敏感风格（ExplodedGraph 回调 + ProgramState map），是论文 §3.1.3
 *   Implementation 产物 checker 的标准形态样例。
 *
 * 【论文映射】三个角色：① build_checker 的正例夹具——test_backend.py::
 *   test_build_checker 用本文件断言编译返回码为 0（§3.1.3 "编译失败则 repair"
 *   闭环的"无需 repair"对照组）；② §3.1.4 Validation 的演示样例——
 *   test_evaluate_linux 用本文件 + commit_id.txt 对 Linux target 跑
 *   validate_checker，期望 (TP,TN)=(1,1)：buggy 版本报 1 警告、patched 版本报
 *   0 警告，即差分验证通过的单点样例；③ 给 LLM 的 few-shot 形态参照（三套头
 *   文件/状态宏/注册四要素的"标准开头"）。同目录 clang-incorrect.cpp 是它的
 *   注错镜像（两处编译错误，供 repair agent 用例）。
 *
 * 【管线角色】上游：csa.py::build_checker（编译成 plugin）；csa.py::
 *   _replace_checker_name_in_code 会把本文件的 "SAGenTestChecker" 批量替换为
 *   唯一 checker 名（SAGenTest 是占位基名，csa.py L200 的默认名）——类名与
 *   注册名 "custom.SAGenTestChecker" 是改名约定的锚点，勿改动拼写。下游：
 *   unittest 与 CI（src/tests/test_backend.py）。
 *
 * 【CSA 语义速查】（对照速查卡 CSA 背景节）checkPostCall=函数调用后回调、
 *   checkPreCall=调用前、checkLocation=内存位置访问；REGISTER_MAP_WITH_
 *   PROGRAMSTATE 给 ProgramState 挂 map；addTransition 提交状态变更生成
 *   ExplodedGraph 后继；generateNonFatalErrorNode+PathSensitiveBugReport+
 *   emitReport 是报警三步曲；getBaseRegion 把子区域归一到分配粒度的基区域。
 *
 * 【关键坑】① PtrAliasMap 声明了但本 checker 未使用——纯演示状态宏写法（论文
 *   合成 checker 里它跟踪指针别名）；② checkLocation 是空实现——演示"一个
 *   checker 可同时订阅多个回调"；③ 用 getMemRegionFromExpr(CE, C) 对整个
 *   CallExpr 求值拿到"调用的返回值区域"，而非 Call API 直取——刻意示范论文
 *   utility 函数的用法（few-shot 教学目的）。
 * ========================================================================== */
// ---- CSA checker 标准头组 ----
// BugReporter/BugType：报警对象与 bug 类别
#include "clang/StaticAnalyzer/Core/BugReporter/BugReporter.h"
#include "clang/StaticAnalyzer/Core/BugReporter/BugType.h"
// Taint：CSA 污点追踪 API（本示例 using 了但未实际调用，保留标准头组形态）
#include "clang/StaticAnalyzer/Checkers/Taint.h"
// Checker：checker 基类模板；CallEvent：调用事件抽象；CheckerContext：回调上下文
#include "clang/StaticAnalyzer/Core/Checker.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/CallEvent.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/CheckerContext.h"
// Environment/ProgramState/ProgramStateTrait/SymExpr：符号执行核心（状态、map 注册宏、符号表达式）
#include "clang/StaticAnalyzer/Core/PathSensitive/Environment.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/ProgramState.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/ProgramStateTrait.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/SymExpr.h"
// CheckerRegistry：plugin 加载后的 checker 注册入口
#include "clang/StaticAnalyzer/Frontend/CheckerRegistry.h"
#include "llvm/Support/raw_ostream.h"
// 论文的 9 个 utility functions（本 checker 用到 getMemRegionFromExpr，安装于 clang/include/.../Checkers/）
#include "clang/StaticAnalyzer/Checkers/utility.h"

// AST 遍历工具头（本示例未直接用；保留标准头组形态）
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/AST/StmtVisitor.h"

using namespace clang;  // Clang 主体命名空间（AST/ASTContext 等）
using namespace ento;   // clang::ento——CSA 引擎命名空间（SVal/MemRegion/CheckerContext 等）
using namespace taint;  // 污点追踪命名空间（TaintTag 等；本示例未实际消费）

// Program state map to track uninitialized memory regions
// ↑ 原注释（保留）。中文说明：给 ProgramState 挂一张 map<const MemRegion*, bool>，
//   key=内存区域，value=是否未初始化（true=kmalloc 脏内存 / false=kzalloc 清零）。
//   宏会生成 trait 与 State->set<UninitMemoryMap>(...) / State->get<...>(...) 帮手——
//   与论文速查卡"PossibleNullPtrMap 跟踪未检查空指针的 MemRegion"同一机制
REGISTER_MAP_WITH_PROGRAMSTATE(UninitMemoryMap, const MemRegion *, bool)
// Program state map to track pointer aliasing
// ↑ 原注释（保留）。中文说明：别名表 map<MemRegion*, MemRegion*>（源区域→别名区域），
//   供指针赋值后同步"脏/干净"标记用。本示例声明未使用，仅演示注册写法
REGISTER_MAP_WITH_PROGRAMSTATE(PtrAliasMap, const MemRegion*, const MemRegion*)

// 匿名命名空间：内部链接，符号不外泄（plugin 编译单元惯例）
namespace {

// Checker<...> 模板参数=订阅的回调事件集：PostCall（调用后）+ PreCall（调用前）
// + Location（内存位置访问）——CSA 在 ExplodedGraph 展开中按事件回调本类成员
class SAGenTestChecker : public Checker<check::PostCall, check::PreCall, check::Location> {
   mutable std::unique_ptr<BugType> BT;  // bug 类别对象；mutable 因回调都是 const 成员而构造要延迟写它（此处构造函数里直接初始化）

   public:
      // BugType(所属 checker, bug 名)：报警的分类标签；"Kernel Information Leak" 会出现在诊断头
      SAGenTestChecker() : BT(new BugType(this, "Kernel Information Leak")) {}

      // 三个回调的声明（实现在下）——CSA 事件驱动：kmalloc/kzalloc 返回后打标（PostCall）、
      // copy_to_user 调用前查标（PreCall）、Location 空转（演示）
      void checkPostCall(const CallEvent &Call, CheckerContext &C) const;
      void checkPreCall(const CallEvent &Call, CheckerContext &C) const;
      void checkLocation(SVal Loc, bool isLoad, const Stmt *S, CheckerContext &C) const;

   private:
      void reportInfoLeak(const MemRegion *MR, CheckerContext &C) const;  // 报警辅助：生成错误节点+BugReport
};

// ===== checkPostCall：分配函数返回后，在状态里给堆区域打"脏/干净"标记 =====
// kmalloc 不清零（脏=true）→ 有信息泄露风险；kzalloc 清零（false）→ 安全
void SAGenTestChecker::checkPostCall(const CallEvent &Call, CheckerContext &C) const {
  ProgramStateRef State = C.getState();  // 当前 ExplodedNode 的 ProgramState（引用计数不可变对象，改状态=派生新状态）
  const IdentifierInfo *Callee = Call.getCalleeIdentifier();  // 被调函数名（函数指针/内联后可能为 null）
  if (!Callee)
    return;

  if (Callee->getName() == "kmalloc") {
    // Track kmalloc allocations, mark memory as uninitialized
    // ↑ 原注释（保留）
    const Expr *expr = Call.getOriginExpr();  // 调用点对应的 AST 表达式（无源表达式时 null）
    if (!expr)
      return;

    const CallExpr *CE = dyn_cast<CallExpr>(expr);  // 收窄为 CallExpr（utility 函数收 Expr*）
    if (!CE)
      return;

    const MemRegion *MR = getMemRegionFromExpr(CE, C);  // 论文 utility ⑤：对整个 CallExpr 求值→SVal→MemRegion，即"本次调用返回值所指的堆区域"（刻意示范 utility 用法而非 Call::getReturnValue）
    if (!MR)
      return;

    MR = MR->getBaseRegion();  // 归一到基区域（剥掉字段偏移等子区域），保证与 copy_to_user 处的 map key 可对上
    if (!MR)
      return;
    State = State->set<UninitMemoryMap>(MR, true);  // 派生新状态：该区域标记"未初始化"（true=脏）
    C.addTransition(State);  // 提交状态变更：在 ExplodedGraph 上生成后继节点（不调 addTransition 的新状态会被丢弃）
  } else if (Callee->getName() == "kzalloc") {
    // Track kzalloc allocations, which zero-initialize memory
    // ↑ 原注释（保留）。与 kmalloc 分支同构，仅标记值不同（false=已清零）
    const Expr *expr = Call.getOriginExpr();
    if (!expr)
      return;

    const CallExpr *CE = dyn_cast<CallExpr>(expr);
    if (!CE)
      return;

    const MemRegion *MR = getMemRegionFromExpr(CE, C);  // 同上：返回值→堆区域
    if (!MR)
      return;

    MR = MR->getBaseRegion();  // 同样的基区域归一
    if (!MR)
      return;
    State = State->set<UninitMemoryMap>(MR, false);  // kzalloc 清零：标记"已初始化"，覆盖可能的脏标记
    C.addTransition(State);
  }
}

// ===== checkPreCall：copy_to_user 调用前，检查源缓冲是否为"脏"区域 =====
// copy_to_user(void __user *to, const void *from, unsigned long n)：1 号参数=内核源缓冲
void SAGenTestChecker::checkPreCall(const CallEvent &Call, CheckerContext &C) const {
  ProgramStateRef State = C.getState();
  const IdentifierInfo *Callee = Call.getCalleeIdentifier();
  if (!Callee)
    return;

  // Check for copy_to_user(user_dst, kernel_src, size)
  // ↑ 原注释（保留）
  if (Callee->getName() == "copy_to_user") {
    SVal Arg1 = Call.getArgSVal(1);  // 取 1 号实参（0-based，即 kernel_src）的符号值
    const MemRegion *MR = Arg1.getAsRegion();  // SVal→区域（这里直接用 SVal API，不再绕 utility——两个途径并存的教学样例）
    if (!MR)
      return;

    MR = MR->getBaseRegion();  // 与 PostCall 打标时相同的归一化，保证查得到
    if (!MR)
      return;
    const bool *Uninit = State->get<UninitMemoryMap>(MR);  // 查脏标记（map 未记录时返回 null 指针）
    if (Uninit && *Uninit) {  // 有记录且为 true：脏内存即将出内核——命中 bug pattern
      reportInfoLeak(MR, C);  // 报警
    }
  }
}

// ===== checkLocation：内存位置访问回调（本示例空实现） =====
// 演示"一个 checker 可订阅多个回调"；真正的读写追踪（把脏区域洗白）可在此扩展
void SAGenTestChecker::checkLocation(SVal Loc, bool isLoad, const Stmt *S, CheckerContext &C) const {

}

// ===== 报警三步曲：错误节点 → 路径敏感报告 → 提交 =====
void SAGenTestChecker::reportInfoLeak(const MemRegion *MR, CheckerContext &C) const {
  ExplodedNode *N = C.generateNonFatalErrorNode();  // 在 ExplodedGraph 上生成错误节点（非致命=路径继续探索；null=该路径已被饱和/剪枝，须放弃）
  if (!N)
    return;

  // PathSensitiveBugReport：携带从入口到出错点的完整路径，诊断时会展示 trace path
  //（对应论文 §3.2 报告蒸馏里保留的 relevant lines + trace path）
  auto report = std::make_unique<PathSensitiveBugReport>(
      *BT, "Potential kernel information leak due to uninitialized kmalloc memory being copied to user space", N);
  C.emitReport(std::move(report));  // 交给 BugReporter（后续由 CSA 去重、排序、输出）
}

} // end anonymous namespace

// plugin 注册入口：.exports 导出的 clang_registerCheckers 指到这里（CSA 加载 .so 时调）
// "custom.SAGenTestChecker" 是 -analyzer-checker= 过滤用的全名；第二参是描述；第三参为空文档 URI
extern "C" void clang_registerCheckers(CheckerRegistry &registry) {
  registry.addChecker<SAGenTestChecker>(
      "custom.SAGenTestChecker",
      "Detects kernel information leaks by uninitialized kmalloc memory being copied to user space",
      "");
}

// plugin ABI 版本协商串（.exports 导出的第二个符号；与加载方 CLANG_ANALYZER_API_VERSION_STRING 比对）
extern "C" const char clang_analyzerAPIVersionString[] =
    CLANG_ANALYZER_API_VERSION_STRING;
