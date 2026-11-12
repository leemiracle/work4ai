# 03 · pdf 技能：唯一不靠 vendored 库的自持文档技能

> 仓根 = `/usr-data/data2/repos/agent-repos/anthropics/skills`，锚为仓根相对路径，行号现场核实。

## 1. 角色定位

pdf 是四大 document skills 里的**异类**：docx/pptx/xlsx 三兄弟共享 vendored office 校验库三倍体，pdf 完全没有 `office/` 目录——它是纯 Python 生态（pypdf 为主）加八个独立小脚本的自持技能。原因在于 PDF 不是 OOXML 家族：没有 ISO 29500 XSD 可验，校验等价物是"渲染成图肉眼核对"。它的触发器也最宽（`skills/pdf/SKILL.md:3`）：读/提取/合并/拆分/旋转/水印/新建/填表/加密解密/抽图/OCR 全覆盖——"If the user mentions a .pdf file, use this skill"。在 `.claude-plugin/marketplace.json` 的 `document-skills` 插件里它与三兄弟并列，但技术路线是平行演化的另一支。

## 2. 内部结构

- **`skills/pdf/SKILL.md`**：速览级指南——Quick Start 用 pypdf 三行读页数提文本（`:15-26`），正文按库分节（pypdf 基础操作/其他库），`:11` 把高级特性引到 `reference.md`、填表引到 `forms.md`。
- **`reference.md`**：高级特性与 JavaScript 库参考手册。
- **`forms.md`**：表单填写专路文档，全技能的行为核心（下文专述）。
- **`scripts/` 八脚本**：check_fillable_fields / extract_form_field_info / extract_form_structure / fill_fillable_fields / fill_pdf_form_with_annotations / check_bounding_boxes / convert_pdf_to_images / create_validation_image。每个都是单职责小工具，`check_fillable_fields.py` 全文仅 9 行——`reader.get_fields()` 非空即"有可填字段"（`scripts/check_fillable_fields.py:5-9`）。

## 3. 外部连接

- **pypdf**：读端主力——表单字段树遍历、页面操作、加密解密。
- **pypdf/pdfium/pdf2image 类工具链**（经 `convert_pdf_to_images.py`）：渲染通路，把页面转成 PNG 供模型视觉分析。
- **PIL**：`create_validation_image.py:1-16` 用 `PIL.Image/ImageDraw` 在渲染页上画字段边界框。
- **对姊妹技能零依赖**：不 import docx/pptx/xlsx 的任何东西，也不被它们引用；四技能在 `.claude-plugin/marketplace.json` 只在插件成员层面同级。
- **imageio-ffmpeg 系合规链**在 `THIRD_PARTY_NOTICES.md:11-13`——gif/视频线（slack-gif-creator 消费）的 FFmpeg 二进制分发走 BSD 条款，与 pdf 技能本身无代码耦合但同仓合规。

## 4. 数据流：填一张表的全链

`forms.md:1-4` 开篇即最高强度指令："**CRITICAL: You MUST complete these steps in order. Do not skip ahead to writing code.**"——第一步永远是无条件分流：

1. **分流**：`python scripts/check_fillable_fields <file.pdf>`（`forms.md:3-4`）。有 AcroForm 字段走"Fillable"路，没有走"Non-fillable"注释路。
2. **可填路·字段提取**：`extract_form_field_info.py <input.pdf> <field_info.json>`（`forms.md:8`）产出字段清单 JSON：每字段 `field_id`（沿 `/Parent` 链拼全限定名）、`page`（1 起）、`rect`（PDF 坐标系 bounding box，**y=0 在页底**）、`type`（text/checkbox/radio_group/choice）；checkbox 附 `checked_value`，radio 附 `radio_options`（`forms.md:9-52` 的 JSON 格式逐字段定义）。
3. **语义理解**：`convert_pdf_to_images.py` 转整页 PNG（`forms.md:54`），模型看图推断每个字段的业务含义——**注意把 PDF 坐标换算到图像坐标**（y 轴翻转+分辨率缩放）。
4. **赋值**：手写 `field_values.json`，`field_id`/`page` 必须与提取 JSON 严格对齐（`forms.md:56-75`）。
5. **回填**：`fill_fillable_fields.py <input> <values> <output>`（`forms.md:74-75`）。
6. **不可填路**：`forms.md:78-79`——先尝试从 PDF 结构提坐标（更准），不行再视觉估位，最后 `fill_pdf_form_with_annotations.py` 以文本注释覆盖方式"盖"出内容（`:284`）。
7. **可视化验收**：`create_validation_image.py`（`scripts/create_validation_image.py:8-16`）把填完的表单页与字段框叠画成图——模型 Read 图片确认每个值落在正确格子里，这是 pdf 技能对"validate.py+渲染验收"等价物的实现。

## 5. 设计决策

- **先探测后动手的强制序**：`forms.md:1` 的 CRITICAL 不是修辞——可填/不可填两条路的工具与精度完全不同，跳步直达写代码必然选错路。这与 docx 的"三路分派表"同构：**SKILL.md 的第一职责是路由不是知识**。
- **JSON 中间文件作契约**：field_info.json 与 field_values.json 两个显式文件（而非管道直传）让提取、人工/模型审阅、回填三步可分别重跑与校验——幂等修复的工程标配。
- **坐标语义显式文档化**：`forms.md:14` 特意注明 "y=0 is the bottom of the page"——PDF 坐标系与图像坐标系相反是填表最常见的翻车点，文档在数据格式定义处就地拆雷（`forms.md:178` 不可填路再次调用 convert_pdf_to_images，`:289` 交付前还有一轮转图核验——视觉核对在流程里出现两次，不是一次）。
- **无 XSD 就用眼睛**：OOXML 三兄弟有官方 schema 可机检，PDF 没有——技能把"校验"重构为"渲染+边界框叠加+视觉核对"（create_validation_image），把验收责任交还给多模态模型本身。这是四技能里唯一把**模型视觉能力**写进质量闸门的。
- **脚本粒度刻意小**：八脚本各一事、无共享库、无配置文件——与 vendored 库的"厚重底座"路线相反，pdf 走"轻工具+文档编排"路线，脚本只是文档指令的精确化锚点。

## 6. 新人提示

- 别通读 SKILL.md 之外的 md：`forms.md` 是唯一带强流程约束的文件，填表任务先读它；其余操作 SKILL.md 的代码块可直接抄。
- 八个脚本先 `--help` 或读前 20 行 docstring 再用，都极短；改脚本不如改调用参数——它们是稳定契约。
- 记住两套坐标系（PDF y 向上/图像 y 向下）与两种字段寻址（AcroForm field_id/视觉坐标），90% 的填表 bug 源于混用。
- 交付前必跑 create_validation_image 走视觉闸——pdf 没有 recalc/validate 级的机器绿灯，图就是唯一的验收证据。
- 想理解"为什么 pdf 不 vendored"：对照 02 篇——不是偷懒，是 PDF 生态没有"官方 XSD 全集"这种可搬资产，自持是唯一选择；同理它的 LICENSE.txt 与三兄弟同款 Proprietary 声明（`skills/pdf/SKILL.md:4`）。
