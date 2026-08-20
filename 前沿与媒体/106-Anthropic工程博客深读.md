# 前沿与媒体 · 106 - Anthropic 工程博客深读（harness/agent 工程 + 工具/安全线，11 篇）

> 105 的配套深读篇。本篇覆盖 harness/agent 工程主线 6 篇（§1-6）+ 工具设计/检索/安全线 5 篇（§7-11，含 2026 最新架构分水岭 Managed Agents），全部基于 2026-08-20 webfetch 全文一手提炼（非转述）。读者定位：harness 工程手册作者、x-kernel agent 设施建设者、MATS interp 申请者。
> 每卡：核心主张 / 机制 / 硬数字 / 可落地 / 局限。交叉锚点指向本仓既有深潜。

---

## 1. Building Effective Agents（2024-12-19，持续更新）

🔗 [原文](https://www.anthropic.com/engineering/building-effective-agents) ｜ ⚠️ **官方已加注**：工具图景已变，当前做法见 Managed Agents（本篇 §2 之 6）

- **核心主张**：最成功的实现用**简单可组合的模式**，不是复杂框架。
- **机制**：核心区分 **Workflows**（预定义代码路径编排 LLM）vs **Agents**（LLM 动态自主决定流程与工具使用，定义="LLMs autonomously using tools in a loop"）。积木=augmented LLM（检索+工具+记忆）。五模式：①Prompt chaining（逐步+中间门控）②Routing（分类分流，含 easy→Haiku/hard→Sonnet 成本路由）③Parallelization（sectioning 分片 / voting 投票）④Orchestrator-workers（中央 LLM 动态拆解分派，适合编码这类子任务不可预测的场景）⑤Evaluator-optimizer（生成-评审循环）。
- **硬数字**：无基准数字（方法论文章）。
- **可落地**：①只在简单方案不足时加复杂度（"find the simplest solution possible"）②框架要能看穿底层（错误假设是客户报错首因）③**ACI 工程纪律**：给工具的投入等同 HCI——SWE-bench 上他们花在优化工具的时间**多于**总 prompt；绝对路径替换相对路径后模型零失误（poka-yoke 防呆设计）④工具格式选模型在网上常见形态（diff 要预知行数、JSON 转义都是坑）。
- **局限**：2024-12 视角；五模式中的 workflow 部分正被 Managed Agents 取代。
- **锚点**：本仓 `harness工程手册/12-最小harness实现`（loop=心脏）；Topics 01 §4.7（loop 为何无 topic）。

## 2. Effective Context Engineering for AI Agents（2025-09-29）

🔗 [原文](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

- **核心主张**：上下文是**有限资源**，好工程=找到"最大化目标行为概率的最小高信号 token 集"。
- **机制**：①**context rot**（token 增→召回降，n² 注意力被摊薄+训练分布短序列偏置）②系统提示要"**right altitude**"——硬编码 if-else 脆 vs 泛泛而谈无效，中间带具体启发③工具是 agent 与信息空间的契约，臃肿工具集+模糊决策点=灾难（"人类工程师都说不清用哪个工具，就别指望 agent"）④**JIT 上下文**：持轻量标识符（路径/查询/链接）运行时按需加载——Claude Code 用 head/tail 分析大库从不全文进上下文⑤混合策略：CLAUDE.md 前置 + glob/grep 按需（绕开索引陈旧问题）。
- **三大长程技术**：**Compaction**（近限摘要重启；保架构决策/未解 bug/实现细节，弃冗余工具输出；最轻形式=tool-result clearing）｜**结构化笔记**（agentic memory：外部文件持久化，Pokémon agent 实例——数千步训练计数、地图、战斗策略）｜**子代理架构**（子代理耗数万 token 探索，只回 1-2K token 蒸馏摘要）。
- **可落地**：compaction prompt 先最大化 recall 再修 precision（在复杂 agent trace 上调）；文件系统元数据（目录层级/命名/时间戳）本身就是免费上下文信号。
- **局限**：承认运行时探索比预取慢；无正确工具引导时 agent 会烧 token 追死胡同。
- **锚点**：x-kernel `docs/ai/repo-map.md`（1-2K token 地图）正是"轻量标识符"策略；token 减量研究 C 报告的 6100→420 即子代理模式实例。

## 3. How We Built Our Multi-Agent Research System（2025-06-13）

🔗 [原文](https://www.anthropic.com/engineering/multi-agent-research-system)

- **核心主张**：多 agent=**并行扩展 token 消耗**的架构；研究类广度优先任务收益最大。
- **硬数字（全仓最密）**：Opus 4 主 + Sonnet 4 子比单 Opus 4 内部评测 **+90.2%**｜BrowseComp 上 **token 用量解释 80% 方差**（三因素共 95%）｜agent 比聊天耗 **4×** token，多 agent **15×**｜子代理工具描述经 tool-testing agent 重写后任务完成时间 **-40%**｜双层并行（lead 并行 spawn 3-5 子代理 + 子代理并行 3+ 工具）砍研究时间 **90%**。
- **机制**：orchestrator-worker；LeadResearcher 计划先写 Memory（防 200K 截断丢失）；CitationAgent 独立负责引用；8 条 prompting 原则（像 agent 一样思考/教 orchestrator 怎么委派——目标+输出格式+工具边界+任务边界/effort 随复杂度伸缩：简单 1 agent 3-10 调用 vs 复杂 10+ 子代理/先宽后窄/interleaved thinking 评工具结果质量）。
- **评测法**：立即用 ~20 条真实查询小样本起步（早期 prompt 改动 30%→80% 效应量大）；LLM-as-judge 单调用 0.0-1.0+pass/fail 最稳；人类测试抓内容农场偏好（SEO 站压过学术 PDF）。
- **生产**：有状态错误复利→checkpoint 恢复+告知 agent 工具故障让它自适应；rainbow deployment 防打断运行中 agent；监控决策模式不监控内容（隐私）。
- **可落地**：子代理产物**直写文件系统**只回引用（防"传话游戏"损耗）；对状态改变型任务用**终态评测**而非逐步骤评测。
- **局限**：同步执行瓶颈（lead 等子代理）；依赖多的任务（多数编码）不适合。
- **锚点**：本次 x-kernel 审计即此架构实战（4 路并行深读）；`讲透Agent/Topics全链路全景` L4 执行机制篇。

## 4. Effective Harnesses for Long-Running Agents（2025-11-26）

🔗 [原文](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

- **核心主张**：跨多上下文窗口的连续工作=**换班工程师问题**；compaction 不够，需要 initializer+coding 双 agent 与结构化交接。
- **两大失败模式**：①想一次做完（one-shot）→上下文中断在半实现状态，下个会话靠猜②后期会话看到已有进度就**提前宣布完工**。
- **机制**：**Initializer agent**（首会话）：写 init.sh（可重启 dev server）+ claude-progress.txt + 初始 git commit + **feature list：200+ 特征全标 failing 的 JSON 文件**（"完整功能的轮廓"）。**Coding agent**（后续每会话）：一次只做一个特征、结束留干净状态（git commit+进度笔记）、只许改 feature 的 passes 字段（强措辞禁删测试）。**JSON 优于 Markdown**——模型更不容易不当改写 JSON。启动仪式：pwd→读 progress→读 features→git log→跑 init.sh→**先端到端冒烟测基线**（防在坏基座上叠新功能）再开新特征。
- **可落地**：测试必须用浏览器自动化（Puppeteer/Playwright MCP）"像人类用户一样"——单元测试+curl 过了但端到端坏是高频漏网；五连启动清单可直接抄。
- **局限**：面向全栈 web app 优化；单通用 coding agent vs 多专化 agent（测试/QA/清理）仍是开放问题。
- **锚点**：`harness工程手册/07-会话生命周期与交接` 同构；x-kernel verify-gate 的"三级门禁+完成定义"即其内核版。

## 5. Harness Design for Long-Running Application Development（2026-03-24，Labs 团队）★最新

🔗 [原文](https://www.anthropic.com/engineering/harness-design-long-running-apps)

- **核心主张**：**GAN 式 generator-evaluator 分离**+planner 三 agent 架构；"每个 harness 组件都是对'模型做不到什么'的一个假设——要压力测试，模型进步后假设会过期"。
- **新概念**：①**context anxiety**——Sonnet 4.5 临近上下文限就提前收工；**reset（清空+结构化交接）> compaction**（compaction 不给干净起点，焦虑仍在）；Opus 4.5 起基本自愈②**自评失效**——agent 给自己的作品打分一律自信吹捧；分离评审者后仍偏宽，但**把独立 evaluator 调苛刻远比让 generator 自我批判容易**。
- **机制**：前端四评分维度（design quality/originality/**craft**/functionality），加权前两者；评分标准明文惩罚"AI slop"（紫渐变白卡片之类模板脸）；"museum quality"措辞会把输出推向特定视觉收敛——**评分措辞本身在塑造输出**。三 agent：**Planner**（1-4 句→野心勃勃的产品 spec，只管产品与高层技术设计，防细粒度错误级联）、**Generator**（sprint 制一次一特征，React/Vite/FastAPI/SQLite→PostgreSQL）、**Evaluator**（Playwright MCP 真点击，硬阈值不过则 sprint 失败返工）。**Sprint contract**：gen 与 eval 在写码前先谈妥"这次 done 是什么"。agent 间通信全走**文件**。荷兰美术馆站第 10 轮迭代扔掉重来做 3D 透视画廊——单次生成从未见过的创造性跳跃。
- **硬数字**：复古游戏机制造器——solo $9/20min（核心玩法坏的）vs 完整 harness $200/6hr（能用+内置 AI 特性）= **20×成本**；DAW：**3h50m / $124.70**（planner $0.46/4.7min；build 三轮 $71+$37+$6；QA 三轮 $3-4/轮）。evaluator 发现精准到行号（`fillRectangle` 未挂 mouseUp；FastAPI 路由序致 422）。
- **可落地**：Claude **开箱是很差的 QA**（发现自己说过的问题后说服自己"不算大事"然后放行；测试浅尝）——调优循环=读它的 log 找判断分歧点改 QA prompt；**Opus 4.6 后删掉 sprint 结构**（原生会分解了），evaluator 变终局单次评审——**新模型发布时逐件拆除不再承重的组件**。
- **局限**：贵且慢（$124-200/次）；evaluator 对"听不见"的领域（音乐品味）失效；产品直觉缺口（工作流顺序引导）是底模问题非 harness 能补。
- **锚点**：这是 `harness工程手册` v1.1 之外**最直接的官方后续**——把手册 12 章骨架推到三 agent GAN 式；x-kernel 深读审计（4 路 delegate + 主会话裁决）就是它的低配实例。

## 6. Introducing Advanced Tool Use（2025-11-24）

🔗 [原文](https://www.anthropic.com/engineering/advanced-tool-use)

- **核心主张**：工具调用三瓶颈各有专门解法：**发现（Tool Search）/执行（Programmatic Tool Calling）/正确性（Tool Use Examples）**，按最大瓶颈分层启用。
- **机制+硬数字**：
  - **Tool Search Tool**：`defer_loading: true` 按需加载；5 server 58 工具 ≈55K token 常驻（Anthropic 实测见过 **134K**）；启用后 77K→**8.7K**（-85%），MCP 评测 Opus 4 **49%→74%**、Opus 4.5 **79.5%→88.1%**；不破坏 prompt cache（延迟工具不进初始 prompt）；官方建议阈值：工具定义 >10K token 或 >10 个工具。
  - **Programmatic Tool Calling**：Claude 写 Python 在 code execution 沙箱里编排工具（asyncio.gather 并行），中间结果不进上下文——预算合规例：200KB 原始数据→**1KB** 结果；复杂任务 token **43,588→27,297（-37%）**；知识检索 25.6%→28.5%、GIA 46.5%→51.2%。适用：3+ 依赖调用、聚合/过滤型任务、50 端点并行检查。
  - **Tool Use Examples**：`input_examples` 进工具定义，教 schema 教不了的惯例（日期格式/ID 约定/参数相关性/嵌套结构何时填）；复杂参数处理准确率 **72%→90%**；1-5 个例子/工具，只加在有歧义处。
- **可落地**：分层策略——上下文膨胀→Search；中间结果污染→PTC；参数错误→Examples。三者互补可叠加。
- **局限**：各加一层延迟/开销，小工具集（<10）不值得。
- **锚点**：MCP 协议生态全景的"无状态化"篇同周期；Skills 渐进披露（`Skills生态全景`）与 defer_loading 是同一思想在两个生态的实现。

---

## 7. Scaling Managed Agents: Decoupling the Brain from the Hands（2026-04-08）★架构分水岭

🔗 [原文](https://www.anthropic.com/engineering/managed-agents) ｜ 官方已把 building-effective-agents 定位为"既往指导"，当前做法看本篇

- **核心主张**：harness 固化的"模型不会做 X"假设会随模型进步**过期**；应仿 OS 抽象（进程/文件）把 agent 虚拟化为**稳定接口**，实现层随便换。
- **机制**：三接口各自可独立失败替换——**session**（append-only 日志）/ **harness**（调模型的循环）/ **sandbox**；脑手分离：`execute(name,input)→string` 调容器，容器死=工具报错而非会话死，`wake(sessionId)` 重启续跑；**凭证永不入沙箱**（git token 初始化织入 remote，MCP OAuth 走 vault+代理）；session≠上下文窗口：`getEvents()` 位置切片回读，压缩/裁剪归 harness 层。
- **硬数字**：p50 TTFT **-60%**，p95 **-90%+**。
- **可落地**：对接口固执、对实现放任；上下文外置为持久可回溯对象（替代不可逆压缩）；凭证隔离在沙箱可达域之外。
- **与五模式的关系**：五模式整体降级为接口背后**可换的实现**而非点名废弃；编排-工人+并行泛化为 many brains / many hands；"context reset 变 dead weight"即假设过期的实例（此段含子代理推断，原文未逐条点名）。
- **局限**：托管服务，自建者只能借接口思想。

## 8. Writing Effective Tools for Agents — with Agents（2025-09-11）

🔗 [原文](https://www.anthropic.com/engineering/writing-tools-for-agents)

- **核心主张**：工具是确定性软件与非确定性 agent 间的**新契约**，按 agent 可供性设计，不是按人读 API 的思维写。
- **机制**：原型→评测→**把 transcript 喂给 Claude Code 自动改工具**的闭环；按任务形状合并工具（schedule_event 取代 list_users+create_event）；命名空间划界（asana_search）——前/后缀选择对结果影响非平凡；返回高信号上下文：UUID→自然语言名、`response_format: concise|detailed`；工具描述即 prompt 工程。
- **硬数字**：concise 72 token vs detailed 206（**1/3**）；Claude Code 工具响应默认截断 **25,000 token**。
- **可落地**：held-out 评测集+CoT 反馈定位卡点；分页/截断+可操作报错；参数名去歧义（user→user_id）。
- **局限**：最优命名/响应格式随模型而变，必须自己跑评测。

## 9. Introducing Contextual Retrieval（2024-09-19）

🔗 [原文](https://www.anthropic.com/engineering/contextual-retrieval)

- **核心主张**：切块丢失上下文是 RAG 检索失败主因；LLM 为每块生成**情境前缀**再做嵌入+BM25。
- **机制**：Contextual Embeddings（Haiku 读全文+块→50-100 token 前缀）；Contextual BM25（同前缀进词法索引，补精确匹配如错误码 TS-999）；叠 rerank（top-150→top-20）。
- **硬数字**：top-20 检索失败率 5.7%→3.7%（**-35%**）→2.9%（+BM25，**-49%**）→1.9%（+rerank，**-67%**）；情境化成本 **$1.02/百万文档 token**；<200k token（约 500 页）知识库直接塞 prompt 更好。
- **可落地**：prompt caching 摊薄成本；embedding+BM25+rerank 全叠；送 top-20 优于 top-10/5。
- **局限**：rerank 增延迟成本；收益随嵌入模型而异。
- **锚点**：`讲透RAG` 系列的官方对照版。

## 10. Claude Code: Best Practices（原发 2025-04-30；官方已 308 跳转至 code.claude.com/docs）

🔗 [现行版](https://code.claude.com/docs/en/best-practices)

- **核心主张**：把 Claude Code 当**可配置同事**：定制环境（CLAUDE.md/权限）+激进上下文管理，胜过反复调 prompt。
- **机制**：CLAUDE.md（/init 生成、/context 验证、子目录按需加载），逐行问"删掉会导致犯错吗"；权限三级：/permissions 白名单+OS 沙箱+auto mode 分类器；上下文：任务间 /clear、/compact、Esc+Esc 回滚；headless `claude -p` 进 CI，bash 循环+--allowedTools 扇出批量迁移。
- **可落地**：批量任务先用前 2-3 个文件调 prompt 再全量；新任务必开新会话；"同一问题纠正超两次即 /clear 重开"。
- **局限**：纯定性经验，无量化评测。

## 11. How We Contain Claude Across Products（2026-05-25）

🔗 [原文](https://www.anthropic.com/engineering/how-we-contain-claude)

- **核心主张**：agent 的爆炸半径只能靠**环境层确定性边界**封顶——概率性防御（模型层/人工审批）必有非零漏网。
- **机制**：三风险（用户滥用/模型失当/外部攻击）×三防御层（环境/模型/外部内容）；按产品分级隔离：claude.ai=gVisor 临时容器、Code=HITL 沙箱（Seatbelt/bubblewrap）、Cowork=本地 VM+出口 MITM 代理；**egress allowlist 本质是能力授予而非目的地过滤**（api.anthropic.com 泄密案）；自研件是最弱点，hypervisor/seccomp/gVisor 标准原语反而不破。
- **硬数字（红队实测）**：权限弹窗 **93% 被批准**（审批疲劳）；OS 沙箱后弹窗 **-84%**；钓鱼红队 **25 次中招 24 次**；Opus 4.7 注入攻击单次 ~0.1%、百次自适应 **5-6%**；auto mode 拦 ~83% 越权、漏 ~17%、误杀 0.4%。
- **可落地**：凭证永不入沙箱；**symlink 解析必须先于路径校验**；项目本地配置解析推迟到信任弹窗之后。
- **局限**：隔离削弱可见性（EDR 看不进 VM）；模型层永不 100%。
- **锚点**：`openclaw` 深读的四档权限+net-policy fail-closed 是同一思想的社区版；PRISM=其安全层插件。

---

## 横向综合：六篇连读的三条主线

1. **Loop→Context→Harness→Generator-Evaluator 的进化链**：五模式(2024-12)→上下文经济学(2025-09)→多 agent 并行(2025-06)→双 agent 交接(2025-11)→GAN 三 agent(2026-03)→**Managed Agents 虚拟化(2026-04)**——每篇都在解决上一篇的剩余问题，且**每代都更贵**（4×→15×→$124-200/任务）但能力边界同步外推。
2. **"假设过期"是 harness 第一定律**：Opus 4.6 让 sprint 结构失业、context anxiety 自愈、context reset 变 dead weight——**模型发布= harness 组件退役审查日**（harness 手册 10 章反模式篇的官方版论据；Managed Agents 把这一定律制度化成了"可换实现"架构）。
3. **自评不可信需要制度化的他评**：从 tool-testing agent（-40%）到 evaluator agent（精准到行号的 FAIL 清单），Anthropic 把"分离评审者+调苛刻"做成了标准件——x-kernel 的 verify-gate 三级门禁是同一原理的编译器版；contain-claude 的数字（93% 批准/25 钓 24 中）则给"他评"补上了安全维度的定量下限。

## refs
- 十一篇全文 webfetch 2026-08-20（主会话 6 篇一手 + 子代理 5 篇逐字读取，数字均出自原文；best-practices 已按官方 308 跳转取现行版）
- 配套：`105-Anthropic官方技术文章全集（sitemap实测）.md`（全量索引）；`107`（interp 线）；`harness工程手册/`（12-15 章）；`讲透Agent/Topics全链路全景/notes/01`（L4 执行机制）

*updated: 2026-08-20*
