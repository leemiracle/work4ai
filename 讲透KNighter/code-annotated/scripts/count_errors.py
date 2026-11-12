# Count the number and types of errors
# Example usage:
# python scripts/count_errors.py --input_file result/input.log --output_file output.csv
# ============================================================================
# 【模块定位】失败模式统计：解析阶段一每个 commit 的验证排名行，把合成 checker
#   的失败模式（编译失败/运行时错/语义错，语义错再细分双报 vs 双漏报）计成 CSV，
#   每个 commit 一行。
#
# 【论文映射】论文 §5 失败模式统计的直接数据来源：273 次失败尝试 = 65 编译错 +
#   1 运行时错 + 207 语义错（其中 34 个双报 buggy+patched、173 个双双漏报）——
#   与本脚本输出的 num_compilation_failures / num_runtime_errors /
#   num_semantic_errors / num_all_bug / num_all_not_bug 五列一一对应。
#   哨兵值语义来自上游：src/checker_gen.py 与 src/backends/csa.py 的
#   validate_checker（差分验证，§3.1.4）。
#
# 【管线角色】上游 = generate 阶段的汇总日志（每行：commit_id bug类型
#   ranking 字面量）；下游 = 论文表格/消融分析。
#
# 【关键依赖与坑】① ranking 哨兵值：TP==-10 表示 checker 编译失败（checker_gen
#   在生成/编译异常或 repair agent 修复 5 次仍失败时写 (i,-10,-10)）；TP==-2
#   表示扫描时 clang 崩溃（csa.py 捕获 "Please consider submitting a bug
#   report" 后返回 (-2,-2)）；TP==-1 表示被扫描的内核对象编译失败（csa.py 返回
#   (-1,-1)）。② 坑：-1 没有单独分桶，会穿过前两个判断落入语义错的
#   num_all_bug 分支（-1 != 0），统计口径上被并进"双报"列。③ eval() 直接还原
#   自产字面量。
# ============================================================================

import fire  # CLI 框架：把 count_errors_from_file(input_file, output_file) 转成 --input_file/--output_file 两个 flag
from pathlib import Path  # 路径对象

# 单行统计：解析一行日志并追加一行 CSV。
# 参数 line：形如 "<commit_id> <bug类型> [(checker_id,TP,TN), ...]" 的日志行；
#      output_file：CSV 输出路径（追加模式，表头由调用方先写好）。
def count_errors(line, output_file):
    commit = line.split()[0]  # 首词 = commit id（12 位短 sha）
    type = line.split()[1]  # 次词 = 该 commit 的 bug 类型（如 Null-Ptr-Deref）
    ranking_text = " ".join(line.split()[2:])  # 其余部分 = ranking.txt 内容的 str 形式（可能含空格，重新拼接）

    ranking_list = eval(ranking_text)  # 还原为 [(checker_id, TP, TN), ...] 元组列表
    any_valid = any([ranking[1] > 0 and ranking[2] > 0 for ranking in ranking_list])  # 该 commit 是否出过 >=1 个 valid checker（TP>0 且 TN>0，§3.1.4 判据）——论文 "61 patch -> 39 valid" 的分子来源

    num_compilation_failures = 0  # 编译失败数（TP==-10：checker 编译不过且 repair 修复失败/生成异常）
    num_runtime_errors = 0  # 运行时错数（TP==-2：CSA 扫描时 clang 自身崩溃）
    num_semantic_errors = 0  # 语义错数（编译通过、能跑、但差分验证不过）
    num_all_bug = 0  # 双报数：buggy 与 patched 两侧都报警（TP>0 但 TN<=0，误报型）
    num_all_not_bug = 0  # 双漏报数：buggy 侧也一个对象都报不出（TP==0，漏报型）
    for ranking in ranking_list:  # 遍历该 commit 的每个合成尝试（最多 checker_nums=10 个）
        if ranking[1] == -10:  # 哨兵 -10：checker 编译失败（含 repair agent 5 次修复仍失败）
            num_compilation_failures += 1
        elif ranking[1] == -2:  # 哨兵 -2：运行时错误（扫描时 clang 崩溃）
            num_runtime_errors += 1
        elif not (ranking[1] > 0 and ranking[2] > 0):  # 其余所有非 valid 的情况 -> 语义错
            num_semantic_errors += 1
            if ranking[1] == 0:  # buggy 侧得分为 0：一个对象都报不出 -> 双双漏报（论文 173 例；这类 checker 在全库扫描时仍可能抓到同类 bug 且 FP 更低）
                num_all_not_bug += 1
            else:  # TP>0 但 TN<=0：buggy+patched 双报（论文 34 例）；注意 TP==-1（内核对象编译失败）也落入此桶，未单列
                num_all_bug += 1

    with open(output_file, 'a') as f:  # 追加一行 CSV：commit,类型,是否有valid,编译失败数,运行时错数,语义错数,双报数,双漏报数
        f.write(f"{commit},{type},{any_valid},{num_compilation_failures},{num_runtime_errors},{num_semantic_errors},{num_all_bug},{num_all_not_bug}\n")


# 文件级入口：写表头 + 逐行调 count_errors。
# 参数 input_file=generate 阶段汇总日志；output_file=输出 CSV 路径。
def count_errors_from_file(input_file, output_file):
    input_file = Path(input_file)
    output_file = Path(output_file)
    output_file.write_text("commit,type,any_valid,num_compilation_failures,num_runtime_errors,num_semantic_errors,num_all_bug,num_all_not_bug\n")  # 先写表头（write_text 覆盖旧文件，重复运行会重置输出）
    for line in input_file.read_text().splitlines():  # 逐行（每行一个 commit 的验证汇总）
        count_errors(line, output_file)

if __name__ == "__main__":
    fire.Fire(count_errors_from_file)  # CLI：python scripts/count_errors.py --input_file result/input.log --output_file output.csv
