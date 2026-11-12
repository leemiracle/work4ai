# 04 · 示例插件生态的解剖学：17 份 manifest 的共性骨架与差异化

## 角色定位

`plugins/examples/` 是 G-Assist 面向社区的主展柜：15 个示例插件覆盖三语言多集成形态，外加共享 `setup.bat`。全仓 17 份 `manifest.json`——15 份在 examples/，另两份属 plugin_emulator 演示件与 plugin-builder 占位。这批示例是**同一副骨架的 17 次变奏**。

## 内部结构

### 共性骨架：五件套

1. **manifest.json**——引擎契约：`executable`/`protocol_version: "2.0"`/`persistent`/`functions[]`。需凭据或引导的插件加 `tether_config`，如 `spotify/manifest.json:8-13`：心跳 5s、超时 20s、`onboarding_timeout: 300`、`allow_passthrough: true`。5/20 是统一节律（多数 onboard=60；spotify 与 twitch 并列 300 最长，非独占——以源码为准）。
2. **plugin.py**——最小形态见 `hello-world/plugin.py`：`Plugin(...)` 初始化（L80）→ `@plugin.command` 登记（L114）→ `on_input` 处理 passthrough（L203）。
3. **config.json**——凭据落点（openrgb/weather 无凭据则省略）。
4. **requirements.txt + libs/**——依赖装进 libs/，靠 plugin.py 顶部 PATH 注入（`plugins/examples/weather/plugin.py:11`）。
5. **文档法务件**——CONTRIBUTING 各插件逐字节一致；ATTRIBUTIONS 按依赖膨胀。

### 共享安装器 setup.bat

`plugins/examples/setup.bat` 用 batch 子程序架构，九个标签：`:setup_plugin`（L70，探测类型并于 L95-97 分派）、`:setup_python`（L115）、`:setup_cpp`（L146）、`:setup_nodejs`（L188）、`:deploy_plugin`（L210）、`:validate_manifest`（L386）、`:check_python_version`（L415）、`:show_help`（L455）、`:done`（L518）。validate_manifest 调 PowerShell 校验 JSON（L407）并拦 0 字节空文件；check_python_version 对比用户与 RISE 内嵌 Python 版本，防解释器漂移。

### 深案例 1：spotify（1053 行，最大）

复杂度全来自 OAuth。**redirect URI 精确匹配陷阱**：`plugins/examples/spotify/plugin.py:163-167` 返回 `http://127.0.0.1:8888/callback`；`plugins/examples/spotify/README.md:44-50` 钉死精确匹配——`localhost` 拒收、https、尾斜杠均不行。**挂起调用机制**：L87 `store_pending_call()` 暂存最初的播放请求，向导完成后 L94 `execute_pending_call()` 回放——onboarding_timeout=300 由此而来。**回调链**：L237 `OAuthCallbackHandler` 捕获授权码，L262 `do_oauth_flow()` 串换 token 全流程。

### 深案例 2：logiled（C++ 线与 V1→V2 断层）

`old_v1/GAssistPlugin.cpp` 保留 V1 尸体：L196-216 一次性 `ReadFile` 进 4096 字节栈缓冲再整体 `json::parse`——无分帧，粘包即碎；写侧 L220-223 以哨兵 `<<END>>` 结尾。新线 `gassist_sdk.hpp`（432 行单头 SDK）：L75-85 先收 4 字节大端长度头再取载荷，L127-135 写侧同构；`plugins/examples/logiled/main.cpp:148` 的 `json::parse` 是加载配置，非协议路径。构建安装：`logiled.vcxproj` 四配置全 `stdcpp20`（L81）；`installer.py` 自提权后拷贝至 `%PROGRAMDATA%\...\nvtopps\rise\plugins`（L80/L515）。

## 外部连接

三层：**对引擎**——stdio 管道，部署终点统一 nvtopps/rise/plugins；**对第三方**——`plugins/examples/mcp-stdio-example/plugin.py:177` 的 `mcp.list_tools()` 把外部 MCP server（`@modelcontextprotocol/server-filesystem`）的工具面自动发现并转登记为 G-Assist 命令，14 个函数全来自这层桥；**对工具链**——plugin-builder 是 Cursor Project Rule，AI 生成流程产出五件套。

## 数据流

spotify 冷启动：读 manifest→拉起 plugin.py 进 tether 模式（心跳 5s）→首命令触发两步向导→浏览器 OAuth→8888 回调换 token→回放挂起的播放请求→调 Web API→结果写回管道。manifest 静态契约、config.json 持久凭据、auth 会话凭据三层分离。

## 设计决策

- **函数描述即路由提示词**：gemini 只登记一个函数 `query_gemini`（manifest:11），描述却 629 字符，内嵌路由规则（"Use ONLY for internet search. DO NOT use for local settings/GPU info..."）——manifest 描述就是 SLM 路由的提示工程。
- **布尔矩阵真相（源码勘误）**：任务背景称"openrgb passthrough=false 唯一"，实测相反——openrgb 的 `allow_passthrough` 为 `true`，全仓无任何插件声明 false；真正布尔离群者是 `weather/manifest.json:5` 的 `"persistent": false`（唯一非持久插件）。
- **依赖形态光谱**：openrgb-python 为 GPLv3，`openrgb/ATTRIBUTIONS.md` 682 行全文收录；nanoleafapi 是 MIT 只需 32 行（L6）；mcp-stdio-example 零 pip 依赖。三档对应三种法务成本。
- **RENAME_ME 占位**：`template_plugin/manifest.json:3` 的 `"executable": "RENAME_ME.exe"` 提醒改名重编，且其 manifest 缺 `protocol_version`——骨架捐赠品非可运行插件。
- 各目录 `plugin-installer.exe` 是 Git LFS 指针存根，需 `git lfs pull`。- **死链与占位甄别**，四处"看起来有、实际没有"：① **README.md:250 Corsair iCUE 死链**——官方清单列 `./plugins/examples/corsair`，目录不存在；② **plugin-builder/plugin.py 是 0 字节空文件**（requirements.txt 同 0 字节），其 manifest 仅 52 字节注释；③ RENAME_ME.exe 占位；④ LFS 存根。README 清单亦漏列 mcp-stdio-example/template_plugin。

## 新人提示

路径：读 `hello-world/plugin.py` 最小骨架→抄 template_plugin 改名→`setup.bat your-plugin -deploy` 走完全链→用 plugin_emulator 单测。三个坑：OAuth 必精确复制 redirect URI；C++ 别参考 old_v1；改 manifest 后必过 validate_manifest。读插件先读 manifest 函数描述——描述含糊的函数等于不存在。
