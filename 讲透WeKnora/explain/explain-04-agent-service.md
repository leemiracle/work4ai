# explain-04 · internal/application/service/agent_service.go — Agent 引擎工厂

```
文件路径: internal/application/service/agent_service.go
行数:     1550 行
所属层:   应用服务层（layer:application）
扇出:     416 条依赖边
一句话:   CreateAgentEngine 按每轮 AgentConfig 组装一次性 AgentEngine——工具/MCP/沙箱/技能全装配。
```

## 一、角色定位

WeKnora 的 Agent **每轮对话现造现用**（internal/agent 跑 ReAct 循环）。本文件实现 interfaces.AgentService（types/interfaces/agent.go:53）：SessionService（session_agent_qa.go:206）与技能安装器（tenant_skill_install.go:1031）调 CreateAgentEngine 时，由它把"这轮允许干什么"译成引擎构造参数。工具可用性取决于运行时能力（KB 面、沙箱、记忆、只读契约），须每轮重算。

## 二、内部结构

**骨架与主工厂**：agentService 持 23 依赖（L95），container.go:321 注入。CreateAgentEngine（L180-296）五步：①校验（L191，MaxIterations 缺省 5、上限 100）；②建工具注册表，注册内置/MCP/沙箱工具（L204）；③KB/选中文档元数据（L224）；④系统提示词模板（L227）；⑤new 引擎并 Set 置顶提及/VLM/技能管理器/浏览器（L241）。

**工具注册策略 registerTools（L838-1161）**：白名单唯一真源（L846，绝不静默注入）；能力探测（L869-909 查 KB 向量/图/wiki 开关；可写面收窄 WritableKBIDs，L906 防跨租户写）；三重过滤：纯 Agent 剔 KB/wiki 工具（L911）、运行时开关压倒存量 allowlist（L949）、硬安全网剔无能力面工具（L1005）；L1053 起大 switch 逐个实例化。

**沙箱与技能**：registerSandboxShellTool（L809）普通 agent 非 root、限 /workspace，安装模式才拿 root；registerSandboxFileTools（L416）文件读写（安装模式改走 write_skill_file）；resolveWorkspaceSandbox（L531）拿会话真实后端；initializeSkillsManager（L564）装载技能，loadInstalledSkillBundle（L664）SHA 防旧档。

## 三、外部连接

import 17 个包：agent 子包、browserskill、mcp、chat/rerank、sandbox、event 等——416 条扇出边来源。被依赖：session_agent_qa.go、tenant_skill_install.go（安装器）及 agent_*.go 扩展，上层只见接口契约。

## 四、数据流

SessionService 载入 AgentConfig→CreateAgentEngine：查 KB 能力定工具集→按 all/selected/none 取 MCP 目录（L299）→拿会话沙箱、注册 shell/文件工具→装载技能→装配 runtime_context→返回引擎。engine.Execute 跑 ReAct 循环（归 agent）：模型调工具，闭包捕获的正是本文件注入的 service 与 scope。

## 五、设计决策

"每轮重建"是刻意为之：工具面/KB/沙箱配置会话级可变，无状态引擎（L177）避免旧工具残留。策略层级：白名单>开关>硬安全网，绝不静默注入、只显式剔除（L846）。可批判：23 参构造是代码异味（L705 自认该拆）；registerTools 320 行承载全部策略，安全网有隐式顺序依赖；错误多 Warn+降级（L377 兜底），健壮但难排查。

## 六、新人提示

- 新增工具：tools 包实现+L1056 加 case+前端 AgentEditorModal.vue 同步（L978 钉了双端义务）。
- "工具没出现"排查：白名单→安全网日志→沙箱是否 advertise 能力。
- SkillInstallMode 特权分支仅内置安装器可进（L806）；共享 agent 只读靠 withoutWikiWriteTools（L1167）——工具不走 HTTP 中间件，删错即越权写。
- 延伸阅读：DeepWiki 3.3-agent-system-and-react-engine、11.9-skills-and-sandbox-execution。
