# 05 · 拓扑搜索引擎：src/graph/search.cc

## 一、角色定位

NCCL 初始化要回答：**给定真实互联拓扑，每个 channel 的数据按什么顺序流过哪些 GPU/NIC 才能吃满带宽？** `src/graph/search.cc`（1557 行）就是这个搜索引擎。它消费 `ncclTopoSystem`（topo.cc 经 XML/sysfs/NVML 探测构建的带权图，topo.h:46-56），产出 `ncclTopoGraph`——`intra[]`（每 channel 的 GPU rank 序列）与 `inter[]`（进出 NIC id），定义在 graph.h:174-192。init.cc 依次搜索五张图：ring/tree/collnetChain/nvls/collnetDirect（init.cc:1428-1465）。搜索本质是**带超时的贪心引导回溯**：解空间是 GPU 排列，靠打分排序与多级 timeout 在约一秒内收敛（全局预算 `1<<19` 步，search.cc:333）。

## 二、内部结构

**搜索前置**。`ncclTopoSearchInit`（search.cc:39）初始化 `system->maxBw/totalBw`：单 GPU 无网直接 `LOC_BW=5000.0`（topo.h:19）；否则取每个 DEV 到最远目标的最优路径带宽（`getMaxBw`:20）与自身 NVLink/PCI 链路聚合带宽（`getTotalBw`:30），init.cc:1399 调用。`ncclTopoComputeCommCPU`（search.cc:56）假设所有 CPU 同架构，取第 0 个 CPU 节点的 arch/vendor。

**带宽记账原语**。每次"尝试"都是沿路径预留/归还带宽：`followPath`（search.cc:81）逐链路扣减 bw（撤销传负数），内嵌三个硬件特例——Intel CPU RC 把 P2P 流量转 64B TLP 带宽乘 6/5（topo.h:44，用点 search.cc:90）；pre-Ampere GPU 需 1/8 反向带宽（search.cc:101-104）；POWER CPU 上 NVLink 需等量反向带宽（search.cc:105-108）。浮点误差用 `SUB_ROUND` 宏消除（search.cc:79）。`ncclTopoFollowPath`（search.cc:127）是记账入口：按 intra/inter 选带宽与类型门槛（search.cc:145-150），失败精确回退已扣步数（rewind，search.cc:169-172）。

**候选排序（收敛关键）**。`ncclTopoSearchNextGpuSort`（search.cc:254）为"下一块 GPU"排序：`cmpScore`（search.cc:202）按 interBw > interPciBw > interNhops > intraBw 优先级比较——**优先挑网络路径最肥的 GPU**。有 NVSwitch 时"邻居优先"（search.cc:294-325），因为 NVSwitch 偏好每 GPU 只与有限 peer 通信。

**递归主体**。pattern 语义注释在 search.cc:866-882（Ring=Split Tree Loop、Tree=Split Tree）：

- `ncclTopoSearchRec`（search.cc:897）：多机走 `ncclTopoSearchRecNet`；单机首条通道用 `FORCED_ORDER_PCI` 铺底（search.cc:910-913），后续通道先重放上一条（`FORCED_ORDER_REPLAY`，search.cc:915-919），`sameChannels==0` 才全枚举。
- `ncclTopoSearchRecNet`（search.cc:758）：轮转选 NIC（`(nChannels+i)%netCount`，search.cc:775），滤掉无 collSupport 与带宽不足者；占用时对同 asic/port 的 NIC 统一扣带宽（search.cc:786-791，模拟多通道共享物理口）。NVLS/COLLNET_DIRECT 只找 NIC→GPU head 组合并去重（search.cc:793-813）；普通模式先试本地 GPU 再试近邻列表（search.cc:832-848）。
- `ncclTopoSearchRecGpu`（search.cc:639）：`step==ngpus` 即排满一条 channel，`ncclTopoCompareGraphs` 判优后 memcpy 进 saveGraph（search.cc:650-661）。`step==backToNet` 分支回 NIC：`ncclTopoSelectNets` 取候选，`ncclTopoSearchCheckNet` 校验约束（search.cc:615-637：跨 plane 永禁、tree 要求对称 NIC、crossNic==2 时奇数通道交替 NIC）；BALANCED_TREE 在前两块 GPU 各记半带宽（search.cc:683-687）。NVLS 与 COLLNET_DIRECT 分别走 `ncclTopoSearchTryNvls`（search.cc:411，NVSwitch↔GPU 双向记账且本端权重 ×2）和 `ncclTopoSearchTryCollnetDirect`（search.cc:374，按 `1/(nGpu-1)` 分摊带宽，非 head rank 直接铺入 intra）。
- `ncclTopoSearchTryGpu`（search.cc:359）：单步三段式——FollowPath 预留 → `used` 位图翻转（search.cc:362）→ 递归 → 全部还原。回溯对称性是正确性根基。

**判优与主循环**。`ncclTopoCompareGraphs`（search.cc:446）依次比：nChannels 达标（search.cc:449）→ 偏好偶数通道（聚合带宽不劣时，search.cc:451-457）→ NVLS 越多越好（search.cc:459-464）→ `nChannels×bwIntra` 聚合带宽（search.cc:466-470）→ 同 pattern 下更少 hops（search.cc:473）。总控 `ncclTopoCompute`（search.cc:1151）：按 compcap 选速度档位表（`ncclTopoGetSpeedArray`:1130 分派默认/sm90/sm100/rubin 四张表，search.cc:1099-1128，Rubin 已到 280.8 GB/s 档）；`NCCL_GRAPH_FILE` 可整图导入 XML 跳过搜索（search.cc:1198-1209）；NVLS 需 NVSwitch 且 ccMin≥90（search.cc:1211）；双插槽 NVLink 分裂（QPI 互联）时强制 minChannels=2 让 Tree 有戏（search.cc:1229-1234）。主循环用 goto 阶梯重试：pass 1 依次尝试 different channels → 简化 BALANCED_TREE 为 TREE → 放宽 typeIntra/typeInter → 开 crossNic → 降速档（search.cc:1277-1329）；pass 2 有解后尝试升速（search.cc:1344-1364）。全灭时退化为"PCI 顺序直排 + bw=0.1"兜底通道（search.cc:1366-1388），保证 comm 永远建得起来。

**XML 与运行时查询**。`ncclTopoGetGraphFromXml`（search.cc:939）解析用户图，`ncclTopoGetXmlFromGraphs`（search.cc:1072）反向导出（`NCCL_GRAPH_DUMP_FILE`）；`ncclTopoDupChannels`（search.cc:1084）复制通道平分带宽。文件尾 `ncclTopoGetNetDev`（search.cc:1480）是运行时查询：按 channel 的 inter[] 取 NIC 并经 `ncclTopoGetIntermediateRank` 决定 proxy 中转 rank（`P2P_PXN_LEVEL` 默认 2，search.cc:1478；档位 2 要求 NIC 本地 GPU 到本 GPU 有 NVLink、到 NIC 有 PXB/P2C + GDR，search.cc:534-553）。

## 三、外部连接

include：comm.h/graph.h/topo.h/xml.h 等（search.cc:8-13）；核心数据依赖 topo.h 的 `ncclTopoNode.paths[][]`（预计算最短路，topo.h:158）与 graph.h 的 PATH 枚举（graph.h:114-152）。被调：init.cc:1393-1401（探测→算路→裁剪→再算路→SearchInit）与 init.cc:1428-1465 五张图的 `ncclTopoCompute`。运行期消费：`ncclTopoGetNetDev` 被 net.cc:309、coll_net.cc:176/198（传输 setup 定 NIC 与 proxy rank）、paths.cc:733（P2P 直连）调用。协作：topo.cc 提供探测入口 `ncclTopoGetSystem`（topo.cc:1989）与 `ncclTopoGetLocalNet`（topo.cc:2374）；graph/connect.cc、rings.cc、trees.cc 把 graph 转成 channel 级拓扑驱动 transport.cc 建连。

## 四、数据流

```
NVML/sysfs/XML 探测(topo.cc) → ncclTopoSystem{nodes[10类], paths[][]}
  → ncclTopoSearchInit: maxBw/totalBw                 [search.cc:39]
  → 每张图{pattern,min/maxChannels} → ncclTopoCompute [search.cc:1151]
      选速度档 → ncclTopoSearchRec
        → RecNet: 轮转 NIC + 扣 NIC 带宽              [search.cc:758]
        → RecGpu: NextGpuSort 排序 → TryGpu
            → ncclTopoFollowPath 扣/还链路带宽         [search.cc:127]
            → step==ngpus → CompareGraphs 判优         [search.cc:446]
      pass1 阶梯降级 / pass2 升速 / DupChannels 复制
  → ncclTopoGraph{intra[], inter[]} → PrintGraph/DumpGraphs(XML)
  → transport 层按 inter[] 选 NIC(ncclTopoGetNetDev)
```

带宽是贯穿始终的"货币"：搜索开始前链路/NIC 的 bw 是物理容量，FollowPath(+1) 预留、失败回退(-1)，saveGraph 留下最优方案下每通道的等分带宽。

## 五、设计决策

1. **超时预算而非完备搜索**：三级 timeout（1<<14 主搜 / 1<<8 sameChannels / 1<<19 全局，search.cc:333-336）+ "PCI 序铺底、打分排序、通道重放"三个加速器，承认组合爆炸现实——要一秒内的好解，不要分钟级最优解。
2. **带宽记账模拟物理争用**：直接在链路剩余带宽上加减（含 Intel TLP 6/5 开销、pre-Ampere 1/8 反向流、同 asic/port NIC 共享扣减），比"仅拓扑距离"更接近真实吞吐。
3. **速度档位表代替连续求解**：40→280.8 GB/s 的离散档位（search.cc:1099-1128）让"降速重搜"成为简单循环，同时天然适配代际硬件。
4. **图即数据、XML 即接口**：结果可序列化（`NCCL_GRAPH_DUMP_FILE`）再注入（`NCCL_GRAPH_FILE`），调优可脱离现场——真机 dump、离线改图验证。
5. **永不失败原则**：搜索全灭时落回 simple order + 0.1 GB/s 兜底（search.cc:1366-1388），把"建不出 comm"从拓扑问题降级为性能问题。

## 六、新人提示

- 开 `NCCL_DEBUG=INFO` + `NCCL_DEBUG_SUBSYS=GRAPH`，`ncclTopoPrintGraph`（search.cc:1398）逐 channel 打印 NET/GPU 序列与 bw/type；固定通道排布做实验用 `NCCL_TOPO_FILE`（系统拓扑 XML）与 `NCCL_GRAPH_FILE`（图 XML）。
- crossNic 三态（`NCCL_CROSS_NIC` 默认 2，search.cc:16）：0=严格同 rail、1=强制允许、2=自动（奇数通道交替 NIC）。多机排查"忽快忽慢"先查它。
- 日志里 typeIntra/typeInter 的 NVL/PIX/PHB/SYS 字符串直接反映通道走了什么硬件；出现 SYS 意味着跨 NUMA 的 QPI/UPI，性能显著掉。
- 改搜索逻辑务必保持 TryGpu/FollowPath 的加减对称，任何路径忘记回退带宽都会让后续通道可行性判断失真——此文件最易引入"偶发次优解"之处。
