# phytvm 飞腾真实改动清单（vs upstream Apache TVM）

> 路径：`/data/usershare/ai/飞腾/phytium_repos/opt-npu/ncsdk/common/phytvm/`
> 基线：upstream Apache TVM（github.com/apache/tvm）
> phytvm 版本：**TVM v0.11.dev0** `[实测-读文件]` version.py:47 `__version__ = "0.11.dev0"`
> 实测日期：2026-07-07

---

## 0. 一句话结论

**oracle 的判断部分正确但需修正**：`codegen_arm.cc` 确实是 vanilla Apache TVM（确认），但飞腾对 TVM 的真实定制**不在 LLVM codegen 层**，而在**设备类型注册层 + runtime 层 + relay contrib codegen 层（NPU/GPU 外部编译器接入）+ Python 量化层**。飞腾的 NPU/GPU 计算走**外部编译器二进制**（npu_compiler、gpu_compiler），**完全不经过 LLVM codegen**。LLVM codegen（src/target/llvm/）在 phytvm 中是 vanilla upstream，未被飞腾触碰。

---

## 1. 确认是 vanilla upstream 的部分（飞腾未改）

### 1.1 `src/target/llvm/codegen_arm.cc` —— vanilla Apache TVM `[实测-读文件]`
- 文件头：标准 ASF license（"Licensed to the Apache Software Foundation"）
- 注释原文（第38-40行）：`// ARM specific code generator, this is used as an example on / how to override behavior llvm code generator for specific target`
- 这是 upstream TVM 的**示例性** ARM codegen，不是飞腾自研后端。**oracle 结论正确。**

### 1.2 `src/target/llvm/` 整个目录 —— upstream TVM `[实测-读文件]`
- 含 codegen_llvm.cc/.h、codegen_arm.cc、llvm_module.cc/.h、llvm_instance.cc/.h、intrin_rule_llvm.cc/.h
- 全部为 upstream TVM 的 LLVM target 实现，未发现飞腾改动标记。

### 1.3 `src/target/opt/` —— upstream TVM build 脚本 `[实测-读文件]`
- 内容：build_aocl_off.cc、build_cuda_off.cc、build_cuda_on.cc、build_hexagon_off.cc、build_metal_off.cc、build_opencl_off.cc、build_rocm_off.cc、build_sdaccel_off.cc、README
- 这些是 upstream TVM 的各 target 构建开关，**无飞腾 NPU 自定义 target**（没有 build_phytium.cc）。

### 1.4 `src/target/source/` —— upstream TVM `[实测-读文件]`
- 标准 codegen_c/cuda/metal/opencl/vhls/aocl，无飞腾定制。

### 1.5 CMakeLists.txt —— 无飞腾构建开关 `[实测-grep]`
- grep `phytium|Phytium|PHYTIUM|use_phytium` 在 phytvm/CMakeLists.txt **无命中**（仅有 input/npu 等通用词的误匹配）。
- 说明 phytvm 构建走标准 TVM CMake，无 `USE_PHYTIUM` 之类开关。

---

## 2. 飞腾真实改动的文件（逐项列出，含证据）

### 2.1 【核心】DLPack 设备类型扩展：`3rdparty/dlpack/include/dlpack/dlpack.h` `[实测-grep]`
飞腾 fork 了 DLPack 标准，新增 **7 个 device type enum**（第93-105行）：
```
kDLPhytium = 16,        // 飞腾总称
kDLPhytiumNPU = 17,     // NPU
kDLPhytiumGPU = 18,     // PHYDNN GPU
kDLPhytiumOpenCL = 19,  // Custom OpenCL
kDLPhytiumCPP = 20,     // Custom C++
kDLPhytiumProfile = 21, // Profile
kDLPhytiumGOCOpenCL = 22 // GOC OpenCL
```
- upstream DLPack 不含这些。这是飞腾对张量设备抽象的根本性扩展。

### 2.2 `include/tvm/runtime/c_runtime_api.h` `[实测-grep]`
- 第144-150行：7 个 `static_assert(kDLPhytium == 16, ...)` 锁定 device type 整数值。

### 2.3 `include/tvm/runtime/device_api.h` `[实测-grep]`
- 第290-302行：新增 7 个 case 分发到 PhytiumDeviceAPI。

### 2.4 【核心】`src/target/target_kind.cc` —— 7 个 target kind 注册 `[实测-读文件]`（第439-458行）
```
TVM_REGISTER_TARGET_KIND("phytium", kDLPhytium)
    .set_default_keys({"phytium", "npu", "phydnn_gpu"});
TVM_REGISTER_TARGET_KIND("npu", kDLPhytiumNPU)
TVM_REGISTER_TARGET_KIND("phydnn_gpu", kDLPhytiumGPU)
TVM_REGISTER_TARGET_KIND("customcl", kDLPhytiumOpenCL)
TVM_REGISTER_TARGET_KIND("customcpp", kDLPhytiumCPP)
TVM_REGISTER_TARGET_KIND("phytium_profile", kDLPhytiumProfile)
TVM_REGISTER_TARGET_KIND("goc_opencl", kDLPhytiumGOCOpenCL)
```
- upstream TVM 不含任何 phytium/npu/phydnn target kind。

### 2.5 【核心】`src/runtime/phytium/` —— 飞腾 runtime（25 文件）`[实测-读文件]`
完整文件清单：
- phytium_device_api.cc/.h（设备 API）
- phytium_module.cc/.h（模块加载）
- phytium_scope.h
- npu_runtime.cc（NPU 运行时）
- gpu_runtime.cc（GPU 运行时）
- offline_gpu_runtime.cc（离线 GPU 编译器运行时）
- customcl_module.cc/.h + customcl_runtime.cc（自定义 OpenCL）
- customcpp_module.cc/.h + customcpp_runtime.cc（自定义 C++）
- events.cc/.h（事件同步）
- profile_device_api.cc/.h + profile_module.cc/.h + profile_runtime.cc（profiling）
- pipeline_executor.cc/.h（流水线执行器）
- runtime_common.cc/.h
- 这是飞腾对接自研 NPU/GPU 硬件的运行时实现。

### 2.6 【核心 + 飞腾专有】`src/relay/backend/contrib/phytium/` —— 12 文件 `[实测-读文件]`
完整文件清单：
- codegen.h（**飞腾专有**：`@copyright Copyright (c) Phytium Technology Co., Ltd. All Rights Reserved` / `@license Strictly Confidential. This is the NC-SDK Standard license`）
- codegen_npu.cc、codegen_phydnn_gpu.cc、codegen_customcl.cc、codegen_customcpp.cc、codegen_goc_cl.cc、codegen_profile.cc
- utils.cc/.h、codegen.h
- customcl_source_module.h、customcpp_source_module.h、goc_cl_source_module.h

**关键发现**：grep `LLVM|llvm|mcpu|target_triple|triple` 在 contrib/phytium/*.cc **零命中** `[实测-grep]`。
- codegen.h 定义的 `PhytiumConfig` 配置的是**外部编译器二进制**：
  - `mapper_bin_path` = "Path to mapper binary **npu_compiler**"
  - `gpu_compiler_bin_path` = "Path to gpu compiler binary **gpu_compiler**"
  - `phydnn_version` 默认 "PHYDNN001008"
- **结论：飞腾 NPU/GPU 的 Relay 子图编译交给外部闭源编译器（npu_compiler/gpu_compiler），不经过 LLVM。**

### 2.7 `python/tvm/relay/phy_quantize/` —— 飞腾量化（8 文件）`[实测-读文件]`
- _annotate.py、_calibrate.py、_partition.py、_partition_conversions.py、_quantize.py、kl_divergence.py、quantize.py、__init__.py
- upstream TVM 有 `relay/quantize/`，但**没有** `phy_quantize/`。这是飞腾针对自研 NPU 量化精度（KL 散度校准、PHYQuantizeAnnotate pass）的定制。
- src/relay/quantize/annotate.cc 第121行：`/* Pass PHYQuantizeAnnotate : phytium annotation during quantize process. */`

### 2.8 `python/tvm/_ffi/runtime_ctypes.py` `[实测-grep]`
- 第216-222行、248-285行：7 个 device type 的 Python 端注册与字符串映射。

### 2.9 `python/tvm/runtime/ndarray.py` `[实测-grep]`
- 第588、603行：`Device(Device.kDLPhytiumNPU, dev_id)` / `Device(Device.kDLPhytiumGPU, dev_id)`

### 2.10 `apps/phytium_deploy/phytium_execute.cc` `[实测-读文件]`
- 飞腾部署应用，引用全部 7 个 device type 常量。

### 2.11 docker 安装脚本 —— 上游 LLVM `[实测-读文件]`
- `docker/install/ubuntu_install_llvm.sh`：从 apt.llvm.org 安装 llvm-4.0/7/8/9 + clang-7/8/9。**完全上游，无飞腾 LLVM fork。**

---

## 3. 未发现飞腾定制的目录（诚实承认）

- `src/relay/`（除 backend/contrib/phytium 外）：upstream Relay IR，无飞腾改动。
- `src/topi/`、`src/te/`、`src/tir/`（除 contrib/ethosu 是 upstream Arm Ethos-U）：upstream，无飞腾改动。
- `src/auto_scheduler/`、`src/autotvm/`、`src/meta_schedule/`：upstream，无飞腾改动。
- `docs/`、`tests/`、`gallery/`：upstream TVM 文档/测试（gallery 有 phytvm 自动调优的 JSON 日志但非定制代码）。

---

## 4. 对 Expert_18 写作的输入建议

1. **核心叙事**："飞腾没有自研 LLVM 后端"——这是本任务最重要的工程实证。oracle 的判断成立，但要**修正精度**：飞腾的编译器创新不在 LLVM codegen，而在 **NPU/GPU 外部编译器（npu_compiler/gpu_compiler，闭源）+ TVM 设备类型扩展**。
2. **架构定位**：phytvm 的 LLVM codegen 只服务 **host CPU target**（FTC862 上跑 host 代码），用的是 vanilla upstream LLVM（对应 Expert_08 AArch64 backend 内容）。NPU 推理绕过 LLVM。
3. **护城河锚点**：可以明确写出飞腾 TVM fork 的 7 个 device type + 25 个 runtime 文件 + 12 个 contrib codegen 文件——这是飞腾公开 SDK 里**唯一可见的编译器层自研痕迹**，但都在 LLVM 之外。
4. **盲区诚实段**：npu_compiler/gpu_compiler 二进制是闭源的，其内部是否基于 LLVM 未知（推测：npu_compiler 可能是图编译器/mapper，非传统 LLVM 后端；无法实测确认）。
5. **对偶链接**：与 Expert_11（GPU 异构后端）对照——飞腾 GPU 走 PHYDNN/OpenCL 离线编译器，非传统 LLVM GPU 后端。
