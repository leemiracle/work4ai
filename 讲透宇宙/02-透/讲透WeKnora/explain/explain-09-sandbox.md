# explain-09 · internal/sandbox/session_manager.go — 会话绑定沙箱管理器

```
文件路径: internal/sandbox/session_manager.go
行数:     1593 行
所属层:   Agent 引擎与沙箱执行层（layer:agent）
一句话:   SessionBoundManager——把"一个租户会话 ↔ 一个持久远程沙箱"的绑定外置到 Redis，对 Cube/E2B/Docker 三种后端做供应商中立管理，是 Agent 代码执行的编排中枢。
```

## 一、角色定位

Agent 的 shell_exec、sandbox_write、技能脚本都要在隔离环境里跑，而 WeKnora 支持 Cube MicroVM、E2B、Docker 三种后端且允许多副本部署。本文件解决：**同一会话的两次执行如何落在同一沙箱、两个副本如何不重复开沙箱、进程重启如何不丢沙箱**。答案是把权威绑定放进 `SessionSandboxBindingStore`（生产 Redis、测试内存，L1-22 包注释），管理器自身无状态代理。`Execute` 带 SessionID 走会话绑定路径（懒创建），空 SessionID 走一次性 `RemoteSandbox` 用完即毁（L265-302）。属 L3 Agent 引擎与沙箱执行层，上承 agent 工具与 application 服务，下驱三个 remote client。

## 二、内部结构

**1. 工作区契约（L39-64）**：`/workspace/input`（附件，只读）、`/workspace/output`（产物）、`/workspace` 根，及 `WEKNORA_SKILL_OUTPUT_DIR` 等环境变量（L50/L56）——注入沙箱自身环境，agent 用 shell 探索时与技能框架读到一致路径。

**2. 核心与构造（L76-227）**：`NewSessionBoundManager` 用 `Client.Provider()` 而非 `Config.Type` 判定身份（L122-125，测试注入别的前端也能投影正确模板/TTL）；空模板立即报错（L171）；套 langfuse 壳（L178）；每请求重建的租户 resolver 可跳过健康探测（L209-215）。

**3. 执行与文件 API**：`Execute`（L265）先过脚本安全校验再分流；`prepareSessionDirs`（L316）以执行账号 bootstrap 目录，失败即中止、"永不重命名删除来自称修复"（L313-315）；`WriteSessionInputFile`（L502，只准入 input）、`WriteSessionWorkspaceFiles`（L543，模型写作但禁入 input）、`WriteSessionFile`（L672，仅限技能镜像根）；路径清洗集中于 L1416-1469。

**4. Shell 与能力接口**：`ShellExecOptions`（L705）含 `ExpectedSandboxID`（防绑定漂移）、`AsRoot` 等；`execShellCommandWithOutputSnapshot`（L780-884）执行前后各拍产物目录快照供增量收集；能力广告方法（L888-980）按后端能力返回 nil 或自身，L1574-1580 接口断言钉住 5 个角色。

**5. 解析与后端差异**：`resolveSession`（L1176）经生命周期协调器（分布式锁串行 create/recover/replace）；`lookupSessionHandleForKey`（L1294）读绑定→Connect→校验一致；`peekBoundSandboxState`（L1192）只 List 不 Connect，避免唤醒暂停实例。`buildSessionCreateRequest`（L1478-1546）：Cube/E2B 超时暂停+自动恢复，Docker 超时直接杀（暂停不释放宿主内存）。

## 三、外部连接

**依赖**：`RemoteSandboxClient` 三实现（cube/e2b/docker_remote_client.go）、binding store 与 lifecycle、`ScriptValidator`。**被依赖**：`manager.go:268`（DefaultManager 兼容层）、`tenant_resolver.go:194`（每请求按租户构建）；上游有 agent/tools 四个工具文件、`agent/skills/manager.go`、application/service 的 artifact_collector 等 4 个服务及 `handler/session/agent_stream_handler.go`（turn 租约 L1074-1104）。

## 四、数据流：一次 shell_exec

Agent 决定执行 `pip install pandas`：① shell_exec 工具带 sessionID 调 `ExecShellCommand`（L733）；② 校验远程后端、清洗 workDir（须绝对路径且在 /workspace 下）；③ `resolveSession`→lifecycle.Resolve：Redis 查绑定，首次则按模板/TTL 创建 MicroVM 并写回；④ `prepareSessionDirs` 确保三目录可写（L857-861）；⑤ `client.Exec`（L866）带流式回调执行，产物落 `/workspace/output`；⑥ 前后两次 `snapshotOutputFiles`（L1327）的差集即新增产物，交 artifact collector 展示。

## 五、设计决策

- **权威状态外置**是"多副本安全"的根本（L7-10），代价是每操作多一跳 Redis 与分布式锁。
- **lookup 与 resolve 严格分离**：终端/桌面/读取绝不触发创建——"打开面板不能唤醒并计费一个暂停的 VM"（L929-936 注释），边界按账单语义而非代码便利划。
- **诚实的词法防护**：`cleanSessionWorkDir` 注释承认 allowlist 只是词法检查、root 命令并无文件系统边界（L1443-1445），隔离责任留给容器/MicroVM。
- 批判点：1593 行实现 8 个接口，能力拆到接口却未拆到实现，后端差异散落三处 switch；"绝不可由模型工具设置"的 flag 靠注释约定而非类型系统，是潜在越权面。

## 六、新人提示

- 报"sandbox: xxx template ID is required"（L171）先查后端 template/image 配置。
- Docker 后端没有 PTY/桌面/快照（L919/L963 注释），UI 显示"不支持"而非"无沙箱"。
- `Cleanup`（L1055）只关管理器不删沙箱——生命周期归 binding store，本地清理反而泄漏给其他副本。
- 执行失败先查 workspace bootstrap（15s 超时，L64），多数是镜像里 /workspace 属主不对。
- 延伸：DeepWiki `11.9-skills-and-sandbox-execution.md`、`11.9.1-sandbox-runtimes-and-configuration.md`、`11.9.3-sandbox-tools-and-artifacts.md`。
