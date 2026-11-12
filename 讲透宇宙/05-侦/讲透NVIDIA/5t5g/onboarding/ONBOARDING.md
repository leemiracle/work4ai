# 5t5g Onboarding

> NVIDIA 5T for 5G——DPDK 实时 SmartNIC 示例（Generator+Receiver 双应用演示 O-RAN U-plane）
> 仓：`/usr-data/data2/repos/agent-repos/NVIDIA/5t5g`（aarch64，C++/CUDA，21 文件）
> 图谱：`.understand-anything/knowledge-graph.json`（59n/99e/8层/12步 tour，0 issues）

## 1. 这是什么项目

NVIDIA 5T for 5G 是一个**教学级示例**，演示如何通过 DPDK 库使用 NVIDIA 5T for 5G 实时 SmartNIC 技术。包含两个应用：

- **Generator**：模拟两台 O-RU（Radio Unit）发送 O-RAN 格式的 U-plane 包，使用不同 slot 时长
- **Receiver**：模拟一个 O-DU（Distribution Unit），能接收 O-RAN CUS U-plane 包并区分来自两台 O-RU 的数据流

主要目标不是展示性能，而是展示如何在应用中启用 5T for 5G 特性。

## 2. 技术栈与依赖

| 层 | 技术 |
|---|---|
| 语言 | C++17（host）+ CUDA（kernel） |
| 网络框架 | DPDK（Data Plane Development Kit） |
| GPU 交互 | GPUDirect（RDMA 直达显存，`RTE_PKTMBUF_HEADROOM=0` 的 mempool 配置） |
| 构建 | CMake（根编排 generator/receiver 双 target） |
| 外部依赖 | DPDK（经 .gitmodules 引入 meson 构建） |

## 3. 架构分层

```
L01 构建系统与元数据     ← 根 CMakeLists + .gitmodules
L02 项目文档             ← README + CONTRIBUTING
L03 公共库接口           ← constants.hpp + ru.hpp + utils.hpp
L04 公共库实现           ← ru.cpp + utils.cpp
L05 Generator 应用       ← main.cpp + ru_gen.hpp + oran_generator.hpp
L06 Receiver 协议头      ← oran_receiver.hpp + cuda_headers.hpp + ru_recv.hpp
L07 Receiver CUDA Kernel ← kernel.cu（GPU 上解析 U-plane 包）
L08 Receiver 应用逻辑    ← main.cpp + ru_recv.cpp（DPDK EAL + rte_flow）
```

## 4. 关键类与继承

```
RU（抽象基类，common/include/ru.hpp）
├── RUGen（generator/include/ru_gen.hpp）   → 发送端
└── RURecv（receiver/include/ru_recv.hpp）  → 接收端
```

RU 基类提供公共接口（初始化/发包/收包），两个子类分别实现发送和接收逻辑。

## 5. 数据流（Receiver GPU 路径）

```
DPDK 收包（rte_eth_rx_burst）
    ↓
GPU mempool（GPUDirect 直达显存，RTE_PKTMBUF_HEADROOM=0）
    ↓
CUDA kernel（receiver/src/kernel.cu）
    ↓ 解析 O-RAN U-plane 包格式
提取 IQ 数据 + 区分两台 O-RU 数据流
```

## 6. O-RAN 协议库分叉

`oran_generator.hpp` 与 `oran_receiver.hpp` 是同一 O-RAN 协议库的**收/发两份拷贝分叉**：
- generator 版：基础 U-plane 包拼装
- receiver 版：**超集**——增加了 C-plane section 结构和 `__host__ __device__` Bitfield 模板（供 CUDA kernel 使用）

这是教学示例的常见做法（避免引入复杂构建依赖），实际工程应统一。

## 7. 新人常见坑

1. **`.DS_Store` 是 macOS 垃圾文件**——图谱标记为 noise，不含有效信息
2. **include guard 笔误**：`constants.hpp` 的 guard 写成 `COSTANTS_H`（上游原文如此）
3. **`oran_generator.hpp` 的 include 路径**：CMake 的 `target_include_directories` 设为 `PUBLIC include + ${COMMON_INCLUDE}`，解析时须按此路径映射（scanner 的 batchImportData 对 C/C++ 全空，18 条 imports 全靠手扫+CMake 路径解析）
4. **kernel.cu 的 tree-sitter 盲区**：`cu` 语言的函数提取全空，需手工补齐
5. **ru_recv.cpp 的 `setup_rules`**：100 行 static 函数（rte_flow 规则构造器），tree-sitter 漏提取

## 8. 如何跑起来

```bash
# 构建（需 DPDK + CUDA）
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j

# 运行 Receiver（先起）
./build/receiver/receiver --help

# 运行 Generator（后起）
./build/generator/generator --help
```

> 术语参考 [O-RAN 标准](https://www.o-ran.org)
