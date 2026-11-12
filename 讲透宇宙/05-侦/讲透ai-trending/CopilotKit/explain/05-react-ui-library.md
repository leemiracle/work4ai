# 05 · react-ui v1 组件库：视觉层、CSS 令牌与考古层

> 定位文件：`packages/react-ui/`（图谱「react-ui v1 组件库」层，81 节点）

## 一、角色定位（16 层架构中位置）

第 10 层「react-ui v1 组件库」：CopilotKit 的**默认视觉皮**。它不管理任何状态——状态全在 react-core（第 3/4 篇），本包只做"把 hooks 的数据渲染成好看的聊天窗"。目录三种资产泾渭分明：`components/chat/`（29 个 TSX 组件）、`css/`（14 个样式文件，全部经 styles.css 聚合）、`v2/`（只有两行文件的转发层）。还有 dev-console（开发者控制台）与 help-modal 等外围。这个包是**冻结代**——v2 的视觉组件已迁入 react-core v2（第 3 篇的 chat 目录），react-ui 留下来服务存量 v1 用户，因此它的考古价值（弃用桥、死 CSS、化石类型）高于演进价值。

## 二、内部结构（关键文件+行号锚拆解）

### 2.1 Chat.tsx（1040 行）：v1 视觉主组件与弃用桥

- 主组件是 `CopilotChat`（Chat.tsx:391），从 v1 context（useCopilotContext/copilotApiConfig）取状态——**不是** v2 的 useCopilotKit。
- **imageUploadsEnabled→attachments 弃用桥**（任务书命题，源码实证）：props 上 `imageUploadsEnabled?: boolean` 标 @deprecated（:215-223，注释给出迁移指南链接与差异说明——旧 prop 只支持图片，新 attachments 支持任意文件）；解析处是一个 IIFE（:443-454）：`attachments` prop 优先直通；否则若 imageUploadsEnabled 为真，调 `deprecationWarning("imageUploadsEnabled", ...)`（:446-450）并映射为 `{ enabled: true, accept: inputFileAccept || "image/*" }`（:451）——连旧的 inputFileAccept 也一并桥接。解析后三默认值：accept `*/*`、maxSize **20MB**（:456-458）。
- deprecationWarning 本体在 attachment-utils.ts:19-25：**生产环境静默**（NODE_ENV 判定）、每 key 只警告一次（suppressedWarnings Set）、可全局 suppress（:28 起 suppressDeprecationWarnings）——弃用警告的三重克制设计。
- 弃用字段的密度是本文件代际身份的指纹：Render*Message 五连弃用（:291-311）、attachment 旧类型（:336-337、:380-383），全部指向 v2 等价物。
- 图谱钉版（NOTES-DIGEST batch-12）：Legacy Render*Message props 仍在透传——弃用≠删除，桥接期常态。

### 2.2 CodeBlock.tsx（423 行）：一段 284 行的内联主题常量

文件后半段整块是 `const highlightStyle: any = {`（CodeBlock.tsx:140）到 `};`（:423）的 **vscDarkPlus 高亮主题手工内联**，起因注释钉版（:136-138）：按 react-syntax-highlighter 文档的 import 方式（`react-syntax-highlighter/dist/esm/styles/prism`）**在 Next.js classic（非 app router）构建立即报错**，于是把整个 VS Code Dark Plus 主题色表复制为本地常量。组件本体（:56-132）则很薄：Prism/Light 双渲染器、复制（useCopyToClipboard 2s 超时）、下载成文件（programmingLanguages 语言→扩展名映射表 :20-45，generateRandomString 排除易混字符 Z/2/I/1/O/0 :47-53）。**代价清单**：主题升级永不可能（除非重抄）、`any` 类型放弃检查、bundle 恒定携带全主题——一个构建工具兼容性问题的十年利息。

### 2.3 css/ 令牌体系：colors.css 为根的消费网

- **colors.css（82 行，30 个令牌）是唯一的令牌定义点**：文件头注释直接摊牌（colors.css:1-4）——"THE DARK AND LIGHT COLORS HERE ARE DUPLICATED BECAUSE NO REUSE METHOD POSSIBLE. WHEN MAKING ANY CHANGE, MAKE SURE TO INCLUDE IT IN ALL DUPLICATIONS."（明暗两套主题靠手工复制维护，改一处必须同步所有副本）。令牌命名 `--copilot-kit-primary-color`/`--copilot-kit-contrast-color`/`--copilot-kit-shadow-sm|md|lg` 等（:10-40），语义化分组（error 三色组、shadow 三档）。
- **消费侧**：其余 css 文件以 `var(--copilot-kit-*)` 消费令牌——messages.css 25 处、input.css 8 处、button.css 6 处。图谱上表现为 colors.css → 各组件 css 的 depends_on 边集群（"令牌消费 depends_on"命题即此）。
- **聚合入口** styles.css 按序 @import 全部 15 个文件（colors 第一、crew 最末）——顺序即优先级，令牌必须先行。

### 2.4 同名 @keyframes：全局命名空间冲突实录

CSS 的 @keyframes 是**全局命名空间**，本包自己就撞了：`copilotKitSpinAnimation` 同时定义在 animations.css:25 与 messages.css:162——后加载者（messages.css 在 import 序中更晚）覆盖前者，若两处定义漂移则以 styles.css 的 import 顺序为准绳，无任何构建期保护。更危险的是 crew.css 用了三个**裸英文单词**动画名：`appear`（crew.css:200）、`pulse`（:211）、`spin`（:221）——宿主应用若定义同名动画即互相覆盖，这是嵌入型组件库（被拷进宿主页面）最经典的污染源。v2 组件库的对策是 `cpk:` 前缀工具类（第 3 篇），v1 时代还没有这层防御。

### 2.5 crew.css = CrewAI 集成遗留（三重证据）

crew.css（277 行）是死样式，三重证据互相印证：

1. **零组件消费者**：全部 class（.copilotkit-response/.copilotkit-response-content/.copilotkit-loader/.copilotkit-spinner 等）在全仓 .tsx/.ts 中**零引用**——grep 实证只有 css 文件自身出现这些名字；
2. **类型化石同源**：`packages/react-core/src/types/crew.ts` 保留着 CrewsResponseStatus（"inProgress"|"complete"|"executing"）/CrewsResponse/CrewsStateItem 类型族（crew.ts:5/13/22），且这些类型在全仓同样零消费者——JS 侧与 CSS 侧的 CrewAI 集成遗迹成对出现；
3. **幽灵注释**：crew.css:1 自述"Default styles for the ResponseRenderer component"——仓内已无名为 ResponseRenderer 的组件。

即：CrewAI（多 agent 编排框架）曾深度集成（响应渲染/加载动画/深色模式全套样式 + TS 类型），功能删除后样式与类型双双重疮不清理。styles.css:15 仍把它 import 进产物——**每个 v1 用户都在为 277 行死 CSS 付 bundle 成本**。

### 2.6 v2/：两行文件的转发层

`src/v2/` 只有两个文件：index.ts（23 字节，内容仅 `import "./styles.css";`）与 styles.css（48 字节，**单行** `@import "@copilotkit/react-core/v2/styles.css";`）。语义：`@copilotkit/react-ui/v2/styles.css` 这个子路径导入不携带任何本包样式，纯粹转发到 react-core v2 的全局样式（后者经 tsdown customExports 最终锚到 react-core src/v2/styles/globals.css——NOTES-DIGEST batch-57 两轮验证）。这是"v2 视觉已搬家，但保留路径兼容"的最小实现——与第 4 篇的反向导出环同一动机。

## 三、外部连接（imports 边上下游）

- **上游**：存量 v1 应用与 examples 的 `<CopilotChat/>`/`<Popup/>`/`<Sidebar/>`；docs 站的组件参考。
- **下游**：`@copilotkit/react-core` 的 v1 hooks 全家（useCopilotContext/useCopilotChat/useCopilotAction——Chat.tsx:435 附近可见 useCopilotContext 解构）；`@copilotkit/shared`（InputContent 类型、attachment 工具）；react-syntax-highlighter（Prism 双渲染器）。注意 barrel 盲区：attachment-utils.ts 的多行 re-export 是 scanner 的 batchImportData 空白（NOTES-DIGEST batch-14），图谱边靠手工补。
- **CSS 边**：colors.css 的令牌被 13 个兄弟 css 文件消费；styles.css 是包级入口（package.json 的 style 字段指向）；v2/styles.css 的边**跨包**指向 react-core。

## 四、数据流（一次带图消息在 v1 组件树中的旅程）

1. `<CopilotChat instructions labels/>` 挂载：弃用桥解析 attachments 配置（Chat.tsx:443-454），users 若同时传 imageUploadsEnabled 与 attachments，后者胜、无警告；
2. ChatContext（ChatContext.tsx，248 行）向 Window/Header/Messages/Input/Modal 子树分发 icons/labels 可定制对象——Modal.tsx:109 注释钉版 Popup/Sidebar 两形态都以 Modal 为基座，且 Window/Button/Header 等子组件可整体替换（组合式定制的 v1 实现）；
3. 用户拖图进 Textarea → attachment-utils 的 matchesAcceptFilter/readFileAsBase64/exceedsMaxSize（20MB 闸）校验 → AttachmentQueue 渲染缩略卡片（attachments.css 提供样式，spin 动画撞名区就在这里）；
4. 发送 → useCopilotChat 的 v1 链路（第 4 篇）→ core RunHandler → agent 回消息；
5. Messages.tsx 渲染流：纯文本走 Markdown.tsx（react-markdown），代码块走 CodeBlock（内联 vscDarkPlus 主题上色）；消息样式从 messages.css 取类、颜色从 var(--copilot-kit-*) 令牌解析回 colors.css 定义的值；
6. 若宿主页面暗色：colors.css 的 prefers-color-scheme 媒体查询切换整套令牌副本（手工复制维护的那套）。

## 五、设计决策（为什么这么设计 + 替代方案）

- **弃用桥 IIFE vs 删 prop**：直接删会让存量应用类型报错+运行时炸；桥接让旧 prop 继续工作并只警告一次（attachment-utils.ts:19-25 的三重克制：生产静默/每 key 一次/可全局关）。映射到等价新配置而非报错，是"弃用即翻译"的范式。
- **内联主题 vs 修构建问题**：根因是 react-syntax-highlighter 的 ESM 路径与 Next.js classic 构建不兼容，正确修法（上游修复/换打包器配置）超出本包控制半径，内联是当时最低成本的止血。教训：**为工具兼容性抄第三方常量，偿还期是永久的**——上游修复后也没人记得回头删。
- **令牌集中 vs 组件内联色**：colors.css 集中定义让宿主换肤只需覆写 CSS 变量（嵌入友好）；但明暗两套靠手工复制（文件头注释自认无解），替代方案是 CSS color-mix()/相对颜色——CSS 当时无此能力，v1 时代的合理局限。
- **v2 转发层 vs 保留副本样式**：若 react-ui/v2 自带样式副本，将出现两份真源随版本漂移；单行 @import 让 react-core v2 的 globals.css 唯一真源，react-ui/v2 只是指路牌。

## 六、新人提示（坑+勘误+延伸阅读）

- **坑（keyframes 撞名）**：宿主应用定义 `spin`/`pulse`/`appear` 动画会与 crew.css 互相覆盖（crew.css:200-221）；包内也有 copilotKitSpinAnimation 双定义（animations.css:25 vs messages.css:162）。定制动画一律加前缀。
- **坑（死代码负担）**：crew.css 277 行零消费者却进产物（styles.css:15）；react-core types/crew.ts 的 Crews 类型族同样零消费。做 bundle 瘦身时这是第一批可删项（删 import 与删文件要同步）。
- **坑（deprecationWarning 静默性）**：生产环境完全不警告（attachment-utils.ts:22-23）——线上排查"为什么附件行为不对"时别指望警告线索，直接查 resolvedAttachments 的解析结果（Chat.tsx:443）。
- **attachment 默认值**：不传 accept 时 `*/*` 全类型放行、上限 20MB（Chat.tsx:456-458）——上生产前显式收紧，别依赖默认。
- **v2 用户别在此包找组件**：`@copilotkit/react-ui/v2` 只转发样式（48 字节单行）；v2 组件在 `@copilotkit/react-core`（第 3 篇）。import 路径写错不报错——只是拿到空模块。
- 延伸阅读：第 3/4 篇（状态与 hooks 的真实住址）；NOTES-DIGEST batch-12 的 react-ui 批注（tree-sitter 对 memo/forwardRef/JSX 常量组件的盲区清单——Icons.tsx 16 个导出全是 JSX 元素常量而非组件）；dev-console（developer-console-modal.tsx 1019 行，本包最大单文件，未在本篇展开）。
