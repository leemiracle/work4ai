# ============================================================================
# 【模块定位】KNighter 的 CSA（Clang Static Analyzer）集成后端：把 LLM 合成的
#   checker 源码编译为 LLVM plugin，驱动 scan-build 对目标代码库（Linux 内核 /
#   V8，fork 增量）做对象级与全库扫描，并从扫描输出解析 bug 计数与报告。
#
# 【论文映射】本文件是论文 §3.1 Algorithm 1 的"执行侧"：
#   - §3.1.3 Implementation：build_checker 把 checker.cpp 编译成 plugin
#     （编译失败时的语法修复循环在 checker_repair.py，读这里的 build_stderr 日志）；
#   - §3.1.4 Validation：validate_checker 做 buggy/patched 两次 checkout 的
#     差分验证（N_buggy vs N_patched，产出 TP/TN 计分）；
#   - §3.2 Refinement / 找 bug：run_checker 是全库与对象级扫描的执行入口。
#
# 【管线位置】上游：checker_gen.py（合成+修复后的 checker 源码，调用
#   validate_checker）、checker_refine.py（refine 后重扫）、checker_scan.py
#   （逐对象扫描）；下游：scan-build HTML 报告 → 本文件后半的 extract_reports
#   → triage agent。本类实现抽象基类 AnalysisBackendFactory（backends/
#   factory.py）约定的四个接口：build_checker / validate_checker / run_checker /
#   extract_reports（最后一个在本文件后半）。
#
# 【关键依赖与坑】
#   - backend_path 指向改过的 LLVM 仓：checker 以 plugins/<Name>Handling/
#     <Name>Checker.cpp 目录约定嵌入 clang/lib/Analysis/plugins/，CMake target
#     名固定为 <Name>Plugin；新 plugin 目录必须重跑 cmake 才对 make 可见；
#   - Linux 扫描走 `make LLVM=1`（对象级目标触发被 scan-build 包裹的 clang），
#     内置 checker 包 core/c++/deadcode/unix/nullability/security 被
#     -disable-checker 六连关闭，只跑合成 checker，避免内置报警淹没差分结果；
#   - -maxloop 4（V8 为 8）限制 CSA 符号执行的循环展开，防 ExplodedGraph 爆炸；
#   - scan-build 结尾统计行 "N bug(s) found." 由 get_num_bugs 正则解析；
#     clang 自身崩溃用输出特征串 "Please consider submitting a bug report" 识别；
#   - run_checker 哨兵值约定：-999=构建失败 / -1=超时 / -10=报警过多被截停；
#   - 多 checker 共存（build_checker_group，fork 增量）：每个 checker 改写出
#     唯一类名/注册名后各自成 plugin；配套 _generate_command_group 尚未接线
#     （标 FIXME），checker_scan.py 目前仍是单 checker 逐对象扫描。
# ============================================================================
import glob  # 文件通配扫描（本文件后半 extract_reports 扫报告目录用）
import json  # 解析 V8 构建产物 compile_commands.json
import os  # 环境变量/路径操作（V8 验证里要过滤 PATH 中的 depot_tools）
import random  # 报告随机采样（后半 extract_reports 采样送 triage 用）
import re  # 正则：解析 "N bug(s) found" 统计行、清洗唯一 checker 名等
import shlex  # 按 shell 词法切分编译命令串（从 V8 编译命令中提取 -o 目标）
import shutil  # 目录拷贝/清理（后半报告抽取阶段使用）
import subprocess as sp  # 驱动 make/ninja/cmake/scan-build 等子进程的核心通道
import threading  # 线程原语（后半 V8 并行分析用）
from collections import defaultdict  # 报告按对象/文件聚合的默认字典
from concurrent.futures import ThreadPoolExecutor, as_completed  # V8 多文件并行分析线程池
from datetime import datetime  # 输出目录时间戳命名（后半 _create_timestamped_output_dir）
from pathlib import Path  # 路径对象（本文件大量使用）
from typing import List, Optional, Tuple  # 类型注解

from html2text import html2text  # 第三方库：scan-build HTML 报告转 markdown（报告蒸馏）
from loguru import logger  # 结构化日志

from backends.factory import AnalysisBackendFactory  # 后端抽象基类（四个必须实现的接口）
from checker_data import ReportData  # 报告数据模型（pydantic，后半 extract_reports 的产出类型）
from targets.factory import TargetFactory  # 目标抽象工厂（linux / v8 两种实现的父类）
from targets.linux import Linux  # Linux 内核目标实现（类型注解 + 对象名映射规则）
from tools import monitor_build_output, remove_text_section  # 构建输出实时监控（warning 上限+超时杀进程）/ 报告 "Annotated Source Code" 节裁剪


# ----------------------------------------------------------------------------
# ClangBackend：CSA 后端的唯一实现类。
# 论文语义：LLM 只负责"写 checker"，本类负责让 checker 真正跑在 Clang Static
# Analyzer 引擎上——编译为 plugin（§3.1.3）、buggy/patched 差分验证（§3.1.4）、
# 全库/对象级扫描（§3.2）。继承 AnalysisBackendFactory 后实现 build_checker /
# validate_checker / run_checker / get_objects_from_report / extract_reports
# （后两个在本文件后半）。
# ----------------------------------------------------------------------------
class ClangBackend(AnalysisBackendFactory):
    """
    Concrete implementation of the Backend class for CSA.
    """
    # （原 docstring 保持不动）

    # Linux 扫描的默认 scan-build 参数表（参数对列表，_generate_command 逐对拼接）。
    # 要点：六个 -disable-checker 关闭 CSA 全部常用内置 checker 包，确保输出只
    # 含合成 checker 的报警——这是 §3.1.4 差分验证与 §3.2 全库扫描可比性的前提；
    # -maxloop 4 限制符号执行循环展开（ExplodedGraph 规模护栏）；
    # -o 指定 scan-build HTML 报告输出目录。
    _default_args = [
        ("-disable-checker", "core"),  # 关闭 core 包（逻辑错误类内置 checker）
        ("-disable-checker", "cplusplus"),  # 关闭 C++ 包
        ("-disable-checker", "deadcode"),  # 关闭死代码包
        ("-disable-checker", "unix"),  # 关闭 unix API 包（含 malloc 类检查）
        ("-disable-checker", "nullability"),  # 关闭可空注解包
        ("-disable-checker", "security"),  # 关闭安全类包
        ("-maxloop", 4),  # 循环展开上限 4 次（注意：原文件此处是裸整数，非字符串）
        ("-o", "tmp/SAGenTestCSAResult"),  # 报告输出目录（差分验证用默认值）
    ]

    # V8 扫描参数（fork 增量）：同样六连关内置包，但 -maxloop 提到 8——
    # V8 是 C++ 代码，循环体与状态机更深，4 次展开会大面积剪掉路径。
    _v8_args = [
        ("-disable-checker", "core"),  # 同上，六连关
        ("-disable-checker", "cplusplus"),  # .
        ("-disable-checker", "deadcode"),  # .
        ("-disable-checker", "unix"),  # .
        ("-disable-checker", "nullability"),  # .
        ("-disable-checker", "security"),  # .
        ("-maxloop", 8),  # V8 循环更深，展开上限放宽到 8（同为裸整数）
        ("-o", "tmp/SAGenTestCSAResult"),  # 报告输出目录
    ]

    # ----------------------------------------------------------------------------
    # build_checker（论文 §3.1.3 Implementation 的编译落地）
    # 职责：把一份 checker C++ 源码写进 LLVM plugin 树并编译为 <Name>Plugin.so。
    # 参数：checker_code=checker 源码文本；log_dir=编译日志目录；checker_name=
    #   plugin 基名（默认 SAGenTest，分组共存时换唯一名）；attempt=编译轮次
    #   （对应 §3.1.3 语法修复循环的第几次尝试，计入日志文件名）；jobs=make
    #   并行度；timeout=编译超时秒数。
    # 返回：(returncode, stderr 文本)。调用方 checker_repair.py 在 returncode!=0
    #   时触发 repair agent 按 stderr 修编译错误（论文：最多 maxAttempts=5 次）。
    # ----------------------------------------------------------------------------
    def build_checker(
        self,
        checker_code: str,
        log_dir: Path,
        checker_name="SAGenTest",
        attempt=1,
        jobs=8,
        timeout=300,
    ):
        """
        Build the checker in the CSA backend.

        Args:
            checker_code (str): The checker code to build.
        """
        # Write the checker code to a file
        checker_file_path = (  # plugin 源文件路径，四段拼接：
            self.backend_path  # LLVM 仓根
            / "clang/lib/Analysis/plugins"  # clang 官方 plugin 目录（多 checker 共存处）
            / f"{checker_name}Handling"  # 每 checker 一个独立子目录（create_plugin.py 的目录约定）
            / f"{checker_name}Checker.cpp"  # 源文件名与 checker 类基名一致
        )
        build_dir = self.backend_path / "build"  # LLVM 构建目录（make 在这里跑）
        if not checker_file_path.parent.exists():  # plugin 子目录须先由 create_plugin.py 建好
            raise FileNotFoundError(
                f"Directory {checker_file_path.parent} does not exist."
            )
        if not build_dir.exists():  # build/ 不存在说明 LLVM 未配置
            raise FileNotFoundError(f"Directory {build_dir} does not exist.")
        log_dir.mkdir(parents=True, exist_ok=True)  # 递归建日志目录

        checker_file_path.write_text(checker_code)  # 覆盖写入：用 LLM 生成的实现替换骨架 cpp
        # Build the checker using the provided build command
        try:
            process = sp.run(
                ["make", f"-j{jobs}", f"{checker_name}Plugin"],  # make -jN <Name>Plugin：CMake target 名约定
                cwd=build_dir,  # 在 LLVM build 目录下执行
                capture_output=True,  # 捕获 stdout/stderr 供日志
                timeout=timeout,  # 编译超时保护
            )
            (log_dir / f"build_steout_{attempt}.log").write_bytes(process.stdout)  # stdout 落盘（注意 "steout" 为原有拼写，消费方按此文件名读取）
            (log_dir / f"build_stderr_{attempt}.log").write_bytes(process.stderr)  # stderr 落盘：repair agent 的修错输入（§3.1.3）
            return process.returncode, process.stderr.decode()  # 返回 (返回码, stderr 文本)
        except Exception as e:  # 子进程启动失败/超时等异常兜底
            logger.error(f"Compilation command failed: {e}")
            # Write error to stderr log if possible
            try:
                (log_dir / f"build_error_{attempt}.log").write_text(  # 异常信息本身也落盘
                    f"Error running subprocess: {e}\n"
                )
            except Exception as log_e:  # 连日志都写不进去（如磁盘满）
                logger.error(f"Failed to write error to log file: {log_e}")
            return -1, f"Error running subprocess: {e}"  # 统一以 -1 返回码上报异常

    # ----------------------------------------------------------------------------
    # build_checker_group（fork 增量：多 checker 共存的成组构建）
    # 论文背景：§3.2 的全库扫描实际是 39 个 valid checker 分组进行的；单 checker
    #   单 plugin 的原始形态无法在一次 scan-build 里同时启用多个 checker。
    # 本方法把 N 个 CheckerData 各自改写出唯一名字、编译成 N 个独立 plugin，
    #   为"一次 -load-plugin 挂多个 .so"的分组扫描准备构建产物。
    # 参数：checker_data_list=CheckerData 列表（含 checker_id 与修复后源码）；
    #   log_dir/attempt/jobs/timeout 语义同 build_checker。
    # 返回：(总返回码, 拼接的错误信息, 成功构建的 checker 名列表)——只要有一个
    #   成功即总码 0，全部失败为 -1（形状上是 build_checker 二元结果的成组扩展）。
    # 现状：仓库内暂无调用方（配套 _generate_command_group 标 FIXME 未完成），
    #   checker_scan.py 目前仍是单 checker 逐对象循环——此为分组扫描基建。
    # ----------------------------------------------------------------------------
    def build_checker_group(
        self,
        checker_data_list: List,
        log_dir: Path,
        attempt=1,
        jobs=8,
        timeout=300,
    ):
        """
        Build multiple checkers simultaneously for group scanning.

        Args:
            checker_data_list: List of CheckerData objects with unique checker names
            log_dir: Directory to store build logs
            attempt: Build attempt number
            jobs: Number of parallel jobs
            timeout: Build timeout in seconds

        Returns:
            Tuple of (return_code, stderr_output, built_checker_names)
        """
        from checker_data import CheckerData  # 函数内局部导入，避免模块级循环依赖

        log_dir.mkdir(parents=True, exist_ok=True)  # 建日志根目录
        built_checker_names = []  # 成功编译的 checker 名列表（供后续组扫描命令引用）
        build_errors = []  # 各 checker 的失败信息汇总

        logger.info(f"Building group of {len(checker_data_list)} checkers...")

        # First, create plugin directories for all unique checker names
        self._create_group_plugin_directories(checker_data_list)  # 先为全组建 plugin 骨架并重跑 cmake（见下）

        # Build each checker individually
        for i, checker_data in enumerate(checker_data_list):  # 逐个串行编译（未并行化）
            if not isinstance(checker_data, CheckerData):  # 类型守卫：跳过脏数据
                logger.error(f"Invalid checker data at index {i}")
                continue

            # Generate unique checker name from checker_id
            checker_name = self._generate_unique_checker_name(checker_data.checker_id)  # "KN-xxx" → 合法 C++ 标识符

            # Replace SAGenTestChecker with the unique name in the code
            modified_code = self._replace_checker_name_in_code(  # 换名后的源码：多 plugin 注册名不冲突的关键
                checker_data.repaired_checker_code, checker_name
            )

            logger.info(
                f"Building checker {checker_name} ({i+1}/{len(checker_data_list)})"
            )

            try:
                return_code, stderr = self.build_checker(  # 复用单 checker 编译；每个 checker 独立日志子目录
                    checker_code=modified_code,
                    log_dir=log_dir / f"checker_{checker_name}",
                    checker_name=checker_name,
                    attempt=attempt,
                    jobs=jobs,
                    timeout=timeout,
                )

                if return_code == 0:  # 编译成功
                    built_checker_names.append(checker_name)  # 记入成功清单
                    logger.info(f"✓ Successfully built checker {checker_name}")
                else:  # 编译失败：不中断循环，继续编其余 checker
                    logger.error(f"✗ Failed to build checker {checker_name}")
                    build_errors.append(f"{checker_name}: {stderr}")

            except Exception as e:  # 单个 checker 异常同样不拖垮全组
                logger.error(f"Error building checker {checker_name}: {e}")
                build_errors.append(f"{checker_name}: {str(e)}")

        # Overall result
        if built_checker_names:  # 至少一个成功 → 总码 0（部分失败信息照常带回）
            logger.info(
                f"Group build completed: {len(built_checker_names)}/{len(checker_data_list)} checkers built successfully"
            )
            return 0, "\n".join(build_errors), built_checker_names
        else:  # 全军覆没 → -1 + 空名单
            logger.error("Group build failed: no checkers built successfully")
            return -1, "\n".join(build_errors), []

    # ----------------------------------------------------------------------------
    # _generate_unique_checker_name：checker_id（形如 "KN-<hash>"，见
    #   checker_data.py 的 checker_id property）→ 30 字符内、字母开头的合法
    #   C++ 标识符。分组共存的关键：plugin 库名/类名/注册名都由它派生，必须唯一。
    # ----------------------------------------------------------------------------
    def _generate_unique_checker_name(self, checker_id: str) -> str:
        """Generate a unique checker name from checker_id."""
        # Remove the KN- prefix and clean up the name
        name = checker_id.replace("KN-", "").replace("-", "_")  # 去 KN- 前缀；连字符转下划线
        # Ensure it's a valid C++ identifier
        name = re.sub(r"[^a-zA-Z0-9_]", "_", name)  # 其余非字母数字下划线字符一律换成 _
        # Ensure it starts with a letter
        if name and not name[0].isalpha():  # C++ 标识符不能以数字开头（此处从严要求字母开头）
            name = f"Checker_{name}"
        # Limit length
        if len(name) > 30:  # 截断到 30 字符，防路径/符号名过长
            name = name[:30]

        return name or "SAGenTest"  # 空名兜底回默认名 SAGenTest

    # ----------------------------------------------------------------------------
    # _replace_checker_name_in_code：把 checker 源码里的默认名整体替换为唯一名。
    # 两处替换缺一不可：
    #   1) 类名 SAGenTestChecker → <Name>Checker——源码中所有引用（类定义、
    #      registry.addChecker 的模板参数等）一并换掉；
    #   2) 注册名字符串 "custom.SAGenTestChecker" → "custom.<Name>Checker"——
    #      checker 的注册全名；多个 plugin 同时 -enable-checker 时靠它区分。
    # ----------------------------------------------------------------------------
    def _replace_checker_name_in_code(self, checker_code: str, new_name: str) -> str:
        """Replace SAGenTestChecker with the new unique name in the checker code."""
        # Replace class name and all references
        modified_code = checker_code.replace("SAGenTestChecker", f"{new_name}Checker")  # 全量字符串替换（类名+所有引用）

        # Also replace the checker registration
        modified_code = modified_code.replace(  # 注册名前缀 custom. 单独再换一次（覆盖 "custom.SAGenTestChecker" 字符串字面量）
            "custom.SAGenTestChecker", f"custom.{new_name}Checker"
        )

        return modified_code

    # ----------------------------------------------------------------------------
    # _create_group_plugin_directories：为组内每个 checker 建 plugin 骨架目录。
    # 流程：① 把 src/llvm_utils/create_plugin.py 拷进 plugins/（复用单 checker
    #   时代的目录生成脚本，cp 做法与 setup_llvm.py 一致）；② 逐 checker 运行
    #   create_plugin.py 生成 <Name>Handling/（CMakeLists + .exports + 骨架
    #   cpp），脚本失败则退回 _create_plugin_directory_manually 手工建；
    #   ③ 最后统一 _regenerate_cmake_build_system 重跑 cmake，让新子目录进入
    #   make 可见范围（否则 make <Name>Plugin 报 No rule to make target）。
    # ----------------------------------------------------------------------------
    def _create_group_plugin_directories(self, checker_data_list: List):
        """Create plugin directories for all checkers in the group."""
        plugin_dir = self.backend_path / "clang/lib/Analysis/plugins"  # LLVM plugin 总目录
        if not plugin_dir.exists():  # 目录都没有说明 LLVM 仓形态不对
            logger.error(f"Plugin directory {plugin_dir} does not exist")
            return

        logger.info(
            f"Creating plugin directories for {len(checker_data_list)} checkers..."
        )

        # Copy create_plugin.py to plugins directory (following setup_llvm.py pattern)
        llvm_utils_script = (  # 源脚本在本仓 src/llvm_utils/ 下
            Path(__file__).parent.parent / "llvm_utils" / "create_plugin.py"
        )
        create_plugin_script = plugin_dir / "create_plugin.py"  # 目标位置（与 plugin 同目录运行）

        if llvm_utils_script.exists():
            logger.info("Copying create_plugin.py to plugins directory...")
            # Use cp command like setup_llvm.py does
            sp.run(["cp", str(llvm_utils_script), str(plugin_dir) + "/"])  # 目标以 / 结尾强制按目录拷入
        else:
            logger.warning(  # 拷不到就只能走手工兜底
                "create_plugin.py not found in llvm_utils, will use manual creation"
            )

        for checker_data in checker_data_list:
            checker_name = self._generate_unique_checker_name(checker_data.checker_id)  # 与 build_checker_group 用同一映射，保证目录名一致

            # Check if plugin directory already exists
            plugin_handling_dir = plugin_dir / f"{checker_name}Handling"  # 该 checker 的子目录路径
            # if plugin_handling_dir.exists():
            #     logger.debug(f"Plugin directory {checker_name}Handling already exists")
            #     continue
            # ↑ 原有"已存在则跳过"的逻辑被整段注释掉：现在每次都重建/覆盖骨架，
            #   保证目录内容与当前 checker 名严格一致（幂等重建策略）。

            if create_plugin_script.exists():
                try:
                    # Use the create_plugin.py script exactly like setup_llvm.py does
                    logger.info(f"Creating plugin directory for {checker_name}")
                    result = sp.run(
                        ["python3", "create_plugin.py", checker_name],  # 在 plugins/ 目录下运行目录生成脚本
                        cwd=plugin_dir.absolute(),  # Use absolute path like setup_llvm.py
                        capture_output=True,
                        text=True,
                        timeout=30,  # 单个目录生成 30s 足够
                    )

                    if result.returncode == 0:  # 脚本成功 → 下一个 checker
                        logger.debug(
                            f"✓ Successfully created plugin directory for {checker_name}"
                        )
                        continue
                    else:  # 脚本失败 → 不 continue，落到下面的手工兜底
                        logger.warning(
                            f"create_plugin.py failed for {checker_name}: {result.stderr}"
                        )

                except Exception as e:  # 脚本自身崩溃（如超时）同样落兜底
                    logger.warning(
                        f"create_plugin.py script failed for {checker_name}: {e}"
                    )

            # Fallback to manual creation
            logger.info(f"Using manual creation for {checker_name}")
            self._create_plugin_directory_manually(checker_name, plugin_dir)  # 手工写三件套

        logger.info("Plugin directory creation completed")

        # Regenerate CMake configuration to recognize new plugins
        self._regenerate_cmake_build_system()  # 新子目录只有 cmake 重建后才可 make（关键收尾）

    # ----------------------------------------------------------------------------
    # _create_plugin_directory_manually：create_plugin.py 失败时的手工兜底，
    #   按该脚本的同款格式生成 plugin 目录四件套：
    #   ① CMakeLists.txt——add_llvm_library(<Name>Plugin MODULE BUILDTREE_ONLY)：
    #     MODULE=可动态加载的 .so；BUILDTREE_ONLY=只在本构建树内可用；并链接
    #     clangAnalysis/clangAST/clangStaticAnalyzerCore/Frontend 四个库
    #     （CSA checker 头文件与符号的来源）；
    #   ② <Name>Checker.exports——只导出 clang_registerCheckers（注册入口）与
    #     clang_analyzerAPIVersionString（API 版本握手串）两个 C 符号，clang
    #     -load plugin 后靠它们识别插件；
    #   ③ 骨架 <Name>Checker.cpp——匿名 namespace 里的 Checker<check::PreCall>
    #     空回调占位（马上会被 build_checker 写入的 LLM 实现覆盖）；
    #   ④ 把 add_subdirectory(<Name>Handling) 插进 plugins/CMakeLists.txt 的
    #     最后一个 endif() 之前，使子目录纳入构建树。
    # 注意：①③ 的内容是 f-string，正文里的 {{ }} 是转义后的字面大括号。
    # ----------------------------------------------------------------------------
    def _create_plugin_directory_manually(self, checker_name: str, plugin_dir: Path):
        """Manually create plugin directory structure if create_plugin.py fails."""
        try:
            plugin_handling_dir = plugin_dir / f"{checker_name}Handling"  # 子目录
            plugin_handling_dir.mkdir(exist_ok=True)  # 已存在不报错（幂等）

            # Create CMakeLists.txt matching create_plugin.py format
            lib_name = f"{checker_name}Plugin"  # CMake target 名 / .so 名（<Name>Plugin.so）
            cpp_file_name = f"{checker_name}Checker.cpp"  # 源文件名
            exports_file_name = f"{checker_name}Checker.exports"  # 导出符号清单文件名

            # ↓ ① CMakeLists.txt 的完整内容（f-string，{{}} 为字面大括号）
            cmake_content = f"""
set(LLVM_LINK_COMPONENTS
  Support
  )

set(LLVM_EXPORTED_SYMBOL_FILE ${{CMAKE_CURRENT_SOURCE_DIR}}/{exports_file_name})
add_llvm_library({lib_name} MODULE BUILDTREE_ONLY {cpp_file_name})

clang_target_link_libraries({lib_name} PRIVATE
  clangAnalysis
  clangAST
  clangStaticAnalyzerCore
  clangStaticAnalyzerFrontend
  )
"""
            cmake_file = plugin_handling_dir / "CMakeLists.txt"  # ① 落盘
            cmake_file.write_text(cmake_content.strip())  # strip() 去掉 f-string 首尾空行

            # Create .exports file matching create_plugin.py format
            # ↓ ② 导出符号清单：两个 C 符号（注册入口 + API 版本串），一行一个
            exports_content = """clang_registerCheckers
clang_analyzerAPIVersionString"""
            exports_file = plugin_handling_dir / exports_file_name
            exports_file.write_text(exports_content)  # ② 落盘

            # Create minimal checker .cpp file
            checker_class_name = f"{checker_name}Checker"  # 骨架类名 <Name>Checker
            # ↓ ③ 骨架源码：结构 = 匿名 namespace 内的 Checker<check::PreCall>
            #   子类（空 checkPreCall 声明）+ extern "C" 的 clang_registerCheckers
            #   注册 "custom.<Name>Checker" + API 版本串，与 §3.1.3 checker 模板
            #   同构，仅回调为空占位（正文字面 {} 由 f-string 转义为 {{ }}）。
            cpp_content = f"""#include "clang/StaticAnalyzer/Core/BugReporter/BugType.h"
#include "clang/StaticAnalyzer/Core/Checker.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/CheckerContext.h"
#include "clang/StaticAnalyzer/Frontend/CheckerRegistry.h"

using namespace clang;
using namespace ento;

namespace {{
/*The checker callbacks are to be decided.*/
class {checker_class_name} : public Checker<check::PreCall> {{
  mutable std::unique_ptr<BugType> BT;

public:
  // Main Check Logic
  void checkPreCall(const CallEvent &Call, CheckerContext &C) const; // Tmp
}};
}} // end anonymous namespace


extern "C" void clang_registerCheckers(CheckerRegistry &registry) {{
  registry.addChecker<{checker_class_name}>(
      "custom.{checker_class_name}",
      "/*Description to be filled*/",
      "");
}}

extern "C" const char clang_analyzerAPIVersionString[] =
    CLANG_ANALYZER_API_VERSION_STRING;"""
            cpp_file = plugin_handling_dir / cpp_file_name
            cpp_file.write_text(cpp_content)  # ③ 落盘（随后被真实实现覆盖）

            # Update main CMakeLists.txt to include this plugin
            main_cmake = plugin_dir / "CMakeLists.txt"  # plugins/ 总 CMakeLists
            if main_cmake.exists():
                main_content = main_cmake.read_text()
                add_line = f"add_subdirectory({checker_name}Handling)"  # ④ 要追加的子目录声明

                if add_line not in main_content:  # 幂等：已存在则不再追加
                    # Add before the last endif()
                    lines = main_content.split("\n")
                    for i in range(len(lines) - 1, -1, -1):  # 从文件尾倒序扫描
                        if "endif()" in lines[i]:  # 找最后一个 endif()
                            lines.insert(i, f"  {add_line}")  # 插在其前（缩进两空格）
                            break

                    main_cmake.write_text("\n".join(lines))
                    logger.info(f"✓ Updated main CMakeLists.txt for {checker_name}")

            logger.info(f"✓ Manually created plugin directory for {checker_name}")

        except Exception as e:  # 任一子步骤失败仅记日志，不让上层组构建中断
            logger.error(
                f"✗ Failed to manually create plugin directory for {checker_name}: {e}"
            )

    # ----------------------------------------------------------------------------
    # _regenerate_cmake_build_system：重跑 cmake 重新生成 Unix Makefiles。
    # 为什么必须：手工往 plugins/CMakeLists.txt 加了 add_subdirectory，但
    #   build/ 下的 Makefile 是 cmake 的生成物——不重新 cmake，make
    #   <Name>Plugin 找不到规则。命令行参数与 setup_llvm.py 首配完全同款
    #   （clang;lld / 仅 X86 / Release / Unix Makefiles），保证增量重建不漂移。
    # 返回：True/False 表示重建是否成功。
    # ----------------------------------------------------------------------------
    def _regenerate_cmake_build_system(self):
        """Regenerate CMake build system to recognize new plugins."""
        try:
            build_dir = self.backend_path / "build"  # LLVM 构建目录
            if not build_dir.exists():
                logger.error(f"Build directory {build_dir} does not exist")
                return False

            logger.info("Regenerating CMake build system for new plugins...")

            # Run cmake to regenerate build files (following setup_llvm.py pattern)
            cmake_cmd = 'cmake -DLLVM_ENABLE_PROJECTS="clang;lld" -DLLVM_TARGETS_TO_BUILD=X86 -DCMAKE_BUILD_TYPE=Release -G "Unix Makefiles" ../llvm'  # 与首配同款的 cmake 命令串

            result = sp.run(
                cmake_cmd,
                shell=True,  # 命令串整体交 shell 执行
                cwd=build_dir,  # 在 build/ 内运行（源在 ../llvm）
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:  # Makefile 已含新 plugin 目标
                logger.info("✓ CMake regeneration completed successfully")
                return True
            else:
                logger.error(f"✗ CMake regeneration failed: {result.stderr}")
                return False

        except Exception as e:  # cmake 进程级异常（超时等）
            logger.error(f"✗ Failed to regenerate CMake build system: {e}")
            return False

    # ----------------------------------------------------------------------------
    # validate_checker（论文 §3.1.4 Validation 入口，抽象接口的实现）
    # 职责：按目标类型分发——linux → _validate_checker_linux（对象级差分），
    #   v8 → _validate_checker_v8（源文件级差分，fork 增量）；其他类型抛
    #   NotImplementedError。
    # 参数：checker_code=待验证 checker 源码；commit_id=bug-fix patch 的提交号
    #   （buggy 版 = commit^，patched 版 = commit）；patch=diff 文本（圈定要
    #   分析的对象/文件范围）；target=目标对象（提供 checkout 与对象映射）；
    #   skip_build_checker=调用方刚编译过则跳过（checker_gen 在 repair 后立即
    #   验证，传 True 省一次重复编译）。
    # 返回：(TP, TN)。上层判 valid 的依据是 TP>0 且 TN>0（checker_gen.py 的
    #   is_perfect），对应论文口径 valid ⟺ N_buggy > N_patched 且
    #   N_patched < T_valid(=50)——代码实现更严，见 linux 版注释。
    # 哨兵：(-1,-1)=任一对象编译失败；(-2,-2)=扫描器自身崩溃（linux 版）。
    # ----------------------------------------------------------------------------
    def validate_checker(
        self,
        checker_code,
        commit_id,
        patch,
        target: TargetFactory,
        skip_build_checker=False,
    ) -> Tuple[int, int]:

        if target._target_type == "linux":  # Linux 内核目标
            return self._validate_checker_linux(
                checker_code, commit_id, patch, target, skip_build_checker
            )
        elif target._target_type == "v8":  # V8 目标（fork 增量）
            return self._validate_checker_v8(
                checker_code, commit_id, patch, target, skip_build_checker
            )
        else:  # 其余目标类型尚未支持
            raise NotImplementedError(
                f"Validation for target type {target._target_type} is not implemented."
            )

    # ----------------------------------------------------------------------------
    # run_checker（论文 §3.2 的执行入口：全库扫描与对象级扫描共用，抽象接口实现）
    # 职责：按目标类型分发到 _run_checker_linux / _run_checker_v8，参数原样透传。
    # 三个调用场景：checker_refine.py refine 后重扫内核（timeout/输出目录由调用
    #   方传入——论文"refine 期间限 1 小时或 100 warnings"护栏即在此层落地）；
    #   checker_refine.py 逐对象细扫（skip_checkout 复用已配置树）；checker_scan.py
    #   正式找 bug（arch/timeout 透传）。
    # 返回：bug 数；哨兵 -999=构建失败 / -1=超时 / -10=报警过多（见 linux 实现）。
    # ----------------------------------------------------------------------------
    def run_checker(
        self,
        checker_code,
        commit_id,
        target,
        object_to_analyze=None,
        jobs=32,
        output_dir="tmp",
        skip_build_checker=False,
        skip_checkout=False,
        **kwargs,
    ) -> int:
        """
        Run the checker against a commit and patch.
        This will dispatch the analysis to the appropriate method based on the target type.

        Args:
            commit_id (str): The commit ID to run the checker against.
            object_to_analyze (str): The object file to analyze.
            target (TargetFactory): The target to be tested.
            jobs (int): Number of jobs to run in parallel.
            output_dir (str): Directory to save the output.

        Returns:
            int: Number of bugs found.
        """

        if target._target_type == "linux":  # Linux 内核目标
            return self._run_checker_linux(
                checker_code,
                commit_id,
                target,
                object_to_analyze=object_to_analyze,  # 给定则对象级增量编译，否则整树（全库扫描）
                jobs=jobs,
                output_dir=output_dir,
                skip_build_checker=skip_build_checker,  # True=复用已编好的 plugin
                skip_checkout=skip_checkout,  # True=不切 commit（逐对象循环续扫用）
                **kwargs,
            )
        elif target._target_type == "v8":  # V8 目标（fork 增量）
            return self._run_checker_v8(
                checker_code,
                commit_id,
                target,
                object_to_analyze=object_to_analyze,
                jobs=jobs,
                output_dir=output_dir,
                skip_build_checker=skip_build_checker,
                skip_checkout=skip_checkout,
                **kwargs,
            )
        else:  # 其余目标类型尚未支持
            raise NotImplementedError(
                f"Running checker for target type {target._target_type} is not implemented."
            )

    # ↓ 以下是本类的自有辅助函数（V8 支持等 fork 增量），不属于抽象接口
    """Self defined functions"""

    # ----------------------------------------------------------------------------
    # _validate_checker_linux（论文 §3.1.4 Validation 的 Linux 实现——差分验证核心）
    # 流程（对照论文）：
    #   ① 可选编译 checker 为 plugin（skip_build_checker=False 时）；
    #   ② checkout 到 buggy 提交（commit^，is_before=True）+ allyesconfig +
    #      olddefconfig，对 patch 涉及的每个 .o 对象跑 `make LLVM=1 ARCH=x86
    #      <obj> -j8`——scan-build 包裹的 clang 编译该 TU 时运行 CSA → N_buggy；
    #   ③ checkout 到 patched 提交（is_before=False）同样再扫 → N_patched；
    #   ④ 差分计分：buggy 版报出 bug → TP+=1（N_buggy>0）；patched 版无报警、
    #      或报警数比 buggy 版少且绝对值 <5 → TN+=1；patched 反而更多 → TN-=1。
    # 哨兵返回：(-1,-1)=任一对象编译失败（对应论文 implementation 无效路径）；
    #   (-2,-2)=scan-build 自身崩溃（输出含 clang crash 特征串）。
    # 与论文口径的差异：论文写 N_patched < T_valid(=50)，代码用更严的
    #   "每对象 N_patched<5 且逐对象对比"，valid 判据为 TP>0 且 TN>0。
    # ----------------------------------------------------------------------------
    def _validate_checker_linux(
        self,
        checker_code: str,
        commit_id: str,
        patch: str,
        target: Linux,
        skip_build_checker=False,
    ):
        """
        Validate the checker against a commit and patch.
        We use x86 architecture for Linux by default.

        Args:
            commit_id (str): The commit ID to validate against.
            patch (str): The patch to apply.
            target (str): The target file or directory.
        """

        TP, TN = 0, 0  # 差分计分初值：真阳（buggy 报警）/ 真阴（patched 干净）
        if not skip_build_checker:  # 调用方没编过就现场编（checker_gen 路径会传 True 跳过）
            self.build_checker(
                checker_code,
                Path("tmp"),
                attempt=1,
            )

        comd_prefix = self._generate_command()  # scan-build 命令前缀（含 -load-plugin、六连 -disable-checker、-maxloop、-o）
        olddefcmd = comd_prefix + "make LLVM=1 ARCH=x86 olddefconfig"  # checkout 后跑 olddefconfig：allyesconfig 生成 .config 后把新增符号补默认值（防构建交互提问）
        target.checkout_commit(commit_id, is_before=True, olddefcmd=olddefcmd)  # 切到 buggy 版：make clean + checkout commit^ + allyesconfig + olddefconfig

        # Get the modified objects from the patch
        num_bug_obj = {}  # {对象: N_buggy}，patched 轮做逐对象对比
        objects = target.get_objects_from_patch(patch)  # patch 涉及的 .c → .o（targets/linux.py 的映射规则）——§3.1.4 只扫 patch 涉及对象
        for obj in objects:  # —— buggy 轮 ——
            comd = comd_prefix + f"make LLVM=1 ARCH=x86 {obj} -j8"  # 对象级增量编译：scan-build 包裹的 clang 只分析该 TU
            logger.info("Running: " + comd)
            try:
                res = sp.run(
                    comd,
                    shell=True,
                    text=True,
                    cwd=target.repo.working_dir,  # 在内核树里执行
                    capture_output=True,
                    timeout=300,  # 单对象 5 分钟超时
                )
                output = res.stdout
            except sp.TimeoutExpired:
                raise Exception(f"Compilation Timeout: {comd}")  # 超时直接抛（不属编译失败哨兵路径）

            logger.info(f"Buggy: {obj} {res.returncode}")
            if (
                res.returncode == 0
                and "Please consider submitting a bug report" in output  # clang 内部崩溃的特征串 → 扫描器自身出错
            ):
                logger.info("Buggy: Error in scan!")
                logger.debug(output)
                return -2, -2  # 哨兵 (-2,-2)：scan-build 崩溃（区别于编译失败 -1）
            elif res.returncode == 0 and "No bugs found" not in output:  # 正常结束且有报警（scan-build 零报警时输出含 "No bugs found"）
                # scan-build: 0 bugs found.
                num_bugs = self.get_num_bugs(output)  # 解析 "N bug(s) found." 统计行（方法在本文件后半）
                num_bug_obj[obj] = num_bugs  # 记录该对象的 N_buggy
                TP += 1  # buggy 版报出 → 真阳 +1
                logger.info(f"Buggy: {num_bugs} bugs found")
            elif res.returncode == 0:  # 正常结束但零报警（buggy 漏报方向，TP 不加）
                logger.info("Buggy: No bugs found!")
            elif res.returncode != 0:  # 对象编译失败 → checker 挡了构建（如语法错/链接错）
                logger.info("Buggy: Error in build!")
                return -1, -1  # 哨兵 (-1,-1)：编译失败

        olddefcmd = comd_prefix + "make LLVM=1 ARCH=x86 olddefconfig"  # 第二次构造（与 519 行同串）：patched checkout 同样需要 olddefconfig
        target.checkout_commit(commit_id, is_before=False, olddefcmd=olddefcmd)  # 切到 patched 版（commit 本身）
        for obj in objects:  # —— patched 轮 ——
            comd = comd_prefix + f"make LLVM=1 ARCH=x86 {obj} -j8 2>&1"  # 注意结尾 2>&1：把 make 的 stderr 并入 stdout 统一交给解析（buggy 轮没有，属两轮命令的小差异）
            try:
                res = sp.run(
                    comd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=target.repo.working_dir,
                    timeout=300,
                )
                output = res.stdout
            except sp.TimeoutExpired:
                raise Exception(f"Compilation Timeout: {comd}")

            logger.info(f"Non-buggy: {obj} {res.returncode}")

            if res.returncode == 0 and "No bugs found" in output:  # patched 零报警 → 最干净的真阴
                TN += 1
                logger.info("Non-buggy: No bugs found!")
            elif res.returncode == 0:  # patched 仍有报警 → 看是否比 buggy 版收敛
                num_bugs = self.get_num_bugs(output)
                if num_bugs < num_bug_obj.get(obj, 0) and num_bugs < 5:  # 报警数比 buggy 少且绝对值 <5（代码版 T_valid=5，严于论文的 50）→ 认可
                    TN += 1
                elif num_bugs > num_bug_obj.get(obj, 0):  # patched 反而更多报警（差分判负）→ 惩罚性扣分
                    TN -= 1
                logger.info(f"Non-buggy: {num_bugs} bugs found")
            elif res.returncode != 0:  # patched 版编译失败同样是无效 checker
                logger.info("Non-buggy: Error in build!")
                return -1, -1
        return TP, TN  # 上层 checker_gen 以 TP>0 且 TN>0 判 valid

    # ----------------------------------------------------------------------------
    # _run_checker_linux（论文 §3.2 的 Linux 扫描实现：全库或对象级）
    # 职责：checkout 目标提交后，用 scan-build 包裹的 `make LLVM=1` 触发 CSA。
    # 与差分验证（两次扫描比计数）不同：这里只扫一次，产出报告目录与 bug 总数，
    # 报告随后由本文件后半 extract_reports 蒸馏并交 triage agent。
    # 关键参数：arch 默认 x86，arm64/riscv 自动追加 CROSS_COMPILE 交叉前缀；
    #   timeout 默认 1800s；object_to_analyze 给定则只编该对象（增量），否则
    #   整树构建（全库扫描）；skip_build_checker / skip_checkout 供逐对象循环
    #   复用前序状态（checker_scan.py：首个对象做 checkout，其余 skip）。
    # 输出监控：monitor_build_output 实时数 warning，超 300 条或超时即杀进程——
    #   论文 §3.2 "refine 期间限 1 小时或 100 warnings" 护栏思想的落地参数
    #   （正式找 bug 时由调用方放开 timeout）。
    # 返回哨兵：-999=make 构建失败（scan_error.log 已落盘）/ -1=超时 /
    #   -10=报警过多被截停；正常返回 bug 数（0 也正常）。
    # ----------------------------------------------------------------------------
    def _run_checker_linux(
        self,
        checker_code: str,
        commit_id: str,
        target: Linux,
        object_to_analyze: str = None,
        jobs: int = 32,
        output_dir: str = "tmp",
        skip_build_checker: bool = False,
        skip_checkout: bool = False,
        **kwargs,  # 额外参数：arch（默认 x86）/ timeout（默认 1800）从这取
    ):
        """
        Run the checker against a commit and patch.

        Args:
            commit_id (str): The commit ID to run the checker against.
            object_to_analyze (str): The object file to analyze.
            target (Linux): The target to be tested.
            object_to_analyze (str): The object file to analyze.
            jobs (int): Number of jobs to run in parallel.
            output_dir (str): Directory to save the output.

        Returns:
            int: Number of bugs found.
        """

        output_dir = Path(output_dir)  # 统一转 Path
        arch = kwargs.get("arch", "x86")  # 目标架构（checker_scan 可传 arm64/riscv）
        timeout = kwargs.get("timeout", 1800)  # 扫描总超时（refine 与正式找 bug 由调用方区分）

        if not skip_build_checker:  # 需要时先编译 plugin
            build_res, _ = self.build_checker(checker_code, Path("tmp"), attempt=1)
            if build_res != 0:  # 编译都过不了，直接异常（不走 -999 哨兵）
                logger.error("Build failed, skipping analysis.")
                raise Exception("Build failed, skipping analysis.")

        comd_prefix = self._generate_command(no_output=True)  # scan-build 前缀，去掉默认 -o
        comd_prefix += "-o " + output_dir.absolute().as_posix()  # 换成调用方指定的绝对报告目录（HTML 报告落这里供 extract_reports/triage）

        # Note: kernel cleaning is handled by target.checkout_commit() which runs 'make clean'
        olddefcmd = comd_prefix + f" make LLVM=1 ARCH={arch} olddefconfig"  # checkout 后补 .config 默认值（前缀带 -o 无害）
        if not skip_checkout:  # 逐对象续扫时可跳过（树已 clean+checkout+config）
            target.checkout_commit(commit_id, olddefcmd=olddefcmd)  # make clean + checkout + allyesconfig + olddefconfig

        # Process the command based on the architecture
        if arch == "arm64":  # ARM64：需要交叉编译前缀
            comd = (
                comd_prefix
                + f" make LLVM=1 ARCH={arch} CROSS_COMPILE=aarch64-linux-gnu- -j{jobs}"
            )
        elif arch == "riscv":  # RISC-V：同理
            comd = (
                comd_prefix
                + f" make LLVM=1 ARCH={arch} CROSS_COMPILE=riscv64-unknown-linux-gnu- -j{jobs}"
            )
        else:  # 默认 x86：本机 clang 直接编
            comd = comd_prefix + f" make LLVM=1 ARCH={arch} -j{jobs}"

        # Object to analyze
        if object_to_analyze:  # 给了对象 → 只编该目标（增量分析）；否则整树=全库扫描
            comd += f" {object_to_analyze}"
        logger.info("Running: " + comd)

        scan_process = sp.Popen(  # 用 Popen 而非 run：monitor_build_output 需要流式逐行读
            comd,
            shell=True,  # comd 是整条 shell 命令串
            cwd=target.repo.working_dir,  # 在内核树里执行
            stdout=sp.PIPE,
            stderr=sp.PIPE,
        )
        output, completed = monitor_build_output(  # 实时监控：warning 超限或超时杀进程（refine 护栏）
            scan_process, warning_limit=300, timeout=timeout
        )

        num_bugs = 0
        if completed == "Complete":  # 正常跑完
            return_code = scan_process.wait()  # 收割退出码
            if return_code != 0:  # make 构建失败（与扫描无报警是两回事）
                logger.error("Fail to build the kernel with checker!")
                logger.error("Return code: " + str(return_code))
                (output_dir / "scan_error.log").write_text(output)  # 失败输出落盘排查
                return -999  # 哨兵：构建失败
            if "No bugs found" not in output:  # 有报警 → 解析计数（零报警走默认 0）
                num_bugs = self.get_num_bugs(output)
                logger.success(f"{num_bugs} bugs found!")
        elif completed == "Timeout":  # 超时被杀
            num_bugs = -1  # 哨兵：超时
            logger.warning("Timeout!")
        else:  # warning 数超限被截停（"Too many bugs" 路径）
            num_bugs = -10  # 哨兵：报警过多
            logger.warning("Too many bugs found!")

        return num_bugs

    # ----------------------------------------------------------------------------
    # _get_compile_entries_for_v8_sources（V8 侧工具，fork 增量）
    # 职责：从 V8 构建产物 compile_commands.json 里取出指定源文件的编译条目
    #   （含完整编译命令与 flags），供后续 clang++ --analyze 精确复刻编译环境。
    # 路径约定：json 里 "file" 字段是相对 out/x64.release 构建目录的
    #   "../../<source_file>"，故查询键统一加 ../../ 前缀。
    # 返回：{源文件: 编译条目 dict}；json 缺失/解析异常返回空 dict（调用方
    #   逐文件跳过）。
    # ----------------------------------------------------------------------------
    def _get_compile_entries_for_v8_sources(
        self, compile_commands_path: Path, source_files: List[str]
    ) -> dict:
        """
        Extract compile entries for specific source files from compile_commands.json.

        Args:
            compile_commands_path: Path to compile_commands.json
            source_files: List of source files to find entries for

        Returns:
            dict: Mapping of source file to compile command entry
        """
        compile_entries = {}  # 结果容器：{source_file: cmd entry}

        if not compile_commands_path.exists():  # json 不存在 → 空结果（上层按无编译命令处理）
            logger.error(f"compile_commands.json not found at {compile_commands_path}")
            return compile_entries

        try:
            with open(compile_commands_path, "r") as f:
                commands = json.load(f)  # 读入全部编译条目

            # Find compile entries for each source file
            for source_file in source_files:  # 逐个 patch 涉及文件查条目
                normalized_source = f"../../{source_file}"  # 路径归一化：加构建目录相对前缀
                for cmd in commands:
                    if cmd.get("file") == normalized_source:  # 精确匹配文件字段
                        compile_entries[source_file] = cmd  # 命中即存（取第一条）
                        break

        except Exception as e:  # json 解析失败等 → 返回已收集的部分
            logger.error(f"Failed to read compile_commands.json: {e}")

        return compile_entries

    # ----------------------------------------------------------------------------
    # _validate_checker_v8（论文 §3.1.4 Validation 的 V8 实现，fork 增量）
    # 与 Linux 版同构的差分验证，差异点：
    #   - V8 无 make 对象映射 → 以 patch 涉及的源文件为分析单位；
    #   - 用 compile_commands.json + ninja 编对象，再用 clang++ --analyze 复用
    #     原编译 flags 重跑单 TU（V8 构建系统无法被 scan-build 整体包裹）；
    #   - TN 判据不同：patched 版零报警或报警数少于 buggy 版即 TN+=1
    #     （没有 Linux 版的 "<5" 绝对阈值，也没有 TN-=1 惩罚）。
    # 开局先从 PATH 移除 depot_tools：防后续步骤触发 gclient sync 悄悄改依赖
    #   版本，破坏两次扫描的可比性（fork 踩坑记录）。
    # ----------------------------------------------------------------------------
    def _validate_checker_v8(
        self,
        checker_code: str,
        commit_id: str,
        patch: str,
        target,
        skip_build_checker=False,
    ):
        """
        Validate the checker against a V8 commit and patch.
        Analyzes files in both buggy and fixed versions to compute TP/TN.
        """
        # Remove depot_tools from PATH to prevent gclient sync from changing V8 dependencies
        original_path = os.environ.get("PATH", "")  # 备份原 PATH（注意：本函数并不恢复它）
        filtered_path = ":".join(  # 逐段过滤含 "depot_tools" 的路径项
            [p for p in original_path.split(":") if "depot_tools" not in p]
        )
        os.environ["PATH"] = filtered_path  # 生效：后续子进程都用净化后的 PATH

        logger.info(f"V8 validation: removed depot_tools from PATH")

        TP, TN = 0, 0  # 差分计分初值
        if not skip_build_checker:  # 可选编译（与 Linux 版一致）
            self.build_checker(
                checker_code,
                Path("tmp"),
                attempt=1,
            )

        # Get source files from patch
        source_files = target.get_source_files_from_patch(patch)  # patch 涉及源文件清单（V8 的分析单位）
        logger.info(f"Source files to analyze from patch: {source_files}")

        # [DEBUG] Clear any existing debug log and create new one
        debug_log = "/tmp/v8_checker_debug.log"  # 调试桩：全流程写 /tmp 便于事后排查
        if os.path.exists(debug_log):
            os.remove(debug_log)  # 每次验证重开日志

        # Write initial debug info
        with open(debug_log, "w") as f:  # 头部信息
            f.write(f"=== V8 Checker Validation Started ===\n")
            f.write(f"Commit ID: {commit_id}\n")
            f.write(f"Source files: {source_files}\n")
            f.write(f"Skip build: {skip_build_checker}\n")
            f.write("=" * 50 + "\n")

        num_bug_files = {}  # {源文件: N_buggy}，fixed 轮对比用

        # Create output directories for validation (consistent with Linux structure)
        # Use tmp directory for validation with timestamped subdirectories
        validation_base_dir = Path("tmp") / "v8_validation" / commit_id  # 本 commit 的验证根目录

        # Create timestamped directories for both buggy and fixed versions
        buggy_base_dir = validation_base_dir / "buggy"  # buggy 版报告基目录
        fixed_base_dir = validation_base_dir / "fixed"  # fixed 版报告基目录
        buggy_base_dir.mkdir(parents=True, exist_ok=True)
        fixed_base_dir.mkdir(parents=True, exist_ok=True)

        buggy_output_dir = self._create_timestamped_output_dir(buggy_base_dir)  # 时间戳子目录防多次运行互相覆盖（方法在本文件后半）
        fixed_output_dir = self._create_timestamped_output_dir(fixed_base_dir)

        # Checkout buggy version
        llvm_build_dir = self.backend_path / "build"  # 自编 LLVM 的 build 目录（bin/ 与 lib/ 都在这）
        target.checkout_commit(  # 切到 buggy 版（V8 版 checkout：fetch + checkout commit^）
            commit_id,
            is_before=True,
            arch="x64",
            build_config="release",
            llvm_path=llvm_build_dir,  # 把自编 LLVM 传给目标侧配置
        )

        # Build the specific object files first
        env = os.environ.copy()  # 子进程环境副本
        env["PATH"] = f"{llvm_build_dir}/bin:" + env.get("PATH", "")  # 自编 clang/ninja 优先于系统工具链

        # Get compile_commands.json to find exact entries for source files
        compile_commands_path = (  # V8 GN/Ninja 构建产物的编译数据库
            Path(target.repo.working_dir) / "out/x64.release/compile_commands.json"
        )

        # Use helper function to get compile entries
        compile_entries = self._get_compile_entries_for_v8_sources(  # 查出各源文件的编译条目
            compile_commands_path, source_files
        )

        # Build and analyze buggy version
        for source_file in source_files:  # —— buggy 轮：逐文件 ——
            if source_file not in compile_entries:  # 没有编译命令就没法复刻环境，跳过
                logger.warning(f"No compile command found for {source_file}")
                continue

            # Build the object file for this source
            obj_file = self._get_object_file_from_source(source_file, target)  # 源文件 → ninja 对象目标
            if obj_file:
                logger.info(f"Building object file: {obj_file}")
                build_result = sp.run(  # ninja 只编这一个对象（比整树快得多）
                    ["ninja", "-C", "out/x64.release", obj_file],
                    cwd=target.repo.working_dir,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if build_result.returncode != 0:
                    logger.error(  # 对象编不过 → 该文件作废，不判全局失败
                        f"Failed to build {obj_file}: {build_result.stderr[:500]}"
                    )
                    continue

            # Create file-specific output directory (validation always needs output)
            safe_filename = source_file.replace("/", "_").replace(".", "_")  # 路径安全化：/ 和 . 都换 _
            file_output_dir = buggy_output_dir / safe_filename  # 每文件独立报告目录
            file_output_dir.mkdir(parents=True, exist_ok=True)

            # Analyze using helper function
            success, num_bugs, error_msg = self._analyze_v8_source_file(  # 核心：clang++ --analyze 单 TU 分析（方法在本文件后半）
                compile_entries[source_file],
                file_output_dir,
                target=target,
                timeout=900,  # 单文件分析 15 分钟
            )

            if not success:  # 分析失败 → 跳过该文件
                logger.warning(f"Failed to analyze {source_file}: {error_msg}")
                continue

            # Append debug info about the analysis
            with open(debug_log, "a") as f:  # 调试桩追加
                f.write(f"\n=== BUGGY VERSION - {source_file} ===\n")
                f.write(f"Analysis success: {success}\n")
                f.write(f"Number of bugs found: {num_bugs}\n")
                if error_msg:
                    f.write(f"Error: {error_msg}\n")
                f.write(f"Output directory: {file_output_dir}\n")

            num_bug_files[source_file] = num_bugs  # 记录 N_buggy
            if num_bugs > 0:  # buggy 版报出 → TP
                TP += 1
                logger.info(f"Buggy: {num_bugs} bugs found for file {source_file}")
            else:
                logger.info(f"Buggy: No bugs found for file {source_file}")

        # Checkout fixed version
        target.checkout_commit(  # 切到 patched 版（commit 本身）
            commit_id,
            is_before=False,
            arch="x64",
            build_config="release",
            llvm_path=llvm_build_dir,
        )

        # Re-read compile_commands.json for fixed version (may have changed after checkout)
        compile_entries = self._get_compile_entries_for_v8_sources(  # checkout 后 flags 可能变化，必须重读（坑）
            compile_commands_path, source_files
        )

        # Build and analyze fixed version
        for source_file in source_files:  # —— fixed 轮：与 buggy 轮逐行对称 ——
            if source_file not in compile_entries:
                logger.warning(f"No compile command found for {source_file}")
                continue

            # Build the object file for this source
            obj_file = self._get_object_file_from_source(source_file, target)
            if obj_file:
                logger.info(f"Building object file: {obj_file}")
                build_result = sp.run(
                    ["ninja", "-C", "out/x64.release", obj_file],
                    cwd=target.repo.working_dir,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if build_result.returncode != 0:
                    logger.error(
                        f"Failed to build {obj_file}: {build_result.stderr[:500]}"
                    )
                    continue

            # Create file-specific output directory (validation always needs output)
            safe_filename = source_file.replace("/", "_").replace(".", "_")  # 同款路径安全化
            file_output_dir = fixed_output_dir / safe_filename  # 注意落在 fixed 目录树
            file_output_dir.mkdir(parents=True, exist_ok=True)

            # Analyze using helper function
            success, num_bugs, error_msg = self._analyze_v8_source_file(
                compile_entries[source_file],
                file_output_dir,
                target=target,
                timeout=900,
            )

            if not success:
                logger.warning(f"Failed to analyze fixed {source_file}: {error_msg}")
                continue

            logger.info(f"Fixed: {source_file} analysis complete")

            # Append debug info about the analysis
            with open(debug_log, "a") as f:
                f.write(f"\n=== FIXED VERSION - {source_file} ===\n")
                f.write(f"Analysis success: {success}\n")
                f.write(f"Number of bugs found: {num_bugs}\n")
                if error_msg:
                    f.write(f"Error: {error_msg}\n")
                f.write(f"Output directory: {file_output_dir}\n")

            if num_bugs == 0 or num_bugs < num_bug_files.get(source_file, 0):  # V8 版 TN 判据：零报警或比 buggy 版少（无绝对阈值、无扣分）
                TN += 1
                logger.info(
                    f"Fixed: Fewer bugs ({num_bugs}) found for file {source_file}"
                )
            else:
                logger.info(
                    f"Fixed: Same/more bugs ({num_bugs}) found for file {source_file}"
                )

        logger.info(f"V8 Validation Result: TP={TP}, TN={TN}")

        # Create softlinks for both buggy and fixed directories
        self._create_v8_report_softlinks(buggy_output_dir, buggy_base_dir)  # 建最新报告软链（方法在本文件后半）
        self._create_v8_report_softlinks(fixed_output_dir, fixed_base_dir)

        # Write final summary to debug log
        with open(debug_log, "a") as f:  # 汇总段：期望 TP=1 且 TN=1（V8 验证以单文件 patch 为主要场景）
            f.write("\n" + "=" * 50 + "\n")
            f.write("=== VALIDATION SUMMARY ===\n")
            f.write(f"True Positives (TP): {TP}\n")
            f.write(f"True Negatives (TN): {TN}\n")
            f.write(f"Bug counts per file:\n")
            for src, count in num_bug_files.items():  # 各文件 N_buggy 明细
                f.write(f"  {src}: {count} bugs\n")
            f.write(f"Expected: TP=1, TN=1\n")
            f.write(f"Success: {TP == 1 and TN == 1}\n")
            f.write("=" * 50 + "\n")

        return TP, TN

    # ----------------------------------------------------------------------------
    # _get_object_file_from_source（V8 侧工具）
    # 职责：V8 源文件 → ninja 对象目标路径。
    # 首选：从 compile_commands.json 查到该文件的编译命令，shlex 词法切分后
    #   取 "-o" 的下一个参数——这是构建系统真实输出的对象路径，零猜测；
    # 兜底（json 缺失/查不到/解析异常）按 V8 构建惯例猜路径：
    #   test/fuzzer/wasm/* → obj/wasm_fuzzer_common/<stem>.o；
    #   src/*（绝大多数源码）→ obj/v8_base_without_compiler/<stem>.o；
    #   其余 → obj/<stem>.o。
    # ----------------------------------------------------------------------------
    def _get_object_file_from_source(self, source_file, target):
        """Convert source file path to corresponding object file path using compile_commands.json."""
        # Try to find the actual object file from compile_commands.json
        compile_commands_path = (
            Path(target.repo.working_dir) / "out/x64.release/compile_commands.json"
        )
        if compile_commands_path.exists():
            try:
                with open(compile_commands_path) as f:
                    commands = json.load(f)  # 读入编译数据库

                # Normalize the source file path (V8 uses ../../ prefix)
                normalized_source = f"../../{source_file}"  # 同款 ../../ 前缀归一化

                # Find the command for this source file
                for cmd in commands:
                    if cmd.get("file") == normalized_source:
                        # Parse the command to find the -o flag
                        parts = shlex.split(cmd["command"])  # shell 词法切分（能正确处理引号）
                        for i, part in enumerate(parts):
                            if part == "-o" and i + 1 < len(parts):  # 找到 -o 且后面还有参数
                                logger.info(
                                    f"Found object file mapping: {source_file} -> {parts[i+1]}"
                                )
                                return parts[i + 1]  # -o 的实参即对象文件路径

                logger.warning(  # 数据库里没有该文件 → 走下面的惯例猜测
                    f"No compile command found for {source_file}, using fallback"
                )
            except Exception as e:
                logger.warning(  # json 损坏等 → 同样走惯例猜测
                    f"Error reading compile_commands.json: {e}, using fallback"
                )

        # Fallback: Use known V8 build patterns
        source_path = Path(source_file)  # 按 Path 组件判定目录层级

        # Special case for test/fuzzer/wasm files
        if source_path.parts[0] == "test" and len(source_path.parts) >= 4:  # test/<...>/<...>/<file> 深路径
            if source_path.parts[1] == "fuzzer" and source_path.parts[2] == "wasm":  # wasm fuzzer 特例
                filename = source_path.stem  # 去扩展名的文件基名
                return f"obj/wasm_fuzzer_common/{filename}.o"  # 惯例：wasm fuzzer 公共库目录

        # For src/ files, most go to v8_base_without_compiler
        if source_path.parts[0] == "src":  # V8 主源码树
            filename = source_path.stem
            # Runtime, heap, builtins, etc. typically go to v8_base_without_compiler
            return f"obj/v8_base_without_compiler/{filename}.o"  # 惯例：绝大多数 src 文件的目标库

        # Default fallback - just use the stem name
        filename = source_path.stem
        return f"obj/{filename}.o"  # 最后兜底：顶层 obj 目录

    # ----------------------------------------------------------------------------
    # _generate_v8_analyzer_command（V8 分析命令生成，fork 增量的核心技巧）
    # 返回值是"函数（闭包）"而非命令字符串——查到编译命令时 cmd 指向内部定义的
    #   run_build_and_analysis，调用方（本文件后半 _analyze_v8_source_file）拿到
    #   后直接调用执行两步：① ninja 先编出对象文件；② 用自编 clang++ --analyze
    #   复用与编译完全相同的 flags 重跑该 TU 跑 CSA。原注释 "the WORKING
    #   approach!" 即 fork 实测结论：scan-build 无法整体包裹 V8 构建，可行路径
    #   是精确复刻编译命令行再挂 plugin。
    # analyzer 参数（-Xanalyzer 前缀表示"转交给分析器而非驱动/前端"）：
    #   -load plugin.so + -analyzer-checker custom.SAGenTestChecker +
    #   6 × -analyzer-disable-checker（core/c++/deadcode/unix/nullability/
    #   security，与 Linux 侧六连关一一对应）。
    # flags 复制规则（从原编译命令剔除会干扰分析的项，其余全保留）：
    #   -c/-MMD/-o/-MF 连同其实参成对跳过；*.o、*.o.d、-fmodule-file=*、
    #   -fmodule-map-file=*、-fmodules、-fno-implicit-module-maps、
    #   -fno-implicit-modules、-fbuiltin-module-map、-DUSE_LIBCXX_MODULES 跳过
    #   （Clang modules 在单 TU --analyze 下不稳）；每个 -Xclang 及其后一个
    #   参数成对跳过。
    # 兜底：查不到该文件命令 → 返回 echo 提示字符串；json 读失败 → echo 串；
    #   compile_commands.json 不存在 → RuntimeError（调用方需区分 cmd 可能是
    #   可调用对象或字符串）。
    # ----------------------------------------------------------------------------
    def _generate_v8_analyzer_command(
        self, source_file, obj_file, target, output_dir: Path
    ):
        """
        Generate an analyzer command for V8 source files using compile_commands.json.
        Uses the exact compilation flags from the build system.
        """
        llvm_build_dir = self.backend_path / "build"  # 自编 LLVM build 目录
        plugin_path = f"{llvm_build_dir}/lib/SAGenTestPlugin.so"  # 编好的 checker plugin（默认名单）

        # Check for compile_commands.json and extract compilation command
        compile_commands_path = os.path.join(
            target.repo.working_dir, "out/x64.release/compile_commands.json"
        )
        compile_cmd = ""  # 该源文件的原始编译命令串（待查）

        if os.path.exists(compile_commands_path):
            try:
                with open(compile_commands_path, "r") as f:
                    compile_commands = json.load(f)  # 编译数据库

                # Find the compilation command for this source file
                for entry in compile_commands:
                    if source_file in entry.get("file", ""):  # 子串包含匹配（比 linux 版宽松）
                        compile_cmd = entry.get("command", "")
                        break

                if compile_cmd:  # 查到了 → 构造两步闭包
                    cmd_parts = shlex.split(compile_cmd)  # 词法切分原编译命令

                    # Create output directory
                    output_dir.mkdir(parents=True, exist_ok=True)  # 报告目录先建好

                    # Build command using clang++ driver with --analyze (the WORKING approach!)
                    def run_build_and_analysis():  # 返回给调用方的执行体（两步）
                        # Step 1: Build the object file
                        env = os.environ.copy()
                        env["PATH"] = f"{llvm_build_dir}/bin:" + env.get("PATH", "")  # 自编工具链优先

                        logger.info(
                            f"Running ninja build: {['ninja', '-C', 'out/x64.release', obj_file]}"
                        )
                        build_result = sp.run(  # ① ninja 编对象（保证依赖与生成物就绪）
                            ["ninja", "-C", "out/x64.release", obj_file],
                            cwd=target.repo.working_dir,
                            env=env,
                            capture_output=True,
                            text=True,
                        )

                        if build_result.returncode != 0:  # 编不过就没必要分析了
                            logger.error(f"Ninja build failed: {build_result.stderr}")
                            return build_result

                        # Step 2: Use clang++ driver with --analyze and EXACT same flags as compilation
                        analyzer_cmd = [f"{llvm_build_dir}/bin/clang++", "--analyze"]  # ② 驱动级 --analyze 单 TU 分析

                        # Add plugin and checker flags
                        analyzer_cmd.extend(  # 挂 plugin + 启用合成 checker + 六连关内置包（全部经 -Xanalyzer 转交分析器）
                            [
                                "-Xanalyzer",  # 下一个参数转交分析器
                                "-load",  # 加载 plugin
                                "-Xanalyzer",
                                plugin_path,  # SAGenTestPlugin.so
                                "-Xanalyzer",
                                "-analyzer-checker",  # 启用注册名 custom.* 下的合成 checker
                                "-Xanalyzer",
                                "custom.SAGenTestChecker",
                                "-Xanalyzer",
                                "-analyzer-disable-checker",  # ①关 core
                                "-Xanalyzer",
                                "core",
                                "-Xanalyzer",
                                "-analyzer-disable-checker",  # ②关 cplusplus
                                "-Xanalyzer",
                                "cplusplus",
                                "-Xanalyzer",
                                "-analyzer-disable-checker",  # ③关 deadcode
                                "-Xanalyzer",
                                "deadcode",
                                "-Xanalyzer",
                                "-analyzer-disable-checker",  # ④关 unix
                                "-Xanalyzer",
                                "unix",
                                "-Xanalyzer",
                                "-analyzer-disable-checker",  # ⑤关 nullability
                                "-Xanalyzer",
                                "nullability",
                                "-Xanalyzer",
                                "-analyzer-disable-checker",  # ⑥关 security
                                "-Xanalyzer",
                                "security",
                            ]
                        )

                        # Extract ALL flags from original compilation except output-related ones
                        build_dir = os.path.join(  # 编译命令的原始工作目录（相对路径的基准）
                            target.repo.working_dir, "out/x64.release"
                        )
                        skip_next = False  # 跳过标记：当前 flag 带独立实参时跳下一个 token
                        for part in cmd_parts[1:]:  # Skip compiler name
                            if skip_next:  # 上一 token 是带实参的 flag → 本 token 是其实参，跳过
                                skip_next = False
                                continue

                            # Skip output-related and module-related flags
                            if part in ["-c", "-MMD", "-o", "-MF"]:  # 只编不链/依赖文件/输出路径类 flag：连实参一起跳
                                skip_next = True
                                continue
                            if (
                                part.endswith(".o")  # 对象文件实参
                                or part.endswith(".o.d")  # 依赖描述文件
                                or part.startswith("-fmodule-file=")  # module 文件
                                or part.startswith("-fmodule-map-file=")  # module 映射
                                or part
                                in [
                                    "-fmodules",  # 以下 modules 相关 flags 在单 TU --analyze 下不稳，全部剔除
                                    "-fno-implicit-module-maps",
                                    "-fno-implicit-modules",
                                    "-fbuiltin-module-map",
                                    "-DUSE_LIBCXX_MODULES",
                                ]
                            ):
                                continue

                            # Handle -Xclang pairs properly - skip -Xclang and the next argument if it's module-related
                            if part == "-Xclang":
                                skip_next = True  # Skip the next argument after -Xclang
                                continue  # -Xclang 及其后实参整体跳过（前端专属参数）

                            # Keep all other flags - they work for compilation, they should work for analysis
                            analyzer_cmd.append(part)  # 其余 flags 原样保留：能编译就能分析

                        # Add output file with HTML format for cross-file diagnostics
                        analyzer_cmd.extend(  # 收尾参数：HTML 报告输出 + 待分析源文件（相对 build 目录的 ../../ 路径）
                            [
                                "-Xanalyzer",
                                "-analyzer-output=html",  # scan-build 同款 HTML 报告（供报告蒸馏管线复用）
                                "-o",
                                str(output_dir.absolute()),
                                f"../../{source_file}",  # Relative to build dir
                            ]
                        )

                        # Step 3: Run the analyzer from build directory (same as compilation)
                        logger.info(f"Running analyzer from: {build_dir}")
                        logger.info(f"Analyzer command: {' '.join(analyzer_cmd)}")

                        analyze_result = sp.run(  # 在 out/x64.release 里执行（与原编译同 cwd，相对路径才成立）
                            analyzer_cmd,
                            cwd=build_dir,  # Run from build directory
                            capture_output=True,
                            text=True,
                        )

                        if analyze_result.returncode != 0:  # 分析器报错（前 500 字符足够定位）
                            logger.error(
                                f"Analyzer failed: {analyze_result.stderr[:500]}"
                            )
                        else:
                            logger.info(f"Analyzer successful: {analyze_result.stdout}")

                        return analyze_result  # 把 subprocess 结果原样交回调用方判定

                    cmd = run_build_and_analysis  # 注意：赋的是函数对象本身，调用方须 cmd() 执行
                else:
                    cmd = f"echo 'No compilation command found for {source_file}'"  # 字符串兜底：echo 提示（cmd 类型可变，调用方需兼容）
            except Exception as e:
                cmd = f"echo 'Error reading compile_commands.json: {str(e)}'"  # json 读失败兜底
        else:
            logger.error(f"compile_commands.json not found at {compile_commands_path}")
            raise RuntimeError(  # 数据库缺失属环境错误，直接抛
                f"compile_commands.json not found at {compile_commands_path}"
            )

        return cmd

    # ----------------------------------------------------------------------------
    # _extract_ninja_compile_command（V8 侧备用通道）
    # 职责：用 `ninja -t commands <obj>` 反查某对象目标对应的真实编译命令行
    #   （-t commands 会展开并打印规则命令）。相比 compile_commands.json，
    #   这是更贴近构建现场的一手来源。
    # 匹配两级：先精确（含文件 basename + " -c " + clang + "-c ../../<src>"
    #   或 "-c <src>" 前缀），再放宽（basename + " -c "）。命中行 strip 后返回；
    #   全量命令同时落盘 tmp/ninja_commands.txt 供人工排查。异常/找不到 → None。
    # ----------------------------------------------------------------------------
    def _extract_ninja_compile_command(self, source_file, target):
        """Extract the actual compilation command from ninja for a source file."""
        # Get the object file name for this source
        from targets.v8 import V8  # 局部导入 V8 目标类（避免循环导入）

        obj_file = V8.get_object_name(source_file)  # V8 侧的源文件 → 对象名映射（静态方法）

        # Use ninja -t commands to get the compilation command
        try:
            result = sp.run(
                f"ninja -C out/x64.release -t commands {obj_file}",  # 让 ninja 吐出该目标的完整命令
                shell=True,
                capture_output=True,
                text=True,
                cwd=target.repo.working_dir,  # 在 V8 仓根执行（out/ 相对路径）
                timeout=10,
            )
            Path("tmp/ninja_commands.txt").write_text(result.stdout)  # 全量落盘备查

            if result.returncode == 0 and result.stdout:
                # The output should contain the compilation command
                lines = result.stdout.strip().split("\n")  # 逐行候选命令

                # Look for the line that compiles this specific source file
                # The source file might be referenced as ../../path/to/file
                source_basename = Path(source_file).name  # 只用文件基名匹配
                for line in lines:
                    # Check if this line is compiling our source file
                    if source_basename in line and " -c " in line and "clang" in line:  # 三重条件：含基名 + 是编译(-c) + 是 clang
                        # Make sure it's actually compiling this file, not just mentioning it
                        if (
                            f"-c ../../{source_file}" in line  # 精确：编译目标正是本文件（构建目录相对路径形态）
                            or f"-c {source_file}" in line  # 或仓根相对路径形态
                        ):
                            logger.info(f"Found ninja command for {source_file}")
                            return line.strip()

                # If exact match not found, try a less strict match
                for line in lines:  # 放宽匹配：基名 + " -c "（可能误配同名文件，兜底用）
                    if source_basename in line and " -c " in line:
                        logger.info(
                            f"Found ninja command (relaxed match) for {source_file}"
                        )
                        return line.strip()

        except Exception as e:  # ninja 超时/不存在等
            logger.warning(f"Failed to extract ninja command: {e}")

        return None

    # ----------------------------------------------------------------------------
    # get_num_bugs_from_direct_analysis（V8 侧报告计数 · 直连 clang 输出通道）
    # 职责：从 clang++ --analyze 的原始输出中数出属于合成 checker 的报警行——
    #   一行同时含 "warning:" 与注册名 "custom.SAGenTestChecker" 才计数（内置
    #   checker 已被六连 -analyzer-disable-checker 关闭，这里按注册名再滤一遍
    #   是双保险）。
    # 注意：src/ 与 scripts/ 内均无调用方——现行 _analyze_v8_source_file 走的是
    #   HTML 报告计数（get_num_bugs_from_scan_build），本方法是上游 #14 早期
    #   "直接分析输出、不落盘 HTML"尝试的遗留工具。
    # 参数：output=clang 原始输出文本；返回：报警行数。
    # ----------------------------------------------------------------------------
    def get_num_bugs_from_direct_analysis(self, output):
        """Parse bugs from direct clang analysis output."""
        # Count warning lines that match our checker
        bug_count = 0  # 计数器
        for line in output.split("\n"):  # 逐行扫描
            if "warning:" in line and "custom.SAGenTestChecker" in line:  # 报警行 + 出自本 checker 双条件
                bug_count += 1
        return bug_count

    # ----------------------------------------------------------------------------
    # get_num_bugs_from_scan_build（V8 侧报告计数 · scan-build 兼容 HTML 通道）
    # 职责：数一个报告目录里的 bug 报告数——递归 glob 全部 *.html（** 跨子目录，
    #   V8 是每源文件一个子目录的形态），只统计文件名含 "report-" 的条目（
    #   scan-build 单条 bug 报告命名 report-XXXXXX.html），天然排除 index.html /
    #   scanview.html 两类汇总页。
    # 这正是 V8 分析器统一加 -analyzer-output=html 的原因：让 V8 报告与 Linux
    #   scan-build 的目录形态对齐，计数逻辑与 §3.2 报告蒸馏管线（extract_reports）
    #   均可复用。差分验证（_validate_checker_v8）与全库扫描的 N_buggy/N_patched
    #   都由它给出。
    # 参数：scan_build_output_dir=报告目录；返回：bug 数（目录不存在/无 HTML → 0）。
    # ----------------------------------------------------------------------------
    def get_num_bugs_from_scan_build(self, scan_build_output_dir="/tmp/test-scan"):
        """Parse bugs from scan-build HTML or plist reports."""
        if not os.path.exists(scan_build_output_dir):  # 目录不存在 → 0（调用方按零报警处理）
            return 0

        # First try HTML files (new format for cross-file diagnostics)
        html_files = glob.glob(  # 递归收集目录下全部 HTML
            os.path.join(scan_build_output_dir, "**/*.html"), recursive=True
        )
        if html_files:
            # Count HTML report files (each represents a bug)
            # Exclude index.html and scanview.html which are summaries
            bug_reports = [f for f in html_files if "report-" in os.path.basename(f)]  # 只留 report-* 单条报告，滤掉汇总页
            return len(bug_reports)  # 一份报告 = 一个 bug（与 scan-build "N bugs found" 口径一致）
        else:
            logger.warning(f"No HTML files found in {scan_build_output_dir}")  # 有目录却无 HTML：分析未产出任何报告
            return 0

    # ----------------------------------------------------------------------------
    # _analyze_v8_source_file（V8 单 TU 分析的核心执行体，上游 #16 落地）
    # 职责：拿 compile_commands.json 的一条编译条目，用自编 clang++ --analyze
    #   复刻该 TU 的原编译 flags 跑 CSA，再从 HTML 报告目录数出 bug 数。
    # 与 _generate_v8_analyzer_command 的闭包方案同源（"the WORKING approach"：
    #   scan-build 包不住 V8 构建，可行路径是精确复刻编译命令行再挂 plugin），
    #   差异：纯函数形态、不先 ninja 编对象；由 _validate_checker_v8（§3.1.4
    #   差分验证）与 _analyze_v8_files_parallel（§3.2 全库扫描）共用。
    # flags 复制规则与闭包版一致：-c/-MMD/-o/-MF 连实参跳过，*.o(.d)、modules
    #   类 flag、-Xclang 及其实参剔除，其余全保留（能编译就能分析）。
    # 比闭包版多的 analyzer 参数：-analyzer-config max-loop=8（对应 _v8_args 的
    #   -maxloop 8，限制 ExplodedGraph 循环展开防爆炸）。
    # 参数：compile_entry={file, command, directory}；output_dir=报告目录；
    #   target=V8 目标（directory 缺失时兜底工作目录）；timeout 默认 900s。
    # 返回：(success, num_bugs, error_msg)；超时/异常也先数出已产出的报告再以
    #   success=False 返回——分析半途崩溃不丢已生成的报警。注意非零退出码仍算
    #   success=True（报告可能已部分产出）。
    # ----------------------------------------------------------------------------
    def _analyze_v8_source_file(
        self, compile_entry, output_dir, target=None, timeout=900
    ):
        """
        Helper function to analyze a single V8 source file using clang++ --analyze.

        Args:
            compile_entry: Entry from compile_commands.json containing:
                - file: source file path
                - command: original compilation command
                - directory: working directory for compilation
            output_dir: Directory to save HTML analysis reports
            target: Optional V8 target for fallback working directory
            timeout: Analysis timeout in seconds

        Returns:
            tuple: (success: bool, num_bugs: int, error_message: str or None)
        """
        source_file = compile_entry.get("file", "")  # 源文件路径（../../ 前缀形态）
        compile_cmd = compile_entry.get("command", "")  # 原始编译命令串
        directory = compile_entry.get("directory", "")  # 编译时的工作目录

        if not source_file or not compile_cmd:  # 条目不完整 → 直接判失败
            return False, 0, "Missing file or command in compile entry"

        # Clean up source file path for logging
        if source_file.startswith("../../"):  # 剥构建目录相对前缀（日志友好）
            clean_source = source_file[6:]
        else:
            clean_source = source_file

        # Build clang++ --analyze command
        llvm_build_dir = self.backend_path / "build"  # 自编 LLVM build 目录
        plugin_path = f"{llvm_build_dir}/lib/SAGenTestPlugin.so"  # 合成 checker plugin（默认名）

        cmd_parts = shlex.split(compile_cmd)  # 词法切分原编译命令（正确处理引号）
        analyzer_cmd = [f"{llvm_build_dir}/bin/clang++", "--analyze"]  # 驱动级 --analyze 单 TU 分析

        # Add plugin and checker configuration
        analyzer_cmd.extend(  # 挂 plugin + 启用合成 checker + 六连关内置包 + max-loop + HTML 输出（全部经 -Xanalyzer 转交分析器）
            [
                "-Xanalyzer",  # 下一参数转交分析器本体
                "-load",  # 加载 plugin .so
                "-Xanalyzer",
                plugin_path,  # SAGenTestPlugin.so
                "-Xanalyzer",
                "-analyzer-checker",  # 启用注册名 custom.* 的合成 checker
                "-Xanalyzer",
                "custom.SAGenTestChecker",
                "-Xanalyzer",
                "-analyzer-disable-checker",  # ①关 core（与 Linux 侧六连关一一对应）
                "-Xanalyzer",
                "core",
                "-Xanalyzer",
                "-analyzer-disable-checker",  # ②关 cplusplus
                "-Xanalyzer",
                "cplusplus",
                "-Xanalyzer",
                "-analyzer-disable-checker",  # ③关 deadcode
                "-Xanalyzer",
                "deadcode",
                "-Xanalyzer",
                "-analyzer-disable-checker",  # ④关 unix
                "-Xanalyzer",
                "unix",
                "-Xanalyzer",
                "-analyzer-disable-checker",  # ⑤关 nullability
                "-Xanalyzer",
                "nullability",
                "-Xanalyzer",
                "-analyzer-disable-checker",  # ⑥关 security
                "-Xanalyzer",
                "security",
                "-Xanalyzer",
                "-analyzer-config",  # 分析器配置项（下接 key=value）
                "-Xanalyzer",
                "max-loop=8",  # 循环展开上限 8（对应 _v8_args 的 -maxloop 8）
                "-Xanalyzer",
                "-analyzer-output=html",  # HTML 报告（scan-build 同款形态，供 get_num_bugs_from_scan_build/extract_reports 消费）
                "-o",
                str(output_dir.absolute())  # 报告输出目录（三元表达式兼容 output_dir 是 str 的情况）
                if hasattr(output_dir, "absolute")
                else str(output_dir),
            ]
        )

        # Extract compilation flags from original command (skip output and module-related flags)
        skip_next = False  # 跳过标记：上一 token 是带独立实参的 flag 时，本 token 是其实参
        for part in cmd_parts[1:]:  # Skip compiler name —— 跳过命令首的编译器可执行名
            if skip_next:
                skip_next = False
                continue

            # Skip flags we don't want
            if part in ["-c", "-MMD", "-o", "-MF"]:  # 只编不链/依赖文件/输出路径类：连实参跳过
                skip_next = True
                continue
            if (
                part.endswith((".o", ".o.d"))  # 对象文件/依赖描述文件实参（tuple 形式一次判两个后缀）
                or part.startswith("-fmodule-file=")  # module 文件
                or part.startswith("-fmodule-map-file=")  # module 映射
                or part == "-Xclang"  # 前端专属参数：-Xclang 及其后实参整体跳过
            ):
                skip_next = True
                continue
            if part in [  # modules 相关 flags：单 TU --analyze 下不稳，逐个剔除
                "-fmodules",
                "-fno-implicit-module-maps",
                "-fno-implicit-modules",
                "-fbuiltin-module-map",
                "-DUSE_LIBCXX_MODULES",
            ]:
                continue

            analyzer_cmd.append(part)  # 其余 flags 原样保留——能编译就能分析

        # Add the source file
        analyzer_cmd.append(source_file)  # 最后追加待分析源文件（保持 ../../ 形态，配合 directory 工作目录解析）

        # Determine working directory
        work_dir = directory or (target.repo.working_dir if target else None)  # 优先编译数据库的 directory，回退 V8 仓根
        if not work_dir:
            return False, 0, "No working directory specified"

        # Run analysis
        try:
            analyze_result = sp.run(  # 在与原编译相同的工作目录执行（相对路径才成立）
                analyzer_cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            # Count bugs from HTML output
            num_bugs = self.get_num_bugs_from_scan_build(str(output_dir))  # 从 HTML 报告目录计数
            error_msg = None

            if analyze_result.returncode != 0:  # 非零退出码：分析器报错，但报告可能已部分产出
                # Non-zero return code but analysis may still have produced results
                error_msg = analyze_result.stderr
                escape_source = clean_source.replace("/", "_")  # 路径安全化文件名
                Path(f"tmp/error-{escape_source}.txt").write_text(error_msg)  # stderr 落盘供排查
                logger.warning(
                    f"Analysis returned non-zero code for {clean_source}: {analyze_result.returncode}"
                )

            return True, num_bugs, error_msg  # 非零退出码仍算 success=True（num_bugs 已数出）

        except sp.TimeoutExpired:  # 超时：先数已产出的报告再报失败（不丢半程成果）
            num_bugs = self.get_num_bugs_from_scan_build(str(output_dir))
            return False, num_bugs, f"Timeout analyzing {clean_source} after {timeout}s"
        except Exception as e:  # 其余异常：同样先数报告
            num_bugs = self.get_num_bugs_from_scan_build(str(output_dir))
            return False, num_bugs, f"Error analyzing {clean_source}: {str(e)}"

    # ----------------------------------------------------------------------------
    # _analyze_v8_files_parallel（V8 全库扫描的并行执行体，fork 增量）
    # 职责：把 compile_commands.json 滤出的 N 个编译条目交 ThreadPoolExecutor
    #   并行跑 _analyze_v8_source_file，汇总 (total_bugs, analyzed_files,
    #   failed_files)。这是 V8 版"全库扫描"的吞吐核心——Linux 侧靠 make -jN
    #   在构建期并行分析各 TU，V8 侧构建已完成，改为纯分析任务的线程池并行
    #   （每线程一个 clang++ 子进程，GIL 不构成瓶颈）。
    # 并发安全：计数器与目录清理都在 threading.Lock 临界区内。
    # 报告目录策略：每文件一个 safe_filename 子目录；零报警/失败/异常的目录随
    #   手 rmtree 清掉——最终目录树只保留真正报 bug 的文件目录（即 §3.2 报告
    #   蒸馏 extract_reports 的输入形态）。
    # 参数：source_entries_list=编译条目列表；unique_output_dir=时间戳报告根
    #   目录；target=V8 目标；max_workers 默认 32（_run_checker_v8 按
    #   global_config.jobs 与文件数取小后传入）。
    # 返回：(总 bug 数, 成功文件数, 失败文件数)。
    # ----------------------------------------------------------------------------
    def _analyze_v8_files_parallel(
        self, source_entries_list, unique_output_dir, target, max_workers=32
    ):
        """
        Analyze V8 source files in parallel.

        Args:
            source_entries_list: List of compile_commands.json entries to analyze
            unique_output_dir: Base output directory for reports
            target: V8 target
            max_workers: Number of parallel workers

        Returns:
            tuple: (total_bugs, analyzed_files, failed_files)
        """

        # Thread-safe counters
        total_bugs = 0  # 总 bug 数（各线程累加，锁保护）
        analyzed_files = 0  # 成功分析的文件数
        failed_files = 0  # 失败文件数（超时/错误/异常）
        lock = threading.Lock()  # 计数器互斥锁

        def analyze_single_file(entry_with_index):  # 单文件工作单元（线程池内执行）
            """Analyze a single source file - designed for parallel execution"""
            i, entry = entry_with_index  # 解包 (序号, 编译条目)——序号只用于进度日志
            nonlocal total_bugs, analyzed_files, failed_files  # 闭包改写外层计数器

            source_file = entry.get("file", "")
            if source_file.startswith("../../"):  # 同款剥 ../../ 前缀
                clean_source = source_file[6:]
            else:
                clean_source = source_file

            # Create unique output directory name from full source path
            safe_filename = clean_source.replace("/", "_").replace(".", "_")  # 全路径换 _ 成唯一目录名（不同目录下的同名文件不冲突）
            file_output_dir = unique_output_dir / safe_filename
            file_output_dir.mkdir(parents=True, exist_ok=True)

            # Log progress for large batches
            if len(source_entries_list) > 10:  # 大批量时节流：首个与每 10 个打一条
                if (i + 1) % 10 == 0 or i == 0:
                    logger.info(
                        f"Progress: {i + 1}/{len(source_entries_list)} files - Analyzing: {clean_source}"
                    )

            try:
                # Use helper function to analyze the file
                success, num_bugs, error_msg = self._analyze_v8_source_file(  # 核心：单 TU clang++ --analyze
                    entry, file_output_dir, target=target, timeout=900
                )

                # Thread-safe updates
                with lock:  # —— 计数器更新临界区 ——
                    if success:
                        if num_bugs > 0:
                            logger.info(
                                f"Found {num_bugs} bugs in {clean_source} -> {safe_filename}/"
                            )
                            total_bugs += num_bugs
                        else:
                            # Remove empty directory
                            shutil.rmtree(file_output_dir, ignore_errors=True)  # 零报警 → 目录即删（只留有 bug 的）
                        analyzed_files += 1
                    else:
                        if "Timeout" in error_msg:  # 超时降级为 warning（大批量下常见，非致命）
                            logger.warning(
                                f"{error_msg} (file {i+1}/{len(source_entries_list)})"
                            )
                        else:
                            logger.error(error_msg)
                        failed_files += 1
                        # Remove directory on failure
                        shutil.rmtree(file_output_dir, ignore_errors=True)  # 失败目录同样清理

            except Exception as e:  # 工作单元内未预期异常兜底（不让单文件拖垮整池）
                with lock:
                    logger.error(f"Unexpected error analyzing {clean_source}: {e}")
                    failed_files += 1
                    # Remove directory on exception
                    shutil.rmtree(file_output_dir, ignore_errors=True)

        # Execute analysis in parallel
        logger.info(f"Starting parallel analysis with {max_workers} workers")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:  # 线程池：任务全部提交，退出时自动 join
            # Submit all tasks
            futures = []
            for i, entry in enumerate(source_entries_list):  # 全量提交（带序号）
                future = executor.submit(analyze_single_file, (i, entry))
                futures.append(future)

            # Wait for all tasks to complete
            completed = 0
            for future in as_completed(futures):  # 按完成序回收（而非提交序）
                completed += 1
                if len(source_entries_list) > 20 and completed % 20 == 0:  # 大批量每 20 个报一次完成度
                    logger.info(
                        f"Completed {completed}/{len(source_entries_list)} files"
                    )

                try:
                    future.result()  # This will raise any exception that occurred —— 工作单元漏抛的异常在此显形
                except Exception as e:
                    with lock:
                        logger.error(f"Future execution error: {e}")
                        failed_files += 1

        logger.info(f"Parallel analysis completed")
        return total_bugs, analyzed_files, failed_files

    # ----------------------------------------------------------------------------
    # _configure_v8_clang（V8 构建系统换用自编 clang 的 GN 配置器 · 实验通道）
    # 职责：找到 gn 可执行文件后，用 gn gen 生成一套让 V8 构建改用自编 clang 的
    #   args（clang_base_path/cxx/cc/ar/ranlib 全指向 backend_path/build）。注释
    #   自述 "for scan-build interception"：若 V8 的编译器本身就是自编 clang，
    #   构建期即可被 scan-build 拦截——这是想让 V8 复刻 Linux `make LLVM=1` 被
    #   scan-build 包裹方案的尝试。
    # 大量 GN 开关是踩坑沉淀：关 chrome 插件/CFI/thinLTO/自动 modules、强制
    #   lld、llvm_android_mainline=true 去掉 crel flags（老 clang 不认）、关
    #   定制 libcxx、禁 -Werror 等，全为让自编工具链编得过 V8。
    # 现状：src/ 内无调用方——最终落地路线是 compile_commands.json + clang++
    #   --analyze 复刻（_analyze_v8_source_file），本方法保留为"构建期拦截"
    #   方案的遗迹（上游 #14 探索路径）。
    # ----------------------------------------------------------------------------
    def _configure_v8_clang(self, target):
        """
        Configure V8 build to use our custom clang for scan-build interception.
        """

        # Find GN executable (similar to v8.py logic)
        gn_exe = None  # gn 可执行文件路径（待找）
        gn_candidates = [  # 两个仓内候选位置：buildtools/linux64/gn 或 third_party/depot_tools/gn
            Path(target.repo.working_dir) / "buildtools" / "linux64" / "gn",
            Path(target.repo.working_dir) / "third_party" / "depot_tools" / "gn",
        ]

        for candidate in gn_candidates:  # 先查仓内候选
            if candidate.exists() and candidate.is_file():
                gn_exe = str(candidate)
                break

        if not gn_exe:
            # Try to find gn in PATH
            gn_exe = shutil.which("gn")  # 兜底：PATH 里找

        if not gn_exe:  # 三处都找不到 → 放弃配置（warning 后返回）
            logger.warning("GN executable not found. Cannot configure custom clang.")
            return

        # Configure V8 to use our custom clang
        clang_base_path = self.backend_path / "build"  # 自编 LLVM build 目录（bin/lib 所在地）

        # Get the clang version
        clang_version_result = sp.run(  # 问自编 clang 的版本号（GN args 需要显式告知以拼资源路径）
            [str(clang_base_path / "bin" / "clang"), "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        clang_version = "21"  # default —— 拿不到版本时的默认值
        if clang_version_result.returncode == 0:
            version_match = re.search(  # 从 "clang version N" 抓主版本号
                r"clang version (\d+)", clang_version_result.stdout
            )
            if version_match:
                clang_version = version_match.group(1)

        logger.info(f"Detected clang version: {clang_version}")

        # Use our custom clang if compiler-rt is available
        gn_args = [  # GN 构建参数表（'key=value' 串列表，空格拼接后经 --args 整体传给 gn gen）
            "is_debug=false",  # release 构建
            f'clang_base_path="{clang_base_path}"',  # 指定自编 clang 根目录
            "clang_use_chrome_plugins=false",  # 关 Chrome 专属 clang 插件（自编 clang 没有）
            f'clang_version="{clang_version}"',  # 版本号
            "use_custom_libcxx=false",  # 不用 Chromium 定制 libc++（自编工具链无配套预编译库）
            "v8_use_external_startup_data=false",  # 内置 snapshot 数据（简化产物）
            "use_clang_modules=false",  # 关 clang modules（与单 TU 分析剔 modules flags 同因）
            "use_autogenerated_modules=false",  # 关自动生成 modules
            "is_clang=true",  # 声明使用 clang 工具链
            # Disable experimental features that clang 18 doesn't support
            "use_cfi=false",  # CFI 依赖新版 clang，关
            "use_thin_lto=false",  # thinLTO 同理，关
            "use_custom_libcxx=false",  # （原文件重复声明第二次，保持原样）
            # Use LLVM's lld linker to avoid archive indexing issues
            "use_lld=true",  # 换 lld 链接器，避开 ar 索引问题
            # Force older clang compatibility
            "llvm_android_mainline=true",  # This disables crel flags —— 兼容开关：禁用 crel 新格式
            # Use our own clang++ and ensure proper C++ standard
            f'cxx="{clang_base_path}/bin/clang++"',  # C++ 编译器指到自编 clang++
            f'cc="{clang_base_path}/bin/clang"',  # C 编译器同理
            # Use LLVM's ar and ranlib to avoid index issues
            f'ar="{clang_base_path}/bin/llvm-ar"',  # 归档器配套用 llvm-ar
            f'ranlib="{clang_base_path}/bin/llvm-ranlib"',  # 索引器配套用 llvm-ranlib
            # Add libcxx include paths for C++20 support
            # f'extra_cppflags=["-I{clang_base_path}/include/c++/v1", "-stdlib=libc++"]',  # （被注释掉的尝试：libc++ 头文件路径）
            # f'extra_ldflags=["-L{clang_base_path}/lib", "-stdlib=libc++", "-lc++", "-lc++abi"]',  # （被注释掉的尝试：libc++ 链接 flags）
            # Add compiler flags to handle C++20 features
            "treat_warnings_as_errors=false",  # 自编 clang 对 V8 会出新 warning，不能 -Werror
        ]

        logger.info(f"Configuring V8 build with custom clang: {clang_base_path}")
        build_dir = "out/x64.release"  # 输出构建目录（全文约定的 x64.release）

        res = sp.run(  # gn gen 重生成构建目录（ninja 文件按上述 args 重写）
            [gn_exe, "gen", build_dir, f"--args={' '.join(gn_args)}"],
            cwd=target.repo.working_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if res.returncode != 0:  # 配置失败：stdout/stderr 双通道落日志，不抛异常
            logger.error(f"Failed to configure V8 with custom clang: {res.stderr}")
            logger.error(res.stdout)
        else:
            logger.info("Successfully configured V8 to use custom clang")

    # ----------------------------------------------------------------------------
    # _run_checker_v8（论文 §3.2 执行入口的 V8 实现，上游 #16——fork 增量的
    #   Generability 代码落地；Linux 版 _run_checker_linux 的姊妹函数）
    # 与 Linux 版的三点结构差异：
    #   1) V8 构建无法被 scan-build 整体包裹 → 先 ninja 整树构建，再对
    #      compile_commands.json 的全部第一方 C++ 条目逐个 clang++ --analyze
    #      复刻原编译 flags（parallel_analysis=True 走线程池，False 串行）；
    #   2) 文件过滤：third_party/buildtools/gen/tools/v8_gypfiles 一律排除
    #      （第三方与生成代码不是找 bug 的对象）；
    #   3) 产物对齐：时间戳目录 + _create_v8_report_softlinks 把子目录报告
    #      软链成扁平结构——checker_refine（§3.2 refinement）与 extract_reports
    #      无需感知 Linux/V8 差异即可取报告。
    # 哨兵与 Linux 版一致：-999=构建失败 / -1=超时（含"单文件且失败"的对象级
    #   语义）/ -10=报警过多（阈值 300，与 Linux monitor warning_limit=300 同源，
    #   这种 checker 在 §3.2 里交 refinement 处理）。
    # 参数：arch 默认 x64、build_config 默认 release（拼出 out/x64.release）、
    #   timeout 默认 1800s；skip_v8_build=True 复用既有构建产物；
    #   skip_checkout/skip_build_checker 供逐对象循环复用前序状态。
    # ----------------------------------------------------------------------------
    def _run_checker_v8(
        self,
        checker_code: str,
        commit_id: str,
        target,
        object_to_analyze: str = None,
        jobs: int = 32,
        output_dir: str = "tmp",
        skip_build_checker: bool = False,
        skip_checkout: bool = False,
        skip_v8_build: bool = False,
        parallel_analysis: bool = True,
        **kwargs,
    ) -> int:
        """
        Run the checker against a V8 commit.

        Pipeline:
        1. Build the entire V8 project with ninja (unless skip_v8_build=True)
        2. Use clang++ --analyze on all source files from compile_commands.json

        Args:
            checker_code (str): The checker code to run.
            commit_id (str): The commit ID to run the checker against.
            target: The V8 target to be tested.
            object_to_analyze (str): The source file to analyze (optional).
            jobs (int): Number of jobs to run in parallel for ninja build.
            output_dir (str): Directory to save the output.
            skip_build_checker (bool): Skip building the checker.
            skip_checkout (bool): Skip checking out the commit.
            skip_v8_build (bool): Skip building V8 (reuse existing out/ directory).
            parallel_analysis (bool): Analyze source files in parallel.

        Returns:
            int: Number of bugs found, or negative values for errors:
                -999: Build failed
                -1: Timeout
                -10: Too many bugs found
        """
        # Remove depot_tools from PATH to prevent interference
        original_path = os.environ.get("PATH", "")  # 备份原 PATH（与 _validate_checker_v8 一样不恢复）
        filtered_path = ":".join(  # 过滤掉含 depot_tools 的路径段
            [p for p in original_path.split(":") if "depot_tools" not in p]
        )
        os.environ["PATH"] = filtered_path  # 生效：后续子进程均用净化后的 PATH

        logger.info(f"V8 run checker: removed depot_tools from PATH")

        # Extract parameters from kwargs
        arch = kwargs.get("arch", "x64")  # 默认 x64
        build_config = kwargs.get("build_config", "release")  # 默认 release
        timeout = kwargs.get("timeout", 1800)  # 整树构建超时（默认 30 分钟，与 Linux 版一致）
        build_dir = f"out/{arch}.{build_config}"  # 构建目录（out/x64.release）

        output_dir = Path(output_dir)  # 报告根目录转 Path

        # Build checker if needed
        if not skip_build_checker:  # 可选：编译 checker plugin
            build_res, stderr = self.build_checker(checker_code, Path("tmp"), attempt=1)
            if build_res != 0:  # 编译失败 → -999 哨兵（Linux 版走异常，这里走哨兵返回）
                logger.error(f"Build failed: {stderr}")
                return -999

        # Use the provided output_dir directly (consistent with Linux)
        # No longer create unique timestamped directories  —— 报告根直接用调用方目录；时间戳子目录在 Step 3 里建

        # Checkout commit if needed
        if not skip_checkout:  # 需要时 checkout（V8 版 fetch+checkout；is_before=False=扫当前态）
            llvm_build_dir = self.backend_path / "build"
            print(commit_id)  # 调试遗留：直接 print commit 号
            target.checkout_commit(
                commit_id,
                is_before=False,  # 找 bug 场景扫目标提交本身（差分验证才切 buggy 前提交）
                arch=arch,
                build_config=build_config,
                llvm_path=llvm_build_dir,  # 传自编 LLVM 供目标侧配置
                skip_v8_build=skip_v8_build,
            )
        else:
            logger.info("Skipping checkout")

        # Step 1: Build entire V8 with ninja (unless skip_v8_build is True)
        llvm_build_dir = self.backend_path / "build"  # （上面 if 分支已赋过，这里无条件再赋一次）
        env = os.environ.copy()  # 子进程环境副本
        env["PATH"] = f"{llvm_build_dir}/bin:" + env.get("PATH", "")  # 自编 clang/ninja 优先于系统工具链

        if not skip_v8_build:  # —— Step 1：整树构建（compile_commands.json 的生产者）——
            logger.info(f"Building entire V8 project with ninja -j{jobs}")

            build_cmd = ["ninja", "-C", build_dir, "-k", "5"]  # -k 5：出错后最多再容忍 5 个失败任务继续编
            if jobs:
                build_cmd.append(f"-j{jobs}")  # 并行度

            logger.info(f"Running: {' '.join(build_cmd)}")

            try:
                build_result = sp.run(  # 在 V8 仓根跑 ninja（可能 30 分钟级）
                    build_cmd,
                    cwd=target.repo.working_dir,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )

                if build_result.returncode != 0:  # 构建有失败：stdout/stderr 落盘排查
                    logger.error(f"Ninja build failed")
                    # Log down the error msg
                    Path("tmp/v8-build-stdout.txt").write_text(build_result.stdout)
                    Path("tmp/v8-build-stderr.txt").write_text(build_result.stderr)

                    # FIXME: There are some issues when building v8 testcases
                    # FIXME: Now we just keep going
                    # return -999  —— 有意不返回：测试用例编不过不影响主源码分析（fork 实测决策）

                logger.info("V8 build completed successfully")

            except sp.TimeoutExpired:  # 整树构建超时 → -1
                logger.error(f"V8 build timeout after {timeout} seconds")
                return -1
            except Exception as e:  # 其他进程级异常 → -999
                logger.error(f"V8 build error: {e}")
                return -999
        else:
            logger.info("Skipping V8 build - using existing build artifacts")  # 复用现成构建（省整树构建时间）

        # Step 2: Get all source files from compile_commands.json
        compile_commands_path = (  # 编译数据库：分析任务清单的唯一来源
            Path(target.repo.working_dir) / build_dir / "compile_commands.json"
        )

        if not compile_commands_path.exists():  # 没有它就无从分析 → -999
            logger.error(f"compile_commands.json not found at {compile_commands_path}")
            return -999

        try:
            with open(compile_commands_path, "r") as f:
                compile_commands = json.load(f)
        except Exception as e:  # 解析失败同样 -999
            logger.error(f"Failed to read compile_commands.json: {e}")
            return -999

        # Filter source files to analyze
        source_files_to_analyze = []  # 待分析编译条目列表

        if object_to_analyze:  # —— 对象级模式：只分析指定源文件 ——
            # Analyze specific file only
            for entry in compile_commands:
                file_path = entry.get("file", "")
                # Normalize path
                if file_path.startswith("../../"):  # 剥 ../../ 前缀再比对
                    file_path = file_path[6:]

                if file_path == object_to_analyze or file_path.endswith(  # 精确相等或后缀匹配（容忍路径前缀差异）
                    f"/{object_to_analyze}"
                ):
                    source_files_to_analyze.append(entry)
                    break  # 命中一条即止（同文件只有一条编译命令）
        else:
            # Analyze all source files —— 全库模式：滤出全部第一方 C++ 条目
            for entry in compile_commands:
                file_path = entry.get("file", "")
                if file_path and file_path.endswith((".cc", ".cpp", ".c")):  # 只要 C/C++ 源（排除 .S 等）
                    # Skip third-party and generated files
                    if not any(  # 排除表：第三方/构建工具/生成代码/gyp 产物（非第一方代码，分析无意义且噪音大）
                        exclude in file_path
                        for exclude in [
                            "third_party/",
                            "buildtools/",
                            "gen/",
                            "tools/v8_gypfiles/",
                        ]
                    ):
                        source_files_to_analyze.append(entry)

        if not source_files_to_analyze:  # 滤完为空 → 按零 bug 返回 0（不视为错误）
            logger.error("No source files to analyze")
            return 0

        logger.info(f"Analyzing {len(source_files_to_analyze)} V8 source files")

        # Create timestamped directory (consistent with Linux scan-build behavior)
        timestamped_output_dir = self._create_timestamped_output_dir(output_dir)  # scan-build 同款时间戳目录（防多轮互相覆盖）

        # Step 3: Run clang++ --analyze on source files (parallel or sequential)
        if parallel_analysis:  # —— 并行模式（默认）：线程池 ——
            # Import here to avoid circular import
            from global_config import global_config  # 局部导入拿全局并行度配置（避免循环依赖）

            # Use parallel analysis
            default_workers = min(global_config.jobs, len(source_files_to_analyze))  # worker 数 = 配置并行度（默认 32）与文件数取小
            max_workers = kwargs.get("max_workers", default_workers)  # 可被 kwargs 覆盖
            logger.info(f"Using parallel analysis with {max_workers} workers")

            total_bugs, analyzed_files, failed_files = self._analyze_v8_files_parallel(
                source_files_to_analyze,
                timestamped_output_dir,  # Use timestamped directory
                target,
                max_workers=max_workers,
            )

            # Handle single file timeout case for parallel analysis
            if failed_files > 0 and len(source_files_to_analyze) == 1:  # 单文件任务且失败 → -1 超时哨兵（对象级扫描的失败语义；多文件任务里个别失败只计数）
                return -1

        else:
            # Use sequential analysis (original logic with tmp directory) —— 串行模式：逐文件循环（原始实现）
            # Progress tracking for large batches
            if len(source_files_to_analyze) > 10:
                logger.info(
                    "Large number of files detected. Progress will be logged every 10 files."
                )

            total_bugs = 0
            analyzed_files = 0
            failed_files = 0

            for i, entry in enumerate(source_files_to_analyze):
                source_file = entry.get("file", "")

                # Clean up source file path for logging
                if source_file.startswith("../../"):  # 剥前缀（日志用）
                    clean_source = source_file[6:]
                else:
                    clean_source = source_file

                # Progress logging
                if len(source_files_to_analyze) > 10:  # 大批量节流（与并行版同款策略）
                    if (i + 1) % 10 == 0 or i == 0:
                        logger.info(
                            f"Progress: {i + 1}/{len(source_files_to_analyze)} files - Analyzing: {clean_source}"
                        )
                else:
                    logger.info(f"Analyzing: {clean_source}")

                # Create temp output directory first
                temp_output_dir = timestamped_output_dir / "tmp"  # 先写临时目录，报了 bug 才转正（零报警文件不留目录）
                temp_output_dir.mkdir(parents=True, exist_ok=True)

                # Use helper function to analyze the file
                success, num_bugs, error_msg = self._analyze_v8_source_file(
                    entry, temp_output_dir, target=target, timeout=900
                )

                if success:
                    if num_bugs > 0:
                        # Only create permanent directory if bugs were found
                        # Use full path with slashes replaced by underscores
                        safe_filename = clean_source.replace("/", "_").replace(".", "_")
                        final_output_dir = timestamped_output_dir / safe_filename  # 转正目录名（与并行版一致）

                        # Move tmp directory to final location

                        if final_output_dir.exists():  # 旧轮同名目录先删
                            shutil.rmtree(final_output_dir)
                        shutil.move(str(temp_output_dir), str(final_output_dir))  # tmp → 正式目录

                        # Recreate tmp dir for next file
                        temp_output_dir.mkdir(parents=True, exist_ok=True)

                        logger.info(
                            f"Found {num_bugs} bugs in {clean_source} -> {safe_filename}/"
                        )
                        total_bugs += num_bugs
                    else:
                        # Clean up tmp directory if no bugs found

                        shutil.rmtree(temp_output_dir, ignore_errors=True)  # 零报警 → 清空 tmp 重建
                        temp_output_dir.mkdir(parents=True, exist_ok=True)

                    analyzed_files += 1
                else:
                    if "Timeout" in error_msg:  # 超时：单文件任务直接 -1 返回（对象级语义），否则计数继续
                        logger.warning(
                            f"{error_msg} (file {i+1}/{len(source_files_to_analyze)})"
                        )
                        failed_files += 1
                        if len(source_files_to_analyze) == 1:
                            return -1
                    else:
                        logger.error(error_msg)
                        failed_files += 1

            # Clean up any remaining tmp directory
            temp_output_dir = timestamped_output_dir / "tmp"  # 收尾：残留 tmp 目录清掉
            if temp_output_dir.exists():

                shutil.rmtree(temp_output_dir, ignore_errors=True)

        # Final summary
        logger.info(f"V8 analysis completed:")  # 汇总日志：成功/失败/总 bug
        logger.info(
            f"  Files analyzed: {analyzed_files}/{len(source_files_to_analyze)}"
        )
        logger.info(f"  Files failed: {failed_files}")
        logger.info(f"  Total bugs found: {total_bugs}")

        # Create softlinks for refinement compatibility if needed
        self._create_v8_report_softlinks(timestamped_output_dir, output_dir)  # 报告结构对齐 scan-build/refine 管线（见下）

        # Handle special cases
        if total_bugs > 300:  # Too many bugs threshold —— 报警过多哨兵（300 与 Linux monitor warning_limit=300 同源）
            logger.warning("Too many bugs found!")
            return -10

        return total_bugs

    # ----------------------------------------------------------------------------
    # _create_timestamped_output_dir：仿 scan-build 的时间戳报告目录。
    # 命名 YYYY-MM-DD-HHMMSS-PID-N（N 为 1..9999 随机数）：时间戳+进程号+随机
    #   后缀三重防撞——同秒、同进程的多次运行也不互相覆盖。Linux 侧 scan-build
    #   自带这种命名，V8 侧没有 scan-build，故手工仿造，使两目标的报告目录形态
    #   一致（extract_reports "按创建时间取最新目录"的排序逻辑才能两边复用）。
    # 参数：base_output_dir=报告根目录；返回：新建的时间戳子目录 Path。
    # ----------------------------------------------------------------------------
    def _create_timestamped_output_dir(self, base_output_dir: Path) -> Path:
        """
        Create a timestamped output directory similar to scan-build's behavior.

        This creates a directory with format: YYYY-MM-DD-HHMMSS-PID-N
        consistent with Linux scan-build timestamps.

        Args:
            base_output_dir: The base output directory

        Returns:
            Path: The timestamped output directory
        """
        # Create timestamp similar to scan-build format
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")  # 秒级时间戳
        pid = os.getpid()  # 进程号（同机并发隔离）
        rand_suffix = random.randint(1, 9999)  # 随机后缀（同进程多次调用隔离）

        # Create directory name: YYYY-MM-DD-HHMMSS-PID-N
        timestamped_name = f"{timestamp}-{pid}-{rand_suffix}"
        timestamped_dir = Path(base_output_dir) / timestamped_name

        # Create the directory
        timestamped_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Created timestamped output directory: {timestamped_dir}")
        return timestamped_dir

    # ----------------------------------------------------------------------------
    # _create_v8_report_softlinks：把 V8 的"每源文件一个子目录"报告结构软链成
    #   scan-build 的扁平结构——§3.2 refinement 管线（checker_refine.py 的
    #   extract_reports / triage）对报告目录形态的假设全部来自 Linux scan-build。
    # 两级软链：
    #   ① 时间戳目录内：每个子目录里的 *.html 链到时间戳根，链接名
    #      <子目录名>_<文件名>（扁平化 + 防同名报告冲突）；
    #   ② 报告根目录：时间戳目录里的全部 *.html（含①刚建的软链）再链到报告根。
    # 失败仅 warning 不中断：报告本体还在子目录里，链接只是兼容层。
    # 参数：timestamped_output_dir=时间戳报告目录；base_output_dir=报告根。
    # ----------------------------------------------------------------------------
    def _create_v8_report_softlinks(
        self, timestamped_output_dir: Path, base_output_dir: Path
    ) -> None:
        """
        Create softlinks to make V8 report structure compatible with refinement process.

        Creates two levels of softlinks:
        1. From timestamped subdirectories to base output dir (for refinement process)
        2. From subdirectory HTML files to timestamped root (for scan-build compatibility)

        Args:
            timestamped_output_dir: The timestamped directory containing V8 report subdirectories
            base_output_dir: The base output directory where refinement expects reports
        """
        try:
            timestamped_output_dir = Path(timestamped_output_dir)  # 统一转 Path（容忍 str 传入）
            base_output_dir = Path(base_output_dir)

            if not timestamped_output_dir.exists():  # 目录不存在（如零报警被清理）→ 无事可做
                return

            # Find all HTML files in subdirectories within timestamped dir
            html_files_in_subdirs = list(timestamped_output_dir.glob("*/*.html"))  # 只抓一层子目录的 HTML（V8 每源文件一目录的形态）

            if not html_files_in_subdirs:
                # No subdirectory structure, reports might already be in root —— 已是扁平结构（或没报告），不动
                return

            logger.info(
                f"Creating V8 report softlinks for {len(html_files_in_subdirs)} files"
            )

            # 1. Create softlinks in the timestamped root directory (scan-build compatibility)
            for html_file in html_files_in_subdirs:  # ① 子目录报告 → 时间戳根扁平化
                subdir_name = html_file.parent.name  # 源文件安全名（即子目录名）
                file_name = html_file.name  # report-XXXXXX.html

                # Create unique link name in timestamped root
                link_name = f"{subdir_name}_{file_name}"  # <源文件名>_<报告名>：不同子目录同名报告不冲突
                timestamped_link_path = timestamped_output_dir / link_name

                # Remove existing link if it exists
                if timestamped_link_path.exists() or timestamped_link_path.is_symlink():  # 先清旧链（is_symlink 单独查：悬空链 exists() 为 False）
                    timestamped_link_path.unlink()

                # Create relative symlink within timestamped directory
                relative_target = Path(subdir_name) / file_name  # 相对目标（目录整体搬移不断链）
                timestamped_link_path.symlink_to(relative_target)

            # 2. Create softlinks from base output dir to timestamped files (refinement compatibility)
            base_output_dir.mkdir(parents=True, exist_ok=True)  # 报告根目录兜底建好

            # Link all HTML files from timestamped directory to base directory
            for html_file in timestamped_output_dir.glob("*.html"):  # ② 时间戳根全部 HTML（含①刚建的软链）→ 报告根
                base_link_path = base_output_dir / html_file.name

                # Remove existing link if it exists
                if base_link_path.exists() or base_link_path.is_symlink():
                    base_link_path.unlink()

                # Create relative symlink from base to timestamped
                timestamped_name = timestamped_output_dir.name  # 时间戳目录名（链接相对目标的路径前缀）
                relative_target = Path(timestamped_name) / html_file.name
                base_link_path.symlink_to(relative_target)

            logger.info(
                f"Created V8 softlinks: {len(html_files_in_subdirs)} in timestamped dir, mirrored to base dir"
            )

        except Exception as e:
            logger.warning(f"Failed to create V8 report softlinks: {e}")  # 软链失败非致命：报告本体仍在，只缺兼容层
            # Non-fatal error - continue without softlinks

    # ----------------------------------------------------------------------------
    # _discover_all_v8_source_files（V8 源文件发现 · 编译数据库优先，fork 增量）
    # 职责：列出可分析的 V8 源文件清单——首选 compile_commands.json（"真的会被
    #   编译的文件"，与分析单位天然一致），剥 ../../ 前缀、只要 .cc/.cpp/.c、
    #   排除第三方/构建目录/生成代码，去重排序返回。
    # 与 _run_checker_v8 的内联排除表相比多了 build/、out/、.git/ 三项（独立
    #   发现通道，口径更保守）。
    # 兜底：json 缺失/损坏 → _discover_v8_source_files_by_traversal 目录遍历。
    # 现状：src/ 内无调用方（_run_checker_v8 直接读 json 内联过滤），保留为
    #   独立发现工具。
    # 参数：target=V8 目标；返回：仓内相对路径的源文件列表。
    # ----------------------------------------------------------------------------
    def _discover_all_v8_source_files(self, target) -> List[str]:
        """
        Discover all V8 source files that can be analyzed.
        Uses compile_commands.json to find all files that are actually compiled.

        Returns:
            List[str]: List of relative source file paths
        """
        source_files = []  # 结果清单
        compile_commands_path = os.path.join(  # 编译数据库路径（x64.release 硬编码，注意与 _run_checker_v8 可配 arch 不同）
            target.repo.working_dir, "out/x64.release/compile_commands.json"
        )

        if os.path.exists(compile_commands_path):
            try:
                logger.info("Reading compile_commands.json to discover V8 source files")
                with open(compile_commands_path, "r") as f:
                    commands = json.load(f)

                # Extract all source files from compile commands
                for cmd in commands:  # 逐条目抽 file 字段
                    file_path = cmd.get("file", "")
                    if file_path:
                        # V8 uses ../../ prefix in compile_commands.json
                        if file_path.startswith("../../"):
                            clean_path = file_path[6:]  # Remove ../../ —— 剥构建目录前缀
                        else:
                            clean_path = file_path

                        # Only include C++ source files
                        if clean_path.endswith((".cc", ".cpp", ".c")):  # C/C++ 源（同 run 版口径）
                            # Filter out third-party and build-generated files
                            if not any(  # 排除表（比 run 版多 build//out//.git/）
                                exclude in clean_path
                                for exclude in [
                                    "third_party/",
                                    "buildtools/",
                                    "build/",
                                    "out/",
                                    ".git/",
                                    "gen/",
                                    # Skip some very large or problematic directories
                                    "tools/v8_gypfiles/",
                                ]
                            ):
                                source_files.append(clean_path)

                # Remove duplicates and sort
                source_files = sorted(list(set(source_files)))  # set 去重 + 字典序排序（结果可复现）
                logger.info(
                    f"Discovered {len(source_files)} V8 source files from compile_commands.json"
                )

                # Log some examples
                if source_files:  # 抽 5 条样例日志，便于人工核对口径
                    logger.info(f"Example files: {source_files[:5]}")
                    if len(source_files) > 5:
                        logger.info(f"... and {len(source_files) - 5} more files")

                return source_files

            except Exception as e:  # json 损坏 → 落入目录遍历兜底
                logger.error(f"Failed to read compile_commands.json: {e}")

        # Fallback: manually discover source files by walking directories
        logger.info("Falling back to directory traversal for source file discovery")
        return self._discover_v8_source_files_by_traversal(target)

    # ----------------------------------------------------------------------------
    # _discover_v8_source_files_by_traversal（V8 源文件发现 · 目录遍历兜底）
    # 职责：compile_commands.json 不可用时，rglob 扫 src/test/samples 三个目录
    #   的 .cc/.cpp/.c，按子串排除表过滤，去重排序；上限 1000 个文件防分析
    #   过载（排序后截前 1000，截断可复现）。
    # 与 json 通道的本质差异：遍历拿到的是"存在的文件"而非"被编译的文件"，
    #   可能混入未参与构建的源（没有编译命令可复刻，分析会失败）——故仅为兜底。
    # ----------------------------------------------------------------------------
    def _discover_v8_source_files_by_traversal(self, target) -> List[str]:
        """
        Fallback method to discover V8 source files by walking the directory tree.

        Returns:
            List[str]: List of relative source file paths
        """
        source_files = []  # 结果清单
        repo_root = Path(target.repo.working_dir)  # V8 仓根

        # Define directories to search and exclude patterns
        search_dirs = ["src", "test", "samples"]  # 只搜三个第一方目录
        exclude_patterns = [  # 路径子串排除表（比 json 版多 node_modules/__pycache__）
            "third_party",
            "buildtools",
            "build",
            "out",
            ".git",
            "gen",
            "node_modules",
            "__pycache__",
        ]

        logger.info(f"Searching for V8 source files in: {search_dirs}")

        for search_dir in search_dirs:
            search_path = repo_root / search_dir
            if not search_path.exists():  # 目录不存在（如精简 checkout）→ 跳过
                continue

            for file_path in search_path.rglob("*.cc"):  # 递归 glob .cc（V8 主源码后缀）
                # Convert to relative path
                relative_path = file_path.relative_to(repo_root)  # 转仓内相对路径
                relative_str = str(relative_path)

                # Skip excluded patterns
                if any(pattern in relative_str for pattern in exclude_patterns):  # 子串排除
                    continue

                source_files.append(relative_str)

            # Also include .cpp and .c files
            for ext in ["*.cpp", "*.c"]:  # 补扫 .cpp/.c（V8 里数量少）
                for file_path in search_path.rglob(ext):
                    relative_path = file_path.relative_to(repo_root)
                    relative_str = str(relative_path)

                    if any(pattern in relative_str for pattern in exclude_patterns):
                        continue

                    source_files.append(relative_str)

        # Remove duplicates and sort
        source_files = sorted(list(set(source_files)))  # 去重排序
        logger.info(f"Discovered {len(source_files)} V8 source files by traversal")

        # Limit the number of files to avoid overwhelming analysis
        max_files = 1000  # Reasonable limit for analysis —— 上限：防一次性塞爆分析管线
        if len(source_files) > max_files:
            logger.warning(
                f"Too many files ({len(source_files)}), limiting to first {max_files}"
            )
            source_files = source_files[:max_files]  # 截前 1000（排序后确定性截断）

        return source_files

    # ----------------------------------------------------------------------------
    # _generate_command（Linux 侧 scan-build 命令前缀生成器——§3.1.4 差分验证
    #   与 §3.2 全库/对象级扫描共用的命令骨架）
    # 输出形如：`PATH=<llvm>/bin:$PATH <llvm>/bin/scan-build --use-cc=clang
    #   -load-plugin <llvm>/lib/<Name>Plugin.so -enable-checker custom.<Name>Checker
    #   + _default_args（六连 -disable-checker / -maxloop 4 / -o ...）`。
    # 调用方把任意 make 命令接在末尾（对象级目标 / olddefconfig / 全树 -jN），
    # scan-build 拦截被包裹 clang 的每次编译跑 CSA——本文件前半 validate/run
    # 两条 Linux 路径的 comd_prefix 全部出自这里。
    # 参数：no_output=True 剔除 -o 对（调用方要换成自己的报告目录，Linux 扫描
    #   版 _run_checker_linux 即此用法）；plugin_names 给出则逐个
    #   -load-plugin + -enable-checker（多 checker 分组扫描的入口参数，与
    #   build_checker_group 配套）。
    # 坑：docstring 里残留 target_type 形参说明，实际签名已无此参数（文档漂移）。
    # ----------------------------------------------------------------------------
    def _generate_command(self, no_output=False, plugin_names=None):
        """
        Generate the command to run the analysis.

        Args:
            no_output (bool): If True, suppress the output file generation.
            plugin_names (list): List of plugin names to enable.
            target_type (str): The type of target ('v8' or None for default).
        Returns:
            str: The command to run the analysis.
        """
        llvm_build_dir = (self.backend_path / "build").absolute()  # 自编 LLVM build 目录（绝对路径）
        comd = f"PATH={llvm_build_dir}/bin:$PATH "  # 前置 PATH 注入：保证 make 内被调 clang 用自编版本
        comd += f"{llvm_build_dir}/bin/scan-build --use-cc=clang "  # scan-build 包裹器 + 指定 CC
        if plugin_names:  # 多 plugin 模式：逐个加载+启用（分组扫描基建）
            for plugin_name in plugin_names:
                comd += f"-load-plugin {llvm_build_dir}/lib/{plugin_name}Plugin.so "
                comd += f"-enable-checker custom.{plugin_name}Checker "
        else:  # 默认单 checker：SAGenTest 命名约定
            comd += f"-load-plugin {llvm_build_dir}/lib/SAGenTestPlugin.so "
            comd += "-enable-checker custom.SAGenTestChecker "

        # Use appropriate arguments based on target type
        args_to_use = self._default_args  # 恒用 Linux 参数表（V8 走 clang++ --analyze，不经此函数）
        for arg_name, arg_value in args_to_use:  # 逐对拼 "-key value"
            if no_output and arg_name == "-o":  # no_output：跳过 -o 对（调用方自行追加 -o <dir>）
                continue
            comd += f"{arg_name} {arg_value} "

        return comd

    # ----------------------------------------------------------------------------
    # _generate_command_group（多 checker 分组扫描命令生成，fork 增量 · WIP）
    # 与 _generate_command 的差异：① 默认必传 plugin_names——组内全部 plugin 逐个
    #   -load-plugin + -enable-checker，一次 scan-build 同时跑 N 个合成 checker；
    #   ② output_dir 参数：-o 可换成调用方目录（默认表的 tmp/... 被覆盖）。
    # 现状：FIXME 自认 "not implemented yet"，且 src/ 内无调用方（checker_scan.py
    #   仍是单 checker 逐对象循环）——与 build_checker_group 同为分组扫描的
    #   未接线基建（论文 §3.2 全库扫描实际按 checker 分组进行，此为其工程化方向）。
    # ----------------------------------------------------------------------------
    def _generate_command_group(
        self, no_output=False, plugin_names=None, output_dir=None
    ):
        """
        [WIP] Generate the command to run analysis with multiple checkers.

        Args:
            no_output (bool): If True, suppress the output file generation.
            plugin_names (list): List of plugin names to enable.
            output_dir (str): Custom output directory for reports.
        Returns:
            str: The command to run the analysis.
        """
        # FIXME: This is not implemented yet —— 组扫描通道整体未接线（见上）

        llvm_build_dir = (self.backend_path / "build").absolute()
        comd = f"PATH={llvm_build_dir}/bin:$PATH "
        comd += f"{llvm_build_dir}/bin/scan-build --use-cc=clang "  # 同款 scan-build 前缀

        # Load all checker plugins
        if plugin_names:  # 组模式：全部 plugin 依次挂载启用
            for plugin_name in plugin_names:
                comd += f"-load-plugin {llvm_build_dir}/lib/{plugin_name}Plugin.so "
                comd += f"-enable-checker custom.{plugin_name}Checker "
        else:  # 未给名单 → 退化为单 checker 默认名（与 _generate_command 一致）
            comd += f"-load-plugin {llvm_build_dir}/lib/SAGenTestPlugin.so "
            comd += "-enable-checker custom.SAGenTestChecker "

        # Add arguments, with custom output directory if specified
        for arg_name, arg_value in self._default_args:  # 参数表逐对拼接，-o 特殊处理
            if no_output and arg_name == "-o":  # no_output：跳过默认 -o
                continue
            if arg_name == "-o" and output_dir:  # 给了自定义目录 → 覆盖默认报告路径
                comd += f"{arg_name} {output_dir} "
            else:  # 其余参数原样
                comd += f"{arg_name} {arg_value} "
        return comd

    # ----------------------------------------------------------------------------
    # get_num_bugs（§3.1.4 差分验证的计数器：从 scan-build 输出解析 bug 总数）
    # 正则 r": (\d+) bug(s?) found" 抓结尾统计行 "scan-build: N bug(s) found."
    #   的数字（group(1)=数字捕获组；bug(s?) 兼容单复数写法）。
    # 失败路径：统计行缺失时 re.search 返回 None → AttributeError 被宽泛的
    #   except Exception 捕获，打印错误并按 0 处理——宽恕式解析，输出格式漂移
    #   不至于崩掉整轮差分验证。
    # 静态方法：本文件前半 _validate_checker_linux / _run_checker_linux 的
    #   N_buggy / N_patched 计数全部出自这里。
    # ----------------------------------------------------------------------------
    @staticmethod
    def get_num_bugs(content: str) -> int:
        try:
            num_bugs = int(re.search(r": (\d+) bug(s?) found", content).group(1))
        except Exception:
            print("Error: Couldn't extract number of bugs from output.")
            num_bugs = 0
        return num_bugs

    # ----------------------------------------------------------------------------
    # get_objects_from_report（报告 → 内核对象文件映射，§3.2 triage 侧工具）
    # 职责：从一条蒸馏后的 markdown 报告里抽出涉及的 .c 源文件并映射为对象路径
    #   ——checker_refine.py 的 triage 流程用它回填 ReportData.report_objects，
    #   判为 FP 的报告对应对象即 refinement agent 要重点修的方向。
    # 三步：① 正则 r"File:\| (.*).c" 抓报告头 "File:| path/to/foo.c"（贪婪 .*
    #   不吃 .c 后缀，随后手工补回）；② 绝对化 + 剥内核仓根前缀得仓内相对路径；
    #   ③ target.get_object_name 做 .c→.o 映射（Linux 目标的对象命名规则）。
    # 坑：FIXME 自认剥前缀的 replace 可能误伤（target_path 作为子串出现在路径
    #   其他位置时）；加尾 "/" 只能防"兄弟目录同名前缀"这一种。
    # ----------------------------------------------------------------------------
    @staticmethod
    def get_objects_from_report(report: str, target: TargetFactory):
        """
        Get the objects from the report.

        Args:
            report (str): The report to extract objects from.
            target (TargetFactory): The target to be tested.

        Returns:
            list: List of objects found in the report.
        """
        # Find `File:| XXX.c`
        pattern = r"File:\| (.*).c"  # 报告头文件行（html2text 转出的 markdown 形态）
        matches = re.findall(pattern, report)  # 全部命中（一条报告可涉多个文件）
        # Filter out non-c files
        matches = [match + ".c" for match in matches]  # 正则没吃 .c 后缀，手工补回
        matches = [Path(match).absolute().resolve().as_posix() for match in matches]  # 绝对化+解析符号链接+posix 化
        # Delete the prefix linux path
        # FIXME: This could be wrong
        target_path = Path(target.repo.working_dir).absolute().resolve().as_posix()  # 内核仓根（同款解析）
        target_path += "/"  # 尾斜杠：防误剥"前缀同名的兄弟目录"
        matches = [match.replace(target_path, "") for match in matches]  # 剥仓根 → 仓内相对路径

        # Replace .c with .o
        matches = [target.get_object_name(match) for match in matches]  # 目标侧映射：.c → .o 对象路径
        return matches

    # ----------------------------------------------------------------------------
    # extract_reports（论文 §3.2 Checker Refinement 的报告蒸馏 + 采样入口，
    #   抽象接口 extract_reports 的 CSA 实现；本文件管线的收官函数）
    # 流程（对照论文 §3.2 "全库扫描 → 报告蒸馏（只留 relevant lines + trace
    #   path）→ triage agent 逐报告判定 FP → refinement"）：
    #   ① 报告根下可能有多轮扫描的时间戳子目录——按创建时间（st_ctime）排序
    #      取最新一轮；
    #   ② 结构兼容：先按 Linux scan-build 扁平结构 glob *.html，没有再按 V8
    #      的 */*.html（每源文件一子目录 + _create_v8_report_softlinks 软链层）；
    #   ③ 每份报告：HTML → html2text 转 markdown → remove_text_section 蒸馏
    #      （删 "Annotated Source Code" 大段源码、Bug Summary 改措辞、附关键
    #      源码行——即论文"只留 relevant lines + trace path"）；按报告头 File:|
    #      行提取源文件名作聚类键，落盘 <output>/<文件名>-<报告ID>.md 并包成
    #      ReportData（triage 结论与对象列表由 refine 侧回填）；上限 max_num 条；
    #   ④ random.seed(seed) 固定种子后按聚类键采样 sampled_num 条（每簇取第
    #      一条），交 checker_refine 的 triage agent——论文"采样 5 条报告判 FP"。
    # 参数语义（论文锚点）：
    #   sampled_num=5 —— 采样送 triage 的报告数；即论文 plausible 判据"采样
    #     5 条中 FP ≤ 1"里的 5（global_config.max_fp_reports_for_refinement
    #     默认也是 5）；
    #   stop_num=5 —— 报告总数低于它直接返回 None（上层 checker_refine 配合
    #     "total_report ≤ 10 即 perfect" 短路，对应论文总报告数阈值思想）；
    #     开头 stop_num=max(sampled_num, stop_num) 保证停止数不小于采样数；
    #   max_num=100 —— 蒸馏处理条数上限（防超大报告目录拖慢 refine 循环）；
    #   seed —— 采样种子：refine 首轮 0，后续轮用 attempt_id（多轮采到不同样本）。
    # 返回：(采样报告列表 or None, 总报告数)；返回 None 表示报告不足/无报告。
    # ----------------------------------------------------------------------------
    @staticmethod
    def extract_reports(
        report_dir, output_dir, sampled_num=5, stop_num=5, max_num=100, seed=0
    ) -> Tuple[Optional[List[ReportData]], int]:
        """
        Extract reports from the report directory and process them into markdown files.
        """
        report_dir = Path(report_dir)
        stop_num = max(sampled_num, stop_num)  # 停止数至少=采样数（否则永远凑不齐采样量）

        # Sort the report dir by time
        report_dir_list = sorted(  # 一级子目录按创建时间排序（每轮扫描一个时间戳目录）
            [x for x in report_dir.iterdir() if x.is_dir()],
            key=lambda x: x.stat().st_ctime,
        )
        if not report_dir_list:  # 连扫描目录都没有 → (None, 0)
            logger.error("No report found!")
            return None, 0
        clustered_report_dir = defaultdict(list)  # {聚类键(源文件名): [ReportData]}——同文件多报告聚一簇

        # The latest report dir
        report_dir = report_dir_list[-1]  # 只处理最新一轮扫描

        report_tmp_dir = Path(output_dir)  # 蒸馏后 markdown 的输出目录
        report_tmp_dir.mkdir(parents=True, exist_ok=True)

        # Check if this is V8-style subdirectory structure or traditional flat structure
        report_html_list = list(report_dir.glob("*.html"))  # 先按 Linux scan-build 扁平结构找

        # If no HTML files directly in report_dir, check subdirectories (V8 structure)
        if not report_html_list:
            # Look for HTML files in subdirectories (e.g., src_objects_objects_cc/)
            report_html_list = list(report_dir.glob("*/*.html"))  # V8 结构：每源文件一子目录
            if report_html_list:
                logger.info(f"Found V8-style report structure with subdirectories")

        num_reports = len(report_html_list)
        if num_reports < stop_num:  # 报告太少 → 不值得 triage，返回 None（上层据此走 perfect 短路）
            logger.warning(f"< {stop_num} reports!")
            return None, num_reports

        max_len = min(max_num, num_reports)  # 实际蒸馏量 = 上限与报告数取小
        # Filename pattern example: `File:| drivers/video/backlight/qcom-wled.c`
        filename_pattern = re.compile(r"File:\| (.+)")  # 报告头源文件行（聚类键来源）
        for report_html in report_html_list[:max_len]:  # —— 蒸馏循环（§3.2 报告蒸馏）——
            html_content = report_html.read_text()  # 读原始 HTML（remove_text_section 还要从它抽源码行）
            md_content = html2text(html_content)  # HTML → markdown（LLM 友好形态）
            # This is specific to the report format
            md_content = remove_text_section(md_content, html_content)  # 蒸馏：删 Annotated Source Code 大段，替换 Bug Summary 措辞并附关键源码
            filename = filename_pattern.search(md_content)
            if filename:
                filename = filename.group(1)  # 命中：取文件路径作聚类键
            else:
                filename = "default"  # 未命中（报告头格式漂移）→ 归入 default 簇

            filename = str(Path(filename).resolve())  # 绝对化（各种相对路径形态在此归一）
            filename = (  # 安全化：路径分隔符与 .c/.h 扩展名全换掉，作文件名前缀
                filename.replace("/", "_").replace(".c", "").replace(".h", "").strip()
            )
            id_name = f"{filename}-{report_html.stem}"  # 报告 ID = <文件名>-<report-XXXXXX stem>（全局唯一）
            report_md = report_tmp_dir / (id_name + ".md")  # 蒸馏产物路径
            report_md.write_text(md_content)  # 落盘——triage agent 的输入即这些 md

            report_data = ReportData(  # 数据模型：triage 结论（report_triage）与对象（report_objects）由 refine 侧回填
                report_id=id_name,
                report_content=md_content,
                report_triage="",
                report_objects=[],
            )
            clustered_report_dir[filename].append(report_data)  # 入簇

        random.seed(seed)  # 固定种子：同 attempt 采样可复现；跨 attempt 换种子采到不同样本
        # Sample the reports
        filtered_keys = []  # 过滤后的候选簇键（排除头文件簇）
        sample_size = min(sampled_num, len(clustered_report_dir))  # 实际采样数（簇不够就有多少采多少）
        logger.warning(f"Sample size: {sample_size} by seed {seed}")

        for key in clustered_report_dir.keys():
            if any(pattern in key for pattern in ["_include_"]):  # 头文件报警（键含 _include_ 路径段）无对应可分析对象，排除
                # We don't want to sample the include files
                continue
            filtered_keys.append(key)

        if len(filtered_keys) < sample_size:  # 排除后不够采 → 从被排除键里随机补齐
            logger.warning(f"Not enough ({sample_size - len(filtered_keys)}) keys")
            other_keys = [
                key for key in clustered_report_dir.keys() if key not in filtered_keys
            ]
            filtered_keys.extend(
                random.sample(other_keys, sample_size - len(filtered_keys))
            )

        selected_keys = random.sample(filtered_keys, sample_size)  # 无放回随机采样 sampled_num 个簇
        reports = []
        for key in selected_keys:
            reports.append(clustered_report_dir[key][0])  # 每簇取第一条（同文件多报告只送一条，簇间多样性优先）
        return reports, len(clustered_report_dir)  # (采样报告, 总簇数)——上层以总数判 perfect/plausible

    # ----------------------------------------------------------------------------
    # _generate_unique_checker_name_static：_generate_unique_checker_name 的
    #   @staticmethod 镜像——逻辑逐行同款（去 KN- 前缀→非法字符换 _→字母开头
    #   补 Checker_ 前缀→截 30 字符→空名兜底 SAGenTest）。docstring 自述
    #   "for use in attribution"：供归因脚本等拿不到 backend 实例的场景复算
    #   同一 checker 命名（同一 checker_id 两处必须得出同一名字）；
    #   src/ 内暂无调用方。
    # ----------------------------------------------------------------------------
    @staticmethod
    def _generate_unique_checker_name_static(checker_id: str) -> str:
        """Static version of _generate_unique_checker_name for use in attribution."""
        name = checker_id.replace("KN-", "").replace("-", "_")  # 去 KN- 前缀；连字符转下划线
        name = re.sub(r"[^a-zA-Z0-9_]", "_", name)  # 其余非标识符字符一律换 _
        if name and not name[0].isalpha():  # 非字母开头 → 补 Checker_ 前缀
            name = f"Checker_{name}"
        if len(name) > 30:  # 截长到 30 字符
            name = name[:30]
        return name or "SAGenTest"  # 空名兜底回默认名
