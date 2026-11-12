# 讲透 NeMo-Agent-Toolkit-UI

> NVIDIA NeMo Agent Toolkit 的聊天前端：Next.js/React18 + **双服务器架构**（3000 proxy 网关+3099 内部 Next，开发/生产同构双进程）+ WebSocket HITL + Markdown 流式渲染 + 安全防线三件套。

## 全链状态表

| 阶段 | 状态 | 产出 |
|---|---|---|
| understand 图谱 | ✅ 2026-11-11 | 仓内 `.understand-anything/knowledge-graph.json`：**281n/507e/14 层/14 步 tour**，双 validate 0/0，fingerprints 164@41cb8cf8 |
| onboarding | ✅ 2026-11-11 | `onboarding/ONBOARDING.md`（8 节 6481 字不计空格，52 锚） |
| explain 6 篇 | ✅ 2026-11-11 | `explain/01-06` 合计 **18809 字符**，236 锚（主会话抽验 5/5 命中） |

## 战况（14 批，双段 worker）

批 worker 自检修复校验脚本前缀误报 2 处后全绿；imports 196 条 scanner 1:1 + 8 条源码重扫补发（6 个 index.ts 桶文件+两级路由链 scanner 漏）；tested_by 21 条。

## 甄别精选（源码级实证）

1. **双服务器架构勘误**：图谱批笔记曾记"生产走 next.config rewrites 不跑 proxy 网关"——实证 `next.config.js` 零 rewrites，`Dockerfile:81-83` CMD 用 concurrently 同起 standalone Next@3099 + proxy/server.js@3000，开发/生产**同构双进程**
2. **流内标签私有协议**：`<intermediatestep>/<observabilitytraceid>` 由 server 端 response-processors 注入、Chat.tsx 剥离——消费者不可见的遥测通道
3. **双套 WS 平行类型的真险点**：types/chat.ts:64 `'error'` vs types/websocket.ts:61 `'error_message'` 字面量漂移；且 next.config.js:14 `ignoreBuildErrors:true` 关掉编译期门禁，只剩 CI typecheck 兜底
4. **死代码**：Chat.tsx:1244 `if (!false)` 恒真——非流式分支（1523-1556）不可达
5. **i18n 骨架空转**：next-i18next 声明 22 语言，磁盘仅 `public/locales/en/common.json` 且内容为 `{}`，t() 全部回落键名
6. 安全防线三件套：SSRF/原型污染/开放重定向双层校验；OAuth redirect/popup 双模式含取消守卫防循环
7. Chat.streaming-edge-cases.test 零项目导入（本地复刻算法守护契约）；AgentAvatar/SystemAvatar 动态 Tailwind 类不生效
8. compose service 子节点（`:sandbox-agent` 等）filePath 与父 yaml 相同——layers 必须按 node id 归层（新坑钉版）

## 分层速览（14 层，164 文件节点）

构建与容器化(13) → GitHub 治理/CI(11) → Proxy 网关(3) → API 路由(3) → 应用入口与全局状态(9) → 聊天核心(11) → Markdown 引擎(9) → 会话侧栏(16) → 通用组件(15) → Hooks/常量/工具(18) → 安全防线(6) → 类型(9) → 测试(19) → i18n/资源/文档(22)

*2026-11-11 · cuda-stack-第七轮会话（舰队夜战 · NeMo-Toolkit 三连之二）*
