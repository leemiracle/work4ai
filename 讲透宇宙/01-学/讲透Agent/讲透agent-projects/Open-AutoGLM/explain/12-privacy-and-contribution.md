# 12 · 隐私政策与贡献外围：resources/、.github/、pre-commit 与打包配置

## ① 角色定位

这一组文件不写一行 Agent 逻辑，却定义了项目的两条边界：**行为边界**（`resources/privacy_policy.txt`/`privacy_policy_en.txt`——6+1 类高风险操作强制确认、五类禁止行为，是 handler 双回调机制的合规源头）与**工程边界**（`.pre-commit-config.yaml`、`.github/` 三模板、`setup.py`/`requirements.txt`——贡献流程与打包形态）。`resources/WECHAT.md` 只是交流群二维码页，`README_coding_agent.md` 是给 AI 助手读的自动化部署说明（人类读者被明言可跳过）。做产品化或二次开发，第一课是读隐私政策；给上游提 PR，第一课是过工程模板。

## ② 内部结构

**隐私政策**（中文版 133 行）两大部分：第一部分讲机制——AutoGLM 工作原理四步（:4-8）、三种部署模式的数据流向（本地/云端/混合，:10-16：本地=屏幕捕获+模型分析+执行全在设备上数据不出门；云端=屏幕内容上传、指令回传，开发者须保传输与云端安全；混合=本地截图传云端模型分析后回本地执行）、权限清单与开发者四责任（:18-29）、数据处理原则（数据最小化/目的限制/安全保障/用户控制，:43-47），并申明"开源项目本身不收集用户数据"（:32）。第二部分是规范：引用网络安全法、生成式 AI 管理办法与 GB45438-2025 内容标识国标（:53）；**6+1 类高风险操作清单**（:55-64）——信息交互与内容传播/文件处置与权限管理/交易订单与权益处置/资金流转与支付结算/账户身份与安全配置/医疗健康与法律合规/+其他高风险；确认机制三要求（操作前触发、展示详情、可随时中止，:66-69）；五类禁止行为（批量刷量与恶意竞争 :94-101、虚假信息与欺诈 :102-108、破坏第三方服务与系统安全 :109-116、侵犯他人权益 :117-123、滥用资源破坏生态 :124-128）；违反后果全责自负（:130-133）。**pre-commit** 四件套：ruff（只 `--select I` 查 import 排序，:13）+ruff-format（:14）、typos 拼写（:15-18）、pymarkdown fix（:19-23），挂 pre-commit 与 commit-msg 两个钩子位（:1-3）。**.github**：PR 模板三类受理（typo 修复免检/bug 修复需引 issue/新功能需说明必要性，:6-12）+命名规范（英文命名、PEP8、禁无意义名，:25-29）；bug_report.yaml 四段（系统信息必填/who-can-help/官方脚本 vs 自改脚本勾选 :34-42/复现过程禁贴截图 :43-58）；feature-request.yaml 三段（建议/动机/你的贡献，:5-35）。**setup.py**：包名 `phone-agent` v0.1.0（:10-11），install_requires 仅 Pillow+openai（:32-34），console script `phone-agent=main:main`（:44-47）。

## ③ 外部连接

隐私政策与代码的对接点即 handler 的双回调：`confirmation_callback` 对应 6+1 类确认（`phone_agent/actions/handler_ios.py:150-156` 的 Tap-with-message、handler.py 同构），`takeover_callback` 对应"用户干预"场景（登录/验证码）；提示词里 `do(action="Tap", element=[x,y], message="重要操作")` 的 message 参数就是政策落地的协议层。工程侧：PR 模板引用 pre-commit（:19-21 `pre-commit run --all-files`）；setup.py 读 README.md 当长描述（:7-9）；requirements.txt 与 setup.py 的依赖面有意不一致（前者多出 iOS 的 requests :4-5）。

## ④ 数据流

合规流：模型输出带 message 的敏感动作→handler 触发 confirmation_callback→终端 Y/N（默认实现 `input()`，handler_ios.py:271-275）→拒绝则任务终止。用户拒绝后责任划分按政策 :69——"用户在确认后未及时终止错误操作导致的损失，由用户自行承担"。贡献流：fork→改码→`pre-commit run --all-files` 过 ruff-format/typos/pymarkdown→按 PR 模板自检（typo 类可跳过其余检查）→CI；Issue 则按 bug_report 必填系统信息+复现（最小复现单元、代码用代码块不用截图）。安装流：`pip install -e .` 走 setup.py → console script 注册；但纯 `pip install phone-agent`（非 -e）时 `main:main` 入口依赖仓库根的 main.py 可导入性，见下。

## ⑤ 设计决策与陷阱

1. **exclude 重复键陷阱（钉版）**：`.pre-commit-config.yaml:4-5` 连写两个 `exclude:`——YAML 规则后键覆盖前键，**实际只排除 `README_en.md`，`apps.py` 没被排除**（注释意图恰恰相反）；ruff-format 若重排 apps.py 的字典会影响键序语义（get_app_name 取首键）。
2. **setup.py 三处硬伤**：url 还是占位符 `https://github.com/yourusername/phone-agent`（:17）；install_requires 漏了 iOS 必需的 requests（requirements.txt:4-5 有）；`entry_points` 指向 `main:main` 而 main.py 不在任何包内，`find_packages()` 收不到它，非 editable 安装后 console script 大概率 ImportError。
3. **PR 模板的遗留章节**：:31-40 "For glmv-reward Contributors" 要求 `cd glmv-reward/ && uv run poe lint`——本仓无此目录，是从智谱另一项目模板带来的残留，提交 PR 时忽略即可。
4. **ruff 只查 import 排序**（`--select I`），不是全量 lint——风格合规≠静态检查全过；typos 对 apps.py 里大量中文键与品牌拼写是主要防线（这或许正是想 exclude 它的原因）。
5. **政策的"开发者责任"前置**：政策 :32 把数据合规责任完全转移给下游开发者；二次开发若接云端模型，:38-42 的加密传输/知情同意/法规合规是硬要求，不是建议。
6. **双语政策非逐字对照**：privacy_policy_en.txt 与中文版结构对应但细节有出入，以中文版（项目主语言）为准。

## ⑥ 新人提示

提 PR 前三步：本地 `pre-commit install`（钩子会同时挂 commit-msg）；跑 `pre-commit run --all-files` 清格式；按 `.github/PULL_REQUEST_TEMPLATE.md` 核对受理类型。Issue 报 bug 务必带系统信息与最小复现（模板 :43-58 明确拒绝截图贴代码）。产品化前通读 privacy_policy.txt 第二部分，把 6+1 类清单映射到自己的 confirmation_callback 实现里（默认的终端 Y/N 只适合调试，生产要换 UI 确认）；`Takeover` 动作对应政策的"及时干预"义务，别删。读 README_coding_agent.md 的应该是你的 AI 助手，不是你。
