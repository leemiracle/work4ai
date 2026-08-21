# steel-browser 深读卡 —— 给 AI Agent 用的云浏览器 API：CDP 全控 + 会话状态 + 反检测 + 代理链

> **定位**：Steel（后并入 Sidebar）出品的开源浏览器 API——AI Agent/应用与 Web 程序化交互的基础设施：管会话/进程/反检测，开发者只管业务逻辑。基于 **CDP（Chrome DevTools Protocol）+ Puppeteer**，REST+WebSocket 接口，会话状态（cookies/localStorage）跨请求保持，内置代理链 IP 轮换+stealth 插件+指纹管理，兼容 Playwright/Selenium。
> **本地**：`repos/steel-browser`（steel-dev/steel-browser）｜**深读**：deepwiki 55 子页归档 `deepwiki/steel-browser/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 浏览器控制 | CDP 全控 | `puppeteer-core`、`CDPService` |
| 会话管理 | 状态跨请求保持 | `SessionService`（cookies/localStorage/state） |
| 代理 | IP 轮换 | `proxy-chain`、`ProxyFactory` |
| 反检测 | stealth+指纹 | `fingerprint-generator`、`fingerprint-injector`、stealth plugins |
| 工具层 | 页面→工具转换 | browser tools APIs |
| 接口 | REST+WebSocket | 会话化 API |

## 二、核心机制

1. **会话即浏览器上下文**：每个 session 独立浏览器上下文（指纹+代理+存储全隔离）——多 agent 并行浏览互不串扰的托管化（对比本地 invisible-playwright：Steel 是云托管版）。
2. **指纹 JS 注入派**：fingerprint-injector 在页面注入一致指纹——与 invisible-playwright 的引擎级补丁相对（轻但可被高级检测识破），两派对照即"反检测工程光谱"。
3. **proxy-chain 轮换**：内置代理链管理——爬虫/多账号场景的 IP 基建。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| 会话化浏览器 | 讲透Agent/02 §浏览器工具（云托管路线） |
| 指纹注入 vs 引擎补丁 | invisible-playwright 对照（反检测光谱） |
| CDP | 浏览器自动化协议层 |

## 四、关键入口

```
（monorepo：SessionService/CDPService/ProxyFactory 等核心服务，详见 wiki 1.3 结构页）
```

## 五、深读子页地图（55 页精选 5）

Overview｜System Architecture｜Key Features｜Monorepo Structure｜Session/反检测实现页。

## 六、与"我们"的关系（一句话）

浏览器 Agent 基础设施"云派"代表——与 invisible-playwright（本地引擎派）/actionbook（知识沉淀派）三足讲全"Agent×浏览器"路线图。

---
生成：2026-08-21 · deepwiki 55 页全归档
