# 01 · docx 技能全链：从 SKILL.md 到 XSD 校验与批注模板

> 仓根 = `/usr-data/data2/repos/agent-repos/anthropics/skills`，锚为仓根相对路径。本篇全部行号现场核实。

## 1. 角色定位

docx 是四大 document skills 的工程学旗舰：它驱动 Claude 生产环境的真实 Word 产出能力（`README.md:20` 点名 source-available 的四技能之一），也是"**分派总纲 + 确定性脚本 + 官方 schema 校验**"这一技能范式的最完整样本。`skills/docx/SKILL.md` 开篇一句话立住心智模型："A `.docx` is a ZIP archive of XML files"（`skills/docx/SKILL.md:9`）——后面所有工具都围绕"安全地拆包、改 XML、合规地打包"展开。frontmatter 的 `license: Proprietary. LICENSE.txt has complete terms`（`:4`）与超长 description 触发器（`:3`）构成它对外的两副面孔：法律上非开源，工程上全公开。

## 2. 内部结构

目录极简，四个自有脚本 + vendored office 库 + 五个 XML 模板：

- **`skills/docx/SKILL.md`**（91 行）：三路分派表在 `:11-15`——Create 走 docx-js（npm 预装，`:21` 明确"不要先 npm install"）、Edit 走 unzip→改 document.xml→zip、Read 走 pandoc。
- **`scripts/merge_runs.py`**（310 行）：编辑前置整理器，合并同格式相邻 run。
- **`scripts/comment.py`**（368 行）：批注落盘器。
- **`scripts/accept_changes.py`**：LibreOffice 宏驱动接受全部修订，`:17-34` 内嵌 StarBasic 模块（`dispatcher.executeDispatch(document, ".uno:AcceptAllTrackedChanges", ...)`）。
- **`scripts/templates/`**：comments.xml / commentsExtended.xml / commentsIds.xml / commentsExtensible.xml / people.xml 五个骨架。
- **`scripts/office/`**：vendored 校验库（50 文件，与 pptx/xlsx 的副本 md5 全等，见 02 篇）。

gotchas 清单（`skills/docx/SKILL.md:23-33`）是全仓被引用最多的 SKILL 写法教材：每条都是"模型已经知道 docx-js API，但不知道的暗雷"——A4 默认页宽要 `width: 12240` DXA（`:23`）、`ShadingType.SOLID` 渲染成黑色要用 CLEAR（`:26`）、`ImageRun` 必须带 `type:`（`:28`）。这不是 API 文档，是**故障模式文档**。

## 3. 外部连接

依赖四个外部工具（`skills/docx/SKILL.md:91`）：`docx` npm 包（创建）、`pandoc`（读取/转换）、LibreOffice（渲染与宏）、`pdftoppm`（PDF 转图）。向内它吃 vendored `office/` 库：`comment.py:38` 直接 `from office.helpers import opc_target, rezip, safe_extract`；`accept_changes.py` 从 `office.soffice` 拿 `get_soffice_env`。与姊妹技能的连接是"复制而非引用"——pptx/xlsx 各有一份逐字节相同副本（md5 实证），零 import 级耦合。向上，整个 docx 技能作为 `document-skills` 插件成员注册于 `.claude-plugin/marketplace.json`。

## 4. 数据流：编辑一份合同并加批注

一条完整数据流走九步（命令全部出自 `skills/docx/SKILL.md:52-87`）：

1. `unzip -q doc.docx -d unpacked/`，紧跟 `find unpacked -type l -delete` 剥符号链接（`:52-53`）——**外部 docx 是不可信输入**，防 zip 路径攻击。
2. `python scripts/merge_runs.py unpacked/`（`:54`）。核心语义在 `scripts/merge_runs.py:12-14`：Word 把段落文本碎在几十个 `<w:r>`（rsid 修订号、proofErr 拼写标记），你肉眼看到的短语在 XML 里不连续；且没有 `xml:space="preserve"` 的 `<w:t>` 边缘空白渲染前会被裁——`<w:t>Hello </w:t>`+`<w:t>world</w:t>` 渲染成 "Helloworld"，合并必须按**渲染文本**而非字节做。不同 `<w:ins>/<w:del>` 包裹的 run 永不合并（docstring 明示，否则修订结构被改写）。
3. 手工编辑 `word/document.xml`：修订模式把 run 包进 `<w:ins>`/`<w:del>`，删除段落 = 段落标记的 `<w:rPr>` 里放 `<w:del/>` 再给每个 run 套 `<w:del>`；`<w:del>` 里文本元素是 `<w:delText>` 不是 `<w:t>`（`:63`）。
4. 包内 `zip -Xr` 打包（`:56`），或走库级 `rezip()`（`office/helpers/__init__.py:85-108`）：临时文件+`os.replace` 原子替换，`[Content_Types].xml` 单独 ZIP_STORED 存储不压缩（`:96`）。
5. `python scripts/office/validate.py out.docx --original doc.docx`（`:57`）。入口按扩展名定族（`office/validate.py:99-106`），docx 装配 `DOCXSchemaValidator`，带 `--author` 再加 `RedliningValidator`（`:124-130`）。
6. XSD 校验：`office/validators/base.py:55-71` 的 `SCHEMA_MAPPINGS` 把 word/ppt/xl/Content_Types/core/rels 等部件名映射到 ISO-IEC29500-4_2016 与 ecma/microsoft 官方 XSD；`base.py:16-22` 用 `lru_cache` 缓存编译后的 `lxml.etree.XMLSchema`；15 类唯一 ID 规则查重复（`base.py:31-47`）。
7. 红线核查：`RedliningValidator`（`office/validators/redlining.py:1-11`）把新增修订撤销后与 `--original` 比对，仍不一致的文本就是**没走修订跟踪的裸编辑**——"easy to do by accident and invisible in the accepted view"（`skills/docx/SKILL.md:63` 原话）。
8. 渲染验收：`soffice.py --headless --convert-to pdf` + `pdftoppm -jpeg -r 100` 转图，Read 图片肉眼检查（`:40-42`）；`pdftoppm` 页号零填充到页数宽度（`:45`）。
9. 批注：`python scripts/comment.py unpacked/ "text"`。脚本自动分配 ID（max+1，`comment.py:14`），写 comments.xml + commentsExtended + commentsIds + commentsExtensible + 关系 + Content_Types 覆盖六件套（`:166-174` 的映射表），从 `templates/` 拷骨架，最后**打印** `<w:commentRangeStart/End>/<w:commentReference>` 片段——模型必须手工贴进 document.xml 才让批注锚定到具体文本，贴之前"comment exists but is not visible"（`skills/docx/SKILL.md:87`）。

## 5. 设计决策

- **修订验证走"撤销再比对"而非正向扫描**：`RedliningValidator` 不解析修订语义，而是把新修订撤销、与原件 diff——这是唯一能抓住"无标记裸编辑"的方法，且天然免疫修订标记本身合法性的坑。
- **批注 ID 自动顺延而非随机**：`comment.py:14` 的 max+1 策略保证与既有批注不冲突，`--id`/`--parent` 留手工逃生门（回复链）。
- **known-failure 文档化**：`skills/docx/SKILL.md:67-72` 诚实记录了 `pandoc --track-changes=accept` 和 `accept_changes.py` 各自何时留空段落——"An empty bullet in either view is an artifact of that view, not a defect"，让模型遇到时不误修。
- **模板外置而非代码内拼**：五个 XML 骨架放 `templates/` 目录由脚本拷贝，主体 comment XML 则在 `comment.py:49-65` 内联字符串模板——卫星文件走拷贝（保证与 Office 生态兼容的固定骨架），内容文件走参数化模板（每条批注不同）。
- **验收强制闭环**："render it and look at it"（`:37`）把肉眼检查写进 SKILL 级别的流程，这是 document skills 与普通代码生成技能的本质差异——产出是给人类看的版式文件。

## 6. 新人提示

- 先读 `skills/docx/SKILL.md` 全文 15 分钟，它是所有命令的索引；脚本不用通读，遇到时看 docstring（本仓 docstring 密度极高且讲"为什么"）。
- 改 XML 前必跑 merge_runs，否则 find-and-replace 会静默失败。
- `validate.py` 报错时逐条修：它"names its fix"（`skills/pptx/SKILL.md:26` 同款承诺）；`--auto-repair` 能修 paraId 超限与缺失的 `xml:space`（`office/validate.py:11-13`）。
- 修订工作流永远带 `--original` 与 `--author`——没有基线的校验分不清"模板的错"和"你的错"。
- 记住渲染语义与字节语义的差异（Helloworld 陷阱），这是本技能最反直觉也最重要的一条。
