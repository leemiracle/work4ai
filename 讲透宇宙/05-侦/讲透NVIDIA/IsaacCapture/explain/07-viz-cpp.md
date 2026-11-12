# 07 · viz C++ 可视化引擎（Televiz）：Vulkan 会话、图层栈与 MuJoCo 数字孪生

## 一、角色定位

`src/viz/` 是 IsaacCapture 唯一的纯渲染领土，代号 **Televiz**。三条显示通路：桌面窗口 kWindow、离屏 kOffscreen、VR kXr（OpenXR）；经 pybind11 暴露为 `isaaccapture.viz`，被 teleop 的 robot twin 线程消费（`teleop_session_manager/twin_runner.py:22`）。包形态镜像 `src/core/`：子模块容器，每子目录一个静态库；91 文件 = core 15 + session 22 + robot_twin 20 + layers 13 + xr 8 + python 6 + shaders 5。核心目标是零拷贝把 CUDA 生产的像素送进 XR 合成器。

## 二、内部结构

**core——Vulkan/CUDA 地基。** `VkContext`（`vk_context.hpp:42`）封装 instance+device+queue，两条 init 路径：standalone 自选显卡，或 XR-bound 走 `xrCreateVulkan*KHR`（`vk_context.hpp:32`）；`match_cuda_device_to_vulkan()`（`vk_context.hpp:114`）按 UUID 把 CUDA 对齐到同一 GPU（错位即每次 submit 一次 peer copy）。像素货币 `VizBuffer`（`viz_buffer.hpp:44`）：非持有式引用，`MemorySpace`（`viz_buffer.hpp:26`）分 kDevice/kHost。持有版 `DeviceImage`（`device_image.hpp:21`）：VkImage 内存经 `VK_KHR_external_memory_fd` 导出、导入 CUDA 成 cudaArray_t，配单向 timeline semaphore 做生产者→消费者同步。`RenderTarget`（`render_target.hpp:34`）为共享中间帧缓冲（RGBA8_SRGB+D32_SFLOAT，格式写死于 `render_target.hpp:40`），resize 保 render pass 兼容。

**session——帧循环与后端。** `VizSession`（`viz_session.hpp:53`）拥有上下文、合成器与图层注册表，每显示面一个；六态生命周期（`viz_session.hpp:36`），XR 独有 kStopping/kLost；帧循环两种拼写：`render()` 或 `begin_frame()/end_frame()` 对。后端抽象 `DisplayBackend`（`display_backend.hpp:31`）每模式一实现（xr_backend.cpp 1389 行最大），`Frame`（`display_backend.hpp:80`）携带 per-view 信息、头姿、同步 semaphore。`Swapchain`（`swapchain.hpp:25`）present 偏好 MAILBOX→FIFO_LATEST_READY→FIFO、跳过 IMMEDIATE（无 vsync 节流的事件循环失控）；`GlfwWindow`（`glfw_window.hpp:23`）对 GLFW 进程级引用计数支持多窗口。

**layers——三路合成。** 抽象根 `LayerBase` 住 session（`layer_base.hpp:137`），子类实现 `record()`（`layer_base.hpp:178`）在 render pass 内发 draw。三条路径：普通 draw 进共享 RT；direct-present——`DirectPresentView`（`layer_base.hpp:43`）把全视图 (color,depth) 直接 copy 进呈现 swapchain；native composition layer——`NativeLayerView`（`layer_base.hpp:78`）把 Quad/Cylinder/Equirect 交 OpenXR runtime 原生合成，解锁其 fast path。`ImageLayerBase`（`image_layer_base.hpp:56`）是 CUDA 喂图层基类：无锁 mailbox，`kMaxFramesInFlight=5`、`kSlotCount=7`（`image_layer_base.hpp:64`），+2 不变式保证空槽（`:38`）。`QuadLayer`（`quad_layer.hpp:37`）是相机画面主力，`openxr_composition`（`quad_layer.hpp:110`）默认 true。`ProjectionLayer` DIRECT-PRESENT ONLY（`projection_layer.hpp:29`），服务每帧产出 RGBD 的渲染器。

**robot_twin——私有 MuJoCo。** 本模块不链接 MuJoCo：宏 `ROBOT_TWIN_MJ_FN`（`mj_api.hpp:21`）把入口点声明成函数指针，`load()` 对随扩展的 `libisaacteleop_mujoco.so` 逐一解析——用户自己的 libmujoco 串不进来（布局不同会静默错乱）。`guarded()`（`mj_guard.hpp:26`）装 handler 用 longjmp 转 C++ 异常。`Readback` 把离屏 framebuffer 直转 `ProjectionLayer.submit()` 消费的 CUDA 缓冲、零主机往返（`gl_readback.hpp:8`），且用 RegisterBUFFER 而非 RegisterImage——后者不吃 depth 格式与多重采样。

**python——绑定。** `_viz` 按 DAG 顺序 core→layers→session 注册（`viz_bindings.cpp:27`）；robot_twin 独立扩展 `_robot_twin`，边界纪律"Nothing typed crosses this boundary"（`robot_twin_bindings.cpp:8`）：pose/fov 裸 float 过界，mjModel/mjData 不出境。

## 三、外部连接

viz_session include core 的 oxr_utils 句柄头（`viz_session.hpp:11`），把 OpenXR 句柄透传给 TeleopSession（`get_oxr_handles()`，`:223`）；日志走 isaaccapture::Logger（`vk_context.hpp:119`）。Python 双向：VizBuffer 暴露 `__cuda_array_interface__`，`cuda_array_to_viz_buffer()`（`bindings_helpers.hpp:77`）反向校验转换。消费方：teleop robot twin——`RobotTwin` Protocol（`twin.py:16`）+ `XrTwinSession`（`viz/robot/session.py:40`）。

## 四、数据流

VR 数字孪生链路：`XrTwinSession.__enter__` 建 `VizSession(kXr)`、等头显（`viz/robot/session.py:31`）、add stereo ProjectionLayer → `begin_frame()` 返回预测显示时刻 per-eye pose/fov → 控制线程异步 `publish(joints=...)`（只写 numpy 视图），渲染线程 `twin.render()`（`scene.py:312`）走 MuJoCo 离屏渲染+`Readback.capture()` 读回 CUDA → `twin.color/depth(view)` 返回即时构造的 CAI dict（`robot_twin_bindings.cpp:49`）→ `ProjectionLayer.submit(color, depth)`：mailbox 选空槽 memcpy2D、signal cuda_done_writing、同步后返回（~0.5ms/1080p，`image_layer_base.hpp:73`）→ `end_frame()` direct-present 逐字节 copy 进呈现 swapchain——深度不经 gl_FragDepth 往返，CloudXR 重投影拿精确深度（`projection_layer.hpp:33`）；kXr 下没 submit 的帧清空 swapchain 而非旧 RGBD 配新 pose（`:54`）。相机 QuadLayer 更短：submit(VizBuffer)→mailbox→默认作 XrCompositionLayerQuad 交 runtime。

## 五、设计决策

- **GPU 同卡对齐**：init 按 UUID 匹配，`get_cuda_device_id()`（`viz_session.hpp:210`）警告多卡机上"不一定是 0"，生产者必须在这台设备分配。
- **三路合成换三样东西**：direct-present 换精确深度，native layer 换 runtime fast path（无源 alpha 才能进 client-reconstructed streaming，`quad_layer.hpp:117`），共享 RT 换通用性；代价是"一个 ProjectionLayer XOR 任意多纹理层"不变式（`viz_session.hpp:124`，`:150` 抛异常强制）。
- **mailbox 尺寸算术推出**：禁止集最坏 1+N，+2 保证空槽，后端超限即抛——隐性撕裂变显式故障。
- **异常安全**：`abort_frame()`（`display_backend.hpp:199`）——submit 后抛异常绝不 present，标 swapchain 待重建。
- **GIL 纪律**：render/submit/readback 全部 call_guard 释放 GIL（`viz_bindings.cpp:17`）。

## 六、新人提示

读码顺序：`viz_session.hpp` 头注释→`layer_base.hpp`（三路径注释都在）→`projection_layer.hpp` 顶部 80 行。`record()` 里别绑 scissor（合成器预绑）、别结束 render pass。add_layer/remove_layer 必须在帧循环线程，唯一例外 `set_visible()`（atomic，晚一帧生效是语义）。显存先算账：stereo 4K QuadLayer ≈464MB/层（`image_layer_base.hpp:48`）；立体 submit 两眼必须同 stream（`image_layer_base.hpp:92`）。`guarded()` 是 longjmp 跳过析构——fn 里只能调 MuJoCo。

## 源码实证勘误

子目录文件数（15/22/20/13/8/6/5）数过属实。修正两点：①"被 teleop 消费"不完整——精确说是 twin_runner + `isaaccapture.viz.robot` 包，ProjectionLayer 注释还点名 gsplat/nvblox；②vk_context.hpp 标"19 扇入"，src/viz 内实际 include 15 处（口径随统计范围而异）。

---
chars(不含空格)=4797 anchors=26 勘误=1
