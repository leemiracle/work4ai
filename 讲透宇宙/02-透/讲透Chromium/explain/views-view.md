# view.cc / view.h —— Views UI 框架的根基类

> 源码：`ui/views/view.cc`（4244 行）/ `ui/views/view.h`（2745 行）

## 一、角色定位

`View` 是 Chromium **Views UI 工具箱的根基类**——工具栏、菜单、对话框、ash 系统面板等原生界面皆是其子类。类声明（view.h:295）组合继承了 8 个 ui 层接口；类注释（view.h:163-168）："A View is a rectangle within the views View hierarchy"，且刻意不设叶子 View。把控件四类能力抽象到一棵树：**绘制**（bounds/paint/transform/layer）、**布局**（LayoutManager 协商）、**事件**（targeter 命中+冒泡）、**无障碍与属性反射**。图谱中 151 个文件 import view.h、41 个类直接继承，是 ui/views 的中心节点。定位细节：Widget 的内容根 RootView 就是 View 子类（root_view.h:53）。

## 二、内部结构：四大机制

### 1. bounds 写入：SetBoundsRect

子树由 `children_` 向量管理（`AddChildViewAtImpl` view.cc:3275；z 序调整 `ReorderChildView` 328）。几何变更总闸门 `SetBoundsRect`（414）：矩形相同且无脏位则提前返回；不同则**对旧、新位置各 SchedulePaint 一次**（425-433）；有 layer 走 `SetLayerBounds`（440），否则向上对齐后代 layer（459）；再调虚函数 `OnBoundsChanged(prev)`（462），尺寸变了就地 `LayoutImmediately`（465-469）。入口 `SetBounds`（410）用 `std::max(0, width)` 钳负尺寸。

### 2. 坐标变换：ConvertPointToTarget 与"layer 断链"

`ConvertPointToTarget`（view.cc:1196）是坐标翻译唯一后端。算法是公共根枢轴：`GetHierarchyRoot`（149）找根并 CHECK 同树（macOS 有特例分支），点经 `ConvertPointForAncestor`（3731）升到根、`ConvertPointFromAncestor`（3740）降至目标。微妙处在 `CalculateOffsetToAncestorWithLayer`（2493）：遇到带 layer 的 View，偏移累加**停在 layer 边界**，改由携带 device_scale_factor 的 `LayerOffsetData` 交给合成器坐标系接力——View 树与 Layer 树形状不同，坐标在交界换轨。

### 3. 绘制：SchedulePaintInRectImpl → Paint

无效化入口 `SchedulePaint*`（1374/1378）进 `SchedulePaintInRectImpl`（3139）：绘制锁期间挂起；有 layer 就 `layer()->SchedulePaint(rect)`，否则转父坐标后**上抛父链**（3152-3155）到 paint root。消费端 `Paint`（1395）：入口 `CHECK_EQ(life_cycle_state_, kAlive)` 防 UAF；未被无效化的子树直接跳过；随后裁剪/变换记录、`OnPaint` 落笔、`PaintChildren`（2466）按 z 序递归。带 layer 的 View 由合成器回调 `OnPaintLayer`（2634）→ `PaintFromPaintRoot`（3220）自成 paint root。

### 4. 布局协商：InvalidateLayout → Layout(PassKey)

两阶段：脏化阶段 `InvalidateLayout`（1017）自下而上冒泡——置 `needs_layout_`、通知 ViewObserver 与 LayoutManager，到根转交 Widget 调度（见数据流）；执行阶段 `Layout(PassKey)`（975）委托 LayoutManager，再给漏网的脏子视图补 `LayoutImmediately`（3886）。另有 PassKey 直调防线（view.h:865）与 `invalidating_` 重入卫兵（1027）防布局环路。偏好尺寸走独立通道：`GetPreferredSize`（586）优先显式 SetPreferredSize，否则虚函数 `CalculatePreferredSize`；`PreferredSizeChanged`（2425）**先**让父级反应、**最后才** InvalidateLayout——顺序反了会重入。

事件命中与分发（`GetEventHandlerForPoint` 1631、`OnMouseEvent` 1778）见数据流一节。

## 三、外部连接

**8 个组合接口**（view.h:295-302）各有落点：`LayerDelegate`→`OnPaintLayer`（2634）、`LayerObserver`→`OnDeviceScaleFactorChanged`（2650）、`LayerOwner` 撑 `SetPaintToLayer`（782）、`AcceleratorTarget` 接加速键、`EventTarget`/`EventHandler` 撑事件分发（构造首行 `SetTargetHandler(this)`，234）、`PropertyHandler`→`OnPropertyChanged`（3049）、`MetaDataProvider`→`BEGIN_METADATA_BASE(View)`（4204；devtools 靠它枚举）。

图谱取证：imports 边覆盖 accessibility/animation/bubble/controls 全目录（button.h 等）；inherits 边含 Button、BubbleDialogDelegateView、FocusRing 等 41 子类。`ViewObserver` 在析构（248）、层级/布局变化（328/1035）等处广播通知，是 bubble 定位、FocusRing 追踪的官方挂点。

## 四、数据流

**鼠标按下**：平台事件 → NativeWidget → Widget → RootView。`RootView::OnMousePressed`（root_view.cc:515）先让 ViewTargeter 找最深命中（view.cc:1631→1635），然后**自命中点向上爬树**（root_view.cc:537）逐个 DispatchEvent，谁先处理谁截停；拖拽会话中 `mouse_pressed_handler_` 锁定首发 View，后续 move/release 直投它。递到 `View::OnMouseEvent`（1778）后：按下 `ProcessMousePressed`（3903）→ 虚函数 `OnMousePressed`（1716，默认 false），右键弹 ShowContextMenu、左键记 PossibleDrag；拖动 `ProcessMouseDragged`（3939），超 `ExceededDragThreshold` 即 DoDrag 启动拖放。**键盘**另走 FocusManager：焦点链由 `GetChildrenFocusList`（2046）按 `SetFocusBehavior`（2088）三态与 z 序决定，`RequestFocusWithReason`（2138）委托 FocusController。

**invalidation→paint**：变更（SetVisible 637/SetTransform 762/SetBoundsRect 414）→ `SchedulePaintInRectImpl`（3139）上抛到 paint root → compositor 下帧回调 → `Paint`（1395）递归走查。**布局流**独立：`InvalidateLayout`（1017）冒泡到根 → `Widget::ScheduleLayout`（widget.cc:1543）→ 调度器稍后 `Layout(PassKey)`（975），布局改 bounds 又自动触发 paint 失效。

## 五、设计决策

**组合优先于巨型继承树**：8 个 ui 接口各管一域（合成/事件/属性/元数据），再以成员对象补齐 Border/Background/LayoutManager/ViewTargeter/ContextMenuController/ViewAccessibility；子类只覆写少量虚函数，外观行为靠换组合件——`OnPaint`（2471）只做"背景+边框"两级委托即此缩影。

**与 Blink DOM 同构**：View↔Element、LayoutManager↔CSS 布局、ViewTargeter↔hit testing、InvalidateLayout/SchedulePaint↔style recalc/paint invalidation、Layer 树↔cc 合成层；`SetPaintToLayer`（782）使带 layer 的兄弟恒在上层，即 layer promotion 的翻版。差异：View 无样式解析与脚本绑定，纯命令式 C++，故用 PassKey（view.h:865）强制"框架驱动时序"。生命周期防御焊进热路径：`SANITIZED_OBJECT()`（view.h:305）、kAlive CHECK（1395）皆 UAF 战争遗迹。

## 六、新人提示

**坑**：① 坐标换算先想两棵树——`ConvertPointToTarget`（1196）要求同 hierarchy root，跨 layer 边界由 `CalculateOffsetToAncestorWithLayer`（2493）换轨；拿 RootView 坐标喂子 View 的 HitTest 是最常见根因。② PreferredSize 协商有方向性：`PreferredSizeChanged`（2425）先通知父级再 InvalidateLayout；覆写 `CalculatePreferredSize` 时别调 SetPreferredSize（显式值优先，586-590）。③ 别手动调 `Layout()`——PassKey 私有（view.h:865），业务代码只能 `InvalidateLayout()`；在 OnBoundsChanged 里同步改 bounds 最易制造布局环路。④ `OnMousePressed` 返回后"我们可能已被删除"——`ProcessMousePressed`（3931）与 `ProcessMouseDragged`（3961）两处大写 WARNING：回调返回后禁止再碰任何成员。⑤ 变换（762）或 layer（782）会改变上抛路径与 paint root，"画不出来"先查。

**测试与文档**：单测 `ui/views/view_unittest.cc` 覆盖全机制；`view_nocompile.nc` 验证不该编译过的 API 误用；平台补充 view_unittest_aura.cc/mac.mm；白盒入口 view_test_api.h。头文件 195-295 行类注释是 property/metadata 约定的唯一权威文档，写新属性前必读。验证跑 `unit_tests --filter=ViewTest*`。
