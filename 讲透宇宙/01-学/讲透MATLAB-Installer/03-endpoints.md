# 03 · 网络端点全景：223 条 URL 的注册表

## 发现方式

`libmwflurlmanager.so`（287KB）是全局 URL 注册表：**30+ 服务族 × 5 环境（prod/stage/integ1/integ2/integ3）共 223 条端点全部硬编码在字符串表**（`strings -n 10 | grep '^https*://'` 一发命中，原始清单存 url_registry_raw.txt）。

## 环境切换机制（反编译实证）

```c
env = getenv("WS_ENV");    // prod(默认)/stage/integ/dev 变体
rel = getenv("WS_REL");    // 默认 "R2024b"
createUrlManager(env, rel, overrides, HonourEnvironmentVariableOverrides);
// 未覆盖时日志："UrlManager: No endpoint overrides for <svc>"
```

配置 PID `mw.UrlManager` 同样可改端点。`MW_DOWNLOADS_SERVICE` 专管下载服务基址。

## prod 端点地图（按用途归组）

**身份与许可**
- `login.mathworks.com`：`loginws2/services/Login`（SOAP）· `authenticationws/service` · `embedded-login/login.html`（**安装器内嵌登录页**，凭据在官方域内完成）
- `licensing.mathworks.com`：`mls/service/v1`（MLS 许可服务）· `authorization/user` · `usage/log`
- `services.mathworks.com/activationws`（激活）· `svaws3/services/StudentVersionActivation`（学生版）

**下载与内容**
- `dws.mathworks.com/dws`（+`/service/v1/mci`、`/service/v2/ssi`、`/mcrdws`）· `services.../daws` · `gds.mathworks.com/gds/` + `gds-jobs.../jobs/`
- `services.mathworks.com/contentservice` · `cws.mathworks.com/contentservice` · `addons.mathworks.com/registry/v1`（支持包）

**遥测与诊断**
- `udc-service.mathworks.com/udc/service(/v1)` + `dduxws/service/v1` · `www.mathworks.com/usagedataws/services/UsageDataService` · `services.../segv/services/SegvService`（崩溃上报）· `ccdiag.mathworks.com`（**明文 http**）
- UI 埋点模板：`www.mathworks.com/pi_{doconline,dlerr,icerr,miferr,...}_mpi_${0}_${1}`

**云产品与消息**
- `matlab/simulink/cloudcenter(-services)/drive/ssd/ai/matlabacademy.mathworks.com`
- `notifications.mathworks.com/notifications` · `authnz.mathworks.com/messages/json` · `apsauthnz.mss-mathworks.com/messages/json` + `apsbroker.mss-mathworks.com/stream`（**独立域 mss-mathworks.com**）

## DWS 下载协议

调用链 `OnlineProductRepoAdapter::download → DWSClient → Downloader → BuildURL`：
1. 请求头 `x-mw-request-id`（幂等）；参数 `includeEntitledProducts / releaseFamily / releasePhase / entitlementId / supportPackageReleaseIds`——**授权感知**：服务端按你的 license 决定可见产品
2. 先下 **`dws.zip`**（产品清单+布局）
3. 产品档案 URL 由服务端**签名分发**（`urlSigning`）——CDN 直下，客户端不拼 URL
4. 异常族 11 个（含 ProxyAuthenticationRequired → UI 代理凭据对话框）；downloader 内建重试

## 传输与代理

libcrypto-mw(OpenSSL 3) + 内嵌 .cachain 根锚 + DigiCert 时间戳链；ProxySelector 服务自动探测系统代理，407 时 UI 收集凭据。

## 安全含义

- **内部拓扑全泄露**：integ1/2/3 + stage 全套端点随生产包分发，`ssd-internal.mathworks.com` 也在——供应链侦察的一手材料（本清单即证）。
- `WS_ENV/WS_REL/MW_DOWNLOADS_SERVICE` 是合法端点劫持通道——共享机器/CI 场景的注入面。
- 防御闭环靠签名 URL + OPC 包加密（04 册）：改了端点拿不到可解密的包。
