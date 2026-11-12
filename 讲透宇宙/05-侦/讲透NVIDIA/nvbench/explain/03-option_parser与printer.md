# 03 option_parser 巨石与 printer 三连：CLI 入口与结果出口

## 角色定位

这是 nvbench 的"进"与"出"。进：`nvbench/option_parser.cu`（1311 行全仓最大源文件）把命令行翻译成运行配置；出：printer 三连把结果渲染成 Markdown（人读）、CSV（脚本）、JSON（工具链）。二者在 `nvbench/main.cuh` 宏体系里装配成流水线：NVBENCH_MAIN（`nvbench/main.cuh:104`）→ NVBENCH_MAIN_BODY（`nvbench/main.cuh:114`）→ parse（`nvbench/option_parser.cu:457`）→ run → print。仓内**不存在 `main_impl` 函数**——装配点是 8 个可覆写宏 + `nvbench::detail::main_*` 内联函数族（`nvbench/main.cuh:191-261`）。

## 内部结构

**option_parser 巨石**：两级 parse 入口 `nvbench/option_parser.cu:439`（argc/argv）与 `:451`；轴过滤 DSL 最难——`--axis/-a` 处理在 `nvbench/option_parser.cu:642`，`:369` 抛 "Invalid axis value spec"，`:1060` 汇聚轴选项错误，`--help-axes` 在 `:537`，`:1022` 把基准专属参数透传给 benchmark args。文档 `docs/cli_help.md`（233 行）+ `docs/cli_help_axis.md`（69 行）。测试 `testing/option_parser.cu`（1905 行全仓最大测试）覆盖 flag 矩阵、--axes DSL 与未识别参数错误路径。

**printer 家族**：骨架 `nvbench/printer_base.cuh`（266 行 15 个 do_ 钩子+状态计数）；三实现——`nvbench/markdown_printer.cu`（638 行控制台默认输出）、`nvbench/csv_printer.cu`（184 行）、`nvbench/json_printer.cu`（682 行，`nvbench/json_printer.cuh:61` version_t 版本管理）；`nvbench/printer_multiplex.cxx:33-141` 把 15 个钩子逐一扇出到多 printer（md+json 并行落盘）。表格原语共享：`nvbench/internal/table_builder.cuh`（95 行）+ `nvbench/internal/markdown_table.cuh`（163 行列宽自适应）。

## 外部连接

- 上游：`nvbench/main.cu`（24 行）只有一行 NVBENCH_MAIN；独立控制壳 `exec/nvbench-ctl.cu`（48 行）。
- 下游：解析结果喂给 `nvbench::detail::main_run_benchmarks`（`nvbench/main.cuh` 内联），printer 事件由 `nvbench/runner.cxx:84` 等运行期钩子触发；json_printer 产物被 Python 线消费（`python/scripts/nvbench_json/reader.py` 版本校验门面）。
- 宏定制面：`nvbench/main.cuh:49-177` 的 8 个 NVBENCH_MAIN_*_CUSTOM 钩子宏，testing/ 的 custom_main_* 四测试即其用例。

## 数据流

argv → NVBENCH_MAIN → parse：option_parser 扫全局 flag（`:618` `--json`、`:624` `--jsonbin`、`:631` `--benchmark`、`:637` `--devices`、`:642` `--axis`），未知参数在 `nvbench/option_parser.cu:666`/`:682` 直接抛 "Unrecognized command-line argument"（无 did-you-mean 猜测）；轴过滤 DSL 解析成 per-benchmark 输入规约，改写 axes_metadata 活跃输入集（`nvbench/type_axis.cxx:36`）。运行期：main_run_benchmarks 统计 total_states → set_total_state_count → 每 state 完成 add_completed_state（进度行）→ print_benchmark_results。JSON 特殊分支：`nvbench/json_printer.cu:347` 在 m_enable_binary_output（`nvbench/json_printer.cuh:86` 默认 false，CLI `nvbench/option_parser.cu:717` 置位）开启时，把样本写成**小端 float32 二进制 sidecar 文件**（`-bin` metadata `nvbench/json_printer.cu:361`、`-freqs-bin` `:373`）——不是 base64 内嵌（README 勘误#2）。

## 设计决策

1. **巨石单文件而非分布式解析**：1311 行集中全部 flag——flag 间相互作用在一处读全；Google Benchmark 同样选集中式。
2. **printer 用 do_ 钩子 + multiplex 扇出**而非事件总线：15 个钩子是固定接口面，`nvbench/printer_multiplex.cxx:33` 起逐一转发——零注册、零开销，代价是新增输出格式要动基类。
3. **表格渲染下沉 internal/ 共享原语**：markdown 与 csv 都走 table_builder+markdown_table，列宽/对齐只写一遍。
4. **二进制样本走 sidecar 而非 JSON 内嵌**：万级 float 进 JSON 膨胀且解析慢；Python 侧 `python/cuda/bench/results/_benchmark_result.py:229` 按 "<f4" 直读。
5. **main 全宏化**：默认零成本、定制零侵入——下游包一层钩子宏即可接管初始化/异常路径。

## 新人提示

- 加新 flag：parse_impl 链加 else-if + `docs/cli_help.md` 补文档 + `testing/option_parser.cu` 补断言，三处一体；漏文档会被 PR 评审清单（`docs/pr_review.md`）抓。
- 同时拿人读与机读：`--json out.json --markdown` 走 multiplex 扇出，各写各的。
- 大样本分析开 `--jsonbin out.json`（:624，`nvbench/option_parser.cu:723` 要求必须落文件路径），Python results 包才能拿全量样本。
- 读 main 流水线从 `nvbench/main.cuh:114` NVBENCH_MAIN_BODY 展开，别找 main_impl——它不存在（README 勘误#1）。
