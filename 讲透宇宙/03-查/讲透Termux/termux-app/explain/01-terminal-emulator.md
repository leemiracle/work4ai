# 01 TerminalEmulator.java —— VT/XTerm 转义序列状态机

`terminal-emulator/src/main/java/com/termux/terminal/TerminalEmulator.java`（3569 行，全仓最大单类；下文锚未注明文件者均指此文件）

## 角色定位

Termux 的"心脏"：把 shell 吐出的字节流（含转义序列）翻译成可渲染的字符网格。类 Javadoc 自述——"仿真 xterm 的一个子集，而 xterm 又是 DEC vt100 子集的仿真器"（:12-13）。一个类身兼三职：**协议解析器**（ESC/CSI/OSC/DCS/APC 五类序列状态机）、**语义执行器**（光标/滚动/样式/DEC 私有模式开关）、**屏幕状态持有者**（主备双缓冲、margins、tab stops、光标）。

图谱 14 层中属 **L01 终端仿真引擎层 Terminal Emulator Core**，onboarding 定性"状态机+缓冲+PTY 宿主"（ONBOARDING.md L01 段）——本文件是"状态机"一角，PTY 宿主（TerminalSession）与缓冲（TerminalBuffer）是协作者。纯逻辑类，唯一 Android 依赖是 `android.util.Base64`（:3，OSC 52 解码用），可被 JUnit 直接驱动，图谱记 3 个测试类回归它。存在理由：Android 无系统级 pty 终端，要跑 vim/tmux/htop 就得造一个足够"像 xterm"的终端——包括对 vim/tmux 探测询问（DA2/DECRQM/termcap）给出与 xterm 一致的应答（:1890-1901、:1181-1269）。

## 内部结构

**状态机核心**：状态仅一个 int `mEscapeState`（:363），取值 24 个 `ESC_*` 常量（:56-173）：`ESC_NONE`（普通文本）→ESC(27)→按次字符分叉 `[`→CSI、`]`→OSC、`P`→DCS、`_`→APC，CSI 再按 `? > $ ' " ! *` 等中间字节细分 10 个子态。状态推进靠 `continueSequence()`（:1992-1995，同时置 `mContinueSequence=true`），`processCodePoint` default 分支末尾统一收口 `if (!mContinueSequence) mEscapeState = ESC_NONE`（:1134）——全状态机的生命线协议。

三层漏斗：`append`（:688-691）逐字节入口 → `processByte`（:693-756）手写 UTF-8 解码（overlong 检测 :703-707、C1 控制符丢弃 :711-716、坏续字节按 Unicode 6.2 规范不吞后续 :726-737）→ `processCodePoint`（:758-1137）先走快车道（OSC/DCS 大数据 fast path :761-777、APC 任意非打印字符 :780-790），再巨型 switch 处理 C0 控制符，default 按 `mEscapeState` 分派到 `doEsc`(:2009)/`doCsi`(:2134)/`doCsiQuestionMark`(:1704)/`doDcs`(:1144)/`receiveOsc`(:2639) 等。参数解析 `parseArg`（:3097-3126）：`;` 分参数、`:` 分子参数（kitty 风格，位记于 `mArgsSubParamsBitSet` :3113-3118），单参数 >9999 钳到 9999（:3108），槽共 32（:176）。

**DECSET 位标志**：13 个 DEC 私有模式开关（应用光标键/反显/原点模式/自动换行/光标可见/四种鼠标模式/括号粘贴等）压进一个 int `mCurrentDecSetFlags`（:374、:179-212），DECSET 码→内部位映射在 `mapDecSetBitToInternalBit`（:464-494），设位内嵌鼠标模式互斥（:450-455）。执行端 `doDecSetOrReset`（:1788-1886）最重的是 alt buffer 切换（case 47/1047/1049，:1851-1878）：按方向 save/restore 光标、按需 resizeScreen、进备屏先清屏。

**屏幕模型**：双缓冲——`mMainBuffer`（带 transcript 回滚，默认 2000 行、合法区 100-50000，:228-230、:541-546）与 `mAltBuffer`（恰好一屏无回滚），`mScreen` 指针二选一（:246-255）；margins 四值（:389），bottom/right 是"末行+1"半开区间（:386-388），DECSTBM 设定 top-1 修正而 bottom 不减（:2379-2385）；光标惰性换行 `mAboutToAutoWrap`（:397）实现 VT deferred wrap——停在最后一列不立即换行，等下一个可打印字符才回卷，BS 因此能"退回上一行尾"（:801-811）；样式四值 `mForeColor/mBackColor/mUnderlineColor/mEffect`（:419-422）由 SGR 处理器 `selectGraphicRendition`（:2461-2587）维护，落格前经 `getStyle()`（:3025）打包成 long；保存/恢复用内部类 `SavedScreenState`（:3555）主备屏各一份（:365-366）。

**字符串命令缓冲**（OSC/DCS/APC 共用）：`mTerminalControlArgs`（:288）容量三态——初始 16（:274）、默认上限 16384（:280）；`setOscTypeVariables`（:2679-2734）识别类型后特批大流量：OSC 52 剪贴板放行 ~100KB（Binder 上限，:2704-2710）、OSC 1337 iTerm 图像放行到 `MAX_BITMAP_SIZE+150` 并开 fast path+忽略 CR/LF 双开关（:2712-2723）。收集器带 OOM 捕获（:3147-3173），超限整段丢弃；释放策略（:3176-3193）小缓冲 setLength(0) 复用、大缓冲直接 new。

**出口 `emitCodePoint`**（:3286-3434）：可打印字符唯一出口——激活行绘制字符集时按 VT102 表把 ASCII 映射为 `█ ┌ ─ │` 等（:3288-3391）；`WcWidth` 定宽后走 autowrap 判定（:3393-3411，双宽字符在末列吞掉 :3407-3410；插入模式先右移腾位 :3413-3418；组合字符回退一列 :3420-3421），最终 `mScreen.setChar`（:3428）落格。此处留着线上 AIOOBE 防御与并发疑云注释（:3423-3427 TODO：怀疑 mCursorCol 被另一线程改）。

## 外部连接

图谱（1284 节点/2762 边）对该文件节点实证：**fan-in=8**（7 imports+1 depends_on）、**fan-out=65**（40 contains/11 imports/10 exports/3 tested_by/1 calls）——出边大头是自包含符号，真实耦合面很小。

**上游 8 个**：同模块 TerminalSession（持有并驱动）；L02 渲染侧 TerminalView 与 TerminalRenderer（`getScreen()` 读网格、`sendMouseEvent()/paste()` 反向喂序列）；app 侧 TermuxService、TermuxTerminalViewClient；跨层引用 termux-shared 的 ShellUtils 与 TermuxPropertyConstants。它是 terminal-emulator 模块的叶子出口——别人 import 它，它不 import 任何模块外类型。

**下游 11 条语义 imports 边**：全为同包类——TerminalBuffer（网格+sixel 宿主）、TextStyle/WcWidth/TerminalColors、TerminalOutput（回写通道）、TerminalSessionClient（回调）、KeyHandler（termcap 应答查表 :1245）、ITermImage/TerminalBitmap/TerminalSixel（两套图像协议）、Logger。**口径勘误**：图谱标 11 条 `imports` 边，但源码 import 语句区只有 Base64 与 `java.*`（:3-9）——同包类无需 import，这是 scanner 对同包引用的语义标注口径。onboarding 的"零依赖"应精确为"零模块外依赖（除 Base64）"，模块内自持 Logger（terminal-emulator/.../Logger.java，非 termux-shared 那个）。

## 数据流

**正向主链（shell→屏幕），以 `ls --color` 红色文件名为例**：shell 写 PTY master → JNI 读线程 → ByteQueue → `TerminalSession$MainThreadHandler.handleMessage` 读最多 64KB，调 `mEmulator.append(mReceiveBuffer, bytesRead)`（TerminalSession.java:345）——**仿真运行在主线程 Handler 上**，随后 `notifyScreenUpdate()` 触发重绘。`\033[38;5;196m` 各字节经 UTF-8 解码进 `processCodePoint`：ESC 触发 `startEscapeSequence`（:1968-1973），`[` 进 ESC_CSI，`3 8 ; 5 ; 1 9 6` 由 `parseArg` 累积，final 字节 `m` 进 `doCsi` case 'm' → `selectGraphicRendition` 识别 38;5 索引色 → `mForeColor=196`（:2555-2563）。紧随的 `f i l e` 每字符走 `emitCodePoint` → `mScreen.setChar(col,row,ch,getStyle())`（:3428），红色前景已打进样式 long。TerminalView.onDraw → `TerminalRenderer.java:69` `getScreen()` 逐行取 TerminalRow 按色彩索引查调色板上屏；sixel 走 `getSixelBitmap/getSixelRect`（TerminalRenderer.java:107-111）。

**反向链（屏幕→shell）**：触摸 → `sendMouseEvent`（TerminalView.java:571 → :553-572）→ DECSET 1006 开启时格式化为 `\033[<b;x;yM/m` 经 `mSession.write` 回 shell；旧协议打包 X10 字节且 >255-32 越界静默丢弃（:564-570）。粘贴走 `paste()`（:3541-3552）：先剥 ESC 与 C1（防转义注入）、\n→\r，再按 DECSET 2004 包 `200~/201~`。查询应答（DA1/DA2/CPR/DECRQM/termcap）同经 `mSession.write` 回流。

## 设计决策

1. **手写 switch 状态机而非表驱动/生成器**（对照 libvterm 分发表、alacritty/vte）。牺牲紧凑性换"每个序列的 VT510 规范注释就地可读"——doCsi 几乎每 case 链到 vt100.net 章节（如 DECCRA :911-920 整段引规范）。文档型状态机，可维护性押注在注释而非结构。

2. **位标志压缩 DECSET**：13 布尔压 1 int，save/restore 与"存取全部模式"（CSI ? s/r，:1763-1779）退化为一次位运算；代价是查表映射的阅读税。

3. **deferred wrap**：光标到行尾"将换未换"，精确复刻 xterm 语义——立即换行会让 BS/CR 与行宽指示全错（:391-397）。终端仿真最经典的 off-by-one 陷阱，作者选择实现而非简化。

4. **快车道优化大流量 OSC/DCS**：iTerm 图像/sixel 可达数十 MB，逐字节过完整 switch 会拖垮主线程；识别出 1337 后 `processCodePoint` 顶部直接旁路（:761-777）。sixel 分片处理（攒到上限一半或遇 `# ! "` 命令边界先消化一截，:1144-1167），并以 Raster Attributes 宽高**预分配**缓冲与位图避免反复扩容（:1620-1643）。

5. **应答策略：能答则像 xterm，不能答则沉默**：`LOG_ESCAPE_SEQUENCES=false` 编译期开关让未实现序列静默（:34）；但对生态探测必须应答且要"撒谎"——DA2 报 `\033[>41;320;0c`（:1901），注释解释 tmux 查 >270、vim 查 >140/>276 才启用矩形区/SGR 鼠标/termcap，320 是刻意跨门槛的兼容性谎报。安全边界明确：CSI t 20/21 报标题"disabled due to security concerns"实返空串（:2424-2428），paste 强制剥 ESC/C1（:3543）。

6. **主线程单线程假设 + 一处存疑**：状态机无锁，靠"唯一写者是主线程 Handler"成立；但 emitCodePoint 的 AIOOBE 防御注释自认 mCursorCol 疑被并发修改（:3423-3427 TODO）——全文件最值得警惕的未决隐患。

**图谱勘误（以源码为准）**：图谱 hub 摘要称"VT100/xterm 转义序列**全量**处理"，源码 Javadoc 明说 "emulates a **subset**"（:13）；显式不实现的有 DECSET 1004（:204）、X10 鼠标（:1819）、LNM（:3037）、reverse wrap（:1826 TODO）、HLS sixel 色（:1543-1546）。"全量"是图谱夸大，实为精心裁剪的子集。

## 新人提示

1. **改状态机先背 `mContinueSequence` 协议**。新加 CSI 子态必须 `continueSequence(新态)` 挂起，否则 :1134 立刻打回 ESC_NONE，后续字节漏进普通文本；处理完忘收尾则相反——正常字符被当参数吞掉。OSC/APC 收到"ESC+非`\`"时必须把 27 和当前字符**双双补回** args 再回 OSC 态（:2666-2672），漏补就是命令莫名缺字。另状态常量编号有洞（无 5，:58-66），别假设连续。

2. **margin 半开区间是所有坐标代码的地基**。`mBottomMargin/mRightMargin` 指"滚动区末行+1"（:386-389），全文件 Math.min/max 钳制、DECCRA/DECERA 矩形运算、emitCodePoint 的 `mRightMargin-displayWidth` 都建立在它上面；DECSTBM 的"top 减 1、bottom 不减"（:2379-2385）与 DECOM 下 `setCursorPosition` 的 effective* 换算（:3054-3063）是最易踩的两处。改 resize 记得它会重置 margins 且 tab stops 重建仅搬运旧列宽（:584-599）。

3. **双缓冲切换代码别只改一半**。`mScreen` 指针切换（:1860）伴随时序：进备屏 saveCursor→切指针→按需 resizeScreen→清屏；出备屏 restoreCursor 且 resized 时恢复"未 clip 的光标"交 resizeScreen 统一裁剪（:1858-1872）。save/restore 按"当前 mScreen"选主/备各自的 SavedScreenState（:2107/:2121），而 restore 只还原 AUTOWRAP|ORIGIN 两个 DEC 位（:2126-2127）——顺手多恢复一个模式会破坏 `CSI ? s/r` 存取对称性。任何序列改动先跑 terminal-emulator 模块测试再上真机。
