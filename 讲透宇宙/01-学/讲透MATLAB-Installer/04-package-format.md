# 04 · 下载与包格式：MathWorks OPC + AES256-GCM

## 安装源抽象

`install::repository_adapter::RepositoryAdapter` 一个接口三个实现 bundle：
- **folder**：本地目录即安装源（离线介质/已下载包）
- **online_product**：在线产品仓库（DWS 协议，03 册）
- **online_supportpackage**：支持包仓库（addons.mathworks.com/registry/v1）

三条产品线（在线装/离线装/补支持包）共享同一安装引擎——适配器模式的教科书用法。

## MathWorks 包格式 = OPC 变体

`libmwopcmwservices.so`（+opccore/opcmodel）实现 OPC（Open Packaging Conventions，.docx/.msi 同族）。内嵌四个私有 schema：

```
schemas.mathworks.com/package/2012/coreProperties      包核心属性
schemas.mathworks.com/package/2013/filesystemManifest  文件系统清单
schemas.mathworks.com/package/2018/cipherData          加密数据条目
schemas.mathworks.com/matlab/compiler/2011/fileManifest 编译产物清单（.ctf 家族）
```

内容类型约定：`application/vnd.mathworks.<product>.<package-type>`（vendor MIME 树）。

## 关系级加密（2018 cipherData）

运行时文案钉版语义：
- `No cipher data found for the given RelationshipSelector.` —— 加密条目按 **RelationshipSelector**（OPC 关系粒度）挂载
- `Unable to create cipher entry. This is likely because the relationshipSelector is already present.` —— 每关系至多一条
- 算法字符串：**AES256-GCM**；密码学栈 `libmwflcrypto → flcryptoutils → flcryptocryptopp`（Crypto++）

即：**包 = OPC zip 容器，包内每个"关系"可独立 AES-256-GCM 加密**，密钥与授权（entitlement）链路派生。公开的 `.mltbx` 是此格式无加密子集；`.ctf` 是 2011 清单一支；安装器下载的产品档案是加密超集。

## 下载-解包链

```
DWSClient（拉 dws.zip 清单 + 签名 URL）
  → Downloader（重试/代理/超时，foundation httpclient_core）
  → 落盘 → libarchive 13.7.5 解包
  → extract_product_files_from_iso（独立 ELF，从 ISO 介质抽产品文件——18GB r2019b ISO 的离线路径）
```

## 网络许可证管理器

`archives/Network_License_Manager242_{common,glnxa64}.zip` 是 FlexLM 服务端独立 payload（"安装网络许可证管理器"工作流部署它），详见 05 册。

## 未解之点（二轮已全部破解）

- buildurl 内 Base64 大块（0x38004-0x386c6，1,278 字节）= **MathWorks 代码签名证书 PEM**（DigiCert G4 签发，2023-05-15~2026-05-14）——用于"下载更新安装器"的签名验证锚。⚠ **证书 2026-05 已过期**：要么更新安装器路径自然失效，要么验证忽略有效期。
- **OPC 实证**：Network_License_Manager 的 payload 本身就是 OPC 包（`[Content_Types].xml` + `_xmlsignatures/sig1.xml` XML-DSig + `metadata/mwcoreProperties*.xml` + `fsroot/` 载荷 zip 内 zip）；安装器全部组件（gcc_runtime/shim/flexnet）都走此格式。
- **密钥链闭环**：`CipherEntry(RelationshipSelector, key, "AES256-GCM", IV)`——密钥是调用方传入的裸字节，**包内零静态密钥**（entitlement/会话层供给）；密码学栈 flcrypto 抽象层 + openssl/cryptopp 双后端。
