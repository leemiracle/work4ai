# 讲透 NCCL（NVIDIA/nccl）

> 上游知识基座，服务于 [讲透KCCL](讲透宇宙/03-查/讲透KCCL)（/usr-data/data2/kylin/kccl，
> 基于 NCCL API 生态的麒麟跨厂商集合通信库二次开发）。
> 本地仓：/usr-data/data2/kylin/nccl（官方 clone，v2.32.3-1-6-g3e46c089，2026-10-28 同步）。

## 流水线状态

| 步骤 | 状态 | 产物 |
| --- | --- | --- |
| DeepWiki 全量抓取 | ✅ 2026-10-28 | `deepwiki/`（58/58 结构页 100%，1.4M，MCP 通道一次过 exit 0，零 extra） |
| understand 图谱 | ✅ 2026-10-31 | 仓内 `.understand-anything/knowledge-graph.json`：**4306 节点/7631 边/16 层/16 步 tour**，validator 双跑 0 issues 0 warnings，fingerprints 723 文件基线@3e46c089（10-28 开跑、10-31 收官，中断两日断点续跑） |
| onboarding | ✅ 2026-10-31 | `onboarding/ONBOARDING.md`（5999 字 8 节 36 唯一行号锚，主会话独立抽验 8/8 命中） |
| explain | ✅ 2026-10-31 | `explain/` 12 篇（API 面/参数系统/生命周期/bootstrap/拓扑搜索/调优模型/传输框架/P2P 通道/net-IB/enqueue/proxy/设备 kernel） |
| infra 量化分析 | ✅ 2026-11-03 | `infra-quant/`（环形/树/协议交叉点/busbw 割集模型 vs 实测；工具库 ai-infra-tools） |
| **DeepSeek 论断验证** | ✅ 2026-11-03/04 | `verify-deepseek/`（把五份 explain 喂给 DeepSeek 的解析做**五层实验验证**：L1 静态 173 条 171 成立 + L2/L3/L5 行为实验全绿 + L4 GPU 代码就绪；活套件 `/usr-data/data2/kylin/nccl-verify-dsseek/`；**3 条勘误 + 1 条验证者自纠**〔首轮误判 `ncclparam -l` 为幻觉，复核翻案——CLI 真实存在〕见该目录 CLAIMS.md） |

## 口径说明（字数与锚）

- 字数采信**不计空格字符**口径：12 篇 4648-6141（组1/组3 落 4800 规格内，组2 漂至
  5.5-6.1K，与 zoo 轮 norm 一致；锚密度高是主因，70-85 锚/篇）。
- 行号锚 557 个全量终验 **0 坏**；组1 用全路径锚，组2/组3 混用裸 basename 锚
  （`p2p.cc:592` 形态），**按篇主题归位消歧**后验证（zoo 轮钉版口径）。

## 本轮源码级实证勘误（vs DeepWiki 快照/常见旧认知）

1. `nccl.h.in` 占位符是 **`${nccl:Major}` 风格非 `@xxx@`**：make 路径 sed 替换
   （`src/Makefile:159-165`），CMake 路径 `string(REPLACE)`（`src/generate_header.cmake:8-12`，
   注释明言为 Windows 兼容替代 sed）。
2. **param 系统双轨制**：遗留 `NCCL_PARAM` 宏（`src/include/param.h:21-31`）全库
   232 处仍是主力；2026 新 `DEFINE_NCCL_PARAM`（模板对象+C 跨 DSO 注册表）**10 处**
   （~~11 处~~，2026-11-03 verify-deepseek 全库 grep 实证修正——原 explain 参数系统篇
   误记 11，且 debug.cc 的 8 个中第 8 个在 :479 非 43-117 段），
   迁移刚起步。conf 优先级实证：进程 env > NCCL_CONF_FILE > ~/.nccl.conf > /etc/nccl.conf
   （`ncclOsSetEnv=setenv(...,0)` 不覆盖已有 env——verify-deepseek L3 实验3c）。
3. **`pnccl*` 符号非手写重复**：`PROFAPI` 下 `NCCL_API` 宏生成 weak `ncclXxx`+强别名
   `pncclXxx`（`src/include/core.h:15-21`），profiler 探桩机制。
4. **net_ib/gdr.cc 不是 GDRCopy**——它探测 GPUDirect RDMA 内核支撑（nvidia_peermem
   sysfs + DMA-BUF dummy 探测）；GDRCopy 本体绑定在 `src/misc/gdrwrap.cc`。
5. **`reduceScatterChunk` 在 v2.32.3 不存在**（全仓 grep 零命中）：`reduce_kernel.h`
   现为类型泛化 pack 框架（FuncSum/Prod/MinMax/PreMulSum/SumPostDiv + Apply_Reduce）。
6. **ibv 绑定无 weak symbol**：现行机制是 `ibvsymbols.cc` 符号表——
   `NCCL_BUILD_RDMA_CORE` 直链，否则 dlopen+dlvsym 按版本挑选（IBVERBS_1.1 基线）。
7. **net_ib 对 LL/LL128 协议完全无感知**：唯一耦合是 `net_ib/p2p.cc:80-81` 的
   128 字节写对齐（注释明言为 LL/LL128 而设）；协议本体在 device 侧。
8. **kernel 主体在 .h 头文件**（`src/device/all_reduce.h` 等由 generate.py 枚举展开），
   `common.cu` 仅 32 行入口壳。
9. **crypt.cc 是 2026 新增 TLS 层**：ncclSetEncryption PSK API + HKDF-SHA256 域分离
   + TLS1.3 单一套件 + OpenSSL3 全 dlopen 弱绑定 + 服务端 accept 三态裁决
   （错误密钥/明文 ClientHello/端口扫描一律丢弃连接保 accept 循环）。
10. bootstrap root 是**"婚介所"模型**（root 发送量 O(N)）、双向双环 AllGather（⌈N/2⌉
    步）、UID_STAGGER 错峰；运行期被约 16 个文件复用为控制面。

## DeepWiki 章节地图（12 章 58 页）

| 章 | 主题 | 对 KCCL 二开的参考价值 |
| --- | --- | --- |
| 1 Overview | 总览+社区 | ★★ |
| 2 Communicator Management | bootstrap/生命周期/split/配置 | ★★★ 2.1 bootstrap 对照 KCCL NetStore rendezvous |
| 3 Topology System | 硬件发现/XML/路径搜索/调优/建链 | ★★★ 3.4 建链对照 dense buffers |
| 4 Communication Pipeline | group/batching/任务调度/kernel 规划 | ★★★ |
| 5 Transport Layer | P2P/IB-RDMA/Socket/NVLS/proxy/CollNet/NetPlugin/GIN-RMA | ★★★★★ 5.3 IBverbs 对照 gloo ibverbs 后端；5.6 proxy 线程模型 |
| 6 Infrastructure | 内存/并发/socket 抽象/调试/profiler/RAS | ★★★★ |
| 7 Device-Side Execution | 集合 kernel/通信原语/对称内存 | ★★★★ 对照 nvthrust 单卡 reduce |
| 8 Build System | 编排/源码构建/配置/打包 | ★★ |
| 9 Plugin Ecosystem | profiler/tuner/env/gin 插件 API | ★★★ |
| 10 Bindings | nccl4py/LLVM-IR/EP 扩展/社区贡献 | ★★ |
| 11 Testing & Examples | 测试基础设施/示例 | ★★ |
| 12 Glossary | 术语表 | ★ |

## 与 KCCL 的关系（阅读指引）

- KCCL 导出 NCCL 风格 API（`nccl.h`，见 kccl include/），内部 dlopen 原厂
  libnccl.so 做组内同构通信；NCCL 的 bootstrap（2.1）↔ KCCL 的 NetStore（TCP KV rendezvous）。
- KCCL 组间跨厂商走 gloo（IB/TCP）；NCCL 自己的 IB 路径在 5.3，proxy 线程模型在 5.6，
  buffer 注册（CollNet/Registration）在 5.7——三条都是 host 中转 + MR 复用设计的对照系。
- NCCL 7.x 章的 ring/tree kernel 与 KCCL G2/G3 的"组内 Reduce→root 交换→组内 Bcast"
  是同一问题的不同切分。
