# 06 · agent-skills 与发布工程：7 技能、dev 守卫、fail-closed CI

## 角色定位
这层是 CompileIQ 的"使用面 + 出厂面"：`agent-skills/` 让 AI 代理直接驱动调优战役，`dev/`（21 脚本）负责组装与验证发行物，`.github/workflows/ci.yml`（15 job）以 fail-closed 语义守门。

## 内部结构
**7 个技能**按 agentskills.io SKILL.md 约定：bootstrap（环境五步自检）/booster-pack（先试精选 ACF）/search-space（provider 选型，att 变体面向 attention）/author-objective（目标函数模板库）/run-search（Search 组装与 worker 选型）/validate-result（统计门）/debug（症状索引）。安装器 `install.sh` 为每种 agent 生成 `mount_`/`unmount_`/`check_` 三件套（claude_code 三件套在 `install.sh:93/112/124`，共 6 个 agent），主循环按 agent×模式 case 派发（`install.sh:443-448`）；`python_bin`（`install.sh:39`）探测保证渲染器可用。**dev 组装/验证/守卫**三段：组装=`compose_compileiq_wheel.py`（"one distribution one platform tag"，`compose_wheel` 在 `compose_compileiq_wheel.py:236`）；验证=`verify_complete_wheel.py`/`test_complete_wheel_install.py`；守卫=`check_public_artifacts.py`（16 格矩阵精确交叉积、私有标识符泄漏拒绝）+`check-linux-abi.py`（GLIBC/GLIBCXX 门）。

## 外部连接
技能引用文档（如 validate-result 引 `docs/flashinfer_booster.md`）；welch_validate.py 的判定门贯穿技能与文档：p<0.05 且均值下降且 Cohen's d>0.2 才 significant（`welch_validate.py:127`），不显著给出机器可读原因（`welch_validate.py:274`），CLI 用例即文档（`welch_validate.py:1-21`）。CI 侧 `test_release_workflow.py` 与 `test_public_artifact_guard.py` **反向锚定 CI 配置**——直接读 `.github/workflows/ci.yml` 文本断言不变式（指针 `test_release_workflow.py:8-10`，断言 release 只对 v 语义 tag 触发 `test_release_workflow.py:27`、目录发布原子且不标 latest `:63`、CI 不再部署 pages `:90`；guard 测试读 `ci.yml` 在 `test_public_artifact_guard.py:228`）——CI YAML 本身成为被测代码，这是罕见形态。

## 数据流
发布链：build-and-smoke-test-wheel 出前端轮 → compose-complete-wheels 按平台合并 amber → complete-wheel-matrix 选格 → verify-and-test-complete-wheel 验收 → ci-pass 聚合 → upload-github-release-wheels（`ci.yml:677`）只上传通过验收的 `compileiq-complete-wheel-*` 产物。

## 设计决策
**fail-closed over every job** 的精确实现：`ci-pass`（`ci.yml:631`）以 `if: always()` 运行、needs 其余 13 个 job，内联 Python 把任何非 success（含 skipped）判失败（`ci.yml:653-671`）——唯一显式例外是 PR 上允许跳过 `verify-and-test-complete-wheel`（`ALLOWED_SKIPS`，`ci.yml:647-651`）。`concurrency` 按 ref 取消旧跑（`ci.yml:15-17`）。首个 job 就是 `public-artifact-guard`（`ci.yml:21`）——公共产物检查置于一切之前。nightly 以 `CIQ_FUZZ_EXAMPLES=100` 深跑 fuzz（`nightly.yml:6`）。

## 新人提示
给代理装技能：`bash agent-skills/install.sh --agents claude-code`（或不带参数自动探测）。改 CI 时务必同步改守卫测试的文本断言——它们会因 YAML 措辞变化而红。宣称任何加速前，先跑 `welch_validate.py`，门不过就不许说 faster。
