<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/treescope · page 5 IPython and Jupyter Integration · fetched 2026-10-26 -->

# IPython and Jupyter Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/api/treescope.rst](docs/api/treescope.rst)
- [treescope/__init__.py](treescope/__init__.py)
- [treescope/_internal/api/ipython_integration.py](treescope/_internal/api/ipython_integration.py)
- [treescope/rendering_parts.py](treescope/rendering_parts.py)

</details>



## Purpose and Scope

This page explains how Treescope integrates with IPython and Jupyter notebook environments to provide interactive HTML visualizations. It covers the mechanisms by which Treescope hooks into IPython's display system, registers as a formatter, and provides convenience functions for rendering objects.

For detailed documentation of individual display functions, see [Display Functions](#5.1). For magic command syntax and usage, see [Magic Commands](#5.2). For configuration options and context management, see [Configuration and Context](#5.3). For details on the rendering pipeline that powers these displays, see [Core Rendering System](#3).

## Integration Architecture

Treescope integrates with IPython at multiple levels to provide seamless interactive visualization:

```mermaid
graph TB
    subgraph "IPython/Jupyter Environment"
        IPythonCore["IPython Core"]
        DisplayFormatter["IPython.display_formatter"]
        HTMLFormatter["text/html formatter"]
        TextFormatter["text/plain formatter"]
        MagicSystem["IPython.core.magic"]
    end
    
    subgraph "Treescope Integration Points"
        RegisterDefault["register_as_default()"]
        RegisterMagics["register_autovisualize_magic()<br/>register_context_manager_magic()"]
        DisplayFunc["display()"]
        ShowFunc["show()"]
        BasicSetup["basic_interactive_setup()"]
    end
    
    subgraph "Treescope Magic Commands"
        AutovizMagic["AutovisualizerMagic<br/>%%autovisualize"]
        ContextMagic["ContextManagerMagic<br/>%%with"]
    end
    
    subgraph "Rendering Pipeline"
        BuildFoldable["build_foldable_representation()"]
        RenderHTML["render_to_html_as_root()"]
        RenderText["render_to_text()"]
        StreamOutput["display_streaming_as_root()"]
    end
    
    BasicSetup --> RegisterDefault
    BasicSetup --> RegisterMagics
    
    RegisterDefault --> DisplayFormatter
    DisplayFormatter --> HTMLFormatter
    DisplayFormatter --> TextFormatter
    
    RegisterMagics --> MagicSystem
    MagicSystem --> AutovizMagic
    MagicSystem --> ContextMagic
    
    DisplayFunc --> BuildFoldable
    ShowFunc --> BuildFoldable
    HTMLFormatter --> BuildFoldable
    
    BuildFoldable --> RenderHTML
    BuildFoldable --> StreamOutput
    TextFormatter --> RenderText
    
    AutovizMagic -.sets context.-> DisplayFunc
    ContextMagic -.sets context.-> DisplayFunc
```

**Integration Architecture Overview**

Sources: [treescope/_internal/api/ipython_integration.py:1-547]()

The integration operates through three primary mechanisms:

1. **Display Formatter Registration**: `register_as_default()` hooks into IPython's formatter system to render objects as HTML or text
2. **Direct Display Functions**: `display()` and `show()` provide explicit rendering control
3. **Magic Commands**: Cell-level directives (`%%autovisualize`, `%%with`) for scoped configuration

## Display Formatter Registration

The `register_as_default()` function establishes Treescope as IPython's default renderer for objects without specialized formatters:

```mermaid
graph TB
    Object["Python Object"]
    
    IPythonDisplay["IPython.display.display(obj)"]
    
    CheckReprHTML{{"Has _repr_html_?<br/>(real method)"}}
    CheckDisplayObj{{"Is DisplayObject?"}}
    CheckIPythonFormat{{"Has IPython<br/>format method?"}}
    CheckTreescopeFormat{{"Has Treescope<br/>format method?"}}
    
    DeferToHTML["Call _repr_html_()<br/>directly"]
    DeferToIPython["Return None<br/>(use IPython default)"]
    RenderTreescope["_render_for_ipython()"]
    
    CheckRootRepr{{"Has __treescope_root_repr__?"}}
    CallRootRepr["Call __treescope_root_repr__()"]
    BuildFoldable["build_foldable_representation()"]
    
    CheckStreaming{{"streaming=True?"}}
    StreamingRender["display_streaming_as_root()"]
    StaticRender["render_to_html_as_root()"]
    
    OutputStealer["Return HTML snippet<br/>(stealable mode)"]
    
    IPythonDisplay --> CheckReprHTML
    CheckReprHTML -->|Yes| DeferToHTML
    CheckReprHTML -->|No| CheckDisplayObj
    CheckDisplayObj -->|Yes| DeferToIPython
    CheckDisplayObj -->|No| CheckIPythonFormat
    CheckIPythonFormat -->|Yes| CheckTreescopeFormat
    CheckTreescopeFormat -->|No| DeferToIPython
    CheckTreescopeFormat -->|Yes| RenderTreescope
    CheckIPythonFormat -->|No| RenderTreescope
    
    RenderTreescope --> CheckRootRepr
    CheckRootRepr -->|Yes| CallRootRepr
    CheckRootRepr -->|No| BuildFoldable
    CallRootRepr --> CheckStreaming
    BuildFoldable --> CheckStreaming
    
    CheckStreaming -->|Yes| StreamingRender
    CheckStreaming -->|No| StaticRender
    
    StreamingRender --> OutputStealer
    StaticRender --> OutputStealer
    OutputStealer --> IPythonDisplay
```

**Formatter Registration Flow**

Sources: [treescope/_internal/api/ipython_integration.py:218-353]()

### Key Components

**Formatter Function**: `_render_for_ipython(value)` [treescope/_internal/api/ipython_integration.py:265-308]()

This function is registered with `IPython.display_formatter.formatters["text/html"]` for the `object` type, making it a fallback for all objects. It implements a priority system:

1. **Defer to `_repr_html_`**: If the object has a real `_repr_html_` method (not inherited), call it directly [treescope/_internal/api/ipython_integration.py:266-275]()
2. **Skip DisplayObjects**: If the object is an `IPython.display.DisplayObject`, return `None` to let IPython handle it [treescope/_internal/api/ipython_integration.py:277-279]()
3. **Check Format Methods**: If the object has IPython format methods (`_repr_pretty_`, `_repr_mimebundle_`) but no Treescope methods, return `None` [treescope/_internal/api/ipython_integration.py:281-292]()
4. **Render with Treescope**: Otherwise, render using Treescope's pipeline [treescope/_internal/api/ipython_integration.py:294-308]()

**Output Stealing**: The rendering is done in "stealable" mode [treescope/_internal/api/ipython_integration.py:300](), which means it displays immediately but returns an HTML snippet that can relocate the output to the correct position (e.g., after the "Out[]" marker in JupyterLab).

**Text Formatter**: For `jax.Array` specifically, a text formatter is registered to avoid copying large arrays to CPU [treescope/_internal/api/ipython_integration.py:314-328]().

**Formatter Ordering**: The HTML formatter is moved to the front of the formatter dict to ensure streaming outputs work correctly [treescope/_internal/api/ipython_integration.py:332-337]().

## Display Functions

Treescope provides two main functions for explicit rendering:

### display()

```mermaid
graph LR
    DisplayCall["display(value, ...)"]
    
    CheckAutovis{{"autovisualize<br/>parameter?"}}
    SetScope["Set active_autovisualizer<br/>scope"]
    
    DisplayHelper["_display_and_maybe_steal()"]
    
    CheckRootRepr{{"Has __treescope_root_repr__?"}}
    CallRoot["Call __treescope_root_repr__()"]
    BuildFoldable["build_foldable_representation()"]
    
    CheckStreaming{{"streaming=True?"}}
    StreamDisplay["display_streaming_as_root()"]
    StaticDisplay["render_to_html_as_root()<br/>+ IPython.display.display()"]
    
    DisplayCall --> CheckAutovis
    CheckAutovis -->|Yes| SetScope
    CheckAutovis -->|No| DisplayHelper
    SetScope --> DisplayHelper
    
    DisplayHelper --> CheckRootRepr
    CheckRootRepr -->|Yes| CallRoot
    CheckRootRepr -->|No| BuildFoldable
    CallRoot --> CheckStreaming
    BuildFoldable --> CheckStreaming
    
    CheckStreaming -->|Yes| StreamDisplay
    CheckStreaming -->|No| StaticDisplay
```

**display() Function Flow**

Sources: [treescope/_internal/api/ipython_integration.py:113-170]()

The `display()` function [treescope/_internal/api/ipython_integration.py:113-170]() renders a single value as an interactive foldable tree. Key parameters:

- `value`: The object to display
- `ignore_exceptions`: Whether to catch rendering errors and show fallbacks [default: `False`]
- `roundtrip_mode`: Whether to start in roundtrip mode [default: `False`]
- `autovisualize`: Override for active autovisualizer - `True` uses default, `False` disables, or provide a custom autovisualizer [default: `None`]
- `streaming`: Whether to use streaming mode (displays structure immediately, fills in expensive parts later) [default: `True`]
- `compress_html`: Whether to zlib-compress output for transmission/storage [default: `True`]

### show()

```mermaid
graph LR
    ShowCall["show(*args, ...)"]
    
    CheckSpaces{{"space_separated=True?"}}
    AddSpaces["Insert ' ' between args"]
    
    CheckAutovis{{"autovisualize<br/>parameter?"}}
    SetScope["Set active_autovisualizer scope"]
    
    InlineFig["figures.inline(*args, wrap=...)"]
    IPythonDisplay["IPython.display.display()"]
    
    ShowCall --> CheckSpaces
    CheckSpaces -->|Yes| AddSpaces
    CheckSpaces -->|No| CheckAutovis
    AddSpaces --> CheckAutovis
    
    CheckAutovis -->|Yes| SetScope
    CheckAutovis -->|No| InlineFig
    SetScope --> InlineFig
    InlineFig --> IPythonDisplay
```

**show() Function Flow**

Sources: [treescope/_internal/api/ipython_integration.py:172-216]()

The `show()` function [treescope/_internal/api/ipython_integration.py:172-216]() is similar to Python's `print()` but with rich display. It renders multiple objects inline, treating strings as plain text and other objects with their Treescope or IPython representations. Parameters:

- `*args`: Objects to show
- `wrap`: Whether to wrap at line end [default: `False`]
- `space_separated`: Whether to add spaces between objects [default: `True`]
- `autovisualize`: Same as `display()`

## Helper Function: _display_and_maybe_steal()

The core rendering logic is in `_display_and_maybe_steal()` [treescope/_internal/api/ipython_integration.py:51-111](), which both `display()` and the registered formatter use. It handles:

1. **Deferred Rendering Collection**: If `streaming=True`, collects deferred renderings [treescope/_internal/api/ipython_integration.py:76-79]()
2. **Root Repr Method**: Checks for `__treescope_root_repr__` for custom root rendering [treescope/_internal/api/ipython_integration.py:81-85]()
3. **Foldable IR Construction**: Builds the intermediate representation [treescope/_internal/api/ipython_integration.py:87-91]()
4. **Streaming or Static**: Renders either as streaming (with deferred updates) or complete HTML [treescope/_internal/api/ipython_integration.py:92-110]()
5. **Stealable Mode**: Optionally returns HTML for output relocation [treescope/_internal/api/ipython_integration.py:98-99]()

Sources: [treescope/_internal/api/ipython_integration.py:51-111]()

## Magic Commands

Treescope provides two IPython magic commands for cell-level configuration:

### AutovisualizerMagic

```mermaid
graph TB
    CellStart["%%autovisualize [arg]<br/>cell contents..."]
    
    ParseArg{{"Argument<br/>provided?"}}
    EvalArg["Evaluate line as Python:<br/>self.shell.ev(line)"]
    DefaultTrue["autovisualizer = True"]
    
    CheckTrue{{"autovisualizer<br/>is True?"}}
    CheckFalse{{"autovisualizer<br/>is False/None?"}}
    
    GetDefault["autovisualizer =<br/>default_magic_autovisualizer.get()"]
    SetNone["autovisualizer = None"]
    KeepValue["Use evaluated value"]
    
    SetScoped["active_autovisualizer.set_scoped()"]
    RunCell["self.shell.run_cell(cell)"]
    
    CellStart --> ParseArg
    ParseArg -->|Yes| EvalArg
    ParseArg -->|No| DefaultTrue
    
    EvalArg --> CheckTrue
    DefaultTrue --> CheckTrue
    
    CheckTrue -->|Yes| GetDefault
    CheckTrue -->|No| CheckFalse
    CheckFalse -->|Yes| SetNone
    CheckFalse -->|No| KeepValue
    
    GetDefault --> SetScoped
    SetNone --> SetScoped
    KeepValue --> SetScoped
    SetScoped --> RunCell
```

**%%autovisualize Magic Flow**

Sources: [treescope/_internal/api/ipython_integration.py:356-442]()

The `AutovisualizerMagic` class [treescope/_internal/api/ipython_integration.py:357-442]() implements the `%%autovisualize` cell magic. Usage patterns:

1. **No arguments or `True`**: Uses `default_magic_autovisualizer` (usually `ArrayAutovisualizer`)
2. **`False` or `None`**: Disables autovisualization
3. **Expression**: Evaluates to an autovisualizer object

Example:
```python
%%autovisualize
result = {"array": jnp.ones((5, 5))}
result  # Arrays will be visualized
```

### ContextManagerMagic

Sources: [treescope/_internal/api/ipython_integration.py:444-475]()

The `ContextManagerMagic` class [treescope/_internal/api/ipython_integration.py:444-475]() implements the `%%with` cell magic for running cells under any context manager:

```python
%%with abbreviation_threshold.set_scoped(2)
large_object = {"nested": {"data": [1, 2, 3, ...]}}
large_object  # Will abbreviate at depth 2
```

The magic evaluates the line as a Python expression to get a context manager [treescope/_internal/api/ipython_integration.py:473](), then runs the cell within it [treescope/_internal/api/ipython_integration.py:474-475]().

## Setup and Registration Functions

### basic_interactive_setup()

```mermaid
graph TB
    Setup["basic_interactive_setup(<br/>autovisualize_arrays=True,<br/>abbreviation_threshold=None)"]
    
    RegDefault["register_as_default()"]
    RegAutoMagic["register_autovisualize_magic()"]
    RegWithMagic["register_context_manager_magic()"]
    
    CheckAutovis{{"autovisualize_arrays?"}}
    SetAutovis["active_autovisualizer.set_globally(<br/>ArrayAutovisualizer())"]
    
    CheckAbbrev{{"abbreviation_threshold<br/>not None?"}}
    SetAbbrev["abbreviation_threshold.set_globally(value)"]
    
    Setup --> RegDefault
    RegDefault --> RegAutoMagic
    RegAutoMagic --> RegWithMagic
    RegWithMagic --> CheckAutovis
    
    CheckAutovis -->|Yes| SetAutovis
    CheckAutovis -->|No| CheckAbbrev
    SetAutovis --> CheckAbbrev
    
    CheckAbbrev -->|Yes| SetAbbrev
    CheckAbbrev -->|No| Done["Setup Complete"]
    SetAbbrev --> Done
```

**basic_interactive_setup() Flow**

Sources: [treescope/_internal/api/ipython_integration.py:514-546]()

The `basic_interactive_setup()` function [treescope/_internal/api/ipython_integration.py:514-546]() is a convenience function that performs common setup steps:

1. Calls `register_as_default()` to hook into IPython's display system
2. Calls `register_autovisualize_magic()` to enable `%%autovisualize`
3. Calls `register_context_manager_magic()` to enable `%%with`
4. If `autovisualize_arrays=True`, globally enables `ArrayAutovisualizer` [treescope/_internal/api/ipython_integration.py:540-542]()
5. If `abbreviation_threshold` is provided, sets it globally [treescope/_internal/api/ipython_integration.py:545-546]()

This is the recommended way to set up Treescope for interactive use.

### register_autovisualize_magic()

Sources: [treescope/_internal/api/ipython_integration.py:482-495]()

Registers the `AutovisualizerMagic` class with IPython [treescope/_internal/api/ipython_integration.py:495](). Must be called after IPython is available.

### register_context_manager_magic()

Sources: [treescope/_internal/api/ipython_integration.py:498-511]()

Registers the `ContextManagerMagic` class with IPython [treescope/_internal/api/ipython_integration.py:511](). Must be called after IPython is available.

## Contextual Configuration

The IPython integration uses a `ContextualValue` for the default magic autovisualizer:

**default_magic_autovisualizer** [treescope/_internal/api/ipython_integration.py:42-48]()

This determines which autovisualizer is used when `%%autovisualize` is called without arguments. Default value is `ArrayAutovisualizer()`. Users can override it:

```python
treescope.default_magic_autovisualizer.set_globally(my_custom_autovisualizer)
```

For more details on contextual configuration and scoping, see [Configuration and Context](#5.3).

## Colab-Specific Integration

Sources: [treescope/_internal/api/ipython_integration.py:339-352]()

When running in Google Colab, `register_as_default()` disables Colab's custom reprs for strings, ndarrays, and functions [treescope/_internal/api/ipython_integration.py:339-352]() to ensure consistent Treescope rendering.

## API Entry Points Summary

| Function | Purpose | Location |
|----------|---------|----------|
| `basic_interactive_setup()` | One-command setup for interactive use | [treescope/_internal/api/ipython_integration.py:514-546]() |
| `display()` | Display single object with Treescope | [treescope/_internal/api/ipython_integration.py:113-170]() |
| `show()` | Display multiple objects inline | [treescope/_internal/api/ipython_integration.py:172-216]() |
| `register_as_default()` | Hook into IPython's display system | [treescope/_internal/api/ipython_integration.py:218-353]() |
| `register_autovisualize_magic()` | Enable `%%autovisualize` magic | [treescope/_internal/api/ipython_integration.py:482-495]() |
| `register_context_manager_magic()` | Enable `%%with` magic | [treescope/_internal/api/ipython_integration.py:498-511]() |

Sources: [treescope/__init__.py:80-88](), [treescope/_internal/api/ipython_integration.py:1-547]()

---

