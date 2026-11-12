# =============================================================================
# 【模块定位】KNighter 的"分析目标"抽象工厂：把与具体代码库强耦合的四类操作——
#   ① checkout 到指定 commit 并准备好构建环境（checkout_commit）
#   ② 源文件名 → 构建系统对象(.o)名（get_object_name）
#   ③ bug-fix patch → 待分析对象列表（get_objects_from_patch）
#   ④ commit → Markdown 格式 patch 材料（get_patch）
# ——抽象成统一接口；Linux（kbuild，src/targets/linux.py）与 V8（gn/ninja，
#   src/targets/v8.py）两个子类各自落地。
#
# 【论文映射】本模块是论文两阶段管线的"目标侧地基"：
#   - get_patch() 是 §3.1.1 Bug Pattern Analysis 的输入组装器：把修复 diff 与
#     tree-sitter 提取的完整函数源码拼成 Markdown 喂给 pattern agent；
#   - checkout_commit()/get_objects_from_patch() 服务于 §3.1.4 Validation 的差分
#     验证：is_before=True checkout 到补丁父提交（=buggy 版本）扫 patch 涉及对象
#     得 N_buggy，is_before=False checkout 到补丁提交（=patched 版本）得 N_patched，
#     valid ⟺ N_buggy > N_patched 且 N_patched < T_valid(=50)；§3.2 全库扫描
#     同样依赖 checkout_commit 做构建准备；
#   - path_similarity() 供子类 get_object_name 消歧同名 .o 时复用（Jaccard）。
#
# 【管线角色】上游：src/global_config.py（读 linux_dir/v8_dir 配置实例化子类并
#   注入 _config["target"]）、src/main.py（CLI 入口）；下游：src/backends/csa.py
#   （差分验证/全库扫描时消费 checkout_commit、get_objects_from_patch、
#   get_object_name）与阶段一 pattern agent（消费 get_patch 产物）。
#
# 【依赖与坑】
#   - GitPython（git.Repo / git.exc.BadName）；src/tools.py 的
#     get_function_codes_with_config（tree-sitter 提取 patch 涉及函数的完整源码，
#     解析失败回退整文件、函数名带 WHOLE_FILE_ 前缀）与 truncate_large_file
#     （整文件截断到 500 行，防撑爆 LLM 上下文窗口）。
#   - 坑：类属性在 import 时求值——子类 _build_commands 会在加载模块时读入构建
#     命令日志文件（Linux 版约 1.7MB）常驻内存；
#   - 坑："buggy commit" 的定义 = 修复补丁的父提交（git 语法 commit_id^）。
# =============================================================================
import os                                    # path_similarity 用 os.sep 把路径切成组件
from abc import ABC, abstractmethod          # ABC + @abstractmethod：强制子类实现核心接口
from pathlib import Path                     # Path().resolve() 把路径规范化为绝对路径再比较
from typing import List                      # get_objects_from_patch 的返回类型注解 List[str]

import git                                   # GitPython：仓库对象封装（commit 解析/checkout/diff）

from tools import get_function_codes_with_config, truncate_large_file
# ↑ src/tools.py 提供的两个工具：
#   get_function_codes_with_config —— tree-sitter 提取 patch 涉及函数的完整源码
#     （§3.1.1 "完整函数源码" 的提供者，回退行为受 global_config 开关控制）；
#   truncate_large_file —— 整文件回退时截到 max_lines 行


# -----------------------------------------------------------------------------
# 目标抽象基类：子类 = Linux（论文主目标）/ V8（fork 增量，对应论文 §6
# Generability 的可迁移性实证）。设计意图：Algorithm 1 的各阶段（pattern/plan/
# implementation/validation）与 backends 完全不感知目标差异，所有目标特有知识
# （构建系统、对象命名规则、依赖管理）都封装在本类子类里。
# -----------------------------------------------------------------------------
class TargetFactory(ABC):
    """
    A class representing a Git repository.
    """
    # ↑ 原有 docstring 按铁律原样保留（docstring 是 AST 字符串节点，一个字节都不能动）

    _target_type = "generic"                 # 目标类型标识：子类覆写为 "linux"/"v8"；
                                             # __str__ 展示与 global_config 按 target_type
                                             # 选择装配哪个实例时都用到它
    _build_commands = None                   # 构建命令日志全文（类属性）：子类在类体里读
                                             # {linux,v8}-build-commands.txt 填充；是
                                             # get_object_name 反查 .o 路径的数据源

    # -----------------------------------------------------------------------------
    # 构造器：打开目标仓库。
    # 参数 repo_path：目标仓库工作树路径（Linux 内核 / V8 的 clone 目录，来自
    #               global_config 的 linux_dir/v8_dir 配置）。
    # 副作用：git.Repo() 会校验仓库合法性，路径无效立即抛 InvalidGitRepositoryError。
    # -----------------------------------------------------------------------------
    def __init__(self, repo_path: str):
        self.repo = git.Repo(repo_path)      # GitPython Repo 句柄：后续 checkout/diff 全走它

    # -----------------------------------------------------------------------------
    # 可读化输出（调试用）：一行打印目标类型 + 仓库工作树绝对路径。
    # -----------------------------------------------------------------------------
    def __str__(self):
        return f"Target Type: {self._target_type}, Repository Path: {self.repo.working_dir}"
                                             # working_dir = 仓库工作树根目录（绝对路径）

    # -----------------------------------------------------------------------------
    # 【抽象接口 1】checkout 到指定 commit 并把构建环境准备好。
    # 论文语义：§3.1.4 差分验证的环境切换动作——
    #   is_before=True  → checkout 到 commit_id^（父提交：bug 已引入、未修复 = buggy）
    #   is_before=False → checkout 到 commit_id（补丁已合入 = patched）
    # 参数：commit_id 目标提交；is_before 是否取父提交；**kwargs 透传目标特有参数
    #   （Linux: arch/olddefcmd；V8: arch/llvm_path/skip_v8_build）。
    # -----------------------------------------------------------------------------
    @abstractmethod
    def checkout_commit(self, commit_id: str, is_before: bool = False, **kwargs):
        """
        Checkout a specific commit in the repository.

        Args:
            commit_id (str): The commit ID to checkout.
            is_before (bool): Whether to checkout before the commit.
            **kwargs: Additional arguments for the checkout command.
        """
        pass                                 # 抽象方法体：仅占位，构建流程由子类实现

    # -----------------------------------------------------------------------------
    # 【抽象接口 2】源文件名 → 构建对象(.o)名（静态方法）。
    # 论文语义：CSA 以翻译单元为分析单位，Linux 侧用 kbuild 的 .o、V8 侧用 ninja
    # 的 obj/ 路径来锁定"这个 .c 编译成哪个对象"；扫描命令据此定位分析目标。
    # 参数 file_name：patch 中的源文件路径。返回：对象路径字符串。
    # -----------------------------------------------------------------------------
    @staticmethod
    @abstractmethod
    def get_object_name(file_name: str) -> str:
        """
        Get the object name from a file name.

        Args:
            file_name (str): The name of the file.

        Returns:
            str: The object name.
        """
        raise NotImplementedError("Subclasses must implement this method.")
                                             # 抽象静态方法：直接抛错强制子类实现

    # -----------------------------------------------------------------------------
    # 【抽象接口 3】bug-fix patch → 待分析对象列表（静态方法）。
    # 论文语义：实现 §3.1.4 的"扫 patch 涉及对象"——差分验证只扫 diff 触及的翻译
    # 单元（成本可控且 bug 必在其中），而不是全库。
    # 参数 patch：unified diff 文本。返回：对象路径列表。
    # -----------------------------------------------------------------------------
    @staticmethod
    @abstractmethod
    def get_objects_from_patch(patch: str) -> List[str]:
        """
        Get the objects to analyze from a patch.

        Args:
            patch (str): The patch to analyze.

        Returns:
            List[str]: The objects to analyze.
        """
        raise NotImplementedError("Subclasses must implement this method.")
                                             # 同上：强制子类实现

    # -----------------------------------------------------------------------------
    # 【具体方法】把一个 bug-fix commit 组装成 Markdown 材料（三段式）：
    #   ## Patch Description —— commit message（修复动机与结论）
    #   ## Buggy Code       —— tree-sitter 提取的受影响函数完整源码（或整文件回退）
    #   ## Bug Fix Patch    —— 与父提交的 unified diff
    # 论文语义：§3.1.1 Bug Pattern Analysis 的 LLM 输入构造——pattern agent 从这
    #   份材料中提炼 targeted bug pattern（刻意收窄：只盯 patch 揭示的具体缺陷形
    #   态，不做"任意可能为空的指针"式泛化）。
    # 参数 commit_id：修复提交（hexsha 或可解析引用）。
    # 返回：拼好的 Markdown 字符串。抛错：commit 不存在时 ValueError。
    # -----------------------------------------------------------------------------
    def get_patch(self, commit_id: str) -> str:
        """
        Get the patch for a specific commit formatted as Markdown.

        Args:
            commit_id (str): The commit ID to get the patch for.

        Returns:
            str: Formatted patch as Markdown including commit message,
                 affected functions, and diff.

        Raises:
            ValueError: If commit_id does not exist in the repository.
        """
        # 先让 GitPython 解析引用；BadName（不存在/不可解析）时转成信息明确的
        # ValueError，让上游按"输入错误"而非 GitPython 内部异常处理
        try:
            commit = self.repo.commit(commit_id)   # 解析为 Commit 对象（支持短哈希/标签）
        except git.exc.BadName:
            raise ValueError(f"Commit '{commit_id}' not found in repository")
                                                   # 带原 commit_id 的错误信息，便于排障

        message = commit.message.strip()           # commit message 去首尾空白 = 修复描述文本

        # Get the diff between this commit and its parent
        parent_id = commit.hexsha + "^"            # git 语法 "<sha>^" = 父提交（buggy 版本所在）
        diff = commit.repo.git.diff(parent_id, commit.hexsha)
                                                   # 与父提交的 unified diff = bug 修复补丁
                                                   # 本体（pattern agent 学习的核心素材）

        # Get affected function code
        func_code_set = get_function_codes_with_config(commit)
                                                   # tree-sitter 从该 commit 涉及文件中提取
                                                   # 受影响函数的完整源码：返回
                                                   # (file_path, func_name, func_code) 集合；
                                                   # 函数级解析失败时回退整文件，func_name
                                                   # 带 "WHOLE_FILE_" 前缀（下面分支处理）

        # Build the markdown content in parts for better readability
        sections = []                              # Markdown 各节的容器（分节拼装再 join）

        # Add commit description
        sections.append("## Patch Description\n\n" + message + "\n")
                                                   # 第 1 节：修复描述（人写的动机/结论）

        # Add buggy code section
        sections.append("## Buggy Code\n")         # 第 2 节标题：buggy 代码（函数源码）
        for file_path, func_name, func_code in func_code_set:
                                                   # 逐个受影响"文件/函数"展开成代码块
            # Skip if func_name is None (parsing failure)
            if func_name is None:
                continue                           # 连整文件回退都失败的条目直接跳过
            if func_name.startswith("WHOLE_FILE_"):
                # Handle whole file fallback case
                file_name = func_name.replace("WHOLE_FILE_", "")
                                                   # 回退模式：func_name 实际存的是整个文件
                                                   # 的路径，剥掉前缀还原出文件名

                # Truncate very large files to avoid overwhelming the prompt
                truncated_code = truncate_large_file(func_code, max_lines=500)
                                                   # 截到 500 行（保头尾），防止大文件把
                                                   # pattern agent 的上下文窗口撑爆

                sections.append(
                    f"```c\n// Complete file: {file_path} (tree-sitter fallback)\n{truncated_code}\n```\n"
                )
                                                   # 整文件 C 代码块，并明确标注这是
                                                   # tree-sitter 解析失败的 fallback 产物
            else:
                # Handle normal function case
                sections.append(
                    f"```c\n// Function: {func_name} in {file_path}\n{func_code}\n```\n"
                )
                                                   # 常规模式：单函数 C 代码块，标注函数名
                                                   # 与所属文件，LLM 据此对齐 diff 上下文

        # Add patch diff
        sections.append("## Bug Fix Patch\n\n```diff\n" + diff + "\n```\n")
                                                   # 第 3 节：修复 diff（```diff 围栏，
                                                   # Markdown 渲染器可对 +/- 行高亮）

        # Join all sections with newlines
        return "\n".join(sections)                 # 各节之间以空行分隔，输出完整 Markdown

    # -----------------------------------------------------------------------------
    # 【工具方法】两个路径的相似度（静态方法；子类 get_object_name 消歧同名 .o 的
    # 共用底座）。
    # 算法：把两个绝对路径按 os.sep 切成组件，取"组件集合"的 Jaccard 相似度 =
    #       |交集| / |并集|。集合语义意味着忽略组件顺序与重复，只看目录名的重合度。
    # 论文语义：不出现在论文正文，是 §3.1.4 "扫 patch 涉及对象" 的工程支撑——
    #   构建日志里同名 stem（不同目录的 foo.c → foo.o）会产生多个候选，必须选出
    #   与源文件路径最相近者，否则差分验证会扫错翻译单元。
    # 参数 path1/path2：待比较路径（str/Path 均可）。返回 [0,1] 浮点，越大越相似。
    # 注意：resolve() 是 non-strict 的——被比较的 .o/源路径常不存在于磁盘，也不抛错。
    # -----------------------------------------------------------------------------
    @staticmethod
    def path_similarity(path1, path2):
        """Calculate the similarity of two paths based on their components."""
        path1 = str(Path(path1).resolve())    # 规范化为绝对路径字符串（消解 ./、../ 等）
        path2 = str(Path(path2).resolve())    # 同一规则处理第二个路径，保证可比
        components1 = path1.split(os.sep)     # 按分隔符切组件，如 /a/b/c.o → ['','a','b','c.o']
        components2 = path2.split(os.sep)     # 同上

        # Count the common components
        common_components = len(set(components1) & set(components2))
                                             # 交集大小：两路径共有的目录/文件名个数
        total_components = len(set(components1) | set(components2))
                                             # 并集大小：去重后的组件总数（Jaccard 分母）

        # Simple ratio of common components to total unique components
        return common_components / total_components
                                             # Jaccard 相似度 ∈ (0,1]，两路径组件完全
                                             # 相同（顺序无关）时取 1
