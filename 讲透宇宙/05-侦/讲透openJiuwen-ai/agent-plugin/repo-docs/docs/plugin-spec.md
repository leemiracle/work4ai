# Plugin 插件包规范（plugin-spec）

> 本文档是 agent-plugin 仓插件包规范的**权威来源**，内容收敛自 jiuwenswarm 主仓
> plugin-creator 技能的 `references/{manifest,rail,tool,skill}-spec.md`。
> 规范变更走本仓 PR 评审，并与主仓 plugin-creator 同步。
> 校验实现：`scripts/validate.py`（L0 规范 / L1 静态 / L2 热加载）。

## 1. 包结构与不变量

```
<plugin-name>/                  # kebab-case，必须等于 manifest.id
├── manifest.json               # 必须
├── README.md                   # 必须（扩展中心详情页正文）
├── avatars/avatar.png          # 可选
├── skills/<skill-name>/SKILL.md    # 可选（+ scripts/ references/ assets/）
├── tools/<name>_tool.py        # 可选
└── rails/<name>_rail.py        # 可选
```

不变量：

1. **`plugins/` 目录里的内容 = 用户最终拿到的内容**。开发态文件（测试、CI 配置、CHANGELOG）一律放仓库层（`tests/plugins/<name>/`），包内出现的东西会随 zip 分发。
2. `skills` / `tools` / `rails` **至少声明一类**；未使用的段**整段省略**，禁止空数组，禁止声明不存在的路径。
3. 插件包**禁止**声明 `persona` / `agent_card` / `model` / `subagents` / `memories` / `rubrics`（插件是能力包，不是人设——那是 agent_template 的职责）；**禁止**声明 `mcps`（MCP 走独立的 `agent-mcp` 资产类型）。
4. `id` 一经发布不可变（Hub 安装态按 id 记账）；改名只能新建插件并在 `renames.json` 登记映射。

## 2. manifest.json 字段

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `version` | string | 是 | semver；更新必须递增（发布流程管理） |
| `package_type` | string | 是 | 固定 `"plugin"` |
| `id` | string | 是 | 唯一标识，**必须等于包目录名**（kebab-case） |
| `name` | string | 是 | 插件包名 |
| `description` | string | 是 | 一句话描述 |
| `display_name` | `{en, zh}` | 是 | 展示名 |
| `display_description` | `{en, zh}` | 是 | 能力介绍，中文约 40-50 字 |
| `category` | string | 是 | `Design` / `Engineering` / `Life` / `IndustryConsultant` / `Others` |
| `source` | string | 是 | 固定 `"local"` |
| `avatar` | string | 否 | 包内相对路径；无则 `""` 或省略 |
| `default_init_input` | `{en, zh}` | 是 | 首次对话引导语，**与 `quick_inputs[0]` 逐字一致** |
| `tags` | `[{en,zh}]` | 是 | 固定 3 个 |
| `quick_inputs` | `[{en,zh}]` | 是 | 固定 3 个，写**能力触发场景** |
| `skills` | array | 否 | 每项 `{"dir": "./skills/<name>", "mode": "all" \| "auto_list"}` |
| `tools` | array | 否 | 见 §4 |
| `rails` | array | 否 | 见 §5 |

`tools[]` / `rails[]` 每项：`file`（包内相对路径）、`class`（与 `.py` 中类名完全一致，PascalCase）、`display_name` / `display_description`（`{en,zh}`）。skills 条目**不写** display 字段（来自 SKILL.md frontmatter）。

## 3. Skill 规范（skills/\<skill-name\>/SKILL.md）

- frontmatter：`name`（必填，等于目录名）、`description`（必填，触发机制：做什么 + 何时用）。
- 正文精简可操作：目标 / 工作流 / 验收标准；较长参考放 `references/`，模板素材放 `assets/`，可执行脚本放 `scripts/`。
- 渐进披露：description 常驻 context，SKILL.md 正文触发时加载，附属资源按需读取——因此**一个插件一个场景**，SKILL.md 保持精简。

## 4. Tool 规范（tools/\<name\>_tool.py）

继承 `openjiuwen.core.foundation.tool.Tool`，通过 `ToolCard` 描述能力：

```python
from openjiuwen.core.foundation.tool import Tool, ToolCard


class MyTool(Tool):
    def __init__(self) -> None:
        super().__init__(
            ToolCard(
                id="my_tool",
                name="my_tool",
                description="工具描述：何时用、做什么",
                input_params={
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string", "description": "参数1描述"},
                    },
                    "required": ["param1"],
                },
            )
        )

    async def invoke(self, inputs, **kwargs):
        return {"success": True, "result": "..."}

    async def stream(self, inputs, **kwargs):
        yield await self.invoke(inputs, **kwargs)
```

约束（L1 静态校验强制）：

- **无参构造**：`__init__(self) -> None`，内部自建 `ToolCard`；禁止注入 Rail / agent / session 等运行时对象。
- `ToolCard.id` 与 `ToolCard.name` 必须显式设置（推荐一致、snake_case）。
- `input_params` 必须是合法 JSON Schema 且 `"type": "object"`（无参数也要写 `{"type": "object", "properties": {}}`）；`properties` 禁止暴露 `artifact_root` / `output_root` / `workspace_root` / `base_output_dir` / `absolute_path`。
- 必须有 `async def invoke(...)`。
- **运行时路径策略**：文件写入路径必须由入参显式传入（如 `output_dir`），禁止 `Path.cwd()` / `os.getcwd()`，禁止写包内路径（包内只读）。
- 拿不到真实数据时返回明确降级字段（`estimated: true` 等）或错误说明；失败必须 `success=false`，不得用文本冒充产物。
- 与 Rail 共享状态：经文件系统按 session 隔离（`get_workspace()`），状态根禁止自定义变量名（`artifact_root` 等）。

## 5. Rail 规范（rails/\<name\>_rail.py）

继承 `openjiuwen.harness.rails.base.DeepAgentRail`，通过生命周期钩子监听执行过程：

```python
from openjiuwen.harness.rails.base import DeepAgentRail


class MyRail(DeepAgentRail):
    def __init__(self) -> None:
        super().__init__()
        self._agent = None

    def init(self, agent) -> None: ...
    def uninit(self, agent) -> None: ...
```

- 可用钩子：`before_invoke` / `after_invoke`、`before_model_call` / `after_model_call`、`before_tool_call` / `after_tool_call`、`before_task_iteration` / `after_task_iteration`；事件数据从 `ctx.inputs` 读取，**只实现需要的钩子，至少一个**。
- Rail 由加载器**无参构造**；依赖在 `init(agent)` 中获取。
- 动态 prompt 增强（`before_model_call`）：`builder.add_section(PromptSection(name=..., content={"cn": ..., "en": ...}))`，同名覆盖；`uninit` 时 `remove_section(同一 name)`。禁止写 `ctx.prompt` / `ctx.messages`。
- 内部状态路径统一 `get_workspace()`（按 session 隔离），禁止写包内路径、禁止 `cwd()`。

## 6. README.md

详情页正文：一句话定位（中/英）、核心能力、组件协作图、目录结构。参考 `plugins/example-plugin/README.md`。

## 7. 版本与发布

- 修改包内容必须递增 `manifest.version`（patch 由发布流程自动递增，minor/major 手动）。
- 发布：`python scripts/publish.py <name>`（详见 [hub-publish.md](hub-publish.md)）；zip ≤50MB，密钥类文件在打包与 Hub 侧双重排除。
- 产品内置通道：`python scripts/sync_builtin.py --repo <主仓路径> --only <name>`，在主仓走正常评审。
