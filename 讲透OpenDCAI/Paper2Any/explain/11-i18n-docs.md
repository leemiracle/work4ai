# 11 · i18n 与文档群：14 命名空间、双生 JSON 与带血统记忆的 docs

> 定位层级：i18n 国际化资源 + docs 文档群。本篇覆盖 `frontend-workflow/src/i18n.ts`（79 行）与 `locales/{en,zh}/` 28 件 JSON，以及 `docs/` 全部 20 个 markdown（含 guides/ 八件、mkdocs.yml 导航）。这条线是产品对外的"脸面层"：一个管界面语言，一个管用户认知。

## 一、角色定位

i18n 层是 react-i18next 标准三件套：`i18n.ts` 集中注册、`locales/{en,zh}/` 双语资源、组件里 `useTranslation` 消费（App.tsx、LanguageSwitcher.tsx、HomePage、MindMapPage、Image2DrawioPage 等页面全量接入）。docs 层是 mkdocs 站点（mkdocs.yml L9-28 定义 nav 三大板块：入门与部署/功能指南/项目参考），开源用户的第一站。两者共同暴露了这个项目的出身：从姊妹项目 DataFlow 剥离而来，剥离得不彻底。

## 二、内部结构

### 2.1 i18n.ts：14 命名空间

`i18n.ts` 用了 28 行 import 把 14 个命名空间的 en/zh 双份 JSON 全量静态引入（L5-32），再在 `resources` 里双语并列（L51-78），最后两行配置定乾坤：`defaultNS: 'common'`（L82）与 `ns` 数组（L84）——**14 个命名空间**依次是 common、login、paper2ppt、pdf2ppt、image2ppt、image2drawio、pptPolish、paper2graph、paper2drawio、paper2rebuttal、paper2video、paper2citation、mindmap、imagePlayground。命名空间即功能页一一对应（每个转换线一个 namespace），common 兜底通用文案。初始化参数里 `debug: true`（L48）是开发期残留——上生产会在控制台刷未命中键的告警。语言检测用 i18next-browser-languagedetector（L43），fallback 到 en（L49）。

### 2.2 28 件 JSON 与"双生"结构

locales/en 与 locales/zh 各 14 件、件件对仗。最有意思的是 **image2ppt.json 与 pdf2ppt.json 的双生关系**：两件在两种语言下都是**12 个顶层键完全同构**——`action/complete/config/demo/desc/descHighlight/dropzone/errors/footer/status/subtitle/title` 一一对应、嵌套结构一致，但**值只有 `complete` 一个键逐字相同**（"转换完成！"/"您的 PPT 文件已准备好下载"），其余 11 键全部按输入格式分化：`errors.imgOnly`"仅支持图片格式 (PNG, JPG)" vs `errors.pdfOnly`"仅支持 PDF 格式"、大小限制 20MB vs 50MB、`config.aiEdit`"AI 智能增强（推荐）" vs "AI 背景增强（5 分钟）"。这是典型的复制起家再分化的文本资产：Pdf2PptPage 先写好，Image2PptPage 连壳带文案抄一份，只改格式相关的值。批判点在维护面——新增一个状态提示要同步四处（两语言×双生件），漏一处就出现英文有中文无的键。

### 2.3 docs 群：三种成色的文档

`docs/` 顶层 11 件 + guides/ 8 件，成色分三档：

- **实档**：guides/open_source_deployment.md（857 行部署总指南，docs 最重一篇）、guides/configuration.md（148 行配置参考）、guides/multimodal_api.md（123 行多模态供应商开发指南）、onlyoffice-editable-ppt.md（116 行，钉版 vendored dom-to-pptx 的上游与 MIT 许可：`frontend-workflow/public/vendor/dom-to-pptx.bundle.js`，上游 github.com/atharva9167j/dom-to-pptx）。
- **占位页 4 件**：guides/paper2figure.md（11 行）、paper2ppt.md（12 行）、paper2technical.md（11 行）、paper2video.md（11 行）——每件只有一句定位加三四条功能列表，尾巴一律是"*(详细文档正在编写中...)*"。mkdocs nav L18-21 却把这四件挂进"功能指南"板块，用户点进去会发现四大主打功能全是坑位。真内容在 guides/index.md（56 行总览，给出每条 workflow 的典型输入/输出）里反而比占位页多。
- **漂移档**：docs/cli.md（385 行）——通篇讲脚手架 CLI（`--agent_name`/`--wf_name`/`--gradio_name` 等参数表 L19-24），但示例路径全是 DataFlow 的目录：L21-22 引 `gradio_app/pages/page_{name}.py`（**本仓根本没有 gradio_app 目录**，前端是 frontend-workflow）、L57 `agentroles/common_agents/sentiment_analyzer_agent.py`、L114 `workflow/wf_text_processing.py`、L215 "重启 `python gradio_app/app.py`"——这些示例文件在本仓全部不存在。本仓真正的 CLI 家族是 `script/cli_env.py`（手动解析 `fastapi_app/.env`、剥离代理变量）加 `script/run_{paper2ppt,paper2video,paper2figure,...}_cli.py` 一族，cli.md 一个字没提。

### 2.4 血统记忆：multimodal_api.md 自称 DataFlow-Agent

guides/multimodal_api.md 开篇第一句就是 "**DataFlow-Agent** 采用灵活的策略模式来支持多种多模态 AI 供应商"（L3）——文档自我介绍时用的是姊妹项目的名字，尽管通篇引用的代码路径（`dataflow_agent/llm_callers/image.py` 的 VisionLLMCaller、`toolkits/multimodaltool/providers.py` 的 AIProviderStrategy、`agentroles/cores/strategies.py` 的 VLMStrategy）在本仓都真实存在。这不是孤立笔误，而是整条文档线从 DataFlow 文档树拷贝时的残留：cli.md 的目录漂移、multimodal_api.md 的自称、外加 `docs/superpowers/plans/` 里的开发计划存档（如 2026-05-11-html2pptx-onlyoffice-integration.md），合起来能还原出"Paper2Any = DataFlow 的论文转换线剥离 + OnlyOffice/html2pptx 增强"的演化史。

## 三、外部连接

- **前端组件**：所有页面组件经 `useTranslation('<ns>')` 按命名空间取文案；LanguageSwitcher 切换的语言落在 localStorage（LanguageDetector 默认策略）。
- **mkdocs 站点**：mkdocs.yml nav 把 docs/ 组织成三板块站（L9-28），changelog/contributing/faq 属"项目参考"；`docs/index.md` 是站点主页。
- **部署文档链**：guides/index.md L9-13 显式分工——部署/环境/`.env`/Supabase/模型服务/端口问题一律踢回 open_source_deployment.md 与 configuration.md（与第 09 篇的 deploy 线互为表里）。
- **vendored 资产**：onlyoffice-editable-ppt.md 声明的 dom-to-pptx bundle 正是第 07 篇 HTML 导出通道的运行时依赖，文档与代码在此交汇。

## 四、数据流

i18n 侧：构建期静态 import 全部 28 件 JSON 进 bundle → i18next.init 注册 → 运行时组件按键取译 → 缺键走 fallbackLng: 'en' → debug 模式控制台告警。无懒加载：14 命名空间全量进首包，当前体量（每件几 KB）尚可接受，但每加一条转换线就是 en+zh 两件进首包。docs 侧：mkdocs build 按 nav 编译静态站；文档与代码没有生成器联动，全手工维护——这也是 cli.md 漂移能存活的原因（没有任何机制校验文档里的路径存在性）。

## 五、设计决策（含批判）

1. **每功能页一个命名空间**：粒度干净、键不互踩、页面删掉连 JSON 一起删，是正确的切法。代价是 14 个 namespace 的注册表全手工同步（import、resources、ns 数组三处），新增页面要改三行还容易漏 ns 数组导致运行时命名空间未注册。
2. **双生 JSON 复制**：image2ppt/pdf2ppt 的 12 键同构证明复制式开发；更稳的做法是抽公共转换页文案进 common 或共享命名空间、只留格式差异键，现在的写法四处同步成本永久化。
3. **debug: true 上线**：一行配置的疏忽，生产环境控制台会持续输出 i18next 调试日志，既是噪音也暴露键名结构。
4. **docs 三档成色无标注**：占位页没有任何"施工中"样式标记（只有文末斜体一句），nav 里与实档平起平坐；开源用户按 nav 顺序读到 paper2figure.md 时预期落差最大。cli.md 则更危险——它教的是本仓跑不通的命令（gradio_app 不存在），等于给新贡献者递错地图。
5. **血统残留是考古资产也是噪音**：DataFlow-Agent 自称与 DataFlow 目录示例，对想理解项目来源的人是无价的线索，对按文档操作的人是坑。最小修正是开头加一行"本文自 DataFlow 项目迁移，路径以本仓 script/ 为准"的勘误框。

## 六、新人提示

- 加新页面时照抄 i18n.ts 三处同步法：import 对、resources 双语各一条、ns 数组追加——漏第三处时组件会拿不到翻译且报 "namespace was not found"。
- 改 image2ppt/pdf2ppt 任一文案前先 diff 两件 JSON，确认改动只该落一边还是两边（`complete` 这类共性键两边都要动）。
- 读文档先分级：open_source_deployment.md 和 configuration.md 是可信的实档；四件 11-12 行的指南是占位；cli.md 的示例路径要拿 `ls` 验证再用，本仓 CLI 真入口在 `script/run_*_cli.py`（配合 `script/cli_env.py` 加载 fastapi_app/.env）。
- 查 vendored 前端依赖的许可证与上游，看 onlyoffice-editable-ppt.md 即可，不用翻 node_modules。
- i18n 未命中键的控制台告警在 debug: true 下非常啰嗦，本地排查文案问题时它是友好的，提 PR 前记得确认不是靠它才发现的缺键漏网。
