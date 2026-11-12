# =============================================================================
# 【模块定位】KNighter 全流程 CLI 入口（调度层）：把命令行模式分派给 checker
#              生成 / 精化 / 扫描 / 分诊 / 标注各功能模块。
# 【论文映射】论文两阶段管线的编排入口（对应 §3.1 + §3.2 的调度层）：
#   - gen     → 阶段一 Checker Synthesis（§3.1 Algorithm 1）：patch2pattern
#               （Bug Pattern Analysis）→ pattern2plan（Plan Synthesis）→
#               plan2checker（Implementation + Syntax Repair，编译失败由
#               repair agent 最多 maxAttempts=5 次修复）→ Validation
#               buggy/patched 差分验证，整循环失败重试至 maxIterations 轮；
#   - refine  → 阶段二 Checker Refinement（§3.2）：全库扫描（限 1 小时或
#               100 warnings）→ 报告蒸馏 → triage agent 判 FP → refinement
#               agent 改 checker → 双准则接受（原 FP 不再报警 + 差分验证仍
#               通过），默认最多 3 轮 refine；
#   - scan    → 用 valid checker 扫内核全库（正式找 bug 阶段不限时/不限条数）；
#   - triage  → §3.2 triage agent：逐报告判定是否 FP（对齐目标 pattern 而
#               非一般代码正确性；论文实测 79 报告 7TP/22FP/50TN/0FN）；
#   - label   → 论文 §4.1 数据收集：给 commit 打 10 类 bug 标签。
#   其余 refine_status / refine_unrefined / list_changed / scan_single 为
#   fork 增量的工程辅助模式（状态查询 / 断点续跑 / 单 checker 调试）。
# 【管线角色】最上游：用户命令行（fire）→ main() → init_config + init_llm
#   → 按 mode 分派 checker_gen / checker_refine / checker_scan /
#   commit_label；所有产物写入 config 中 result_dir 指定的目录树。
# 【依赖与坑】①fire 把 main() 包装成 Google 风格 CLI
#   （python3 main.py <mode> --key=value）；②config_file 从 kwargs 取出后
#   必须 del 再透传，否则多余关键字参数会让下游函数 TypeError；③main()
#   docstring 提到的 'evolve' 模式实际不存在（文档漂移，合法模式以 modes
#   字典键为准）；④init_config 里 agent.result_dir 赋值是遗留接口，
#   agent.py 内部实际只读 global_config.result_dir（等效死代码）。
# =============================================================================
from pathlib import Path  # 仅用于把 result_dir 字符串规整成 Path 注入 agent 模块

import fire  # Python CLI 框架：把 main() 的形参反射成命令行选项（见文件尾）

import agent  # LLM agent 函数库（patch2pattern/pattern2plan/plan2checker/
# check_report/repair_FP/repair_syntax 等）；此处 import 主要为向该模块命名
# 空间注入 result_dir（遗留兼容，见 init_config）

from checker_gen import gen_checker  # 阶段一 Checker Synthesis 主入口（gen 模式）
from checker_refine import (
    check_refinement_status,  # 只读查询某 checker 目录的 refinement 进度/状态
    list_successfully_changed_checkers,  # 列出 refine 中源码被成功修改的 checker
    refine_checker,  # 阶段二 Refinement 主入口（refine 模式，默认 max_tries=3）
    refine_unrefined_checkers,  # 断点续跑：只补跑尚未成功 refine 的 checker
)
# 三个扫描入口：scan=全库扫描 / scan_single=单 checker 扫描调试 /
# triage_report=FP 分诊（triage 模式）
from checker_scan import scan, scan_single_checker, triage_report
from commit_label import label_commits  # label 模式：commit 数据集打 bug 类型标签
from global_config import global_config, logger  # 全局配置单例 + loguru 日志器
from model import init_llm  # LLM 客户端池初始化（论文默认模型 o3-mini，见 model.py）


def init_config(config_file: str):
    """Initialize the configuration file."""
    # 【职责】所有模式的公共前置步骤：加载 YAML 配置并完成全局环境初始化
    #   （GlobalConfig 单例 setup：LLM 密钥、loguru 文件日志、target 对象、
    #   ClangBackend 分析后端）。
    # 【参数】config_file：YAML 配置文件路径（示例见 config-example.yaml：
    #   result_dir / LLVM_dir / linux_dir / key_file / model 等）。
    # 【论文语义】载入论文实验设置：目标代码库（Linux 内核，fork 增量
    #   V8/Chromium → src/targets/）、分析后端（CSA → src/backends/csa.py）、
    #   LLM 型号（论文默认 o3-mini）等。
    global_config.setup(config_file)

    # result_dir：本轮运行所有产物（checker 元数据/prompt 历史/编译日志/
    # 扫描报告）的根目录
    result_dir = global_config.get("result_dir")
    # 遗留兼容：把 result_dir 注入 agent 模块命名空间；agent.py 内部实际
    # 统一通过 global_config.result_dir 取值，此赋值目前等效死代码
    agent.result_dir = Path(result_dir)

    # 调试日志：确认配置文件、产物目录、分析后端（ClangBackend=CSA 引擎
    # 封装）与扫描目标（Linux/V8 target 实例）加载正确
    logger.debug("Config file: " + config_file)
    logger.debug("Result dir: " + result_dir)
    logger.debug("Analysis backend: " + str(global_config.get("backend")))
    logger.debug("Target: " + str(global_config.get("target")))


def main(mode: str, *args, **kwargs):
    """
    Main entry point for the checker generation and improvement pipeline.

    Args:
        mode (str): Operation mode - 'gen', 'evolve', or 'refine'
        *args: Variable arguments passed to the specific mode function
        **kwargs: Keyword arguments passed to the specific mode function

    Raises:
        ValueError: If an invalid mode is provided
    """
    # 【职责】模式分派器：维护"模式名 → (处理函数, 描述)"注册表，统一完成
    #   配置加载与 LLM 客户端初始化后，把 *args/**kwargs 原样透传给对应模块。
    # 【坑】上方 docstring 里写的 'evolve' 模式在下方 modes 表中并不存在
    #   （历史文档漂移），合法模式以 modes 字典的键为准。
    # 模式注册表：模式名 → (处理函数, 用途描述)
    modes = {
        # 阶段一 Checker Synthesis（§3.1 Algorithm 1）：按 commit 文件批量
        # 合成 CSA checker（含语法修复与 buggy/patched 差分验证）
        "gen": (gen_checker, "Generate new checkers"),
        # 阶段二 Checker Refinement（§3.2）：扫描 → triage 判 FP →
        # refinement agent 修改 checker → 双准则接受；max_tries 默认 3 轮
        "refine": (refine_checker, "Refine and improve checkers"),
        # 只读查询 checker 目录的 refinement 状态；包一层 lambda 是给
        # detailed 参数补默认值 False（fire 透传时可省略该关键字）
        "refine_status": (
            lambda checker_dir, detailed=False: check_refinement_status(
                checker_dir, detailed
            ),
            "Check refinement status of checkers",
        ),
        # 断点续跑：跳过已成功 refine 的 checker，只补跑未成功的
        "refine_unrefined": (
            refine_unrefined_checkers,
            "Refine only checkers that haven't been successfully refined",
        ),
        # 列出 refine 过程中源码被实际修改成功的 checker（评估代码演进）
        "list_changed": (
            list_successfully_changed_checkers,
            "List checkers with successful code changes",
        ),
        # 全库扫描：对内核（默认 drivers/ 等目录，见 global_config.
        # group_scan_targets）跑全部 valid checkers；对应 §3.2 第一步全库
        # 扫描与 §4.4 正式找 bug（此阶段不限 1 小时/100 条报警）
        "scan": (scan, "Scan the kernel with valid checkers"),
        # 从单个 checker 文件发起扫描：调试/复现单 checker 行为的辅助入口
        "scan_single": (scan_single_checker, "Scan with a single checker from file"),
        # triage 模式（§3.2 triage agent）：遍历报告 HTML 逐份判定是否 FP
        # （对齐目标 bug pattern 而非一般代码正确性；论文 0 FN 关键组件）
        "triage": (triage_report, "Triage the report"),
        # label 模式（§4.1 数据收集）：给 commits 文件逐条打 10 类 bug 标签
        # （NPD/整数溢出/越界/缓冲区溢出/内存泄漏/UAF/Double-Free/UBI/
        # 并发/误用），供 gen 模式消费
        "label": (label_commits, "Label commits"),
    }

    # 未知模式直接 ValueError（fire 会以非零退出码结束进程）
    if mode not in modes:
        raise ValueError(
            f"Invalid mode: {mode}. Valid modes are: {', '.join(modes.keys())}"
        )

    # Get configuration file
    # 从关键字参数取配置文件路径；注意默认名 "config.json" 只是字符串，
    # 实际内容是 YAML（由 global_config._load_config 用 yaml.safe_load 解析）
    config_file = kwargs.get("config_file", "config.json")
    # 加载配置并初始化 target/backend/文件日志（详见 init_config 注释）
    init_config(config_file)
    # Delete the config_file from the kwargs
    # 必须把 config_file 从 kwargs 删除后再透传：下游函数签名没有这个参数，
    # 不删会以多余关键字参数触发 TypeError
    del kwargs["config_file"]
    # 初始化 LLM 客户端池：按 llm_keys.yaml 里有哪些 key 决定可用后端，
    # 并从 config.yaml 读 model/temperature/max_tokens（论文默认 o3-mini）
    init_llm()

    # 查表取出该模式的处理函数与描述
    func, description = modes[mode]
    logger.info(f"{description}")

    try:
        # 把剩余位置参数/关键字参数原样透传给模式处理函数
        # （如 gen 的 --commit_file、refine 的 checker 目录、scan 的 arch 等）
        func(*args, **kwargs)
    except Exception as e:
        # 记录错误后 re-raise：让进程以非零退出码结束，便于脚本/CI 判定失败
        logger.error(f"Error in {mode} mode: {str(e)}")
        raise


# fire.Fire(main)：进程入口。fire 反射 main 的签名，把命令行映射为
# "python3 main.py <mode> [位置参数...] [--key=value ...]"
# （README 用法示例：python3 main.py gen --config_file config.yaml
#  --commit_file commits-selected.txt）
if __name__ == "__main__":
    fire.Fire(main)
