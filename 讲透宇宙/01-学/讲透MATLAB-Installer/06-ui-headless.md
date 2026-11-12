# 06 · UI 栈与无头安装

## 前端栈

`ui/install/product_installer_ui/`：**mf0（MathWorks "mf::zero" 框架）+ Dojo Toolkit 1.x**，webpack 单文件 bundle.index.js 2.2MB + contenthash 资产 + AMD i18n（en/zh-cn/ja-jp/ko-kr/es 五语）。

mf0 是**模型驱动 UI**：后端 `mwinstall_datamodels_*_ms_gen.so` 生成数据模型 → MetamodelLoader 加载 → UI 按模型自动渲染（元 schema：`schema.mathworks.com/mf0/`）。向导每屏是模型实例，不是硬编码页面——这就是 MathWorks 安装器、MATLAB Desktop Online 共用的前端底座。

## UI ↔ C++ 双桥

**通道 A `window.cefclient`（窗口旁路）**——bundle 实测调用面：
- `sendMessage("close" | "openFolder" [path] | "restore" | "bringToFront" | "js-custom-close-set")`
- `removeMessageCallback` / `handleWindowClosed`
- 特性检测 `isCefClient()`：无 CEF 时降级纯浏览器行为（window.close）

**通道 B Connector 本地总线**——本地 HttpServer（**Poco C++ Libraries** 栈）+ **Bayeux(CometD) 长轮询**推送 + ContainerDispatcher(v1) 分发 + NonceService 防重放。CEF 前端本质是本地 Web 应用的客户端。安全细节（反编译实证）：仅绑定 **https://localhost** 双端口窗（正则 `^https://localhost:31[56][0-9]{2}$` 与 `^https://localhost:2718[0-9]$`，27180 段是 MATLAB Connector 知名段）；`PocoHttpServer::getNextPort` 用 **random_device 在窗口内随机挑端口**（防本地抢注）；过滤器族 HttpLocalHostFilter/OriginFilter/**FevalAllowlistFilter**（远程 eval 白名单）+ HSTS；鉴权路由 `connector/v1/httpNonce` + `connector/http/session`。

**Catapult 协议**：cefcatapultmessageprotocol.so 承载 CEF 外进程窗口控制（webwindowManager_extprocess）。

渲染兜底：无 GPU 机器走 SwiftShader（libvk_swiftshader/libEGL/libGLESv2）；无显示器走 sys/Xvfb + fluxbox 自造显示层。

## 向导步骤流（resources XML key 考古）

```
登录(authenticationHeader)
 → 许可选择（excessEntitlementsWarning 多授权警告）
 → 工作流四选一（标准在线/Activation Key/FIK/网络许可管理器，05 册）
 → 目标目录（destinationFolderTitle；12 个 folder* 校验：非绝对路径/是安装器根/无写权限/非英文字符/尾点...）
 → 产品选择（additionalProducts*；controllingProductConflict）
 → 下载（downloadTitle→downloadCompleted）→ 解压（ExtractError*）
 → 激活（activateNow/activateLater）
```
另有 EZDeploy 简易部署流与 Runtime 已装检测（alreadyHasRuntimeMsg / alreadyHasPrereleaseRuntimeMsg）。

## 无头安装（headless）

```bash
./install -inputFile my_input.txt
```

参数全集（模板原文键）：
```
destinationFolder=      目标目录
fileInstallationKey=    FIK 离线 Key
agreeToLicense=yes      接受 EULA
licensePath=            license 文件
outputFile=             输出
enableLNU=              License Network Utility
desktopShortcut= startMenuShortcut= setFileAssoc=   桌面集成
createAccelTask=        加速任务（win）
improveMATLAB=yes       ⚠ 模板唯一默认启用行 = 遥测默认开
```

**合规提醒**：无人值守装机默认上报遥测（DDUX/UDC/usagedataws/ccdiag 四路），敏感环境应显式 `improveMATLAB=no`。

## 遥测矩阵（UI 侧）

埋点模板 `pi_{doconline,dlerr,icerr,miferr,mpi_macajre,mri_macajre,unc}_mpi_${0}_${1}`——帮助/下载错误/安装错误/JRE 问题/未分类，六类上报 www.mathworks.com。
