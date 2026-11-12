# 11 · 中文文档群考古：sandbox/docs 与 examples 的承诺与落差

> 所属仓库：OpenDCAI/AgentFlow（图谱 909 节点/1857 边）。本篇做文档考古：`sandbox/docs/`（zh-CN 全量 10 份 + en-US 6 份，中文侧是完整版）+ `examples/` 五篇 agent 指南（合计约 2250 行）+ 根 README 双语。结论先行：**这套文档写于代码的"黄金期"，之后代码多轮重构而文档停更**——按文档动手的新人会撞上一片断链。以下每条勘误均已对盘核实。

## 一、角色定位

文档树三层分工：

- **sandbox/docs/zh-CN/**——sandbox 子系统专文档，是全仓唯一的系统性技术文档：`guides/ARCHITECTURE.md`（618 行，架构总纲）、`guides/USAGE_GUIDE.md`（192 行）+ `guides/USAGE_demo.md`（38 行）、`development/` 四篇（API_TOOL_TUTORIAL 343 行、BACKEND_DEVELOPMENT 1408 行、REGISTRATION_GUIDE 910 行、RESULT_FORMATTER 430 行）、`api/` 两篇（ERROR_CODES 781 行、QUICK_REFERENCE 312 行）。en-US 目录只有 6 份（缺 development 后三篇与 USAGE_demo）——**中文才是第一公民**，英文是残缺子集。
- **examples/ 五篇**——按域的端到端 cookbook：DocAgent（541 行）、WebAgent（507 行）、Text2SQL（548 行）、RAGAgent（467 行）、DSAgent（188 行），每篇走"沙箱配置→synthesis 造数→trajectory 采集→infer 评测"全流程。
- **根 README.md/README_zh.md**——项目门面与成绩表（MMLongBench-Doc/DocBench 榜单，README.md:239）。

这套文档的**真实价值**在于讲透了设计意图（架构图、生命周期、Session 路由、错误码表都相当细）；**真实风险**在于具体路径与文件名大面积失真——它是一份优秀的"设计快照"，不是可靠的"操作手册"。

## 二、内部结构（以 ARCHITECTURE.md 为主轴）

`zh-CN/guides/ARCHITECTURE.md`（618 行）九节：整体架构→核心组件→数据流→生命周期→Session 管理→工具注册→后端扩展→配置系统→API 接口。质量最高的部分：

- **核心组件节**给出 ResourceRouter 会话路由的内存结构 `self._backends: Dict[str, Backend]`（ARCHITECTURE.md:128）与状态查询响应样例（ARCHITECTURE.md:250 `{"backends": {"rag": {"loaded": True, "warmed_up": True}}}`）——与 sandbox/server 的 ResourceRouter 实现对得上；
- **配置系统节**的 backend_class 动态加载示例（ARCHITECTURE.md:493 `"sandbox.server.backends.resources.vm.VMBackend"`）与 config_loader.py:334-357 的实现一致；
- **API 接口节**的响应信封 `{code, message, data, meta}` 与 result_formatter.py:23-35 一致。

`development/` 四篇是给后端开发者的：API_TOOL_TUTORIAL 教无状态 API 后端（四步：写工具类→注册→quick 验证→进配置）、BACKEND_DEVELOPMENT（1408 行全仓最长文档）教有状态资源后端的完整生命周期、REGISTRATION_GUIDE 讲 @tool 注册机制、RESULT_FORMATTER 讲九类格式化器（与 result_formatter.py 实现对齐，是少数没有夸大未实现类的文档）。

`api/ERROR_CODES.md`（781 行）把沙箱错误码逐个列表——这份与 sandbox/server/backends/error_codes.py 对应，是排障时最值得信任的文档。

## 三、外部连接

- **对代码**：文档声称的路径就是它与代码的接口——也是断链重灾区（下节详表）。
- **examples 对 projects/DocDancer**：DocAgent.md 的评测链最终指向 projects/DocDancer/eval/ 的两份 prompt md（第 10 篇）；ARCHITECTURE.md 头部互链 BACKEND_DEVELOPMENT.md 与 USAGE_GUIDE.md。
- **README 成绩表对外部基准**：MMLongBench-Doc acc/F1/LasJ 与 DocBench LasJ 列（README.md:239、README_zh.md:224）复用 projects/DocDancer/README.md:191 的同一套数字——两处 README 与子项目三方联动，改一处要改三处。

## 四、文档 vs 磁盘：勘误清单（全部实测核实）

### A. sandbox-server 启动脚本名（波及最广）

全部文档写 `./sandbox-server.sh`（README.md:110、README_zh.md:92、USAGE_GUIDE.md、五篇 examples），**根目录实际文件名是 `start_sandbox_server.sh`**。另有 API_TOOL_TUTORIAL.md 写 `bin/sandbox-server.sh`（bin/ 目录整个不存在）。新人照 README 敲第一条命令就 No such file。

### B. ARCHITECTURE.md 的三后端幻影

ARCHITECTURE.md:469-471 的目录树声称 `backends/` 下有 `bash.py`（Bash 终端后端）、`browser.py`（浏览器混合后端）、`code_executor.py`（代码执行后端）；ARCHITECTURE.md:613 再次声称 `resources/` 重量级后端含 "vm, rag, bash, browser, code_executor"。**实测 `sandbox/server/backends/resources/` 只有 `vm.py`、`rag.py`、`mcp/`、`utils/` 四项**——bash/browser/code_executor 三个文件不存在。这三类后端要么从未进主仓、要么已被移除（rollout 配置里也确无这三类资源），但架构文档的核心目录树仍带着它们。

### C. profiles 配置体系不存在

ARCHITECTURE.md、BACKEND_DEVELOPMENT.md、REGISTRATION_GUIDE.md 多处引用 `configs/profiles/dev.json`、`configs/profiles/production.json`（如 ARCHITECTURE.md 的配置章节）——**configs/profiles/ 目录不存在**，config_loader.py 也没有任何 profile 分层逻辑。文档描述的是一套设计过的"多环境配置"机制，代码里没落地。

### D. 虚构的辅助脚本与机器路径

- `quick_sandbox.py`：API_TOOL_TUTORIAL.md:3/96-133 反复引用的快速验证脚本，**全仓不存在**；文中给的运行命令是 `python /home/a1/sdb/tzw/Synthesis/quick_sandbox.py`（API_TOOL_TUTORIAL.md:133）——**另一位原作者机器的绝对路径**。
- `sandbox.py`/`sandbox.sh`（ARCHITECTURE.md、BACKEND_DEVELOPMENT.md 引用）：不存在。
- USAGE_GUIDE.md 引用 `configs/sandbox-server/vm_config.json`：不存在（vm→GUI 改名遗留，实际是 GUI_config.json——第 07/09 篇同源坑）；API_TOOL_TUTORIAL.md 引用 `configs/server/my_api_sandbox.json`（configs/server 目录不存在）。

### E. examples 五篇的三类断链

1. **file:// 本地链失效**：DSAgent.md 通篇 7 处链接形如 `[configs/.../ds_config.json](file:///Users/bytedance/Documents/trae_projects/agentflow218/agentflow218/AgentFlow/...)`（DSAgent.md:3、54-55、71、137、157、165）——**原作者（bytedance，trae IDE 工程目录）的本机绝对路径直接进了公开文档**，任何环境点开全失效。其余四篇是正常相对链接，只有 DSAgent 带毒。
2. **扩展名系统性错误**：五篇全部把种子与基准写成 `.json`（`seeds/doc/seeds.json`、`benchmark/rag_benchmark.json`……），**实际全是 `.jsonl`**——批量笔误说明五篇是同一模板套出来的。
3. **Text2SQL.md 三引用不存在**：`configs/infer/text2sql_infer.json`（Text2SQL.md:368-371 还给出完整配置样例）、`benchmark/text2sql_benchmark.json`、`seeds/text2sql/seeds.json`——text2sql 场景**只有 synthesis 层配置**（configs/synthesis/text2sql_config.json），infer 层与基准数据都不存在。文档画的"text2sql_infer→benchmark→infer_results"流程图（Text2SQL.md:99）是规划稿而非现状。

### F. 其余小项

USAGE_GUIDE.md 引用 `sandbox/configs/profiles/dev.json`（sandbox/ 下无 configs 目录）；DSAgent.md 引用 `seeds/ds/seeds.json`（.jsonl 之误）；DocAgent.md 引用 `benchmark/doc_benchmark.json`（实际在 `benchmark/doc_benchmark/Input/doc_benchmark.jsonl`，深两层）。

## 五、设计决策（含批判）

**做得好的**：①zh-CN 文档的**概念层**质量是真的——生命周期、Session 路由、错误码、工具注册四份"机制讲解"至今与代码吻合，读懂它们再读源码事半功倍；②examples 的"全流程四段式"结构（沙箱→造数→采轨迹→评测）是好骨架，五域复用同一骨架降低认知成本；③文档间互链成网（ARCHITECTURE↔BACKEND_DEVELOPMENT↔USAGE_GUIDE），有体系的野心。

**要批判的**：

1. **文档与代码无同步机制**是最根本的问题——vm→GUI 改名、后端裁撤、脚本改名、目录重组全部发生而文档零跟进。病灶是文档里的路径全是**手写内联**而非生成或 CI 校验，一个"文档路径体检"脚本（本篇第三节的方法，30 行 Python）就能在 CI 里拦住全部 A-E 类断链。
2. **机器路径与 file:// 链外泄**（DSAgent.md 的 /Users/bytedance/...、API_TOOL_TUTORIAL 的 /home/a1/sdb/tzw/...）暴露文档出自多作者各自环境直接粘贴，没过发布卫生检查。顺带这也泄露了组织信息（字节系 trae IDE 工程目录）。
3. **规划当现状写**：Text2SQL 的 infer 链、profiles 配置体系都是"文档先行"的产物，读者无从分辨哪些是已实现哪些是路线图——文档没有 status 标注。
4. **双语不同步**：en-US 缺四份核心开发文档，英文用户拿到的是半套系统认知。

## 六、新人提示

- **读文档的正确姿势**：概念章节（机制、生命周期、错误码）可信度高，直接读；**任何具体路径/文件名/命令先对盘再执行**——`ls` 或 `test -f` 一下，本篇第三节就是现成的断链地图。
- **起沙箱的正确命令**是 `./start_sandbox_server.sh --config configs/sandbox-server/<域>_config.json`，README 与所有文档里的 `sandbox-server.sh` 一律脑内替换。
- **学后端开发**：BACKEND_DEVELOPMENT.md（1408 行）+ REGISTRATION_GUIDE.md + RESULT_FORMATTER.md 三连读仍是最佳路径，讲解质量高于源码 docstring；但跳过其中所有 profiles/configs/server 相关段落。
- **学 text2sql 场景**：以 examples/Text2SQL.md 的**概念流程**为纲，落地的配置只有 configs/synthesis/text2sql_config.json 一份，infer 层要自己照 ds_infer.json 抄一份（sandbox-server 侧的 text2sql_config.json 是现成的）。
- **别用 DSAgent.md 的链接跳转**，全部失效；把它当纯文本读，路径自己拼。
- **贡献文档前**：跑一遍路径体检（提取 md 里的 repo 路径正则逐个 test -e），别给断链地图再添一笔；已有断链的修复优先级：A（脚本名，挡第一命令）> B（后端幻影，误导架构认知）> E（examples 三类，挡实操）。
