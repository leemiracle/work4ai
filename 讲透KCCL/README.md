# 讲透KCCL

麒麟多厂商 GPU 统一集合通信库（/usr-data/data2/kylin/kccl，NCCL v2.32.3 基座）知识库。

| 产物 | 位置 | 状态 | 日期 |
| --- | --- | --- | --- |
| understand 图谱 | 仓内 .understand-anything/knowledge-graph.json（219n/463e/11 层/16 步） | ✅ | 2026-10-28 |
| ONBOARDING + explain 12 篇 | 完成记录见仓内 PROGRESS.md:15-16（6050 字/12 篇 62,855 字/678 锚 0 坏）；产物文件未见于本目录与 kccl 仓，需要时按仓内图谱+台账重建 | ⚠️ 文件待定位 | 2026-10-28 |
| **多厂商链路量化对比** | [infra-quant-KCCL.md](infra-quant-KCCL.md)——割集模型场景矩阵：混合域 AllReduce 比纯 NVL8 慢 6-21×，瓶颈=min(组间桥, 最弱组内)；厂商带宽锚点带来源分级 | ✅ | 2026-11-03 |
| **三节点真机实测** | 同报告 §7：沐曦 C500×4 busbw 100.1 GB/s（校准 preset 96）、天数×4 22.6 GB/s（PCIe 71%）、跨机混合域 CommInitRank 死锁根因链（exchange_caps 协议+NetStore 互锁，gdb 符号级）；原始日志 infra-quant/raw/ | ✅ | 2026-11-03 |
| **充分逆向+性能方案全集** | 仓内 `infra-analysis/REVERSE-202611/`（REPORT 295 行+notes 四件 923 行）：kccl 源码精读（新缺陷 17/改进 18）+三节点栈探测（**翻案：在役 MCCL=2.30.4 非复盘 2.16.5，本地头是旧头；天数=NCCL 2.28.9 零改名；RCCL 停 2.22**）+DeepSeek CUDA 用法 20 项映射+量化差距全公式；**§6 方案全集 40 项**（正确性 9/性能 11/调优 7/削量 4/训练 6/推理 6/可观测 4/混合域 5） | ✅ | 2026-11-04 |

姊妹产物：[讲透NCCL](../讲透NCCL/)（DeepWiki 58 页 + 图谱 4306n + infra-quant 单域深度对照）。
工具集：/data/usershare/ai/ai-infra-tools/（topology_cut --kccl-mixed 可复算本报告全部场景）。
