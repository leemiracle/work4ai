# 12 · 文档站构建中枢：`docs/source/conf.py`

## 1. 角色定位

180 行（wc 实测），Sphinx 文档站配置文件——torchjd.org 的"总装配线"。本仓文档哲学是"docstring 即文档"（autodoc 渲染 docstring，doctest 让示例真跑），本文件是该哲学的工程载体三件套：①**单一配置源**——作者/版本/项目名全部从 `pyproject.toml` 现读（:27-37），杜绝双处漂移；②**linkcode**——API 页每个符号挂"跳到 GitHub 源码行"链接（:85-146）；③**自定义 doctest 指令**——给内置 `testcode` 补 `:emphasize-lines:` 高亮（:149-180）。CI 侧 build-doc job（`checks.yml:79`）执行 `make dirhtml`（:97）+ `make doctest`（:101），警告即失败（`docs/Makefile:6` `SPHINXOPTS ?= -W --keep-going -n`），再经 `build-deploy-docs.yml` 部署（tag→版本号、main→latest/stable）。图谱归入"API 文档站"层，与 49 页 rst 构成 documents 边网络。

## 2. 内部结构：函数地图

**元数据段**（:18-37）：`_PATH_ROOT`（:22）定位仓根；`with open(_PATH_PYPROJECT, ...) as fp: pyproject_config = tomli.load(fp)`（:27-28）载入；随后 `authors`（:30）、`project`（:34）、`copyright`（:35）、`release`（:37）逐项取——conf.py 自身零硬编码版本号。

**扩展与主题**（:42-76）：七个扩展（:42-50）——`autodoc`（docstring 渲染）、`linkcode`（源码链接）、`sphinx_autodoc_typehints`（类型进签名）、`intersphinx`（:60-63 配 Python 官方与 **PyTorch 稳定版**两目标）、`myst_parser`（markdown 支持）、`sphinx_design`（双栏对照卡片）、`doctest`。主题 `furo`（:55），深浅双 logo 与双色变量（:66-76）；自托管统计挂 `stats.torchjd.org`（:78-80，非第三方追踪）。`autodoc_member_order = "bysource"`（:59）——按源码序而非字母序排成员，与"读源码式的文档"气质一致。

**linkcode 四件套**（:85-146）：
- `linkcode_resolve(domain, info)`（:85-110）：`domain != "py"` 即 None（:93）；`_get_obj` 沿 fullname 逐级 getattr（:113-122，:121 `inspect.unwrap` 剥装饰器）；`_get_file_name`（:125-131，property 的 TypeError 退 None :129-130）；`_get_line_str`（:134-138）用 `getsourcelines` 生成 `#L{start}-L{end}` 锚；`_get_version_str`（:141-146）优先 `TORCHJD_VERSION` 环境变量、缺省 `"main"`（:145）；拼 `https://github.com/SimplexLab/TorchJD/blob/{version}/{file}#L...`（:109）——**文档站每个符号都能一键跳到精确行号的源码**，本 explain 系列的行号锚方法论与它同源。

**自定义指令**（:149-180）：`_TestcodeWithEmphasisDirective(TestcodeDirective)`（:149）——`option_spec` 增 `"emphasize-lines"`（:162-165）；`run()`（:167-176）把行号规格转 `hl_lines` 塞进节点 `highlight_args`（:171-175），与 `code-block` 机制对齐；docstring（:153-159）注明理想归宿是上游 Sphinx（附 issue #6915/#6858）。`setup(app)`（:179-180）以 `override=True` 替换内置 testcode。

## 3. 外部连接

**输入依赖**：`pyproject.toml`（:23 路径、:27-28 读取——版本 bump 只改一处，文档自动跟随）；`docs/Makefile`（严格模式开关 :6）；`icons/favicon.ico`（:65）与 `_static`/`_templates`（:56-57）。**消费方**：`docs/source/docs/` 全部 rst 页（aggregation/scalarization/autojac/linalg/autogram 五个 index.rst 加各 API 页，图谱 documents 边 118 条的主要落点）、`docs/source/examples/` 11 篇教程、`index.rst` 四子包 toctree；CI 三方（`checks.yml:79` build-doc、`build-deploy-docs.yml` 部署、release 流程打版本时 `TORCHJD_VERSION` 环境变量注入 :143 使 linkcode 指向 tag 而非 main）。**doctest 的运行时依赖**：示例里 import 的 torchjd 本体——`make doctest` 等于每次 CI 都把文档示例当测试跑一遍，`backward` docstring 的 `param.jac` 期望值（09 篇）就是被它守住的。

## 4. 数据流：一次文档构建的走读

`uv run make dirhtml`（CI `checks.yml:97`）触发：

1. Sphinx 启动，import conf.py——顶层代码先跑：tomli 读 pyproject（:27-28）→ 全部全局变量就位（:30-37）→ `setup(app)`（:179-180）注册增强版 testcode；
2. autodoc 扫描各 rst 页的 `.. autoclass::`/`.. autofunction::` 指令，import torchjd 并抽取 docstring；`sphinx_autodoc_typehints` 把类型标注（如 `Weighting[PSDMatrix]`，06 篇）插进签名渲染；
3. 每个被文档化对象触发 `linkcode_resolve`（:85）：`_get_obj` 逐段 getattr（:118-119）→ `unwrap`（:121）→ `getsourcefile` 相对化（:127-128）→ `getsourcelines` 取行区间（:135-137）→ 拼 GitHub URL（:109）；`TORCHJD_VERSION` 由部署工作流按 tag 注入（:143），线上 stable 文档的 [source] 链接因此精确指向发布 tag 源码；
4. doctest 阶段（`make doctest`，CI :101）：收集所有 `.. testcode::` 块逐块执行、比对 `testoutput`——`_engine.py:84-112`、`_backward.py:53-66`、aggregation/scalarization 包 docstring 的示例全部在此过关；
5. `-W --keep-going -n`（Makefile :6）把警告升级为错误、nitpicky 模式检查所有交叉引用——坏链接/漏文档直接红 CI，文档债无法静默累积；
6. 部署工作流把 `_build/dirhtml` 推到 TorchJD-documentation 仓，GitHub Pages 生效。

## 5. 设计决策（含批判视角）

- **conf.py 读 pyproject 而非抄写**（:27-37）：版本/作者单一事实源。发布流程（skills/prepare-release）改一处，文档、PyPI、Citation 全同步——消灭了"文档说 0.1 实际 0.2"这一开源库经典事故；
- **linkcode 行号锚**（:134-138）：`getsourcelines` 的 start/end 天然精确到定义区间，比"链接到文件"体验高一档；`inspect.unwrap`（:121）处理装饰器包装是个容易被忽略的细节——漏掉它时 `@overload` 或 property 的链接会指向装饰器本身；
- **向上游提交前的本地补丁**（:149-180）：`emphasize-lines` 是 Sphinx doctest 的已知缺口（docstring 引 #6915/#6858），本仓选择子类化本地解决而非等待——30 行换教程示例的可读性，且 `override=True` 挂载无侵入；
- 批判视角一：`linkcode_resolve` 在构建期对每个对象做 `getattr`+`inspect` 反射（:113-138），任何符号导入失败/property 抛异常都要靠 try/except 兜（:98-100、:129-130）——防御式代码两处，说明这条路天然脆弱：新增奇形对象（如描述符）时这里是最可能悄悄断链的地方，且 `-n` 模式不查 linkcode 有效性；
- 批判视角二：`_get_version_str` 缺省 `"main"`（:145）意味着本地构建的文档链接全部指向 main 分支——线上 main 与本地 checkout 的行号可能已漂移，链接"精确"是有前提的（tag 构建）；
- 批判视角三：自托管统计脚本（:78-80）内嵌远程 JS，文档站离线/内网环境会静默缺失统计——工程上无伤大雅，但"文档站零第三方依赖"的洁癖在这里留了个小口（域名虽自有，仍是运行时外链）。

## 6. 新人提示

1. 改任何公共 docstring 前记住两件事：它会被 autodoc 原样渲染到 torchjd.org（AGENTS.md:1-2 规定 Sphinx 风格、不用 `:returns:`），其中的 `>>>` 示例会被 `make doctest` 真跑——写错数值等于写错断言；本地验证一条命令：`uv run make -C docs doctest`；
2. 加新 API 页的固定动作：`docs/source/docs/<子系统>/` 建 rst → `index.rst` toctree 挂链 → CI 的 `-n` 模式会逼你把所有 `:class:` 交叉引用写对（intersphinx 已配 torch/python 两库，`:func:`torch.autograd.grad`` 这类写法可直接跨链）；
3. 教程示例想高亮关键行：用 `.. testcode::` + `:emphasize-lines: 5-6`（本仓 :149 的增强指令，`_engine.py:82` 的 docstring 是现成范例）——普通 `code-block` 之外的唯一可运行且可高亮的容器；
4. 发布版本的文档差异：`build-deploy-docs.yml` 会注入 `TORCHJD_VERSION`（:143 的读取点），所以"线上 stable 文档的 [source] 链接指向 tag 快照、latest 指向 main"——排查"文档与代码不一致"时先确认你看的是哪个版本入口。
