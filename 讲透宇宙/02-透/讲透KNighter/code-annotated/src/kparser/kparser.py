# =============================================================================
# 【模块定位】tree-sitter C++ 解析器的加载与薄封装：把 vendored 的
#  tree-sitter-cpp 语法库编译成共享库，对外提供 KParser.parse_file /
#  parse_code 两个"源码 → 语法树根节点"入口。
#
# 【论文映射】KNighter 论文 §3.1.1 Bug Pattern Analysis 的解析基础设施
#  （速查卡"关键资产"：tree-sitter 提取 patch 涉及的完整函数源码 →
#  src/kparser/）。调用链：本文件 KParser → kfunction.KernelFunction.
#  from_file（递归收集函数）→ tools.get_function_codes（hunk 行号 → 完整
#  函数源码）→ targets/factory.py（组 pattern agent 的 prompt）。语法选
#  tree-sitter-cpp 而非 tree-sitter-c：C 是 C++ 语法的子集，一套库同时
#  服务 Linux（.c/.h）与 fork 增量的 V8/Chromium（.cc）两类目标。
#
# 【管线角色】最底层解析原语：parse_file/parse_code 返回 tree-sitter Node
#  （语法树根节点 translation_unit），函数级语义由上层 KernelFunction 递归
#  挖掘；本模块不涉及 git/patch/LLM。
#
# 【关键依赖与坑】
#  - requirements.txt 钉死 tree-sitter==0.21.3：Language.build_library 在
#    0.22+ 已被移除、set_language 在新版被 language 属性取代——升级依赖
#    会直接破坏本文件（API 代际锚点）。
#  - import 即副作用：加载本模块就触发 build_library，用 C 编译器现场把
#    vendored 语法源码（parser.c + scanner.c）编成 build/my-languages.so；
#    首次 import 显著变慢，产物落在本文件同级 build/ 目录（源码未变时
#    重建很快跳过）。
#  - COMMON-ISSUES.md 记录的环境坑：部分编译器下 scanner.c:126 的
#    static_assert 报 "Error: undefined symbol: static_assert"，解法是把
#    vendored scanner.c 中该 static_assert 两行注释掉后重新触发构建
#    （改的是 vendored C 源，不属本仓 Python 代码）。
#  - get_language.restype = ctypes.c_void_p：把 C 函数返回值显式声明为
#    指针宽度，避免 ctypes 默认按 c_int 截断 64 位地址；Language(ptr,
#    "cpp") 是 0.21 版"直接喂原始指针"的构造姿势。
# =============================================================================
import ctypes  # dlopen 编译产物 my-languages.so，并取导出符号 tree_sitter_cpp 的函数指针
from pathlib import Path  # 构建产物与语法库源码都锚定在本文件同级目录（CURR）

from tree_sitter import Language, Node, Parser  # py-tree-sitter 0.21 API：Language 语言对象 / Node 树节点（本文件仅作类型标注）/ Parser 解析器

CURR = Path(__file__).parent  # kparser/ 目录：vendored 语法库源码与 build/ 产物的根锚点

# 模块级副作用（import 即执行）：把 vendored tree-sitter-cpp 语法源码编译为
# 共享库。首参是输出 .so 路径，次参是语法库源码目录列表——要支持更多语言
# 就向列表追加目录（当前只有 C++ 一门）。
Language.build_library(
    str(CURR / "build/my-languages.so"),  # 输出：kparser/build/my-languages.so（字符串化兼容 0.21 API）
    [str(CURR / "tree-sitter-cpp")],  # 输入：vendored 语法库目录（含 src/parser.c、src/scanner.c）
)


# -----------------------------------------------------------------------------
# C/C++ 源码解析器封装：加载共享库 → 取语言指针 → 绑定到 Parser 实例。
# 【实例化成本】每次 KParser() 都重新 CDLL 加载一次 .so（无缓存）；上层
#   KernelFunction 的递归路径通过透传同一 parser 实例规避重复加载（见
#   kfunction.py 的 from_file），但 tools.get_function_codes 的逐文件循环
#   仍会每文件新建一个实例。
# -----------------------------------------------------------------------------
class KParser:
    def __init__(self):
        # Load the shared library
        lib = ctypes.CDLL(str(CURR / "build/my-languages.so"))  # dlopen 上方模块级步骤产出的语法库

        # Get the language function pointer
        get_language = lib.tree_sitter_cpp  # 库导出的 C 符号：TSLanguage *tree_sitter_cpp(void)
        get_language.restype = ctypes.c_void_p  # 返回类型显式声明为 void*：保证 64 位指针不被默认 c_int 截断

        # Create language with pointer instead of path
        # 0.21 构造姿势：直接把 C 指针（此刻已是 Python int）+ 语言注册名交给
        # Language 构造；0.22+ 移除该姿势（requirements 钉 0.21.3 的主因之一）
        cpp_language = Language(get_language(), "cpp")  # "cpp" 是 py-tree-sitter 侧的语言注册名
        parser = Parser()  # 新建空解析器
        parser.set_language(cpp_language)  # 绑定 C++ 语法（0.21 API；新版改为 parser.language = lang）
        self.parser = parser  # 挂到实例上供 parse_file / parse_code 使用

    # -------------------------------------------------------------------------
    # 文件 → 语法树根节点。
    # 【坑】open() 文本模式用平台默认编码读取、再 encode 回 utf-8 字节：若
    #   源文件含非法字节，strict 解码会在此抛异常（上层 tools.
    #   get_function_codes 的整文件兜底分支负责接住这类失败）。
    # 【参数】fpath: Path —— 待解析的源文件
    # 【返回】Node —— 根节点（translation_unit），遍历交给上层
    # -------------------------------------------------------------------------
    def parse_file(self, fpath: Path) -> Node:
        source_code = open(fpath, "r").read()  # 整文件读入文本（默认编码，见坑注）
        tree = self.parser.parse(bytes(source_code, "utf8"))  # tree-sitter 输入必须 bytes：显式转 utf-8
        return tree.root_node  # 返回根节点

    # -------------------------------------------------------------------------
    # 内存字符串 → 语法树根节点（无需落盘；供直接解析代码片段的场景）。
    # 【参数】code: str —— C/C++ 源码文本
    # 【返回】Node —— 根节点
    # -------------------------------------------------------------------------
    def parse_code(self, code: str) -> Node:
        tree = self.parser.parse(bytes(code, "utf8"))  # 同 parse_file 的字节转换，输入来自内存
        return tree.root_node
