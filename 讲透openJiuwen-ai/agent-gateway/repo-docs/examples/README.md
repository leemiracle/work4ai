# 示例

本目录提供可直接运行的 Agent Gateway 示例。每个示例目录都有独立 README，说明运行命令与预期输出。

| 示例 | 用途 | 依赖 |
| --- | --- | --- |
| [mock-agent-server](mock-agent-server/) | 用 Mock AgentServer 模拟下游，验证 Gateway 启动与 `/tui` 路由的完整往返 | 仅本仓依赖，无需模型配置 |

## 使用方式

在仓库根目录执行（确保已完成 `uv sync`）：

```bash
uv run python examples/mock-agent-server/mock_agent_server.py 19501
```

完整的上下游启动与验证步骤见[快速开始](../docs/zh/tutorial/01-quick-start.md)或[本地功能验证](../docs/zh/how-to/local-validation.md)。
