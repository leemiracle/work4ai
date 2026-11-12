# =============================================================================
# 【模块定位】内核扫描命令构造器：拼装"scan-build 跑 CSA + 加载合成 checker
#              plugin"的 shell 命令前缀（Linux 内核目标专用）。
# 【论文映射】对应论文 §3.1.4 Validation（buggy/patched 差分验证）与 §3.2
#   全库扫描的执行机制——CSA 经 scan-build 包裹内核构建系统（make/clang）
#   对每个翻译单元做路径敏感符号执行（构建 ExplodedGraph），合成 checker
#   以 plugin 形式注入。本文件把"禁用官方 checker 包 + 限循环展开 + 加载
#   plugin"固化为可复用的命令模板。
# 【管线角色】上游：src/checker_scan.py 的 scan_batch_checkers（唯一调用
#   方，import generate_command）；下游：LLVM 构建目录里的 scan-build 与
#   lib/*Plugin.so。注意新主路径已迁至 backends/csa.py 的
#   ClangBackend._generate_command（自带按 target 分的 _default_args），
#   本文件是早期/轻量路径的遗留实现；generate_command_file 与
#   generate_command_obj 目前全仓无调用方。
# 【依赖与坑】①plugin 库名与 checker 注册名的约定：<名>Plugin.so ↔
#   custom.<名>Checker（SAGen=Static Analysis GENeration，合成 checker 的
#   默认占位名）；②generate_command_obj 标注 -> str 却没有 return 语句，
#   实际返回 None（遗留半成品，见函数内注释）。
# =============================================================================
# CSA scan-build 全局参数表：(参数名, 参数值) 二元组序列。
# 设计动机：只让"合成出来的 custom checker"报警——
args = [
    # 禁用 CSA 内置 checker 包（core/cplusplus/deadcode/unix/nullability/
    # security 全关）：避免官方 checker 的海量既有报告混入 triage 与
    # refinement 流程——论文的报告蒸馏与 FP 判定只针对合成 checker 输出
    ("-disable-checker", "core"),
    ("-disable-checker", "cplusplus"),
    ("-disable-checker", "deadcode"),
    ("-disable-checker", "unix"),
    ("-disable-checker", "nullability"),
    ("-disable-checker", "security"),
    # 限制符号执行的循环展开轮数为 4：路径敏感分析对循环极敏感（同一循环
    # 体每多展开一轮，ExplodedGraph 节点近似翻倍），4 轮是精度/成本折中
    # （注意值是整数 4 而非字符串）
    ("-maxloop", 4),
    # 报告输出目录（默认值；调用方常用 no_output=True 丢弃后再自行 -o 覆盖）
    ("-o", "tmp/SAGenTestCSAResult"),
]


def generate_command(llvm_build_dir: str, no_output=False, plugin_names=None) -> str:
    # 【职责】拼出 scan-build 命令前缀：PATH 注入 + 指定 clang + 加载一个
    #   或多个合成 checker plugin + 追加全局参数表。
    # 【参数】llvm_build_dir：LLVM 构建目录（bin/scan-build 与
    #   lib/*Plugin.so 都在它下面）；no_output：True 时跳过 -o 参数（输出
    #   目录由调用方接管，如 checker_scan 里另接 "-o <result_dir>/reports"）；
    #   plugin_names：要启用的 plugin 名列表（多 checker 组扫描），None 则
    #   加载默认测试 plugin。
    # 【返回】可直接再拼接 make/clang 目标的命令前缀字符串（末尾留空格）。
    # 命令先注入 PATH：scan-build 递归调用 clang 时能找到全套 LLVM 工具链
    comd = f"PATH={llvm_build_dir}/bin:$PATH "
    # scan-build 包裹编译器做分析；--use-cc=clang 指定分析 C 代码用 Clang
    # （CSA 随 CC 编译器走，内核是 C 代码故不用 --use-c++）
    comd += f"{llvm_build_dir}/bin/scan-build --use-cc=clang "
    if plugin_names:
        # 多 checker 组扫描：每个合成 checker 编译产物是一个独立 plugin 库，
        # -load-plugin 载入库，-enable-checker 用注册名（custom.<名>Checker）
        # 打开其中的 checker
        for plugin_name in plugin_names:
            comd += f"-load-plugin {llvm_build_dir}/lib/{plugin_name}Plugin.so "
            comd += f"-enable-checker custom.{plugin_name}Checker "
    else:
        # 未指定列表 → 默认加载单个测试 plugin（SAGenTestChecker，
        # SAGen=Static Analysis GENeneration 的默认占位名）
        comd += f"-load-plugin {llvm_build_dir}/lib/SAGenTestPlugin.so "
        comd += "-enable-checker custom.SAGenTestChecker "
    # 追加全局参数表（禁 checker 包/maxloop/-o）；no_output=True 时跳过 -o
    for arg_name, arg_value in args:
        if no_output and arg_name == "-o":
            continue
        comd += f"{arg_name} {arg_value} "
    return comd


def generate_command_file(file: str, llvm_build_dir: str) -> str:
    # 【职责】单文件冒烟测试命令：scan-build 包裹下直接 clang 编译一个独立
    #   C 文件（不经内核构建系统），可执行产物 tmp/SAGenTest.out。
    # 【用途】checker 刚编译成 plugin 后的最小可运行验证（比 make 内核对象
    #   轻量得多）；当前全仓无调用方（遗留 helper）。
    # 先取 scan-build 前缀（默认单 plugin SAGenTest）
    comd = generate_command(llvm_build_dir)
    # 直接编译目标文件：被 scan-build 包裹后 CSA 会对该翻译单元跑符号
    # 执行并产出分析报告
    comd += f"clang {file} -o tmp/SAGenTest.out"
    return comd


def generate_command_obj(obj: str, llvm_build_dir: str) -> str:
    # 【职责】单内核对象扫描命令：scan-build 包裹下用 make 构建指定内核
    #   目标文件（如 drivers/xxx/foo.o）——差分验证"只扫 patch 涉及对象"
    #   的命令形态即由此而来。
    # 【参数】obj：make 目标（.o 文件路径）；LLVM=1 让内核构建系统改用
    #   Clang 工具链（CSA 依赖 Clang 前端）；ARCH=x86 固定 x86 架构；
    #   -j32 三十二路并行编译。
    # 【坑】函数标注 -> str 但函数体没有 return 语句——实际返回 None，
    # 遗留半成品；当前全仓无调用方（新路径在 backends/csa.py 的
    # _generate_command/_generate_command_group）。
    comd = generate_command(llvm_build_dir)
    # 用 make 构建单个内核对象（scan-build 会拦截其编译过程做分析）
    comd += f"make LLVM=1 ARCH=x86 {obj} -j32"
