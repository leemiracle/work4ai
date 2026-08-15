# mermaid-render

把 markdown 里的 ` ```mermaid ` 代码块批量渲染成 PNG 图片。语法错的块会报错并打印源码，方便定位。

## 安装（仅首次）

```bash
cd ~/ai/work4ai/mermaid-render
npm install @mermaid-js/mermaid-cli    # 装 mermaid-cli (puppeteer 会自动下 chrome, 本机用不上)
```

前提：Node.js ≥ 18、Python 3、系统 chromium。本机 chromium 在 `/usr/bin/chromium-browser`（aarch64 原生），已通过 `puppeteerConfig.json` 指定——**不要让 puppeteer 用它自己下的 chrome**（那是 x86_64 的，在 ARM 上跑不了，会报 `libglib-2.0.so.0` 缺失）。换机器时改 `puppeteerConfig.json` 里的 `executablePath`。

## 用法

```bash
# 单个文件 — 图输出到 md 同级的 assets/
bash render_mmd.sh notes/00-overview/02-architecture.md

# 单个文件 — 指定输出目录
bash render_mmd.sh notes/00-overview/02-architecture.md out/png/

# 整个目录递归 — 每个 md 的图各自进同级的 assets/
bash render_mmd.sh notes/

# 整个目录 — 全部图集中到一个目录
bash render_mmd.sh notes/ out/all-png/
```

输出命名：`<md文件名>-<两位序号>.png`，如 `02-architecture-03.png`（按 mermaid 块在 md 里出现的顺序编号）。

## 文件

| 文件 | 作用 |
|------|------|
| `render_mmd.sh` | 主入口：提取 mermaid 块 → 逐个渲染 PNG，失败的打印源码 |
| `extract_mermaid.py` | 从 md 抽 ` ```mermaid ` 块到独立 `.mmd` 文件 |
| `puppeteerConfig.json` | 让 mmdc 用系统 chromium（含 `--no-sandbox` 等 ARM 必需参数） |

## 已知陷阱：节点 label 里的括号

`graph`/`flowchart` 里，节点 label **方括号内出现裸 `(` 会被解析器误判为圆柱形节点 `[(...)]` 语法的起点**，导致 `Parser.parseError`：

```mermaid
graph TD
    A[foo max(k*4, 60)]   ✗ 整图渲染失败
    B["foo max(k*4, 60)"] ✓ 给 label 加双引号即可
```

规则：label 里含 `( ) : ;` 等特殊字符时，**一律用双引号包裹** `A["..."]`。`sequenceDiagram` 的 message 文本不受此限制（自由文本，可有 `:` 和 `()`）。
