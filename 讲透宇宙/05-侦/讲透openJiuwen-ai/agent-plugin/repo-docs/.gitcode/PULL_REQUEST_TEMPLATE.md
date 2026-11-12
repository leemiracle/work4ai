<!--  Thanks for sending a pull request!  Here are some tips for you:

1) If this is your first time, please read our contributor guidelines: CONTRIBUTING.md and docs/plugin-spec.md

2) PR 质量门禁（.github/workflows/pr-quality.yml）会自动运行：
   结构检查 + L0/L1 校验 + catalog 一致性 + 密钥扫描 + 单元测试。
   本地等价命令：python scripts/pr_check.py
-->

**What type of PR is this?**
<!--
选择下面一种标签替换下方 `/kind <label>`，可选标签类型有：
- /kind bug
- /kind task
- /kind feature
- /kind refactor
-->
/kind <label>

---

**What does this PR do / why do we need it**:

---

**Which issue(s) this PR fixes**:
<!--
*Automatically closes linked issue when PR is merged.
Usage: `Fixes #<issue number>`, or `Fixes (paste link of issue)`.
-->
Fixes #

---

**Test Plan and Test result**:
<!--
写明验证方式与结果，至少包含本地执行门禁的输出：
python scripts/pr_check.py
涉及 tools/ 或 rails/ 时，另需在 jiuwenswarm 运行环境执行并贴出 RESULT 行：
python scripts/validate.py --only <name> --require-hot-load
-->

---

**Self-checklist**（**请自检，在 [ ] 内打上 x，我们将检视你的完成情况，否则会导致 PR 无法合入**）:

+ - [ ] `python scripts/pr_check.py` 本地全绿（RESULT: PASS）
+ - [ ] 涉及 `tools/` 或 `rails/` 可执行代码时，已按 [docs/review-checklist.md](../docs/review-checklist.md) 第一节完成安全自查（不涉及则标注 N/A）
+ - [ ] `manifest.version` 已递增（仅当修改了既有插件包内容）
+ - [ ] `python scripts/catalog.py` 已重新生成 catalog 并提交
+ - [ ] `plugins/<name>/` 内没有混入开发态文件（测试/脚本/文档放 `tests/plugins/<name>/`）
+ - [ ] 插件 id 未改名、未与既有插件冲突
