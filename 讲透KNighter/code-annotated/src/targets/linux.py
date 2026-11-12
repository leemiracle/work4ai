# =============================================================================
# 【模块定位】Linux 内核目标实现——KNighter 论文的主分析目标：TargetFactory 四
#   接口的 kbuild 版本（checkout + make allyesconfig 构建准备、源文件 → .o 对象
#   名反查、patch → 对象列表）。
#
# 【论文映射】
#   - checkout_commit()：§3.1.4 Validation 差分验证的环境准备——is_before=True
#     checkout 到补丁父提交（buggy，N_buggy 侧），is_before=False checkout 到补丁
#     提交（patched，N_patched 侧）；也是 §3.2 全库扫描前的构建准备。论文战果
#     （61 patch → 37 plausible → 92 新 bug：77 confirmed / 57 fixed / 30 CVE）
#     全部在该目标上取得。
#   - get_objects_from_patch()/get_object_name()：实现"扫 patch 涉及对象"——CSA
#     以翻译单元（.c → .o）为分析单位，必须把 diff 里的源文件映射成构建对象。
#   - make LLVM=1 ARCH=x86 allyesconfig：LLVM=1 强制全 clang 工具链（CSA 是
#     clang 的静态分析器，必须同一编译器接管全部翻译单元）；allyesconfig 把
#     CONFIG_* 尽量全开，最大化可分析的翻译单元覆盖（全库扫描覆盖率的技术前提）。
#
# 【管线角色】上游：src/global_config.py 读 linux_dir 配置实例化 Linux（target_type
#   非 v8 时的默认目标）；下游：src/backends/csa.py 差分验证（checkout_commit +
#   get_objects_from_patch，见其 validate 相关函数）与全库扫描；src/tests/ 端到端
#   测试直接驱动真实内核仓库。
#
# 【依赖与坑】
#   - 数据文件 linux-build-commands.txt（与本文件同目录，约 1.7MB）：一次全量
#     内核构建的命令日志，每条编译命令都含 "-o <输出路径>.o"；get_object_name
#     用它把 "foo.c" 反查成 "drivers/xxx/foo.o" 形式的对象路径。类属性在 import
#     时读入、常驻内存。
#   - 坑：两次 checkout 之间必须 make clean——残留旧 .o 会污染差分验证的两轮扫描；
#   - 坑：跨版本 checkout 后 .config 的选项集合会变，需 olddefcmd（olddefconfig
#     类命令）用默认值补齐新增选项，否则后续构建配置不完整；
#   - 坑：make 失败一律 RuntimeError 硬中断（脏环境会让 N_buggy/N_patched 不可比）。
# =============================================================================
import re                                    # 正则：构建日志反查 .o、从 diff 提取文件名
import subprocess as sp                      # 子进程：make clean / allyesconfig / olddefcmd
from pathlib import Path                     # 路径处理：stem 提取、后缀替换、数据文件定位
from typing import List                      # 类型注解 List[str]

from loguru import logger                    # loguru 结构化日志（info/error 双通道输出）

from targets.factory import TargetFactory    # 抽象基类：本类实现其四个接口


# -----------------------------------------------------------------------------
# Linux 内核仓库目标。注意 _build_commands 在类体（import 时）求值。
# -----------------------------------------------------------------------------
class Linux(TargetFactory):
    """
    A class representing the Linux kernel repository.
    """
    # ↑ 原有 docstring 原样保留

    _target_type = "linux"                   # 类型标识："linux"——global_config 默认目标
    _build_commands = (Path(__file__).parent / "linux-build-commands.txt").read_text()
                                             # 类属性（import 时求值）：读入同目录全量构建
                                             # 命令日志文本——每个 .c 的编译命令里都有
                                             # "-o <路径>/<stem>.o"，是 get_object_name
                                             # 反查对象名的数据源；约 1.7MB 常驻内存

    # -----------------------------------------------------------------------------
    # 【接口 1 实现】checkout + 内核构建环境准备（差分验证前置）。流程四步：
    #   1) make clean：清掉上次构建产物（防止旧 .o 干扰本轮扫描）；
    #   2) is_before=True 时把 commit_id 改写为 "<id>^"（父提交 = buggy 版本）；
    #   3) git checkout 切换工作树；
    #   4) make LLVM=1 ARCH=<arch> allyesconfig 生成全开配置；
    #   5) （可选）olddefcmd：olddefconfig 类命令补齐跨版本 .config 差异。
    # kwargs 参数：arch 目标架构（默认 "x86"）；olddefcmd 补 config 的命令
    #   （str 或 list，list 会被 join 成命令行、以 shell 执行）。
    # 失败语义：任何一步非零退出都 logger.error + RuntimeError 中断管线——构建
    #   环境不可信会让 N_buggy/N_patched 失去可比性，差分验证即失效。
    # -----------------------------------------------------------------------------
    def checkout_commit(self, commit_id, is_before=False, **kwargs):
        """
        Checkout a specific commit in the Linux kernel repository and prepare the build environment.

        Args:
            commit_id (str): The commit ID to checkout.
            is_before (bool): Whether to checkout before the commit.
            arch (str): The architecture to build for.
            olddefcmd (str): The command to run for the olddefconfig.
        """
        logger.info(
            f"Checking out commit {commit_id} {'before' if is_before else 'after'}"
        )
                                             # 记录 checkout 方向：before=父提交（buggy，
                                             # N_buggy 侧）/ after=补丁提交（patched，
                                             # N_patched 侧），差分验证两轮各调一次

        res = sp.run(["make", "clean"], cwd=self.repo.working_dir, capture_output=True)
                                             # 第 1 步：清理构建产物；capture_output 收集
                                             # stdout/stderr（bytes，后面要 decode）
        if res.returncode != 0:
            logger.error(f"Failed to clean the repository: {res.stderr.decode()}")
                                             # 先记错误日志（含 stderr 详情）
            raise RuntimeError(f"Failed to clean the repository: {res.stderr.decode()}")
                                             # 再抛 RuntimeError 硬中断（两处文本一致，
                                             # 便于日志与异常栈对齐）

        if is_before:
            commit_id = commit_id + "^"      # 第 2 步：git 语法加 "^" 取父提交——
                                             # 修复补丁的父提交 = 含 bug 的版本（buggy）

        self.repo.git.checkout(commit_id)    # 第 3 步：工作树切到目标提交

        res = sp.run(
            ["make", "LLVM=1", f"ARCH={kwargs.get('arch', 'x86')}", "allyesconfig"],
                                             # 第 4 步：LLVM=1 全 clang 构建（CSA 是
                                             # clang 的分析器，必须同一编译器）；ARCH 从
                                             # kwargs 取、默认 x86；allyesconfig 尽量
                                             # 全开 CONFIG_*，最大化可分析翻译单元覆盖
            cwd=self.repo.working_dir,
            capture_output=True,
        )
        if res.returncode != 0:
            logger.error(f"Failed to run allyesconfig: {res.stderr.decode()}")
            raise RuntimeError(f"Failed to run allyesconfig: {res.stderr.decode()}")
                                             # allyesconfig 失败 = 构建环境不可用，硬失败

        olddefcmd = kwargs.get("olddefcmd")  # 可选第 5 步：跨版本 checkout 后 .config
                                             # 有新增/废弃选项，olddefconfig 类命令用
                                             # 默认值补齐，保证后续 make 可用
        if olddefcmd:
            if isinstance(olddefcmd, list):
                olddefcmd = " ".join(olddefcmd)
                                             # 允许以 list 传参（免手拼引号），空格连接
                                             # 成完整命令行字符串

            res = sp.run(
                olddefcmd, cwd=self.repo.working_dir, capture_output=True, shell=True
            )
                                             # shell=True：olddefcmd 是命令字符串而非 argv
                                             # （由调用方 csa.py 拼好传入）
            if res.returncode != 0:
                logger.error(f"Failed to run olddefcmd: {res.stderr.decode()}")
                raise RuntimeError(f"Failed to run olddefcmd: {res.stderr.decode()}")
                                             # config 补齐失败同样硬失败（后续构建不可信）

    # -----------------------------------------------------------------------------
    # 【接口 2 实现】源文件名 → kbuild 对象(.o)路径（静态方法）。
    # 原理：linux-build-commands.txt 是一次全量构建的命令日志，每个 .c 的编译命令
    #   都带 "-o <输出路径>.o"；用正则把与源文件同 stem（主名相同）的输出全部捞出，
    #   多候选时按 path_similarity 选与源路径最相近者（同名不同目录消歧）。
    # 参数 file_name：patch 中的源文件路径（相对仓库根，如 drivers/net/foo.c）。
    # 返回：对象路径字符串；日志中查不到时回退为源路径直接把 .c 换 .o。
    # -----------------------------------------------------------------------------
    @staticmethod
    def get_object_name(file_name: str) -> str:
        file_path = Path(file_name)           # 包装成 Path 便于取 stem / 换后缀
        stem_name = file_path.stem            # 主名（去目录与 .c 后缀），如 foo——同名
                                             # .c 与 .o 的对应关系就建立在 stem 相等上

        pattern = rf"-o\s+.*?/{stem_name}\.o"
                                             # 匹配 "-o <路径>/<stem>.o"：
                                             #   `-o`         编译器输出开关的字面量
                                             #   `\s+`        其后一个以上空白（kbuild 输出
                                             #               恒为单空格，故下方 [3:] 安全）
                                             #   `.*?`        非贪婪任意字符（目录前缀）
                                             #   `/`          要求至少一层目录（形如 dir/foo.o）
                                             #   `{stem_name}` f-string 注入的源文件主名
                                             #   `\.o`        对象后缀（raw 串保住 \ 语义）
        match = re.search(pattern, Linux._build_commands)
                                             # 先探测日志中是否存在任一匹配
        if match:
            all_matches = re.findall(pattern, Linux._build_commands)
                                             # 存在则全量捞出（findall 无捕获组时返回
                                             # 整个匹配串，即 "-o dir/foo.o" 形式）
            all_matches = [match[3:] for match in all_matches]
                                             # 剥掉开头 "-o " 恰好 3 个字符（'-'、'o'、
                                             # 空格）得到纯对象路径；注意推导式变量 match
                                             # 遮蔽外层 search 的 match（推导作用域独立，
                                             # 不泄漏），返回列表元素仍是 str
            # Sort by edit distance to the file name
            # （原注释写 edit distance，实际实现是按 path_similarity 路径组件
            #   Jaccard 相似度降序排——同名 stem 多候选时的消歧策略）
            all_matches.sort(
                key=lambda x: Linux.path_similarity(x, file_name), reverse=True
            )
                                             # reverse=True：相似度最高的排最前
            return str(all_matches[0])        # 取与源文件路径最相似的对象（多半是正主）
        else:
            # If not found, return the default name
            return str(file_path.with_suffix(".o"))
                                             # 兜底：日志查不到（新文件/未参与过该次
                                             # 构建）就按源路径把 .c 后缀换成 .o

    # -----------------------------------------------------------------------------
    # 【接口 3 实现】bug-fix patch → 待分析对象(.o)列表（静态方法）。
    # 论文语义：§3.1.4 差分验证只扫 "patch 涉及对象"——bug 必在 diff 触及的翻译
    #   单元里，扫描成本可控。
    # 参数 patch：git diff 文本（unified diff；与 get_patch() 的 "## Bug Fix Patch"
    #   节同源）。返回：对象路径列表（一个 .c 条目 → 一个 .o）。
    # -----------------------------------------------------------------------------
    @staticmethod
    def get_objects_from_patch(patch: str) -> List[str]:
        """
        Get the objects to analyze from a patch.
        """
        # Find `--- a/` lines in the patch
        pattern = r"^--- a/(.*)$"             # unified diff 的"旧文件"行：--- a/<路径>；
                                             # 捕获组取 a/ 之后的完整相对路径
        matches = re.findall(pattern, patch, re.MULTILINE)
                                             # re.MULTILINE 让 ^ 逐行匹配；捞出 diff
                                             # 涉及的全部源文件路径（改动旧侧）
        # Filter out non-c files
        matches = [match for match in matches if match.endswith(".c")]
                                             # 只留 .c：CSA 的分析单位是 .c 翻译单元；
                                             # 纯 .h 改动会被跳过（其影响经 #include 体现在
                                             # 各个包含它的 .c 里）
        # Replace .c with .o
        matches = [Linux.get_object_name(match) for match in matches]
                                             # 逐个源文件映射成构建对象路径（原注释
                                             # "Replace .c with .o"描述整体效果）
        return matches                        # 对象列表交给 csa.py 驱动 CSA 扫描
