# 08 · 开发指南

> 本文覆盖**贡献代码到 Open-AutoGLM**所需的所有信息：开发环境、代码质量工具、测试、PR 流程。
> 源材料来自 `setup.py`、`requirements.txt`、`.pre-commit-config.yaml`、`.gitignore` 和 [DeepWiki 9.x](https://deepwiki.com/zai-org/Open-AutoGLM/9-development-guide)。

## 文件地图

| 文件 | 行数 | 作用 |
|------|------|------|
| `setup.py` | 49 | 包定义、依赖、entry_points |
| `requirements.txt` | 20 | 运行时 + 部署 + 开发依赖 |
| `.pre-commit-config.yaml` | 23 | 代码质量 hooks 配置 |
| `.gitignore` | 63 | 忽略规则 |
| `.github/PULL_REQUEST_TEMPLATE.md` | — | PR 模板 |
| `.github/ISSUE_TEMPLATE/` | — | bug_report + feature-request 模板 |

## 开发环境设置

### 基础要求

- **Python 3.10+**（`setup.py:31` 强制；classifiers 写了 3.10/3.11/3.12）
- Git
- 平台对应的设备工具（adb / hdc / idevice，看你测哪个平台）

### 标准安装流程

```bash
git clone https://github.com/zai-org/Open-AutoGLM.git
cd Open-AutoGLM

# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# 2. 安装运行时依赖
pip install -r requirements.txt

# 3. 以"可编辑"模式安装本包(含 dev extras)
pip install -e ".[dev]"
```

### `pip install -e ".[dev]"` 做了什么

`-e` 表示**可编辑安装**：Python 直接引用源码目录，改代码立即生效，不需重装。

`[dev]` 触发 `setup.py:36-43` 的 `extras_require["dev"]`：

```python
"dev": [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
    "ruff>=0.1.0",
],
```

> ⚠️ **潜在冲突**：`black` 和 `ruff-format` 都是 formatter，规则可能冲突。实际项目用 pre-commit 跑 ruff-format（见下文），dev extras 里的 `black` 是冗余的。**建议只用 ruff**，把 black 从 extras 删掉。

## `setup.py` 详解

```python
setup(
    name="phone-agent",                    # PyPI 包名
    version="0.1.0",
    author="Zhipu AI",
    description="AI-powered phone automation framework",
    url="https://github.com/yourusername/phone-agent",   # ⚠ 占位符,未改成 zai-org
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=["Pillow>=12.0.0", "openai>=2.9.0"],
    extras_require={"dev": [...]},
    entry_points={
        "console_scripts": ["phone-agent=main:main"],
    },
)
```

### 关键观察

1. **包名 `phone-agent`**（不是 `open-autoglm`）—— `pip install phone-agent` 安装的就是这个项目
2. **`entry_points` 注册了 `phone-agent` 命令**（`setup.py:44-48`）—— 装完后**直接 `phone-agent --help` 就能用**，不必 `python main.py`
3. **`install_requires` 漏了 `requests`** —— iOS 支持（`xctest/` 模块）用 `requests` 调 WDA HTTP，但 `requests` 只在 `requirements.txt` 里、没在 `setup.py` 里。**通过 `pip install phone-agent` 安装的用户跑 iOS 会 ImportError**。这是潜在 bug
4. **`url` 还是 `yourusername/phone-agent` 占位符** —— 应改成 `zai-org/Open-AutoGLM`
5. **Apache 2.0 许可证**（`setup.py:22`），与 `LICENSE` 文件一致

### `phone-agent` 命令

```bash
# 装完后(pip install -e . 或 pip install phone-agent)
phone-agent --help
phone-agent --list-apps
phone-agent --base-url http://localhost:8000/v1 "打开微信"
```

效果与 `python main.py` 完全相同（都调 `main.py:main()`）。

## `requirements.txt` 详解

```
Pillow>=12.0.0          # 截图处理(读宽高、JPEG→PNG 转换)
openai>=2.31.0          # OpenAI 兼容 API 客户端

# For iOS Support
requests>=2.31.0        # 调 WebDriverAgent HTTP 端点

# For Model Deployment (注释掉,按需启用)
# sglang>=0.5.6.post1
# vllm>=0.12.0
# transformers>=5.0.0rc0

# Optional: for development (注释掉,建议用 pip install -e ".[dev]")
# pytest>=7.0.0
# pre-commit>=4.5.0
# black>=23.0.0
# mypy>=1.0.0
```

**分层依赖**：
- **必装**：`Pillow` + `openai`（Android/HarmonyOS 基础功能）
- **iOS 必装**：再加 `requests`
- **本地部署模型**：再加 `vllm` 或 `sglang` + `transformers>=5.0.0rc0`
- **开发**：`pip install -e ".[dev]"` 或手动装 `pytest/pre-commit/black/mypy`

> **transformers 依赖冲突可忽略**：README 明确说"上述步骤出现的关于 transformers 的依赖冲突可以忽略"。

## Pre-commit Hooks

项目用 [pre-commit](https://pre-commit.com/) 框架在 `git commit` 前自动跑代码质量检查。

### 一次性安装

```bash
pip install pre-commit
pre-commit install        # 在 .git/hooks/ 注册 hook
pre-commit run --all-files   # 首次全量跑一遍,验证安装
```

之后每次 `git commit` 会自动触发。

### 三个工具

`.pre-commit-config.yaml` 配置了 3 个工具：

| 工具 | 仓库 | 版本 | 作用 | 自动修复 |
|------|------|------|------|---------|
| **Ruff**（lint）| `astral-sh/ruff-pre-commit` | v0.11.7 | Python lint + import 排序 | ✅（`--fix`）|
| **Ruff**（format）| 同上 | v0.11.7 | Python 代码格式化 | ✅ |
| **Typos** | `crate-ci/typos` | v1.32.0 | 拼写检查 | ❌（仅报告）|
| **PyMarkdown** | `jackdewinter/pymarkdown` | v0.9.29 | Markdown 格式 | ✅（`fix`）|

### Ruff 配置

```yaml
- id: ruff
  args: [--output-format, github, --fix, --select, I]
- id: ruff-format
```

- `--output-format github`：错误格式适配 GitHub Actions
- `--fix`：自动修可修的（import 排序）
- `--select I`：**只启用 import 排序规则**（ruff 的 `I` 规则集等价于 isort）
- `ruff-format`：用默认规则格式化（等价于 black 但更快）

> **注意**：项目**没有 `pyproject.toml` 或 `ruff.toml`** 单独配置 ruff，所有规则都通过 pre-commit args 传。如果想启用更多 ruff 规则（如 `E` pycodestyle、`F` pyflakes），要改 `.pre-commit-config.yaml:13` 的 `--select` 参数。

### Typos 配置

```yaml
- id: typos       # 无特殊 args,用默认字典
```

扫描所有文本文件（`.py` / `.md` / `.yaml`）找常见拼写错误。

**若误报**（如项目专有名词被标错）：在仓库根加 `typos.toml`：

```toml
[default.extend-words]
autoglm = "autoglm"
xctest = "xctest"
```

### PyMarkdown 配置

```yaml
- id: pymarkdown
  args: [fix]    # 自动修复 Markdown 格式问题
```

检查 Markdown 链接语法、列表缩进、标题层级、代码块围栏等。

### 文件排除

`.pre-commit-config.yaml:4-5`：

```yaml
exclude: '^phone_agent/config/apps\.py$'
exclude: '^README_en\.md$'
```

⚠️ **这是 YAML 重复 key 的潜在 bug**：YAML 规范中后出现的 `exclude:` 会**覆盖**前一个。所以实际效果是只排除 `README_en.md`，**`apps.py` 仍然会被检查**。

正确写法应该用正则 `|` 或列表：

```yaml
# 方式 1: 正则或
exclude: '^(phone_agent/config/apps\.py|README_en\.md)$'

# 方式 2: exclude + 单独 exclude_regex（pre-commit 不支持列表）
```

**如果你是 maintainer，建议修这个 bug**。当前 `apps.py`（226 行的字典）会被 ruff/typos/pymarkdown 检查，可能误报。

### 手动跑 hooks

```bash
pre-commit run                    # 只跑 staged 文件
pre-commit run --all-files        # 跑所有文件
pre-commit run ruff               # 只跑 ruff
pre-commit run --files main.py    # 跑指定文件
```

### 绕过 hooks（不推荐）

```bash
git commit --no-verify            # 跳过所有 hooks
```

仅用于紧急情况，正常开发不要用。

### Hook 失败后怎么处理

| 失败类型 | 处理 |
|---------|------|
| Ruff 自动修复了 import | `git diff` 看改了啥 → `git add` → 重 commit |
| Typos 报错 | 手动改正解拼错的词；若是专有名词加 `typos.toml` |
| PyMarkdown 自动修复 | `git diff` 看改了啥 → `git add` → 重 commit |

### 更新 hook 版本

```bash
pre-commit autoupdate     # 把 .pre-commit-config.yaml 里的 rev 更新到最新
```

## 测试

### 当前状态：无单元测试

```bash
pytest tests/    # README 推荐命令
```

**但仓库目前没有 `tests/` 目录**（只在 `.gitignore:37` 预留了 `.pytest_cache/`）。所以 `pytest tests/` 会报 `ERROR: file or directory not found`。

### 实际的"测试"方式

1. **部署验证脚本**：`scripts/check_deployment_cn.py`（测模型服务）—— 见 [07-deployment.md](07-deployment.md#部署后验证)
2. **system requirements 自检**：`python main.py` 启动时的 `check_system_requirements()` —— 测设备工具+连接
3. **examples 手动跑**：`python examples/basic_usage.py` 端到端测
4. **真机验证**：`python main.py "打开微信发消息给文件传输助手：部署成功"`

### 补测试的建议

如果要补 `tests/`，优先级：

| 优先级 | 测什么 | 怎么测 |
|-------|-------|-------|
| P0 | `parse_action` 各路径 | 单元测试，纯字符串解析，无外部依赖 |
| P0 | `_convert_relative_to_absolute` | 单元测试，纯数学 |
| P1 | `ModelClient._parse_response` 四条规则 | 单元测试，纯字符串 |
| P1 | `MessageBuilder` 各方法 | 单元测试，纯 dict 操作 |
| P2 | `ActionHandler.execute` 调度逻辑 | mock DeviceFactory |
| P3 | 端到端 Agent 循环 | mock model_client + device_factory |

**例**：`tests/test_parse_action.py`

```python
from phone_agent.actions.handler import parse_action

def test_parse_tap():
    assert parse_action('do(action="Tap", element=[500, 300])') == \
        {"_metadata": "do", "action": "Tap", "element": [500, 300]}

def test_parse_type_with_special_chars():
    result = parse_action('do(action="Type", text="hello\nworld")')
    assert result["action"] == "Type"
    assert "hello" in result["text"]

def test_parse_finish():
    assert parse_action('finish(message="done")') == \
        {"_metadata": "finish", "message": "done"}
```

## 代码风格

### Ruff 规则

当前 `--select I` 只启用了 import 排序。其他规则没启用。

**import 排序约定**（ruff 默认）：
1. 标准库（`import os`）
2. 第三方（`from openai import OpenAI`）
3. 本项目（`from phone_agent import ...`）

每组之间空一行。看 `main.py:16-34` 就是范例。

### 类型 hints

代码库**全量使用类型 hints**（PEP 604 新语法 `str | None` 而非 `Optional[str]`）。新代码也必须用。

```python
# ✅ 推荐(项目风格)
def foo(x: int | None = None) -> str | None: ...

# ❌ 避免
def foo(x: Optional[int] = None) -> Optional[str]: ...
```

### Docstring

- **模块级**：每个 `.py` 顶部一行 `"""..."""` 描述
- **类**：三引号 docstring 描述用途，关键类有 `Args:` 段
- **方法**：公开方法有 docstring，私有方法（`_xxx`）通常省略
- **dataclass**：字段即文档，不必加 docstring

## 调试技巧

### 启用 HDC verbose

`main.py:701-704` 启动时若用 HDC 会自动开 verbose：

```python
if device_type == DeviceType.HDC:
    from phone_agent.hdc import set_hdc_verbose
    set_hdc_verbose(True)
```

### 单步调试（step 模式）

用 `PhoneAgent.step()` 而非 `run()`，逐步推进，每步插入断点：

```python
agent = PhoneAgent(...)
result = agent.step("打开美团")
breakpoint()   # 在这里检查 agent._context / agent.step_count
while not result.finished:
    result = agent.step()
    breakpoint()
```

详见 [02-agent-loop.md](02-agent-loop.md#steptask-none单步调试)。

### Monkey-patch 模型

不想真调模型（耗钱/耗时），可 mock：

```python
from phone_agent.model.client import ModelClient, ModelResponse

def fake_request(self, messages):
    print(f"[MOCK] Got {len(messages)} messages")
    return ModelResponse(
        thinking="测试思考",
        action='do(action="Home")',
        raw_content="<think>测试思考</think><answer>do(action=\"Home\")</answer>",
        time_to_first_token=0.1, time_to_thinking_end=0.2, total_time=0.3,
    )

ModelClient.request = fake_request
# 之后 PhoneAgent 会用这个 mock
```

### 保存每步截图

```python
import base64
from phone_agent.device_factory import get_device_factory

class DebugAgent(PhoneAgent):
    def _execute_step(self, *args, **kwargs):
        result = super()._execute_step(*args, **kwargs)
        shot = get_device_factory().get_screenshot()
        with open(f"debug/step_{self._step_count:03d}.png", "wb") as f:
            f.write(base64.b64decode(shot.base64_data))
        return result
```

详见 [EXTENDING.md](EXTENDING.md#加-step-hook)。

## PR 流程

### 提 PR 前 checklist

- [ ] 跑 `pre-commit run --all-files` 通过
- [ ] `python main.py --list-apps` 不报错（基础冒烟）
- [ ] 若改了 prompt → 跑端到端任务验证效果不退化
- [ ] 若改了设备层 → 至少在一个平台真机验证
- [ ] commit message 清晰（项目无 CLAUDE/Conventional Commits 强制约定）

### PR 模板

`.github/PULL_REQUEST_TEMPLATE.md`（40 行）定义了贡献指南：

- **接受的 PR 类型**：修 typo / 修 bug（引用 issue 号）/ 新功能（说明必要性）
- **代码风格**：跑 `pre-commit run --all-files` 通过
- **命名规范**：必须用**英文**（不拼音）；遵循 PEP8；避免 `a/b/c` 无意义名
- ⚠️ **小 bug**：第 31-39 行有 "For glmv-reward Contributors" 小节，引用了 `glmv-reward/` 目录和 `uv run poe lint` —— 但 **Open-AutoGLM 仓库没有这个子目录**，这是从其他项目复制粘贴遗留的错误，提 PR 时可忽略该小节

### Issue 模板

`.github/ISSUE_TEMPLATE/`：
- `bug_report.yaml`（72 行）：报 bug，含字段：
  - System Info（CUDA/Transformers/Python/OS/硬件）
  - Who can help（@ 维护者，最多 3 人）
  - Information（官方脚本 vs 自己修改的脚本）
  - Reproduction（复现步骤，要求最小复现单元）
  - Expected behavior
- `feature-request.yaml`：提功能请求

提 issue 时按模板填，能加快响应。

## .gitignore 关键项

```
# Python 标准忽略(__pycache__ / *.egg-info / build/ ...)
# 虚拟环境(venv/ .venv ENV)
# IDE(.idea/ .vscode/ *.swp)
# 测试(.pytest_cache/ .coverage .mypy_cache/)
# 项目特定
screenshots/            # 截图临时文件
*.log
/tmp/
call_model.py           # 旧文件,迁移期保留 ignore
app_package_name.py     # 同上
.claude/                # 开发者用 Claude Code 留下的目录
```

`.claude/` 被忽略说明**项目维护者用 Claude Code 开发**。`.opencode/` 没被忽略（你看到的当前会话就在那）。

## 与上游同步

```bash
git remote add upstream https://github.com/zai-org/Open-AutoGLM.git
git fetch upstream
git checkout main
git merge upstream/main    # 或 rebase
```

DeepWiki 显示**最后 indexed 是 2026 年 3 月 9 日**，commit `86f553`（与当前 HEAD 一致）。

## 已知问题（贡献机会）

如果你想给项目提 PR，以下是发现的待办：

| 问题 | 文件 | 难度 |
|------|------|------|
| `.pre-commit-config.yaml` 重复 `exclude:` key | `.pre-commit-config.yaml:4-5` | 易 |
| `setup.py` 的 `install_requires` 漏 `requests` | `setup.py:32-35` | 易 |
| `setup.py` 的 `url` 还是占位符 | `setup.py:17` | 易 |
| `extras_require["dev"]` 同时有 black + ruff（冲突） | `setup.py:36-43` | 易 |
| **PR template 引用了不存在的 `glmv-reward/` 目录** | `.github/PULL_REQUEST_TEMPLATE.md:31-39` | 易 |
| `prompts.py` 遗留废弃，无人 import | `phone_agent/config/prompts.py` | 易（删文件）|
| `handler.py:345` debug print 残留 | `phone_agent/actions/handler.py` | 易 |
| `handler.py:_send_keyevent` 死代码 | `phone_agent/actions/handler.py:258-318` | 中（评估是否删）|
| `xctest/device.py:9` SCALE_FACTOR=3 硬编码 | `phone_agent/xctest/device.py` | 中（动态算）|
| 没有 `tests/` 目录 | — | 中（补单测）|
| DeviceFactory 不支持 iOS（架构不一致） | `device_factory.py:44-45` | 难（重构）|

## 下一步

- 环境搭好 → [07-deployment.md](07-deployment.md) 起模型服务
- 想扩展功能 → [EXTENDING.md](EXTENDING.md)
- 想了解架构 → [ARCHITECTURE.md](ARCHITECTURE.md)
- 准备提 PR → 本文「PR 流程」+「已知问题」

---
