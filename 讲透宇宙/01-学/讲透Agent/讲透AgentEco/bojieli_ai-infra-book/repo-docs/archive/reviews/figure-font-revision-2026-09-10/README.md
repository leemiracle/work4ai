# 中文字体修订复核

- 章节标题、各级小节标题与正文中文粗体使用思源黑体 Bold；普通正文保留宋体。
- 12 章全部 393 张正文配图改用思源黑体。标签常规字重，标题及强调文字使用对应字重。
- LaTeX 使用项目固定的 OTF；Matplotlib 使用同版本的静态 TrueType，避免 Type 42 嵌入 CFF 字体引起的类型警告。
- PDF 嵌入字体；SVG 文字转矢量轮廓；PNG 与网页配图也重新生成。字体与许可证位于 `manuscripts/figure_style/fonts/`。
- 保留紧凑配图和自动浮动、原生公式字号、封面标题位置。增加公式与脚注的最小间距，消除密集页面的高度溢出。
- 与并行术语修订任务共用工作区；最终编译在配图重建结束后进行，使用最新正文。

## 预览

- [章节标题和正文](chapter-02-typography.png)
- [配图字体前后对比](font-comparison.png)（同时包含术语任务对图例文字的更新）
- [全书 PDF](../../../book/AI-Infra-Book.pdf)
- [第二章 PDF](../../../book/AI-Infra-Book-Chapter-02.pdf)

## 验证

`book/check_typography.py` 检查全部 393 张正文引用配图中的思源黑体、SVG 不依赖本机字体，以及成书中宋体正文和思源黑体粗体均存在。结果见 [typography-validation.json](typography-validation.json)。

`book/verify_pdf.py` 与 `book/check_layout.py` 均通过：字体均已嵌入，无缺字、越出页边界、LaTeX 溢出或未定义引用；公式保持正常字号。仅保留原模板的 `Command \@parboxrestore has changed` 包兼容提示。十二章网页的桌面和手机视口检查及资源校验通过。

- `AI-Infra-Book.pdf`：393 页、393 张图。
- `AI-Infra-Book-Chapter-02.pdf`：51 页、32 张图。
