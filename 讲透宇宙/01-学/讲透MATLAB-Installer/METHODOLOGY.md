# 商业软件分发架构的五年演变 —— MATLAB 安装器逆向实录（2019b → 2024b）

> 2026-10-19 · 基于六轮静态逆向：MATLAB R2024b 在线安装器（217MB zip，R2024b Update 2）与 MATLAB R2019b 离线介质（18GB ISO）双侧全谱分析。
> 工具：REA 6.5.0 + Ghidra 12.1.4（aarch64 自编译 decompiler）+ binutils + javap + qemu-x86_64-static。
> 证据锚齐全版：`/usr-data/data1/reverse/matlab-r2024b/reports/`（9 份深报告）。

## 摘要

把一个商业安装器从头到尾拆开能看到什么？本文拆解了 MathWorks 两代安装器，得到了一个完整的"商业软件分发架构五年演变"样本：**2019→2024，MathWorks 把 Java/SOAP/Swing/混淆包裹的单体安装器，重写为 C++/REST/Web/签名容器的微服务安装器；而商业语义层（entitlement 数据模型、FIK 工作流、FlexLM 部署形态）一行未动**。重构发生在"怎么分发与验证"，不触碰"卖什么与怎么授权"——这是商业系统重构纪律的教科书样本。

## 一、两代架构一图流

```
R2019b（离线 ISO 18GB）                    R2024b（在线安装器 217MB）
─────────────────────────                  ─────────────────────────
install(sh, 1997 模板)                      install(sh, 同一 1997 模板)
 └ install_unix(sh)                         └ MathWorksProductInstaller(46KB ELF)
    └ java -jar install.jar                 └ libmwcommonproductinstalldriver
       (自带 JRE 1.8.0_202, 17 jar)            └ CppMicroServices 容器
          Swing 向导                            ├ 64 bundle / 130 SCR 组件
          Apache Axis SOAP 客户端               ├ CEF(Chromium)+mf0 模型驱动 UI
          9 个原生辅助 so                       ├ Connector 本地 HTTP+Bayeux 总线
                                                └ 223 URL 注册表×5 环境
产品档案: .enc = zip XOR {1a,1b,1c,1d}     组件包: .enc = OPC+XML-DSig+AES-GCM
FlexNet 11.16.2.1 (x64_lsb)                FlexNet 11.19.5.0 (x64_linux)
```

## 二、六个"变"与九个"不变"

**变（工程层全部重做）**：介质（全量 ISO→云端按需）· 语言（Java→C++）· UI（Swing→CEF Web）· 服务协议（Axis SOAP→REST）· 包格式（XOR 混淆→签名+加密分离）· 安全治理（散落 http→集中注册表 https+五环境）。

**不变（商业语义层）**：① install 脚本 1997 模板逐字同源；② VersionInfo.xml 结构；③ installer_input 参数命名族；④ entitlement 数据模型（2019 的 `getEntitlementByActivationKey` → 2024 的 entitlementId 贯穿下载/许可/包密钥全链）；⑤ FlexLM 三件套（lmgrd/lmutil/MLM）；⑥ `.enc` 扩展名（同名异构）；⑦ Dojo（从局部公式渲染升为全站栈，最长寿前端资产）；⑧ `MW_*_SERVICE` 端点 override 键族（2019 环境变量→2024 UrlManager 同名连续）；⑨ 档案 entry 语义（`_common.xml`/`mwcontents_` 前缀）。

**为什么这样重构**：能从证据直接读出三条动机——离线 ISO→云分发的成本结构变化；供应链安全标准升级（混淆不满足合规，签名+加密分离才满足）；UI 跨产品线统一（安装器与 MATLAB Online 共用 mf0 栈）。而 entitlement/FlexLM/FIK 不动，因为它们是收入语义，动它们的风险与收益不成比例。

## 三、供应链安全的"混淆→密码学工程"阶梯

这个样本最有教学价值的是包格式演变：

1. **R2019b：混淆层**。`.enc` = 标准 zip 做循环 XOR，静态密钥 4 字节 `TMWkey={0x1a,0x1b,0x1c,0x1d}`（从安装器 jar 反编译 `DecodeInputStream` 字节码钉版；对 ISO 全部 3,005 个档案 100% 有效）。防顺手解包，不防认真的人——18GB 介质实质明文。
2. **R2024b：密码学工程**。OPC 标准容器（zip+XML）+ XML-DSig 独立签名（不 解密也能验完整性）+ 关系级 AES256-GCM（按 RelationshipSelector 选择性加密；密钥由授权链供给，包内零静态密钥）。签名与加密职责分离是现代供应链安全的核心模式。
3. **教训**：高熵 ≠ 加密（deflate 压缩流同样高熵——先试已知容器 magic 的 XOR 再谈密码分析）；**逆向先找解密器代码再破译密文**（jar 字节码比 hex 分析快一个量级）。

## 四、微服务安装器：OSGi for C++

2024b 安装器是"迷你应用服务器"：CppMicroServices 3.8.3 复刻 Eclipse OSGi/SCR 模型，64 个 bundle（每 so 内嵌 manifest.zip 自描述+独立签名）、130 个服务组件按接口注入。分域清晰：foundation（网络）/ install（安装域）/ connector（本地 Web 总线）/ cef_services（前端宿主）/ mf0（模型驱动 UI）/ licensing。

**UI 是本地 Web 应用**：CEF 前端经 Connector 的本地 HttpServer+Bayeux(CometD) 总线与后端通信——仅绑 `https://localhost` 双端口窗（31500-31699/27180-27189），random_device 窗口内随机挑端口防抢注，NonceService 防重放，**FevalAllowlistFilter**（远程 eval 白名单）。`window.cefclient` 只是窗口控制旁路。

**栈血缘**：2024b 安装器不是凭空新写——2019b MATLAB 本体已含 `+connector/+internal/webwindowmanager.m`（JCEF 时代的 connector 命名空间）、mlconnector_bridge.jar、libmatlab_toolbox_mvm。安装器 = MATLAB Desktop 连接器生态的原生 C++ 重写，命名未变。

## 五、端点治理与安全观察

- **集中注册表**：libmwflurlmanager.so 内嵌 223 条端点×5 环境（prod/stage/integ1-3），`WS_ENV/WS_REL` 环境变量切换——内部测试拓扑随生产包分发（供应链侦察的一手材料）。
- **下载协议**：DWS 服务按 entitlement 授权返回**签名 URL**（服务端决定你能下什么、URL 防篡改），首步拉 `dws.zip` 清单。
- **防御纵深**：ELF 全家族自签名四节（certificate/cachain/signature/timestamp，RFC3161）+ TLS 双锚 + 下载签名 URL + 包级 AES-GCM。
- **风险面**：`WS_ENV/MW_DOWNLOADS_SERVICE` 环境变量是合法端点劫持通道；`ccdiag` 走明文 http；**更新安装器的签名验证锚证书 2026-05-14 已过期**（DigiCert G4 签发的 MathWorks 证书硬编码在 buildurl 模块——旧安装器的长期可维护性负债）；`improveMATLAB=yes` 是无头安装模板唯一默认启用行。

## 六、方法论工具箱（本次验证有效的招式）

1. **环境三重复活**：noexec 盘（整仓 rsync 到可执行位）→ TS 7 tsc 原生化（同为 noexec 死路）→ Ghidra 无 arm64 decompiler（**包内源码 `make install_ghidraopt ARCH_TYPE= OSDIR=linux_x86_64` 自编译**，Makefile 命令行覆盖绕过架构探测）。
2. **manifest 考古**：CppMicroServices bundle 的 so 内嵌 zip manifest——批量提取即得完整服务图（64 bundle/130 组件），比反编译快百倍。
3. **字符串→xrefs→decompile 三段论**：先 strings 拿锚点，Ghidra xrefs 定位函数，decompile 读伪代码（本次 UrlManager/端口选择/密钥链全用此法）。
4. **jar 常量池考古**：javap -c 的字节码里静态块、常量表、方法名都是明文（TMWkey 就在 static{} 的四个 bipush 里）。
5. **zip 尾部快解**：批量档案只 XOR EOCD+中央目录（O(目录) 而非 O(文件)），18GB/3,005 档案秒级扫完。
6. **qemu-user 动态验证**：`qemu-x86_64-static -L sysroot` 跑 lmgrd -v，字符串证据升级为运行时实证（2019b 的 x64_lsb 目标还揭示了 LSB→Linux 的切换）。
7. **公开性核查**：WebSearch+gh-grep 验证破译的独立性（TMWkey 无公开先例）。

## 七、结语

安装器是商业软件的"门面"，也是最完整的架构自白书：它必须诚实交代如何验证用户（licensing）、如何传输（网络端点）、如何保证完整性（包格式）、如何呈现（UI 栈）。MATLAB 这五年交出的答案是：**传输与验证全面现代化，商业语义纹丝不动**。对逆向工程者，这类"门面"产品是练手金矿——自包含、自描述（manifest/注册表齐全）、且每个防御机制都值得单独研究。

（完）
