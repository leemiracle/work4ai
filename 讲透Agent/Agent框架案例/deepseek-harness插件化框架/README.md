# DeepSeek Harness（dsh）插件化 Agent 框架 · 案例笔记

> 一句话定位：**DeepSeek 官方开源的 agent harness——"一切皆插件"架构的工业级实现，219 个插件包，把 loop/日志/工具/沙箱/审批全部做成可替换的 Cordis 插件。**
>
> 上游：https://github.com/deepseek-ai/deepseek-harness （MIT）
> 本地克隆：`C:\workspace\deepseek-harness`（bash 路径 `/c/workspace/deepseek-harness`）
> 笔记钉版 HEAD：`47f943859b`（2026-08-13，developer preview v0.1.0-rc.5，**无兼容性承诺**）
>
> 本案例组织方式参照 [`Agent记忆系统案例/mem0开源记忆层`](../../Agent记忆系统案例/mem0开源记忆层/) 的分层笔记约定。

## 为什么值得深读

1. **接缝化（capability seam）设计**是"换一个 Provider = 换整个产品形态"的最完整公开实现——挂载 E2B 远程执行世界，Bash/PTY/LSP/文件工具零改动迁移。
2. **"Model-visible ⟺ logged"**：模型看到的与审计到的必须是同一份日志，有运行时断言强制——agent 无法两面派。
3. **信任平面**：沙箱 wrap-argv 契约、fail-closed 审批、DNS-rebinding 栅栏、供应链 SHA 锁定，全部 fail-loud。
4. 与 opencode / Claude Code / Codex 等同类对比，dsh 是唯一把 harness 本身做成插件系统的（见笔记 05）。

## 阅读顺序

| # | 笔记 | 回答的问题 |
|---|---|---|
| 1 | [00-overview/01-定位与全景](notes/00-overview/01-定位与全景.md) | 它是什么、多大、怎么跑起来、目录怎么读 |
| 2 | [01-core-runtime/01-agent与loop](notes/01-core-runtime/01-agent与loop.md) | Agent 生命周期、inbox、turn/step 状态机 |
| 3 | [01-core-runtime/02-session事件日志](notes/01-core-runtime/02-session事件日志.md) | append-only 日志如何成为唯一事实源 |
| 4 | [01-core-runtime/03-tools管线与系统提示](notes/01-core-runtime/03-tools管线与系统提示.md) | 七段工具管线、审批降级、prompt 组装 |
| 5 | [02-capability-seams/01-接缝模式与能力矩阵](notes/02-capability-seams/01-接缝模式与能力矩阵.md) | 三角色接缝模式、30+ 能力族全表 |
| 6 | [02-capability-seams/02-插件机制全景](notes/02-capability-seams/02-插件机制全景.md) | 插件本体：Plugin 形态、cordis.yml/!!js、Loader/HMR、effect 处置、scope、自修改、preset、skill/hook |
| 7 | [03-trust/01-信任平面与反欺骗](notes/03-trust/01-信任平面与反欺骗.md) | 沙箱/审批/网络栅栏/供应链，反欺骗的架构落地 |
| 8 | [04-assembly/01-启动装配与Web](notes/04-assembly/01-启动装配与Web.md) | profile/bundle 分层、Web 双半架构、Typert RPC |
| 9 | [04-assembly/02-SDK-ACP-Python](notes/04-assembly/02-SDK-ACP-Python.md) | JSON-RPC SDK、ACP、Python 单文件运行时 |
| 10 | [06-deepwiki/01-DeepWiki对照与增补](notes/06-deepwiki/01-DeepWiki对照与增补.md) | DeepWiki 10 章映射 + 增补事实（构建面/测试基建/UI/i18n/glossary） + 错误记录 |
| 11 | [07-ecosystem/01-dsh-plugin生态分析](notes/07-ecosystem/01-dsh-plugin生态分析.md) | dsh-plugin topic star>66 全部 59 仓库分类与六大赛道 |
| 12 | [05-lessons/01-设计决策与可借鉴](notes/05-lessons/01-设计决策与可借鉴.md) | 15 条可迁移决策、与同类对比、已知局限 |
| 13 | [08-graph-analysis/01-模块依赖图与工程全景](notes/08-graph-analysis/01-模块依赖图与工程全景.md) | graphify 工具链、219 包依赖分层规律、质量门禁闭环 |
| 14 | [09-codegraph-forensics/01-符号级代码图谱与枢纽分析](notes/09-codegraph-forensics/01-符号级代码图谱与枢纽分析.md) | codegraph.db 取证：35K 符号/226K 边、hub 全是类型契约、跨包引用流 |
| 15 | [09-codegraph-forensics/02-源码级机制取证](notes/09-codegraph-forensics/02-源码级机制取证.md) | 五机制 file:line 锚点：相位机/inbox/surface/五事件管线/stream seam/cordis 内核 |
| 16 | [09-codegraph-forensics/03-工程节奏与谱系定位](notes/09-codegraph-forensics/03-工程节奏与谱系定位.md) | 65 天 12289 commit、1372 Agent Notes、vs LangChain/Mastra/opencode |

## 审计总命令

```bash
$ cd /c/workspace/deepseek-harness
$ ls -d packages/*/*/ | wc -l          # 219 个插件包
$ git log -1 --format=%h               # 笔记钉版 47f943859b（若漂移，行号需重验）
$ cat AGENTS.md | head -5              # 项目自述：一切皆插件
$ sqlite3 .codegraph/codegraph.db "SELECT kind, COUNT(*) FROM edges GROUP BY kind;"   # 符号图边分布（09笔记）
```

## 项目内交叉引用

- 欺骗动力学视角（反欺骗四机制解剖）：[`欺骗动力学-AI纪实验包.md`](../../欺骗动力学-AI纪实验包.md) 实验 5
- Agent 记忆案例对照：[`Agent记忆系统案例/mem0开源记忆层`](../../Agent记忆系统案例/mem0开源记忆层/)
- 讲透Agent 实战篇已收录本案例：[`讲透Agent/README.md`](../../讲透Agent/README.md)
- 用例库（279 仓横向谱系）定位参考：[`用例库/README.md`](../../用例库/README.md) 之"透视Agent系统工程"行——dsh 不在 279 快照内（发布于快照后），作为官方旗舰特写补充
