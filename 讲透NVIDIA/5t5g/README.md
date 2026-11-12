# 讲透 5t5g

> NVIDIA 5T for 5G——DPDK 实时 SmartNIC 示例（Generator+Receiver 双应用演示 O-RAN U-plane）
> 仓库：https://github.com/NVIDIA/5t5g | 21 文件 | C++17 + CUDA + DPDK

## 全链状态

| 阶段 | 状态 | 产出 |
|---|---|---|
| DeepWiki | N/A（仓未收录） | — |
| understand 图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`（59n/99e/8层/12步 tour，validator 0/0） |
| ONBOARDING | ✅ | `onboarding/ONBOARDING.md`（8 节，~3800 字符） |
| explain | ✅ | `explain/`（6 篇小仓从简，~5900 字符） |

## 勘误清单

| # | 发现 | 证据 |
|---|---|---|
| 1 | `constants.hpp` include guard 写作 `COSTANTS_H` | common/include/constants.hpp:5（上游笔误） |
| 2 | `common/.DS_Store` 为 macOS 垃圾文件 | file 节点标记 noise |
| 3 | `oran_generator.hpp` 与 `oran_receiver.hpp` 为同库分叉拷贝（receiver=超集） | 两文件内容对照（receiver 多 C-plane section + Bitfield `__host__ __device__`） |
| 4 | tree-sitter 对 `.cu` 语言函数提取全空 | kernel.cu 两个 CUDA 函数手工补齐 |
| 5 | tree-sitter 漏提取 `setup_rules`（100 行 static 函数） | ru_recv.cpp 手工补 |
| 6 | scanner `batchImportData` 对 C/C++ 全空（18 条 imports 全手扫） | CMake `target_include_directories` 路径解析+磁盘验证 |
| 7 | `common/include/oran_generator.hpp` 不存在（唯一路径为 `generator/include/`） | 磁盘验证 |

## 一句话总结

DPDK + GPUDirect 的 5G O-RAN 教学示例：Generator 模拟 O-RU 发包，Receiver 在 GPU 上实时解析——`RTE_PKTMBUF_HEADROOM=0` 让 DPDK 包直达显存是核心。
