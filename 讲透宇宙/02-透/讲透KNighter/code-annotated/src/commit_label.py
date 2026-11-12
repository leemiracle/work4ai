# =============================================================================
# 【模块定位】论文 §4 commit collection 的调度层：批量给候选 bug-fix commit
#   打标签（是否 bug 修复 / bug 类型 / 检测难度 / 可泛化性 / 是否漏洞），产出
#   commit_labels.csv——阶段一 Checker Synthesis 的"原材料筛矿机"。
#
# 【论文映射】KNighter（arXiv:2503.09002, SOSP'25）§4：61 个人工精选 patch 覆盖
#   10 类 bug（NPD/整数溢出/越界/缓冲区溢出/内存泄漏/UAF/Double-Free/UBI/
#   并发/误用，每类 >=5 条，双人独立标注复核）。本模块承担机器初筛 + LLM
#   精标：两级廉价预筛（merge commit 检测、17 个 bug 关键词）先滤掉明显无关
#   的 commit，再由 agent.label_commit（LLM，prompt_template/label_commit.md）
#   输出结构化五元组标签，人工只复核通过初筛的少量候选。
#
# 【管线角色】
#   上游：scripts/collect_commits.py 收集的候选 commit 清单文件（默认文件名
#     "commits"，每行一个 commit id）。
#   下游：commit_labels.csv 供人工双人标注复核（论文口径）；精选 patch 进入
#     src/checker_gen.py 跑阶段一 Checker Synthesis（patch2pattern 起点）。
#   入口：src/main.py 子命令 label。
#
# 【关键依赖与坑】
#   - global_config.target.get_patch：取 Markdown 格式化 patch（commit message
#     + 受影响函数 + diff，见 targets/factory.py）——非线程安全，git 操作用
#     模块级 threading.Lock（load_patch_lock）串行化。
#   - 坑1：<think> 剥离对应论文多模型消融（GPT-4o/DeepSeek-R1/Gemini-2-flash）：
#     R1 类推理模型会把思考链混进输出，须取 </think> 之后的部分再匹配标签。
#   - 坑2：关键词筛选取 patch 第 2~50 行（跳过 markdown 头两行元信息）且截到
#     "## Buggy Code" 结构化代码段标题之前——只筛 commit 描述文本，防止代码
#     体内恰好出现 "fix" 等词造成假阳性。
#   - 坑3：结果先 set 去重再 sort——同 commit 重复跑只留一行，排序保证输出
#     确定性（diff 友好）。
#   - 坑4：patch.md 落盘即缓存——重跑直接复用，get_patch 不会重复执行；
#     label_commit 的 LLM 响应同样在 prompt_history 有缓存。
# =============================================================================
import concurrent.futures               # ThreadPoolExecutor：多线程并发标注 commit
import re                               # 正则：从 LLM 响应提取 type/difficulty/generability/vulnerability 字段
import threading                        # Lock：串行化非线程安全的 get_patch（git 操作）
from pathlib import Path                # 路径：commit 清单读取、结果目录管理

from agent import label_commit          # LLM 标注 agent（论文 §4）：读 patch 输出结构化五元组标签
from global_config import global_config, logger  # 全局配置单例（result_dir/target）+ loguru 日志

load_patch_lock = threading.Lock()  # 模块级互斥锁：get_patch 内部跑 git 命令非线程安全，须串行


# -----------------------------------------------------------------------------
# label_commits(commit_file="commits", num_workers=5) —— 批量 commit 标注主流程
# 职责：读入候选 commit 清单 -> 线程池并发执行两级预筛 + LLM 精标 ->
#       去重排序 -> 写 result_dir/commit_labels.csv。
# 参数：commit_file —— 候选清单文件（每行一个 commit id，默认文件名 "commits"）；
#       num_workers —— 并发线程数（默认 5）。
# 返回：无（产物 commit_labels.csv：每行
#   "commit_id,是否bug修复,类型,难度,可泛化性,是否漏洞" 或失败/筛除标记）。
# 内层 process_commit(commit_id) 的返回值约定：
#   "{id},failed"（取 patch 失败）/ "{id},Merge-Tag"（merge commit 筛除）/
#   "{id},No-Keywords"（无关键词筛除）/ 正常五元组行。
# 论文语义：§4 十类 bug 池的机器初筛层，最终入库还需双人独立标注。
# -----------------------------------------------------------------------------
def label_commits(commit_file="commits", num_workers=5):
    logger.info(f"Labeling commits with {num_workers} workers")  # 汇报并发规模

    commit_list = Path(commit_file).read_text().splitlines()  # 逐行读入候选 commit id 清单
    result_dir = Path(global_config.get("result_dir"))  # 结果根目录
    result_dir.mkdir(parents=True, exist_ok=True)  # 递归创建（已存在复用）

    def process_commit(commit_id):  # 单个 commit 的标注流水线（线程池 worker 体）
        # Load patch and run label_commit  ← 原注释：取 patch + 跑标注
        logger.info(f"Processing commit {commit_id}")  # 汇报当前 commit

        prompt_history_dir = (  # 该 commit 的留档目录：result_dir/label-commits/prompt_history/{commit_id}/
            Path(result_dir) / "label-commits" / "prompt_history" / str(commit_id)
        )
        patch_file = prompt_history_dir / f"patch.md"  # patch 缓存文件路径
        if patch_file.exists():  # 已缓存（重跑/续跑场景）
            patch = patch_file.read_text()  # 直接读缓存，跳过 git 调用
        else:  # 首次处理
            try:  # get_patch 可能失败（commit 不存在/仓库异常）
                with load_patch_lock:  # 持锁串行执行：git show 非线程安全
                    patch = global_config.target.get_patch(commit_id)  # 取 Markdown 格式化 patch（message+受影响函数+diff）
                prompt_history_dir.mkdir(parents=True, exist_ok=True)  # 建留档目录
                patch_file.write_text(patch)  # patch 落盘即缓存
            except Exception as e:  # 取 patch 失败
                logger.error(f"Error loading patch for commit {commit_id}: {e}")  # 记录异常
                return f"{commit_id},failed"  # 结果行标记 failed

        first_10_lines = patch.splitlines()[:10]  # 预筛1取样：patch 前 10 行（commit message 头部所在）
        first_10_lines = "\n".join(first_10_lines).lower()  # 拼回字符串并统一小写（大小写不敏感匹配）
        if "merge tag" in first_10_lines or "merge branch" in first_10_lines:  # merge commit 判定：两类合并提交标志串
            logger.warning(f"Commit {commit_id} is a merge commit")  # 记录筛除原因
            return f"{commit_id},Merge-Tag"  # 结果行标记 Merge-Tag（merge commit 无单一 bug 语义，直接筛除）

        first_50_lines = patch.splitlines()[2:50]  # 预筛2取样：第 2~49 行（跳过 markdown patch 的头两行元信息，取 commit message 起的正文）
        first_50_lines = "\n".join(first_50_lines).lower()  # 拼回并小写
        first_50_lines = first_50_lines.split("## Buggy Code")[0]  # 截到结构化代码段标题前：只筛描述文本，防止代码体内出现关键词造成假阳性（该标题是 get_patch/examples 格式化 patch 的固定段名）
        keywords = [  # 17 个 bug 修复语义关键词（commit message 常用词表）
            "fix",  # 修复
            "bug",  # 缺陷
            "error",  # 错误
            "issue",  # 问题
            "incorrect",  # 不正确
            "fault",  # 故障
            "flaw",  # 漏洞（口语）
            "defect",  # 缺陷（正式）
            "vulnerability",  # 安全漏洞
            "security",  # 安全
            "avoid",  # 避免（如 "avoid overflow"）
            "prevent",  # 防止
            "resolve",  # 解决
            "repair",  # 修补
            "solve",  # 解决
            "address",  # 处理（如 "address a race"）
            "mitigate",  # 缓解
        ]

        if not any(keyword in first_50_lines for keyword in keywords):  # 一个关键词都不含：几乎不可能是有价值的 bug-fix
            logger.warning(f"Commit {commit_id} does not contain any keywords")  # 记录筛除原因
            return f"{commit_id},No-Keywords"  # 结果行标记 No-Keywords

        result = label_commit("label-commits", commit_id, commit_id, patch)  # 过预筛，调 LLM 标注 agent：实参 = (id, iter, commit_id, patch)，内部填 label_commit.md 模板 {{input_patch}} 并落 prompt_history 缓存

        if not result:  # LLM 返回空（调用失败/被跳过）
            return f"{commit_id},failed"  # 结果行标记 failed

        result = result.lower()  # 统一小写做后续匹配
        if "<think>" in result:  # 推理模型（如 DeepSeek-R1，论文多模型消融之一）输出带思考链
            result = result.split("</think>")[-1]  # 取 </think> 之后的部分（split 取最后段 = 思考链之后的正式答案）
        # Determine whether this is a bug fix and extract details  ← 原注释：判定是否 bug 修复并提取细节
        is_bug_fix = "bug-fix: yes" in result  # 布尔字段：LLM 输出约定含 "bug-fix: yes/no"，子串命中即 True

        type_pattern = re.compile(r"type: ([\w-]+)")  # 提取 bug 类型（\w+连字符，如 null-ptr-derefence/use-after-free，对应论文十类分类）
        if type_pattern.search(result):  # 命中
            bug_type = type_pattern.search(result).group(1)  # 取捕获组
        else:  # 未命中
            bug_type = "unknown"  # 兜底值

        difficulty_pattern = re.compile(r"difficulty: (\w+)")  # 提取 CSA 检测难度（prompt 约定输出 easy/medium/hard）
        if difficulty_pattern.search(result):  # 命中
            difficulty = difficulty_pattern.search(result).group(1)  # 取捕获组
        else:  # 未命中
            difficulty = "unknown"  # 兜底值

        generability_pattern = re.compile(r"generability: (\w+)")  # 提取可泛化性（bug pattern 能否泛化到其他代码路径——影响 checker 复用价值）
        if generability_pattern.search(result):  # 命中
            generability = generability_pattern.search(result).group(1)  # 取捕获组
        else:  # 未命中
            generability = "unknown"  # 兜底值

        vulnerability_pattern = re.compile(r"vulnerability: (\w+)")  # 提取是否安全漏洞（筛 CVE 级候选，论文 30 个 CVE 的源头信号）
        if vulnerability_pattern.search(result):  # 命中
            vulnerability = vulnerability_pattern.search(result).group(1)  # 取捕获组
        else:  # 未命中
            vulnerability = "unknown"  # 兜底值

        return f"{commit_id},{is_bug_fix},{bug_type},{difficulty},{generability},{vulnerability}"  # 拼成 CSV 行：commit,是否bug修复,类型,难度,可泛化性,是否漏洞

    # Use ThreadPoolExecutor to process commits concurrently  ← 原注释：线程池并发处理
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:  # num_workers 个线程
        result_list = list(executor.map(process_commit, commit_list))  # map 保序：输出顺序与输入清单一致（异常在迭代时抛出）

    result_list = list(set(result_list))  # 去重：同 commit 重复出现在清单/重复跑只留一行
    result_list.sort()  # 排序：保证输出确定性（diff 友好、可复现）

    result_file = result_dir / "commit_labels.csv"  # 输出文件：result_dir/commit_labels.csv
    result_file.write_text("\n".join(result_list))  # 逐行落盘（供人工双人标注复核，论文 §4 口径）
