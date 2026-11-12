# 安全策略

## 支持范围

安全修复面向最新发布版本。请在报告中注明 Gateway 版本（见 `pyproject.toml`）与运行环境。

## 报告漏洞

请勿在公开 Issue 中披露漏洞细节。推荐方式：

1. 在 [agent-gateway Issues](https://gitcode.com/openJiuwen/agent-gateway/issues) 创建**私有** Issue，并标记为安全问题；或
2. 按 [openJiuwen 社区安全漏洞治理及披露](https://gitcode.com/openjiuwen/community/tree/main/contribute/社区安全漏洞治理及披露.md) 中的渠道联系社区安全响应工作组。

报告建议包含：

- 受影响的版本与部署方式
- 复现步骤或 PoC
- 影响评估（信息泄露、权限绕过、拒绝服务等）
- 已知的缓解措施

请勿在报告中包含真实用户数据、生产环境凭据或第三方系统的敏感信息。

## 处理流程

社区安全响应工作组会验证问题、评估 CVSS 等级、组织修复，并在修复后按负责任的披露原则发布安全公告。详见：

- [社区安全漏洞治理及披露](https://gitcode.com/openjiuwen/community/tree/main/contribute/社区安全漏洞治理及披露.md)
- [安全公告](https://gitcode.com/openjiuwen/community/tree/main/security/disclosure.md)
- [网络安全事件管理](https://gitcode.com/openjiuwen/community/tree/main/contribute/网络安全事件管理.md)

## 安全设计

Gateway 侧的安全设计（Origin 校验、`user_id` 白名单、认证键清洗、工作区隔离等）见[架构说明](docs/zh/explanation/architecture.md)与 [openJiuwen 安全设计规范](https://gitcode.com/openJiuwen/community/tree/main/contribute/style-guide/openJiuwen-security-design-guide.md)。
