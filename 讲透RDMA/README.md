# 讲透RDMA · RDMA/网络栈 42 仓知识库（2026-11-11 建组）

范围：/usr-data/data2/kylin/network/rdma/ 下 42 仓（24 真目录 + 19 symlink→agent-repos/NVIDIA 真身 + nccl 同）。
两线流水线：**deepwiki 全量**（本组 `<仓>/deepwiki/`）+ **understand 全链图谱**（图谱在仓内 `.understand-anything/knowledge-graph.json`，onboarding/explain 在本组 `<仓>/`）。
台账：/usr-data/data2/kylin/network/rdma/PROGRESS.md；deepwiki 批次：该仓 `deepwiki-batch/`。

## 状态表（42 行，Gymnasium 模板）

| 仓 | slug | 代码文件 | deepwiki | understand | 备注 |
|---|---|---|---|---|---|
| async-rdma | datenlord/async-rdma | 43 | ✅24页 | ⬜ | 异步 RDMA 库 |
| DeepEP | deepseek-ai/DeepEP | 45 | ✅35页(11-11 刷新) | ⬜ | 旧产物在讲透DeepEP(9-5~11)；本组新做 |
| gpu_direct_rdma_access | Mellanox/gpu_direct_rdma_access | 12 | ✅23页 | ⬜ | |
| infinity | claudebarthels/infinity | 26 | ✅25页 | ⬜ | |
| libfabric | ofiwg/libfabric | 1504 | ✅32页 | ⬜ | 大仓 |
| libvma | Mellanox/libvma | 423 | ✅31页 | ⬜ | |
| Mooncake | kvcache-ai/Mooncake | 2405 | ✅74页(11-11 刷新) | ⬜ | 大仓最后做；旧 deepwiki 在讲透Mooncake |
| open-rdma | open-rdma/open-rdma | 0 | ✅27页 | ⏭️ skip | 纯文档仓无代码 |
| opensm | linux-rdma/opensm | 264 | ✅30页 | ⬜ | |
| perftest | linux-rdma/perftest | 67 | ✅26页 | ⬜ | |
| qperf | linux-rdma/qperf | 7 | 📄repo-docs 1 文件 | ⬜ | NOT_INDEXED |
| rdma_bench | efficient/rdma_bench | 154 | 📄repo-docs 19 | ⬜ | NOT_INDEXED |
| rdma-core | linux-rdma/rdma-core | 546 | ✅28页 | ⬜ | |
| rdma-example | animeshtrivedi/rdma-example | 4 | 📄repo-docs 1 | 🔄 | NOT_INDEXED；小仓校准第一仓 |
| rdmapp | howardlau1999/rdmapp | 40 | 📄repo-docs 1 | ⬜ | NOT_INDEXED |
| rdmatop | uccl-project/rdmatop | 44 | 📄repo-docs 15 | ⬜ | NOT_INDEXED |
| RDMA-tutorial | StarryVae/RDMA-tutorial | 6 | 📄repo-docs 18 | ⬜ | NOT_INDEXED |
| RDMA-Tutorial | jcxue/RDMA-Tutorial | 14 | 📄repo-docs 1 | ⬜ | NOT_INDEXED |
| rust-ibverbs | jonhoo/rust-ibverbs | 29 | ✅30页 | ⬜ | Rust 仓（rust_use_rescan） |
| softiwarp | zrlio/softiwarp | 24 | ✅17页 | ⬜ | 内核模块 |
| ucc | openucx/ucc | 590 | ✅28页 | ⬜ | |
| uccl | uccl-project/uccl | 965 | ✅37页 | ⏭️ skip understand | 本实验室自有代码 |
| ucx | openucx/ucx | 1015 | ✅28页 | ⬜ | 大仓 |
| 5t5g | NVIDIA/5t5g | 6 | 📄repo-docs 2(cp 讲透NVIDIA) | ⏭️ skip | 已有图谱 59n/8L/12T+onboard+explain（真身） |
| aerial-framework | NVIDIA/aerial-framework | 390 | ✅40页 | ⬜ 候选 | |
| ansible-collection-dpu-ops | NVIDIA/ansible-collection-dpu-ops | 5 | 📄repo-docs 15(cp) | ⏭️ skip | yaml 配置仓 |
| apt-packaging-fabric-manager | NVIDIA/apt-packaging-fabric-manager | 0 | 📄repo-docs 2(cp) | ⏭️ skip | 打包配置仓 |
| cloud-native-stack | NVIDIA/cloud-native-stack | 4 | ✅24页 | ⏭️ skip | 文档仓 |
| daqiri | NVIDIA/daqiri | 608 | 📄repo-docs 76(cp) | ⬜ 候选 | |
| dl-lowlat-infer | NVIDIA/dl-lowlat-infer | 51 | 📄repo-docs 9(cp) | ⬜ 候选 | |
| Fabric-Manager-Client | NVIDIA/Fabric-Manager-Client | 1 | ✅25页 | ⏭️ skip | 已有图谱 11n（仓库本身极小） |
| gdrcopy | NVIDIA/gdrcopy | 32 | ✅22页 | ⏭️ skip | 已有图谱 224n+onboard+explain |
| gds-nvidia-fs | NVIDIA/gds-nvidia-fs | 23 | ✅25页 | ⏭️ skip | 已有图谱 139n+onboard |
| jetson-rdma-picoevb | NVIDIA/jetson-rdma-picoevb | 27 | ✅45页 | ⬜ 候选 | |
| l2fwd-nv | NVIDIA/l2fwd-nv | 8 | ✅29页 | ⏭️ skip | 已有图谱 44n+onboard+explain |
| mpi-acx | NVIDIA/mpi-acx | 12 | 📄repo-docs 2(cp) | ⬜ 候选 | |
| nccl | NVIDIA/nccl | 931 | ⏭️ skip | ⏭️ skip | 讲透NCCL 全链已有（58页+4306n 图谱在 /usr-data/data2/kylin/nccl） |
| nccl-extensions | NVIDIA/nccl-extensions | 138 | 📄repo-docs 24(cp) | ⬜ 候选 | |
| nccl-tests | NVIDIA/nccl-tests | 62 | ✅45页 | ⬜ 候选 | |
| networking-yang | NVIDIA/networking-yang | 0 | 📄repo-docs 3(cp) | ⏭️ skip | YANG 模型仓 |
| nvshmem | NVIDIA/nvshmem | 684 | ✅42页 | ⏭️ skip | 已有全链 1458n/16L/16T+onboard+explain（真身） |
| yum-packaging-fabric-manager | NVIDIA/yum-packaging-fabric-manager | 0 | 📄repo-docs 2(cp) | ⏭️ skip | 打包配置仓 |

## 汇总

- **deepwiki 线：42/42 收官**——25 TRUE_100 + 16 NOT_INDEXED→repo-docs（非空验证）+ 1 nccl skip（讲透NCCL 已有）
- **understand 线：进行中**——队列=小仓 12（校准轮）→中仓 6→大仓 3（ucx/libfabric/Mooncake）→NVIDIA 候选 7；skip 13（nccl+uccl+open-rdma+已有图谱 6+零代码 4）+cloud-native-stack
- 图例：✅=TRUE_100 页数；📄=repo-docs 兜底文件数；⏭️=skip（理由如列）；⬜=待做；🔄=进行中

## 来源与新鲜度

- deepwiki 全部 2026-11-11 抓取（dw_fetch_mcp.py）；NVIDIA 9 仓 repo-docs 复制自讲透NVIDIA（10-26/11-04 轮收割，勿重收）
- understand 图谱锚定当日仓内 commit（见各仓 .understand-anything/fingerprints.json）
