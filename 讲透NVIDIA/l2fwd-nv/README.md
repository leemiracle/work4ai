# 讲透 NVIDIA/l2fwd-nv

DPDK×GPU 二层转发基准程序：在 l2fwd 的 RX/TX core 之间插入可切换 workload（无/CPU/GPU 每突发 kernel/持久 kernel/CUDA Graphs 五模式），度量 GPU 参与网络转发路径的开销。4 个实现文件 + DPDK/gdrcopy 源码子模块。

## 全链状态表

| 产物 | 状态 | 位置 |
|---|---|---|
| DeepWiki 全量 | ✅ TRUE_100 | `deepwiki/` |
| understand 图谱 | ✅ 44n/68e/4 层/6 步 tour，0 issues，fingerprints 12 文件 @ 3ef308b7 | 仓内 `.understand-anything/knowledge-graph.json` |
| ONBOARDING | ✅ 6 节 / 66 行号锚（任务书 6 节 20 锚超额） | `onboarding/ONBOARDING.md` |
| explain | ✅ 2 篇（kernel.cu 三形态 / main.cpp 运行时主线） | `explain/01-…md` `explain/02-…md` |
| NOTES-DIGEST | ✅ 5 条 | 仓内 `.understand-anything/NOTES-DIGEST.md` |

## 源码级勘误清单（6 条，行号实证 @ 3ef308b7）

1. **IPV4_UDP_MODE 是悬空开关**：`CMakeLists.txt:30` 定义 `OPTION(IPV4_UDP_MODE "Encapsulate eCPRI packets in IPv4/UDP" OFF)`，但该宏在 src/include 全仓**零引用**（grep 实证）——eCPRI over IPv4/UDP 的实验分支只存在于构建开关层，代码从未接线；连同 `:63` 起禁用 baseband/* 等驱动看，此构建脚本携带着上游 eCPRI 变体的基因残留。
2. **README "next 8 bursts" 口径易误读**：README:27 说 Graphs 模式 "a number of CUDA kernels is triggered for the next 8 bursts"，代码真相是每张图录 8 个突发（`common.h:36` GRAPH_BURST=8）、共 **512 张图**（`N_GRAPHS=4096/8`，`:35-37`；录制循环 `pipeline.cpp:68-75`）——"8"是图的粒度不是总量。
3. **mlx5 硬校验藏在 main 深处而非 README 前置**：`main.cpp:689-690` 非 `mlx5_pci` 网卡直接 `rte_exit("Non-Mellanox NICs have not been validated")`；README 快速开始未把"Mellanox 网卡是硬条件"放在依赖清单同级位置。
4. **headers.h↔pipeline.h 循环包含**：`include/headers.h:77` include pipeline.h，而 `include/pipeline.h:20` include headers.h——靠 include guard 成立的 aggregator 环（图谱 L3/L4 交界形成合法 include 环）；改声明时须意识到两文件互相可见。
5. **默认 workload 是 CPU 而非 No workload**：`main.cpp:25` `static int conf_workload = CPU_WORKLOAD;`——不带 `-w` 跑的是 CPU 换 MAC 模式；README:179 的 `-w` 帮助文本未标注默认值，与"基准应从 -w 0 起步"的直觉相反。
6. **tree-sitter 对 kernel.cu 零提取**：`.cu` 文件（301 行三 kernel + 三包装）的函数结构在图谱中全部为手扫补充（digest 钉版）；引用函数行号时以源码 grep 为准，勿信图谱 contains 边的完整性。

## 快速上手

硬条件：Mellanox mlx5 网卡 + CUDA ≥11（`CMakeLists.txt` `FIND_PACKAGE(CUDA 11 REQUIRED)`）+ DPDK/gdrcopy 子模块 init。起步 `-w 0`（纯 I/O 转发），逐级 `-w 2/3/4` 对比三 GPU 形态；用 `-t`（每包纳秒负载）与 `-b`（burst 尺寸）联合扫描（README:184）。分析开 `-DENABLE_NVTX=1`（CMakeLists.txt:32）配 nsight systems，色轨定义在 `cuda_related.h:28-34`。

## 深讲入口

- 三种 GPU 形态与 __globaltimer 计时设计：`explain/01`
- main 六步主线/mempool 双形态/buffer split 互斥：`explain/02`
- 图谱导览：`.understand-anything/onboard-input.json`（4 层/6 步 tour）
