# cc/trees/layer_tree_impl.cc —— impl 侧层树容器与双树交换核心

> 源码 src@8fe2331：`/usr-data/data1/browser/chromium/src/cc/trees/layer_tree_impl.cc`（3421 行）+ `layer_tree_impl.h`（1078 行），行号实证；图谱 48 节点为 cc 之最。

## 一、角色定位

Blink 主线程产出 Layer 树，经 commit 送进合成器线程，被消费的容器即 `LayerTreeImpl`。`LayerTreeHostImpl` 持有三棵：`active_tree_`（被 draw 消费出 CompositorFrame）、`pending_tree_`（接收新 commit）、`recycle_tree_`（回收的树壳）。

"是哪棵树"是动态身份：`IsActiveTree()` 即 `host_impl_->active_tree() == this`（cc:2167），Pending/Recycle/Sync 同理（2171/2175/2179）。同一对象先后经历 pending→active→recycle（复用见 client_layer_tree_host_impl.cc:343）。

它不持有渲染资源（settings 等全穿透 `host_impl_`，h:917），持有层状态快照：`layer_list_`（h:997）、`property_trees_`（h:922）、viewport 属性 id（h:925）。

## 二、内部结构

**构造与生命周期闸**：构造函数（cc:154）接收三个跨树共享 `scoped_refptr<Synced*>`（page scale 等）。`LayerTreeLifecycle`（h:74-101）是四态机：`kNotSyncing→kBeginningSync→kSyncedPropertyTrees→kSyncedLayerProperties`，`AdvanceTo()`（cc:139-152）以 `DCHECK_EQ(state_ + 1, next_state)` 强制按序；`AllowsPropertyTreeAccess()`（h:92）决定同步中间态能否读属性树（如 cc:221）。

**commit 拉取主链 `PullPropertiesFrom`**（cc:754-843）：`SynchronizeTrees` 结构对齐（769）→ `PullPropertyTreesFrom`（779/845：按 sequence number 决定 preserve 或先搬脏标记）→ `PushLayerProperties` 逐层推属性（789）→ `PushScrollUpdatesFromMainThread`（807）→ `PullLayerTreePropertiesFrom` 拉树级杂项（816）→ 动画 host push（833）→ `MoveChangeTrackingToLayers`（838）。

**`SetPropertyTrees`**（cc:687-752）：preserve 时先合并旧树脏状态（691-694）；暂存滚动中节点（701），整体赋值（714），`CreateOrReuseRenderSurfaces` 复用 surface（722），再恢复滚动节点、刷新 viewport ids（745/751）。

**激活推送**：`PushPropertyTreesTo`（954）与 `PushPropertiesTo`（1004），见第四节。

**`UpdateDrawProperties`**（cc:1857）：入口即清 `needs_update_draw_properties_`（1868，不许早退）；`CalculateDrawProperties` 算 surface 列表与可见性（1893），`OcclusionTracker` 算遮挡（1900），`UpdateTiles()`（1957）压 tile 优先级。

**`DidUpdateScrollOffset`**（cc:218）：impl 滚动后回调，双闸（233-236）决定是否立即改 transform 节点（250-265）；active 树滚动还扇出同步 pending/recycle（271-281）与滚动条几何（285-292）。

**其余**：swap promise 四件套（2310-2361）、命中测试（2767/2948）、UI 资源队列（2410）、tracing `AsValueInto`（2278）；遍历靠 `begin()/end()` 适配器（h:268-274）。

## 三、外部连接

图谱实证：本 .cc import 51 头；反向 **62 文件 import `layer_tree_impl.h`**——`layer_tree_host_impl.cc`、`tree_synchronizer.cc`、`draw_property_utils.cc`、20+ 个 `*_layer_impl.cc`、input 6 文件、测试 9+ 文件、viz 进程的 `layer_context_impl.cc`。

commit 入口链：`proxy_impl.cc:888` 与 `single_thread_proxy.cc:260` → `ClientLayerTreeHostImpl::FinishCommit`（client_layer_tree_host_impl.cc:120）→ 132 行 `sync_tree()->PullPropertiesFrom(...)`；`BeginCommit`（109）先 `CreatePendingTree()`。激活驱动 `LayerTreeHostImpl::ActivateSyncTree`（layer_tree_host_impl.cc:3787）。

## 四、数据流：pending→active 激活时序

`ActivateSyncTree()`（layer_tree_host_impl.cc:3787）：

1. active 树推进 `kBeginningSync`（3799）；pending 树消化 UI 资源队列（3804）；需全量则 `SynchronizeTrees(pending, active)`（3806）；
2. `PushPropertyTreesTo`（3816）→ `kSyncedPropertyTrees`（3818）。内部按 sequence number 相等与否决定 merge 还是先搬脏标记再整体覆盖（cc:961-985）；
3. `PushLayerProperties(pending, active)`（3820）→ `kSyncedLayerProperties`（3823）；
4. `PushPropertiesTo`（3825）推树级杂项：**scroll offset** 走 `PushScrollUpdatesFromPendingTree`（cc:1010-1012）保住主线程未确认的 impl 滚动；swap promise 经 `PassSwapPromises` 转交（1019）；page scale 两树共享 `SyncedScale` 只推 limits（1029）；
5. pending 树 `ResetAllChangeTracking()`（3827）→ `kNotSyncing`（3830）；
6. **免锁交换在此**：`pending_tree_.swap(recycle_tree_)`（3836）；
7. `DidBecomeActive()`（3873 → cc:2090）：逐层 `layer->DidBecomeActive()`（2101）、swap promise 逐个 `DidActivate()`（2104）。

**damage 追踪**：属性树自带 changed 节点列表，`MoveChangeTrackingToLayers()`（cc:1180）覆盖前把脏标记搬上 LayerImpl；commit 中止时 `ApplySentScrollAndScaleDeltasFromAbortedCommit`（cc:1772）回滚已发 delta。

## 五、设计决策

**三棵树 vs 单树加锁**：合成器线程每 vsync 读树出帧，commit 是突发写；单树加锁则 draw 被 commit 阻塞生 jank。双树读写分离，交换收敛为指针 swap（3836 行，O(1) 免锁，时机由 Scheduler 定）；第三棵 recycle 纯为复用 LayerImpl 对象池。代价是状态都要回答"两树不一致"，大量 preserve/merge/rollback 代码由此而来。另一极端 `CommitsToActiveTree()` 模式（sync_tree() 直接返回 active，layer_tree_host_impl.h:652），省 pending 但失去并发 commit。

**与 viz 衔接**：active 树是 `LayerTreeHostImpl::Draw` 唯一输入，其 surface 列表与 tile 组出 viz::CompositorFrame；跨进程嵌入靠 `SetSurfaceRanges`（cc:2052）。TreesInViz 模式下（`kTreesInViz`，cc/base/features.h:133）`PushPropertiesTo` 跳过 fanout 的 `MoveChangeTrackingToLayers()` 改轻量 `UpdateChangeTracking()`（cc:1121-1134，active 树不再绘制、序列化开销是瓶颈）。`PushPageScaleFactorAndLimits`（cc:1489）两段式 `PushMainToPending`/`PushPendingToActive`（1502/1506）+ `SyncedProperty` 模板，是 impl 可变值跨线程一致的通用答案。

## 六、新人提示

- **先吃透 lifecycle**：同步中间态读属性树会撞 `AllowsPropertyTreeAccess()` DCHECK（h:92-97）；崩溃先打 `lifecycle().state()`。
- **顺序敏感但只有注释守卫**：`PushScrollUpdatesFromMainThread` 须晚于 push properties（cc:803-806 TODO(pdr)），动画 host push 又须在其后（823-828）；tickmarks 需在 SetPropertyTrees 之后（cc:1089）。
- **`UpdateDrawProperties` 不许早退**：看 1866-1877 注释再加工。
- **改滚动必看** `DidUpdateScrollOffset` 三路扇出（cc:218），漏 recycle 同步是经典 bug。
- **测试**：单元在 `cc/trees/layer_tree_impl_unittest.cc`（51 TEST_F）；集成在 layer_tree_host_unittest_*.cc 全家。
- **调试**：`AsValueInto`（cc:2278）打 trace、`LayerListAsJson`（cc:3303）导层树。

📌 **下一步**：commit 线读 `proxy_impl.cc:888 → client_layer_tree_host_impl.cc:120 → tree_synchronizer.cc`；激活线读 `layer_tree_host_impl.cc:3787`；补 `property_tree.cc` 的 changed 节点机制。
