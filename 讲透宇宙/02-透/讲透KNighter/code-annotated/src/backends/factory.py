# =============================================================================
# 【模块定位】KNighter 的"分析后端"抽象基类：把 checker 合成完成之后一切与
#   具体静态分析引擎强耦合的操作——
#   ① 把 checker C++ 源码编译成引擎可加载的形式（build_checker）
#   ② 差分验证 checker 是否复现原 patch 修复的 bug（validate_checker）
#   ③ 全库扫描产出原始报告（run_checker）
#   ④ 从报告文本反解出被分析的构建对象（get_objects_from_report）
#   ⑤ 从报告目录采样/蒸馏报告供 LLM 消费（extract_reports）
# ——抽象成统一接口。当前唯一实现 = src/backends/csa.py::ClangBackend（Clang
#   Static Analyzer，论文主引擎）；论文 §6 Generability 讨论了把本抽象换成
#   CodeQL/Semgrep 等其他引擎的可能（global_config.py:47 的 FIXME 亦为伏笔）。
#
# 【论文映射】五个抽象方法分别锚定管线的不同阶段：
#   - build_checker → §3.1.3 Implementation/Syntax Repair 的"编译"动作：
#     LLM 产出的 checker.cpp 必须编译成 LLVM 插件（llvm_utils/create_plugin.py
#     生成 opaq 壳插件骨架），编译失败即触发 checker_repair.py 的修复循环
#     （checker_repair.py:53 消费本接口拿 return_code/stderr 喂修复 prompt）；
#   - validate_checker → §3.1.4 Validation 差分验证：返回 (TP, TN) 二元组
#     （checker_gen.py:422 消费），valid 判据 = buggy 版本报数 > patched 版本
#     报数且 patched 报数 < 50（N_buggy > N_patched），见 targets/factory.py 头注；
#   - run_checker → §4/§5 全库扫描：扫描整个代码库并返回 bug 计数
#     （checker_scan.py:182 消费，-j32 并行、禁内置 checker 包）；
#   - extract_reports → §3.2 采样协议：最多解析 max_num(=100) 条报告、按涉及
#     文件聚类后采 sampled_num(=5) 个文件各取首条、seed 控制可复现采样
#     （checker_refine.py:1097/1126 消费——refine 首轮 seed=0、后续轮换
#     attempt_id 防重复采样）；
#   - get_objects_from_report → §3.2 triage 后的定位复验：从单条报告反解
#     构建对象名，供 checker_refine.py:1182 在"对象级"重扫确认 FP 是否消除。
#
# 【管线角色】上游：src/global_config.py:59（唯一实例化点
#   ClangBackend(self.get("LLVM_dir"))，经 backend property 注入 _config，
#   全仓单例）；下游：checker_gen（validate）/checker_repair（build）/
#   checker_scan（run）/checker_refine（extract_reports+get_objects）。
#   与 targets/factory.py::TargetFactory 互为对偶：Target 抽象"被分析的代码库"
#   （Linux/V8），本类抽象"执行分析的引擎"（CSA）——两者交叉注入使管线五阶段
#   对目标与引擎双双无感知。
#
# 【依赖与坑】
#   - backend_path 语义 = LLVM 源码树根（config 键 LLVM_dir，由 scripts/
#     setup_llvm.py / setup_llvm_21.py 安装）：csa.py 内部拼 backend_path/"build"
#     找 LLVM 构建产物、backend_path/"clang/lib/Analysis/plugins" 落 checker 插件；
#   - 坑：validate_checker/run_checker 签名里的 target: TargetFactory 是引擎与
#     目标两个抽象的交接点——csa.py 实现里按 target._target_type 分派
#     _linux/_v8 两套私有实现（组合优于继承的运行期双分派）；
#   - 坑：build_checker 的 attempt 参数只影响日志目录命名（区分多次编译尝试），
#     不参与编译语义；skip_build_checker=True 用于复用上轮编译产物省时；
#   - 坑：extract_reports 的 stop_num/max_num 参数在本类 docstring 中未列出
#     （上游文档缺漏），实际语义见 csa.py 实现——累计 stop_num 条全 FP 即
#     提前停止采样。
# =============================================================================
from abc import ABC, abstractmethod          # ABC + @abstractmethod：强制子类实现全部五接口
from pathlib import Path                     # backend_path 规范化为 Path，便于后续 / 拼接
from typing import List, Optional, Tuple     # extract_reports 返回 Tuple[Optional[List[ReportData]], int]

from checker_data import ReportData          # 报告数据类：extract_reports 采样蒸馏的载体
                                              # （含 bug 信息/trace/文件行号，refine 的输入单元）
from targets.factory import TargetFactory    # 对偶抽象：被分析目标（Linux/V8），见
                                              # validate_checker/run_checker 的 target 形参


# -----------------------------------------------------------------------------
# 分析后端抽象基类：唯一子类 = ClangBackend（csa.py）。设计意图与 TargetFactory
# 相同——论文 §3.1 的各 agent 阶段只面向本接口编程，换引擎（CodeQL/Semgrep）
# 时只需新增子类并在 global_config.py:59 换装配，管线代码零改动。
# -----------------------------------------------------------------------------
class AnalysisBackendFactory(ABC):
    """
    Abstract base class for different backends.
    """
    # ↑ 原有 docstring 按铁律原样保留（docstring 是 AST 字符串节点，一个字节都不能动）

    # -----------------------------------------------------------------------------
    # 构造器：记录后端根路径。
    # 参数 backend_path：对 CSA 后端 = LLVM 源码树根（config 键 LLVM_dir）；
    #                   csa.py 用它拼出 build/ 与 clang/lib/Analysis/plugins/。
    # 注意：基类只存路径不开辟资源；具体初始化（如构建目录准备）在子类进行。
    # -----------------------------------------------------------------------------
    def __init__(self, backend_path: str):
        """
        Initialize the backend with a path.

        Args:
            backend_path (str): The path to the backend.
        """
        # ↑ 原有 docstring 按铁律原样保留（docstring 是 AST 字符串节点，一个字节都不能动）
        self.backend_path = Path(backend_path)  # str → Path：后续所有路径拼接的前缀句柄

    # -----------------------------------------------------------------------------
    # 接口① 编译 checker：把 LLM 生成的 checker C++ 源码编译成引擎可加载产物。
    # 调用方：checker_repair.py:53（Syntax Repair 循环——编译失败把 stderr 喂回
    #         LLM 修代码，max 5 次，论文 §3.1.3）+ csa.py 内部 build_checker_group。
    # 参数 attempt：第几次编译尝试（仅用于日志目录命名，区分多轮修复产物）。
    # -----------------------------------------------------------------------------
    @abstractmethod
    def build_checker(self, checker_code: str, log_dir: Path, attempt=1, **kwargs):
        """
        Build the checker in the backend.

        Args:
            **kwargs: Additional arguments for the build command.
        """
        raise NotImplementedError("Subclasses must implement this method.")
        # ↑ 抽象方法体恒 NotImplementedError；@abstractmethod 已保证子类不实现
        #   就无法实例化，此处 raise 只是防御性双保险（下同，四接口皆然）

    # -----------------------------------------------------------------------------
    # 接口② 差分验证（论文 §3.1.4 Validation 核心）：
    #   对同一 checker 分别扫 buggy 版本（补丁父提交）与 patched 版本（补丁提交）
    #   的 patch 涉及对象，返回 (TP, TN)——TP=buggy 版本上真报出的目标 bug 数，
    #   TN=patched 版本上的报数；valid ⟺ TP > TN 且 TN < 50。
    # 调用方：checker_gen.py:422（Algorithm 1 合成循环的接受闸门）。
    # 参数 skip_build_checker：复用已有编译产物跳过重编（差分两轮共享一次编译）。
    # -----------------------------------------------------------------------------
    @abstractmethod
    def validate_checker(
        self,
        checker_code: str,
        commit_id: str,
        patch: str,
        target: TargetFactory,
        skip_build_checker=False,
    ) -> Tuple[int, int]:
        """
        Validate the checker against a commit and patch.

        Args:
            commit_id (str): The commit ID to validate against.
            patch (str): The patch to apply.
            target (TargetFactory): The target to be tested.
            skip_build_checker (bool): Whether to skip building the checker.
        Returns:
            Tuple[int, int]: The number of true positives and true negatives.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    # -----------------------------------------------------------------------------
    # 可读化输出（调试用）：一行打印后端根路径。
    # -----------------------------------------------------------------------------
    def __str__(self):
        return f"Analysis Backend Path: {self.backend_path}"

    # -----------------------------------------------------------------------------
    # 接口③ 全库扫描（论文 §4/§5 部署形态）：加载编译好的 checker 扫整个代码库。
    # 调用方：checker_scan.py:182（返回 bug_count，后续进 triage/refine 闭环）。
    # 参数 object_to_analyze：None=全库，否则只扫指定构建对象（局部复验用）；
    #         jobs：并行度（论文默认 -j32）；output_dir：scan-build 报告落盘目录；
    #         skip_checkout：不切 commit（已就位时省一次 checkout）。
    # -----------------------------------------------------------------------------
    @abstractmethod
    def run_checker(
        self,
        checker_code: str,
        commit_id: str,
        target: TargetFactory,
        object_to_analyze=None,
        jobs=32,
        output_dir="tmp",
        skip_build_checker=False,
        skip_checkout=False,
        **kwargs,
    ):
        """
        Run the checker against a commit and patch.

        Args:
            checker_code (str): The code of the checker to run.
            commit_id (str): The commit ID to validate against.
            target (TargetFactory): The target to be tested.
            object_to_analyze (str): The object to analyze.
            jobs (int): The number of jobs to run in parallel.
            output_dir (str): The directory to store the output.
            **kwargs: Additional arguments for the run command.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    # -----------------------------------------------------------------------------
    # 接口④ 报告 → 构建对象反解：从单条报告文本提取被分析的 .o 对象名。
    # 调用方：checker_refine.py:1182——triage 判定某报告为 FP 后，拿到对象名做
    # "对象级"重扫，验证 refinement 后该 FP 是否消失（§3.2 双准则接受之一）。
    # @staticmethod：不依赖实例状态（纯文本解析），子类按各自报告格式实现。
    # -----------------------------------------------------------------------------
    @staticmethod
    @abstractmethod
    def get_objects_from_report(report: str, target: TargetFactory):
        """
        Get the objects from the report.

        Args:
            report (str): The report to parse.
            target (TargetFactory): The target to be tested.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    # -----------------------------------------------------------------------------
    # 接口⑤ 报告采样与蒸馏（论文 §3.2 采样协议）：取报告目录里最新一轮扫描，
    #   最多解析前 max_num 条 HTML → 按涉及文件聚类 → 随机采 sampled_num 个
    #   文件、每文件取首条，返回 (报告列表或 None, 聚类文件数)。
    #   stop_num 语义（上游 docstring 未列）：先取 max(sampled_num, stop_num)
    #   作为最低报告数闸门——总报数不足即判"checker 已足够干净、无需 refine"，
    #   返回 (None, 报数)（对应 checker_refine 的 "Checker is perfect!" 分支）。
    # 调用方：checker_refine.py:1097/1126——蒸馏后的报告才喂 triage/refine agent
    #   （直接喂原始 scan-build 报告会爆 token，见 agent.py::reduce_report）。
    # 坑：docstring 漏了 stop_num/max_num 两参说明（上游文档缺漏，实参语义
    #   以 csa.py 实现为准）；seed=attempt_id 的换种子策略防跨轮重复采样。
    # -----------------------------------------------------------------------------
    @staticmethod
    @abstractmethod
    def extract_reports(
        report_dir: str,
        output_dir: str,
        sampled_num: int = 5,
        stop_num: int = 5,
        max_num: int = 100,
        seed: int = 0,
    ) -> Tuple[Optional[List[ReportData]], int]:
        """
        Extract reports from the report directory.

        Args:
            report_dir (str): The directory containing the reports.
            output_dir (TargetFactory): The directory to store the extracted reports.
            sampled_num (int): The number of reports to sample.
            stop_num (int): The number of reports to stop at.
            seed (int): The seed for random sampling.
        """
        raise NotImplementedError("Subclasses must implement this method.")
