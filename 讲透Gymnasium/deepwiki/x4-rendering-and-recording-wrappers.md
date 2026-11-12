<!-- source: DeepWiki mcp.deepwiki.com · repo Farama-Foundation/Gymnasium · extra page Rendering and Recording Wrappers · fetched 2026-10-14 -->

# Rendering and Recording Wrappers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gymnasium/wrappers/rendering.py](gymnasium/wrappers/rendering.py)
- [gymnasium/wrappers/vector/__init__.py](gymnasium/wrappers/vector/__init__.py)
- [gymnasium/wrappers/vector/rendering.py](gymnasium/wrappers/vector/rendering.py)
- [tests/utils/test_save_video.py](tests/utils/test_save_video.py)
- [tests/wrappers/test_human_rendering.py](tests/wrappers/test_human_rendering.py)
- [tests/wrappers/test_record_episode_statistics.py](tests/wrappers/test_record_episode_statistics.py)
- [tests/wrappers/test_record_video.py](tests/wrappers/test_record_video.py)
- [tests/wrappers/vector/test_record_video.py](tests/wrappers/vector/test_record_video.py)

</details>



This page provides detailed documentation for Gymnasium's rendering and recording wrappers, including `HumanRendering`, `RecordVideo`, `RecordEpisodeStatistics`, and related utilities like `save_video`. These wrappers are essential for visualizing environment interactions, debugging agents, and generating demonstrations.

## RenderCollection Wrapper

The `RenderCollection` wrapper [gymnasium/wrappers/rendering.py:34-164]() collects rendered frames of an environment into a list. This allows users to retrieve all frames generated since the last `render()` call or `reset()` call, depending on configuration. It is designed for single environments and does not have a vector version.

### How it Works

The `RenderCollection` wrapper stores frames in an internal `frame_list` [gymnasium/wrappers/rendering.py:124]().
- When `step()` is called, it performs the step in the base environment and then appends the rendered frame from the base environment to `frame_list` [gymnasium/wrappers/rendering.py:137-143]().
- When `reset()` is called, it resets the base environment. If `reset_clean` is `True` (default), it clears the `frame_list` before appending the initial rendered frame [gymnasium/wrappers/rendering.py:146-155]().
- When `render()` is called on the wrapper, it returns the collected `frame_list`. If `pop_frames` is `True` (default), the `frame_list` is cleared after being returned [gymnasium/wrappers/rendering.py:157-164]().

The wrapper requires the base environment's `render_mode` to be an array-based mode (e.g., `"rgb_array"`) and not end with `"_list"` [gymnasium/wrappers/rendering.py:117-122](). It modifies the wrapper's `render_mode` property to append `"_list"` to the base environment's `render_mode` (e.g., `"rgb_array_list"`) [gymnasium/wrappers/rendering.py:133-136]().

### Configuration Parameters

- `env`: The environment to wrap.
- `pop_frames` (bool): If `True`, the `frame_list` is cleared after `render()` is called. Defaults to `True` [gymnasium/wrappers/rendering.py:109]().
- `reset_clean` (bool): If `True`, the `frame_list` is cleared when `reset()` is called. Defaults to `True` [gymnasium/wrappers/rendering.py:110]().

### RenderCollection Data Flow
```mermaid
graph TD
    A[User calls env.reset()] --> B{reset_clean is True?}
    B -- Yes --> C[Clear frame_list]
    B -- No --> D[Keep frame_list]
    C --> E[Base env.reset()]
    D --> E
    E --> F[Base env.render()]
    F --> G[Append frame to frame_list]
    G --> H[Return observation, info]

    I[User calls env.step(action)] --> J[Base env.step(action)]
    J --> K[Base env.render()]
    K --> L[Append frame to frame_list]
    L --> M[Return observation, reward, terminated, truncated, info]

    N[User calls env.render()] --> O[Get frame_list]
    O --> P{pop_frames is True?}
    P -- Yes --> Q[Clear frame_list]
    P -- No --> R[Keep frame_list]
    Q --> S[Return frame_list]
    R --> S
```
Sources:
- [gymnasium/wrappers/rendering.py:100-164]()

## RecordVideo Wrapper

The `RecordVideo` wrapper [gymnasium/wrappers/rendering.py:166-184]() records videos of environment episodes. It uses the environment's `render()` function to capture frames and saves them as video files. This wrapper supports both single and vector environments.

### How it Works

The `RecordVideo` wrapper manages video recording based on user-defined triggers.
- It requires the base environment's `render_mode` to be an array-based mode (e.g., `"rgb_array"`) [gymnasium/wrappers/rendering.py:190-192]().
- Recording is initiated when either an `episode_trigger` or `step_trigger` function returns `True` [gymnasium/wrappers/rendering.py:176-178](). If neither is provided, a default `episode_trigger` (`capped_cubic_video_schedule`) is used [gymnasium/wrappers/rendering.py:182-183]().
- During `step()` and `reset()` calls, if recording is active, frames are collected [gymnasium/wrappers/rendering.py:290-300]().
- When an episode ends or the `video_length` is reached, the collected frames are saved to a video file using `save_video` [gymnasium/wrappers/rendering.py:302-309]().

### Configuration Parameters

- `env`: The environment to wrap.
- `video_folder` (str): The folder where videos will be saved [gymnasium/wrappers/rendering.py:200]().
- `episode_trigger` (Callable): A function that takes the episode number and returns `True` to start recording. Defaults to `capped_cubic_video_schedule` [gymnasium/wrappers/rendering.py:201]().
- `step_trigger` (Callable): A function that takes the global step number and returns `True` to start recording [gymnasium/wrappers/rendering.py:202]().
- `name_prefix` (str): A prefix for video filenames [gymnasium/wrappers/rendering.py:203]().
- `disable_logger` (bool): If `True`, disables the logger [gymnasium/wrappers/rendering.py:204]().
- `video_length` (int): The maximum number of steps to record for a single video. If `None`, records until the episode ends [gymnasium/wrappers/rendering.py:205]().
- `video_aspect_ratio` (tuple[int, int]): The aspect ratio of the video (width, height). Defaults to `(1, 1)` [gymnasium/wrappers/rendering.py:206]().

### RecordVideo Workflow
```mermaid
graph TD
    A[Initialize RecordVideo Wrapper] --> B{episode_trigger or step_trigger met?}
    B -- Yes --> C[Start Recording]
    C --> D[Call base env.reset()]
    D --> E[Collect initial frame]
    E --> F[Loop: env.step(action)]
    F --> G[Call base env.step(action)]
    G --> H[Collect frame]
    H --> I{Episode terminated/truncated OR video_length reached?}
    I -- No --> F
    I -- Yes --> J[Save collected frames to video]
    J --> K[Stop Recording]
    K --> L{Next episode/step trigger met?}
    L -- Yes --> C
    L -- No --> M[Continue without recording]
    M --> F
```
Sources:
- [gymnasium/wrappers/rendering.py:166-309]()
- [tests/wrappers/test_record_video.py:13-42]()
- [tests/wrappers/vector/test_record_video.py:15-57]()

## HumanRendering Wrapper

The `HumanRendering` wrapper [gymnasium/wrappers/rendering.py:400-402]() (for single environments) and `gymnasium.wrappers.vector.rendering.HumanRendering` [gymnasium/wrappers/vector/rendering.py:25-26]() (for vector environments) provides human-friendly rendering by converting `rgb_array` or `depth_array` frames into a displayable window using `pygame`.

### How it Works

The `HumanRendering` wrapper intercepts `render()` calls and displays the frames in a `pygame` window.
- It requires the base environment's `render_mode` to be `rgb_array`, `rgb_array_list`, `depth_array`, or `depth_array_list` [gymnasium/wrappers/rendering.py:409-411](), [gymnasium/wrappers/vector/rendering.py:28-33]().
- During `step()` and `reset()` calls, it calls the base environment's `render()` method to get the frame(s) and then displays them in a `pygame` window [gymnasium/wrappers/rendering.py:430-434](), [gymnasium/wrappers/vector/rendering.py:76-94]().
- For vector environments, it arranges the individual environment renders into a grid within the `pygame` window [gymnasium/wrappers/vector/rendering.py:118-176]().
- The `close()` method ensures the `pygame` window is properly shut down [gymnasium/wrappers/rendering.py:449-452](), [gymnasium/wrappers/vector/rendering.py:200-203]().

### Configuration Parameters

- `env`: The environment to wrap.
- `screen_size` (tuple[int, int], optional): The size of the rendering window. If `None`, it defaults to the environment's render size [gymnasium/wrappers/rendering.py:403](), [gymnasium/wrappers/vector/rendering.py:43]().

### HumanRendering (Vector) Diagram
```mermaid
graph TD
    A[User calls VectorEnv.reset()] --> B[HumanRendering.reset()]
    B --> C[Base VectorEnv.reset()]
    C --> D[HumanRendering._render_frame()]
    D --> E[Base VectorEnv.render()]
    E --> F{Render mode is _list?}
    F -- Yes --> G[Get last frame from list]
    F -- No --> H[Get frame]
    G --> I[Process frames (transpose, scale, merge)]
    H --> I
    I --> J[Display frames in Pygame window]
    J --> K[Return observation, info]

    L[User calls VectorEnv.step(actions)] --> M[HumanRendering.step()]
    M --> N[Base VectorEnv.step(actions)]
    N --> D
    D --> O[Return observation, reward, terminated, truncated, info]
```
Sources:
- [gymnasium/wrappers/vector/rendering.py:25-203]()
- [tests/wrappers/test_human_rendering.py:11-24]()

## RecordEpisodeStatistics Wrapper

The `RecordEpisodeStatistics` wrapper [gymnasium/wrappers/vector/common.py:1-10]() (for single environments) and `gymnasium.wrappers.vector.common.RecordEpisodeStatistics` [gymnasium/wrappers/vector/common.py:1-10]() (for vector environments) records episode-wise statistics such as returns and lengths. These statistics are added to the `info` dictionary returned by `step()` when an episode terminates or truncates.

### How it Works

- It maintains internal counters for the current episode's return (`episode_returns`) and length (`episode_lengths`) [gymnasium/wrappers/vector/common.py:39-40]().
- In `step()`, it updates these counters. If an episode ends (terminated or truncated), it adds the `episode_returns`, `episode_lengths`, and `episode_times` to the `info` dictionary under the key `"episode"` [gymnasium/wrappers/vector/common.py:50-64]().
- It also stores these statistics in `deque` objects (`return_queue`, `length_queue`, `time_queue`) for a specified `deque_size` [gymnasium/wrappers/vector/common.py:41-43]().

### Configuration Parameters

- `env`: The environment to wrap.
- `deque_size` (int): The maximum number of episode statistics to store in the internal deques. Defaults to 100 [gymnasium/wrappers/vector/common.py:35]().

### RecordEpisodeStatistics Data Flow
```mermaid
graph TD
    A[Initialize RecordEpisodeStatistics] --> B[episode_returns = 0, episode_lengths = 0]
    B --> C[User calls env.reset()]
    C --> D[Base env.reset()]
    D --> E[Reset episode_returns, episode_lengths, episode_times]
    E --> F[Return observation, info]

    G[User calls env.step(action)] --> H[Base env.step(action)]
    H --> I[Update episode_returns, episode_lengths]
    I --> J{Terminated or Truncated?}
    J -- Yes --> K[Add "episode" key to info dict with r, l, t]
    K --> L[Append r, l, t to deques]
    L --> M[Reset episode_returns, episode_lengths, episode_times]
    J -- No --> N[Keep current episode_returns, episode_lengths]
    N --> O[Return observation, reward, terminated, truncated, info]
```
Sources:
- [gymnasium/wrappers/vector/common.py:1-10]()
- [tests/wrappers/test_record_episode_statistics.py:11-28]()

## save_video Utility

The `save_video` utility function [gymnasium/utils/save_video.py:1-10]() is a standalone function used by `RecordVideo` to write a list of image frames to a video file.

### How it Works

- It takes a list of `RenderFrame` (NumPy arrays), a `video_folder`, `fps`, and optional trigger functions and indices.
- It uses `imageio` to write the frames to an MP4 file.
- It determines the filename based on `name_prefix`, `episode_index`, and `step_starting_index` [gymnasium/utils/save_video.py:100-107]().
- It includes a `capped_cubic_video_schedule` [gymnasium/utils/save_video.py:12-25]() function which is used as the default `episode_trigger` for `RecordVideo`. This schedule records videos at episodes that are powers of 3 until 1000, then every 1000 episodes.

### `save_video` Parameters

- `frames` (list[RenderFrame]): A list of image frames to save.
- `video_folder` (str): The directory to save the video.
- `fps` (int): Frames per second for the video.
- `name_prefix` (str): Prefix for the video filename.
- `episode_trigger` (Callable): Function to determine if an episode should be recorded.
- `step_trigger` (Callable): Function to determine if a step should be recorded.
- `episode_index` (int): The current episode number.
- `step_starting_index` (int): The global step number when the recording started.

Sources:
- [gymnasium/utils/save_video.py:1-10]()
- [tests/utils/test_save_video.py:10-39]()

## Additional Rendering Wrappers

Gymnasium also includes other rendering-related wrappers:

-   `AddWhiteNoise` [gymnasium/wrappers/rendering.py:5-6](): Randomly replaces pixels with white noise.
-   `ObstructView` [gymnasium/wrappers/rendering.py:7](): Randomly places patches of white noise to obstruct the pixel rendering.

These wrappers are typically used for testing robustness or simulating visual impairments.

Sources:
- [gymnasium/wrappers/rendering.py:5-7]()

---

