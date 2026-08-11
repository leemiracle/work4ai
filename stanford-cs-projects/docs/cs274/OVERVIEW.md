# CS274: Computational Molecular Biology

> Stanford University, Autumn 2026
> 领域: 生物信息学 / 算法
> Prerequisites: CS161（算法）或同等经验
> Units: 3-4
> Difficulty: ⭐⭐⭐

---

## 📚 定位

用算法与计算方法解决分子生物学问题——DNA 序列比对、基因组组装、蛋白质分析。

---

## 🎯 学习目标

- 理解中心法则（DNA→RNA→蛋白质）的计算映射
- 掌握经典生物信息学算法（Needleman-Wunsch、Smith-Waterman）
- 能处理大规模基因组数据（FASTA / FASTQ 格式）
- 理解测序技术与组装算法的工程挑战

---

## 📅 核心模块

### Module 1: 序列分析基础
- DNA / RNA / 蛋白质序列表示
- GC 含量、密码子与开放阅读框（ORF）
- 序列统计与特征检测

### Module 2: 序列比对
- 编辑距离（Levenshtein Distance）
- 全局比对：Needleman-Wunsch 动态规划
- 局部比对：Smith-Waterman 算法
- BLAST 快速相似性搜索

### Module 3: 基因组组装
- 测序技术（Sanger → Illumina → Nanopore）
- De Bruijn 图与短读组装
- 重叠-布局-共识（OLC）方法

### Module 4: 系统发育
- 进化树构建（UPGMA、Neighbor-Joining）
- 最大似然法
- 分子钟假说

### Module 5: RNA 与调控
- RNA 二级结构预测（Nussinov 算法）
- 转录因子结合位点
- 基因表达调控

---

## 💻 项目代码

📁 `supplementary/undergrad_projects.py::cs274_demo`

**实现内容**:
1. ✅ 随机生成 100bp DNA 序列
2. ✅ GC 含量计算
3. ✅ ORF 检测（寻找起始密码子 ATG）
4. ✅ 编辑距离算法（动态规划序列比对）

**运行**:
```bash
cd supplementary
python3 undergrad_projects.py
```

**输出示例**:
```
序列长度: 100, GC 含量: 52.0%
起始密码子 (ATG) 位置: [5, 33, 61]
编辑距离 'ACGTACGT' vs 'ACGTTACG': 2
```

---

## 📊 关键概念/论文

| 概念 | 说明 |
|------|------|
| **Needleman-Wunsch** | 全局序列比对 DP 算法 (1970) |
| **Smith-Waterman** | 局部序列比对 (1981) |
| **BLAST** | 快速局部比对工具 |
| **De Bruijn 图** | 基因组组装核心数据结构 |

### 关键论文
1. Needleman & Wunsch 1970 — 全局比对
2. Altschul et al. 1990 — BLAST
3. Li et al. 2008 — BWA 短读比对

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **CS 学生想做生物** | CS274 是最佳入口 |
| **生物学生学编程** | 理论 + 实践并重 |
| **算法爱好者** | DP 在生物中的优雅应用 |
| **医学基因组方向** | CS274 → CS173A → 研究 |

---

## 🚀 扩展方向

1. 学习 Biopython 库进行真实数据分析
2. 探索多序列比对（ClustalW / MUSCLE）
3. 阅读 *Bioinformatics Algorithms* (Compeau & Pevzner)
4. 参与 ROSALIND 在线刷题平台

---

**对应代码**: `supplementary/undergrad_projects.py::cs274_demo`
