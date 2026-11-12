# 示例插件（example-plugin）

JiuwenSwarm 官方参考插件：在一个插件包内同时演示 **skill（指导）/ tool（执行）/ rail（监听）** 三类能力组件的标准写法。它本身解决一个极小的真实场景——文本字数统计与会话轮次记录——所有代码保持最小可读，供插件开发者照抄结构。

## English

Official reference plugin for JiuwenSwarm. It demonstrates the standard layout of the three capability components — `skills/`, `tools/`, `rails/` — in one plugin package, around a tiny real scenario: text word counting and session turn tracking.

## 核心能力

- **usage-report（skill）**：接到「统计字数 / 生成使用报告」类请求时，指导智能体按固定工作流调用字数统计工具并输出结构化报告。
- **word_count（tool）**：纯函数式工具，入参 `text`，返回字符数、非空字符数、单词数、行数；无文件写入、无外部依赖。
- **turn_counter（rail）**：监听 `before_invoke` / `after_invoke` 生命周期钩子，在内存中累计当前会话的调用轮次。

## 组件协作

```
用户请求字数报告 ──► usage-report skill（工作流指导）
                        │ 调用
                        ▼
                  word_count tool（执行统计）
                        │ 返回结构化结果
                        ▼
                  智能体按 skill 模板输出报告

turn_counter rail（旁路）──► 每轮 invoke 前后自动计数，不参与内容生成
```

## 目录结构

```
example-plugin/
├── manifest.json                  # 插件包清单（组件声明 + 双语展示字段）
├── README.md                      # 本文件：详情页正文
├── skills/
│   └── usage-report/
│       └── SKILL.md               # 技能入口（frontmatter: name/description）
├── tools/
│   └── word_count_tool.py         # WordCountTool(Tool)
└── rails/
    └── turn_counter_rail.py       # TurnCounterRail(DeepAgentRail)
```

## 开发参考

- manifest 字段规范、tool / rail / skill 编写约束见仓库 [docs/plugin-spec.md](../../docs/plugin-spec.md)。
- 本包必须能通过 `python scripts/validate.py --only example-plugin`（L0 规范 / L1 静态 / L2 热加载三层校验）。
