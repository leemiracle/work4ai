# =====================================================================================
# [模块定位] KNighter 的 LLVM-18.1.8 一键环境搭建脚本（论文主线 / Linux 内核目标专用）：
#            下载源码 → 注入 SAGenTest plugin 脚手架与 9 个 utility functions →
#            覆盖式改写 StaticAnalyzer Checkers 的 CMakeLists → cmake + make 全量编译。
#            终产物 = $LLVM_DIR/build/lib/SAGenTestPlugin.so（clang -load-plugin 加载对象）。
#
# [论文映射] 论文 §4/§5 软硬件环境的工程前提，支撑 §3.1 Algorithm 1 全流程：
#            §3.1.3 Implementation+Syntax Repair 产出的 checker.cpp 编译为 CSA plugin、
#            §3.1.4 Validation 的 buggy/patched 差分扫描、§3.2 Refinement 全库扫描，
#            全部跑在这棵定制 LLVM 树上。scripts/README.md 明言本脚本为 "self-repair"
#            阶段准备 SAGenTestPlugin——repair agent（maxAttempts=5）反复编译试错的
#            载体就是这个固定名字的 plugin target。
#
# [管线角色] 上游：人工一次性环境准备（主 README "Setting up"：python3 scripts/
#            setup_llvm.py LLVM_PATH）。下游：src/checker_scan.py 的 scan_batch_checkers()
#            在同一棵树上为每个合成 checker 跑 create_plugin.py {id}，并把 checker 源码
#            类名 SAGenTestChecker 批量替换为 {id}Checker；src/kernel_commands.py 生成
#            -load-plugin $LLVM/build/lib/SAGenTestPlugin.so
#            -enable-checker custom.SAGenTestChecker 扫描命令。
#
# [依赖与坑] ① 需 pip 装 fire、loguru；② 必须在 KNighter 仓根运行——cp 源是相对路径
#            llvm_utils/...；③ plugin/utility 的 cp 与 create_plugin.py 调用均无
#            check=True，源缺失静默失败，错误延迟到 cmake/make 才爆；④ make -j32
#            硬编码 32 并行度；⑤ LLVM 全量 Release 构建 1-3 小时、约 20GB 磁盘；
#            ⑥ CMakeLists 整体覆盖写，清单须与 18.1.8 目录实际文件对齐（见 L80 上注释）。
#            与 setup_llvm_21.py（V8 目标）的逐点差异也见该处注释。
# =====================================================================================
import subprocess as sp  # 子进程执行外部命令：wget/unzip/cp/rm/cmake/make 全靠它
from pathlib import Path  # 面向对象路径操作：拼接 / 重命名 / resolve 绝对化

from fire import Fire  # Google Fire：函数参数直转 CLI 参数（用法见文件尾 __main__）
from loguru import logger  # 日志门面：info/warning/error/success 四级


# 职责：搭建 KNighter 专用 LLVM-18.1.8 环境，四步流水：
#   ① llvm_dir 不存在 → 下载 llvmorg-18.1.8.zip 并解压改名；
#   ② 注入 plugin 脚手架（create_plugin.py SAGenTest）；
#   ③ 注入 utility.cpp/h 并整体改写 Checkers 的 CMakeLists；
#   ④ cmake 配置 + make -j32 全量编译 + make SAGenTestPlugin 链出 plugin .so。
# 参数：llvm_dir_str —— LLVM 源码树目标路径（fire 从 CLI 位置参数注入）；已存在则
#       跳过 ①（幂等，可重复运行）。
# 返回：None；cmake/make 失败仅 logger.error 后 return（温和失败，不抛异常）。
# 论文语义：§3.1 Algorithm 1 的编译与扫描基座（详见文件头注释）。

def setup_llvm(llvm_dir_str: str):
    llvm_dir = Path(llvm_dir_str)  # 字符串转 Path，后续路径操作统一基于它
    if not llvm_dir.exists():  # 幂等闸门：目录已存在则跳过整个下载分支（重复运行安全）
        logger.warning(f"LLVM directory {llvm_dir} does not exist.")  # warning 级别：缺目录是待办不是错误——进入下载分支

        # Download the zip file
    # ↓ ① 获取 18.1.8 源码四连：wget tag zip → unzip → rename → 删 zip。
    #   18.1.8 = 论文实验固定版本（scripts/README.md："specifically for the LLVM-18.1.8"）；
    #   V8 目标需要更新的 clang，见 setup_llvm_21.py（差异①）。

        zip_filename = "llvmorg-18.1.8.zip"  # GitHub tag 归档名（tag 固定命名 llvmorg-<版本>）
        zip_path = llvm_dir.parent / zip_filename  # zip 放目标目录的父目录——与稍后的解压产物同级

        logger.info("Downloading LLVM source...")  # 约 200MB，视网络数分钟
        sp.run(  # 列表式传参（不经 shell，无注入/通配歧义）；对比后面 cmake/make 用 shell=True
            [
                "wget",  # 官方 tag 归档 URL
                "https://github.com/llvm/llvm-project/archive/refs/tags/llvmorg-18.1.8.zip",
                "-O",  # 显式指定输出文件名（不依赖服务器命名）
                str(zip_path),
            ],
            cwd=llvm_dir.parent,  # 工作目录=父目录：zip 与解压产物都落这里
            check=True,  # 下载失败抛 CalledProcessError 硬终止——没源码一切免谈
        )

        logger.info("Extracting LLVM source...")  # 解压约 1-2 分钟
        # Extract the zip file - this creates llvm-project-llvmorg-18.1.8/
        sp.run(["unzip", str(zip_path)], cwd=llvm_dir.parent, check=True)  # 解压出固定名目录 llvm-project-llvmorg-18.1.8/；check=True 失败即终止

        # Rename the extracted directory to the desired llvm_dir name
        extracted_dir = llvm_dir.parent / "llvm-project-llvmorg-18.1.8"  # GitHub tag zip 解压出的固定目录名
        if extracted_dir.exists():  # 防御：万一解压名不符则跳过改名（不影响后续 mkdir 语义）
            extracted_dir.rename(llvm_dir)  # 原子改名为调用方指定的 llvm_dir——对外约定统一用该名字（global_config 的 LLVM_dir）

        # Delete the zip file
        logger.info("Cleaning up zip file...")
        zip_path.unlink()  # 删 zip 释放 ~200MB 磁盘

    llvm_abs_dir = llvm_dir.resolve()  # 转绝对路径：cp 目标前缀。cp 子进程继承脚本 CWD，绝对化后才与 CWD 无关

    # Prepare the plugin files
    logger.info("Copying plugin files...")  # 步骤②：注入 plugin 脚手架
    # cp llvm_utils/create_plugin.py $LLVM_DIR/clang/lib/Analysis/plugins/
    # ↓ 把 plugin 脚手架生成器拷进 LLVM 树（上方原注释即等价 shell 命令）

    sp.run(
        [  # 复制命令
            "cp",  # 相对路径——坑：必须在 KNighter 仓根运行本脚本
            "llvm_utils/create_plugin.py",  # 目标：LLVM 官方 plugin 目录（SampleAnalyzer 所在地）
            f"{llvm_abs_dir}/clang/lib/Analysis/plugins/",
        ]
    )  # 无 check=True：cp 失败静默（源不存在时错误延迟到 create_plugin.py 才爆）
    plugin_work_dir = llvm_dir / "clang" / "lib" / "Analysis" / "plugins"  # plugin 工作目录（下一步的 cwd）
    # python3 ./create_plugin.py SAGenTest
    # ↓ 在 plugins 目录内运行脚手架生成器（必须 cwd=plugins，其内部按相对路径读写 ./CMakeLists.txt）。
    #   占位名固定 SAGenTest（Static Analyzer Generated Test）：
    #   · 生成 SAGenTestHandling/ 子目录——CMakeLists（add_llvm_library(SAGenTestPlugin
    #     MODULE BUILDTREE_ONLY SAGenTestChecker.cpp) + clang_target_link_libraries）、
    #     SAGenTestChecker.cpp 空壳模板（Checker<check::PreCall>）、SAGenTestChecker.exports
    #     （只导出 clang_registerCheckers 与 clang_analyzerAPIVersionString 两个 C 符号）
    #   · 把 add_subdirectory(SAGenTestHandling) 注入 plugins/CMakeLists.txt 的 endif()
    #     之前——为后面的 cmake 接入做准备
    #   占位语义：扫描阶段 src/checker_scan.py 为每个合成 checker 执行 create_plugin.py
    #   {id} 生成 {id}Handling/，再把 checker 源码类名 SAGenTestChecker 批量替换为
    #   {id}Checker——SAGenTest 是全家族的"模板姓"。

    sp.run(["python3", "create_plugin.py", "SAGenTest"], cwd=plugin_work_dir.absolute())  # 无 check；cwd 必须 absolute()——create_plugin.py 内部按相对路径工作

    # Prepare utility functions
    logger.info("Copying utility functions...")  # 步骤③：注入 utility functions
    # cp llvm_utils/utility.cpp $LLVM_DIR/clang/lib/StaticAnalyzer/Checkers/
    # cp llvm_utils/utility.h $LLVM_DIR/clang/include/clang/StaticAnalyzer/Checkers/
    # ↓ 注入 9 个 utility functions（论文 §3.1.2 Plan Synthesis 提供给 LLM 的 utility
    #   清单；llvm_utils/utility.{h,cpp} 与 prompt_template/knowledge/utility.md 对应）。
    #   设计意图：把 MemRegion/SVal 等 CSA 底层操作封装成稳定函数，LLM 合成 checker 时
    #   只需 #include "utility.h" 直接调用，不必重写底层操作——显著降低 §3.1.3
    #   实现阶段的手滑错误。实现进 lib/（下方 CMakeLists 随库编译），头文件进
    #   include/（checker 源码引用）。

    sp.run(
        [  # 复制命令
            "cp",  # 9 个 utility 的实现（getMemRegionFromExpr 等）
            "llvm_utils/utility.cpp",  # → 官方 checker 源码目录（下方 CMakeLists 把它编进库）
            f"{llvm_abs_dir}/clang/lib/StaticAnalyzer/Checkers/",
        ]
    )
    sp.run(
        [  # 复制命令
            "cp",  # 头文件 → include/（合成 checker 源码 #include "utility.h" 直接引用）
            "llvm_utils/utility.h",  # → clang 头文件目录
            f"{llvm_abs_dir}/clang/include/clang/StaticAnalyzer/Checkers/",
        ]
    )

    # ↓ 步骤③b：定位 Checkers 库的构建清单（下面整体覆盖其内容）

    cmakefile = (
        llvm_dir / "clang" / "lib" / "StaticAnalyzer" / "Checkers" / "CMakeLists.txt"  # 待覆盖的目标：StaticAnalyzer Checkers 库的构建清单
    )
    # ↓↓↓ 整体覆盖写 clang/lib/StaticAnalyzer/Checkers/CMakeLists.txt ↓↓↓
    # 目的只有一个：把 KNighter 的 utility.cpp 塞进 add_clang_library(
    # clangStaticAnalyzerCheckers ...) 的源清单（见字符串倒数段 utility.cpp 一行，
    # 全文件唯一"私货"），使其编译进 libclangStaticAnalyzerCheckers.a；plugin 的
    # CMakeLists（create_plugin.py 生成）经 clang_target_link_libraries 链到该库，
    # 合成 checker 源码里的 utility 调用符号由此解析。
    # 策略：不 append 不 sed，直接 write_text 整体重写——上游文件结构随版本漂移，
    # 带上完整源清单最稳；代价=清单必须与 18.1.8 该目录实际文件逐一对上（CMake 对
    # 列出不存在的源文件直接报错；漏列的 checker 只是不参与编译，不影响本管线）。
    # 清单结构（四段）：
    #   set(LLVM_LINK_COMPONENTS ...)  链接的 LLVM 组件（FrontendOpenMP/Support/TargetParser）
    #   add_clang_library(clangStaticAnalyzerCheckers <源文件>)  官方 checker 共 134 项
    #     （含 cert/、MPI-Checker/、RetainCountChecker/、UninitializedObject/、WebKit/ 子目录）
    #   LINK_LIBS                      依赖的 clang 库（AST/ASTMatchers/Analysis/Basic/Lex/StaticAnalyzerCore）
    #   DEPENDS                        omp_gen、ClangDriverOptions（表生成依赖）
    # ◆ 与 setup_llvm_21.py 清单的差异②（上游 18→21 三年演进的快照，11 删 11 增、行数守恒）：
    #   18 独有 11：ArrayBoundCheckerV2 / CheckSizeofPointer / IdenticalExprChecker /
    #     MallocOverflowSecurityChecker / PointerIterationChecker / PointerSortingChecker /
    #     cert/PutenvWithAutoChecker / WebKit/{NoUncountedMembers,UncountedCallArgs,
    #     UncountedLambdaCaptures,UncountedLocalVars}Checker
    #   21 新增 11：AssumeModeling / NoOwnershipChangeVisitor / PutenvStackArrayChecker
    #     （= cert/PutenvWithAutoChecker 更名并移出 cert/）/ SetgidSetuidOrderChecker /
    #     WebKit/{ForwardDecl,MemoryUnsafeCast,RetainPtrCtorAdopt}Checker /
    #     WebKit/RawPtrRef{CallArgs,LambdaCaptures,LocalVars,Member}Checker
    #     （WebKit 家族 Uncounted* → RawPtrRef* 大更名，上游 raw-ptr/ref 方案落地；
    #      cert/InvalidPtrChecker 两版都在）

    new_cmakefile_content = """\
set(LLVM_LINK_COMPONENTS
  FrontendOpenMP
  Support
  TargetParser
  )

add_clang_library(clangStaticAnalyzerCheckers
  AnalysisOrderChecker.cpp
  AnalyzerStatsChecker.cpp
  ArrayBoundChecker.cpp
  ArrayBoundCheckerV2.cpp
  BasicObjCFoundationChecks.cpp
  BitwiseShiftChecker.cpp
  BlockInCriticalSectionChecker.cpp
  BoolAssignmentChecker.cpp
  BuiltinFunctionChecker.cpp
  CStringChecker.cpp
  CStringSyntaxChecker.cpp
  CallAndMessageChecker.cpp
  CastSizeChecker.cpp
  CastToStructChecker.cpp
  CastValueChecker.cpp
  CheckObjCDealloc.cpp
  CheckObjCInstMethSignature.cpp
  CheckPlacementNew.cpp
  CheckSecuritySyntaxOnly.cpp
  CheckSizeofPointer.cpp
  CheckerDocumentation.cpp
  ChrootChecker.cpp
  CloneChecker.cpp
  ContainerModeling.cpp
  ConversionChecker.cpp
  CXXDeleteChecker.cpp
  CXXSelfAssignmentChecker.cpp
  DeadStoresChecker.cpp
  DebugCheckers.cpp
  DebugContainerModeling.cpp
  DebugIteratorModeling.cpp
  DereferenceChecker.cpp
  DirectIvarAssignment.cpp
  DivZeroChecker.cpp
  DynamicTypePropagation.cpp
  DynamicTypeChecker.cpp
  EnumCastOutOfRangeChecker.cpp
  ErrnoChecker.cpp
  ErrnoModeling.cpp
  ErrnoTesterChecker.cpp
  ExprInspectionChecker.cpp
  FixedAddressChecker.cpp
  FuchsiaHandleChecker.cpp
  GCDAntipatternChecker.cpp
  GenericTaintChecker.cpp
  GTestChecker.cpp
  IdenticalExprChecker.cpp
  InnerPointerChecker.cpp
  InvalidatedIteratorChecker.cpp
  cert/InvalidPtrChecker.cpp
  Iterator.cpp
  IteratorModeling.cpp
  IteratorRangeChecker.cpp
  IvarInvalidationChecker.cpp
  LLVMConventionsChecker.cpp
  LocalizationChecker.cpp
  MacOSKeychainAPIChecker.cpp
  MacOSXAPIChecker.cpp
  MallocChecker.cpp
  MallocOverflowSecurityChecker.cpp
  MallocSizeofChecker.cpp
  MismatchedIteratorChecker.cpp
  MmapWriteExecChecker.cpp
  MIGChecker.cpp
  MoveChecker.cpp
  MPI-Checker/MPIBugReporter.cpp
  MPI-Checker/MPIChecker.cpp
  MPI-Checker/MPIFunctionClassifier.cpp
  NSAutoreleasePoolChecker.cpp
  NSErrorChecker.cpp
  NoReturnFunctionChecker.cpp
  NonNullParamChecker.cpp
  NonnullGlobalConstantsChecker.cpp
  NullabilityChecker.cpp
  NumberObjectConversionChecker.cpp
  ObjCAtSyncChecker.cpp
  ObjCAutoreleaseWriteChecker.cpp
  ObjCContainersASTChecker.cpp
  ObjCContainersChecker.cpp
  ObjCMissingSuperCallChecker.cpp
  ObjCPropertyChecker.cpp
  ObjCSelfInitChecker.cpp
  ObjCSuperDeallocChecker.cpp
  ObjCUnusedIVarsChecker.cpp
  OSObjectCStyleCast.cpp
  PaddingChecker.cpp
  PointerArithChecker.cpp
  PointerIterationChecker.cpp
  PointerSortingChecker.cpp
  PointerSubChecker.cpp
  PthreadLockChecker.cpp
  cert/PutenvWithAutoChecker.cpp
  RetainCountChecker/RetainCountChecker.cpp
  RetainCountChecker/RetainCountDiagnostics.cpp
  ReturnPointerRangeChecker.cpp
  ReturnUndefChecker.cpp
  ReturnValueChecker.cpp
  RunLoopAutoreleaseLeakChecker.cpp
  SimpleStreamChecker.cpp
  SmartPtrChecker.cpp
  SmartPtrModeling.cpp
  StackAddrEscapeChecker.cpp
  StdLibraryFunctionsChecker.cpp
  StdVariantChecker.cpp
  STLAlgorithmModeling.cpp
  StreamChecker.cpp
  StringChecker.cpp
  Taint.cpp
  TaintTesterChecker.cpp
  TestAfterDivZeroChecker.cpp
  TraversalChecker.cpp
  TrustNonnullChecker.cpp
  TrustReturnsNonnullChecker.cpp
  UndefBranchChecker.cpp
  UndefCapturedBlockVarChecker.cpp
  UndefResultChecker.cpp
  UndefinedArraySubscriptChecker.cpp
  UndefinedAssignmentChecker.cpp
  UndefinedNewArraySizeChecker.cpp
  UninitializedObject/UninitializedObjectChecker.cpp
  UninitializedObject/UninitializedPointee.cpp
  UnixAPIChecker.cpp
  UnreachableCodeChecker.cpp
  VforkChecker.cpp
  VLASizeChecker.cpp
  ValistChecker.cpp
  VirtualCallChecker.cpp
  WebKit/NoUncountedMembersChecker.cpp
  WebKit/ASTUtils.cpp
  WebKit/PtrTypesSemantics.cpp
  WebKit/RefCntblBaseVirtualDtorChecker.cpp
  WebKit/UncountedCallArgsChecker.cpp
  WebKit/UncountedLambdaCapturesChecker.cpp
  WebKit/UncountedLocalVarsChecker.cpp
  utility.cpp

  LINK_LIBS
  clangAST
  clangASTMatchers
  clangAnalysis
  clangBasic
  clangLex
  clangStaticAnalyzerCore

  DEPENDS
  omp_gen
  ClangDriverOptions
  )
"""
    cmakefile.write_text(new_cmakefile_content)  # 覆盖写（非追加）：上游原文件被整体替换——侵入式但一劳永逸

    # Build the LLVM
    logger.info("Building LLVM...")  # 步骤④：构建（全流程最耗时，Release 全量 1-3 小时@32 核）
    # mkdir -p $LLVM_DIR/build
    build_dir = llvm_dir / "build"  # 构建目录约定 $LLVM_DIR/build——下游按 build/lib/SAGenTestPlugin.so 取产物
    # Delete the build directory if it exists
    # ↓ 18 版策略：旧 build 目录（含全部 .o 缓存）存在则整个删掉、全量重建——
    #   简单粗暴，代价是每次重跑 setup 都重付全量编译时间。
    #   （21 版把这两行注释掉改 mkdir(exist_ok=True) 做增量，见 setup_llvm_21.py 差异③）

    if build_dir.exists():  # 旧构建目录存在（含全部编译缓存）？
        sp.run(["rm", "-rf", build_dir])  # 整目录删除（argv 传 Path 对象合法，subprocess 自动转字符串）；无 check
    build_dir.mkdir()  # 新建空 build（无 exist_ok：上一步刚删过或本就不存在）

    # cmake
    # cmake -DLLVM_ENABLE_PROJECTS="clang;lld" -DLLVM_TARGETS_TO_BUILD=X86 -DCMAKE_BUILD_TYPE=Release -G "Unix Makefiles" ../llvm
    # ↓ 配置阶段（shell=True 整串命令，引号语义交给 /bin/sh）：
    #   ENABLE_PROJECTS="clang;lld"  只启用 clang（CSA 宿主）+lld——刻意裁剪省时
    #   TARGETS_TO_BUILD=X86         只建 X86 后端（内核目标为 x86_64，够用）
    #   BUILD_TYPE=Release           Release 优化——扫描 3000 万行内核，性能关键
    #   -G "Unix Makefiles"          Make 生成器，与后续 make 配套（非 Ninja）
    #   ../llvm                      指向 LLVM 顶层 CMakeLists（相对 build 目录）
    # 此步同时把 create_plugin.py 注入的 add_subdirectory(SAGenTestHandling) 接入构建
    # （create_plugin.py 尾注：新增 plugin 后必须重新 cmake 才能编译——本脚本先
    #  create_plugin.py 后 cmake，顺序正确）；checker_scan.py 后续批量建 checker 时
    #  会重跑同一串 cmake 捡起新的 {id}Handling 子目录。

    res = sp.run(  # shell=True 整串命令：引号语义交给 /bin/sh（与前面列表式风格不一致）
        'cmake -DLLVM_ENABLE_PROJECTS="clang;lld" -DLLVM_TARGETS_TO_BUILD=X86 -DCMAKE_BUILD_TYPE=Release -G "Unix Makefiles" ../llvm',
        cwd=build_dir,  # 构建目录内执行
        shell=True,  # 整串交 shell 执行
    )  # res=CompletedProcess：下方手动检查 returncode（未用 check=True）
    if res.returncode != 0:  # 配置失败（缺依赖/源清单与目录不符/编译器过老）
        logger.error("CMake failed.")  # 只记日志
        return  # 温和退出——不抛异常，由人工看日志处置

    # make
    # ↓ 全量编译：clang+lld 全部目标 + 注入的 utility.cpp（随 clangStaticAnalyzerCheckers
    #   库一起产出）。-j32 硬编码 32 并行度：核少的机器会 OOM，核多的浪费。
    #   编译日志直吐终端（21 版改为捕获落盘，见 setup_llvm_21.py 差异⑤）。

    make_res = sp.run("make -j32", cwd=build_dir, shell=True)  # 全量构建：clang+lld 全目标+utility.cpp；-j32 硬编码 32 线程
    if make_res.returncode != 0:  # 编译失败（OOM 最常见）
        logger.error("Make failed.")  # 记日志
        return  # 温和退出

    # ↓ 单独链接 SAGenTestPlugin 目标（create_plugin.py 生成的
    #   add_llvm_library(SAGenTestPlugin MODULE BUILDTREE_ONLY ...)）：
    #   MODULE=可动态加载的 .so；BUILDTREE_ONLY=只在构建树产出、不随 install 安装。
    #   依赖（含 utility 符号）已由上一步全量 make 备齐，此步只做链接，秒级完成。
    #   产物 build/lib/SAGenTestPlugin.so = 扫描命令 -load-plugin 的加载对象
    #   （src/kernel_commands.py：-load-plugin $LLVM_dir/build/lib/SAGenTestPlugin.so
    #    -enable-checker custom.SAGenTestChecker）。

    make_res = sp.run("make SAGenTestPlugin -j32", cwd=build_dir, shell=True)  # 单独构建 plugin 目标（全量 make 已备齐依赖，此步秒级）
    if make_res.returncode != 0:  # 链接失败（多为 utility 符号/头文件问题）
        logger.error("Make failed.")  # 记日志
        return  # 温和退出
    logger.success("LLVM setup completed.")  # 全绿：环境就绪，可跑主管线（§3.1 合成→§3.1.4 差分验证→§3.2 refine）


if __name__ == "__main__":  # 直接运行入口（python3 scripts/setup_llvm.py LLVM_PATH，README "Setting up" 节）
    Fire(setup_llvm)  # fire：CLI 位置参数 LLVM_PATH 绑定到 setup_llvm(llvm_dir_str)
