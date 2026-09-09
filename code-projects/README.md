# code-projects · code 领域自研项目区

> **2026-09-09 建立**：把 C:\workspace 六个外部项目收编入 work4ai 的 code 领域集中区——不保留原文件夹，按内容整理；与仓库重合的内容去重后落指针，互不重复。
> 收编依据：六路只读重叠分析（与 讲透模型/讲透数学/讲透社会学/top-cs-projects 等既有内容逐项比对）+《本地仓库全景-Cworkspace迭代索引》既有策展结论。

## 收录三档原则

| 档 | 判据 | 项目 |
|---|---|---|
| **全量** | 仓库无等价物，互补不重复 | 政治学研修（讲透政治学只是 GB/T 目录骨架）、体系结构实验室（仓库唯一真机算子/Verilog 实验链）、tech-insight（仓库唯一自动采集分析管线） |
| **选粹** | 与既有系列真实重合，弃收部分全部落指针表 | 世界模型与AI4Sci调研（保留 29.8%，其余→讲透模型/讲透数学/讲透Agent 等等价物）、社会规律计算实验室（弃收 10 个与数理社会学/博弈论重复的 py，保留不等价四领域+CSSCI 论文库） |
| **蒸馏** | 源头大而信息密度低，只留提取物 | GitHub热门仓分析（453 仓克隆 177 万文件不入库，只留 2 份单文件分析+1 份去重索引） |

## 六项目一览

| 目录 | 来源 | 一句话定位 | 收录形态 | 入口 |
|---|---|---|---|---|
| [政治学研修/](./政治学研修/) | political-studies | 三大圆环/七模块/三阶段的政治学系统研修，62 万字+10 个可跑 py | 全量 233 文件，修复源内 206 条断链 | [入库说明.md](./政治学研修/入库说明.md) |
| [体系结构实验室/](./体系结构实验室/) | 体系结构（kernel-opt-lab+体系结构实验） | 飞腾 D3000 真机从 PMU 观测到 NEON 算子优化 + DDCA Verilog/Capstone RV32I/Nand2Tetris | 双库选收（剔除 ~170MB 工具运行时与外部资源堆） | [README.md](./体系结构实验室/README.md) |
| [tech-insight/](./tech-insight/) | tech-insight | 14 源采集→SQLite+向量→LLM 分析的技术媒体洞察平台（无 key 降级可跑） | 全量 83 文件 | [README.md](./tech-insight/README.md)（含入库说明节） |
| [世界模型与AI4Sci调研/](./世界模型与AI4Sci调研/) | world-ai4sci-math | 133 万字世界模型×AI4Sci×AI4Math 调研卷选粹：研究课题+学习路径+跨领域对照独有 | 选粹 62 文件（29.8%），弃收对照表 15 行全验证 | [README.md](./世界模型与AI4Sci调研/README.md) |
| [社会规律计算实验室/](./社会规律计算实验室/) | social-laws | 五段式规律卡（历史→直觉→数学→Python→批判）的社会科学计算实验室，21 篇 CSSCI 双轨校准 | 选粹 113 文件（PDF 本地不入库），指针表 9 行 | [README.md](./社会规律计算实验室/README.md) |
| [GitHub热门仓分析/](./GitHub热门仓分析/) | trending-repos | 424 热门仓的一次性横断分析：FlashMLA 代码级深读+熵/中心性数学分析+227 条去重索引 | 蒸馏 4 文件 | [INDEX.md](./GitHub热门仓分析/INDEX.md) |

## 与仓库其他区的关系

- **top-cs-projects/（九校库）**：那边是外部课程实战（CS61C/CSAPP 等），本区是自研项目——体系结构实验室恰好补九校库无 18-447 级深度实验的缺。
- **讲透宇宙**：理论侧；本区项目 README 均落等价物指针表，重合内容不双收。
- **透视GitHub-LLM高星仓库全景.md**：LLM 名仓深读正典；本区 GitHub热门仓分析/INDEX 的 LLM 条目全部回链该文件，只补非 LLM 趋势仓广度。

## 收编后状态

六个源目录（C:\workspace\{political-studies, social-laws, tech-insight, trending-repos, world-ai4sci-math, 体系结构}）在验收提交后删除，副本即唯一存档；trending-repos 的 453 个公开仓克隆未搬运（可直接访问上游）。
