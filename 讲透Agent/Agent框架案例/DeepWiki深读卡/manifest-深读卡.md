# manifest 深读卡 —— 面向个人 AI Agent 的自托管 LLM 智能路由网关：23 维打分自动分层选模省钱

> **定位**：Manifest 是 Manifold 出品、面向个人 AI Agent（OpenClaw/Claude Code/Hermes/各类 SDK）的智能 LLM 路由器——Agent 把 baseURL 指过来、模型填 `manifest/auto`，它用 23 维评分引擎把每条请求分级路由到"最便宜且够用"的模型，宣称最多省 70% 推理成本。核心差异化：不用 LLM 做 LLM 路由（纯启发式、零额外推理开销）+ 可复用 ChatGPT Plus/Claude Pro/Copilot 等包月订阅当 API 额度 + 自托管 Docker 全栈（NestJS+SolidJS+PostgreSQL 16）。注意：**并非通用 backend-as-a-service**（无存储/文件 API），本质是 OpenAI/Anthropic 双协议兼容的 LLM API 网关。
> **本地**：`repos/manifest`（mnfst/manifest）｜**深读**：deepwiki 33 子页归档 `deepwiki/manifest/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 接入层 | OpenAI 兼容 `/v1/chat/completions`、`/v1/responses` + Anthropic 兼容 `/v1/messages`；限流/并发槽 | ProxyController, ProxyRateLimiter, AgentKeyAuthGuard |
| 决策层 | 23 维评分 → 四 Tier（simple/standard/complex/reasoning） | scoreRequest, KeywordTrie, specificity-detector |
| 解析层 | Tier → 模型路由与凭证解密（AES-256-GCM） | ResolveService, ProviderKeyService, ModelRoute |
| 执行层 | 转发 + fallback 链 + 凭证轮换 + 错误脱敏 | ProxyFallbackService, shouldTriggerFallback |
| 供给层 | Provider/OAuth 订阅管理、模型发现、价格同步（models.dev）、免费模型 | UserProvider, PricingSyncService, TierAutoAssignService |
| 观测层 | token/成本记录、OTLP 摄取、SSE 实时 dashboard | AgentMessage, ProxyMessageRecorder, IngestEventBusService |
| 管控层 | 预算硬上限 + 定时邮件告警 | LimitCheckService, NotificationCronService |
| 持久层 | PostgreSQL 16 + TypeORM 多租户实体 + Better Auth 会话 | Tenant/Agent/AgentApiKey, setup wizard |

## 二、核心机制

1. **23 维评分引擎：不烧 token 的"模型调度器"（Scoring Engine 页）**——Aho-Corasick 式 `KeywordTrie` 单遍扫关键词 + 结构维度（token 数/工具数/对话深度/代码占比/约束密度），sigmoid 归一化映射四 Tier；<50 字符短消息走 fast path 直接 simple，"prove that"类触发 formal-logic 强制 Reasoning。创新本质：与 LiteLLM/OpenRouter 的"静态规则或 LLM-as-router"不同，它用纯启发式做实时复杂度分类，路由零成本、零延迟加成。
2. **`manifest/auto` 虚拟模型 + 订阅复用（Agent Integration / Provider Management 页）**——Agent 侧零改造（只改 baseURL+model 名），双协议兼容；上游凭证支持 `api_key` 与 `subscription`（ChatGPT Plus/Claude Pro/GitHub Copilot 的 OAuth/设备流）双轨，把包月订阅变成 Agent 可耗的额度——这是对 OpenRouter 纯按量计费模式的最大差异点。
3. **为真实 Agent 流量打磨的"净化"细节（Scoring Engine 页）**——`peelEnvelope` 剥离 OpenClaw 等塞进消息的 JSON/YAML 元数据包裹（防止短指令被信封误判成复杂任务）；session momentum 向近期 Tier 收敛防止对话中途跳模型；system/developer 角色不计分防止大 system prompt 灌水。评分引擎读的是"人话"，不是 Agent 的信封。
4. **生产级韧性链（Fallback and Resilience / Security Hardening 页）**——429/5xx 触发 `fallback_routes` 依序迭代 + 同模型内凭证轮换（api_key↔subscription）+ 传输错误合成 503 + `proxy-error-sanitizer` 脱敏防上游 key 回显；配套 SSRF URL 校验、mnfst_* key scrypt 哈希入库、自托管模式 loopback 免钥。

## 三、与讲透系列的对位

| manifest 概念 | 讲透Agent/多Agent协作/学习型Agent 对应概念 |
|---|---|
| `manifest/auto` 动态选模 | 模型选型外置：Agent 不写死模型，"模型即可调度资源"（对比讲透Agent 的模型调用层） |
| 23 维请求画像 + specificity 检测 | 上下文工程（复杂度感知路由），反向教材：零 LLM 参与的特征工程 |
| session momentum | 记忆机制（会话级短期记忆防抖，类比"粘性"路由） |
| fallback 链 + 凭证轮换 | 工具调用容错/重试模式的网关版 |
| SpecificityPenaltyService（用户纠错→类别降权） | 自进化的最小反馈闭环（人工反馈驱动，非学习型） |
| 预算硬限/OTLP/SSE 观测 | 安全沙盒（资源限额）+ Agent 可观测性 |

## 四、关键入口

```
packages/backend/src/routing/proxy/proxy.controller.ts      # /v1/* 三协议入口，acquireSlot/releaseSlot 并发控制
packages/backend/src/routing/proxy/proxy.service.ts         # 主编排：resolve → 解密凭证 → 转发 → fallback
packages/backend/src/scoring/index.ts                       # scoreRequest：23 维打分主函数
packages/backend/src/scoring/envelope-peeler.ts             # 剥 Agent 元数据信封，评"人话"不评"包装"
packages/backend/src/scoring/specificity-signals.ts         # URL/代码围栏/工具名信号 → CODING/WEB_BROWSING 等任务类型
packages/backend/src/routing/proxy/proxy-fallback.service.ts # fallback 迭代 + 凭证轮换 shouldTriggerFallback
packages/backend/src/routing/resolve/resolve.service.ts     # Tier → ModelRoute 解析（含 fallback_routes）
packages/backend/src/otlp/services/api-key.service.ts       # mnfst_* key 生成，scrypt 哈希，租户/Agent 初始化
```

## 五、深读子页地图（33 页精选 6）

1. **Scoring Engine（10）**——全仓智力核心：23 维→四 Tier 完整决策管线，特征工程教科书
2. **Proxy Pipeline（11）**——三协议翻译/限流并发/思考签名缓存/消息记录
3. **Fallback and Resilience（12）**——容错范式：fallback 链、凭证轮换、错误脱敏
4. **Provider Management（13）**——OAuth 订阅流复用包月额度 + SSRF 防护，最差异化的一页
5. **Agent Integration（7）**——`manifest/auto` 接入 8 类 Agent/SDK 的零改造模式
6. **Notifications and Alerts（21）**——预算硬限 + React Email 模板定时告警

## 六、与"我们"的关系（一句话）

对学 Agent 的人，它是"Agent 之下一层"的完整工程范本——把模型选型、容错、成本、观测做成独立基础设施，且评分引擎本身就是一份可运行的"请求复杂度特征工程"实战教材。

---
生成：2026-08-21 · deepwiki 33 页全归档
