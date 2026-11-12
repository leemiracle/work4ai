# =============================================================================
# 【模块定位】论文 §3.1.3 Implementation + Syntax Repair 中"语法修复"的编排器：
#   checker.cpp 首次编译失败后，把编译错误喂给 repair agent 修语法，循环往复
#   直到编译通过或次数耗尽——全模块仅一个对外函数 repair_checker()。
#
# 【论文映射】KNighter（arXiv:2503.09002, SOSP'25）§3.1.3 / Algorithm 1 Stage 3：
#   实现阶段生成 checker.cpp 后编译失败，则 repair agent 依编译错误修复，
#   最多 maxAttempts=5 次。本实现 = 1 次首编 + MAX_REPAIR_ATTEMPTS=4 次修复
#   共 5 次尝试，与论文口径一一对应。论文消融：引入 Plan 阶段后语法错误从
#   52 降到 28（validity 12 vs 8），本修复循环是 validity 的最后一道闸；
#   273 次失败尝试中 65 次是编译错（最终修不好的部分即由这里放弃）。
#
# 【管线角色】
#   上游调用方三处：src/checker_gen.py:391（§3.1 阶段一实现阶段的主路径——
#     plan2checker 产出初版 checker 后交本函数"编译+修复"）；
#     src/checker_refine.py 两处（§3.2 refinement agent 改完 checker 逻辑后
#     需重新编译，同样复用本修复循环兜底语法问题）。
#   下游：global_config.backend.build_checker（backends/csa.py——写 cpp 到
#     LLVM plugin 目录并 make {name}Plugin，返回 returncode+stderr）；
#     agent.repair_syntax（repair agent，prompt_template/repair.md：
#     {checkercode} + {errors} 两个占位符）。
#
# 【关键依赖与坑】
#   - repair_syntax 返回 LLM 原始文本，必须经 tools.extract_checker_code 剥掉
#     ```cpp 围栏才是可编译源码；剥取失败（None）只 continue——注意这会白白
#     消耗一轮：下一轮 attempt 用旧代码再编译必然复现同一错误。
#   - 坑1：函数 docstring 声称返回三元组 Tuple[bool, Optional[str], list]，
#     实际签名/返回只有 (bool, Optional[str])——原仓笔误，保留不动。
#   - 坑2：repair_syntax 走 agent 层的 prompt_history 落盘机制
#     （prompt_history/{repair_name}/response_repair_syntax-{times}.md），
#     同名重跑直接复用缓存响应，不重复烧 LLM 调用。
#   - 坑3：编译错误先经 tools.grab_error_message 正则（"error:.*" 行）提取
#     成 markdown 清单再进 prompt——只喂错误行，不喂整个 stderr。
# =============================================================================
from pathlib import Path                        # 路径类型：中间版本/日志目录管理
from typing import Optional, Tuple              # 类型标注：返回 (bool, Optional[str])

from agent import repair_syntax                 # repair agent（论文 §3.1.3）：LLM 依编译错误修 checker 语法
from global_config import global_config, logger # 全局配置单例（result_dir/backend）+ loguru 日志
from tools import extract_checker_code          # 从 LLM 响应剥 ```cpp 围栏，提取纯 checker 源码

# Define constants for clarity  ← 原注释：常量化便于理解
MAX_REPAIR_ATTEMPTS = 4  # 修复次数上限：4 次修复 + 1 次首编 = 论文 maxAttempts=5 次总尝试


# -----------------------------------------------------------------------------
# repair_checker(id, repair_name, checker_code, max_idx, intermediate_dir)
#   —— "编译 + LLM 语法修复"循环（论文 §3.1.3 Syntax Repair 封装）
# 职责：反复【编译 checker → 失败则把 stderr 错误喂 repair_syntax（repair agent）
#       修代码 → 再编译】，直到编译通过（return True + 最终代码）或次数/错误
#       信息耗尽（return False, None）。
# 参数：id —— checker 标识（结果目录名，通常为 commit_id）；repair_name ——
#   本次修复会话名（区分生成期/各轮 refine 期的产物目录）；checker_code ——
#   初版 checker 源码；max_idx —— 修复次数上限（默认 MAX_REPAIR_ATTEMPTS=4，
#   总尝试 = max_idx+1 = 5，对应论文 maxAttempts=5）；intermediate_dir ——
#   中间版本落盘目录（默认 base_dir/intermediate-{repair_name}）。
# 返回：(success, repaired_code)：成功 = (True, 最终可编译代码)；
#   失败 = (False, None)。注意 docstring 里写的 list 返回是原仓笔误，实际二元组。
# -----------------------------------------------------------------------------
def repair_checker(
    id: str,
    repair_name: str,
    checker_code: str,
    max_idx: int = MAX_REPAIR_ATTEMPTS,
    intermediate_dir: Optional[Path] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Repair the checker code using a language model.

    Args:
        id (str): The ID of the checker.
        repair_name (str): The name of the repair.
        checker_code (str): Initial checker code.
        max_idx (int): The maximum number of repair attempts.
        intermediate_dir (Optional[Path]): Directory for intermediate files.
    Returns:
        Tuple[bool, Optional[str], list]: A tuple containing:
            - success (bool): Whether the repair was successful.
            - repaired_code (Optional[str]): The repaired checker code.
    """

    base_dir = Path(global_config.result_dir) / id  # 该 checker 的结果根目录：result_dir/{id}/

    # Setup directories  ← 原注释：三件套目录初始化
    prompt_history_dir = base_dir / "prompt_history" / repair_name  # prompt/响应留档目录（LLM 调用可追溯 + 断点复用）
    prompt_history_dir.mkdir(parents=True, exist_ok=True)  # 递归创建（已存在复用）

    if intermediate_dir is None:  # 调用方未指定中间目录
        intermediate_dir = base_dir / f"intermediate-{repair_name}"  # 默认：result_dir/{id}/intermediate-{repair_name}/
    intermediate_dir.mkdir(parents=True, exist_ok=True)  # 递归创建

    log_dir = base_dir / "build_logs" / repair_name  # 编译日志目录（build_stderr_{attempt}.log 逐轮落盘）
    log_dir.mkdir(parents=True, exist_ok=True)  # 递归创建

    current_checker_code = checker_code  # 当前待编译版本（随修复轮次演进）

    for attempt in range(1, max_idx + 2):  # attempt = 1..max_idx+1，即 1..5：第 1 次是初版代码首编，之后每次编译修复后的新代码
        # Allow max_idx attempts + 1 initial try  ← 原注释：max_idx 次修复 + 1 次首编
        logger.info(f"Compilation attempt {attempt}/{max_idx + 1}")  # 汇报进度（如 3/5）

        return_code, stderr_content = global_config.backend.build_checker(  # 经 backend 编译：写 cpp 到 LLVM plugin 目录 + make（stdout/stderr 逐轮落 log_dir）
            current_checker_code,  # 当前版本源码
            log_dir,  # 编译日志目录
            attempt=attempt,  # 日志文件名带轮次号
        )

        if return_code == 0:  # 编译通过——修复成功（或初版本来就通过）
            logger.info("Syntax repair successful!")  # 成功日志
            # Read the successfully compiled code back, in case _run_compilation modified it (unlikely here)  ← 原注释：防御性说明
            final_code = current_checker_code  # 直接取当前版本（backend 理论上不改代码）
            return True, final_code  # 返回成功 + 最终代码

        # Compilation failed  ← 原注释：编译失败路径
        logger.warning(  # 记录失败轮次与返回码
            f"Compilation attempt {attempt} failed with return code {return_code}."
        )
        if not stderr_content:  # stderr 为空：无从得知错误，repair agent 没有输入
            logger.warning("Compilation failed, but stderr was empty.")  # 提示异常情形
            return False, None  # 直接放弃（无法修复）
        if attempt > max_idx:  # 修复次数已耗尽（第 max_idx+1 轮仍失败）
            logger.error(f"Repair failed after {max_idx} attempts.")  # 终局失败日志
            return False, None  # 放弃（对应论文 22 个 invalid 中 13 个 implementation 不准的一部分）

        # Attempt repair  ← 原注释：进入 LLM 修复
        logger.info(f"Attempting repair {attempt} using LLM...")  # 汇报修复轮次
        try:  # LLM 调用与代码提取的兜底
            llm_response = repair_syntax(  # 调 repair agent（论文 §3.1.3）：repair.md 模板填 {checkercode}=当前源码 + {errors}=grab_error_message 提取的错误行清单
                id, repair_name, attempt, current_checker_code, stderr_content  # 实参 = (id, 会话名, 轮次, 当前代码, 编译 stderr)
            )
            new_checker_code = extract_checker_code(llm_response)  # 剥掉响应里的 ```cpp 围栏，提取纯源码（失败返回 None）

            if new_checker_code is None:  # 提取失败（LLM 没按格式输出代码块）
                logger.error(  # 记录提取失败
                    f"Failed to extract new checker code from LLM response for attempt {attempt}."
                )
                continue  # 跳过本轮（注意：下一轮仍用旧代码编译，必然复现同一错误，等效浪费一次尝试）
            else:  # 提取成功
                # Write back the new checker code for the next attempt  ← 原注释：回写新代码供下轮编译
                current_checker_code = new_checker_code  # 更新当前版本
                (intermediate_dir / f"checker-{attempt}.cpp").write_text(  # 中间版本留档（checker-{轮次}.cpp，便于事后审计 LLM 每轮改了什么）
                    current_checker_code
                )
        except Exception as e:  # LLM 调用/写盘任意异常
            logger.error(f"Error during LLM repair call for attempt {attempt}: {e}")  # 记录异常
            # Decide whether to retry or fail  ← 原注释：此处选择直接失败（不重试）
            return False, None  # 放弃
    # Should not be reached if loop logic is correct, but as a safeguard:  ← 原注释：逻辑上不可达的兜底分支
    logger.error("Exited repair loop unexpectedly.")  # 记录异常退出
    return False, None  # 安全兜底返回失败
