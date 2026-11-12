# 01 | README.md——全仓门面与教程路线总览

## ① 角色定位

`README.md` 是本仓唯一的全局导览层文件，位于图谱九层之上（不属任何一层，但 tour step-01/step-12 的选线与收束都以其为事实入口）。职责有三：定义仓库身份（README.md:3-7 "The open-source playbook for turning AI agents into real-world products"）、以赞助商矩阵+分类表格给出 22 个教程的入口索引（README.md:313 起）、规定使用边界（非商业许可 README.md:685、教育用途免责 README.md:673-679）。它不是教程本体——每条线的正文在各自目录的 notebook/文档里。

## ② 内部结构

全文 700 行，六段式：
- **身份区**（README.md:1-18）：标题、tagline、SEO 关键词注释（README.md:11）、作者社交链接。
- **Tutorial Sponsors 矩阵**（README.md:24-207）：三行表格 10 家公司，每个 logo 链接到其贡献的教程目录——LangChain→`tutorials/LangGraph-agent`（README.md:38）、Redis→agent-memory-with-redis（README.md:55）、Contextual→agent-RAG-with-Contextual（README.md:72）、Tavily→agent-with-tavily-web-access（README.md:115）、JetBrains→kotlin-agent-with-koog（README.md:149）、Mem0（README.md:174）、RunPod→runpod-gpu-deploy（README.md:191）。注意 logo 走 `assets/repos_images/sponsors_logos/`（README.md:42）。
- **General Sponsors + 订阅区**（README.md:209-275）：CodeRabbit（README.md:223）与 newsletter 引流。
- **Introduction + 架构图**（README.md:295-309）：核心主张"每个教程独立目录、可运行 notebook"（README.md:297），配 `ai_architecture_diagram.svg`（README.md:305）。
- **Tutorials 分类表**（README.md:313-616）：按 12 个主题分表——Tool Integration（315）、Data Processing（332）、RAG（356）、Memory（373）、Deployment（404）、Multi-agent（435）、GPU Deployment（453）、Security（470）、Agent Frameworks（512）、Model Customization（550）、Tracing（567）、Evaluation（584）、UI（601）。带 NEW 徽章的行是近期新增（如 Arcade README.md:324、Koog README.md:542）。
- **Getting Started + 法律区**（README.md:620-699）：clone→进目录→装依赖→跑 notebook 四步（README.md:636-659）。

## ③ 外部连接

README 是纯出度文件：以相对链接指向 `tutorials/` 下 22 个目录与 `assets/` 图片仓，反向无人 import 它。图谱中五份教程 README（agent-security-apex、ai-memory-with-cognee、kotlin-agent-with-koog、runpod crew 教程）是它索引对象的深覆盖子集；每份教程 README 首行的 views-tracker 像素（如 security README.md:1）与根 README.md:695 同源，是作者的全仓浏览统计设施。CONTRIBUTING.md（README.md:669 引用）定义新教程入选规范，与 LICENSE 共同构成治理层。

## ④ 数据流

输入：无（静态门面）。输出两类读者流量——(1) 浏览型：分类表描述→点 GitHub-View 徽章→进教程目录读各自 README/notebook；(2) 运行型：Quick Setup（README.md:634-639）clone 全仓→`cd tutorials/<目标线>`→装该目录 requirements→跑 notebook。赞助商教程的 logo 点击直达教程（README.md:38 等以相对路径保证仓内可达），普通教程多给绝对 GitHub URL（如 README.md:385）。

## ⑤ 设计决策与陷阱

- **决策：赞助内容与教程正文同体**。10 家公司各买一个教程位，README.md:26-28 明示"Click a logo to open the tutorial"——教程集的商业模式直接写进门面，学习时应意识到部分教程是厂商视角。
- **陷阱 1：Quick Setup 引用不存在的目录**。README.md:646-647 示例 `cd tutorials/agentic-applications-by-xpander.ai` + `pip install -r meeting-recorder-agent/requirements.txt`——`tutorials/` 下 22 个目录中并无此目录（ls 实证），是教程下架/改名后的遗留片段，照抄必失败。
- **陷阱 2：A2A 小节整段重复**。"Multi-agent Coordination" 表格在 README.md:435-451 与 README.md:494-510 出现两次，内容逐字相同——目录若自动汇总会产生 23 个教程的假象。
- **陷阱 3：README.md:264 HTML 畸形**。订阅区表格 `🎯<br/><b>Top 0.1%<b>Content</b>` 内层 `<b>` 未闭合，属排版瑕疵。
- **决策：不设统一依赖**。根 README 从不给出全仓 requirements——每教程自带版本互斥的清单（cognee==0.3.3 vs crewai>=0.12），这是"每目录一 venv"组织的源头。

## ⑥ 新人提示

先读 README.md:296-297 的 Introduction 与架构图（README.md:305）建立 12 主题心智地图，再按兴趣从分类表跳线；图表注意 NEW 徽章代表新线、成熟度未必高。跑教程前务必确认目标目录真实存在（陷阱 1 的教训）；若要系统性学完，建议顺序：docker-intro→fastapi-agent→某条赞助商主线，最后 agent-security-apex 做攻防收尾。本仓 LICENSE 是自定义非商业许可（README.md:685），企业内复用代码前先读 LICENSE 原文。
