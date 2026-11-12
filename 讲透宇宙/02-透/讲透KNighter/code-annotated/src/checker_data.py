# =============================================================================
# [模块定位] KNighter 管线的"数据模型层"：定义 checker 生成→验证→精化全生命周期
#            流转的核心数据结构（CheckerData / CheckerStatus / RefineAttempt /
#            RefinementResult / ReportData）及其 YAML 单文件、目录树两种持久化格式。
#
# [论文映射] KNighter: Transforming Static Analysis with LLM-Synthesized Checkers
#            (arXiv:2503.09002, SOSP'25)。本模块是两阶段管线的"数据骨架"：
#   - CheckerData      §3.1 Algorithm 1（Checker Synthesis）单次 iteration（index）
#                      的全部产物：patch 输入 → pattern(§3.1.1 Bug Pattern Analysis)
#                      → plan(§3.1.2 Plan Synthesis) → checker 源码+语法修复(§3.1.3
#                      Implementation + Syntax Repair) → TP/TN 差分验证分数(§3.1.4
#                      Validation)，并延展到 §3.2 Refinement 的 final_checker_code。
#   - CheckerStatus    §3.1.4 判定术语的状态机：INIT / NON_COMPILABLE / INVALID /
#                      VALID（注意 §3.2 的 plausible 状态不在此处，由
#                      RefinementResult 的报告统计决定）。
#   - RefineAttempt    §3.2 对单条 FP 报告的一次 refinement 尝试档案：三级代码快照
#                      initial → syntax_correct → semantic_correct 恰好对应
#                      "refinement agent 改写 → 语法修复 → 双准则接受验证"流水；
#                      killed_objects 即准则 1（原 FP 不再报警）的证据。
#   - RefinementResult §3.2 一轮 refine 的汇总（num_TP/num_FP/num_reports），是
#                      plausible 判定（总报告 < T_plausible=20 或采样 5 条 FP≤1）
#                      的直接数据源。
#   - ReportData       §3.2 报告蒸馏后的单条报告单元（只留 relevant lines + trace
#                      path 的 report_content）+ triage agent 判定结果。
#
# [管线角色] 上游写入方：src/checker_gen.py（生成循环构造/填充/落盘 CheckerData）、
#            src/checker_refine.py（构造并驱动 RefineAttempt/RefinementResult/
#            ReportData）、src/backends/csa.py + src/checker_scan.py（产出原始报告）；
#            下游消费：results/ 目录树与 checker-*.yaml 落盘（供人审与跨阶段恢复）。
#
# [依赖与坑] 1) pydantic BaseModel 用于 RefineAttempt/RefinementResult/ReportData；
#            CheckerData 是普通类（含 Path 与动态属性），序列化靠手写 to_dict+yaml。
#            2) RefineResult / RepairResult 是遗留占位类：全仓无消费者，真实路径
#            分别是 pydantic 版 RefinementResult 与 checker_repair.repair_checker
#            的 (correct, repaired_code) 元组返回。
#            3) load_intermediate_files / load_final_checker_code 引用的
#            self.intermediate_dir / self.checker_file_path 全仓从未赋值——
#            一旦调用即 AttributeError（当前也无调用方，属未完成代码）。
#            4) load_checker_data_from_dir 的 dir_path 注解为 str 却按 Path 使用；
#            反解出的 index 是 str（构造器注解却是 int）；base_result_dir 被设为
#            checker 自身目录，load 后 output_dir 属性不再指回原目录。
# =============================================================================
import difflib  # 标准库 diff：generate_diff_patch 用 unified_diff 生成精化/修复前后对比补丁
import enum  # 标准库枚举：CheckerStatus 状态机的基类
from pathlib import Path  # 路径对象：所有落盘目录/文件的构造（注意本文件多处按 Path 接口使用 str 参数）
from typing import List, Optional, Set  # 类型注解：List 列表 / Optional 可空 / Set 集合（error_objects 去重用）

import pydantic  # 数据模型基类：RefineAttempt/RefinementResult/ReportData 继承 BaseModel 获得字段校验
import yaml  # YAML 读写：CheckerData.dump() 落盘与 load_checker_data_from_file 恢复（save_refined_code 内还有一次冗余的函数内局部导入）

# checker 唯一 ID 前缀："KN" = KNighter。完整 ID 格式为
# KN-{commit_type}-{commit_id 前 8 位}-{iteration 序号}，
# 例如 KN-Null-Pointer-Dereference-2e29b997-0（见 CheckerData.checker_id 属性）。
# 所有结果目录与落盘文件名都靠它区分于官方 CSA checker。
CHECKER_ID_PREFIX = "KN-"


# ----------------------------------------------------------------------------
# generate_diff_patch：生成两段代码字符串之间的 unified diff 补丁（纯工具函数）。
# 论文语义：§3.2 Refinement 的可追溯性产物——refine/repair 前后的代码差异以
# *.patch 形式随 RefineAttempt/RefinementResult 落盘，供人工审查 LLM 究竟改了
# 什么（支撑论文"checker 一次性生成、人可读可维护"的卖点）。
# 参数：original_code/refined_code 为新旧源码字符串；*_filename 仅作为 diff 头部
#       的文件名标注（不读盘）。返回 unified diff 字符串（无差异时为空串）。
# ----------------------------------------------------------------------------
def generate_diff_patch(
    original_code: str, refined_code: str, original_filename: str, refined_filename: str
) -> str:
    """Generate a unified diff patch between two code strings.

    Args:
        original_code: The original code as a string
        refined_code: The refined/modified code as a string
        original_filename: Name to use for the original file in the diff header
        refined_filename: Name to use for the refined file in the diff header

    Returns:
        A string containing the unified diff patch
    """
    # splitlines(keepends=True) 保留行尾换行符：unified_diff 要求逐行输入，
    # keepends 保证最后一行无换行符时也能与带换行的行正确对齐
    original_lines = original_code.splitlines(keepends=True)  # 旧版本行序列
    refined_lines = refined_code.splitlines(keepends=True)  # 新版本行序列

    diff = difflib.unified_diff(  # 生成 unified diff（--- a/xxx +++ b/xxx + @@ hunk 头）
        original_lines,  # 旧版本行序列
        refined_lines,  # 新版本行序列
        fromfile=original_filename,  # diff 头 "--- <original_filename>"
        tofile=refined_filename,  # diff 头 "+++ <refined_filename>"
        lineterm="",  # 行尾符置空：输入行已自带 keepends 的换行，避免 diff 每行再追加空行
    )

    return "".join(diff)  # unified_diff 返回行迭代器，直接拼接为完整补丁字符串


# ----------------------------------------------------------------------------
# CheckerStatus：checker 生成过程的状态机（枚举）。
# 论文映射：§3.1.4 Validation 的判定术语——
#   INIT           初始态（刚进入 Algorithm 1 的一次 iteration）
#   NON_COMPILABLE 编译不过（§3.1.3 Syntax Repair 用尽 maxAttempts=5 次仍失败）
#   INVALID        可编译但差分验证失败（buggy/patched 两版本行为不满足 valid 条件）
#   VALID          §3.1.4 的 valid：buggy 版本（patch 父提交）能报出 bug 且
#                  patched 版本不再报（N_buggy > N_patched 且 N_patched < T_valid）
# 注意：全仓 grep 显示该枚举当前无外部消费者——实际有效性判定走
# CheckerData.is_valid（TP/TN 分数），此枚举属于保留的状态机骨架。
# ----------------------------------------------------------------------------
class CheckerStatus(enum.Enum):
    """Enum representing the status of a checker generation process."""

    INIT = "init"  # 初始态：iteration 刚开始，尚无任何产物

    NON_COMPILABLE = "non_compilable"  # 语法修复失败：checker.cpp 始终编译不过
    INVALID = "invalid"  # 差分验证失败：对 buggy/patched 版本的报警行为不满足 valid 条件
    VALID = "valid"  # 差分验证通过（§3.1.4），有资格进入 §3.2 Refinement


# ----------------------------------------------------------------------------
# RefineAttempt（pydantic BaseModel）：§3.2 中"一条被 triage agent 判为 FP 的报告"
# 所触发的单次 checker 精化尝试的完整档案。
# 构造于 checker_refine._refine_false_positives（refine_id = "refine-{轮次}-{报告序号}"），
# 字段被 _attempt_report_refinement 流水逐步填充，三级代码快照对应论文三道关口：
#   initial_refine_code          → refinement agent 改写出的新 checker 源码
#                                  （extract_checker_code 从 LLM 输出中剥出）
#   syntax_correct_refine_code   → 经过 repair_checker 语法修复后编译通过
#   semantic_correct_refine_code → 通过 buggy/patched 差分复验（newTP>0 且 newTN>0，
#                                  即论文双准则接受之准则 2）
# killed_objects 记录精化后不再报警的对象文件（准则 1：原 FP 案例不再报警）。
# ----------------------------------------------------------------------------
class RefineAttempt(pydantic.BaseModel):
    refine_id: str  # 本次精化尝试 ID：refine-{attempt_id 轮次}-{idx FP 报告序号}
    report_data: "ReportData"  # 触发本次精化的那条 FP 报告（字符串前向引用：ReportData 定义在本文件后方）
    original_code: str  # 精化前的 checker 源码（所有 diff 的 baseline）
    initial_refine_code: Optional[str] = None  # LLM 初版精化代码（未经任何验证）
    syntax_correct_refine_code: Optional[str] = None  # 编译修复通过后的代码
    semantic_correct_refine_code: Optional[str] = None  # 通过差分验证被最终接受的代码
    killed_objects: List[str] = []  # 精化后"不再报警"的对象文件清单（FP 被消除的证据）
    reasoning_process: Optional[str] = None  # refinement agent 的推理过程（LLM 原始输出剥去代码块后的剩余文本）

    def dump_dir(self, output_dir: Path):
        """Dumps the RefineAttempt instance to a YAML file."""
        # （注意 docstring 与实现不符：实际落盘的是目录树——txt/cpp/patch 文件，非 YAML）
        output_dir = Path(output_dir) / "refine" / self.refine_id  # 落盘位置：<checker 输出目录>/refine/<refine_id>/
        output_dir.mkdir(parents=True, exist_ok=True)  # 递归建目录（父目录不存在也一并创建）

        self.report_data.dump(output_dir)  # 先落触发报告本体：report_content/report_triage/report_objects 三个 txt

        (output_dir / "original_code.cpp").write_text(self.original_code)  # 精化前源码快照
        if self.initial_refine_code:  # 若拿到了 LLM 初版精化代码
            (output_dir / "initial_refine_code.cpp").write_text(
                self.initial_refine_code
            )

        if self.syntax_correct_refine_code:  # 若通过了语法修复关口
            (output_dir / "syntax_correct_refine_code.cpp").write_text(
                self.syntax_correct_refine_code
            )
            diff_patch = generate_diff_patch(  # 附带 original→syntax_correct 的 unified diff 供人审
                self.original_code,
                self.syntax_correct_refine_code,
                "original_code.cpp",
                "syntax_correct_refine_code.cpp",
            )
            (output_dir / "original_to_syntax_correct.patch").write_text(diff_patch)

        if self.semantic_correct_refine_code:  # 若通过了差分验证关口（被接受的精化）
            (output_dir / "semantic_correct_refine_code.cpp").write_text(
                self.semantic_correct_refine_code
            )
            diff_patch = generate_diff_patch(  # 附带 original→semantic_correct 的 unified diff
                self.original_code,
                self.semantic_correct_refine_code,
                "original_code.cpp",
                "semantic_correct_refine_code.cpp",
            )
            (output_dir / "original_to_semantic_correct.patch").write_text(diff_patch)

        if self.killed_objects:  # 若有被"消灭"的 FP 对象，逐行落盘
            (output_dir / "killed_objects.txt").write_text(
                "\n".join(self.killed_objects)
            )

        # LLM 推理过程存档。（坑）失败路径下 reasoning_process 仍为 None 时
        # write_text(None) 会抛 TypeError，且调用方该处位于 try 块之外
        (output_dir / "reasoning_process.txt").write_text(self.reasoning_process)


# ----------------------------------------------------------------------------
# RefineResult（遗留占位类）：文件内注释自证 "Placeholder ... might be defined
# elsewhere"。全仓 grep 无实例化方——§3.2 真实的一轮精化结果走下方 pydantic 版
# RefinementResult；本类仅被 CheckerData.refinement_history 的类型注解引用
# （load_final_checker_code 会读取其实例的 refined/checker_code 字段）。
# ----------------------------------------------------------------------------
# Placeholder for refinement results, assuming it might be defined elsewhere
# or based on the structure of refine.log entries.
class RefineResult:
    """Represents the outcome of a single refinement step."""

    def __init__(
        self,
        attempt_id: int,  # 精化轮次编号
        result: str,  # 单轮判定结果字符串
        refined: bool,  # 本轮是否产出了可用的精化代码
        checker_code: Optional[str] = None,  # 精化成功时的 checker 源码
        scan_id: Optional[int] = None,  # 本轮精化前那次全库扫描的 ID
    ):
        self.attempt_id: int = attempt_id
        self.result: str = (
            result  # e.g., "Perfect", "Uncompilable", "High-TP", "Refined"
        )
        self.refined: bool = refined
        self.checker_code: Optional[
            str
        ] = checker_code  # Code after refinement if successful
        self.scan_id: Optional[
            int
        ] = scan_id  # ID of the scan performed before this refinement

    def __str__(self) -> str:  # 日志/打印友好表示：Attempt <轮次>: Result=<结果>, Refined=<是否精化>
        return (
            f"Attempt {self.attempt_id}: Result={self.result}, Refined={self.refined}"
        )


# ----------------------------------------------------------------------------
# RepairResult（遗留类）：单次"语法修复"尝试的结果记录。全仓无消费者——真实语法
# 修复走 src/checker_repair.py 的 repair_checker（返回 (correct, repaired_code)
# 元组而非此对象）。对应论文 §3.1.3 的 repair agent：checker.cpp 编译失败时依
# 编译错误修复，最多 maxAttempts=5 次；CheckerData.syntax_repair_log 的类型
# 注解引用了本类但从未真正填充。
# ----------------------------------------------------------------------------
class RepairResult:
    """Represents the result of a syntax repair attempt."""

    def __init__(
        self,
        attempt_id: int,  # 修复尝试序号（1..maxAttempts）
        original_code,  # 待修复的 checker 源码（无类型注解，实际为 str）
        repaired_code: str,  # 修复后的 checker 源码
        error_message: Optional[str] = None,  # 编译错误信息；None 视为编译通过（成功）
    ):
        self.attempt_id: int = attempt_id
        self.original_code: str = original_code  # 待修复源码原样保存（供 diff/审计）
        self.repaired_code: str = repaired_code  # 修复后源码
        self.error_message: Optional[str] = error_message  # 编译错误信息（None=成功）

    def __str__(self) -> str:
        # FIXME: This should be more informative
        # 以"无编译错误信息"作为本次修复成功的判据
        return f"Repair Attempt {self.attempt_id}: Success={self.error_message is None}"


# ----------------------------------------------------------------------------
# CheckerData：KNighter 数据模型的中枢——记录"一次 checker 生成（+可选精化）尝试"
# 的全部输入、中间产物与验证分数。对应论文 §3.1 Algorithm 1 的一次 iteration
# （构造参数 index 即循环变量 i，同一 commit 最多循环 maxIterations 次）。
# 字段与论文阶段一一对应：patch 输入 → pattern(§3.1.1) → plan/refined_plan(§3.1.2)
# → initial_checker_code(§3.1.3) → syntax_repair_log/repaired_checker_code(§3.1.3
# Syntax Repair) → tp_score/tn_score(§3.1.4 差分验证) → refinement_history/
# final_checker_code(§3.2 Refinement)。
# 生命周期：src/checker_gen.py 构造并填充（阶段一），src/checker_refine.py 续写
# （阶段二），dump()/dump_dir() 双格式落盘，三个 load_* 方法支持从盘上恢复。
# ----------------------------------------------------------------------------
class CheckerData:
    """
    Represents the data and state associated with a single attempt
    to generate and potentially refine a checker.
    Corresponds roughly to one iteration in the generation loop (index `i`).
    """

    def __init__(
        self,
        commit_id: str,  # 输入 bug-fix patch 的 commit 哈希
        commit_type: str,  # bug 类别标签（10 类之一，多词类型用连字符拼接，如 Null-Pointer-Dereference）
        base_result_dir: Path,  # 结果根目录：output_dir = base_result_dir / checker_id
        index: int,  # Algorithm 1 本次 iteration 的序号 i（同一 commit 的第几次尝试）
        patch: Optional[str] = None,  # patch diff 文本（可选：也可事后经 load_* 从盘上恢复）
    ):
        self._status: CheckerStatus = CheckerStatus.INIT  # 状态机初始态（见 CheckerStatus 注释：当前无外部消费者）
        # Basic attributes
        self.commit_id: str = commit_id
        self.commit_type: str = commit_type
        self.index: int = index

        self._base_result_dir: Path = base_result_dir  # 结果根目录（下划线=私有，可经 update_base_result_dir 迁移）

        self.patch: Optional[str] = patch
        # Data generated during the initial generation phase (checker_gen.py)
        # §3.1.1 产物：LLM 从 patch 提炼的 targeted bug pattern（刻意收窄范围）
        self.pattern: Optional[str] = None
        # §3.1.2 产物：高层实现计划（用哪些 CSA 回调、维护什么状态）
        self.plan: Optional[str] = None
        self.refined_plan: Optional[str] = None  # Note: often same as plan in snippets
        self.initial_checker_code: Optional[str] = None  # Code before repair/refinement

        # Syntax Repair
        # §3.1.3 Syntax Repair 各次修复尝试的日志（类型为遗留 RepairResult，实际从未填充）
        self.syntax_repair_log: List[RepairResult] = []  # List of repair attempts
        self.repaired_checker_code: Optional[
            str
        ] = None  # Code after repairChecker step

        # Evaluation results
        # §3.1.4 Validation 差分验证分数（backends/csa.py validate_checker 返回）：
        # TP = patch 涉及对象 checkout 到 buggy 版本（patch 父提交）扫描时报出 bug 的
        #      对象数（>0 = checker 能在旧代码上抓到被修复的 bug）；
        # TN = checkout 到 patched 版本后正确不报警（或按"报警数比 buggy 版少且 <5"
        #      的启发式折算）的对象数；编译/运行出错返回 (-1,-1)/(-2,-2) 哨兵。
        # 默认 -10 = "尚未评估"，与任何真实评估结果（含负分哨兵）区分开。
        self.tp_score: int = -10  # True Positives, default from checker_gen.py
        self.tn_score: int = -10  # True Negatives, default from checker_gen.py

        # Data from the refinement phase (checker_refine.py)
        # §3.2 各轮精化记录（类型为遗留 RefineResult，实际精化走 RefinementResult）
        self.refinement_history: List[RefineResult] = []
        # §3.2 结束后的最终 checker 源码（精化链的末端快照）
        self.final_checker_code: Optional[str] = None

    def update_base_result_dir(self, base_result_dir: Path):
        """Updates the base result directory."""
        # 迁移结果根目录（checker_refine.py 在阶段二换目录续写时调用，随后 dump_dir 到新位置）
        self._base_result_dir = base_result_dir

    def load_intermediate_files(self):
        """Loads data from intermediate files created during generation."""
        # （坑）self.intermediate_dir 在本类及全仓从未赋值——调用本方法必抛
        # AttributeError，属未完成代码（无调用方）；文件名与 checker_gen.py 落盘的
        # generation/checker_XX/01_pattern.txt 等编号前缀也不一致
        if self.intermediate_dir.exists():
            # 中间产物文件名 → CheckerData 属性名的映射表
            files_to_load = {
                "pattern.txt": "pattern",  # §3.1.1 pattern
                "plan.txt": "plan",  # §3.1.2 plan
                "refined_plan.txt": "refined_plan",  # 精化后 plan
                "checker-0.txt": "initial_checker_code",  # Assuming checker-0 is the first generated code
                # Repair log/result might need specific parsing if stored
            }
            for filename, attr_name in files_to_load.items():  # 逐文件尝试恢复
                file_path = self.intermediate_dir / filename
                if file_path.exists():  # 存在才读（部分产物可能尚未生成）
                    try:
                        setattr(self, attr_name, file_path.read_text())  # 动态设属性
                    except Exception as e:  # 单文件读失败不中断整体恢复
                        print(f"Warning: Could not read {file_path}: {e}")

    def load_final_checker_code(self):
        """Loads the final checker code if the file exists."""
        # （坑）self.checker_file_path 同样全仓从未赋值——首个分支调用即
        # AttributeError；下方三个 elif 是"最终代码"的回退链
        if self.checker_file_path.exists():
            try:
                self.final_checker_code = self.checker_file_path.read_text()  # 首选：独立的最终代码文件
            except Exception as e:
                print(
                    f"Warning: Could not read final checker {self.checker_file_path}: {e}"
                )
        # If final code isn't saved separately, it might be the last refined code
        # 回退 1：最后一轮精化成功 → 用其产出的代码
        elif self.refinement_history and self.refinement_history[-1].refined:
            self.final_checker_code = self.refinement_history[-1].checker_code
        # Or the repaired code if no refinement happened
        # 回退 2：只做过语法修复 → 用修复后代码
        elif self.repaired_checker_code:
            self.final_checker_code = self.repaired_checker_code
        # Or the initial code if no repair/refinement
        # 回退 3：未修复未精化 → 用 LLM 初版代码
        elif self.initial_checker_code:
            self.final_checker_code = self.initial_checker_code

    @property
    def is_valid(self) -> bool:
        """Checks if the checker data is valid based on TP and TN scores."""
        # FIXME: This should consider the number of total reports
        # 论文 §3.1.4 的 valid 判定的代码化：buggy 版本能报（TP>0）且 patched 版本
        # 不报（TN>0）→ 差分验证通过。-10（未评估）与 -1/-2（出错哨兵）都天然不满足。
        return self.tp_score > 0 and self.tn_score > 0

    def to_dict(self) -> dict:
        """Converts the CheckerData instance to a JSON-serializable dictionary."""
        # 手写序列化（CheckerData 非 BaseModel）：逐字段挑拣，含 Path→str 转换；
        # syntax_repair_log/refinement_history/final_checker_code 被刻意排除
        # （遗留对象无 to_dict，最终代码另由 dump_dir 的 checker-final.cpp 承载）
        return {
            "commit_id": self.commit_id,
            "commit_type": self.commit_type,
            "index": self.index,
            # Convert Path objects to strings
            "_base_result_dir": str(self._base_result_dir),  # Path 对象不能直接进 YAML/JSON
            "patch": self.patch,
            "pattern": self.pattern,  # §3.1.1 产物
            "plan": self.plan,  # §3.1.2 产物
            "refined_plan": self.refined_plan,
            "initial_checker_code": self.initial_checker_code,  # §3.1.3 初版代码
            # Convert list of custom objects by calling their to_dict method
            # "syntax_repair_log": [log.to_dict() for log in self.syntax_repair_log],
            "repaired_checker_code": self.repaired_checker_code,  # §3.1.3 修复后代码
            "tp_score": self.tp_score,  # §3.1.4 差分验证 TP
            "tn_score": self.tn_score,  # §3.1.4 差分验证 TN
            # Convert list of custom objects
            # "refinement_history": [hist.to_dict() for hist in self.refinement_history],
            # "final_checker_code": self.final_checker_code,
        }

    @property
    def checker_id(self) -> str:
        """Generates a unique ID for the checker based on commit ID and index."""
        # commit 哈希截断长度：短于 8 位则全取（防越界），正常 git 哈希取前 8 位
        shortened_commit_id_length = min(len(self.commit_id), 8)
        # {commit_type}-{commit_id[:shortened_commit_id_length]}-{index}
        # 拼接为 KN-{类型}-{短哈希}-{序号}，如 KN-Null-Pointer-Dereference-2e29b997-0
        return (
            CHECKER_ID_PREFIX  # 固定前缀 "KN-"
            + self.commit_type  # bug 类别（可含连字符的多词类型）
            + "-"
            + self.commit_id[:shortened_commit_id_length]  # commit 短哈希
            + "-"
            + str(self.index)  # iteration 序号（同一 commit 的多次尝试靠它区分）
        )

    @property
    def output_dir(self) -> str:
        """Generates the output directory path for the checker."""
        # 每个 checker 一个独立结果目录：<结果根>/<checker_id>/
        return str(self._base_result_dir / self.checker_id)

    def dump(self):
        """Dumps the CheckerData instance to a file."""
        # 持久化格式一：YAML 单文件（<结果根>/checker-<checker_id>.yaml），
        # 内容为 to_dict() 挑拣的字段；default_flow_style=False 用块风格便于人读
        yaml.dump(
            self.to_dict(),
            (self._base_result_dir / f"checker-{self.checker_id}.yaml").open("w"),
            default_flow_style=False,
        )

    def dump_dir(self):
        """Dumps the CheckerData instance to a directory."""
        # 持久化格式二：目录树（<结果根>/<checker_id>/ 下一组固定名字的文件），
        # checker_gen.py/checker_refine.py 实际采用这一格式落盘
        output_dir = Path(self.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)  # 递归建 checker 专属目录

        # None 值统一回退为空串写入（or "" 的作用），保证文件总是存在
        (output_dir / "patch.txt").write_text(self.patch or "")  # 输入 patch diff
        (output_dir / "pattern.txt").write_text(self.pattern or "")  # §3.1.1 pattern
        (output_dir / "plan.txt").write_text(self.plan or "")  # §3.1.2 plan
        (output_dir / "refined_plan.txt").write_text(self.refined_plan or "")  # 精化后 plan
        (output_dir / "checker-initial.cpp").write_text(self.initial_checker_code or "")  # LLM 初版代码
        (output_dir / "checker-repaired.cpp").write_text(
            self.repaired_checker_code or ""
        )  # 语法修复后代码
        (output_dir / "checker-final.cpp").write_text(self.final_checker_code or "")  # 最终代码
        (output_dir / "score.txt").write_text(
            f"TP: {self.tp_score}\nTN: {self.tn_score}"
        )  # 差分验证分数（load_checker_data_from_dir 会回读此文件）

    @staticmethod
    def load_checker_data_from_file(file_path: str) -> "CheckerData":
        """Loads CheckerData from a YAML file."""
        # 恢复入口一：读 dump() 产出的 YAML 单文件（当前仓内无自动调用方，
        # 属手工恢复/离线分析入口）
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)  # safe_load 防任意对象反序列化

        # 先用 YAML 中的必备四字段重建实例（其余字段默认值）
        checker_data = CheckerData(
            commit_id=data["commit_id"],
            commit_type=data["commit_type"],
            base_result_dir=Path(data["_base_result_dir"]),  # str → Path 还原
            index=data["index"],
        )

        # Load other attributes
        # 可选字段逐个回填（get 缺省 None）；分数缺省 -10（"未评估"哨兵）
        checker_data.patch = data.get("patch")
        checker_data.pattern = data.get("pattern")
        checker_data.plan = data.get("plan")
        checker_data.refined_plan = data.get("refined_plan")
        checker_data.initial_checker_code = data.get("initial_checker_code")
        checker_data.repaired_checker_code = data.get("repaired_checker_code")
        checker_data.tp_score = data.get("tp_score", -10)
        checker_data.tn_score = data.get("tn_score", -10)
        return checker_data

    @staticmethod
    def load_checker_data_from_dir(dir_path: str) -> "CheckerData":
        """Loads CheckerData from a directory."""
        # 恢复入口二：从 dump_dir() 的目录树重建（靠目录名反解 checker_id 三段）
        # First check whether the dir_path is with the PREFIX
        # （坑）参数注解是 str，下面却直接用 Path 接口（.name / / 运算符）——
        # 实际必须传 Path 对象，传 str 会在 dir_path.name 处抛 AttributeError
        if not dir_path.name.startswith(CHECKER_ID_PREFIX):
            raise ValueError(
                f"Directory {dir_path} does not start with {CHECKER_ID_PREFIX}"
            )

        # For instance, KN-Null-Pointer-Dereference-2e29b997-0
        # 按 "-" 切分目录名：["KN", "Null", "Pointer", "Dereference", "2e29b997", "0"]
        # 从尾部定位三要素，避开 commit_type 自身含连字符的歧义
        splits = dir_path.name.split("-")
        commit_id = splits[-2]  # 倒数第二段 = commit 短哈希（只有 8 位，非完整哈希）
        commit_type = "-".join(splits[1:-2])  # 中段全部拼回 = bug 类别（如 Null-Pointer-Dereference）
        index = splits[-1]  # 末段 = iteration 序号（注意：str 类型，构造器注解却是 int）

        print(commit_id, commit_type, index)  # 调试遗留：反解结果直接打印

        # （坑）base_result_dir 传的是 checker 目录自身——重建后 output_dir 属性
        # = <checker 目录>/<checker_id>，不再指回原目录
        checker_data = CheckerData(
            commit_id=commit_id,
            commit_type=commit_type,
            base_result_dir=dir_path,
            index=index,
        )

        # Load the files
        # 逐个回读 dump_dir 落盘的产物文件（此处无 or "" 兜底：文件缺失会直接抛异常）
        checker_data.patch = (dir_path / "patch.txt").read_text()
        checker_data.pattern = (dir_path / "pattern.txt").read_text()
        checker_data.plan = (dir_path / "plan.txt").read_text()
        checker_data.refined_plan = (dir_path / "refined_plan.txt").read_text()
        checker_data.initial_checker_code = (
            dir_path / "checker-initial.cpp"
        ).read_text()
        checker_data.repaired_checker_code = (
            dir_path / "checker-repaired.cpp"
        ).read_text()

        # 差分验证分数：score.txt 两行 "TP: x" / "TN: y"，按 ":" 切开取尾部转 int
        score_file = dir_path / "score.txt"
        if score_file.exists():
            score_content = score_file.read_text().splitlines()  # 拆成 [ "TP: x", "TN: y" ]
            print(score_content)  # 调试遗留
            checker_data.tp_score = int(score_content[0].split(":")[-1].strip())  # 第 1 行 → TP
            checker_data.tn_score = int(score_content[1].split(":")[-1].strip())  # 第 2 行 → TN

        return checker_data


# ----------------------------------------------------------------------------
# RefinementResult（pydantic BaseModel）：§3.2 Refinement 一轮（论文最多 3 轮）的
# 汇总结果。由 checker_refine.py 构造：全库扫描 → 报告蒸馏 → triage agent 逐条
# 判定 → 统计 num_TP/num_FP；num_reports/num_TP/num_FP 正是 plausible 判定
# （总报告 < T_plausible=20 或采样 5 条报告中 FP≤1）的数据来源。
# error_objects 收集 FP 报告涉及的对象文件，精化后复扫（_scan_remaining_objects）
# 从中剔除已不再报警者——剩余即"仍未消除的 FP 对象"。
# ----------------------------------------------------------------------------
class RefinementResult(pydantic.BaseModel):
    refined: bool  # 本轮是否产出了被接受的精化代码
    checker_code: str  # 本轮结束时的 checker 源码（精化成功=新代码，否则=原代码）
    result: str  # 单轮判定标签（如 Refined / Perfect 等）
    num_TP: int  # triage 判为真阳性的报告数
    num_FP: int  # triage 判为 NotABug（FP）的报告数
    num_reports: int  # 本轮全库扫描的总报告数（plausible 判定的阈值比较对象）
    attempt_id: int  # 精化轮次编号
    refine_attempt_list: List[RefineAttempt] = []  # 本轮逐条 FP 的精化尝试档案（§3.2 refinement agent 执行单元）
    error_objects: Set[str] = set()  # FP 报告涉及的对象文件集合（去重；随精化复扫逐步收缩）
    original_checker_code: Optional[str] = None  # Store the code before this refinement

    def __str__(self):
        # 精确率 = TP / (TP+FP)，分母加 1e-5 防零除；输出"结果,精确率,总报告数,轮次"
        # 的逗号分隔日志行（refine 流程的状态行）
        tp_rate = self.num_TP / (self.num_TP + self.num_FP + 0.00001)
        return f"{self.result},{tp_rate:.2f},{self.num_reports},{self.attempt_id}"

    def save_refined_code(self, output_dir: Path, checker_id: str) -> None:
        """Save the successfully refined checker code to files."""
        output_dir = Path(output_dir)  # 容错转换：允许传 str
        refinement_dir = output_dir / "refinements"  # 所有精化产物统一收在 refinements/ 子目录
        refinement_dir.mkdir(parents=True, exist_ok=True)  # 递归建目录

        # Save the refined code if this attempt was successful
        if self.refined and self.checker_code:  # 仅当本轮精化被接受才落"正式"产物
            # 按轮次命名的精化代码存档
            refined_file = refinement_dir / f"refined_attempt_{self.attempt_id}.cpp"
            refined_file.write_text(self.checker_code)

            # Also save as the latest successful refinement
            # 固定名"最新成功精化"副本：下游免枚举直接取最新版
            latest_file = refinement_dir / "latest_refined.cpp"
            latest_file.write_text(self.checker_code)

            # Save metadata about this refinement
            # 元数据：轮次/标签/报告统计/精确率/尝试次数（精确率分母为 0 时记 0）
            metadata = {
                "attempt_id": self.attempt_id,
                "result": self.result,
                "refined": self.refined,
                "num_reports": self.num_reports,
                "num_TP": self.num_TP,
                "num_FP": self.num_FP,
                "precision": self.num_TP / (self.num_TP + self.num_FP)
                if (self.num_TP + self.num_FP) > 0
                else 0,
                "refinement_attempts": len(self.refine_attempt_list),
            }
            metadata_file = (
                refinement_dir / f"refined_attempt_{self.attempt_id}_metadata.yaml"
            )
            import yaml  # 函数内局部导入（模块顶部已 import 过，冗余但无害）

            metadata_file.write_text(yaml.dump(metadata, default_flow_style=False))

        # Always save the current state (even if not refined)
        # 无论成功与否都落一份本轮快照，保证失败轮次也可追溯
        attempt_file = refinement_dir / f"attempt_{self.attempt_id}.cpp"
        attempt_file.write_text(self.checker_code)

        # Save original code for comparison (if available)
        if self.original_checker_code:  # 精化前代码可用则生成对比 diff
            # Generate and save diff between original and refined code
            diff_patch = generate_diff_patch(
                self.original_checker_code,
                self.checker_code,
                f"attempt_{self.attempt_id}_original.cpp",
                f"attempt_{self.attempt_id}.cpp",
            )
            diff_file = refinement_dir / f"attempt_{self.attempt_id}_diff.patch"
            diff_file.write_text(diff_patch)


# ----------------------------------------------------------------------------
# ReportData（pydantic BaseModel）：§3.2 报告处理链的最小单元。全库扫描产出原始
# CSA 报告 → 报告蒸馏（只保留 relevant lines + trace path）得到 report_content →
# triage agent（check_report）判定写入 report_triage（含 "NotABug" 即判 FP）→
# backend.get_objects_from_report 提取涉及对象写入 report_objects。
# 既是 RefineAttempt 的触发载荷，也由 RefineAttempt.dump_dir 逐报告落盘归档。
# ----------------------------------------------------------------------------
class ReportData(pydantic.BaseModel):
    report_id: str  # 报告唯一 ID（扫描侧生成；group 扫描覆盖路径下形如 group_report_{i}）
    report_content: str  # 蒸馏后的报告正文（relevant lines + trace path）
    report_triage: str  # triage agent 的判定文本；含 "NotABug" 子串 = FP（触发 refinement）
    report_objects: List[str]  # 报告涉及的对象文件清单（.o 目标名，供对象级差分复扫）

    def dump(self, output_dir):
        # 每条报告一个子目录：<父目录>/<report_id>/ 下三个 txt
        report_output_dir = Path(output_dir) / self.report_id
        report_output_dir.mkdir(parents=True, exist_ok=True)

        (report_output_dir / "report_content.txt").write_text(self.report_content)  # 报告正文
        (report_output_dir / "report_triage.txt").write_text(self.report_triage)  # triage 判定
        (report_output_dir / "report_objects.txt").write_text(
            "\n".join(self.report_objects) if self.report_objects else "NONE"
        )  # 涉及对象逐行写入；空清单写占位串 "NONE"（区分"无对象"与"空文件"）
