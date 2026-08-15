# 01 — Node CLI 入口与命令树（`@mem0/cli`）

> `@mem0/cli` 是 Mem0 的 Node.js 命令行工具,基于 Commander + Chalk + ora + cli-table3。
> **跟 Python CLI 功能 1:1 对应**,但工具链不同（Biome / vitest / tsup）。

---

## 1. 安装与入口

```bash
npm install -g @mem0/cli
# 或 pnpm add -g @mem0/cli
# 安装后:`mem0` 命令可用
```

```json
// cli/node/package.json
{
  "name": "@mem0/cli",
  "version": "0.2.12",
  "type": "module",                     // ⭐ ESM only
  "bin": { "mem0": "./dist/index.js" },
  "scripts": {
    "build": "tsup",
    "dev": "tsx src/index.ts",
    "test": "vitest run",
    "lint": "biome check src/",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "commander": "^12.0.0",
    "chalk": "^5.3.0",
    "cli-table3": "^0.6.4",
    "ora": "^8.0.0",
    "boxen": "^7.1.0"
  }
}
```

---

## 2. 文件结构

```
cli/node/src/
├── index.ts             # ⭐ 主 Commander program + 命令注册
├── version.ts           # CLI_VERSION
├── branding.ts          # Chalk 颜色 + brand 文本
├── output.ts            # 表格/json 输出
├── config.ts            # 配置文件 load/save
├── state.ts             # 全局 state（agent mode）
├── telemetry.ts         # PostHog 遥测
├── help.ts              # 自定义 help 格式
├── agent-detect.ts      # 检测 AI agent 环境
├── plugin-sync.ts       # 编辑器插件同步
├── globals.d.ts         # TS 全局类型
├── backend/
│   ├── base.ts          # Backend interface
│   ├── platform.ts      # HTTP backend
│   └── index.ts         # getBackend factory
└── commands/
    ├── init.ts          # mem0 init
    ├── memory.ts        # mem0 add/search/get/...
    ├── entities.ts
    ├── events.ts
    ├── config.ts
    ├── whoami.ts
    ├── identify.ts
    ├── agent-mode.ts
    ├── agent-rush.ts
    └── utils.ts
```

---

## 3. ⭐ `index.ts` 顶层

```typescript
#!/usr/bin/env node

import { Command } from "commander";
import { getBackend } from "./backend/index.js";

const program = new Command();

program
  .name("mem0")
  .description("◆ Mem0 CLI · The Memory Layer for AI Agents")
  .version(CLI_VERSION);

// 全局 options
program
  .option("--json", "Output JSON (agent mode)")
  .option("--agent", "Enable agent mode")
  .option("--api-key <key>", "Override API key")
  .option("--base-url <url>", "Override base URL");

// 子命令注册
program.command("init").action(initCmd);
program.command("add <text>").action(addCmd);
program.command("search <query>").action(searchCmd);
// ... etc

program.parse();
```

### 工具栈

| 库 | 用途 |
|---|------|
| `commander` | 命令解析 |
| `chalk` | 颜色（ESM v5+） |
| `cli-table3` | 表格输出 |
| `ora` | spinner |
| `boxen` | 框输出 |

---

## 4. 命令清单（与 Python CLI 同构）

| 命令 | 用途 |
|------|------|
| `mem0 init` | 初始化 |
| `mem0 init --agent --agent-caller claude-code` | Agent signup |
| `mem0 add <text>` | 添加 memory |
| `mem0 search <query>` | 搜索 |
| `mem0 get <id>` | 取单条 |
| `mem0 get-all` | 列出 |
| `mem0 update <id>` | 更新 |
| `mem0 delete <id>` | 删除 |
| `mem0 delete-all` | 批量删 |
| `mem0 history <id>` | 历史 |
| `mem0 entity ...` | 实体 |
| `mem0 event ...` | 事件 |
| `mem0 config ...` | 配置 |
| `mem0 whoami` | 当前账号 |
| `mem0 identify` | 环境检测 |
| `mem0 agent-mode on/off` | Agent 模式 |
| `mem0 agent-rush ...` | 批量 |

> **命令完全对齐 Python CLI**——同一份用户文档,两边都能跑。

---

## 5. ⭐ Backend 抽象

```typescript
// cli/node/src/backend/base.ts（推断）
export interface Backend {
  ping(timeout?: number): Promise<Record<string, unknown>>;
  add(messages, opts?): Promise<Record<string, unknown>>;
  search(query, opts?): Promise<Record<string, unknown>>;
  // ... get/getAll/update/delete/deleteAll/history
}

// cli/node/src/backend/platform.ts
export class PlatformBackend implements Backend {
  constructor(apiKey: string, baseUrl: string) { ... }
  async ping(timeout?) { ... }
  // ...
}

// cli/node/src/backend/index.ts
export function getBackend(config: Mem0Config): Backend {
  if (config.platform.apiKey) {
    return new PlatformBackend(config.platform.apiKey, config.platform.baseUrl);
  }
  throw new Error("No backend configured");
}
```

> 跟 Python CLI 完全对应（但 TS 只有 Platform backend,没 OSS——因为 TS SDK 体积大,CLI 不内置）。

---

## 6. ⭐ `getBackendAndConfig` 流程

```typescript
async function getBackendAndConfig(
  apiKey?: string,
  baseUrl?: string,
): Promise<{ backend: Backend; config: Mem0Config }> {
  const config = loadConfig();

  if (apiKey) config.platform.apiKey = apiKey;
  if (baseUrl) config.platform.baseUrl = baseUrl;

  if (!config.platform.apiKey) {
    printError(
      "No API key configured.",
      "Run 'mem0 init' or set MEM0_API_KEY environment variable.",
    );
    process.exit(1);
  }

  const backend = getBackend(config);

  // Validate the API key upfront with 5s timeout
  try {
    const pingData = (await Promise.race([
      backend.ping(),
      new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error("timeout")), 5000),
      ),
    ])) as Record<string, unknown>;

    const email = pingData?.user_email as string | undefined;
    if (email) {
      _validatedUserEmail = email;
      if (config.platform.userEmail !== email) {
        config.platform.userEmail = email;
        try {
          saveConfig(config);
        } catch {
          /* ignore */
        }
      }
    }
  } catch (e) {
    if (e instanceof AuthError) {
      printError("Invalid or expired API key.", "Run 'mem0 init'...");
      process.exit(1);
    }
    printWarning("Could not validate API key (network issue). Proceeding anyway.");
  }

  return { backend, config };
}
```

> 跟 Python CLI 一致：先 load config → 验 API key → cache email。

---

## 7. ⭐ Agent 模式

```typescript
// state.ts
let _agentModeFlag = false;

export function isAgentMode(): boolean {
  return _agentModeFlag ||
    process.env.MEM0_AGENT_MODE === "1" ||
    // 检测 program options
    checkProgramAgentOpts();
}

export function setAgentMode(on: boolean) {
  _agentModeFlag = on;
}
```

### 检测 AI agent 环境（agent-detect.ts）

```typescript
// 看各种 env 变量
const AGENT_ENV_HINTS = [
  "CLAUDE_CODE",
  "CURSOR_TRACE_ID",
  "CODEX_TRACE_ID",
  // ...
];

export function detectAgentCaller(): string | undefined {
  for (const hint of AGENT_ENV_HINTS) {
    if (process.env[hint]) return mapHintToName(hint);
  }
  return undefined;
}
```

---

## 8. 工具链差异 vs Python CLI

| 维度 | Python CLI | Node CLI |
|------|-----------|---------|
| 框架 | Typer + Rich | Commander + Chalk + ora + cli-table3 |
| Lint | ruff（line 100） | Biome |
| Test | pytest | vitest |
| Build | hatch | tsup（ESM） |
| Backend 抽象 | Platform + OSS | Platform only |
| 同步/异步 | sync | 全 async |
| 异常美化 | Rich（默认禁用） | 简单 console.error |

---

## 9. 选哪个 CLI？

| 场景 | 推荐 |
|------|------|
| Python 用户 | Python CLI |
| Node 用户 | Node CLI |
| 同时用两个语言环境 | 任选（命令一样） |
| AI agent 集成 | 任选（都支持 agent mode） |
| 性能 | Node 略快（启动快） |

> README 推荐 `npm install -g @mem0/cli`（一行先说 npm,pip 是备选）。但功能完全对等。

---

## 10. 接下来

| 想看 | 去哪 |
|------|------|
| Python CLI | [`../06-cli-python/01-entry-and-commands.md`](../06-cli-python/01-entry-and-commands.md) |
| Hosted Platform | [`../00-overview/05-two-modes.md`](../00-overview/05-two-modes.md) |
| 编辑器集成 | [`../08-integrations/01-mem0-plugin.md`](../08-integrations/01-mem0-plugin.md) |

---

📌 **下一步** → [`../08-integrations/`](../08-integrations/) 6 个集成。
