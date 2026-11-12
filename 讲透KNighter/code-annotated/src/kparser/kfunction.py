# =============================================================================
# 【模块定位】基于 tree-sitter 的函数提取器：从 C/C++ 源文件（语法树）中
#  定位全部 function_definition 节点，包装成携带"完整源码 + 函数名 + 起止
#  行号"的 KernelFunction 对象。
#
# 【论文映射】论文 §3.1.1 Bug Pattern Analysis："patch diff 之外还给 LLM
#  完整函数上下文"的直接实现——tools.get_function_codes 用本类把 patch 的
#  hunk 行号映射到"包含该行的完整函数"，函数源码（func.code）最终进入
#  pattern agent 的 prompt（速查卡"关键资产"：tree-sitter 提取 patch 涉及
#  的完整函数源码 → src/kparser/）。
#
# 【管线角色】上游 KParser（同目录 kparser.py）产出语法树；本模块把树节点
#  包装为富对象；下游 tools.get_function_codes → targets/factory.py 消费。
#  命名里的 K=Kernel 源自 Linux 内核起点，但语法是 tree-sitter-cpp（C 为
#  子集），故同一提取器也服务 fork 增量的 V8/Chromium 目标（上游 #16 即为
#  V8 兼容补的兜底，见 __find_name）。
#
# 【关键依赖与坑】
#  - 行号坐标系：get_line_numbers 返回 tree-sitter 的 0 基行
#    （start_point[0]），而 git diff hunk 头 "@@ -N," 是 1 基行——上游
#    tools.get_function_codes 的包含判定存在系统性 ±1 行边界误差（取舍保
#    留，注释版不动代码）。
#  - @dataclass 装饰但手写 __init__（只收 file_path/node 两参）：dataclass
#    不覆盖类体内显式定义的 __init__，自动生成的 __repr__/__eq__ 仍按全部
#    字段工作（Node 未定义 __eq__，按对象标识比较）。
#  - from_files 的多进程 Pool.map 需把含 Node（C 指针）的结果对象跨进程传
#    回，可行性取决于 py-tree-sitter 的序列化实现；主调用链
#    （tools.get_function_codes）只走单文件 from_file，不经过此入口。
#  - __is_function / from_file / from_files 均未标 @staticmethod
#    （__is_function 甚至没有 self 形参，只能经类名调用）——上游风格，
#    经类名调用均成立，保持原样。
# =============================================================================
from __future__ import annotations  # 延迟注解求值：类型标注不在定义期强制解析（上游风格保留）

from dataclasses import dataclass  # @dataclass：自动生成 __repr__/__eq__ 等（__init__ 被手写版覆盖，见文件头坑注）
from itertools import chain  # chain.from_iterable：把递归返回的多个列表摊平成单个迭代器
from multiprocessing import Pool  # from_files 的多进程批量入口（每文件一个任务）
from pathlib import Path  # 类型标注与路径处理

from tree_sitter import Node  # 语法树节点类型（用于类型标注与节点类型判断）

from .kparser import KParser  # 解析器：from_file 在未显式传入 parser 时按需构造（相对导入，同包内）

CURR = Path(__file__).parent  # 本模块目录（当前实现未再使用，保留作锚点）


# -----------------------------------------------------------------------------
# 内核/目标函数对象：一个 function_definition 语法树节点的富包装。
#
# 【字段】file_path 源文件路径 / node 原始树节点 / code 完整函数源码（UTF-8
#   文本，即喂给 LLM 的"完整函数上下文"）/ name 函数名 / start_line、
#   end_line 起止行（0 基，见文件头坑注）。
# 【构造】手写 __init__ 只要求 (file_path, node)，其余字段从 node 自举：
#   校验必须是 function_definition → 取源码文本 → 求函数名 → 记起止行。
# -----------------------------------------------------------------------------
@dataclass
class KernelFunction:
    file_path: Path  # 源文件路径（dataclass 字段声明；实际赋值在手写 __init__）
    node: Node  # 原始 tree-sitter 节点（code/name/行号的唯一事实来源）
    code: str  # 完整函数源码文本（node.text 直接解码）
    name: str  # 函数名（__find_name 递归求出；宏生成声明可能为 ""）

    def __init__(
        self,
        file_path: Path,
        node: Node,
    ):  # 手写两参构造：dataclass 不会覆盖类体内显式定义的 __init__
        self.file_path = file_path  # 记录来源文件
        self.node = node  # 保留原始节点（后续可再做树查询）

        if node.type != "function_definition":  # 防御式校验：只接受函数定义节点
            raise ValueError("Node is not a function definition")  # 传错节点类型立即报错
        self.code = node.text.decode("utf-8")  # 节点文本 = 函数完整源码（§3.1.1 完整函数上下文的载体）
        self.name = self.__find_name(node)  # 私有方法递归求函数名（可能返回 ""，见下）
        self.start_line = node.start_point[0]  # 起始行：tree-sitter point=(row, col)，row 为 0 基
        self.end_line = node.end_point[0]  # 结束行（0 基；闭区间语义，供包含判定）

    # -------------------------------------------------------------------------
    # 递归求函数名：应对 C/C++ 声明符的嵌套形态。
    # 【策略】看 function_definition 的直接子节点类型：
    #   - function_declarator（普通函数 int foo(...)）→ 在其子节点里找
    #     identifier（即函数名）；找不到返回 ""（上游 #16 为 V8 目标补的
    #     兜底：宏生成的声明可能没有 identifier 子节点，此前会失配）。
    #   - pointer_declarator（带指针的声明符链，如函数指针风格定义）→
    #     递归进入该子树继续找。
    #   - 其余 → ""。
    # 【参数】node: Node —— 起始为 function_definition 本身
    # 【返回】str —— 函数名；无法识别时 ""（由上层 prompt/WHOLE_FILE 兜底）
    # -------------------------------------------------------------------------
    def __find_name(self, node: Node) -> str:
        children = [c for c in node.children]  # 直接子节点列表（列表化便于按下标取）
        types = [c.type for c in children]  # 对应的节点类型列表（与 children 同序）
        if "function_declarator" in types:  # 普通函数声明符分支
            decl = children[types.index("function_declarator")]  # 取第一个 function_declarator 子节点
            for c in decl.children:  # 在声明符子树内扫函数名
                if c.type == "identifier":  # identifier 节点即函数名
                    return c.text.decode("utf-8")
            # If no identifier found, return empty string
            return ""  # 上游 #16（run_checker for v8）新增：宏生成声明无 identifier 时的兜底
        elif "pointer_declarator" in types:  # 指针声明符分支：递归下钻
            return self.__find_name(children[types.index("pointer_declarator")])
        else:
            return ""  # 两种声明符都没有（非典型形态）→ 空名

    # -------------------------------------------------------------------------
    # 判定节点是否是"带正常声明符的函数定义"。
    # function_definition 但既无 function_declarator 又无 pointer_declarator
    # 直接子节点的（宏展开产物等），不当作可提取函数。
    # 【注意】定义漏了 self 形参——只能以 KernelFunction.__is_function(node)
    # 形式调用（上游风格，保持原样）。
    # -------------------------------------------------------------------------
    def __is_function(node: Node) -> bool:
        if node.type != "function_definition":  # 先看节点类型
            return False
        types = [c.type for c in node.children]  # 子节点类型清单
        return "function_declarator" in types or "pointer_declarator" in types  # 有任一声明符即认可

    def get_line_numbers(self) -> int:
        # 起止行二元组（0 基；tools.get_function_codes 用它做 hunk 包含判定，
        # 与 1 基 diff 行号之间存在 ±1 边界误差，见文件头坑注）。
        # 注：返回类型标注 int 实为 tuple——上游笔误，按"不动代码"铁律保留。
        return self.start_line, self.end_line

    # -------------------------------------------------------------------------
    # 【主入口】从单个文件（或给定子树）递归收集全部 KernelFunction。
    # 【参数】fpath 源文件 / node 起始节点（None=解析整个文件）/ rec_depth
    #   递归深度预算（防病态嵌套，30 层足够 C/C++）/ parser 复用的解析器
    #   （None=现场 new；递归时透传，避免反复 CDLL 加载语法库）。
    # 【返回】list[KernelFunction] —— 该文件/子树内所有函数定义
    # -------------------------------------------------------------------------
    def from_file(
        fpath: Path,
        node: Node = None,
        rec_depth: int = 30,
        parser: KParser = None,
    ) -> list[KernelFunction]:
        if rec_depth <= 0:  # 深度预算耗尽：放弃更深的子树（剪枝保护）
            return []

        if parser is None:  # 顶层调用（每文件一次）：构造解析器
            parser = KParser()
        if node is None:  # 未给起始节点 → 解析整个文件取根节点
            node = parser.parse_file(fpath)

        if KernelFunction.__is_function(node):  # 命中函数定义：包装后立即返回（递归终止条件之一）
            return [KernelFunction(fpath, node)]
        elif node.children is not None:  # 非函数但还有子节点：对每个孩子递归再摊平
            return list(
                chain.from_iterable(  # 把各子树的结果列表摊平成一层
                    [
                        KernelFunction.from_file(fpath, c, rec_depth - 1, parser)
                        for c in node.children
                    ]  # 每个子节点递归（深度 -1；parser 透传复用）
                )
            )
        else:
            return []  # 叶子节点且非函数定义：空

    # -------------------------------------------------------------------------
    # 多文件批量入口：multiprocessing Pool 并行跑 from_file。
    # 【参数】files 路径列表 / num_procs 进程数（默认 20）
    # 【注意】map 按文件分发任务，worker 内 from_file(fpath) 会各自 new
    #   KParser（每文件重新 CDLL 加载语法库）；且返回对象携带 Node（C
    #   指针），跨进程传输依赖 py-tree-sitter 的序列化行为——主调用链
    #   （tools.get_function_codes）未使用此入口（见文件头坑注）。
    # -------------------------------------------------------------------------
    def from_files(files: list[Path], num_procs: int = 20) -> list[KernelFunction]:
        with Pool(num_procs) as p:  # 进程池上下文（退出自动收拢）
            results = p.map(KernelFunction.from_file, files)  # 每文件一个任务 → list[list[KernelFunction]]
            return list(chain.from_iterable(results))  # 摊平为单层函数列表
