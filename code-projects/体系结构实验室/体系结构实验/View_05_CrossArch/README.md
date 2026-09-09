# View_05_CrossArch — 飞腾 vs 全球 CPU 横向对比

> **切入问题**：飞腾 D3000M 在全球 CPU 矩阵里什么位置？
> 与 Apple / AMD / Intel / Ampere / 鲲鹏 / Graviton 比起来如何？
>
> **主导思维**：不孤立看飞腾——同一时代（2022-2024）的同期产品横向对比。

---

## 1. 总览对比表（2022-2024 同代 CPU）

| 厂商 | 型号 | 工艺 | ISA | 核数 | 频率 | IPC | 单核性能 | 多核性能 | TDP |
|------|------|----:|----|----:|-----:|----:|--------:|--------:|---:|
| **Phytium** | **D3000M (FTC862)** | 7nm* | ARMv8.4 | 8 | 2.5 GHz | ~2 | ~5 spec | ~40 spec | ~72W |
| Apple | M3 Max P-core | 3nm | ARMv8.6 | 12P+4E | 4.0 GHz | ~3.5 | ~20 spec | ~200 spec | ~22W |
| Ampere | Altra Max | 7nm | ARMv8.2 | 128 | 3.0 GHz | ~1.5 | ~6 spec | ~600 spec | ~250W |
| 华为 | 鲲鹏 920 | 7nm | ARMv8.2 | 64 | 2.6 GHz | ~2 | ~6 spec | ~400 spec | ~180W |
| AWS | Graviton 4 | 4nm | ARMv9.2 | 96 | 2.8 GHz | ~2.5 | ~8 spec | ~700 spec | ~70W/chip |
| Intel | Xeon 8480+ (Sapphire Rapids) | Intel 7 | x86-64 | 56 | 3.8 GHz | ~2 | ~12 spec | ~600 spec | ~350W |
| AMD | EPYC 9654 (Genoa) | 5nm | x86-64 | 96 | 2.4/3.7 GHz | ~2.5 | ~10 spec | ~900 spec | ~360W |
| 龙芯 | 3A6000 | 12/14nm* | LoongArch | 4 | 2.5 GHz | ~1.8 | ~5 spec | ~20 spec | ~50W |

\* 推测

**飞腾 D3000M 评级**：
- 单核：⭐⭐（主流跟随 80% 水平）
- 多核：⭐⭐（落后 Apple M3 Max / AMD Genoa 一代）
- 功耗：⭐⭐⭐（与同代 ARM 持平）
- 商业：⭐⭐⭐⭐（信创红利，但份额落后鲲鹏）

---

## 2. 单核 SPEC 性能（估算）

> 数据来自 SPECrate 2017 公开数据 + 推测。

| CPU | SPECint 2017 | SPECfp 2017 | 相对飞腾 |
|------|---------:|---------:|------:|
| Apple M3 P | ~14 | ~22 | **3.0×** |
| Intel 8480+ | ~12 | ~18 | **2.5×** |
| AMD 9654 | ~10 | ~16 | **2.2×** |
| Graviton 4 | ~8 | ~12 | 1.6× |
| 鲲鹏 920 | ~6 | ~9 | 1.2× |
| **飞腾 D3000M** | **~5** | **~7** | **1.0×** |
| 龙芯 3A6000 | ~5 | ~6 | 1.0× |
| Cortex-A78 | ~5 | ~7 | 1.0× |

**结论**：飞腾 D3000M 单核性能相当于 ARM Cortex-A78（2020）水平，
落后 Apple M3 / AMD Zen 4 约 50-200%。

---

## 3. 微架构对比

| 维度 | 飞腾 D3000M | Apple M3 P | AMD Zen 4 | Intel Golden Cove |
|------|-----------|-----------|----------|------------------|
| Issue Width | 4 | 8（推测） | 6 | 6 |
| 流水线深度 | 15+（推测） | 10（推测） | 19 | 14-16 |
| 重命名容量 | ~50 PR（实测） | ~350 PR | ~256 PR | ~512 PR |
| L1 I-Cache | 64KB/4-way | 192KB/8-way | 32KB/8-way | 32KB/8-way |
| L2 | 512KB | 16MB（共享）| 1MB | 1.25MB/2.5MB |
| L3 | 8MB shared | 16-64MB | 32-128MB | 105MB |
| SMT | ❌ | ❌ | ✅ SMT2 | ✅ SMT2 |
| 推测执行 | ✅ | ✅ | ✅ | ✅ |
| 安全缓解 | v8.5 SSBS | 完整 | 完整 | 完整 |
| 分支预测器 | TAGE-SC-L 变种 | TAGE 变种 | Perceptron+TAGE | TAGE |

**飞腾差距**：
- ❌ Issue Width 落后（4 vs 8）
- ❌ L2 偏小（512KB vs 1MB+）
- ❌ L3 偏小（8MB vs 32MB+）
- ❌ 无 SMT
- ❌ 无 BF16/I8MM（ML 加速）

---

## 4. 内存带宽对比

| 平台 | DRAM 类型 | 带宽 | 注释 |
|------|---------|----:|------|
| 飞腾 D3000M | DDR4-3200 ×4ch | 102 GB/s | 实测数据手册 |
| Apple M3 Max | LPDDR5-6400 | 400 GB/s | 大带宽 |
| AMD 9654 | DDR5-4800 ×12ch | 460 GB/s | 12 通道 |
| Intel 8480+ | DDR5-4800 ×8ch | 307 GB/s | |
| Graviton 4 | DDR5-5600 ×8ch | ~336 GB/s | |
| 鲲鹏 920 | DDR4-2933 ×8ch | 187 GB/s | 老一代 |

**飞腾劣势**：仍在 DDR4-3200，落后 DDR5 一代。
**建议**：D4000 必须升 DDR5-5600。

---

## 5. ML 推理性能对比

> Llama 7B Q4 推理 token/s（推测/公开数据）。

| 平台 | token/s | 备注 |
|------|--------:|----|
| **飞腾 D3000M 8 核** | **2-5** | 无 BF16/I8MM |
| Apple M3 Max | 20-30 | Neural Engine + GPU |
| Graviton 4 | 10-15 | 有 BF16 + SVE2 |
| Ampere Altra Max | 15-20 | 有 BF16 |
| Intel Xeon Max | 30-50 | HBM + AMX |
| NVIDIA A100 | 80-100 | Tensor Core |
| NVIDIA H100 | 200+ | Transformer Engine |

**飞腾 ML 推理**：⭐ 落后一代。下一代 D4000 必须加 BF16 + I8MM。

---

## 6. 商业 / 价格对比

| CPU | 单价（参考）| 毛利率 | 主要市场 |
|------|---------:|------:|---------|
| 飞腾 D3000M | $200-500（信创）| 60-80% | 政企 + 工业 |
| Apple M3 Max（整机）| 含在 Mac 里 | - | 桌面 |
| Intel Xeon 8480+ | $7,500-8,000 | 80% | 服务器 |
| AMD EPYC 9654 | $11,000+ | 75% | 服务器 |
| Ampere Altra Max | $2,500-3,500 | 60% | 云服务器 |
| Graviton 4 | 不卖（AWS 自用）| - | AWS EC2 |
| 鲲鹏 920 | 不卖（华为自用 + 信创）| - | 信创 |
| 龙芯 3A6000 | $100-200 | 50% | 信创 |

---

## 7. 5 年路线图对比（2024-2029）

### Intel
- 2024: Emerald Rapids
- 2025: Granite Rapids (Intel 3)
- 2026: Diamond Rapids (Intel 18A)
- 2027+: 14A 工艺

### AMD
- 2024: Zen 5 (4nm)
- 2025: Zen 6 (3nm)
- 2027: Zen 7 (2nm)
- 集成 NPU（Ryzen AI）

### ARM / Apple
- ARM v9.5+ (2024)
- Apple M4 / M5 (3nm GAA / 2nm)
- ARM Cortex-X5+ 持续提升

### 飞腾（推测）
- 2024-2025: D3000 系列（当前）
- 2026-2027: D4000（推测 6-wide + SVE2 + BF16 + DDR5）
- 2028+: D5000（推测 chiplet + HBM 选项）
- **风险**：受制裁影响，可能落后主线 2-3 年

---

## 8. 飞腾的差异化优势

虽然飞腾技术指标落后，但**有独特的市场护城河**：

1. ✅ **信创目录**：政企强制国产化
2. ✅ **国密合规**：SM2/SM3/SM4 硬件加速
3. ✅ **军工资质**：长期合作
4. ✅ **完整工具链**：PhyGCC + PhyTune + 数据手册
5. ✅ **国产 OS 适配**：统信 / 麒麟 / 欧拉

**对比 RISC-V 厂商**：飞腾有 ARM 生态（Linux/Android）
**对比 Intel/AMD**：飞腾有信创政策
**对比 Apple**：飞腾有服务器场景
**对比 华为鲲鹏**：飞腾份额小但关系更稳定（与华为无内部业务竞争）

---

## 9. 与其他视角对偶

- Expert_02 架构师：横向对比印证 PPA 决策
- Expert_06 标准政策：ISA 选择决定生态
- Expert_07 商业：市场份额与价格定位

---

## 10. 参考文献

- 各厂商官方数据手册
- SPEC CPU 2017 公开结果：[spec.org](https://spec.org)
- Wikichip / Anandtech / Chips and Cheese 深度评测
- 中国信通院国产 CPU 报告

📌 **下一步**：去 [Expert_03_HW_Designer](../Expert_03_HW_Designer/) 看硬件设计视角的具体代码。
