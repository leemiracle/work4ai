# 05 · OSWorld vendored 考古：desktop_env、机载 server 与三处明文凭据

## 角色定位

`sandbox/server/backends/resources/utils/desktop_env/` 是整仓原样收编的 **OSWorld** 桌面环境代码（xlang-ai 的真实计算机环境 benchmark），AgentFlow 把它 vendored 进来而非 pip 依赖，使 VMBackend（04 篇）能直接驱动 docker/aliyun 虚机、调用其评测器。同目录的 `osworld-settings/` 是 OSWorld 任务配置夹带的应用账号设置。这一篇是「考古」视角：vendored 代码有上游的血统、伤疤与遗留危险品，读懂它们才能安全改造。

## 内部结构

**desktop_env 全量盘点**：53 个文件、其中 45 个 Python（排除 __pycache__ 实测），五大板块——`providers/`（vm 供给层：base.py 97 行双 ABC + docker 184 行 + aliyun 430 行，04 篇已析）、`controllers/`（setup.py 的 SetupController 与 python.py 等，负责向机内 agent server 发指令）、`evaluators/`（**getters/ 12 文件 + metrics/ 16 文件**）、`server/`（机载 Flask main.py）、顶层 actions.py/proxy_pool.py。

**evaluators 是 OSWorld 的评测心脏**，采用 getter×metric 组合式协议：getter 从环境取实况（chrome.py 一个文件集中 **32 个模块级 getter 函数**，全目录之最——从读标签页、书签、历史到扩展 manifest 都有；另 file/general/vlc/vscode/gimp 等 11 个兄弟文件），metric 对「实况 vs 期望」打分（chrome/docs/slides/table/thunderbird/vlc/vscode/gimp/libreoffice/basic_os/general/others/pdf/utils 16 文件）。VMBackend 的 vm:evaluate（vm.py L2093-2105）正是按字符串名把 evaluator 配置路由到这两个模块的函数——OSWorld 任务 JSON 里的 `func/result/expected` 结构原样穿透到 vendored 代码。

**机载 server**（server/main.py，**1988 行**）：跑在虚机内部的单文件 Flask 应用，实测 **27 个路由路径**（`@app.route` 双引号/单引号混用；其中 `/setup/execute` 与 `/execute`（L77-78）、`/setup/execute_with_verification` 与 `/execute_with_verification`（L121-122）两对是同函数别名，实际 25 个处理函数）。按功能分五族：执行族（execute/execute_with_verification，pyautogui 动作落地）、观测族（screenshot L264 / terminal L348 / accessibility L903 / cursor_position / platform）、文件族（file/list_directory/desktop_path/wallpaper）、setup 族（launch/upload/download_file/open_file/activate_window/close_window/change_wallpaper，布置任务初始状态）、录制与代码族（start/end_recording L1497/L1565 + recording_status L1640、run_python L1762、run_bash_script L1857）。文内 fixme 密度可观：L72 录制进程是全局单例「temporary solution for recording, need to be changed to support multiple-process」、L266/L274 虚机上光标不被截图捕获的两处临时补丁——这些都是上游已知债。

**osworld-settings/**（应用账号配置）：google/、googledrive/、proxy/、thunderbird/ 四目录，正式文件与 `.template` 并存。googledrive 的 credentials.json 与 client_secrets.json 实测为空占位（OAuth 侧干净）；**但三处是真实明文凭据、完全未脱敏**：

- `google/settings.json` L2-3：真实 Gmail 账号 `wordalan99@gmail.com` + 明文密码（template 里对应位置是 `your_google_account` 占位，diff 实证）；
- `proxy/dataimpulse.json` L5-6：DataImpulse 代理服务的真实 username/password（template 为 `your_username/your_password`，diff 实证）；
- `thunderbird/settings.json`：真实 Outlook 账号 `anonym-x2024@outlook.com` + 一个高熵明文密码——且 `settings.json.template` 与正式文件内容相同，**连模板都带着真凭据**（grep 实证）。

## 外部连接

上游被 VMBackend 消费：vm.py L51-54 import PythonController/SetupController/create_vm_manager_and_provider/metrics/getters；GUI 场景（configs/sandbox-server/GUI_config.json、seeds/GUI）的种子与 evaluator 配置按 OSWorld 任务格式组织。机载 server 由 SetupController 经 HTTP（默认 5000 口）与 pyautogui/截图/文件操作通信，chromium 9222、vlc 8080 等辅助端口由 SetupController.__init__（setup.py L113）携带。proxy_pool.py 与 proxy/dataimpulse.json 配套——OSWorld 某些任务需要走代理访问外网，这正是 DataImpuse 凭据的用途；use_proxy 开关从 VMBackend 配置一路透传到 setup 调用（vm.py L2012-2027 的惰性 `_proxy_setup`）。

## 数据流

一次 GUI 评测的环境流：GUI_config.json → VMBackend 建池 → docker provider 起容器（server 5000/chromium 9222/vnc 8006/vlc 8080 四口映射）→ initialize 时 SetupController 依次调 `/setup/launch`、`/setup/execute`（osworld-settings 里的账号在此刻注入应用：google 登录、thunderbird 配置、代理设置）→ agent 循环里 vm:* 动作全转成对机内 server 的 HTTP 请求 → vm:evaluate 时 getter 再经 server 从应用实况取状态 → metric 算分。

## 设计决策（含批判）

- **vendored 而非依赖**：OSWorld 无稳定 PyPI 包、且 AgentFlow 需要贴着改（providers 工厂签名加 os_type 参即是一例），收编合理；代价是与上游更新彻底脱钩，上游修复不会自动到达。
- **上游伤疤两处钉版**：① `evaluators/getters/calc.py` L9-14 的缩进缺陷——`with open(csv_path) as f:` 块内只有 `reader = csv.reader(f)` 一行，`next(reader)`（跳表头）与列表推导（取第三列）都写在 with 块外：文件句柄离开 with 即关闭，`next(reader)` 会在「I/O operation on closed file」上炸——此 getter 按原样不可运行，是 vendored 代码「看着在、跑着崩」的典型；② `controllers/setup.py` L718 与 L766 两处 `port = self.chromium_port  # fixme: this port is hard-coded, need to be changed from config file`——9222 默认口在构造参数里可配，但这两处注释承认实际取值路径没有真正接到配置文件，docker provider 又会动态选口（provider.py L96 `_get_available_port(9222)`），两相叠加时 chrome 相关 getter 可能连错端口。
- **明文凭据是本仓最高优先级安全问题**：三份真实凭据直接进 git 历史，`.template` 机制形同虚设（thunderbird 连模板都泄漏）。处置建议：立即轮换三组凭据、正式文件改 gitignore、走 01 篇协议层的 `${VAR}` 展开注入。评测账号往往是共享资产，泄漏面比个人账号更大。
- **机载 server 单文件 1988 行**：上游为容器内自包含而设计，可理解；但 27 端点无鉴权（虚机内网假定信任），一旦端口映射到宿主外网即是裸奔面——部署时 docker 端口绑定务必收口。

## 新人提示

1. 不要假设 vendored 代码「上游测过所以能跑」——calc.py 的闭文件 bug 证明至少部分 getter 从未被这条链路触发过；用到新 getter 先单测。
2. 排查 GUI 任务失败时分两层：先 curl 机内 server 的 /platform 确认容器活着，再看 SetupController 日志里的 setup 步骤——一半的「评测失败」其实是环境没布好。
3. 改 providers 记得 vm.py L466-468 的 TypeError 兼容——上游 `start_emulator(path, headless)` 双参与本仓三参 `(path, headless, os_type)` 并存，新 provider 两种签名都要能接。
4. 任何要引用 osworld-settings 的脚本，先确认自己读的是 template 还是正式文件；提 PR 前跑一遍 `git grep -n "password" sandbox/server/backends/resources/utils/osworld-settings/` 防止二次泄漏。
