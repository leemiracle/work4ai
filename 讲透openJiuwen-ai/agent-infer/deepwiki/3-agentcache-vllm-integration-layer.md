<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/agent-infer · page 3 AgentCache: vLLM Integration Layer · fetched 2026-11-02 -->

# AgentCache: vLLM Integration Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agentinfer/agentcache/__init__.py](agentinfer/agentcache/__init__.py)
- [agentinfer/agentcache/core/__init__.py](agentinfer/agentcache/core/__init__.py)
- [agentinfer/agentcache/core/factory.py](agentinfer/agentcache/core/factory.py)
- [agentinfer/agentcache/core/scheduler.py](agentinfer/agentcache/core/scheduler.py)
- [design/module/scheduling/vllm-runtime-integration.md](design/module/scheduling/vllm-runtime-integration.md)

</details>



## Purpose and Scope

The AgentCache integration layer embeds AgentInfer's agent-aware scheduling and prefix-caching policies into vLLM V1 [design/module/scheduling/vllm-runtime-integration.md:36-38](). It acts as an integration bridge that intercepts request arrivals and completions, manages request retention before native vLLM admission, and communicates lifecycle events across Data Parallel (DP) ranks—all without replacing vLLM's underlying token-level scheduler, block allocator, or continuous batching engine [agentinfer/agentcache/core/scheduler.py:5-7](). 

This parent page provides a high-level overview of the vLLM integration subsystems. For granular technical specifications, please consult the child pages linked below.

---

## 3.1 Scheduler Bridges and Controller Factory

AgentCache integrates with vLLM's execution loop through specialized scheduler subclasses: `AgentCacheAsyncSchedulerBridge` (for asynchronous V1 execution) and `AgentCacheSyncSchedulerBridge` (for synchronous setups) [agentinfer/agentcache/core/__init__.py:8-9](). These bridges inherit from vLLM's native scheduler classes (`AsyncScheduler` and `Scheduler`) and coordinate with an underlying `EmbeddedSchedulerController` [agentinfer/agentcache/core/scheduler.py:20-21, 45-104]().

The policy controller itself is instantiated via `build_progress_ttl_controller`, which parses `additional_config.agentcache` properties to construct a configured `ProgramScheduler` running the Progress-TTL strategy [agentinfer/agentcache/core/factory.py:76-80]().

### Diagram: Scheduler Integration Architecture
```mermaid
flowchart TB
    subcode["Code Entity Space"]
        subclass1["AgentCacheAsyncSchedulerBridge\n(agentinfer/agentcache/core/scheduler.py)"]
        subclass2["AgentCacheSyncSchedulerBridge\n(agentinfer/agentcache/core/scheduler.py)"]
        controller["build_progress_ttl_controller\n(agentinfer/agentcache/core/factory.py)"]
        queue["AgentAwareQueue\n(agentinfer/agentcache/core/request_queue.py)"]
        engine["vLLM EngineCore\n(vLLM V1 Scheduler)"]
    end

    subnat["Natural Language Space"]
        ns1["Async vLLM Server Mode"]
        ns2["Sync vLLM Server Mode"]
        ns3["Policy Rule Validation"]
    end

    ns1 --> subclass1
    ns2 --> subclass2
    ns3 --> controller
    subclass1 --> engine
    subclass2 --> engine
    controller --> subclass1
    controller --> subclass2
    queue --> subclass1

    classDef code fill:#f9f9f9,stroke:#333,stroke-width:1px;
    class subclass1,subclass2,controller,queue,engine code;
```
*Sources: [agentinfer/agentcache/core/scheduler.py:20-43](), [agentinfer/agentcache/core/factory.py:76-80]()*

For details on scheduler bridges, the `AgentAwareQueue` waiting queue [agentinfer/agentcache/core/scheduler.py:36-43](), and policy configuration validation, see [Scheduler Bridges and Controller Factory](#3.1).

---

## 3.2 API Adapter: Identity and Lifecycle Middleware

To extract session headers and track conversational programs, AgentCache provides ASGI/WSGI middleware components: `AgentCacheIdentityMiddleware` and `AgentCacheLifecycleMiddleware` [agentinfer/agentcache/core/api_adapter.py:6-7](). 

The identity middleware normalizes incoming framework headers, processes `agent_hint` fields, and bridges Anthropic Messages protocol semantics into vLLM's internal `vllm_xargs.agentic_context` [design/module/scheduling/vllm-runtime-integration.md:104](). Meanwhile, the lifecycle middleware optionally parses API output streams for tool-use completions, emitting terminal signals across DP ranks via Unix datagram sockets (`AGENTCACHE_VLLM_LIFECYCLE_SOCKET`) [design/module/scheduling/vllm-runtime-integration.md:63, 105]().

### Diagram: API Middleware and Datagram Lifecycle Signalling
```mermaid
flowchart LR
    subcode["Code Entity Space"]
        im["AgentCacheIdentityMiddleware\n(agentinfer/agentcache/core/api_adapter.py)"]
        lm["AgentCacheLifecycleMiddleware\n(agentinfer/agentcache/core/api_adapter.py)"]
        sock["UnixLifecycleReceiver\n(agentinfer/agentcache/core/api_adapter.py)"]
    end

    subnat["Natural Language Space"]
        req["Incoming HTTP Request"]
        resp["Streaming API Response"]
        dp["Multi-DP Rank Cluster"]
    end

    req --> im
    im -->|identity mapping| req
    resp --> lm
    lm -->|Unix Datagrams| sock
    sock --> dp

    classDef code fill:#f9f9f9,stroke:#333,stroke-width:1px;
    class im,lm,sock code;
```
*Sources: [agentinfer/agentcache/core/api_adapter.py:1-25](), [design/module/scheduling/vllm-runtime-integration.md:63-109]()*

For details on middleware lifecycle interception, socket communication, and request normalization, see [API Adapter: Identity and Lifecycle Middleware](#3.2).

---

## 3.3 Entrypoints, LLM Wrapper and AgentRouter

Client interactions with AgentCache are mediated via several high-level entrypoints and wrappers. The `agentinfer.LLM` class exposes an embedding wrapper for programmatic usage, while the `agentcache` command-line entrypoint (`vllm` integration mode) and benchmark runners simplify server provisioning [design/module/scheduling/vllm-runtime-integration.md:57-84](). Additionally, native middleware patches for `agentrouter` inject `agent_hint_affinity` parameters and manage token offsets prior to backend dispatch.

For details on the LLM wrapper, command-line entrypoints, and agentrouter middleware patches, see [Entrypoints, LLM Wrapper and AgentRouter](#3.3).

---

