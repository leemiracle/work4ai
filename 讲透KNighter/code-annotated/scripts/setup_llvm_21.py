# =====================================================================================
# [模块定位] KNighter 的 LLVM-21.1.0 环境搭建脚本（fork 增量：V8/Chromium 目标专用，
#            上游 PR #14 引入，配套 "feat: implement run_checker for v8"）。
#            流程与 setup_llvm.py 完全同构（函数名同为 setup_llvm），仅五处差异：
#            ① 版本字面量 18.1.8 → 21.1.0；② Checkers 的 CMake 源清单按 21 目录重抄
#            （11 删 11 增）；③ build 目录改增量编译（rm -rf 被注释掉）；
#            ④ cmake 追加 compiler-rt/clang-tools-extra 与 libcxx 自举参数；
#            ⑤ make 失败时编译日志落盘 build_log.txt/build_err.txt。
#
# [论文映射] 论文 Generability 讨论的 V8/Chromium 目标扩展（fork 增量线，对应
#            src/targets/ 的 v8 target）在环境层的痕迹：V8 源码重度使用 C++20/23
#            新特性，宿主机发行版 libstdc++ 跟不上，必须用 LLVM 21 新 clang +
#            自举 libc++ 才能解析构建（差异④的动机）。其余角色与 setup_llvm.py
#            相同：§3.1 Checker Synthesis / §3.1.4 Validation / §3.2 Refinement
#            的编译与扫描基座。
#
# [管线角色] 与 setup_llvm.py 相同（SAGenTestPlugin 脚手架 + utility 注入 + 全量构建），
#            区别只在服务目标：Linux 内核线（论文主线）用 18.1.8，V8 线用 21.1.0，
#            按 global_config 的 LLVM_dir 指向择一。
#
# [依赖与坑] 继承 setup_llvm.py 全部坑（相对路径 CWD、cp 无 check 静默失败、-j32
#            硬编码、CMakeLists 覆盖写），另加三条：① make 成功时输出被
#            capture_output 吞掉，终端无编译进度、静默数小时属正常；②
#            build_log/err.txt 用相对路径写，落点=脚本运行时 CWD 而非 build 目录；
#            ③ .decode("utf-8") 遇编译器输出的非 UTF-8 字节会 UnicodeDecodeError，
#            日志反而写不出来。
# =====================================================================================
import subprocess as sp  # 子进程执行外部命令：wget/unzip/cp/cmake/make 全靠它（21 版不再用 rm，见差异③）
from pathlib import Path  # 面向对象路径操作：拼接 / 重命名 / resolve 绝对化

from fire import Fire  # Google Fire：函数参数直转 CLI 参数（用法见文件尾 __main__）
from loguru import logger  # 日志门面：info/warning/error/success 四级


# 职责：搭建 KNighter 专用 LLVM-21.1.0 环境（V8/Chromium 目标线）。四步流水与 18 版
#   同构：① 下载 21.1.0 源码 → ② create_plugin.py SAGenTest 注入 plugin 脚手架 →
#   ③ utility.cpp/h 注入 + 覆盖 Checkers CMakeLists → ④ cmake/make 全量编译 +
#   make SAGenTestPlugin。五处差异（版本字面量/源清单/增量构建/cmake 参数/失败日志）
#   详见文件头与各差异点注释。
# 参数：llvm_dir_str —— LLVM 源码树目标路径（fire 从 CLI 位置参数注入）；已存在则
#       跳过 ①（幂等，可重复运行）。
# 返回：None；cmake/make 失败仅 logger.error 后 return（温和失败，不抛异常）。
# 论文语义：fork 增量线（论文 Generability 的 V8 目标）的编译与扫描基座。

def setup_llvm(llvm_dir_str: str):
    llvm_dir = Path(llvm_dir_str)  # 字符串转 Path，后续路径操作统一基于它
    if not llvm_dir.exists():  # 幂等闸门：目录已存在则跳过整个下载分支（重复运行安全）
        logger.warning(f"LLVM directory {llvm_dir} does not exist.")  # warning 级别：缺目录是待办不是错误——进入下载分支

        # Download the zip file
    # ↓ ① 获取 21.1.0 源码四连：wget tag zip → unzip → rename → 删 zip。
    #   差异①：版本字面量全部换成 21.1.0（zip 名/URL/解压目录名/日志文案共 5 处），
    #   其余逻辑与 18 版逐字节相同。21.1.0 = 2025-09 起的稳定分支，V8 线所需。

        zip_filename = "llvmorg-21.1.0.zip"  # GitHub tag 归档名（tag 固定命名 llvmorg-<版本>；此处即差异①之一）
        zip_path = llvm_dir.parent / zip_filename  # zip 放目标目录的父目录——与稍后的解压产物同级

        logger.info("Downloading LLVM 21.1.0 source...")  # 21 版日志文案带版本号（18 版只写 "Downloading LLVM source..."）
        sp.run(  # 列表式传参（不经 shell，无注入/通配歧义）；对比后面 cmake/make 用 shell=True
            [
                "wget",  # 官方 tag 归档 URL（21.1.0）
                "https://github.com/llvm/llvm-project/archive/refs/tags/llvmorg-21.1.0.zip",
                "-O",  # 显式指定输出文件名（不依赖服务器命名）
                str(zip_path),
            ],
            cwd=llvm_dir.parent,  # 工作目录=父目录：zip 与解压产物都落这里
            check=True,  # 下载失败抛 CalledProcessError 硬终止——没源码一切免谈
        )

        logger.info("Extracting LLVM source...")  # 解压（21 代码量更大，耗时更长）
        # Extract the zip file - this creates llvm-project-llvmorg-21.1.0/
        sp.run(["unzip", str(zip_path)], cwd=llvm_dir.parent, check=True)  # 解压出固定名目录 llvm-project-llvmorg-21.1.0/；check=True 失败即终止

        # Rename the extracted directory to the desired llvm_dir name
        extracted_dir = llvm_dir.parent / "llvm-project-llvmorg-21.1.0"  # GitHub tag zip 解压出的固定目录名（21.1.0）
        if extracted_dir.exists():  # 防御：万一解压名不符则跳过改名（不影响后续 mkdir 语义）
            extracted_dir.rename(llvm_dir)  # 原子改名为调用方指定的 llvm_dir——对外约定统一用该名字（global_config 的 LLVM_dir）

        # Delete the zip file
        logger.info("Cleaning up zip file...")
        zip_path.unlink()  # 删 zip 释放磁盘

    llvm_abs_dir = llvm_dir.resolve()  # 转绝对路径：cp 目标前缀。cp 子进程继承脚本 CWD，绝对化后才与 CWD 无关

    # Prepare the plugin files
    logger.info("Copying plugin files...")  # 步骤②：注入 plugin 脚手架（与 18 版完全一致）
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
    #   {id}Checker——SAGenTest 是全家族的"模板姓"。21 版 V8 线同样复用此机制
    #   （src/tests/clang-v8.cpp 的 SAGenTestChecker 即该占位名下的 V8 checker）。

    sp.run(["python3", "create_plugin.py", "SAGenTest"], cwd=plugin_work_dir.absolute())  # 无 check；cwd 必须 absolute()——create_plugin.py 内部按相对路径工作

    # Prepare utility functions
    logger.info("Copying utility functions...")  # 步骤③：注入 utility functions（与 18 版完全一致）
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
    # ↓↓↓ 差异②：整体覆盖写 clang/lib/StaticAnalyzer/Checkers/CMakeLists.txt ↓↓↓
    # 目的与 18 版相同：把 utility.cpp 塞进 add_clang_library(clangStaticAnalyzerCheckers ...)
    # 的源清单（字符串倒数段 utility.cpp 一行，全文件唯一"私货"），编进
    # libclangStaticAnalyzerCheckers.a 供 plugin 链接（utility 调用符号由此解析）。
    # 本清单按 LLVM 21.1.0 该目录实际文件重抄——与 18 版相比 11 删 11 增、行数守恒 134：
    #   删除 11：ArrayBoundCheckerV2 / CheckSizeofPointer / IdenticalExprChecker /
    #     MallocOverflowSecurityChecker / PointerIterationChecker / PointerSortingChecker /
    #     cert/PutenvWithAutoChecker / WebKit/{NoUncountedMembers,UncountedCallArgs,
    #     UncountedLambdaCaptures,UncountedLocalVars}Checker
    #   新增 11：AssumeModeling / NoOwnershipChangeVisitor / PutenvStackArrayChecker
    #     （= cert/PutenvWithAutoChecker 更名并移出 cert/）/ SetgidSetuidOrderChecker /
    #     WebKit/{ForwardDecl,MemoryUnsafeCast,RetainPtrCtorAdopt}Checker /
    #     WebKit/RawPtrRef{CallArgs,LambdaCaptures,LocalVars,Member}Checker
    #     （WebKit 家族 Uncounted* → RawPtrRef* 大更名=上游 raw-ptr/ref 方案落地；
    #      cert/InvalidPtrChecker 两版都保留）
    # 注意：CMake 只校验"列出的文件必须存在"，漏列的 checker 只是不参与编译，不影响
    # utility 注入与 plugin 链接——清单微误不致命；但列出不存在的文件会直接报错。
    # 清单四段结构：LLVM_LINK_COMPONENTS（链接组件）/ add_clang_library 源清单 /
    # LINK_LIBS（clangAST·ASTMatchers·Analysis·Basic·Lex·StaticAnalyzerCore）/
    # DEPENDS（omp_gen、ClangDriverOptions）。

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
  AssumeModeling.cpp
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
  NoOwnershipChangeVisitor.cpp
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
  PointerSubChecker.cpp
  PthreadLockChecker.cpp
  PutenvStackArrayChecker.cpp
  RetainCountChecker/RetainCountChecker.cpp
  RetainCountChecker/RetainCountDiagnostics.cpp
  ReturnPointerRangeChecker.cpp
  ReturnUndefChecker.cpp
  ReturnValueChecker.cpp
  RunLoopAutoreleaseLeakChecker.cpp
  SetgidSetuidOrderChecker.cpp
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
  WebKit/ASTUtils.cpp
  WebKit/ForwardDeclChecker.cpp
  WebKit/MemoryUnsafeCastChecker.cpp
  WebKit/PtrTypesSemantics.cpp
  WebKit/RefCntblBaseVirtualDtorChecker.cpp
  WebKit/RetainPtrCtorAdoptChecker.cpp
  WebKit/RawPtrRefCallArgsChecker.cpp
  WebKit/RawPtrRefLambdaCapturesChecker.cpp
  WebKit/RawPtrRefLocalVarsChecker.cpp
  WebKit/RawPtrRefMemberChecker.cpp
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
    logger.info("Building LLVM...")  # 步骤④：构建（21 全量更贵，好在差异③让重跑可增量续编）
    # mkdir -p $LLVM_DIR/build
    build_dir = llvm_dir / "build"  # 构建目录约定 $LLVM_DIR/build——下游按 build/lib/SAGenTestPlugin.so 取产物
    # ↓ 差异③：build 目录改增量复用——18 版的"存在则 rm -rf 全量重建"两行被注释
    #   保留（原文对照），mkdir(exist_ok=True) 允许带着旧缓存续编。动机：LLVM 21
    #   全量构建更贵，且 V8 线 checker 迭代期会反复跑本脚本，每次删掉数小时的
    #   编译缓存不可接受。

    # Delete the build directory if it exists  # 18 版在此删除旧 build 目录；21 版注释掉（差异③）
    # if build_dir.exists():  # 18 版的删除逻辑（注释保留供对照，不执行）
    #     sp.run(["rm", "-rf", build_dir])  # 同上——被注释的两行
    build_dir.mkdir(exist_ok=True)  # exist_ok=True：旧 build 直接复用做增量编译（18 版是无条件重建）

    # cmake
    # cmake -DLLVM_ENABLE_PROJECTS="clang;lld" -DLLVM_TARGETS_TO_BUILD=X86 -DCMAKE_BUILD_TYPE=Release -G "Unix Makefiles" ../llvm
    # ↓ 配置阶段——差异④（V8 动机）。基础参数与 18 版相同（clang+lld 裁剪 / 仅 X86 /
    #   Release / Unix Makefiles / ../llvm），追加五项：
    #   · ENABLE_PROJECTS 追加 "compiler-rt;clang-tools-extra"——V8 构建工具链所需
    #   · ENABLE_RUNTIMES="libcxx;libcxxabi;libunwind"——runtimes 走二阶段构建：用
    #     刚编出的 clang 再编 libc++ 全家（自举），产出与 clang 同版本的标准库
    #   · LLVM_ENABLE_LIBCXX=ON——工具链默认链 libc++ 而非宿主机 libstdc++
    #   · LIBCXX_ENABLE_INCOMPLETE_FEATURES=ON——放行 libc++ 未完成的 C++20/23 设施
    #   动机：V8/Chromium 代码库重度使用 C++20/23 新特性，宿主机发行版 libstdc++
    #   太旧解析不了 V8 源码，必须整套自举——这正是 V8 线需要 LLVM 21 新 clang 的原因。
    # 此步同时把 create_plugin.py 注入的 add_subdirectory(SAGenTestHandling) 接入构建
    # （create_plugin.py 尾注：新增 plugin 后必须重新 cmake 才能编译——本脚本先
    #  create_plugin.py 后 cmake，顺序正确）。

    res = sp.run(  # shell=True 整串命令：引号语义交给 /bin/sh（参数差异见上方注释）
        'cmake -DLLVM_ENABLE_PROJECTS="clang;lld;compiler-rt;clang-tools-extra" -DLLVM_TARGETS_TO_BUILD=X86 -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_RUNTIMES="libcxx;libcxxabi;libunwind" -DLLVM_ENABLE_LIBCXX=ON -DLIBCXX_ENABLE_INCOMPLETE_FEATURES=ON -G "Unix Makefiles" ../llvm',
        cwd=build_dir,  # 构建目录内执行
        shell=True,  # 整串交 shell 执行
    )  # res=CompletedProcess：下方手动检查 returncode（未用 check=True）
    if res.returncode != 0:  # 配置失败（缺依赖/源清单与目录不符/编译器过老）
        logger.error("CMake failed.")  # 只记日志
        return  # 温和退出——不抛异常，由人工看日志处置

    # make
    # ↓ 全量编译（差异⑤a）：编译全部目标 + utility.cpp（随 clangStaticAnalyzerCheckers
    #   库产出）。-j32 硬编码 32 并行度。与 18 版差异：capture_output=True——成功时
    #   编译日志被吞（终端无进度，静默数小时属正常）；失败时由下方两行落盘排查。

    make_res = sp.run("make -j32", cwd=build_dir, shell=True, capture_output=True)  # 全量构建；capture_output=True 为差异⑤（成功时终端无编译进度）
    if make_res.returncode != 0:  # 编译失败（OOM 最常见）→ 下方两行落盘日志排查
        logger.error("Make failed.")  # 记日志
    # ↓ 差异⑤b：编译失败时把 make 的 stdout/stderr 落盘（LLVM 21 全量构建错误输出
    #   巨大，终端回滚缓冲看不全）。三个坑：①相对路径——文件写到脚本运行时 CWD
    #   （通常=KNighter 仓根）而非 build 目录；②decode("utf-8") 遇非 UTF-8 字节
    #   会 UnicodeDecodeError，在写日志这步再炸一次；③真正的错误通常在 stderr
    #   （build_err.txt），stdout（build_log.txt）多为正常编译输出。

        Path("build_log.txt").write_text(make_res.stdout.decode("utf-8"))  # make 的 stdout（正常编译输出）→ 当前工作目录的 build_log.txt
        Path("build_err.txt").write_text(make_res.stderr.decode("utf-8"))  # make 的 stderr（错误信息通常在这里）→ build_err.txt
        return  # 温和退出

    # ↓ 单独链接 SAGenTestPlugin 目标（与 18 版完全一致）：add_llvm_library(
    #   SAGenTestPlugin MODULE BUILDTREE_ONLY ...)——MODULE=可动态加载 .so；
    #   BUILDTREE_ONLY=只在构建树产出、不随 install 安装。依赖（含 utility 符号）
    #   已由上一步全量 make 备齐，此步只做链接，秒级完成。产物
    #   build/lib/SAGenTestPlugin.so = 扫描命令 -load-plugin 的加载对象。

    make_res = sp.run("make SAGenTestPlugin -j32", cwd=build_dir, shell=True)  # 单独构建 plugin 目标（全量 make 已备齐依赖，此步秒级）
    if make_res.returncode != 0:  # 链接失败（多为 utility 符号/头文件问题）
        logger.error("Make failed.")  # 记日志
        return  # 温和退出
    logger.success("LLVM setup completed.")  # 全绿：V8 线环境就绪


if __name__ == "__main__":  # 直接运行入口（python3 scripts/setup_llvm_21.py LLVM_PATH）
    Fire(setup_llvm)  # fire：CLI 位置参数 LLVM_PATH 绑定到 setup_llvm(llvm_dir_str)
