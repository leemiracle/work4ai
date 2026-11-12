# 01 · 启动链与总体架构

## 包身份

- `matlab_R2024b_Linux (1).zip`：217MB 压缩 / 557MB 展开 / 1026 文件 = **在线安装器**
- `VersionInfo.xml`：R2024b **Update 2**，版本 24.2.0.2773142，2024-10-22
- 不是 MATLAB 本体；装完的产品在 `~/MATLAB/R2024b`（由 controllingProduct.json 定义布局：`MATLAB` 目录、bin/matlab 启动、matlab/mex 符号链接）

## 三级启动链

```
install (11KB POSIX sh)
  └─ 判 ARCH（uname -m：x86_64→glnxa64 / aarch64→linux-arm-64）
  └─ 按存在性四选一：MathWorksProductInstaller / MATLABRuntimeInstaller / install_unix / install_unix_legacy
  └─ RHEL7/CentOS7 (glibc 2.17) 时 LD_PRELOAD glibc-2.17_shim.so
  └─ exec bin/glnxa64/MathWorksProductInstaller "$@"
       └─ (46KB ELF, main 在 Driver.cpp) → libmwcommonproductinstalldriver.so
            └─ CppMicroServices 容器加载 64 bundle（业务全在插件）
```

**1997 年代活化石**：install 脚本内嵌 `archlist_template.sh`/`arch_template.sh` 两段，注释自标模板边界、版权头 1997-2016——27 年骨架未换。macOS 段还有 Rosetta 检测（bin/maci64 与 bin/maca64 共存时选 native）。

## 主程序为何只有 46KB

`.text` 仅 8.8KB / 258 函数：它只做引导 + 自验证。真正的安装逻辑分布在 `bin/glnxa64/` 的插件树（`foundation/`、`install_plugins/`、`cef_services/`、`activation/`、`agent/`、`connector_plugins/`...见 02 册）。

## 自定义 ELF 签名节

主程序（及全部 libmw*.so）带四个 MathWorks 自定义节：

| 节 | 内容 |
|---|---|
| `.certificate` | 自身签名证书 |
| `.cachain` | PEM 证书链 |
| `.signature` | 签名值 |
| `.timestamp` | RFC3161 时间戳 |

证书主题统一 `C=US, ST=Massachusetts, L=Natick, O="The MathWorks, Inc."`。第三方链锚定 DigiCert（ocsp/crl3/cacerts.digicert.com 内嵌各业务 so）。

## 目录地图（installer/）

```
install                    启动脚本
installer_input.txt        无头安装参数模板（06 册）
VersionInfo.xml readme.txt license_agreement.txt  身份与法律
bin/
  ProductData.json         全产品清单（basecode/number）
  controllingProduct.json  产品家族布局（ML/Runtime/DW/PR/MW/Polyspace×4）
  glnxa64/                 672 文件：全部 ELF（见 02/03 册）
  icutzdata/ lcdata*.xml   ICU 时区与 locale 数据
ui/install/product_installer_ui/   Web 前端（06 册）
resources/                 licensing_services/scl/product_installer/multimedia/registration/mf0/...
archives/                  Network_License_Manager242_{common,glnxa64}.zip（05 册）
sys/                       Xvfb + fluxbox + os 兜底库（无头图形）
cefclient/sys/             CEF 客户端 OS 兜底（gtk2 等）
```

## 第三方栈版本（strings 考古）

CEF(libcef.so 199MB) · Qt 5.15.16 · Boost 1.81.0（MathWorks 自带）· OpenSSL 3(libcrypto-mw) · ICU 72.1 · xerces-c 3.2 · protobuf 3.21.9 · libarchive 13.7.5 · avrocpp 1.11.1 · libcurl · Crypto++(cryptopp)
内部构建路径泄露：`/mathworks/hub/3rdparty/R2024b/11242549/`（build 号 11242549）
