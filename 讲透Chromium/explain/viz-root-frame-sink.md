# viz-root-frame-sink — RootCompositorFrameSinkImpl：viz 显示合成的顶层汇合点

文件：`components/viz/service/frame_sinks/root_compositor_frame_sink_impl.cc`（1059 行）＋同名头文件

## 一、角色定位

viz（visuals）是 Chromium 的显示合成服务，跑在 GPU 进程：所有客户端（browser UI、renderer 页面等）把绘制结果打包成 `CompositorFrame` 提交，由 viz 聚合成一帧送屏。本类就是这条链的**顶层 frame sink**——头文件 L51-54 钉死三重身份：同时实现 `mojom::CompositorFrameSink`（接客户端帧提交）、`mojom::DisplayPrivate`（接 browser 对 Display 的私控）与 `DisplayClient`（反观察 Display 生命周期）。浏览器 UI 与页面内容在此汇合：每个根窗口一个实例，把帧提交入口、`Display`（真正画屏的聚合器）、`BeginFrameSource`（vsync 时钟）捏合到一个对象。对照：非根客户端只是普通 `CompositorFrameSinkImpl`，无 Display 无时钟——"根"的特权就是这两样。

## 二、内部结构

**内嵌类＋巨型工厂＋三组转发面：**

- `StandaloneBeginFrameObserver`（L74）：替远程观察者订阅 begin frame，mojo 转发（L99），断连自摘除（L106）。
- 静态工厂 `Create`（L119，约 200 行）：先经 `OutputSurfaceProvider` 造 GPU 依赖（L130）与 `OutputSurface`（L132），失败返回 nullptr（L138）让 browser 换合成模式重试；再按平台造 begin frame source——外部控制器走 `ExternalBeginFrameSourceMojo`（L166），否则 Android 用 `ExternalBeginFrameSourceAndroid`（L190）、无帧率限制用 `BackToBackBeginFrameSource`（L203）、兜底 `DelayBasedBeginFrameSource`（L232），`CHECK` 保必有时钟（L243）。随后造 `DisplayScheduler`（L249）、overlay 处理器（L257）、`Display`（L263），`base::WrapUnique` 调私有构造（L277）；vsync 回调绑定 L290-295。
- 构造（L629）：`support_` 在初始化列表造 `CompositorFrameSinkSupport` 且 `/*is_root=*/true`（L646/L650）；正文注册 begin frame source 进 `FrameSinkManagerImpl`（L657）、`display_->Initialize`（L659）、挂 hit-test（L660）。析构（L322）对应反注册（L332）。
- 帧率决策组：`UpdateFrameIntervalDeciderSettings`（L690）组装 matcher 链（输入加速 L705/L708、视频节流 L712、视频会议 L727），`FrameIntervalDeciderResultCallback`（L778）把决策写回 begin frame source 或 output surface（L842/L850）。
- DisplayClient 回调组：`DisplayOutputSurfaceLost`（L853）、`DisplayDidReceiveCALayerParams`（L932）等，多为平台条件编译；`DisplayDidDrawAndSwap`（L1030）空实现。

## 三、外部连接

图谱实证：9 节点（1 file＋1 class＋7 function）、35 条边（8 contains＋27 imports）。imports 聚向 viz 自家三块——`viz/service/display`（display.h 等）、`viz/service/display_embedder`（output_surface_provider.h）、`viz/service/frame_sinks`（frame_sink_manager_impl.h＋四平台 external_begin_frame_source*.h），另经 `viz/common/frame_sinks/begin_frame_source.h` 接 common 层（viz 层 service↔common 523 条耦合边之一）。

关键协作：①`FrameSinkManagerImpl`——创建入口 `frame_sink_manager_impl.cc` L339 调 `Create`，成功存 `root_sink_map_`（L345）；begin frame source 注册/反注册（L657/L332）经它。②`Display`——聚合绘制走其 `SurfaceAggregator`（display.h L323）与 `FrameIntervalDecider`（L331）。③`CompositorFrameSinkSupport`——帧提交执行者。上游：browser 的 `viz_process_transport_factory.cc` L461/L464 经 `HostFrameSinkManager::CreateRootCompositorFrameSink`（host_frame_sink_manager.cc L215/L239）跨进程请求 GPU 进程。

## 四、数据流

**一帧时序（提交→聚合→上屏）：**

1. **vsync 驱动**：begin frame source 产生 `BeginFrameArgs`，经 `FrameSinkManagerImpl` 路由到子 sink→renderer 的 cc 调度器开始产帧。
2. **客户端提交**：根客户端调 `SubmitCompositorFrame`（L579）。根特有预处理：若 `LocalSurfaceId` 比已激活的新且未被逐出，立即 `display_->SetLocalSurfaceId`（L586）并按根帧 `output_rect` 调 Display 尺寸防 gutter（L589-590）。
3. **入库**：`support_->MaybeSubmitCompositorFrame`（L593）过 Surface 生命周期校验后落 `SurfaceManager`；`ACCEPTED` 返回（L596），失败 `ResetWithReason` 掐断连接（L603）——对不可信客户端的防御性关闭。
4. **damage 传播**：Surface 更新触发 `SurfaceObserver::OnSurfaceDamaged`→`DisplayDamageTracker`（display.h L326；display.cc L378 创建、L385 挂给 DisplayScheduler）标记待绘。
5. **聚合上屏**：下一 begin frame、DisplayScheduler 判可绘→`Display::DrawAndSwap` 用 SurfaceAggregator 把整棵 surface 树合成 `AggregatedRenderPassList`，经 OutputSurface swap 上屏。绘制前回调 `DisplayWillDrawAndSwap`（L861）聚合 hit-test 区域（L864-865）供输入路由，并采样 UMA 对比决策与实际帧率（L874 起）。

**vsync 回流**：OutputSurface 或外部时钟报新 vsync→`SetDisplayVSyncParameters`（L387）更新 timebase/interval（preferred interval 模式有 5% 漂移容忍，L415）→`UpdateVSyncParameters`（L450）分发给 synthetic source 与 `vsync_listener_`。

## 五、设计决策

**为何显示合成跨进程集中到 GPU 侧？** 若各 renderer 自行画屏，跨进程内容（页面嵌 browser UI、视频 overlay）无法正确合成，窗口遮挡/缩放需全知视角。viz 把"最后一合成"放特权进程：安全（renderer 只产出声明式帧描述）与正确性（全局排序）兼得；代价是每帧跨进程传输，故 CompositorFrame 传资源引用（gpu mailboxes）而非像素。`ResetWithReason`（L603）同逻辑：坏帧断管，绝不猜。

**FrameSinkId 为何是 (client_id, sink_id) 二元组？**（frame_sink_id.h L28-44）client_id 按进程分配，不同客户端永不撞名——它是 SurfaceId 第一分量，SurfaceManager 得以一张全局表管所有 surface 无歧义，跨进程引用天然带权属。根特权（is_root，compositor_frame_sink_support.h L91/L113）严格由本类设置，非根 sink 冒领不了 hit-test 与 Display 所有权。

**Create 为何是 200 行平台迷宫？** 时钟源本质是平台问题（Android SurfaceFlinger、Mac CVDisplayLink、Win DComp），集中在此隔离，构造（L629）只做注册接线；失败路径（L138）让 browser 换合成模式重试（frame_sink_manager_impl.cc L338 注释）。

## 六、新人提示

- **行号时效**：基于 2026-10 快照（8fe2331 代）；Android/iOS 分支高频改动，先 `grep -n` 重锚。
- **测试**：无专属 unittest，入口测试在 `frame_sink_manager_unittest.cc`（L288）与 `host_frame_sink_manager_unittest.cc` L267 起；显示效果跑 `viz/service/display/` 的 pixeltest。
- **改 begin frame 逻辑**注意双 source 语义：`begin_frame_source()`（L1032）优先 external；vsync 回调绑定（L290-295）依赖"impl→display→output surface"寿命链，乱动所有权会悬垂。
- **坑**：①`use_preferred_interval_`（L393）三态纠缠（iOS 强制、无多刷新率硬件、ChromeOS feature），改帧率先画状态表；②`DidEvictSurface`（L336）只逐出同 frame sink 且序号更新者（L347），乱放宽会闪屏；③Android 决策回调（L778）的 interval 伴随 compat 枚举（L813），漏改会破坏 SurfaceFlinger 协商。
- **文档**：`components/viz/README.md` 指向 //services/viz/README.md 与 Compositor Stack slides（帧率/vrr 权威）；调试走 `chrome://tracing` 的 `graphics.pipeline` 分类（L90 起埋 trace 点）。
