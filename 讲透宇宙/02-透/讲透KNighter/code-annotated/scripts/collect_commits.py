# This script is from https://github.com/harperchen/SEAL/blob/main/helper_scripts/00_patch_collector.py.
# It is used to collect patches from the Linux kernel repository.
# ============================================================================
# 【模块定位】从本地 Linux 内核仓的 git 历史中"粗筛"疑似 bug-fix commit，产出
#   候选清单 CSV（hexsha / GitHub 链接 / summary / author / bug_type 五列）。
#
# 【论文映射】KNighter 论文 §4 "Input Commit Collection" 的数据侧起点：阶段一
#   Checker Synthesis（§3.1 Algorithm 1）的输入 patch 即出自这里的候选池。
#   本脚本只负责关键词召回 + 三重硬过滤（目录白名单 / 提交信息关键词 / 改动
#   规模），语义精筛交给 src/commit_label.py（LLM 辅助标注）+ 两位作者独立
#   人工标注（论文口径：10 类 bug、每类 >=5 条、双人标注后仲裁，最终得 61 个
#   精选 patch）。
#
# 【管线角色】上游 = torvalds/linux 本地镜像（v6.13 分支历史）；
#   下游 = src/commit_label.py 精筛 -> 人工双标注 -> checker 合成输入。
#
# 【关键依赖与坑】① 整体移植自 SEAL 的 00_patch_collector.py，保留了若干 SEAL
#   遗留死代码：commit_pattern 正则、num_* 计数器、check_if_cc_stable /
#   check_if_code_changes 在本脚本中从未被调用。② 第 8 行 pip._internal 的 Git
#   导入会被下方 `from pydriller import *` 的同名类覆盖——self.repo1 实际用的
#   是 pydriller 的 Git（只有它提供 get_commit/modified_files/changed_methods）。
#   ③ source_dir 硬编码为作者机器路径，换环境必须先改。④ get_patches 每命中
#   一条候选就全量重写一次 CSV（断点友好但 O(n^2) 写盘）。
# ============================================================================

import re  # 标准库：commit log 解析与 bug 分型正则
import sys  # 读取命令行参数（argv[1]=子命令，argv[2]=输出 CSV 路径）
import chardet  # 字节流编码探测（仅 SEAL 遗留函数 check_if_code_changes 使用）

from pip._internal.vcs.git import Git  # 【实际无效】SEAL 遗留导入：Git 名字会被下方 pydriller 星号导入覆盖
from unidiff import PatchSet  # 解析 unified diff（仅遗留函数 check_if_code_changes 使用）

import pandas as pd  # 候选清单 DataFrame 与 to_csv 落盘
from git import Repo  # GitPython：只读遍历提交历史（iter_commits/hexsha/summary/author）
from pydriller import *  # 提交级深度挖掘：Git.get_commit -> Commit{msg,modified_files,insertions,deletions}；其 Git 覆盖上面 pip 的同名导入
from rich.progress import track  # 终端进度条：遍历 20 万 commit 时的可视化

# SEAL 遗留死代码：解析 `git log` 原始文本的四段正则（40 位完整 sha / Author 行 /
# Date 行 / 提交正文），re.DOTALL 让 . 也匹配换行，(?=\n\ndiff) 前瞻在 diff 处
# 截断正文——本脚本全程未使用该 pattern（get_patches 走 pydriller 而非 log 文本）。
commit_pattern = re.compile(r'^(commit\s[a-f0-9]{40})\n(Author:\s.+)\n(Date:\s+.*?)(?=\n\n)(.+?)(?:(?=\n\ndiff)|$)',
                            re.DOTALL)
# bug-fix 正向关键词表：提交信息命中任一即视为"疑似修 bug"。注意 'check' 也在
# 表内（大量真实修复就是"补一个缺失的检查"），'leak' 兜住各类泄漏——这就是论文
# §4 里"关键词检索内核 git log"的具体词表。
bug_fix_keywords = ["fix", "bug", "issue", "error", "crash", "hang",
                    "fault", "fail", "check", "mistake",
                    "incorrect", "defect", "leak"]

# bug-fix 反向（排除）关键词：命中任一则否决——修编译错/拼写错/链接错/加功能
# 支持等"非功能性变更"不是我们要的 bug-fix patch（与正向词同时命中时按否决算）。
not_bug_fix_keywords = ["fix compilation", "fix compile", "add support", "support",
                        "build error", "spell", "typo", "link error", "no functional change"]

release_date_v4_19 = 'Oct 22 2018'  # SEAL 遗留常量：v4.19 发布日期，本脚本未使用

# SEAL 遗留统计计数器：以下 num_* 与 num_bug_type（15 个细类）在本脚本中从未被
# 更新或读取（原 SEAL 版逐 commit 计数用），原样移植保留。
num_code_changes = 0
num_for_4_19 = 0
num_drivers = 0
num_reverted = 0
num_cc_stable = 0
num_dynamic = 0
num_static = 0
num_bug = 0
num_bug_fix = 0
# 15 个 bug 细类字典：论文 §4 的 10 大类（NPD/整数溢出/越界/缓冲区溢出/内存泄漏/
# UAF/Double-Free/UBI/并发/误用）是对这 15 细类的归并；键名与 set_bug_type 返回值对应
num_bug_type = {'Use-After-Free': 0, 'Resource-Leak': 0, 'Null-Ptr-Deref': 0,
                'UnInitialization': 0, 'Out-of-bound': 0, 'Divide-by-zero': 0,
                'Double-free': 0, 'Taint-Style': 0, 'Wrong-Error-Code': 0,
                'Error-Handling': 0, "Memory-Leak": 0, 'Lock-Misuse': 0,
                'Integer-Flow': 0, "Memory-Corruption": 0, 'Signedness-Bug': 0}

# ----------------------------------------------------------------------------
# PatchCollector：单个内核仓的候选收集器。
# 核心判定链 check_is_related_to_bug = 三个过滤器的与门：
#   check_if_interest（文件类型 + 目录白名单）
#   AND check_patch_description（提交信息像 bug-fix，或有动/静态工具报告背书）
#   AND check_code_changes（改动规模：<=5 文件、<=30 增/删行、1~5 个函数）
# ----------------------------------------------------------------------------
class PatchCollector:
    # 构造函数：repo_name 仅用于打印展示；内核仓路径硬编码（坑：换机器须先改）
    def __init__(self, repo_name) -> None:
        self.repo_name = repo_name  # 仓库名（展示用，如 "kernel"）
        self.source_dir = "/scratch/chenyuan-data/linux"  # in commit v6.2  ← 硬编码的内核仓本地路径（原注释说明该镜像停在 v6.2）
        self.repo = Repo(self.source_dir)  # GitPython 只读句柄：iter_commits 遍历历史、取 hexsha/summary/author
        self.repo1 = Git(self.source_dir)  # pydriller 句柄（变量名叫 repo1）：get_commit 深挖单 commit 的 msg/改动文件/增删行
        self.commit_url = "https://github.com/torvalds/linux/commit/"  # 候选 patch 的 GitHub 溯源链接前缀

    # 主入口：遍历分支历史 -> 三重过滤 -> bug 分型 -> 逐条追加进 CSV。
    # 参数 patch_file_path：输出 CSV 路径；无返回值（结果全量落盘）。
    def get_patches(self, patch_file_path):
        branch = "v6.13"  # 遍历的分支（注意与 source_dir 处 v6.2 注释口径不一致：镜像在 v6.2，历史遍历到 v6.13）
        print("Collecting patches in ", self.repo_name, branch)
        # 2019/02/19-2023/02/19 commits in v6.2  ← SEAL 原注释：候选时间窗口口径
        idlist = list(
            self.repo.iter_commits(
                branch, max_count=200000, no_merges=True,  # 最多取 20 万条；no_merges 排除 merge commit（无 diff 语义）
            )
        )
        df = pd.DataFrame()  # 空表起步，逐行 concat 追加
        print(f"Processing all the patches to find suspects, total patch number is: {len(idlist)}")
        for i in track(idlist):  # rich 进度条包装的逐 commit 循环
            patch = f"{self.commit_url}{i.hexsha[:12]}"  # 拼 GitHub 短链（12 位短 sha，与 GitHub URL 兼容）
            if self.check_is_related_to_bug(i.hexsha[:12]):  # 三重过滤与门（见类头注释）

                commit = self.repo1.get_commit(i.hexsha)  # pydriller 取完整 commit（msg 含 subject+body+trailer）

                subject, message, _, _ = self.parse_commit_log(commit.msg)  # 拆出标题/正文（trailer 与 is_revert 在此丢弃）

                # 关键词分型的输入串：正文+标题拼接再 lower（parse_commit_log 内部已
                # 整体 lower，此处 .lower() 冗余但无害）；末尾补空格保证 ' gpf ' 这类
                # 带空格定界的关键词在串尾也能命中
                to_be_checked = message.lower() + ' ' + subject.lower() + ' '
                bug_type = self.set_bug_type(to_be_checked)  # 15 细类关键词规则表分型（UnKnown=未识别）

                # 一行候选记录：12 位短 sha / GitHub 链接 / 标题 / 作者名 / bug 类型
                item = {"hexsha": i.hexsha[:12], "patch": patch, "summary": i.summary, "author": i.author.name, "bug_type": bug_type,}

                df_new_row = pd.DataFrame([item])  # 单行字典转 DataFrame（pandas 2.x 已不推荐逐行 concat，原样保留）
                df = pd.concat([df, df_new_row], ignore_index=True)  # 追加一行并重排索引
                df.to_csv(patch_file_path, index=False)  # 每命中一条就全量落盘：中途崩溃已写行不丢（断点友好），代价是反复重写
        print(f"Done, the collected patch is {len(df)}, save to file " + patch_file_path)


    # 总判定（与门）：三个过滤器全部通过才视为"与 bug 相关"的候选
    def check_is_related_to_bug(self, hexsha):
        return bool(self.check_if_interest(hexsha)  # 过滤器 1：改动文件类型 + 目录白名单
                    and self.check_patch_description(hexsha)  # 过滤器 2：提交信息关键词 / 工具报告背书
                    and self.check_code_changes(hexsha))  # 过滤器 3：改动规模与函数数

    # 过滤器 1：所有被改文件必须同时满足（a）是 .c/.h（b）落在内核主要源码子树。
    # 白名单目录 = drivers/sound/arch/samples/include/net/fs——CSA 扫描的主战场是
    # 驱动代码（论文目标抽象也是 drivers 子系统）。new_path 为 None 表示纯删除/
    # 重命名移除的文件，此时该项检查跳过（两个 if 是相互独立的判断）。
    def check_if_interest(self, hexsha):
        commit = self.repo1.get_commit(hexsha)  # pydriller 深挖该 commit 的改动文件列表
        for f in commit.modified_files:  # 逐个改动文件检查
            if f.new_path and not f.new_path.endswith('.c') \
                    and not f.new_path.endswith('.h'):  # 改到 .c/.h 之外的文件（如 .dts/.py/文档）-> 一票否决
                return False
            if f.new_path \
                    and not f.new_path.startswith("drivers/") \
                    and not f.new_path.startswith("sound/") \
                    and not f.new_path.startswith("arch/") \
                    and not f.new_path.startswith("samples/") \
                    and not f.new_path.startswith("include/") \
                    and not f.new_path.startswith("net/") \
                    and not f.new_path.startswith("fs/"):  # 不在七个白名单顶层目录内 -> 一票否决
                return False
        return True  # 全部通过（或没有任何带 new_path 的文件）

    # 过滤器 2：提交信息层面判定"这是不是一次 bug 修复"。依次短路求值：
    # revert 提交排除 -> 必须命中 bug-fix 正/负关键词 -> 有动态工具（KASAN/
    # syzkaller 等）或静态工具（Smatch/Coverity）报告背书则直接放行 -> 否则至少
    # 要能被 set_bug_type 分出具体类型（UnKnown 则拒绝）。
    def check_patch_description(self, hexsha):
        commit = self.repo1.get_commit(hexsha)
        subject, message, sign_off, is_revert = self.parse_commit_log(commit.msg)  # 拆标题/正文/trailer/是否 revert
        if is_revert:  # revert 不是我们要的"引入修复"的模式样本 -> 拒收
            return False
        to_be_checked = message + ' ' + subject + ' '  # 正文+标题拼接（正文在前标题在后），末尾补空格保词边界
        to_be_checked = to_be_checked.lower()  # 统一小写做子串匹配
        if not self.check_if_bug_fix(to_be_checked):  # 正/负关键词判定不通过 -> 拒绝
            return False
        if self.check_if_dynamic(to_be_checked):  # 有动态工具报告背书 -> 放行
            return True
        if self.check_if_static(to_be_checked):  # 有静态工具报告背书 -> 放行
            return True
        if self.set_bug_type(to_be_checked) == "UnKnown":  # 既无背书又分不出类型 -> 拒绝
            return False
        return True  # 能分出具体 bug 类型 -> 通过

    # 过滤器 3：改动规模闸门——patch 必须小而聚焦（后续 LLM 上下文窗口装得下、
    # 双人标注工作量可承受、提炼的 bug pattern 不发散）：
    #   文件数 <=5 且 增行 <=30 且 删行 <=30；
    #   函数级：被修改的函数总数在 1~5 之间（0 个=非代码逻辑变更；>5 个=大重构）。
    def check_code_changes(self, hexsha):
        commit = self.repo1.get_commit(hexsha)
        if commit.files > 5 or commit.insertions > 30 or commit.deletions > 30:  # 规模超限一票否决
            return False

        # func-level check: no modification for func or too many funcs
        modified_func = []  # 汇总所有改动文件里被修改的函数名（pydriller changed_methods）
        for f in commit.modified_files:
            modified_func.extend(method.name for method in f.changed_methods)
        return 1 <= len(modified_func) <= 5  # 双端闭区间：至少改 1 个函数、至多 5 个

    # bug 分型规则表（静态方法）：对"正文+标题"小写串按优先级自上而下做子串/
    # 正则匹配，返回 15 个细类之一；elif 链即优先级——特异词（user-controlled/
    # integer overflow）必须排在泛化词（overflow/leak）之前，否则会被泛化类抢先
    # 吞掉。论文 §4 的 10 大类（NPD/整数溢出/越界/缓冲区溢出/内存泄漏/UAF/
    # Double-Free/UBI/并发/误用）即对这 15 细类的归并。
    @staticmethod
    def set_bug_type(to_be_checked):
        # Taint-Style（污点风格，归入"误用"大类）：不可信输入直达敏感操作——
        # 用户可控/malicious device/malformed 等表述。放最前：最特异，不能被
        # 下面的泛化词（null/leak 等）抢走。
        if 'sanity' in to_be_checked or \
                'controlled by user' in to_be_checked or \
                'malicious device' in to_be_checked or \
                'malicious user' in to_be_checked or \
                'user-controlled' in to_be_checked or \
                'malfunctioning' in to_be_checked or \
                'malformed' in to_be_checked or \
                'from user' in to_be_checked or \
                'user data' in to_be_checked or \
                'user input' in to_be_checked:
            return "Taint-Style"
        # Use-After-Free：三种写法（带连字符/空格/缩写 uaf）
        elif 'use after free' in to_be_checked or \
                'use-after-free' in to_be_checked or \
                'uaf' in to_be_checked:
            return "Use-After-Free"
        # Resource-Leak：资源泄漏（io/irq/pm 等，区别于下面的 Memory-Leak）
        elif 'resource leak' in to_be_checked or \
            'refcount leak' in to_be_checked:
            return "Resource-Leak"
        # Lock-Misuse（并发类）：正则用空格定界匹配独立的 lock/unlock/deadlock 词
        # ——两侧必须有空格，避免误中 clock/block 等词根
        elif re.search(r" (lock|unlock|deadlock) ", to_be_checked):
            return 'Lock-Misuse'
        # Signedness-Bug：符号扩展/无符号比较错误
        elif 'sign extension' in to_be_checked or \
                'sign-extension' in to_be_checked or \
                'signedness bug' in to_be_checked or \
                'unsigned comparison' in to_be_checked:
            return 'Signedness-Bug'
        # Null-Ptr-Deref（NPD，关键词最全的一类）：null pointer 的各种写法/缩写
        # npd、' gpf '（general protection fault，x86 保护异常日志用语，前后空格
        # 定界防误中）、dereferenced、以及内核 oops 报告惯用语 "handle kernel
        # paging request"——oops 日志原文是判 NPD 的强信号。
        elif 'null ptr' in to_be_checked or \
                'pointer dereference' in to_be_checked or \
                'null pointer dereference' in to_be_checked or \
                'null dereference' in to_be_checked or \
                'npd' in to_be_checked or \
                'null pointer' in to_be_checked or \
                'null-ptr-deref' in to_be_checked or \
                'null-deref' in to_be_checked or \
                'null check' in to_be_checked or \
                ' gpf ' in to_be_checked or \
                'protection fault' in to_be_checked or \
                'null-pointer' in to_be_checked or \
                'dereferenced' in to_be_checked or \
                'handle kernel paging request' in to_be_checked:
            return 'Null-Ptr-Deref'
        # UnInitialization（UBI，未初始化使用）：注意 'initialized' 宽匹配——
        # "not correctly initialized" 这类否定表述也会命中（靠上下文语义仍指向 UBI）
        elif "uninitialize" in to_be_checked or \
                'uninit-value' in to_be_checked or \
                'ununit-value' in to_be_checked or \
                'uninit value' in to_be_checked or \
                'initialized' in to_be_checked:
            return 'UnInitialization'
        # Integer-Flow：整数上溢/下溢、索引下溢、移位越界——必须排在 Out-of-bound
        # 之前（'integer overflow' 含泛化词 overflow，否则会被 Out-of-bound 抢走）
        elif 'integer overflow' in to_be_checked or \
                'integer underflow' in to_be_checked or \
                'index underflow' in to_be_checked or \
                'shift_out_of_bounds' in to_be_checked:
            return 'Integer-Flow'
        # Out-of-bound（越界，论文 10 大类的"越界+缓冲区溢出"归并处）：'overflow'
        # 泛化词在此兜底（缓冲区溢出多表述为 buffer overflow）
        elif 'out of bound' in to_be_checked or \
                'oob' in to_be_checked or \
                'out-of-bound' in to_be_checked or \
                'overflow' in to_be_checked or \
                'handle page fault' in to_be_checked:
            return 'Out-of-bound'
        # Divide-by-zero：除零——除固定短语外还接受共现组合（'divide' 与 'zero'
        # 同时出现即可，哪怕不相邻）与 'zero out' 宽松词
        elif 'divide by zero' in to_be_checked or \
                'zero divide' in to_be_checked or \
                ('divide' in to_be_checked and 'zero' in to_be_checked) or \
                ('division' in to_be_checked and 'zero' in to_be_checked) \
                or 'divide error' in to_be_checked \
                or 'zero out' in to_be_checked:
            return 'Divide-by-zero'
        # Double-free：双重释放（空格/连字符两种写法）
        elif 'double free' in to_be_checked or \
                'double-free' in to_be_checked:
            return "Double-free"
        # Memory-Leak（内存泄漏）：除 'leak' 泛化词外，两个正则抓"补上缺失的
        # xxx() 调用"句式（.* 前缀无锚定等价于子串搜索）——漏掉 kfree()/
        # clk_disable() 等清理调用的修复常不出现 "leak" 字样，用函数调用形态来抓
        elif 'mem leak' in to_be_checked or \
                'memleak' in to_be_checked or \
                'memory leak' in to_be_checked or \
                'ref count' in to_be_checked or \
                'refcount' in to_be_checked or \
                'refcnt leak' in to_be_checked or \
                'unbalanced' in to_be_checked or \
                'imbalance' in to_be_checked or \
                'leak' in to_be_checked or \
                re.search('.*fix missing.*\(\)', to_be_checked) or \
                re.search('.*add missing.*\(\)', to_be_checked):
            return "Memory-Leak"
        # Memory-Corruption：内存损坏
        elif 'memory corruption' in to_be_checked:
            return "Memory-Corruption"
        # Wrong-Error-Code（归入"误用"大类）：错误码/返回值写错
        elif 'error code' in to_be_checked or \
                'wrong return value' in to_be_checked or \
                'error return code' in to_be_checked or \
                'incorrect return value' in to_be_checked or \
                'fix return value' in to_be_checked or \
                'return value check' in to_be_checked or \
                'fix error code' in to_be_checked:
            return "Wrong-Error-Code"
        # Error-Handling（错误处理，兜底大类）：未检查返回值/错误路径处理不当；
        # 'return value' 单独出现也算；'error handl' 同时兜住 handle/handling 拼写
        elif 'unchecked return' in to_be_checked or \
                'error handle' in to_be_checked or \
                'error handl' in to_be_checked or \
                'check return' in to_be_checked or \
                'check for return value' in to_be_checked or \
                'check for error' in to_be_checked or \
                'error handling' in to_be_checked or \
                'error path' in to_be_checked or \
                'error check' in to_be_checked or \
                'error return' in to_be_checked or \
                'return value' in to_be_checked or \
                'handle error' in to_be_checked:
            return "Error-Handling"
        else:
            return "UnKnown"  # 兜底：无法分型（上游 check_patch_description 会拒收 UnKnown）

    # commit log 拆解（静态方法）：把 pydriller 的完整 Commit.msg（=subject 标题
    # + body 正文 + trailer 标签区）拆成四元组。
    # 参数 commit_log：完整提交信息原文；
    # 返回 (message_subject 标题, message_body 压平成单行的正文, "\n" 连接的
    # trailer 区原文, is_revert 是否 revert 提交)。
    @staticmethod
    def parse_commit_log(commit_log: str):
        commit_log = commit_log.lower()  # 整体转小写——下游所有 .lower() 调用实际都是冗余的
        # trailer 行正则：内核邮件列表标签（Signed-off-by/Reported-by/Tested-by/
        # Reviewed-by/Cc:/Fixes:/Acked-by/Change-Id/Link:/Suggested-by 等）；
        # MULTILINE 让 ^ 匹配每一行行首；IGNORECASE 在已 lower 的文本上再兜底
        signature_pattern = re.compile(
            r'^(?:signed-off-by:|reported-by:|tested-by:|reviewed-by:|cc:|fixes:|'
            r'acked-by:|change-Id:|link:|suggested-by:|requested-by:|reported by:|merged from|reported-and-tested-by:).*',
            re.MULTILINE | re.IGNORECASE)
        signed_off_by_matches = re.findall(signature_pattern, commit_log)  # 收集全部 trailer 行

        # 目标：找到"正文（非 trailer 部分）"的结束位置 signed_off_by_start
        if signed_off_by_matches is None or len(signed_off_by_matches) == 0:
            # 一条 trailer 都没匹配到：
            if 'Signed-off-by:'.lower() in commit_log.lower() or \
                    'Reported-by:'.lower() in commit_log.lower() or \
                    'Tested-by:'.lower() in commit_log.lower() or \
                    'Reviewed-by:'.lower() in commit_log.lower() or \
                    'Cc:'.lower() in commit_log.lower() or \
                    'Acked-by:'.lower() in commit_log.lower() or \
                    'Change-Id:'.lower() in commit_log.lower() or \
                    "Fixes:".lower() in commit_log.lower():
                # 但文本里明明含这些标签——说明是格式变体导致正则漏匹配，拆解不可靠，
                # 返回空串让上游放弃该 commit
                return "", ""
            else:
                # print("[{}/{}] Signed off not match: {}\n{}".format(i, num_patches, filepath, message))
                # 确实没有 trailer：用 'diff --git' 的位置当正文终点（pydriller 的
                # msg 通常不含 diff，find 返回 -1，由下方 >= 判断兜住）
                signed_off_by_start = commit_log.find('diff --git')
        else:
            # 正常路径：第一个 trailer 行的起始位置即正文终点
            signed_off_by_start = commit_log.find(signed_off_by_matches[0])

        # 若正文里混入了 diff 头且位置不晚于当前终点，把终点提前到 diff 处
        # （防把 diff 文本误当正文参与关键词匹配）
        if 'diff --git' in commit_log and signed_off_by_start >= commit_log.find('diff --git'):
            signed_off_by_start = commit_log.find('diff --git')

        commit_info = commit_log[:signed_off_by_start].strip()  # 截取正文并去首尾空白
        message_items = commit_info.split("\n\n")  # 按空行分段：内核规范第一段=标题，其后=正文各段

        message_subject = message_items[0] if len(message_items) >= 1 else ""  # 标题（首段）
        # 单段时整段即正文；多段时正文=其余段重新拼接
        message_body = commit_info if len(message_items) == 1 else "\n\n".join(message_items[1:])
        # 删除正文里内核惯用的 commit 引用（形如 `abc1234e ("标题")` 的 sha+标题
        # 组合）——非实义文本，留着会污染关键词匹配
        message_body = re.sub(r'[0-9a-fA-F]+\s\(\".*?\"\)', '', message_body)

        is_revert = False
        if 'revert'.lower() in message_subject.lower():  # 标题含 revert -> 判为 revert 提交（上游会拒收）
            is_revert = True

        # 返回四元组；body 把换行压平成空格（后续做子串关键词匹配不受换行干扰）
        return message_subject, message_body.replace('\n', ' '), "\n".join(signed_off_by_matches), is_revert



    # 动态工具报告背书检测（静态方法）：命中任一关键词说明该 bug 有内核动态测试
    # 基础设施的报告背书，真实性高，check_patch_description 会直接放行——对应
    # 论文 §4 "以 sanitizer/syzkaller 报告为锚"的收集口径。
    # 词表：kasan（地址消毒器：UAF/越界）、fuzzing/fuzzer、syzkaller/syzbot
    # （内核模糊测试）、kmemleak（泄漏检测）、kcsan（并发消毒器）、kmsan（未初始
    # 化检测）、ubsan（未定义行为）。
    @staticmethod
    def check_if_dynamic(to_be_checked: str):
        if 'kasan' in to_be_checked:
            return True
        if 'fuzzing' in to_be_checked:
            return True
        if 'fuzzer' in to_be_checked:
            return True
        if 'syzkaller' in to_be_checked:
            return True
        if 'kmemleak' in to_be_checked:
            return True
        if 'kcsan' in to_be_checked:
            return True
        if 'kmsan' in to_be_checked:
            return True
        if 'ubsan' in to_be_checked:
            return True
        if 'syzbot' in to_be_checked:
            return True

        return False  # 无任何动态工具信号

    # 静态工具报告背书检测（静态方法）：提交信息提到 smatch/static analysis/
    # coverity 说明已有静态分析工具报过，同样放行。注意 coccinelle 被注释禁用
    # （其报告偏脚本化风格/语义检查，噪声大）；' smatch' 带前置空格防误中其他词。
    @staticmethod
    def check_if_static(to_be_checked: str):
        if ' smatch' in to_be_checked:
            return True
        if 'static analysis' in to_be_checked:
            return True
        if 'coverity' in to_be_checked:
            return True
        # if 'coccinelle' in to_be_checked:
        #     return True

        return False  # 无任何静态工具信号

    # bug-fix 正/负关键词判定（静态方法）：正向词命中任一 -> is_error=True；
    # 排除词命中任一 -> is_support=True；返回 is_error and not is_support
    # ——同时命中排除词则整体否决（"fix compile error" 这类不算 bug 修复）。
    @staticmethod
    def check_if_bug_fix(to_be_checked: str):
        is_error = False
        for error in bug_fix_keywords:  # 遍历正向词表
            if error in to_be_checked:
                is_error = True  # 命中即置位（不 break，全表扫完）

        is_support = False
        for support in not_bug_fix_keywords:  # 遍历排除词表
            if support in to_be_checked:
                is_support = True
        return is_error and not is_support  # 正向命中且未被排除词否决

    # CC stable 检测（静态方法，SEAL 遗留死代码）：commit 是否抄送了 stable 邮箱
    # （stable@vger.kernel.org / stable@kernel.org）——CC stable 通常意味着
    # "确有 bug 且已影响已发布版本"，是高置信信号。本脚本从未调用。
    @staticmethod
    def check_if_cc_stable(commit_log: str):
        if 'stable' in commit_log:  # 先粗筛：文本含 stable 才细看
            if 'stable@vger.kernel.org' in commit_log:
                return True
            elif 'stable@kernel.org' in commit_log:
                return True
            else:
                return False  # 提到 stable 但没抄送邮箱（如 stable tree 讨论）
        return False

    # patch 文件代码变更检测（静态方法，SEAL 遗留死代码）：读 unified diff 文件，
    # 检查被修改文件里有 .c/.h。本脚本从未调用。隐患：chardet.detect 对纯 ASCII/
    # 空文件可能返回 encoding=None，open(encoding=None) 会抛 TypeError——因从未
    # 被调用而未爆发；且 global 引用的 modified_func_tot 在本模块并不存在。
    @staticmethod
    def check_if_code_changes(file_path: str):
        global modified_func_tot  # SEAL 遗留：该全局名在本模块未定义（真调用会 NameError）
        is_c_h_file = False
        with open(file_path, mode='rb') as file:  # 先按字节读
            raw_data = file.read()
            encoding = chardet.detect(raw_data)['encoding']  # 探测文件编码

        with open(file_path, mode='r', encoding=encoding, errors="ignore") as file:  # 按探测编码文本读（坏字符忽略）
            patch = PatchSet(file)  # unidiff 解析 patch

            for patched_file in patch.modified_files:  # 遍历 patch 中被修改的文件
                if patched_file.path.endswith('.c') or patched_file.path.endswith('.h'):  # 有 C 源/头文件改动即算代码变更
                    is_c_h_file = True

        return is_c_h_file

if __name__ == '__main__':
    if sys.argv[1] == 'collect':  # 子命令 collect：全量收集（唯一的子命令分支）
        patch_file_path = sys.argv[2]  # 位置参数 2：输出 CSV 路径
        collecter = PatchCollector("kernel")  # 变量名拼写 collecter（原样保留）；repo_name 仅展示用
        collecter.get_patches(patch_file_path)  # 遍历 v6.13 历史 -> 三重过滤 -> 增量落盘 CSV
        