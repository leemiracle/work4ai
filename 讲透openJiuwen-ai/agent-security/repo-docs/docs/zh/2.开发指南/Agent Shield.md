# Agent Shield

agent-shield（分发名 `agent-shield`，导入名 `agent_shield`）是进程内的判定 SDK。它做两件事：对一次工具调用给出 allow、ask 或 deny；对进入模型的内容给出风险信号。

---

## 1. 两个子模块

| 导入 | 目录 | 结果 |
| --- | --- | --- |
| `agent_shield.tool_permission` | `agent_shield/tool_permission/` | 确定性的 allow / ask / deny |
| `agent_shield.detection` | `agent_shield/detection/` | 风险级别和置信度。`is_safe` 为假表示检出风险，本包不据此中断调用 |

包根不导出名字。调用方从子模块根导入：

```python
from agent_shield.tool_permission import PermissionEngine
from agent_shield.detection import RuleBasedPromptInjectionBackend
```

`toolguard`、`fileguard`、`netguard`、`hostguard` 是 `tool_permission` 内部目录，不作为稳定导入路径。

## 2. 动作决策看什么

`PermissionEngine` 在一次工具调用上跑一组组件，取更严的结论。组件覆盖命令、路径、出站地址和分层工具策略。`enabled` 必须是布尔，缺省为真。设为假时，`check_permission` 直接返回 allow。

## 3. 安装与测试

```bash
cd agent_shield
pip install -e ".[dev]"
pytest
```

未安装 tree-sitter 时，命令解析使用保守扫描。

## 4. 组件与配置参考

更细的组件职责、配置项、剥壳/拆子命令与 `check_permission` 流程，见同目录 [Agent Shield组件与配置参考](Agent%20Shield组件与配置参考.html)（单页 HTML）。
