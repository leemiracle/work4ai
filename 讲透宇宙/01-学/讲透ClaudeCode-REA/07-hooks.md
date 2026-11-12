# 07 · Hooks：33 事件双体系与权限汇合

> 证据：minified 源码偏移考古（事件注册表 `uG()`[offset=4006050]、执行器
> `uge`[5155747]、权限汇合 `sho`[2282130]）[S]。深报告（33 事件全表+输出
> schema+IPC 协议 14 种消息）：`rea-claude/reports/07-hooks.md`（44KB）。

## 1. 事件体系：33 个（不是 12 个）[S]

权威清单=插件 hook 注册表：`PreToolUse / PostToolUse / PostToolUseFailure /
PostToolBatch / PermissionDenied / PermissionRequest / UserPromptSubmit /
UserPromptExpansion / SessionStart / SessionEnd / Stop / StopFailure /
SubagentStart / SubagentStop / PreCompact / PostCompact / PreModelSwitch /
PostModelSwitch / Notification / Setup / TeammateIdle / TaskCreated /
TaskCompleted / Elicitation / ElicitationResult / ConfigChange /
WorktreeCreate / WorktreeRemove / InstructionsLoaded / CwdChanged /
FileChanged / DirectoryAdded / MessageDisplay`。

- 每事件有 matchQuery（matcher 比对值：tool_name/source/trigger/agent_type/
  to_model…）与专有输出字段（PreToolUse 的 permissionDecision/updatedInput、
  UserPromptSubmit 的 additionalContext/sessionTitle、PermissionRequest 的
  decision…）；
- **async hooks 支持 12 个事件**：stdout 首行 `{"async":true,"asyncTimeout":ms}`
  转后台，超时后结果经 rewake 通道回来；
- 容器端裁剪表：云会话给事件分级（runs_locally/low_value/later/container_internal）。

## 2. 执行器（shell 形态）[S]

- **默认超时 10 分钟**（例外：UserPromptSubmit 30s；prompt 型 30s；agent 型 60s；
  SessionEnd 夹 [1.5s,60s] 且关机前只等 30s）；
- shell/exec 双形态；`${CLAUDE_PROJECT_DIR}/${CLAUDE_PLUGIN_ROOT}/
  ${CLAUDE_PLUGIN_DATA}` 变量替换（插件专属变量在 settings.json 用会抛错）；
- env 注入：CLAUDE_PLUGIN_OPTION_<KEY>（插件 user_config）等；
  `${user_config.*}` 在 shell 形态拒绝（防二次解析注入）；
- **并发**：shell/http/mcp_tool/prompt/agent 型并发跑，SDK callback 型串行；
- **聚合序：deny > defer > ask > allow > passthrough**（allow 仅在无任何其他
  决定时生效）；同构 hook 跨层级去重；
- **`if` 条件语法=权限规则**（如 `Bash(rm:*)`）——复用 preparePermissionMatcher。

**五种 hook 形态**：shell / http / mcp_tool / prompt（直接调 LLM 判定，Stop 事件
要求模型只答 `{"ok":true/false,"impossible":...}` JSON）/ agent（起带工具的
子 agent 验证停止条件，"verify that the agent completed the given plan"）。

## 3. function hooks（插件 JS 运行时）[S]

- 插件模块必须导出 `register(on, options)`；`on(event, matcher, hook)`
  （matcher=结构化 partial）；
- **hooks-worker = Bun Worker 进程**（MessageChannel per-plugin，IPC 协议
  14 种消息）；脚本本体已解出全文；
- **`$` 宿主 API 40+**：model.complete / tool.call / store.* / fs.* / ui.*——
  插件拿到的是受控宿主能力面而非裸 Node；
- JSX UI 组件（Box/Text/Button/Input/Select/Svg/Link，vm 沙箱序列化）；
  模块限额 1MB/文件、512 文件、8MB 总量。

## 4. 配置合并 [S]

三源：policy 启动快照 + settings/SDK + 插件；policy disableAllHooks /
allowManagedHooksOnly 分层压制（**disableAllHooks 下 SDK callback hooks 仍跑**）。

## 5. 权限汇合（最关键发现）[S]

PreToolUse 的 hook 决定与权限规则在 `sho()` 合成，硬序：

```
hook deny 一票否决（不查规则）
  > deny 规则（hook allow 也压不过）
  > ask 规则（hook allow 被重浮为 ask）
  > hook allow（可越过"默认需询问"，但 canUseTool/auto 分类器仍拦）
  > 正常权限管线
```

- `updatedInput` 不过工具 schema → 直接 deny；
- **confined session 一律忽略 hook allow**（"takes grants only from its
  command line"）——防注入的纵深：grant 只来自命令行。

## 6. 手搓启示（→ rl-and-agents/）

1. hook 体系的本质是**策略外挂点**：12+ 事件 × 5 种形态（shell/http/LLM/agent/JS）
   覆盖从"跑个脚本"到"LLM 判定停止条件"的全谱；
2. **hook allow 权限低于 deny 规则**——扩展不能给自己提权，这是安全模型的
   基石，手搓任何插件系统先定这条；
3. prompt/agent 型 hook 是"LLM 判定"的工程化：约束输出为 JSON 三态、证据不足
   =不满足、impossible 单列——值得任何 stop-condition 系统抄；
4. 去重+聚合序（deny>ask>allow）让多 hook 组合可预测——没有"最后一个 hook
   说了算"的混沌。
