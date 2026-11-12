# DeepGEMM 新人指南（简版）

> 依据仓库 knowledge-graph（571 节点/1117 边/10 层/12 步导览）与 README 整理。图谱位于仓内 `.understand-anything/knowledge-graph.json`。

## 一、项目是什么与定位

DeepGEMM 是 DeepSeek 开源的统一高性能 Tensor Core 内核库，把现代大模型的关键计算原语——FP8/FP4/BF16 GEMM、融合 MoE（Mega MoE，通信与计算重叠）、lightning indexer 的 MQA logits 打分、HyperConnection 等——收进一份干净的 CUDA 代码库，是 DeepSeek-V3 系列训练与推理的核心算子底座。两个鲜明取舍：①**全部内核运行时 JIT 编译**，安装时无需编译 CUDA——用编译时间换任意 M/N/K 与数据布局组合的全形状覆盖；②只借鉴 CUTLASS/CuTe 概念而不重度依赖其模板体系，核心内核数量少，官方明确把它定位为**学习 GPU 内核优化的干净教材**。性能不输专家调优的库：H800 上 FP8 GEMM 最高 1550 TFLOPS。新人还需先记两个约定：命名中的 `1d1d`/`1d2d` 指缩放因子（SF）粒度——前者激活与权重均逐块缩放，后者激活逐元素、权重逐块（V3 训练的实际形态）；SM90 要求 SF 为 FP32 格式，SM100 要求打包为 UE8M0（4 个装进一个 `torch.int`），两代架构不通用。

## 二、架构分层（按图谱 10 层）

图谱自上而下 10 层，可归为四个带：

- **工程带（L1-L2）**：文档与工程配置层、构建安装与 CI 层——README、cutlass/fmt 子模块声明、setup.py/CMake、develop/install 脚本与 GitHub Actions wheel 流水线。
- **接口带（L3-L4）**：Python API 与旧版接口层（`deep_gemm` 包入口、mega/testing/utils 子包、legacy Triton 分组 GEMM）；C++ API 与 pybind 绑定层（`csrc/apis` 各算子注册 + `python_api.cpp` 总入口）。
- **JIT 中枢带（L5-L6）**：JIT 编译框架层（运行时拼源码→nvcc/NVRTC 编译→缓存→加载句柄）；JIT 内核实现与启发式层（形状→block 布局/流水线参数的决策与调用代码生成）。
- **内核带（L7-L9）**：C++ 公共工具层；CUDA 内核模板层（`deep_gemm/include` 下按 SM90/SM100 × 精度 × 布局组织的 `.cuh` 内核本体）；CUDA 支撑原语层（PTX 内联汇编、MMA 封装、TMA、静态调度器、epilogue、同步 barrier）。
- **L10 测试与第三方基线层**：tests/ 端到端用例与 tilelang_ops 对照。

一句话调用链：Python API → pybind → 启发式选配置 → JIT 生成/编译/缓存 → 加载 `.cuh` 模板实例化出的内核 → 原语层支撑执行。

## 三、核心模块（每层 1-2 个）

| 层 | 代表模块 | 职责 |
|---|---|---|
| L1 | README.md、.gitmodules | 门面文档；cutlass/fmt 子模块 |
| L2 | setup.py、develop.sh | 打包 `_C` 扩展；开发就地构建+软链头文件 |
| L3 | `deep_gemm/__init__.py`、`deep_gemm/mega/` | 包入口懒加载导出；MegaMoE 对称缓冲与权重交错预处理 |
| L4 | `csrc/python_api.cpp`、`csrc/apis/gemm.hpp` | pybind 总入口聚合七组 API；GEMM 家族注册面 |
| L5 | `csrc/jit/compiler.hpp`、`cache.hpp` | 运行时拼源码调 nvcc/NVRTC；按源码哈希缓存产物 |
| L6 | `heuristics/sm90.hpp`/`sm100.hpp`、`impls/*.hpp` | 形状→布局/流水线决策；内核调用代码生成 |
| L7 | `utils/exception.hpp`、`utils/layout.hpp` | DGException 统一异常；SF 布局与 TMA 对齐校验 |
| L8 | `sm90_fp8_gemm_1d2d.cuh`、`sm100_fp8_fp4_mega_moe.cuh` | Hopper FP8 主力内核；Blackwell mega 内核（约 1400 行单内核） |
| L9 | `common/tma_copy.cuh`、`ptx/wgmma.cuh`/`tcgen05.cuh` | TMA 搬运封装；两代 MMA 指令词汇表 |
| L10 | `tests/test_fp8_fp4.py`、`generators.py` | FP8/FP4 正确性+性能用例；量化测试数据生成 |

## 四、快速上手

**环境**：SM90/SM100 GPU；Python ≥3.8；C++20 编译器；CUDA ≥12.3（SM90，官方强烈推荐 12.9+；SM100 需 12.9+）；PyTorch ≥2.1；CUTLASS ≥4.0 与 `{fmt}` 经子模块引入。

```bash
# 开发（必须 --recursive 拉子模块）
git clone --recursive git@github.com:deepseek-ai/DeepGEMM.git
cd DeepGEMM && ./develop.sh   # 软链 cutlass/cute 头 + 构建 CPP JIT 模块
# 安装
./install.sh                  # 打 wheel 并强制重装
```

**常用接口**（命名约定 `D = C + A@B`，NT 布局）：`fp8_gemm_nt` 普通 FP8 GEMM；`m_grouped_fp8_gemm_nt_contiguous` MoE 连续布局分组（M 需按 `get_mk_alignment_for_contiguous_layout()` 对齐）；`m_grouped_fp8_gemm_nt_masked` 解码期 CUDA graph 掩码分组；`fp8_mqa_logits`/`fp8_paged_mqa_logits` V3.2 indexer 打分；`fp8_fp4_mega_moe` 多进程对称内存 mega kernel。

**测试**：`python tests/test_fp8_fp4.py`、`test_bf16.py`、`test_attention.py`、`test_mega_moe.py`（注意 README 提到的 `tests/test_core.py` 已不存在，以 tests/ 实际文件为准）。

**布局与转置注意**：SM90 只支持 NT 布局（A 行主、B 列主），SM100 支持全部 NT/TN/NN/TT；LHS 缩放因子必须 TMA 对齐且转置存放，官方提供 `transform_sf_into_required_layout`、`get_mn_major_tma_aligned_packed_ue8m0_tensor` 等工具函数兜底。

**实用环境变量**：`DG_JIT_CACHE_DIR`（内核缓存目录，默认 `~/.deep_gemm`）、`DG_PRINT_CONFIGS=1`（打印选中配置）、`DG_JIT_DUMP_SASS=1`（dump 产物）、`DG_JIT_USE_NVRTC=1`（编译提速但可能掉性能）。注意：输入转置、FP8 cast 等前处理需用户自行完成或融合进上游内核。

## 五、学习路径（按图谱 12 步 Tour）

1. **门面与构建**：读 README 领会"JIT 换全形状覆盖"的取舍，看 setup.py/CMakeLists——注意构建产物里没有预编译内核。
2. **Python 入口**：`__init__.py` 按架构懒加载扩展，mega/testing/utils 子包只管生命周期与易用性。
3. **pybind 与 C++ API**：`python_api.cpp` 聚合注册 attention/einsum/hyperconnection/gemm/layout/mega/runtime 七组 API。
4. **JIT 框架（全仓最有特色）**：`compiler.hpp` 运行时拼 CUDA 源码调 nvcc，`cache.hpp` 以源码哈希为键缓存 so，`include_parser.hpp` 递归哈希头依赖——理解"为什么 JIT"是理解全仓的钥匙。
5. **启发式**：`heuristics/sm90/sm100.hpp` 为给定形状选 block 布局与流水线级数，`config.hpp` 定义 GemmDesc/LaunchConfig 数据模型。
6. **SM90 FP8 主力**：对照 `impls` 侧 `.hpp`（生成调用代码）与 `include` 侧 `.cuh`（TMA+wgmma 内核本体），体会双面结构。
7. **底层原语**：`ptx/tcgen05.cuh`、`ptx/wgmma.cuh`、`mma/sm90.cuh`、`common/math.cuh`——构成全仓指令词汇表。
8. **SM100 Blackwell**：tcgen05 MMA + TMEM 新编程模型，看 `sm100_fp8_fp4_gemm_1d1d.cuh` 与 `epilogue/sm100_store_cd.cuh`，对比两代差异。
9. **MegaMoE**：权重交错预处理 + 编译期静态调度 + NVLink 通信重叠，V3 推理加速核心链路。
10. **注意力算子**：`sm90_fp8_paged_mqa_logits.cuh` 页式 KV + SPLIT_KV。
11. **外围**：`comm/barrier.cuh` 跨 GPU barrier、einsum/hyperconnection 小众算子、cuBLASLt 非 JIT 后备。
12. **测试收尾**：`test_fp8_fp4.py`/`test_mega_moe.py` + `testing/numeric.py` 校验体系，CI 按架构矩阵出 wheel。

建议节奏：第 1-5 步建立全局观（半天），第 6-8 步精读内核（核心投入），第 9-12 步按需深入。
