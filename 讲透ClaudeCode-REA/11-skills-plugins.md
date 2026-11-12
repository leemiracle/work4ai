# 11 · Skills 与插件：命令即技能、三层披露、marketplace

> 证据：minified 源码偏移考古 + 内嵌 [D] 文档（plugin-eval-*.md、
> example-plugins、SKILL-*.md 15 个）[S]。深报告（frontmatter 17 字段全表+
> marketplace 11 种源类型+eval 六型 graders）：`rea-claude/reports/11-skills-plugins.md`（38KB）。

## 1. 命令即技能：统一管线 [S]

**Skill 与 slash command 是同一 `type:"prompt"` 结构的两态**，共用
processPromptSlashCommand 管线——/foo 与 Skill(name=foo) 走同一条路。
SKILL.md frontmatter 17 字段（zod schema 实证）：name/description/model/
allowed-tools/disable-model-invocation/user-invocable/when_to_use/paths/hooks/
context fork/agent/background/created_by(dream-proposal)/mcpServers 等。

## 2. 渐进披露三层 [S]

| 层 | 内容 | 成本 |
|---|---|---|
| L1 常驻 | skill_listing 附件：`- name: description - when_to_use` 行 | desc ≤1536 字符截断；**总预算=上下文×4%**；超限按优先级降级 name-only（bundled 永不降级）；只对**新出现**的技能发 |
| L2 调用时 | Skill 工具 call() → **整份正文注入**（"Base directory for this skill: \<dir\>" + 全文） | 无"核心节提取"——全文进上下文 |
| L3 附属文件 | 正文里的相对路径引用由模型自己 Read | 按需 |

## 3. 插件体系 [S]

插件根合法结构：`.claude-plugin/plugin.json`（或顶层双路径）+ skills/ +
commands/ + agents/ + hooks/hooks.json + hooks/*.ts（function hooks 模块）+
.mcp.json（工具名 `mcp__plugin_<plugin>_<server>__<tool>`）+ .lsp.json +
output-styles/themes/workflows/monitors/routines/——全部过 path-traversal 检查。

plugin.json 关键字段：组件显式指认（逃逸即错）/userConfig（settings 提供值，
不合 schema 则 "loading on its defaults"）/dependencies（semver 相交校验）/
installationPreference（org 下发 available/required/auto_install/not_available）/
experimental.evals。

**marketplace 11 种源类型**：github/url/git/**npm（未实现）**/file/directory/
hostPattern/pathPattern/skills-dir/settings（org 管理员内嵌市场）/claudeai；
可自动更新的源=github/git/url/settings 四种；git-subdir 走 sparse-checkout。
安装态：`~/.claude/plugins/{cache,data}`、installed_plugins.json v2、
**五源 enabledPlugins 合并**、独立技能目录被采纳为 `name@skills-dir` 伪插件、
账号技能走 `skills/synced/` 惰性同步缓存。

## 4. propose_skills 真身（勘误补全）[S]

= claude.ai 远程会话的**账号技能提案卡片**（render-only + read-before-improve
校验）；与 save_skill、SendUserFile 构成三条技能交付通道（09 报告已证它不是
agent 动态注册）。

## 5. plugin eval [S+D]

`claude plugin eval`：evals/ 目录、**六型 graders**、MCP mock 回放、隔离沙箱、
v1 JSON 契约——插件质量门禁的完整形态（内嵌文档全量还原）。

## 6. 生态侧增量（worker 内部见 07 册）[S]

userConfig 合流进 hooks-worker、ui.log 预算、plugins sync、**插件标记写保护**。

## 7. 手搓启示（→ rl-and-agents/）

1. "命令即技能"统一管线：slash command 与 skill 不分家——**不要做两套系统**，
   一个 prompt 结构 + 两个入口；
2. 渐进披露的预算设计（listing 4% + 超限降级 + bundled 永不降级 + 只发新增）
   是上下文经济学的范本；
3. 插件权限模型贯穿始终：path-traversal 检查、userConfig schema 校验、
   插件版 agent 定义忽略 permissionMode/hooks/mcpServers（09 册）——
   **生态开放但提权通道全部焊死**；
4. marketplace 的 settings 型源（org 管理员内嵌市场）是企业分发的关键设计：
   无需外部仓库即可组织级推送插件。
