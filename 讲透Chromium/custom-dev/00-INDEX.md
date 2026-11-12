# Chromium 定制开发实战手册（custom-dev 系列·全栈 56 篇版）

> 2026-10-12~13 产出。基于源码 @8fe2331 逐行级走读 + understand 图谱（40,412 节点）导航 + 官方文档交叉验证。
> 目标：定制开发 Chromium / 自制浏览器的系统性参考——市面资料空白区的第一手知识库。**31 组勘误纠正了全网流传的过时教程**（速查表见下）。

## 三期新增：media 与自动化线（15.x / 16.x）

| 篇 | 标题 | 亮点 |
|---|---|---|
| 15.1 | media 栈总览 | 播放管线全图+进程分布；**media/blink 拆迁勘误** |
| 15.2 | 编解码/硬解/DRM | 四级解码闸门+平台后端矩阵；**CDM 独立服务进程**（反勘误 15.1） |
| 15.3 | 视频产品定制 | PiP/录制三通道/DRM 截帧边界/MP4+AV1 编码服务 |
| 16.1 | CDP 总览 | 协议域三层分类+Page.navigate 全链；**自定义域五步** |
| 16.2 | CDP 自动化实战 | 三通道选型+50 行零依赖采集器；--headless=old 已死 |
| 16.3 | Agent 通道 | **chrome/browser/actor 官方 agent 引擎解剖**（101 文件）+isTrusted 事实基线 |

## 二期新增：内核线（13.x Blink / 14.x V8）

| 篇 | 标题 | 亮点 |
|---|---|---|
| 13.1 | Blink 总览 | 四层解剖+public 出口面；**override.json5 fork 官方通道** |
| 13.2 | DOM 到像素 | lifecycle 状态机六段；UA 样式 C++ 注入更优解 |
| 13.3 | Web 标准行为定制 | runtime_enabled_features.json5（7803 行）三层汇流 |
| 13.4 | 绑定层管线 | IDL 声明式路线四步加 API；**Jinja 架构已死勘误** |
| 13.5 | 脚本注入 | 注入通道矩阵+用户脚本引擎五件套（油猴类刚需） |
| 14.1 | V8 总览 | 9 场景 isolate 拓扑全实证；gin 共同基座发现 |
| 14.2 | 自定义 JS API | 注入三路线对比+mybrowser bridge 全链 |
| 14.3 | V8 flag 与性能 | gin:281 消费链+产品调优基线方法 |
| 14.4 | V8 sandbox | ⏸ 用户中止（初稿在盘，未终验） |

## 读者路径建议

- **第一次定制**：01 → 1.1 → 1.3 → 3.3（先把"自己的浏览器"跑起来）
- **自制浏览器/嵌入**：2.1 → 2.2 → 2.3（最小嵌入清单=11 件套 4600 行）
- **UI 产品化**：4.2（自建 chrome:// 页最容易）→ 4.1 → 4.3
- **跨平台**：5.1 → 5.2 → 3.2 → 5.3
- **AI 浏览器**（kylin-ai 类）：12.1 全景 → 12.2 官方内容管线 → 12.4 换芯 → 12.3 面板 → 7.2 五通道
- **网络定制**：6.1 → 6.2 →（6.3 代理 / 6.4 证书 / 6.5 DNS 按需）

## 全篇清单（40 文件）

| 组 | 篇目 |
|---|---|
| 00 总览 | 01-custom-dev-map（路线决策地图） |
| 1.x 构建系统（4） | 1.1 总流程 · 1.2 GN 语言 · 1.3 args 矩阵 · 1.4 打包分发 |
| 2.x Content API（3） | 2.1 三大 Client 契约 · 2.2 嵌入范例对比 · 2.3 导航生命周期 |
| 3.x 启动品牌（3） | 3.1 桌面启动链 · 3.2 Android 启动链 · 3.3 品牌+去 Google 化 |
| 4.x UI（3） | 4.1 views 加控件 · 4.2 WebUI 自建页面 · 4.3 窗口结构 |
| 5.x 平台（3） | 5.1 平台抽象双轴 · 5.2 Android×Linux · 5.3 分发矩阵 |
| 6.x 网络栈（5） | 6.1 服务化架构 · 6.2 请求拦截/自定义 scheme · 6.3 代理 · 6.4 证书 · 6.5 DNS |
| 7.x 渲染（4） | 7.1 管线全景 · 7.2 内容获取五通道 · 7.3 图层定制 · 7.4 GPU 命令流 |
| 8.x 扩展（2+1merged） | 8.1 架构与管控（含原 8.2 预装/白名单） · 8.3 自定义 API |
| 9.x 进程沙箱（3） | 9.1 进程模型真相 · 9.2 沙箱 · 9.3 孵化与命令行注入 |
| 10.x mojo（3） | 10.1 入门 · 10.2 加服务实战 · 10.3 服务化版图 |
| 11.x 存储（3） | 11.1 Profile · 11.2 pref · 11.3 存储与隐私 |
| 12.x AI（4） | 12.1 注入全景 · 12.2 内容管线 · 12.3 面板 UI · 12.4 内置 AI 换芯 |

## 全库高频勘误速查（18 组，均 file:line 实证，详见各篇⑥）

| 过时认知 | 现实（本库实证） |
|---|---|
| OverrideWebkitPrefs | **OverrideWebPreferences**（blink::web_pref） |
| RegisterNonNetworkNavigationURLLoaderFactories | 不存在；Create（:1811）与 Register 三件套（:1824/36/47）两族 |
| chrome:// 页面在工厂 if-chain 注册 | **WebUIConfig 体系**（chrome_web_ui_configs.cc:254） |
| ChromeApplication.java | **SplitChromeApplication**+Impl 反射委托 |
| RunNamedProcessTypeMain | **RunProcess**（std::variant） |
| ninja 主构建 | **Siso**（docs 明示） |
| tools/gn/tutorial 教程 | roll 桩；真身 gn.googlesource.com |
| BrowserFrame 类 | **已删除**（BrowserWidget+FrameView 接管） |
| browser_navigator.cc 在 ui/ 根 | 已搬 **ui/navigator/** |
| pref 走 mojo 独立服务 | **Preference Service 已删**（README 自证） |
| --ignore-certificate-errors 失效/全效之争 | **仍生效**且连 PKP 一起豁免（6.4 全链实证；6.1 初判已修正） |
| AllowCertificateError 处理拦截页 | 只剩 DENY；主入口 **SSLErrorNavigationThrottle** |
| ServiceManager 注册服务 | 时代 API 已删；正门=**ServiceProcessHost::Launch**（:197） |
| RenderWidget/RenderWidgetCompositor | **已删除**并入 blink（LayerTreeView/WidgetBase） |
| WebFrame::ContentAsText | **WebFrameContentDumper::DumpFrameTreeAsText**（:40） |
| 扩展 schema=JSON | **向 WebIDL 迁移中**（新 API 写 .webidl） |
| SystemNetworkDelegate 实例注入 | 退化为**静态工具类** |
| 证书查看器 chrome://view-cert | view-cert（新）+ policy 模板迁 policies.yaml |

**发行版加分项**：`_api_features.override.json`（8.3）与 blink `override_generated.runtime_enabled_features.json5`（13.1）是官方为 downstream fork 预留的覆盖通道（rebase 零冲突）。

## 二期新增勘误（6 组）

| 过时认知 | 现实（本库实证） |
|---|---|
| public/web 分 stable/unstable 目录 | 无此分法，稳定度在 runtime flag status |
| v8_initializer.cc:1072（gin） | 实指 **blink 侧**同名文件（gin 仅 685 行） |
| bindings=Jinja+idl_compiler.py | **已死**→pickle 数据库+code_node+11 并行 action |
| IDLExtendedAttributes.txt | 已不存在→validator/rules/supported_extended_attributes.py |
| ScriptController::ExecuteScriptInWorld | 已重构→PausableScriptExecutor+ClassicScript |
| ExecuteJavaScript 在 web_contents.h | 已迁 **render_frame_host.h:611+** |

## 三期新增勘误（7 组）

| 过时认知 | 现实（本库实证） |
|---|---|
| media/blink/ 目录 | 已拆迁至 **blink/renderer/platform/media**（README 过时） |
| CDM 在 GPU 进程 | **独立 CDM 服务进程**（cdm_type+profile+site 三元组隔离） |
| FFmpeg 软解全格式 | 现仅 **H.264**（ffmpeg_video_decoder.cc:121 原注释） |
| Linux 硬解 10bit | GL 路径**结构性降 8bit**（gpu_mojo_media_client_linux TODO） |
| RenderFrameHost::ExecuteJavaScript 通用 | **仅限 chrome:// 与 devtools://**（render_frame_host.h:617） |
| navigator.webdriver 反映远程调试 | 只看 **AutomationControlled/Emulation 覆盖**（navigator.cc:84-90） |
| --headless=old | **M132 已死**，迁移 chrome-headless-shell |

## 规模统计

- 41 篇（40 文件+1 merged），约 30 万字符总量，全部行号抽查验证
- 10 组主题，单日 4 并发子代理+主会话第 5 线产出
- 工程档案：`/usr-data/data1/browser/chromium/customdev/`（RUNBOOK+MATRIX.tsv）

## 与既有知识库的关系

- `../onboarding/ONBOARDING.md`：全景入门（先读）
- `../explain/`：12 篇核心文件深解（机制向）
- 本系列：**定制实操向**（改哪里/怎么改/怎么验证）

## 已知边界（诚实声明）

- 本机构建链未通（googlesource/CIPD 被墙）：各篇⑦验证节的命令输出待构建打通后回填实证
- clank 内部增量不可得：Android 篇以公开代码为准，推断处显式标注
- Blink/V8 内核级深改未覆盖（本库聚焦 chrome/content/服务层定制）——需要时另立项
