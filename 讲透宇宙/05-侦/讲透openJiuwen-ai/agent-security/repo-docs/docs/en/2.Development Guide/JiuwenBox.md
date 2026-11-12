# JiuwenBox

JiuwenBox (package `jiuwenbox`) is the sandbox service. A FastAPI process manages sandbox create and stop, file transfer, and command execution. A policy file decides the isolation, and the service applies that policy inside its own process.

Install, startup flags, and the HTTP API are specified in [jiuwenbox/README.md](../../../jiuwenbox/README.md).

---

## 1. Layout

| Directory | Role |
| --- | --- |
| `jiuwenbox/src/jiuwenbox/server` | Service: lifetime, policy loading, audit, routes |
| `jiuwenbox/src/jiuwenbox/supervisor` | Turns a policy into isolation controls |
| `jiuwenbox/src/jiuwenbox/models` | Models for policies, sandboxes, and API payloads |
| `jiuwenbox/src/jiuwenbox/proxy` | Inference privacy proxy for routing and key injection |
| `jiuwenbox/src/jiuwenbox/configs` | Policies shipped with the package |

The samples are `default-policy.yaml`, `code-agent-policy.yaml`, `enterprise-policy.yaml`, `inference-policy.yaml`, `java-policy.yaml`, and `windows-policy.yaml`. When `JIUWENBOX_POLICY_PATH` is unset, the service uses the packaged `default-policy.yaml`.

## 2. Isolation on Linux

The Linux runtime starts sandbox processes with bubblewrap. A policy can also enable network namespaces, Landlock, seccomp, and namespace or capability limits. Network isolation needs iproute2, iptables, and nftables. JavaScript execution needs nodejs on the host.

The default listen port is 8321. To select another policy, set `JIUWENBOX_POLICY_PATH` to that file's absolute path.

## 3. Relation to the other components

JiuwenBox is a separate service. Agent SSAS does not create sandboxes. agent-shield does not start this service. The caller keeps the sandbox address and manages sandboxes through the API in the README.
