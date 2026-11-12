# PR 安全审查清单（review-checklist）

> reviewer 审查 PR 时逐项核对；贡献者在 PR 模板中自查。
> 背景：插件包里的 `tools/` 与 `rails/` 是**进程内执行**的 Python 代码，
> 这是 plugin 仓相对纯文档仓的核心风险差异点。

## 一、可执行代码安全（涉及 tools/、rails/ 时必审）

1. **import 期无副作用**：模块顶层不发起网络请求、不起子进程、不写文件系统；初始化只在 `__init__` / `init()` / `invoke()` 内做。
2. **写入路径受控**：文件写入路径必须来自工具入参（如 `output_dir`）或 `get_workspace()` 会话隔离目录；禁止 `Path.cwd()` / `os.getcwd()` / 写包内路径（L1 有 AST 拦截，人工复核绕过面：动态拼接、eval、装饰器注入）。
3. **密钥零入库**：manifest 与代码中不得出现明文 token / 私钥；需要配置的能力在 README 写明环境变量约定（密钥由 jiuwenswarm 的 MCP/connector 体系管理）。
4. **依赖声明**：优先 stdlib；引入三方库必须在 PR 描述声明、README 标注，且运行时按「依赖缺失 → `success=false` + 明确错误」降级（禁止 import 失败即崩溃）。
5. **Rail 钩子最小化**：只实现需要的钩子；prompt 注入使用 `PromptSection` 且 `uninit` 时 `remove_section` 清理，避免跨会话泄漏；不得读写 `agent.rails` 或其他 Rail 实例字段。
6. **产物诚实**：拿不到真实数据时返回明确降级字段（`estimated: true` 等）；不得用 JSON/文本冒充 PPTX/DOCX/PDF 等最终产物；`success=true` 前自校验文件存在且非空。

## 二、包规范（全部 PR 适用）

7. 结构合规：`manifest.json` + `README.md` + `skills/` + `tools/` + `rails/`，id = 目录名（kebab-case），无禁止字段（`persona` / `agent_card` / `model` / `subagents` / `memories` / `rubrics` / `mcps`）。
8. 展示字段完整：`display_name` / `display_description` / `tags`(3) / `quick_inputs`(3) 全部 `{en, zh}`；`default_init_input` 与 `quick_inputs[0]` 逐字一致。
9. 路径诚实：manifest 声明的每个路径真实存在；未用段整段省略（无空数组）。
10. **1:1 不变量**：`plugins/<name>/` 内只放要分发给用户的内容；测试 / 脚本 / 文档放仓库层（`tests/plugins/<name>/`）。
11. 版本：修改包内容必须递增 `manifest.version`。

## 三、仓库一致性

12. `catalog/catalog.json` 已通过 `python scripts/catalog.py` 重新生成并提交（CI 会 `--check`）。
13. 插件 id 未与既有插件 / 主仓内置 skills 冲突；无改名（改名走 `renames.json` 流程）。
14. 新插件有 `tests/plugins/<name>/` 行为测试（纯 skill 包可豁免并说明）。

## 审查结论模板

```
- [ ] 可执行代码安全项 1-6（不涉及 tools/rails 时标注 N/A）
- [ ] 包规范项 7-11
- [ ] 仓库一致性项 12-14
- L2 热加载：reviewer 在本地 jiuwenswarm 环境执行
  python scripts/validate.py --only <name> --require-hot-load 并贴出 RESULT 行
```
