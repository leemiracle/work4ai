<!-- source: DeepWiki mcp.deepwiki.com · repo openai/gym3 · page 5 Visualization and Interaction · fetched 2026-10-26 -->

# Visualization and Interaction

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gym3/interactive.py](gym3/interactive.py)
- [gym3/internal/renderer.py](gym3/internal/renderer.py)
- [gym3/viewer.py](gym3/viewer.py)

</details>



This document covers gym3's visualization and interaction capabilities, which enable human observation and control of environments through desktop windows. The system provides tools for displaying environment state visually and accepting keyboard input from users.

For information about recording environment data to files, see [Advanced Features](#6). For details about environment execution patterns, see [Environment Execution](#4).

## Overview

gym3's visualization system consists of three main components that work together to provide rich interactive experiences:

```mermaid
graph TB
    subgraph "High-Level Interfaces"
        ViewerWrapper["ViewerWrapper<br/>Display Only"]
        Interactive["Interactive<br/>Human Control"]
    end
    
    subgraph "Core Rendering Engine"
        Renderer["Renderer<br/>OpenGL Backend"]
        ModernGL["ModernGL<br/>Context Management"]
        GLFW["GLFW<br/>Window System"]
        FontSystem["Font System<br/>font.bin"]
    end
    
    subgraph "Environment Data"
        Env["gym3.Env"]
        Observations["observations"]
        InfoDict["info['rgb']"]
    end
    
    subgraph "User Interface"
        Window["Desktop Window"]
        Keyboard["Keyboard Input"]
        Display["Visual Output"]
    end
    
    Env --> Observations
    Env --> InfoDict
    Observations --> ViewerWrapper
    InfoDict --> ViewerWrapper
    Observations --> Interactive
    InfoDict --> Interactive
    
    ViewerWrapper --> Renderer
    Interactive --> Renderer
    
    Renderer --> ModernGL
    Renderer --> GLFW
    Renderer --> FontSystem
    
    ModernGL --> Window
    GLFW --> Window
    GLFW --> Keyboard
    Renderer --> Display
    
    Keyboard --> Interactive
```

**System Architecture Overview**

Sources: [gym3/viewer.py:1-138](), [gym3/interactive.py:1-278](), [gym3/internal/renderer.py:1-307]()

## Core Components

### ViewerWrapper

The `ViewerWrapper` class provides a simple way to display environment images in a window without user interaction capabilities. It wraps any gym3 environment and automatically displays frames after each action.

| Feature | Description |
|---------|-------------|
| **Purpose** | Display-only environment visualization |
| **Data Source** | Observations or info dict RGB data |
| **Controls** | Basic playback controls (pause, fast mode, overlay) |
| **Threading** | Synchronous with environment steps |

Key characteristics:
- Inherits from `gym3.Wrapper`
- Supports both observation-based and info-based image sources
- Built-in frame rate limiting
- Overlay system for help text and status

Sources: [gym3/viewer.py:18-137]()

### Interactive

The `Interactive` class enables human-in-the-loop environment control through keyboard input. Unlike `ViewerWrapper`, it allows users to control the environment directly.

| Feature | Description |
|---------|-------------|
| **Purpose** | Human control of environment actions |
| **Input Method** | Keyboard mapping to environment actions |
| **Execution Modes** | Synchronous and asynchronous |
| **Display** | Episode statistics and environment info |

Key characteristics:
- Requires `keys_to_act` function for keyboard-to-action mapping
- Supports both synchronous (step-by-step) and asynchronous (real-time) control
- Automatically tracks episode statistics
- Built-in episode completion display

Sources: [gym3/interactive.py:18-277]()

### Renderer

The `Renderer` class provides the low-level OpenGL rendering engine used by both high-level interfaces. It handles window management, graphics rendering, and input processing.

| Component | Technology |
|-----------|------------|
| **Graphics API** | OpenGL 3.3 Core Profile |
| **Window System** | GLFW |
| **Context Management** | ModernGL |
| **Font Rendering** | Custom bitmap font system |

Sources: [gym3/internal/renderer.py:88-307]()

## Rendering Pipeline

The visualization system follows a structured rendering pipeline from environment data to screen display:

```mermaid
flowchart TD
    subgraph "Data Extraction"
        EnvStep["env.act(action)"]
        Observe["env.observe()"]
        GetInfo["env.get_info()"]
    end
    
    subgraph "Image Acquisition"
        ObKey["ob[ob_key][env_index]"]
        InfoKey["info[env_index][info_key]"]
        ImageValidation["Validate RGB uint8<br/>(H,W,3) format"]
    end
    
    subgraph "Renderer Operations"
        RendererStart["renderer.start()"]
        DrawBitmap["renderer.draw_bitmap()"]
        DrawText["renderer.draw_text()"]
        RendererFinish["renderer.finish()"]
    end
    
    subgraph "OpenGL Pipeline"
        LoadTexture["Load image as OpenGL texture"]
        BitmapShader["Apply bitmap vertex/fragment shaders"]
        TextFont["Convert text to RGBA via font.bin"]
        BlendAlpha["Alpha blending for overlays"]
    end
    
    subgraph "Window Output"
        SwapBuffers["glfw.swap_buffers()"]
        Display["Display to screen"]
        InputEvents["Process keyboard events"]
    end
    
    EnvStep --> Observe
    EnvStep --> GetInfo
    Observe --> ObKey
    GetInfo --> InfoKey
    ObKey --> ImageValidation
    InfoKey --> ImageValidation
    
    ImageValidation --> RendererStart
    RendererStart --> DrawBitmap
    RendererStart --> DrawText
    DrawBitmap --> LoadTexture
    DrawText --> TextFont
    LoadTexture --> BitmapShader
    TextFont --> BlendAlpha
    BitmapShader --> BlendAlpha
    
    BlendAlpha --> RendererFinish
    RendererFinish --> SwapBuffers
    SwapBuffers --> Display
    SwapBuffers --> InputEvents
```

**Rendering Pipeline from Environment Data to Display**

Sources: [gym3/viewer.py:53-93](), [gym3/interactive.py:111-175](), [gym3/internal/renderer.py:195-284]()

## Usage Patterns

### Display-Only Visualization

For simple environment visualization without user interaction:

```python
# Basic usage pattern
env = SomeGym3Env()
env = ViewerWrapper(env, env_index=0, info_key="rgb")
# Viewer automatically displays frames during env.act() calls
```

The `ViewerWrapper` integrates into the environment's `act()` method, automatically displaying frames and handling basic controls like pause (`P`), fast mode (`F`), and overlay toggle (`O`).

Sources: [gym3/viewer.py:125-137]()

### Interactive Control

For human control of environment actions:

```python
# Interactive usage pattern  
env = SomeGym3Env(num=1)  # Must be single environment
interactive = Interactive(env, keys_to_act=my_key_mapping)
interactive.run()  # Enters main loop until window closed
```

The `Interactive` class requires a `keys_to_act` function that maps keyboard key names to environment actions. It supports both synchronous (step-by-step) and asynchronous (real-time) execution modes.

Sources: [gym3/interactive.py:268-277]()

## Technical Architecture

### Graphics System Stack

The rendering system is built on modern OpenGL with careful abstraction layers:

```mermaid
graph TB
    subgraph "Application Layer"
        ViewerWrapper_act["ViewerWrapper.act()"]
        Interactive_run["Interactive.run()"]
    end
    
    subgraph "Renderer API"
        start["Renderer.start()"]
        draw_bitmap["Renderer.draw_bitmap()"]
        draw_text["Renderer.draw_text()"] 
        finish["Renderer.finish()"]
    end
    
    subgraph "OpenGL Abstraction"
        mgl_context["moderngl.Context"]
        mgl_texture["moderngl.Texture"]
        mgl_shader["moderngl.Program"]
        mgl_vao["moderngl.VertexArray"]
    end
    
    subgraph "System Libraries"
        glfw_window["glfw window management"]
        opengl_driver["OpenGL 3.3 driver"]
        font_bin["font.bin bitmap data"]
    end
    
    ViewerWrapper_act --> start
    ViewerWrapper_act --> draw_bitmap
    ViewerWrapper_act --> finish
    
    Interactive_run --> start
    Interactive_run --> draw_bitmap
    Interactive_run --> draw_text
    Interactive_run --> finish
    
    draw_bitmap --> mgl_texture
    draw_bitmap --> mgl_shader
    draw_text --> font_bin
    draw_text --> mgl_texture
    
    start --> glfw_window
    finish --> glfw_window
    
    mgl_context --> opengl_driver
    mgl_texture --> opengl_driver
    mgl_shader --> opengl_driver
    mgl_vao --> opengl_driver
```

**Low-Level Graphics Architecture**

Sources: [gym3/internal/renderer.py:96-161](), [gym3/internal/renderer.py:152-154]()

### Font Rendering System

Text rendering uses a custom bitmap font system for reliable cross-platform display:

| Component | Details |
|-----------|---------|
| **Font Data** | Pre-rendered bitmap fonts in `font.bin` |
| **Text Processing** | `_str_to_array()` converts strings to character arrays |
| **Rendering** | `_convert_ascii_to_rgba()` maps characters to RGBA bitmaps |
| **Sizes** | Multiple font sizes available (16px, 32px, etc.) |

The font system converts text strings to numpy arrays, then maps each character to its corresponding bitmap in the font atlas, producing RGBA images that can be rendered as textures.

Sources: [gym3/internal/renderer.py:14-51](), [gym3/internal/renderer.py:253-284]()

### Input Processing

Keyboard input flows through GLFW's event system with custom key mapping:

```mermaid
sequenceDiagram
    participant GLFW as "GLFW Events"
    participant Renderer as "Renderer"
    participant Interactive as "Interactive"
    participant Environment as "gym3.Env"
    
    GLFW->>Renderer: Key press/release events
    Renderer->>Renderer: Update _keys_clicked/_keys_pressed sets
    Interactive->>Renderer: renderer.start()
    Renderer->>Interactive: Return (keys_clicked, keys_pressed)
    Interactive->>Interactive: keys_to_act(keys)
    Interactive->>Environment: env.act(action)
    Environment->>Interactive: New observation/reward
    Interactive->>Renderer: draw_bitmap()/draw_text()
    Interactive->>Renderer: renderer.finish()
```

**Input Processing Flow**

Sources: [gym3/internal/renderer.py:162-173](), [gym3/interactive.py:200-266]()

---

