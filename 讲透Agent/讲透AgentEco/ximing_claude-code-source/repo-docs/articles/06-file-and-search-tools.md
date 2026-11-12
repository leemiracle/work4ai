---
title: Claude Code 源码拆解 06：文件与搜索工具——为什么是 grep 而不是向量索引
date: "2026-04-05 10:30"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 06/20 篇 · 对应主题：Coding Agent 内核

# 文件与搜索工具：为什么是 grep 而不是向量索引

在 RAG 盛行的 2023-2024 年，不少 Coding Agent 选择了"代码库 embedding + 向量检索"的路线。Claude Code 的源码里没有任何向量索引模块：搜索靠 ripgrep 进程，定位靠 glob，语义查询靠 LSP，文件选择靠一个手写的模糊匹配器。本篇逐一拆解这六个工具与两个支撑模块，看这个选择如何在代码里落地。

## FileReadTool：一个文件读取器能做到多复杂

FileReadTool.ts 有 1183 行，远超"打开文件返回内容"的直觉。入口的 input schema 只有四个字段：file_path、offset、limit、pages（src/tools/FileReadTool/FileReadTool.ts:227-243），但输出 schema 是一个六元判别联合：text、image、notebook、pdf、parts、file_unchanged（src/tools/FileReadTool/FileReadTool.ts:257-331）。

读取内容之前先过两层限额。limits.ts 头部的注释把设计权衡直接写成了表格：maxSizeBytes 默认 256KB、用一次 stat 在读取前拦截；maxTokens 默认 25000、读完后按实际 token 数拦截（src/tools/FileReadTool/limits.ts:2-16）。注释还记录了一次被回滚的实验：把超限行为从抛错改成截断，结果是工具错误率下降但平均 token 消耗上升，因为 100 字节的错误提示变成了 25K token 的内容（src/tools/FileReadTool/limits.ts:9-13）。token 校验本身也是两段式：先用粗略估计，估计值低于限额四分之一就直接放行，超过才调 API 精确计数（src/tools/FileReadTool/FileReadTool.ts:755-772）。

非文本分支各自独立。ipynb 走 readNotebook 解析成 cells，超限时的错误信息里直接教模型改用 `cat file | jq '.cells[:20]'` 分段读（src/tools/FileReadTool/FileReadTool.ts:822-836）。图片走 readImageWithTokenBudget：单次读入 buffer，先标准缩放，超预算再激进压缩，最终兜底是 sharp 缩到 400x400、质量 20 的 JPEG（src/tools/FileReadTool/FileReadTool.ts:1097-1182）。PDF 支持 pages 参数按页范围抽取成图片块，页数超过阈值就拒绝整读（src/tools/FileReadTool/FileReadTool.ts:894-955）。此外还有一层纯路径检查：/dev/zero、/dev/random、/dev/tty 等设备文件会直接 hang 住进程，被硬编码进黑名单（src/tools/FileReadTool/FileReadTool.ts:98-115）。

file_unchanged 这个输出类型值得单独看。如果模型对同一文件重复发起相同 offset/limit 的读取，且磁盘 mtime 未变，工具不返回内容，只返回一个 stub 占位（src/tools/FileReadTool/FileReadTool.ts:547-572）。注释里给出了数据：BQ 代理观测到约 18% 的 Read 调用是同文件碰撞，内部灰度两小时命中 1734 次去重（src/tools/FileReadTool/FileReadTool.ts:525-533）。去重只对 offset 有定义（即确实由 Read 写入）的缓存项生效：Edit/Write 写入的缓存项 offset 为 undefined，去重会把模型错指回编辑前的旧内容（src/tools/FileReadTool/FileReadTool.ts:543-546）。

## FileEditTool：775 行的字符串匹配引擎

FileEditTool 的核心不在 FileEditTool.ts，而在 utils.ts 这个 775 行的匹配引擎。它要解决的问题是：模型生成的 old_string 和磁盘上的真实字节之间永远存在系统性偏差。

第一层偏差是引号。模型输出不了花引号，源码里专门用常量定义它们，因为"Claude can't output curly quotes"（src/tools/FileEditTool/utils.ts:18-24）。findActualString 先尝试精确匹配，失败后把搜索串和文件内容同时做花引号归一化再匹配，命中后按归一化前的坐标从原文件截取真实子串返回（src/tools/FileEditTool/utils.ts:73-93）。匹配成功后还有逆向操作 preserveQuoteStyle：如果文件用的是花引号而模型给的是直引号，new_string 会被重新弯化，通过"前一个字符是空白或开括号则为开引号"的启发式判断开合，字母之间的撇号（don't）特判为右单引号（src/tools/FileEditTool/utils.ts:104-199）。

第二层偏差是 API 侧的内容消毒。DESANITIZATIONS 表维护了一组映射：模型在上下文里看到的 `<function_results>` 被洗成了 `<fnr>`，它生成的编辑串自然带着短标签，匹配前必须还原，且同样的替换要镜像应用到 new_string 上（src/tools/FileEditTool/utils.ts:531-550, 623-639）。

第三层是编辑序列自身的冲突检测。getPatchForEdits 逐条应用编辑前，会检查当前 old_string 是否是某条已应用 new_string 的子串，命中即抛错；这是模型连环编辑时最常见的自踩踏模式（src/tools/FileEditTool/utils.ts:297-311）。任何一条编辑应用后文件内容没变，也抛错（src/tools/FileEditTool/utils.ts:324-327）。

validateInput 还有几项前置防御。old_string 与 new_string 完全相同时直接拒绝（errorCode 1）；目标文件超过 1 GiB 拒绝编辑，注释解释了换算逻辑：V8/Bun 字符串上限约 2^30 字符，ASCII 文件 1 字节约等于 1 字符，1 GiB 是防止 OOM 的字节级安全线（src/tools/FileEditTool/FileEditTool.ts:79-84, 148-156）。读入文件时按 BOM 探测 UTF-16LE，并把 CRLF 统一归一化为 LF 再参与匹配（src/tools/FileEditTool/FileEditTool.ts:202-221）。

唯一性校验在 validateInput 里：`file.split(actualOldString).length - 1` 统计匹配数，多于 1 且 replace_all 为 false 时拒绝执行，错误信息明确要求模型"提供更多上下文以唯一标识"（src/tools/FileEditTool/FileEditTool.ts:329-343）。整套流程是"精确替换为主、归一化兜底、失败给可操作错误"的回退链，每一步的失败信息都写成模型能自我纠正的形式。

## FileWriteTool 与 fileStateCache：读过才准写

写路径的权限依据是 readFileState，一个挂在 ToolUseContext 上的 FileStateCache。它是带路径归一化的 LRU，默认 100 项、25MB 上限，每项记录 content、timestamp、offset、limit（src/utils/fileStateCache.ts:4-39）。offset/limit 这两个字段不是读取参数的回显，而是"模型看过文件的哪一部分"的证据。

FileWriteTool.validateInput 的核心规则：目标文件已存在但 readFileState 里没有该文件的读取记录（或记录被标记为 isPartialView，即 CLAUDE.md 自动注入时被裁剪过的部分视图），拒绝写入，报错"File has not been read yet"（src/tools/FileWriteTool/FileWriteTool.ts:198-206; src/utils/fileStateCache.ts:9-14）。读过之后再比 mtime：磁盘修改时间晚于读取时间，说明文件被用户或 linter 动过，拒绝写入（src/tools/FileWriteTool/FileWriteTool.ts:211-219）。

但 validateInput 的检查只是提前拦截，写入前的最后一次校验在 call() 内部：写完之前的临界区里用同步读重新加载文件，再次比对 readFileState 的时间戳（src/tools/FileWriteTool/FileWriteTool.ts:266-295）。两处之间所有异步操作（mkdir、fileHistoryTrackEdit）都被刻意挪到临界区外，注释说明原因："a yield between the staleness check and writeTextContent lets concurrent edits interleave"（src/tools/FileWriteTool/FileWriteTool.ts:249-254）。mtime 判为过期但读取时是全文读时，还会回退到内容比对，避免 Windows 上云同步、杀毒软件改时间戳造成的误报（src/tools/FileWriteTool/FileWriteTool.ts:283-294）。写成功后立即用新 mtime 更新缓存，使下一次写的前置检查基于新基准（src/tools/FileWriteTool/FileWriteTool.ts:332-337）。行尾策略也有一段历史：Write 是全量替换，按"模型在 content 里显式给出的行尾就是它要的"处理，固定写 LF。注释记录了旧实现的问题：旧实现保留旧文件行尾、新文件用 ripgrep 采样仓库行尾，曾在 Linux 上用 CRLF 内容覆盖 bash 脚本时静默引入 \r，cwd 下的二进制文件也会污染采样结果（src/tools/FileWriteTool/FileWriteTool.ts:300-305）。

UI 侧也参与权限确认。渲染 tool_use 时用 HighlightedCode 完整展示待写内容，拒绝时走 WriteRejectionDiff 异步加载磁盘原文生成 diff 供用户对照（src/tools/FileWriteTool/UI.tsx:98, 184-197）。模型在 UI 上"看到"的就是用户在确认框里看到的。

## Grep 与 Glob：ripgrep 进程而非向量索引

GrepTool 的 call() 是一个 ripgrep 命令行组装器。入参 schema 几乎逐字段映射 rg 参数：-A/-B/-C/-n/-i、--type、--glob、multiline 对应 `-U --multiline-dotall`（src/tools/GrepTool/GrepTool.ts:33-90）。组装时固定注入几组参数：`--hidden`、排除六个 VCS 目录（.git/.svn/.hg/.bzr/.jj/.sl）、`--max-columns 500` 防止 base64 和压缩文件刷屏，再把权限系统里的 ignore 模式翻译成 rg 的 `!**/pattern` 形式追加进去（src/tools/GrepTool/GrepTool.ts:329-427）。

输出控制围绕上下文预算设计。默认 head_limit 为 250，注释说明动机：无上限的 content 模式 grep 可以填满 20KB 的持久化阈值，一个 grep 密集的会话会烧掉 6-24K token（src/tools/GrepTool/GrepTool.ts:104-108）。传 head_limit=0 才是显式的无限逃生门（src/tools/GrepTool/GrepTool.ts:110-128）。files_with_matches 模式下，结果按文件 mtime 降序排列，最近改动的文件排在前面，这是给模型的相关性启发（src/tools/GrepTool/GrepTool.ts:529-553）。所有返回给模型的绝对路径都会被相对化以省 token（src/tools/GrepTool/GrepTool.ts:456-465）。

rg 二进制本身也有三级回退：系统 rg（只用命令名 'rg' 解析，防止当前目录下恶意 rg.exe 的 PATH 劫持）、bundled 模式下以 argv0='rg' 自举的静态编译 bun、以及按平台打包的 vendor 二进制（src/utils/ripgrep.ts:40-65）。超时默认 20 秒、WSL 放宽到 60 秒，超时不返回空结果而是抛 RipgrepTimeoutError，让模型知道搜索没完成，而不是误以为没有匹配（src/utils/ripgrep.ts:94-133）。GlobTool 更薄：同样走 ripGrep，只是参数换成 `--files` 加 glob 过滤，上限 100 个结果（src/tools/GlobTool/GlobTool.ts:154-176; src/utils/glob.ts:100-119）。

对照 RAG 路线看这组设计的取舍。向量索引需要离线建库、随编辑增量更新、在仓库切换和 worktree 场景下维持多份索引；grep 路线的索引成本是零，时效性是实时的：rg 扫的就是此刻磁盘上的字节，不存在"索引没追上代码"的窗口。代价是每次搜索都付出全量扫描的 CPU，但 ripgrep 本身就是为全量扫描优化过的工具，而 250 条 head_limit 和 20 秒超时把最坏情况钉死。对 Agent 场景还有一层考虑：grep 的结果是可验证的，返回的行号加内容就是文件里的原文，模型可以立刻用 Read 复核；向量检索返回的是相关性排序的片段，错误是软性的，模型难以自查。Coding Agent 的搜索大多是"找到那个符号/字符串在哪"，是精确问题而非相似性问题，这与 grep 的能力正好匹配。

## LSPTool：语义层的补充

grep 回答"哪里出现了这个字符串"，回答不了"这个符号的定义在哪、谁调用了它"。LSPTool 补的是这层。它支持九个操作：goToDefinition、findReferences、hover、documentSymbol、workspaceSymbol、goToImplementation、prepareCallHierarchy、incomingCalls、outgoingCalls（src/tools/LSPTool/LSPTool.ts:61-72）。

工具有两个生命周期特征：`shouldDefer: true` 且 isEnabled 依赖 isLspConnected()，语言服务器没起来时工具不出现在工具列表里（src/tools/LSPTool/LSPTool.ts:136-139）。调用时若初始化仍是 pending 就先 waitForInitialization，避免误报"no server available"（src/tools/LSPTool/LSPTool.ts:230-233）。大多数 LSP 服务器要求先 didOpen，所以工具在发请求前检查文件是否已打开，未打开则读入内容（上限 10MB）后调 manager.openFile（src/tools/LSPTool/LSPTool.ts:53, 261-278）。incomingCalls/outgoingCalls 是两步协议：先 prepareCallHierarchy 拿 CallHierarchyItem，再用第一项发第二次请求（src/tools/LSPTool/LSPTool.ts:299-334）。返回给模型前，findReferences 等位置类结果会过滤掉 gitignore 的文件（src/tools/LSPTool/LSPTool.ts:336-374）。

在工具分工上，LSP 是搜索的精确化分支：Grep 给候选面，LSP 给语义确定性。它同样不需要自建索引：索引在语言服务器进程里，由编辑器生态维护了几十年。

## native-ts/file-index：手写模糊搜索移植

最后一个模块不在工具链上，而在 @-mention 文件补全里。native-ts/file-index/index.ts 的头部注释写明来历：它是 vendor 下 Rust NAPI 模块（包装 helix-editor 的 nucleo 模糊匹配库）的纯 TypeScript 移植，API 与打分语义保持一致（src/native-ts/file-index/index.ts:1-16）。上层消费者是 hooks/fileSuggestions.ts：用 git ls-files 取跟踪文件、ripgrep 补未跟踪文件，喂给 loadFromFileListAsync（src/hooks/fileSuggestions.ts:190, 253-274）。

移植版的核心优化在两处。索引阶段为每个路径预计算小写串、a-z 字母位图和长度；搜索第一阶段用 `(charBits[i] & needleBitmap) !== needleBitmap` 做 O(1) 拒绝：路径缺少查询串中任何一个字母就直接跳过。注释给出的数据是宽查询下仍有 10%+ 的拒绝收益，稀有字符可达 90%+ 拒绝率（src/native-ts/file-index/index.ts:153-167, 208-210）。通过位图的候选走融合的 indexOf 扫描：利用 JSC/V8 的 SIMD 加速定位每个字符的最早位置，同时在循环内累计 gap 惩罚和连续奖励，避免第二次扫描（src/native-ts/file-index/index.ts:214-232）。

```typescript
// Top-k: maintain a sorted-ascending array of the best `limit` matches.
const topK: { path: string; fuzzScore: number }[] = []
let threshold = -Infinity
// ...
if (topK.length === limit &&
    scoreCeiling + consecBonus - gapPenalty <= threshold) {
  continue
}
```

（src/native-ts/file-index/index.ts:201-241）这段是 top-k 维护：只保留 limit 个最优结果，避免对所有匹配做 O(n log n) 排序；scoreCeiling 给出"假设全部拿到边界奖励"的分数上界，上界减去已知 gap 惩罚仍低于当前阈值时，连边界打分都跳过。打分常数近似 fzf-v2/nucleo：匹配 16 分、边界奖励 8、camelCase 6、连续 4，gap 起点罚 3、延伸罚 1（src/native-ts/file-index/index.ts:23-30）。最终分数是归一化的名次分，含 "test" 的路径吃 1.05 倍惩罚让非测试文件略微靠前（src/native-ts/file-index/index.ts:276-290）。大索引（注释提到 270k+ 路径）用 loadFromFileListAsync 按 4ms 时间片分块构建，首块完成即开放查询、边建边搜（src/native-ts/file-index/index.ts:72-93, 109-131）。

把原生模块移植成纯 TS 的动机没有写在代码里，但效果明确：去掉 NAPI 依赖意味着这个模糊搜索在 bundled 单文件分发、不支持原生模块的环境里也能跑。整个文件 370 行，无第三方依赖。它要替代的 nucleo 很快，但 CLI 分发要的是"够快且到处能跑"。

## 本篇涉及的源码文件

- `src/tools/FileReadTool/FileReadTool.ts`：文件读取工具，含文本/图片/PDF/notebook 分支、双层限额、重复读取去重
- `src/tools/FileReadTool/limits.ts`：读取限额定义与回滚实验记录
- `src/tools/FileEditTool/FileEditTool.ts`：编辑工具主体，含唯一性校验、mtime 陈旧检查、临界区写入
- `src/tools/FileEditTool/utils.ts`：775 行匹配引擎，含引号归一化、去消毒、编辑序列冲突检测
- `src/tools/FileWriteTool/FileWriteTool.ts`：写入工具，读过才准写、写前二次校验、行尾保留策略
- `src/tools/FileWriteTool/UI.tsx`：写入确认 UI，高亮预览与拒绝 diff
- `src/utils/fileStateCache.ts`：路径归一化 LRU 文件状态缓存，"读过"证据的载体
- `src/tools/GrepTool/GrepTool.ts`：ripgrep 参数组装器，含 head_limit、VCS 排除、mtime 排序
- `src/utils/ripgrep.ts`：rg 二进制三级回退、超时与缓冲区管理
- `src/tools/GlobTool/GlobTool.ts` + `src/utils/glob.ts`：基于 `rg --files` 的文件名匹配
- `src/tools/LSPTool/LSPTool.ts`：LSP 九操作代码智能工具，语义层搜索补充
- `src/native-ts/file-index/index.ts`：nucleo 模糊匹配的纯 TS 移植，含位图拒绝、top-k、分块异步构建
- `src/hooks/fileSuggestions.ts`：file-index 的消费方，git ls-files + ripgrep 文件列表来源
