# ISA 兴衰史（1970s → 2025）

> **首席科学家 + 标准政策专家视角**配套。
> 60 年来 30+ 商业 ISA 兴起、互相借鉴、最终衰亡或存活。

---

## 0. 时间线一图

```
1970s ──── IBM 360 (1964) → 370 → ESA/390 → z/Architecture
              ↓ 启发
1970s ──── DEC PDP-11 → VAX (CISC, 死)
              ↓ 简化
1980s ──── MIPS / SPARC / ARM (RISC 革命)
              ↓
1980s ──── Intel 8086 → x86 (CISC 商业最成功)
              ↓
1990s ──── Alpha / POWER / PA-RISC (RISC 服务器混战)
              ↓
2000s ──── Itanium (VLIW 失败) / x86-64 / ARM 嵌入式崛起
              ↓
2010s ──── ARMv8 (64-bit, 进服务器) / Apple ARM Mac
              ↓
2020s ──── RISC-V (开源) / ARMv9 / LoongArch (自研)
```

---

## 1. RISC 革命（1980s）

### 1.1 背景
- 1970s CISC（VAX / x86）指令复杂，单条做多事
- 但**实际代码 80% 是简单指令**（load/store/branch/add）
- 复杂指令难流水化

### 1.2 RISC 思想（Berkeley RISC / Stanford MIPS, 1981）
- 精简指令：每条 1 cycle、固定长度
- Load/Store 架构（只有它们访问内存）
- 大寄存器堆（32+ 寄存器）
- 软件复杂度上升（编译器优化补偿）

### 1.3 RISC 四大流派
1. **MIPS**（Stanford, Hennessy）—— 1985 商业化
2. **SPARC**（Berkeley, Patterson）—— Sun 公司
3. **ARM**（Acorn, 1985）—— 嵌入式起步
4. **PowerPC**（Apple/IBM/Motorola 联盟）—— Mac 用

---

## 2. ISA 死亡时间表

### 2.1 Alpha（1992-2022，活了 30 年）
- DEC 1992 推出，最早商用 64-bit
- 性能领先 Intel 1 代（21264 时代）
- **衰亡路径**：DEC → Compaq (1998) → Intel (2001 收购) → 2022 EOL
- **遗产**：双 cluster / Hybrid 预测器 / 大 PRF 思想被 AMD/Intel 继承

### 2.2 MIPS（1985-2017+，主流 30 年）
- SGI 工作站 / Sony Playstation 1 / 路由器（很多 MIPS-based）
- **衰亡路径**：被 ARM 嵌入式蚕食 → SGI 倒 → MIPS Technologies 卖 → ImTech → 2017 转 RISC-V
- **遗产**：经典 RISC 设计被 RISC-V 继承

### 2.3 SPARC（1987-2017）
- Sun 服务器 / 日本 K 计算机（SPARC64）
- **衰亡路径**：Sun 卖给 Oracle (2010) → Oracle SPARC 路线图终止 (2017)
- **遗产**：多线程研究基础

### 2.4 PowerPC / POWER（1991-至今但市场缩水）
- Apple Mac 用 10 年（1994-2005），后转 x86
- IBM 服务器仍在用（POWER10）
- 嵌入式（汽车 / 游戏）部分仍在
- **现状**：服务器市场份额 < 5%

### 2.5 Itanium / IA-64（2001-2021）
- Intel + HP 联合，VLIW 思想
- 性能不达预期，编译器复杂
- **死亡**：2021 停产。号称"Itanic"

### 2.6 PA-RISC / Motorola 68k
- 各自公司专有，2010 前后基本退场

---

## 3. 现存主流 ISA（2025）

### 3.1 x86-64（Intel + AMD，1969 → 至今，57 年）
- 商业最成功的 CISC（虽然内部 RISC 微架构）
- 服务器 / 桌面统治地位
- 但移动完全没份额

### 3.2 ARMv8/v9（1985 → 至今，40 年）
- **嵌入式 → 移动 → 服务器 → 桌面**全场景
- Apple Silicon (M1/M2/M3) 让 ARM 在桌面爆发
- AWS Graviton / Ampere / 鲲鹏 让 ARM 进服务器
- **飞腾 D3000M 是这一派**（ARMv8.4-A）

### 3.3 RISC-V（2010 → 至今，开源崛起）
- 完全开源，无授权费
- 嵌入式 / IoT 主流（平头哥 / SiFive）
- 高性能 / 服务器：生态薄弱，追赶中
- **预测**：2030 前后在嵌入式统治，服务器仍落后

### 3.4 LoongArch（2021 →，龙芯自研）
- 中国"完全自主"路线
- 政策市场（信创）支撑
- 但生态全靠自己建（vs ARM 借力全球）

---

## 4. ISA 长寿的秘密

### 长寿 ISA（>30 年）
- **x86 (1969-)**：商业 + 兼容性 + 软件生态
- **ARM (1985-)**：嵌入式红利 + 移动红利 + Apple 加持
- **IBM Z (1964-)**：金融业专用，60 年不换

### 短寿 ISA（<20 年）
- **Alpha**：被并购 + 工作站市场萎缩
- **Itanium**：技术不成熟 + 编译器坑
- **PA-RISC**：被 Itanium 替代

**关键因素**：
1. **软件生态**（最重要）—— Windows for x86 / Linux for ARM
2. **公司战略**—— DEC 卖 Alpha / Intel 推 Itanium
3. **技术开放性**—— ARM 授权模式 / RISC-V 开源
4. **历史机遇**—— 移动时代给 ARM、嵌入式给 RISC-V

---

## 5. 飞腾的 ISA 抉择（与历史教训）

飞腾选 ARMv8 的历史背景：
- ✅ ARM 生态红利（Linux + Android + 全栈工具链）
- ✅ 嵌入式 → 服务器全覆盖
- ⚠️ ARM v9 受制裁（2021 后不授权中国）
- ❌ 与 LoongArch "完全自主" 叙事不符

**历史教训**：
- **Alpha 案例**：技术领先不如商业成功
- **Itanium 案例**：技术激进不如兼容稳定
- **ARM 案例**：选对时机（移动爆发前）+ 生态建设
- **RISC-V 案例**：开源降低入门门槛，但生态仍要建

飞腾的**最大风险**：ARM v9 不授权 + 鲲鹏竞争 + RISC-V 崛起。
**最大机会**：信创政策红利 + 与国产 OS/数据库协同。

---

## 6. 参考文献

1. Patterson, "Requirements, Principles, and Challenges for ISA Design" (2008)
2. *Computer Architecture: A Quantitative Approach* Appendix A
3. Richard, *The Alpha 21264 Microprocessor* (1999) — Alpha 经典
4. *Chip War* (Chris Miller 2022) — 半导体地缘
5. RISC-V International Specifications
6. 中国信通院《信创产业发展白皮书》

📌 **下一步**：[pipeline_history.md](./pipeline_history.md) 看流水线深度代际演进。
