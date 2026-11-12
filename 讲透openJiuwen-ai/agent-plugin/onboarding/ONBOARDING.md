# agent-plugin 新人上手指南（ONBOARDING）

> 基于知识图谱（162 节点 / 331 边 / 14 层 / 15 步 tour @f05b329）与源码逐文件核实。行号锚全部经过源码验证。

## 1. 项目定位

agent-plugin 是 **JiuwenSwarm（九问蜂群）官方 plugin 插件包集合仓**：对应 Hub 市场（swarmskills.openjiuwen.com）的 `agent-plugin` 资产类型，为智能体提供三类能力扩展（README.md:5-7）——**skill**（SKILL.md 指令，教智能体"何时做、怎么做"）、**tool**（继承 `openjiuwen.core.foundation.tool.Tool` 的可执行类）、**rail**（继承 `openjiuwen.harness.rails.base.DeepAgentRail` 的生命周期钩子）。

在 openJiuwen 生态中：**jiuwenswarm 主仓是插件运行时，本仓是内容供给方**——主仓 extension_package_manager 只扫一层目录加载 `plugin_packages/{local,built_in}/<name>/`，本仓 `plugins/` 每个目录就是最终落盘形态（repo-structure-design.md:13-21）。分发三通道（README.md:9-11）：Hub 在线安装 / 产品内置 / 开发者直拷 local。一句话哲学（repo-structure-design.md:57）：**`plugins/` 里的内容 = 用户拿到的内容（1:1）**，开发态产物全放仓库层。

## 2. 技术栈与代码形态

- **纯 stdlib 工具链**：`scripts/` 七脚本（init/validate/catalog/build/publish/sync_builtin/pr_check）零第三方依赖，仓内没有 requirements.txt——刻意设计，任何 CI 节点装个 pytest 即可全量开发（pr-quality.yml:27）。
- **openjiuwen SDK 是强依赖但未发布公开 pip**：组件 import `openjiuwen.*`（word_count_tool.py:13、turn_counter_rail.py:14），CI 注释明言"openjiuwen 尚未发布到公开源，临时方案见 hub-publish.md"（pr-quality.yml:50）——这决定了 L2 热加载在普通环境只能 SKIP。
- **代码形态**：2 个插件（example-plugin 三组件齐全的教科书；web-to-markdown 真实可用、342 行纯 stdlib、无 rail 段）+ 五类脚手架模板 + 7 工具脚本 + 9 测试文件 + 双语社区模板。最大文件 `scripts/validate.py`（1008 行）。
- **CI/测试**：GitHub Actions（Python 3.11）+ pytest（pytest.ini：`testpaths = tests`、`-q`）；社区模板面向 GitCode 平台。

## 3. 目录结构导览（对应图谱 14 层）

```
agent-plugin/
├── plugins/                  # L07-L08：插件实体（扁平一层，一包一目录 = 分发物）
├── templates/plugin-template/# L02：五类占位符模板（init.py 消费）
├── scripts/                  # L03-L06：工具链（脚手架/校验/打包发布/门禁）
├── catalog/catalog.json      # L01：生成物（lockfile 式，禁止手改）
├── docs/                     # L11：plugin-spec / hub-publish / review-checklist / design
├── tests/                    # L09-L10：scripts 单测 + plugins 行为测试
└── .gitcode/                 # L13-L14：PR 模板（三语）+ Issue 模板（中英各六类）
```

分层逻辑即贡献流程：L01 配置 → L02 模板 → L03 脚手架 → L04 校验 → L05 打包发布 → L06 质量门禁 → L07/L08 成品插件 → L09/L10 双层测试 → L11 规范文档 → L12 总览 → L13/L14 社区接口。

## 4. 核心数据流与工作流：一个插件的完整旅程

**主旅程（六步）**：

1. **init 脚手架**：`scripts/init.py my-plugin --skill usage-guide --tool counter`——`NAME_RE` 拦非 kebab 名（init.py:59-61），拷模板并替换 `{{PLUGIN_ID}}` 等占位符（init.py:67-97）；满屏 `[TODO]`，L0 专拦。
2. **开发填充**：按 docs/plugin-spec.md 灭掉全部 `[TODO]`；行为测试写仓库层 `tests/plugins/<name>/`。
3. **validate 三层校验**：L0 规范 → L1 静态（AST）→ L2 热加载；前层有错则 L2 直接 SKIP（validate.py:973-975）。
4. **catalog 登记**：`catalog.py` 重扫 `plugins/` 生成 catalog.json+同步 README 表格，随 PR 提交。
5. **CI 门禁**：pr_check.py 五连：结构+L0/L1+catalog `--check`+密钥扫描+pytest（pr_check.py:231-243）。
6. **build/publish（维护者）**：合并不自动发布（CONTRIBUTING.md:60）；publish.py 一条龙校验→打包→上传（publish.py:232-253），产物 dist/ 不进 git。

**L2 线（子进程隔离）**：validate.py 主进程不 import openjiuwen，subprocess 起 `hot_load_worker.py`（120s 超时，validate.py:43、847-855），只回收 stdout 最后一行 JSON（validate.py:821-832）；worker 探测 import openjiuwen 失败即 skip（hot_load_worker.py:152-163）——缺 SDK 降级为 SKIP 而非崩溃。

## 5. 关键模块深潜

### 5.1 scripts/validate.py（1008 行校验引擎）

- **L0 质量**：`[TODO` 残留扫描（validate.py:215-231）；i18n 字段须 `{en, zh}` 双语非空；`default_init_input` 与 `quick_inputs[0]` 逐字一致（validate.py:243-255）。
- **L1 静态（纯 ast）**：运行时路径策略拦 `Path.cwd()`/包内写入（validate.py:439-482）、ToolCard 字面量与产物根参数黑名单（validate.py:504-555）、无参构造+`async def invoke`（validate.py:727-735）。
- **manifest 基础**：`id` 必须等于目录名（validate.py:619-623）、空能力数组报错"整段省略"（validate.py:624-629）、SKILL.md frontmatter `name` 等于目录名（validate.py:674-680）。
- **与主仓同源**：逻辑移植自 jiuwenswarm plugin-creator，规范变更需两仓同步（validate.py:14-16）。

### 5.2 scripts/catalog.py（单一事实源生成器）

`collect_entries()` 是唯一裁判：id 重复、id≠目录名、version 非 `X.Y.Z` 直接抛错（catalog.py:70-87）；README 表格夹在 `<!-- catalog:begin/end -->` 锚点间整体重写（catalog.py:32-33、145-158），`--check` 字节级比对防漂移（catalog.py:178-190）。

### 5.3 plugins/example-plugin（三组件教科书）

manifest.json:50-83 声明三类组件：WordCountTool 无参构造+字面量 ToolCard+`async invoke`（word_count_tool.py:19-42）；TurnCounterRail 只实现 before_invoke 一个钩子（turn_counter_rail.py:25-38）；SKILL.md"目标/工作流/验收标准"三段式，明确"统计结果必须来自工具真实返回值，禁止自行估算"（SKILL.md:12）。

### 5.4 plugins/web-to-markdown（真实工程样本）

342 行纯 stdlib。亮点是 SSRF 纵深防御：解析主机全部 IP 防 DNS 绕过（web_to_markdown_tool.py:57-72），重定向逐跳复检（:84-93），响应体 2MB 上限+Content-Type 白名单（:327-334）；`_MarkdownExtractor` 用 `_skip_counts` 计数处理未闭合标签（:129-131）。manifest 无 rails 段（"整段省略"活样本）。

## 6. 设计决策与权衡

- **`plugins/` = 分发物 1:1**（plugin-spec.md:22）：主仓打包器不剔除 tests/、包内测试会原样发给用户（repo-structure-design.md:196）——开发态全放仓库层，build.py 再把 `tests` 列打包黑名单兜底（build.py:43）。
- **纯 stdlib 工具链**：CI 只装 pytest（pr-quality.yml:27）；代价是手搓 multipart（publish.py:149-165）与确定性 zip（build.py:62），收益是 clone 即开发。
- **catalog.json lockfile 式生成物**：提交进 git 但禁手改，CI `--check` 拒漂移（repo-structure-design.md:172）；README 表格、内置同步、Hub 对账三消费者共享（catalog.py:5-7）。
- **openjiuwen 未发布公开 pip**：CI 的 L2 作业里 `pip install openjiuwen` 本身是 TODO（pr-quality.yml:48-52），被 `ENABLE_HOT_LOAD` 变量默认关死——对策=子进程隔离+SKIP 语义，普通环境永远 PARTIAL 而非 FAIL。
- **renames.json 借鉴 claude-plugins-official**：id 一经发布不可变（repo-structure-design.md:81），但 **publish.py 并不读取 renames.json**——9 处引用全在文档层，"据此在 Hub 侧登记别名"是设计意图而非已实现行为。

## 7. 常见任务上手

**新建一个插件（五步）**：

```bash
# 1. 骨架
python scripts/init.py my-plugin --skill usage-guide --tool counter
# 2. 填 manifest/README/组件，消灭 [TODO]（docs/plugin-spec.md）
# 3. 行为测试 tests/plugins/my-plugin/（纯 skill 包可豁免）
# 4. 三层校验（无环境则 PARTIAL）
python scripts/validate.py --only my-plugin
# 5. 更新目录清单并提 PR
python scripts/catalog.py && git add catalog/ README.md
```

**本地校验（等价 CI 门禁）**：`python scripts/pr_check.py`；快查单包 `validate.py --only <name> --no-hot-load`。

**发布到 Hub（维护者）**：设 `JIUWENSWARM_HUB_TOKEN`（不落文件，publish.py:222-225）后 `publish.py <name>`；覆盖/私有 `--force`/`--private`；回滚勿原地 force 覆盖已安装版本（hub-publish.md:30、37）。

**sync_builtin 进主仓**：`sync_builtin.py --repo <主仓> --only <name>`（已存在需 `--force`），同步完在主仓走正常评审（sync_builtin.py:76-79）；建议仅旗舰插件走此通道。

## 8. 新人提示与坑

1. **CI 的 L2 作业默认不跑**：被 `ENABLE_HOT_LOAD` 仓库变量门控（pr-quality.yml:36）——reviewer 需在本地 jiuwenswarm 环境跑 `--require-hot-load` 贴 RESULT 行（review-checklist.md:36-37）。
2. **PARTIAL 退出码是 0、普通环境必 SKIP**：L2 被跳过时 validate.py 默认返回 0（validate.py:999-1002）；行为测试靠 `pytest.importorskip("openjiuwen")` 整体跳过（test_example_plugin.py:17）—本地全绿可能"假绿"；当失败须 `--require-hot-load`。
3. **改名没有自动化**：id 不可变，改名=新建插件+renames.json 登记+旧包发最后版本指路（hub-publish.md:38），且无代码消费 renames.json（见 §6）；catalog.json 与 README 表格同样禁手改，`--check` 拦漂移。
4. **社区模板笔误与冗余**：中文 Issue 模板 `channel-WharsApp` 应为 WhatsApp（ISSUE_TEMPLATE.zh/001-bug-report.yml:52 等）；PR 模板 `.md` 与 `.zh-CN.md` 内容完全相同（md5 一致），实为双语双份。
5. **图谱扫描盲区**：tests/conftest.py:10-12 把 `scripts/` 注入 sys.path（裸导入合法），静态 import 分析对运行时注入零感知。
6. **改包必递增 version**（CONTRIBUTING.md:33）：同版本重传要 `--force`，用户端可能已缓存旧包（hub-publish.md:30）。
