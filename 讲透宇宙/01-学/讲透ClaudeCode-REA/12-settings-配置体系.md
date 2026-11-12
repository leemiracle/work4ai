# 12 · 配置体系：settings / CLAUDE.md / 环境变量

> 证据：源码中 100+ 个环境变量的引用密度统计 [S]、CLI --help [S]、内嵌文档 [D]。
> 本册是"把 Claude Code 当黑盒用"时的权威速查。

## 1. 配置文件层级（优先级从高到低）[S+D]

```
1. 命令行参数            claude --model ... --allowedTools ...
2. 会话内命令            /model /permissions /output-style ...
3. 项目本地  .claude/settings.local.json    （不进 git）
4. 项目共享  .claude/settings.json
5. 插件/托管 .claude/plugin/…、企业策略 managed-settings
6. 用户全局  ~/.claude/settings.json        （env/model/permissions/hooks）
7. 环境变量   （见 §3）
8. 记忆文件   CLAUDE.md 层级（企业 ~ → 用户 → 项目 → 子目录，按需注入）
```

`--bare` 模式 [S]（--help 实证）会跳过 hooks/LSP/插件同步/CLAUDE.md 自动发现/
密钥链读取，认证严格限定 `ANTHROPIC_API_KEY` 或 `apiKeyHelper`——CI/容器场景用。

## 2. settings.json 关键字段（~/.claude/settings.json）[S]

```jsonc
{
  "env": {                       // 注入到会话与子进程
    "ANTHROPIC_BASE_URL": "...",     // API 端点覆盖（代理/网关用）
    "ANTHROPIC_AUTH_TOKEN": "...",   // Bearer token（区别于 x-api-key）
    "ANTHROPIC_MODEL": "..."         // 默认模型
  },
  "model": "...",                // 等价 /model
  "permissions": {               // 三态规则表，见 06 册
    "allow": ["Bash(git diff:*)", "Read(~/.zshrc)"],
    "ask":   ["Bash(git push:*)"],
    "deny":  ["Read(./.env)", "Bash(curl:*)"]
  },
  "hooks": { "PreToolUse": [{ "matcher": "Bash", "hooks": [...] }] },
  "statusLine": { "type": "command", "command": "..." },
  "outputStyle": "default",
  "includeCoAuthoredBy": true,
  "apiKeyHelper": "/path/to/script",   // 每次调用输出 key（比静态 env 安全）
  "forceLoginMethod": "clerk|azureAd|...",
  "mcpServers": { ... }         // 用户级 MCP 服务器
}
```

## 3. 环境变量全景（按引用密度排序的代表性子集）[S]

### 认证与账户
| 变量 | 作用 |
|---|---|
| `ANTHROPIC_API_KEY` | x-api-key 认证（104 处引用） |
| `ANTHROPIC_AUTH_TOKEN` | Bearer 认证（51）——OAuth/网关场景 |
| `CLAUDE_CODE_OAUTH_TOKEN` / `..._FILE_DESCRIPTOR` | OAuth 凭据直传/fd 传递（90） |
| `CLAUDE_CODE_API_KEY_FILE_DESCRIPTOR` | key 走 fd 而非 env（防 ps 泄露） |
| `apiKeyHelper`（settings） | 外部脚本供给凭据 |
| `CLAUDE_CODE_ORGANIZATION_UUID` / `..._ACCOUNT_UUID` | 企业账户绑定 |

### API 端点与多云路由
| 变量 | 作用 |
|---|---|
| `ANTHROPIC_BASE_URL` | 端点覆盖（77）——**接入代理/自建网关的主通道** |
| `ANTHROPIC_CUSTOM_HEADERS` | 附加请求头（41） |
| `CLAUDE_CODE_USE_BEDROCK` / `_USE_VERTEX` / `_USE_FOUNDRY` | AWS / GCP / Azure Foundry 通道（17/18/12） |
| `CLAUDE_CODE_USE_ANTHROPIC_AWS` / `_GOOGLE_CLOUD` | Anthropic-on-cloud 直供（14/14） |
| `CLAUDE_CODE_USE_MANTLE` + `ANTHROPIC_BEDROCK_MANTLE_BASE_URL` | Mantle 层（内部 AWS 封装，15/13） |
| `CLAUDE_CODE_USE_GATEWAY` + `..._ENABLE_GATEWAY_MODEL_DISCOVERY` | 企业网关模式（12/10） |
| `ANTHROPIC_BEDROCK_BASE_URL` / `ANTHROPIC_VERTEX_BASE_URL` / `ANTHROPIC_FOUNDRY_BASE_URL` | 各云自定义端点 |
| `CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL` | 把自定义端点当一方服务对待（13） |

### 模型选择
| 变量 | 作用 |
|---|---|
| `ANTHROPIC_MODEL` | 默认模型（22） |
| `ANTHROPIC_DEFAULT_OPUS_MODEL`（35）/ `_SONNET_`（29）/ `_HAIKU_`（28）/ `_FABLE_`（21） | **按档位别名自定义映射**——四大家族都可作为路由目标 [S] |
| `ANTHROPIC_SMALL_FAST_MODEL` | 后台小任务模型（16，历史名 Haiku 槽位） |
| `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` | 强制子代理模型（15） |
| `MAX_THINKING_TOKENS` | thinking 预算上限（10） |
| `CLAUDE_CODE_EFFORT_LEVEL` | 推理努力档位（14） |
| `CLAUDE_CODE_EXTRA_BODY` | 透传额外请求体字段（12） |

### 会话与运行形态
| 变量 | 作用 |
|---|---|
| `CLAUDE_CODE_ENTRYPOINT` | 入口标记：cli/sdk/vscode…（89） |
| `CLAUDE_CODE_SESSION_KIND` / `_ENVIRONMENT_KIND` / `_REMOTE_ENVIRONMENT_TYPE` | 会话/环境分类（42/26/10） |
| `CLAUDE_CODE_REMOTE` / `_REMOTE_SESSION_ID` / `_REMOTE_MEMORY_DIR` | 云远程会话体系（158/53/11）——**全库引用密度第一**，远程/云形态是主战场 [I] |
| `CLAUDE_CODE_CHILD_SESSION` / `_WORKER_EPOCH` | 子代理/worker 会话标记 |
| `CLAUDE_CODE_IS_COWORK` | Cowork 产品形态标记（12）[D: Cowork Plugin Authoring] |
| `CLAUDE_CODE_SIMPLE` | --bare 模式内部标记（20） |
| `CLAUDE_CODE_TMPDIR` | 临时目录（31） |
| `CLAUDE_CODE_SHELL_PREFIX` | shell 命令前缀包装（20，审计/包装用） |
| `CLAUDE_CODE_PROCESS_WRAPPER` | 进程包装器（13） |

### 行为开关（节选）
| 变量 | 作用 |
|---|---|
| `DISABLE_TELEMETRY` / `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | 遥测/非必要流量关闭（10/18） |
| `DISABLE_AUTOUPDATER` / `DISABLE_UPDATES` | 自更新关闭 |
| `DISABLE_COMPACT` | 关闭自动压缩（14） |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW` | autocompact 窗口（11） |
| `CLAUDE_CODE_DISABLE_CLAUDE_MDS` | 跳过 CLAUDE.md 注入（10） |
| `CLAUDE_CODE_USE_POWERSHELL_TOOL` | Windows PowerShell 工具切换（8） |
| `ENABLE_TOOL_SEARCH` | 工具延迟发现（deferred tools，17） |
| `MCP_TOOL_TIMEOUT` / `MCP_SERVERS_GROUP` / `MCP_CLIENT_SECRET` | MCP 控制（10/8/8） |
| `CLAUDE_CODE_ENABLE_CFC` | 提示缓存强开（8） |
| `CLAUDE_CODE_SKIP_*_AUTH`（bedrock/vertex/…6 个） | 跳过各云认证链（外部供给凭据） |

## 4. CLAUDE.md 记忆体系 [S]

- 发现顺序：项目根 `./CLAUDE.md`（或 `CLAUDE.local.md`）→ 上级目录 →
  `~/.claude/CLAUDE.md`（用户全局）；企业可加策略层。
- 注入方式：作为 system prompt 的一部分按需加载；`@import` 语法支持引用子文件
  （本仓 `--help` 与行为实证）。
- `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` 全关；`--bare` 隐含关闭。
- 与 skills 的分工：CLAUDE.md = 常驻上下文（每次都在），SKILL.md = 按需知识包
  （触发词命中才注入）——上下文经济学的两级缓存 [I]。

## 5. 一页纸结论

1. **端点全覆盖三通道**：`ANTHROPIC_BASE_URL`（直连代理）、`USE_BEDROCK/VERTEX/
   FOUNDRY`（云原生认证）、`USE_GATEWAY/MANTLE`（企业封装）——任何企业网络拓扑
   都有接法 [S]。
2. **模型路由四档别名**：opus/sonnet/haiku/**fable** 四族各有 DEFAULT_*_MODEL
   覆盖点——fable 族在 2.1.261 已是一等公民 [S]。
3. **凭据安全分级**：env 明文 < settings.json < apiKeyHelper 脚本 < fd 传递
   （`*_FILE_DESCRIPTOR`）——后两者防 `ps`/日志泄露 [I]。
4. **远程形态是重心**：`CLAUDE_CODE_REMOTE` 系 158 处引用居首，云会话/远程
   worker/Cowork 是产品主航道 [I]。

---
← [11-skills-插件](11-skills-插件.md) · → [13-遥测与反馈](13-遥测与反馈.md) · 总览 [01-总体架构](01-总体架构.md)
