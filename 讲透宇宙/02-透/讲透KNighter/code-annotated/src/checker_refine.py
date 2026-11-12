# =============================================================================
# 【模块定位】KNighter 阶段二 Checker Refinement 的驱动层（编排 + 进度跟踪 + 状态
#             盘点 + 日志落盘）。真正的"单轮 refine 核心"（扫描→采样→triage→
#             repair_FP→双准则验证）在同文件 715 行之后，由后续批次注释。
#
# 【论文映射】SOSP'25 论文《KNighter: Transforming Static Analysis with
#             LLM-Synthesized Checkers》(arXiv:2503.09002v3) §3.2 Checker
#             Refinement 的实现：
#             - refine 对象 = 阶段一（§3.1 Algorithm 1）validation 通过的 valid
#               checker（差分验证 N_buggy > N_patched 且 N_patched < T_valid）；
#             - "最多 3 轮 refine" → 本文件 max_tries=3（refine_checker /
#               refine_checker_with_max_attempts 两级默认值）；
#             - "采样 5 条报告 triage" → global_config.max_fp_reports_for_refinement
#               （默认 5），在 715 行后的 _process_reports* 中消费；
#             - triage agent = agent.check_report（判 NotABug 即 FP）、
#               refinement agent = agent.repair_FP（依 FP 报告改 checker 逻辑，如
#               学会 unlikely() 宏是合法空检查），均在 715 行后的
#               refine_checker_attempt/_triage_reports/_refine_false_positives 中调用；
#             - 双准则接受 = (1) 原 FP 对象不再报警（_validate_on_objects /
#               _scan_objects）+ (2) 仍通过 buggy/patched 差分验证
#               （_validate_on_commit）——均在 715 行后。
#             注：论文口径的 refine 期扫描预算"1 小时或 100 warnings"由后端与
#             group scan 路径控制（global_config.group_scan_timeout=3600，
#             checker_scan.py 消费）；本文件每轮 attempt 的扫描限时走
#             global_config.scan_timeout（默认 600s）参数透传。
#
# 【管线角色】上游：checker_gen.py（阶段一合成，产出 KN-* checker 子目录，含
#             checker.yaml/pattern/plan/checker-repaired.cpp）；入口：main.py 的
#             refine / refine_status / refine_unrefined 三种模式全部路由到本文件；
#             下游：src/backends/csa.py（run_checker 编译+扫描、extract_reports
#             报告蒸馏采样、validate_checker 差分验证）与 agent.py（LLM agent）。
#
# 【全文件结构】（"※"= 本批已注释（原 1-714 行），"…"= 715 行起、后批注释）
#   ※ refine_checker ...................... refine 主入口：过滤 valid checker 后逐个
#                                          调 refine_checker_with_max_attempts
#   ※ _create/_update/_finalize_progress_tracker ... refinement_progress.log 三件套
#   ※ check_refinement_status ............. 离线盘点所有 checker 的 refine 状态
#   ※ list_successfully_changed_checkers .. 只列"真改了代码"的 checker
#   ※ refine_unrefined_checkers ........... 断点续跑：只 refine 尚未成功的 checker
#   ※ refine_checker_with_max_attempts .... 单 checker ≤3 轮 refine 状态机（含扫描
#                                          结果复用）
#   ※ _log_attempt_result ................. 单轮结果日志（含 killed objects 聚合）
#   ※ _check_code_changed ................. "名义 refined"vs"真改码"鉴别器
#   ※ _log_refine_results ................. 跨轮汇总日志（本批注释至原 714 行截止，
#                                          函数尾部 715-731 行归后批）
#   … _save_refine_log_to_file ............ 把汇总日志写成 refinement_logs/*.md
#                                          + <id>_status.txt（供本文件
#                                          check_refinement_status 回读解析）
#   … create_refinement_summary ........... refinements/README.md 汇总表
#   … refine_checker_attempt .............. 单轮核心：扫描→采样→triage→FP 修复→
#                                          双准则验证（论文 §3.2 主流程）
#   … _initialize_refinement .............. 起点代码先过一次编译（repair_checker）
#   … _scan_target .................... 调 backend.run_checker 全库扫描
#   … _process_reports / _process_reports_with_count .. 报告采样（seed 复现）
#   … _convert_override_reports_to_report_data ....... group scan 报告注入转换
#   … _triage_reports ..................... triage agent 逐报告判 TP/FP
#   … _refine_false_positives ............. 对每个 FP 报告跑 refinement agent
#   … _attempt_report_refinement .......... repair_FP→抽代码→编译修复→双准则验证
#   … _validate_on_objects / _validate_on_commit ..... 双准则接受（论文两条件）
#   … _scan_remaining_objects / _scan_objects / get_object_id .. 对象级复扫
#
# 【关键依赖与坑】
#   1. CheckerData.is_valid ≡ tp_score>0 且 tn_score>0（阶段一差分验证得分），
#      invalid checker 一律跳过——refine 只作用于 valid checker（论文 §3.2 前提）。
#   2. refine_checker 的 max_fp_reports 形参实际未被函数体使用（采样数真正来源是
#      global_config.max_fp_reports_for_refinement），传了也白传。
#   3. _finalize_progress_tracker 统计的 "SKIPPED:" 在本文件中没有任何写入方，
#      skipped_count 恒为 0（invalid checker 在进循环前就被过滤、不写 tracker）。
#   4. refine_checker_with_max_attempts 的 timeout 形参默认 900，但两个调用方都
#      显式传 global_config.scan_timeout（默认 600），默认值是摆设。
#   5. reports_override 注入点（group scan 批量报告直接喂 refine）在当前仓内无
#      外部调用方，属预留扩展位（fork 增量的 group 扫描线）。
#   6. 状态文件 <id>_status.txt 的六段格式由 _save_refine_log_to_file 写出、由
#      本文件 check_refinement_status 解析——读写两端分居 714 行边界两侧，改格式
#      必须两头同步。
#   7. RefinementResult.attempt_id = attempt+1（0-based 循环变量落盘为 1-based），
#      而 last_scan_id 复用的是 0-based 的 attempt，两者口径不同，阅读时留意。
# =============================================================================
from pathlib import Path  # Path 对象：checker 目录/日志路径统一处理
from typing import Dict, List, Optional, Set  # 类型标注（Set 用于 error_objects 聚合）

# LLM agent 层：check_report=论文 §3.2 的 triage agent（判报告是否 FP）；
#              repair_FP=论文 §3.2 的 refinement agent（依 FP 反馈改 checker）
from agent import check_report, repair_FP
from checker_data import (  # pydantic 数据模型 + checker 目录状态（详见各字段注释）
    CHECKER_ID_PREFIX,  # 常量 "KN-"：所有 checker 子目录名的前缀（checker_id = KN-{commit_type}-{commit_id[:8]}-{index}）
    CheckerData,  # 单个 checker 的完整状态：commit/pattern/plan/代码/tp_score/tn_score/output_dir 等
    RefineAttempt,  # 对一个 FP 报告的一次 refine 尝试（refine_id/三轮代码快照/killed_objects/reasoning_process）
    RefinementResult,  # 一轮 refine 的结果（refined/result/num_TP/num_FP/num_reports/refine_attempt_list/error_objects）
    ReportData,  # 单条扫描报告（report_id/report_content/report_triage/report_objects）
)
from checker_repair import repair_checker  # 语法修复 agent 循环（论文 §3.1.3 的 repair 在 refine 阶段复用，最多 4 次）
from global_config import global_config, logger  # 全局配置（YAML 加载）与统一 logger
from tools import extract_checker_code  # 从 LLM 回复中抠出 ```cpp fence 内的 checker 代码


# =============================================================================
# 【函数】refine_checker —— 论文 §3.2 阶段二的批处理主入口（main.py "refine" 模式）
# 【职责】对 checker_dir 下所有 *valid* checker 逐个执行"最多 max_tries(=3) 轮"的
#         refinement（论文："最多 3 轮 refine"），并维护进度日志。
# 【参数】checker_dir     —— checker 子目录的父目录（阶段一产出，子目录名以 KN- 开头）
#         scan           —— 是否真的用 checker 扫全库（False 则复用既有扫描报告）
#         max_tries      —— 每个 checker 最多 refine 轮数，默认 3（论文口径）
#         max_fp_reports —— 【坑】形参未使用；采样条数实际由
#                           global_config.max_fp_reports_for_refinement（默认 5）决定
# 【返回】None（结果全部落盘 + logger 输出）
# =============================================================================
def refine_checker(checker_dir, scan=True, max_tries=3, max_fp_reports=None):
    """
    This will refine tha *valid* checkers under the checker_dir.

    Args:
        checker_dir (str): The directory containing the checker subdirs.
        scan (bool): Whether to scan the kernel with the checker.
        max_tries (int): The maximum number of attempts to refine the checker.
        max_fp_reports (int): Maximum number of FP reports to use for refinement (defaults to config).
    """
    # ↑ 原 docstring 原样保留（docstring 是 AST 节点，禁止改动；注意原文 "tha" 为上游笔误）
    checker_dir = Path(checker_dir)  # 统一转成 Path，后续 iterdir()/路径拼接才可用

    # Initialize progress tracking
    # 在 checker_dir 下创建 refinement_progress.log 并写入头块（时间戳+基目录）
    progress_tracker = _create_progress_tracker(checker_dir)

    # Get all checker directories
    # 枚举 checker_dir 下一层子目录，只留目录名以 "KN-"（CHECKER_ID_PREFIX）开头的
    # ——这是阶段一 checker_gen.py 产出的命名约定，可过滤掉日志/杂项目录
    all_checker_subdirs = [
        subdir  # 列表推导式元素：checker 子目录 Path
        for subdir in checker_dir.iterdir()  # 遍历第一层子项
        if subdir.is_dir() and subdir.name.startswith(CHECKER_ID_PREFIX)  # 双条件：是目录 且 名字带 KN- 前缀
    ]

    # Filter out invalid checkers first
    # 先做一轮有效性过滤：只有阶段一差分验证通过（is_valid）的 checker 才值得 refine
    valid_checker_subdirs = []  # 通过过滤、待 refine 的 checker 子目录
    invalid_checker_count = 0  # 被过滤掉的 invalid/损坏 checker 计数（仅日志用途）

    logger.info(f"Found {len(all_checker_subdirs)} checker directories, validating...")

    for checker_subdir in all_checker_subdirs:  # 逐个加载校验
        try:
            checker_data = CheckerData.load_checker_data_from_dir(checker_subdir)  # 从子目录的 yaml/落盘文件恢复 CheckerData 对象
            if checker_data.is_valid:  # is_valid ≡ tp_score>0 且 tn_score>0（阶段一差分验证得分）
                valid_checker_subdirs.append(checker_subdir)  # valid → 进入 refine 名单
            else:
                invalid_checker_count += 1  # invalid → 计数并告警跳过（refine 的对象只能是 valid checker，论文 §3.2）
                logger.warning(
                    f"[INVALID] Checker {checker_data.checker_id} is not valid - skipping"
                )
        except Exception as e:  # 子目录损坏/文件缺失等加载异常同样按 invalid 处理，不让单个坏目录炸掉整批
            invalid_checker_count += 1
            logger.error(
                f"[INVALID] Error loading checker {checker_subdir.name}: {e} - skipping"
            )

    if invalid_checker_count > 0:  # 有过滤发生时打一条汇总（0 个则静默）
        logger.info(f"Filtered out {invalid_checker_count} invalid checkers")

    logger.info(
        f"Starting refinement of {len(valid_checker_subdirs)} valid checkers in {checker_dir}"
    )
    # tracker 同步记录开工信息（首行进度，含 checker 总数）
    _update_progress_tracker(
        progress_tracker,
        f"Starting refinement of {len(valid_checker_subdirs)} valid checkers",
    )

    for i, checker_subdir in enumerate(valid_checker_subdirs):  # 主循环：逐 checker refine
        logger.info(
            f"[{i+1}/{len(valid_checker_subdirs)}] Refining checker {checker_subdir}..."
        )  # 1-based 进度序号（i+1）
        _update_progress_tracker(
            progress_tracker,
            f"[{i+1}/{len(valid_checker_subdirs)}] Processing {checker_subdir.name}",
        )

        try:  # 单 checker 失败只记日志，继续下一个（批量任务的隔离策略）
            checker_data = CheckerData.load_checker_data_from_dir(checker_subdir)  # 再次加载（前面过滤时加载过一次，这里重新实例化）

            # Update the output_dir to the checker and dump it to the new output_dir
            # 把 CheckerData 的基地址重定位到本次运行的 result_dir，并把状态快照
            # dump 到新目录——保证本轮 refine 的全部产物（报告/代码/日志）写进新目录
            checker_data.update_base_result_dir(global_config.result_dir)
            checker_data.dump_dir()  # 落盘 patch/pattern/plan/checker-*.cpp/score.txt 等状态快照

            # Use the improved refine logic with max attempts and logging
            # 核心：带"最多 max_tries 轮 + 扫描复用 + 全程日志"的 refine 状态机；
            # timeout 用 global_config.scan_timeout（默认 600s）覆盖形参默认 900
            refine_results = refine_checker_with_max_attempts(
                checker_data,
                scan=scan,
                max_tries=max_tries,
                timeout=global_config.scan_timeout,
            )

            # Log the final results
            # 汇总日志（成功数/真改码数/逐轮指标演进），并调 _save_refine_log_to_file 落盘
            _log_refine_results(
                checker_data.checker_id, refine_results, Path(checker_data.output_dir)
            )

            # Update progress tracker with result
            final_status = refine_results[-1].result if refine_results else "No Results"  # 最后一轮的状态串（Perfect/Refined/High-TP/...）；空列表兜底 "No Results"
            success = any(r.refined for r in refine_results)  # 任一轮达成 refined 即算 SUCCESS（论文口径的"refine 成功"）
            _update_progress_tracker(
                progress_tracker,
                f"COMPLETED: {checker_data.checker_id} - {final_status} ({'SUCCESS' if success else 'FAILED'})",
            )  # "COMPLETED:"/"SUCCESS" 关键词供 _finalize_progress_tracker 回读统计，不能随意改词

        except Exception as e:  # 任何异常（加载/扫描/LLM/IO）都吞掉，写 "ERROR:" 进 tracker
            logger.error(f"Error processing checker {checker_subdir}: {e}")
            _update_progress_tracker(
                progress_tracker, f"ERROR: {checker_subdir.name} - {str(e)}"
            )

    # Finalize progress tracking
    # 收尾：给 tracker 追加 Completion Summary（完成/成功/错误计数）
    _finalize_progress_tracker(progress_tracker)
    logger.info(f"Refinement process completed for directory: {checker_dir}")


# =============================================================================
# 【函数】_create_progress_tracker —— 进度日志三件套之一：创建
# 【职责】在 base_dir 下新建 refinement_progress.log，写入头块（标题/生成时间/
#         基目录绝对路径）。长跑任务（每 checker 一轮全库扫描 10 分钟级 × N 个
#         checker）需要断点可观测的心跳文件。
# 【参数】base_dir —— checker 目录（tracker 与 checker 同目录，便于一并归档）
# 【返回】progress_file 的 Path（后续 _update/_finalize 都往它追加）
# 【坑】    每次调用都会覆盖重写同名日志（write_text 非追加）——同一目录二次
#           refine 会清掉上一轮的进度记录
# =============================================================================
def _create_progress_tracker(base_dir: Path) -> Path:
    """Create a progress tracking file for the refinement process."""
    import datetime  # 函数内局部导入 datetime（仅此处用，避免模块级导入）

    progress_file = base_dir / "refinement_progress.log"  # 日志路径：<checker_dir>/refinement_progress.log

    # f-string 三引号头块：Markdown 风格——标题、生成时间（%Y-%m-%d %H:%M:%S）、基目录绝对路径
    header = f"""# Refinement Progress Log
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Base Directory: {base_dir.absolute()}

## Progress Log
"""
    progress_file.write_text(header)  # 覆盖写（同目录重跑会清旧日志，见上"坑"）
    logger.info(f"Progress tracking initialized: {progress_file}")
    return progress_file


# =============================================================================
# 【函数】_update_progress_tracker —— 进度日志三件套之二：追加
# 【职责】向 tracker 追加一行 "[HH:MM:SS] message" 心跳。所有长耗时步骤（开工/
#         每个 checker 开始/完成/出错）都会调用，形成可 tail -f 的时间线。
# 【参数】progress_file —— _create_progress_tracker 返回的路径
#         message      —— 事件文本（含 "COMPLETED:"/"ERROR:"/"SUCCESS" 等约定
#                         关键词，_finalize 靠它们做统计）
# 【返回】None
# 【坑】    写失败（如目录被删）只记 error 不抛异常——日志永远不能拖崩主流程
# =============================================================================
def _update_progress_tracker(progress_file: Path, message: str) -> None:
    """Update the progress tracking file with a new message."""
    import datetime  # 局部导入，同上

    try:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")  # 只到时分秒（日期在头块）
        log_entry = f"[{timestamp}] {message}\n"  # 拼成一行心跳记录

        # Append to the file
        with open(progress_file, "a") as f:  # 追加模式，多进程/多次调用不覆盖
            f.write(log_entry)
    except Exception as e:  # 日志写失败不中断 refine 主流程
        logger.error(f"Failed to update progress tracker: {e}")


# =============================================================================
# 【函数】_finalize_progress_tracker —— 进度日志三件套之三：收尾统计
# 【职责】读回 tracker 全文，按行内关键词统计完成/成功/跳过/错误数，追加
#         "## Completion Summary" 段（含完成时间戳与四项计数）后整体重写文件。
# 【参数】progress_file —— tracker 路径
# 【返回】None
# 【坑】    skipped_count 统计的是 "SKIPPED:" 关键词，但本文件没有任何写入方写
#           这个前缀（invalid checker 在进循环前就被过滤，不写 tracker），
#           所以 Skipped (Invalid) 恒为 0——预留字段，实际无效
# =============================================================================
def _finalize_progress_tracker(progress_file: Path) -> None:
    """Finalize the progress tracking file with summary information."""
    import datetime  # 局部导入，同上

    try:
        # Read current content
        current_content = progress_file.read_text()  # 先整体读回（后面要整体重写）

        # Add completion timestamp
        completion_info = f"\n## Completion Summary\nProcess completed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"  # Markdown 二级标题 + 完成时间

        # Count success/failure/skipped from the log
        lines = current_content.split("\n")  # 按行拆开做关键词统计
        completed_count = len([line for line in lines if "COMPLETED:" in line])  # 走完流程的 checker 数（成功+失败都算 COMPLETED）
        skipped_count = len([line for line in lines if "SKIPPED:" in line])  # 恒 0（无写入方，见函数头"坑"）
        error_count = len([line for line in lines if "ERROR:" in line])  # 处理中途抛异常的 checker 数
        success_count = len(
            [line for line in lines if "COMPLETED:" in line and "SUCCESS" in line]  # COMPLETED 行内再含 SUCCESS（任一轮 refined=True）
        )

        # 逐行拼出四项计数（Markdown 列表）
        completion_info += f"- Total Processed: {completed_count}\n"
        completion_info += f"- Successful Refinements: {success_count}\n"
        completion_info += f"- Skipped (Invalid): {skipped_count}\n"
        completion_info += f"- Errors: {error_count}\n"

        # Write back to file
        progress_file.write_text(current_content + completion_info)  # 原文 + 统计段整体重写
        logger.info(f"Progress tracking completed: {progress_file}")

    except Exception as e:  # 同样：收尾失败不抛异常
        logger.error(f"Failed to finalize progress tracker: {e}")


# =============================================================================
# 【函数】check_refinement_status —— 离线盘点 refine 状态（main.py "refine_status" 模式）
# 【职责】不发 LLM、不扫描，纯读盘：逐 checker 解析
#         <output_dir>/refinement_logs/<checker_id>_status.txt，分桶统计。
# 【参数】checker_dir —— checker 子目录父目录
#         detailed   —— True 时额外打印每类 checker 的明细列表
# 【返回】Dict：refined / not_refined / invalid / no_logs 四个列表 + summary 字典
#         （含 refinement_rate、code_change_rate 百分比）
# 【状态文件格式】六段竖线分隔：
#         checker_id|attempts|successful|code_changed_attempts|final_code_changed|final_status
#         由 715 行后的 _save_refine_log_to_file 写出（读写两端分居批次边界，
#         改格式须两头同步）；final_code_changed 取值 "True"/"False" 字符串
# 【旧格式兼容】len(parts)>=4 且 <6 时按旧四段格式解析（无 code_changed 字段，
#         相应字段填默认值）；再短则归入 no_logs
# =============================================================================
def check_refinement_status(
    checker_dir: str, detailed: bool = False
) -> Dict[str, Dict]:
    """
    Check the refinement status of all checkers in a directory.

    Args:
        checker_dir: Directory containing checker subdirectories
        detailed: If True, provide detailed status information

    Returns:
        Dictionary with checker status information
    """
    checker_dir = Path(checker_dir)  # 转 Path
    status_info = {  # 返回值骨架：四桶 + 汇总
        "refined": [],  # successful>0：至少一轮 refine 成功
        "not_refined": [],  # 有状态日志但从无成功轮
        "invalid": [],  # is_valid=False 的 checker（只有 id 字符串，无详情）
        "no_logs": [],  # 找不到状态文件/解析不出（从未 refine 过或产物丢失）
        "summary": {},  # 后面填充的计数汇总
    }

    logger.info(f"Checking refinement status in: {checker_dir}")

    # Get all checker directories
    # 与 refine_checker 相同的枚举逻辑：一层子目录 + KN- 前缀过滤
    checker_subdirs = [
        subdir
        for subdir in checker_dir.iterdir()
        if subdir.is_dir() and subdir.name.startswith(CHECKER_ID_PREFIX)
    ]

    for checker_subdir in checker_subdirs:  # 逐 checker 盘点
        checker_id = checker_subdir.name  # 目录名即 checker_id

        try:
            # Load checker data
            checker_data = CheckerData.load_checker_data_from_dir(checker_subdir)  # 恢复 CheckerData（拿 output_dir 与 is_valid）

            if not checker_data.is_valid:  # 阶段一 validation 没过 → invalid 桶
                status_info["invalid"].append(checker_id)
                continue

            # Check for refinement logs
            log_dir = Path(checker_data.output_dir) / "refinement_logs"  # 状态日志目录（由 _save_refine_log_to_file 创建）
            status_file = log_dir / f"{checker_id}_status.txt"  # 机器可读状态文件（六段竖线格式）
            log_file = log_dir / f"{checker_id}_refinement.md"  # 人类可读 Markdown 日志（可选存在）

            if status_file.exists():
                # Parse status file: checker_id|attempts|successful|code_changed_attempts|final_code_changed|final_status
                status_content = status_file.read_text().strip()  # 读出并去首尾空白
                parts = status_content.split("|")  # 按竖线切段

                if len(parts) >= 6:  # 新六段格式（含 code_changed 两列）
                    attempts = int(parts[1])  # 总 refine 轮数
                    successful = int(parts[2])  # refined=True 的轮数
                    code_changed_attempts = int(parts[3])  # "真改了代码"的轮数（_check_code_changed 口径）
                    final_code_changed = parts[4].lower() == "true"  # 最后一轮是否真改码（"True"/"False" 字符串转 bool）
                    final_status = parts[5]  # 最后一轮状态串（Perfect/Refined/High-TP/...）

                    checker_info = {  # 该 checker 的详情字典（进 refined/not_refined 桶的元素）
                        "checker_id": checker_id,
                        "attempts": attempts,
                        "successful_refinements": successful,
                        "code_changed_attempts": code_changed_attempts,
                        "final_code_changed": final_code_changed,
                        "final_status": final_status,
                        "is_refined": successful > 0,  # "refine 成功"判定：任一轮 refined 即可
                        "is_code_changed": final_code_changed,  # "真改码"判定（更严：LLM 返回的代码确实变了且验证通过）
                        "log_file": str(log_file) if log_file.exists() else None,  # Markdown 日志路径（存在才给）
                        "output_dir": checker_data.output_dir,
                    }

                    if successful > 0:  # 分桶：成功过 → refined
                        status_info["refined"].append(checker_info)
                    else:  # 从未成功 → not_refined
                        status_info["not_refined"].append(checker_info)
                elif len(parts) >= 4:
                    # Handle old format for backward compatibility
                    # 旧四段格式：checker_id|attempts|successful|final_status（无 code_changed 列）
                    attempts = int(parts[1])
                    successful = int(parts[2])
                    final_status = parts[3]

                    checker_info = {  # 同构详情字典，code_changed 相关字段填"未知"默认值
                        "checker_id": checker_id,
                        "attempts": attempts,
                        "successful_refinements": successful,
                        "code_changed_attempts": 0,  # Unknown for old format
                        "final_code_changed": False,  # Unknown for old format
                        "final_status": final_status,
                        "is_refined": successful > 0,
                        "is_code_changed": False,  # 旧格式无从判断，保守置 False
                        "log_file": str(log_file) if log_file.exists() else None,
                        "output_dir": checker_data.output_dir,
                    }

                    if successful > 0:  # 分桶逻辑与新版一致
                        status_info["refined"].append(checker_info)
                    else:
                        status_info["not_refined"].append(checker_info)
                else:  # 段数既不足 6 也不足 4 → 视为无有效日志
                    status_info["no_logs"].append(checker_id)
            else:  # 状态文件不存在 → 从未 refine 过（或产物丢了）
                status_info["no_logs"].append(checker_id)

        except Exception as e:  # 加载/解析异常也归 no_logs（保证盘点永不中途崩溃）
            logger.error(f"Error checking status for {checker_id}: {e}")
            status_info["no_logs"].append(checker_id)

    # Create summary
    total_checkers = len(checker_subdirs)  # 分母：所有 KN-* 目录（含 invalid/no_logs）

    # Count code changes
    # "真改码"计数只在 refined/not_refined 两桶里找（这两桶的元素才是详情字典）
    code_changed_count = 0
    for info in status_info["refined"] + status_info["not_refined"]:
        if info.get("final_code_changed", False):  # .get 兜底：旧格式无该键
            code_changed_count += 1

    status_info["summary"] = {  # 汇总字典：六项计数 + 两项百分比
        "total_checkers": total_checkers,
        "refined_count": len(status_info["refined"]),
        "not_refined_count": len(status_info["not_refined"]),
        "invalid_count": len(status_info["invalid"]),
        "no_logs_count": len(status_info["no_logs"]),
        "code_changed_count": code_changed_count,
        "refinement_rate": len(status_info["refined"]) / total_checkers * 100  # refine 成功率（%）
        if total_checkers > 0  # 分母为零（空目录）时直接给 0，防除零
        else 0,
        "code_change_rate": code_changed_count / total_checkers * 100  # 真改码率（%）——比 refinement_rate 更严的口径
        if total_checkers > 0
        else 0,
    }

    # Print summary
    # 控制台汇总（带符号前缀便于人眼扫读；✓✗🔧⚠? 为原代码字符，保留）
    summary = status_info["summary"]
    logger.info(f"=== Refinement Status Summary ===")
    logger.info(f"Total checkers: {summary['total_checkers']}")
    logger.info(f"✓ Successfully refined: {summary['refined_count']}")
    logger.info(f"✗ Not refined: {summary['not_refined_count']}")
    logger.info(f"🔧 Code actually changed: {summary['code_changed_count']}")  # 真改码数（与上行 refined 数对照可看出"空 refine"占比）
    logger.info(f"⚠ Invalid checkers: {summary['invalid_count']}")
    logger.info(f"? No refinement logs: {summary['no_logs_count']}")
    logger.info(f"Refinement rate: {summary['refinement_rate']:.1f}%")
    logger.info(f"Code change rate: {summary['code_change_rate']:.1f}%")

    if detailed:  # detailed=True：逐 checker 明细
        logger.info(f"\n=== Detailed Status ===")

        if status_info["refined"]:  # 成功桶明细
            logger.info(f"\n✓ Successfully Refined ({len(status_info['refined'])}):")
            for info in status_info["refined"]:
                code_status = (  # 三元组表达式跨行：真改码标记
                    "CODE_CHANGED"
                    if info.get("final_code_changed", False)
                    else "NO_CODE_CHANGE"
                )
                code_attempts = info.get("code_changed_attempts", 0)  # 真改码轮数（旧格式默认 0）
                logger.info(  # 明细行：成功数/总轮数、改码轮数、改码标记、末轮状态
                    f"  - {info['checker_id']}: {info['successful_refinements']}/{info['attempts']} attempts, "
                    f"{code_attempts} code changes, {code_status}, final: {info['final_status']}"
                )

        if status_info["not_refined"]:  # 失败桶明细（同上格式）
            logger.info(f"\n✗ Not Refined ({len(status_info['not_refined'])}):")
            for info in status_info["not_refined"]:
                code_status = (
                    "CODE_CHANGED"
                    if info.get("final_code_changed", False)
                    else "NO_CODE_CHANGE"
                )
                code_attempts = info.get("code_changed_attempts", 0)
                logger.info(
                    f"  - {info['checker_id']}: {info['attempts']} attempts, "
                    f"{code_attempts} code changes, {code_status}, final: {info['final_status']}"
                )

        if status_info["invalid"]:  # invalid 桶：只有 id，无明细
            logger.info(f"\n⚠ Invalid Checkers ({len(status_info['invalid'])}):")
            for checker_id in status_info["invalid"]:
                logger.info(f"  - {checker_id}")

        if status_info["no_logs"]:  # 无日志桶：只有 id
            logger.info(f"\n? No Refinement Logs ({len(status_info['no_logs'])}):")
            for checker_id in status_info["no_logs"]:
                logger.info(f"  - {checker_id}")

    return status_info  # 返回完整盘点结果（供 list_successfully_changed_checkers 等复用）


# =============================================================================
# 【函数】list_successfully_changed_checkers —— 列出"真改了代码"的 checker
# 【职责】check_refinement_status 的薄封装：只保留 refined 桶中
#         final_code_changed=True 的 checker（即 refinement agent 的修改既真实
#         落到代码、又通过双准则验证的那批——论文 §3.2 真正"学会新知识"的 checker）。
# 【参数】checker_dir —— checker 子目录父目录
# 【返回】List[Dict]：真改码 checker 的详情字典列表
# =============================================================================
def list_successfully_changed_checkers(checker_dir: str) -> List[Dict]:
    """
    List checkers that have been successfully refined with actual code changes.

    Args:
        checker_dir: Directory containing checker subdirectories

    Returns:
        List of checker information dictionaries for successfully changed checkers
    """
    status_info = check_refinement_status(checker_dir, detailed=False)  # 复用盘点逻辑（不需要明细输出）

    # Filter checkers that have actual code changes
    changed_checkers = []  # 只收 final_code_changed=True 的（refined 但没真改码的剔除——LLM"假 refine"防御）
    for info in status_info["refined"]:
        if info.get("final_code_changed", False):
            changed_checkers.append(info)

    logger.info(f"=== Successfully Changed Checkers ===")
    logger.info(f"Found {len(changed_checkers)} checkers with actual code changes:")

    if changed_checkers:  # 有则逐个打印（成功轮/总轮、改码轮、末轮状态、日志路径）
        for info in changed_checkers:
            code_attempts = info.get("code_changed_attempts", 0)
            logger.info(
                f"✓ {info['checker_id']}: {info['successful_refinements']}/{info['attempts']} attempts, "
                f"{code_attempts} code changes, final: {info['final_status']}"
            )
            logger.info(f"  Log: {info['log_file']}")
    else:
        logger.info("No checkers have been successfully refined with code changes.")

    return changed_checkers


# =============================================================================
# 【函数】refine_unrefined_checkers —— 断点续跑（main.py "refine_unrefined" 模式）
# 【职责】只对"尚未成功 refine"的 checker（盘点结果中 not_refined + no_logs 两桶）
#         重跑 refinement。长时间批量任务中断后用它增量续跑，避免重复 refine
#         已成功的 checker（省下每轮 10 分钟级的全库扫描）。
# 【参数】checker_dir —— checker 子目录父目录
#         scan       —— 是否重新扫描（同 refine_checker）
#         max_tries  —— 每个 checker 最多轮数，默认 3（论文口径）
# 【返回】None
# 【与 refine_checker 的差异】①先经 check_refinement_status 筛"未成功"名单；
#         ②加载后只 update_base_result_dir、没有调 dump_dir()（不重写状态快照）
# =============================================================================
def refine_unrefined_checkers(
    checker_dir: str, scan: bool = True, max_tries: int = 3
) -> None:
    """
    Refine only the checkers that haven't been successfully refined yet.

    Args:
        checker_dir: Directory containing checker subdirectories
        scan: Whether to scan the kernel with the checker
        max_tries: Maximum number of attempts to refine each checker
    """
    checker_dir = Path(checker_dir)  # 转 Path

    # Check current status
    status_info = check_refinement_status(str(checker_dir), detailed=False)  # 先盘点当前状态

    # Get list of checkers that need refinement
    unrefined_checkers = []  # 待 refine 名单
    for info in status_info["not_refined"]:  # 有日志但从未成功
        unrefined_checkers.append(info["checker_id"])
    for checker_id in status_info["no_logs"]:  # 无日志（从未跑过/产物丢失）——注意：盘点时 invalid 的 checker 已被排除在外，不会出现在此名单
        unrefined_checkers.append(checker_id)

    if not unrefined_checkers:  # 名单为空 → 全部已成功，直接收工
        logger.info("All valid checkers have already been successfully refined!")
        return

    logger.info(f"Found {len(unrefined_checkers)} checkers that need refinement:")
    for checker_id in unrefined_checkers[:10]:  # Show first 10 —— 只展示前 10 个防刷屏
        logger.info(f"  - {checker_id}")
    if len(unrefined_checkers) > 10:  # 超过 10 个则打省略提示
        logger.info(f"  ... and {len(unrefined_checkers) - 10} more")

    # Filter unrefined checkers to only include valid ones
    # 名单二次过滤：逐个重验有效性（no_logs 里可能混着子目录已损坏/加载失败的）
    valid_unrefined_checkers = []
    invalid_unrefined_count = 0

    for checker_id in unrefined_checkers:
        checker_subdir = checker_dir / checker_id  # 由 id 反推子目录路径
        if not checker_subdir.exists():  # 目录都没了（被清理/移动）
            logger.warning(f"Checker directory not found: {checker_subdir}")
            invalid_unrefined_count += 1
            continue

        try:
            checker_data = CheckerData.load_checker_data_from_dir(checker_subdir)  # 加载并验证
            if checker_data.is_valid:  # 有效才进最终名单
                valid_unrefined_checkers.append(checker_id)
            else:  # 阶段一就没过 validation → 跳过（refine 只作用于 valid checker）
                invalid_unrefined_count += 1
                logger.warning(
                    f"[INVALID] Checker {checker_data.checker_id} is not valid - skipping"
                )
        except Exception as e:  # 加载异常 → 计数跳过，不炸整批
            invalid_unrefined_count += 1
            logger.error(
                f"[INVALID] Error loading checker {checker_id}: {e} - skipping"
            )

    if invalid_unrefined_count > 0:  # 二次过滤有淘汰时打汇总
        logger.info(
            f"Filtered out {invalid_unrefined_count} invalid unrefined checkers"
        )

    if not valid_unrefined_checkers:  # 全被过滤光 → 收工
        logger.info("No valid unrefined checkers found!")
        return

    # Initialize progress tracking for valid unrefined checkers
    progress_tracker = _create_progress_tracker(checker_dir)  # 新建 tracker（注意：会覆盖旧 refinement_progress.log）
    _update_progress_tracker(
        progress_tracker,
        f"Starting refinement of {len(valid_unrefined_checkers)} valid unrefined checkers",
    )

    # Process only valid unrefined checkers
    for i, checker_id in enumerate(valid_unrefined_checkers):  # 主循环：与 refine_checker 同构
        checker_subdir = checker_dir / checker_id  # 由 id 反推子目录（refine_checker 版本直接持有 Path）

        logger.info(
            f"[{i+1}/{len(valid_unrefined_checkers)}] Refining unrefined checker {checker_id}..."
        )
        _update_progress_tracker(
            progress_tracker,
            f"[{i+1}/{len(valid_unrefined_checkers)}] Processing {checker_id}",
        )

        try:
            checker_data = CheckerData.load_checker_data_from_dir(checker_subdir)
            # Update the output_dir to the checker
            # 重定位结果目录到本次 run 的 result_dir（注意：与 refine_checker 不同，这里没有 dump_dir() 重写状态快照）
            checker_data.update_base_result_dir(global_config.result_dir)

            # Use the improved refine logic with max attempts and logging
            # 与 refine_checker 完全相同的核心调用（≤max_tries 轮 + 全程日志）
            refine_results = refine_checker_with_max_attempts(
                checker_data,
                scan=scan,
                max_tries=max_tries,
                timeout=global_config.scan_timeout,
            )

            # Log the final results
            # 汇总日志 + 落盘（同 refine_checker）
            _log_refine_results(
                checker_data.checker_id, refine_results, Path(checker_data.output_dir)
            )

            # Update progress tracker with result
            final_status = refine_results[-1].result if refine_results else "No Results"  # 末轮状态（空列表兜底）
            success = any(r.refined for r in refine_results)  # 任一轮 refined 即 SUCCESS
            _update_progress_tracker(
                progress_tracker,
                f"COMPLETED: {checker_data.checker_id} - {final_status} ({'SUCCESS' if success else 'FAILED'})",
            )

        except Exception as e:  # 单 checker 异常隔离（同 refine_checker）
            logger.error(f"Error processing checker {checker_id}: {e}")
            _update_progress_tracker(
                progress_tracker, f"ERROR: {checker_id} - {str(e)}"
            )

    # Finalize progress tracking
    _finalize_progress_tracker(progress_tracker)  # 收尾统计（同 refine_checker）
    logger.info(f"Unrefined checker refinement process completed")


# =============================================================================
# 【函数】refine_checker_with_max_attempts —— 单 checker 的 ≤max_tries 轮 refine 状态机
# 【职责】论文 §3.2 "最多 3 轮 refine" 的循环骨架：每轮调 refine_checker_attempt
#         （715 行后：扫描→采样 5 条→triage→repair_FP→双准则验证），根据轮结果
#         决定 终止/续跑/复用上一轮扫描结果。收尾调 create_refinement_summary 落盘。
# 【参数】checker_data      —— 待 refine 的 checker 状态（代码在
#                              repaired_checker_code 字段，refine 成功后回写）
#         scan             —— 本轮是否真扫描（失败续跑时会被置 False 复用旧报告）
#         max_tries        —— 最多轮数，默认 3（论文口径；调用方 refine_checker/
#                              refine_unrefined_checkers 均传默认 3）
#         timeout          —— 单轮全库扫描限时（秒）；形参默认 900，但两个调用方
#                              都传 global_config.scan_timeout（默认 600）——默认值实际是摆设
#         reports_override —— 可选：直接注入报告列表（group scan 批量路径预留，
#                              跳过扫描；当前仓内无外部调用方）
# 【返回】List[RefinementResult]：每轮一个结果（含 refined/result/num_TP/num_FP/
#         refine_attempt_list 等）
# 【轮结果字符串】Perfect=无报告（checker 太干净）/ Uncompilable=起点代码编不过 /
#         Unscannable=扫描跑不起来 / No-FP=采样内无 FP / High-TP=precision≥0.75 /
#         Refined=改码成功 / Failed=异常
# =============================================================================
def refine_checker_with_max_attempts(
    checker_data: CheckerData,
    scan: bool = True,
    max_tries: int = 3,
    timeout: int = 900,
    reports_override: Optional[List[Dict]] = None,
) -> List[RefinementResult]:
    """
    Refine a checker with multiple attempts and detailed logging.

    Args:
        checker_data: Data about the checker to refine
        scan: Whether to scan the kernel with the checker
        max_tries: Maximum number of refinement attempts (default: 3)
        timeout: Timeout for scanning in seconds
        reports_override: Optional list of reports to use instead of scanning

    Returns:
        List of RefinementResult objects for each attempt
    """
    refine_results = []  # 每轮的 RefinementResult 收集列表（返回值）
    last_scan_id = None  # 上一轮扫描的 attempt 编号（0-based）；非 None 时下一轮复用该轮报告、跳过扫描
    orig_scan = scan  # 记住调用方原始 scan 意愿：refine 成功后要恢复真扫描去验证新代码

    logger.info(
        f"Starting refinement of checker {checker_data.checker_id} with max {max_tries} attempts"
    )

    for attempt in range(max_tries):  # 论文"最多 3 轮 refine"主循环；attempt 为 0-based 轮号
        logger.info(f"=== Refinement Attempt {attempt + 1}/{max_tries} ===")  # 人读进度（1-based）
        logger.info(f"Last scan ID: {last_scan_id}")  # 调试信息：None=本轮要真扫描，数字=复用该轮报告

        # 单轮核心（715 行后）：初始化编译 → 扫描/取报告 → triage → FP 修复 → 双准则验证
        refine_result = refine_checker_attempt(
            checker_data,
            scan=scan,  # 可能已被上一轮置 False（复用报告模式）
            attempt_id=attempt,  # 0-based：既用于目录命名 scan-reports-{id}，也当采样 seed
            timeout=timeout,  # 扫描限时透传
            last_scan_id=last_scan_id,  # 复用报告时指向上一轮的扫描目录
            reports_override=reports_override,  # 注入报告直通用（group scan 预留）
        )

        refine_results.append(refine_result)  # 收集本轮结果

        # Log attempt result
        _log_attempt_result(checker_data.checker_id, attempt + 1, refine_result)  # 单轮日志（attempt+1 转回 1-based 展示）

        # Save refined code if successful
        if refine_result.refined:  # 本轮 refine 成功 → 立即把新代码落盘（refinements/refined_attempt_N.cpp + latest_refined.cpp + metadata）
            refine_result.save_refined_code(
                Path(checker_data.output_dir), checker_data.checker_id
            )

        # Check if we should stop refining
        # 终止判定（优先级从上到下）：
        if refine_result.result in ["Uncompilable", "Unscannable", "No-FP", "High-TP"]:
            # 环境性失败（编不过/扫不动）或已达标（采样内无 FP / precision≥0.75）——再试无意义，提前止损
            logger.info(f"Stopping refinement: {refine_result.result}")
            break
        elif refine_result.result == "Perfect":
            logger.info("Checker is perfect - stopping refinement")  # 零报告：checker 干净到无可 refine，停
            break
        elif refine_result.refined:
            # [FIXME] Update the checker data with the refined code
            # Not sure whether this is correct
            # ↑ 原作者的 FIXME 原样保留：把 refine 后代码回写 CheckerData，供下一轮
            #   作为起点代码（该赋值的正确性作者自己存疑）
            checker_data.repaired_checker_code = refine_result.checker_code  # 回写：下一轮 refine_checker_attempt 以新代码为起点
            last_scan_id = None  # 清空：新代码必须重新全库扫描看效果（不能复用旧代码的报告）
            scan = orig_scan  # 恢复真扫描模式（上一轮失败时可能被置 False）
            logger.info(f"Attempt {attempt + 1} successful - checker refined!")
        else:
            # Failed attempt - reuse scan results for next attempt
            # Do not need to scan again
            # 失败续跑：checker 代码没变（或没验证通过），同一份扫描报告完全可以复用——
            # 省掉一轮 10 分钟级的全库扫描，只让 LLM 换着法子再试
            if last_scan_id is None:  # 首次失败：登记本轮扫描供下一轮复用
                last_scan_id = attempt  # 注意存的是 0-based 轮号（与 scan-reports-{id} 目录名对齐）
            scan = False  # 下一轮进"复用报告"分支（refine_checker_attempt 里读旧目录）
            logger.warning(f"Attempt {attempt + 1} failed - will reuse scan results")

    # Create comprehensive summary
    # 全轮结束后生成 refinements/README.md 汇总表（所有轮指标 + 文件结构清单）
    create_refinement_summary(
        checker_data.checker_id, refine_results, Path(checker_data.output_dir)
    )

    return refine_results  # 返回逐轮结果列表（调用方据此判定 success=any(refined)）


# =============================================================================
# 【函数】_log_attempt_result —— 单轮 refine 结果日志
# 【职责】把一轮 RefinementResult 的关键指标打到 logger：状态/refined 标记/是否
#         真改码/报告数/TP/FP/precision/refine 尝试数；真改码时聚合本轮全部
#         killed_objects（被新 checker"消灭"报警的目标对象）并示例前 3 个。
# 【参数】checker_id   —— checker 标识（日志定位用）
#         attempt_num  —— 1-based 轮号（调用方已 +1）
#         result       —— 本轮 RefinementResult
# 【返回】None
# 【语义】killed_objects = refine 后复扫不再报警的 .o 目标文件集合——论文双准则
#         之 (1)"原 FP 案例不再报警"的对象级证据
# =============================================================================
def _log_attempt_result(
    checker_id: str, attempt_num: int, result: RefinementResult
) -> None:
    """Log the result of a single refinement attempt."""
    logger.info(f"Attempt {attempt_num} Result:")
    logger.info(f"  - Status: {result.result}")  # 状态串（Refined/Failed/High-TP/...）
    logger.info(f"  - Refined: {result.refined}")  # 本轮是否 refine 成功（名义口径）

    # Check if code was actually changed
    code_changed = _check_code_changed(result)  # 严口径：代码真变了 且 有验证通过的 refine 尝试
    if code_changed:
        logger.info(f"  - ✓ Code Changed: YES (checker was successfully modified)")
    else:
        logger.info(f"  - ✗ Code Changed: NO (no valid modifications made)")  # refined=True 但代码没变/验证没过 → "空 refine"

    logger.info(f"  - Reports: {result.num_reports}")  # 后端总报告数（采样前的全量计数）
    logger.info(f"  - True Positives: {result.num_TP}")  # triage agent 判定为真阳性的报告数
    logger.info(f"  - False Positives: {result.num_FP}")  # triage 判 NotABug（FP）的报告数
    if result.num_reports > 0:  # 有报告才算 precision（分母 TP+FP 为 0 时给 0 防除零）
        precision = (
            result.num_TP / (result.num_TP + result.num_FP)
            if (result.num_TP + result.num_FP) > 0
            else 0
        )
        logger.info(f"  - Precision: {precision:.2%}")  # 百分比格式（如 75.00%）
    logger.info(f"  - Refine Attempts: {len(result.refine_attempt_list)}")  # 本轮对每个 FP 报告各做了一次 refine 尝试

    # Log successful object kills if code was changed
    if code_changed and result.refine_attempt_list:  # 只在真改码时统计 kill 战果
        total_killed_objects = set()  # 用 set 去重（同一对象可能被多次 refine 尝试消灭）
        for attempt in result.refine_attempt_list:
            total_killed_objects.update(attempt.killed_objects)  # 并集聚合本轮全部尝试的 killed_objects
        if total_killed_objects:
            logger.info(f"  - Objects Successfully Killed: {len(total_killed_objects)}")
            # Show first few objects as examples
            example_objects = list(total_killed_objects)[:3]  # 示例前 3 个目标对象（.o 文件名）
            logger.info(
                f"    Examples: {', '.join(example_objects)}"
                + ("..." if len(total_killed_objects) > 3 else "")  # 超过 3 个补省略号
            )


# =============================================================================
# 【函数】_check_code_changed —— "真改码"鉴别器
# 【职责】区分两种"refined"：LLM 名义上改了（refined=True）vs 代码确实变了且
#         至少一次 refine 尝试通过双准则验证。防两类假阳性：(a) LLM 原样返回
#         旧代码；(b) 代码变了但从未通过对象级/commit 级验证。
# 【判定】refined=True 且 original_checker_code 非空 且 strip 后新旧代码不同 且
#         refine_attempt_list 中存在"killed_objects 非空 且
#         semantic_correct_refine_code 非空"的尝试（后者即通过 _validate_on_commit
#         差分验证后被记录的代码，715 行后函数写入）。
# 【参数】result —— 待鉴别的 RefinementResult
# 【返回】bool：True=真改码（状态文件 final_code_changed 的来源，统计口径）
# =============================================================================
def _check_code_changed(result: RefinementResult) -> bool:
    """Check if the checker code was actually changed and validated during refinement."""
    if not result.refined or not result.original_checker_code:  # 没成功 refine 或没有起点代码快照 → 直接判 False
        return False

    # Compare original and final code
    original_code = result.original_checker_code.strip()  # 起点（本轮 refine 前的）代码，去首尾空白
    final_code = result.checker_code.strip()  # 终点（refine 后的）代码，同样处理保证可比

    # Check if codes are different
    if original_code == final_code:  # 一字不差 → LLM 没真改代码，判 False（"空 refine"防御之一）
        return False

    # Check if there were successful refinement attempts with killed objects
    if result.refine_attempt_list:  # 有 refine 尝试记录才继续
        for attempt in result.refine_attempt_list:
            if attempt.killed_objects and attempt.semantic_correct_refine_code:
                # 双保险：消灭过 FP 报警对象 + 代码通过了 commit 级差分验证
                return True

    return False  # 代码虽然变了但没有一次尝试通过双准则验证 → 仍不算真改码


# =============================================================================
# 【函数】_log_refine_results —— 跨轮汇总日志（本批注释截止于原 714 行）
# 【职责】对 refine_checker_with_max_attempts 返回的全部轮次做汇总：总轮数/
#         成功轮数/真改码轮数/末轮状态/全部 killed_objects 聚合/逐轮指标演进表
#         （Reports/TP/FP/Precision），最后调 _save_refine_log_to_file（715 行后）
#         把同样内容落盘为 refinement_logs/<id>_refinement.md + <id>_status.txt。
# 【参数】checker_id        —— checker 标识
#         results           —— 逐轮 RefinementResult 列表
#         checker_output_dir —— 落盘目录（None 时 _save_refine_log_to_file 落到
#                              当前工作目录 refinement_logs/ 下）
# 【返回】None
# 【注意】本函数尾部（原 715-731 行，逐轮演进表 + 落盘调用）属后续注释批次，
#         本批注释到 714 行边界为止
# =============================================================================
def _log_refine_results(
    checker_id: str, results: List[RefinementResult], checker_output_dir: Path = None
) -> None:
    """Log the final summary of all refinement attempts."""
    logger.info(f"=== Final Refinement Summary for {checker_id} ===")
    logger.info(f"Total attempts: {len(results)}")  # 实际跑的轮数（可能 < max_tries：提前 break）

    if not results:  # 一轮结果都没有（理论不可达，防御性兜底）
        logger.warning("No refinement results available")
        return

    final_result = results[-1]  # 末轮结果（其 result 即对外最终状态）
    successful_attempts = sum(1 for r in results if r.refined)  # 名义成功轮数（refined=True）

    # Track code changes across all attempts
    code_changed_attempts = sum(1 for r in results if _check_code_changed(r))  # 真改码轮数（严口径）
    final_code_changed = _check_code_changed(final_result)  # 末轮是否真改码（status 文件 final_code_changed 字段的来源）

    logger.info(f"Successful refinements: {successful_attempts}")  # 名义口径
    logger.info(f"Code actually changed: {code_changed_attempts} attempts")  # 严口径（两数对照可看"空 refine"占比）
    logger.info(f"Final status: {final_result.result}")
    logger.info(f"Final checker refined: {final_result.refined}")
    logger.info(f"Final code changed: {'YES' if final_code_changed else 'NO'}")

    # Log total objects killed across all attempts
    if code_changed_attempts > 0:  # 只要有任一轮真改码，就聚合全部 kill 战果
        all_killed_objects = set()  # set 去重（跨轮/跨尝试消灭的同一对象只算一次）
        for result in results:
            if _check_code_changed(result):  # 只统计真改码轮（失败轮的 kill 不算数）
                for attempt in result.refine_attempt_list:
                    all_killed_objects.update(attempt.killed_objects)

        if all_killed_objects:  # 打总数 + 前 5 个示例
            logger.info(f"Total objects successfully killed: {len(all_killed_objects)}")
            logger.info(  # 跨行 f-string 拼接：前 5 个对象名逗号连接，超过 5 个补省略号
                f"Examples: {', '.join(list(all_killed_objects)[:5])}"
                + ("..." if len(all_killed_objects) > 5 else "")
            # ↑ 本批注释边界：原 714 行止；下行的右括号及函数其余部分（原 715-731 行，
            #   逐轮演进表 + _save_refine_log_to_file 调用）为后续注释批次范围
            # 本批（批1）注释至此，715 行起保持原样由后批接力
            )  # ← 批1/批2 接力点：logger.info(...) 调用闭合（原 715 行）——批2注释自此行起

    # Log progression of metrics across attempts
    # 逐轮指标演进表：状态|真改码标记|报告数|TP|FP|precision 一行一览，
    # 用于人工检视 refine 是否朝 precision 变好的方向推进（以及"空 refine"轮占比）
    logger.info("Refinement progression:")
    for i, result in enumerate(results):  # i 为 0-based 轮号，展示时 +1（与 RefinementResult.attempt_id 的 1-based 口径一致）
        precision = 0  # 先置 0：该轮 TP+FP=0（如 Uncompilable/Unscannable 轮）时保持 0，兼防除零
        if (result.num_TP + result.num_FP) > 0:  # 只有 triage 过至少一条报告的轮才有 precision 可算
            precision = result.num_TP / (result.num_TP + result.num_FP)  # precision = TP/(TP+FP)（只看 triage 采样，不含未采样报告）
        code_changed = _check_code_changed(result)  # 该轮是否"真改码"（严口径，见 _check_code_changed）
        code_status = "CODE_CHANGED" if code_changed else "NO_CHANGE"  # 表格友好标记
        logger.info(
            f"  Attempt {i+1}: {result.result} | {code_status} | Reports: {result.num_reports} | "
            f"TP: {result.num_TP} | FP: {result.num_FP} | Precision: {precision:.2%}"
        )  # 跨行 f-string 隐式拼接：一行打完该轮全部指标

    # Save detailed log to file
    # 同样内容落盘：_save_refine_log_to_file 写出 refinement_logs/<id>_refinement.md
    # （人类可读 Markdown）+ <id>_status.txt（机器可读六段格式，前段
    # check_refinement_status 回读解析——读写两端分居批1/批2 区段，改格式须两头同步）
    _save_refine_log_to_file(checker_id, results, checker_output_dir)


# =============================================================================
# 【函数】_save_refine_log_to_file —— refine 日志落盘（Markdown 全量版 + 状态速查版）
# 【职责】把 _log_refine_results 已打到控制台的汇总写成两类文件：
#         ① <output_dir>/refinement_logs/<id>_refinement.md —— 人类可读
#            Markdown（Summary + 逐轮 Detailed Attempt Log，含每个 refine 尝试
#            的 refine_id/killed_objects/semantic_correct 标记/代码行数变化）；
#         ② 同目录 <id>_status.txt —— 机器可读六段竖线格式
#            checker_id|attempts|successful|code_changed_attempts|final_code_changed|final_status，
#            正是前段 check_refinement_status 解析的格式（写在此、读在前段——
#            批1 头注坑 6 的另一端）。
# 【参数】checker_id         —— checker 标识（决定文件名）
#         results            —— 逐轮 RefinementResult 列表
#         checker_output_dir —— 落盘基目录；None 时退化到当前工作目录
# 【返回】None
# 【坑】    整函数包 try/except 只记日志——落盘失败绝不影响 refine 主流程；
#           Python bool 经 f-string 落盘成 "True"/"False" 字符串，前段读取端
#           用 parts[4].lower()=="true" 还原，两端约定一致
# =============================================================================
def _save_refine_log_to_file(
    checker_id: str, results: List[RefinementResult], checker_output_dir: Path = None
) -> None:
    """Save detailed refinement log to a file under the checker's directory."""
    try:  # 全函数兜底：日志失败只记 error，不影响 refine 结果本身
        import datetime  # 局部导入（与本文件其他日志函数风格一致）

        log_content = f"# Refinement Log for Checker: {checker_id}\n\n"  # Markdown 头：checker 标识
        log_content += (
            f"**Generated**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"  # 生成时间戳
        )
        log_content += f"**Working Directory**: {Path().cwd()}\n"  # 记录 cwd（落盘退化到相对路径时便于溯源）
        log_content += f"**Total Attempts**: {len(results)}\n\n"  # 实际轮数（可能 < max_tries：提前 break）

        # Summary section
        # Summary 段：名义成功 / 真改码 / 末轮状态三组口径
        successful_attempts = sum(1 for r in results if r.refined)  # 名义成功轮数（refined=True）
        code_changed_attempts = sum(1 for r in results if _check_code_changed(r))  # 真改码轮数（严口径）
        log_content += f"## Summary\n"
        log_content += (
            f"- **Successful Refinements**: {successful_attempts}/{len(results)}\n"  # 成功轮/总轮
        )
        log_content += f"- **Code Actually Changed**: {code_changed_attempts}/{len(results)} attempts\n"  # 真改码轮/总轮（与上行对照看"空 refine"占比）
        if results:  # 有结果才写末轮状态段（空列表跳过）
            final_result = results[-1]  # 末轮结果
            final_code_changed = _check_code_changed(final_result)  # 末轮是否真改码
            log_content += f"- **Final Status**: {final_result.result}\n"  # 末轮状态串
            log_content += f"- **Final Refined**: {final_result.refined}\n"  # 末轮名义 refined 标记
            log_content += (
                f"- **Final Code Changed**: {'YES' if final_code_changed else 'NO'}\n"  # 末轮真改码标记
            )

            # Add total objects killed if any code changes occurred
            # 只要有真改码轮，就聚合全部 killed_objects（跨轮/跨尝试 set 去重）
            if code_changed_attempts > 0:
                all_killed_objects = set()  # set 去重
                for result in results:
                    if _check_code_changed(result):  # 只统计真改码轮的战果
                        for attempt in result.refine_attempt_list:
                            all_killed_objects.update(attempt.killed_objects)

                if all_killed_objects:  # 有 kill 才写该行
                    log_content += (
                        f"- **Total Objects Killed**: {len(all_killed_objects)}\n"  # 被 refine 后 checker"消灭"报警的目标对象总数
                    )
        log_content += f"\n"  # Summary 段与 Detailed 段之间空行（Markdown 排版）

        # Detailed attempt information
        # Detailed 段：逐轮明细（每轮一个三级标题）
        log_content += f"## Detailed Attempt Log\n\n"
        for i, result in enumerate(results):  # 逐轮展开（i 0-based，展示 +1）
            code_changed = _check_code_changed(result)  # 该轮真改码判定
            log_content += f"### Attempt {i+1}\n"  # 轮标题（1-based）
            log_content += f"- **Status**: {result.result}\n"  # 状态串
            log_content += f"- **Refined**: {result.refined}\n"  # 名义 refined 标记
            log_content += (
                f"- **Code Changed**: {'✓ YES' if code_changed else '✗ NO'}\n"  # 真改码标记（✓/✗ 为原代码字符）
            )
            log_content += f"- **Reports**: {result.num_reports}\n"  # 报告总数（注意复用轮口径=采样条数，见 refine_checker_attempt 坑注）
            log_content += f"- **True Positives**: {result.num_TP}\n"  # triage 判 TP 数
            log_content += f"- **False Positives**: {result.num_FP}\n"  # triage 判 FP（NotABug）数

            if (result.num_TP + result.num_FP) > 0:  # 有 triage 结果才写 precision（防除零）
                precision = result.num_TP / (result.num_TP + result.num_FP)
                log_content += f"- **Precision**: {precision:.2%}\n"

            log_content += f"- **Refine Attempts**: {len(result.refine_attempt_list)}\n"  # 本轮对 FP 报告的 refine 尝试数

            if result.refine_attempt_list:  # 有尝试才展开明细子列表
                log_content += f"- **Refine Attempt Details**:\n"
                for j, attempt in enumerate(result.refine_attempt_list):  # 逐尝试（j 0-based，展示 +1）
                    log_content += f"  - Attempt {j+1}: `{attempt.refine_id}`\n"  # 尝试标识（refine-{轮号}-{采样序号}）
                    log_content += f"    - Report ID: {attempt.report_data.report_id if attempt.report_data else 'N/A'}\n"  # 对应 FP 报告 id（report_data 缺失兜底 N/A）
                    log_content += (
                        f"    - Killed Objects: {len(attempt.killed_objects)}\n"  # 该尝试消灭的报警对象数
                    )
                    log_content += f"    - Semantic Correct: {'YES' if attempt.semantic_correct_refine_code else 'NO'}\n"  # 是否通过 _validate_on_commit 差分验证（论文双准则之(2)的证据字段）
                    if attempt.killed_objects:  # 有 kill 则列前 3 个对象名示例
                        log_content += (
                            f"    - Objects: {', '.join(attempt.killed_objects[:3])}"
                            + ("..." if len(attempt.killed_objects) > 3 else "")  # 超过 3 个补省略号
                            + "\n"
                        )

            # Add code diff information if code was changed
            if code_changed and result.original_checker_code:  # 真改码且留有起点快照 → 记录规模变化
                original_lines = len(result.original_checker_code.split("\n"))  # 起点代码行数
                final_lines = len(result.checker_code.split("\n"))  # 终点代码行数
                log_content += (
                    f"- **Code Changes**: {original_lines} → {final_lines} lines\n"  # 行数变化（仅规模对比，非逐行 diff）
                )

            log_content += "\n"  # 每轮明细之间空一行

        # Determine save location - prefer checker's output directory
        # 落盘位置：优先 checker 自己的 output_dir，退化到 cwd
        if checker_output_dir:
            log_dir = Path(checker_output_dir) / "refinement_logs"  # <output_dir>/refinement_logs/
        else:
            log_dir = Path("refinement_logs")  # 当前工作目录下（溯源靠头部 cwd 行）

        log_dir.mkdir(parents=True, exist_ok=True)  # 递归建目录（已存在不报错）
        log_file = log_dir / f"{checker_id}_refinement.md"  # Markdown 全量日志路径
        log_file.write_text(log_content)  # 一次写全
        logger.info(f"Detailed refinement log saved to: {log_file}")

        # Also create a simple status file for quick checking
        # 机器可读状态速查文件：六段竖线格式（前段 check_refinement_status 的解析契约）
        code_changed_attempts = sum(1 for r in results if _check_code_changed(r))  # 重算一遍（与 Summary 段同值，冗余但无害）
        final_code_changed = _check_code_changed(results[-1]) if results else False  # 末轮真改码（空列表兜底 False）
        status_content = f"{checker_id}|{len(results)}|{successful_attempts}|{code_changed_attempts}|{final_code_changed}|{results[-1].result if results else 'No Results'}\n"  # 六段：id|总轮|成功轮|改码轮|末轮改码|末轮状态（bool 落盘成 True/False 字符串）
        status_file = log_dir / f"{checker_id}_status.txt"  # 状态文件路径
        status_file.write_text(status_content)

    except Exception as e:  # 任何落盘异常只记日志（日志失败不影响 refine 结果）
        logger.error(f"Failed to save refinement log: {e}")


# =============================================================================
# 【函数】create_refinement_summary —— refinements/README.md 汇总表生成
# 【职责】把 refine_checker_with_max_attempts 的全部轮次写成 Markdown 汇总：
#         全轮指标表格（Attempt|Status|Refined|Reports|TP|FP|Precision）、
#         成功轮明细、以及 refinements/ 目录的文件结构清单——该目录正是
#         RefinementResult.save_refined_code 落盘 refined_attempt_N.cpp /
#         latest_refined.cpp 的地方，README 相当于这批产物的目录页。
# 【参数】checker_id —— checker 标识（写进标题）
#         results    —— 逐轮 RefinementResult 列表
#         output_dir —— 输出基目录（取 <output_dir>/refinements/README.md）
# 【返回】None
# 【坑】    同样整体 try/except 只记日志；File Structure 清单是按命名约定
#           "拼出来的预期清单"，并非扫描真实目录生成——实际缺文件时 README
#           不会反映；successful_attempts 变量名有误导性：里面装的是
#           RefinementResult（轮），不是 RefineAttempt（单 FP 尝试），仅沿用
#           上游命名
# =============================================================================
def create_refinement_summary(
    checker_id: str, results: List[RefinementResult], output_dir: Path
) -> None:
    """Create a comprehensive summary of all refinement attempts and successful refinements."""
    try:
        summary_dir = Path(output_dir) / "refinements"  # 与 save_refined_code 同目录：refined 代码与 README 放一起
        summary_dir.mkdir(parents=True, exist_ok=True)  # 递归建目录

        # Create summary file
        # 头部：标题 + 总轮数 + 成功轮数
        summary_content = f"# Refinement Summary for Checker: {checker_id}\n\n"
        summary_content += f"Total attempts: {len(results)}\n"  # 实际轮数（≤ max_tries，提前 break 会更少）

        successful_attempts = [r for r in results if r.refined]  # 名义成功轮列表（元素是 RefinementResult，见函数头坑注）
        summary_content += f"Successful refinements: {len(successful_attempts)}\n\n"

        # Create table of all attempts
        # 全轮指标表：表头 + 对齐分隔行
        summary_content += "## All Attempts\n\n"
        summary_content += (
            "| Attempt | Status | Refined | Reports | TP | FP | Precision |\n"
        )
        summary_content += (
            "|---------|--------|---------|---------|----|----|----------|\n"
        )

        for result in results:  # 逐轮一行
            precision = (
                result.num_TP / (result.num_TP + result.num_FP)  # precision = TP/(TP+FP)
                if (result.num_TP + result.num_FP) > 0  # 分母为零（无 triage 结果的轮）给 0
                else 0
            )
            summary_content += (
                f"| {result.attempt_id} | {result.result} | {result.refined} | "  # 行前半：轮号(1-based)|状态|refined 标记
            )
            summary_content += f"{result.num_reports} | {result.num_TP} | {result.num_FP} | {precision:.2%} |\n"  # 行后半：报告数|TP|FP|precision

        # List successful refinements
        # 成功轮明细段（仅名义成功轮）
        if successful_attempts:
            summary_content += "\n## Successful Refinements\n\n"
            for attempt in successful_attempts:  # 逐成功轮一个小节
                summary_content += f"### Attempt {attempt.attempt_id}\n"  # 轮号（1-based）
                summary_content += f"- **Status**: {attempt.result}\n"  # 状态串
                summary_content += f"- **Reports**: {attempt.num_reports}\n"  # 报告数
                summary_content += f"- **True Positives**: {attempt.num_TP}\n"  # TP 数
                summary_content += f"- **False Positives**: {attempt.num_FP}\n"  # FP 数
                precision = (
                    attempt.num_TP / (attempt.num_TP + attempt.num_FP)  # 同上口径
                    if (attempt.num_TP + attempt.num_FP) > 0
                    else 0
                )
                summary_content += f"- **Precision**: {precision:.2%}\n"
                summary_content += (
                    f"- **Code File**: `refined_attempt_{attempt.attempt_id}.cpp`\n"  # 指向 save_refined_code 的落盘文件名（按约定拼接）
                )
                summary_content += f"- **Metadata File**: `refined_attempt_{attempt.attempt_id}_metadata.yaml`\n\n"  # 同名 metadata 文件（成对产出）

        # File locations
        # 文件结构清单段：按命名约定拼出 refinements/ 目录的预期内容树
        summary_content += "## File Structure\n\n"
        summary_content += "```\n"  # 代码块开始（树形图）
        summary_content += "refinements/\n"
        summary_content += "├── README.md                    # This summary\n"  # 本文件自身
        if successful_attempts:  # 有成功轮才有 latest_refined.cpp（save_refined_code 写的最新成功版）
            summary_content += (
                "├── latest_refined.cpp           # Latest successful refinement\n"
            )
            for attempt in successful_attempts:  # 每个成功轮一对文件：代码 + metadata
                summary_content += f"├── refined_attempt_{attempt.attempt_id}.cpp      # Successful refinement #{attempt.attempt_id}\n"
                summary_content += f"├── refined_attempt_{attempt.attempt_id}_metadata.yaml  # Metadata for attempt #{attempt.attempt_id}\n"

        for result in results:  # 每轮（无论成败）都有当时代码快照；留有起点快照的还多一份 _original
            summary_content += f"├── attempt_{result.attempt_id}.cpp               # Code from attempt #{result.attempt_id}\n"
            if result.original_checker_code:  # 该轮记录了 refine 前起点代码 → 对应 _original.cpp 也列出
                summary_content += f"├── attempt_{result.attempt_id}_original.cpp      # Original code before attempt #{result.attempt_id}\n"
        summary_content += "```\n"  # 代码块结束

        # Save summary
        summary_file = summary_dir / "README.md"  # 固定文件名 README.md（refinements/ 的目录页）
        summary_file.write_text(summary_content)
        logger.info(f"Refinement summary saved to: {summary_file}")

    except Exception as e:  # 汇总失败只记日志（refine 主结果已在 RefinementResult 里）
        logger.error(f"Failed to create refinement summary: {e}")


# =============================================================================
# 【函数】refine_checker_attempt —— 论文 §3.2 单轮 refinement 的核心执行体
#         （全模块心脏：扫描 → 报告蒸馏采样 → triage → FP 修复 → 双准则验证）
# 【论文映射】单轮流程逐步落地论文 §3.2 "Checker Refinement"：
#         ① 起点代码先过编译闸（_initialize_refinement——论文 §3.1.3 的 syntax
#            repair agent 在 refine 阶段复用）；
#         ② 全库扫描收报告（_scan_target）→ 报告蒸馏 + 采样 5 条
#            （_process_reports* ← global_config.max_fp_reports_for_refinement=5，
#            论文"采样 5 条报告"）；
#         ③ triage agent 逐报告判 Bug/NotABug（_triage_reports →
#            agent.check_report；判定口径=是否对齐目标 pattern，而非一般代码
#            正确性）；
#         ④ 早停判据：总报告≤10 或采样为空 → "Perfect"（与论文 plausible 判据
#            的总量门槛"总报告数<T_plausible(=20)"同型，实现常数取 10）；
#            FP=0 → "No-FP"；precision≥0.75 → "High-TP"（采样 5 条时等价于
#            FP≤1，即论文"采样 5 条报告中 FP≤1"判据的 precision 表达）；
#         ⑤ 对每个 FP 报告跑 refinement agent（_refine_false_positives →
#            agent.repair_FP 修改 checker 逻辑，如学会 unlikely() 宏是合法
#            空检查）；
#         ⑥ 双准则接受（论文的接受条件，两条都要过）：_validate_on_objects
#            （原 FP 对象不再报警）+ _validate_on_commit（buggy/patched 差分
#            验证仍通过）。
# 【参数】checker_data      —— 待 refine 的 checker 状态（起点代码在
#                              repaired_checker_code 字段）
#         scan             —— True=本轮真扫描；False=复用 last_scan_id 轮报告
#         attempt_id       —— 0-based 轮号（scan-reports-{id} 目录名 + 采样 seed）
#         timeout          —— 扫描限时秒数
#         last_scan_id     —— 复用模式指向的 0-based 轮号（None=非复用）
#         reports_override —— group scan 注入报告（fork 增量扩展位，跳过扫描）
# 【返回】RefinementResult（result 取值：Uncompilable/Unscannable/Perfect/
#         No-FP/High-TP/Refined/Failed——外层 refine_checker_with_max_attempts
#         按这些字符串决定终止/续跑/复用）
# 【坑】    result 字符串是外层状态机的协议契约，改词=改状态机；复用轮
#           （scan=False 路径）的 num_reports 口径是采样条数而非后端总数
#           （_process_reports 拿不到总数），与扫描轮不一致
# =============================================================================
def refine_checker_attempt(
    checker_data: CheckerData,
    scan: bool = True,
    attempt_id: int = 0,
    timeout: int = 900,
    last_scan_id: Optional[int] = None,
    reports_override: Optional[List[Dict]] = None,
) -> RefinementResult:
    """Refines a checker by analyzing reports and fixing false positives.

    Args:
        checker_data: Data about the checker to refine
        scan: Whether to scan the kernel with the checker
        attempt_id: ID of the current refinement attempt
        timeout: Timeout for scanning in seconds
        last_scan_id: ID of the last scan if reusing results
        reports_override: Optional list of reports to use instead of scanning

    Returns:
        RefinementResult containing refinement status and results
    """
    # 轮结果对象：默认值全为"失败态"，后续步骤逐步改写
    refine_result = RefinementResult(
        refined=False,  # 尚未 refine 成功
        checker_code="",  # 由 _initialize_refinement 填入编译通过的起点代码
        result="Failed",  # 默认状态：任何提前 return 都带着可读终态
        num_TP=0,  # triage 计数（TP）
        num_FP=0,  # triage 计数（FP）
        num_reports=0,  # 后端报告总数（采样前的全量计数）
        attempt_id=attempt_id + 1,  # 0-based 轮号转 1-based 落盘（与 last_scan_id 的 0-based 口径不同，见批1 头注坑 7）
        refine_attempt_list=[],  # 本轮逐 FP 报告的 refine 尝试记录
        error_objects=set(),  # 全部 FP 报告涉及的 .o 对象集合（kill 验证的靶子池）
        original_checker_code=checker_data.repaired_checker_code,  # Store original code
    )
    # ↑ 起点（refine 前）代码快照：_check_code_changed 靠它判"真改码"

    # Initialize refinement
    # 步骤①：起点代码编译闸（过不了 → "Uncompilable" 直接出局）
    if not _initialize_refinement(checker_data, refine_result):
        return refine_result

    report_dir = Path(checker_data.output_dir) / f"scan-reports-{attempt_id}"  # 本轮扫描产物目录（attempt_id 为 0-based）
    report_dir.mkdir(parents=True, exist_ok=True)  # 递归建目录（已存在不报错）

    # Handle reports - either use override or scan
    # 步骤②：取报告——三条互斥路径（override 注入 / 真扫描 / 复用上轮）
    if reports_override:
        # Use provided reports (from group scanning)
        # 路径 A：group scan 批量报告直接注入（fork 增量；免扫描免采样）
        reports = _convert_override_reports_to_report_data(reports_override)  # Dict 列表 → ReportData 列表
        total_reports_in_backend = len(reports_override)  # 注入多少算多少（无后端总量概念）

        logger.info(f"Using {len(reports_override)} reports from group scan override")
        refine_result.num_reports = total_reports_in_backend  # 记录报告总数

        if not reports:  # 注入为空（或全部转换失败）→ 无可 triage → "Perfect"
            refine_result.result = "Perfect"
            return refine_result
    else:
        # Standard scanning and report processing
        # 路径 B/C：标准流程（真扫描 or 复用上轮报告）
        if scan:
            # Only create directories and scan if scan=True
            # 路径 B：真扫描（首轮 / 上轮 refine 成功后重新验证新代码）
            scan_bug_report_dir = report_dir / "main-report"  # 全库扫描报告子目录
            scan_bug_report_dir.mkdir(parents=True, exist_ok=True)

            # Scan the target
            # We use the refine_result.checker_code to scan the target
            # 用刚过编译闸的代码全库扫描（跑不动 → "Unscannable" 出局）
            if not _scan_target(
                refine_result.checker_code, scan_bug_report_dir, timeout, refine_result
            ):
                return refine_result

            # Process reports from scan
            # 报告蒸馏+采样：后端把 CSA 原始报告蒸馏成 relevant lines + trace
            # path，再按 seed 采样 sampled_num 条返回（详见 _process_reports_with_count）
            reports, total_reports_in_backend = _process_reports_with_count(
                scan_bug_report_dir, attempt_id, last_scan_id
            )
        else:
            # Now we are using last step's reports
            # 路径 C：复用上轮扫描产物（上轮失败、代码没变 → 没必要再全库扫一遍）
            report_dir = Path(checker_data.output_dir) / f"scan-reports-{last_scan_id}"  # 改指上轮目录（last_scan_id 为 0-based）
            scan_bug_report_dir = report_dir / "main-report"  # 上轮的全库扫描报告目录

            reports = _process_reports(scan_bug_report_dir, attempt_id, last_scan_id)  # 重新采样（seed=本轮号 → 换一批 FP 案例）
            total_reports_in_backend = len(reports)  # 【坑】复用轮拿不到后端总数，num_reports 退化为采样条数（与扫描轮口径不一致）

        # Set the total number of reports found by the backend
        refine_result.num_reports = total_reports_in_backend  # 记录后端报告总数（路径 B 为真总数）

        if not reports:  # 无有效报告（0 条 / 总量≤10 判 perfect / 提取异常）→ "Perfect"
            refine_result.result = "Perfect"
            return refine_result

    # Triage reports
    # 步骤③：triage agent 逐报告判 TP/FP（论文 §3.2；填 num_TP/num_FP/error_objects）
    if not _triage_reports(reports, checker_data, attempt_id, refine_result):
        return refine_result

    if refine_result.num_FP == 0:  # 采样内一个 FP 都没有 → 无需 refine（此时 num_TP>0，除法安全）
        refine_result.result = "No-FP"
        return refine_result
    elif (refine_result.num_TP / (refine_result.num_TP + refine_result.num_FP)) >= 0.75:
        # precision ≥ 0.75：采样 5 条时等价于 FP≤1 —— 论文 plausible 判据
        # "采样 5 条报告中 FP≤1"的 precision 表达；已足够好，提前收工
        refine_result.result = "High-TP"
        return refine_result

    # Refine checker for false positives
    # 步骤⑤：对每个 FP 报告跑 refinement agent（步骤⑥双准则验证在其内部）
    refine_result.refine_attempt_list = _refine_false_positives(
        reports, checker_data, attempt_id, refine_result, report_dir
    )

    # Save the refined code to files
    # 把（可能已被 refine 的）代码落盘 refinements/（外层 refined=True 时还会再存一次）
    refine_result.save_refined_code(
        Path(checker_data.output_dir), checker_data.checker_id
    )

    return refine_result


# =============================================================================
# 【函数】_initialize_refinement —— 单轮 refine 的编译闸（起点代码必须能编）
# 【职责】把 checker_data.repaired_checker_code（本轮起点代码：首轮=阶段一
#         产物，续轮=上一轮 refine 成功后外层回写的代码）交给 repair_checker
#         编译。论文 §3.1.3 的 syntax repair agent 循环在 refine 阶段复用——
#         起点代码理论上已在阶段一修复过，此处主要起"编译确认 + 拿到规范化
#         代码"作用；真编不过说明代码已损坏 → "Uncompilable" 终止本轮。
# 【参数】checker_data  —— checker 状态（取 checker_id 与起点代码）
#         refine_result —— 成功时回填 checker_code；失败时改写 result
# 【返回】bool：True=编译通过（refine_result.checker_code 已填入，作为本轮
#         working code）；False=失败（result 已置 "Uncompilable"/"Failed"，
#         调用方直接 return 本轮结果）
# =============================================================================
def _initialize_refinement(
    checker_data: CheckerData, refine_result: RefinementResult
) -> bool:
    """Initialize refinement context and compile checker."""
    try:
        correct, checker_code = repair_checker(  # 编译（必要时自动语法修复）；返回 (是否成功, 规范化代码)
            checker_data.checker_id,  # checker 标识（中间产物目录命名用）
            "syntax-repair-" + checker_data.checker_id,  # repair 会话前缀（阶段一修复命名的延续）
            checker_code=checker_data.repaired_checker_code,  # 起点：上一环节留存的"已修复"代码
        )
        if not correct:  # 编不过（连 repair 循环都救不回）→ 本轮判 "Uncompilable"
            logger.error("Failed to compile original code!")
            refine_result.result = "Uncompilable"
            return False

        logger.info("Compiled original code successfully!")
        refine_result.checker_code = checker_code  # 编译通过的代码成为本轮 refine 的 working code（后续 repair_FP 以它为底）
        return True
    except Exception as e:  # 编译流程本身抛异常 → "Failed"（区别于编不过的 "Uncompilable"）
        logger.error(f"Error initializing refinement: {e}")
        refine_result.result = "Failed"
        return False


# =============================================================================
# 【函数】_scan_target —— 用（编译通过的）checker 代码全库扫描收报告
# 【职责】调 backend.run_checker（src/backends/csa.py：编译 checker 为 CSA
#         plugin → 按 target 配置扫目标代码库 → 收集 bug 报告到 output_dir），
#         即论文 §3.2 的"valid checker 全库扫描"步骤（refine 期由 timeout 与
#         报告数双限控制预算，见批1 模块头注）。
# 【参数】checker_code  —— 要上阵的 checker 源码（本轮编译闸通过的版本）
#         bug_report_dir —— 报告输出目录（scan-reports-N/main-report）
#         timeout       —— 扫描限时秒数（来自 global_config.scan_timeout）
#         refine_result —— 失败时改写 result（"Unscannable"/"Failed"）
# 【返回】bool：True=扫描跑完（哪怕 0 报告也算成功——0 报告走 "Perfect"）；
#         False=跑不动（调用方直接 return 本轮结果）
# 【坑】    run_checker 返回 -999 是后端"执行失败"哨兵值（超时/环境坏）而非
#           报告数——只有它触发 "Unscannable"；0 是合法报告数，不在此判失败
# =============================================================================
def _scan_target(
    checker_code: str,
    bug_report_dir: Path,
    timeout: int,
    refine_result: RefinementResult,
) -> bool:
    """Scan kernel with checker and return success status."""
    try:
        run_res = global_config.backend.run_checker(  # 后端执行扫描；返回报告条数（或 -999 哨兵）
            checker_code,  # checker 源码（后端负责编译成 CSA plugin）
            commit_id=global_config.scan_commit,  # 扫描目标 commit（refine 期选定的工作版本，非 checker 出身的 bug commit）
            target=global_config.target,  # 目标抽象（Linux 内核 allyesconfig；fork 增量支持 v8/Chromium）
            jobs=global_config.jobs,  # 并行编译/扫描任务数
            timeout=timeout,  # 扫描限时（论文 refine 期预算的 timeout 一侧）
            output_dir=bug_report_dir,  # 报告落盘目录
        )
        if run_res == -999:  # 哨兵值：扫描根本没跑成（区别于合法的 0 报告）
            logger.error("Failed to run the checker!")
            refine_result.result = "Unscannable"
            return False
        return True  # 跑完即成功；报告多少由后续 extract_reports 处理
    except Exception as e:  # 后端抛异常 → "Failed"（区别于 -999 的 "Unscannable"）
        logger.error(f"Error scanning target: {e}")
        refine_result.result = "Failed"
        return False


# =============================================================================
# 【函数】_process_reports —— 报告蒸馏+采样（复用扫描轮路径）
# 【职责】调 backend.extract_reports：把 CSA 原始输出"报告蒸馏"成只含
#         relevant lines + trace path 的报告（论文 §3.2 报告蒸馏步骤），再按
#         seed 采样 sampled_num 条——采样数 = global_config.max_fp_reports_
#         for_refinement（默认 5，论文"采样 5 条报告"）。本变体用于 scan=False
#         复用路径：同一份全库扫描结果，每轮用不同 seed（=attempt_id）换着
#         采样，让重试轮的 refinement agent 看到不同的 FP 案例。
# 【参数】kernel_report_dir —— 全库扫描报告目录（上轮的 main-report）
#         attempt_id       —— 当前 0-based 轮号（复用模式下作采样 seed）
#         last_scan_id     —— 复用指向的轮号（None → 视为非复用，seed 固定 0）
# 【返回】List[ReportData]：采样报告；空列表 = 无报告/总量过少（调用方置
#         "Perfect"）
# 【坑】    "总量≤10 也判 perfect"：报告太少说明 checker 已足够干净，refine
#           无从下手——与论文 plausible 判据的总量门槛（总报告数 <
#           T_plausible=20）同型，实现常数取 10
# =============================================================================
def _process_reports(
    kernel_report_dir: Path, attempt_id: int, last_scan_id: Optional[int]
) -> List[ReportData]:
    """Process and extract reports from kernel scan."""
    try:
        seed = attempt_id if (last_scan_id is not None) else 0  # 复用轮：seed=当前轮号（每轮换样本）；非复用：seed=0（固定样本）
        reports, total_report = global_config.backend.extract_reports(  # 蒸馏+采样；返回 (采样报告列表, 后端报告总数)
            kernel_report_dir,  # 原始扫描报告目录（main-report）
            kernel_report_dir.parent / "reports",  # 蒸馏后报告落盘目录（main-report 的兄弟目录 reports/）
            seed=seed,  # 采样随机种子（同 seed 同样本，可复现）
            sampled_num=global_config.max_fp_reports_for_refinement,  # 采样条数：默认 5（论文口径）
        )

        logger.info(f"Total reports: {total_report}")  # 后端报告总数（采样前全量）
        if not reports or total_report <= 10:  # 没采到 / 总量太少 → 判 perfect（无需 refine）
            logger.info("Checker is perfect!")
            return []  # 空列表 → 调用方置 "Perfect"

        logger.info(f"Extracted {len(reports)} reports!")  # 实际采样条数（≤5）
        return reports
    except Exception as e:  # 提取失败按"无报告"处理（→ "Perfect"），不让异常炸掉整轮
        logger.error(f"Error processing reports: {e}")
        return []


# =============================================================================
# 【函数】_process_reports_with_count —— 报告蒸馏+采样（真扫描轮路径，带总数）
# 【职责】与 _process_reports 同一套蒸馏+采样逻辑，区别是把"后端报告总数"一并
#         返回（refine_result.num_reports 需要真总数口径；复用路径的
#         _process_reports 拿不到总数，只能退化为采样条数——两路口径不一致，
#         见 refine_checker_attempt 坑注）。
# 【参数】kernel_report_dir —— 全库扫描报告目录（本轮 main-report）
#         attempt_id / last_scan_id —— 同 _process_reports（seed 决定逻辑相同）
# 【返回】tuple (reports, total_reports_in_backend)：采样报告列表 + 后端报告
#         总数；异常时 ([], 0)
# =============================================================================
def _process_reports_with_count(
    kernel_report_dir: Path, attempt_id: int, last_scan_id: Optional[int]
) -> tuple[List[ReportData], int]:
    """Process and extract reports from kernel scan, returning both reports and total count.

    Returns:
        tuple: (extracted_reports, total_reports_found_in_backend)
    """
    try:
        seed = attempt_id if (last_scan_id is not None) else 0  # 同 _process_reports：复用轮换 seed，扫描轮固定 0
        reports, total_reports_in_backend = global_config.backend.extract_reports(  # 蒸馏+采样（逻辑同上，本变体保留总数）
            kernel_report_dir,
            kernel_report_dir.parent / "reports",  # 蒸馏报告落盘：scan-reports-N/reports/
            seed=seed,
            sampled_num=global_config.max_fp_reports_for_refinement,  # 采样 5 条（论文口径）
        )

        logger.info(f"Backend found {total_reports_in_backend} total reports")  # 总数（num_reports 的真口径）
        logger.info(
            f"Extracted {len(reports) if reports else 0} reports for processing"  # 采样条数（reports 为 None 时兜底 0）
        )

        if not reports or total_reports_in_backend <= 10:  # 同 _process_reports 的 perfect 门槛（总量≤10）
            logger.info("Checker is perfect - very few reports found!")
            return [], total_reports_in_backend  # 注意：总数照样带回（num_reports 记真总量）

        return reports, total_reports_in_backend
    except Exception as e:  # 异常 → 无报告 + 总数 0
        logger.error(f"Error processing reports: {e}")
        return [], 0


# =============================================================================
# 【函数】_convert_override_reports_to_report_data —— group scan 报告格式转换
# 【职责】reports_override 路径的适配器：把 group 扫描（fork 增量：多个 checker
#         一次扫描共享报告，省重复扫描）产出的 Dict 列表转成统一 ReportData
#         对象，让后续 triage/refine 流程与标准扫描路径完全同构。
# 【参数】reports_override —— group scan 产出的报告 Dict 列表（键：id/content）
# 【返回】List[ReportData]；单条转换失败只跳过不中断
# 【语义】  report_triage/report_objects 都留空不是缺陷——_triage_reports 会
#           分别用 check_report / get_objects_from_report 重新填
# =============================================================================
def _convert_override_reports_to_report_data(
    reports_override: List[Dict],
) -> List[ReportData]:
    """Convert override reports (from group scanning) to ReportData format."""
    report_data_list = []  # 转换结果收集

    for i, report_dict in enumerate(reports_override):  # 逐条转换（i 用于兜底命名）
        try:
            report_data = ReportData(
                report_id=report_dict.get("id", f"group_report_{i}"),  # 优先取注入的 id；缺失按序号造一个
                report_content=report_dict.get("content", ""),  # 报告正文（蒸馏后的 markdown）；缺失给空串
                report_triage="",  # triage 结论留空（_triage_reports 填）
                report_objects=[],  # 涉及对象留空（_triage_reports 填）
            )
            report_data_list.append(report_data)
        except Exception as e:  # 单条失败（如字段类型不对）跳过，继续转下一条
            logger.error(f"Error converting override report {i}: {e}")
            continue

    return report_data_list


# =============================================================================
# 【函数】_triage_reports —— 论文 §3.2 的 triage agent 逐报告分诊（TP/FP 判定）
# 【职责】对采样出的每条报告做两件事：
#         ① 提取报告涉及的 .o 目标对象（get_objects_from_report）——FP 报告的
#            对象累积进 refine_result.error_objects，作为后续 kill 验证的靶子池；
#         ② 调 agent.check_report（★ triage agent，论文 §3.2）：LLM 依据目标
#            bug pattern 判定报告是真 bug（TP）还是误报（NotABug→FP）。论文
#            强调判定口径是"是否对齐目标 pattern"而非一般代码正确性——
#            checker 只要报出了 pattern 描述的 bug 形态即算 TP。论文战果：
#            triage agent 79 报告 7TP/22FP/50TN/0FN（零漏报）。
# 【参数】reports       —— 采样报告列表（就地填 report_objects/report_triage）
#         checker_data  —— 提供 checker_id 与 pattern（triage prompt 的判定锚）
#         attempt_id    —— 轮号（透传 check_report，用于会话命名/缓存）
#         refine_result —— 就地累加 num_TP/num_FP；FP 对象并入 error_objects
# 【返回】bool：恒 True（当前实现无失败路径；单报告异常只跳过该报告）
# 【坑】    ① check_report 的 patch= 形参传的实参是 checker_data.pattern 而
#           非 checker_data.patch（对照 _attempt_report_refinement 里 repair_FP
#           同位置传的是 checker_data.patch）——疑似上游笔误，忠实保留不改；
#           ② 判 FP 用 "NotABug" 子串匹配（容忍 LLM 输出前后缀噪声），其余
#           一律计 TP——不确定情形倾向当 TP 交给 refine 阈值判定，而非漏计；
#           ③ 单报告 triage 异常被 continue 跳过，num_TP/num_FP 可能轻微低估
# =============================================================================
def _triage_reports(
    reports: List[ReportData],
    checker_data: CheckerData,
    attempt_id: int,
    refine_result: RefinementResult,
) -> bool:
    """Triage reports into true/false positives.
    It will update the refine_result.num_FP, refine_reuslt.num_TP, refine_result.error_objects.
    Store the error objects in refine_result.error_objects.
    """
    # ↑ 原 docstring 原样保留（"refine_reuslt" 为上游笔误）
    for report_data in reports:  # 逐条分诊（每条一次 LLM 调用）
        try:
            objects = global_config.backend.get_objects_from_report(  # 从报告正文解析涉及的 .o 对象（供对象级复扫）
                report_data.report_content, global_config.target
            )
            report_data.report_objects = objects  # 回填报告对象（_validate_on_objects 消费）

            check_res = check_report(  # ★ triage agent（agent.py 的 LLM 调用）：判 Bug / NotABug
                checker_data.checker_id,  # checker 标识
                attempt_id,  # 轮号
                report_id=report_data.report_id,  # 报告 id（prompt/日志锚定）
                report_md=report_data.report_content,  # 报告正文（蒸馏后的 relevant lines + trace path）
                pattern=checker_data.pattern,  # 目标 bug pattern（判定锚：对齐 pattern 而非一般正确性）
                patch=checker_data.pattern,  # 【坑】实参是 pattern 而非 checker_data.patch，疑上游笔误（见函数头坑①）
            )
            report_data.report_triage = check_res  # 回存 triage 原始结论（含推理；_refine_false_positives 按 "NotABug" 子串分流）

            if "NotABug" in check_res:  # 结论含 NotABug → FP（子串匹配；亦作为 repair_FP 的输入让 refinement agent 理解误报原因）
                refine_result.num_FP += 1  # FP 计数
                refine_result.error_objects.update(objects)  # FP 对象并入靶子池（后续 _scan_remaining_objects 逐一验杀）
            else:  # 其余结论（含 "Bug"/不确定措辞）按 TP 计
                refine_result.num_TP += 1

        except Exception as e:  # 单条失败（LLM/解析异常）跳过继续——该报告不计入 TP/FP
            logger.error(f"Error triaging report {report_data.report_id}: {e}")
            continue

    logger.info(f"TP: {refine_result.num_TP}, FP: {refine_result.num_FP}")  # 分诊汇总（No-FP/High-TP 早停判据的输入）
    return True


# =============================================================================
# 【函数】_refine_false_positives —— 对每个 FP 报告跑 refinement agent（论文 §3.2）
# 【职责】过滤出 triage 判 NotABug 的报告，逐个调 _attempt_report_refinement
#         （repair_FP 改 checker → 语法修复 → 双准则验证）。两个关键设计：
#         ① 顺序组合——同一轮内第 2 个 FP 的 refine 以第 1 个 FP refine 后的
#            代码为底（refine_result.checker_code 滚动更新），多个 FP 的修复
#            叠加在一份代码上；
#         ② 每次成功后立即 _scan_remaining_objects：用最新代码复扫靶子池里
#            全部存活 FP 对象——既验当前 FP 被消灭，也回归检查此前 FP 的对象
#            在新代码下依然不再报警（跨 FP 回归）。
# 【参数】reports        —— 全部采样报告（函数内按 triage 结论过滤 FP）
#         checker_data   —— checker 状态
#         attempt_id     —— 轮号（refine_id 组成部分）
#         refine_result  —— 就地更新 checker_code/refined/result/error_objects
#         bug_report_dir —— 对象级复扫报告基目录
# 【返回】List[RefineAttempt]：每个 FP 报告一条尝试记录（成功失败都入列；
#         但 except 分支 continue 的尝试不落盘，见函数内坑注）
# =============================================================================
def _refine_false_positives(
    reports: List[ReportData],
    checker_data: CheckerData,
    attempt_id: int,
    refine_result: RefinementResult,
    bug_report_dir: Path,
) -> List[RefineAttempt]:
    """Refine checker for false positive reports.

    reports: List[ReportData]
    checker_data: CheckerData
    attempt_id: int
    refine_result: RefinementResult
    bug_report_dir: Path
    """
    refine_attempts = []  # 尝试记录收集（无论成败都保留）

    for idx, report_data in enumerate(reports):  # 遍历采样报告（idx 为采样序号，进 refine_id）
        if "NotABug" not in report_data.report_triage:  # 非 FP（TP/未分诊）跳过——只 refine FP
            continue

        logger.info(f"Refine report {idx}...")  # 开始处理第 idx 个 FP（采样序号，非 report_id）

        refine_attempt = RefineAttempt(  # 本 FP 的尝试记录壳（三轮代码快照字段由后续步骤填充）
            refine_id=f"refine-{attempt_id}-{idx}",  # 尝试标识：轮号-采样序号
            report_data=report_data,  # 关联的 FP 报告
            original_code=refine_result.checker_code,  # 本次 refine 的底码=当前 working code（可能是本轮前几个 FP 叠加修复后的版本）
        )
        refine_attempts.append(refine_attempt)  # 先入列（哪怕后续失败也保留记录）

        try:
            refined_code = _attempt_report_refinement(  # ★ refinement agent 全流程：repair_FP → 抽代码 → 编译修复 → 双准则验证
                checker_data, report_data, refine_result, refine_attempt, bug_report_dir
            )

            if refined_code:  # 拿到通过双准则验证的新代码
                refine_result.checker_code = refined_code  # 滚动更新 working code（下一个 FP 以它为底——顺序组合）
                refine_result.refined = True  # 本轮标记 refined（名义口径）
                refine_result.result = "Refined"  # 状态置 Refined（外层状态机会重新扫描验证新代码）

                # Scan remaining error objects
                # 用最新代码复扫全部存活 FP 对象：杀掉的记入本尝试 killed_objects
                # 并移出靶子池（没杀掉的留给后续尝试继续处理）
                _scan_remaining_objects(
                    refined_code,
                    refine_result.error_objects,
                    bug_report_dir,
                    refine_attempt,
                )

        except Exception as e:  # 单个 FP 的 refine 异常：跳过该报告继续下一个
            # 【坑】此 continue 跳过了下方的 dump_dir——异常尝试的快照不落盘
            logger.error(f"Error refining report {idx}: {e}")
            continue

        refine_attempt.dump_dir(checker_data.output_dir)  # 尝试记录落盘（output_dir 下按 refine_id 归档三轮快照）

    return refine_attempts


# =============================================================================
# 【函数】_attempt_report_refinement —— 单个 FP 报告的 refinement 全流程
#         （论文 §3.2 refinement agent + 双准则接受）
# 【职责】四步流水：
#         ① repair_FP（agent.py 的 ★ refinement agent，论文 §3.2）：把 FP
#            报告、triage 结论、当前 checker 代码、pattern/patch 喂给 LLM，
#            让它修改 checker 逻辑消除该类 FP（论文例：学会 unlikely() 宏
#            是合法空检查）；
#         ② extract_checker_code 从回复中抠出 ```cpp fence 代码；推理过程
#            （回复去掉代码后的剩余文本）存进 refine_attempt.reasoning_process；
#         ③ repair_checker 编译 + 语法修复（§3.1.3 repair agent 复用；中间
#            产物落 output/intermediate/）；
#         ④ 双准则验证（论文的接受条件，两条都要过）：
#            (1) _validate_on_objects——该 FP 报告涉及对象复扫不再报警；
#            (2) _validate_on_commit——buggy/patched 差分验证仍通过（检出
#                能力没被改没）。
# 【参数】checker_data / report_data —— checker 状态与 FP 报告
#         refine_result  —— 提供当前 working code（refine 的底码）
#         refine_attempt —— 记录壳（reasoning_process/三轮代码快照在此填充）
#         report_dir     —— 对象级复扫报告基目录
# 【返回】Optional[str]：通过全部验证的新 checker 代码；任一步失败返回 None
# =============================================================================
def _attempt_report_refinement(
    checker_data: CheckerData,
    report_data: ReportData,
    refine_result: RefinementResult,
    refine_attempt: RefineAttempt,
    report_dir: Path,
) -> Optional[str]:
    """Attempt to refine checker for a single report."""
    refined_code = repair_FP(  # ★ refinement agent（agent.py 的 LLM 调用）：修改 checker 逻辑消除 FP
        checker_data.checker_id,  # checker 标识
        report_data.report_id,  # 触发本次 refine 的 FP 报告 id
        checker_data.commit_id,  # checker 出身的 bug commit（LLM 上下文）
        checker_data.pattern,  # 目标 bug pattern（LLM 判定锚）
        report_data.report_content,  # FP 报告正文（要消除的报警）
        refine_result.checker_code,  # 当前 checker 代码（修改底码——顺序组合的接续点）
        report_data.report_triage,  # triage agent 判词（含 NotABug 推理，供 LLM 理解为何误报）
        patch=checker_data.patch,  # 原始 bug-fix patch（对照：_triage_reports 同位置误传 pattern，见其坑①）
    )

    if not refined_code:  # LLM 没返回内容 → 放弃本报告
        logger.error("Failed to get the refined code!")
        return None

    # Also log down the reasoning process
    # 推理过程留档：先存 LLM 完整回复，再抽出代码，最后把代码从回复中删掉——
    # 剩下的纯文本就是 reasoning_process（RefineAttempt 落盘字段之一）
    refine_attempt.reasoning_process = refined_code  # 暂存完整回复（代码+推理混在一起）
    refined_code = extract_checker_code(refined_code)  # 抠出 ```cpp fence 内的 checker 代码（tools.py）
    refine_attempt.reasoning_process = refine_attempt.reasoning_process.replace(
        refined_code, ""  # 从完整回复中删除代码段（首次出现处）
    ).strip()  # 去首尾空白 → 纯推理文本

    if not refined_code:  # 回复里抠不出代码（没写 fence 等）→ 放弃
        logger.error("Failed to extract checker code!")
        return None

    refine_attempt.initial_refine_code = refined_code  # 三轮快照之一：LLM 原始产出（未编译修复）

    # Compile refined code (and repair if needed)
    # 编译+语法修复（§3.1.3 repair agent 循环；中间版本落 intermediate/ 便于排查）
    correct, repaired_code = repair_checker(
        checker_data.checker_id,
        "syntax-repair-" + refine_attempt.refine_id,  # 会话前缀带 refine_id（与初始编译闸的前缀区分）
        checker_code=refined_code,
        intermediate_dir=Path(checker_data.output_dir) / "intermediate",  # 编译失败中间产物归档目录
    )
    if not correct:  # 连 repair 循环都编不过 → 放弃本报告
        logger.error("Failed to compile refined code!")
        return None

    refine_attempt.syntax_correct_refine_code = repaired_code  # 三轮快照之二：语法正确版

    # Validate on objects
    # 双准则 (1)：该 FP 报告的对象复扫不再报警（对象级验证）
    if not _validate_on_objects(
        repaired_code, report_data.report_objects, report_dir, refine_attempt
    ):
        logger.error("Failed to validate on objects!")
        return None

    # Validate on original commit
    # 双准则 (2)：buggy/patched 差分验证仍通过（检出能力未被改没）
    if not _validate_on_commit(repaired_code, checker_data, refine_attempt):
        logger.error("Failed to validate on the original commit!")
        return None

    return repaired_code  # 两准则全过 → 新代码正式生效（调用方滚动更新 working code）


# =============================================================================
# 【函数】_validate_on_objects —— 双准则之 (1)：原 FP 对象不再报警（对象级验证）
# 【职责】用 refine 后的 checker 逐对象复扫（_scan_objects 的单对象扫描远快于
#         全库扫描），收集"不再报警"的对象（no_bug_objects）。判定口径：
#         no_bug_objects 非空即通过——实践上单条报告通常只涉及一个 .o 对象，
#         此时等价于"该 FP 报告消失"（论文双准则条件 (1)）；若一条报告涉及
#         多个对象，属"至少消灭一个"的弱判据。杀掉的对象记入
#         refine_attempt.killed_objects（_check_code_changed 真改码判定的
#         证据之一）。
# 【参数】checker_code   —— refine 后待验代码
#         objects        —— 该 FP 报告涉及的对象列表
#         report_dir     —— 复扫报告基目录（其下按对象建 report-* 子目录）
#         refine_attempt —— 成功时追加 killed_objects
# 【返回】bool：True=至少一个对象不再报警（通过）；False=全部对象仍在报警
# =============================================================================
def _validate_on_objects(
    checker_code: str,
    objects: List[str],
    report_dir: Path,
    refine_attempt: RefineAttempt,
) -> bool:
    """Validate refined checker on specific objects."""
    objects = list(set(objects))  # 去重（同一对象可能被重复解析出）
    no_bug_objects = _scan_objects(checker_code, objects, report_dir)  # 复扫：返回不再报警的对象子集
    if not no_bug_objects:  # 一个都没杀掉 → FP 仍在 → 验证失败
        return False

    refine_attempt.killed_objects.extend(no_bug_objects)  # 记入战果（真改码判定+日志统计的依据）
    return True


# =============================================================================
# 【函数】_validate_on_commit —— 双准则之 (2)：buggy/patched 差分验证仍通过
# 【职责】把 refine 后的代码送回阶段一的 validation（论文 §3.1.4 差分验证在
#         refine 阶段复跑）：backend.validate_checker 会 checkout 到 patch 的
#         父提交（buggy）扫 patch 涉及对象、再 checkout 到 patched 提交扫，
#         返回 (newTP, newTN)。接受条件 newTP>0 且 newTN>0：buggy 侧仍能
#         报出（检出能力保住了）且 patched 侧不报（没引入新 FP）——防止
#         refinement agent"矫枉过正"把 checker 改成永不报警的哑巴。
# 【参数】checker_code   —— refine 后待验代码（已过语法修复）
#         checker_data   —— 提供 commit_id 与 patch（差分验证的两个锚点）
#         refine_attempt —— 通过时写入 semantic_correct_refine_code（三轮
#                           快照之三；_check_code_changed 真改码判定的必要字段）
# 【返回】bool：True=差分验证通过；False=newTP/newTN 任一不达标
# =============================================================================
def _validate_on_commit(
    checker_code: str, checker_data: CheckerData, refine_attempt: RefineAttempt
) -> bool:
    """Validate refined checker on original commit."""
    newTP, newTN = global_config.backend.validate_checker(  # 差分验证：返回 (buggy 侧检出分, patched 侧干净分)
        checker_code,
        checker_data.commit_id,  # checker 出身的 bug commit
        checker_data.patch,  # 原始 bug-fix patch（父提交=buggy / 本提交=patched）
        target=global_config.target,  # 目标抽象（与阶段一验证同配置，保证可比）
        skip_build_checker=True,  # 跳过重新编译 checker（repair_checker 刚编过，直接复用 plugin）
    )

    if not (newTP > 0 and newTN > 0):  # 任一侧不达标（检不出真 bug / 在 patched 侧引入新报）→ 验证失败
        return False

    refine_attempt.semantic_correct_refine_code = checker_code  # 语义正确快照（_check_code_changed 的必要条件之一）
    return True


# =============================================================================
# 【函数】_scan_remaining_objects —— 用最新 refine 代码复扫靶子池（跨 FP 回归）
# 【职责】每次单 FP refine 成功后调用：对 refine_result.error_objects（本轮
#         全部 FP 报告涉及、且尚未被杀掉的对象）做单对象复扫。杀掉的对象
#         ① 记入当前 refine_attempt.killed_objects（战果归属本次尝试）；
#         ② 从靶子池移除（后续 FP 的复扫只查仍存活的，省扫描次数）。
#         这同时是回归检查：上一个 FP 的对象在新代码下若"复活"，会留在池中
#         继续被后续尝试处理。
# 【参数】checker_code   —— 最新的 refine 后代码（滚动 working code）
#         error_objects  —— 靶子池（Set，就地删除已杀对象）
#         report_dir     —— 复扫报告基目录
#         refine_attempt —— 战果归属的尝试记录
# 【返回】None（战果与池更新都是副作用）
# =============================================================================
def _scan_remaining_objects(
    checker_code: str,
    error_objects: Set[str],
    report_dir: Path,
    refine_attempt: RefineAttempt,
) -> None:
    """Scan remaining error objects with refined checker."""
    no_bug_objects = _scan_objects(checker_code, list(error_objects), report_dir)  # 复扫全部存活靶子（Set 转列表以稳定遍历）
    refine_attempt.killed_objects.extend(no_bug_objects)  # 本轮新杀掉的对象记入当前尝试
    for obj in no_bug_objects:  # 从靶子池移除已杀对象（no_bug_objects ⊆ 传入的 error_objects，remove 安全不抛 KeyError）
        error_objects.remove(obj)


# =============================================================================
# 【函数】_scan_objects —— 对象级复扫（单对象粒度的 checker 验证引擎）
# 【职责】对每个 .o 目标对象单独跑一次 backend.run_checker（object_to_analyze
#         限定只分析该编译单元——远快于全库扫描），返回其中"0 报告"（=该
#         对象上的报警已被 refine 消灭）的对象列表。这是论文双准则 (1) 的
#         执行引擎，被 _validate_on_objects（验当前 FP）与
#         _scan_remaining_objects（回归验历史 FP）共用。
# 【参数】checker_code —— 待验 checker 源码
#         objects     —— 目标对象列表（如 "drivers/net/foo.o"）
#         report_dir  —— 报告基目录（每对象一个 report-{id} 子目录）
# 【返回】List[str]：不再报警的对象子集（被"杀掉"的靶子）
# 【性能】 skip_build_checker=True：checker plugin 已编译过（本轮编译闸/
#         repair_checker 产物），直接复用；skip_checkout=(i>0)：仅首个对象
#         做目标库 checkout，其后对象复用同一工作区（原注释措辞略歧义，
#         实际语义如此）——同批对象必然同 commit（scan_commit），checkout
#         一次就够
# =============================================================================
def _scan_objects(checker_code: str, objects: List[str], report_dir: str) -> List[str]:
    """
    Scan objects with the checker.
    It will return the objects that don't have bug.

    Args:
        checker_code (str): The code of the checker.
        objects (List[str]): The objects to scan.
        report_dir (str): The directory to store the reports.

    Returns:
        List[str]: The objects that don't have bug.
    """
    no_bug_objects = []  # 被杀掉的靶子收集
    for i, target_object in enumerate(objects):  # 逐对象扫描（i 用于首对象 checkout 策略）
        cur_report_dir = Path(report_dir) / f"report-{get_object_id(target_object)}"  # 每对象独立报告目录（对象名净化后作目录名）

        # For performance, we skip the checker build and linux checkout for the first object
        # 单对象扫描：object_to_analyze 限定分析范围；skip 策略见函数头【性能】注
        num_bug = global_config.backend.run_checker(
            checker_code,
            commit_id=global_config.scan_commit,  # 与全库扫描同一 commit（结果可比性前提）
            target=global_config.target,
            object_to_analyze=target_object,  # 只分析这一个编译单元
            output_dir=cur_report_dir,  # 该对象的报告落盘
            skip_build_checker=True,  # plugin 已建，复用
            skip_checkout=(i > 0),  # 首对象做 checkout，其余复用工作区
        )
        if num_bug == 0:  # 0 报告 = 该对象上的报警消失（0 是合法结果，与 -999 哨兵区分）
            logger.info(f"Object {target_object} doesn't have bug!")
            no_bug_objects += [target_object]  # 记入战果
    return no_bug_objects


# =============================================================================
# 【函数】get_object_id —— 对象路径 → 报告目录名（路径净化）
# 【职责】把 .o 对象路径变成可作目录名的标识："drivers/net/foo.o" →
#         "drivers-net-foo"（/ → -、删 .o、去首尾空白）。供 _scan_objects
#         构造 report-{id} 子目录名。
# 【坑】    replace 是子串级而非后缀级：路径中任何 ".o" 子串都会被删（如
#           "a.o.omic" → "a-mic"）；内核 .o 对象路径实践中不构成问题
# =============================================================================
def get_object_id(object_name: str) -> str:
    return object_name.replace("/", "-").replace(".o", "").strip()  # / → -（目录分隔符不能进目录名）；删 .o 子串；去首尾空白

# =============================================================================
# 【批2 接力完成】checker_refine.py 全文件注释至此收口：
#   批1 = 原 1-714 行（驱动层：编排/进度/盘点/状态机/日志鉴别器）；
#   批2 = 原 715-1414 行（核心执行层：_save_refine_log_to_file /
#   create_refinement_summary / refine_checker_attempt 及全部子步骤）。
#   论文 §3.2 的 triage（check_report 判 NotABug 即 FP）、refinement
#   （repair_FP 改 checker 逻辑）、双准则接受（_validate_on_objects 对象
#   复扫 + _validate_on_commit buggy/patched 差分验证）与"采样 5 条"
#   （global_config.max_fp_reports_for_refinement）的落地点均在本段。
#   验证：AST 等价 + token 等价 + compile + 真空行只增；批1 区段逐字节未动。
# =============================================================================
