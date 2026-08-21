# 生态分析文档 DeepWiki 增补（第七部分）

> 副本来源：~/ai/agent/awesome-agents/AWESOME-AGENTS-ANALYSIS.md（2026-08-21 增补章节）

# 第七部分：DeepWiki 全景增补（2026-08-21）

> **背景**：本报告最初基于 133 仓库源码静态分析。2026-08-21 完成 DeepWiki（deepwiki.com）全量抓取：**98/135 仓库有 AI 生成 wiki**（含全部子页面与 mermaid 架构图），全文归档于 `deepwiki/{name}/full.md`，导航骨架 `skeleton.md`；37 仓库未收录（含 crewai/langchain/llama_index/memgpt/swe-agent/e2b 等大牌——DeepWiki 未索引 ≠ 不重要）。总索引见 [DEEPWIKI-INDEX.md](./DEEPWIKI-INDEX.md)，深读卡见 work4ai `讲透Agent/Agent框架案例/DeepWiki深读卡/`。

## 7.1 对前文的关键事实修正（DeepWiki 2026-08 快照）

| 前文表述 | 2026-08 实况 | 来源 |
|---|---|---|
| AutoGen 为活跃微软框架 | **官方维护模式**：不再新增特性，新项目指路 Microsoft Agent Framework（README.md:14-26）；SK 同步宣布汇入 | autogen-ms wiki Overview |
| OpenHands V0 架构（AgentController+EventStream） | **V0 已删除**（2026-04-01），V1 = app_server + 外部 openhands-sdk + 沙盒内 agent-server 镜像 | openhands wiki 1.2 |
| swarm 为 OpenAI 实验框架 | **官方废弃**，README 顶部声明被 openai-agents-python (Agents SDK) 取代 | swarm wiki Overview |
| AgentGPT/BabyAGI-UI 为可用工具 | 均已**归档/停维护**——价值转为第一代架构教具 | 各自 wiki |
| aider/RepoMap、DSPy/MIPROv2 等分析 | 经 wiki 全文核验**依然准确**（第四部分增强可信度） | 各自 wiki |

## 7.2 新增创新点清单（前文未覆盖，源自 98 仓深读）

1. **AEON：GitHub Actions 当运行时 + git 仓库当数据库**——零基础设施自主 Agent，Prefetch/Post-process 双脚本绕沙箱网络限制，Exit Taxonomy 六类退出码支撑自愈（37 页）。
2. **ACE：Recursive Reflector**——LLM 在受限 REPL 里写 Python 代码程序化分析执行 trace（而非单遍总结），Skillbook 策略库带引用追踪（93 页，Tau2 pass 率翻倍）。
3. **bernstein：zero-LLM coordination**——纯 Python 状态机协调 40+ CLI coding agents，HMAC-SHA256 审计链 + 确定性重放（48 页）。
4. **aden-hive：Goal→Judge 验收驱动 + coding agent 改图自进化**——路由让位于成功判据（ACCEPT/RETRY/ESCALATE），失败日志喂给 Claude Code 改 agent 图（31 页）。
5. **actionbook：发现/执行分离**——ReAct 浏览器探索一次，沉淀带置信度多路 selector 的"网站操作手册"资产，号称 10x 执行提速/100x token 节省（40 页）。
6. **claw-code：Worker Boot 状态机 + Recovery Recipes**——启动失败六分类（PromptDelivery/TrustGate/BranchDivergence…）各有自愈配方；Trident 三级压缩（Supersede/Collapse/Cluster）+ 边界保护（35 页）。
7. **AG2：工具依赖注入**——register_function 按参数类型注解自动注入运行时对象（ConversableAgent/db 连接），超越 plain function calling（59 页）。
8. **screenpipe：SQL 行级权限过滤**——pipe.md 声明式 Agent 插件权限贯彻到数据库查询行，而非网关 URL 拦截（48 页）。
9. **openhands：沙盒即服务三后端**——Docker/Remote/Process 统一 SandboxService ABC + 沙盒内 ActionExecutionServer（:60000）执行下推（88 页）。
10. **cline：Focus Chain**——跨上下文压缩的结构化进度链，压缩后不丢总目标（85 页）。

## 7.3 前文趋势预测的 2026-08 校验

| 6.3 预测 | 校验结果 |
|---|---|
| MCP 标准化 | ✅ 已兑现且超预期：双向 MCP（AutoGen 可当 Host 反向 sampling/elicitation）、AG2/cline/opencode 全员原生支持 |
| 代码即动作 | ✅ CodeAct（openhands）成为主流范式；smolagents CodeAgent + LocalPythonExecutor 安全执行成熟 |
| 记忆系统成熟 | ⚠️ 进行中：Condenser 三策略（openhands）/三级压缩（opencode/claw-code）落地，但"五层标配"未发生——竞争焦点转向**上下文工程**（PageRank/树地图/压缩管线） |
| 自动 Prompt 优化 | ✅ DSPy 优化器族扩张（MIPROv2/GEPA/SIMBA），framework 内集成仍有限 |
| 安全沙盒化 | ⚠️ 部分兑现：microVM 未普及，Docker 沙盒（openhands/codel）成默认；注意 codel 挂 docker.sock 的反面案例 |
| Agent 评估标准化 | ✅ phoenix（OpenInference 数据契约）+ agbench + LLM-as-judge 工具化 |
| 多 Agent 去中心化 | ❌ 未兑现：uAgents 路线仍小众，主流收敛到编排框架+协议层（MCP/A2A/AG-UI） |

## 7.4 DeepWiki 数据使用指南

- **找某框架的权威细节**：先查 `DEEPWIKI-INDEX.md` → 状态 ✅ 则读 `deepwiki/{name}/skeleton.md` 定位页 → 按 full.md 行号精读（每页带源文件引用与行号）。
- **深读卡（31+ 张）**：work4ai `讲透Agent/Agent框架案例/DeepWiki深读卡/`，含创新点×缺点批判总览（00-创新点与缺点总览.md）。
- **注意**：DeepWiki 是 AI 生成快照（各仓库索引时间不一），关键结论应交叉本地源码验证——深读卡的"关键入口"字段即为此设计。
