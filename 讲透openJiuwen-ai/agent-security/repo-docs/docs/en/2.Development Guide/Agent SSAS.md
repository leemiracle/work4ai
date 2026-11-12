# Agent SSAS

Agent SSAS (package `agent-ssas`, import name `agent_ssas`) collects agent runtime events, runs threat detection, and stores the result as an OCSF log. It is not tied to one agent framework. The current JiuwenSwarm integration is a security rail.

The component's own documentation is [agent_ssas/docs/README.md](../../../agent_ssas/docs/README.md): tutorials, how-to guides, configuration reference, and architecture notes. This page only places it inside the repository.

---

## 1. Two subsystems

| Subsystem | Package path | Role |
| --- | --- | --- |
| AgentSSASCore | `agent_ssas.core` | Detection engine: preprocessing, analysis pipeline, detection modules, storage, OCSF output |
| AgentSSASClient | `agent_ssas.backend_client` | Collects events and reports them. The openjiuwen client's main class is `AgentSSASSecurityRail` |

The detection engine can be embedded in any Python process. Only the JiuwenSwarm client depends on an agent runtime.

## 2. Runtime modes

| Mode | Behavior |
| --- | --- |
| `inprocess` | Default. Detection runs in the same process |
| `http` | A standalone FastAPI service shared by several agents |

`observe_only` records and allows every call. `active_protection` blocks critical findings and warns on the rest. A failure inside the detection engine does not stop the caller.

Built-in detection modules include `agent_moss` and `security_rail_detection`. `test_detection` is off by default. A new module is declared with `module.yaml` and does not require a framework change.

## 3. Continue here

| Goal | Document |
| --- | --- |
| Concepts | `agent_ssas/docs/en/tutorial/01-introduction.md` |
| In-process loop | `agent_ssas/docs/en/tutorial/02-quickstart.md` |
| JiuwenSwarm integration | `agent_ssas/docs/en/tutorial/03-integrate-jiuwenswarm.md` |
| Configuration fields | `agent_ssas/docs/en/reference/configuration.md` |

Examples are in `agent_ssas/examples/`. The JiuwenSwarm integration patches are in `agent_ssas/patches/`.
