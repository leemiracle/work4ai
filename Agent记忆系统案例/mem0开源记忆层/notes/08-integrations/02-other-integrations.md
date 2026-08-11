# 02 — 其他 5 个集成（OpenClaw / Pi / Vercel AI / n8n / Zapier）

> 除了 `mem0-plugin`,Mem0 还有 5 个独立集成,各服务一个第三方平台。本篇对比各自定位、安装、能力。

---

## 1. 5 个集成对比

| 集成 | 包名 | 平台 | 用途 | npm 发布 |
|------|-----|------|------|---------|
| **openclaw** | `@mem0/openclaw-mem0` | OpenClaw agent | Long-term memory for OpenClaw | ✅ |
| **pi-agent-plugin** | `@mem0/pi-agent-plugin` | Pi Agent | Persistent semantic memory | ✅ |
| **vercel-ai-sdk** | `@mem0/vercel-ai-provider` | Vercel AI SDK | wrap Memory as AI SDK provider | ✅ |
| **n8n-nodes-mem0** | `@mem0/n8n-nodes-mem0` | n8n workflow | community node, workflow 里 add/search memory | ✅ |
| **zapier-mem0** | — | Zapier | Zap 步骤:add/search/get/delete | ❌（部署到 Zapier） |

---

## 2. ⭐ OpenClaw（`@mem0/openclaw-mem0`）

### 定位

> "Long-term memory for OpenClaw agents. Your agent forgets everything between sessions. This plugin fixes that."

OpenClaw 是个 AI agent 框架,本集成给它加跨会话记忆。

### 三种工作模式

| 模式 | 行为 |
|------|------|
| **Skills mode**（默认） | agent 控制何时记（triage）/如何回忆（recall）/定期清理（dream） |
| `autoRecall`（默认开） | 自动搜相关 memory 注入 |
| `autoCapture`（默认开） | 自动存对话 |

### 安装

```bash
openclaw --version  # >= 2026.4.25
openclaw mem0 init --api-key $MEM0_API_KEY --user-id <id>
```

### Quick path for agents

```bash
mem0 init --agent --json  # 拿 eval API key
openclaw mem0 init --api-key $MEM0_API_KEY --user-id <id>
```

---

## 3. ⭐ Pi Agent Plugin（`@mem0/pi-agent-plugin`）

### 定位

> "Persistent semantic memory for Pi Agent. Automatically captured from conversations."

Pi Agent 是 pi.dev 的 AI agent。

### 特性

- ✅ **自动 capture** —— 从 user + assistant 消息抽 memory
- ✅ **语义搜索** —— 按意思,不只关键词
- ✅ **Scoped memory** —— project / session / global 三层 scope
- ✅ **Monorepo-aware** —— 用 git root 检测项目,子目录共享 app_id
- ✅ **Dream consolidation** —— 合并重复、解决矛盾、清理过期
- ✅ **Confirmation dialogs** —— 危险操作前问
- ✅ **8 slash commands**
- ✅ **Agent tool** —— `mem0_memory` tool 让 agent 自主管理

### 安装

```bash
pi install npm:@mem0/pi-agent-plugin
```

---

## 4. ⭐ Vercel AI SDK Provider（`@mem0/vercel-ai-provider`）

### 定位

> "Wrap Mem0 as a Vercel AI SDK provider,让 Vercel AI 应用直接用 mem0。"

Vercel AI SDK 是个流行的 TS AI 框架。本集成让 `streamText` / `generateText` 等 API 自带 memory。

### 特性

- 🧠 持久 memory 存储
- 🔄 Vercel AI SDK 无缝集成
- 🚀 多 LLM provider 支持（通过 Vercel AI）
- 📝 Rich message 格式
- ⚡ 流式响应
- 🔍 上下文感知

### 安装

```bash
npm install @mem0/vercel-ai-provider
```

### 用法

```typescript
import { Mem0Provider } from '@mem0/vercel-ai-provider';
import { streamText } from 'ai';

const provider = new Mem0Provider({
  apiKey: process.env.MEM0_API_KEY,
  userId: 'alice',
});

const result = await streamText({
  model: provider,  // ⭐ 当 model 用
  messages: [{ role: 'user', content: 'Hi' }],
});
```

> Mem0 在背后自动 add + search memory。

---

## 5. ⭐ n8n Node（`@mem0/n8n-nodes-mem0`）

### 定位

n8n 是开源 workflow 自动化平台。本集成让 n8n workflow 能 add/search/update/delete memory。

### Operations

| Operation | Endpoint |
|-----------|---------|
| Add | `POST /v3/memories/add/` |
| Search | `POST /v3/memories/search/` |
| Get Many | `POST /v3/memories/` |
| Get | `GET /v1/memories/{id}/` |
| Update | `PUT /v1/memories/{id}/` |
| Delete | `DELETE /v1/memories/{id}/` |

### 异步 Add

> By default, Add runs LLM extraction asynchronously: API returns event ID,node polls until extraction finishes.

可选 "Wait for Completion" 让节点等。

### 安装

按 [community nodes installation guide](https://docs.n8n.io/integrations/community-nodes/installation/) 装 `@mem0/n8n-nodes-mem0`。

### Workflow 示例

```
[Trigger: Webhook] → [Mem0: Add Memory] → [Mem0: Search] → [OpenAI: Generate] → [Respond]
```

> 让 chat webhook 自动 capture + retrieve + respond。

---

## 6. ⭐ Zapier App（`integrations/zapier-mem0/`）

### 定位

[Zapier](https://zapier.com) 是商业 workflow 自动化。本集成让 Zap 操作 memory。

> ⚠️ Zapier app **不发布 npm**,部署到 Zapier 平台（用 Zapier Platform CLI）。

### Actions

| Type | Name | Endpoint |
|------|------|---------|
| Create | Add Memory | `POST /v3/memories/add/` |
| Create | Delete Memory | `DELETE /v1/memories/{id}/` |
| Search | Search Memories | `POST /v3/memories/search/` |
| Search | Get Memories | `POST /v3/memories/` |

### 异步 Add

> Add Memory runs LLM extraction asynchronously,returns event ID by default.
> Turn on "Wait for Completion" 让 action poll until done.
> 注意 timeout ≠ failure（Zapier 限制 step 时间,但服务端通常仍完成）。

### Authentication

Custom (API key):
```
Authorization: Token <key>
```

### 部署

```bash
cd integrations/zapier-mem0
pnpm install
pnpm build
zapier push  # 部署到 Zapier（需 ZAPIER_DEPLOY_KEY）
```

> Zapier app **不在 release router** —— 手动 dispatch `zapier-mem0-cd.yml`。

---

## 7. 5 个集成的差异

| 维度 | OpenClaw | Pi | Vercel AI | n8n | Zapier |
|------|---------|----|---------|-----|--------|
| 类型 | Agent plugin | Agent plugin | SDK provider | Workflow node | Workflow app |
| 运行环境 | OpenClaw runtime | Pi Agent runtime | Node.js | n8n server | Zapier cloud |
| 安装方式 | `openclaw install` | `pi install npm:` | `npm install` | n8n UI 装 | Zapier UI 装 |
| 发布到 | npm | npm | npm | npm | Zapier marketplace |
| 自动 capture | ✅ | ✅ | ✅ | ❌（workflow 触发） | ❌ |
| Slash commands | — | 8 个 | — | — | — |
| LLM provider | OpenClaw 选 | Pi 选 | Vercel AI 任选 | workflow 自定 | Zapier app 自定 |
| 开源 | ✅ | ✅ | ✅ | ✅ | ✅（代码）,Zapier 部署 binary |

---

## 8. 选哪个集成？

| 场景 | 推荐 |
|------|------|
| 用 Claude Code/Cursor/Codex | `mem0-plugin` |
| 用 OpenClaw | `openclaw-mem0` |
| 用 Pi Agent | `pi-agent-plugin` |
| 用 Vercel AI SDK | `vercel-ai-provider` |
| 用 n8n 自动化 | `n8n-nodes-mem0` |
| 用 Zapier | `zapier-mem0` |
| 都不用,自己写 | `mem0ai` SDK 直接调 |

---

## 9. 共同点

所有 5 个集成：

1. **都需要 Mem0 API key**（从 app.mem0.ai 拿）
2. **都走 HTTPS 到 Mem0 Platform**（或自托管 server）
3. **都不在本地存 memory**（数据在 Mem0）
4. **都支持 add + search + get + delete**
5. **都是 Apache-2.0**

---

## 10. 加新集成的步骤

如果要加新的第三方集成（比如 LangChain / AutoGen 等）：

1. `integrations/<name>/` 建独立目录
2. `package.json`（如果是 npm 包）,设 `repository.directory`
3. 写代码（继承 `MemoryClient` 或直接 HTTP）
4. `.github/workflows/<name>-checks.yml` + `.github/workflows/<name>-cd.yml`
5. 注册到 `ci-gate.yml`（filter + call job + gate.needs）
6. 注册到 `release.yml`（tag prefix case）
7. 文档 `docs/integrations/<name>.mdx` + `docs/llms.txt`
8. 更新 `AGENTS.md`

详见 [`../00-overview/04-cicd.md`](../00-overview/04-cicd.md) §8。

---

## 11. 接下来

| 想看 | 去哪 |
|------|------|
| mem0-plugin（最大集成） | [`01-mem0-plugin.md`](./01-mem0-plugin.md) |
| Skills 系统 | [`../09-skills/01-skills-overview.md`](../09-skills/01-skills-overview.md) |
| 加新 provider / integration | [`../00-overview/01-repo-layout.md`](../00-overview/01-repo-layout.md) §9 |

---

📌 **下一步** → [`../09-skills/`](../09-skills/) 6 个 skill。
