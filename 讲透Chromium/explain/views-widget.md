# widget.cc / widget.h —— Views 的窗口容器：View 树的宿主与平台窗口的桥

> 源码：`ui/views/widget/widget.cc`（3224 行）/ `ui/views/widget/widget.h` · slug: views-widget

## 一、角色定位

`Widget` 是 Views 里**"窗口"概念的载体**：一头拥有 RootView 及整棵 View 树（widget.h:105 "Owns a RootView and thus a View hierarchy"），一头握着平台相关的 NativeWidget。类注释（widget.h:106-107）点明**双层设计**：Widget 承载平台无关状态机（激活/可见性/主题/事件/生命周期），NativeWidget 负责 OS 真窗口（Aura/Mac/ash 各一套）。类声明（widget.h:153）继承 `NativeWidgetDelegate`（被 NativeWidget 回调）、`ui::EventSource`、`FocusTraversable`（焦点链）。图谱取证：69 节点（1 文件+4 类+64 函数），函数数全仓前列。

## 二、内部结构：生命周期与所有权

### 1. Init 一步到位（widget.cc:499）

179 行：CanActivate 定激活语义（241）→ 绑 delegate（无则 `DefaultWidgetDelegate` 184 兜底）→ 创建 NativeWidget（辅助函数 122：显式注入→ViewsDelegate 工厂（测试借道）→默认创建）→ 按所有权决定是否包进 `owned_native_widget_`（572）→ `CreateRootView`（2831，直接 `new internal::RootView(this)`）→ NonClientView 类窗口（`RequiresNonClientView` 486）装 FrameView 并 SetInitialBounds，无边框则 `SetContentsView` 挂 delegate 内容（645）；结尾注册主题观察并广播 init 完成（659-676）。

### 2. 所有权三态与析构序列

`InitParams::Ownership`（widget.h:275）：**CLIENT_OWNS_WIDGET**（288，现行推荐：客户端持 `unique_ptr<Widget>`，reset 即关窗，widget.h:110）；NATIVE_WIDGET_OWNS_WIDGET（296，旧默认，NativeWidget 析构反删 Widget）；WIDGET_OWNS_NATIVE_WIDGET（308，测试栈对象常用）。析构器 `~Widget`（282）按所有权分三路（300-326）：前两态通知已由 native 侧发起；CLIENT_OWNS_WIDGET 在此补发——`ClientDestroyedWidget()`→`HandleWidgetDestroying()`（3083：通知 OnWidgetDestroying、WindowClosing）→`native_widget_->Close()`→`HandleWidgetDestroyed()`（3101：发 OnWidgetDestroyed、`DeleteDelegate()`、`native_widget_.reset()`）；双 CHECK（342-343）保证通知必走且只走一次。末尾 `DestroyRootView()`（2835）先 `RemoveAllChildViews` 再 reset，拆树中 `GetRootView()` 不断链。

### 3. 关闭双轨

`Close()`（1083）=`CloseWithReason(kUnspecified)`（1015），协商式关闭，**五道撤销闸**：`override_close_` 回调（MakeCloseSynchronous 1078 装载，拦截 //ui 内部发起的 Close，让客户端统一 unique_ptr 销毁）、`widget_closed_` 幂等、`block_close_`、NonClientView `OnWindowCloseRequested`（对话框借此拒关）、delegate `OnCloseRequested`。全过后置 `widget_closed_`（1057，防 crbug.com/714334 重入）、存位置、清焦点、通知 OnWidgetClosing，最后 `native_widget_->Close()` 异步走平台。`CloseNow()`（1087）是同步轨：通知后直接 `native_widget_->CloseNow()`——Widget 可能其中被销毁，此后不得碰 this。

### 4. 防自毁与激活语义

RAII 卫兵 `ScopedCallStackLock`（163）：析构器首行 `CHECK(!on_call_stack_)`（283）防同栈重入 UAF；Close/CloseNow/尺寸回调等可重入点都套它。激活核心 `OnNativeWidgetActivationChanged`（2031，80 行）：存位置、通知观察者、沿父链广播 OnWidgetTreeActivated，并维护**父链 paint-as-active 锁**（2090）：子激活时锁父（`LockPaintAsActive` 1851 返回引用计数锁 `PaintAsActiveLockImpl` 215），失活且计数归零才解锁（crbug/1303549）。`ShouldPaintAsActive`（1875）综合显式覆盖与父级状态，供控件配 active 颜色。

## 三、外部连接：分层协作（图谱边取证）

图谱 107 条边勾勒五层。**向下**：import root_view.h（`root_view_` widget.h:1733）、native_widget_private.h（`native_widget_` 是 WeakPtr，widget.h:1700；仅 WIDGET_OWNS_NATIVE_WIDGET 有强引用 owned_native_widget_ 1706）——互为弱引用，靠所有权字段定生死。**向上**：一组 OnNativeWidget* 回调（激活 2031/尺寸 2216/销毁 2171/绘制 2288…）实现 `NativeWidgetDelegate`，平台事件从这扇门进来。**横向**：widget_observer.h（`observers_` widget.h:1710，AddObserver 732）、widget_delegate.h、views_delegate.h、focus_manager.h（ClearFocusManagerFromWidget 3047）、any_widget_observer_singleton.h。**子模块**：sublevel_manager.h（z 序子层级）、tooltip_manager.h、input_protection/（防遮挡/合成事件误激活，EnableInputEventActivationProtection 1381）。

## 四、数据流：事件下行与像素上行

**输入**：NativeWidget 捕获 OS 输入 → `OnKeyEvent/OnMouseEvent/OnScrollEvent`（2309/2320/2445）→ RootView。`OnMouseEvent`（2320，107 行）最精细：kMousePressed 先造 `WidgetDeletionObserver` 自保（2334），`root_view->OnMousePressed()` 返回 true 且 widget 存活可见、鼠标仍按下、capture 未变时才置 `is_mouse_button_pressed_` 并设 capture（2353）；kMouseReleased 先放 capture 再派发（2366）；move/drag 按 capture+按下状态分流。**绘制上行**：View 无效化到 `SchedulePaintInRect`（1516）——有 native_widget_ 则转发（Aura 下进 compositor），拆树期丢弃；合成器回流走 `OnNativeWidgetPaint`（2288）→`GetRootView()->PaintFromPaintRoot(context)`，整树从此落笔。**布局**：RootView 失效上行 `OnRootViewLayoutInvalidated`（1525）→ autosize widget 投递异步 ResizeToDelegateDesiredBounds，普通路径 `ScheduleLayout`（1543）转 native。尺寸下行 `OnNativeWidgetSizeChanged`（2216）：RootView SetSize→通知 caret→广播 OnWidgetBoundsChanged。

## 五、设计决策：为什么两层、为什么 3224 行

分层是本文件存在的理由：窗口语义（控件树、焦点、主题、激活）平台无关地写一遍（64 函数大半是这套状态机），OS 窗口创建/事件泵/拖放（RunDragDropLoop 1454、RunMoveLoop 970）下沉平台子类。这也解释 63+ 函数挤一个文件：Widget 是**所有窗口语义的汇合点**，函数多而薄——转发+通知+守卫，拆文件只会撕碎同一条状态流。三个细节：①WeakPtr 互指（1700）而非裸指针，"窗口先死于平台"的边缘情况可检测；②主题走 ColorProviderKey（GetColorProviderKey 2732：native theme+渲染器上下文），web 内容与原生 chrome 配色由此同步（GetRendererColorMap 2762）；③与 chrome/browser 的衔接不在本文件而在 `ui/views/controls/webview/webview.h`（45-51 注释）：WebView 只是一个 View，持有并显示 WebContents 提供的 native view——浏览器窗口=Widget+NonClientView(标题栏/工具栏)+WebView(网页)，两层抽象在此合拢。

## 六、新人提示

①**所有权别选错**：用 `CreateWindowWithParent/Context`（357）或 CLIENT_OWNS_WIDGET+unique_ptr 模式（widget.h:110）；选错会在析构器 314 吃 CHECK。②**关闭时序**：Close() 异步（"closed but not destroyed"中间态），观察者按 OnWidgetClosing→OnWidgetDestroying→OnWidgetDestroyed 收通知；Close/事件处理中 Widget 可能同步死亡，须 WidgetDeletionObserver/GetWeakPtr 自保（2334 样板）。③改 OnNativeWidget* 回调先学 `native_widget_initialized_`/`widget_closed_` 守卫（OnNativeWidgetPaint 2291 Linux 提前绘制分支）。④测试：widget_unittest.cc 与 native_widget_unittest.cc 编入 `views_unittests`（ui/views/BUILD.gn:1287）。⑤上游读 widget.h:100-151 所有权注释，配合 views-root-view 篇。
