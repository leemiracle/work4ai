# claw-code 🦀 Claude Code 净室重写 · 案例笔记

> 一句话定位：**2026-03-31 Claude Code 源码泄露（512K 行 TS 经 npm .map 暴露）后的净室重写——先用 Python 通宵镜像架构，再以 Rust 为正典；它同时是"harness 怎么造"的教材和"agent 自管仓库"的社会实验，最终自己声明为博物馆展品。**
>
> 上游：https://github.com/ultraworkers/claw-code （MIT，前身 instructkr/claw-code，泄露后 2 小时 50K star，GitHub 史上最快增速之一）
> 本地克隆：`~/ai/agent/awesome-agents/repos/claw-code`
> 笔记钉版 HEAD：`08106b0`（2026-08-16，docs: add hierarchical AGENTS.md knowledge base）
> 规模实测（2026-08-20）：**1690 commits（2026-03-31 → 2026-08-16）**；Rust 正典 **11 crates / 101 个 .rs / 115,957 行**（4 月初检查点仅 48,599 行，5 个月翻 2.4 倍）；Python 伴生工作区 68 个 .py；主要贡献者 YeonGyu-Kim(564)/Yeachan-Heo(535)/bellman(412)/Jobdori(117)——**头部提交者几乎全是"爪子"（agent 工作流）**

## 为什么值得深读

1. **官方 harness 的"泄漏解剖"唯一可引用实现**：泄密分析（Daniel Zhang 六支柱、Raschka 六杀手锏、12 层 harness 论）里的每个机制——agent 循环/系统提示动态边界/三级→五级权限/上下文压缩/会话持久化——这里都有可引用的 Rust 源码对照。
2. **治理工程密度极高**：PARITY.md 9-lane 并行合并（每条带 commit 哈希）+ mock parity harness（12 场景/21 个捕获请求）+ g002-g013 质量门验证地图 + `.omx/` 里 Ralph 循环的执行回执（ledger.jsonl/quality-gate JSON）——**agent 自管的证据链直接进了仓库**。
3. **"仓库即展品"的元实验**：PHILOSOPHY.md 明说代码是副产品，真正的产品课是 OmX+clawhip+OmO 协调系统；README 的 IMPORTANT 框直接把用户劝去 LazyCodex/Gajae-Code——一个 1690 commit 的项目主动降级为化石，这本身是 agent 时代仓库生命周期的新样本。
4. **三产品线的清晰分层**：全量 `claw`（55 工具）→ `claw-analog`（NDJSON 合同+默认只读的 CI 精简 agent）→ `claw-rag-service`（独立 RAG 进程）——"重 CLI/轻 agent/旁路服务"的切法值得照抄。
5. **与 openclaw/dsh 构成三极对照**：openclaw=插件宿主个人助手，dsh=官方插件化 harness，claw-code=净室重写+agent 自管——三种"harness 即产品"路线的分歧点全在同维度可比。

## 阅读顺序

| # | 笔记 | 回答的问题 |
|---|---|---|
| 1 | [01-泄露事件与净室重写](notes/01-泄露事件与净室重写.md) | 泄露怎么发生、净室重写怎么在一夜完成、后来为何变成博物馆 |
| 2 | [02-Rust正典harness解剖](notes/02-Rust正典harness解剖.md) | ConversationRuntime/SystemPromptBuilder/权限/压缩/会话/55 工具的 file:line 实证 |
| 3 | [03-治理系统与agent自管证据](notes/03-治理系统与agent自管证据.md) | PARITY 9-lane、mock parity harness、g002-g013 质量门、.omx 回执、防 slop 治理 |
| 4 | [04-Python镜像层与三产品线](notes/04-Python镜像层与三产品线.md) | 镜像优先的移植方法学 + claw-analog NDJSON + claw-rag-service |
| 5 | [05-批判与可借鉴](notes/05-批判与可借鉴.md) | 缺点清单、与 openclaw/dsh 对比、对 work4ai 的按件拆借 |

## 审计总命令

```bash
cd ~/ai/agent/awesome-agents/repos/claw-code
git log -1 --format=%h                      # 笔记钉版 08106b0（漂移则行号需重验）
git log --oneline | wc -l                   # 1690
find rust -name '*.rs' -not -path '*/target/*' -print0 | xargs -0 cat | wc -l   # 115957
grep -n 'name: "' rust/crates/tools/src/lib.rs | sed -n '1,55p'                 # 55 工具表
cat PARITY.md .omx/ultragoal/ledger.jsonl | head -40                            # 治理回执
```

## 项目内交叉引用

- **本体源码深读**（主卡）：[ClaudeCode源码深读](../ClaudeCode源码深读/README.md)——泄露的 512K 行 TS 原版逐模块 file:line 解剖；本卡（净室重写仓）与其逐机制对照（散见各 notes）
- 同维度对照案例：[openclaw](../openclaw/README.md)（插件宿主路线，386,825★）· [deepseek-harness插件化框架](../deepseek-harness插件化框架/README.md)（官方插件化路线，219 插件包）
- harness 理论底座：[harness工程手册](../../../工程化手册库/harness工程手册/README.md)（六组件模型——本卡 02 篇逐件对表）
- 生态观测锚点：[透视GitHub-Harness高星仓库全景.md](../../../透视GitHub-Harness高星仓库全景.md)
- Claude Code 本体侧解读见本卡 01 篇"解读文献地图"（新智元/Daniel Zhang/掘金/WaveSpeed 等 7 篇，2026-03-31~04-02）
