# 讲透 MATLAB R2024b Linux 安装器（REA 逆向精编）

> 生成：2026-10-19 · 方法：REA 6.5.0 + Ghidra 12.1.4（aarch64 自编译 decompiler）全静态分析
> 深报告（证据锚密集版）：/usr-data/data1/reverse/matlab-r2024b/reports/（7 份）
> 本目录为面向人的精编叙事版；所有事实与深报告一一对应。

## 这是什么

`matlab_R2024b_Linux (1).zip`（217MB）不是 MATLAB 本体，是 **R2024b Update 2 的在线安装器**：解压后 535MB/1026 文件，内含一个完整的 CEF(Chromium)+Qt5+CppMicroServices 桌面应用。运行后登录 MathWorks 账号，按授权从 mathworks.com 下载并安装产品。完整离线介质是另一形态（ISO，如同目录 18GB 的 r2019b）。

## 册目

| 册 | 内容 | 关键发现速览 |
|---|---|---|
| [01-启动链与总体架构](01-architecture.md) | install 脚本→引导→微服务容器 | 1997 年代 sh 模板活化石；46KB 主程序；ELF 自签名四节 |
| [02-微服务总线](02-microservices.md) | 64 bundle/130 组件服务图 | OSGi for C++；dev/prod 双 realm；Connector 本地 HTTP+Bayeux |
| [03-网络端点全景](03-endpoints.md) | 223 URL×5 环境 | WS_ENV/WS_REL 环境切换；DWS 签名 URL 下载协议 |
| [04-下载与包格式](04-package-format.md) | OPC 家族+AES256-GCM | schemas.mathworks.com/package/*；关系级加密；`dws.zip` 清单 |
| [05-许可与激活](05-licensing.md) | FlexLM+OLL 双轨 | lc_gethostid 设备绑定；FIK 离线工作流；学生版 svaws3 |
| [06-UI 栈与无头安装](06-ui-headless.md) | mf0+Dojo on CEF | 模型驱动 UI；cefclient/Connector 双桥；installer_input 十参数 |
| [07-五年演变对照](07-evolution.md) | R2019b ISO vs R2024b | Java/SOAP/Swing→C++/REST/Web；XOR 混淆→OPC 签名包；九不变+栈血缘+依赖图 |
| [方法论长文](METHODOLOGY.md) | 六轮逆向实录浓缩 | 六变九不变；混淆→密码学工程阶梯；七招工具箱 |

## 五分钟版结论

1. **架构**：MathWorks 把安装器做成"迷你应用服务器"——CppMicroServices(OSGi 模型) 插件总线承载 64 个服务 bundle，UI 是跑在 CEF 里的 mf0(模型驱动)+Dojo 前端，经本地 HTTP+Bayeux(CometD) 总线与后端通信。
2. **网络**：libmwflurlmanager.so 是全局 URL 注册表：30+ 服务族 × prod/stage/integ1-3 五环境 223 条端点全部内嵌；`WS_ENV`/`WS_REL` 环境变量切换。下载走 DWS 服务：服务端按 entitlement 授权返回签名 URL。
3. **包格式**：产品包 = MathWorks OPC（zip+XML，同 .docx 思路）+ **关系级 AES256-GCM 加密**（2018 cipherData schema），密钥与授权链绑定。
4. **许可**：FlexLM 内核（lc_* API、Macrovision 时代 JNI）+ OLL 在线许可 + FIK/Activation Key 双 Key；激活按 hostid 设备绑定。
5. **无头安装**：`./install -inputFile installer_input.txt`，模板十参数（destinationFolder/fileInstallationKey/agreeToLicense/licensePath/...）；注意 `improveMATLAB=yes` 是模板唯一默认启用行（遥测默认开）。
6. **安全**：二进制全家族自签名（含 RFC3161 时间戳）；风险面=环境变量端点劫持通道 + 内部拓扑泄露（integ 端点随包分发）+ ccdiag 走明文 http。

## 环境方法论（REA 复活记）

本机 Kylin aarch64 + `/usr-data/data1` noexec 挂载，三重障碍逐一破：noexec 盘构建 REA → 整仓搬 /tmp；TS 7.0.2 tsc 已原生二进制化 → 同样搬走即活；Ghidra 12.1.4 无 arm64 decompiler → **包内源码 `make install_ghidraopt ARCH_TYPE= OSDIR=linux_x86_64` 原生编译**，产物拷 `os/linux_arm_64/` 后 REA doctor 全绿。详见深报告 07。
