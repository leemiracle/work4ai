# =============================================================================
# 【模块定位】KNighter 阶段二/部署期的"全库扫描 + 报告收集 + triage"驱动模块。
#
# 【论文映射】KNighter: Transforming Static Analysis with LLM-Synthesized
#   Checkers（arXiv:2503.09002, SOSP'25）§3.2 Checker Refinement 与部署阶段：
#   论文流程"valid checker 全库扫描 → 报告蒸馏 → triage agent 逐报告判 TP/FP"
#   的三步分别对应本模块 scan/scan_batch_checkers/scan_single_checker（扫描执行）、
#   collect_reports（报告蒸馏：只留 relevant lines + trace path）、
#   triage_report（调度 triage agent = agent.check_report）。
#   论文口径：refine 期间全库扫描限 1 小时或 100 warnings，正式找 bug 时不限——
#   本模块 scan_batch_checkers 即"正式找 bug"模式（monitor 不设 warning 上限）。
#
# 【管线角色】
#   上游：src/checker_gen.py（§3.1 阶段一合成出的 valid checker 元数据目录，
#     每个子目录一份 CheckerData 落盘，含 checker1.cpp）；
#     src/checker_refine.py（§3.2 精化循环内部复用 collect_reports 收集报告）。
#   下游：src/backends/csa.py（把 checker 编译为 CSA plugin 并真跑扫描）、
#     src/agent.py::check_report（triage agent，prompt_template/check_report.md）。
#   入口：src/main.py 子命令 scan / scan_single / triage。
#
# 【关键依赖与坑】
#   - kernel_commands.generate_command：拼 scan-build 命令前缀，逐 checker 追加
#     "-load-plugin {id}Plugin.so -enable-checker custom.{id}Checker"。
#   - tools.remove_text_section：报告蒸馏核心——删掉 HTML 报告里整段
#     "Annotated Source Code" 源码区，只留 Bug Summary + relevant lines。
#   - 坑1：scan() 形参名 valid_chekcer_meta_dir 是原仓拼写笔误（chekcer），不改。
#   - 坑2：global_config.target 是 @property（返回 Linux/V8 等 Target 实例），
#     不能写成 target()——上游 PR #26（基准 commit f4e834b3）刚修复
#     scan_batch_checkers 中 target().checkout_commit 触发的
#     "TypeError: 'Linux' object is not callable"。
#   - 坑3：monitor_build_output(process, -1) 的 -1 = 不设 warning 上限（正式找
#     bug 不限量）；该函数返回 (输出文本, 是否正常结束)，此处只消费输出文本。
#   - 坑4：collect_reports 的 max_num_reports=100 判据是"唯一源文件数"而非报告
#     总数，对应论文 §3.2 refine 期间"最多 100 warnings"上限；超限整批判
#     too_many、放弃 triage（视为 checker 匹配过宽）。
#   - 坑5：triage 判定用 `"NotABug" in check_result` 子串匹配（triage agent 输出
#     约定为 "Decision: {Bug/NotABug}"），正文任何位置出现该词都会命中，较脆弱。
# =============================================================================
import re                                    # 正则：从 HTML 报告 <title> 提取被报警的源文件路径
import subprocess                            # 子进程：cmake/make 编译 plugin、Popen 起全库扫描
from collections import defaultdict          # 报告聚合：file_reports[源文件名] -> [(md, html), ...]
from pathlib import Path                     # 路径遍历：checker 元数据目录、scan-build 报告目录

from html2text import html2text              # CSA 的 HTML 报告 -> markdown（报告蒸馏第一步，供 triage agent 阅读）

from agent import check_report               # triage agent（论文 §3.2）：判定单条报告是否命中目标 bug pattern
from checker_data import CheckerData         # checker 元数据容器：加载 pattern/patch 供 triage prompt 使用
from global_config import global_config, logger  # 全局配置单例（LLVM_dir/jobs/result_dir/target/backend）+ loguru 日志
from kernel_commands import generate_command     # 生成 scan-build 命令前缀（加载 plugin + enable custom checker）
from tools import monitor_build_output, remove_text_section  # 构建输出实时监控 / 报告蒸馏（删源码大段）


# -----------------------------------------------------------------------------
# scan(valid_chekcer_meta_dir, arch="x86") —— 全库批量扫描的总入口（main.py 子命令 scan）
# 职责：把阶段一产出的一批 valid checker 元数据目录装配成 {checker名: C++源码}
#       字典，转交 scan_batch_checkers 执行"编译 plugin + 全库扫描"。
# 参数：valid_chekcer_meta_dir —— 元数据根目录，每个子目录 = 一个 checker 的
#         CheckerData 落盘（约定须含 checker1.cpp；形参名 chekcer 为原仓笔误）；
#       arch —— 目标架构（x86/arm64/riscv），对应内核构建 ARCH= 变量。
# 返回：无（副作用：扫描报告 HTML 落盘 result_dir/reports）。
# 论文语义：§3.2 之后"正式找 bug"模式——不限时限量，用全部 valid checker 扫 master。
# -----------------------------------------------------------------------------
def scan(valid_chekcer_meta_dir, arch="x86"):
    """
    Scan the kernel with multiple checkers from a directory of checker metadata.

    Args:
        valid_chekcer_meta_dir: Directory containing checker subdirectories
        arch: Target architecture (default: x86)
    """
    # FIXME: THIS SHOULD BE REFACTORED  ← 原仓遗留标记：装载逻辑应并入 CheckerData 统一管理
    valid_chekcer_meta_dir = Path(valid_chekcer_meta_dir)  # 统一转 Path 以便 iterdir 遍历子目录
    checker_dir = {}  # 装配结果：{plugin/checker 唯一名: checker C++ 源码文本}
    for sub_checker in valid_chekcer_meta_dir.iterdir():  # 遍历每个 checker 的元数据子目录
        if sub_checker.is_dir():  # 只处理子目录（跳过杂散文件）
            checker_file = sub_checker / "checker1.cpp"  # 约定文件名：repair 成功后落盘的最终 checker 源码
            if not checker_file.exists():  # 缺 checker 源码 = 该目录不是有效 checker
                logger.info(f"Fail to find checker1.cpp in {sub_checker}!")  # 记录但不中断整批
                continue  # 跳过该子目录
            checker_code = checker_file.read_text()  # 读入 checker C++ 源码
            name = "SagenScan" + sub_checker.name[:12]  # checker 唯一名 = 固定前缀 + 子目录名前 12 字符（截断防过长；子目录名通常含 commit_id）
            checker_dir[name] = checker_code  # 登记进待扫描字典
    logger.info(f"Scanning with {len(checker_dir)} checkers for {arch}...")  # 汇报本批 checker 数量与架构
    scan_batch_checkers(checker_dir, arch=arch)  # 转入批量扫描：plugin 编译 + checkout master + 全库 make


# -----------------------------------------------------------------------------
# scan_batch_checkers(checker_dict, arch="x86") —— 手工创建 plugin 的批量全库扫描
# 职责：把 N 个 checker 源码逐个注入 LLVM 源码树的 plugin 目录（create_plugin.py
#       脚手架 + 类名重命名），编译成 .so plugin 后，用 scan-build 前缀挂载全部
#       plugin 对目标仓库（默认 Linux 内核）做一次全库构建扫描。
# 参数：checker_dict —— {checker_id: checker_code}；
#       arch —— x86/arm64/riscv（arm64/riscv 追加交叉编译前缀 CROSS_COMPILE）。
# 返回：无（报告 HTML 由 scan-build -o 写入 result_dir/reports，构建日志写 tmp-output）。
# 论文语义：论文 §3.2 部署期"正式找 bug"模式——一次性挂载所有合成 checker 扫
#   全库（论文战果 92 个新 bug / 30 CVE 的产出通道），与 refine 期间的限量扫描相区别。
# -----------------------------------------------------------------------------
def scan_batch_checkers(checker_dict, arch="x86"):
    """
    Scan the kernel with multiple checkers using manual plugin creation.

    Args:
        checker_dict (dict): Dictionary mapping checker_id -> checker_code
        arch (str): Target architecture (default: x86)
    """
    # FIXME: This should be refracted  ← 原仓遗留标记（refracted 系笔误，应为 refactored）
    llvm_build_dir = Path(global_config.get("LLVM_dir")) / "build"  # LLVM 构建目录（plugin 编译与 scan-build 均在此）
    jobs = global_config.get("jobs")  # 并行编译作业数（-j）

    plugin_name_str = ""  # 累积全部 plugin 的 make 目标名（空格分隔，供一次性 make）
    for checker_id, checker_code in checker_dict.items():  # 逐个 checker 注入 LLVM 源码树
        plugin_dir = Path(global_config.get("LLVM_dir")) / "clang/lib/Analysis/plugins"  # CSA plugin 的标准落点目录（LLVM 源码树内）
        subprocess.run(["python3", "create_plugin.py", checker_id], cwd=plugin_dir)  # 跑脚手架脚本生成 {id}Handling/{id}Checker.cpp 骨架并注册进构建系统
        checker_file_path = (  # 生成的 checker 源文件路径（Handling 目录约定）
            plugin_dir / f"{checker_id}Handling" / f"{checker_id}Checker.cpp"
        )
        checker_code = checker_code.replace("SAGenTestChecker", f"{checker_id}Checker")  # 类名重命名：合成 checker 统一叫 SAGenTestChecker，改成专属名才能与 -enable-checker custom.{id}Checker 对应
        checker_file_path.write_text(checker_code)  # 用真实 checker 源码覆盖脚手架骨架
        plugin_name_str += f"{checker_id}Plugin "  # 收集本 checker 的 plugin make 目标名

    skip_llvm_build = False  # 编译开关：False = 必须重新 cmake/make（保留该旗标便于调试时跳过编译）
    if not skip_llvm_build:  # 默认恒真分支
        subprocess.run(  # 重新跑 cmake 配置：启用 clang+lld 工程、只编 X86 后端、Release、Unix Makefiles（../llvm 是相对 build 目录的源码路径）
            'cmake -DLLVM_ENABLE_PROJECTS="clang;lld" -DLLVM_TARGETS_TO_BUILD=X86 -DCMAKE_BUILD_TYPE=Release -G "Unix Makefiles" ../llvm',
            cwd=llvm_build_dir,  # 在构建目录内执行
            shell=True,  # 整条命令含引号，必须经 shell 解释
        )

        subprocess.run(  # 增量编译：只编所有 checker 的 plugin 目标（不动整个 LLVM 树）
            f"make {plugin_name_str} CFLAGS+='-Wall' -j{jobs}",  # plugin_name_str 形如 "SagenScanxxxxPlugin SagenScanyyyyPlugin "
            cwd=llvm_build_dir,  # 在构建目录内执行
            shell=True,  # CFLAGS+= 追加语法需要 shell
        )
        subprocess.run(f"make CFLAGS+='-Wall' -j{jobs}", cwd=llvm_build_dir, shell=True)  # 全量构建兜底：确保 plugin 的链接依赖齐全

    output_dir = Path(global_config.get("result_dir")) / "reports"  # 全部报告的输出根目录
    commit = "master"  # 扫描目标 commit：master（正式找 bug 扫最新代码；区别于差分验证的 buggy/patched 两点）
    comd_prefix = generate_command(  # 生成 scan-build 命令前缀：PATH 注入 + 挂载全部 plugin + enable 全部 custom checker
        llvm_build_dir, no_output=True, plugin_names=list(checker_dict.keys())  # no_output=True 先不带 -o（由下方统一指定输出目录）
    )
    output_dir_str = str(output_dir.absolute().as_posix())  # 报告目录的绝对 POSIX 路径字符串（喂给 scan-build -o）
    print(output_dir_str)  # 打印报告目录位置（供外部脚本定位产物）
    comd_prefix += f"-o {output_dir_str} "  # 把统一输出目录追加到命令前缀
    olddefcmd = comd_prefix + f"make LLVM=1 ARCH={arch} olddefconfig"  # checkout 后的配置命令：以默认值补全 .config（新增配置项自动取 default）

    global_config.target.checkout_commit(  # 目标仓库切到 master 并清理构建环境（make clean 等）
        commit, is_before=False, olddefcmd=olddefcmd, arch=arch  # is_before=False：取该 commit 本身而非其父提交（差分验证 buggy 侧才用 True）
    )  # 注意：target 是 @property 不能加括号调用——PR #26 刚修复此处 target().checkout_commit 的 TypeError

    if arch == "arm64":  # ARM64 分支：需要交叉编译前缀
        logger.warning("ARM64")  # 原样：用 warning 级别提示架构分支
        comd = (  # 全库构建扫描命令：scan-build 前缀 + LLVM=1（Clang 构建）+ 交叉编译 + 并行
            comd_prefix
            + f"make LLVM=1 ARCH={arch} CROSS_COMPILE=aarch64-linux-gnu- -j{jobs}"  # aarch64 交叉工具链前缀
        )
    elif arch == "riscv":  # RISC-V 分支：同样需要交叉编译前缀
        logger.warning("RISCV")  # 原样：warning 级别提示
        comd = (
            comd_prefix
            + f"make LLVM=1 ARCH={arch} CROSS_COMPILE=riscv64-unknown-linux-gnu- -j{jobs}"  # riscv64 交叉工具链前缀
        )
    else:  # 默认分支：x86 本地编译（无需 CROSS_COMPILE）
        comd = comd_prefix + f"make LLVM=1 ARCH={arch} -j{jobs}"  # 全量构建，scan-build 在每个编译单元上跑 CSA 分析
    logger.info("Running: " + comd)  # 记录完整扫描命令（复现实验的关键日志）

    process = subprocess.Popen(  # 在目标仓库工作目录起全库扫描进程（异步，交由 monitor 读输出）
        # comd.split(" "),  ← 原仓保留的注释掉的旧写法（曾尝试列表参数模式）
        comd,  # 整条 shell 命令串（含引号与 CFLAGS 语法）
        stdout=subprocess.PIPE,  # 捕获 stdout 供监控
        stderr=subprocess.PIPE,  # 捕获 stderr（编译错误也走这里）
        cwd=global_config.target.repo.working_dir,  # 目标（内核）仓库工作目录——make 必须在仓库根执行
        shell=True,  # 命令串需 shell 解释
        bufsize=1,  # 行缓冲，配合逐行监控
    )
    output, completed = monitor_build_output(process, -1)  # 实时读输出防管道涨死；-1 = 不设 warning 上限（正式找 bug 不限量，对应论文口径）
    Path("tmp-output").write_text(output)  # 构建日志落盘 tmp-output（事后排查编译/分析问题）


# -----------------------------------------------------------------------------
# scan_single_checker(checker_file, target_path, checker_id, arch, output_dir)
#   —— 单 checker 扫描入口（main.py 子命令 scan_single）
# 职责：读入一份 checker.cpp，经 global_config.backend 抽象层跑一次扫描——
#   backend.run_checker 按 target 类型分发到 _run_checker_linux / _run_checker_v8
#   （fork 增量的 V8/Chromium 支持，对应论文 Generability 讨论）。
# 参数：checker_file —— checker 源码路径；target_path —— 可选被分析对象（传了
#   只扫该对象，不传扫全库；差分验证场景传 patch 涉及对象）；checker_id ——
#   plugin 命名用 ID（默认 "SAGenTest"）；arch —— 目标架构；output_dir ——
#   输出目录（默认 result_dir/single_scan/{checker_id}）。
# 返回：int bug 数。错误码协议（与 backends/csa.py 约定）：-999 构建或扫描失败
#   （归一化为 -1 返回）；-1 超时；-10 报警过多被熔断；>=0 正常完成。
# -----------------------------------------------------------------------------
def scan_single_checker(
    checker_file: str,
    target_path: str = None,
    checker_id: str = None,
    arch: str = "x86",
    output_dir: str = None,
):
    """
    Scan a single file or directory using one checker.

    Args:
        checker_file (str): Path to the file containing the checker code
        target_path (str): Path to the specific file to scan (if None, scans whole directory)
        checker_id (str): Unique identifier for the checker (auto-generated if None)
        arch (str): Target architecture (default: x86)
        output_dir (str): Output directory for scan results (default: auto-generated)

    Returns:
        int: Number of bugs found, or -1 if scanning failed
    """
    # Validate inputs  ← 原注释：输入校验
    checker_file_path = Path(checker_file)  # 转 Path 做存在性检查
    if not checker_file_path.exists():  # checker 文件不存在直接失败
        logger.error(f"Checker file not found: {checker_file}")  # 记录错误路径
        return -1  # 约定错误码：失败

    # Read checker code  ← 原注释：读入 checker 源码
    try:  # 读文件可能抛 IO 异常（权限/编码等），单独兜底
        checker_code = checker_file_path.read_text()  # 读入 checker C++ 源码
        logger.info(f"Loaded checker from: {checker_file}")  # 确认装载成功
    except Exception as e:  # 任意读文件异常
        logger.error(f"Failed to read checker file: {e}")  # 记录异常细节
        return -1  # 失败返回

    # Generate checker ID if not provided  ← 原注释：缺省时生成 checker ID
    if checker_id is None:  # 调用方未指定 ID
        checker_id = "SAGenTest"  # 用默认 ID（与 backends/csa.py build_checker 的默认 checker_name 一致）

    # Setup output directory  ← 原注释：确定输出目录
    if output_dir is None:  # 未指定输出目录
        base_output_dir = Path(global_config.get("result_dir", "results"))  # 全局结果根目录（缺省 "results"）
        output_dir = base_output_dir / "single_scan" / checker_id  # 按 checker ID 隔离：result_dir/single_scan/{id}
    else:  # 调用方显式指定
        output_dir = Path(output_dir)  # 转 Path 统一类型

    output_dir.mkdir(parents=True, exist_ok=True)  # 递归建目录（已存在则复用）
    logger.info(f"Scan output directory: {output_dir}")  # 打印输出目录

    try:  # 扫描主流程整体兜底（backend 层异常不外泄给调用方）
        commit = global_config.get("scan_commit", "HEAD")  # 待扫描 commit（默认 HEAD 当前检出）
        jobs = global_config.get("jobs", 4)  # 并行度（默认 4）
        timeout = global_config.get("scan_timeout", 1800)  # 扫描超时秒数（默认 1800s=30min；论文 refine 场景限 1 小时，此处经配置对齐）

        # Determine what to analyze based on target_path  ← 原注释：按 target_path 决定分析范围
        object_to_analyze = target_path if target_path else None  # 被分析对象：指定则只扫它，否则 None = 全库（差分验证传 patch 涉及对象）

        if target_path:  # 指定对象分支
            logger.info(f"Scanning specific target: {target_path}")  # 提示定向扫描
        else:  # 未指定分支
            logger.info(f"Scanning entire directory with architecture: {arch}")  # 提示全库扫描

        # Use the backend to run the checker  ← 原注释：经 backend 抽象层执行
        bug_count = global_config.backend.run_checker(  # backend.run_checker（内部按 target._target_type 分发 linux/v8 实现）
            checker_code,  # checker 源码（backend 负责 build_checker 编译为 plugin）
            commit_id=commit,  # 目标 commit
            target=global_config.target,  # 目标仓库抽象（Linux/V8）
            object_to_analyze=object_to_analyze,  # None=全库；否则定向对象
            jobs=jobs,  # 并行度
            output_dir=str(output_dir),  # 报告输出目录
            arch=arch,  # 目标架构
            timeout=timeout,  # 超时
        )

        # Handle the results  ← 原注释：结果分发（错误码协议）
        if bug_count == -999:  # 错误码 -999：编译或扫描阶段失败
            logger.error("Failed to run the checker - build or scan error")  # error 级别记录
            return -1  # 向调用方归一化为 -1
        elif bug_count == -1:  # 错误码 -1：超时
            logger.warning("Scan timed out")  # warning 记录（结果不完整但非致命）
        elif bug_count == -10:  # 错误码 -10：报警过多触发熔断（对爆量 checker 的防护）
            logger.warning("Too many bugs found - scan may have been terminated")  # 提示扫描被提前终止
        elif bug_count >= 0:  # 正常完成
            logger.info(f"Scan completed successfully. Bugs found: {bug_count}")  # 汇报 bug 数

        # Create scan summary  ← 原注释：写扫描摘要
        _create_scan_summary(  # 写 scan_summary.md 供人工复核
            output_dir,  # 摘要落盘目录
            checker_id,  # checker 标识
            checker_file,  # checker 源文件
            target_path,  # 扫描对象（None=全库）
            arch,  # 架构
            bug_count,  # bug 数（含 -1/-10 等特殊码）
            bug_count >= 0,  # completed successfully if non-negative  ← 原注释：非负数才算完成
        )

        return bug_count  # 原样返回（含 -1/-10 特殊码，调用方自行判读）

    except Exception as e:  # 扫描执行期任意异常
        logger.error(f"Error during scan execution: {e}")  # 记录异常
        return -1  # 归一化失败


# -----------------------------------------------------------------------------
# _create_scan_summary(...) —— 私有辅助：写 scan_summary.md 扫描摘要
# 职责：把单次扫描的元信息（checker/目标/架构/时间/状态/bug 数）落成 markdown
#       摘要；bug 数 >0 时追加"下一步"指引（查日志/查 HTML 报告/人工甄别 FP）。
# 参数：output_dir —— 摘要写入目录；checker_id / checker_file / target_path /
#   arch —— 扫描元信息；bug_count —— bug 数（可为 -1/-10 特殊码）；
#   completed —— 是否正常完成（bug_count 非负）。
# 返回：无（写 output_dir/scan_summary.md）。
# 注意：summary_content 是三引号 f-string 模板，内部行属于字符串内容，不可插入注释。
# -----------------------------------------------------------------------------
def _create_scan_summary(
    output_dir: Path,
    checker_id: str,
    checker_file: str,
    target_path: str,
    arch: str,
    bug_count: int,
    completed: bool,
):
    """Create a summary of the scan results."""
    import datetime  # 函数内延迟 import（原仓风格：时间戳仅此处用到）

    # 下方整块三引号 f-string 是摘要模板，内联条件表达式填充各字段（此块内部不可加注释）
    summary_content = f"""# Single Checker Scan Summary

## Scan Information
- **Checker ID**: {checker_id}
- **Checker File**: {checker_file}
- **Target**: {"Whole directory" if target_path is None else target_path}
- **Architecture**: {arch}
- **Scan Time**: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Status**: {"Completed" if completed else "Timed out or interrupted"}

## Results
- **Bugs Found**: {bug_count}
- **Output Directory**: {output_dir.absolute()}

## Files Generated
- `scan_output.log`: Complete scan output
- `scan_summary.md`: This summary file
"""

    if bug_count > 0:  # 有报警时追加操作指引段（同为三引号 f-string，内部不可插注释）
        summary_content += f"""
## Next Steps
1. Review the scan output in `scan_output.log`
2. Check for HTML report files in the output directory
3. Analyze the reported issues for false positives
"""

    summary_file = output_dir / "scan_summary.md"  # 摘要文件路径
    summary_file.write_text(summary_content)  # 落盘
    logger.info(f"Scan summary saved to: {summary_file}")  # 记录落盘位置


# -----------------------------------------------------------------------------
# collect_reports(commit_report_dir, max_num_reports=100) —— 报告收集 + 蒸馏
# 职责：递归收集 scan-build 产出的报警 HTML，逐份做报告蒸馏（html2text 转
#   markdown + remove_text_section 删掉整段源码注释区，只留 Bug Summary 与
#   relevant lines——论文 §3.2"报告蒸馏"步骤），按被报警源文件分组返回。
# 参数：commit_report_dir —— 单次扫描的报告目录（含若干 *.html + index.html）；
#   max_num_reports —— 上限（默认 100，对应论文 refine 期间"最多 100 warnings"）。
# 返回：(file_reports, too_many)：file_reports = {源文件名: [(md, html), ...]}；
#   唯一文件数超上限时返回 ({}, True)。判据是唯一源文件数而非报告总数。
# -----------------------------------------------------------------------------
def collect_reports(commit_report_dir: str, max_num_reports=100) -> tuple[dict, bool]:
    """Collect reports from the given directory.

    Args:
        commit_report_dir (str): The directory path containing the reports.
        max_num_reports (int): The maximum number of reports to collect.
    Returns:
        tuple: A tuple containing a dictionary of file reports and a boolean indicating if there are too many reports.
    """
    commit_report_dir = Path(commit_report_dir)  # 转 Path 以便 rglob 递归遍历
    file_reports = defaultdict(list)  # 聚合容器：{源文件名: [(md, html), ...]}（同文件多条报警追加在列表里）

    # First pass: collect all reports and group by filename  ← 原注释：第一遍遍历，收集并按文件名分组
    for report_file in commit_report_dir.rglob("*.html"):  # 递归找全部报警 HTML（scan-build 每个报警一个文件）
        if report_file.stem == "index":  # 跳过 scan-build 的索引页（不是报警）
            continue

        html_content = report_file.read_text()  # 读原始 HTML（后续分流落档还要用）
        md_content = html2text(html_content)  # HTML -> markdown（triage agent 的阅读格式）
        md_content = remove_text_section(md_content, html_content)  # 蒸馏：删 "### Annotated Source Code" 起的整段源码并回填精简源码（relevant lines）

        # Extract filename from the title tag  ← 原注释：从 <title> 提取被报警文件名
        title_pattern = re.compile(r"<title>(.+)</title>")  # CSA 报告的 title 即被报警源文件路径
        match = title_pattern.search("\n".join(html_content.splitlines()[:100]))  # 只在 HTML 前 100 行找（title 在头部，避免正文大段源码拖慢匹配）
        if match:  # 命中
            file_name = match.group(1)  # 取 title 文本 = 源文件路径
        else:  # 未命中（异常报告）
            file_name = "default"  # 兜底名，全部归入同组
        file_name = file_name.replace("/", "_").replace(".c", "").replace(".h", "")  # 路径清洗：斜杠换下划线、去 .c/.h 后缀（后续用作文件名/目录名）
        file_reports[file_name].append((md_content, html_content))  # (蒸馏后 md, 原始 html) 成对入组

    # Count unique filenames instead of total HTML files  ← 原注释：判据用唯一文件数而非 HTML 总数
    num_unique_files = len(file_reports)  # 唯一被报警文件数（同文件多条报警算一个）
    logger.info(f"Number of unique files with reports: {num_unique_files}")  # 汇报规模
    if num_unique_files > max_num_reports:  # 超上限：报警面过宽（论文视为 checker 匹配过宽的信号）
        logger.warning(f"Too many reports: {num_unique_files}!")  # 警告
        return {}, True  # 空结果 + too_many 旗标（调用方将放弃该 checker 的 triage）

    return file_reports, False  # 正常返回分组结果


# -----------------------------------------------------------------------------
# triage_report(report_dir) —— 最终报告分诊调度（main.py 子命令 triage）
# 职责：遍历 report_dir 下每个 checker 子目录（一次批量扫描的产物），加载该
#   checker 的 pattern/patch，取最新一轮扫描报告，逐"被报警文件"调 triage
#   agent（agent.check_report，论文 §3.2：判定报告是否对齐目标 bug pattern 而
#   非一般代码正确性），按 Decision: Bug/NotABug 分流 is_bug / is_not_bug，
#   汇总产出 triage_report.csv。
# 参数：report_dir —— 批量扫描结果根目录（其下每个子目录 = 一个 checker）。
# 返回：无（产物：各 checker 的 triage_output/{check_reports,is_bug,is_not_bug,
#   bug_files.txt} + 根目录 triage_report.csv）。
# 缓存：{file_name}.check 存在则直接复用 triage 结果——断点续跑不重烧 LLM 调用。
# -----------------------------------------------------------------------------
def triage_report(report_dir):
    """
    Go through all the html files and triage them.

    Args:
        report_dir (str): The directory path containing the reports.
    """
    report_dir = Path(report_dir)  # 转 Path 以便 iterdir
    commit_bug_num = {}  # 汇总表：{checker 目录名: (bug 数, not-bug 数)}

    for checker_dir in report_dir.iterdir():  # 逐 checker 处理（每个子目录 = 一个 checker 的一轮批量扫描产物）
        if not checker_dir.is_dir():  # 跳过非目录项
            continue
        logger.info(f"Processing {checker_dir.name}...")  # 汇报当前 checker

        checker_data = CheckerData.load_checker_data_from_dir(checker_dir)  # 反序列化该 checker 的元数据（pattern/patch/源码等）
        triage_output_dir = checker_dir / "triage_output"  # 本 checker 的 triage 产物根目录

        md_report_dir = triage_output_dir / "kernel_reports_md"  # 报告 md 归档目录（预留位）
        md_report_dir.mkdir(parents=True, exist_ok=True)  # 递归创建

        final_report_dir = None  # 待定位的"最新一轮扫描报告"目录
        for i in range(10, -1, -1):  # 从 scan-reports-10 倒序找到 scan-reports-0：编号越大轮次越新
            temp_dir = checker_dir / f"scan-reports-{i}" / "main-report"  # 每轮扫描的报告主目录约定路径
            if temp_dir.exists() and temp_dir.is_dir():  # 取第一个存在的（即最新一轮）
                final_report_dir = temp_dir  # 记录
                break  # 停止回溯
        if final_report_dir is None:  # 没有任何扫描报告
            logger.warning("No final report found!")  # 警告
            continue  # 跳过该 checker
        logger.info(f"Final report directory: {final_report_dir}")  # 汇报选定轮次

        # Collect reports  ← 原注释：收集并蒸馏该轮报告
        file_reports, too_many_reports = collect_reports(final_report_dir)  # 默认 max_num_reports=100（论文 refine 期上限）
        if too_many_reports:  # 超 100 唯一文件：匹配过宽，无法逐条 triage
            logger.warning("Too many reports!")  # 警告
            continue  # 放弃该 checker

        check_report_dir = triage_output_dir / "check_reports"  # triage 输入留档 + 结果缓存目录
        check_report_dir.mkdir(parents=True, exist_ok=True)  # 递归创建

        is_bug_dir = triage_output_dir / "is_bug"  # TP 分流目录（triage 判为真报警）
        is_not_bug_dir = triage_output_dir / "is_not_bug"  # FP 分流目录（triage 判为误报）
        is_bug_dir.mkdir(parents=True, exist_ok=True)  # 创建 TP 目录
        is_not_bug_dir.mkdir(parents=True, exist_ok=True)  # 创建 FP 目录

        pattern = checker_data.pattern  # 目标 bug pattern（triage 的对齐标尺——判"是否该 pattern 意义上的 bug"而非泛泛代码正确性）
        patch = checker_data.patch  # 源头 bug-fix patch（给 triage agent 提供模式来源上下文）
        num_bug = 0  # TP 计数
        num_not_bug = 0  # FP 计数
        bug_files = []  # TP 文件名清单（refine agent 的输入素材）
        for file_name, reports in file_reports.items():  # 逐被报警文件 triage
            logger.info(f"Triaging {file_name}...")  # 汇报进度

            file_name = (  # 二次清洗（比 collect_reports 多 ".."->"--" 与 strip）：确保能安全用作本地文件名
                file_name.replace("/", "_")
                .replace(".c", "")
                .replace(".h", "")
                .replace("..", "--")
                .strip()
            )
            # We only consider the first report for each file  ← 原注释：每文件只取第一条报告
            md_content = reports[0][0]  # 首条报告的蒸馏 md（同文件多条报警视为同源，省 LLM 调用）
            html_content = reports[0][1]  # 首条报告的原始 html

            (check_report_dir / f"{file_name}.md").write_text(md_content)  # triage 输入留档（md 版）
            (check_report_dir / f"{file_name}.html").write_text(html_content)  # triage 输入留档（html 版）

            check_report_file = check_report_dir / f"{file_name}.check"  # triage 结果缓存文件路径
            if check_report_file.exists():  # 已 triage 过（断点续跑）
                check_result = check_report_file.read_text()  # 直接复用缓存，不再调 LLM
            else:  # 未 triage 过
                check_result = check_report(  # 调 triage agent（论文 §3.2）：prompt = check_report.md 模板填 report/pattern/patch，temperature=0.01
                    checker_dir.name, 0, file_name, md_content, pattern, patch  # 实参 = (id, iter=0, report_id, 报告md, 目标pattern, 源patch)
                )
                check_report_file.write_text(check_result)  # 写缓存（下次续跑直接命中）

            if "NotABug" in check_result:  # triage agent 输出约定 "Decision: {Bug/NotABug}"；子串命中 NotABug = FP（注意正文任意位置出现该词也会命中，较脆弱）
                num_not_bug += 1  # FP 计数

                (is_not_bug_dir / f"{file_name}.md").write_text(md_content)  # FP 分流：md
                (is_not_bug_dir / f"{file_name}.html").write_text(html_content)  # FP 分流：html
                (is_not_bug_dir / f"{file_name}.check").write_text(check_result)  # FP 分流：triage 判词
            else:  # 判为 Bug（TP）
                num_bug += 1  # TP 计数
                bug_files.append(file_name)  # 记入 TP 清单

                (is_bug_dir / f"{file_name}.md").write_text(md_content)  # TP 分流：md
                (is_bug_dir / f"{file_name}.html").write_text(html_content)  # TP 分流：html
                (is_bug_dir / f"{file_name}.check").write_text(check_result)  # TP 分流：triage 判词

        commit_bug_num[checker_dir.name] = (num_bug, num_not_bug)  # 登记该 checker 的 (TP, FP) 计数
        (triage_output_dir / "bug_files.txt").write_text("\n".join(bug_files))  # TP 文件清单落盘（后续 refinement 的输入）

    logger.warning("finish")  # 全部 checker 处理完（原样用 warning 级别）
    answer_text = f"Commit ID,Num_Bugs,Num_Not_Bugs\n"  # CSV 表头（checker 目录名即 commit ID）
    for commit_id, (num_bug, num_not_bug) in commit_bug_num.items():  # 逐 checker 汇总成行
        answer_text += f"{commit_id},{num_bug},{num_not_bug}\n"  # 追加一行：commit,TP数,FP数
    (report_dir / "triage_report.csv").write_text(answer_text)  # 总表落盘（人工复核入口）
