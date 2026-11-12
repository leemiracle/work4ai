# 02 TerminalView.java —— 终端渲染画布与输入分发中枢

`terminal-view/src/main/java/com/termux/view/TerminalView.java`（1520 行，`final class TerminalView extends View` :46；未注明文件的锚均指此文件）

## 角色定位

terminal-view 模块的单点枢纽：**自绘 View**（继承 View 而非 TextView/EditText，:46），身兼**渲染画布**（`onDraw` 画字符网格，:1022-1037）与**输入分发中枢**（四路输入归一为 PTY 写入，:433/:908）。图谱 14 层属 **L02 终端渲染视图层**（层内 12 节点：终端画布+文本渲染+手势+文本选择游标，下接 L01 上供 app 嵌入）。

存在理由：终端语义 Android 无现成组件——按键变控制序列（方向键→`\033[D`）、像素换算列行、滚回历史与主备屏滚动差异、死键组合，EditText 全给不了，只能自绘+自实现 `InputConnection`。依赖链 `terminal-emulator ← terminal-view ← termux-shared ← app` 中间层：向下仅依赖 L01，向上供 shared 与 app 消费。

## 内部结构

**构造器即手势配置**（:136-262）：匿名 `GestureAndScaleRecognizer.Listener` 七回调——轻触在鼠标跟踪时合成左键按下+释放（:145-150）、滚动像素→整行+余数入 `mScrollRemainder`（:180-183）、fling 用 Scroller 逐帧驱动（:215-217）、长按起文本选择（:250-257）。

**IME 通道**（:309-438）：inputType 双策略（见设计决策）；`imeOptions` 固定 `NO_FULLSCREEN`（:341，TV 回车依赖）。匿名 `BaseInputConnection`（:343）覆写三入口：冲刷缓冲（:346-353）、`commitText`（:356-368）、删除译 N 次 KEYCODE_DEL（:371-379）。`sendTextToTerminal`（:381-435）拼代理对（:387-396）、virtual shift 转大写（:399-400）、codePoint≤31 按 penti 键盘约定映射 Ctrl 字符（:403-431，\n→\r 修 AOSP 键盘 :404-410）。

**按键通道**（:770-946）：`onKeyDown` 五级瀑布——client 优先（:778）→系统键放行（:781）→`ACTION_MULTIPLE` 直写（:783-785）→keyMod 组装（:796-800）交 `handleKeyCode`（:802）：`KeyHandler.getCode`（:922→KeyHandler.java:156）命中即转义序列直写 session（:924）；未命中清 Ctrl/左 Alt 位（:807-817，右 Alt 留 AltGr）→`getUnicodeChar`（:820）→死键组合（:827-840）→公共出口 `inputCodePoint`（:847-910）：Ctrl 字母折 1-26、Ctrl+标点映射控制符（:864-885）、蓝牙键盘私用 Unicode 替回 ASCII（:890-905）、`writeCodePoint`（:908→TerminalSession.java:183，prependEscape 让 Alt+B 在 readline 生效）。shift+PageUp/Down 滚历史特判（:936-942）。

**滚动触摸**：`doScroll`（:575-590）三态（见设计决策）；滚轮一档 3 行（:594-602）；`onTouchEvent`（:607-644）选择优先（:611-614）、鼠标右键弹菜单（:617）、中键剪贴板 `paste`（:619-628）、跟踪模式左键上报（:629-639）。

**渲染与子系统**：`mTopRow` 为滚动位置（:70，负值=翻历史）。`onScreenUpdated`（:455-500）回程总闸——选择中或禁自动滚时跟随下移而非跳底（:465-483，顶穿历史才中止 ：471-472）；正常态跳回 0 行、距底>3 行才唤醒滚动条（:485-492）；滚动计数读清配对（:467/:496）；`invalidate`（:498）、无障碍 `setContentDescription`（:499）。`updateSize`（:985-1019）像素→列行最小 4（:991-992），变化才 `session.updateSize`（:995→TerminalSession.java:103，等价 SIGWINCH）、回调 `onEmulatorSet`（:997）、按缓存恢复 `mTopRow`（:1006-1014）。`onDraw` 无 emulator 涂纯黑（:1024）否则交 `mRenderer.render`（:1032）。另：光标闪烁钳 100-2000ms（:1219-1222）、AutoFill 请求→复位（:1088-1194）、文本选择懒创建+detach 强收（:1368-1379/:1466-1472）。

## 外部连接

图谱实证：**fan-out=58**（contains 27/exports 22/imports 7/calls 2）、**fan-in=10**（imports 7/depends_on 3）——大头是自包含符号，耦合面小。

**fan-in 7 import 方**：app 层 TermuxActivity.java:59（装配 :490）与 TermuxTerminalExtraKeys.java:19；shared 层 TermuxPropertyConstants.java:12 与 TerminalExtraKeys.java:14（extra keys 回环注入：直调 `onKeyDown`（:65）与 `inputCodePoint`（:70），CTRL/ALT 靠 `readControlKey()` 回调，TerminalViewClient.java:53-59 共 23 法）；模块内 textselection 三件套。2 条 depends_on：TextSelectionCursorController 的 `updatePosition`/`setInitialTextSelectionPosition` 用本文件 `getCursorX/getCursorY`（:222-223/:264-265）；布局边 activity_termux.xml:26 实例化本类。

**fan-out**：字面 import 仅 4 个 com.termux.*（:40-43）；图谱 7 条 imports 边中 GestureAndScaleRecognizer/TerminalRenderer/TerminalViewClient 同包无需 import（:56/:74/:58）——scanner 语义口径（与字面差 3），以源码为准。2 条 calls 边指向 KeyHandler.java 与 TerminalRenderer.java（字体度量 :30-51）。回程入口不在本文件：`onScreenUpdated` 由 TermuxTerminalSessionActivityClient.java:79/:121 驱动，闪烁器由 TermuxTerminalViewClient.java:663/:668 驱动。

## 数据流

按键回路（Gboard 输 a）：`commitText("a")`（:356）→ `sendTextToTerminal`（:381）→ `inputCodePoint`（:433）→ `onCodePoint` 钩子先过（:862）→ `writeCodePoint`（:908）→ TerminalSession 队列 → PTY → shell；回显：InputReader 读 PTY → emulator.append 落格（L01 链）→ app 回调 `onScreenUpdated()`（TermuxTerminalSessionActivityClient.java:79）→ 钳滚动/清计数（:462-496）→ `invalidate`（:498）→ `render` 画 `mTopRow` 起的网格（:1032）。

## 设计决策

- **inputType 双策略**（:314-337）：TYPE_NULL 最正确但部分键盘在其上行为坏（注释钉 #87 等），留后门切 `VISIBLE_PASSWORD`（:315-323，防 Samsung 键盘不重置）——"假密码框"骗键盘关自动纠正，代价是 AOSP log warning（:319-322）。
- **onKeyPreIme ROM 兼容**（:647-671）：Back 键在 IME 激活时到不了 onKeyDown，须 PreIme 拦截按配置转 Escape（:650-663）；ctrl+space 部分 ROM 不触发 onKeyDown 同样提前拦（:664-669，注释自认两头难全）。
- **滚动三态**（:578-589）消费权让给程序：鼠标跟踪程序收滚轮事件（:579-580）> 备屏程序收 DPAD 键自滚（:581-584，点名 less）> 本地滚并钳 transcript（:586）。
- **选择时跟随**（:465-483）：输出到达不跳底而同步下移并给手柄做 Y 递减补偿（:480-481），顶穿历史才放弃。
- **闪烁器复用主线程**（:1264-1270）：postDelayed 自续（`finally` 续期 :1356-1358）而非独立线程——UI 状态必须主线程改。
- **勘误（源码实证）**：`getCursorY` 硬编码 `(y-40)`（:1052）与 `getColumnAndRow` 用 `mFontLineSpacingAndAscent`（:549）口径不一——大字号下手柄首轮落点偏，勿再复制。另 onboarding §4.1 的 `sendTextToTerminal（:356-381）` 区间略窄（实至 :435），语义无误。

## 新人提示

1. **装配顺序即雷区**：`mClient` 无空判——`updateSize` 尾部直接 `mClient.onEmulatorSet()`（:997），先 `attachSession`（:290，内部调 updateSize :300）后 `setTerminalViewClient`（:270）必 NPE。
2. **scrollCounter 契约**：`onScreenUpdated` 读（:467）必须 `clearScrollCounter()`（:496）配对，漏清则越滚越多。`setTopRow` 双参版（:1074-1079）控制是否回写 emulator，转屏恢复（:1006-1014）依赖该缓存，乱用单参版视图与仿真器滚动劈叉。
3. **坐标换算两套口径**：触摸/鼠标用 `getColumnAndRow`（:547-554），选择手柄用 `getCursorX/Y`+`getPointX/Y`（:1047-1064，含魔数 40）。改字体度量（`setTextSize` :515-518 重建 Renderer）须双路径验证。
4. **生命周期时序注释是合同**（:1242-1252）：首次进入须等 `onEmulatorSet` 回调而非紧跟 attachSession（宽高为 0 时 updateSize 静默返回 ：988）——违者症状是"光标不闪"。
