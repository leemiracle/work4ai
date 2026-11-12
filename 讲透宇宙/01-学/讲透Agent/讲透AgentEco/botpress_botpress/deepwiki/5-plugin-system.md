<!-- source: DeepWiki mcp.deepwiki.com · repo botpress/botpress · page 5 Plugin System · fetched 2026-10-27 -->

# Plugin System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bots/knowledgiani/package.json](bots/knowledgiani/package.json)
- [bots/synchrotron/package.json](bots/synchrotron/package.json)
- [packages/sdk/src/bot/implementation.ts](packages/sdk/src/bot/implementation.ts)
- [packages/sdk/src/bot/server/index.ts](packages/sdk/src/bot/server/index.ts)
- [packages/sdk/src/bot/server/types.test.ts](packages/sdk/src/bot/server/types.test.ts)
- [packages/sdk/src/bot/server/types.ts](packages/sdk/src/bot/server/types.ts)
- [packages/sdk/src/plugin/implementation.ts](packages/sdk/src/plugin/implementation.ts)
- [packages/sdk/src/plugin/server/types.ts](packages/sdk/src/plugin/server/types.ts)
- [plugins/file-synchronizer/package.json](plugins/file-synchronizer/package.json)
- [plugins/hitl/package.json](plugins/hitl/package.json)
- [plugins/hitl/src/hooks/before-incoming-event/all.ts](plugins/hitl/src/hooks/before-incoming-event/all.ts)
- [plugins/hitl/src/hooks/before-incoming-event/index.ts](plugins/hitl/src/hooks/before-incoming-event/index.ts)
- [plugins/hitl/src/hooks/index.ts](plugins/hitl/src/hooks/index.ts)
- [plugins/hitl/src/index.ts](plugins/hitl/src/index.ts)
- [plugins/knowledge/package.json](plugins/knowledge/package.json)
- [plugins/personality/package.json](plugins/personality/package.json)
- [plugins/synchronizer/package.json](plugins/synchronizer/package.json)
- [plugins/synchronizer/src/index.ts](plugins/synchronizer/src/index.ts)

</details>



The plugin system provides a framework for extending bot functionality with reusable modules that encapsulate actions, event handlers, message processors, and lifecycle hooks. Plugins are defined using `PluginDefinition`, implemented via `PluginImplementation`, and integrated into bots through the `BotImplementation` class.

This page covers the core plugin architecture and how plugins integrate with bots. For plugin creation details, see [Plugin Definition & Implementation](#5.1). For the HITL plugin implementation, see [HITL Plugin](#5.2). For details on other specialized plugins, see [Other Plugins](#5.3).

## Plugin Architecture Overview

The plugin system consists of three main layers: definition (contract), implementation (logic), and integration (bot composition).

### Plugin System Layers

**Plugin Definition Layer**

The `PluginDefinition` class defines the plugin contract: configuration schema, actions, events, states, and interface requirements.

```mermaid
graph TB
    subgraph "Definition Layer"
        PD["PluginDefinition<br/>@botpress/sdk"]
        CONFIG["configuration.schema<br/>z.object()"]
        ACTIONS["actions<br/>Action definitions"]
        EVENTS["events<br/>Event definitions"]
        STATES["states<br/>State definitions"]
        INTERFACES["interfaces<br/>Interface requirements"]
    end
    
    subgraph "Implementation Layer"
        PIMPL["PluginImplementation<br/>packages/sdk/src/plugin/implementation.ts"]
        PROPS["PluginImplementationProps<br/>actions: ActionHandlers"]
        INIT["initialize(PluginRuntimeProps)"]
    end
    
    subgraph "Bot Integration Layer"
        BI["BotImplementation<br/>packages/sdk/src/bot/implementation.ts"]
        PLUGINS["_plugins: Record<string, PluginImplementation>"]
        MERGE["Handler Merging<br/>Plugin + Bot Handlers"]
    end
    
    PD --> PIMPL
    CONFIG --> PROPS
    ACTIONS --> PROPS
    
    PIMPL --> INIT
    INIT --> BI
    BI --> PLUGINS
    PLUGINS --> MERGE
```

Sources: [packages/sdk/src/plugin/implementation.ts:46-57](), [packages/sdk/src/bot/implementation.ts:35-41](), [packages/sdk/src/bot/implementation.ts:43-77]()

### Plugin Component Architecture

```mermaid
graph TB
    subgraph "PluginImplementation Core"
        PIMPL["PluginImplementation<TPlugin><br/>packages/sdk/src/plugin/implementation.ts:57"]
        RUNTIME["_runtimeProps?: PluginRuntimeProps<br/>Line 58"]
        ACTION_H["_actionHandlers: ActionHandlers<br/>Line 60"]
        MSG_H["_messageHandlers: OrderedMessageHandlersMap<br/>Line 61"]
        EVT_H["_eventHandlers: OrderedEventHandlersMap<br/>Line 62"]
        STATE_H["_stateExpiredHandlers: OrderedStateExpiredHandlersMap<br/>Line 63"]
        HOOK_H["_hookHandlers: OrderedHookHandlersMap<br/>Line 64-75"]
        WF_H["_workflowHandlers: OrderedWorkflowHandlersMap<br/>Line 76-80"]
        REG_ORDER["_registerOrder: number<br/>Line 82"]
    end
    
    subgraph "Handler Proxies"
        AH_PROXY["actionHandlers getter<br/>Line 127-145"]
        MH_PROXY["messageHandlers getter<br/>Line 147-186"]
        EH_PROXY["eventHandlers getter<br/>Line 188-228"]
        SH_PROXY["stateExpiredHandlers getter<br/>Line 230-262"]
        HH_PROXY["hookHandlers getter<br/>Line 264-325"]
        WH_PROXY["workflowHandlers getter<br/>Line 327-393"]
    end
    
    subgraph "Registration API"
        ON["on object<br/>Line 395"]
        MSG_REG["on.message(type, handler)<br/>Line 396-404"]
        EVT_REG["on.event(type, handler)<br/>Line 406-414"]
        HOOK_REG["on.beforeIncomingMessage(type, handler)<br/>Line 436-444"]
        WF_REG["on.workflowStart(type, handler)<br/>Line 542-550"]
    end
    
    PIMPL --> ACTION_H
    PIMPL --> MSG_H
    PIMPL --> EVT_H
    PIMPL --> STATE_H
    PIMPL --> HOOK_H
    PIMPL --> WF_H
    
    ACTION_H --> AH_PROXY
    MSG_H --> MH_PROXY
    EVT_H --> EH_PROXY
    STATE_H --> SH_PROXY
    HOOK_H --> HH_PROXY
    WF_H --> WH_PROXY
    
    MSG_REG --> MSG_H
    EVT_REG --> EVT_H
    HOOK_REG --> HOOK_H
    WF_REG --> WF_H
```

Sources: [packages/sdk/src/plugin/implementation.ts:57-580]()

## Plugin Lifecycle

Plugins follow a two-phase lifecycle: construction and initialization. Construction creates the plugin instance with action handlers, while initialization injects runtime context.

### Initialization Flow

```mermaid
graph TB
    subgraph "Construction Phase"
        CONSTR["new PluginImplementation(props)<br/>packages/sdk/src/plugin/implementation.ts:84"]
        PROPS["PluginImplementationProps<br/>actions: ActionHandlers<TPlugin>"]
        ASSIGN["this._actionHandlers = props.actions<br/>Line 85"]
    end
    
    subgraph "Initialization Phase"
        INIT["initialize(PluginRuntimeProps)<br/>Line 88"]
        RUNTIME["PluginRuntimeProps<br/>configuration, interfaces, integrations, alias"]
        STORE["this._runtimeProps = props<br/>Line 89"]
    end
    
    subgraph "Runtime Access"
        GETTER["get _runtime()<br/>Line 93"]
        CHECK["if (!this._runtimeProps)<br/>Line 94"]
        ERROR["throw Error<br/>'Plugin not correctly initialized'"]
        RETURN["return this._runtimeProps<br/>Line 99"]
    end
    
    subgraph "Tool Generation"
        TOOLS["_getTools(client)<br/>Line 102"]
        CONFIG["configuration from _runtime"]
        INTERFACES["interfaces from _runtime"]
        PROXIES["proxyActions, proxyStates,<br/>proxyWorkflows, proxyEvents"]
    end
    
    CONSTR --> PROPS
    PROPS --> ASSIGN
    
    ASSIGN --> INIT
    INIT --> RUNTIME
    RUNTIME --> STORE
    
    STORE --> GETTER
    GETTER --> CHECK
    CHECK --> ERROR
    CHECK --> RETURN
    
    RETURN --> TOOLS
    TOOLS --> CONFIG
    TOOLS --> INTERFACES
    TOOLS --> PROXIES
```

Sources: [packages/sdk/src/plugin/implementation.ts:84-125]()

### Handler Registration and Execution

Handlers are registered via the `on` object and stored in ordered maps. When accessed via proxy getters, they are merged with interface handlers, sorted by registration order, and injected with plugin tools (actions, states, users, conversations, etc.).

```mermaid
graph LR
    subgraph "Handler Registration"
        REG["on.message('text', handler)<br/>Line 396-404"]
        PUSH["utils.arrays.safePush<br/>Add to _messageHandlers[type]"]
        ORDER["{ handler, order: _registerOrder++ }"]
    end
    
    subgraph "Handler Access"
        PROXY["get messageHandlers[messageName]<br/>Line 147-186"]
        STRIP["_stripAliasPrefix(messageName)<br/>Line 152"]
        SPECIFIC["specificHandlers = _messageHandlers[messageName]"]
        GLOBAL["globalHandlers = _messageHandlers['*']"]
        UNIQUE["utils.arrays.unique([...])<br/>Line 155"]
        SORT["sort((a, b) => a.order - b.order)<br/>Line 157"]
    end
    
    subgraph "Handler Execution"
        INJECT["handler({...input, ...this._getTools(input.client)})<br/>Line 161"]
        TOOLS["Tools: actions, states, users, conversations, messages"]
    end
    
    REG --> PUSH
    PUSH --> ORDER
    ORDER --> SPECIFIC
    
    PROXY --> STRIP
    STRIP --> SPECIFIC
    STRIP --> GLOBAL
    
    SPECIFIC --> UNIQUE
    GLOBAL --> UNIQUE
    UNIQUE --> SORT
    SORT --> INJECT
    
    INJECT --> TOOLS
```

Sources: [packages/sdk/src/plugin/implementation.ts:147-186](), [packages/sdk/src/plugin/implementation.ts:396-404](), [packages/sdk/src/plugin/implementation.ts:102-125]()

## Plugin Integration into Bots

The `BotImplementation` class integrates plugins by storing them in a `_plugins` map and merging their handlers with bot handlers. Action calls use the `PLUGIN_PREFIX_SEPARATOR` (`#`) to route to the correct plugin.

### Bot-Plugin Handler Composition

```mermaid
graph TB
    subgraph "BotImplementation Constructor"
        CONSTR["constructor(props)<br/>packages/sdk/src/bot/implementation.ts:73"]
        ACTION_ASSIGN["this._actionHandlers = props.actions<br/>Line 75"]
        PLUGIN_ASSIGN["this._plugins = props.plugins<br/>Line 76"]
    end
    
    subgraph "Action Handler Proxy"
        ACTION_GET["get actionHandlers<br/>Line 83-109"]
        PROXY["new Proxy({}, { get })<br/>Line 84"]
        SPLIT["actionName.split(PLUGIN_PREFIX_SEPARATOR)<br/>Line 98"]
        BOT_CHECK["let action = this._actionHandlers[actionName]<br/>Line 88"]
        PLUGIN_LOOP["for plugin in this._plugins<br/>Line 97"]
        PREFIX_MATCH["if (actionPrefix !== pluginAlias)<br/>Line 99"]
        PLUGIN_ACTION["return plugin.actionHandlers[nameWithoutPrefix]<br/>Line 102"]
    end
    
    subgraph "Message Handler Proxy"
        MSG_GET["get messageHandlers<br/>Line 111-136"]
        PLUGIN_FLAT["Object.values(this._plugins).flatMap<br/>Line 117"]
        SELF_SPECIFIC["this._messageHandlers[messageName]<br/>Line 120"]
        SELF_GLOBAL["this._messageHandlers['*']<br/>Line 121"]
        MERGE["[...pluginHandlers, ...selfHandlers]<br/>Line 132"]
        SORT["sort((a, b) => a.order - b.order)<br/>Line 123"]
    end
    
    CONSTR --> ACTION_ASSIGN
    CONSTR --> PLUGIN_ASSIGN
    
    PLUGIN_ASSIGN --> ACTION_GET
    ACTION_GET --> PROXY
    PROXY --> BOT_CHECK
    BOT_CHECK --> PLUGIN_LOOP
    PLUGIN_LOOP --> SPLIT
    SPLIT --> PREFIX_MATCH
    PREFIX_MATCH --> PLUGIN_ACTION
    
    PLUGIN_ASSIGN --> MSG_GET
    MSG_GET --> PLUGIN_FLAT
    MSG_GET --> SELF_SPECIFIC
    MSG_GET --> SELF_GLOBAL
    PLUGIN_FLAT --> MERGE
    SELF_SPECIFIC --> MERGE
    SELF_GLOBAL --> MERGE
    MERGE --> SORT
```

Sources: [packages/sdk/src/bot/implementation.ts:73-136](), [packages/sdk/src/consts.ts:3]()

## Handler Types and Registration

Plugins support multiple handler types, each registered via the `on` object. Handlers are stored in ordered maps with registration sequence numbers to preserve execution order.

### Handler Registration Methods

| Handler Type | Registration Method | Storage Type |
|--------------|-------------------|--------------|
| Action | Constructor `props.actions` | `ActionHandlers` |
| Message | `on.message(type, handler)` | `OrderedMessageHandlersMap` |
| Event | `on.event(type, handler)` | `OrderedEventHandlersMap` |
| State Expired | `on.stateExpired(name, handler)` | `OrderedStateExpiredHandlersMap` |
| Hook | `on.beforeIncomingMessage(type, handler)` | `OrderedHookHandlersMap` |
| Workflow | `on.workflowStart(name, handler)` | `OrderedWorkflowHandlersMap` |

Sources: [packages/sdk/src/plugin/implementation.ts:395-580]()

### Hook Handler Types

The plugin system provides hooks for intercepting operations at different lifecycle points. Hooks can be stoppable (returning `{ stop: true }`) or data-transforming.

```mermaid
graph TB
    subgraph "Incoming Hooks (Stoppable)"
        BIE["before_incoming_event<br/>packages/sdk/src/plugin/server/types.ts:245"]
        BIM["before_incoming_message<br/>Line 249"]
        AIE["after_incoming_event<br/>Line 265"]
        AIM["after_incoming_message<br/>Line 269"]
        BICA["before_incoming_call_action<br/>Line 261"]
        AICA["after_incoming_call_action<br/>Line 281"]
    end
    
    subgraph "Outgoing Hooks (Non-stoppable)"
        BOM["before_outgoing_message<br/>Line 253"]
        AOM["after_outgoing_message<br/>Line 273"]
        BOCA["before_outgoing_call_action<br/>Line 257"]
        AOCA["after_outgoing_call_action<br/>Line 277"]
    end
    
    subgraph "Hook Output"
        STOPPABLE["{ data?: T, stop?: boolean }<br/>For stoppable hooks"]
        NON_STOP["{ data?: T }<br/>For non-stoppable hooks"]
    end
    
    BIE --> STOPPABLE
    BIM --> STOPPABLE
    AIE --> STOPPABLE
    AIM --> STOPPABLE
    BICA --> STOPPABLE
    AICA --> STOPPABLE
    
    BOM --> NON_STOP
    AOM --> NON_STOP
    BOCA --> NON_STOP
    AOCA --> NON_STOP
```

Sources: [packages/sdk/src/plugin/server/types.ts:244-285]()

## Plugin Runtime Environment

Plugins receive a runtime environment through `initialize(PluginRuntimeProps)` containing configuration, interface mappings, and an optional alias. The `_getTools` method creates proxy objects for actions, states, events, and workflows.

### Runtime Props Structure

| Property | Description | Source |
|----------|-------------|--------|
| `configuration` | Plugin configuration values defined in schema | [packages/sdk/src/plugin/server/types.ts:139]() |
| `interfaces` | Mapping of interface dependencies to implementations | [packages/sdk/src/plugin/server/types.ts:144]() |
| `integrations` | Mapping of integration dependencies to implementations | [packages/sdk/src/plugin/server/types.ts:149]() |
| `alias` | The unique identifier for the plugin instance in the bot | [packages/sdk/src/plugin/server/types.ts:155]() |

Sources: [packages/sdk/src/plugin/server/types.ts:138-155]()

### Plugin Tool Generation

```mermaid
graph TB
    subgraph "_getTools Method"
        GET_TOOLS["_getTools(client)<br/>packages/sdk/src/plugin/implementation.ts:102"]
        EXTRACT["const { configuration, interfaces, integrations, alias } = this._runtime<br/>Line 103"]
    end
    
    subgraph "Proxy Creation"
        ACTION_P["proxyActions(client, this._runtime)<br/>Line 104"]
        STATE_P["proxyStates(client, this._runtime)<br/>Line 105"]
        WORKFLOW_P["proxyWorkflows({ client, pluginAlias })<br/>Line 106"]
        USER_P["proxyUsers({ client, pluginAlias })<br/>Line 108"]
        CONV_P["proxyConversations({ client, plugin })<br/>Line 109"]
    end
    
    subgraph "Tools Object Return"
        RETURN["return { configuration, interfaces, integrations, actions, states, alias, workflows, events, users, conversations, messages }<br/>Line 112-124"]
    end
    
    GET_TOOLS --> EXTRACT
    EXTRACT --> ACTION_P
    EXTRACT --> STATE_P
    EXTRACT --> WORKFLOW_P
    EXTRACT --> USER_P
    EXTRACT --> CONV_P
    
    ACTION_P --> RETURN
    STATE_P --> RETURN
    WORKFLOW_P --> RETURN
    USER_P --> RETURN
    CONV_P --> RETURN
```

Sources: [packages/sdk/src/plugin/implementation.ts:102-125]()

## Plugin Prefix System

Actions implemented by plugins use a prefix system to avoid naming conflicts. The prefix format is `{pluginAlias}#{actionName}` using the `PLUGIN_PREFIX_SEPARATOR` constant.

### Action Resolution with Prefixes

```mermaid
graph LR
    subgraph "BotImplementation Resolution"
        CALL["Action Call<br/>'myPlugin#doSomething'"]
        SPLIT["Split on PLUGIN_PREFIX_SEPARATOR<br/>'myPlugin' + 'doSomething'"]
        LOOKUP["Plugin Lookup<br/>this._plugins['myPlugin']"]
    end
    
    subgraph "PluginImplementation Resolution"
        STRIP["_stripAliasPrefix(actionName)<br/>Remove 'myPlugin#'"]
        EXEC["Handler Execution<br/>handler({...input, ...tools})"]
    end
    
    CALL --> SPLIT
    SPLIT --> LOOKUP
    LOOKUP --> STRIP
    STRIP --> EXEC
```

Sources: [packages/sdk/src/bot/implementation.ts:97-103](), [packages/sdk/src/plugin/implementation.ts:132-141](), [packages/sdk/src/consts.ts:3]()

---

