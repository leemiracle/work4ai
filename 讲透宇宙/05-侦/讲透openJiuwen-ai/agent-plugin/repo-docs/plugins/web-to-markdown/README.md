# 网页转 Markdown 笔记（web-to-markdown）

抓取网页正文并转换为结构化的 Markdown 笔记：输入一个 URL，输出干净的 Markdown 文本（标题 + 正文），方便保存到知识库或笔记应用。核心能力由 `web_to_markdown` 工具完成，`web-to-markdown` 技能负责指导输出成笔记。

## English

Fetch a web page's main content and convert it into clean, structured Markdown notes. The `web_to_markdown` tool does the fetching and conversion; the `web-to-markdown` skill guides the agent to present the result as a note.

## 核心能力

- **web-to-markdown（skill）**：接到「把网页 / 链接转成 Markdown 笔记」类请求时，指导智能体调用转换工具并把结果组织成笔记（标题 + 正文），按需保存为 `.md` 文件。
- **web_to_markdown（tool）**：纯标准库实现（`urllib` + `html.parser`），入参 `url`，抓取网页正文并转换为 Markdown；不写文件、不注入运行时对象、无第三方依赖。

## 组件协作

```
用户给 URL ──► web-to-markdown skill（工作流指导）
                  │ 调用
                  ▼
            web_to_markdown tool（抓取 + 转 Markdown）
                  │ 返回 {title, markdown}
                  ▼
            智能体按 skill 模板输出笔记（可选保存 .md）
```

## 目录结构

```
web-to-markdown/
├── manifest.json                     # 插件包清单（组件声明 + 双语展示字段）
├── README.md                         # 本文件：详情页正文
├── skills/
│   └── web-to-markdown/
│       └── SKILL.md                  # 技能入口（frontmatter: name/description）
└── tools/
    └── web_to_markdown_tool.py       # WebToMarkdownTool(Tool)
```

## 依赖与安全

- 纯标准库实现，无第三方依赖；抓取仅在 `invoke` 内联网，`import` 期无副作用。
- 工具只返回 Markdown 文本，不写文件；文件保存由智能体按技能指导完成。
- 网页无正文或抓取失败时返回 `success=false` 与明确错误，不会用空内容冒充产物。

## 开发参考

- 插件包规范见仓库 [docs/plugin-spec.md](../../docs/plugin-spec.md)。
- 本包必须能通过 `python scripts/validate.py --only web-to-markdown`（L0 规范 / L1 静态 / L2 热加载三层校验）。
