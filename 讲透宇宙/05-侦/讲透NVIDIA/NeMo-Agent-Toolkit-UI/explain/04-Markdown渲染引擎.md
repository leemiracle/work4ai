# 04 · Markdown 消息渲染引擎（components/Markdown 群）

## 角色定位

`components/Markdown/` 八个文件是聊天气泡的内容渲染引擎：把 LLM 输出的 markdown 文本（含 GFM 表格、LaTeX 公式、内嵌 HTML、代码块、七类图表 JSON、折叠的中间步骤树）变成可交互 UI。它与 ChatMessage.tsx 是「壳与芯」关系——壳管头像/编辑/反馈，芯管一切富文本。

## 内部结构

**入口双通道**（ChatMessage.tsx）：中间步骤区与正文区各一个 MemoizedReactMarkdown 实例（`ChatMessage.tsx:352-372`、`ChatMessage.tsx:376-395`），插件栈同为 remarkGfm+remarkMath+rehypeRaw（`ChatMessage.tsx:321-322`）；组件映射来自工厂（`ChatMessage.tsx:91`）。导出/复制时把步骤树与正文文本合流（`ChatMessage.tsx:239-248`）。

**MemoizedReactMarkdown.tsx（31 行）**：核心是 `customUrlTransform`——react-markdown v9 默认 urlTransform 会剥掉 data: URI，此处对 `data:` 前缀直接放行、其余走默认（`MemoizedReactMarkdown.tsx:10-17`），粘贴的 base64 内联图才活得了；memo 自定义比较器只比 children 与 className（`MemoizedReactMarkdown.tsx:27-29`）。

**CustomComponents.tsx（198 行）**：`getReactMarkDownCustomComponents(messageIndex)` 工厂按消息索引闭包生成 14 种元素映射（`CustomComponents.tsx:12-16`）。每个组件独立 memo + lodash isEqual 深比较——code 内联码与块码分岔（`CustomComponents.tsx:27-46`，language- 正则判内联）、chart 把 children 去 newline 后 JSON.parse 喂 Chart（`CustomComponents.tsx:51-62`）、a 强制 target=_blank+noopener（`CustomComponents.tsx:97-112`）、sup 过滤空串与孤立逗号（`CustomComponents.tsx:135-167`）、img/video/details/summary 各委托专门组件（`CustomComponents.tsx:181-196`）。

**CodeBlock.tsx（121 行）**：Prism+oneDark 高亮（`CodeBlock.tsx:100-117`）；json 语言先单引号→双引号替换（`CodeBlock.tsx:22-28`）再 pretty-print（`CodeBlock.tsx:30-36`）；复制按钮 2s 反馈（`CodeBlock.tsx:38-52`）；下载按钮按 programmingLanguages 扩展名映射生成 blob 链接（`CodeBlock.tsx:54-77`）。

**CustomDetails.tsx（137 行）**：中间步骤折叠面板。`shouldOpen` 策略三级：sessionStorage 用户手动态最优先（`CustomDetails.tsx:54`）、设置项 expandIntermediateSteps 且末条消息（`CustomDetails.tsx:65-68`）、流式中最后一步强制展开；手动切换写回 sessionStorage（`CustomDetails.tsx:88-93`）；流式中顶层面板挂进度条（`CustomDetails.tsx:127-133`，animate-loadingBar）；展开态变化时 autoScroll 联动 scrollIntoView（`CustomDetails.tsx:77-85`）。

**配套小件**：Chart.tsx 306 行（recharts 七类图 + react-force-graph-2d 力导向图，dynamic ssr:false 规避 window）、Image/Video 走 `utils/media/validation.ts:6` 的 SSRF 校验后才渲染、Loading.tsx 流式占位。

## 外部连接

上游是 ChatMessage 传入的 message.content 文本与 intermediateSteps 树（经 `utils/app/helper.ts:272` 的 generateContentIntermediate 转成 markdown 的 details 嵌套结构）；主题色 #76b900（NVIDIA 绿）散布在各组件 className；codeblock.ts 提供 programmingLanguages 扩展名表与随机文件名（`CodeBlock.tsx:7-10` import）。

## 数据流

一条助手消息更新 → ChatMessage 重渲染 → MemoizedReactMarkdown 浅比较拦截未变区域 → 变化节点进 CustomComponents 工厂映射 → 深比较 isEqual 再拦一层 → 只有内容真正变化的 code/chart/table 等重建。中间步骤树：WS 步骤消息 → helper 树合并 → generateContentIntermediate 序列化成 `<details>` markdown → details/summary 映射接管交互。

## 设计决策

①**工厂而非静态映射表**：details 需要闭包 messageIndex 判断「是否末条消息」（`CustomDetails.tsx:48`），静态表做不到；②**双层 memo（组件级 isEqual + ReactMarkdown 实例级）**：流式期间每个 chunk 都触发消息级更新，两层拦截让重渲染收敛到正在生长的文本节点；③**data: URI 放行收在最小范围**：只覆写 urlTransform 一处而非关掉整个安全过滤，其它 URL 仍走默认清洗；④**chart 走 markdown 自定义元素**（`<chart>` 标签）而非代码块转义——LLM 只要输出合法 JSON 就能出图。

## 新人提示

加新元素映射记得同步 memo 包装与比较器，漏了比较器会在流式期间整树重渲染；`CustomComponents.tsx:41` 的 `key={Math.random()}` 是反模式（每次重建丢状态）但为时已久，改动前先测复制按钮；react-markdown 已被 jest.config.js 映射到 mock（`jest.config.js:21`），组件测试里它不渲染真实 markdown，断言请落在 mock 透传的 children 上；改展开逻辑先读 `CustomDetails.tsx:52-71` 的三级优先级注释，sessionStorage 键是 `details-${id}`。
