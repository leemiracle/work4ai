# =============================================================================
# 【模块定位】KNighter 两阶段管线的公共工具函数库：编译错误蒸馏、LLM 回复
#  中的 checker 代码抽取、子进程监控与强杀、CSA(scan-build) HTML 报告蒸馏、
#  以及基于 tree-sitter 的"patch 涉及函数完整源码"提取——论文各阶段的公共
#  底座（本文件全部为无状态纯函数/工具，不持有配置与 LLM 客户端）。
#
# 【论文映射】（术语对照 paper-brief 速查卡）
#  - grab_error_message / error_formatting → 论文 §3.1.3 Implementation +
#    Syntax Repair：把 clang 编译错误蒸馏成 markdown 反馈给 repair agent
#    （消费方 src/agent.py；论文统计 273 次失败尝试中 65 次编译错，靠此
#    反馈循环最多修复 maxAttempts=5 轮）。
#  - grab_cpp_code / extract_checker_code → 从 implementation agent（§3.1.3）
#    / repair agent（§3.1.3）/ refinement agent（§3.2）的 LLM 回复中抽取
#    ```cpp 围栏里的 checker.cpp 源码（消费方 checker_gen.py /
#    checker_repair.py / checker_refine.py 三处 import）。
#  - monitor_build_output / force_terminate_process(_group) /
#    create_monitored_process / _drain_queue → 差分验证（§3.1.4）与全库
#    扫描（§3.2）的子进程监控层：超时 timeout + 警告数 warning_limit 双闸门，
#    即论文"refine 期间限 1 小时或 100 warnings、正式找 bug 时不限"的工程
#    落点——实际调用：backends/csa.py 传 warning_limit=300+timeout，
#    checker_scan.py 全库扫描传 warning_limit=-1（不设警告闸门）。
#  - get_source_code / remove_text_section → 论文 §3.2 报告蒸馏：从
#    scan-build 的 HTML 报告只保留 relevant lines + trace path，喂给 triage
#    agent 判 FP（消费方 backends/csa.py:2328、checker_scan.py:285）。
#  - get_function_codes(_with_config) / get_changed_lines_in_diff /
#    truncate_large_file → 论文 §3.1.1 Bug Pattern Analysis 的输入构造：
#    "patch diff 之外还给 LLM 完整函数上下文"（消费方 targets/factory.py）。
#  - path_similarity / object_name / get_num_bugs → Linux 单目标时代版本；
#    现行调用链已在 targets/linux.py（linux-build-commands.txt）、
#    targets/v8.py（v8-build-commands.txt）、backends/csa.py:2244 各内嵌
#    一份同逻辑副本——此三函数在 src/ 内已无 import 方，仅作历史保留。
#
# 【管线角色】被 agent.py / checker_gen.py / checker_scan.py /
#  checker_refine.py / checker_repair.py / backends/csa.py /
#  targets/factory.py 七处 import，横跨 Checker Synthesis（阶段一）与
#  Checker Refinement（阶段二）。
#
# 【关键依赖与坑】
#  - KernelFunction 来自 src/kparser/kfunction.py（tree-sitter==0.21.3 +
#    vendored tree-sitter-cpp；grammar 编译坑见 kparser/kparser.py 头注释）。
#  - lstrip/rstrip 的字符串实参是"字符集合"而非前缀：extract_checker_code
#    与 error_formatting 两处属"侥幸正确"（代码以 #include 开头时 '#' 不在
#    集合内），详见各函数处注释。
#  - get_function_codes 把 patch 父版本源码写到 CWD 的 __temp.c 临时文件
#    （正常/异常路径均有 unlink 清理，但进程被强杀时可能残留）。
#  - object_name 依赖 CWD 下的 commands.txt（编译命令库），只能在正确的
#    working directory 下调用（历史函数，见上）。
# =============================================================================
import datetime  # 日期时间 stdlib；上游遗留 import，本文件内实际未使用（按"只增注释不动代码"铁律保留）
import html  # html.unescape：还原 &lt; &gt; &amp; 等 HTML 实体（get_source_code 清洗源码行用）
import io  # io.TextIOWrapper：给子进程的二进制管道套 UTF-8 文本流，供逐行读取
import json  # 解析 scan-build HTML 内嵌 JS 变量 relevant_lines = {...} 的 JSON 字面量
import os  # os.sep 路径分隔符 / os.name 平台判断 / os.setsid 建新进程组（create_monitored_process）
import re  # 全文件正则底座：编译错误抓取、代码围栏抽取、diff hunk 行号、.o 目标匹配
import subprocess  # Popen/TimeoutExpired：子进程创建、等待与超时判定
import threading  # monitor_build_output 的 stdout/stderr 双读线程 + threading.Event 停止信号
import time  # time.time() 计时实现 timeout 闸门（与 warning_limit 构成双闸）
from pathlib import Path  # 面向对象路径：临时文件 __temp.c、stem 提取、.o 后缀推导
from queue import Queue  # 线程安全队列：读线程 → 主监控线程 传递输出行（哨兵 None 表示流结束）

from bs4 import BeautifulSoup  # 解析 scan-build HTML：拆 <table class="code"> 源码表与 msgEvent/msgControl 轨迹行
from loguru import logger  # 结构化日志（贯穿全仓的标准日志门面）

from kparser.kfunction import KernelFunction  # tree-sitter 函数对象；get_function_codes 用它提取完整函数源码（论文 §3.1.1）


# -----------------------------------------------------------------------------
# 从编译器输出中抓取 clang 诊断错误块。
#
# 【职责】用正则从（checker 编译/链接的）输出里切出"error 消息行 + 源码定位
#   行"两行一组的错误片段，供 error_formatting 二次加工成 markdown。
# 【论文语义】§3.1.3 Syntax Repair 的第一步：LLM 生成的 checker.cpp 编译
#   失败时，需把错误蒸馏后反馈给 repair agent（消费方 src/agent.py）。
# 【参数】error_content: str —— 编译命令的完整输出文本
# 【返回】list[str] —— 每个元素是一次匹配到的两行错误块
# -----------------------------------------------------------------------------
def grab_error_message(error_content: str) -> list:
    # 正则拆解：r"error:.*\n\s*\d+\s*\|\s+.*\n"
    #   error:.*\n   → 以 "error:" 开头到行尾的一行（clang 诊断首行）
    #   \s*\d+\s*    → 下一行行首缩进 + 十进制行号（\s* 兼容对齐空格）
    #   \|           → 字面竖线：clang 的 "行号 | 源码" 定位格式
    #   \s+.*\n      → 竖线后至少一个空白 + 源码内容到行尾
    #   re.MULTILINE → 多行模式下 ^ $ 按行界（防御多错误连排场景）
    pattern = r"error:.*\n\s*\d+\s*\|\s+.*\n"
    error_list = re.findall(pattern, error_content, re.MULTILINE)  # 全量收集所有错误块

    return error_list


# -----------------------------------------------------------------------------
# 把 grab_error_message 抓到的错误块渲染成 markdown 列表（repair agent 的
# prompt 素材，由 agent.py 组装进修复请求）。
# 【职责】每条错误输出两行："Error Line"（源码定位行）+ 缩进的
#   "Error Messages"（error 消息行）。
# 【坑】error_parts[0].lstrip("error: ") 的实参是字符集合 {'e','r','o',':',' '}
#   而非前缀字符串——对 "error: reference to ..." 这类消息，剥完前缀后会
#   继续把 'r','e' 剥掉得到 "ference to ..."（已实测复现）。多数消息首字符
#   不在集合内故侥幸正确；属上游遗留隐患，注释版原样保留。
# 【参数/返回】error_list: list[str]（grab_error_message 输出）→ markdown 文本
# -----------------------------------------------------------------------------
def error_formatting(error_list: list) -> str:
    error_list_md = ""  # 累积的 markdown 结果串
    for error in error_list:  # 逐条错误块处理
        error_list_md += "- Error Line: "  # 列表项头：源码定位行标签
        error_parts = error.split("\n")  # 两行错误块按行拆开：[0]=error 消息行，[1]=定位行
        error_list_md += error_parts[1].lstrip()  # 定位行去缩进后拼入（形如 "123 | foo();"）
        error_list_md += "\n\n"  # 与错误消息隔一空行
        error_list_md += "\t- Error Messages: "  # 缩进一级的错误消息标签
        error_list_md += error_parts[0].lstrip("error: ")  # 剥 "error: " 前缀（注意字符集合语义，见上方坑注）
        error_list_md += "\n\n"  # 与下一条错误块隔开
    return error_list_md  # 拼好的 markdown（空列表时返回 ""）


# -----------------------------------------------------------------------------
# 从 LLM 回复中抽取第一个 C++ 代码围栏（返回值含围栏标记本身）。
#
# 【职责】两段式匹配：优先找 ```cpp 围栏，找不到再退而匹配无语言标注的
#   裸 ``` 围栏（兼容模型偶尔省略 cpp 标签）。
# 【论文语义】§3.1.3 implementation agent / repair agent 与 §3.2 refinement
#   agent 的输出都把 checker.cpp 写在代码围栏里，本函数是统一出口（经
#   extract_checker_code 被 checker_gen/checker_repair/checker_refine 消费）。
# 【参数】llm_response: str —— 模型原始回复
# 【返回】str | None —— 匹配到的完整围栏文本（```cpp\n...\n```）；无围栏 None
# -----------------------------------------------------------------------------
def grab_cpp_code(llm_response: str) -> str:
    # 第一优先：带 cpp 语言标注的围栏。
    # 正则拆解：r"```cpp\n([\s\S]*?)\n```"
    #   ```cpp\n    → 围栏起始（字面三反引号+cpp+换行）
    #   ([\s\S]*?)  → 惰性捕获组：[\s\S] 匹配任意字符（含换行），*? 保证
    #                 停在"第一个"结束围栏，避免跨多个围栏贪心吞并
    #   \n```       → 结束围栏前的换行 + 三个反引号
    pattern = r"```cpp\n([\s\S]*?)\n```"
    match = re.search(pattern, llm_response)  # 只取第一个匹配
    if match:
        return match.group()  # 注意返回 group()=group(0)：连围栏标记一起返回

    # 兜底：无语言标注的围栏（模型偶尔输出裸 ```）
    pattern = r"```\n([\s\S]*?)\n```"  # 同上，仅少了 cpp 标注
    match = re.search(pattern, llm_response)
    if match:
        return match.group()
    return None  # 回复里没有任何代码围栏——上游据此报 "Failed to extract checker code!"


# -----------------------------------------------------------------------------
# 从 LLM 回复中抽出可落盘的 checker.cpp 源码（剥掉围栏标记）。
#
# 【职责】grab_cpp_code 的薄封装：拿到围栏后剥掉 ```cpp\n 前缀与 ``` 尾部，
#   返回纯代码文本，供调用方直接写成 checker 源文件交给编译。
# 【论文语义】§3.1.3/§3.2 各 agent 输出的统一后处理；三个消费方：
#   checker_gen.py（implementation agent）、checker_repair.py（repair
#   agent）、checker_refine.py（refinement agent）。
# 【坑】lstrip/rstrip 实参同样是字符集合：lstrip("```cpp\n") =
#   {'`','c','p','\n'}——围栏本身全由这些字符组成可正确剥除，但若代码恰好
#   以 c/p/反引号开头（如 "class ..." 会被剥成 "lass ..."，已实测复现）。
#   实际 checker 源码以 "#include" 开头（'#' 不在集合内）故侥幸正确；
#   rstrip("```") 同理（代码尾部几乎不会是反引号）。注释版原样保留。
# 【返回】str | None —— 纯 checker 源码；无围栏时 None（并打 error 日志）
# -----------------------------------------------------------------------------
def extract_checker_code(llm_response: str) -> str:
    checker_code = grab_cpp_code(llm_response)  # 先抓围栏（含标记）
    if checker_code is None:  # 回复里没有代码块——本次生成作废
        logger.error("Failed to extract checker code!")
        return None
    checker_code = checker_code.lstrip("```cpp\n")  # 剥头部围栏（字符集合语义，见上方坑注）
    checker_code = checker_code.lstrip("```\n")  # 兜底：若匹配到的是无标注围栏，剥裸 ``` 前缀
    checker_code = checker_code.rstrip("```")  # 剥尾部围栏
    return checker_code


# -----------------------------------------------------------------------------
# 强制终结单个子进程（无进程组语义）：先礼后兵两段式。
# 【职责】SIGTERM（terminate）→ 等 timeout 秒 → 仍未退出则 SIGKILL（kill）。
# 【使用场景】monitor_build_output 在 psutil 缺席时的兜底路径（只能杀直接
#   子进程，可能漏掉孙进程）。
# 【参数】process: Popen 对象；timeout: 优雅退出的宽限秒数
# 【返回】True=进程已退出；False=连 SIGKILL 都没收尸（僵尸/权限异常）
# -----------------------------------------------------------------------------
def force_terminate_process(process, timeout=5):
    """
    Force terminate a process with timeout.
    First tries SIGTERM, then SIGKILL if process doesn't exit.
    """
    if process.poll() is not None:  # poll() 非 None = 进程已退出，无需处理
        return True

    process.terminate()  # 发 SIGTERM，请求优雅退出
    try:
        process.wait(timeout=timeout)  # 给 timeout 秒宽限期
        return True
    except subprocess.TimeoutExpired:  # 宽限期内没退出 → 升级手段
        logger.warning(
            f"Process didn't terminate after {timeout} seconds, sending SIGKILL"
        )

    process.kill()  # 发 SIGKILL，内核级强杀
    try:
        process.wait(timeout=3)  # 再给 3 秒确认收尸
        return True
    except subprocess.TimeoutExpired:  # SIGKILL 后仍收不到——僵尸/权限问题
        logger.error("Process couldn't be killed!")
        return False


# -----------------------------------------------------------------------------
# 实时监控构建/扫描子进程的输出，超时或警告数超限即中止。
#
# 【职责】两条守护线程分别读 stdout/stderr（避免管道缓冲区写满导致子进程
#   写阻塞死锁），主循环轮询双队列统计 "warning:" 行数；命中任一闸门
#   （timeout / warning_limit）即清理并终止进程。
# 【论文语义】§3.1.4 差分验证与 §3.2 全库扫描的资源闸门——"refine 期间限
#   1 小时或 100 warnings、正式找 bug 时不限"的工程落点。实际调用方：
#   backends/csa.py:666（验证扫描，warning_limit=300 + timeout）、
#   checker_scan.py:116（全库扫描，warning_limit=-1 即不设警告闸门）。
# 【参数】process: Popen；warning_limit: 允许的最大警告数（<=0 不设限）；
#   timeout: 最长等待秒数（None 不限时）
# 【返回】(output_text, status)：status 为 "Complete"（自然跑完）或
#   "Terminated"（触闸被杀）——上游只在 "Complete" 时解析 bug 数
# -----------------------------------------------------------------------------
def monitor_build_output(process, warning_limit=100, timeout=None):
    """
    Monitor build output in real-time and stop if warning limit is exceeded.
    Improved version with proper thread and process cleanup.

    Args:
        process: subprocess.Popen object
        warning_limit: Maximum number of allowed warnings
        timeout: Maximum time to wait in seconds

    Returns:
        tuple: (output_text, process_completed)
    """
    try:
        import psutil  # 有 psutil 才能按"进程组"杀干净（连子孙进程一起收割）
    except ImportError:  # 缺依赖则降级为只杀直接子进程
        logger.warning("psutil not available, using basic process termination")
        psutil = None  # 置 None，finally 分支按有无分别走组杀/单杀

    warning_count = 0  # 已观测到的 "warning:" 行计数（闸门变量）
    output_lines = []  # 全量输出行缓存（返回值的一部分）
    process_completed = True  # 结束状态：触闸中止时置 False
    stop_monitoring = threading.Event()  # 读线程的停止信号（set() 对所有持有线程可见）

    # 嵌套读线程函数：逐行读一个字节流管道，转手投递到队列
    def read_output(stream, queue, stop_event):
        """Read output stream line by line and put in queue."""
        try:
            # 二进制管道套 UTF-8 文本包装：errors="replace" 保证源码里的
            # 非 UTF-8 字节不炸读线程（内核源码偶有非 UTF-8 注释字节）
            text_stream = io.TextIOWrapper(stream, encoding="utf-8", errors="replace")
            while not stop_event.is_set():  # 主线程发停止信号前持续读
                try:
                    # Use readline with a small timeout to allow checking stop_event
                    line = text_stream.readline()  # 阻塞读一行（EOF 返回 ""）
                    if not line:  # EOF reached
                        break  # 流关闭（子进程退出）→ 结束读循环
                    queue.put(line)  # 交给主监控线程
                except Exception:  # 管道已关/读取异常：安静退出读循环
                    break
        except Exception:  # 包装器构造失败等极端情况：吞掉，靠哨兵收尾
            pass
        finally:
            queue.put(None)  # Signal that stream has ended —— 哨兵：通知主循环本流已尽

    # Create queues for stdout and stderr
    stdout_queue = Queue()  # stdout 专用队列
    stderr_queue = Queue()  # stderr 专用队列（clang 诊断主要走 stderr，两流都要收）

    # Start threads to read stdout and stderr
    stdout_thread = threading.Thread(  # stdout 读线程
        target=read_output, args=(process.stdout, stdout_queue, stop_monitoring)
    )
    stderr_thread = threading.Thread(  # stderr 读线程
        target=read_output, args=(process.stderr, stderr_queue, stop_monitoring)
    )

    stdout_thread.daemon = True  # 守护线程：主进程退出时不被读线程拖住
    stderr_thread.daemon = True
    stdout_thread.start()
    stderr_thread.start()

    # Monitor both queues until both streams are done or limits exceeded
    start_time = time.time()  # 起跑时刻（timeout 闸门基准）
    stdout_done = stderr_done = False  # 双流结束标志（各收到哨兵 None 时置位）

    try:
        # 主监控循环：双流未完 且 进程未退出 时持续轮询
        while not (stdout_done and stderr_done) and process.poll() is None:
            # Check for timeout first
            if timeout is not None and time.time() - start_time > timeout:  # 超时闸门（None=不限时）
                logger.warning(f"Timeout of {timeout} seconds exceeded! Build stopped.")
                process_completed = False  # 标记为被中止
                break  # 跳出进 finally 清理

            # Check stdout
            if not stdout_done:  # stdout 未收尾才查（0.1s 节拍轮询，让出空档查另一流与闸门）
                try:
                    line = stdout_queue.get(timeout=0.1)  # 最多等 0.1s 的非阻塞节奏
                    if line is None:  # 哨兵：stdout 读线程收工
                        stdout_done = True
                    else:
                        output_lines.append(line)  # 归档输出行
                        if "warning:" in line.lower():  # 大小写不敏感统计 warning
                            warning_count += 1
                            if (
                                warning_count <= 10
                            ):  # Only log first 10 warnings to reduce spam
                                # 前 10 条逐条打日志（早期判断扫描质量）
                                logger.warning(
                                    f"Warning {warning_count}: {line.strip()}"
                                )
                            elif (
                                warning_count % 10 == 0
                            ):  # Log every 10th warning after that
                                # 之后每 10 条打一条进度，防日志刷屏
                                logger.warning(
                                    f"{warning_count} warnings found so far..."
                                )
                except Exception:  # 队列空（0.1s 超时）——正常节拍，继续轮询
                    pass

            # Check stderr（与 stdout 完全对称）
            if not stderr_done:
                try:
                    line = stderr_queue.get(timeout=0.1)
                    if line is None:
                        stderr_done = True
                    else:
                        output_lines.append(line)
                        if "warning:" in line.lower():
                            warning_count += 1
                            if warning_count <= 10:
                                logger.warning(
                                    f"Warning {warning_count}: {line.strip()}"
                                )
                            elif warning_count % 10 == 0:
                                logger.warning(
                                    f"{warning_count} warnings found so far..."
                                )
                except Exception:
                    pass

            # Check warning count
            if warning_limit > 0 and warning_count > warning_limit:  # 警告闸门：limit<=0（如 -1）表示不设限
                logger.error(
                    f"Warning limit of {warning_limit} exceeded! Build stopped."
                )
                process_completed = False
                break  # 触闸中止（checker_scan.py 全库扫传 -1 时永不触发此分支）

    finally:
        # Cleanup: Signal threads to stop
        stop_monitoring.set()  # 通知读线程停（阻塞在 readline 的线程靠关流解阻）

        # Terminate the process if it's still running
        if process.poll() is None:  # 进程还活着才需要杀
            logger.info("Terminating build process...")
            if psutil:  # 有 psutil：连子孙进程（编译 worker 等）整组收割
                success = force_terminate_process_group(process, psutil)
            else:  # 无 psutil：只杀直接子进程（可能漏掉孤儿孙进程）
                success = force_terminate_process(process)
            if not success:
                logger.error("Failed to properly terminate build process!")

        # Close streams to unblock threads
        try:
            if process.stdout:  # 关管道 → readline 中的读线程得到 EOF 解除阻塞
                process.stdout.close()
            if process.stderr:
                process.stderr.close()
        except Exception:  # 流已被对端关闭等：忽略
            pass

        # Wait for threads to finish with timeout
        for thread, name in [(stdout_thread, "stdout"), (stderr_thread, "stderr")]:
            if thread.is_alive():  # 最多等 3 秒让读线程自然退出
                thread.join(timeout=3)
                if thread.is_alive():  # 仍存活（极端阻塞）只能告警——daemon 兜底
                    logger.warning(f"{name} thread did not terminate cleanly")

        # Drain any remaining items from queues
        _drain_queue(stdout_queue, output_lines)  # 清空队列残留行，尽量保全完整输出
        _drain_queue(stderr_queue, output_lines)

    # Return format compatible with existing code
    if process_completed:  # 自然结束：上游据此进入 bug 数解析
        return "".join(output_lines), "Complete"
    else:  # 被闸门中止：上游跳过解析（视为本次扫描失败）
        return "".join(output_lines), "Terminated"


# -----------------------------------------------------------------------------
# 按"进程组"强制收割子进程及其全部子孙（psutil 版两段式）。
# 【职责】枚举子孙进程逐个 SIGTERM（优雅期）→ 超时则全部 SIGKILL；psutil
#   访问失败（进程消失/权限拒绝）时逐级降级，最坏退回 process.kill()。
# 【为什么必须杀组】scan-build/ninja 一类驱动进程会再 spawn 编译 worker，
#   只杀父进程会留一窝孤儿继续吃 CPU（跑的可是全内核/全 V8 编译）。
# 【参数】psutil_module 显式传入而非模块内 import——避免循环导入/缺依赖
#   时的导入问题；timeout//2：优雅期与强杀期对半分配总预算。
# 【返回】True=整组已终结；False=最终仍没杀掉
# -----------------------------------------------------------------------------
def force_terminate_process_group(process, psutil_module, timeout=10):
    """
    Force terminate a process and all its children with proper cleanup.

    Args:
        process: subprocess.Popen object
        psutil_module: psutil module (passed to avoid import issues)
        timeout: Maximum time to wait for graceful termination

    Returns:
        bool: True if process was successfully terminated
    """
    if process.poll() is not None:  # 已退出：无需动手
        return True

    try:
        # Try to get the process group and terminate all child processes
        try:
            parent = psutil_module.Process(process.pid)  # 把 PID 包装成 psutil 进程对象
            children = parent.children(recursive=True)  # 递归枚举全部子孙（编译 worker 等）

            # First, try graceful termination
            logger.info(
                f"Terminating process group (PID: {process.pid}) and {len(children)} children..."
            )

            # Send SIGTERM to all processes
            for child in children:  # 先杀子孙再杀父（防父进程死前再拉起新 worker）
                try:
                    child.terminate()  # 对每个子孙发 SIGTERM
                except (psutil_module.NoSuchProcess, psutil_module.AccessDenied):
                    pass  # 个别进程恰好已退出/无权限：跳过即可

            parent.terminate()  # 最后对父进程发 SIGTERM

            # Wait for processes to terminate gracefully
            try:
                process.wait(timeout=timeout // 2)  # 优雅期 = 总预算一半
                logger.info("Process group terminated gracefully")
                return True
            except subprocess.TimeoutExpired:  # 优雅期超时 → 升级 SIGKILL
                logger.warning("Graceful termination timed out, using SIGKILL")

        except (psutil_module.NoSuchProcess, psutil_module.AccessDenied):
            # Fallback to original method if psutil fails
            logger.warning("Could not access process group, using fallback method")  # 进程树查询失败 → 走下面的强杀路径

        # If graceful termination failed, use SIGKILL
        try:
            parent = psutil_module.Process(process.pid)  # 重新枚举（优雅期后树可能已变）
            children = parent.children(recursive=True)

            # Kill all child processes
            for child in children:  # 对全部子孙发 SIGKILL
                try:
                    child.kill()
                except (psutil_module.NoSuchProcess, psutil_module.AccessDenied):
                    pass  # 已死/无权限：跳过

            parent.kill()  # 杀父进程

        except (psutil_module.NoSuchProcess, psutil_module.AccessDenied):
            # Final fallback
            process.kill()  # 树都查不到：只杀 Popen 直接持有的进程

        # Final wait
        try:
            process.wait(timeout=timeout // 2)  # 强杀后同样等半个预算确认收尸
            logger.info("Process group killed successfully")
            return True
        except subprocess.TimeoutExpired:  # SIGKILL 后仍收不到——异常状态
            logger.error("Failed to kill process group!")
            return False

    except Exception as e:  # 最外层兜底：任何意外都不让清理路径抛出
        logger.error(f"Error terminating process group: {e}")
        # Last resort fallback
        try:
            process.kill()  # 最后手段：直接 kill + 短等待
            process.wait(timeout=3)
            return True
        except:
            return False  # 彻底失败（裸 except 属上游风格，保留）


# -----------------------------------------------------------------------------
# 排空队列残留：把主循环中止瞬间还没消费的行并入输出缓存。
# 哨兵 None 丢弃；get_nowait 抛 queue.Empty（裸 except 捕获）即队列已空、
# 结束循环。外层再包一层防御，保证清理路径绝不抛异常。
# -----------------------------------------------------------------------------
def _drain_queue(queue, output_lines):
    """Drain any remaining items from a queue into output_lines."""
    try:
        while True:  # 一直取到队列空为止
            try:
                item = queue.get_nowait()  # 非阻塞取
                if item is not None:  # None 是流结束哨兵，不进输出
                    output_lines.append(item)
            except:  # queue.Empty：队列已空 → 结束（裸 except 属上游风格）
                break
    except Exception:  # 外层防御：兜住任何意外
        pass


# -----------------------------------------------------------------------------
# 创建带"进程组"语义的受监控子进程（monitor_build_output 的标准搭档）。
# 【职责】统一注入 stdout/stderr 管道 + shell=True + 行缓冲；Unix 上用
#   os.setsid 让子进程自立新会话/新进程组——之后对组长发信号即可整组收割
#   （配合 force_terminate_process_group）。
# 【坑】preexec_fn 在多线程宿主里有 fork 安全隐患（POSIX 仅保证 fork 后
#   exec 前调用 async-signal-safe 函数）；本项目单进程串行使用无碍。
# 【参数】cmd 命令串；cwd 工作目录；**kwargs 覆盖默认 Popen 参数
# 【返回】subprocess.Popen 对象（调用方再交给 monitor_build_output 监控）
# -----------------------------------------------------------------------------
def create_monitored_process(cmd, cwd=None, **kwargs):
    """
    Create a subprocess with proper process group setup for easier cleanup.

    Args:
        cmd: Command to execute
        cwd: Working directory
        **kwargs: Additional subprocess.Popen arguments

    Returns:
        subprocess.Popen object
    """
    import os  # 局部 import（模块顶部已有 os，此处冗余但无害，上游风格保留）

    # Default arguments for better process management
    # preexec_fn=os.setsid：Unix 上让子进程建新会话/新进程组（杀组长=杀全组）；
    # Windows 无对应语义置 None。行内原英文注释保留在原位置。
    default_kwargs = {
        "stdout": subprocess.PIPE,  # 必须接管管道，否则读线程无从读起
        "stderr": subprocess.PIPE,  # 同上（clang 诊断主要走 stderr）
        "shell": True,  # 命令串含 PATH=... 前缀与 && 链，需要 shell 解释
        "bufsize": 1,  # 行缓冲，配合逐行读取
        "preexec_fn": os.setsid
        if os.name != "nt"
        else None,  # Create new process group on Unix
    }

    # Update with user-provided kwargs
    default_kwargs.update(kwargs)  # 用户参数覆盖默认值

    # Set working directory if provided
    if cwd:  # 工作目录（通常是目标仓 working_dir；commands.txt 等相对路径按它解析）
        default_kwargs["cwd"] = cwd

    return subprocess.Popen(cmd, **default_kwargs)


# -----------------------------------------------------------------------------
# 从 scan-build（LLVM/CSA）HTML 报告中蒸馏"相关源码 + 路径事件"文本。
#
# 【职责】两步走：
#   1) 从 HTML 内嵌 JS 变量 relevant_lines = {...} 解出 {file_id: {行号:…}}
#      （报告自身标注的触发路径行）；
#   2) 遍历 <table class="code"> 源码表，只保留相关行及其前 50 / 后 30 行
#      的源码行（拼成 "行号| 内容"），并保留 msgEvent/msgControl 消息行
#      （ExplodedGraph 路径上的事件/控制消息，构成 trace path）。
# 【论文语义】§3.2 Checker Refinement 的"报告蒸馏"：单条报告的 HTML 正文
#   可达数千行，直接塞给 triage agent 会淹没上下文；蒸馏后只剩 relevant
#   lines + trace path（消费链：csa.py / checker_scan.py →
#   remove_text_section → triage agent 判 FP）。
# 【参数】html_text: str —— scan-build 原始 HTML 报告
# 【返回】str —— 拼接好的多行文本（'\n'.join）
# -----------------------------------------------------------------------------
def get_source_code(html_text):
    """
    Extract the relavent source code from the html report.
    Note, this is specifically for LLVM style reports.
    """
    # --- 第 1 步：抠出 JS 变量 relevant_lines 的 JSON 字面量 ---
    # 从 "relevant_lines = " 之后截到下一个分号，中间即 {"fileid": {"行号": 1,...}, ...}
    start = html_text.find("relevant_lines = ") + len("relevant_lines = ")  # JSON 起点（find 失败时 find 返回 -1，+len 后仍指向串首附近——上游未防御，正常报告必含该变量）
    end = html_text.find(";", start)  # 该 JS 语句的结束分号
    relevant_lines = json.loads(html_text[start:end])  # 解析为 dict：{file_id: {line_no: ...}}

    soup = BeautifulSoup(html_text, "html.parser")  # 解析整页 HTML
    output = []  # 蒸馏结果行缓存
    for table in soup.find_all("table", class_="code"):  # 每张 <table class="code"> 是一个文件的带行号源码表
        file_id = table.get("data-fileid")  # 表 ↔ 文件的关联键（与 relevant_lines 的键对应）
        if not file_id or file_id not in relevant_lines:  # 无键或不在相关行清单 → 整表跳过
            continue
        relevant_line_numbers = list(relevant_lines[file_id].keys())  # 该文件的相关行号（dict 键，str 类型）
        relevant_line_numbers.sort(key=int)  # 按数值升序排（键是字符串，须按 int 排序）
        # Expand the relevant line numbers to include the lines before 50 and after 30 lines
        # 行窗口扩展：每条相关行向前 50 行、向后 30 行也纳入——给 triage agent
        # 留足上下文判断"报警是否真的对齐目标 pattern"（而非一般代码正确性）
        expanded_line_numbers = set()  # 集合去重（相邻相关行的窗口会重叠）
        for line_no in relevant_line_numbers:  # 每条相关行扩散一圈
            expanded_line_numbers.add(line_no)  # 相关行自身（字符串原样入集）
            for i in range(-50, 31):  # -50..+30（range 上界 31 不含端点）
                expanded_line_numbers.add(str(int(line_no) + i))  # 窗口行转回字符串（与 data-linenumber 属性同型可比）

        for line in table.find_all("tr"):  # 逐行遍历该表
            # Check whether it is class 'codeline' and has a 'data-linenumber' attribute
            if line.get("class") == ["codeline"]:  # 源码行（class 恰为 ["codeline"] 单元素列表）
                line_no = line.get("data-linenumber")  # 该行行号（字符串属性）
                if line_no in expanded_line_numbers:  # 只保留扩展窗口内的行
                    # Extract the content of the line while ignoring unwanted spans
                    code_td = line.find("td", class_="line")  # 源码内容单元格
                    if code_td:
                        # Remove unwanted spans (like 'macro_popup') from the line
                        for unwanted_span in code_td.find_all(
                            "span", class_="macro_popup"
                        ):  # 宏展开悬浮层是冗余 DOM
                            unwanted_span.decompose()  # Remove the unwanted span —— 从 DOM 树直接拆除
                        # Get the cleaned text and decode HTML entities
                        # get_text 拼接各文本节点（separator="" 保持行内格式，strip=False 保留缩进），
                        # unescape 还原 &lt; &amp; 等实体
                        cleaned_text = html.unescape(
                            code_td.get_text(separator="", strip=False)
                        )
                        # Add the cleaned line to the output
                        # 统一为 grep 风格："行号(左对齐 6 宽)| 源码"
                        cleaned_text = str(line_no).ljust(6) + "| " + cleaned_text
                        output.append(cleaned_text)
            elif line.find("div", class_="msg msgEvent"):  # 路径事件行（ExplodedGraph 上 checker 事件，trace path 主体）
                cleaned_text = html.unescape(line.get_text(separator="", strip=False))  # 同样还原实体
                cleaned_text = " " * 4 + cleaned_text  # 4 空格缩进，与源码行视觉区分
                output.append(cleaned_text)
            elif line.find("div", class_="msg msgControl"):  # 控制流消息行（分支/循环等路径约束信息）
                cleaned_text = html.unescape(line.get_text(separator="", strip=False))
                cleaned_text = " " * 4 + cleaned_text
                output.append(cleaned_text)
    return "\n".join(output)  # 拼成单个文本块


# -----------------------------------------------------------------------------
# 报告蒸馏总出口：把 markdown 报告里巨大的"Annotated Source Code"整节替换
# 为 get_source_code 蒸馏出的相关源码块。
#
# 【职责】scan-build 报告经 html2text 转 markdown 后正文携带整份带注源码
#   （动辄数千行）；本函数从 "### Annotated Source Code" 标题之后全部截断，
#   换成蒸馏块，并顺手把 "### Bug Summary" 改名 "### Report Summary"。
# 【论文语义】§3.2 报告蒸馏的实现——triage agent 只看 relevant lines +
#   trace path；消费方 backends/csa.py:2328 与 checker_scan.py:285。
# 【参数】text: html2text 转出的 markdown；html_text: 原始 HTML 报告
#   （蒸馏数据源——markdown 里行号信息已丢失，必须回到 HTML 取）
# 【返回】str —— 蒸馏后的 markdown（找不到标记时原样返回）
# -----------------------------------------------------------------------------
def remove_text_section(text, html_text):
    """
    Removes text between '### Annotated Source Code' and 'Show only relevant lines  Show control flow arrows'
    (including the latter line).

    Args:
        text (str): Input text to process

    Returns:
        str: Text with the specified section removed
    """
    start_marker = "### Annotated Source Code"  # 截断起点：带注源码节标题
    end_marker = "Show only relevant lines  Show control flow arrows"  # 名义终点（实际实现是"截到起点之后"，该常量未被消费，上游保留）

    # Find the start and end positions
    start_pos = text.find(start_marker)  # 定位起点；-1 表示没有该节
    if start_pos == -1:
        return text  # Start marker not found, return original text —— 没有源码节，无需蒸馏

    # Start removal after the start_marker plus newline
    removal_start = start_pos + len(start_marker) + 1  # 越过标题行（+1 吃掉行尾换行符）

    text = text[:removal_start]  # 保留标题（含），丢弃其后全部正文
    text = text.replace("### Bug Summary", "### Report Summary")  # 措辞对齐 triage 语境（判"报告"而非判"bug"）
    source_code = get_source_code(html_text)  # 从原始 HTML 蒸馏相关源码（见上）

    return text + "\n\n" + source_code  # 标题 + 蒸馏块拼成新正文


# -----------------------------------------------------------------------------
# 两路径的组件级 Jaccard 相似度：|共同组件| / |全部不同组件|。
# 【用途】object_name 在多个同名 stem.o 候选里挑与源文件路径最像的那个。
# 【示例】"drivers/net/foo.c" vs "drivers/usb/foo.c" → 交集 {drivers,foo.c}
#   为 2，并集 {drivers,net,usb,foo.c} 为 4 → 相似度 0.5
# 【注】Linux 目标早期实现；现行 targets/linux.py 与 targets/v8.py 各内嵌
#   一份同逻辑副本（本 tools 版在 src/ 内已无 import 方）。
# -----------------------------------------------------------------------------
def path_similarity(path1, path2):
    """Calculate the similarity of two paths based on their components."""
    components1 = path1.split(os.sep)  # 按平台分隔符拆路径组件
    components2 = path2.split(os.sep)

    # Count the common components
    common_components = len(set(components1) & set(components2))  # 交集组件数
    total_components = len(set(components1) | set(components2))  # 并集组件数

    # Simple ratio of common components to total unique components
    return common_components / total_components  # Jaccard 系数（0~1）


# -----------------------------------------------------------------------------
# 源文件路径 → 对应的 .o 目标文件路径（差分验证"只扫 patch 涉及对象"）。
#
# 【职责】读 CWD 下 commands.txt（目标全量编译命令库，含大量 "-o xxx/foo.o"
#   片段），按文件 stem 找出全部同名 .o 编译目标，再用 path_similarity 挑
#   路径最像的一个。
# 【论文语义】§3.1.4 Validation 的支撑：N_buggy / N_patched 都只对涉事 .o
#   重编重扫，避免全库重编的时间黑洞。
# 【注】现行 targets/linux.py（读 linux-build-commands.txt）与 targets/v8.py
#   （读 v8-build-commands.txt）各有一份改进副本，csa.py 走
#   target.get_object_name；本函数是 Linux 单目标时代版本（读 CWD 的
#   commands.txt），src/ 内已无 import 方。
# 【坑】匹配失败兜底返回"同目录 stem.o"——只在 CWD 恰为源码树根时碰巧
#   可用；下方列表推导的循环变量 match 遮蔽外层同名变量（无害但易误读）。
# -----------------------------------------------------------------------------
def object_name(file_name: str) -> str:
    file_path = Path(file_name)  # 包一层 Path 取工具方法
    stem_name = file_path.stem  # 不含扩展名的文件名（xxx.c → xxx）

    # This should be
    command_content = Path("commands.txt").read_text()  # 读编译命令库（相对 CWD！见上方坑注）

    # Pattern is like `-o XXX/stem_name.o`
    # 正则拆解：rf"-o\s+.*?/{stem_name}\.o" —— 惰性匹配任意目录下的同名目标；
    # rf 串把 stem 插值进模式（stem 含正则元字符时会被误解释，内核/Chromium
    # 文件名实践上安全）
    pattern = rf"-o\s+.*?/{stem_name}\.o"
    match = re.search(pattern, command_content)  # 先探测是否存在任一候选
    if match:
        all_matches = re.findall(pattern, command_content)  # 收集全部同名 .o 候选（不同子目录常撞名）
        all_matches = [match[3:] for match in all_matches]  # 每条剥掉 "-o "（前 3 字符）→ 剩目标路径；推导变量 match 遮蔽外层同名变量
        # Sort by edit distance to the file name
        # 注释名义写 edit distance，实现实为 path_similarity（Jaccard）：
        # 按与源文件路径的相似度降序，取最像者
        all_matches.sort(key=lambda x: path_similarity(x, file_name), reverse=True)
        return str(all_matches[0])  # 最相似的 .o 路径
    else:
        # If not found, return the default name
        return str(file_path.with_suffix(".o"))  # 兜底：同路径同 stem 换 .o 后缀


# -----------------------------------------------------------------------------
# 从扫描输出文本解析 bug 总数（": N bug(s) found" 收尾汇总行）。
# 【用途】§3.1.4 差分验证的 N_buggy / N_patched 提取（"N bugs found." 是
#   scan-build/CSA 的固定收尾行）；解析失败按 0 处理（保守：0 不会误判
#   valid，valid 判据是 N_buggy > N_patched）。
# 【注】backends/csa.py:2244 有一份同实现静态副本（本 tools 版在 src/ 内
#   已无 import 方）。
# -----------------------------------------------------------------------------
def get_num_bugs(content: str) -> int:
    try:
        # 正则拆解：r": (\d+) bug(s?) found"
        #   : (\d+)  → 冒号空格后的数字即计数（捕获组 1）
        #   bug(s?)  → 兼容单数 bug / 复数 bugs（捕获组 2 无人消费）
        #   found    → 行尾固定词
        num_bugs = int(re.search(r": (\d+) bug(s?) found", content).group(1))
    except Exception:  # 无匹配（re.search 返回 None → AttributeError）等任何异常
        print("Error: Couldn't extract number of bugs from output.")  # 直接 print（非 logger），上游风格保留
        num_bugs = 0  # 兜底 0
    return num_bugs


# -----------------------------------------------------------------------------
# 从 unified diff 文本提取每个 hunk 的起始行号（旧文件侧 = patch 前版本）。
# 【职责】匹配 "@@ -起,数 @@..." 头，取减号侧起始行号列表——供
#   get_function_codes 做"函数是否被 patch 触及"的包含判定。
# 【近似性】只取 hunk 起点、不含 hunk 覆盖范围：若 hunk 首行落在函数 A 而
#   后续改动行落在函数 B，B 会被漏判（上游取舍：hunk 通常整体在单函数内）。
# 【参数】diff: str —— 单文件的 unified diff 文本
# 【返回】list[str] —— 各 hunk 起始行号（字符串；消费方再 int()）
# -----------------------------------------------------------------------------
def get_changed_lines_in_diff(diff):
    lines = []  # 收集各 hunk 起始行号
    for line in diff.split("\n"):  # 逐行扫 diff
        if line.startswith("@@"):  # hunk 头以 @@ 开头
            # 正则拆解：@@ -(\d*),.* @@.* —— 只捕获减号侧（旧侧）起始行号；
            # 旧侧行号正是 patch 前（buggy）代码的行号坐标，与函数提取用的
            # 父版本源码同坐标系
            match = re.search(r"@@ -(\d*),.* @@.*", line)
            if match:
                lines.append(match.group(1))  # 捕获组 1 = 起始行号（str）
    return lines


# -----------------------------------------------------------------------------
# 【本模块核心】从 bug-fix commit 的 diff 出发，提取被触及函数的完整源码。
#
# 【论文语义】§3.1.1 Bug Pattern Analysis 的输入构造：LLM 只看 patch diff
#   不足以理解 bug 语境，还要给它"改动行所在的完整函数"（diff 之外的完整
#   函数上下文）；消费方 targets/factory.py:91 → 组进 pattern agent prompt。
# 【流程】
#   1) commit.diff(父提交, create_patch=True) 拿 unified diff；
#   2) 只看 .c/.h 改动文件，取其父版本（=buggy 版本）全文；
#   3) 落临时文件 __temp.c，KernelFunction.from_file 用 tree-sitter 解析出
#      该文件全部函数；
#   4) hunk 起始行（1 基）落在某函数行号区间内 → 该函数完整源码入结果集；
#   5) 兜底：一个函数都没命中（或 tree-sitter 抛异常）时，文件 ≤100KB 则
#      整文件作为一个 "WHOLE_FILE_xxx" 伪函数入集，超限则跳过。
# 【返回】set[(file_path, function_name, function_code)] —— 三元组去重集合
# 【已知坑】
#   - 行号坐标系混用：diff hunk 行号 1 基 vs tree-sitter start/end_point[0]
#     0 基（见 kfunction.py），包含判定存在系统性 ±1 行边界误差；
#   - __temp.c 写在 CWD：并发调用会互踩文件名（当前调用链为串行单文件
#     循环，暂无实际竞争；进程被强杀时可能残留临时文件）；
#   - 每个文件新建一次 KParser（重复 CDLL 加载语法库），量大时有性能损耗。
# -----------------------------------------------------------------------------
def get_function_codes(commit, include_whole_file_fallback=True, max_file_size_kb=100):
    """
    Extract function codes from commit diffs using tree-sitter.

    Args:
        commit: Git commit object
        include_whole_file_fallback: If True, include whole file content when tree-sitter fails
        max_file_size_kb: Maximum file size in KB to include as whole file (default: 100KB)

    Returns:
        Set of tuples: (file_path, function_name, function_code)
    """
    codes = set()  # (路径, 函数名, 完整源码) 三元组去重集合
    diffs = commit.diff(commit.hexsha + "^", create_patch=True)  # 与父提交（hexsha^，即修复前的 buggy 提交）做 diff，产出 unified diff 对象列表

    for diff in diffs:  # 逐个改动文件处理
        if diff.a_path.endswith(".c") or diff.a_path.endswith(".h"):  # 只关心 C 源文件/头文件（跳过文档、脚本等改动）
            # 取父提交（修复前）版本的文件全文："{commit}:{path}" 是 git show
            # 的对象寻址语法——bug pattern 要学的是"修复前怎么错"，故取旧版
            file_content_before = commit.repo.git.show(
                f"{commit.hexsha}^:{diff.a_path}"
            )
            changed_lines = get_changed_lines_in_diff(diff.diff.decode("utf-8"))  # 该文件 diff 内各 hunk 起始行号（1 基）

            # Try to extract functions using tree-sitter
            temp_file = Path("__temp.c")  # tree-sitter 按文件解析：先落临时文件（写在 CWD，见函数头坑注）
            temp_file.write_text(file_content_before)  # 写入父版本源码

            try:
                functions = KernelFunction.from_file(temp_file)  # tree-sitter 解析 → 该文件全部函数对象列表
                if temp_file.exists():  # 正常路径删临时文件（from_file 不负责清理）
                    temp_file.unlink()

                # Check if we found any functions containing changed lines
                functions_found = False  # 是否至少有一个函数被 hunk 命中
                for func in functions:  # 逐函数 × 逐 hunk 起始行做包含判定
                    for line in changed_lines:
                        start_line, end_line = func.get_line_numbers()  # 函数起止行（tree-sitter 0 基，见函数头坑注）
                        if start_line <= int(line) <= end_line:  # hunk 起始行落在函数体内 → 该函数被 patch 触及
                            codes.add((diff.a_path, func.name, func.code))  # 完整函数源码入集（§3.1.1 完整函数上下文）
                            functions_found = True

                # Fallback: if tree-sitter didn't find any relevant functions, include whole file
                if not functions_found and include_whole_file_fallback:  # 解析成功但没命中（如改动在宏/全局定义区）→ 整文件兜底
                    file_size_kb = len(file_content_before.encode("utf-8")) / 1024  # 按字节数折 KB（防多字节字符低估体积）

                    if file_size_kb <= max_file_size_kb:  # 小文件整个塞入（保护 LLM 上下文预算）
                        logger.warning(
                            f"Tree-sitter failed to find functions for {diff.a_path}, including whole file ({file_size_kb:.1f}KB)"
                        )

                        # Create a "whole file" entry
                        file_name = Path(diff.a_path).name  # 仅取文件名（不含目录）做伪函数名后缀
                        codes.add(
                            (
                                diff.a_path,  # 保留完整路径（与其他条目坐标系一致）
                                f"WHOLE_FILE_{file_name}",  # 伪函数名：下游 prompt 里可识别"这是整文件"
                                file_content_before,  # 整文件源码
                            )
                        )
                    else:  # 超大文件放弃兜底（塞进去会挤爆 prompt）
                        logger.warning(
                            f"Tree-sitter failed for {diff.a_path}, but file too large ({file_size_kb:.1f}KB > {max_file_size_kb}KB), skipping"
                        )

            except Exception as e:  # tree-sitter 解析直接失败（语法异常/编码问题等）
                logger.error(f"Tree-sitter parsing failed for {diff.a_path}: {e}")

                # Clean up temp file if it exists
                if temp_file.exists():  # 异常路径同样清理临时文件，防残留
                    temp_file.unlink()

                # Fallback: include whole file when tree-sitter completely fails
                if include_whole_file_fallback:  # 与上面同样的整文件兜底（此分支是"解析器炸了"而非"没命中"）
                    file_size_kb = len(file_content_before.encode("utf-8")) / 1024

                    if file_size_kb <= max_file_size_kb:
                        logger.warning(
                            f"Including whole file {diff.a_path} due to tree-sitter failure ({file_size_kb:.1f}KB)"
                        )
                        file_name = Path(diff.a_path).name
                        codes.add(
                            (
                                diff.a_path,
                                f"WHOLE_FILE_{file_name}",
                                file_content_before,
                            )
                        )
                    else:
                        logger.warning(
                            f"Tree-sitter failed for {diff.a_path}, but file too large ({file_size_kb:.1f}KB > {max_file_size_kb}KB), skipping"
                        )

    return codes  # 全部被触及函数（或整文件兜底）的源码集合


# -----------------------------------------------------------------------------
# get_function_codes 的 global_config 感知包装：从全局配置读兜底开关与文件
# 大小上限，配置不可用时回退默认行为。
# 【消费方】targets/factory.py:91——目标抽象层（Linux/V8）统一从这里取
# "patch 涉及函数源码"，使 §3.1.1 的函数上下文构造对所有 target 复用。
# 【设计点】函数内延迟 import global_config：避免模块加载期的循环依赖/
# 配置未就绪问题（global_config 是运行期单例）。
# 【配置键】tree_sitter_fallback_enabled（默认 True）、
#   tree_sitter_fallback_max_size_kb（默认 100）
# -----------------------------------------------------------------------------
def get_function_codes_with_config(commit):
    """
    Wrapper function that uses global config for fallback behavior.
    """
    try:
        from global_config import global_config  # 延迟导入（见上方设计点）

        # Check if whole file fallback is enabled in config
        fallback_enabled = global_config.get("tree_sitter_fallback_enabled", True)  # 整文件兜底开关
        max_file_size = global_config.get("tree_sitter_fallback_max_size_kb", 100)  # 兜底文件大小上限

        return get_function_codes(commit, fallback_enabled, max_file_size)  # 显式透传两参数
    except ImportError:  # global_config 模块缺席（独立工具化场景）
        # Fallback to default behavior if global_config is not available
        return get_function_codes(commit)  # 用函数默认参（True / 100KB）


# -----------------------------------------------------------------------------
# 超长文件/函数源码的"掐头留尾"截断（LLM 上下文预算控制）。
# 【职责】超过 max_lines 行时保留前一半 + 后一半，中段插入
#   "// ... [TRUNCATED: N lines omitted] ..." 标记行，让模型知道被截断。
# 【论文语义】§3.1.1 输入构造的护栏：WHOLE_FILE 兜底或巨型函数（内核函数
#   动辄数百行）塞进 pattern agent prompt 前先截断；消费方
#   targets/factory.py:110（max_lines=500）。
# 【注意】截断标记用 // 注释风格——目标语言是 C/C++，对 LLM 而言无语法
#   歧义（该文本只进 prompt，不参与编译）。
# 【参数】content: 文本；max_lines: 保留行数上限（头尾各半）
# 【返回】≤max_lines 行的文本；未超限时原样返回（零成本路径）
# -----------------------------------------------------------------------------
def truncate_large_file(content: str, max_lines: int = 500) -> str:
    """
    Truncate file content if it's too large, keeping the beginning and end.

    Args:
        content: File content to potentially truncate
        max_lines: Maximum number of lines to keep

    Returns:
        Truncated content with indication if truncation occurred
    """
    lines = content.split("\n")  # 拆行
    if len(lines) <= max_lines:  # 未超限——原样返回
        return content

    # Keep first and last portions
    keep_each = max_lines // 2  # 头尾各保留一半预算
    first_part = lines[:keep_each]  # 头部切片（函数签名、局部变量声明等关键语境）
    last_part = lines[-keep_each:]  # 尾部切片（返回、资源清理路径常在尾部）

    truncated_content = "\n".join(first_part)  # 拼头部
    truncated_content += (
        f"\n\n// ... [TRUNCATED: {len(lines) - max_lines} lines omitted] ...\n\n"
    )  # 中段省略标记：被省略行数 = 总行数 - max_lines（前后各留一空行缓冲）
    truncated_content += "\n".join(last_part)  # 接尾部

    return truncated_content
