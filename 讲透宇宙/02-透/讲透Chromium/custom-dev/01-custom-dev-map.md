# 01 · Chromium 定制开发全景地图（本系列总览）

> 定制开发 Chromium / 自制浏览器，第一步不是读代码，是**选路线**。本文给出路线决策地图 + 全系列导航。
> 基线：chromium/chromium @8fe2331（2026-10 main）。

## 一、三条定制路线（先选对，再动手）

| 路线 | 做法 | 适合 | 成本量级 | 本系列覆盖 |
|---|---|---|---|---|
| **A. 发行版定制** | 在完整 chrome/ 层上改：品牌、默认行为、裁剪服务、加功能 | 企业内网浏览器、区域化产品、AI 浏览器（改壳为主） | 中（一次编译跑通后，每次改动可控） | 1.x/3.x/4.x/5.x + 6.x-12.x |
| **B. Content 层自制** | 只用 content/public 嵌入契约自建浏览器壳（官方支持面） | 极简浏览器、特殊用途壳（kiosk/采集/内嵌面板） | 中高（要自己实现 UI/下载/书签等全部产品功能） | 2.x 全组（shell/headless/webview 四范例） |
| **C. 外挂式** | CEF / Electron / WebView（不编 Chromium 源码） | 桌面应用内嵌网页 | 低（但不改引擎行为，不在本系列主线） | 仅参照对照 |

**决策要点**：
- 只想改"浏览器产品行为"（首页/搜索/默认设置/UI/加 AI 侧栏）→ 路线 A，入口在 chrome/ 层，几乎不碰 content/
- 想要"自己的浏览器"且接受功能从简 → 路线 B，content/public/browser 的三大 Client 是全部契约面
- 两条路线都要过的第一关：**把源码编出来**（1.1/1.3），这是所有资料缺失的根源——本文库用源码实证补齐

## 二、代码地图：定制者视角的分层

（图谱 16 层的定制热力版；🔥=定制高频层）

```
chrome/          🔥🔥🔥 发行版定制主战场（Browser/UI/品牌/服务绑定/策略）
extensions/      🔥 扩展系统（加载策略/白名单/预装扩展）
content/         🔥🔥 自制浏览器的契约层（public/=嵌入面，browser/renderer=实现）
android_webview/ + chrome/android  🔥🔥 Android 形态（webview 嵌入 / clank 完整浏览器）
ui/ (views/aura/ozone/webui)  🔥🔥 UI 三选一：views 原生 / WebUI 网页 / Android Java
cc/ viz/ gpu/    渲染管线（注入截图/水印/视频处理的切入点）
net/ services/network  🔥 网络定制（代理/证书/拦截/DNS）
mojo/ ipc/       服务化 IPC（加自定义服务接口）
sandbox/ base/   地基（进程模型/线程/平台抽象，5.1）
blink(third_party) V8   引擎内核（一般不碰，除非改 Web 标准行为）
```

**读文件的后缀语法**（平台差异第一课）：`*_android.cc` / `*_linux.cc` / `*_mac.mm` / `*_win.cc` / `*_ozone.cc` 是同名逻辑的平台实现，BUILD.gn 的 `sources` 里按平台条件过滤链接（详见 5.1）。

## 三、系列导航（随产出更新）

| 组 | 篇目 | 解决什么 |
|---|---|---|
| 1 构建系统 | 1.1 总流程 · 1.2 GN 深解 · 1.3 args 矩阵 · 1.4 品牌打包 | 把源码变成可运行产物 |
| 2 Content API | 2.1 三大 Client · 2.2 嵌入范例对比 · 2.3 WebContents/导航 | 路线 B 的全部知识 |
| 3 启动+品牌 | 3.1 桌面启动链 · 3.2 Android 启动链 · 3.3 品牌定制/去 Google 化 | 路线 A 第一批实操 |
| 4 UI+WebUI | 4.1 views · 4.2 WebUI/自建页面 · 4.3 窗口结构 | 产品级 UI 定制 |
| 5 平台差异 | 5.1 平台抽象 · 5.2 Android×Linux · 5.3 分发 | 多平台维护 |
| 6-12（规划） | 网络/渲染注入/扩展/沙箱/mojo/存储/AI 集成 | 深度定制专题 |

## 四、定制开发者的最小闭环（先跑通这个）

1. 编译出 chrome（1.1）→ 2. 改个名字/图标跑起来（3.3）→ 3. about:flags 加一个自己的 flag 或加一个 chrome:// 页面（4.2）→ 4. 改一个启动行为（3.1 找挂点）→ 5. 拦一个网络请求（6.x）
每一步都是"改→编→验证"闭环，跑通即入门。

## 五、诚实声明

- 本机源码链路：googlesource/CIPD 被墙，源码来自 GitHub 官方镜像 chromium/chromium；**构建实操（gn gen/ninja）尚未在本机跑通**，涉及命令输出的一律标注"据源码/文档推断，待本机构建验证"。
- clank（Chrome on Android 的 Google 内部增量仓）目录为空：Android 篇以 chrome/android + android_webview 公开代码为准，内部结构推断处显式标注。
