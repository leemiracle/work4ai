# KCCL 多厂商链路量化对比 —— 用《深入理解 AI Infra》割集模型（含 2026-11-03 麒麟集群实测回填）

> 工具：`~/ai/ai-infra-tools/topology_cut.py`（--preset / --kccl-mixed 模式）。
> 对象：/usr-data/data2/kylin/kccl（麒麟多厂商 GPU 统一集合通信库，v2.32.3 NCCL 基座）。
> 姊妹报告：讲透NCCL/infra-quant/REPORT.md（单域 NCCL 深度对照）。2026-11-03。

## 1. KCCL 架构的通信模型（源码锚定）

KCCL 把一次跨厂商 AllReduce 拆成三段（`src/funcs/comminitrank.h` 厂商探测 → `kcclAllReduceG2/G3`）：

```
组内原厂归约 → 组长间 gloo AllReduce（RDMA/IB 或 TCP）→ 组内原厂广播
```

- 组 = 同厂商 rank 分组（NVIDIA `/dev/nvidia0`、沐曦 `/dev/mxcd`、天数 `/dev/iluvatar0`、海光 `gputype=="HG"`，`comminitrank.h:249-260`）
- 组内走原厂库（dlopen NCCL/MCCL），组间走 gloo 转发（README:12-13）

**这正是书 ch07「分层归约」的多厂商版**：机内高速域 + 跨域慢桥。割集模型给出一阶时间：

```
T ≈ max_group(2(g−1)/g · M / B_intra)  +  2(G−1)/G · M / B_bridge
```

## 2. 厂商互联带宽锚点（来源分级，勿混用官方与第三方口径）

| 预设 | 互联 | 单向带宽 | 来源 |
| --- | --- | ---: | --- |
| h100-nvl8 | NVLink4/NVSwitch | 450 GB/s | 书 §5 实测锚点（397.5）+官方 |
| b200-nvl8 | NVLink5 | 900 GB/s | 官方 |
| a100-nvl8 | NVLink3 | 312 GB/s | 官方 |
| metax-c550 | MetaXLink 8 卡全互联 | 448 GB/s | 沐曦官方 896 GB/s 聚合口径 ÷2 |
| metax-c500 | MetaXLink 4 卡 | 192 GB/s | **第三方评测**（ChaiTEX 2026-10，384 GB/s ÷2，官方未标注） |
| iluvatar-tg100 | PCIe Gen4 x16 Switch | 32 GB/s | 天数官方技术博客（64 GB/s 双向，无专用互联） |
| pcie-gen5 | PCIe Gen5 x16 | 64 GB/s | 书 §5 锚点 |

海光 K100 卡间互联无公开数值，未设预设（行业分析：国产互联普遍 <400 GB/s，除昇腾外）。

## 3. 场景矩阵（M=1 GiB AllReduce，一阶下界模型）

| 场景 | 组成 | 总耗时 | busbw 上界 | vs 纯 NVL8 基线 | 瓶颈 |
| --- | --- | ---: | ---: | ---: | --- |
| 基线：单域 | H100 NVL8 ×8 | 4.18 ms | 449.6 GB/s | 1× | 无（链路满载） |
| A：两厂商 RDMA 桥 | H100×4 + 沐曦C550×4 | 25.07 ms | 75.0 GB/s | **6.0×慢** | 组桥 21.5 ms（86%） |
| B：两厂商 TCP 桥 | 同上，100GbE | 89.49 ms | 21.0 GB/s | **21.4×慢** | TCP 桥 85.9 ms（96%） |
| C：三厂商含弱组 | H100×4+C550×2+天数×2 | 62.19 ms | 30.2 GB/s | 14.9×慢 | 最弱组内 33.6 ms（天数 PCIe）> 桥 28.6 ms |

复现：
```bash
T=~/ai/ai-infra-tools
python3 $T/collective_model.py --n 8 --bytes 1073741824 --bw 450e9 --alpha-us 0.24   # 基线
python3 $T/topology_cut.py --kccl-mixed nvidia:4,metax-c550:4 --bytes 1073741824 --bridge 50e9
python3 $T/topology_cut.py --kccl-mixed nvidia:4,metax-c550:4 --bytes 1073741824 --bridge 12.5e9
python3 $T/topology_cut.py --kccl-mixed nvidia:4,metax-c550:2,iluvatar-tg100:2 --bytes 1073741824 --bridge 50e9
```

## 4. 结论（数据搬移五问口径）

1. **混合域 AllReduce 的有效带宽 = min(桥带宽, 最弱组内带宽) 主导**——场景 C 中天数 PCIe 组
   （32 GB/s）把整个 8 卡联盟拖到 30 GB/s，比 RDMA 桥（50 GB/s）更先成为瓶颈割集。
   "组内原厂高速"救不了"联盟里有短板"。
2. **桥的字节量是不可消除项**：组长间 gloo AllReduce 每组长仍要发 2(G−1)/G·M——混厂商
   大消息训练的通信代价天然比同构 NVLink 域高一个数量级（6-21×）。工程含义：跨厂商训练
   应把并行策略尽量限制在厂商域内（组内 TP/DP，组间只做低频梯度同步或参数服务器）。
3. **TCP 桥只适合小消息/控制面**：100GbE TCP 把 busbw 压到 21 GB/s（96% 时间在桥上），
   与 RDMA 桥差 4 倍——KCCL 组间走 gloo 时传输选择（RDMA vs TCP）是第一性能开关。
4. **口径警示**：沐曦 C500 的 384 GB/s 来自第三方评测、官方 896 GB/s 是 C550 聚合口径，
   换算单向时必须 ÷2 并标注来源——不同来源口径混用会得出 2 倍级误差的结论（书方法论：
   不把标称聚合带宽当单流带宽）。

## 5. 局限

- 一阶模型：组内/组桥按串行求和（KCCL 两阶段实现的保守估计）；若组内 reduce 与组桥
  流水重叠，实际耗时介于 sum 与 max 之间。
- 未建模：gloo 协议栈 CPU 开销、跨厂商 dtype 对齐转换、组长单点 incast。
- 厂商带宽为标称值；实际部署应以 nccl-tests/mccl-tests 实测回填（busbw_table.py 算利用率）。

## 6. 实测回填（2026-11-03 麒麟集群真机，部分完成）

集群：10.44.11.13=沐曦 C500×4（x86_64）、10.44.11.14=天数 CoreX×4+沐曦×1（aarch64）、
10.44.11.18=海光 K100_AI×1。原始日志：nccl 仓 `infra-analysis/measured/`。

### 6.1 单厂商组内实测（已完成）

| 平台 | 工具 | 大消息 busbw 渐近 | 小消息延迟 | 对照 §2 预设 |
| --- | --- | ---: | ---: | --- |
| 4× 沐曦 C500（MCCL 2.31 官方 mccl_tests） | all_reduce_perf float 8B-1G | **100.1 GB/s @1GB**（98.1@128MB） | ~7.5 µs（64B-8KB 平台期） | 预设 192 → **修正**：第三方"4 卡 384 GB/s"系聚合口径（÷4≈96/卡），实测 100.1=104% 满载 ✓ |
| 4× 天数 CoreX（KCCL 2.28.9 单组透传=天数 libnccl） | kccl_cross_bw 自研 1KB-64M | **22.6 GB/s @64MB**（21.1@16MB） | ~55 µs（比 C500 高 7×） | 预设 32（PCIe Gen4 单向）→ 利用率 70%，PCIe 典型效率 ✓ |
| 海光 K100_AI×1 | — | N/A（单卡无集合通信） | — | RCCL 2.22.3+IB MT4123 环境已记录 |

要点：
- **C500 实测直接校准了预设口径**——4 卡 MetaXLink 的"384 GB/s"必须按聚合÷4 而非双向÷2，
  busbw 渐近 100 GB/s 就是该 4 卡域的链路容量（割集模型里的 B_intra 实测值）。
- C500 全曲线在 128KB 处有延迟台阶（22µs vs 邻点 11/18µs）——MCCL 算法/协议切换点，
  与书 §7.2.2 的 M*=αB 交叉点机制同构。
- 天数小消息 55µs 延迟主导（PCIe Switch 无 NVLink 级直连），印证 §4 结论"弱组拖累"。

### 6.2 跨厂商混合域（框架就绪，握手未通）

自研 kccl_cross_bw（带宽矩阵版，无 MPI，KCCL_COMM_ID 婚介）已部署双端并完成
**单机验证**；跨机（13 沐曦组 rank0-3 + 14 天数组 rank4-7）TCP 层已通
（14→13:31512 ESTAB 实证），但 gtype 交换卡死——根因是 13 端库版本宏 21605
（CMake 缓存未刷新）与 14 端 22809 协议不一致。**重试路径**：13 上清 CMakeCache
全量重编对齐 22809 后，双端 `bash /tmp/start13.sh` / `bash /tmp/start14.sh`
（注意 13 的 /tmp noexec 须解释器派发）。13 节点留有 kccl-22809-NOTE.md 公告。

### 6.3 预期与校验点（混合域重试时）

混合域实测应落在 §3 一阶模型的 sum（保守）与 max（并行下界）之间；本集群的一阶预测
（替换预设为实测值：沐曦组 100 GB/s、天数组 22.6 GB/s、桥=IB MT4123 ≈ 40Gb IB）：

```
T ≈ max(2·3/4·M/100e9, 2·3/4·M/22.6e9) + 2·1/2·M/B_bridge
  = 0.0667·M/1e9 s（天数组内主导）+ M/B_bridge
```

若低于 max 下界 → 组间有额外序列化（ag0.log 实锤的 ibv_reg_mr 回退 host copy 即首要嫌疑）。

---

## 7. 实测回填（✅ 2026-11-03 真机，13/14/18 三节点）

集群：**13=10.44.11.13（x86_64，沐曦 MetaX C500×4，MACA 2.31/3.9.1 + MCCL）**、
**14=10.44.11.14（aarch64，沐曦×1 + 天数 CoreX×4 + RTX4090，corex-4.4/5.0）**、
**18=10.44.11.18（海光 K100_AI×1，DTK 26.04.1 + RCCL 2.22.3 + IB MT4123）**。

### 7.1 单厂商域实测（MCCL 原厂 all_reduce_perf，20 iter 均值）

**4×沐曦 C500（13 节点，机内）**：

| 消息 | busbw (GB/s) | 备注 |
| ---: | ---: | --- |
| 8 MB | 82.6 | |
| 64 MB | 95.8 | |
| 256 MB | 99.3 | |
| **1 GB** | **100.1** | 渐近；小消息延迟 ~7.5 µs；128 KB 处有算法切换台阶（21→22 µs） |

**4×天数 CoreX（14 节点，KCCL 透传原厂，PCIe Gen4 Switch）**：

| 消息 | busbw (GB/s) | 备注 |
| ---: | ---: | --- |
| 1 MB | 11.2 | |
| 16 MB | 21.1 | |
| **64 MB** | **22.6** | 渐近；小消息延迟 ~54 µs（C500 的 7 倍） |

### 7.2 实测 vs 一阶模型校准

| 平台 | §2 锚点（单向） | 实测 busbw 渐近 | 校准结论 |
| --- | ---: | ---: | --- |
| 沐曦 C500 ×4 | 192 GB/s（第三方评测 384÷2） | 100.1 GB/s | **评测"4 卡 384 GB/s"是聚合口径**：每卡方向容量 ≈96 GB/s，实测 100.1=104% 打满——preset 校准为 96 |
| 天数 CoreX ×4 | 32 GB/s（PCIe Gen4 官方） | 22.6 GB/s | 71% 利用率；缺口=PCIe 共享 switch + KCCL 透传层 |
| H100 NVL8（对照，官方表） | 450 GB/s | 484 GB/s | 107%——双向环（§姊妹报告） |

**跨厂商带宽鸿沟实测坐实**：沐曦域内 100 GB/s vs 天数域内 22.6 GB/s——同一集群混部时
**最弱组把联盟整体拖到 ≤22.6 GB/s**，与 §4 结论 1（min(桥,最弱组) 主导）一致；
且天数组小消息延迟 54 µs 是沐曦组 7.5 µs 的 7 倍，小消息 AllReduce 联盟延迟也被最弱组锁死。

### 7.3 跨机跨厂商混合域：CommInitRank 死锁（工程发现，未跑通）

场景：13 端 4×沐曦（rank0-3）+ 14 端 4×天数（rank4-7），KCCL_COMM_ID=10.44.11.13:31999。
**结果：8 rank 全部死等**（gdb 钉到符号级）：

1. **首因（已修未解）**：两端 libkccl 版本/协议不一致——14 端新版有 `kccl_exchange_caps`
   （NetStore `comm` 命令），13 端旧版 x86 无此协议 → 14 端 `NetStore::comm` recv 永等。
   已把 14 端源码传 13 重编 x86 版（协议对齐）。
2. **次因（当前卡点）**：协议对齐后仍互锁——14 端卡 `kccl_exchange_caps→NetStore::comm recv`，
   13 端卡 `gloo tcp createAndConnectAllPairs→NetStore::comm recv`，两端同时等 rank0 内嵌
   NetStore server 响应；疑似 **NetStore server 单线程处理 comm 时与 HashStore wait 互锁**。
3. 架构坑：14 是 aarch64、13 是 x86_64——libkccl 不可跨节点二进制通用，必须各端同源码编译。

**给 KCCL 的修复建议**：① comm 命令加协议版本协商（版本不匹配快速失败而非死等）；
② NetStore server 多线程/请求超时；③ CommInitRank 全程加超时+诊断输出。
辅助发现：`KCCL_DISABLE_IB=1` 后 gloo 线程栈仍见 `ibverbs::Device::loop`（开关疑似未全生效）；
`KCCL_GPU_TYPE` 自动探测函数缺 return（README 已警示，实测必须显式设置）。

### 7.4 复现命令

```bash
# 沐曦组内（13 节点，原厂工具）
export M3=/opt/maca-3.9.1; export LD_LIBRARY_PATH=${M3}/lib:${M3}/ompi/lib:/opt/maca-2.31.0/lib
${M3}/ompi/bin/mpirun -n 4 --allow-run-as-root -mca btl self,tcp \
  /opt/maca-2.31.0/samples/mccl_tests/perf/tests/all_reduce_perf -b 8 -e 1G -d float -f 2 -g 1 -t 1 -n 20 -w 5
# 天数组内（14 节点，本报告新增 kccl_cross_bw，源码在 kccl 仓 test/）
KCCL_COMM_ID=127.0.0.1:31999 KCCL_GPU_TYPE=TS KCCL_DISABLE_IB=1 KCCL_USE_GPU_PEERMEM=0 \
KCCL_GPU_RUNTIME_LIB=<corex>/lib64/libcudart.so KCCL_ORIGIN_COMM_LIB=<corex>/lib64/libnccl.so.2 \
LD_LIBRARY_PATH=<corex>/lib64:/root/kccl/build ./kccl_cross_bw <r> 4 <dev>   # r=0..3
```

## 8. C500 PCIe Gen5 通路实测（✅ 2026-11-03，13 节点）

问题：C500 的 LnkCap 是 Gen5 x16，但集合通信走 MetaXLink——PCIe 通路代次需独立实测。
工具：`kccl/test/h2d_bw.cpp`（dlopen libmcruntime 解析 mc* API，头文件无关版）。

| 路径 | 实测带宽 | 判读 |
| --- | ---: | --- |
| H2D pageable 1GB×20 | 33.0 GB/s | staging buffer 限制（≈Gen4 峰值，假信号） |
| **H2D pinned** | **48.5 GB/s** | 真 PCIe 通路 |
| **D2H pinned** | **53.0 GB/s** | 53 > Gen4 物理上限 32 → **Gen5 实际激活**（53/64=83% 典型实效） |

链路铁证：负载中 `lspci -vv` LnkSta = **Speed 32GT/s (ok), Width x16**；sysfs
current_link_speed=32.0 GT/s PCIe。三证据链闭环（LnkCap 能力→LnkSta 协商→带宽物理超 Gen4）。

方法论注：**pageable 拷贝测 PCIe 代次是经典假信号**（33 GB/s 恰=Gen4 峰值纯属 staging 巧合），
必须 pinned；NCCL 侧无需任何配置（topo.cc:625 kvDictPciGen 表 Gen1-6 全覆盖，sysfs 自动探测）。
