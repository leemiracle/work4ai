# 精讲：csrc/apis/gemm.hpp —— GEMM 算子的 C++ API 总入口

> 原文件：`csrc/apis/gemm.hpp`（DeepGEMM，771 行）

## 一、角色定位

这是 DeepGEMM 所有 GEMM 算子的 **C++ API 层与 pybind 注册层**，位于 Python 调用与 JIT 内核实现之间：上层 `deep_gemm/__init__.py` 从 `_C` 扩展模块导入的 `fp8_gemm_nt`、`m_grouped_fp8_fp4_gemm_nt_contiguous`、`bf16_gemm_nt` 等函数，全部在本文件的 `register_apis()` 中注册（命名空间 `deep_gemm::gemm`）。它不写任何 CUDA 内核，职责是**校验、归一化、分发**：把五花八门的转置组合、缩放因子（SF）格式、架构差异收敛成对底层实现的规范化调用。全仓函数节点数最多（图谱计 20 个），是理解 API 全景的第一站。

## 二、内部结构

文件按算子家族组织，全部为 `static` 自由函数：

- **辅助函数**：`early_return`（空问题/k==0 累加等平凡场景短路）、`check_k_grouped_args`（K 分组参数校验并求 sum_k）。
- **FP8/FP4 家族**：核心 `fp8_fp4_gemm_nt`，以及 `nn/tn/tt` 三个仅做 transpose 的包装；分组版 `m_grouped_fp8_fp4_gemm_nt_contiguous`（contiguous 布局，带 `use_psum_layout`）、`_nn_contiguous`、`_nt_masked`（masked 布局，带 `masked_m/expected_m`）；K 分组版 `k_grouped_fp8_gemm_tn_contiguous`（SM100 专用）与 `_nt_contiguous`（SM90，自配 tensormap 缓冲）。
- **BF16 家族**：`bf16_gemm_nt` + 三转置包装 + 分组版。
- **cuBLASLt 兜底**：`cublaslt_gemm_nt` 等 4 个，转发到 `smxx_cublaslt.hpp`。
- **注册函数** `register_apis`：约 25 个 `m.def`，含 `py::arg` 默认值（如 `compiled_dims` 默认 `"nk"`/`"mn"`），并用 `m.attr` 建立旧名别名：`fp8_gemm_nt = fp8_fp4_gemm_nt`。

## 三、外部连接

向上被 `csrc/python_api.cpp` 调用完成注册；向下 include 各架构实现：`jit_kernels/impls/sm90_fp8_gemm_1d1d.hpp`、`sm90_fp8_gemm_1d2d.hpp`、`sm100_fp8_fp4_gemm_1d1d.hpp` 等。依赖两个全局运行时：`device_runtime->get_arch_major()` 判断 SM90/SM100，`heuristics_runtime->get_mk_alignment_for_contiguous_layout()` 取对齐。SF 布局转换全部委托给 `apis/layout.hpp` 的 `transform_sf_pair_into_required_layout` / `transform_k_grouped_sf_into_required_layout`。编译期由 `compatibility.hpp` 的 `DG_FP8_COMPATIBLE`/`DG_TENSORMAP_COMPATIBLE` 宏控制条件编译，兼容老 CUDA 版本。

## 四、数据流

以 `fp8_fp4_gemm_nt` 为例走读：①输入是 `(data, sf)` 张量对，先 `get_major_type_ab` 检查布局（FP8 要求 K-major 时断言）；②`check_ab_fp8_fp4` 提取并核对 M/N/K 与 d 的形状、dtype；③`early_return` 处理空场景——k==0 时直接把 C 拷到 D 或清零；④`transform_sf_pair_into_required_layout` 把用户侧 SFA/SFB 变换成内核所需布局，返回统一的 `(sfa, sfb, gran_k_a, gran_k_b)`；⑤按架构分发：`arch_major==9` 且 sfa 为 float 时走 SM90（`gran_n==1` 选 1D1D 内核，否则 1D2D）；`arch_major==10` 且 sfa 为 int（UE8M0 打包）走 SM100。分组变体多出 `grouped_layout` 校验与 `psum_sfa_layout` 透传（让 SFA 打包跳过空洞行）。

## 五、设计决策

- **转置归一化**：nn/tn/tt 一律 transpose 成 NT 核心路径，内核只需实现一种主序，代价是元数据视图变换。
- **`(Tensor, Tensor)` 对统一 FP8/FP4**：数据与缩放因子捆绑传递，recipe（如 `(1,1,128)`）描述粒度，SM90 float SF 与 SM100 int SF 的差异在 `transform_sf_pair` 内部消化。
- **`compiled_dims` 参数**（"nk"/"mn"）：把指定维度编译成 JIT 常量，是运行时特化的开关。
- **防御式校验**：大量 `DG_HOST_ASSERT` 前置检查，C/D 同指针时要求 sizes/strides 全等并复用缓冲。
- **SM90 K 分组 NT 的细节**：手动分配 `num_sms * 4 * sizeof(CUtensorMap)` 的 tensormap 缓冲（A/B 双操作数各双缓冲）。

## 六、新人提示

读此文件可快速建立 API 全景，但别在此找计算逻辑。注意三点：①Python 侧 `fp8_gemm_*` 是 `fp8_fp4_gemm_*` 的别名，文档与代码搜索时要对上；②新增算子的路径是"写 impl → 此处加函数 → `register_apis` 注册 → `generate_pyi.py` 生成类型存根"；③`DG_HOST_UNREACHABLE` 分支意味着架构/SF 类型组合非法，报错时先查 GPU 架构与 recipe 是否匹配，再查内核实现。
