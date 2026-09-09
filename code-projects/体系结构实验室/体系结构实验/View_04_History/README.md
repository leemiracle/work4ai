# View_04_History — 历史演进视角

> **切入问题**：每个现代 CPU 的设计决策都不是凭空产生的——它们是 **40 年研究 + 失败 + 商业博弈**的沉淀。
> 不懂历史，就看不懂"为什么飞腾选 4-wide 而不是 8-wide"。

---

## 4 篇代际演进史

1. **[分支预测器代际演进](./branch_predictor_evolution.md)**（1981 → 2025）
   - 1-bit → 2-bit → Two-Level → gshare → Tournament → Perceptron → TAGE → 神经网络
   - 准确率从 85% 到 98%+
   - 每个现代 CPU（含飞腾）都用 TAGE-SC-L 变种

2. **[Cache 架构代际演进](./cache_architecture_history.md)**（1980s → 2025）
   - direct-mapped → set-assoc → victim cache → non-inclusive L3 → 3D V-Cache → CXL
   - 一致性协议 MSI → MESI → MOESI → directory
   - 飞腾 D3000M cache 在主流跟随位置

3. **[ISA 兴衰史](./isa_history.md)**（1960s → 2025）
   - Alpha/MIPS/SPARC/Itanium/PA-RISC 死亡时间表
   - x86-64 / ARMv8 / RISC-V / LoongArch 存活路线
   - 飞腾选 ARM 的历史必然 + 风险

4. **[流水线深度代际演进](./pipeline_history.md)**（1980s → 2025）
   - 5 级 → 7-9 级 → Pentium 4 失败（31 级）→ Apple M1 反向（10 级 8-wide）
   - 飞腾 D3000M 是主流平衡路线（15+ 级 4-wide 2.5 GHz）

---

## 跨历史的共同 pattern

### Pattern 1：技术领先 ≠ 商业成功
- Alpha 技术最强，死了
- x86 商业最强，活得久
- **教训**：飞腾必须兼顾技术 + 政策市场

### Pattern 2：每次"激进押注"都有失败案例
- Itanium（VLIW）失败
- Pentium 4（深流水线）失败
- **教训**：保守路线 = 主流路线 = 安全

### Pattern 3：生态是长寿关键
- ARM 靠移动生态爆发
- RISC-V 靠开源生态扩张
- LoongArch 靠政策生态维持
- **教训**：飞腾必须深耕国产软件生态（OS/数据库/中间件）

### Pattern 4：研究 → 产品 滞后 10-15 年
- Tomasulo 1967 → 商用 1980s
- TAGE 2006 → 商用 2015+
- 神经网络预测器 2020s 研究 → 2035+ 商用？
- **教训**：飞腾现在押注的研究方向，2035 才能见效

---

## 历史人物（致敬）

| 人物 | 贡献 |
|------|------|
| **Robert Tomasulo**（1967）| 乱序执行基础算法 |
| **John Hennessy** | MIPS + CAQA 教材 |
| **David Patterson** | RISC + CAQA + RISC-V |
| **Yale Patt** | Two-Level 分支预测 |
| **Andre Seznec** | TAGE 系列 |
| **Daniel Jiménez** | Perceptron 预测器 |
| **Joel Emer** | Intel 首席架构师 + 学术 |
| **Jim Keller** | Alpha → AMD → Apple → Tesla（传奇架构师）|

---

## 阅读建议

- **30 分钟**：读分支预测器代际演进（最有趣）
- **2 小时**：完整读 4 篇 + 主 [README](../README.md)
- **1 周**：每篇读完后看其引用的 1-2 篇经典论文

📌 **下一步**：去 [View_05_CrossArch](../View_05_CrossArch/) 看飞腾在现代 CPU 矩阵中的位置。
