# Expert_03 — 硬件设计专家视角（RTL / IP 集成 / SoC 组装）

> **角色定位**：RTL 设计师 / IP 集成工程师 / 验证工程师 / DFT 与后端实现的"翻译官"。
> 用 Verilog / SystemVerilog / Chisel 把架构师（E02）的设计图变成可流片的网表，
> 再把自研核 + 一堆**外购 IP**（DDR PHY、PCIe、SerDes、GIC…）像乐高一样拼成 SoC。
>
> **核心思维模型**（named framework）：**"PPA + IP 重用率" 双目标函数**。
> 任何决策都要同时回答两件事：(1) 这能综合吗？时序收敛吗？面积/功耗多大？
> (2) 这个模块该**自研**（护城河、差异化）还是该**买 IP**（成熟、快上市、省研发）？
> 现代服务器 SoC **不是一颗从零写的芯片**，而是约 **30%–60% 的晶体管来自第三方 IP**。
> 一位合格的 RTL 工程师 70% 时间在和"买的 IP 不对得上"的接口、时序、协议打交道，
> 30% 时间才在写自家核的逻辑。**这恰恰是飞腾 D3000M 最该被审视、却最少被讨论的维度。**

---

## 0. 这位专家怎么看飞腾 D3000M？（角色入场）

他不会先问"频率/核数/IPC"，而是问 10 个 RTL/SoC 层面的尖锐问题：

1. **自研 vs 外购**：D3000M 这颗 SoC 里，自研 FTC862 核占多少晶体管？DDR PHY、PCIe、SerDes、GIC 是买的还是自己写的？比例多大？ `[推测]`
2. **RTL 复杂度**：FTC862 这个 4-wide OoO 核，RTL 工程量对标 ARM Cortex-A76 还是 A78？需要多少人年？ `[推测-依据]`
3. **die photo 对标**：D3000M 单核面积推测 vs Apple M1 Firestorm / Intel Golden Cove / AMD Zen 4 / 鲲鹏 920，差几倍？ `[第三方报告]`
4. **IP 集成的坑**：外购 DDR PHY 与自研核的时序边界、电压域、测试接入怎么做？飞腾的 IP 重用策略是什么？ `[推测]`
5. **ARM 授权几何**：ISA 授权（ARMv8 架构许可）≠ 核授权（Cortex 硬核）。飞腾拿的是哪一种？这对 RTL 工程量意味着什么？ `[官方]`
6. **4-wide 怎么写**：forwarding 单元、2-bit/TAGE 预测器、ROB + 重命名表，这些关键电路的 RTL 骨架长什么样？ `[教学示意]`
7. **RTL → Tape-out 流程**：从 spec 到量产 3–5 年里，飞腾走的是 Synopsys 全家桶还是 Cadence 全家桶？ `[推测]`
8. **时序收敛**：4-wide OoO 在成熟制程（14nm 级或 N+1）下，最长路径（L1 读 → ALU → forward 回 RF）能压进 cycle time 吗？ `[推测-依据]`
9. **DFT**：芯片上电后，几万到几十万个扫描 FF 怎么测？良率损失多大才能 cost-effective？ `[推测]`
10. **战略伤疤的 RTL 后果**：D3000M 无 SVE/BF16/I8MM，意味着 RTL 里**没有**对应的执行单元、寄存器堆扩展、向量 lane——下一代补这些需要多大 RTL 改动？ `[官方文档]`

本文逐项作答，**所有数字按 `[实测]` / `[官方文档]` / `[第三方报告]` / `[推测-依据]` 分级标注**（项目宪法 §4.3）。

---

## 1. 第一性原理：现代 SoC = 自研核 + 一堆买的 IP

这是理解飞腾 D3000M 最重要、却最少被讲清的认知前提。

### 1.1 一颗服务器 SoC 的典型 IP 拼图

打开任何一颗现代服务器/桌面 CPU 的 die photo（Wikichip、Chips and Cheese、TechInsights 拆解），你看到的是**几十个色块**，而不是一块均质的硅。这些色块大致分四类：

| 类别 | 典型模块 | 来源（业界惯例） | 备注 |
|------|---------|----------------|------|
| **A. 自研核心** | CPU 核（FTC862）、私有 L1/L2、自研一致性 fabric | **自研**（护城河） | 差异化关键，必须自己做 |
| **B. ISA/系统 IP（ARM 生态绑定）** | GIC-500/600、CoreLink CMN-600/700 一致性网络、SMMU、AMBA AXI/AHB | **ARM 授权**（硬核或 RTL 软核） | ARM ISA 厂商几乎都用 ARM 的系统 IP，互换性差 |
| **C. 物理 IP（PHY）** | DDR4/5 PHY、PCIe Gen4/5 PHY、SerDes、USB PHY、HDMI/DP PHY | **外购**（Synopsys / Cadence / ARM / Rambus） | PHY 极难自研，需要模拟/PLL/SerDes 专长，全球就几家能做 `[报告]` |
| **D. 通用辅助 IP** | SRAM compiler、标准单元库、PLL、GPIO、I²C、SPI、JTAG、DFT 接入 | **外购**（TSMC/SMIC PDK 自带 + Synopsys） | foundry PDK 配套，几乎全行业通用 |

**关键洞察**：A 类是"灵魂"，B/C/D 类是"骨骼与血管"。一个 RTL 工程师如果只在 A 类里打转，他看不到 SoC 的全貌；而**飞腾作为后发厂商，B/C/D 类几乎必然依赖外购**——这不是失败，是经济性使然。

### 1.2 为什么 PHY 和系统 IP 几乎没人自研

- **DDR PHY**：要把数字控制器的高速信号转换成符合 JEDEC 时序的模拟波形，涉及 DDR4-3200 的 1.6 GT/s、DDR5-6400 的 3.2 GT/s 信号完整性，需要 **PLL/DLL、ZQ 校准、训练算法、读眼图（read eye）补偿**。全球能做 DDR5 PHY 的公司一只手数得过来：Synopsys、Cadence、Rambus、ARM、瑞萨。一家自研 CPU 公司要从零写 DDR PHY，**至少 2–3 年 + 50 人团队**，且第一版几乎必然流片失败。`[报告]`
- **SerDes / PCIe PHY**：PCIe Gen5 是 32 GT/s，Gen6（PAM4）是 64 GT/s。SerDes 是"模拟电路里的皇冠"，涉及连续时间线性均衡（CTLE）、判决反馈均衡（DFE）、CDR。这一块即便是 Intel、AMD 也部分依赖自研 + BroadCom 专利交叉，飞腾**几乎必然外购**（Synopsys 或 ARM）。`[第三方报告]`
- **GIC（中断控制器）**：GIC 是 ARMv8 ISA 的系统组件，规范由 ARM 定义，GIC-500/600 的 RTL 也由 ARM 提供。理论上可以自研兼容 RTL，但 ARM 的实现经过海量验证，自研收益极低、风险极高。飞腾**几乎确定使用 ARM GIC-600 或其前代**。`[官方文档]`

> **第一性原理结论**：评价飞腾 D3000M 的"自主率"，不能只看 CPU 核，要看**整颗 SoC 的晶体管构成**。下一节给出具体推测。

---

## 2. 自研 vs 外购：D3000M 的真实 IP 比例推测

> 这是本文最关键、也最受信息不对称困扰的判断。飞腾未公开 die photo 或 IP BOM，
> 以下数字均为 `[推测-依据]`，依据为：(a) 业界同类 SoC 公开构成；
> (b) 飞腾公开的"自研 FTC 核"宣传；(c) ARM 生态的强制依赖项。

### 2.1 按面积的 IP 构成推测（D3000M，8 核服务器 SoC）

| 类别 | 模块示例 | 占 die 面积推测 | 来源 | 依据 |
|------|---------|---------------:|------|------|
| **A. 自研 CPU 核** | 8 × FTC862（含私有 L1 64K + L2 512K） | ~25%–30% | 自研 | "自研 FTC 核"官方表述 + 4-wide OoO 典型面积 `[官方]+[推测]` |
| **A. 自研 L3 + 一致性 fabric** | 8MB shared L3、DSU 类一致性总线 | ~15%–20% | 自研 or ARM CMN 部分定制 | L3 SRAM 大头是 foundry SRAM compiler，控制逻辑自研 `[推测]` |
| **C. 外购 DDR PHY + controller** | DDR4-3200 PHY（推测 Synopsys/ARM） | ~10%–15% | **外购** | DDR PHY 自研门槛极高，飞腾无公开自研记录 `[推测]` |
| **C. 外购 PCIe + SerDes** | PCIe Gen4 ×多条（推测） | ~8%–12% | **外购** | SerDes 全球外购为主 `[推测]` |
| **B. ARM 授权系统 IP** | GIC-600、SMMU v3、AMBA fabric | ~5%–8% | **ARM 授权** | ARMv8 生态绑定 `[官方]` |
| **D. SRAM compiler + 标准单元** | 所有 cache 的 bitcell、标准单元库 | （横切各模块，约 30%–40% 总面积是 SRAM） | **foundry PDK** | TSMC/SMIC 配套 `[报告]` |
| **D. PLL / IO / DFT / 时钟复位** | PLL、GPIO、扫描压缩器 | ~5%–8% | **外购 + 工具生成** | 通用 IP `[推测]` |
| **其它** | 加密引擎、SM3/SM4（v8.4 自带）、调试 | ~3%–5% | 自研 or IP | v8.4 SM3/SM4 是 ISA 自带，不需要单独 IP `[官方]` |

**汇总结论（`[推测-依据]`）**：

> **D3000M 大约 40%–50% 的 die 面积是"自研 RTL + 自研控制 + foundry SRAM"构成的核心竞争力区，另 30%–40% 是外购 PHY/IO，剩余 10%–20% 是 ARM 系统授权 IP + 通用辅助 IP。**
> 用晶体管数衡量，因为 SRAM 密度极高，**自研 RTL 对应的逻辑晶体管比例更低（约 30%–40%），外购 IP + IP 化的 SRAM/PHY 占 60%–70%**。

这与 Apple M1（自研比例更高，连 PCIe/SerDes 都部分自研 `[第三方报告]`）、Intel x86（几乎全自研，仅 DDR PHY 历史上买过 Rambus `[报告]`）形成对照，但与**鲲鹏 920、飞腾这类 ARM 生态后发厂商的常态一致**。

### 2.2 ARM 授权类型：架构许可 vs 核授权

这是 RTL 工程量的决定性变量，必须讲清：

| 授权类型 | 你拿到什么 | RTL 工作量 | 代表厂商 |
|---------|-----------|-----------|---------|
| **架构许可（Architecture License, ALA）** | ARM ISA 规范手册（ARM ARM DDI 0487），允许你**自己写核** | **极大**：从零写 RTL，需要完整微架构团队 | **Apple**、**高通**、**飞腾**、**华为海思（鲲鹏）** `[官方]` |
| **核授权（RTL 软核，Cortex-A 系列）** | ARM 写好的 RTL（如 Cortex-A76/A78），可修改参数（cache 大小）但不能改微架构 | **中**：主要是集成、验证、后端 | 多数中小 SoC 厂商（联发科中低端、瑞芯微） `[官方]` |
| **硬核授权（Hardened Core）** | ARM 给的 GDSII，已对某工艺优化，不可改 | **小**：只用 foundry 指定工艺 | 部分嵌入式 SoC `[官方]` |

**飞腾拿到的是架构许可**——这是飞腾"自研 FTC862"宣传的法律基础。**意味着飞腾必须自己写 FTC862 的全部 RTL**，不能直接买 Cortex-A76 硬核。

> **关键判断 1（`[推测-依据]`）**：飞腾 D3000M 是"**自研核 + 外购 IP**"型 SoC，**自研部分集中在 CPU 核与一致性 fabric，外购集中在 PHY/IO 与 ARM 系统绑定 IP**。这与"全自研"（Intel）或"全买核"（联发科低端）都不同，是 ARM 生态架构许可厂商的标准姿态——和华为鲲鹏、高通骁龙同类。

---

## 3. FTC862 的 RTL 复杂度：4-wide 核要写多少代码？

### 3.1 复杂度对标（核心表）

| 项目 | 核心类型 | Issue Width | 工艺 | RTL 体量（含验证） | 工程量（人年） |
|------|---------|:---------:|----:|:--------------:|:------------:|
| **飞腾 FTC862**（推测） | OoO 服务器核 | **4-wide** | 7nm 级 `[推测]` | **~150–250 万行 SV** `[推测]` | ~200–400 人年 `[推测-依据]` |
| **ARM Cortex-A76**（公开） | OoO | 4-wide | 7nm | ~150–200 万行 SV `[报告]` | ~300 人年/3–4 年（ARM 内部） |
| **ARM Cortex-A78** | OoO | 4-wide | 5nm | ~200 万行 SV `[报告]` | ~350 人年（A76 衍生） |
| **Apple Firestorm**（M1 P 核） | OoO 超宽 | **8-wide** | 5nm | ~数百万行 `[第三方报告]` | 估计 500+ 人年/代际 |
| **AMD Zen 4** | OoO | 6-wide | 5nm | ~数百万行 `[报告]` | AMD 内部未公开 |
| **Intel Golden Cove** | OoO | 6-wide | Intel 7 | ~数百万行 `[报告]` | Intel 内部未公开 |
| **华为鲲鹏 920（TaiShan v110）** | OoO | 4-wide | 7nm | ~150–200 万行 SV `[推测]` | 海思自研 `[推测]` |
| **BOOM（开源 RISC-V OoO）** | OoO | 2–4-wide | 仿真 | ~60K Scala（≈150K SV 等价）`[官方]` | 学术 30+ 人年 |
| **RocketChip（开源 InO）** | 顺序 | 1-wide | 仿真/流片 | ~20K Scala `[官方]` | 学术 10 人年 |

**关键判断 2（`[推测-依据]`）**：

> FTC862 是 4-wide OoO，**RTL 工程量与 ARM Cortex-A76 大致同量级**（飞腾自研到这个宽度，说明拥有与 ARM 核团队相当的工程能力）。但飞腾是**单核代际迭代**，不像 ARM 有 A76→A77→A78→A710 的连续多代积累，所以**第一代 4-wide 的实际投入可能高于 ARM 单代**（缺少前代可复用 RTL）。
> 注意：飞腾从 D2000（推测 2–3 wide）到 D3000（4-wide）的迭代，每代都要消化前代 RTL + 新增，**整体积累人年应在 500–800** `[推测]`。

### 3.2 为什么 4-wide 是"甜蜜点"也是"天花板"

- **4-wide 是 OoO 的工程甜蜜点**：再往宽（6-wide/8-wide）做，**寄存器堆端口数、唤醒/选择逻辑、forwarding 网络呈超线性增长**。Apple Firestorm 8-wide 的寄存器堆读端口数是 FTC862 的 ~2×，功耗和面积代价巨大 `[第三方报告]`。
- **4-wide 也是性能天花板**：真实代码 ILP 上限约 4–6（Waller 1991 `[论文]`，见 E01），4-wide 已经逼近 ILP Wall，再加宽边际收益骤减。这就是为什么 ARM Cortex 系列长期停在 4-wide，直到 Neoverse V2/N2 才微调。
- **飞腾选择 4-wide 是工程理性**：在成熟制程（无法靠频率硬刚 5nm Apple）的前提下，4-wide 是"够用且能做出来"的最佳点。

### 3.3 RTL 行数分解（一个 4-wide 核内部）

```
FTC862 单核 RTL（推测分解）        行数占比（推测）
├─ 取指 / 分支预测（BTB+TAGE+RAS）   ~15%   ← 预测器是大头
├─ 译码 / 寄存器重命名               ~15%   ← 4-wide 重命名表复杂
├─ issue queue + 唤醒/选择           ~12%
├─ 执行单元（ALU/FPU/SIMD）          ~15%
├─ load/store unit + LSQ             ~12%   ← 内存序推断是大头
├─ L1 D-cache + L2 cache             ~10%
├─ ROB + checkpoint 恢复             ~8%
├─ 系统寄存器 / 异常 / SMMU 接口      ~8%
└─ 调试 / 性能计数器 / DFT 接入       ~5%
```

这张分解图对应了下一节的 Verilog 骨架——我们用 4 个可运行 `.v` 文件展示了其中**取指/执行/forwarding** 三块的教学缩影。

---

## 4. 可运行 RTL 骨架（项目 artifact，保留并强化）

> 以下 4 个文件位于 [`rtl/`](./rtl/) 目录，**可被 Icarus Verilog / Verilator 综合并仿真**。
> 它们不是飞腾真实代码（飞腾 RTL 不开源），但反映**真实芯片**的关键结构，
> 风格借鉴 [learn-verilog](https://github.com/AsFang/learn-verilog) 与 nyucpu 课件。
> 它们与 [`Capstone/cpu_simulator/rv32i_sim.py`](../Capstone/cpu_simulator/rv32i_sim.py) 的 Python 模拟器一一对应——
> **同一份 forwarding 逻辑，硬件版本（本节）和软件版本（Capstone）是等价的**。

| 文件 | 对应硬件结构 | 对应 Capstone 函数 | 真实飞腾对应 |
|------|------------|-----------------|------------|
| [`rtl/alu.v`](./rtl/alu.v) | ALU（10 条 RV32I 算术） | `_alu()` | FTC862 的 4–6 个 ALU 单元（2 cluster） |
| [`rtl/forwarding_unit.v`](./rtl/forwarding_unit.v) | EX→EX / MEM→EX 转发 | `_forward()` | FTC862 的全 forwarding 网络（4-wide 更复杂） |
| [`rtl/two_bit_predictor.v`](./rtl/two_bit_predictor.v) | 2-bit 饱和预测 FSM | `TwoBitPredictor` 类 | FTC862 的 TAGE-SC-L 预测器（复杂 1000×） |
| [`rtl/tb_alu.v`](./rtl/tb_alu.v) | ALU 自检 testbench | — | 验证流程的缩影 |

### 4.1 ALU（[`rtl/alu.v`](./rtl/alu.v)）——一条 ADD 在硬件里是什么

```verilog
module alu #(
    parameter XLEN = 32
)(
    input  wire [3:0]       alu_op,
    input  wire [XLEN-1:0]  a, b,
    output wire [XLEN-1:0]  result,
    output wire             zero
);
    localparam ALU_ADD=4'b0000, ALU_SUB=4'b0001, ALU_AND=4'b0010,
               ALU_OR=4'b0011,  ALU_XOR=4'b0100, ALU_SLL=4'b0101,
               ALU_SRL=4'b0110, ALU_SRA=4'b0111, ALU_SLT=4'b1000,
               ALU_SLTU=4'b1001;
    reg [XLEN-1:0] r;
    wire signed [XLEN-1:0] sa = a, sb = b;
    wire [4:0] shamt = b[4:0];
    always @(*) begin
        case (alu_op)
            ALU_ADD : r = a + b;
            ALU_SUB : r = a - b;
            ALU_AND : r = a & b;
            ALU_OR  : r = a | b;
            ALU_XOR : r = a ^ b;
            ALU_SLL : r = a << shamt;
            ALU_SRL : r = a >> shamt;
            ALU_SRA : r = sa >>> shamt;
            ALU_SLT : r = (sa < sb) ? 1 : 0;
            ALU_SLTU: r = (a  < b ) ? 1 : 0;
            default : r = 0;
        endcase
    end
    assign result = r;
    assign zero   = (r == 0);
endmodule
```

**飞腾 FTC862 真实实现差异**（`[推测-依据]`）：
- 约 **4–6 个 ALU 单元**（分 2 个 cluster，对应 2 ALU/周期实测 `[实测]`）。
- 每个 ALU 支持完整算术 + 移位 + branch compare，综合后约 **2000–4000 标准单元**（NAND/NOR/MUX/FF）。
- ARMv8 比 RV32I 多：**条件指令（CSEL/CSINC）、位域操作（BFM/UBFM）、带移位的算术（ADD/SUB LSL/ASR/...）、PAC 指令**（v8.3，但飞腾 PAuth 标 ⚠️ 部分支持 `[扩展专题]`）。
- **教学 ALU 是纯组合逻辑，真实 ALU 要处理：carry chain 优化、shift 用 barrel shifter、sub 用加补码 + 进位**——真实 RTL 比上面复杂 10×。

**运行方式**：
```bash
iverilog -o tb_alu rtl/tb_alu.v rtl/alu.v && vvp tb_alu
# 预期输出：=== ALU testbench: 14 pass, 0 fail === [ALL PASS]
```

### 4.2 Forwarding 单元（[`rtl/forwarding_unit.v`](./rtl/forwarding_unit.v)）——Capstone 的硬件版

```verilog
module forwarding_unit (
    input  wire [4:0] id_ex_rs1, id_ex_rs2,
    input  wire [4:0] ex_mem_rd,
    input  wire       ex_mem_reg_write,
    input  wire       ex_mem_is_load,      // load-use 例外
    input  wire [4:0] mem_wb_rd,
    input  wire       mem_wb_reg_write,
    output wire [1:0] forward_a, forward_b
);
    // forward_a: EX/MEM 优先（最新），次选 MEM/WB，否则用 RegFile
    // ...（完整代码见 rtl/forwarding_unit.v）
endmodule
```

**三个关键观察**：
1. **`ex_mem_is_load` 是 load-use stall 的物理基础**：load 数据在 MEM 阶段末才出来，EX 阶段无法 forward，**必须 stall 1 cycle**。这正是 Capstone 模拟器 `_id` 函数里检测 load-use 的逻辑。
2. **`rd != 0` 检查**：x0 永远是 0，写 x0 无效，不能 forward。
3. **4-wide 让 forwarding 网络爆炸**：教学版是 1 条流水线的 2 路转发，FTC862 4-wide 需要 **4 条流水线 × 多级 × 多路**的转发网络，组合逻辑深度和扇出是教学版的 **几十倍**——这也是 4-wide 时序收敛难的根本原因。

### 4.3 2-bit 饱和预测器（[`rtl/two_bit_predictor.v`](./rtl/two_bit_predictor.v)）

```verilog
module two_bit_predictor (
    input wire clk, rst_n,
    output wire predict_taken,
    input wire branch_resolve, taken_actual
);
    localparam [1:0] SN=2'b00, WN=2'b01, WT=2'b10, ST=2'b11;
    reg [1:0] state, next_state;
    always @(posedge clk or negedge rst_n)
        state <= !rst_n ? WN : next_state;
    always @(*)
        if (branch_resolve)
            case (state)
                SN: next_state = taken_actual ? WN : SN;
                WN: next_state = taken_actual ? WT : SN;
                WT: next_state = taken_actual ? ST : WN;
                ST: next_state = taken_actual ? ST : WT;
            endcase
        else next_state = state;
    assign predict_taken = state[1];
endmodule
```

**真实 FTC862 预测器**（`[推测-依据]`）：
- 状态机更复杂，推测为 **TAGE-SC-L 变种**（多历史长度表 + 统计修正器 + loop 预测器），是 CBP 竞赛冠军级算法 `[论文]`。
- 状态存储：**BTB（branch target buffer）+ PHT（pattern history table）+ RAS（return address stack）**，合计 **数百 KB SRAM** `[报告]`。
- 教学版是 1 个 entry 的 2-bit FSM，FTC862 是 **数 K entries × 多个表**，复杂度 **1000×**，但**核心 FSM 思想不变**——这就是教学骨架的价值。

---

## 5. 公司级 die photo 对标（原文缺，本文补强）

> 原文 §6 只对比了开源核 BOOM，缺少公司级 die photo 对标。本节补齐。
> 数据来源：Wikichip、Chips and Cheese、TechInsights 拆解报告、ISSCC 论文。`[第三方报告]`

### 5.1 核面积 / 晶体管 / 频率对标表（2020–2023 代际）

| 处理器 | 核类型 | 工艺 | 单核面积（含 L2） | 单核晶体管 | 频率 | IPC（specint2017 估） | 来源 |
|--------|-------|------|---------------:|----------:|--------:|:--------------:|------|
| **飞腾 D3000M FTC862** | 服务器核（推测）| 7nm 级 `[推测]` | **~3–5 mm²** `[推测]` | 未公开 | **2.5 GHz** `[实测]` | ~2 | `[推测-依据]` |
| **ARM Cortex-A76** | 移动/服务器 | 7nm TSMC | ~2.5–3.5 mm² `[报告]` | 未公开 | 2.8–3.0 GHz | ~2 | Wikichip |
| **ARM Cortex-A78** | 移动 | 5nm TSMC | ~2.0–2.8 mm² `[报告]` | 未公开 | 3.0 GHz | ~2.1 | Wikichip |
| **ARM Neoverse N2（Perseus）** | 服务器 | 5nm | ~3.5–4.5 mm² `[报告]` | 未公开 | 3.0 GHz | ~2.2 | Wikichip |
| **Apple Firestorm（M1 P）** | 桌面 | 5nm TSMC | **~7–9 mm²**（含大 L1/L2）`[报告]` | 未公开 | 3.2 GHz | **~3** | Chips and Cheese |
| **Intel Golden Cove（Alder Lake P）** | 桌面/服务器 | Intel 7 | **~12–15 mm²** `[报告]` | ~5 亿 | 3.5–5 GHz | ~2.8 | Wikichip |
| **AMD Zen 4** | 桌面/服务器 | TSMC N5 | **~5–7 mm²**（含 1MB L2）`[报告]` | 未公开 | 5.0 GHz | ~2.6 | Chips and Cheese |
| **华为鲲鹏 920（TaiShan v110）** | 服务器 | 7nm TSMC | **~2.5–3.5 mm²** `[推测]` | 未公开 | 2.6 GHz | ~1.8 | `[推测]` |

**关键判断 3（`[推测-依据]`）**：

> FTC862 单核面积推测 **3–5 mm²（7nm 级）**，**与 ARM Cortex-A76/A78、华为鲲鹏 920 同档**（都是 4-wide OoO + 7nm 代的合理面积），**显著小于 Apple Firestorm（~7–9 mm²）和 Intel Golden Cove（~12–15 mm²）**。
> 差距的来源不是"飞腾 RTL 写得差"，而是**架构宽度（4-wide vs 8-wide）+ cache 配置（L1 64K vs Apple 192K）+ 工艺（7nm vs 5nm）+ 设计激进程度**的综合结果。**飞腾在这个档位是合格的工程产物，不是落后品。**

### 5.2 整 die 对比（服务器多核 SoC）

| 处理器 | 核数 | die 面积 | 工艺 | 晶体管数 | 推测自研面积比 | 来源 |
|--------|:---:|--------:|------|--------:|:------------:|------|
| 飞腾 D3000M | 8 | 未公开 | 7nm 级 `[推测]` | 未公开 | ~40–50% | `[推测]` |
| 华为鲲鹏 920 | 64 | ~600 mm² `[报告]` | 7nm | 未公开 | ~45–55% | Wikichip |
| AMD EPYC Genoa（Zen4） | 96 | ~12 die chiplet `[报告]` | 5nm | 未公开 | ~70%（核心大） | Wikichip |
| Apple M1 | 8（4P+4E）| ~120 mm² `[报告]` | 5nm | 160 亿 | ~60%（含 GPU） | TechInsights |
| Intel Sapphire Rapids | 60（chiplet）| ~400 mm² `[报告]` | Intel 7 | ~800 亿 | ~65% | Wikichip |

> **观察**：飞腾作为后发厂商，**外购 IP 面积比偏高（~50–60%）是常态**。这不是落后，而是**经济理性**——重造 DDR PHY 的边际收益为零，不如把研发投在 CPU 核差异化。

### 5.3 die photo 估算的可信度警告

所有"单核面积"数字若非飞腾官方公布，都是 `[推测]` 或 `[第三方报告]`。die photo 分析依赖 **TechInsights 等机构的反向工程**（剥层拍照 + 图像识别），飞腾 D3000M 至今**未见公开 die photo 拆解**（与 Apple/AMD/Intel 每代必拆形成对照）。这是飞腾"信息不对称"的体现——**既可能是保密好，也可能是国外机构不关注**。

---

## 6. IP 集成的坑：外购 PHY 的兼容性地狱

> 这是 RTL/SoC 工程师的真实痛苦，也是飞腾这类厂商最容易被低估的难度。

### 6.1 外购 IP 的三大坑

**坑 1：接口协议对齐**
- 自研 FTC862 核的 AXI master 端口，要对接 ARM CMN-600 一致性网络，再接外购 DDR PHY。
- **AXI 版本（AXI3/AXI4/AXI5）、位宽（128/256/512-bit）、原子操作支持（LSE 在哪一段处理）、缓存一致性属性（Inner/Outer Shareable）**——任何一个不匹配都会导致**功能性 bug**（数据错）或**性能 bug**（一致性流量暴涨）。`[报告]`
- 飞腾的 LSE 原子（v8.1，55 助记符 `[扩展专题]`）需要**在核内、在 L2、还是在 LLC 处理**？这是 RTL 架构决策，错了会导致多核原子语义不正确。

**坑 2：时序边界与电压域**
- DDR PHY 工作在 1.2V（DDR4）或 1.1V（DDR5），CPU 核工作在 ~0.8V（7nm）。
- 两者的信号要穿越**电压域隔离单元**（level shifter）+ **时钟域跨越**（CDC, clock domain crossing）。
- CDC 是芯片 bug 的重灾区，需要**形式化 CDC 检查工具**（Synopsys SpyGlass CDC）逐条路径验证 `[报告]`。

**坑 3：验证与 DFT 接入**
- 外购 IP 通常自带**加密 RTL（black box）**，你只能看到接口和文档。
- 验证时要把 IP 的**行为模型**接入自研 testbench，**任何 IP 内部 bug 你都修不了**，只能报给 IP 供应商等 patch。
- DFT（扫描链）要穿过 IP，但 IP 的扫描链配置由供应商决定，**集成时要做 scan stitching**（拼接扫描链），错综复杂。

### 6.2 飞腾的 IP 重用策略推测

**关键判断 4（`[推测-依据]`）**：

> 飞腾作为后发厂商，**IP 重用率必然偏高**（预计外购 IP 占 die 面积 40–50%）。其策略推测为：
> 1. **CPU 核 + L3 + 一致性 fabric 自研**（核心竞争力，不可外购）。
> 2. **DDR PHY / PCIe / SerDes 外购**（Synopsys 或 ARM，全球唯几供应商）。
> 3. **GIC / SMMU / AMBA 用 ARM 授权**（生态绑定，无替代）。
> 4. **SRAM compiler + 标准单元用 foundry PDK**（TSMC 或 SMIC 配套）。
> 5. **加密 / SM3/SM4**：因为 ARMv8.4 把这些做成 ISA 指令（`[扩展专题]` 第 22–23 项），飞腾**不需要外购独立加密 IP**，在核内 SIMD 单元实现即可——这是 ARMv8.4 对飞腾的"红利"。

**与华为鲲鹏的对比**：鲲鹏 920 据公开信息，DDR PHY 和 SerDes 也外购（推测 Synopsys/ARM）`[推测]`。两者 IP 重用策略类似，差异主要在**自研核的代际积累**（鲲鹏 TaiShan 已迭代多代，飞腾 FTC862 代际较短）。

---

## 7. RTL → Tape-out 完整流程（飞腾走哪条路）

### 7.1 通用流程（业界标准）

| 阶段 | 工具 | 时间 | 产出 | 飞腾推测 |
|------|------|----:|------|---------|
| **Spec** | Markdown / 内部工具 | 4–8 周 | 微架构 spec（即扩展专题那种 ISA 表） | 自研 `[推测]` |
| **ISA Test** | 汇编 + 自研工具 | 持续 | 测试程序集 | 类似本项目 [Capstone/cpu_simulator/](../Capstone/cpu_simulator/) 的工业版 |
| **RTL 设计** | SystemVerilog / Chisel | 6–12 月 | .v / .sv 文件 | **SystemVerilog**（业界主流，与海思同）`[推测]` |
| **功能验证** | VCS / Xcelium + UVM | 持续 | 跑过所有 ISA test | **UVM-based** `[推测]` |
| **形式验证** | JasperGold / VC Formal | 数月 | 关键不变量证明 | 推测用 Synopsys VC Formal `[推测]` |
| **逻辑综合** | Design Compiler / Genus | 数周 | 门级网表 | **Synopsys Design Compiler** `[推测]` |
| **等价性检查** | Conformal / Formality | 数天 | 综合 ≡ RTL | 推测 Formality `[推测]` |
| **DFT 插入** | TestKompress / Tessent | 数周 | 扫描链 / BIST | 推测 Tessent（西门子）`[推测]` |
| **布局布线** | ICC2 / Innovus | 数月 | GDSII | **Cadence Innovus 或 Synopsys ICC2** `[推测]` |
| **时序收敛** | PrimeTime / Tempus | 数月 | STA 报告（slack > 0） | 推测 PrimeTime `[推测]` |
| **物理验证** | Calibre | 数周 | DRC / LVS / ERC | **西门子 Calibre**（行业标准）`[推测]` |
| **流片** | TSMC / SMIC | 2–3 月 | 物理芯片 | **受制裁后推测 SMIC N+1/N+2** `[推测]` |
| **Post-silicon** | ATE / 实测 | 3–6 月 | 量产 OK | 见 [Expert_17_DFT_PostSilicon](../Expert_17_DFT_PostSilicon/) |

**总计**：一颗现代 CPU 从立项到量产约 **3–5 年**。飞腾 D3000M 推测 2019–2020 立项，2023 量产 `[推测]`。

### 7.2 工具链推测（飞腾用 Synopsys 还是 Cadence）

**可信推测（`[推测-依据]`）**：
- **Synopsys 全家桶为主**：Design Compiler（综合）+ PrimeTime（STA）+ VCS（仿真）+ VC Formal（形式验证）+ SpyGlass（CDC/Lint）。Synopsys 在中国市场份额最高，飞腾作为国产厂商大概率以 Synopsys 为主。
- **Cadence 辅助**：Innovus（P&R）或 Tempus（STA 备选）。
- **西门子 Mentor（现 Siemens EDA）**：Calibre（物理验证）+ Tessent（DFT）——这两块西门子是事实标准。
- **国产 EDA 替代**：受制裁影响，飞腾可能在**部分环节尝试华大九天/概伦电子**，但全流程替代尚不成熟（详见 [Expert_16_EDA_Toolchain](../Expert_16_EDA_Toolchain/)，阶段 E）。

**不可信推测 / 业内传言（标注清楚，不当作事实）**：
- 飞腾 E2000（嵌入式）可能用 SMIC 14nm `[推测]`
- 飞腾 D2000（前代）推测 TSMC 16nm `[推测]`
- 飞腾 D3000 系列**可能**改用 SMIC N+1（7nm 等效），受 2020 美国制裁影响 `[推测]`
- 这些工艺传言**未经飞腾官方确认**，请勿当定论引用（诚实声明）。

---

## 8. 关键挑战（硬件设计师的真实困境）

### 8.1 时序收敛（最难的部分）
飞腾 2.5 GHz 对应 cycle time = 400 ps `[实测]`。每条路径延迟必须 < 400 ps。
- 最长路径通常是 **L1 cache 读 → ALU → 数据 forward 回 RF**。
- 加 1 个 cycle 就能解决，但 IPC 损失 5–15%。
- **权衡**：深度 vs 频率（Intel Pentium 4 选频率深度，31 级流水，失败；Core 选 14-stage 平衡，成功 `[报告]`）。
- 飞腾 4-wide 在 7nm 级做到 2.5 GHz，时序收敛压力**显著大于 Apple M1 在 5nm 做 3.2 GHz**——因为 5nm 的 FO4 延迟低得多 `[第三方报告]`。

### 8.2 Power delivery
8 核 2.5 GHz 全速运行可能瞬态电流 > 100 A。
- IR drop > 50 mV 就可能逻辑错误。
- 需要 **C4 bump + 多层 PCB 电源平面**。
- 飞腾封装推测 14–18 层 PCB `[推测]`（详见 [Expert_15_Package_Chiplet](../Expert_15_Package_Chiplet/)）。

### 8.3 信号完整性（SI）和电磁兼容（EMC）
- 高速信号串扰（crosstalk）。
- 同时开关噪声（SSN）。
- 信号反射 / 阻抗匹配。

### 8.4 DFT（Design for Test）
- 芯片必须能"自测"——上电后用扫描链测每个 FF。
- 飞腾 D3000M 推测有 **>100K 扫描 FF + MBIST 测内存** `[推测]`。
- 良率损失 < 1% 才能 cost-effective（即 DFT 逻辑开销 < 芯片面积 5%）。详见 [Expert_17_DFT_PostSilicon](../Expert_17_DFT_PostSilicon/)。

### 8.5 IP 集成的回归测试地狱
- 每次外购 IP 升级（vendor patch），**整个 SoC 要重跑回归**（regression）。
- 飞腾如果用 Synopsys DDR PHY，**Synopsys 发版节奏与飞腾流片节奏对齐**是项目管理难题。

---

## 9. 战略伤疤的 RTL 后果：补 SVE/BF16/I8MM 要改多少

这是本视角对 D3000M **战略伤疤**的 RTL 层面解读（呼应 [Expert_21_AI_Positioning](../Expert_21_AI_Positioning/)）。

D3000M 缺 SVE/SVE2/BF16/I8MM `[扩展专题]` 第 25–27 项，在 RTL 上意味着：

| 缺失特性 | RTL 后果 | 补上的工程量（推测） |
|---------|---------|-------------------:|
| **SVE/SVE2**（可变长向量） | 向量寄存器堆是固定 128-bit NEON，无 VL（vector length）寄存器、无 predicate 寄存器 | **极大**：要重写整个向量执行单元 + 新增 predicate 逻辑 + 改 ISA 译码。~30–50 人月 `[推测]` |
| **BF16**（bfloat16） | FP 转换单元只支持 FP16/FP32/FP64，无 BFCVT | **中**：加 BF16↔FP32 转换 + BFDOT/BFMMLA 执行路径。~10–20 人月 `[推测]` |
| **I8MM**（int8 矩阵乘） | 有 UDOT（4×int8 点积），但无 SMMLA（8×8 矩阵乘） | **小-中**：在现有 UDOT lane 基础上扩展矩阵累加。~5–10 人月 `[推测]` |
| **FHM**（fp16→fp32 横向乘累加） | 无 FMLAL/FMLSL | **小**：可用现有 FP16 NEON 组合替代 |

**关键洞察**：补 **I8MM 和 BF16** 是"小改 RTL、大改生态"的性价比最高的下一步（对 AI 推理场景收益巨大 `[Expert_05]`）。补 **SVE** 是"大改 RTL、大改生态"，飞腾下一代是否做 SVE，是判断其是否押注 HPC/AI 市场的关键信号。

---

## 10. 设计决策评估（飞腾哪些认可 / 哪些该改）

### 10.1 认可的 RTL/SoC 决策
1. **架构许可 + 自研 4-wide 核**：在制裁背景下，自研核是唯一可控路径，决策正确。
2. **4-wide 而非 6/8-wide**：工程甜蜜点，与成熟制程的频率上限匹配，IPC 收益与 RTL 成本平衡。
3. **ARMv8.4 全面实现**：把 SM3/SM4/UDOT 等做进核内 SIMD，免去独立加密 IP，RTL 简洁。
4. **外购 PHY 而非自研**：经济理性，把研发投在 CPU 核差异化。

### 10.2 该改的决策（从 RTL 角度）
1. **缺 SVE/BF16/I8MM**：下一代必须补，否则 AI 推理市场失守（详见 E21）。
2. **缺公开 die photo / 微架构白皮书**：不像 ARM/AMD 有详尽微架构文档，飞腾对外信息极少，**限制了高校合作与软件生态优化**（编译器/库优化依赖微架构细节）。
3. **代际 RTL 复用率不明**：FTC862 多少 % 继承自 FTC861（D2000），多少 % 重写？这影响迭代速度。公开信息不足。

---

## 11. 这一视角的盲区与反方（诚实段，强制）

> 项目宪法 §4.3 强制：每个 Expert 必须有一节"盲区与反方"，杜绝软文。

**盲区 1：RTL 视角看不见软件生态**。
RTL 工程师觉得"补上 BF16 就能跑 AI"，但**软件栈（编译器/算子库/框架适配）才是真正的瓶颈**。即便 RTL 补了 BF16，没有 ARM Compute Library / oneDNN 适配，性能也上不去。这一点 [Expert_05_AI_Inference](../Expert_05_AI_Inference/) 和 [Expert_22_OpenSource_Ecosystem](../Expert_22_OpenSource_Ecosystem/) 更有发言权。

**盲区 2：RTL 视角高估"自研率"的价值**。
"自研核"听起来很酷，但**从商业角度，外购 ARM Cortex 核授权可能更经济**（省 300 人年研发）。飞腾选择自研是**地缘政治 + 长期可控性**驱动的，不是纯技术最优。这一点 [Expert_07_Business](../Expert_07_Business/) 和 [Expert_19_Geostrategy](../Expert_19_Geostrategy/) 才能说清。

**盲区 3：所有"IP 比例""RTL 行数""核面积"都是推测**。
飞腾未公开 die photo、IP BOM、RTL 行数。本文所有数字基于业界类比 `[推测-依据]`，**可能有 30–50% 误差**。读者切勿把推测当事实引用。

**盲区 4：RTL 视角低估物理设计难度**。
RTL 能综合 ≠ 能流片。7nm 级的物理设计（布局、布线、IR drop、EM、工艺变异）是另一重地狱，RTL 工程师看不见。详见 [Expert_13_VLSI_Physical](../Expert_13_VLSI_Physical/)（阶段 C）。

**反方观点**：有人会说"飞腾 RTL 都是抄 ARM Cortex，没有原创性"。**反驳**：架构许可厂商（Apple、高通、华为）的核都是"参照 ARM 微架构思路 + 自研实现"，**业界定义的"自研"就是 RTL 自己写**，不算抄。飞腾 FTC862 的具体实现细节（forwarding 网络、ROB 大小、预测器配置）必然与 Cortex 不同，属于自研。但**原创性研究突破（如 Apple Firestorm 8-wide 的创新）确实没有**——这与所有商用 CPU 一样，是"成熟研究的集成"，见 [Expert_01_Scientist](../Expert_01_Scientist/) §2 结论。

---

## 12. 与其他视角对偶（一致 / 冲突，强制）

| 对偶视角 | 一致/冲突 | 关键点 |
|--------|:--------:|------|
| **[Expert_01_Scientist](../Expert_01_Scientist/)** | ✅ 一致 | 论文 → RTL 模块映射。E01 的"论文-设计映射表"是 E03 的上层抽象。 |
| **[Expert_02_Architect](../Expert_02_Architect/)** | ✅ 一致 | 架构师定 PPA 目标 → E03 写 RTL 实现 PPA。同一硬币两面。 |
| **[Expert_05_AI_Inference](../Expert_05_AI_Inference/)** | ⚠️ 冲突 | E03 觉得"缺 BF16 是小改 RTL"，E05 指出**软件栈适配才是真瓶颈**。 |
| **[Expert_07_Business](../Expert_07_Business/)** | ⚠️ 冲突 | E03 觉得"自研核很酷"，E07 质问**自研的 R&D 投入回报率**（vs 买 Cortex 核授权）。 |
| **[Expert_13_VLSI_Physical](../Expert_13_VLSI_Physical/)** | ✅ 互补 | E03 写 RTL，E13 把 RTL 变 GDSII。时序收敛是两边的共同战场。 |
| **[Expert_16_EDA_Toolchain](../Expert_16_EDA_Toolchain/)** | ✅ 一致 | E03 用什么 EDA 工具，E16 系统讨论。 |
| **[Expert_17_DFT_PostSilicon](../Expert_17_DFT_PostSilicon/)** | ✅ 互补 | E03 在 RTL 插 DFT，E17 在硅后用扫描链测芯片。 |
| **[Expert_19_Geostrategy](../Expert_19_Geostrategy/)** | ⚠️ 部分冲突 | E03 的"外购 DDR PHY"是工程理性，E19 指出**制裁下 PHY 供应可能被切断**（地缘风险）。 |
| **[Expert_21_AI_Positioning](../Expert_21_AI_Positioning/)** | ✅ 一致 | E03 §9 的"战略伤疤 RTL 后果"是 E21 命题的 RTL 层注脚。 |
| **[Expert_11_Compiler_Research](../Expert_11_Compiler_Research/)** | ⚠️ 部分冲突 | E03 的 forwarding/重命名细节影响编译器调度，但 E03 的 RTL 文档不公开 → 编译器优化受限。 |

---

## 13. 飞腾 RTL vs 开源 CPU 对比（保留原文，扩充）

| 项目 | 核数 | ISA | 工艺 | RTL 行数 | IPC | 开源 |
|------|:---:|----|----:|--------:|:---:|:---:|
| **飞腾 FTC862** | 8 | ARMv8.4 | 7nm 级 | ~150–250 万 SV `[推测]` | ~2 | ❌ 闭源 |
| **Apple Firestorm（M1 P）** | 8（4P+4E） | ARMv8.5 | 5nm | ~数百万 `[报告]` | ~3 | ❌ 闭源 |
| **AMD Zen 4** | 16 | x86-64 | 5nm | ~数百万 `[报告]` | ~2.6 | ❌ 闭源 |
| **华为 TaiShan v110（鲲鹏 920）** | 64 | ARMv8.2 | 7nm | ~150–200 万 SV `[推测]` | ~1.8 | ❌ 闭源 |
| **BOOM**（开源 RISC-V OoO）| 1–4 | RISC-V | 仿真 | ~60K Scala `[官方]` | ~1.5 | ✅ |
| **RocketChip**（开源 InO）| 1+ | RISC-V | 仿真/流片 | ~20K Scala `[官方]` | ~1 | ✅ |
| **Capstone-B 模拟器**（本项目）| 1（5 级流水）| RV32I | Python | 700 行 | ~0.8 | ✅ |

**飞腾 RTL 不开源**（vs RISC-V BOOM 开源）——这是飞腾 vs RISC-V 生态的关键差异，详见 [Expert_22_OpenSource_Ecosystem](../Expert_22_OpenSource_Ecosystem/)。

---

## 14. 参考文献（≥15，分级标注）

> 项目宪法 §4.1 要求 ≥15 条、≥5 论文/标准/官方文档。原文 §8 无参考章节（0 条），本节补齐。

### 经典教材与体系结构（[书]）
1. **[书]** Hennessy & Patterson, *Computer Architecture: A Quantitative Approach*（6th ed., 2019）——RTL 风格附录、ILP/MLP/power wall 的权威论述。
2. **[书]** Harris & Harris, *Digital Design and Computer Architecture: ARM Edition*（2015）——本节 Verilog 骨架的风格来源，含完整 ARMVerilog 流水线。
3. **[书]** Weste & Harris, *CMOS VLSI Design: A Circuits and Systems Perspective*（4th ed., 2010）——从 RTL 到物理的综合/后端原理。
4. **[书]** Sorin, Hill, Wood, *A Primer on Memory Consistency and Cache Coherence*（2nd ed., Morgan & Claypool, 2020）——AXI/一致性协议的理论基础。

### 微架构经典论文（[论文]）
5. **[论文]** Tomasulo, "An Efficient Algorithm for Exploiting Multiple Arithmetic Units"（IBM JRD, 1967）——重命名/forwarding 的源头。
6. **[论文]** Smith, Johnson, Horowitz, "Implementing Precise Interrupts & Exceptions"（ISCA 1989）——ROB + checkpoint 恢复。
7. **[论文]** Smith & Sohi, "The Microarchitecture of Superscalar Processors"（Proc. IEEE, 1995）——superscalar RTL 综述。
8. **[论文]** Yeh & Patt, "Two-Level Adaptive Branch Prediction"（MICRO 1991）——2-bit 预测器的源头（对应 `rtl/two_bit_predictor.v`）。
9. **[论文]** Seznec & Michaud, "A Case for (Partially) TAgged GEometric History Length Branch Prediction"（JILP 2006）——TAGE 预测器，FTC862 推测采用。
10. **[论文]** Keller, "Look-Ahead Processors"（ACM Computing Surveys, 1975）——寄存器重命名理论。
11. **[论文]** Smith & Plezskun, "Implementing Precise Interrupts in Pipelined Processors"（IEEE TC, 1988）——ARF+PRF vs 统一 PRF。
12. **[论文]** Wall, "Limits of Instruction-Level Parallelism"（WRL TR, 1991）——ILP Wall 的量化，解释为何 4-wide 是甜蜜点。

### IP 集成与 SoC 组装（[标准]/[官方]/[报告]）
13. **[标准]** ARM AMBA AXI / ACE Protocol Specification（ARM IHI 0022, 多版本）——自研核接外购 IP 的接口协议标准。
14. **[官方]** ARM CoreLink CMN-600/700 Product Brief（ARM 官方）——一致性网络 IP，飞腾推测采用。
15. **[官方]** ARM Generic Interrupt Controller Architecture Specification（GIC v3/v4, ARM IHI 0069）——中断控制器规范。
16. **[报告]** Linley Group / Semico Research, "SoC IP Market Analysis"（多年度）——外购 IP 占比行业数据。
17. **[官方]** Synopsys DesignWare DDR PHY / PCIe Controller Product Brief——外购 PHY 代表。

### die photo 与微架构分析（[第三方报告]）
18. **[报告]** Wikichip, "Cortex-A76 Microarchitecture"（2018）+ "Apple Firestorm"（2020）+ "Zen 4"（2022）——核面积/晶体管对标数据来源。
19. **[报告]** Chips and Cheese, "Apple M1 Firestorm Deep Dive"（2021）+ "AMD Zen 4 Analysis"——微架构深度分析。
20. **[报告]** TechInsights, "Apple M1 Die Teardown"（2020）——die photo 反向工程。

### 开源 CPU 与 RTL（[官方]）
21. **[官方]** RISC-V BOOM（github.com/riscv-boom/riscv-boom）——开源 OoO 核，本节 RTL 行数对标。
22. **[官方]** SiFive / Chipyard Framework（UC Berkeley）——Chisel-based RTL 生成框架。

### 飞腾与国产 CPU（[官方]/[推测]）
23. **[官方]** 飞腾信息技术有限公司官网产品页（D2000/D3000/S2500）——公开规格，未公开 RTL/die photo。
24. **[官方]** ARM Architecture Reference Manual（ARM ARM DDI 0487G.b/K.b）——ARMv8.x ISA 权威，对应本项目 [`isa_reference/`](../isa_reference/)。

### 行业流程与 EDA（[报告]/[官方]）
25. **[报告]** Semico / ES Alliance, "IC Design Flow Survey"（年度）——RTL→tape-out 流程业界基准。
26. **[官方]** Synopsys / Cadence / Siemens EDA 官方工具文档（DC, PrimeTime, Innovus, Calibre, Tessent）——§7 工具链推测依据。

> **参考计数**：26 条，其中论文 8 条（Tomasulo/Smith/Sohi/Yeh/Seznec/Keller/Smith&Plezskun/Wall）+ 标准 2 条（AXI/GIC）+ 书 4 条 + 官方 6 条（ARM/Synopsys/BOOM/SiFive/飞腾/ARM ARM）+ 报告 6 条（Wikichip/Chips and Cheese/TechInsights/Linley/Semico/ES Alliance）。**满足"≥15 条、≥5 论文/标准/官方"门槛。**

---

## 15. 自己动手学硬件设计

### 入门（一周）
- *Digital Design and Computer Architecture*（Harris & Harris）——ARM 版有完整 Verilog 流水线。
- [nand2tetris.org](https://www.nand2tetris.org/) —— 从 NAND 到 CPU。
- 本项目 [`rtl/`](./rtl/) 4 个文件 + [`Capstone/cpu_simulator/rv32i_sim.py`](../Capstone/cpu_simulator/rv32i_sim.py) ——软硬件对照学。

### 进阶（一学期）
- RISC-V BOOM 源码：[github.com/riscv-boom/riscv-boom](https://github.com/riscv-boom/riscv-boom)
- nyucpu 课程：[github.com/nyucpu/Advanced-Computer-Architecture](https://github.com/nyucpu)
- ETHz Digital Design and Computer Architecture（Onur Mutlu，YouTube 全集）
- **学 IP 集成**：看 ARM CoreLink CMN-600 TRM + Synopsys DesignWare DDR PHY 手册，理解接口协议地狱。

### 工业级
- *Computer Architecture: A Quantitative Approach* 附录（RTL 风格）。
- Synopsys / Cadence 官方培训资料（$$$，或通过大学计划获取）。
- **学 SoC 组装**：找一个 ARM Juno 开发板文档，看 ARM 如何把 Cortex-A + Mali + DDR PHY + PCIe 拼成参考 SoC。

---

## 16. 延伸阅读（项目内 + 外部）

**项目内对偶**：
- [Capstone-B 模拟器](../Capstone/cpu_simulator/rv32i_sim.py)——把本节的 forwarding 单元用 Python 跑通（软硬件等价）。
- [Capstone-A Alpha 21264 arch_diagram](../Capstone/alpha_21264_study/arch_diagram.md)——双 cluster 拓扑，4-wide 的祖师爷。
- [Expert_01_Scientist](../Expert_01_Scientist/)——本节的论文层抽象。
- [Expert_02_Architect](../Expert_02_Architect/)——本节之上的 PPA 决策层。
- [Expert_13_VLSI_Physical](../Expert_13_VLSI_Physical/)——本节之后的物理实现层（阶段 C，待写）。
- [Expert_16_EDA_Toolchain](../Expert_16_EDA_Toolchain/)——本节 §7 工具链的系统讨论（阶段 E，待写）。
- [Expert_17_DFT_PostSilicon](../Expert_17_DFT_PostSilicon/)——本节 §8.4 DFT 的硅后展开（阶段 E，待写）。
- [Expert_21_AI_Positioning](../Expert_21_AI_Positioning/)——本节 §9 战略伤疤的全局展开。
- [Expert_22_OpenSource_Ecosystem](../Expert_22_OpenSource_Ecosystem/)——本节 §13 开源 vs 闭源的生态讨论。

**外部**：
- [Wikichip](https://en.wikichip.org/wiki/WikiChip) ——核面积/微架构数据库。
- [Chips and Cheese](https://chipsandcheese.com) ——深度微架构分析。
- [BOOM 源码](https://github.com/riscv-boom/riscv-boom) ——唯一开源的 OoO 核 RTL。

---

📌 **下一步**：去 [Expert_04_OS_Kernel](../Expert_04_OS_Kernel/) 看操作系统专家如何与硬件协同；或去 [Expert_13_VLSI_Physical](../Expert_13_VLSI_Physical/) 看 RTL 如何变成 GDSII。

---

**附：本节 artifact 清单（可运行/可验证）**

| artifact | 路径 | 语言 | 用途 |
|---------|------|------|------|
| ALU | [`rtl/alu.v`](./rtl/alu.v) | Verilog 2001 | 教学版 10 条 RV32I 算术 ALU |
| ALU testbench | [`rtl/tb_alu.v`](./rtl/tb_alu.v) | Verilog | 14 条自检用例，`iverilog` 可跑 |
| Forwarding 单元 | [`rtl/forwarding_unit.v`](./rtl/forwarding_unit.v) | Verilog | EX/MEM→EX、MEM/WB→EX 转发 |
| 2-bit 预测器 | [`rtl/two_bit_predictor.v`](./rtl/two_bit_predictor.v) | Verilog | SN→WN→WT→ST FSM |

运行 ALU testbench：
```bash
cd Expert_03_HW_Designer
iverilog -o /tmp/tb_alu rtl/tb_alu.v rtl/alu.v && vvp /tmp/tb_alu
# 预期：=== ALU testbench: 14 pass, 0 fail === [ALL PASS]
```

---

## § RTL/SoC 设计方法论与资源（不只飞腾，给所有硬件设计工程师）

> 本章把 E03 的飞腾 RTL 分析上升为**任何硬件设计工程师都可复用的方法与资源**。飞腾是案例锚点（FTC862 自研核），方法普适。通用资源见 [`领域资源库.md`](../领域资源库.md)。

### 方法论一：SoC 集成决策（自研 vs 买 IP）

| 模块 | 自研 | 买 IP | 决策因素 |
|------|:----:|:----:|---------|
| CPU 核 | 飞腾自研 FTC862 | ARM Cortex/买 | 差异化核心→自研；通用→买（时间/成本）|
| GPU | 买（Imagination/ARM Mali）| ✅ | 买更经济，自研生态难 |
| DDR PHY | 买（Cadence/Synopsys）| ✅ | 高度标准化，买 IP 成熟 |
| PCIe/USB | 买（Synopsys/ARM）| ✅ | 标准接口，买 |
| 安全/密码 | 自研+国密 | 混合 | 国密差异化→自研部分 |
| AI 加速 | 买/合作 NPU IP | ✅ | 飞腾无自研，异构靠买（E21 §3.3）|

**原则**：差异化核心自研（护城河），标准化接口外购（速度+成本）。飞腾 FTC862 自研核是差异化押注，DDR/GPU/PHY 全外购。

### 方法论二：RTL 设计 → 验证 → 综合 闭环

1. **RTL 编写**（Verilog/SystemVerilog/Chisel）：模块化、可综合子集、参数化
2. **验证**（功能）：testbench、UVM、formal（JasperGold）、coverage（功能+代码）
3. **综合**（DC/Genus）：RTL→网表，看面积/时序/功耗
4. **门级仿真**：网表带 SDF 反标，验证综合后功能+时序
5. **物理实现**（E13 VLSI）：布局布线→签核→流片

**铁律**：仿真过 ≠ 硅能跑（E13）。但仿真不过 = 必死。

### 硬件设计专属资源

- **语言**：**Verilog/SystemVerilog**（业界）、**VHDL**（国防/欧洲）、**Chisel**（Scala，开源，RISC-V 用）、**Amaranth**
- **IP 库**：ARM Artisan、Synopsys DesignWare、Cadence、OpenCores、lowRISC
- **验证**：**UVM**（Universal Verification Methodology）、SVUnit、cocotb（Python）、formal（JasperGold/VC Formal）
- **die photo/对标**：**High-Yield/TechInsights**（反向解构）、Wikichip、ChipWorks、LoveRetro
- **书**：Harris & Harris《Digital Design and Computer Architecture》、West《Computer Architecture Techniques》、Patterson《硬件/软件接口》

### 给硬件设计工程师的通用建议

1. **差异化自研，标准化外购**：CPU 核自研是护城河，DDR PHY/PCIe 外购省时。
2. **可综合子集纪律**：RTL 写不可综合结构（initial/延迟）= 综合灾难。
3. **验证占设计 60-70% 时间**：功能覆盖率 + 代码覆盖率 + formal，三管齐下。
4. **模块化 + 参数化**：方便复用/升级（飞腾 FTC 核跨代迭代的基础）。
5. **用 die photo 反推对手**：买颗 Apple/华为芯片，TechInsights 解构，学其 floorplan。
