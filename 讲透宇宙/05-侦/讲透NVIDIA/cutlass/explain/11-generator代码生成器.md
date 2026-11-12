# 11 · generator 代码生成器：13092 行单文件与 12 代际旗舰

## 角色定位

`python/cutlass_library/generator.py`（13092 行）是 CUTLASS kernel 清单的代码生成器：按代际枚举"数据类型×tile 形状×代际特性"组合，吐出 C++ 编译单元注册代码与 kernel 测试清单。它由 CMake 消费（customConfigs.cmake:48-52 以 `PYTHONPATH=CUTLASS_LIBRARY_PACKAGE_DIR` 调 generator.py `--architectures=${CUTLASS_NVCC_ARCHS}`），是"Python 生成 C++ 模板实例"工程范式的发动机。图谱域 142 节点/21 文件。

## 内部结构

**入口无 main()**：全部逻辑在 `if __name__ == "__main__":` 块（generator.py:13035）——define_parser（argparse 见 generator.py:12998）、`Manifest(args)`（generator.py:13042）、`--heuristics-problems-file` 分支（generator.py:13046）后逐代际展开；`_add_package_disablement_flag`（generator.py:70）给 `--disable-cutlass-package-imports`。

**12 个代际旗舰函数**是骨架：`GenerateSM50`（generator.py:1357）、`GenerateSM60`（generator.py:1482）、`GenerateSM61`（generator.py:1542）、`GenerateSM70`（generator.py:1749）、`GenerateSM75`（generator.py:2390）、`GenerateSM80`（generator.py:4923）、`GenerateSM89`（generator.py:5217）、`GenerateSM90_Conv3x`（generator.py:12574）、`GenerateSM100`（generator.py:12472）、`GenerateSM107`（generator.py:12542）、`GenerateSM120`（generator.py:12548）、`GenerateSM90`（generator.py:12945）。__main__ 块先无条件展开 SM50..SM90（generator.py:13047-13052），Blackwell 门控 `blackwell_arch_list`（generator.py:13057-13066，100a..121f 十四条目）命中才跑 SM100/SM120，Rubin 门控 `rubin_arch_list`（generator.py:13076）再跑 SM107。**甄别**：SM103 没有顶层入口——`GenerateSM103_TensorOp_fp4_ultra…`（generator.py:9359）在 `GenerateSM100` 内部被调（generator.py:12527-12528，两次不同 gemm_kind）。

**族函数宇宙**：旗舰之下是 130+ 个 `GenerateSMxx_TensorOp_*` 族函数（SM80 一个代际就有 16816/16832/1688/884 系列数十个，SM100 覆盖 fp8/fp4/mixed_8bits/MoE/blockscaled）。**三张纯数据表**供形状：`sm90_shapes.py`（212 行）、`sm100_shapes.py`（372 行）、`sm107_shapes.py`（108 行）——模块级 dict，**零函数零类**，sm100 表配合 DynamicClusterShape 支持动态 cluster；工具层 sm90/sm100/sm107_utils.py（753/886/251 行）。

**Manifest 与发射器**（manifest.py 868 行）：`EmitOperationKindAll`（manifest.py:69，上下文管理器 __enter__ manifest.py:131/emit manifest.py:152）、`EmitOperationKindLibrary`（manifest.py:178）、`EmitInterfaceLibrary`（manifest.py:377）。各 op 形状由 gemm_operation.py、conv2d/conv3d_operation.py、rank_k/symm/trmm_operation.py 承担；`emit_kernel_listing.py` 支持 generator_target=kernel_testlist_l0/l1（generator.py:13085-13089 消费）；`library.py`（1701 行）是枚举宇宙（DataType/OpcodeClass/GemmKind…）；heuristics.py（415 行）支持离线启发式表。

## 外部连接

上游 CMake：customConfigs.cmake:48-52 是唯一构建内调用点，`--operations` 等参数决定生成面；下游产物是 generated/ 目录的 C++ 源与 CMake 片段，被仓根 CMakeLists.txt 的 kernel 注册逻辑吞掉。operators 库（第 09 篇）metadata/design 与本生成器互补——前者是 Python-first 新世界，后者仍服务 C++ 模板实例化。版本勘误：根 pyproject.toml:7 的 `version = "4.2.0.0"` 落后于 include/cutlass/version.h:41-43 的 4.8.0——Python 轮子版本由发布管线单独维护。

## 数据流

CMake 配置期 → generator.py __main__（generator.py:13035）→ Manifest 收集各代际旗舰压入的 operation 实例 → `--generator_target` 分流：`library` 走 manifest.emit 写 generated/ 源码与注册文件；`kernel_testlist_l0/l1` 走 emit_gemm_kernel_testlist 写测试清单；`--selected-kernel-list` 把命中名单写文件（generator.py:13090-13094）。heuristics_problems_file 分支不发射代码，走 filter_manifest_and_write_heuristics_file（generator.py:13047）产出启发式表。

## 设计决策

1. **单文件巨兽而非包**：13092 行集中放置使"哪个代际有哪些族"一眼可扫——代价是重构动全身，家族函数以命名约定代替继承树。
2. **代际门控在入口而非函数内**：blackwell/rubin_arch_list（generator.py:13057/13076）集中判定，GenerateSMxx 本身不感知是否被调——生成面完全由 --architectures 决定。
3. **shapes 表纯数据**：三张表零函数零类，形状变更只动数据不动逻辑（sm107_shapes.py 仅 108 行，Rubin 早期）。
4. **无 main() 直奔 __main__**：与"只被 CMake 当子进程调"的定位一致，argparse/日志全在尾块组装。

## 新人提示

- 定位 kernel 生成来源：先查 __main__（generator.py:13035-13094）确认代际门控，再跳对应 GenerateSMxx 旗舰，最后进族函数。
- SM100/SM103/SM120/SM107 关系易混：103 挂在 100 里（generator.py:12527），120 与 100 同受 blackwell 门控但函数独立（generator.py:12548 vs 12472），107 走 rubin 门控。
- 加新 tile 形状改对应 smXX_shapes.py 即可；加新代际特性才需动 generator.py。
- 生成量大用 --operations/--selected-kernel-list 裁剪（emit 路径按名过滤）。
