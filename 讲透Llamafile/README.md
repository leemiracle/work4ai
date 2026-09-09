# 讲透 Llamafile

llamafile（Mozilla）——单文件 LLM 分发系统：Cosmopolitan Libc + APE 把模型权重、推理引擎、Web UI 打包成一个跨平台可执行文件。知识库基于源码 v0.10.x 与知识图谱（1994 节点/3051 边/14 层/15 步导览）构建。

## 资产目录

| 目录 | 内容 | 说明 |
|---|---|---|
| [deepwiki/](deepwiki/INDEX.md) | DeepWiki 56 页全量转 md | 官方 wiki 镜像：架构/构建/调试/测试/依赖 16 章 |
| [onboarding/](onboarding/ONBOARDING.md) | ONBOARDING.md（6000 字/8 节） | 新人导览：总览→14 层架构→核心模块→关键概念→学习路径→文件地图→复杂度热点→生态对比 |
| [explain/](explain/) | 5 篇精讲（各 ~2500 字/六节结构） | 见下表 |

## explain 精讲索引

| 文章 | 主题 |
|---|---|
| [llamafile-main.md](explain/llamafile-main.md) | main.cpp+args 参数系统：四模式分发、flag 过滤、combined 双线程编排 |
| [llamafile-chatbot.md](explain/llamafile-chatbot.md) | chatbot_* 系列：双后端抽象（Direct/API）、token 历史栈、bestline REPL |
| [llamafile-sgemm.md](explain/llamafile-sgemm.md) | sgemm/tinyblas/iqk 三件套：CPUID 运行时分发、单模板多 ISA、量化矩阵乘 |
| [llamafile-sandbox.md](explain/llamafile-sandbox.md) | sandbox.c：pledge/unveil 双沙箱、anet 只进不出、可治理性探针 |
| [llamafile-server.md](explain/llamafile-server.md) | server 集成：server.cpp 补丁三件事、BUILD.mk 六段式、Web UI 预构建管线 |

## 推荐阅读顺序

1. ONBOARDING.md 全文（30 分钟建立全景）
2. 按兴趣下钻 explain 五篇（互相独立）
3. deepwiki/ 作参考手册按需查询

上游源码：`~/ai/llamafile/`（含 .understand-anything/ 知识图谱）。
