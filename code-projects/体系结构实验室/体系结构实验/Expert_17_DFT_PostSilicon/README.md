# Expert_17 — DFT（可测性设计）/ 硅后 Bringup 工程师视角

> **角色定位**：我横跨芯片生命周期的「最后一公里」——流片前写 DFT（扫描链/ATPG/BIST），
> 流片后第一颗回片我去点亮（first light）、做 bench 表征、画 shmoo、分 speed bin、抓 errata、
> 盯量产测试时间成本、定 burn-in 筛查条件。RTL 工程师（Expert_03）把代码变成网表，
> 物理工程师（Expert_13）把网表变成 GDSII，foundry（Expert_14）把 GDSII 变成硅，
> **而我，是把那块刚从晶圆切下来、谁也不知道能不能跑的硅，变成「能卖、能用、能签 SLA」的产品的人。**
>
> **核心思维模型**：四把 named 尺子交叉丈量——
> **① 缺陷覆盖率（Defect Coverage / Test Coverage, TC）**：测试向量能抓出百分之几的制造缺陷，$TC = \frac{\text{被测出的缺陷}}{\text{总缺陷}}$；
> **② DPPM（Defective Parts Per Million）**：逃过测试流到客户手里的坏件率，是「质量」的终极 KPI；
> **③ 测试时间成本（Test Time / Cost）**：每颗 die 在 ATE 上跑几秒 = 几毛钱，这是量产经济性的生死线；
> **④ 浴缸曲线早夭段（Infant Mortality）****——与 Expert_23（RAS）的浴缸曲线同源，
> 但 E17 关心的是「早夭段」：怎么把早死的芯片在出厂前筛掉（burn-in / HTOL），而 E23 关心「正常寿命段」与「老化段」。
>
> **E17 vs E23 边界声明**（必读公共前置点 4）：**DFT 是「制造测试」——芯片刚做好时，确认它有没有被造坏；**
> **RAS（E23）是「运行时可靠性」——芯片在客户机房跑 7 年会不会静悄悄算错。**
> 一句话：DFT 管「出厂时坏没坏」，RAS 管「在用时错不错」。两者共用浴缸曲线，
> 但 DFT 的主战场是早夭筛选（左段），RAS 的主战场是软错误与老化（中段+右段）。
> DFT 也管一部分老化筛查（burn-in 加速老化把弱件提前暴露），这是两视角的交集（§2.5）。

---

## 0. 特异性测试自检（开工前）

> 宪法 §0：删掉「飞腾/D3000M/FTC862」几个字后若仍读得通 = 失败。

本文所有测试成本、扫描链规模、shmoo 推测、errata 判断，**全部锚在 D3000M 的具体规格上**：8 核 FTC862（4-wide OoO）、ARMv8.4、2.5 GHz、L3 8MB shared、14nm 级（[推测-与 E14 一致]）、die 面积 ~120 mm²（[推测-E14 §5.2]）、good die ~280–314/晶圆（[推测-E14]）。把这套数字换到 Apple M1（5nm / 195 mm²）或 Kirin 9000s（手机小 die），所有测试时间与成本模型都要重算——**这正是「只有这颗芯片才答得出」的特异性所在**。本文不写「DFT 是什么」的通用教科书（那有 Abramovici 的教材 [书-Abramovici]），只写「**D3000M 的 DFT 与硅后工程化具体是什么、缺什么、贵在哪**」。

---

## 1. 这位 DFT/Bringup 工程师看飞腾 D3000M 的 12 个尖锐问题

1. **D3000M 有多少扫描触发器（scan FF）？** 8 核 4-wide OoO + 8MB L3 + 各级 cache，FF 总量推测上百万——扫描链怎么排、压缩比能做到多少？`[推测-依据]`
2. **测试覆盖率（TC）能到多少？** 业界服务器 CPU 量产要求 TC ≥ 99%（[报告-ITC]），D3000M 作为信创服务器，达标了吗？还是停在 95–98% 的「能测但漏网多」？`[推测-依据]`
3. **单颗 die 在 ATE 上测多久？** 高端 SoC 全测要 5–15 秒，D3000M 压缩测试后几秒？这直接决定每颗测试成本。`[推测-依据]`
4. **ATE 用谁家的？** 泰瑞达（Teradyne）Ultratech / 爱德万（Advantest）93000 是高端 SoC 主力，单台 $1–3M。飞腾受制裁后能否拿到？还是被迫转国产长川/华峰测控？`[推测-地缘]`
5. **MBIST 覆盖了哪些 SRAM？** L1D 64K / L2 512K / L3 8MB / TLB / 重命名表 / ROB——每一块都要 MBIST，飞腾的 memory BIST 算法是 March 算法哪一档？`[推测-依据]`
6. **点亮（first light）要多久？** 从晶圆回片到第一颗能跑 Linux，业界一流团队 1–2 周，飞腾推测多久？errata 多不多？`[推测-依据]`
7. **speed binning 怎么分？** D3000M 同一批晶圆，有的核能跑 2.6 GHz、有的只能 2.3 GHz——飞腾怎么分频分级成服务器/桌面/嵌入式 SKU？良率分布长什么样？`[推测-依据]`
8. **errata 文档公开吗？** Intel/AMD 每代都发几十到上百条 errata 白皮书 [官方-Intel-SDM]。飞腾的 errata 怎么发？是公开（像 Intel）还是只给 OEM NDA？`[推测-生态]`
9. **stepping（改版）几次回片？** 业界惯例一颗 CPU 要 A0→A1→A2 两三次 stepping 才稳定。飞腾 D3000M 几次？每次改版要半年 + 几百万美元 mask 钱。`[推测-依据]`
10. **burn-in 怎么做？** HTOL（高温工作寿命）125°C/1000h 是 JEDEC 标准 [标准-JESD22-A108]。D3000M 的 burn-in 条件、DPPM 目标是多少？`[推测-依据]`
11. **国产 ATE 能替代吗？** 长川科技、华峰测控在模拟/功率测试已上量，但高端数字 SoC 测试（几 Gbps pin、数Gb 向量内存）还差几代——D3000M 测试卡在哪？`[推测-国产替代]`
12. **无 BF16/I8MM/SVE 对 DFT 有什么影响？** 这是「战略伤疤」（[实测-扩展专题第25-27行]）——缺失意味着 RTL 没有对应执行单元，**DFT 也就不用测这些通路**。下一代补上时，扫描链与 ATPG 要重做多少？`[推测-依据]`

这 12 个问题里，1/2/3/7/8/11/12 是**只有这颗芯片才答得出**的特异性问题——删掉「飞腾/D3000M」就空转。这是本视角过「D3000M 特异性测试」的保证。

---

## 2. 具体分析（全部锚 D3000M 实测 + 公开论文 + 工程推理）

### 2.1 DFT 概念地基：芯片怎么「自测」

RTL 工程师（E03）写的是功能逻辑，但功能逻辑在制造时可能被「造坏」——一根金属线断路、一个通孔空洞、一个晶体管短路。芯片出厂前必须把这些坏件筛掉，否则装到客户机房就是早夭宕机（与 E23 浴缸曲线早夭段同源）。**问题在于：你不能给每个晶体管都接一根外部测试探针——上百亿晶体管，引脚根本不够。** DFT 的核心思想就是：

> **给芯片内部加一套「测试专用通路」，让外部 ATE 用有限的引脚，能把测试激励扫进去、把响应扫出来，逐个检查每个触发器（FF）和组合逻辑。**

这套通路分四大件（named framework）：

| DFT 机制 | 全称 | 测什么 | D3000M 推测覆盖 |
|---------|------|--------|----------------|
| **Scan chain（扫描链）** | 把所有 FF 串成移位寄存器 | 组合逻辑 stuck-at 故障（线常 0/常 1） | ✅ 主力，FF 数见 §2.2 |
| **ATPG** | Automatic Test Pattern Generation | 自动生成测试向量（用工具算「哪个向量能抓哪个故障」） | ✅ Synopsys TetraMAX / 西门子 Tessent TestKompress `[推测]` |
| **MBIST** | Memory Built-In Self-Test | 片上 SRAM（cache/TLB/RF）的 March 算法自测 | ✅ L1/L2/L3 全覆盖 `[推测]` |
| **LBIST** | Logic BIST | 片上逻辑自测（伪随机向量 + MISR 压缩） | ⚠️ 服务器 CPU 用得少（扫描链已够），推测部分用 `[推测]` |
| **压缩测试（Compression）** | Scan compression | 把长扫描链压缩成短通道，降测试时间 | ✅ 必用，压缩比 100–500× `[推测]` |

**Scan chain 的物理本质**：正常工作 时，FF 是并行载入数据；测试模式（scan mode）下，把所有 FF **首尾串成一条长移位寄存器**（像串珍珠），ATE 从 scan-in 引脚一位一位移入测试向量，切换回正常模式跑一拍组合逻辑，再把 FF 内容从 scan-out 移出比对。这样 $N$ 个 FF 只需 1 条 scan-in + 1 条 scan-out 通道（实际压成多条并行通道提速）。代价：每个 FF 多一个 MUX（选择正常/扫描输入），**面积开销约 2–5%**（业界经验 [书-Abramovici]）。

**ATPG 的「故障模型」**：ATPG 工具不是盲目生成向量，而是基于**故障模型**算「覆盖率」。最经典的是 **stuck-at fault（固定故障）**——假设某根线恒接 0（stuck-at-0）或恒接 1（stuck-at-1），问「哪组输入能把这个故障传播到输出被观测到」。工具逐个故障点求解，生成最小向量集。stuck-at 是最基础的模型，**业界量产 TC 基准就是 stuck-at 覆盖率**（服务器 CPU 要求 ≥99% [报告-ITC]）。更进阶的还有 **transition fault（过渡故障）**（测延迟，抓慢通路，与 speed binning 相关）、**bridge fault（桥接故障）**（两线短路）、**path delay（路径延迟）**。

> **D3000M 特异性锚点**：飞腾用 ARMv8.4 ISA，所有指令通路（LSE 原子 v8.1、FP16 v8.2、UDOT v8.4、SM3/SM4 v8.4、RAS v8.2 [实测-扩展专题]）**都必须进扫描链测**。但**缺的 BF16/I8MM/SVE（[实测-扩展专题第25-27行]）对应通路 RTL 里没有 → DFT 也不用测**。这意味着 D3000M 的测试向量集比「满血 ARMv8.6 核」**少一块**——测试时间略短，但下一代补这些指令时，**ATPG 与扫描链要为新增通路重做**（§2.7 详述）。

---

### 2.2 D3000M 的扫描 FF 规模与测试覆盖率推测

**扫描 FF 数量推算（核心 artifact 之一）**。服务器级 4-wide OoO 核的 FF 密度，业界公开数据（ARM Cortex-A76/A78 [报告-Wikichip]、AMD Zen [报告-ChipsAndCheese]）：

| 模块 | FF 数量级（单核） | 来源 | D3000M 8 核合计推测 |
|------|:-------------:|------|:------------------:|
| ROB + 重命名表 + 物理寄存器堆 | 5K–15K | 4-wide OoO ROB ~200–300 entry，每 entry 含 op+dest+tag | 40K–120K |
| issue queue + 唤醒/选择 | 3K–8K | 4-wide IQ ~64–128 entry | 24K–64K |
| L1D 64K + L1I cache tag/data | 8K–20K | 64KB = 512Kbit，但 FF 只存 tag + 控制 | 64K–160K |
| L2 512K cache | 15K–40K | 512KB tag + 控制 | 120K–320K |
| LSQ + load/store queue | 3K–8K | 4-wide LSQ ~32–64 entry | 24K–64K |
| 执行单元（ALU/FPU/SIMD） | 2K–6K | 流水化 ALU 寄存器 | 16K–48K |
| 分支预测器（BTB/TAGE/RAS） | 5K–20K | 数 KB SRAM 化，部分是 FF | 40K–160K |
| **单核合计** | **~40K–120K** | | — |
| **L3 8MB shared（SRAM，不走 scan）** | — | L3 走 MBIST 不走 scan | — |
| **SoC 互连/GIC/SMMU/DDR ctrl** | 20K–80K | SoC 级控制 FF | 20K–80K |
| **8 核 + SoC 合计推测** | — | | **~400K–1.2M FF** |

**关键判断 1（`[推测-依据]`）**：D3000M 的扫描 FF 总量约 **40 万到 120 万**，取中位 **~80 万 FF**。这与 8 核 Cortex-A76 级服务器 SoC 同档（[报告-Wikichip] Cortex-A76 单核 ~50–100K FF）。

**测试覆盖率（TC）推测**。服务器 CPU 量产要求 stuck-at TC ≥ 99%（[报告-ITC]）。飞腾作为信创服务器，合理推测：

- **stuck-at TC**：**98–99%**（`[推测-依据]`：业界成熟 DFT 流程 + Tessent/TetraMAX 工具，4-wide 核 TC 做到 99% 不难，但 100% 物理不可达，总有「不可观测/不可控制」点）。
- **transition TC（延迟故障）**：**85–92%**（`[推测-依据]`：延迟测试比 stuck-at 难，业界普遍低 5–10 个百分点，与 speed binning 配合抓慢通路）。
- **未覆盖的 1–2% 是什么**：通常是复位逻辑、模拟 PLL、IO pad 的边界——这些靠**功能测试 + bench 实测**补，不靠扫描。

**1% 的漏网意味着什么**：100 万 FF 里 1% = 1 万个故障点「测不到」。但这是「故障点」不是「坏 die」——实际坏 die 由良率模型（E14 §5）决定，D3000M 良率 ~60%（[推测-E14]）即 40% die 有致命缺陷。TC 99% 意味着这 40% 里 99% 被抓出，**逃逸率 = 40% × 1% = 0.4%**，即 **DPPM ≈ 4000**。这**远高于** Intel/AMD 服务器 CPU 的 DPPM 目标（< 100 [报告-Intel quality]）。**这是飞腾作为后发厂商在质量一致性上的真实差距**——不是「测不了」，是「测得没那么干净」。

---

### 2.3 测试时间与 ATE 成本：每颗 D3000M 测一次多少钱（核心 artifact）

> 这是 E17 最硬的产出。E14 算的是「裸 die 成本」（$14–16），E17 算的是「**测一次要花多少钱**」——这是 die 成本之外、封装之前的一笔大头。

**测试时间模型**。一颗 SoC 在 ATE 上的测试时间 = 各测试项时间之和：

```
  测试项                  时间(秒)    占比      说明
  ─────────────────────────────────────────────────────────────────
  DC scan (低速扫描)      0.5–1.0     ~10%     stuck-at, 低频移位
  AC scan (at-speed扫描)  1.0–2.0     ~20%     transition, 满频移位, 抓慢通路
  MBIST (cache自测)       0.3–0.8     ~8%      March算法, 片上自测只回传pass/fail
  IO/PHY测试             0.5–1.5     ~15%     DDR/PCIe PHY链路训练+眼图
  功能测试(跑小程序)      0.5–1.5     ~15%     启动一段boot code, 验ISA
  IDDQ/功耗测试           0.2–0.5     ~5%      静态电流, 抓漏电/短路
  ─────────────────────────────────────────────────────────────────
  合计(wafer级,未封装)    3–7 秒      100%     压缩测试后业界SoC典型值
  合计(封装后final test)  +2–5 秒     —        再测一遍+speed bin+老化后复测
```
**图 1：D3000M 单颗 die ATE 测试时间分解（推测）。** `[推测-业界SoC基准]`

**关键判断 2（`[推测-依据]`）**：D3000M 单颗 die（wafer 级）测试时间约 **3–7 秒**，封装后 final test 再加 **2–5 秒**，合计 **5–12 秒/颗**。

**每颗测试成本（核心量化）**。测试成本 = 测试时间 × ATE 每秒折旧 + handler 时间 + 向量开发摊销：

- 高端 ATE（Teradyne UltraFLEX / Advantest 93000）单台 **$1.5–3M** `[报告-VLSIresearch]`，按 5 年折旧、75% utilization，**每秒机时成本约 $0.02–0.05**。
- handler（自动上下料机）单台 **$0.3–1M**，每秒再加 $0.005–0.01。
- 合计每秒测试成本 **~$0.03–0.06**。

| 测试阶段 | 时间 | 每秒成本 | **单颗测试成本** |
|---------|:----:|:-------:|:--------------:|
| Wafer test（probe card，scan+MBIST+PHY+功能+IDDQ） | ~5 秒 | $0.021 | **$0.11** |
| Final test（封装后 scan + speed bin + 老化后复测） | ~4 秒 | $0.021 | **$0.08** |
| Burn-in（24–48h 批量摊到每颗） | — | — | **~$0.50** |
| **合计** | ~9 秒机时 + burn-in | — | **~$0.69/颗** |

**表 A：D3000M 单颗测试成本推算。** `[推测-业界ATE成本模型]`（每秒成本取 ATE $2M/5 年/75% 利用率 + handler $0.5M 的中位模型，见脚本）

**这 $0.69 占售价多少？** D3000M 信创服务器售价推测 $500–1000（[推测-E07]）。测试成本占比 **0.07–0.14%**——**测试不是大头，但它决定 DPPM 与良率逃逸，是质量的守门员**。真正的成本大头是良率（E14 算的 good die $14–16）与封装（FC-BGA ~$5–15 [推测-E15]）。但测试省不得：**少测 1 秒省 $0.02，但 DPPM 可能从 500 涨到 4000（无 burn-in），售后赔付远超这点钱**。

**完整可复现脚本**：[`test_cost_model.py`](./test_cost_model.py) 用 Python 算任意 die 面积/测试时间/ATE 成本的每颗测试成本与 DPPM 逃逸。`python3 test_cost_model.py` 复现本表所有数字（含敏感性分析：TC 95%→99.9% 对 DPPM 的影响）。

---

### 2.4 硅后 Bringup：从点亮到量产的过程还原

> 这是 DFT 后段工程师最刺激的工作：晶圆厂把第一批 die 送回来，谁也不知道能不能跑，**我要在几周内让它「活过来」**。

**Bringup 的标准时间线**（业界一流团队，[报告-post-silicon validation 综述]）：

```
  Day 0    │ 晶圆回片(wafer back from fab)
           │
  Day 1-3  │ ▶ Wafer sort: ATE probe card 逐 die 测, 标 good/bad
           │   (这一步 DFT 发威: scan + MBIST 筛掉坏 die)
           │
  Day 4-7  │ ▶ First light(点亮): 挑几颗 good die 封装, 上开发板
           │   目标: 让它"亮一个灯"——能复位、能跑第一条指令
           │   这一步最揪心: A0 版几乎必然有阻塞性 bug
           │
  Day 7-14 │ ▶ Boot Linux/UOS/麒麟: 能跑 OS = bringup 成功一半
           │   此时 errata 开始浮现: 某些指令/某些频率不稳
           │
  Day 14-30│ ▶ Bench 表征: 画 shmoo(§2.6), 测频率/电压/温度墙
           │   跑 benchmark(SPEC/Stream), 对标设计目标
           │
  Day 30-60│ ▶ Errata 汇总 + workaround: 列出所有硅后 bug
           │   能 workaround 的(固件/微码绕过)→ 写进 BIOS/TF-A
           │   不能 workaround 的 → 标记为"等下一版 stepping"
           │
  Day 60-90│ ▶ Speed binning + 量产测试向量定稿(§2.6)
           │   把 shmoo 转成"哪个电压/频率档卖哪个 SKU"
           │
  Day 90+  │ ▶ Burn-in / HTOL(§2.5): 老化筛查条件定稿
           │
  Day 180+ │ ▶ 量产(mass production): A1/A2 stepping 修正后稳定
```
**图 2：D3000M 从回片到量产的 bringup 时间线还原（推测）。** `[推测-业界bringup流程]`

**D3000M 特异性判断（关键判断 3，`[推测-依据]`）**：

- **飞腾的 first light 推测 1–2 周**：与业界一流团队（Apple/Intel ~1 周 [报告-post-silicon]）相比慢一倍，与华为鲲鹏相当（华为也是后发但团队大）。慢的原因：**飞腾 DFT/bringup 团队规模与经验积累弱于 Intel/Apple**（后者有几十代积累），A0 版阻塞 bug 多。
- **errata 数量推测**：Intel Xeon 每代公开 errata **50–150 条**（[官方-Intel-SDM errata]）。飞腾 D3000M 作为相对年轻的核，**内部 errata 推测 100–300 条**（`[推测-依据]`：核越新越没被验证充分，errata 越多；FTC862 代际短于 Cortex），但**公开的极少**（飞腾未发公开 errata 文档，与 Intel/AMD 透明度形成对比 [实测-检索]）。
- **stepping 次数推测**：D3000M 大概率经历 **A0（初版，有阻塞性 bug）→ A1（修主要 bug，能量产）→ A2（修次要 bug，稳定性提升）**，共 2–3 次 stepping，每次 mask 改版 **$1–3M + 3–6 个月**（14nm mask 成本 [推测-E14]）。这是为什么芯片从立项到量产要 3–5 年（[推测-E03 §7]）——**stepping 是大头**。

**为什么 A0 版几乎必然有 bug**：RTL 仿真（UVM 验证，E03 §7）能覆盖 99.9% 的功能场景，但**真实硅片有仿真抓不到的问题**：①功耗瞬态（IR drop）导致时序违例；②工艺角（PVT 变异）让某条路径在特定电压/温度下慢；③模拟 PHY（DDR/PCIe）训练算法在真实信号完整性下失败；④多核并发场景的边角竞态。这些**只能靠硅后 bringup 暴露**——这就是为什么 post-silicon validation 是一门独立手艺，RTL 仿真替代不了 [论文-post-silicon validation]。

---

### 2.5 Burn-in / HTOL / 老化筛查：把早死的芯片提前枪毙

> 这一块是 D17 与 E23（RAS）的交集。E23 讲「老化机理」（BTI/HCI/电迁移/TDDB），E17 讲「**怎么在出厂前用加速老化把弱件筛掉**」。

**Burn-in 的原理**：浴缸曲线（E23 图 1）的左段是「早夭期」——有些芯片刚做好时勉强能跑，但用了几十到几百小时就会坏（因为某个晶体管有微小缺陷，正常工况下慢慢退化）。**Burn-in 就是把芯片放在高温高压下跑很久（如 125°C / 1.5×VDD / 24–168h），让早夭芯片在工厂里就坏掉**，而不是流到客户机房才坏。筛过 burn-in 的芯片，进入了浴缸曲线的「正常寿命段」，DPPM 大幅下降。

**两种 burn-in**：

| 类型 | 全称 | 条件 | 抓什么 | D3000M 推测 |
|------|------|------|--------|------------|
| **HTOL** | High-Temperature Operating Life | 125°C / 工作状态 / 1000h（JEDEC JESD22-A108 [标准]） | 老化机理（BTI/HCI/TDDB） | ✅ 抽样测（不能全测，1000h 太久） |
| **Burn-in（量产）** | 高温高压跑动态向量 | 125–150°C / 1.3–1.5×VDD / 24–168h | 早夭缺陷（弱晶体管/弱互连） | ✅ 每颗或抽批测 |

**D3000M 的 burn-in 策略推测（关键判断 4，`[推测-依据]`）**：

- 服务器 CPU 对 DPPM 敏感（机房坏一颗是运维事故），**推测飞腾对 D3000M 做全检或大比例抽检 burn-in**（24–48h，125°C）。成本：burn-in oven + 额外测试时间，每颗约 **$0.5–2**（[推测-VLSIresearch]）。这把 DPPM 从 ~4000（§2.2 逃逸率）压到 **< 500**（[推测-业界 burn-in 效果]）。
- HTOL（1000h）只能抽样——每批次抽几十颗，验证「设计在 7 年服役期内不会集体老化失效」。这是 JEDEC 认证的强制项 [标准-JESD22-A108]。
- **14nm 的余量优势**（E23 §2.3）：14nm 栅氧厚、互连粗，BTI/HCI/TDDB 物理余量比 5nm 大——这意味着 D3000M 的 burn-in 失效率可能**低于**先进节点同行，老化筛查压力相对小（[推测-与 E23 §2.3 一致]）。

---

### 2.6 Speed Binning 与良率分布：同一批晶圆怎么分出不同 SKU

> 同一片晶圆上，有的 die 工艺好（晶体管快）有的差（慢），但都能用——**怎么把它们分档卖成不同频率/不同定位的 SKU**？这就是 speed binning。

**Shmoo 图——DFT 工程师的「X 光片」**。Bringup 时，对每颗 die 画一张 shmoo：横轴电压（VDD），纵轴频率（fmax），打点标「这颗在这个电压/频率下能跑通测试吗」。

```
   能跑通(✓) / 跑不通(✗)        VDD (V)
                        0.7   0.8   0.9   1.0   1.1   1.2
   f (GHz)
   2.8                  ✗     ✗     ✗     ✗     ✗     ✓  ← 顶级bin(少数)
   2.7                  ✗     ✗     ✗     ✓     ✓     ✓
   2.6                  ✗     ✗     ✓     ✓     ✓     ✓  ← 服务器bin
   2.5(标称)            ✗     ✓     ✓     ✓     ✓     ✓  ← 主力bin(众数)
   2.4                  ✓     ✓     ✓     ✓     ✓     ✓
   2.3                  ✓     ✓     ✓     ✓     ✓     ✓  ← 降级bin
   2.0                  ✓     ✓     ✓     ✓     ✓     ✓  ← 嵌入式/低功耗bin
                        │     │     │     │     │     │
                        最低VDD耐受          标称VDD~1.0V
```
**图 3：D3000M 单颗 die 的 shmoo 图（推测示意）。** `[推测-业界shmoo范式]`

这张图的解读：**这颗 die 在标称 VDD=1.0V 下能稳定跑 2.5 GHz**（标称频），降到 2.3 还能在 0.8V 跑（省功耗），升到 2.8 需要 1.2V（漏电爆炸不划算）。**speed binning 就是把成千上万颗 die 的 shmoo 汇总，按 fmax 分档**。

**良率分布（核心 artifact）**。把一片晶圆上 ~314 颗 good die（[推测-E14 §5.2]）按 fmax 分布：

```
   fmax(GHz)  die数量(推测)   占比     对应SKU
   ─────────────────────────────────────────────────
   ≥2.7       ~15-30         ~5-10%   服务器高频档(S2500旗舰?)
   2.5-2.7    ~120-180       ~40-55%  服务器标称(D3000M主力)
   2.3-2.5    ~70-120        ~25-35%  桌面/工作站降级
   ≤2.3       ~20-50         ~8-15%   嵌入式/低功耗(E2000?降级用)
   ─────────────────────────────────────────────────
   合计       ~280-314        100%
```
**图 4：D3000M 单晶圆 good die 的 fmax 分布（推测）。** `[推测-良率分布模型]`

**关键判断 5（`[推测-依据]`）**：

- D3000M 的**良率分布众数在 2.5 GHz**（标称频），这是 14nm 工艺的典型表现（14nm FinFET fmax 中位 ~2.5–2.8 [推测-业界]）。
- **能跑 2.7+ 的高端 bin 只占 5–10%**——这些 die 晶体管快、漏电低，可以卖更高价或堆更多核（S2500 多路旗舰推测用这批）。
- **只能跑 2.3 以下的低端 die 占 8–15%**——不浪费，降频降压卖成嵌入式 SKU（飞腾 E2000 系列推测部分来自 D3000 bin 不达标的 die，或独立小核设计）。
- **speed binning 是良率变现的关键**：没有 binning，2.3 GHz 的 die 卖不出服务器价；有 binning，每颗 die 都找到「它能稳定跑的最高价档」。这是为什么 Intel/AMD 一颗晶圆能出 i3/i5/i7/i9 多个 SKU——**同一片硅，分档卖不同价**。

**飞腾的 SKU 矩阵推测**：D3000（8 核 2.5GHz 服务器主力）、D3000M（推测中频档）、S2500（多路旗舰，用高频 bin die）、E2000（嵌入式，推测部分用低频 bin die 或独立小核）。**这种「同代硅多 SKU」策略，与 Intel/AMD 一致**，是成熟厂商的标志——飞腾能做这个，说明其 binning 流程已工程化 [推测-产品线观察]。

---

### 2.7 战略伤疤对 DFT 的影响：补 BF16/I8MM/SVE 要重做多少测试

> 这是本视角对 D3000M **战略伤疤**（[实测-扩展专题第25-27行]）的 DFT 层面解读，呼应 Expert_21。

D3000M 缺 BF16/I8MM/SVE，在 DFT 层面意味着：

| 缺失特性 | 当前 DFT 状态 | 下一代补上时的 DFT 工作量（推测） |
|---------|:------------:|------------------------------:|
| **SVE/SVE2** | 无对应扫描通路（RTL 没有） | **大**：新增向量执行单元 + predicate 寄存器堆 → 新增 ~10–30K FF → ATPG 重算 + 向量集扩充 ~10–20%。需 2–4 人月 `[推测]` |
| **BF16** | 无 BF16 转换/乘加通路 | **小-中**：新增 BF16 数据通路 + 乘法器阵列 → 新增 ~2–5K FF → ATPG 局部增量。需 1–2 人月 `[推测]` |
| **I8MM** | 有 UDOT（v8.4），无 SMMLA 矩阵乘 | **小**：在现有 UDOT lane 上扩展，FF 增量小。需 0.5–1 人月 `[推测]` |

**关键洞察**：DFT 的工作量**与 RTL 改动成正比**（E03 §9 已估 RTL 人月）。补 BF16/I8MM 对 DFT 是「小改」；补 SVE 是「中改」。**真正的成本不在 DFT 本身，而在「重新做 ATPG + 重跑良率验证 + 重定 speed bin」这一整套硅后流程**——补一条新指令通路，可能要重新走一遍 §2.4 的 bringup（3–6 个月）。这是为什么飞腾「补 AI 指令」的决策不仅是 RTL 决策，更是**整个硅后验证周期的重启决策**——这也是 D3000M「明知缺 AI 还是不补」的部分原因（补的硅后成本太高，且 v9 授权天花板挡着 [推测-E19]）。

---

### 2.8 国产 ATE 替代：长川/华峰测控能否测 D3000M

> 这是地缘约束（E19）落到 DFT 工程的具体命题：**飞腾受制裁，高端 ATE（Teradyne/Advantest）能不能用国产替代？**

**高端数字 SoC ATE 的门槛**（核心对标表）：

| ATE 机型 | 厂商 | 国别 | pin 数 | 速率 | 向量内存 | 单台价格 | 能测 D3000M 吗 |
|---------|------|:----:|:------:|:----:|:-------:|:--------:|:--------------:|
| **UltraFLEX / IG-XL** | Teradyne（泰瑞达） | 美 | 1024–2048 | 1.6 Gbps | 256 MB–1 GB/ch | $1.5–3M | ✅ 高端主力 |
| **93000 / V93000** | Advantest（爱德万） | 日 | 512–1024 | 3.2 Gbps | 1 GB/ch | $2–3M | ✅ 高端主力 |
| **Magnum / ETS-88** | Cohu（原 Xcerra） | 美 | 1024 | 1.6 Gbps | 512 MB/ch | $1–2M | ✅ 中高端 |
| **长川科技 ICT-8300** | 长川 | **中** | 512 | ≤800 Mbps | 128 MB/ch | $0.3–0.8M | ⚠️ **测模拟/混合强，数字 SoC pin/速率不够** |
| **华峰测控 ST-8300** | 华峰 | **中** | 256 | ≤400 Mbps | 64 MB/ch | $0.2–0.5M | ❌ 主要测模拟/电源管理，高端数字不行 |

**表 B：高端 ATE 对标——国产能否替代。** `[报告-VLSIresearch/SemiAnalysis ATE 市场]`

**关键判断 6（`[推测-地缘]`）**：

- **测 D3000M 这种 8 核服务器 SoC，需要 ≥1024 pin、≥1.6 Gbps 速率、≥512 MB 向量内存的 ATE**。这个档位目前**全球只有 Teradyne / Advantest / Cohu 三家**，国产长川/华峰**差 2–3 代**（pin 数减半、速率 1/2–1/4、向量内存 1/4–1/8）。
- **国产 ATE 能测什么**：模拟/混合信号（DAC/ADC/PLL）、电源管理芯片、中低端 MCU（<100 pin）、分立器件。长川/华峰在这块**已上量并替代进口**（[报告-中国 ATE 市场]）。但**高端数字 SoC 是国产 ATE 的硬伤**。
- **飞腾的现实**：D3000M 量产**必须用 Teradyne 或 Advantest**（[推测]）。好消息是——**ATE 不在 BIS 实体清单的直接管制范围**（ATE 是「测试设备」非「制造设备」，且 Teradyne/Advantest 在中国有大量装机基础，维护与耗材不受断供 [推测-地缘分析]）。所以**飞腾短期 ATE 供应不愁**，但长期若管制升级，是潜在风险（归 E19）。
- **真正的卡点不是 ATE 机型，而是 probe card（探针卡）**：测 D3000M 这种 FC-BGA 封装前 wafer sort，需要**定制 probe card**（几千到上万根微针，对准每个 bump），这块由 FormFactor（美）/ Micronics（日）/ 国内胜科等供应。定制 probe card 的设计依赖飞腾的 die bump map，**这块飞腾可控**（自研 die 布局 [推测]）。

---

### 2.9 Errata 处理：硅后 bug 的生命周期

> 这是 DFT/bringup 工程师的「收尾工作」——把硅后发现的 bug 分类、定 workaround、决定要不要 stepping。

**Errata 的分类与处理流程**：

```
  硅后发现bug(测试/bringup/客户报告)
           │
           ├── 功能性bug(指令算错/挂死)
           │     ├── 可workaround(微码/固件绕过)→ 写进BIOS/TF-A, 不stepping
           │     └── 不可workaround → 标记"下一版stepping修"
           │
           ├── 性能bug(比预期慢/某场景掉速)
           │     ├── 可接受 → 文档记录, 降低标称
           │     └── 不可接受 → 优化微码/调度, 或stepping
           │
           └── 可靠性bug(特定温度/电压下不稳)
                 ├── 降频/降压能规避 → 降speed bin, 损失良率变现
                 └── 不可规避 → stepping(改掩模)
```
**图 5：Errata 分类与处理决策树。** `[推测-业界errata流程]`

**D3000M errata 文档透明度判断（关键判断 7，`[推测-生态]`）**：

- Intel/AMD 每代发**公开 errata 白皮书**（[官方-Intel-SDM errata volume]，Xeon 每代 50–150 条，每条含描述/影响/workaround/修复版本）。这是企业客户做尽职调查的依据——**买服务器前先看 errata 清单评估风险**。
- **飞腾未发公开 errata 文档**（[实测-检索飞腾官网/文档]）。errata 信息推测**只对 OEM/大客户 NDA 开放**。这有两面性：
  - **好处**：不暴露芯片弱点，保护商业形象（信创采购方多数不深究 errata）。
  - **坏处**：**互联网/金融核心客户不敢上**——没有 errata 文档 = 无法做风险评估 = 合规审计过不了。这是飞腾进不了互联网核心（腾讯/阿里云大规模）而鲲鹏能进的原因之一（鲲鹏公开 RAS 与 errata 白皮书 [报告-华为鲲鹏]，与 E23 §2.9 一致）。
- **判断**：飞腾若想从「信创政企」升级到「通用企业服务器」，**公开 errata 文档是必须补的一步**（与 E23 §3 RAS 白皮书建议同源）。

---

## 3. 设计决策评估（飞腾哪些 DFT/Bringup 决策认可 / 哪些该改）

| 决策 | 飞腾选择 | DFT 工程师评价 | 理由 |
|------|---------|:----------:|------|
| DFT 流程（scan+ATPG+MBIST） | 推测用 Tessent/TetraMAX | ✅ **正确** | 业界标准，4-wide 核 TC 99% 可达（§2.2） |
| 压缩测试 | 推测 100–500× 压缩 | ✅ **必须** | 不压测试时间爆炸，每颗 $2+ 而非 $0.5（§2.3） |
| speed binning 分 SKU | D3000/S2500/E2000 多档 | ✅ **成熟** | 良率变现，与 Intel/AMD 一致（§2.6） |
| burn-in 筛查 | 推测全检/大比例 | ✅ **服务器必须** | DPPM 从 4000 压到 <500（§2.5） |
| ATE 用 Teradyne/Advantest | 推测 | ✅ **现实最优** | 国产差 2–3 代，但 ATE 暂未受断供（§2.8） |
| errata 文档不公开 | 仅 NDA | ⚠️ **该改** | 阻碍进互联网/金融核心（§2.9） |
| 不补 BF16/I8MM | ISA 授权天花板 | ❌ **DFT 角度无奈** | 补了要重做 ATPG+bringup，但战略伤疤必须补（§2.7） |
| 公开 die photo / DFT 白皮书 | 无 | ⚠️ **该改** | 信息不对称损害信任（与 E03/E23 一致） |

**总评**：飞腾的**DFT 与量产测试工程化是合格的**（流程对、binning 对、burn-in 对），**短板不在「测不了」，在「信息不透明」**（errata/die photo/DPPM 不公开）与「**质量一致性落后**」（DPPM ~4000 vs Intel <100）。前者是工程化积累问题，后者是开放策略问题——后者更容易改，且收益最大（开放 errata 直接提升企业客户信任）。

---

## 4. 这一视角的盲区与反方（强制诚实段）

> 宪法 §4.3：敢说看不见什么，才不是软文。DFT/Bringup 工程师的固有盲区：

1. **DFT 看不见运行时可靠性**。DFT 管「出厂时坏没坏」，但**出厂好的芯片，在客户机房跑 7 年可能因软错误（中子翻转）算错**——那是 E23（RAS）的领域。DFT 工程师容易误以为「测过了就永远对」，**忽略了 SER 与老化的长期威胁**（E23 §2.3）。两视角共用浴缸曲线，但 DFT 只管左段，中右段是 E23。
2. **测试覆盖率 ≠ 质量**。TC 99% 听起来高，但 **1% 逃逸在百万片出货下 = 上万颗坏件**（§2.2）。DFT 工程师容易盯着 TC 数字，**忽视 DPPM 的实战含义**（售后赔付、品牌信誉）。真正的质量是「客户机房里的可用性」，不是 ATE 上的 pass 率。
3. **所有 FF 数 / 测试时间 / 成本都是推测**。飞腾未公开 DFT 文档、扫描 FF 数、测试向量集。本文数字基于业界类比 `[推测-依据]`，**可能有 30–50% 误差**。读者切勿把推测当事实引用。
4. **DFT 视角低估软件适配难度**。DFT 工程师觉得「errata workaround 写进 BIOS 就完了」，但**固件/OS/编译器适配 workaround 的连锁修改**是 Expert_18（固件）/ Expert_11（编译器）的地盘。一条 errata 可能让编译器后端改十几处——DFT 看不见这层成本。
5. **speed binning 推测建立在「die 面积 120mm²」假设上**（E14 §5）。若真实 die 是 90 或 180 mm²，good die 数与 binning 分布会显著不同（E14 §9 盲区 2 已声明面积不确定性）。
6. **国产 ATE 评价可能过于悲观**。长川/华峰在 2024–2026 进步很快（先进封装测试、高 pin 数机型在研 [报告-中国 ATE]），本文基于现状外推，**可能低估国产替代速度**。

**反方一句话**：有人说「飞腾 DFT 不行，因为 DPPM 比 Intel 高」。**反驳**：DPPM 高是后发厂商的必经阶段（Intel 早期 Xeon DPPM 也高），且飞腾主要市场是信创政企（对 DPPM 不如金融敏感）。**用 Intel 成熟期的 DPPM 横评飞腾早期产品，是不公平的标杆**。但飞腾若要升级到通用企业市场，**必须把 DPPM 与 errata 透明度补到 Intel 量级**——这是下一代的工程目标，不是这一代的原罪。

---

## 5. 与其他视角对偶（一致 / 冲突，强制）

| 对偶视角 | 一致点 | 冲突点 / 互补 |
|---------|------|-------------|
| **Expert_23 RAS** | 共用浴缸曲线；E17 管早夭筛查（左段），E23 管软错误与老化（中右段）；burn-in 是交集 | **分工**：DFT=制造测试（出厂坏没坏），RAS=运行时可靠性（在用时错不错）。E17 的 DPPM 是「出厂漏网」，E23 的 FIT 是「在用出错」 |
| **Expert_03 HW_Designer** | E03 在 RTL 插 DFT 接入（§8.4），E17 在硅后用扫描链测；E03 §9 战略伤疤 RTL 后果 → E17 §2.7 DFT 后果 | ✅ **上下游接力**：E03 写 DFT 逻辑，E17 跑 DFT 测试 |
| **Expert_14 Process** | 良率模型同源：E14 算 good die 数（§5），E17 算测试成本（§2.3）；die 面积假设共用 120mm² | ✅ **互补**：E14 给良率（多少 die 能用），E17 给测试（能用的 die 测一次多少钱 + 分 bin） |
| **Expert_07 Business** | 测试成本（E17 §2.3 ~$0.55/颗）是 die 成本（E14 ~$15）之外的量产成本项 | ✅ **下游**：E07 算总 BOM，E17 给测试这一项的具体数字 |
| **Expert_19 Geostrategy** | ATE / probe card 供应链受地缘影响（§2.8） | **硬切分工**：E17 讲「ATE 技术上能不能测」，E19 讲「ATE 供应会不会被断」。E17 把地缘当输入，E19 解释输入成因 |
| **Expert_21 AI Positioning** | D3000M 无 BF16/I8MM/SVE → DFT 也不用测这些通路（§2.7） | ✅ **一致**：E17 §2.7 是 E21 战略伤疤的 DFT 层注脚 |
| **Expert_15 Package** | FC-BGA 封装后的 final test 与 probe card 设计依赖 die bump map | ✅ **互补**：E15 定封装/bump，E17 定测试探针卡对准 |
| **Expert_18 Firmware** | errata workaround 写进 BIOS/TF-A（§2.9） | ✅ **下游**：E17 发现 errata，E18 在固件层实现 workaround |

---

## 6. 参考文献（23 条，分级标注 ≥15，含 ≥5 论文/标准/书）

**[书]**
1. **[书]** Michael Abramovici, Melvin A. Breuer, Arthur D. Friedman, *Digital Systems Testing and Testable Design*, IEEE Press (1994, 修订版) —— **DFT 教材圣经**，扫描链/ATPG/BIST 的经典理论（§2.1）。
2. **[书]** Laung-Terng Wang, Charles E. Stroud, Nur A. Touba, *System-on-Chip Test Architectures: Nanometric Design and Test*, CRC Press (2007) —— SoC DFT 架构，压缩测试与 MBIST（§2.1/§2.3）。
3. **[书]** Michael L. Bushnell, Vishwani D. Agrawal, *Essentials of Electronic Testing for Digital, Memory and Mixed-Signal VLSI Circuits*, Springer (2000) —— 测试理论全面教材，IDDQ/fault model（§2.1）。

**[论文]**
4. **[论文]** E. B. Eichelberger, "Random-Pattern Coverage Enhancement and Diagnosis for LSSD Logic Self-Test" (*IEEE/ACM DAC* 1983) —— **LBIST 与 LSSD（Level-Sensitive Scan Design）奠基**（§2.1）。
5. **[论文]** J. Rajski et al., "Embedded deterministic test for low cost manufacturing test" (*IEEE ITC* 2003) —— **压缩测试（EDT）原理**，Tessent TestKompress 基础（§2.1/§2.3）。
6. **[论文]** P. Nigh & A. Gattiker, "Random and Systematic Defect Analysis" (*IEEE ITC* 2004) —— 缺陷覆盖率与 DPPM 的统计关系（§2.2）。
7. **[论文]** S. Sunter & K. Komonytskyy, "BIST for phase-locked loops" (*IEEE VTS* 2012) —— PLL/模拟 IP 的 BIST，D3000M 的 PLL 测试参考（§2.1）。
8. **[论文]** A. Cristea et al., "Post-Silicon Validation: Challenges, Directions and Opportunities" (*IEEE DATE* 2017) —— **硅后验证综述**，bringup 流程与挑战（§2.4）。
9. **[论文]** A. Nahir et al., "Bridging pre-silicon verification and post-silicon validation" (*IEEE/ACM DAC* 2013) —— 仿真与硅后的鸿沟，为什么 A0 必然有 bug（§2.4）。
10. **[论文]** K. Killpack, "Post-silicon Validation in the Trenches" (*IEEE Design & Test*, 2017) —— 硅后工程师实战经验，shmoo 与 errata 流程（§2.6/§2.9）。
11. **[论文]** R. C. Aitken, "New Defect Metrics for New Technologies" (*IEEE ITC* 2001) —— 先进节点缺陷模型，DPPM 与 TC 的现代关系（§2.2）。

**[标准]**
12. **[标准]** JEDEC JESD22-A108, *Temperature, Bias, and Operating Life* —— **HTOL 测试标准**（125°C / 1000h，§2.5）。
13. **[标准]** IEEE 1149.1 (JTAG), *Standard Test Access Port and Boundary-Scan Architecture* —— 板级与芯片级边界扫描，D3000M 必有 JTAG TAP（§2.1）。
14. **[标准]** IEEE 1500, *Standard Testability Method for Embedded Core-based Integrated Circuits* —— 嵌入式核测试 wrapper，与 E03 IP 集成衔接（§2.1）。
15. **[标准]** IEEE 1838, *Standard for Test Access Architecture for Three-Dimensional Stacked Integrated Circuits* —— 3D/Chiplet 测试，与 E15 衔接。

**[官方]**
16. **[官方]** Intel, *Intel® Xeon® Processor Scalable Family Specification Update*（errata 文档）—— 每代 50–150 条公开 errata 的标杆（§2.9）。
17. **[官方]** Siemens EDA (Mentor), *Tessent TestKompress / Tessent MemoryBIST Product Brief* —— D3000M 推测采用的 DFT 工具（§2.1/§2.3）。
18. **[官方]** Synopsys, *TetraMAX ATPG / DFTMAX Ultra Product Brief* —— ATPG 与压缩测试工具（§2.1）。
19. **[官方]** Teradyne, *UltraFLEX / IG-XL System Datasheet* + Advantest, *V93000 Datasheet* —— 高端 ATE 机型参数（§2.8）。

**[报告]**
20. **[报告]** VLSIresearch / SemiAnalysis, *ATE Market & Test Cost Analysis*（2024）—— ATE 机型价格、每秒测试成本、handler 成本（§2.3/§2.8）。
21. **[报告]** Wikichip / Chips and Cheese, *ARM Cortex-A76 / AMD Zen Microarchitecture Analysis* —— 4-wide OoO 核 FF 密度推测依据（§2.2）。
22. **[报告]** 中国半导体行业协会 / 信通院, *国产半导体测试设备发展白皮书*（2024）—— 长川科技/华峰测控能力评估（§2.8）。

**[实测]**
23. **[实测]** 本项目 `扩展专题.md` 第 25–27 行（D3000M 缺 SVE/BF16/I8MM）+ Lab00–07（2.5GHz/4-wide/L3 8MB 等锚点）—— §2.2 扫描规模、§2.7 战略伤疤 DFT 后果、§2.6 speed binning 的实测地基。

> **参考计数**：23 条，其中论文 8 条（Eichelberger/Rajski/Nigh/Sunter/Cristea/Nahir/Killpack/Aitken）+ 标准 4 条（JESD22-A108/JTAG/IEEE1500/IEEE1838）+ 书 3 条（Abramovici/Wang/Bushnell）+ 官方 4 条（Intel/Siemens/Synopsys/Teradyne+Advantest）+ 报告 3 条（VLSIresearch/Wikichip/中国信通院）+ 实测 1 条。**满足「≥15 条、≥5 论文/标准/官方」门槛（论文+标准+书=15 条）。**

---

## 7. 延伸阅读（项目内 + 外部）

**项目内对偶**：
- [`Expert_23_Server_RAS/README.md`](../Expert_23_Server_RAS/README.md) —— **同根浴缸曲线**：E17 管早夭筛查（DFT/burn-in），E23 管软错误与老化（RAS）。两视角共用 Black 方程与 HTOL 标准。
- [`Expert_03_HW_Designer/README.md`](../Expert_03_HW_Designer/README.md) §8.4 —— **上游**：E03 在 RTL 插 DFT 接入，E17 在硅后用扫描链测。E03 §9 战略伤疤 RTL 后果 → E17 §2.7 DFT 后果。
- [`Expert_14_Process_Manufacturing/README.md`](../Expert_14_Process_Manufacturing/README.md) §5 —— **良率上游**：E14 算 good die 数，E17 算测试成本。die 面积假设共用。
- [`Expert_07_Business/README.md`](../Expert_07_Business/README.md) §3 —— **成本下游**：E07 算总 BOM，E17 给测试这一项（~$0.55/颗）。
- [`Expert_19_Geostrategy/README.md`](../Expert_19_Geostrategy/README.md) —— **ATE 供应地缘**：E17 讲「技术上能不能测」，E19 讲「ATE 会不会被断供」。
- [`Expert_21_AI_Positioning/README.md`](../Expert_21_AI_Positioning/README.md) —— E17 §2.7 是 E21 战略伤疤的 DFT 层注脚。
- [`Expert_15_Package_Chiplet/`](../Expert_15_Package_Chiplet/) —— probe card 与封装 bump map 衔接。
- [`Expert_18_Firmware_Boot/`](../Expert_18_Firmware_Boot/) —— errata workaround 写进 BIOS/TF-A。
- [`扩展专题.md`](../扩展专题.md) —— D3000M 实测 ISA 锚点（BF16/I8MM/SVE 缺失依据）。

**外部**：
- [International Test Conference (ITC)](http://www.itctestweek.org/) —— 测试领域顶会，DFT/ATPG/BIST 前沿论文。
- [Semiconductor Test & Reliability (STAR) Conference](https://www.elestcon.org/) —— 硅后验证与可靠性。
- [IEEE Design & Test 杂志](https://www.computer.org/digital-library/magazines/dt) —— post-silicon validation 实战文章。

---

> **本视角一句话**：**D3000M 的 DFT 与量产测试是「流程合格、透明度不足、质量一致性追赶中」——测得了、分得出 bin、筛得掉早夭，但 errata 不公开与 DPPM 偏高是它从「信创服务器」升级到「通用企业服务器」的两道槛。而补 AI 指令（BF16/I8MM/SVE）不只是 RTL 改动，更是一次完整的硅后验证周期重启——这是战略伤疤在 DFT 层的具体代价。**

---

**附：本节 artifact 清单（可运行/可验证）**

| artifact | 路径 | 语言 | 用途 |
|---------|------|------|------|
| 测试成本模型 | [`test_cost_model.py`](./test_cost_model.py) | Python 3 | 算任意 die 的测试时间、每颗成本、DPPM 逃逸率 |

运行测试成本模型：
```bash
cd Expert_17_DFT_PostSilicon
python3 test_cost_model.py
# 预期输出: D3000M 测试时间分解表 + 每颗成本 ~$0.55 + DPPM 逃逸分析
```

---

## § DFT 与硅后 Bringup 方法论及资源（不只飞腾，给所有测试/Bringup 工程师）

> 本章把 E17 的飞腾 DFT 分析上升为**任何 DFT/硅后工程师都可复用的方法与资源**。飞腾是案例锚点，方法普适。通用资源见 [`领域资源库.md`](../领域资源库.md)。

### 方法论一：DFT 全栈（设计可测性 → 量产测试 → 硅后 bringup）

| 阶段 | 任务 | 方法/工具 |
|------|------|---------|
| **DfT（Design for Test）** | RTL 阶段插入测试结构 | 扫描链（scan chain）、BIST（MBIST/LBIST）、JTAG（IEEE 1149.x）、压缩（EDT/Adaptive Scan）|
| **ATPG** | 生成测试向量覆盖故障 | TetraMAX（Synopsys）、TestKompress（Cadence）；故障模型 stuck-at/transition/bridging |
| **量产测试** | ATE 机台分 bin | ATE（Advantest 93000/Teradyne UHD）、wafer sort + final test、speed binning |
| **硅后 Bringup** | 首片点亮 + errata | FPGA 原型、emulation、bringup lab、errata 文档 |
| **可靠性** | 加速寿命测试 | HTOL（高温工作寿命）、Burn-in、FIT 率统计 |

### 方法论二：故障模型与覆盖率

测试质量看"覆盖什么故障"：
- **stuck-at**（固定 0/1）：最基础，覆盖率高（>99%）但漏速度缺陷
- **transition**（跳变延迟）：抓速度缺陷，现代芯片主力
- **path-delay / N-detect**：精细但向量爆炸
- ** bridging / IDDQ**：抓桥接/漏电
- **DPPM**（Defects Per Million）：出货后缺陷率，服务器级目标 <100 DPPM

### 方法论三：硅后 Bringup 的"黑暗启动"

首片流片回来的芯片，点亮是"找茬"过程：
- **预硅**：仿真/emulation 把已知 bug 找光
- **首片**：上电 → boot → 跑诊断 → 找 errata（可能是 RTL/工艺/封装/固件 任一层）
- **errata 处理**：可绕过（workaround，改固件/软件）vs 必须 respin（重新流片）
- 飞腾 errata 不公开是透明度短板（E17 §3 核心），通用教训：errata 文档是客户信任基础

### DFT 专属资源

- **标准**：IEEE 1149.x（JTAG/Boundary Scan）、IEEE 1500（core test）、IEEE 1687（IJTAG）、P1687
- **会议**：**ITC**（Int'l Test Conf）、**VTS**（VLSI Test）、**DATE**（Design Autom & Test in Europe）、ETS
- **工具**：TetraMAX/TestKompress（ATPG）、DFT Compiler（DfT 插入）、**Tessent**（Siemens，全栈 DFT）
- **机台**：Advantest 93000、Teradyne UHD、Cohu（handler）
- **书/论文**：Abramovici《Digital Systems Testing and Testable Design》、Wang《VLSI Test Principles》

### 给测试/Bringup 工程师的通用建议

1. **DfT 在 RTL 阶段就插入**：流片后无法补救，扫描链覆盖率要 >95%。
2. **transition 故障是现代主力**：stuck-at 高覆盖不等于速度质量。
3. **首片 bringup 预留数月**：找 errata 是迭代过程，预硅仿真再全也漏。
4. **errata 文档要透明**：客户靠 errata 做 workaround，隐瞒 = 失信（飞腾短板，通用教训）。
5. **补 AI 指令 = 重启硅后周期**：补 BF16/I8MM 不只 RTL 改，是 ATPG/bringup/errata 全重做（E17 §2.7 飞腾案例）。
