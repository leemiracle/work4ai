# Repository and install

The repository root has no single install entry. Each component has its own `pyproject` and is installed from its own directory.

---

## 1. Environment

All three components require Python 3.11 or newer.

| Component | Extra requirements |
| --- | --- |
| Agent SSAS | HTTP mode needs fastapi, uvicorn, and httpx. It runs on Windows, Linux, and macOS |
| JiuwenBox | Linux needs bubblewrap. Network isolation also needs iproute2, iptables, and nftables |
| agent-shield | No third-party packages at runtime. Tests can use tree-sitter for command parsing |

## 2. Local install

From the repository root, enter each component directory.

Agent SSAS:

```bash
cd agent_ssas
uv venv
uv pip install -e .
uv pip install -e ".[http]"
```

JiuwenBox build and start commands are in [jiuwenbox/README.md](../../../jiuwenbox/README.md). Sample policies are in `jiuwenbox/src/jiuwenbox/configs/`.

agent-shield:

```bash
cd agent_shield
pip install -e ".[dev]"
pytest
```

## 3. Where to go next

| Component | In-repo document |
| --- | --- |
| Agent SSAS | [Agent SSAS](Agent%20SSAS.md). The full tutorial set is `agent_ssas/docs/README.md` |
| JiuwenBox | [JiuwenBox](JiuwenBox.md). API and deployment notes are in `jiuwenbox/README.md` |
| agent-shield | [Agent Shield](Agent%20Shield.md) |
