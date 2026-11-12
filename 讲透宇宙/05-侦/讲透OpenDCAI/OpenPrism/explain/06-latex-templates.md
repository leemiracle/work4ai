# 06 论文 LaTeX 模板群与 SwiftLaTeX wasm 引擎

## 角色定位

`templates/` 是模板转换功能（第 3 篇）的"目标端弹药库"，五目录两种血统：**ACL 与 CVPR 是官方套件原样拷入**（acl/ 含 acl.sty 11615B + acl_natbib.bst 45186B + latex/lualatex 双入口；cvpr/ 含 cvpr.sty 17969B + ieeenat_fullname.bst + sec/ 五节拆分 + rebuttal.tex——manifest 里 "CVPR (skeleton)" 标签名不副实）；**arxiv/ 是官方 arXiv 套件**（arxiv.sty + template.tex + License.txt）；**icml/ 与 neurips/ 是自写骨架**——两份 main.tex 各 35 行，替换 ICML/NeurIPS 字样后 `diff` 零差异逐行同构，L8 自注 "lightweight skeleton. Replace with official ... for final submission"。

## 内部结构

**manifest.json 只注册四个模板**（acl/cvpr/neurips/icml），**templates/arxiv/ 未注册是勘误实锤**——但后果比"不出现"更隐蔽：templateService.js:16-42 的自动补注册会扫描未登记目录，发现 arxiv/ 有 .tex 就生成占位条目，硬编码 `mainFile:'main.tex'`（L34）——而 arxiv/ 的主文件实际叫 template.tex，目录里根本没有 main.tex。于是 arxiv 在模板列表里"看得见"，选中后 TransferPanel.tsx:161 取 `selectedTemplate.mainFile` 得到一个不存在的路径，转换管线在 analyzeTarget 读目标主文件时即崩。

**bst 挂载点两种范式**：ACL 把 `\bibliographystyle{acl_natbib}` 内嵌在 acl.sty:195——用户 tex 无需也不应再写 bibliographystyle；CVPR 则在 main.tex:56 显式 `\bibliographystyle{ieeenat_fullname}`（rebuttal.tex:133 同款）；icml/neurips main.tex:32 用内置 `plain`（所以它们的目录里没有 .bst）；arxiv template.tex:169 用 `unsrtnat`。排查"引用样式不生效"先分清模板属于哪一派。

## 外部连接

模板的两个消费方都走 `readTemplateManifest`：transfer.js:38-41 校验 targetTemplateId，建项目时 `copyDir` 整目录拷贝（transfer.js:65-66）；health.js 的 `/api/templates/upload` 反向写入（templateService.js:48-62 持久化新条目）。`TEMPLATE_DIR/MANIFEST` 路径由 constants.js:8-9 钉在仓库根。

**SwiftLaTeX wasm 引擎是本篇最大勘误源**：`apps/frontend/public/latex/` 里躺着 swiftlatexpdftex.js 与 .wasm（1,782,913 字节）——js 是 Emscripten 压缩产物，**全部代码折叠在第 1 行**（整文件 90,100 字节仅一行），Module 上导出 `_compileLaTeX/_compileBibtex/_compileFormat/_setMainEntry` 等入口。但**前端源码对它零引用**：src/ 下 grep 不到任何加载点，`src/latex/engine.ts` 只是 7 行纯类型文件（CompileOutcome 接口），真正的编译走后端 compileService spawn 本地 TeX（第 5 篇）。vite.config.ts:15-19 的 `/texlive`→texlive.swiftlatex.com 代理与 README.md:582 的 "latex/ # TexLive integration" 都指向这条从未接通的客户端编译线。另：public/latex/README.md 自述产物来自 `/data/users/liuzhou/online/SwiftLaTeX`——开发者本机路径泄漏。

## 数据流

建项目：模板目录 → copyDir → 项目根。转换：manifest 校验 → 模板全量拷入新项目 → 管线按 targetMainFile 改写 → compile。上传模板：zip 流式解包（health.js:23 起，同第 5 篇防穿越）→ 落 TEMPLATE_DIR/<id>/ → manifest 增条目。

## 设计决策（含批判）

自动补注册（templateService.js:16-42）本意是"放目录即生效"的零配置体验，代价是拿不到 label 且 mainFile 靠猜——arxiv 正好踩中最坏分支；显式注册 + 启动校验（mainFile 存在性检查）才是稳态。**LICENSE 缺失**：仓库根无 LICENSE 文件，README.md:10 徽章与 :663 的 MIT 链接双双指向不存在的文件；templates/ 仅 arxiv/License.txt（arXiv 官方许可非本项目授权）——ACL/CVPR 官方套件的再分发条款未声明，合规裸奔。wasm 引擎是"引入未接线"的半成品：1.7MB 资产进仓库却无人加载，要么接通要么删除并同步改 README 与 vite 代理。

## 新人提示

加新模板三选一：manifest 显式注册（推荐，mainFile 可控）/扔目录赌自动补注册（主文件必须叫 main.tex）/UI 上传。调 bst 先查挂载点范式（sty 内嵌 vs tex 显式）。想接通 wasm 编译，入口在 Module._compileLaTeX，宏包源走 /texlive 代理（SwiftLaTeX 云上 TeXLive）；接通前别信"浏览器本地编译"文案。
