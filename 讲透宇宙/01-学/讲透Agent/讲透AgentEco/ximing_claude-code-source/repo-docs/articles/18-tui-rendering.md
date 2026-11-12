---
title: Claude Code 源码拆解 18：TUI 渲染与交互层——重度 fork 的 Ink
date: "2026-04-12 13:30"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 18/20 篇 · 对应主题：交互工程广度

# TUI 渲染与交互层：重度 fork 的 Ink

Claude Code 的终端界面建立在 Ink（React-for-CLI）之上，但 `src/ink/` 已经不是打补丁级别的 fork：reconciler、screen buffer、输出 diff、逃逸序列解析、布局引擎全部自研或重写，外加终端能力探测、虚拟化滚动、键位系统、vim 模式和语音输入。本篇按"渲染管线 → 终端协议 → 输入系统"的顺序拆解。

## 自研 reconciler 与提交管线

渲染管线的骨架是 `react-reconciler` 的自定义 host config（src/ink/reconciler.ts:224）。宿主节点不是 DOM，而是 `createNode` 产出的 `DOMElement`/`TextNode`（src/ink/reconciler.ts:8-23），每个元素挂一个 Yoga 布局节点。host config 里有几个针对终端的特化：

- `createInstance` 把 `<Text>` 内的嵌套文本降级为 `ink-virtual-text`，并直接禁止 `<Box>` 嵌在 `<Text>` 内（src/ink/reconciler.ts:338-345），因为终端没有任意矩形嵌套语义。
- `resetAfterCommit` 是管线的驱动点：先调 `rootNode.onComputeLayout()` 跑 Yoga 布局，再调 `onRender` 渲染（src/ink/reconciler.ts:277-304）。布局发生在 React commit 阶段，`useLayoutEffect` 能读到当帧的布局数据。
- 内置了 commit 级 profiling：`CLAUDE_CODE_COMMIT_LOG` 打开后记录每秒 commit 数、最大间隔、慢布局（>20ms）和慢绘制（>10ms）（src/ink/reconciler.ts:250-313）。
- 调试重绘时，`createInstance` 会沿 Fiber 的 `_debugOwner`/`return` 链向上收集组件名（跳过 ink-box 等宿主元素），存到节点的 `debugOwnerChain`，由 `CLAUDE_CODE_DEBUG_REPAINTS` 开启（src/ink/reconciler.ts:152-185, 354-356）。这让"哪个组件导致了这次重绘"在没有 DevTools 的终端里可回答。

`Ink` 类负责帧调度。`scheduleRender` 是按 `FRAME_INTERVAL_MS` 节流的 `queueMicrotask(this.onRender)`（src/ink/ink.tsx:212-216）。注释解释了为什么用 microtask 而不是同步渲染：`resetAfterCommit` 早于 React 的 layout 阶段，同步渲染会让 `useDeclaredCursor` 这类 layout effect 设置的 cursor 状态滞后一个 commit，原生光标就会比输入框插入符慢一键（src/ink/ink.tsx:203-209）。`onComputeLayout` 里直接对根 Yoga 节点 `setWidth` + `calculateLayout` 并记录耗时（src/ink/ink.tsx:246-257）。

`onRender` 一帧的工作：调用 renderer 把 DOM 树画进 back buffer，处理滚动跟随时的选区平移，然后套选区/搜索高亮 overlay（src/ink/ink.tsx:420-539）。选区 overlay 直接改写 screen buffer 里单元格的 styleId，"让 diff 把选区当作普通单元格变化拾取，LogUpdate 保持为纯 diff 引擎"（src/ink/ink.tsx:515-517）。resize 处理刻意不做 debounce：debounce 会打开一个窗口，`stdout.columns` 已是新值而 Yoga 还是旧值，期间任何节流渲染（spinner、时钟）都会被 log-update 判定为宽度变化而清屏，debounce 触发后再清一次，形成双重闪烁；同步处理保证尺寸状态始终一致（src/ink/ink.tsx:303-315）。

## Screen buffer：打包单元格与差量 stdout 写入

`screen.ts`（1486 行）是渲染性能优化的重心。终端屏幕不是对象数组，而是打包的 `Int32Array`：每个单元格占 2 个 Int32，word0 是 charId（CharPool 字符串驻留池的索引），word1 是 `styleId[31:17] | hyperlinkId[16:2] | width[1:0]`（src/ink/screen.ts:332-348）。注释给出了动机：200×120 的屏幕避免分配 24000 个对象，diff 时每次比较只有 2 次整数加载（src/ink/screen.ts:355-364）。另有一个 `BigInt64Array` 视图用于整块填充清零（src/ink/screen.ts:369-370）。

三个共享池把比较全部整数化：`CharPool` 对 ASCII 走 128 项直查表快路径（src/ink/screen.ts:29-48）；`StylePool` 的 intern 把"样式是否对空格可见"（背景、反色、下划线）编码进 ID 的 bit 0，渲染器用一次位掩码就能跳过不可见空格（src/ink/screen.ts:122-141）；样式间的转移序列（`diffAnsiCodes` 的结果）按 `(fromId, toId)` 缓存成字符串，首次之后零分配（src/ink/screen.ts:148-162）。宽字符（CJK/emoji）用显式 spacer 单元格表示：`Wide` 本体 + `SpacerTail` 占位 + 软换行边界的 `SpacerHead`（src/ink/screen.ts:288-300）。

```typescript
function packWord1(
  styleId: number,
  hyperlinkId: number,
  width: number,
): number {
  return (styleId << STYLE_SHIFT) | (hyperlinkId << HYPERLINK_SHIFT) | width
}
```

打包的回报在 diff 路径上：未写入的单元格两个 word 全为 0，与"显式清除过的单元格"在位级不可区分，`diffEach` 因此可以不做任何归一化直接比较原始整数（src/ink/screen.ts:315-323）。除了单元格本体，`Screen` 还按帧维护三个附加结构：`damage` 是被写入（非 blit）区域的包围盒，diff 只需遍历可能变化的部分（src/ink/screen.ts:379-383）；`noSelect` 是每单元格 1 字节的位图，给 `<NoSelect>` 标记行号、diff 符号等栏位，让鼠标拖选 diff 时复制出干净的代码（src/ink/screen.ts:385-392）；`softWrap` 按行记录软换行续行信息，使复制时能把词回绕断开的行拼回原样（src/ink/screen.ts:394-414）。这三个结构都由 blit/shiftRows 随单元格一起拷贝，保证滚动优化不丢失语义。

`LogUpdate.render(prev, next)` 负责把两帧的差变成 stdout 字节流（src/ink/log-update.ts:123-128）。它的分支对应终端渲染里几类难处理的情况：

- 视口变化：高度变矮或宽度变化时无法预测重排后的布局，直接全量重绘（`fullResetSequence_CAUSES_FLICKER`）（src/ink/log-update.ts:142-147）。
- DECSTBM 硬件滚动：ScrollBox 的 scrollTop 变化时，不重写整个区域，而是发 `CSI top;bot r` 设滚动区 + `CSI n S/T` 硬件滚动，同时用 `shiftRows` 在 prev buffer 上模拟同样的位移，让后续 diff 自然只剩"滚进来的新行"（src/ink/log-update.ts:149-185）。`decstbmSafe=false` 时（终端不支持 DEC 2026 同步更新）退回普通 diff，因为没有原子性保证时中间态会造成可见跳动。

```typescript
if (altScreen && next.scrollHint && decstbmSafe) {
  const { top, bottom, delta } = next.scrollHint
  if (top >= 0 && bottom < prev.screen.height && bottom < next.screen.height) {
    shiftRows(prev.screen, top, bottom, delta)
    scrollPatch = [{
      type: 'stdout',
      content:
        setScrollRegion(top + 1, bottom + 1) +
        (delta > 0 ? csiScrollUp(delta) : csiScrollDown(-delta)) +
        RESET_SCROLL_REGION + CURSOR_HOME,
    }]
  }
}
```

这里有双重记账：发给终端的是硬件滚动序列，发给本地 prev buffer 的是等价的 `shiftRows`，两者必须严格一致，否则下一帧的 diff 基准就错了。`scrollHint` 由上游 `render-node-to-output.ts` 在检测到 ScrollBox scrollTop 变化且其余布局未动时设置（src/ink/render-node-to-output.ts:44-50）。
- scrollback 不可达检测：光标只能用相对移动，而已滚进 scrollback 的行无法到达。渲染前先用 `diffEach` 早退扫描，只要变化落在 scrollback 行就触发全量重绘（src/ink/log-update.ts:221-248）。
- 主循环逐单元格 diff：跳过 spacer、跳过无需覆盖的空单元格（避免行尾空格触发自动换行）、`moveCursorTo` 后用 StylePool 的缓存转移串写样式（src/ink/log-update.ts:308-363）。

再往上，`render-node-to-output.ts`（1462 行）把布局后的 DOM 树画进 `Output`。主要优化是子树 blit：节点不脏且 Yoga 位置尺寸与缓存一致时，直接从 prevScreen 拷贝整块矩形而不重新渲染（src/ink/render-node-to-output.ts:452-482）。`Output` 把绘制表达为操作流，操作有 `write`/`clip`/`unclip`/`blit`/`clear`/`shift`/`noSelect`（src/ink/output.ts:62-69）；clip 用 `intersectClip` 做父子裁剪区求交（src/ink/output.ts:104-112）。滚轮滚动还有终端自适应：xterm.js（VS Code）用固定步长的平滑 drain（≤5 行一次 drain 完，避免慢速点击的卡顿感），iTerm2/Ghostty 等按比例 drain（src/ink/render-node-to-output.ts:106-150）。

## termio：逃逸序列 tokenizer 与能力探测

`src/ink/termio/` 是一套 ANSI 逃逸序列处理库。`tokenize.ts` 是流式 tokenizer：状态机覆盖 ground/escape/csi/ss3/osc/dcs/apc 等状态，只做序列边界切分，不做语义解释（src/ink/termio/tokenize.ts:16-24）。

```typescript
type State =
  | 'ground'
  | 'escape'
  | 'escapeIntermediate'
  | 'csi'
  | 'ss3'
  | 'osc'
  | 'dcs'
  | 'apc'
```

它支持增量 feed + flush，缓冲区保留不完整序列，TCP 式的分包不会切断序列（src/ink/termio/tokenize.ts:57-92）。一个细节：`x10Mouse` 选项只在 stdin 侧开启：`\x1b[M` 在输入流里是 X10 鼠标事件前缀，在输出流里是 CSI DL（删行），在输出侧开启会吞掉显示文本（src/ink/termio/tokenize.ts:37-44）。同一字节流在两个方向上的语义分歧被显式建模为选项，而不是隐式约定。`parser.ts` 在 tokenizer 之上产出语义 Action，并自己做 grapheme 宽度判定（emoji、东亚宽字符区间）（src/ink/termio/parser.ts:29-69）。OSC 侧还处理了 tmux/screen 的 DCS passthrough 包装：tmux 下把 `\x1b` 双写后包进 `\x1bPtmux;...\x1b\\`，且刻意不包装 BEL：裸 `\x07` 会触发 tmux 的 bell-action，而包装后是 tmux 不可见的 DCS 载荷（src/ink/termio/osc.ts:23-44）。

`terminal-querier.ts` 解决的是"终端查询与键盘输入共享 stdin"的响应归属问题。它不用超时：每批查询以 DA1（`CSI c`）作为哨兵收尾。自 VT100 起所有终端都会应答 DA1，且终端按序应答，所以响应先于 DA1 到达即支持，DA1 先到即不支持（src/ink/terminal-querier.ts:9-12）。查询构造器覆盖 DECRQM（同步更新模式 2026）、Kitty keyboard 协议、OSC 10/11 动态颜色、DECXCPR 光标位置等（src/ink/terminal-querier.ts:49-101）。

```typescript
export function decrqm(mode: number): TerminalQuery<DecrpmResponse> {
  return {
    request: csi(`?${mode}$p`),
    match: (r): r is DecrpmResponse => r.type === 'decrpm' && r.mode === mode,
  }
}
```

每个查询是"出站序列 + 入站响应匹配器"的对子，querier 批量发出后按到达顺序兑现 Promise。其中 DECXCPR 特意用 `CSI ? 6 n` 的 DEC 私有形式，因为普通 DSR 的响应 `CSI row;col R` 与 Shift+F3（`CSI 1;2 R`）无法区分（src/ink/terminal-querier.ts:83-92）；XTVERSION 查询用来识别 xterm.js，它走 pty 而非环境变量，所以 SSH 场景下依然有效（src/ink/terminal-querier.ts:103-113）。识别结果回流到渲染层：前文滚轮 drain 的 xterm.js 特判就依赖这个探测（src/ink/render-node-to-output.ts:20-25）。

## Yoga 的纯 TypeScript 移植

布局引擎不用原生 WASM/编译模块，而是 `src/native-ts/yoga-layout/index.ts`（2578 行），即 Meta yoga-layout 的纯 TS 移植。文件头明确列出了取舍：单遍 flexbox 实现覆盖 Ink 实际使用的子集（flex-direction/grow/shrink/basis、align、justify、margin/padding/border/gap、measure 函数），另有为规范对齐而实现但 Ink 未用的 flex-wrap、align-content、display: contents、baseline 对齐；不实现 aspect-ratio、content-box、RTL（src/native-ts/yoga-layout/index.ts:1-38）。移植版还带了 instrumentation：`getYogaCounters()` 暴露 visited/measured/cacheHits/live 计数，reconciler 的慢布局日志直接读它（src/ink/reconciler.ts:283-288）。纯 TS 的好处是消除了原生模块的构建/分发矩阵，代价是需要自行保证与上游语义对齐。

## VirtualMessageList：长对话虚拟化

对话 transcript 可能有几千条消息，`VirtualMessageList.tsx`（1081 行）与 `useVirtualScroll` 配合做窗口化渲染。主要参数在 `useVirtualScroll.ts`：未测量项的默认估高故意取低（3 行），高估会导致视口底部留白，低估只是多挂几项进 overscan（src/hooks/useVirtualScroll.ts:14-19）；overscan 上下各 80 行（src/hooks/useVirtualScroll.ts:24）；scrollTop 按 `OVERSCAN_ROWS >> 1` 量化后才作为 `useSyncExternalStore` 的快照，否则每次滚轮 tick 都触发完整 React commit + Yoga 布局 + Ink diff（src/hooks/useVirtualScroll.ts:27-36）；单次 commit 最多新挂 25 项（`SLIDE_STEP`），因为每个 MessageRow 首渲染约 1.5ms，一次挂 194 项会造成约 290ms 的同步阻塞（src/hooks/useVirtualScroll.ts:48-58）。

`VirtualMessageList` 本身只渲染 `messages.slice(start, end)`（src/components/VirtualMessageList.tsx:859），上下用 spacer 补足高度。组件还承载了 transcript 搜索的整套状态机：`JumpHandle` 暴露 `setSearchQuery`/`nextMatch`/`prevMatch`/`warmSearchIndex` 等命令式接口（src/components/VirtualMessageList.tsx:48-68）；搜索文本预先 lowercase 并缓存，每次击键只做 `indexOf`（src/components/VirtualMessageList.tsx:84-88）；n/N 跳转若目标未挂载，先 `scrollToIndex` 触发挂载，再在 passive effect 里扫描定位高亮，跳转中的连续 n/N 用一深队列合并（src/components/VirtualMessageList.tsx:417-447）。

## keybindings：分层、校验与保留键

键位系统分四层。默认绑定按 context（Global/Chat/…）组织成 `KeybindingBlock[]`，并处理平台差异：Windows 上图片粘贴是 `alt+v`（`ctrl+v` 是系统粘贴），无 VT 模式的 Windows Terminal 用 `meta+m` 替代 `shift+tab` 切换模式（src/keybindings/defaultBindings.ts:15-30）；feature flag 控制下的绑定（如 QUICK_SEARCH 的 `ctrl+shift+f`）在构建期决定是否编入（src/keybindings/defaultBindings.ts:52-59）。`ctrl+c`/`ctrl+d` 定义在默认绑定里但标记为不可重绑（src/keybindings/defaultBindings.ts:36-41）。

用户绑定从 `~/.claude/keybindings.json` 加载，chokidar 监听变更并等写入稳定（500ms 阈值、200ms 轮询）后热重载。编辑器保存通常是"写临时文件 + rename"的多步操作，稳定窗口避免读到半截 JSON；目前该能力由 GrowthBook gate `tengu_keybinding_customization_release` 控制（src/keybindings/loadUserBindings.ts:41-56）。加载结果带 telemetry：自定义绑定加载事件每天最多上报一次，用于估算自定义键位的用户占比（src/keybindings/loadUserBindings.ts:83-90）。按键字符串的解析支持修饰键别名（ctrl/control、alt/opt/option、cmd/super/win）和特殊键名归一（esc→escape、return→enter、Unicode 箭头→up/down 等）（src/keybindings/parser.ts:13-75）。解析是纯函数，`resolveKey` 在给定 active contexts 下做匹配，"后出现的绑定覆盖先出现的"，`action: null` 表示显式解绑（src/keybindings/resolver.ts:31-58）；chord（`ctrl+x ctrl+k`）有独立的 `chord_started` 中间态（src/keybindings/resolver.ts:15-19）。

校验层枚举了哪些键不能重绑：`ctrl+c`/`ctrl+d` 硬编码不可重绑，`ctrl+m` 因为在终端里与 Enter 同发 CR 而禁止，macOS 的 `cmd+c/v/q/w/space` 等会被系统拦截（src/keybindings/reservedShortcuts.ts:16-67）。比较前先做 chord 感知的归一化：按空格分段、逐段拆修饰键排序，避免把 "ctrl+x ctrl+b" 压扁成最后一个键（src/keybindings/reservedShortcuts.ts:86-127）。`validate.ts` 还检查未知 context、JSON 重复键，以及 command 绑定必须放在 Chat context（src/keybindings/validate.ts:158-213, 250-263）。

## vim 模式：显式状态机

vim 编辑不是正则堆出来的，而是一张显式状态转移表。`CommandState` 有 11 个状态：idle、count、operator、operatorCount、operatorFind、operatorTextObj、find、g、operatorG、replace、indent（src/vim/types.ts:59-75）。`transition()` 按状态类型分发到各自的 `from*` 函数（src/vim/transitions.ts:59-88），每个函数返回 `{ next?, execute? }`，要么转移状态，要么产生一个闭包执行副作用。

```typescript
export function transition(
  state: CommandState,
  input: string,
  ctx: TransitionContext,
): TransitionResult {
  switch (state.type) {
    case 'idle':           return fromIdle(input, ctx)
    case 'count':          return fromCount(state, input, ctx)
    case 'operator':       return fromOperator(state, input, ctx)
    case 'operatorCount':  return fromOperatorCount(state, input, ctx)
    case 'operatorFind':   return fromOperatorFind(state, input, ctx)
    // ...
  }
}
```

这个结构把 vim 的"操作符 + 次数 + 动作"文法直接编码成状态：`d` 进入 operator，`d2` 进入 operatorCount，`d2w` 在 fromOperatorCount 里合成执行。返回闭包而非直接执行，是为了让调用方决定何时应用副作用（撤销分组的边界）。motions 是纯函数：`resolveMotion` 按 count 重复应用单步 motion，撞到边界（`next.equals(result)`）即停（src/vim/motions.ts:13-25）；`h/l/j/k/w/b/e/W/B/E/0/^/$/G/gj/gk` 全部委托给 `Cursor` 类的方法（src/vim/motions.ts:30-67）。vim 语义细节有显式标注：`e/E/$` 是 inclusive motion，`j/k/G/gg` 是 linewise，而 `gj/gk` 按 `:help gj` 是 characterwise exclusive（src/vim/motions.ts:70-82）。operators 通过 `OperatorContext` 拿到 cursor/text/register/recordChange 等能力（src/vim/operators.ts:26-37），`executeOperatorMotion` 先解析 motion 求 range，再 `applyOperator` 并记录变更以支持 `.` 重复（src/vim/operators.ts:42-54）。

## useVoice：按住说话

语音输入是一个 hook：按住绑定键录音、松开提交，按键自动重复事件重置内部计时器，`RELEASE_TIMEOUT_MS`（200ms）内没有新按键事件就自动停止。这兼容了终端无法上报"物理按键松开"的限制：按住不放时终端只会持续发来重复的 keydown（src/hooks/useVoice.ts:1-7, 160）。录音走 macOS 原生音频模块或 SoX，STT 走 Anthropic voice_stream（Deepgram 后端）的 WebSocket。语言处理是防御式的：系统 locale 语言名（含本地名，如"日本語"、"español"）映射到 BCP-47 码，且必须落在服务端 allowlist 子集内，否则服务端会以 1008 关闭连接，不支持的回退到 `en`（src/hooks/useVoice.ts:34-93）。原生模块延迟加载，因为 macOS 上 dlopen 音频模块会触发 TCC 麦克风权限弹窗（src/hooks/useVoice.ts:136-138, 526）。还有 focus 驱动模式：终端获得焦点自动开始录音（src/hooks/useVoice.ts:572-573）。

## 本篇涉及的源码文件

- `src/ink/ink.tsx`：Ink 主类，帧调度、resize/挂起恢复、选区 overlay 接入
- `src/ink/reconciler.ts`：react-reconciler host config 与 commit 级 profiling
- `src/ink/screen.ts`：打包 Int32Array screen buffer、CharPool/StylePool 驻留池
- `src/ink/log-update.ts`：帧间 diff 到 stdout 操作流，DECSTBM 硬件滚动与 scrollback 检测
- `src/ink/render-node-to-output.ts`：布局后 DOM 树到 Output 的绘制，子树 blit 与滚动 drain
- `src/ink/output.ts`：绘制操作流（write/clip/blit/clear/shift）与裁剪求交
- `src/ink/termio/tokenize.ts`：流式逃逸序列边界 tokenizer
- `src/ink/termio/parser.ts`：语义 Action 解析器与 grapheme 宽度判定
- `src/ink/termio/osc.ts`：OSC 序列生成、tmux/screen passthrough、OSC 52 剪贴板
- `src/ink/terminal-querier.ts`：DA1 哨兵式终端能力探测（DECRQM/Kitty/OSC 颜色/XTVERSION）
- `src/native-ts/yoga-layout/index.ts`：yoga-layout 的 2578 行纯 TS 移植
- `src/components/VirtualMessageList.tsx`：长对话虚拟化渲染与 transcript 搜索状态机
- `src/hooks/useVirtualScroll.ts`：窗口化参数，overscan、scrollTop 量化、分批挂载
- `src/keybindings/defaultBindings.ts`：默认绑定与平台/feature-flag 差异
- `src/keybindings/loadUserBindings.ts`：用户 keybindings.json 加载与热重载
- `src/keybindings/parser.ts`：按键字符串与 chord 解析
- `src/keybindings/resolver.ts`：纯函数按键解析（含 chord 中间态）
- `src/keybindings/reservedShortcuts.ts`：不可重绑/系统保留快捷键与归一化比较
- `src/keybindings/validate.ts`：用户绑定的 context/重复键/命令绑定校验
- `src/vim/transitions.ts`：vim 命令状态机转移表（490 行）
- `src/vim/motions.ts`：motion 纯函数与 inclusive/linewise 语义标注
- `src/vim/operators.ts`：operator 执行与变更记录（支持 `.` 重复）
- `src/vim/types.ts`：CommandState 11 状态与变更记录类型
- `src/hooks/useVoice.ts`：按住说话录音、voice_stream STT 与语言回退
