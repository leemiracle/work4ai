# Mooncake 蒸馏卡（2026-11-12）

> 依据 [deepwiki/](deepwiki/INDEX.md)（kvcache-ai/Mooncake，71 页，抓取 2026-10-21）按 `deepwiki-distill` skill 蒸馏。所有结论带章节锚点。

## 1. 本质一句话

**以 KVCache 为中心的存算分离平台**（Kimi 的生产动力 [1.2]）：把 prefill/decode 算力与 KV 缓存存储解耦，集群闲置内存（DRAM/VRAM/CXL/SSD）池化成全局 KV 池——没有它，长上下文服务的 KV 只能挤在单引擎单机的显存里，prefill 与 decode 抢同一池资源 [1.1]。

## 2. 架构三要点

1. **三层解耦** [1.1]：Tier3 应用集成（vLLM connector + SGLang HiCache 扩展 + TransferEnginePy）→ Tier2 存储/控制面（Mooncake Store：MasterService 集中协调 + RealClient/DummyClient 对象生命周期）→ Tier1 数据面（TransferEngine + MultiTransport 零拷贝传输）。
2. **Segment 池化抽象** [1.2]：连续内存段是统一分配单元，可落 DRAM/VRAM/CXL/NVMe-oF SSD 任一层；客户端把段贡献给全局池，Master 管注册与放置，NUMA 感知；副本（Replica）与租约（Lease）由 Master 统一管理。
3. **TransferEngine 双后端 bridge** [4.1]：facade 委托给 `impl_`（Classic：静态拓扑发现+成熟稳健）或 `impl_tent_`（TENT "Transfer Engine Next"：动态路径选择+声明式传输意图+自适应传输选择），`use_tent_` 运行时切换，编译期 `USE_TENT` 门控。

## 3. 关键设计决策

- **MultiTransport 可插拔传输** [1.1][4.x]：RdmaTransport/TcpTransport/IntraNodeNvlinkTransport/AscendDirectTransport/HipTransport/CxlTransport 等并列注册，按拓扑与硬件选择——一份 API 覆盖 CPU/GPU/NPU 异构与 RDMA/TCP/NVLink/EFA 多协议 [4.1]。
- **零拷贝 + batch 优先**：Python API 层零拷贝张量操作与批量操作为一等公民 [3.4][3.5]——KV 复用的收益对拷贝开销极敏感，API 形态服从性能本质。
- **集中式 Master 而非全对等** [1.2]：段注册/副本/租约走 MasterService 集中管理（`master_service.cpp`）——用控制面集中换数据面完全去中心的零拷贝直传。

## 4. 与本库相邻单元对比

| 相邻单元 | 差异一句话 |
|---|---|
| [讲透LMCache](../讲透LMCache/deepwiki/INDEX.md) | LMCache 是 vLLM 生态的 KV 复用库（引擎内挂件）；Mooncake 是跨引擎的 KV 基础设施平台（vLLM/SGLang 皆接） |
| [讲透3FS](../../04-研/讲透3FS/README.md) | 3FS 在文件系统层做通用训练数据吞吐；Mooncake 在对象层做 KV 专用池化——存储层互补而非竞品 |
| DeepSeek V3.2 DSA 路线（[讲透DeepSeek-V3.2-Exp](../../04-研/讲透DeepSeek-V3.2-Exp/README.md)） | 两种省 KV 的路：DSA 把 KV 压小（算法侧），Mooncake 把 KV 搬走（系统侧） |

## 5. 建议去向

**留查区（L查·D3）**：推理引擎侧认知已由 02-透 的 vLLM/SGLang 覆盖，Mooncake 是 KV 基础设施侧互补原料，当前无重复蒸馏需求。若未来孵化 D5 通信存储教学单元（知识地图治理清单"学区断层"项），本仓 Segment 池化 + MultiTransport 是现成案例素材；TENT 动态路径选择是值得持续跟踪的演进线（4.2）。
