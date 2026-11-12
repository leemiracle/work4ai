# =============================================================================
# 【模块定位】KNighter 阶段一 Checker Synthesis 的总编排器：论文 §3.1 Algorithm 1
#   "Synthesize checkers with input patch" 的工程实现——读入 bug-fix patch commit
#   列表，驱动 pattern→plan→checker→repair→validation 迭代循环，产出候选 CSA
#   checker 及其 TP/TN 排名。
#
# 【论文映射（代码结构 ↔ Algorithm 1 行号语义）】
#   gen_checker_worker 内 `for i in range(..., checker_nums)` = Algorithm 1 的
#   `for iter = 1 to maxIterations` 外层循环（checker_nums 默认 10，见
#   config-example.yaml，对应论文 maxIterations=10）：
#     · Step 1 patch2pattern  = Algorithm 1 的 Bug Pattern Analysis（§3.1.1）：
#       LLM 从 patch diff 提炼 targeted bug pattern（刻意收窄，不做泛化空指针）；
#     · Step 2 pattern2plan    = Plan Synthesis（§3.1.2）：pattern + 9 个 utility
#       函数签名清单 → CSA 回调/状态维护的高层实现计划（消融证明该阶段把
#       validity 从 8 提到 12、语法错从 52 降到 28）；
#     · Step 3 plan2checker    = Implementation（§3.1.3 前半）：pattern+plan+
#       预定义模板+few-shot 例子 → checker.cpp 源码；
#     · Step 4 repair_checker(max_idx=4) = Syntax Repair（§3.1.3 后半）：1 次首编
#       + 4 次 LLM 依编译错误修复 = 共 5 次编译尝试，对应论文 maxAttempts=5；
#     · Step 5 validate_checker = Validation（§3.1.4 差分验证）：checkout 到
#       buggy（父提交）扫 patch 涉及对象累计 TP，checkout 到 patched 累计 TN；
#       论文判据 valid ⟺ N_buggy > N_patched 且 N_patched < T_valid 在代码中按
#       对象粒度实例化（csa.py: `num_bugs < num_bug_obj[obj] and num_bugs < 5`
#       ⇒ TN+=1），本文件将其聚合为 "perfect ⟺ TP>0 且 TN>0"；
#     · perfect 即 break = Algorithm 1 中 valid 即返回 checker；maxIterations
#       耗尽仍无 perfect = 论文的 return Null（本实现不显式返回 Null，而是
#       perfect_checkers==0，但 ranking.txt 仍按 (TP,TN) 降序保留全部尝试供下游
#       /人工检视——工程上不丢信息的 Null 等价物）。
#
# 【管线角色】上游 main.py 按 config 调 gen_checker（批量）/gen_checker_worker
#   （单 commit）；本模块把 LLM 调用委托给 src/agent.py 的 4 个 agent
#   （patch2pattern/pattern2plan/plan2checker/patch2checker），把编译修复委托给
#   src/checker_repair.py，把差分验证委托给 src/backends/csa.py 的
#   validate_checker；产物（checkers/*.cpp、ranking.txt、summary.json）交给
#   阶段二 src/checker_refine.py（论文 §3.2 Refinement）消费。
#
# 【关键依赖与坑】
#   · global_config 单例提供 backend（CSA）/target（Linux/V8/Chromium）/checker_nums；
#   · ranking.txt 断点续跑用 eval() 反序列化（安全隐患，非 json）；
#   · gen_checker 的 result_file 形参在函数体内被同名时间戳输出文件覆盖
#     （先读旧文件去重、再写新文件的 resume 语义）；
#   · commit 行 split(",") 位于 try 之外，格式非法会炸掉整批循环；
#   · 哨兵约定：(i,-10,-10)=生成/编译失败、(-1,-1)=验证期内核对象构建失败
#     （直接 break 整个 commit）、(-2,-2)=scan-build 崩溃（仅记录不 break）；
#   · ARCHITECTURE.md 所述 CheckerGenerator/GenerationConfig/GenerationResult
#     三个"Key Classes"实际并不存在——文档滞后于代码，勿据文档找类。
# =============================================================================
import json  # 序列化 metadata.json / summary.json / 06_validation.json
import time  # 步骤计时（step_times）与时间戳文件名（%Y%m%d_%H%M%S）
from dataclasses import dataclass, field  # 定义下方两个记录型 dataclass
from datetime import datetime  # 批次/提交级开始与结束时间戳（isoformat 落盘）
from pathlib import Path  # 结果目录树与 01~06 编号中间产物路径操作
from typing import Any, Dict, List  # 类型注解（GenerationSummary.to_dict 等）

# 四个 LLM agent 入口（src/agent.py）：use_multi=True 时按论文三阶段走前三个；
# patch2checker 是"一步到位"的单阶段变体（对应论文消融实验的无分解 baseline）
from agent import patch2checker, patch2pattern, pattern2plan, plan2checker
from checker_data import CheckerData  # 单次迭代全部状态的数据容器（yaml 可落盘）
from checker_example import init_example  # 加载 3 个人工 few-shot 端到端例子（prompt_template/examples/，论文称 40 人时打磨）
from checker_repair import repair_checker  # §3.1.3 Syntax Repair 循环（编译失败→LLM 修复→重编）
from global_config import global_config, logger  # 全局单例配置（backend/target/result_dir）与统一 logger
from tools import extract_checker_code  # 从 LLM 响应中剥掉 ```cpp markdown 围栏，抽出纯 C++ 源码


# =============================================================================
# GenerationProgress —— 纯 UI/可观测性辅助类（Algorithm 1 的步骤 1~6 进度条）
# =============================================================================
# 进度跟踪器：把一次 checker 合成拆成 6 个可视化步骤（Pattern→Plan→Code→
# Repair→Validation→Summary），与论文 §3.1 的四个 Agent 阶段 + 汇总一一对应。
# 注意：step_names 里的默认图标（🔍/📋/...）与实际调用处传入的名字（🧩/...）
# 存在装饰性不一致——step_times 以名字字符串为键，不影响计时正确性。
@dataclass
class GenerationProgress:
    """Track progress of checker generation."""  # 原 docstring 保留：跟踪 checker 生成进度

    total_steps: int = 6  # 总步骤数：模式提取/计划/代码生成/语法修复/验证/汇总
    current_step: int = 0  # 当前步骤序号（0 起，start_step 时自增）
    step_names: List[str] = field(  # 步骤名默认表：仅当 start_step() 不传名字时兜底使用
        default_factory=lambda: [  # dataclass 可变默认值必须用 default_factory（列表陷阱）
            "🔍 Pattern Extraction",  # Step1 pattern 提取（§3.1.1）
            "📋 Plan Generation",  # Step2 plan 合成（§3.1.2）
            "💻 Code Generation",  # Step3 checker 代码生成（§3.1.3 Implementation）
            "🔧 Syntax Repair",  # Step4 编译修复（§3.1.3 Syntax Repair）
            "✅ Validation",  # Step5 差分验证（§3.1.4）
            "📊 Summary",  # Step6 结果汇总（工程附加）
        ]
    )
    start_time: datetime = field(default_factory=datetime.now)  # 整轮生成起始时刻（get_total_time 用）
    step_times: Dict[str, float] = field(default_factory=dict)  # 步骤名→时间戳/耗时（开始存时间戳，完成后覆写为秒数）

    def start_step(self, step_name: str = None):
        """Start a new step."""  # 原docstring保留：开始一个新步骤
        if step_name is None:  # 未显式给名字则按 current_step 查默认表
            step_name = self.step_names[self.current_step]

        self.current_step += 1  # 步骤指针前移
        progress = (self.current_step / self.total_steps) * 100  # 百分比进度（基于 6 步）

        logger.info(f"[{progress:5.1f}%] {step_name}")  # 写日志（:5.1f 定宽对齐）
        print(f"⏳ [{progress:5.1f}%] {step_name}...")  # 终端进度提示

        self.step_times[step_name] = time.time()  # 记录该步骤开始时刻（绝对时间戳）
        return step_name  # 回传步骤名，供配对的 complete_step/fail_step 使用

    def complete_step(self, step_name: str, details: str = ""):
        """Complete the current step."""  # 原docstring保留：完成当前步骤
        if step_name in self.step_times:  # 配对到 start_step 的时间戳
            duration = time.time() - self.step_times[step_name]  # 计算耗时
            self.step_times[step_name] = duration  # 原地覆写为耗时秒数（时间戳→时长）
        else:
            duration = 0  # 未配对（理论上不发生）按 0 计

        print(f"✅ {step_name} ({duration:.1f}s)")  # 终端打勾
        if details:
            print(f"   └── {details}")  # 缩进的补充细节行（如 "TP: 1, TN: 1"）
        logger.info(f"Completed: {step_name} in {duration:.1f}s - {details}")

    def fail_step(self, step_name: str, error: str):
        """Mark step as failed."""  # 原docstring保留：标记步骤失败
        if step_name in self.step_times:
            duration = time.time() - self.step_times[step_name]  # 只算耗时
        else:
            duration = 0  # 未配对按 0 计

        # 注意：与 complete_step 不同，这里不把 step_times 覆写为时长（保留开始
        # 时间戳）——轻微不对称，属实现细节，无功能影响
        print(f"❌ {step_name} ({duration:.1f}s)")  # 终端打叉
        print(f"   └── Error: {error}")  # 错误详情
        logger.error(f"Failed: {step_name} in {duration:.1f}s - {error}")

    def get_total_time(self) -> float:
        """Get total elapsed time."""  # 原docstring保留：获取总耗时
        return (datetime.now() - self.start_time).total_seconds()  # 自构造起的总秒数（写进 GenerationSummary.total_time）


# =============================================================================
# GenerationSummary —— 单 commit 的合成结果统计（供 batch 汇总与 summary.json）
# =============================================================================
# 结果摘要：一个 commit 的 checker 合成战报。字段语义：
#   perfect（TP>0 且 TN>0）= 论文意义的 valid checker（差分验证通过）；
#   successful（TP>0 或 TN>0）= 至少在一个方向上判对（半成品，仍有参考价值）。
@dataclass
class GenerationSummary:
    """Summary of checker generation results."""  # 原docstring保留：生成结果摘要

    commit_id: str  # 被分析的 bug-fix commit 哈希
    commit_type: str  # bug 类别标签（NPD/UAF/Double-Free 等 10 类，见 src/commit_label.py）
    total_checkers: int  # 本 commit 总尝试次数（含编译失败的 -10 哨兵条目）
    successful_checkers: int  # TP>0 或 TN>0 的 checker 数（任一方向判对）
    perfect_checkers: int  # TP>0 且 TN>0 的 checker 数（= 论文 valid 数；>0 即 Algorithm 1 提前返回）
    best_tp: int  # 所有尝试中的最大 TP（最好抓 bug 能力）
    best_tn: int  # 所有尝试中的最大 TN（最好抑制误报能力）
    total_time: float  # 本 commit 整轮耗时（秒）
    errors: List[str] = field(default_factory=list)  # 逐条累积的错误信息（打印时只展示前 3 条）

    def to_dict(self) -> Dict[str, Any]:
        # 序列化为可 json.dump 的纯字典（补上派生字段 success_rate 与时间戳）
        return {
            "commit_id": self.commit_id,
            "commit_type": self.commit_type,
            "total_checkers": self.total_checkers,
            "successful_checkers": self.successful_checkers,
            "perfect_checkers": self.perfect_checkers,
            "best_tp": self.best_tp,
            "best_tn": self.best_tn,
            "total_time": self.total_time,
            "errors": self.errors,
            "success_rate": self.successful_checkers / max(self.total_checkers, 1),  # max(...,1) 防 0 除
            "timestamp": datetime.now().isoformat(),  # 落盘时刻（isoformat 便于排序）
        }

    def print_summary(self):
        """Print a formatted summary."""  # 原docstring保留：打印格式化摘要
        print("\n" + "=" * 60)  # 60 字符宽分隔线
        print(f"🎯 GENERATION SUMMARY")  # 摘要标题
        print("=" * 60)
        print(f"📋 Commit: {self.commit_id} ({self.commit_type})")  # commit 与 bug 类别
        print(f"⏱️  Total Time: {self.total_time:.1f}s")  # 总耗时
        print(f"🔢 Checkers Generated: {self.total_checkers}")  # 尝试总数
        print(f"✅ Successful: {self.successful_checkers}/{self.total_checkers}")  # 任一方向判对的比例
        print(f"🎉 Perfect: {self.perfect_checkers}")  # valid（差分验证通过）数量——核心指标
        print(f"🏆 Best Scores: TP={self.best_tp}, TN={self.best_tn}")  # 双向最佳得分

        if self.errors:  # 有错误则只展示前 3 条，余者计数提示
            print(f"⚠️  Errors: {len(self.errors)}")
            for i, error in enumerate(self.errors[:3], 1):  # 切片取前 3，enumerate 从 1 编号
                print(f"   {i}. {error}")
            if len(self.errors) > 3:
                print(f"   ... and {len(self.errors) - 3} more")

        success_rate = self.successful_checkers / max(self.total_checkers, 1)  # 防除零的成功率
        # 三档口语化评语（≥0.8 优 / ≥0.5 良 / 其余提示复查参数）
        if success_rate >= 0.8:
            print("🌟 Excellent generation rate!")
        elif success_rate >= 0.5:
            print("👍 Good generation rate")
        else:
            print("⚠️  Low generation rate - consider reviewing parameters")
        print("=" * 60)  # 收尾分隔线


# =============================================================================
# gen_checker —— 批量入口：遍历 commits.txt，逐 commit 调 gen_checker_worker
#   （论文 61 个人工精选 patch 的批量合成即走此入口）
# =============================================================================
# 批量驱动器：对 commit 清单里每个 "commit_id,commit_type" 行跑一次完整的
# Algorithm 1 循环，聚合批次统计并落盘三份时间戳文件（log/txt/json）。
def gen_checker(
    commit_file="commits.txt",  # 输入清单：每行 "commit_id,commit_type"
    result_file=None,  # 旧结果文件（可选）：用于断点续跑去重；注意函数体内会被同名新文件覆盖（见下）
    use_multi=True,  # True=论文三阶段（pattern→plan→checker）；False=patch2checker 单阶段消融
    use_general=False,  # True=patch2pattern 换用泛化模板（一般化 bug pattern，非论文默认的 targeted 收窄模式）
    no_utility=False,  # True=计划阶段剔除 9 个 utility 函数清单（论文消融开关之一）
    sample_examples=False,  # True=按 embedding 相似度动态采样 few-shot 例子；False=固定默认 3 例
):
    """Generate checkers for multiple commits with improved output format."""

    print("🚀 Starting Checker Generation")  # 批次启动横幅
    print(
        f"📁 Config: multi={use_multi}, general={use_general}, utility={not no_utility}"  # 打印生效配置（utility 取反映显开关）
    )
    logger.info(f"Starting batch generation with multi={use_multi}")

    content = Path(commit_file).read_text()  # 读入全部 commit 行
    result_dir = Path(global_config.result_dir)  # 全局结果根目录（config 的 result_dir）
    result_dir.mkdir(parents=True, exist_ok=True)  # 幂等建目录

    result_content = ""  # 旧结果内容（断点续跑的查重源）
    if result_file:
        result_content = Path(result_file).read_text()  # 读旧结果文件：已完成的 commit 将被跳过

    # Init example checkers if needed
    # 若开启动态采样，先把 3 个人工 few-shot 例子载入内存（ExampleChecker 列表，
    # 供 agent.py 的 choose_example 做 embedding 余弦相似度检索）
    if sample_examples:
        print("📚 Initializing example checkers...")
        init_example()

    # Setup output files
    # 三份时间戳输出文件：人类可读日志 / 机器可续跑结果 / 批次 JSON 汇总。
    # ⚠️ 坑：result_file 形参在此被覆盖为新时间戳路径——去重读旧文件、追加写
    # 新文件，两份文件并存，跨批续跑时要把旧文件作为形参再传入
    timestamp = time.strftime("%Y%m%d_%H%M%S")  # 批次时间戳（文件名去重）
    log_file = result_dir / f"generation_log_{timestamp}.log"  # 逐 commit 原始结果日志
    result_file = result_dir / f"generation_results_{timestamp}.txt"  # "commit,type,True/False/Exception" 续跑标记
    summary_file = result_dir / f"generation_summary_{timestamp}.json"  # 批次级 JSON 汇总

    batch_summary = {  # 批次统计骨架（结束时补 end_time/success_rate 后整体落盘）
        "start_time": datetime.now().isoformat(),  # 批次开始时刻
        "total_commits": 0,  # 实际处理的 commit 数（跳过的不计）
        "successful_commits": 0,  # 至少产出 1 个 perfect checker 的 commit 数
        "results": [],  # 每 commit 一个 GenerationSummary.to_dict()
    }

    # 逐行遍历（enumerate 从 1 编号，仅用于展示）；splitlines 天然跳过文件末尾换行
    for line_num, line in enumerate(content.splitlines(), 1):
        # 断点续跑去重：line 形如 "commit_id,commit_type"，旧结果行形如
        # "commit_id,commit_type,True/False"。外层 `line in result_content` 是
        # 粗粒度子串匹配（commit 哈希互为前缀时可能误伤），内层追加 ",False"/
        # ",True" 才是精确判定；旧记录为 ",Exception" 的行不匹配 → 允许重试
        if result_content and line in result_content:
            if line + ",False" in result_content or line + ",True" in result_content:
                print(f"⏭️  Skipping {line} (already processed)")
                logger.info(f"Skip {line}")
                continue  # 已有终态结果，跳过该 commit

        if not line.strip():
            # Skip empty lines
            continue  # 跳过空行

        # ⚠️ 坑：此行在 try 之外——清单行缺逗号会抛 ValueError 直接炸掉整批循环
        commit_id, commit_type = line.split(",")  # 拆出 commit 哈希与 bug 类别标签
        batch_summary["total_commits"] += 1  # 计入本批实际处理数

        print(f"\n📦 Processing commit {line_num}: {commit_id}")  # commit 处理横幅
        print(f"🏷️  Type: {commit_type}")  # bug 类别（NPD/UAF/...）

        try:
            # 核心：单 commit 的 Algorithm 1 完整循环（见下方 gen_checker_worker）
            checker_results, summary = gen_checker_worker(
                commit_id,
                commit_type,
                use_multi=use_multi,  # 三阶段 vs 单阶段
                use_general=use_general,  # targeted vs general pattern 模板
                no_utility=no_utility,  # 是否剔除 utility 清单
                sample_examples=sample_examples,  # few-shot 例子的选取方式
            )

            # Log results
            with open(log_file, "a") as flog:  # 原始 (i,TP,TN) 列表追加进人类日志
                flog.write(f"{commit_id} {commit_type} {checker_results}\n")

            with open(result_file, "a") as fres:  # 续跑标记文件：True=存在 perfect checker
                # correct = 任意一次尝试 TP>0 且 TN>0（= 论文 valid）；
                # 空列表时 any([])==False，全部失败自然记 False
                correct = any([TP > 0 and TN > 0 for _, TP, TN in checker_results])
                fres.write(f"{commit_id},{commit_type},{correct}\n")

            batch_summary["results"].append(summary.to_dict())  # 收编进批次 JSON
            if summary.perfect_checkers > 0:  # 有 valid checker 才计入成功 commit
                batch_summary["successful_commits"] += 1

            summary.print_summary()  # 终端打印该 commit 战报

        except Exception as e:
            # 单 commit 异常不炸整批：错误压平成单行（换行→空格）后记录并继续
            error_msg = str(e).replace("\n", " ")
            print(f"❌ Error processing {commit_id}: {error_msg}")
            logger.error(f"Error processing {commit_id}: {e}")

            with open(log_file, "a") as flog:  # 日志记 ERROR 行
                flog.write(f"{commit_id} {commit_type} ERROR: {error_msg}\n")
            with open(result_file, "a") as fres:  # 结果文件记 ",Exception"（续跑时该行不匹配 True/False → 可重试）
                fres.write(f"{commit_id},{commit_type},Exception\n")

    # Save batch summary
    # 批次收尾：补结束时刻与成功率（max(...,1) 防全跳过时的 0 除），整体落盘
    batch_summary["end_time"] = datetime.now().isoformat()
    batch_summary["success_rate"] = batch_summary["successful_commits"] / max(
        batch_summary["total_commits"], 1
    )

    with open(summary_file, "w") as f:  # 批次 JSON 汇总（indent=2 人类可读）
        json.dump(batch_summary, f, indent=2)

    print(f"\n🎊 Batch Complete!")  # 批次完成横幅
    print(
        f"📊 Success Rate: {batch_summary['successful_commits']}/{batch_summary['total_commits']}"  # 成功 commit / 总 commit
    )
    print(f"📄 Summary saved to: {summary_file}")  # 汇总文件路径回显


# =============================================================================
# gen_checker_worker —— ★ 本模块核心：论文 §3.1 Algorithm 1 的单 commit 实现 ★
#   maxIterations 循环 = `for i in range(len(checker_results), checker_nums)`；
#   每轮迭代：patch2pattern（§3.1.1）→ pattern2plan（§3.1.2）→ plan2checker
#   （§3.1.3 Implementation）→ repair_checker（§3.1.3 Syntax Repair，1+4=5 次
#   编译尝试 = 论文 maxAttempts=5）→ validate_checker（§3.1.4 差分验证，TP/TN）；
#   perfect（TP>0 且 TN>0）即 break（Algorithm 1 的 valid 即返回）；循环耗尽无
#   perfect = 论文 return Null 的工程等价（perfect_checkers==0）。
# =============================================================================
# 为单个 commit 合成至多 checker_nums 个候选 checker，带进度展示、断点续跑、
# 中间产物落盘与结果排名。
def gen_checker_worker(
    commit_id,  # bug-fix commit 哈希（patch 来源）
    commit_type,  # bug 类别标签
    use_multi=True,  # True=三阶段管线；False=patch2checker 一步生成（消融 baseline）
    use_plan_feedback=False,  # ⚠️ 死参数：本函数体从不消费。plan 反馈能力在 agent.pattern2plan 的
    #   no_tp_plans/no_fp_plans 形参上，但生成阶段从不传入（失败 plan 反馈属
    #   保留钩子，与阶段二 refinement 的失败反馈机制区分）
    use_general=False,  # patch2pattern 用泛化模板
    no_utility=False,  # plan/checker 生成剔除 utility 函数清单
    sample_examples=False,  # few-shot 例子动态采样（embedding 相似度）
):
    """Generate checkers for one commit with improved progress tracking."""

    progress = GenerationProgress()  # 6 步进度跟踪器（pattern→…→summary）
    analysis_backend = global_config.backend  # 静态分析后端（src/backends/csa.py 的 CSABackend：编译/扫描/验证）
    target = global_config.target  # 目标抽象（src/targets/：Linux allyesconfig 或 fork 增量的 V8/Chromium）

    checker_results = []  # [(迭代号 i, TP, TN), ...]——TP/TN 哨兵：-10 生成失败 / -1 构建失败 / -2 扫描崩溃
    checker_data_list: List[CheckerData] = []  # 每次迭代的完整数据容器（Step 6 统一 dump 为 yaml）
    checker_nums = global_config.get("checker_nums")  # maxIterations（config-example.yaml 默认 10）

    id = f"AllGen-{commit_type}-{commit_id}"  # 本 commit 的结果目录名（AllGen=全生成阶段产物前缀）
    result_dir = Path(global_config.result_dir)  # 全局结果根目录

    # Build directory structure
    _build_directory(id)  # 幂等建 5 个子目录（generation/checkers/build_logs/prompt_history/validation）

    # Create organized output structure
    output_dir = result_dir / id  # 本 commit 的输出根（=<result_dir>/AllGen-<type>-<commit>）
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save metadata
    # 元数据先行落盘：记录全部生效开关与 checker_nums，保证结果目录自解释、可复现
    metadata = {
        "commit_id": commit_id,
        "commit_type": commit_type,
        "generation_config": {
            "use_multi": use_multi,
            "use_general": use_general,
            "no_utility": no_utility,
            "sample_examples": sample_examples,
            "checker_nums": checker_nums,
        },
        "start_time": datetime.now().isoformat(),
    }

    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    patch = target.get_patch(commit_id)  # 从目标仓 git show 拿 bug-fix diff（后续所有阶段的输入）
    (output_dir / "commit_id.txt").write_text(commit_id)  # 目录自标识：commit 哈希
    (output_dir / "patch.md").write_text(patch)  # 原始 patch 存档（§3.1.1 Bug Pattern Analysis 的输入）

    # Check for existing results
    # 断点续跑：ranking.txt 存在说明本 commit 已跑过（可能未完成）。eval() 把
    # "[(0,1,1),(1,-10,-10),...]" 文本反序列化回元组列表——⚠️ 对文件内容直接
    # eval 存在代码执行风险，工程上应换 ast.literal_eval（此处为已知坑）
    ranking_file = output_dir / "ranking.txt"
    if ranking_file.exists():
        checker_results = eval(ranking_file.read_text())
        # 已有 perfect（TP>0 且 TN>0 = 论文 valid）→ 幂等缓存命中，直接返回
        # 零成本 summary（total_time=0），不再消耗 LLM 调用
        has_perfect = any([TP > 0 and TN > 0 for _, TP, TN in checker_results])
        if has_perfect:
            print("🎉 Perfect checker already exists!")
            logger.info(f"Perfect checker found for {id}")

            # 用既有结果拼一份摘要（不做任何重算）：三档统计 + best_tp/tn
            summary = GenerationSummary(
                commit_id=commit_id,
                commit_type=commit_type,
                total_checkers=len(checker_results),
                successful_checkers=len(  # TP>0 或 TN>0（任一方向判对）
                    [r for r in checker_results if r[1] > 0 or r[2] > 0]
                ),
                perfect_checkers=len(  # TP>0 且 TN>0（差分验证通过 = valid）
                    [r for r in checker_results if r[1] > 0 and r[2] > 0]
                ),
                best_tp=max([r[1] for r in checker_results], default=0),  # 空列表兜底 0（default=）
                best_tn=max([r[2] for r in checker_results], default=0),
                total_time=0,  # 缓存命中：不再计时
            )
            return checker_results, summary

    # Generate checkers
    # ★ Algorithm 1 主循环：从已完成尝试数续跑到 checker_nums（=maxIterations）。
    # 上面的早退已处理"有 perfect"情形，走到这里说明上次要么跑满要么中途
    # break 于 -1/-1（环境构建失败）——都从断点继续重试
    errors = []  # 本 commit 级错误累积（进 summary.errors）
    for i in range(len(checker_results), checker_nums):
        print(f"\n🔄 Generating checker {i+1}/{checker_nums}")  # 迭代进度（论文 iter/maxIterations）

        checker_data = CheckerData(commit_id, commit_type, result_dir, i, patch)  # 本次迭代的状态容器（tp/tn 默认 -10 哨兵）

        # Create organized intermediate directory
        intermediate_dir = output_dir / "generation" / f"checker_{i:02d}"  # :02d 零填充保证字典序=迭代序
        intermediate_dir.mkdir(parents=True, exist_ok=True)

        try:
            if use_multi:
                # Step 1: Pattern Extraction
                # §3.1.1 Bug Pattern Analysis：patch diff → targeted bug pattern
                # 文本（LLM agent，prompt 模板见 prompt_template/patch2pattern.md；
                # use_general 切换为泛化模板）。产出写入 01_pattern.txt
                step_name = progress.start_step("🧩 Pattern Extraction")
                pattern = patch2pattern(id, i, patch, use_general=use_general)
                progress.complete_step(step_name, f"Extracted {len(pattern)} chars")

                # Step 2: Plan Generation
                # §3.1.2 Plan Synthesis：pattern + patch + few-shot 例子 → 高层
                # 实现计划（选哪些 CSA 回调、维护什么 ProgramState map）。消融：
                # no_utility 剔除 9 个 utility 函数清单；sample_examples 改用
                # embedding 相似度采样的例子（否则固定默认 3 例）
                step_name = progress.start_step("📋 Plan Generation")
                plan = pattern2plan(
                    id,
                    i,
                    pattern,
                    patch,
                    no_utility=no_utility,
                    sample_examples=sample_examples,
                )
                refined_plan = plan  # 生成阶段无 plan 精修：直接透传（plan 反馈参数未被本模块使用，见函数头注释）
                progress.complete_step(
                    step_name, f"Generated {len(plan.splitlines())} line plan"
                )

                # Step 3: Code Generation
                # §3.1.3 Implementation：pattern + plan + patch + 例子 →
                # checker.cpp 源码（LLM agent，模板 plan2checker.md）
                step_name = progress.start_step("💻 Code Generation")
                checker_code = plan2checker(
                    id,
                    i,
                    pattern,
                    refined_plan,
                    patch,
                    no_utility=no_utility,
                    sample_examples=sample_examples,
                )
                progress.complete_step(
                    step_name, f"Generated {len(checker_code.splitlines())} lines"
                )
            else:
                # 单阶段消融分支：跳过 pattern/plan，直接 patch→checker 一步生成
                # （对应论文"无计划分解"的 ablation baseline；中间产物置空串
                # 以便后续统一落盘）
                step_name = progress.start_step("💻 Direct Code Generation")
                pattern = ""
                plan = ""
                refined_plan = ""
                checker_code = patch2checker(id, i, patch)
                progress.complete_step(
                    step_name, f"Generated {len(checker_code.splitlines())} lines"
                )

            # 剥掉 LLM 响应外层的 ```cpp markdown 围栏，抽出纯 C++ 代码体
            checker_code = extract_checker_code(checker_code)

            # Update checker data
            checker_data.pattern = pattern  # 回填 pattern（§3.1.1 产物）
            checker_data.plan = plan  # 回填 plan（§3.1.2 产物）
            checker_data.initial_checker_code = checker_code  # 回填修复前原始代码（§3.1.3 产物）

            # Save intermediate files with clear naming
            # 编号中间产物：审计时可逐阶段对照论文四步（01~04 对应生成侧）
            (intermediate_dir / "01_pattern.txt").write_text(pattern)
            (intermediate_dir / "02_plan.txt").write_text(plan)
            (intermediate_dir / "03_refined_plan.txt").write_text(refined_plan)
            (intermediate_dir / "04_initial_code.cpp").write_text(checker_code)

            # Step 4: Syntax Repair
            # §3.1.3 Syntax Repair：repair_checker 内部循环 = 1 次首编 + max_idx
            # 次"读编译错误→LLM 修复→重编"，此处 max_idx=4 ⇒ 共 5 次编译尝试，
            # 对应论文 maxAttempts=5；成功返回 (True, 修复后代码)，失败 (False, None)
            step_name = progress.start_step("🔧 Syntax Repair")
            ret, repaired_checker_code = repair_checker(
                id=id,
                repair_name=f"syntax-repair-{i:02d}",  # 修复子目录名（含迭代号）
                max_idx=4,  # 4 轮修复 + 1 次首编 = 5 次编译（论文 maxAttempts=5）
                intermediate_dir=intermediate_dir,  # 修复日志/中间版本落盘位置
                checker_code=checker_code,
            )

            if not ret:
                # 5 次编译尝试仍失败：本次迭代作废（Algorithm 1 该 iter 计为
                # 失败），记 -10 哨兵后 continue 进入下一迭代
                error_msg = f"Failed to generate compilable checker {i}"
                progress.fail_step(step_name, error_msg)
                errors.append(error_msg)
                checker_results.append((i, -10, -10))  # -10 = 不可编译哨兵（CheckerData 默认值同源）
                checker_data_list.append(checker_data)  # 失败尝试的数据也保留（Step 6 落盘供审计）
                continue

            progress.complete_step(step_name, "Compilation successful")
            checker_data.repaired_checker_code = repaired_checker_code  # 回填修复后代码

            # Save repaired code
            (intermediate_dir / "05_repaired_code.cpp").write_text(
                repaired_checker_code
            )

            # Also save in checkers directory for compatibility
            # 双写兼容目录：checkers/checker_XX.cpp 是阶段二 refinement 及脚本
            # 约定的最终 checker 位置（generation/ 下才是全量中间产物）
            checkers_dir = output_dir / "checkers"
            checkers_dir.mkdir(parents=True, exist_ok=True)
            (checkers_dir / f"checker_{i:02d}.cpp").write_text(repaired_checker_code)

            # Step 5: Validation
            # §3.1.4 差分验证（csa.py::_validate_checker_linux）：
            #   checkout buggy（patch 父提交）→ 逐个编译 patch 涉及对象并
            #   scan-build → 报 bug 则 TP+=1；
            #   checkout patched → "No bugs found" 则 TN+=1；若报数比 buggy 侧
            #   减少且 <5 也 TN+=1（论文判据 N_buggy>N_patched 且 N_patched<
            #   T_valid 的按对象实例化）；报数反超则 TN-=1；
            #   构建失败 ⇒ 返回 (-1,-1)；scan-build 崩溃 ⇒ 返回 (-2,-2)。
            # skip_build_checker=True：Step 4 刚编译过 plugin .so，无需重复构建
            step_name = progress.start_step("✅ Validation")
            TP, TN = analysis_backend.validate_checker(
                repaired_checker_code,
                commit_id,
                patch,
                target,
                skip_build_checker=True,
            )

            # Update checker data
            checker_data.tp_score = TP  # 回填差分验证得分（buggy 侧检出）
            checker_data.tn_score = TN  # 回填差分验证得分（patched 侧安静度）
            checker_results.append((i, TP, TN))  # 计入排名列表
            checker_data_list.append(checker_data)

            progress.complete_step(step_name, f"TP: {TP}, TN: {TN}")

            # Save validation results
            # 06 号中间产物：结构化验证记录（is_perfect 即论文的 valid 判定）
            validation_result = {
                "checker_id": i,
                "tp_score": TP,
                "tn_score": TN,
                "is_perfect": TP > 0 and TN > 0,  # valid ⟺ 双向都判对
                "timestamp": datetime.now().isoformat(),
            }
            (intermediate_dir / "06_validation.json").write_text(
                json.dumps(validation_result, indent=2)
            )

            if TP > 0 and TN > 0:
                # perfect = valid：Algorithm 1 的"验证通过即返回该 checker"——
                # 提前终止 maxIterations 循环，省掉剩余迭代的 LLM 调用
                print(f"🎉 Perfect checker {i} found!")
                logger.info(f"Perfect checker {i} found: TP={TP}, TN={TN}")
                break
            elif TP == -1 and TN == -1:
                # 验证期内核对象构建失败：环境性故障（与 checker 质量无关），
                # 同一 commit 重试大概率仍失败 → break 终止整个 commit 的循环
                #（注意：-2/-2 的 scan-build 崩溃不走此分支，仅被记录后继续）
                error_msg = f"Failed to evaluate checker {i}"
                errors.append(error_msg)
                logger.error(error_msg)
                break

        except Exception as e:
            # 单次迭代异常（LLM 调用失败/解析异常等）不终止循环：记 -10 哨兵
            # 后 continue——Algorithm 1 中该 iter 作废、继续下一轮重试的语义
            error_msg = f"Error generating checker {i}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
            checker_results.append((i, -10, -10))
            continue

    # Step 6: Summary Generation
    # 收尾汇总：全部尝试的数据落盘 + 排名 + summary.json（工程附加步骤，非
    # 论文 Algorithm 1 的显式行，但对应"全失败返回 Null"前的信息保全）
    step_name = progress.start_step("📊 Summary Generation")

    # Save all checker data
    # 每次尝试的 CheckerData 双路落盘：dump() 写 checker-<id>.yaml（全字段），
    # dump_dir() 写目录化产物（供阶段二 refinement 按目录续接）
    for checker_data in checker_data_list:
        checker_data.dump()
        checker_data.dump_dir()

    # Sort and save results
    # 按 (TP, TN) 双键降序——best checker 排首位；str(列表) 即后续 eval 续跑
    # 反序列化的来源（与上方 ranking_file 读取格式闭环）
    checker_results = sorted(checker_results, key=lambda x: (x[1], x[2]), reverse=True)
    ranking_file.write_text(str(checker_results))

    # Create comprehensive summary
    # 汇总统计：三档计数 + 双向最佳 + 总耗时 + 错误清单（列表推导逐项统计）
    summary = GenerationSummary(
        commit_id=commit_id,
        commit_type=commit_type,
        total_checkers=len(checker_results),
        successful_checkers=len([r for r in checker_results if r[1] > 0 or r[2] > 0]),  # 任一方向判对
        perfect_checkers=len([r for r in checker_results if r[1] > 0 and r[2] > 0]),  # valid 数（论文主指标）
        best_tp=max([r[1] for r in checker_results], default=0),
        best_tn=max([r[2] for r in checker_results], default=0),
        total_time=progress.get_total_time(),  # 自 worker 构造起墙钟总耗时
        errors=errors,
    )

    # Save summary
    (output_dir / "summary.json").write_text(json.dumps(summary.to_dict(), indent=2))

    progress.complete_step(
        step_name, f"Generated summary for {len(checker_results)} checkers"
    )

    # 返回 (排名后的 (i,TP,TN) 列表, 摘要)。maxIterations 全失败时无 perfect
    # 条目——即论文 return Null 的工程等价（调用方据 perfect_checkers==0 判定）
    return checker_results, summary


def _build_directory(id: str):
    """Build the directory structure for the result."""  # 原docstring保留：搭建结果目录结构
    basedir = Path(global_config.result_dir) / id  # 本 commit 结果根目录
    basedir.mkdir(parents=True, exist_ok=True)  # 幂等创建（断点续跑可重复调用）

    # Create organized subdirectories
    # 五个固定子目录：生成中间产物 / 最终 checker / 编译日志 / LLM prompt
    # 历史 / 验证结果——gen_checker_worker 与 repair/refine 模块按此约定读写
    subdirs = [
        "generation",  # Individual checker generation steps  （原注释保留）逐迭代 01~06 中间产物
        "checkers",  # Final checker files  （原注释保留）修复后的最终 checker.cpp
        "build_logs",  # Compilation logs  （原注释保留）repair_checker 的编译/修复日志
        "prompt_history",  # LLM interaction history  （原注释保留）agent.py 各阶段 prompt+响应存档
        "validation",  # Validation results  （原注释保留）差分验证（TP/TN）产物
    ]

    for subdir in subdirs:  # 逐个幂等创建
        (basedir / subdir).mkdir(parents=True, exist_ok=True)
