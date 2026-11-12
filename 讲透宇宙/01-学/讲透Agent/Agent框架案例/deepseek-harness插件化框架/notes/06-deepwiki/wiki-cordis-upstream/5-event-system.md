---
deepwiki-url: https://deepwiki.com/cordiverse/cordis/5-event-system
indexed: 2026-08-16
commit: 8cc9e33f (upstream master)
---

# Event System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/core/src/events.ts](packages/core/src/events.ts)
- [packages/core/tests/events.spec.ts](packages/core/tests/events.spec.ts)

</details>



The Event System provides publish-subscribe communication capabilities within the Cordis framework. It enables loosely coupled communication between components through a centralized event bus managed by the `EventsService` class. The system supports multiple dispatch modes for different event handling patterns and integrates seamlessly with the Context system and Fiber lifecycle management.

For information about the broader Context system that hosts the Event System, see [Context System](). For details about plugin lifecycle management that interacts with events, see [Fiber Lifecycle]().

## EventsService Architecture

The `EventsService` class serves as the central event bus for all Cordis contexts. It maintains event hooks, handles event registration and dispatch, and provides multiple execution modes for different event handling patterns.

Title: EventsService Logic and Entity Space
```mermaid
graph TB
    subgraph "EventsService Core [packages/core/src/events.ts]"
        EventsService["EventsService"]
        Hooks["_hooks: Record<keyof any, Hook[]>"]
        Context["ctx: Context"]
    end
    
    subgraph "Event Registration [packages/core/src/events.ts]"
        On["on(name, listener, options)"]
        Once["once(name, listener, options)"]
        Register["register(label, hooks, callback, options)"]
        Unregister["unregister(hooks, callback)"]
    end
    
    subgraph "Event Dispatch [packages/core/src/events.ts]"
        Parallel["parallel(...args)"]
        Emit["emit(...args)"]
        Serial["serial(...args)"]
        Bail["bail(...args)"]
        Waterfall["waterfall(...args)"]
        Resolve["_resolve(type, args)"]
    end
    
    subgraph "Integration Points"
        FiberEffect["ctx.fiber.effect() [packages/core/src/fiber.ts]"]
        ReflectBind["ctx.reflect.bind() [packages/core/src/reflect.ts]"]
        ContextFilter["Context.filter [packages/core/src/context.ts]"]
    end
    
    EventsService --> Hooks
    EventsService --> Context
    
    On --> Register
    Once --> On
    Register --> FiberEffect
    
    Emit --> Resolve
    Parallel --> Resolve
    Serial --> Resolve
    Bail --> Resolve
    Waterfall --> Resolve
    
    Resolve --> ContextFilter
    On --> ReflectBind
```

Sources: [packages/core/src/events.ts:45-167]()

## Dispatch Modes

The Event System supports five distinct dispatch modes, each serving different communication patterns. The system uses the `isBailed` utility to determine if a return value should stop execution in `serial` and `bail` modes (defined as not being `null`, `false`, or `undefined` [packages/core/src/events.ts:6-8]()).

| Mode | Method | Execution | Return Value | Use Case |
|------|--------|-----------|--------------|----------|
| `emit` | `emit()` | Synchronous, all listeners | `void` | Fire-and-forget notifications |
| `parallel` | `parallel()` | Asynchronous, concurrent | `Promise<void>` | Independent async operations; throws `AggregateError` on failure |
| `serial` | `serial()` | Asynchronous, sequential | `Promise<result>` | Ordered processing with early exit via `isBailed` |
| `bail` | `bail()` | Synchronous, sequential | `result` | Synchronous processing with early exit via `isBailed` |
| `waterfall` | `waterfall()` | Synchronous/Asynchronous | `result` | Middleware-style processing using a `next` callback |

Title: Dispatch Execution Flow
```mermaid
sequenceDiagram
    participant C as "Context"
    participant E as "EventsService"
    participant L1 as "Listener 1"
    participant L2 as "Listener 2"
    participant L3 as "Listener 3"
    
    Note over C,L3: Emit Mode (Fire-and-forget)
    C->>E: emit("event", data)
    E->>L1: callback(data)
    E->>L2: callback(data)
    E->>L3: callback(data)
    
    Note over C,L3: Serial Mode (Sequential with bail)
    C->>E: serial("event", data)
    E->>L1: callback(data)
    L1-->>E: return null
    E->>L2: callback(data)
    L2-->>E: return "result"
    Note over E,L3: L3 not called (bailed via isBailed)
    E-->>C: return "result"
    
    Note over C,L3: Waterfall Mode (Middleware chain)
    C->>E: waterfall("event", data, inner)
    E->>L1: callback(data, next1)
    L1->>L2: next1() calls L2
    L2->>L3: next2() calls L3
    L3-->>L2: return result
    L2-->>L1: return result
    L1-->>E: return result
    E-->>C: return result
```

Sources: [packages/core/src/events.ts:14](), [packages/core/src/events.ts:89-126](), [packages/core/src/events.ts:6-8]()

## Event Registration and Hooks

Events are registered through the `on()` and `once()` methods, which create `Hook` objects stored in the `_hooks` registry. Each hook contains context information and callback references. Registration is lifecycle-aware and requires the fiber to be active [packages/core/src/events.ts:150]().

Title: Registration and Hook Entity Space
```mermaid
graph LR
    subgraph "Hook Structure [packages/core/src/events.ts]"
        Hook["Hook"]
        HookCtx["ctx: Context"]
        HookCallback["callback: Function"]
        HookOptions["EventOptions"]
    end
    
    subgraph "EventOptions [packages/core/src/events.ts]"
        Prepend["prepend?: boolean"]
        Global["global?: boolean"]
    end
    
    subgraph "Registration Flow"
        OnCall["ctx.on(name, listener, options)"]
        ReflectBind["ctx.reflect.bind(listener)"]
        FiberAssert["ctx.fiber.assertActive()"]
        BailListener["bail(ctx, 'internal/listener', ...)"]
        RegisterHook["register(label, hooks, callback, options)"]
        FiberEffect["ctx.fiber.effect()"]
    end
    
    Hook --> HookCtx
    Hook --> HookCallback
    Hook --> HookOptions
    
    HookOptions --> Prepend
    HookOptions --> Global
    
    OnCall --> FiberAssert
    OnCall --> ReflectBind
    OnCall --> BailListener
    OnCall --> RegisterHook
    RegisterHook --> FiberEffect
```

Sources: [packages/core/src/events.ts:35-43](), [packages/core/src/events.ts:128-158]()

## Internal Events

The Event System defines a set of internal events that enable system-level communication and monitoring. These events are often prefixed with `internal/`.

| Event | Purpose | Parameters | Context |
|-------|---------|------------|---------|
| `internal/plugin` | Plugin lifecycle notifications | `fiber: Fiber` | System |
| `internal/status` | Fiber state changes | `fiber: Fiber, oldValue: FiberState` | System |
| `internal/service` | Service registration | `name: string, value: any` | Context |
| `internal/update` | Configuration updates | `config: any, noSave: boolean, next: () => void` | Fiber |
| `internal/get` | Property access interception | `ctx: Context, name: string, error: Error, next: () => any` | System |
| `internal/set` | Property modification interception | `ctx: Context, name: string, value: any, error: Error, next: () => boolean` | System |
| `internal/listener` | Event listener registration | `name: string, listener: any, options: EventOptions` | Context |
| `internal/dispatch` | Event dispatch monitoring | `type: string, name: string, args: any[], thisArg: any` | System |

Sources: [packages/core/src/events.ts:169-176](), [packages/core/src/events.ts:75-77]()

## Context Integration

### Event Filtering and Scope

Events can be filtered based on context relationships using the `Context.filter` mechanism. The `_resolve` method handles this logic, checking if a listener's context is compatible with the dispatching context [packages/core/src/events.ts:72-81]().

```mermaid
graph TB
    subgraph "Event Resolution Flow [packages/core/src/events.ts]"
        ResolveCall["_resolve(type, args)"]
        ExtractArgs["Extract thisArg and name"]
        InternalDispatch["emit('internal/dispatch', ...)"]
        GetHooks["Get hooks from _hooks[name]"]
        FilterHooks["Filter hooks"]
        MapCallbacks["Map to callback functions"]
    end
    
    subgraph "Filtering Logic"
        GlobalFlag["hook.global"]
        NoFilter["!filter"]
        FilterCall["filter.call(thisArg, hook.ctx)"]
    end
    
    ResolveCall --> ExtractArgs
    ExtractArgs --> InternalDispatch
    InternalDispatch --> GetHooks
    GetHooks --> FilterHooks
    FilterHooks --> MapCallbacks
    
    FilterHooks --> GlobalFlag
    FilterHooks --> NoFilter
    FilterHooks --> FilterCall
```

Sources: [packages/core/src/events.ts:72-81]()

### Fiber Lifecycle Integration

Event listeners are automatically managed through the Fiber lifecycle system. When a context becomes inactive, its event listeners are automatically disposed of through the effect system via `ctx.fiber.effect()` [packages/core/src/events.ts:130-134]().

The `internal/update` event receives special handling in the constructor. Listeners for `internal/update` that are not global are stored in the Fiber's own `_hooks` collection (a `DisposableList`) rather than the global `EventsService._hooks` [packages/core/src/events.ts:54-60]().

Sources: [packages/core/src/events.ts:54-70](), [packages/core/src/events.ts:128-134]()

### Reflection Integration

Event listeners are bound through the reflection system using `ctx.reflect.bind()` [packages/core/src/events.ts:151](). This ensures that when an event listener is called, its `this` context is correctly set to the context that registered it, allowing access to services and other context-bound properties.

Sources: [packages/core/src/events.ts:151]()
