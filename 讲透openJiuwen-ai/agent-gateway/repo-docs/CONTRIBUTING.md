# 贡献指南

感谢你对 Agent Gateway 的关注。无论是提交 Bug、开发功能、完善文档还是补充示例，都欢迎参与。

English: [CONTRIBUTING.en.md](CONTRIBUTING.en.md)

## 行为准则

- 尊重每一位贡献者，友善交流
- Issue 和 PR 中保持客观、聚焦问题本身
- 欢迎不同水平的开发者参与，乐于帮助新人

## 提交 Issue

在 [GitCode Issues](https://gitcode.com/openJiuwen/agent-gateway/issues) 提交，并按 `.gitcode/ISSUE_TEMPLATE.*` 选择模板：

| 类型 | 说明 |
| --- | --- |
| Bug Report | 复现步骤、预期行为、实际行为、环境信息 |
| Feature Request | 使用场景、期望效果、替代方案 |
| Documentation | 文档缺失、错误或改进建议 |

Bug 报告建议包含：Gateway 版本、操作系统与 Python 版本、复现命令、相关日志（`<root>/agent/.logs/`）。

## 提交 Pull Request

1. Fork [openJiuwen/agent-gateway](https://gitcode.com/openJiuwen/agent-gateway)。
2. 从 `agent_os` 分支拉出特性分支（后续将切换到 `develop`）：

```bash
git checkout -b feature/your-feature-name origin/agent_os
```

3. 完成修改并本地验证：

```bash
uv sync
./run_tests.sh -u          # 单元测试
bash scripts/build.sh      # 需要时验证打包
```

4. 使用约定式提交并携带 sign-off：

```bash
git commit -s -m "feat(gateway): add xxx"
```

5. 推送分支并创建 PR，按 `.gitcode/PULL_REQUEST_TEMPLATE.md` 填写问题、变更与测试结果。

## 分支与提交规范

- 分支名：`feature/<name>`、`fix/<name>`、`docs/<name>`、`chore/<name>`
- 提交信息：[Conventional Commits](https://www.conventionalcommits.org/zh-hans/v1.0.0/)，格式 `<type>(<scope>): <summary>`
- 常用 type：`feat`、`fix`、`docs`、`refactor`、`test`、`chore`
- 一个 PR 只做一件事，避免混入无关格式化或重构

## 代码规范

- Python 遵循 PEP 8，使用类型注解；保持修改处的现有风格
- 新增测试放在 `tests/unit_tests/`，文件命名 `test_*.py`，函数命名 `test_*`
- 新增 Python 文件应包含版权与许可头（与仓内现有文件保持一致）
- 不提交 `.venv/`、`build/`、`dist/`、覆盖率产物、日志或真实密钥

## 文档要求

功能 PR 必须同步更新文档：

- 中文为权威源：`docs/zh/`；英文跟随：`docs/en/`，两份结构对称
- 按 Diátaxis 四类归位：`tutorial/`、`how-to/`、`reference/`、`explanation/`
- Tutorial 使用 `01-`、`02-` 数字前缀；其余类别使用 kebab-case 语义名，不编号
- 新增示例放入 `examples/<name>/`，并提供 README（运行命令、预期输出）
- 更新 `docs/README.md` 与 `docs/README_EN.md` 的导航链接

## 审查与合入

- PR 需要至少一名 Committer 审查通过
- 审查问题全部解决后方可合入
- 禁止合入自己创建的 PR
- 合入前确保关联流水线与测试通过

## 社区规范

提交代码即表示你同意以 [Apache License 2.0](LICENSE) 授权你的贡献。请同时遵守：

- [openJiuwen 贡献指南](https://gitcode.com/openJiuwen/community/blob/main/CONTRIBUTING_zh.md)
- [许可证与版权规范](https://gitcode.com/openjiuwen/community/tree/main/contribute/许可证与版权规范.md)
- [社区行为准则](https://gitcode.com/openJiuwen/community/blob/main/openJiuwen社区行为准则.md)
