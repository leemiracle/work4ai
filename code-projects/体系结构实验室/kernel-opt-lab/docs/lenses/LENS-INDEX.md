# Kernel-Lab 多视角分析框架（Lens Framework）

> **v0.10**：从"单一优化工程师视角"扩展为 **20 视角全方位审视**（5 技术 lens + 15 专家 lens）。
> 覆盖技术/芯片/市场/政策/规范/供应链/学术/法律/伦理/ESG/客户全维度。
> 用户诉求："尽可能全、大、新、好"——本框架是覆盖度的可视化。

---

## 一、技术维度 lens（项目自身可跑的工具）

来自 `analysis/lens-*.c`，每个独立编译运行，输出 markdown：

| Lens | 视角 | 文件 | 关键产出 |
|---|---|---|---|
| **Roofline** | compute vs memory bound | `analysis/lens-roofline.c` | D3000 各级带宽（L1=79/L2=70/L3=28/DRAM=28 GB/s）+ 各算子 AI |
| **PMU** | 微架构计数器 | `analysis/lens-pmu.c` | IPC（GEMM 2.83、Stream 0.96）/ cache 命中 / branch 准确 |
| **Thermal** | 热设计 + DVFS | `analysis/lens-thermal.c` | 20 秒持续负载温度曲线 + 频率降速检测 |
| **Precision** | 数值稳定性 | `analysis/lens-precision.c` | FP16/INT8 在不同输入分布下的误差分布 |
| **Latency** | 长尾延迟 | `analysis/lens-latency.c` | p50/p90/p99/max 分布 + 实时性评估 |

跑法：`make analyze` 一键全套，输出到 `results/lenses/`。

---

## 二、专家角色 lens（20 个资深专家视角）

来自 councillor delegate + 作者亲撰的深度审查，覆盖 5 大域：

### 🔧 技术域（10 个）
| 编号 | 角色 | 报告 | 关键发现 |
|---|---|---|---|
| **01** | 性能架构师 | [`01`](01-performance-architect.md) | 零 prefetch / 宏参数未探索 / 多核 57% 误诊 / posix_memalign 实测无提升（附录）|
| **02** | 算法科学家 | [`02`](02-algorithm-scientist.md) | BF16 全缺席 / FP16 在 FP16 累加是**算法错误** / 距离 Llama-7B 还差 90% |
| **03** | OS/运行时 | [`03`](03-os-runtime-expert.md) | 8 核 57% 误诊（真因 MC×NC 分块缺失）/ OMP_PROC_BIND 实测反直觉 |
| **04** | 编译器专家 | [`04`](04-compiler-expert.md) | PhyGCC/clang/gcc 零横评 / `-ffast-math` 未测 |
| **05** | 硬件设计 | [`05`](05-hardware-engineer.md) | 4 FVU 是 4 独立 vs 2×256? / Spec store bypass Vulnerable |
| **06** | 教育者 | [`06`](06-developer-advocate.md) | 缺 TUTORIAL+VISUAL+COMMON-PITFALLS 三件套 |
| **07** | DevOps/SRE | [`07`](07-sre.md) | CI 跑 Graviton 不是 D3000 / 静默性能退化是最难抓 bug |
| **08** | QA | [`08`](08-qa.md) | 覆盖率 0.006% / 零 property testing / attention ⚠️ CI 漏洞（已修）|
| **09** | 安全 | [`09`](09-security.md) | malloc 零 NULL check / tail 静默错误（已修）/ NaN 链路 |
| **10** | 应用集成 | [`10`](10-integration.md) | 全仓 0 个 .h、38 static kernel（已加 include/kernel_lab.h）|

### 🔬 芯片/供应链/学术（3 个）
| 编号 | 角色 | 报告 | 关键发现 |
|---|---|---|---|
| **12** | 芯片设计深度 | [`12`](12-silicon.md) | 4 FVU 实为"4×128 + lane-broadcast port=4"（regfile 物理取舍）/ 代码 4FVU/dual FVU/single FVU 三个矛盾数字 / 软件侧优化已榨干 |
| **16** | 供应链/制造 | [`16`](16-supply-chain.md) | FTC862 TSMC 7nm 已停产 / ARM ISA 不可升级 v9 / PhyGCC GPL 雷 / 本项目最大资产是"软件库存" |
| **17** | 学术/未来 | [`17`](17-academic.md) | 2:4 sparse/FP8/MoE MLA 全零 / 距 ISCA 论文差 Novelty+对比基线+科学问题 |

### 📊 商业/客户（2 个）
| 编号 | 角色 | 报告 | 关键发现 |
|---|---|---|---|
| **13** | 市场/产品 | [`13`](13-market.md) | **市场定位错位**：8 核+双通道 DDR4 不是服务器，应 reframe 为"国产边缘/信创算力 SoC"（已改 README）|
| **15** | 政企客户 CIO | [`15`](15-customer.md) | 答了"跑多快"但没答 CIO 真正问的"能否替代 Intel/多少钱/出事谁管" |

### 🏛️ 政策/规范（2 个）
| 编号 | 角色 | 报告 | 关键发现 |
|---|---|---|---|
| **11** | 科技政策 | [`11`](11-policy.md) | 自主可控二级 / 飞腾 entity list / 4 FVU 是稀缺软件层实证（已加 AUTONOMY-STATEMENT）|
| **14** | 规范/标准 | [`14`](14-standards.md) | 国密 SM3/SM4 零实现是信创一票否决 / MISRA Rule 21.3 全仓违反 |

### ⚖️ 法律/伦理/ESG（3 个合集）
| 编号 | 角色 | 报告 | 关键发现 |
|---|---|---|---|
| **18-20** | 法律/伦理/ESG | [`18-20`](18-20-cross-cutting.md) | 缺 LICENSE 是法律红线 / 算力主权叙事需诚实承认政治性 / Jevons Paradox 高估节能贡献 |

**视角总计**：20 个完整报告（5 技术 + 15 专家），覆盖**技术 + 芯片 + 市场 + 政策 + 规范 + 供应链 + 学术 + 法律 + 伦理 + ESG + 客户**全维度。

---

## 三、核心交叉发现（多视角共识）

### 3.1 跨视角重叠结论（高置信度）

- **BF16 缺失**（算法/学术/政策三方共识——可能是 IP 授权拿不到，非工程遗漏）
- **SDK 化缺失**（应用集成/DevOps/客户三方共识）
- **双用途/出口管制风险**（法律/伦理/政策三方共识）
- **市场定位错位**（市场/客户共识——应 reframe 为"国产边缘/信创算力 SoC"）

### 3.2 反共识洞察

不同视角独立得出的**反直觉发现**：
- OMP_PROC_BIND=close 在 D3000 上反而慢（OS 视角实测）
- posix_memalign 对 NEON 无提升（架构师视角实测）
- "98% 峰值"是 K=1024 假象（架构师 + 算法 + 市场三方共识）

### 3.3 单视角盲区 = 多视角核心价值

| 维度 | 单视角答案 | 多视角补充 |
|---|---|---|
| "性能 98% 峰值够吗？" | 性能架构师："不够" | 市场分析："对客户够，因客户跑中等尺寸" |
| "该用 FP16 还是 BF16？" | 算法："必须 BF16" | 供应链："BF16 是 ARMv8.6+，飞腾 IP 授权可能拿不到" |
| "应该开源吗？" | 应用集成："开源才能生态化" | 法律/伦理："GPL + 双用途审查才能开源" |
| "4 FVU 是优势吗？" | 硬件："是，比 A78 多 2×" | 学术："理论先进但实际跑不出 2× 因访存瓶颈" |
| "项目能商业化吗？" | DevOps："缺容器/release" | 政企 CIO："缺 POC 验收清单和 ROI 模型" |
| "飞腾 D3000 是国产替代吗？" | 硬件："4 FVU 自研" | 政策："自主可控二级，三大硬受制点（ISA/流片/EDA）" |

---

## 四、改造优先级（按跨视角共识）

### 🔥 P0（v0.11 必做）

1. **LICENSE + AUTONOMY-STATEMENT + ETHICS-STATEMENT** 三件套（法律/政策/伦理共识）
2. **README reframe 为"国产边缘/信创算力 SoC"**（市场/客户共识，已完成）
3. **国密 SM3/SM4 NEON 实现**（规范 P0，信创一票否决）
4. **BF16 + causal + KV-cache + GQA attention**（算法/学术共识）
5. **MISRA Rule 21.3 清零**（规范/安全共识）
6. **PyTorch Custom Op binding**（应用集成/DevOps/客户三方）

### 🎯 P1

7. **2:4 sparse GEMM**（学术 P0，论文卖点）
8. **Flash-Decoding**（学术 P0，修复 N=128 倒挂）
9. **MLPerf 跑分**（规范/市场共识，国际对标）
10. **TCO 模型 + POC 清单**（客户 P0）
11. **供应链风险文档 + 二供预案**（供应链 P0）
12. **SVE2/SME 探测 + 迁移研究**（学术/编译器共识）

---

## 五、方法论价值（最重要的资产）

这个 lens 框架本身是项目最大的资产——**专家会走，方法论留下**。把任意新算子（BF16、W4A16、RoPE、SM3）扔进这个框架，立刻能得到 20 个视角的诊断。

**这才是"可复用的核心"**，而非某个特定算子。

### 跑全套视角

```bash
# 技术 lens（可执行）
make lens && make analyze        # 5 个技术 lens 报告 → results/lenses/

# 专家 lens（councillor 审查报告）
ls docs/lenses/                  # 20 份 markdown 审查报告

# 跨视角综合分析
cat docs/lenses/LENS-INDEX.md    # 本文档（总览 + 交叉发现）
cat docs/lenses/LENS-COVERAGE-MATRIX.md  # 覆盖矩阵
```

