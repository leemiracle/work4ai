<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-apps-sdk-examples · extra page Shopping Cart Widget · fetched 2026-10-26 -->

# Shopping Cart Widget

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [shopping_cart_python/README.md](shopping_cart_python/README.md)
- [shopping_cart_python/requirements.txt](shopping_cart_python/requirements.txt)
- [src/shopping-cart/icons.tsx](src/shopping-cart/icons.tsx)
- [src/shopping-cart/index.tsx](src/shopping-cart/index.tsx)

</details>



## Purpose and Scope

This document details the Shopping Cart widget implementation, which demonstrates session-based state persistence across conversational turns using `widgetSessionId`. The widget showcases how to synchronize state between the MCP server, the widget UI, and the host environment's `widgetState`, enabling users to modify cart contents both through natural language commands and direct UI interactions while maintaining consistency across all three layers.

For broader state management patterns applicable to all widgets, see [State Management Patterns](). For server-side patterns using FastMCP, see [Python Server Architecture Patterns]().

---

## Architecture Overview

The Shopping Cart widget implements a three-way state synchronization model between the MCP server, the widget component, and the host environment's persistent storage.

```mermaid
graph TB
    subgraph HostEnv["ChatGPT Host Environment"]
        ToolOutput["window.openai.toolOutput<br/>Incoming cart items from tool"]
        WidgetState["window.openai.widgetState<br/>Persistent cart state"]
        SessionId["widgetSessionId<br/>Cart identifier key"]
    end
    
    subgraph Widget["Shopping Cart Widget<br/>src/shopping-cart/index.tsx"]
        App["App Component"]
        UseWidgetState["useWidgetState hook<br/>line 88-90"]
        UseOpenAiGlobal["useOpenAiGlobal hook<br/>line 85-87"]
        MergeEffect["useEffect merge logic<br/>line 160-224"]
        CartState["cartState<br/>Local React state"]
        AddItem["addItem function<br/>line 99-123"]
        AdjustQty["adjustQuantity function<br/>line 125-156"]
    end
    
    subgraph Server["shopping_cart_python/main.py"]
        AddToCart["add_to_cart tool"]
        GetOrCreate["_get_or_create_cart"]
        CartsDict["carts: Dict[str, List]"]
        StructuredContent["structuredContent response"]
        MetaSessionId["_meta.widgetSessionId"]
    end
    
    ToolOutput -->|Read via| UseOpenAiGlobal
    UseOpenAiGlobal -->|Provides| MergeEffect
    WidgetState -->|Read/Write via| UseWidgetState
    UseWidgetState -->|Provides| CartState
    
    MergeEffect -->|Merges incoming items| CartState
    CartState -->|Triggers| UseWidgetState
    UseWidgetState -->|Updates| WidgetState
    
    AddItem -->|User clicks Add| AdjustQty
    AdjustQty -->|Modifies| CartState
    
    AddToCart -->|Returns| StructuredContent
    AddToCart -->|Sets| MetaSessionId
    MetaSessionId -->|Keys| SessionId
    SessionId -->|Restores| WidgetState
    
    AddToCart -->|Retrieves/Creates| GetOrCreate
    GetOrCreate -->|Accesses| CartsDict
    
    StructuredContent -->|Populates| ToolOutput
```

**Sources:**
- [src/shopping-cart/index.tsx:1-224]()
- [shopping_cart_python/README.md:33-48]()

---

## State Synchronization Flow

The widget implements a sophisticated state merge pattern that reconciles three sources of data: incoming tool responses, persistent widget state from previous turns, and user modifications made through the UI.

```mermaid
sequenceDiagram
    participant User
    participant Model
    participant Server as shopping_cart_python.main
    participant Host as window.openai
    participant Widget as App Component
    
    User->>Model: "Add 2 eggs to cart"
    Model->>Server: CallToolRequest<br/>add_to_cart({items: [{name:"Eggs",quantity:2}]})
    
    Server->>Server: _get_or_create_cart(None)<br/>Generate new cart_id
    
    Server->>Host: CallToolResult<br/>structuredContent: {cartId, items}<br/>_meta.widgetSessionId: cart_id
    
    Host->>Widget: Update toolOutput<br/>Update widgetState (via sessionId)
    
    Widget->>Widget: useEffect triggered<br/>line 160-224
    Note over Widget: serializedToolOutput check<br/>line 169-182
    
    Widget->>Widget: Extract incomingItems<br/>from toolOutput.items<br/>line 185-189
    
    Widget->>Widget: Get baseState<br/>from widgetState || cartState<br/>line 194
    
    Widget->>Widget: Merge into itemsByName Map<br/>baseItems + incomingItems<br/>line 201-212
    
    Widget->>Widget: setCartState(nextState)<br/>line 223
    
    Widget->>Host: Updates window.openai.widgetState
    
    Note over Widget: Widget renders with<br/>2 eggs in cart
    
    User->>Widget: Click + button on Eggs
    Widget->>Widget: adjustQuantity("Eggs", 1)<br/>line 125-156
    Widget->>Widget: setCartState updates quantity to 3
    Widget->>Host: Updates widgetState
    
    User->>Model: "Add 1 milk"
    Model->>Server: CallToolRequest<br/>add_to_cart({cartId: cart_id, items: [{name:"Milk",quantity:1}]})
    
    Server->>Host: structuredContent: {items: [milk]}<br/>widgetSessionId: cart_id
    
    Host->>Widget: toolOutput: new milk item<br/>widgetState: existing state (3 eggs)
    
    Widget->>Widget: useEffect merge<br/>baseState has 3 eggs (from widgetState)<br/>incomingItems has milk
    
    Widget->>Widget: itemsByName.set merges both
    
    Note over Widget: Final state:<br/>3 eggs + 1 milk
```

**Sources:**
- [src/shopping-cart/index.tsx:160-224]()
- [shopping_cart_python/README.md:33-37]()

---

## Widget Implementation

### Component Structure

The Shopping Cart widget is a single-page React application that renders a two-column layout with suggested items and the current cart contents.

| Component Element | Purpose | Code Reference |
|-------------------|---------|----------------|
| `App` | Root component managing all state | [src/shopping-cart/index.tsx:84]() |
| `JsonPanel` | Debug view for `widgetState` and `toolOutput` | [src/shopping-cart/index.tsx:37-52]() |
| `suggestedItems` | Static array of pre-defined items with icons | [src/shopping-cart/index.tsx:54-75]() |
| `iconMatchers` | Keyword-based icon selection logic | [src/shopping-cart/index.tsx:77-82]() |

### State Hooks and Data Flow

```mermaid
graph TB
    subgraph Hooks["React Hooks"]
        UseOpenAiGlobal1["useOpenAiGlobal('toolOutput')<br/>line 85"]
        UseOpenAiGlobal2["useOpenAiGlobal('toolResponseMetadata')<br/>line 86"]
        UseOpenAiGlobal3["useOpenAiGlobal('widgetState')<br/>line 87"]
        UseWidgetStateHook["useWidgetState&lt;CartWidgetState&gt;<br/>line 88-90"]
        UseRef["useRef&lt;string&gt;<br/>lastToolOutputRef<br/>line 158"]
        UseEffect["useEffect<br/>Merge logic<br/>line 160-224"]
    end
    
    subgraph State["Component State"]
        ToolOutputVar["toolOutput<br/>Incoming items from server"]
        ToolMetaVar["toolResponseMetadata<br/>Response metadata"]
        WidgetStateVar["widgetState<br/>Host persistent state"]
        CartStateVar["cartState<br/>Local cart snapshot"]
        SetCartState["setCartState<br/>State updater"]
        CartItems["cartItems<br/>Array.isArray check<br/>line 91"]
    end
    
    UseOpenAiGlobal1 --> ToolOutputVar
    UseOpenAiGlobal2 --> ToolMetaVar
    UseOpenAiGlobal3 --> WidgetStateVar
    UseWidgetStateHook --> CartStateVar
    UseWidgetStateHook --> SetCartState
    
    CartStateVar --> CartItems
    
    ToolOutputVar --> UseEffect
    ToolMetaVar --> UseEffect
    WidgetStateVar --> UseEffect
    CartStateVar --> UseEffect
    
    UseEffect --> SetCartState
    SetCartState -.Updates.-> CartStateVar
    SetCartState -.Propagates to.-> WidgetStateVar
    
    UseRef --> UseEffect
```

**Sources:**
- [src/shopping-cart/index.tsx:85-91]()
- [src/shopping-cart/index.tsx:158-224]()

### Merge Logic Implementation

The core state synchronization occurs in the `useEffect` hook, which runs whenever `toolOutput` or `toolResponseMetadata` changes.

**Key Steps:**

1. **Duplicate Detection** ([src/shopping-cart/index.tsx:169-182]()): Serializes `toolOutput` and `toolResponseMetadata` and compares against a ref to prevent redundant merges triggered by UI updates.

2. **Extract Incoming Items** ([src/shopping-cart/index.tsx:185-189]()): Safely extracts the `items` array from `toolOutput` with type guards.

3. **Determine Base State** ([src/shopping-cart/index.tsx:194]()): Uses `widgetState` as the authoritative source if available, falling back to `cartState`, then default state.

4. **Merge Using Map** ([src/shopping-cart/index.tsx:201-212]()): Creates a `Map<string, CartItem>` keyed by item name, populates it with base items, then overwrites/adds incoming items.

5. **Update Cart State** ([src/shopping-cart/index.tsx:223]()): Calls `setCartState` with the merged result, which automatically propagates to `window.openai.widgetState`.

**Sources:**
- [src/shopping-cart/index.tsx:160-224]()

### UI-Triggered Actions

The widget provides two user interaction patterns:

**Add Item** ([src/shopping-cart/index.tsx:99-123]()):
- Triggered by clicking "Add" buttons on suggested items.
- Finds existing item by name or creates new entry.
- Increments quantity if item already exists.
- Updates `cartState` via functional setter to ensure atomic updates.

**Adjust Quantity** ([src/shopping-cart/index.tsx:125-156]()):
- Triggered by +/- buttons on cart items.
- Supports both increment (+1) and decrement (-1).
- Removes item from array when quantity reaches 0.

```mermaid
graph LR
    subgraph UserActions["User Actions"]
        ClickAdd["Click 'Add' on<br/>suggested item"]
        ClickPlus["Click '+' button<br/>on cart item"]
        ClickMinus["Click '-' button<br/>on cart item"]
    end
    
    subgraph Functions["Action Handlers"]
        AddItemFunc["addItem(name)<br/>line 99-123"]
        AdjustFunc["adjustQuantity(name, delta)<br/>line 125-156"]
    end
    
    subgraph StateUpdate["State Update Logic"]
        PrevState["setCartState((prevState) => {...})"]
        FindIdx["items.findIndex<br/>Find item by name"]
        CheckQty["Check if nextQuantity === 0"]
        SpliceOrUpdate["Splice if 0,<br/>else update quantity"]
    end
    
    ClickAdd --> AddItemFunc
    ClickPlus --> AdjustFunc
    ClickMinus --> AdjustFunc
    
    AddItemFunc --> PrevState
    AdjustFunc --> PrevState
    
    PrevState --> FindIdx
    FindIdx --> CheckQty
    CheckQty --> SpliceOrUpdate
```

**Sources:**
- [src/shopping-cart/index.tsx:99-156]()

---

## Server Implementation

### Tool Definition and Session Management

The server ships an `add_to_cart` tool. Every `call_tool` response sets `_meta["widgetSessionId"]` to the cart identifier and returns a `structuredContent` payload containing the new cart items ([shopping_cart_python/README.md:35]()).

### Resource Serving

The server implements MCP resource serving to provide the widget HTML. It uses a fallback pattern to load the static assets ([shopping_cart_python/README.md:17-21]()).

**Sources:**
- [shopping_cart_python/README.md:15-31]()

---

## Production Considerations

The README explicitly notes that this demo relies on `window.openai.widgetState` for simplicity, but production systems should implement server-side persistence ([shopping_cart_python/README.md:40-46]()):

1. **Persist to Datastore**: On each `add_to_cart` tool call, load the cart from your datastore using the session ID, apply changes, and persist.
2. **Authoritative Server State**: Treat the datastore as the source of truth. UX interactions (like incrementing quantities) should invoke the backend—either via MCP tool call or direct HTTP request.
3. **Session Locking**: Continue setting `_meta["widgetSessionId"]` so the host and widget stay locked to the same cart across turns.

**Sources:**
- [shopping_cart_python/README.md:40-48]()

---

## Testing the Widget

### Example Conversation Flow

The README provides a test script demonstrating multi-turn state persistence ([shopping_cart_python/README.md:49-61]()):

1. **Turn 1**: "Add 2 eggs to my cart" → Widget renders with 2 eggs.
2. **Turn 2**: "Now add milk" → Widget shows 2 eggs + 1 milk (merged).
3. **UI Interaction**: Add 2 avocados from the UI → `widgetState` updates.
4. **Turn 3**: "Now add 3 tomatoes" → Widget shows merged state of eggs, milk, avocados, and tomatoes.

**Sources:**
- [shopping_cart_python/README.md:49-61]()

---

