# 09 · 通用应用结构分析方法

> 分析 Electron / VS Code Fork / Node 应用的通用方法。本文档**不包含任何针对特定商业产品的解包命令或结果**——只讲通用工具链和分析流程。

---

## 一、为什么需要"应用结构分析"

做 Agent 产品的架构调研时，常需要理解已有产品的架构模式。对**闭源商业应用**，无法直接读源码，需要通过**解包 + 结构分析**推断架构。对**开源应用**，可直接读源码。

> ⚠️ **本文档只讲通用方法**。所有分析应限于"理解架构模式"（用于借鉴设计），不涉及绕过许可/破解/ redistribute 他人二进制。开源产品直接读源码；闭源产品的分析以公开可获取的安装包结构为限。

---

## 二、通用工具链（全部为公开工具）

### Linux deb 包结构分析

| 任务 | 工具 |
|---|---|
| 解包 deb | `ar x package.deb` |
| 解压 data | `tar -xf data.tar.xz` |
| 查看文件树 | `find usr/ -type f` |

### macOS DMG 结构分析

| 任务 | 工具 |
|---|---|
| DMG → raw image | `dmg2img` |
| raw image 解压 | `7z x` 或 APFS 工具 |
| APFS image 挂载 | `fsapfsmount`（libfsapfs-utils）|

### Electron asar 解包

| 任务 | 工具 |
|---|---|
| asar extract | `npx @electron/asar extract app.asar out/` |
| 重新打包 | `npx @electron/asar pack in/ app.asar` |

### webpack bundle 分析

| 任务 | 工具 |
|---|---|
| 字符串提取 | `strings bundle.js | grep -i <keyword>` |
| 类名/字段提取 | Python 正则 |
| 模块边界识别 | `grep "webpackChunk"` 等 |

### Protobuf schema 提取

| 任务 | 工具 |
|---|---|
| typeName 提取 | `grep -oE '"\.\w+\.\w+"' bundle.js \| sort -u` |
| schema 还原 | 手工从 typeName 推断 message 结构 |

### TypeScript 源码阅读（开源产品）

直接 `git clone` 或读本地仓库，用 ripgrep / ast-grep 搜模式。

---

## 三、通用分析流程

```
1. 确定应用打包格式
   ├─ Linux: deb / appimage / snap
   ├─ macOS: dmg / app bundle
   └─ 开源: git 仓库

2. 解包到文件层（用上面对应工具）

3. 定位 AI 相关模块
   ├─ VS Code Fork: extensions/ 目录下的 AI extension
   ├─ Electron app: main 进程的 webpack bundle
   └─ 开源: packages/ 或 src/ 目录

4. 提取架构模式（核心）
   ├─ 进程模型: 单进程 / 多进程 / daemon
   ├─ 协议设计: JSON RPC / Protobuf / 自有协议
   ├─ Agent Loop: 单层 / 双层 / 死循环恢复
   ├─ 扩展机制: extension / plugin / skill / MCP
   ├─ 安全模型: 沙箱 / 权限 / attribution / hooks
   └─ 持久化: SQLite / 文件 / 云端

5. 与公开实现交叉验证
   ├─ 对照开源项目（同形态）
   ├─ 对照技术博客 / 论文
   └─ 对照产品公开文档
```

---

## 四、Electron / VS Code Fork 应用的通用结构

### Electron app 通用结构

```
App.app/ (或 linux 的 /usr/lib/app/)
├── Contents/  (macOS)
│   ├── Info.plist              ← 元数据（Bundle ID / 签名 / URL scheme）
│   ├── MacOS/
│   │   └── Electron            ← 启动器
│   └── Resources/
│       ├── app.asar            ← ★ 主代码（webpack bundle 打包）
│       ├── native modules      ← .node 原生模块
│       └── assets              ← 图标 / 模板 / 配置
```

### VS Code Fork 通用结构

```
VSCode-Fork/
├── resources/
│   └── app/
│       ├── product.json        ← ★ 产品配置（feature 开关 / 扩展 / 路径）
│       ├── out/                ← 编译产物（main.js / renderer）
│       └── extensions/         ← ★ AI extension 所在
└── package.json
```

**AI 模块化的两种风格**（见 [00-overview](./00-overview.md)）：
- **集中式**（IDE-A 风格）：所有 AI 塞进单一大型 extension bundle
- **模块化**（IDE-B 风格）：AI 拆成多个独立 extension（agent-exec / retrieval / mcp 等）

---

## 五、minified bundle 的通用分析技巧

闭源 Electron 应用的 bundle 通常是 webpack minified（变量名混淆）。通用分析技巧：

1. **`strings` + 关键词 grep**：搜 `Agent` / `Tool` / `MCP` / `Protobuf` / `permission` 等领域词
2. **类名/字段名提取**：minified 通常保留字符串字面量（类名 / typeName / 字段名）——用 Python 正则提取
3. **typeName 推断 schema**：Protobuf 的 typeName（如 `agent.v1.ToolCall`）能反推 message 结构
4. **import 边界识别**：`webpackChunk` / `__webpack_require__` 标记模块边界
5. **不要试图反混淆全部代码**——只提取架构相关的类名/字段名/协议名

---

## 六、方法学声明

- 本文档只讲**通用的、公开的**应用结构分析方法
- 所有工具（ar / tar / dmg2img / asar / strings / grep）都是公开标准工具
- 分析目的限于**理解架构模式**（用于设计借鉴）
- **不涉及**绕过软件许可 / 破解 license / redistribute 他人二进制
- 开源产品（如本调研的 CLI/TUI 框架、多渠道网关形态）直接读源码即可，无需解包

---

## 下一步
- 回到架构模式 → [`00-overview.md`](./00-overview.md)
- 做选型决策 → [`08-blueprint.md`](./08-blueprint.md)
