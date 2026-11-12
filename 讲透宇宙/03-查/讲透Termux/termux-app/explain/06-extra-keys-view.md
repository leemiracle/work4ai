# 06 · ExtraKeysView——Termux 的自绘扩展键盘

`termux-shared/src/main/java/com/termux/shared/termux/extrakeys/ExtraKeysView.java`（681 行）

## 角色定位

Android 软键盘给不出 Esc/Ctrl/Alt/方向键，Termux 的答案不是写 IME，而是自绘**按键网格**：`ExtraKeysView extends GridLayout`（ExtraKeysView.java:76），坐镇工具栏 ViewPager 第 0 页，按 `ExtraKeysInfo` 矩阵生成 MaterialButton。图谱归 **L06「Termux 业务核心层」**，该层契约"键定义留配置、交互行为留 shared、接线留宿主"，本文件是"交互行为"载体：只负责**把 JSON 矩阵变成带长按/连发/锁定/popup 四种交互的网格**。装配链见 javadoc :39-75：Termux 定义布局，`TerminalToolbarViewPager.instantiateItem()` inflate 后注入 client 并 `reload()`。它是 termux-shared 少数 UI 组件，与 L02 TerminalView 同走自绘路线，但后者是像素级渲染，这里只是标准控件编排。

## 内部结构

**IExtraKeysView 接口（:79-109）**：唯一行为出口——`onExtraKeyButtonClick`（:93）分发按键语义（含宏/popup 键），`performExtraKeyButtonHapticFeedback`（:107）让宿主优先接管震动；特殊键不走回调，改由 `readSpecialButton()` 轮询（:84-85）。

**常量四组（:113-144）**：主题 attr 4 个（:113-119，对应 attrs.xml:3-6）；颜色兜底 4 个（:122-128）；长按阈值 200/3000/400（:133-137）；连发周期 5/2000/80（:140-144，`MIN_LONG_PRESS__REPEAT_DELAY` 双下划线是冻结进 public API 的笔误）。

**字段（:149-209）**：client 引用（:149）；特殊键表与 key 集（:153/:157，供 `isSpecialButton()` :628 判定）；连发名单（:166，默认 UP/DOWN/LEFT/RIGHT/BKSP/DEL/PGUP/PGDN，ExtraKeysConstants.java:13-16）；四色+全大写开关（:170-181）；两时长（:191 默认取系统长按阈值，:199）；popup/调度器/Handler/`mLongPressCount`（:204-209）。构造器（:212-226）装默认名单、四特殊键 CTRL/ALT/SHIFT/FN（:367-374，SpecialButton.java:12-15）、主题色与两时长（:224-225）。

**reload() 网格重建（:386-487）**：`getMatrix()` 取矩阵（:395）→ 清特殊键按钮表（:390-391）→ `removeAllViews()`（:393）→ 逐格造按钮：特殊键 `createSpecialButton(key,true)`（:405-407，登记以联动染色），普通键 new（:409）。每按钮挂 OnClickListener（:417-420）与 touch 状态机（:422-470）：DOWN 染色+启动长按计时（:424-428）；MOVE 中 `event.getY()<0` 弹 popup、划回收掉（:430-443）；CANCEL 还原+停调度（:445-448）；UP 停调度后按 `mLongPressCount==0 || mPopupWindow!=null`（:454）分流——短按 `view.performClick()`（:462），popup 松手发 popup 键（:456-460），长按后松手不补发。

**长按调度双子系统（:535-585）**：`startScheduledExecutors()`（:535-558）先 stop 旧的（:536，同时只允许一个连发键）；连发键起单线程 executor，以 `mLongPressTimeout` 为初延迟、`mLongPressRepeatDelay` 为周期回调点击（:542-545）；特殊键改 `postDelayed` 长按 Runnable（:546-556），`run()`（:579-584）翻转激活+锁定+计数。`stopScheduledExecutors()`（:560-570）双清。`mLongPressCount` 一字段三用：连发计数（:543）、长按标记（:583）、UP 分流判据（:454）。

**特殊键读取（:643-667）**：`readSpecialButton` 返回 null=未注册（:645）；激活返回 true，且 `autoSetInActive && !isLocked` 时翻回 false（:651-652）——"一次性粘滞修饰键"语义来源。`SpecialButtonState.setIsActive()`（SpecialButtonState.java:39-43）同步给登记按钮换字色。

## 外部连接

图谱 file 节点 **fan-in 6 / fan-out 30**。fan-in：3 条 imports（`TermuxActivity.java:49`、`TerminalToolbarViewPager.java:14`、`TerminalExtraKeys.java:11`）+ 2 条 depends_on（布局 XML 以根标签实例化本类，view_terminal_toolbar_extra_keys.xml:2；`SpecialButtonState.java` 反向持有 `mExtraKeysView`）+ 1 条 configures（attrs.xml:3-6）。fan-out 30 中 12 contains+11 exports 是自身 3 类 8 函数的结构边，真外连 7 条：同包五件套 ExtraKeyButton/SpecialButton/ExtraKeysInfo/ExtraKeysConstants/SpecialButtonState + imports TerminalExtraKeys（仅 javadoc 链接）与 ThemeUtils。grep 全仓引用 10 文件，多出的 4 个均非 import：`TermuxTerminalViewClient.java:344-345` 经 getter 消费特殊键、`FullScreenWorkAround.java:10` 注释、同包 javadoc 互引——**运行时真实依赖方 5 个**：装配方二（TerminalToolbarViewPager、TermuxActivity）、client 链（TermuxTerminalExtraKeys.java:23）、读取方、布局 XML。import 列表（:3-37）不含 terminal-view/emulator 类——shared 与渲染层隔离肉眼可证。

## 数据流

长按 ↓ 键连发全链：① termux.properties 的 extra-keys JSON 取出（TermuxTerminalExtraKeys.java:47-48），`new ExtraKeysInfo`（:65，失败回退 :71）生成矩阵（ExtraKeysInfo.java:149）；② inflate+注入 client+`reload`（TerminalToolbarViewPager.java:44-50）；高度按矩阵行数算（TermuxActivity.java:536），主题变更重建（TermuxActivity.java:972-974）；③ DOWN（:424-428）→ "DOWN"∈名单（:538）→ 80ms 周期连发回调（:542-545）；④ client `TerminalExtraKeys.onExtraKeyButtonClick`（TerminalExtraKeys.java:28-51）：宏键拆空格累积 CTRL/ALT/SHIFT/FN 修饰位再发普通键；普通键到 `onTerminalExtraKeyButtonClick`（:55-76）合成带 metaState 的 KeyEvent 塞 `mTerminalView.onKeyDown`（:63-64），非控制字符 `inputCodePoint` 注入；⑤ UP（:450-452）`shutdownNow()`，输入经 TerminalView→PTY 进 L01。另分支：特殊键激活态不推送，TerminalView 处理物理按键时经 `readExtraKeysSpecialButton`（TermuxTerminalViewClient.java:343-349，传 true）拉取——推（普通键）拉（特殊键）双模式。

## 设计决策

**★ 已钉版 bug：setLongPressRepeatDelay 校验验错对象（:356-362，病灶 :357）**，条件两操作数都是**字段旧值**：

```java
if (mLongPressRepeatDelay >= MIN_LONG_PRESS__REPEAT_DELAY && mLongPressRepeatDelay <= MAX_LONG_PRESS__REPEAT_DELAY)
    mLongPressRepeatDelay = longPressRepeatDelay;   // 参数只在赋值右侧
```

"用旧值校验新值"笔误，对照 `setLongPressTimeout`（:342-348 用参数 `longPressDuration`）即可确诊。**后果链四环**：① 构造器首调（:225 传 DEFAULT=80）时字段为 0，`0>=5` 恒假落 else 赋 DEFAULT——恰与传参一致，bug 隐身；② 此后旧值恒在区间，后续任何调用条件恒真，**新值免检生效**，:140/:142 的 MIN/MAX 防线整体失效，javadoc :196-197 承诺的"越界回退 DEFAULT"是假契约；③ **崩溃链**：外部传 0（合法预期回退 80）真存 0，用户长按连发键（ExtraKeysConstants.java:13-16）→ `scheduleWithFixedDelay(...,0,MS)`（:542-545）按 Java 规范 period≤0 抛 IllegalArgumentException，从触摸回调裸抛——**app 崩溃**；负数同理，传 100000 则连发形同虚设；④ **毒化反转**：字段一旦越界，后续合法调用也落 else 被重置 80，校验方向颠倒。**为何无人报**：全仓 grep 实证该 setter 仅构造器 :225 一个调用点且传的就是 DEFAULT，Termux 自身永不踩雷；但这是发布库 public API，fork/插件照 javadoc 调用即中招。**一行修法**：:357 两处 `mLongPressRepeatDelay` 改参数 `longPressRepeatDelay`，恢复"验新值"。（onboarding :49 已收录，本节为后果链展开。）

**其余决策与勘误**：① **API 21 特判**（:474-478）：`height=0`+权重（:480-481）是均分工具栏正规手段，Lollipop 的 GridLayout 权重计算有平台 bug，SDK 21 改显式 `heightPx+0.5`——非死代码。② **单击绕道 performClick**（:462）：吞掉全部事件后短按仍触发 OnClickListener（:417-420），保住无障碍语义；`@SuppressLint`（:385）因 lint 看不见 switch 内调用。③ **推拉双模式**：普通键推送，特殊键拉取+消费即失效（:651-652 配合 TermuxTerminalViewClient:345），复刻 PC 修饰键"按住生效一次"心智，长按锁定（:579-584）对应 CapsLock。④ **触觉三层闸**：client 优先（:499）→ 系统开关（:503-504）→ API<28 加查 zen_mode≠2（:510）。⑤ **防御不对称**：getter 拷贝（:243/:255），setter 直存引用（:248/:266）。⑥ **勘误**：javadoc :70 称 ExtraKeysInfo 由 `TermuxAppSharedProperties.setExtraKeys()` 创建，实际在 app 侧 `TermuxTerminalExtraKeys.setExtraKeys()`（:43-75）——滞后于重构。

## 新人提示

1. **暴露该 setter 配置前先修 :357**："把连发延迟做成用户设置"会撞上崩溃链（设计决策节③）：用户填 0/负数，一长按方向键即崩溃。先修复再暴露。
2. **reload 是全量爆破式重建**（:390-393），`createSpecialButton(key,needUpdate)` 参数易搞反：reload 传 true 登记（:406）获联动染色，`showPopup` 传 false（:594）否则弹窗按钮被连带换色。增量更新前先想清 SpecialButtonState.buttons 生命周期。
3. **touch 状态机全分支 return true**（:428/:443/:448/:465/:468），默认按压态与无障碍语义全被接管——新增手势分支必做：显式 return true，且任何离开路径调 `stopScheduledExecutors()`；:536 先 stop 的兜底只保护"下一次按下"，不防"永远不再按下"的泄漏。
