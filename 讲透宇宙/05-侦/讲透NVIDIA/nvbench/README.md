# 讲透 nvbench

NVIDIA [nvbench](https://github.com/NVIDIA/nvbench)——GPU 微基准框架：用户写 `void bench(nvbench::state&)` + `NVBENCH_BENCH` 一行注册，框架完成参数空间展开（轴体系）、kernel 启动、冷/热/CPU/CUPTI 四种测量、收敛判停（stdrel/entropy/sample-count）、统计汇总与 Markdown/CSV/JSON 三格式输出；C++ 头文件库 + CLI + Python cuda-bench 包三形态一体。

## 全链状态表

| 阶段 | 状态 | 明细 |
|---|---|---|
| understand 图谱 | ✅ | 649 节点 / 979 边 / 14 层 / 16 步 tour，validator 0 issues（仓内 `.understand-anything/knowledge-graph.json`） |
| fingerprints | ✅ | 348 文件基线 @410dcdd2 |
| onboarding | ✅ | [ONBOARDING.md](onboarding/ONBOARDING.md) 11817 字（不计空格）8 节 86 锚（全路径行号锚终验 0 坏） |
| explain | ✅ | 4 篇六节结构：[01 轴与判据体系](explain/01-轴与判据体系.md) / [02 测量器家族 cold-hot-CUPTI](explain/02-测量器家族cold-hot-CUPTI.md) / [03 option_parser 与 printer](explain/03-option_parser与printer.md) / [04 compare_robust 与 Python 生态](explain/04-compare_robust与Python生态.md) |

（DeepWiki 收录状态见仓内 deepwiki/ 目录；本图谱与讲透产物为源码级知识源。）

## 结构速览

- C++ 核心三明治：轴/类型系统（`nvbench/type_list.cuh` 等）→ 基准对象与状态（`nvbench/state.cuh` 397 行、`nvbench/benchmark_base.cuh` 377 行）→ 测量器四策略（`nvbench/detail/measure_cold.cu` 573 行最大）+ 三判据 + CUPTI/NVPW 双剖析后端
- 出入口：`nvbench/option_parser.cu`（1311 行 CLI 巨石）与 printer 三连（`nvbench/json_printer.cu` 682 / `nvbench/markdown_printer.cu` 638 / `nvbench/csv_printer.cu` 184）+ multiplex 扇出
- Python 线：cuda.bench 装饰器 API（`python/src/py_nvbench.cpp` 1577 行绑定）+ 结果解析 + `python/scripts/nvbench_compare_robust.py`（3591 行稳健比较 CLI）
- 测试：testing/ 37 个 .cu（自研断言 + 每测试独立 main），最大 `testing/option_parser.cu` 1905 行
- CI：CUDA 12.0-12.9 × gcc7-14/llvm14-20 矩阵，40+ devcontainer 变体，L4 GPU runner 跑 wheel 冒烟

## 勘误清单（源码实证，全部行号已核）

1. **`main_impl` 不存在**：NOTES-DIGEST/图谱节点称"外部项目可用 nvbench::main_impl 组装自己的入口"——全仓 grep `main_impl` 零命中。真实机制：`nvbench/main.cuh:104` NVBENCH_MAIN 宏 → `:114` NVBENCH_MAIN_BODY → `:191-261` 的 `nvbench::detail::main_initialize/main_run_benchmarks/main_print_results` 内联函数族 + 8 个 NVBENCH_MAIN_*_CUSTOM 钩子宏。
2. **json 样本旁挂不是 base64**：NOTES batch-20 称"样本数组以 base64/二进制旁挂"——全仓 grep "base64" 零命中。实际（`nvbench/json_printer.cu:361`/`:373`）是 `-bin`/`-freqs-bin` 后缀的**小端 float32 二进制 sidecar 文件**，CLI 入口 `--jsonbin`（`nvbench/option_parser.cu:624`，`:723` 限定必须落文件路径）。
3. **示例是 11 个不是 12 个**：图谱 tour T14 与 L03 描述"12 个示例"——`examples/` 实测 11 个 .cu（auto_throughput/axes/cpu_only/custom_criterion/enums/exec_tag_sync/exec_tag_timer/skip/stream/summaries/throughput）+ 1 个 CMakeLists。
4. **测试框架不是 gtest**：图谱 L14 称"testing/ 44 个 gtest 文件"——nvbench 测试是自研宏体系：`testing/test_asserts.cuh:26` ASSERT、`:40` ASSERT_MSG、`:58` ASSERT_THROWS_ANY，常规测试各自带 `int main()`（如 `testing/state.cu:131`，custom_main_* 四变体走 NVBENCH_MAIN 宏），无 TEST() 宏无 gtest 依赖；44 文件中 37 个 .cu（`testing/CMakeLists.txt:1-35` 注册 35 个目标 + device/noisy_bench + cmake/test_export/test_bench）。
5. **判据注册名带连字符**：第三判据注册名是 `sample-count` 不是 `sample_count`（`nvbench/criterion_manager.cxx:36`），CLI `--criterion` 参数写错名会查表失败。
6. **graph 工艺：.cuh 全盲 + C++ 手扫 519 条**：scan-result.json 实证 scanner 对 348 文件产出 0 符号（file 级只有 path/language/sizeLines），.cuh/.cu 的类与函数全部由批阶段子代理源码手扫补充（C++ 声明手扫 519 条），行号锚以源码复核为准——与 NCCL/KCCL 轮"C/C++ tree-sitter 盲区"钉版一致。
7. **graph 工艺：documents 边初稿错目标修正**：CMakeLists.txt/python/CMakeLists.txt/DetectSupportedStandards.cmake 等被 scanner 按 fileCategory 归为 docs，初稿挂了错误目标类型的边；批阶段按"构建脚本实质"重挂 document 节点并在 notes 说明（NOTES batch-13/17/8 甄别记录）。
8. **stdrel 判据有"不收敛出口"**：常见误解是 stdrel 只看相对标准误阈值——`nvbench/detail/stdrel_criterion.cxx:103-115` 还有噪声稳定窗口（窗口 64/检查间隔 16）：噪声长期稳定在阈值之上也判停，天生噪声大的基准不会永不收敛。

## 工艺备注

- 批阶段 27 条甄别笔记已收割至仓内 `.understand-anything/NOTES-DIGEST.md`（pimpl/RAII 甄别、共享计时核心双消费者、异常控制流等）。
- 任务书"testing 16 套件"口径与实测不符：真实为 37 个 .cu 测试文件/36 个测试可执行（35+noisy_bench）+ cmake 导出冒烟组；本 README 以 `testing/CMakeLists.txt` 实证为准。
- 字数口径：onboarding/explain 均按"不计空格字符"统计；锚点为全路径 `path:line` 形式，终验脚本对 348 文件基线全量界内检查 0 坏。
