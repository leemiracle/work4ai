# JiuwenSwarm Agent Plugin

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](./LICENSE)

JiuwenSwarm（九问蜂群）**官方 plugin 插件包集合仓**：对应 Hub 市场资产类型
`agent-plugin`，为智能体提供**技能（skill）/ 工具（tool）/ 生命周期钩子（rail）**
三类能力扩展的一站式内容源。

- Hub 在线安装：扩展中心 → 搜索 / 安装本仓发布的插件
- 产品内置：旗舰插件随 jiuwenswarm `built_in` 目录分发
- 开发者直装：把 `plugins/<name>/` 拷贝到 `~/.jiuwenswarm/agent/workspace/plugins/plugin_packages/local/`

> English overview: [README_EN.md](./README_EN.md)

## 插件目录

<!-- catalog:begin -->
| 插件 | 版本 | 分类 | 能力组成 | 简介 |
| --- | --- | --- | --- | --- |
| [example-plugin](./plugins/example-plugin) | 1.0.0 | Engineering | 1 skill + 1 tool + 1 rail | 官方参考插件：用 skill 指导、tool 执行、rail 监听三类组件演示插件包的标准写法。 |
| [web-to-markdown](./plugins/web-to-markdown) | 1.0.0 | Engineering | 1 skill + 1 tool | 把网页正文抓取并转换为结构化 Markdown 笔记，支持保存与二次编辑，适合知识整理与收藏归档。 |
<!-- catalog:end -->

> 上表由 `python scripts/catalog.py` 生成，请勿手改。

## 仓库结构

```
agent-plugin/
├── plugins/                  # 插件包实体（扁平一层，一包一目录；内容 = 用户拿到的内容）
├── templates/plugin-template/   # 脚手架模板（scripts/init.py 消费）
├── scripts/                  # 工具链：init / validate / catalog / build / publish / sync_builtin
├── catalog/catalog.json      # 生成物：插件目录清单（lockfile 式）
├── docs/                     # 插件包规范、发布流程、仓库设计文档
└── tests/                    # 工具链单测 + 各插件行为测试（不随包分发）
```

## 快速开始（开发一个插件）

```bash
# 1. 生成骨架（可选预置组件）
python scripts/init.py my-plugin --skill usage-guide --tool counter

# 2. 填充 manifest.json / README.md / 组件内容，消灭全部 [TODO]
#    规范见 docs/plugin-spec.md

# 3. 三层校验（L0 规范 / L1 静态 / L2 热加载，L2 需 jiuwenswarm 运行环境）
python scripts/validate.py --only my-plugin

# 4. 更新目录清单并提交 PR（PR 质量门禁见 .github/workflows/pr-quality.yml）
python scripts/catalog.py
```

完整贡献流程与安全审查要求见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

## 文档

- [插件包规范（manifest / skill / tool / rail）](./docs/plugin-spec.md) — 权威来源
- [Hub 发布流程](./docs/hub-publish.md)
- [PR 安全审查清单](./docs/review-checklist.md)
- [仓库结构设计](./docs/design/repo-structure-design.md)

## 许可证

[Apache-2.0](./LICENSE) © Huawei Technologies Co., Ltd.
