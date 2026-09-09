# CS 必学工具箱（csdiy 必学工具 × 环境配置 × 好书）

> 对应 [csdiy·CS学习规划](https://csdiy.wiki/CS%E5%AD%A6%E4%B9%A0%E8%A7%84%E5%88%92/) 的「必学工具/环境配置/好书推荐」三节（页面版本 2026-02-21，检索校准 2026-09-09）。本仓库此前只有课程地图（[CS学习规划-课程地图.md](CS学习规划-课程地图.md)）没有工具层——本文档补上这一层：每项给**正典入口+速通路径**，能与仓库资源互链的都互链。
>
> 收录纪律：只收公开正典（官方文档/开源仓库/开放讲义）；csdiy 原页的翻墙条目不收录（公开仓库法律敏感），以「国内镜像与源加速」替代——后者是同一个问题的合规解法。

## 一、必学工具（csdiy 顺序）

### 1.1 学会提问

开源世界的元技能：先自己排查（周期太长的问题不值得问别人），实在卡住再把「处境+目的」写清楚。

- 正典：[提问的智慧](https://github.com/ryanhanwu/how-to-ask-questions-the-smart-way)（中文版）——提问前/时/后的完整礼仪
- 进阶：[XY Problem](http://xyproblem.info/)——你以为的问题不是你的问题
- 仓库呼应：调试方法论见 [讲透软件工程](../讲透计算机科学技术/讲透计算机软件/讲透软件工程/)（缺陷与根因分析支）

### 1.2 工具课一站式：MIT-Missing-Semester

[Missing Semester](https://missing.csail.mit.edu/)（[中文版](https://missing-semester-cn.github.io/)）覆盖下表绝大部分工具的正式教学：shell、vim、git、调试、性能分析、密码学基础……csdiy 建议学完一门导论课后再上它（会提到开发流程术语）。

### 1.3 命令行

「被低估的生产力倍增器」。

- 正典：[命令行的艺术](https://github.com/jlevy/the-art-of-command-line/blob/master/README-zh.md)（GitHub 十万 star，反复通读）
- Shell 脚本：[Shell 脚本教程](https://www.shellscript.sh/)（英文正典）
- 仓库呼应：九校库所有 `*.py` 都可纯命令行跑（`python xxx.py`），是命令行的天然练习场

### 1.4 编辑器与 IDE

| 场景 | 推荐 |
|---|---|
| 轻量日常 | VS Code（插件生态最简单）/ Sublime Text |
| 大型工程 | PyCharm（Python）/ IDEA（Java）/ CLion（C++） |
| 命令行 | Vim（见下） |

### 1.5 Vim / Emacs

- Vim：入门 `vimtutor`（装完 Vim 自带，30 分钟）；进阶在 Missing Semester 第 3 讲；现代 IDE 均有 Vim 插件（先学移动/编辑动词，不必一步登天）
- Emacs：与 Vim 齐名，扩展性更强（可配置成编辑器也可长成 IDE）；入门 [GNU Emacs Tour](https://www.gnu.org/software/emacs/tour/)
- 仓库呼应：本仓库脚本小而自包含，任何编辑器都够；编辑器之争的正确姿势是「先精通一个」

### 1.6 Git 与 GitHub

- Git 入门：[Pro Git 中文版](https://git-scm.com/book/zh/v2)（正典全书，免费）前 3 章
- 可视化练习：[Learn Git Branching](https://learngitbranching.js.org/?locale=zh_CN)（交互式闯关，最短路径）
- GitHub：仓库托管+开源社区；进阶（PR/Issue/Actions 工作流）在 [讲透软件开发环境](../讲透计算机科学技术/讲透计算机软件/讲透软件开发环境/)
- 仓库呼应：本仓库本身就是 git 管理的长期项目，`git log` 是最好的项目史教材（每条 commit message 都是结构化写作）

### 1.7 构建工具：GNU Make → CMake

- [跟我一起写 Makefile](https://seisman.github.io/how-to-write-makefile/)（中文正典）；Make 培养模块化习惯+编译链接直觉
- [CMake 官方教程](https://cmake.org/cmake/help/latest/guide/tutorial/index.html)（掌握 Make 之后再学）
- 仓库呼应：本仓库纯 Python（标准库零依赖），无构建步骤——这是刻意设计（学习脚本不配被构建系统劫持）；构建工具的真实战场在 C++ 项目

### 1.8 LaTeX

论文排版正典。

- 入门：[一份（不太）简短的 LaTeX 介绍](https://github.com/lshort/lshort-zh-cn)（lshort 中文版）
- 在线写：[Overleaf](https://www.overleaf.com/)（零配置起步）
- 仓库呼应：数学公式的 LaTeX 记法遍布 [讲透数学](../讲透数学/) 各家族（`$...$` 行内式），读仓库文档=免费 LaTeX 阅读训练

### 1.9 Docker

轻量级环境封装。

- [Docker 官方 Get Started](https://docs.docker.com/get-started/)；中文 [Docker — 从入门到实践](https://github.com/yeasy/docker_practice)
- 用途：把「在我机器上能跑」变成「在容器里能跑」；服务器端见 §二

### 1.10 其他

- 实用工具箱：csdiy 的 [工具箱页](https://csdiy.wiki/%E5%AE%9E%E7%94%A8%E5%B7%A5%E5%85%B7%E7%AE%B1/)（下载/设计/学习站合集）
- 论文 Word 写作：csdiy 原页 Thesis 条目（本仓库场景用 LaTeX，不收录）

## 二、环境配置

> csdiy 名言：你以为的开发=疯狂码代码；实际的开发=配环境配几天。

### 2.1 PC 端（Windows/macOS）

- **Windows**：[Scoop](https://scoop.sh/)——命令行包管理器，把 Windows 配出类 Unix 体验（本仓库开发机即 Windows+Scoop/Git Bash）
- **macOS**：csdiy 推荐的 [macOS 开发环境指南](https://github.com/donnemartin/dev-setup)
- 终端美化与软件源加速：Missing Semester 环境配置讲 + 各镜像站（见 2.3）

### 2.2 服务器端（Linux/运维）

- 入门讲义：[中科大 LUG《Linux 101》](https://101.lug.ustc.edu.cn/)（中文，在线免费）
- 系统课程：[Aspects of System Administration](https://www.cs.cornell.edu/courses/cs3141/)（csdiy 推荐运维课）
- 运维百科：[DevOps-Guide](https://github.com/Pradumnasaraf/DevOps-Guide)（Docker/K8s/Linux/CI-CD/GitHub Actions 速查）

### 2.3 国内镜像与源加速（合规替代方案）

csdiy 用翻墙解决的问题，大部分场景有镜像解法：

| 需求 | 镜像 |
|---|---|
| PyPI | `pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple`（清华源） |
| GitHub 克隆慢 | `https://ghproxy.com/https://github.com/...` 前缀代理；或 [gitcode 等镜像站](https://gitcode.com/) |
| HuggingFace 模型 | `HF_ENDPOINT=https://hf-mirror.com` |
| Anaconda | [清华 Anaconda 镜像](https://mirrors.tuna.tsinghua.edu.cn/help/anaconda/) |
| Ubuntu/Debian apt | `mirrors.tuna.tsinghua.edu.cn` 各发行版帮助页 |

> 本仓库纪律：纯标准库零第三方依赖——`git clone` 之后任何 Python 3.8+ 直接跑，环境配置问题被架构消灭（学习仓库的最优环境策略）。

## 三、好书推荐

csdiy 的[好书推荐页](https://csdiy.wiki/%E5%A5%BD%E4%B9%A6%E6%8E%A8%E8%8D%90/)按「以人为本」标准选书。本仓库已有深读锚：

| 书 | 仓库深读 |
|---|---|
| CSAPP《深入理解计算机系统》（15-213 配套） | [CSAPP_HARDWARE_TRUTHS.md](CSAPP_HARDWARE_TRUTHS.md)（8 个硬件真相+可运行 demo） |
| Agner Fog 优化手册五卷 | [AGNER_FOG_OPTIMIZATION.md](AGNER_FOG_OPTIMIZATION.md)（完全综合+demo） |
| 龙书《编译原理》 | [讲透编译系统](../讲透计算机科学技术/讲透计算机软件/讲透编译系统/) |
| 《算法导论》/Sedgewick 算法 | [algorithms/](../algorithms/) + [讲透算法理论](../讲透计算机科学技术/讲透计算机基础/讲透算法理论/) |
| 教材免费获取 | [top-math-courses/BIBLIOGRAPHY.md](../top-math-courses/BIBLIOGRAPHY.md)（9 校 75 门课约 90 本教材去重+免费合法来源标注） |

## 四、速通路径（把工具箱串成一周计划)

1. **Day 1**：提问的智慧通读（30 分钟）+ Learn Git Branching 前几关
2. **Day 2-3**：命令行的艺术通读 + 本仓库 `git clone` 后跑通任一家族实验（命令行+git 同时练）
3. **Day 4**：vimtutor 30 分钟 + 装 VS Code 配 Vim 插件
4. **Day 5**：Missing Semester 挑 shell/git/调试三讲精读
5. **Day 6-7**：按需——写论文走 LaTeX(lshort)，服务器走 Linux 101，容器走 Docker Get Started

> 工具是砍柴刀，不是柴：每周用一次以上的工具才值得学深，其余知道存在即可（Missing Semester 的立场，也是本仓库的立场）。

## 治理

- 本文档=工具层导航（正典入口+速通路径），不复制正典内容；深读归外部正典与仓库内讲透家族
- 检索校准 2026-09-09（csdiy 页面版本 2026-02-21）；镜像站可用性以各站现状为准
- 建档 2026-09-09；与 [CS学习规划-课程地图.md](CS学习规划-课程地图.md) 互为前后件（先工具后课程）
