# 视角 13：半导体市场/产品分析师（Market & Product Analyst）

> **审查时间**：2026-06-30
> **审查者**：councillor delegate（eager-emerald-otter），20 年服务器 CPU 市场分析经验（IDC/Gartner 半导体组）
> **方法**：read-only 审查商业化、竞品定位、TCO、市场份额维度

---

我已完成对项目的深度审查。**关键事实**：全仓 `grep` 显示"鲲鹏/Ampere/Graviton/Intel/SPEC2017/TCO/竞品/信创/定价"等关键词仅出现 13 次，且全部是技术 lens 里的**一笔带过引用**，**零独立市场分析文档**。

## 1. 视角定位

20 年服务器 CPU 市场分析老兵。我不看 GFLOPS——我看**这块芯片卖给谁、凭什么替代 incumbents、TCO 算不算得过来、生态能不能闭环**。本项目的工程深度是 A+，但作为商业化/产品文档是 **D**：它是优秀的工程实验记录，却完全没有回答"FTC862 在 ARM 服务器市场凭什么赢"这个核心商业问题。

## 2. 八大盲区（作为"产品技术白皮书"的硬伤）

| # | 盲区 | 证据 & 影响 |
|---|---|---|
| **B1** | **零竞品横向 benchmark** | 全仓无 FTC862 vs 鲲鹏 920 / Ampere Altra / Graviton3 / Xeon / EPYC 的同口径 GEMM/Attention 对比。"97.9% 峰值"——**没有参照系是孤证**。客户第一句永远是"比鲲鹏快多少？"，这里答不出。 |
| **B2** | **零 SPEC2017/SPECrate 数据** | 服务器 CPU 行业通用语是 SPEC，不是 GEMM GFLOPS。FTC862 8 核 SPEC2017 int_rate **完全缺失**（合理估算 ~120-160）。鲲鹏 920-6426 公开 ~1200+、Ampere Altra Max ~2200。客户/集采招标**直接卡死**在这一项。 |
| **B3** | **TCO 模型完全缺席** | 无 docs/TCO-MODEL.md。信创采购看 **3 年总拥有成本**。FTC862 单核 FP32 40 GFLOPS 但 8 核受 DDR4 双通道 51 GB/s 带宽墙拖到 170 GFLOPS（57% 效率），**能效 GFLOPS/W 无数据**，无法和 Ampere Altra（< 5W/核）拼绿色数据中心。 |
| **B4** | **零客户案例 / PoC 报告** | 无 case-study。真实采购决策需要"某政务云用 FTC862 跑 ResNet-50 推理，QPS=X，延迟 p99=Y"。项目 Attention 只到 N=1024 玩具级，**距离 Llama-7B 还差 90%**。 |
| **B5** | **市场定位表述混乱** | README 称"服务器级 ARM SoC"，但 8 核 + 双通道 DDR4-3200（51 GB/s）**根本不是 datacenter 级**（鲲鹏 920 是 8 通道 204 GB/s，Ampere 是 8 通道）。FTC862 真实定位应是**信创桌面/边缘推理/工业控制**，自抬到"服务器"会让懂行的采购方质疑专业性。 |
| **B6** | **定价 / BOM / 渠道策略零提及** | 无 docs/PRICING.md。FTC862 单颗芯片估价、整机 BOM、对标 Intel i3/i5 还是赛扬？信创集采的批量化折扣？全无。GFLOPS/$ 算不出。 |
| **B7** | **零市场份额 / 替代率数据** | 无 IDC/Gartner 中国 ARM 服务器出货量、信创替代率（2025 信创 x86→ARM 替代目标 ~30%）。无 FTC862 在边缘 AI 推理、车载、HPC 各细分的目标份额。 |
| **B8** | **SDK / 生态闭环断裂** | 38 个 `static` kernel、零 `.h`、零 `.so`——**可调用性=0**。竞品（鲲鹏 KAE、Ampere Optimized ML）都给客户可直接 `pip install` 的 SDK。 |

## 3. 改造建议

### 🔴 P0 — 补齐商业闭环（1-2 周）

**P0.1 新增 `docs/COMPETITIVE-LANDSCAPE.md`**：同口径对比表。

| 芯片 | 核/频 | FP32 peak/核 | 8核 GEMM 实测 | DRAM 带宽 | SPEC2017 int_rate |
|---|---|---|---|---|---|
| **FTC862 (本项目)** | 8@2.5G | 40 | **170 (tiled 4核 143)** | 51 GB/s | ~120-160 (估) |
| 鲲鹏 920-6426 | 64@2.6G | ~20.8 | — | 204 GB/s | ~1200 (公开) |
| Ampere Altra Max | 128@3.0G | ~48 | — | 204 GB/s | ~2200 |
| Graviton3 | 64@2.6G | ~41 (SVE) | — | 300 GB/s | ~1600 |
| Xeon 8380 (AVX512) | 40@2.3G | ~73.6 | — | 204 GB/s | ~1000 |

诚实结论：**FTC862 在多核吞吐上无法正面竞争 datacenter CPU，但单核 ML 算力密度（4 FVU）有差异化**。

**P0.2 新增 `docs/TCO-MODEL.md`**：3 年 TCO 对比 FTC862 边缘盒 vs Ampere Altra 云实例 vs Jetson Orin。需补能效实测。

**P0.3 新增 `docs/MARKET-POSITIONING.md`**：明确 FTC862 的 **3 个真实市场窗口**（见第 4 节）。

### 🟡 P1 — 销售赋能材料（2-4 周）

**P1.1 `docs/case-studies/`** 模板 + 首批 3 个：
- `resnet50-edge-inference.md`（INT8 80 GOPS 跑 CV 推理）
- `gov-cloud-信创替代.md`（政策驱动，非性能驱动）
- `industrial-control.md`（p99 延迟稳定）

**P1.2 `docs/PRICING-STRATEGY.md`**：GFLOPS/$ 推算 + 信创集采量价模型。

**P1.3 把 lens 10 的 SDK 化提到 P0**——无 `.so` 一切商业材料都是空中楼阁。

### 🟢 P2 — 市场情报（持续）

- `docs/MARKET-SHARE.md`：IDC China Server Tracker 季度数据
- `docs/CUSTOMER-INTERVIEW-TEMPLATE.md`：信创客户痛点访谈框架

## 4. 关键洞察

**4.1 本项目的真实商业价值 = 飞腾对外 PR 的"技术弹药库"**。
当前全网公开资料里，FTC862 的微架构参数（4 FVU、L2=512KB、L3 双段、DRAM=28GB/s 实测带宽）**几乎是零**。这份 lab 是**活的硬件百科**。它的最大用处不是卖芯片，而是：(a) 技术白皮书的硬数据来源；(b) 客户 PoC 时话术背书；(c) 招聘/生态布道。

**4.2 FTC862 在 ARM 服务器市场的真实定位 = 不是鲲鹏的对手，是它的补充**。
8 核 + 51 GB/s 带宽墙决定了 FTC862 **进不了主流 datacenter**。但 FTC862 有 **3 个真实可赢窗口**：
1. **信创政务云桌面/瘦服务器**——政策驱动，不拼绝对性能，拼"全国产 + 可控"。这是 FTC862 的主场，份额护城河。
2. **边缘 AI 推理**——INT8 80 GOPS/核 + 单核 Attention 6.58× 加速，对标 Jetson Orin / Rockchip RK3588，**性价比可能赢**（待 TCO 模型验证）。
3. **工业/车载**——`lens-latency` p99/p50=1.01× 极稳定，`lens-thermal` 20 秒负载 38°C 不降频，这是**实时性 + 低功耗**的杀手锏，Xeon/EPYC 完全不做。

**4.3 最致命的市场认知错位**：项目把自己框成"服务器 CPU 优化"，但 8 核 + 双通道 DDR4 的物理事实让它**够不着服务器**。应该 reframe 为**"国产边缘/信创算力 SoC 算子优化实验室"**——这样竞品从鲲鹏换成 Jetson/RK3588/晶晨，FTC862 反而是**性能领先方**，故事完全反转。**这是一行 README 修改带来的定位质变**。

## 5. 新增内容清单

| 文件 | 优先级 | 核心内容 |
|---|---|---|
| `docs/COMPETITIVE-LANDSCAPE.md` | **P0** | FTC862 vs 鲲鹏/Ampere/Graviton/Xeon/EPYC 同口径表 |
| `docs/TCO-MODEL.md` | **P0** | 3 年 TCO：边缘盒 vs 云 ARM vs Jetson |
| `docs/MARKET-POSITIONING.md` | **P0** | 3 个真实市场窗口 + reframe |
| `docs/PRICING-STRATEGY.md` | P1 | GFLOPS/$ + 集采量价 |
| `docs/case-studies/{resnet50,信创,industrial}.md` | P1 | PoC 案例模板 |
| `docs/MARKET-SHARE.md` | P2 | 季度份额追踪 |

---

**结论**：
- 作为工程实验：✅ **GO** — 98% 峰值、10+ 专家 lens、可复用方法论。
- 作为产品/商业文档：❌ **NO-GO（当前）** — 缺竞品、缺 TCO、缺案例、缺 SDK、缺定位。
- **最高杠杆单点改动**：**重构 README 定位**（从"服务器级"→"国产边缘/信创算力 SoC"），竞品从鲲鹏换成 Jetson/RK3588，**FTC862 立刻从追赶者变成领先者**——这是零成本的市场叙事翻转。
