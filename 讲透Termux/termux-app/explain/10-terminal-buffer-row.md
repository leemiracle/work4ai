# 10 · 屏幕缓冲与行存储：TerminalBuffer + TerminalRow

> 目标文件：`terminal-emulator/src/main/java/com/termux/terminal/TerminalBuffer.java` 与同目录 `TerminalRow.java`。L01 终端仿真引擎层的存储半壁：仿真器负责"解释"，这两个类负责"记住"。

## 一、角色定位

TerminalBuffer 类 Javadoc 第一句即自我定义："A circular buffer of TerminalRow:s which keeps notes about what is visible on a logical screen and the scroll history"（TerminalBuffer.java:14）——一个环形数组同时装下可见屏幕与滚出顶部的回滚历史（transcript），靠 `mScreenFirstRow` 分界。TerminalRow 是环上一槽位：一行的紧凑 char 文本数组 + 每列一个打包样式 long（TerminalRow.java:43,49）。

图谱 L01 层（21 文件）枢纽数据：TerminalBuffer fanIn=5 / fanOut=44，TerminalRow fanIn=2 / fanOut=12（onboard-input.json）。fanIn 与 import 实测吻合：跨包 import 仅 3 处（TerminalRenderer.java:12、TextSelectionCursorController.java:16、ShellUtils.java:7），加同包免 import 的 TerminalEmulator 与 TerminalBitmap 恰为 5 个消费者。

存在理由：TerminalEmulator 是纯转义序列状态机，屏幕内容须落在可被渲染、选区、导出共享读取的独立结构——否则 vim 退出恢复画面、选中复制、错误报告抓上下文（ShellUtils.java:64-66）都谈不上。

## 二、内部结构

### TerminalRow：一行双数组

核心是**双索引体系并存**：`char[] mText` + `mSpaceUsed`（TerminalRow.java:43-45）按 Java char 偏移紧凑存储，长度可变（组合字符追加、代理对占 2 char）；`long[] mStyle`（:49）严格每列一格。列号→char 偏移由 `findStartOfColumn()` 换算（:94-130）：逐 char 走行、按 `WcWidth.width()` 累加显示宽、跳过零宽字符。

mStyle 的 64 位打包由 TextStyle 定义：低 16 位 flags（11 个在用）+ 中 24 位背景色 + 高 24 位前景色（TextStyle.java:4-12）。调色板色仅占 9 位移到 16/40 位，真彩色占满 24 位并置标志位（:53-65）。sixel 位图复用同一 long 做**标签联合体**：num<<16 | y<<32 | x<<48 塞进与颜色重叠的位段（:94-95），靠 bit15 的 TERMINAL_BITMAP 分流解码（:99）。

`setChar()`（TerminalRow.java:155-278）是单点写入核心。先走快路径：本行从未出现非 1 宽字符/代理对（`mHasNonOneWidthOrSurrogateChars`，:51）时列号==char 偏移，直接 `mText[columnToSet]=(char)codePoint` 返回（:168-174）。慢路径处理四类边角：组合字符（宽 0）附着列尾而非覆盖（:216-219），每列上限 15——UAX15-D3 标准 30 的一半，防恶意序列撑爆内存（:26-38）；覆盖宽字符后半时递归清前半为空格（:186）；列 span 变化时 System.arraycopy 平移、不足按 `text.length+mColumns` 步长扩容（:226-242）；宽→窄补空格、窄→宽吞下一列（:248-277）。构造预留 1.5 倍列数余量（:12,58），`clear()` 把 mSpaceUsed 重置为 mColumns 而非数组长（:149）。

### TerminalBuffer：环形数组 + 双坐标系

五字段撑起状态（TerminalBuffer.java:27-35）：`mLines` 行数组、`mTotalRows` 数组长、`mScreenRows/mColumns` 可见区、`mActiveTranscriptRows` 有效历史数、`mScreenFirstRow` 屏幕起点。外部坐标系 `-mActiveTranscriptRows .. mScreenRows-1`（负=历史，0 起=屏幕），`externalToInternalRow()` 取模映射（:241-246），Javadoc 附对照表（:220-236）。

滚动是最便宜的操作：`scrollDownOneLine()` 不搬行数据，只 `mScreenFirstRow=(mScreenFirstRow+1)%mTotalRows`（:460），历史未满 `mTotalRows-mScreenRows` 时自增（:462），再清底端新露出行（:465-474）。滚动区外的固定行靠 `blockCopyLinesDown()` 自底向上搬**指针**保位（:428-440）。`blockCopy/blockSet` 服务 CSI 区域指令（:489-499,506-518）；`setOrClearEffect` 服务 DECCARA，按列直写 `line.mStyle[x]`（:536-558）。另有 sixel 登记处：位图 HashMap+30 秒节流引用扫描 GC（:46,604-675,740-767）。

## 三、外部连接

**上游写入方**：TerminalEmulator 持三引用——`mMainBuffer`（带 transcript，历史行数默认 2000、可配 100-50000，TerminalEmulator.java:228-230,541-543）、`mAltBuffer`（totalRows=rows 零历史，:499）、`mScreen` 指向当前者，DECSET 1049 切屏换指向（:1856）。调用面实测：`blockCopy`×13、`blockSet`×6、`setChar`×3、sixel 族×8。

**下游读取方**：渲染热路径 TerminalRenderer.render() 每帧直取 `lineObject.mText` 与 `getSpaceUsed()` 逐 char 绘制（TerminalRenderer.java:87-89）；选区控制器用 `getSelectedText` 逐格试探（TextSelectionCursorController.java:99-104）。位图写入侧 TerminalBitmap.buildOrThrow 逐格写 `'+'` 占位+打包样式（TerminalBitmap.java:373）。测试：TerminalRowTest 15 用例直测行模型（含 ATE145 回归 :366），ResizeTest/ScreenBufferTest 走全链。

## 四、数据流

以输出 `echo 好` 为例：emitCodePoint 算目标列并防御 column<0（TerminalEmulator.java:3423-3427）→ `mScreen.setChar(...)`（:3428）→ buffer 边界检查后 `allocateFullLineIfNecessary()` 懒分配（首次写才 new 行，TerminalBuffer.java:520-528）→ TerminalRow.setChar：'好'宽 2，首次写入即把该行永久降级慢路径（TerminalRow.java:169-170），mStyle[列]=样式（:159）+ mText 平移写入（:246）。渲染侧读同一份 mText 画字上色。换行触底时 emulator.scrollDownOneLine 判断无横向 margin 后调 buffer 版只挪指针（TerminalEmulator.java:3065-3075）——一行零拷贝进历史。

## 五、设计决策

**1. 双数组而非 Cell 对象数组。** 80 列×万行历史=80 万对象，GC 不可接受；现方案纯 ASCII 行零换算，仅宽/组合字符行付换算税。

**2. 环形缓冲而非尾部追加+头部删除。** 后者每次滚动 O(历史行数)；前者 O(1) 挪指针，代价是每次访问取一次模。

**3. resize 双路径。** 快路径（列不变且行数不增，TerminalBuffer.java:270-297）不碰行内容：缩行自底向上跳过光标下方空行少丢内容（:275-281），扩行从历史最多取回 `mActiveTranscriptRows` 行、不足补空（:282-291），最后只调三个数。慢路径（列变，:298-415）重建全部行后**逐字符重排**：按新列宽重新断行、处理代理对与零宽字符、边排边滚动溢出，O(全部历史字符)——字体一变列数必变，无法避免。

**4. 自曝的家丑注释。** 慢路径里 "NEWLY INTRODUCED BUG! Should not index oldLine.mStyle with char indices"（TerminalBuffer.java:359-360）——被注释掉的判断想同时比样式，但循环变量是 char 下标而 mStyle 按列索引，必错位。

**5. 与 TerminalEmulator 的分工红线。** buffer 不知道光标与转义状态，emulator 不持行内容；但 scrollDownOneLine 有语义陷阱——buffer 版会把滚出行**送入历史**，emulator 包一层：有横向 margin 时改走 blockCopy+blockSet 不进历史（TerminalEmulator.java:3068-3073），选错版本历史被污染。

**6. alt 屏与位图回收。** alt 屏 resize 时历史强制归零（TerminalBuffer.java:295）。位图回收同时扫 blankRow 与 internal row+1 两行（:722-733）——滚动区可设在屏幕中部（TerminalEmulator.java:3074），多行位图可能骑两行，须一并回收。

## 六、新人提示

1. **列号与 char 偏移绝不能混用**（最大坑）。`mStyle[x]` 的 x 必须是列号，`mText[i]` 的 i 必须先经 findStartOfColumn 换算；TerminalBuffer.java:359 注释就是前人踩坑现场。
2. **不要绕过 setChar 直写 mText**。快路径由 `mHasNonOneWidthOrSurrogateChars` 单向开关保护（置 true 永不回头，TerminalRow.java:168-171），直写宽字符不置位会让后续写入错位；同理 resize 慢路径后 mLines 全换新对象（TerminalBuffer.java:300-303），缓存的行引用会指向旧世代。
3. **resize 传参三件套别拼错**。列数差 1 就走全量重排；cursor 是 int[2] 且被原地改写（TerminalBuffer.java:413-414,418）；alt 屏标志决定历史归零（:295）。另：宽字符写末列抛 IllegalArgumentException（TerminalRow.java:262-263），emulator 上游有 column 越界防御（TerminalEmulator.java:3423-3427），自加写入路径须设防。
