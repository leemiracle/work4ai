<!-- source: DeepWiki mcp.deepwiki.com · repo Farama-Foundation/Gymnasium · extra page MujocoEnv Base Class and Rendering · fetched 2026-10-14 -->

# MujocoEnv Base Class and Rendering

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gymnasium/envs/mujoco/mujoco_env.py](gymnasium/envs/mujoco/mujoco_env.py)
- [gymnasium/envs/mujoco/mujoco_py_env.py](gymnasium/envs/mujoco/mujoco_py_env.py)
- [gymnasium/envs/mujoco/mujoco_rendering.py](gymnasium/envs/mujoco/mujoco_rendering.py)
- [gymnasium/envs/mujoco/utils.py](gymnasium/envs/mujoco/utils.py)
- [tests/envs/mujoco/assets/walker2d_v5_uneven_feet.xml](tests/envs/mujoco/assets/walker2d_v5_uneven_feet.xml)
- [tests/envs/mujoco/test_mujoco_custom_env.py](tests/envs/mujoco/test_mujoco_custom_env.py)
- [tests/envs/mujoco/test_mujoco_rendering.py](tests/envs/mujoco/test_mujoco_rendering.py)

</details>



This page details the internal workings of the `MujocoEnv` base class in Gymnasium, focusing on its structure, how it loads MuJoCo models, handles `frame_skip`, manages the simulation state with `set_state` and `do_simulation`, and provides rendering capabilities through the `MujocoRenderer` for both offscreen and windowed viewers.

## MujocoEnv Base Class

The `MujocoEnv` class [gymnasium/envs/mujoco/mujoco_env.py:35-36]() serves as the foundational class for all MuJoCo-based environments within Gymnasium. It encapsulates the core logic for interacting with the MuJoCo physics engine.

### Initialization and Model Loading

When a `MujocoEnv` is instantiated, it performs several key initialization steps:
1.  **Path Expansion**: The `model_path` provided during initialization is expanded to a full path using `expand_model_path()` [gymnasium/envs/mujoco/mujoco_env.py:21-32](). This function handles relative paths, user home directory shortcuts (`~`), and ensures the file exists.
2.  **Simulation Initialization**: The `_initialize_simulation()` method [gymnasium/envs/mujoco/mujoco_env.py:118-130]() is called to load the MuJoCo model from the XML path and create the corresponding `mujoco.MjModel` and `mujoco.MjData` objects.
    *   Crucially, it ensures that the offscreen framebuffer dimensions (`model.vis.global_.offwidth`, `model.vis.global_.offheight`) are never shrunk below the sizes specified in the XML model, but can be grown if the requested `width` or `height` for rendering is larger [gymnasium/envs/mujoco/mujoco_env.py:126-128](). This prevents issues where a user-supplied high-resolution renderer might be inadvertently downscaled [tests/envs/mujoco/test_mujoco_custom_env.py:156-162]().
3.  **Initial State Storage**: The initial generalized positions (`qpos`) and velocities (`qvel`) are stored as `self.init_qpos` and `self.init_qvel` [gymnasium/envs/mujoco/mujoco_env.py:81-82](). These are used during environment resets.
4.  **Action Space Definition**: The `_set_action_space()` method [gymnasium/envs/mujoco/mujoco_env.py:112-116]() defines the environment's action space based on the MuJoCo model's actuator control ranges (`self.model.actuator_ctrlrange`). It creates a `spaces.Box` with appropriate `low` and `high` bounds.
5.  **Renderer Initialization**: A `MujocoRenderer` object is instantiated to handle all rendering operations [gymnasium/envs/mujoco/mujoco_env.py:98-110](). This renderer is configured with the MuJoCo model and data, along with rendering parameters like `width`, `height`, `camera_id`, and `camera_name`.

```mermaid
graph TD
    A[MujocoEnv.__init__] --> B{Expand model_path};
    B --> C[Call _initialize_simulation];
    C --> D[mujoco.MjModel.from_xml_path];
    D --> E[Adjust model.vis.global_.offwidth/offheight];
    E --> F[mujoco.MjData(model)];
    F --> G[Store init_qpos/qvel];
    G --> H[Call _set_action_space];
    H --> I[Define spaces.Box from actuator_ctrlrange];
    I --> J[Instantiate MujocoRenderer];
    J --> K[Store self.mujoco_renderer];
    K --> L[MujocoEnv Initialized];

    style A fill:#f9f,stroke:#333,stroke-width:2px;
    style L fill:#f9f,stroke:#333,stroke-width:2px;
```
**Diagram: `MujocoEnv` Initialization Flow**
Sources: [gymnasium/envs/mujoco/mujoco_env.py:35-110](), [gymnasium/envs/mujoco/mujoco_env.py:21-32](), [gymnasium/envs/mujoco/mujoco_env.py:118-130](), [gymnasium/envs/mujoco/mujoco_env.py:126-128](), [tests/envs/mujoco/test_mujoco_custom_env.py:156-162](), [gymnasium/envs/mujoco/mujoco_env.py:81-82](), [gymnasium/envs/mujoco/mujoco_env.py:112-116]()

### `frame_skip`

The `frame_skip` parameter [gymnasium/envs/mujoco/mujoco_env.py:41]() determines how many MuJoCo simulation steps are performed for each single `step()` call in the Gymnasium environment.
*   During a `step()` operation, the `_step_mujoco_simulation()` method [gymnasium/envs/mujoco/mujoco_env.py:144-156]() is called, which in turn executes `mujoco.mj_step(self.model, self.data, nstep=n_frames)` [gymnasium/envs/mujoco/mujoco_env.py:150]() where `n_frames` is `frame_skip`.
*   This allows for controlling the granularity of the simulation relative to the agent's actions. A higher `frame_skip` means the agent's actions persist for longer in the simulation, potentially speeding up training but also making the environment dynamics coarser.

### `set_state` and `do_simulation`

*   **`set_state(qpos, qvel)`**: This method [gymnasium/envs/mujoco/mujoco_env.py:132-143]() allows direct manipulation of the MuJoCo model's generalized positions (`qpos`) and velocities (`qvel`). It copies the provided `qpos` and `qvel` arrays into `self.data.qpos` and `self.data.qvel` respectively, and then calls `mujoco.mj_forward()` to update the physics state based on these new values. This is crucial for resetting the environment to a specific configuration or for testing purposes.
*   **`do_simulation(ctrl, n_frames)`**: This method is typically implemented by subclasses of `MujocoEnv` and internally calls `_step_mujoco_simulation()` [gymnasium/envs/mujoco/mujoco_env.py:144-156](). It applies the control input `ctrl` to the MuJoCo model's actuators (`self.data.ctrl[:] = ctrl`) and then advances the simulation by `n_frames` steps using `mujoco.mj_step()` [gymnasium/envs/mujoco/mujoco_env.py:150](). After the simulation steps, `mujoco.mj_rnePostConstraint()` is called to compute force-related quantities if necessary [gymnasium/envs/mujoco/mujoco_env.py:155-156]().

### Resetting the Environment

The `reset()` method [gymnasium/envs/mujoco/mujoco_env.py:173-187]() in `MujocoEnv` first calls `super().reset()` for general Gymnasium environment reset logic. Then, it resets the MuJoCo data using `mujoco.mj_resetData(self.model, self.data)` [gymnasium/envs/mujoco/mujoco_env.py:180](). The actual environment-specific reset logic, such as setting initial joint positions and velocities, is delegated to the abstract `reset_model()` method, which must be implemented by subclasses. The `set_state` method is often used within `reset_model()` to apply the initial `qpos` and `qvel` [tests/envs/mujoco/test_mujoco_custom_env.py:77-79]().

## MuJoCo Renderer

The `MujocoRenderer` class [gymnasium/envs/mujoco/mujoco_rendering.py:43-848]() is responsible for handling all rendering aspects of MuJoCo environments. It acts as an interface between the `MujocoEnv` and the underlying MuJoCo rendering utilities.

### `MujocoRenderer` Internals

The `MujocoRenderer` is initialized with the MuJoCo `model` and `data` objects, along with rendering configuration parameters. It manages:
*   **Scene and Camera**: It initializes `mujoco.MjvScene`, `mujoco.MjvCamera`, `mujoco.MjvOption`, and `mujoco.MjvPerturb` objects [gymnasium/envs/mujoco/mujoco_rendering.py:63-67]() which are fundamental for defining what is rendered and how the camera views it.
*   **Rendering Context**: It creates a `mujoco.MjrContext` [gymnasium/envs/mujoco/mujoco_rendering.py:76]() which is the main rendering context for MuJoCo.
*   **Visual Options**: It applies any provided `visual_options` to the `self.vopt.flags` [gymnasium/envs/mujoco/mujoco_rendering.py:69-71](), allowing customization of rendering features like showing contacts, joint frames, etc.
*   **Markers and Overlays**: It provides methods `add_marker()` [gymnasium/envs/mujoco/mujoco_rendering.py:94]() and `add_overlay()` [gymnasium/envs/mujoco/mujoco_rendering.py:86]() to dynamically add visual markers and text overlays to the rendered scene. The `_add_marker_to_scene()` method [gymnasium/envs/mujoco/mujoco_rendering.py:96-117]() handles adding markers to the `MjvScene`, with a legacy mode for older MuJoCo versions [gymnasium/envs/mujoco/mujoco_rendering.py:100-101]().

### Offscreen and Window Viewers

The `MujocoRenderer` internally uses different viewer implementations based on the `render_mode`:

#### OffScreenViewer

*   The `OffScreenViewer` class [gymnasium/envs/mujoco/mujoco_rendering.py:174-175]() is used for offscreen rendering, typically for `rgb_array`, `depth_array`, or `rgbd_tuple` render modes.
*   It dynamically selects an OpenGL backend (`glfw`, `egl`, or `osmesa`) based on the `MUJOCO_GL` environment variable [gymnasium/envs/mujoco/mujoco_rendering.py:203-206]().
*   It initializes a camera (`self.cam`) with a free type and sets its lookat point and distance based on the model's geometry [gymnasium/envs/mujoco/mujoco_rendering.py:196-201]().
*   The `render()` method of `OffScreenViewer` captures the scene and returns it as a NumPy array. The dimensions of this array correspond to the `width` and `height` specified during initialization [tests/envs/mujoco/test_mujoco_rendering.py:54]().

#### Windowed Viewer (Human Rendering)

*   For `human` render mode, a windowed viewer is used, which typically relies on GLFW for creating and managing the display window.
*   This viewer provides interactive control, allowing users to manipulate the camera, pause the simulation, and inspect the environment in real-time.
*   The `MujocoRenderer` manages the lifecycle of this window, including its creation, updating, and closing.

```mermaid
graph TD
    A[MujocoEnv] --> B[self.mujoco_renderer: MujocoRenderer];

    subgraph MujocoRenderer
        B --> C[model: mujoco.MjModel];
        B --> D[data: mujoco.MjData];
        B --> E[self.render(render_mode)];
        E --> F{render_mode == "human"?};
        F -- Yes --> G[Windowed Viewer (e.g., GLFW)];
        F -- No --> H[OffScreenViewer];
        H --> I{OpenGL Backend Selection};
        I --> J[GLContext (glfw, egl, or osmesa)];
        J --> K[mujoco.MjrContext];
        K --> L[Render to buffer];
        L --> M[Return numpy array (rgb_array, depth_array, rgbd_tuple)];
        G --> N[Display in window];
    end

    subgraph OffScreenViewer
        H --> O[self.cam: mujoco.MjvCamera];
        H --> P[self.scn: mujoco.MjvScene];
        H --> Q[self.vopt: mujoco.MjvOption];
    end

    style A fill:#f9f,stroke:#333,stroke-width:2px;
    style B fill:#f9f,stroke:#333,stroke-width:2px;
    style G fill:#f9f,stroke:#333,stroke-width:2px;
    style M fill:#f9f,stroke:#333,stroke-width:2px;
    style N fill:#f9f,stroke:#333,stroke-width:2px;
```
**Diagram: `MujocoRenderer` Data Flow**
Sources: [gymnasium/envs/mujoco/mujoco_env.py:98-110](), [gymnasium/envs/mujoco/mujoco_rendering.py:43-848](), [gymnasium/envs/mujoco/mujoco_rendering.py:63-67](), [gymnasium/envs/mujoco/mujoco_rendering.py:76](), [gymnasium/envs/mujoco/mujoco_rendering.py:69-71](), [gymnasium/envs/mujoco/mujoco_rendering.py:94](), [gymnasium/envs/mujoco/mujoco_rendering.py:86](), [gymnasium/envs/mujoco/mujoco_rendering.py:96-117](), [gymnasium/envs/mujoco/mujoco_rendering.py:100-101](), [gymnasium/envs/mujoco/mujoco_rendering.py:174-175](), [gymnasium/envs/mujoco/mujoco_rendering.py:203-206](), [gymnasium/envs/mujoco/mujoco_rendering.py:196-201](), [tests/envs/mujoco/test_mujoco_rendering.py:54]()

### Rendering Modes

The `MujocoEnv` supports several `render_mode` options [gymnasium/envs/mujoco/mujoco_env.py:57]():
*   `"human"`: Renders the environment to an interactive window.
*   `"rgb_array"`: Returns an RGB image of the current observation as a NumPy array.
*   `"depth_array"`: Returns a depth map of the current observation as a NumPy array.
*   `"rgbd_tuple"`: Returns a tuple containing both the RGB image and the depth map [tests/envs/mujoco/test_mujoco_rendering.py:168-186]().

The `render()` method of `MujocoEnv` [gymnasium/envs/mujoco/mujoco_env.py:157-161]() delegates the actual rendering to `self.mujoco_renderer.render(self.render_mode)`.

### Closing the Renderer

The `close()` method of `MujocoEnv` [gymnasium/envs/mujoco/mujoco_env.py:163-167]() ensures that the `mujoco_renderer` is properly closed, releasing any resources (like OpenGL contexts or GLFW windows) it might be holding. This is crucial for preventing resource leaks, especially in environments with windowed rendering.

Sources: [gymnasium/envs/mujoco/mujoco_env.py:35-190](), [gymnasium/envs/mujoco/mujoco_rendering.py:1-206](), [gymnasium/envs/mujoco/utils.py:1-76](), [tests/envs/mujoco/test_mujoco_custom_env.py:1-178](), [tests/envs/mujoco/test_mujoco_rendering.py:1-186]()

---

