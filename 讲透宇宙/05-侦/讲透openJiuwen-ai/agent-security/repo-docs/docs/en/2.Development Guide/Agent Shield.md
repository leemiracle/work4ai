# Agent Shield

agent-shield (distribution name `agent-shield`, import name `agent_shield`) is the in-process decision SDK. It does two things: it returns allow, ask, or deny for one tool call, and it returns a risk signal for content that is about to reach a model.

---

## 1. Two submodules

| Import | Directory | Result |
| --- | --- | --- |
| `agent_shield.tool_permission` | `agent_shield/tool_permission/` | A deterministic allow / ask / deny |
| `agent_shield.detection` | `agent_shield/detection/` | A risk level and a confidence. `is_safe` false means a risk was found. This package does not stop the call from that flag |

The package root exports nothing. Import from a submodule root:

```python
from agent_shield.tool_permission import PermissionEngine
from agent_shield.detection import RuleBasedPromptInjectionBackend
```

`toolguard`, `fileguard`, `netguard`, and `hostguard` are directories inside `tool_permission`. They are not a stable import path.

## 2. What an action decision covers

`PermissionEngine` runs a set of components on one tool call and keeps the stricter result. The components cover commands, paths, outbound addresses, and tiered tool policy. `enabled` must be a boolean and defaults to true. When it is false, `check_permission` returns allow.

## 3. Install and test

```bash
cd agent_shield
pip install -e ".[dev]"
pytest
```

Without tree-sitter, command parsing uses the conservative scanner.
