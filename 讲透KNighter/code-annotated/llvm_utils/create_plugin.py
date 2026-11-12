# Purpose: Create a Clang static analyzer plugin based on SampleAnalyzer.
#
# Uasge: Copy this python script to the clang/lib/Analysis/plugins/ directory and run it.
# cd /path/to/clang/lib/Analysis/plugins/
# python3 ./create_plugin.py [PLUGIN_NAME] (No need to add "Checker"/"Plugin" suffix)
#
# =============================================================================
# 【模块定位】LLVM/Clang CSA（Clang Static Analyzer）插件脚手架生成器：在一个已
#   编译好的 LLVM 源码树的 plugins/ 目录下，为新 checker 生成整套可编译的 plugin
#   骨架——<NAME>Handling/ 目录 + CMakeLists.txt + <NAME>Checker.cpp（占位骨架）
#   + <NAME>Checker.exports（导出符号清单）。
#
# 【论文映射】KNighter 论文 §3.1 Algorithm 1 Stage 3（Implementation + Syntax
#   Repair，速查卡 §3.1.3）的编译基础设施：plan2checker 产出的 checker.cpp 必须
#   编译成 clang plugin（.so）才能被 CSA 加载去扫代码库（"CSA 集成：编译 checker
#   为 plugin、扫描、报告解析"）。本脚本负责在 LLVM 源码树里"挖好坑"（plugin 目录
#   + CMake 注册），随后 csa.py 把 LLM 生成的真实 checker 代码写进坑里再触发编译。
#
# 【管线角色】上游：scripts/setup_llvm.py（搭建 LLVM 环境时先跑一次
#   `create_plugin.py SAGenTest` 做自检，并把 utility.{h,cpp} 拷进 Clang 源码树）；
#   日常消费方：src/backends/csa.py::_create_group_plugin_directories——每个新
#   checker 调 `python3 create_plugin.py <checker_name>`，失败则 fallback 到
#   _create_plugin_directory_manually（内容等价的手工实现，两边格式刻意保持一致）。
#
# 【关键坑】① 脚本内部写死相对路径 "./"（必须在 plugins/ 目录下运行，完整路径
#   只存在于注释里）；② 生成的目录名固定加 "Handling" 后缀，csa.py 侧约定相同；
#   ③ create_plugin_files() 没有 return 语句（返回 None），主流程
#   `if not res: exit(1)` 恒触发——三件套其实已全部生成，但退出码恒为 1、
#   "Finish creation!" 永不打印，因此 csa.py 侧实际总走 manual fallback（幂等
#   无害，见 src/backends/csa.py L255-L279）；④ 新增 plugin 后必须重新 cmake 整
#   个 Clang 工程再编译（文件尾注释，对应 csa.py::_regenerate_cmake_build_system）；
#   ⑤ 首行 "Uasge" 为原仓 typo，按"只增注释不动代码"铁律保留不改。
# =============================================================================

import argparse
import os


# Update the main CMakeLists.txt file to include the plugin directory
# ↑ 原注释（保留）
# 职责：把 add_subdirectory(<NAME>Handling) 插进 plugins/ 目录的主 CMakeLists.txt，
#   让新 plugin 子目录纳入整体构建；幂等——已注册过则直接视为成功。
# 参数：无（直接读模块级全局 PLUGIN_NAME——脚本式写法，作为模块 import 会 NameError，
#   只能当 __main__ 脚本跑）
# 返回：bool——True=注册成功或本已存在；False=找不到主 CMake 文件/找不到 endif() 行
def update_main_cmake():
    # main_cmake_path = os.path.join('clang', 'lib', 'Analysis', 'CMakeLists.txt')
    main_cmake_path = os.path.join("./", "CMakeLists.txt")  # 约定本脚本已被拷贝到 plugins/ 下运行，目标就是当前目录的 plugins/CMakeLists.txt（上一行完整路径为历史写法）
    if not os.path.exists(main_cmake_path):  # 找不到主 CMake 文件：多半是运行目录不对（没在 plugins/ 下）
        print(f"Failed to find the main CMakeLists.txt file: {main_cmake_path}")
        return False

    with open(main_cmake_path, "r") as f:  # 整文件按行读入（保留行结构，稍后按行号插入）
        lines = f.readlines()
    cmake_content = [line.strip() for line in lines]  # 逐行去首尾空白生成"成员资格比较用"的副本（strip 后 in 判断，与逐字比较区分）

    add_subdirectory_line = f"add_subdirectory({PLUGIN_NAME}Handling)"  # 要插入的 CMake 指令：把 <NAME>Handling 子目录纳入构建
    if (  # 幂等检查：两种写法（带/不带 Handling 后缀）都没注册过才真正插入
        add_subdirectory_line not in cmake_content
        and f"add_subdirectory({PLUGIN_NAME})" not in cmake_content  # 兼容历史的不带后缀写法
    ):
        for i in range(len(lines)):  # 按行扫描，找第一个 "endif()" 行——plugins/CMakeLists.txt 的惯例结构是 if(...) 包住所有示例 plugin 再 endif()
            if "endif()" in lines[i]:
                lines.insert(i, f"  {add_subdirectory_line}\n")  # 在 endif() 之前插入（缩进两空格，与 if 块内条目对齐）；insert(i,·) 即插到原第 i 行前面
                break  # 只插一次
        else:  # for-else：循环正常跑完（没被 break，即整个文件没有 endif()）才进入
            print("Failed to find the 'endif()' line!")
            return False
        # Update.
        with open(main_cmake_path, "w") as file:  # 回写修改后的 CMakeLists.txt（上方原注释"# Update."保留）
            file.writelines(lines)
        print(f"Updated the main CMakeLists.txt: {PLUGIN_NAME}Handling")
        return True
    else:
        print("Main CMakeLists.txt already includes the plugin directory setting!")  # 已注册——幂等地视为成功
        return True


# Create the plugin directory and files
# ↑ 原注释（保留）
# 职责：创建 <NAME>Handling/ 目录及三件套：
#   ① CMakeLists.txt（构建脚本，MODULE plugin 编译配置）
#   ② <NAME>Checker.cpp（最小可编译的 checker 占位骨架，随后被 csa.py 写入的
#      LLM 生成代码覆盖/复用同名目录）
#   ③ <NAME>Checker.exports（动态库导出符号白名单）
# 注意：本函数无 return 语句（隐式返回 None）→ 主流程 `if not res: exit(1)` 恒触发，
#   见文件头【关键坑】③——文件已生成但脚本总以退出码 1 结束。
def create_plugin_files():
    if not os.path.exists(PLUGIN_PATH):  # 首次运行：创建 plugin 目录
        os.makedirs(PLUGIN_PATH)
        print(f"Mkdir: {PLUGIN_PATH}")
    else:  # 已存在也继续往下走：三件套会被重写，等价于幂等重建（csa.py 重试同一 checker 时依赖此行为）
        print(f"Already exist: {PLUGIN_PATH}")

    cmake_file = os.path.join(PLUGIN_PATH, "CMakeLists.txt")  # 三件套①的落盘路径
    cpp_file = os.path.join(PLUGIN_PATH, f"{PLUGIN_NAME}Checker.cpp")  # 三件套②：checker 源码占位
    exports_file = os.path.join(PLUGIN_PATH, f"{PLUGIN_NAME}Checker.exports")  # 三件套③：导出符号清单
    cpp_file_name = f"{PLUGIN_NAME}Checker.cpp"  # 供 CMake 引用的文件名（裸文件名形式，填进下方模板）
    exports_file_name = f"{PLUGIN_NAME}Checker.exports"  # 同上
    lib_name = f"{PLUGIN_NAME}Plugin"  # 编译产物名：lib<NAME>Plugin.so（make <NAME>Plugin 的目标名）

    # 创建 CMakeLists.txt 文件
    # ↑ 原注释（保留）。三件套①的内容（f-string 模板，${{...}} 转义为字面 ${...}）：
    #   · LLVM_LINK_COMPONENTS=Support：链接 LLVM Support 基础库；
    #   · LLVM_EXPORTED_SYMBOL_FILE：限定动态库只导出 .exports 列出的符号；
    #   · add_llvm_library(... MODULE BUILDTREE_ONLY ...) 是关键——MODULE 表示编成
    #     可动态加载的 plugin 模块（-analyzer-plugin 加载的 .so/.dylib）而非链进
    #     Clang 主库，BUILDTREE_ONLY 表示只在源码树内构建、不随 install 安装；
    #   · clang_target_link_libraries 链 clangAnalysis/clangAST/clangStaticAnalyzerCore/
    #     clangStaticAnalyzerFrontend 四个静态库，覆盖 CSA checker API 的全部依赖面。
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
    with open(cmake_file, "w") as f:
        f.write(cmake_content.strip())  # strip 掉 f-string 首尾的换行再落盘
    print(f"  Created: {cmake_file}")

    # 三件套③的内容：plugin 动态库对外只导出这两个 C 符号（缺一不可）：
    #   · clang_registerCheckers——CSA 加载 plugin 时调用的注册入口，checker 在
    #     这里登记进 CheckerRegistry（见下方 cpp 模板里的同名函数）；
    #   · clang_analyzerAPIVersionString——API 版本串，加载时与主程序做 ABI
    #     版本协商，不匹配则拒绝加载。
    exports_content = """
clang_registerCheckers
clang_analyzerAPIVersionString
"""
    with open(exports_file, "w") as f:
        f.write(exports_content.strip())
    print(f"  Created: {exports_file}")

    checker_name = f"{PLUGIN_NAME}Checker"  # C++ checker 类名基名（csa.py 侧 _replace_checker_name_in_code 用同样的 <NAME>Checker 约定改成唯一名）
    # 三件套②的内容：最小可编译 checker 骨架——四要素齐全（Checker<check::PreCall>
    # 模板子类注册 checkPreCall 回调 + 匿名命名空间藏实现 + clang_registerCheckers
    # 注册入口 + API 版本串），保证"空坑也能编译过"，随后被 LLM 生成的真实
    # checker 代码替换。csa.py::_create_plugin_directory_manually 生成内容逐字符
    # 等价的文件，即本脚本的手工镜像。
    cpp_content = f"""
#include "clang/StaticAnalyzer/Core/BugReporter/BugType.h"
#include "clang/StaticAnalyzer/Core/Checker.h"
#include "clang/StaticAnalyzer/Core/PathSensitive/CheckerContext.h"
#include "clang/StaticAnalyzer/Frontend/CheckerRegistry.h"

using namespace clang;
using namespace ento;

namespace {{
/*The checker callbacks are to be decided.*/
class {checker_name} : public Checker<check::PreCall> {{
  mutable std::unique_ptr<BugType> BT;

public:
  // Main Check Logic
  void checkPreCall(const CallEvent &Call, CheckerContext &C) const; // Tmp
}};
}} // end anonymous namespace


extern "C" void clang_registerCheckers(CheckerRegistry &registry) {{
  registry.addChecker<{checker_name}>(
      "custom.{checker_name}",
      "/*Description to be filled*/",
      "");
}}

extern "C" const char clang_analyzerAPIVersionString[] =
    CLANG_ANALYZER_API_VERSION_STRING;
"""
    with open(cpp_file, "w") as f:
        f.write(cpp_content.strip())
    print(f"  Created: {cpp_file}")
    # 无 return → 返回 None（文件头【关键坑】③的根源）


def parse_args():  # 命令行解析：唯一的必需位置参数 plugin_name（本文件无 docstring，说明全走 # 注释）
    parser = argparse.ArgumentParser(
        description="Create a Clang static analyzer plugin based on SampleAnalyzer."
    )
    parser.add_argument(  # 位置参数：plugin 基名（勿带 Checker/Plugin 后缀，脚本自动拼接）
        "plugin_name", type=str, help="The name of the plugin to create."
    )
    return parser.parse_args()


if __name__ == "__main__":
    # Uasge: python3 ./create_plugin.py RetvalNullDeref (No need to add "Checker" suffix)
    args = parse_args()  # 解析命令行（plugin_name 为必填位置参数，缺参 argparse 自行报错退出）
    # PLUGIN_DIR = 'clang/lib/Analysis/plugins'
    PLUGIN_DIR = "./"  # 约定运行目录=plugins/（上一行完整路径为历史写法），与 update_main_cmake 的 "./CMakeLists.txt" 呼应
    # 兜底值 "MyAnalyzer" 实际不可达：位置参数必填，只有显式传空串才会落到 or 右支
    PLUGIN_NAME = (
        args.plugin_name or "MyAnalyzer"
    )  # User defined plugin name, e.g., RetvalNullDeref or KernelUninitMem.
    # ↑ 原行尾注释（保留）
    PLUGIN_PATH = os.path.join(PLUGIN_DIR, f"{PLUGIN_NAME}Handling")  # 目标目录：<NAME>Handling/——"Handling" 后缀是本脚本与 csa.py 的共同约定（csa.py L72/L245 同款拼接）
    print(f"Start creating Clang Analyzer plugin: {PLUGIN_NAME}...")

    # Step 1
    res = update_main_cmake()  # 第一步：把 plugin 子目录注册进主 CMakeLists.txt（在第一个 endif() 前插 add_subdirectory）
    if not res:
        exit(1)  # 主 CMake 缺失/结构不符——硬失败

    # Step 2
    res = create_plugin_files()  # 第二步：生成目录三件套；因该函数返回 None，下一行 exit(1) 恒触发（文件头【关键坑】③）——csa.py 以退出码判失败后走 manual fallback，不依赖这里的成功路径
    if not res:
        exit(1)
    print("Finish creation!")  # 实际不可达（上一行恒退出）——保留原代码不改

# Note that: After adding a new plugin, we need to re-cmake the Clang project before compiling the plugin.
# ↑ 原尾注（保留）+ 中文补充：新增 plugin 后必须重新 cmake 整个 Clang 工程再 make，
#   因为 CMake 只在 re-configure 时才会发现新 add_subdirectory 的目录——这正是
#   csa.py::_regenerate_cmake_build_system 存在的原因（建完 plugin 目录必调）。
# cd build
# cmake -DLLVM_ENABLE_PROJECTS="clang;lld" -DLLVM_TARGETS_TO_BUILD=X86 -DCMAKE_BUILD_TYPE=Release -G "Unix Makefiles" ../llvm
# make {PluginName}Plugin -j24
