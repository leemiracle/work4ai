# anthropics/skills Onboarding（Anthropic 官方 Agent Skills 仓）

> 图谱基线：commit `8a1541c4a`，615 节点/803 边/16 层，373 文件。行号锚为**仓根相对全路径**（仓根=`/usr-data/data2/repos/agent-repos/anthropics/skills`），全部现场核实。

## 1. 仓库定位与 marketplace 分发

一句话：**Skills 是"指令+脚本+资源"的文件夹，Claude 按需动态加载以在专门任务上变现**（`README.md:5` 原文定义）。本仓是 Agent Skills 生态的**参考实现+示例集**：`skills/` 下 19 个技能目录（非 tour 所记 20，见文末勘误），覆盖文档处理/创意设计/开发测试/企业沟通。

分发形态不是一仓一技能，而是**一个 marketplace 切五个可安装插件**（`.claude-plugin/marketplace.json`）：`document-skills`（4 件）、`example-skills`（12 件）、`claude-api`/`academy-guide`/`discernment-nudge`（各 1 件）。用户入口 `/plugin marketplace add anthropics/skills`（`README.md:37`）。`strict: false` 允许技能集动态增删，owner 实名 Keith Lazuka。

**许可分层是第一道门槛**：`README.md:20` 明说四大 document skills 是 **source-available 非 open source**——驱动 Claude 生产环境真实文档能力，源码公开仅作参考；frontmatter 声明 `license: Proprietary`（`skills/docx/SKILL.md:4`），其余技能默认 Apache 2.0。`THIRD_PARTY_NOTICES.md:303-305` 处理 OFL 字体合规，`:11-13` BSD 条款包裹 imageio-ffmpeg 分发的 FFmpeg。

## 2. 规范与模板

**规范本体不在本仓**：`spec/agent-skills-spec.md` 全文 3 行——标题加重定向到 agentskills.io。治理信号：规范已升格中立标准站，本仓退居参考实现位，**勿当完整规范引用**。`template/SKILL.md:1-6` 六行最小骨架，frontmatter 只约束 `name`+`description`——即规范的最小必需元数据。实际演化方向：`skills/claude-api/SKILL.md:5-6` 的 description 写成带可执行 grep 的触发/跳过判定；`skills/academy-guide/SKILL.md` 用 YAML 折叠块写整段触发规格。目录级约定见 `skills/skill-creator/SKILL.md:75-84` Anatomy 图：`SKILL.md`+`scripts/`+`references/`+`assets/`。

## 3. 四大 document skills 地图

四技能共享同一心智——**Office 文件是 ZIP 包着的 XML**（`skills/docx/SKILL.md:9`）——分工如下：

- **docx**：三路分派（新建 docx-js/编辑 unzip-zip/读取 pandoc，`skills/docx/SKILL.md:11-15`）；gotchas（`:23-33`）是 SKILL 写法范本——每条都是"模型知道 API 但不知道的暗雷"（A4 默认页宽、`ShadingType.SOLID` 渲染成黑）。
- **pptx**：`skills/pptx/SKILL.md:21-28` 五脚本表；`:34-47` 列多种**直接损坏文件**的写法（井号色值/8 位 hex/负阴影偏移/堆叠图 outEnd/双副轴缺 valAxes）；簿记三件套见 `skills/pptx/scripts/add_slide.py:3-9`（Content_Types 注册+rels 新 rId+sldIdLst 插入）。
- **xlsx**：自有代码最薄（仅 recalc.py），八条交付硬要求全押 LibreOffice 无头重算（`skills/xlsx/SKILL.md:30-46`）；`skills/xlsx/scripts/recalc.py:244` 以 `success/errors_found` 双态出 JSON，`errors_found` 照样退出 0；公式生存学：六个 2007 后函数须 `_xlfn.` 前缀、`XLOOKUP` 等六个**任何前缀都不能用**（`:66-68`）。
- **pdf**：唯一**无 vendored office 库**的自持技能（`skills/pdf/SKILL.md:3` 触发器覆盖 OCR/加密/拆合），8 脚本全走 pypdf 生态；表单先 check_fillable_fields 分流双通道（`skills/pdf/forms.md:1-4`）。

## 4. 核心链路：一个 docx 从 SKILL.md 到 XSD 校验的旅程

以"编辑合同并加批注"走全链：

1. **分派**：SKILL.md 表格判"编辑"路——unzip 解包后先剥符号链接（外部 docx 不可信，`skills/docx/SKILL.md:52-53`）。
2. **整理**：`merge_runs.py` 合并同格式相邻 run（`skills/docx/SKILL.md:54`）。必须的原因：Word 把文本碎在几十个 `<w:r>`，且无 `xml:space="preserve"` 的边缘空白渲染前被裁——`<w:t>Hello </w:t>`+`<w:t>world</w:t>` 渲染成 "Helloworld"（`skills/docx/scripts/merge_runs.py:12-14`）。
3. **编辑**：改 `word/document.xml`，修订包 `<w:ins>/<w:del>`（`skills/docx/SKILL.md:63`）。
4. **打包**：`office/helpers/__init__.py:85-108` 的 `rezip()` 临时文件+`os.replace` 原子替换，`[Content_Types].xml` 强制 ZIP_STORED（`:96`）。
5. **校验**：`office/validate.py:99-106` 按扩展族分派，docx 族装 `DOCXSchemaValidator`+可选 `RedliningValidator`（`:124-130`）。
6. **XSD 本体**：`office/validators/base.py:55-71` 的 `SCHEMA_MAPPINGS` 把部件名映射到 ISO/IEC 29500-4:2016 官方 XSD（word→wml/ppt→pml/xl→sml）；`base.py:16-22` `lru_cache` 缓存编译后 schema；另查 15 类唯一 ID（`base.py:31-47`）、关系完整性、Content_Types 一致性。
7. **红线核查**：`--author` 触发 `RedliningValidator`——撤销新增修订后与原件比对，仍不一致即**没走修订跟踪的裸编辑**（`office/validators/redlining.py:1-11`）；`--original` 给模板基线防误归咎（`skills/pptx/SKILL.md:26`）；接受全部修订走 `skills/docx/scripts/accept_changes.py:17-34` 内嵌宏。
8. **渲染验收**：soffice 转 pdf+pdftoppm 转图肉眼查（`skills/docx/SKILL.md:40-42`）。
9. **批注**：`comment.py` 写六个互联文件，ID 自动 max+1（`skills/docx/scripts/comment.py:14`），从 `scripts/templates/` 拷五个 XML 骨架，打印 commentRangeStart/End 片段贴进 document.xml 锚定（`skills/docx/SKILL.md:87`）。

## 5. 关键设计决策：vendored 自包含分发哲学

**docx/pptx/xlsx 各自内嵌整套逐字节相同的 office 校验库**——50 文件×3，md5 全等实测；schema 资产同样三份（ISO 全套+ecma+microsoft+mce）。为什么复制不共享：**skill 是分发最小单位**，用户可能只装 xlsx，跨技能 import 在别人机器上就是断链；代价是修 bug 改三处。两个证据细节：目录名 `ecma/fouth-edition/` 是上游拼写笔误（应 fourth）**三技能同错**；`microsoft/wml-2010.xsd:2-5` 对三个 MS 专有 schema 的 import 被注释——文件从未随仓收录，是已知断链死资产。

库中最精巧的是 `office/soffice.py`：解决沙箱禁 AF_UNIX socket 致 LibreOffice 挂死。运行时探测（`soffice.py:53-59`），受限就把 `_SHIM_SOURCE`（`:78-185` 约 108 行 C）gcc 现场编译注入 LD_PRELOAD（`:62-74`）：C 层拦截 socket/listen/accept/close，socketpair 顶替 AF_UNIX，FD≥1024 直通（`:95-100`），close 写 wake pipe 解除阻塞后 `_exit(0)`（`:180-181`）。契约在 docstring：**必须走 `run_soffice()` 而非拿 `get_soffice_env()` 自己起进程**——env 无 profile 名，非 root 沙箱必失败（`soffice.py:11-15`；`run_soffice` 自动注入临时 profile `:41-45`）。零依赖偏好：office 库仅 defusedxml/lxml，`skills/skill-creator/scripts/utils.py` 手写 frontmatter 扫描不引 PyYAML。

## 6. claude-api 文档线

`skills/claude-api/SKILL.md` 603 行全仓最长，三纪律（`:22-27`）：官方 SDK 优先/绝不裸 HTTP/绝不凭记忆猜 SDK 用法；`:35` 定默认值（claude-opus-5-5+adaptive thinking+默认流式）。结构三层：**总纲+八语言目录+shared 事实层**——八语言同构覆盖，python 最全（README 566 行），curl 最薄（2 件）。`shared/`：`models.md:3` 自我声明"精确 model ID 唯一来源"；`model-migration.md` 2252 行；`managed-agents-*.md` 14 件托管智能体手册（加六语言副本共 21 件，全仓最大同主题簇）——`managed-agents-overview.md:3` 心智模型"每 session 一容器当工作区，agent loop 跑编排层"，`:5-18` 强制 Agent（建一次）→Session（每跑一次）。不只 markdown：`shared/evals/report/build-report-lite.mjs:26-38` 纵深防御范本（O_NOFOLLOW 防 symlink TOCTOU）；`shared/preserved-thinking-migration/drop_block_probe.py:1-30` 与 prefix_diff.py 组成签名失配诊断双探针。

## 7. 测试与工具：技能的生产线

`skills/skill-creator/` 是"用技能造技能"元循环：485 行 SKILL.md 定义草稿→跑测→viewer→重写。`scripts/run_eval.py:35-49` 用 `claude -p` 子进程测**技能触发率**——描述临时注册成命令文件，`select` 监听流式输出靠 `content_block_start` 提前判定（`run_eval.py:108,133`）。防过拟合靠 `run_loop.py:24` 的 holdout 划分（默认 0.4，`run_loop.py:254`）：改进只看 train，test 做诚实验收。三 agent 评测管线（comparator→analyzer→grader）在 `agents/`。mcp-builder 是另一条元工程技能：四阶段方法论+`scripts/connections.py:13-70` 的 `MCPConnection` 用 AsyncExitStack 统一 stdio/SSE/HTTP 三传输（子类 `:73/:88/:100`）；`scripts/evaluation.py:17-30` 评测 prompt 要求三标签——**工具设计质量本身是被测项**。

## 8. 新人上手路线

1. **10 分钟**：`README.md`+`marketplace.json`+`template/SKILL.md`+`spec/agent-skills-spec.md`——建框架。
2. **30 分钟**：`skills/docx/SKILL.md` 全文+第 4 节链路——document skills 工程学浓缩。
3. **30 分钟**：`skills/pptx/SKILL.md:29-50`（gotchas 最密）+`skills/xlsx/SKILL.md:30-69`（公式生存学）+`skills/pdf/forms.md`（双通道）。
4. **20 分钟**：精读 `office/soffice.py` 与 `office/validators/base.py`——vendored 一份等于三份。
5. **20 分钟**：`skills/skill-creator/SKILL.md:86-96` Progressive Disclosure（三级加载：metadata 恒在/SKILL 体 <500 行/资源按需）+`run_eval.py`——写自己技能抄作业。
6. **按需**：claude-api 当手册查勿通读；设计系统（canvas-design 27 份 OFL 字体、theme-factory 十主题+showcase 确认流）与长尾技能（internal-comms 瘦路由、webapp-testing"先 --help 后读源"）按兴趣。

三条心法：**description 就是触发器**，写技能先写这段；**一切产出必须 validate.py+渲染肉眼验收**（recalc 绿灯只证明公式能算不证明算得对，`skills/xlsx/SKILL.md:48-50`）；**技能内文件优先于模型记忆**（`skills/claude-api/SKILL.md:49`）。

## 勘误（实测 vs 图谱/tour 笔记）

1. **技能目录 19 个非 20**：`skills/` 点数 19；`marketplace.json` 注册 4+12+1+1+1=19。
2. **base.py 875 行非 848**：三份全等 `wc -l`=875（NOTES-DIGEST 记 848）。
3. **唯一 ID 规则 15 类非 14 类**：`base.py:31-47` 字典实数 15 条目（comment/rangestart/rangeend/bookmark×2/sldid/sldmasterid/sldlayoutid/cm/sheet/definedname/cxnsp/sp/pic/grpsp）。
4. **wml-2010.xsd 断链三 import 为 orel/oartbasetypes/oartsplineproperties**（`microsoft/wml-2010.xsd:2-5`）；第 2 行另有被注释的 rel 变体，计数勿混。
