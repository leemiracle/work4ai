# csdiy.wiki 资源下载汇总 (全部完成)

来源: https://csdiy.wiki/ (CS自学指南 / cs-self-learning by PKUFlyingPig)
完成时间: 2026-07-04
主仓库最新提交: 2026-02-24 (已是最新)

## ✅ 全部完成

| 类别 | 数量 | 状态 |
|------|------|------|
| 主仓库 cs-self-learning | 1 | ✅ |
| GitHub 仓库 | **103** | ✅ (含 REKCARC 4.83GB) |
| 书籍 PDF | 3 | ✅ |
| PBR 官方书 (第4版在线+第3版源码) | 334 页 | ✅ |
| RTR 资源说明 | 1 | ✅ |
| 网站镜像 | 270 页 | ✅ |

## 目录结构

```
csdiy/
├── cs-self-learning/              # 主仓库 (MkDocs 源码 + 40+ 课程 Markdown)
├── website/                       # 全站离线镜像 (270 页, 中英双语)
├── books/
│   ├── *.pdf                      # 3 本直链 PDF
│   ├── pbr-official/              # PBR 官方书 (第4版在线 327页 + 第3版源码)
│   └── rtr-official/README.md     # RTR 替代方案说明
└── github-repos/                  # GitHub 资源 (103 仓库)
    ├── PKUFlyingPig/  (33)        # 作者课程仓库, 全部完成
    ├── third-party/   (48)        # 第三方课程作业/解答
    ├── references/    (18)        # 参考资料 + REKCARC 4.83GB
    ├── ddia/ craftinginterpreters_zh/ deeplearningbook-chinese/
```

## GitHub 仓库明细 (103)

### PKUFlyingPig/* (33, 全部完成)
作者为每门课维护的资源/作业实现仓库: CMU10-714, CS106L, CS110L,
CS144-Computer-Network, CS149-parallel-computing, CS169-Software-Engineering,
CS186, CS224n, CS229, CS61A, CS61B, CS61C-summer20,
Computer-Network-A-Top-Down-Approach, EE16A, EECS126, MIT18.330,
MIT6.031-software-construction, MIT6.1600, MIT6.5940_TinyML, MIT6.824,
MIT6.S081-2020fall, NandToTetris, Princeton-Algorithm, Self-learning-Computer-Science,
Standford_CVX101, Thesis-Template, UCB-CS161, UCB-CS168, UCB-CS170, UCB-CS70,
UCB-EE120, cs50_ai, rubber-docker

### 第三方课程仓库 (48)
含 InsideEmpire 系列, cmu-db/bustub, seed-labs, kaist-cp, xv6 系列,
MIT6.824-2021, CS143-Compilers-Stanford, GAMES103, nano-vllm 等

### 参考资料 (18, 含 REKCARC)
free-programming-books, build-your-own-x, project-based-learning, CS-Notes,
**REKCARC-TSC-UHT (清华CS课程资料 4.83GB, 10学期/14578文件)**, nanoGPT,
micrograd, mlc-ai/notebooks, How-To-Ask-Questions, the-art-of-command-line,
vim-galore-zh_cn, public-apis, DevOps-Guide, cs-video-courses, self-taught-CS,
Starter-Guide, Awesome-LLM, LLMSys-PaperList, books

### 顶层好书引用 (3)
ddia (DDIA中文版), craftinginterpreters_zh (Crafting Interpreters中文版),
deeplearningbook-chinese (深度学习中文版)

## REKCARC-TSC-UHT 详情 ✅
清华计算机系课程资料聚合, 4.83GB 完整下载, 解压后 10 个学期目录:
大一上/下/小学期, 大二上/下/小学期, 大三上/下/小学期, 大四上 (14578 文件)
经 gh-proxy.com 代理下载 (github.com 直连被屏蔽, 该代理 ~10MB/s)

## 仅 1 项不存在
- **CS144/minnow**: GitHub API 返回 404, 非公开仓库
  (Stanford CS144 实验代码经课程内部分发; csdiy.wiki CS144 页面资源已在
   github-repos/PKUFlyingPig/CS144-Computer-Network/ 中)

## 书籍说明
- 3 本直链 PDF: 计算机网络自顶向下 7e, 数据库系统架构, 概率机器人
- PBR: 原 quanfita.cn 链接失效, 已用官方免费源替代
  (pbr-book.org 第4版在线书 327 页 + 第3版源码)
- RTR: 无官方免费完整 PDF (版权), 已记录替代方案
- 受版权教材 (CSAPP/OSTEP 等) 原网站仅给豆瓣链接, 作者建议 libgen 查找

## 使用方式
- 离线浏览网站: 打开 `website/index.html`
- 本地构建文档: `cd cs-self-learning && pip install -r requirements.txt && mkdocs serve`
- 阅读 PBR 书: 打开 `books/pbr-official/pbr-book-online/index.html`
- 清华课程资料: `github-repos/references/REKCARC-TSC-UHT/`
