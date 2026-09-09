# csdiy.wiki 深度展开索引（v0.14）

> **v0.14 新增**：把 csdiy.wiki 全 80+ 门课程/工具**逐门深度展开**（编号+讲师+难度+学时+官网+视频+GitHub+教材+作业+项目相关度）。
> 与 v0.11/v0.12/v0.13 的区别：
> - v0.11 = 5 阶段精读路径（13 门核心 + 11 论文）
> - v0.12 = 80+ 门完整索引（5 档相关度速查表）
> - v0.13 = 路线图隐藏课程 + ML 教材
> - **v0.14 = 每门课 200+ 字详情**（本目录）

## 目录结构

```
docs/CSDIY-DEEP-DIVE/
├── 00-INDEX.md                          # 本文件（总索引）
├── 01-tools.md                          # 必学工具 13 项（Git/Make/Docker/Vim...）
├── 02-math.md                           # 数学基础+进阶 9 门（18.06/18.330/EE364A...）
├── 03-programming-languages.md          # 编程语言 17 门（C/C++/Rust/OCaml...）
├── 04-systems-architecture-os.md        # 系统+体系+OS 10 门（CSAPP/CS61C/ETHz CA/6.S081...）
├── 05-parallel-compilers-distributed.md # 并行+编译+分布式 8 门（CS149/MLC/CS143/6.824...）
├── 06-database-network-security.md      # 数据库+网络+安全+软分 17 门（15-445/6.858...）
├── 07-ai-ml-dl-llm.md                   # AI/ML/DL/LLM 25+ 门（Karpathy/CS231n/CMU 11-868...）
├── 08-graphics-web-data-science.md      # 图形+Web+数据科学 11 门
├── 09-algorithms.md                     # 数据结构与算法 5 门
└── 10-mapping-to-kernel-lab.md         # 项目 lens × 课程 精确映射矩阵
```

## 状态

✅ = 已完成

| 文件 | 状态 | 课程数 |
|---|---|---|
| 01-tools.md | ✅ | 13 |
| 02-math.md | ✅ | 9 |
| 03-programming-languages.md | ✅ | 17 |
| 04-systems-architecture-os.md | ✅ | 10 |
| 05-parallel-compilers-distributed.md | ✅ | 8 |
| 06-database-network-security.md | ✅ | 19 |
| 07-ai-ml-dl-llm.md | ✅ | 25+ |
| 08-graphics-web-data-science.md | ✅ | 11 |
| 09-algorithms.md | ✅ | 5 |
| 10-mapping-to-kernel-lab.md | ✅ | 20 lens × 课程矩阵 |

**总计：117+ 门课程 + 13 项工具 + 20 lens 映射 = 完整教学体系**

## 每门课的标准格式

```
### [课程编号] [课程名]
- **大学/讲师**：
- **难度**：🌟 ~ 🌟🌟🌟🌟🌟
- **学时**：
- **课程官网**：[URL](URL)
- **视频 URL**：YouTube / Bilibili
- **GitHub 仓库**：
- **教材**：
- **作业/Project**：
- **一句话说明**：
- **对飞腾 D3000 NEON 算子优化项目的相关度**：核心 ⭐⭐⭐ / 中等 ⭐⭐ / 弱 ⭐
  - 具体对应：项目 lens XX / 算法 YY / 实验 ZZ
```
