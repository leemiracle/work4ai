# CS173A: Computational Human Genomics

> Stanford University, Autumn 2026
> 领域: 人类基因组学 / 精准医疗
> Prerequisites: CS274 或同等生物信息学基础
> Units: 3-4
> Difficulty: ⭐⭐⭐⭐

---

## 📚 定位

聚焦人类基因组计算——从变异检测到全基因组关联分析（GWAS），理解精准医疗的数据基础。

---

## 🎯 学习目标

- 理解人类基因组结构与变异类型
- 掌握变异检测（Variant Calling）流程
- 能进行 GWAS 分析与统计推断
- 理解人群遗传学与进化信号

---

## 📅 核心模块

### Module 1: 人类基因组基础
- 基因组结构（常染色体 / 性染色体 / 线粒体）
- 变异类型：SNP / Indel / CNV / 结构变异
- 参考基因组（GRCh38）与基因组注释

### Module 2: 测序与变异检测
- 全基因组测序（WGS）vs 外显子组（WES）
- 比对（BWA）→ 变异检测（GATK）→ 注释（VEP）
- 变异质量控制（VQSR）

### Module 3: 群体遗传学
- 等位基因频率与哈代-温伯格平衡
- 连锁不平衡（LD）与单倍型块
- 选择信号检测（Fst、iHS）

### Module 4: GWAS 与统计遗传
- 全基因组关联分析（GWAS）
- 曼哈顿图与多重检验校正
- 多基因风险评分（PRS）
- 孟德尔随机化

### Module 5: 临床应用
- 罕见病基因诊断
- 药物基因组学
- 肿瘤基因组（体细胞突变）
- 伦理：基因隐私与遗传歧视

---

## 💻 项目代码

> CS173A 与 CS274 共享生物信息学基础设施。

📁 `supplementary/undergrad_projects.py::cs274_demo`

**相关实现**:
1. ✅ DNA 序列生成与 GC 含量分析
2. ✅ ORF 检测与编辑距离比对
3. ✅ 序列差异的动态规划计算

**运行**:
```bash
cd supplementary
python3 undergrad_projects.py   # 查看 cs274_demo
```

---

## 📊 关键概念/论文

| 概念 | 说明 |
|------|------|
| **GWAS** | 全基因组关联分析 |
| **PRS** | 多基因风险评分 |
| **LD** | 连锁不平衡 |
| **VCF** | 变异调用格式 |
| **GATK** | 基因组分析工具包 |

### 关键论文
1. **1000 Genomes Project** 2015 — 人群基因组多样性
2. **GTEx Consortium** 2020 — 组织特异性表达
3..PRICE Team — PRS 方法论

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **想做精准医疗** | CS173A → CS522 → 临床合作 |
| **统计遗传方向** | GWAS + PRS 是核心工具 |
| **CS274 进阶** | 从分子到人群 |
| **生物信息从业者** | GATK 流程必备 |

---

## 🚀 扩展方向

1. 使用 PLINK 进行真实 GWAS 分析
2. 探索 UK Biobank 公开数据
3. 学习 Hail（大规模基因组分析框架）
4. 阅读 *Human Molecular Genetics* (Strachan & Read)

---

**对应代码**: `supplementary/undergrad_projects.py::cs274_demo`（共享基础）
