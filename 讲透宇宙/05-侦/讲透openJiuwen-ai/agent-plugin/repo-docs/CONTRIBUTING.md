# 贡献指南（CONTRIBUTING）

感谢为 JiuwenSwarm 插件生态做贡献！请先阅读 [插件包规范](./docs/plugin-spec.md)
与 [仓库结构设计](./docs/design/repo-structure-design.md)，再按以下流程操作。

## 贡献流程

```bash
# 1. 初始化骨架（组件可选；--skill/--tool/--rail 传 kebab-case 名称）
python scripts/init.py my-plugin --skill usage-guide --tool counter

# 2. 填充内容
#    - manifest.json / README.md：消灭全部 [TODO]（L0 校验会拦截残留）
#    - skills/<name>/SKILL.md：frontmatter name = 目录名；正文精简可操作
#    - tools/<name>_tool.py / rails/<name>_rail.py：遵守规范 §4 / §5
#    - 行为测试：tests/plugins/my-plugin/test_*.py

# 3. 本地校验（PR 质量门禁的本地等价物）
python scripts/validate.py --only my-plugin                    # 默认含 L2；需 jiuwenswarm 运行环境（缺环境则 PARTIAL）
python scripts/catalog.py                                # 生成 catalog 并同步 README 表格
pytest                                                   # 工具链与插件测试

# 4. 提 PR
#    PR 模板含安全审查自查项（针对 tools/rails 可执行代码），reviewer 按
#    docs/review-checklist.md 审查
```

## 硬性规则

1. **命名**：插件 id = 目录名 = `manifest.id`，kebab-case，发布后**不可变**；改名走「新建插件 + `renames.json` 登记」。
2. **1:1 不变量**：`plugins/<name>/` 内只放要分发给用户的内容；测试、脚本、文档放仓库层。
3. **能力声明诚实**：`skills` / `tools` / `rails` 至少声明一类；没有的整段省略，禁止空数组、禁止声明不存在的路径。
4. **版本**：修改包内容必须递增 `manifest.version`。
5. **展示字段双语**：`display_name` / `display_description` / `tags` / `quick_inputs` 一律 `{en, zh}`；`default_init_input` 与 `quick_inputs[0]` 逐字一致。
6. **一个插件一个场景**：细粒度小插件优于大杂烩（渐进披露控制 token 成本）。

## PR 质量门禁

PR 会自动运行 `.github/workflows/pr-quality.yml`：

- **L0/L1 校验**（必须全绿）：规范质量 + 静态结构（AST 级 tool/rail 检查）
- **catalog 一致性**：`scripts/catalog.py --check` 防目录清单漂移
- **密钥扫描**：密钥 / 私钥 / token 不得入库
- **测试**：`pytest`（工具链单测 + 已有插件行为测试）

热加载（L2）在具备 jiuwenswarm 运行环境的流水线节点执行；本地可用
`--require-hot-load` 自检。

## 安全审查（tools / rails 必审）

插件中的 `tools/` 与 `rails/` 是**进程内执行**的 Python 代码，PR 必须通过
[docs/review-checklist.md](./docs/review-checklist.md) 的审查，重点：

- import 期无副作用（不联网、不起子进程、不写文件）
- 写入路径来自工具入参或 `get_workspace()` 会话目录，禁止自行推导
- 密钥零入库；第三方依赖须声明并按「缺依赖 → success=false」降级

## 发布

合并到 main **不**自动发布。维护者按 [docs/hub-publish.md](./docs/hub-publish.md)
执行：`python scripts/publish.py <name>`（需 `JIUWENSWARM_HUB_TOKEN`）。
