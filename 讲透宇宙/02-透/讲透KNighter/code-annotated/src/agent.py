# =============================================================================
# 【模块定位】KNighter 的 LLM agent 编排层：两阶段管线中所有 LLM 调用点的
#            prompt 组装、知识注入与响应落盘都集中在本模块（纯 prompt 工程，
#            不含任何业务循环——循环编排在 checker_gen.py / checker_refine.py）。
# 【论文映射】KNighter: Transforming Static Analysis with LLM-Synthesized
#            Checkers（arXiv:2503.09002, SOSP'25）。本模块函数与论文章节一一对应：
#   - patch2pattern()  → §3.1.1 Bug Pattern Analysis（Algorithm 1 Stage 1：
#                         patch diff + 完整函数源码 → targeted bug pattern，
#                         刻意收窄不做泛化）
#   - pattern2plan()   → §3.1.2 Plan Synthesis（Algorithm 1 Stage 2：pattern +
#                         utility 函数签名清单 → 高层实现计划；消融证明该阶段
#                         validity 12 vs 8、语法错误 28 vs 52）。
#                         no_tp_plans/no_fp_plans 参数即精化反馈轮（对应模板
#                         pattern2plan-feedback.md 的变体语义：把失败 plan 注回
#                         prompt，让 LLM 避免重蹈覆辙）
#   - plan2checker()   → §3.1.3 Implementation（Algorithm 1 Stage 3：pattern +
#                         plan + 预定义 checker 模板 + utility 清单 → checker.cpp）
#   - repair_syntax()  → §3.1.3 Syntax Repair（编译失败依错误信息修复；
#                         调用方 checker_repair.py 共 1+4=5 次编译尝试 = 论文
#                         maxAttempts=5）
#   - check_report()   → §3.2 triage agent（逐报告判 TP/FP，对齐目标 pattern
#                         而非一般代码正确性）
#   - reduce_report()  → §3.2 报告蒸馏（只保留 relevant lines + trace path）
#   - repair_FP()      → §3.2 refinement agent（依 FP 案例修改 checker 逻辑，
#                         如学会 unlikely() 宏是合法空检查）
#   - patch2checker()  → 单步基线（patch 直出 checker，跳过 pattern/plan 中间
#                         表示；checker_gen.py use_multi=False 的消融对照）
#   - label_commit()   → commit 标注 agent（bug 类型/检测难度分级，服务
#                         scripts/collect_commits.py 数据收集，见 §4 数据集构建）
# 【管线角色】上游调用方：checker_gen.py（生成主循环）、checker_repair.py
#            （语法修复循环）、checker_refine.py（triage+refine）、
#            checker_scan.py（triage 模式）、commit_label.py（标注）；
#            下游：model.invoke_llm 统一发出 LLM 请求（默认 O3-mini），
#            checker_example.choose_example 提供 RAG 检索（论文的 118 个官方
#            CSA checker 知识库，ada-002 embedding）。
# 【关键依赖与坑】
#   1) import 即副作用：模块加载时就遍历 prompt_template/examples/ 读入 3 个
#      few-shot 端到端例子（double-free / null-ptr-derefence / uninit，论文
#      §3.3 所述 40 人时打磨资产）——例子目录缺失/损坏会让所有 import 本模块
#      的代码在 import 期直接崩。
#   2) 所有 prompt 与 LLM 响应均落盘 {result_dir}/{id}/prompt_history/{iter}/
#      （审计 + 复现 + 部分函数断点续跑）；label_commit/reduce_report 有响应
#      缓存（文件存在即复用不再调 LLM），其余函数每次真调。
#   3) model.invoke_llm 对超长 prompt（>400000 字符 ≈ 100k tokens）与 API
#      失败返回 None：label_commit/check_report/repair_syntax 做了 SKIP 防护，
#      patch2checker/patch2pattern/pattern2plan/plan2checker/repair_FP 未设防
#      （write_text(None) 会 TypeError，依赖上层 try-except 兜底）。
#   4) 模板占位符约定不统一：多数模板用 {{xxx}}，repair.md 用单括号
#      {checkercode}——str.replace 是字面替换不区分两者，阅读时留意。
# =============================================================================
from pathlib import Path  # Path 对象：定位 prompt 模板目录、拼接落盘路径（绝对路径派生，不依赖 cwd）

from loguru import logger  # 结构化日志库（免配置，替代 stdlib logging）
from pydantic import BaseModel  # 数据模型基类：Example 四元组的类型校验

from checker_example import choose_example  # RAG 检索：按 ada-002 embedding 余弦相似度从 checker_database 挑最相似的 3 个例子（论文 RAG 知识库通道）
from global_config import global_config  # 全局单例配置：result_dir（结果根目录）等运行参数
from model import invoke_llm  # 统一 LLM 客户端入口：按 model_config 分发到 OpenAI/Anthropic/Google/DeepSeek 等 provider
from tools import error_formatting, grab_error_message  # 编译错误抓取（正则）与 markdown 格式化，专供 repair_syntax 用

# prompt_template/ 目录：本模块所有 .md 模板与知识文件的根。
# __file__=src/agent.py → parent=src → parent.parent=仓库根，拼出绝对路径。
prompt_template_dir = Path(__file__).parent.parent / "prompt_template"
example_dir = prompt_template_dir / "examples"  # few-shot 例子目录（每个子目录=一个端到端例子）
default_checker_examples = []  # few-shot 例子列表，模块加载时由下方 for 循环填充（import 副作用）

# 三份领域知识（论文 §3.1.2/§3.1.3 注入 prompt 的静态知识，模块加载时一次性读入）：
UTILITY_FUNCTION = (prompt_template_dir / "knowledge" / "utility.md").read_text()  # 9 个 utility 函数签名清单（如 getMemRegionFromExpr，实现于 llvm_utils/utility.{h,cpp}，LLM 可直接在 plan/checker 中调用）
SUGGESTIONS = (prompt_template_dir / "knowledge" / "suggestions.md").read_text()  # checker 开发最佳实践（NULL 检查、MemRegion vs SymbolRef 选型、generateNonFatalErrorNode 等）
TEMPLATE = (prompt_template_dir / "knowledge" / "template.md").read_text()  # 预定义 checker 代码骨架（含 {{Callback Functions}}/{{Bug Type}} 等待填槽位的 CSA Checker 模板子类框架）


class Example(BaseModel):  # few-shot 例子的数据模型：一个例子=patch→pattern→plan→checker_code 全链四元组
    patch: str  # 输入侧：bug-fix patch 的 markdown 文本
    pattern: str  # 中间表示 1：人工提炼的 bug pattern（§3.1.1 的目标输出格式）
    plan: str  # 中间表示 2：人工撰写的实现计划（§3.1.2 的目标输出格式）
    checker_code: str  # 输出侧：人工验证过的 CSA checker C++ 源码（§3.1.3 的目标输出）

    @staticmethod
    def load_example_from_dir(checker_dir: str):  # 从例子目录（patch.md/pattern.md/plan.md/checker.cpp 四件套）加载一个 Example
        checker_dir = Path(checker_dir)  # 参数标注 str 但调用处实际传 Path，Path() 幂等转换兼容两者
        patch = (checker_dir / "patch.md").read_text()  # 读 patch 文本
        pattern = (checker_dir / "pattern.md").read_text()  # 读 pattern 文本
        plan = (checker_dir / "plan.md").read_text()  # 读 plan 文本
        checker_code = (checker_dir / "checker.cpp").read_text()  # 读 checker 源码

        return Example(  # 组装为 pydantic 模型实例（字段类型自动校验）
            patch=patch, pattern=pattern, plan=plan, checker_code=checker_code
        )


# 【import 副作用】遍历 examples/ 下所有子目录，加载全部 few-shot 例子。
# iterdir() 返回文件系统序（不排序、不保证跨平台一致）。
for checker_dir in example_dir.iterdir():
    if not checker_dir.is_dir():  # 跳过非目录项（防脏文件，如 .DS_Store/README）
        continue
    default_checker_examples.append(Example.load_example_from_dir(checker_dir))  # 追加进全局默认例子表


def get_example_text(  # 按"阶段需求"拼装 few-shot 例子的 markdown 文本
    example_list,  # Example 列表（默认 3 例或 RAG 检索的 top-3）
    need_patch: bool = False,  # 是否拼入 patch 段（patch2pattern 阶段需要）
    need_pattern: bool = False,  # 是否拼入 pattern 段
    need_plan: bool = False,  # 是否拼入 plan 段（pattern2plan 阶段需要）
    need_checker: bool = False,  # 是否拼入 checker 代码段（plan2checker/patch2checker 阶段需要）
):
    # （原函数无 docstring，为保 AST 等价不加，说明置此）
    # 职责：把 Example 列表渲染成 "## Example N" 分节的 few-shot 文本。
    # 阶段适配原则：每个 agent 只看它那个阶段需要的例子成分——
    # patch2pattern 只给 patch+pattern（还没到 plan 阶段）；
    # pattern2plan 给 pattern+plan；plan2checker 给 pattern+plan+checker 全链。
    # 这样 few-shot 演示的输入输出映射与该 agent 的任务一一对应。
    # 返回：拼好的 few-shot markdown 文本（空列表时返回 ""）。
    example_text = ""
    for i, example in enumerate(example_list):  # 逐例子编号拼接
        example_text += f"## Example {i+1}\n"  # 例子的 markdown 二级标题
        if need_patch:
            example_text += example.patch + "\n\n"  # patch 原文（自身已是 markdown）
        if need_pattern:
            example_text += example.pattern + "\n\n"  # pattern 原文（含 "## Bug Pattern" 结构）
        if need_plan:
            example_text += example.plan + "\n\n"  # plan 原文
        if need_checker:  # checker 代码需包 ```cpp 围栏：
            example_text += "### Checker Code\n```cpp\n"  # 一是示意输出格式，
            example_text += example.checker_code  # 二是与 tools.grab_cpp_code 的
            example_text += "```\n\n"  # 提取正则（```cpp\n...\n```）对齐，保证可自动抽取
    return example_text


# ------------------------- 模板预组装（模块加载期完成）-------------------------
# 静态槽位（utility/suggestions/template/固定例子）在此一次填好；
# 动态槽位（input_patch/input_pattern/input_plan/RAG 例子/失败反馈）留到各
# agent 函数内调用时再填——这样每次 LLM 调用只做少量 replace。

# 【单步基线模板】patch2checker.md：patch 直出完整 checker（消融对照，
# 对应 checker_gen.py use_multi=False 分支）。预注入全部三类知识。
patch2checker_template = (prompt_template_dir / "patch2checker.md").read_text()
patch2pattern_template = (  # ⚠ 变量命名陷阱：此处临时借名 patch2pattern_template
    patch2checker_template.replace("{{utility_functions}}", UTILITY_FUNCTION)  # 装 patch2checker 模板注入
    .replace("{{suggestions}}", SUGGESTIONS)  # 三类知识后的中间结果（命名
    .replace("{{checker_template}}", TEMPLATE)  # 与内容不符，系重构残留）。
)
patch2checker_template = patch2pattern_template.replace(  # 再把中间结果填入固定例子后换回正确名字。
    "{{examples}}",  # 本基线的例子只给 patch+checker 两段
    get_example_text(  # （跳过 pattern/plan——该基线本就没有中间表示）
        default_checker_examples,
        need_patch=True,
        need_pattern=False,
        need_plan=False,
        need_checker=True,
    ),
)

"""Patch to Pattern"""
# ↑ 裸三引号字符串（表达式语句，非注释——AST 里是 Expr/Constant 节点，无任何
#   运行时效果），充当源码分节标题。下面才是真正的 §3.1.1 模板：

# 【§3.1.1 Bug Pattern Analysis 模板】pattern 输出刻意"specific and accurate"——
# 只盯 patch 所示的那类 bug（如 devm_kzalloc 返回值未检查），不做泛化。
patch2pattern_template = (prompt_template_dir / "patch2pattern.md").read_text()  # 重新赋值，覆盖上面的临时借名（故借名无害）
patch2pattern_template = patch2pattern_template.replace(
    "{{examples}}",  # 例子只给 patch→pattern 映射（该阶段任务就是 patch→pattern）
    get_example_text(
        default_checker_examples,
        need_patch=True,
        need_pattern=True,
        need_plan=False,
        need_checker=False,
    ),
)

# 【§3.1.1 泛化变体模板】要求 pattern "general and abstract enough"——能识别
# 代码库其他部位的同类 bug。use_general=True 时启用（论文 Generability 讨论）。
patch2pattern_general_template = (
    prompt_template_dir / "patch2pattern-general.md"
).read_text()
patch2pattern_general_template = patch2pattern_general_template.replace(
    "{{examples}}",  # 例子拼法与 targeted 版相同
    get_example_text(
        default_checker_examples,
        need_patch=True,
        need_pattern=True,
        need_plan=False,
        need_checker=False,
    ),
)

"""Pattern to Plan"""
# ↑ 同上：裸字符串分节标题（合法表达式语句，非注释）。

# 【§3.1.2 Plan Synthesis 模板】只预注入 utility 函数清单（该阶段的核心知识：
# LLM 据此决定 plan 里引用哪些已实现的 CSA 底层封装）。{{examples}} 槽
# 故意留到调用时填——sample_examples=True 时要用 RAG 检索的动态例子集。
pattern2plan_template = (prompt_template_dir / "pattern2plan.md").read_text()
pattern2plan_template = pattern2plan_template.replace(
    "{{utility_functions}}", UTILITY_FUNCTION  # 注入 9 个 utility 函数签名
)

"""Pattern to Plan without utility functions"""
# ↑ 裸字符串分节标题。

# 【§3.1.2 消融模板】pattern2plan-no-utility.md：不注入 utility 清单——
# 论文消融实验用来量化 utility 知识对 plan 质量（进而对 checker validity）的贡献。
pattern2plan_template_no_utility = (
    prompt_template_dir / "pattern2plan-no-utility.md"
).read_text()

"""Plan to Checker"""
# ↑ 裸字符串分节标题。

# 【§3.1.3 Implementation 模板】预注入全部三类知识：utility 清单（可直接调用）
# + suggestions（避坑）+ checker 骨架模板（在其 {{...}} 槽位上填空）。
# {{examples}} 同样留到调用时填（RAG 时动态）。
plan2checker_template = (prompt_template_dir / "plan2checker.md").read_text()
plan2checker_template = (
    plan2checker_template.replace("{{utility_functions}}", UTILITY_FUNCTION)
    .replace("{{suggestions}}", SUGGESTIONS)
    .replace("{{checker_template}}", TEMPLATE)
)

# 【§3.1.3 消融模板】无 utility 版：去掉 utility 清单，但保留 suggestions 与
# checker 骨架（消融只隔离 utility 这一变量）。
plan2checker_template_no_utility = (
    prompt_template_dir / "plan2checker-no-utility.md"
).read_text()
plan2checker_template_no_utility = plan2checker_template_no_utility.replace(
    "{{suggestions}}", SUGGESTIONS
).replace("{{checker_template}}", TEMPLATE)

# 【数据收集模板】commit 标注：是否 bug fix、10 类 bug 分类、CSA 检测难度
# （easy/medium/hard）、pattern 泛化度——服务论文 §4 的 commit 数据集构建
# （每类≥5 条、双人独立标注）。
label_commit_template = (prompt_template_dir / "label_commit.md").read_text()


# =============================================================================
# label_commit —— commit 标注 agent（非论文主线管线，服务数据集收集）
# 职责：把 patch 交给 LLM 判定是否 bug fix 并分类（NPD/整数溢出/越界/...）
# 参数：id=任务标识（结果目录名）；iter=轮次号（prompt_history 子目录）；
#       commit_id=commit 哈希（落盘文件名后缀）；patch=diff 文本
# 返回：LLM 标注文本；LLM 空响应时返回字面量 "SKIP"（调用方据此跳过）
# 特点：唯一有响应缓存的标注入口——response 文件已存在则直接复用不再花钱
# =============================================================================
def label_commit(id: str, iter: int, commit_id, patch: str):
    logger.info("start generating label_commit prompts")  # 记录入口日志
    label_commit_prompt = label_commit_template.replace("{{input_patch}}", patch)  # 唯一动态槽位：填入待标注 patch

    prompt_history_dir = (  # 落盘目录：{result_dir}/{id}/prompt_history/{iter}/
        Path(global_config.result_dir) / id / "prompt_history" / str(iter)
    )
    path2store = prompt_history_dir / f"label_commit-{commit_id}.md"  # prompt 存档名（带 commit_id 便于追溯）
    prompt_history_dir.mkdir(parents=True, exist_ok=True)  # 递归建目录（已存在不报错）

    path2store.write_text(label_commit_prompt)  # prompt 落盘（审计/复现）
    logger.info("finish label_commit generation")

    response_store = prompt_history_dir / f"response_label_commit-{commit_id}.md"  # 响应存档名
    if response_store.exists():  # 【断点续跑】已有响应则直接复用
        logger.info("label_commit already exists")
        response = response_store.read_text()
    else:  # 否则真调 LLM
        response = invoke_llm(label_commit_prompt)

    if response is not None:  # 正常响应：落盘原文
        response_store.write_text(response)
    else:  # 空响应（prompt 超长/API 失败）：写 SKIP 标记，返回 None
        response_store.write_text("SKIP")
    return response


# =============================================================================
# patch2checker —— 单步基线 agent（论文消融对照）
# 职责：跳过 pattern/plan 中间表示，patch 直出完整 checker.cpp（一步到位）。
#       checker_gen.py 的 use_multi=False 分支调用；论文用它对照证明三阶段
#       分解（§3.1.1→§3.1.2→§3.1.3）对 validity 与语法正确率的提升。
# 参数：id/iter 同上；patch=diff 文本
# 返回：LLM 生成的完整响应（含 ```cpp 围栏的 checker，由调用方 extract_checker_code 抽取）
# ⚠ 无响应缓存、无 None 防护：invoke_llm 返回 None 时 write_text(None) 会 TypeError
# =============================================================================
def patch2checker(id: str, iter: int, patch: str):
    logger.info("start generating patch2checker prompts")
    patch2checker_prompt = patch2checker_template.replace("{{input_patch}}", patch)  # 模板已预装三类知识+固定例子，只填 patch 槽

    prompt_history_dir = (  # 落盘目录同上
        Path(global_config.result_dir) / id / "prompt_history" / str(iter)
    )
    path2store = prompt_history_dir / "patch2checker.md"  # 基线每轮只有一份 prompt（无 commit 后缀）
    prompt_history_dir.mkdir(parents=True, exist_ok=True)

    path2store.write_text(patch2checker_prompt)  # prompt 落盘
    logger.info("finish patch2checker generation")

    response = invoke_llm(patch2checker_prompt)  # 真调 LLM（无缓存）
    response_store = prompt_history_dir / "response_checker.md"  # 响应存档（与 plan2checker 同名 response_checker.md——两者不同时混用同一 iter 目录，不冲突）
    response_store.write_text(response)  # ⚠ response=None 时此处 TypeError
    return response


# =============================================================================
# patch2pattern —— 论文 §3.1.1 Bug Pattern Analysis agent（Algorithm 1 Stage 1）
# 职责：从 bug-fix patch 中提炼 targeted bug pattern（bug 的根因模式——具有该
#       模式的程序大概率有同类 bug）。输出 "## Bug Pattern" 格式文本，作为
#       下一阶段 pattern2plan 的输入。
# 参数：id/iter 同上；patch_info=patch diff（含 tree-sitter 提取的完整函数源码，
#       由上游 checker_gen.py 组装）；use_general=True 切换泛化模板
#       （pattern 更抽象，可识别代码库其他部位同类 bug）
# 返回：LLM 响应全文（pattern 描述）
# ⚠ 无响应缓存、无 None 防护
# =============================================================================
def patch2pattern(id: str, iter: int, patch_info: str, use_general=False):
    logger.info("start generating patch2pattern prompts")
    if use_general:  # 泛化模式：warning 级日志显式提示（实验路径）
        logger.warning("Use general template for patch2pattern")
        template = patch2pattern_general_template
    else:  # 默认：targeted 模式（论文主线，pattern 收窄以保证 checker 可实现）
        template = patch2pattern_template

    patch2pattern_prompt = template.replace("{{input_patch}}", patch_info)  # 例子已在预组装期填好，只填目标 patch 槽

    prompt_history_dir = (
        Path(global_config.result_dir) / id / "prompt_history" / str(iter)
    )
    path2store = prompt_history_dir / "patch2pattern.md"  # prompt 落盘名
    prompt_history_dir.mkdir(parents=True, exist_ok=True)

    path2store.write_text(patch2pattern_prompt)
    logger.info("finish patch2pattern generation")

    response = invoke_llm(patch2pattern_prompt)  # 真调 LLM（无缓存）
    response_store = prompt_history_dir / "response_patch2pattern.md"

    response_store.write_text(response)  # ⚠ response=None 时 TypeError
    return response


# =============================================================================
# pattern2plan —— 论文 §3.1.2 Plan Synthesis agent（Algorithm 1 Stage 2）
# 职责：依 bug pattern 制定高层实现计划——选哪些 CSA 回调（checkPostCall/
#       checkBranchCondition/checkBind...）、是否自定义 ProgramState
#       （REGISTER_MAP_WITH_PROGRAMSTATE 等）、每步如何实现。plan 是 §3.1.3
#       写 checker 的施工图；论文消融：有 plan 时 validity 12 vs 8、语法错误
#       28 vs 52。
# 参数：id/iter 同上；pattern=上一阶段输出；patch=原 diff（辅助理解 pattern）；
#       no_tp_plans=历史失败 plan（检测不到 buggy 模式→漏报型）；
#       no_fp_plans=历史失败 plan（把 non-buggy/patched 代码标成 bug→误报型）；
#       no_utility=True 用消融模板（不注入 utility 清单）；
#       sample_examples=True 用 RAG 检索例子替代固定 3 例
#       （choose_example 按 pattern embedding 余弦相似度取 top-3，即论文的
#        checker_database 知识库通道）
# 返回：LLM 响应全文（plan 描述）
# 【精化反馈轮】no_tp_plans/no_fp_plans 注入 {{failed_plan_examples}} 槽
#       （pattern2plan.md 预留位；配套变体 pattern2plan-feedback.md 的指令为
#       "refer to the failed plans first to avoid repeating the same mistakes"：
#       漏报型→放宽匹配，误报型→收紧判定）。主调用方 checker_gen.py 当前
#       不传这两个参数，主路径反馈恒为空串——该通道为迭代重试/实验预留。
# ⚠ docstring 中 no_fp_plans 的描述 "can label the non-buggy pattern correctly"
#       与其注入意图（错误标注 non-buggy 的失败 plan）字面相反，系原注释笔误
# ⚠ 无响应缓存、无 None 防护
# =============================================================================
def pattern2plan(
    id: str,
    iter: int,
    pattern: str,
    patch: str,
    no_tp_plans=None,
    no_fp_plans=None,
    no_utility=False,
    sample_examples=False,
):
    """Generate plan based on the given pattern and patch.

    Args:
        id (str): The id of the current task.
        iter (int): The iteration number.
        pattern (str): The pattern of the bug.
        patch (str): The patch of the bug.
        no_tp_plans (list, optional): Plans that cannot detect the buggy pattern. Defaults to None.
        no_fp_plans (list, optional): Plans that can label the non-buggy pattern correctly. Defaults to None.
        no_utility (bool, optional): Whether to use utility functions. Defaults to False.
        sample_examples (bool, optional): Whether to sample examples. Defaults to False.
    """
    logger.info("start generating pattern2plan prompts")
    if no_utility:  # 消融路径：不注入 utility 清单（warning 显式提示）
        logger.warning("No utility functions are used in pattern2plan")
        template = pattern2plan_template_no_utility
    else:  # 主路径：带 utility 清单的模板
        template = pattern2plan_template

    if sample_examples:  # RAG 路径：按 pattern 语义检索最相似的历史 checker 例子
        logger.warning("Sample examples for pattern2plan")
        example_list = choose_example(pattern, "pattern")  # 用 pattern 文本的 embedding 检索（type="pattern" 对 pattern_embedding.pt 比相似度）
    else:  # 默认：固定 3 个人工例子
        example_list = default_checker_examples

    example_text = get_example_text(  # 例子只给 pattern→plan 映射（阶段适配）
        example_list,
        need_patch=False,
        need_pattern=True,
        need_plan=True,
        need_checker=False,
    )
    pattern2plan_prompt = (  # 三连填槽：pattern 本体 + 原始 patch（理解语境）+ 例子
        template.replace("{{input_pattern}}", pattern)
        .replace("{{input_patch}}", patch)
        .replace("{{examples}}", example_text)
    )

    # ---- 失败 plan 反馈段拼装（精化反馈轮，见函数头注释） ----
    feedback_plan_text = ""
    if no_tp_plans:  # 漏报型失败 plan：buggy 代码上没报警
        no_tp_plan_text = "# Plans that cannot detect the buggy pattern\n"
        # The last three plans if there are more than 3 failed plans
        if len(no_tp_plans) > 3:  # 只保留最近 3 个失败 plan（[-3:] 截尾），防 prompt 无限膨胀
            no_tp_plans = no_tp_plans[-3:]

        for i, plan in enumerate(no_tp_plans):  # 逐个渲染为 "## Failed Plan N" 分节
            no_tp_plan_text += f"## Failed Plan {i+1}\n"
            no_tp_plan_text += plan + "\n\n"
        feedback_plan_text += no_tp_plan_text
    if no_fp_plans:  # 误报型失败 plan：patched（non-buggy）代码上仍报警
        no_fp_plan_text = "# Plans that can label the non-buggy pattern correctly\n"
        # ⚠ 上行标题字面义（"能正确标注"）与注入意图（错误标注、需收紧）相反，
        #   与 docstring 同源笔误；语义以 pattern2plan-feedback.md 指令为准

        if len(no_fp_plans) > 3:  # 同样截尾最近 3 个
            no_fp_plans = no_fp_plans[-3:]

        for i, plan in enumerate(no_fp_plans):
            no_fp_plan_text += f"## Failed Plan {i+1}\n"
            no_fp_plan_text += plan + "\n\n"
        feedback_plan_text += no_fp_plan_text

    pattern2plan_prompt = pattern2plan_prompt.replace(  # 把反馈段（无失败 plan 时为空串）填入预留槽
        "{{failed_plan_examples}}", feedback_plan_text
    )

    prompt_history_dir = (  # 落盘三件套：目录/prompt/响应（同前述模式）
        Path(global_config.result_dir) / id / "prompt_history" / str(iter)
    )
    path2store = prompt_history_dir / "pattern2plan.md"
    prompt_history_dir.mkdir(parents=True, exist_ok=True)

    path2store.write_text(pattern2plan_prompt)
    logger.info("finish pattern2plan generation")

    response = invoke_llm(pattern2plan_prompt)  # 真调 LLM（无缓存）
    response_store = prompt_history_dir / "response_plan.md"

    response_store.write_text(response)  # ⚠ response=None 时 TypeError
    return response


# =============================================================================
# plan2checker —— 论文 §3.1.3 Implementation agent（Algorithm 1 Stage 3）
# 职责：依 pattern + plan 生成可编译的 CSA checker.cpp——在预定义 Checker 骨架
#       模板的 {{...}} 槽位上填空（回调注册、BugType、报警构造），可调用 utility
#       函数。输出由调用方 tools.extract_checker_code 从 ```cpp 围栏中抽取，
#       随后进入 Syntax Repair 循环（repair_syntax）与差分验证（§3.1.4）。
# 参数：id/iter 同上；pattern=§3.1.1 输出；refined_plan=§3.1.2 输出的 plan
#       （参数名 refined_plan 暗示可传入精化后的 plan，当前主链直接透传 plan）；
#       patch=原 diff；no_utility/sample_examples 语义同 pattern2plan
#       （sample_examples 时用 plan embedding 检索例子——choose_example 的
#        type="plan" 分支）
# 返回：LLM 响应全文（含 ```cpp 围栏的完整 checker 源码）
# ⚠ 无响应缓存、无 None 防护
# =============================================================================
def plan2checker(
    id: str,
    iter: int,
    pattern: str,
    refined_plan: str,
    patch: str,
    no_utility=False,
    sample_examples=False,
):
    logger.info("start generating plan2checker prompts")
    if no_utility:  # 消融路径：无 utility 清单（suggestions/template 仍保留）
        logger.warning("No utility functions are used in plan2checker")
        template = plan2checker_template_no_utility
    else:  # 主路径：全知识模板（utility+suggestions+checker 骨架）
        template = plan2checker_template

    if sample_examples:  # RAG 路径：用 plan（而非 pattern）的 embedding 检索
        logger.warning("Sample examples for plan2checker")
        example_list = choose_example(refined_plan, "plan")  # type="plan" 对 plan_embedding.pt 比相似度
    else:
        example_list = default_checker_examples

    example_text = get_example_text(  # 实现阶段例子给全链：pattern+plan+checker
        example_list,  # （few-shot 演示"从 pattern/plan 到可编译 checker"的完整映射）
        need_patch=False,
        need_pattern=True,
        need_plan=True,
        need_checker=True,
    )

    plan2checker_prompt = (  # 四连填槽：pattern + plan + patch + 例子
        template.replace("{{input_pattern}}", pattern)
        .replace("{{input_plan}}", refined_plan)
        .replace("{{input_patch}}", patch)
        .replace("{{examples}}", example_text)
    )

    prompt_history_dir = (
        Path(global_config.result_dir) / id / "prompt_history" / str(iter)
    )
    path2store = prompt_history_dir / "plan2checker.md"
    prompt_history_dir.mkdir(parents=True, exist_ok=True)

    path2store.write_text(plan2checker_prompt)
    logger.info("finish plan2checker generation")

    response = invoke_llm(plan2checker_prompt)  # 真调 LLM（无缓存）
    response_store = prompt_history_dir / "response_checker.md"

    response_store.write_text(response)  # ⚠ response=None 时 TypeError
    return response


# =============================================================================
# check_report —— 论文 §3.2 triage agent
# 职责：判定单份 CSA 扫描报告是 TP 还是 FP。判定基准是"对齐目标 bug pattern"
#       而非一般代码正确性——报告与 pattern 不符（或非真 bug）即 FP
#       （check_report.md 模板要求 LLM 做根因比对、数值/空指针可行性推演）。
#       论文战果：triage agent 79 报告 7TP/22FP/50TN/0FN（0 漏判）。
# 参数：id/iter 同上；report_id=报告标识（落盘名后缀）；report_md=报告正文；
#       pattern=目标 bug pattern（strip("```") 剥掉 LLM 输出残留的 markdown
#       围栏再入 prompt）；patch=原 diff（判 FP 的参照之一）
# 返回：LLM 判定文本（含 "NotABug" 关键字即 FP——调用方 checker_refine.py
#       以 `if "NotABug" in check_res` 计数）；空响应返回 "SKIP due to empty response"
# 特点：temperature=0.01 显式压低（判定任务要确定性；生成类任务才用默认温度）
# 调用方：checker_refine._triage_reports（精化轮逐报告 triage）、
#       checker_scan.py（triage 模式批量判报告）
# ⚠ 无响应缓存（每次真调）；每次调用现读模板文件（其他 agent 用预组装常量）
# =============================================================================
def check_report(id: str, iter: int, report_id, report_md, pattern: str, patch: str):
    logger.info("start generating check_report prompts")
    check_report = (prompt_template_dir / "check_report.md").read_text()  # 每次现读模板（未预组装，也无需填静态知识）
    check_report_prompt = check_report.replace("{{input_bug_report}}", report_md)  # 槽 1：待判报告正文
    check_report_prompt = check_report_prompt.replace(
        "{{input_bug_pattern}}", pattern.strip("```")  # 槽 2：目标 pattern（剥 ``` 围栏——patch2pattern 的 LLM 输出常带围栏）
    )
    check_report_prompt = check_report_prompt.replace("{{input_patch}}", patch)  # 槽 3：修复 patch（TP 的最终参照：报告案例应能被类似 fix 修复）

    prompt_history_dir = (
        Path(global_config.result_dir) / id / "prompt_history" / str(iter)
    )
    path2store = prompt_history_dir / f"check_report-{report_id}.md"  # 每份报告独立存档
    prompt_history_dir.mkdir(parents=True, exist_ok=True)

    path2store.write_text(check_report_prompt)
    logger.info("finish check_report generation")

    response = invoke_llm(check_report_prompt, temperature=0.01)  # 低温判定：最大化可复现性
    response_store = prompt_history_dir / f"response_check_report-{report_id}.md"

    if response is not None:  # 正常：落盘判定原文
        response_store.write_text(response)
    else:  # 空响应兜底：logger.error(None) 无信息量（原样保留），返回哨兵串
        logger.error(response)
        response = "SKIP due to empty response"  # 哨兵：不含 "NotABug"，调用方会计入 TP 侧（保守）
        response_store.write_text("SKIP")  # 盘上只写短标记

    return response


# =============================================================================
# reduce_report —— 论文 §3.2 报告蒸馏 agent
# 职责：把冗长的 CSA bug 报告压缩为"可复现/可验证的最小内核"——保留全部
#       trace messages（| | N| 行）及其所在函数的完整函数体、相关数据结构
#       定义（reduce_report.md 模板），即论文所述"只留 relevant lines +
#       trace path"。蒸馏后的报告用于 triage/refine 阶段控制上下文长度。
# 参数：id/iter 同上；report_id=报告标识；report_md=原始报告
# 返回：蒸馏后的报告文本；命中缓存时直接读盘返回（未命中且 LLM 空响应时
#       不落盘、隐式返回 None）
# 特点：响应缓存（幂等，断点续跑不重复蒸馏）
# ⚠ 坑 1：模板用相对路径 Path("prompt_template/...")（本模块唯一一处），
#         依赖进程 cwd=仓库根，从其他目录运行会 FileNotFoundError
# ⚠ 坑 2：src/scripts 中已无调用方（孤儿入口，供离线分析/历史流程复用）
# =============================================================================
def reduce_report(id: str, iter: int, report_id, report_md):
    logger.info("start generating reduce_report prompts")
    prompt_history_dir = (  # 先定位响应存档：缓存检查前置（命中则连模板都不读）
        Path(global_config.result_dir) / id / "prompt_history" / str(iter)
    )
    response_store = prompt_history_dir / f"response_reduce_report-{report_id}.md"
    if response_store.exists():  # 【断点续跑】已蒸馏过：直接复用
        logger.info("reduce_report already exists")
        return response_store.read_text()

    reduce_report = Path("prompt_template/reduce_report.md").read_text()  # ⚠ 相对路径（见函数头注释坑 1）
    reduce_report_prompt = reduce_report.replace("{{input_bug_report}}", report_md)  # 唯一动态槽：原始报告

    path2store = prompt_history_dir / f"reduce_report-{report_id}.md"
    prompt_history_dir.mkdir(parents=True, exist_ok=True)

    path2store.write_text(reduce_report_prompt)
    logger.info("finish reduce_report generation")

    response = invoke_llm(reduce_report_prompt, temperature=0.01)  # 低温：蒸馏是抽取任务，不要创造性

    if response is not None:  # 有响应才落盘（None 时不写、函数返回 None）
        response_store.write_text(response)
    return response


# =============================================================================
# repair_FP —— 论文 §3.2 refinement agent
# 职责：针对一个已 triage 为 FP 的报告修改 checker 逻辑（如学会 unlikely()
#       宏是合法空检查），要求消除该 FP 的同时仍能检测目标 bug（repair_FP.md：
#       "the repaired checker needs to still detect the target buggy code"）。
#       修改后的 checker 由 checker_refine.py 做双准则接受：①原 FP 案例不再
#       报警 ②buggy/patched 差分验证（§3.1.4）仍通过；最多 3 轮 refine。
# 参数：id/iter 同上；commit_id=来源 commit（落盘名后缀）；pattern=目标 bug
#       pattern（strip 围栏）；report=被判定 FP 的报告正文；checker_code=当前
#       checker 源码；analysis=triage agent 的判定分析文本（repair_FP 依此理解
#       FP 根因）；patch=原 diff
# 返回：LLM 响应全文（含修复后的完整 checker，调用方抽取后重编译重扫）
# ⚠ 无响应缓存、无 None 防护
# =============================================================================
def repair_FP(
    id: str,
    iter: int,
    commit_id: str,
    pattern: str,
    report,
    checker_code,
    analysis,
    patch,
):
    logger.info("start generating repair_FP prompts")
    repair_FP = (prompt_template_dir / "repair_FP.md").read_text()  # 每次现读模板
    repair_FP_prompt = repair_FP.replace("{{input_checker}}", checker_code)  # 槽 1：当前 checker 源码（待修改对象）
    repair_FP_prompt = repair_FP_prompt.replace(
        "{{input_bug_pattern}}", pattern.strip("```")  # 槽 2：目标 pattern（剥围栏，保检测能力的锚）
    )
    repair_FP_prompt = repair_FP_prompt.replace("{{input_bug_report}}", report)  # 槽 3：FP 报告（要消除的对象）
    repair_FP_prompt = repair_FP_prompt.replace("{{input_analysis}}", analysis)  # 槽 4：triage 分析（FP 根因解释）
    repair_FP_prompt = repair_FP_prompt.replace("{{input_patch}}", patch)  # 槽 5：原 diff（TP 语义参照）

    repair_FP_prompt = repair_FP_prompt.replace(  # 槽 6：utility 清单（改 checker 时可调用的现成封装）
        "{{utility_functions}}", UTILITY_FUNCTION
    )

    prompt_history_dir = (
        Path(global_config.result_dir) / id / "prompt_history" / str(iter)
    )
    path2store = prompt_history_dir / f"repair_FP-{commit_id}.md"  # 按 commit 区分存档
    prompt_history_dir.mkdir(parents=True, exist_ok=True)

    path2store.write_text(repair_FP_prompt)
    logger.info("finish repair_FP generation")

    response = invoke_llm(repair_FP_prompt)  # 真调 LLM（无缓存）
    response_store = prompt_history_dir / f"response_repair_FP-{commit_id}.md"

    response_store.write_text(response)  # ⚠ response=None 时 TypeError
    return response


# =============================================================================
# repair_syntax —— 论文 §3.1.3 Syntax Repair agent
# 职责：checker 编译失败时，把编译错误信息连同 checker 源码交给 LLM 修复
#       （修 API 误用/参数类型/缺头文件等，repair.md 模板内置两类 BugReport
#       构造签名约束与两个修复示例）。由 checker_repair.py 的 repair_checker
#       循环驱动：MAX_REPAIR_ATTEMPTS=4，循环 1..5 = 1 次初始编译 + 4 次修复
#       重编译，合计 5 次编译尝试 = 论文 maxAttempts=5。
# 参数：id=任务标识；iter=修复轮名（如 "syntax-repair-00"，作 prompt_history
#       子目录）；times=当前修复序号（落盘名后缀，如 repair_syntax-1.md）；
#       checker_code=编译失败的 checker 源码；error_content=编译 stderr 原文
# 返回：LLM 响应全文（含修复后的完整 checker；空响应返回 "SKIP"——
#       调用方 extract_checker_code 抽不出代码会 continue 到下一轮）
# 错误处理管线：grab_error_message 用正则 r"error:.*\n\s*\d+\s*\|\s+.*\n"
#       抓"错误消息行+`行号| 源码行`"两行一组；error_formatting 转成
#       "- Error Line / - Error Messages" markdown 列表——与 repair.md
#       Example 节格式对齐，教 LLM 按此格式理解错误。
# ⚠ 占位符为单括号 {checkercode}/{errors}（repair.md 模板约定，非 {{}}）
# =============================================================================
def repair_syntax(id: str, iter: int, times, checker_code, error_content):
    logger.info("start generating repair_syntax prompts")
    template = (prompt_template_dir / "repair.md").read_text()  # 每次现读模板

    error_list = grab_error_message(error_content)  # 从 stderr 抓结构化错误对（错误消息+定位行）
    error_list_md = error_formatting(error_list)  # 转 markdown 列表（与模板 Example 对齐）
    prompt = template.replace("{checkercode}", checker_code).replace(  # 单括号占位符：填 checker 源码
        "{errors}", error_list_md  # 与格式化错误列表
    )

    prompt_history_dir = (
        Path(global_config.result_dir) / id / "prompt_history" / str(iter)
    )
    path2store = prompt_history_dir / f"repair_syntax-{times}.md"  # 按修复序号区分存档
    prompt_history_dir.mkdir(parents=True, exist_ok=True)

    path2store.write_text(prompt)
    logger.info("finish repair_syntax generation")

    response = invoke_llm(prompt)  # 真调 LLM（无缓存）
    if response is None:  # 空响应兜底：返回哨兵 "SKIP"（可落盘不炸）
        logger.error("Empty response")
        response = "SKIP"

    response_store = prompt_history_dir / f"response_repair_syntax-{times}.md"
    response_store.write_text(response)
    return response
