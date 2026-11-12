# ============================================================================
# 【模块定位】归集工具：从阶段一 Checker Synthesis 的结果目录里，把所有 valid
#   checker（差分验证通过的合成 checker）连同其 pattern/plan/patch 附件，按
#   commit 汇总复制到统一的输出目录，供阶段二 Refinement、人工分析与论文统计
#   （61 patch -> 39 valid）直接取用。
#
# 【论文映射】§3.1.4 Validation 之后的资产归集步骤：valid 判据即本脚本第 31 行
#   的 TP > 0 and TN > 0（等价于论文的 N_buggy > 0 且 patched 侧不误报，由
#   src/backends/csa.py 的 validate_checker 差分验证产出三元组排名）。
#
# 【管线角色】上游 = src/checker_gen.py（每个 commit 落盘 commit_id.txt /
#   ranking.txt / checkers/*.cpp / intermediate-* 中间产物）；下游 = §3.2
#   Refinement 与人工评估。
#
# 【关键依赖与坑】① ranking.txt 是 str([(checker_id, TP, TN), ...]) 字面量，
#   这里直接 eval() 还原（自产数据，非安全输入场景）。② 大坑：本脚本读取的目录
#   布局是旧版 checker_gen 的命名——checkers/checker{N}.cpp、
#   intermediate-{N}/{pattern,refined_plan}.txt、patchfile.md；现行 checker_gen.py
#   已改为 generation/checker_{NN}/01_pattern.txt、03_refined_plan.txt、
#   checkers/checker_{NN}.cpp（下划线+两位补零）与 patch.md。对现行管线输出直接
#   跑会 FileNotFoundError，需先用旧结果目录或自行适配路径。③ 同一 commit 可能
#   有多个 valid checker，用递增编号 checker1/checker2... 找空位避免互相覆盖。
# ============================================================================

from pathlib import Path  # 面向对象的文件系统路径操作

import fire  # Google fire：把函数签名自动转成 CLI（python collect_valid_checkers.py <result_dir> <output_dir>）


# 主函数：遍历结果目录，收集每个 commit 的全部 valid checker 到 output_dir。
# 参数 result_dir=阶段一输出根目录（每 commit 一个子目录）；
#      output_dir=归集目标目录（每 commit 一个子目录，内含 checkerN.cpp 及三份附件）。
def find_valid_checkers(result_dir: str, output_dir: str):
    result_dir = Path(result_dir)  # 转成 Path 对象
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)  # 递归建目标目录（已存在则复用）

    for commit_dir in result_dir.iterdir():  # 遍历结果根下每个条目（一 commit 一目录）
        if not commit_dir.is_dir():  # 跳过散落的文件（如日志/汇总文件）
            continue
        if "label-commit" in commit_dir.name:  # 跳过 src/commit_label.py 产生的 label-commits 标注工作目录——那是数据标注产物，不是 checker 合成结果
            continue
        try:
            commit_id = (commit_dir / "commit_id.txt").read_text().strip()  # 首选：checker_gen.py 落盘的 commit id 文件
        except FileNotFoundError:
            commit_id = commit_dir.name.split("-")[-1]  # 兜底：目录名最后一段（目录名形如 <type>-<sha12>，取 sha12 当 commit id）

        if (output_dir / commit_id).exists():  # 幂等/断点续跑：该 commit 已归集过则跳过
            print(f"Already processed {commit_id}, skipping.")
            continue

        ranking_file = commit_dir / "ranking.txt"  # 差分验证排名文件：[(checker_id, TP, TN), ...] 按 (TP,TN) 降序
        if not ranking_file.exists():  # 没有排名文件=该 commit 尚未跑完 Validation -> 跳过
            continue
        ranking_list = eval(ranking_file.read_text())  # 把 Python 字面量字符串还原为元组列表

        for checker, TP, TN in ranking_list:  # 逐个合成尝试：checker=序号，TP=buggy 侧报出 bug 的对象数，TN=patched 侧干净度得分
            if TP > 0 and TN > 0:  # 论文 §3.1.4 的 valid 判据（差分验证通过=能抓到原 bug 且修复后不误报）
                checker_file = commit_dir / "checkers" / f"checker{checker}.cpp"  # 该 checker 的源码（旧版命名，现行是 checker_{N:02d}.cpp）
                checker_code = checker_file.read_text()
                checker_code = f"// {checker_file}\n" + checker_code  # 首行插 C++ 注释记录原始路径——归档后仍可溯源到源结果目录

                commit_output_dir = output_dir / commit_id  # 该 commit 的归集子目录
                commit_output_dir.mkdir(parents=True, exist_ok=True)

                # Find an ID for the checker
                checker_id = 1  # 从 1 起找空位编号：同一 commit 可能有多个 valid checker，避免覆盖
                while (commit_output_dir / f"checker{checker_id}.cpp").exists():
                    checker_id += 1

                output_file = commit_output_dir / f"checker{checker_id}.cpp"
                output_file.write_text(checker_code)  # 写出带溯源头的 checker 源码

                plan_file = commit_dir / f"intermediate-{checker}" / "refined_plan.txt"  # §3.1.2 Plan Synthesis 产物（经精修的 plan；旧版路径）
                (commit_output_dir / f"checker{checker_id}-plan.txt").write_text(
                    plan_file.read_text()  # plan 与 checker 同号归档，便于对照"计划->实现"
                )

                pattern_file = commit_dir / f"intermediate-{checker}" / "pattern.txt"  # §3.1.1 Bug Pattern Analysis 产物（targeted bug pattern；旧版路径）
                (commit_output_dir / f"checker{checker_id}-pattern.txt").write_text(
                    pattern_file.read_text()  # pattern 同号归档——这是"LLM 从 patch 学到的 bug 模式"的第一手文本
                )

                patch_file = commit_dir / "patchfile.md"  # 输入的 bug-fix patch 原文（旧版命名，现行 checker_gen 写 patch.md）
                (commit_output_dir / f"patch.md").write_text(patch_file.read_text())  # 统一改名 patch.md 归档


if __name__ == "__main__":
    fire.Fire(find_valid_checkers)  # CLI 入口：python3 collect_valid_checkers.py /path/to/synthesized_checkers /path/to/output_dir
