# 05 · 许可与激活：FlexLM 与 OLL 双轨

## 三层结构

```
FlexLM 内核（libmwinstall_licensefileutility.so：lc_* C API）
   ↑ 单机/网络许可证的解析、校验、hostid
OLL 在线许可（license.xml 资源 + licensing.* 端点）
   ↑ 无本地许可文件时在线拉取；授权/用量上报
激活层（ActivationService + DeviceBasedUtils + activationws）
   ↑ hostid 设备绑定；标准/学生版双服务
```

## FlexLM 内核证据（导出符号）

`lc_gethostid / l_new_hostid / lc_free_hostid`（机器指纹）· `lc_check_key / lc_add_key_filter / l_prikey_sign`（许可文件是私钥签名授权）· `lc_install_license_path / lc_lic_where` · `lc_date_has_passed`（过期）· `la_statGetEntitlementId / la_statGetExpirationDate`（**entitlement 是一等公民**）· `Java_com_macrovision_flexlm_HostId_lGetNativeHostId`（Macrovision 时代 JNI，钉版内核渊源）。

## OLL 文案（licensing_services/license.xml）

- "No local license file found. You must be online and able to contact MathWorks servers to download a license file."
- "Unable to communicate with required MathWorks services"（授权服务不可达）
- "You are not licensed to use {0}."（release 级准入）
- 激活失败："Unable to write the required activation files to your machine."（**激活标记文件** = 装机目录内 hostid 绑定凭据）

## 用户可见的四条入口（UI 原文）

1. **标准在线**："I want to do a standard install"——登录账号 → `prodAuthOnline`（"I want to select a license"）或 `prodAuthOffline`（"I want to use a license file"）
2. **Activation Key**："An Activation Key links your MathWorks Account to a license."
3. **FIK**："A File Installation Key identifies the products you can install and allows you to install them **without an internet connection**. You must also have your license file..."——离线企业的正式路径（Key 定产品集 + license 文件给权限）
4. **网络许可证管理器**："I want to install network license manager"——部署 archives/ 里的 FlexLM 服务端三件套：**lmgrd**（FlexNet 主守护，`Copyright (c) 1988-2023 Flexera`，2023 内核/35 年血统）+ **lmutil**（lmstat/lmremove）+ **MLM**（MathWorks License Manager vendor daemon，自研；内嵌 V7.1/V8.0/V8.1 LM_KEY/LM_SIGN 协议兼容矩阵）

彩蛋：学生版分流按钮内部键名 `guiltForwardButtonLabel`（显示文案 "I am a student"）→ svaws3 StudentVersionActivation。

## 服务端点（prod）

`licensing.mathworks.com/mls/service/v1` · `licensing.../authorization/user` · `licensing.../usage/log` · `services.mathworks.com/activationws` · `services.../svaws3/services/StudentVersionActivation`

## 装机后的许可工具（controllingProduct.json）

Linux：`bin/glnxa64/MathWorksProductAuthorizer.sh`（激活）/ `MathWorksLicenseDeactivation`（去激活）；MATLAB 家族建 `matlab`/`mex` 符号链接；LNU（enableLNU 参数）与 License Center 深链 `www.mathworks.com/licensecenter/links/setupmdcs`。

## 要点

- 双轨并存是历史包袱也是企业刚需：账号制（个人/教育）与 FlexLM（企业浮动/网络）各服务一类客户。
- FIK 是**官方离线通道**，不是破解后门；绕过 `lc_check_key/l_prikey_sign` 验证违反 EULA，本文档不涉及。
- entitlementId 贯穿全链：DWS 下载参数、MLS 授权、la_stat 查询、OPC 包密钥派生——**一条 entitlement 轴串起"你能装什么、能下什么、包解得开什么"**。
