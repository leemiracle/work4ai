<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/mujoco · extra page Filament Renderer Backend · fetched 2026-10-26 -->

# Filament Renderer Backend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [doc/programming/rendering.rst](doc/programming/rendering.rst)
- [include/mujoco/mjrfilament.h](include/mujoco/mjrfilament.h)
- [python/mujoco/render_filament_generated.cc.inc](python/mujoco/render_filament_generated.cc.inc)
- [sample/render.cc](sample/render.cc)
- [src/experimental/filament/CMakeLists.txt](src/experimental/filament/CMakeLists.txt)
- [src/experimental/filament/compat/scene_bridge.cc](src/experimental/filament/compat/scene_bridge.cc)
- [src/experimental/filament/compat/scene_bridge.h](src/experimental/filament/compat/scene_bridge.h)
- [src/experimental/filament/compat/scene_geom_util.cc](src/experimental/filament/compat/scene_geom_util.cc)
- [src/experimental/filament/compat/scene_geom_util.h](src/experimental/filament/compat/scene_geom_util.h)
- [src/experimental/filament/mjr_compat.cc](src/experimental/filament/mjr_compat.cc)
- [src/experimental/studio/ux/imgui_widgets.h](src/experimental/studio/ux/imgui_widgets.h)
- [src/render/filament/assets/decor.mat](src/render/filament/assets/decor.mat)
- [src/render/filament/assets/decor_fade.mat](src/render/filament/assets/decor_fade.mat)
- [src/render/filament/assets/pbr.mat](src/render/filament/assets/pbr.mat)
- [src/render/filament/assets/pbr_packed.mat](src/render/filament/assets/pbr_packed.mat)
- [src/render/filament/assets/phong_2d.mat](src/render/filament/assets/phong_2d.mat)
- [src/render/filament/assets/phong_2d_fade.mat](src/render/filament/assets/phong_2d_fade.mat)
- [src/render/filament/assets/phong_2d_uv.mat](src/render/filament/assets/phong_2d_uv.mat)
- [src/render/filament/assets/phong_2d_uv_fade.mat](src/render/filament/assets/phong_2d_uv_fade.mat)
- [src/render/filament/core/builtins.h](src/render/filament/core/builtins.h)
- [src/render/filament/core/color_grading_options.h](src/render/filament/core/color_grading_options.h)
- [src/render/filament/core/filament_context.cc](src/render/filament/core/filament_context.cc)
- [src/render/filament/core/filament_context.h](src/render/filament/core/filament_context.h)
- [src/render/filament/core/filament_platform_factory.cc](src/render/filament/core/filament_platform_factory.cc)
- [src/render/filament/core/filament_platform_factory.h](src/render/filament/core/filament_platform_factory.h)
- [src/render/filament/core/imgui_editor.cc](src/render/filament/core/imgui_editor.cc)
- [src/render/filament/core/light.cc](src/render/filament/core/light.cc)
- [src/render/filament/core/light.h](src/render/filament/core/light.h)
- [src/render/filament/core/material_manager.cc](src/render/filament/core/material_manager.cc)
- [src/render/filament/core/material_manager.h](src/render/filament/core/material_manager.h)
- [src/render/filament/core/object_manager.cc](src/render/filament/core/object_manager.cc)
- [src/render/filament/core/object_manager.h](src/render/filament/core/object_manager.h)
- [src/render/filament/core/render_target.h](src/render/filament/core/render_target.h)
- [src/render/filament/core/scene_view.cc](src/render/filament/core/scene_view.cc)
- [src/render/filament/core/texture.cc](src/render/filament/core/texture.cc)
- [src/render/filament/core/texture.h](src/render/filament/core/texture.h)
- [src/render/filament/core/types.h](src/render/filament/core/types.h)
- [src/render/filament/mjrfilament.cc](src/render/filament/mjrfilament.cc)
- [src/render/filament/support/filament_util.cc](src/render/filament/support/filament_util.cc)
- [src/render/filament/support/filament_util.h](src/render/filament/support/filament_util.h)
- [src/render/filament/support/mjrf_ptr.h](src/render/filament/support/mjrf_ptr.h)
- [src/render/filament/support/model_lights.cc](src/render/filament/support/model_lights.cc)
- [src/render/filament/support/model_lights.h](src/render/filament/support/model_lights.h)
- [src/render/filament/support/model_renderables.cc](src/render/filament/support/model_renderables.cc)
- [src/render/filament/support/model_renderables.h](src/render/filament/support/model_renderables.h)
- [src/render/filament/support/model_resources.cc](src/render/filament/support/model_resources.cc)
- [src/render/filament/support/model_resources.h](src/render/filament/support/model_resources.h)
- [src/render/filament/support/renderer.cc](src/render/filament/support/renderer.cc)
- [src/render/filament/support/renderer.h](src/render/filament/support/renderer.h)
- [test/render/model_resources_test.cc](test/render/model_resources_test.cc)
- [test/render/renderer_test.cc](test/render/renderer_test.cc)
- [test/render/testdata/BUILD.bazel](test/render/testdata/BUILD.bazel)
- [test/sample/render_test.sh](test/sample/render_test.sh)

</details>



The purpose of this page is to document the **Filament Renderer Backend** (`src/render/filament`) in MuJoCo, which provides a high-performance, modern PBR (Physically Based Rendering) pipeline built on Google's Filament graphics engine. This backend implements the `mjrf_*` API (`include/mujoco/mjrfilament.h` [include/mujoco/mjrfilament.h:1-421]()) and includes compatibility layers (`src/experimental/filament/`) to support classic rendering workflows using Filament.

---

## Architecture and Core Managers

The Filament renderer backend is organized around core manager classes that wrap and interact with Google's Filament engine components. `FilamentContext` owns the core `filament::Engine`, `ObjectManager`, and `MaterialManager`.

```
+-------------------------------------------------------------+
|                     FilamentContext                         |
|  - Manages filament::Engine (OpenGL / Vulkan backend)       |
|  - Owns ObjectManager, MaterialManager, ReflectionManager   |
+-------------------------------------------------------------+
        |                          |                  |
        v                          v                  v
+------------------+     +-------------------+     +------------------+
|  ObjectManager   |     |  MaterialManager  |     |   SceneView      |
|  - Manages meshes|     |  - PBR / Phong    |     |  - filament::View|
|  - Textures, etc.|     |  - Material cache |     |  - Cameras/Lights|
+------------------+     +-------------------+     +------------------+
```
Sources: `src/render/filament/mjrfilament.cc`, `include/mujoco/mjrfilament.h`, `src/render/filament/core/material_manager.cc`

- **`FilamentContext`**: Initialized via `mjrf_createContext` [src/render/filament/mjrfilament.cc:134-136](), it establishes the underlying graphics API (OpenGL or Vulkan) and manages lifecycle allocations.
- **`ObjectManager`**: Manages low-level graphics assets like geometries, buffers, and primitive bindings.
- **`MaterialManager`**: Caches and manages `filament::MaterialInstance` objects based on material types (PBR, Phong, Unlit UI, transparent variants, etc.) and vertex attributes [src/render/filament/core/material_manager.cc:73-117]().
- **`SceneView`**: Implements `mjrfScene` wrapping `filament::Scene`, multiple `filament::View` instances (main, depth/segmentation, reflections), and camera management [src/render/filament/core/scene_view.cc:140-167]().

---

## Renderables, Lights, and Textures

The backend maps MuJoCo model elements and visualization items (`mjvGeom`, `mjvScene`) to Filament entities using specialized support and core classes.

### Renderables and Geometry Processing
- **`ModelRenderables`**: Traverses the model and scene data to generate and update renderable entities [src/render/filament/support/model_renderables.cc:165-184]().
- **Primitive Geometries**: Geometries like boxes, spheres, cylinders, and capsules (`mjGEOM_SPHERE`, `mjGEOM_BOX`, etc.) are mapped to procedural meshes with configurable stacks, slices, and quads (`vis.quality.numstacks`, `vis.quality.numslices`) [src/experimental/filament/compat/scene_geom_util.cc:31-132]().
- **Flex and Skin Meshes**: Flex elements and skins are handled dynamically, updating vertex positions and index buffers per frame [src/experimental/filament/compat/scene_bridge.cc:122-152]().

### Lighting and Shadows
- **`ModelLights`**: Configures scene lights, directional/point lights, and camera-aligned headlights based on model specifications and render requests [src/experimental/filament/compat/scene_bridge.cc:54]().
- Shadows and reflections are managed at the `SceneView` level, supporting shadow mapping, cascade configurations, and reflection planes [src/render/filament/core/scene_view.cc:161-167]().

### Textures and Materials
- **`Texture`**: Wraps `filament::Texture` for 2D, cubemap, and compressed texture formats, supporting uploads of `mjrfTextureData` [src/render/filament/mjrfilament.cc:148-207]().
- **Material Selection**: `MaterialManager::GetMaterialType` chooses between PBR packed, standard PBR, Phong, and fade/transparent variants depending on texture availability, specular/roughness properties, and alpha values [src/render/filament/core/material_manager.cc:119-195]().

---

## The `mjrfilament` API

The public C interface for the Filament renderer is defined in `include/mujoco/mjrfilament.h` [include/mujoco/mjrfilament.h:1-421](). It provides opaque handles and request structures for asynchronous rendering:

| Opaque Handle / Struct | Purpose |
| :--- | :--- |
| `mjrfContext` | Rendering context wrapping `filament::Engine`. |
| `mjrfScene` | Scene container wrapping `filament::Scene` and `filament::View`. |
| `mjrfMesh` | Vertex and index buffer container. |
| `mjrfTexture` | Texture object wrapper. |
| `mjrfRenderable` | Renderable object container. |
| `mjrfRenderTarget` | Offscreen render target attachment. |
| `mjrfRenderRequest` | Parameters for a single render operation (viewport, camera, draw mode, shadows, headlight) [include/mujoco/mjrfilament.h:80-96](). |

```
+------------------+         mjrf_render()         +--------------------+
| mjrfRenderRequest| ----------------------------> | Filament Engine    |
| - camera         |                               | - Asynchronous     |
| - viewport       |         mjrfReadRequest       |   queue execution  |
| - draw_mode      | <---------------------------- | - Readback pixels  |
+------------------+      mjrf_waitForFrame()      +--------------------+
```
Sources: `include/mujoco/mjrfilament.h`, `src/render/filament/mjrfilament.cc`

---

## Compatibility Layer (`mjr` to `mjrf`)

To allow applications built around classic MuJoCo rendering (`mjr_*`) to use Filament without rewriting their rendering loops, `src/experimental/filament/` provides a drop-in compatibility layer (`mjr_compat.cc`) [src/experimental/filament/mjr_compat.cc:1-327]() and the `SceneBridge` class [src/experimental/filament/compat/scene_bridge.cc:43-55]().

```
+-------------------------------------------------------+
|                Classic mjr_* API Calls                |
|       (mjr_makeContext, mjr_render, mjr_readPixels)   |
+-------------------------------------------------------+
                           |
                           v
+-------------------------------------------------------+
|         experimental/filament/mjr_compat.cc           |
|  - CompatContext thread-local state wrapper           |
+-------------------------------------------------------+
                           |
                           v
+-------------------------------------------------------+
|                      SceneBridge                      |
|  - Translates mjvScene geoms -> mjrfRenderable        |
|  - Manages ModelResources, ModelLights, SceneObjects  |
+-------------------------------------------------------+
                           |
                           v
+-------------------------------------------------------+
|                    mjrf_* Backend                     |
+-------------------------------------------------------+
```
Sources: `src/experimental/filament/mjr_compat.cc`, `src/experimental/filament/compat/scene_bridge.cc`, `src/experimental/filament/CMakeLists.txt`

- **`SceneBridge`**: Bridges `mjvScene` objects to Filament renderables [src/experimental/filament/compat/scene_bridge.cc:43-112](). During `SceneBridge::Update`, it clears previous frame drawables, processes `mjvGeom` items (including flex vertices/edges), updates materials, and computes projection/view matrices using `CalculateClipFromWorld` [src/experimental/filament/compat/scene_bridge.cc:73-177]().
- **Offscreen Readback**: `CompatContext::ReadPixels` allocates `mjrfRenderTarget` attachments for RGB and depth formats, submits render and read requests via `mjrf_render`, and blocks on `mjrf_waitForFrame` [src/experimental/filament/compat/scene_bridge.cc:119-184]().

Sources:
- `src/experimental/filament/CMakeLists.txt`
- `src/experimental/filament/compat/scene_bridge.cc`
- `src/experimental/filament/compat/scene_geom_util.cc`
- `src/render/filament/support/model_renderables.cc`
- `src/render/filament/core/material_manager.cc`
- `include/mujoco/mjrfilament.h`
- `test/render/renderer_test.cc`
- `src/render/filament/core/scene_view.cc`
- `src/render/filament/mjrfilament.cc`
- `src/experimental/filament/mjr_compat.cc`
- `sample/render.cc`
- `src/experimental/filament/compat/scene_bridge.h`

---

