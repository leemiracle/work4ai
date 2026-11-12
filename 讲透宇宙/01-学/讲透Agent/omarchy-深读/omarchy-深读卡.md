# omarchy 深读卡 —— AI 编码 Agent 的一等公民桌面：把 agent 选择/启动/用量/崩溃诊断做进 OS 层的 Hyprland 发行版

> **定位**：omarchy（basecamp/omarchy，MIT，DHH）是基于 Arch + Hyprland + Quickshell 的 opinionated 桌面发行版。对 work4ai 的价值不在"又一个 Linux 发行版"，而在它是**第一个把 AI coding agent 当系统组件设计的桌面**：`omarchy-agent` 家族（默认 agent 选择/无值守启动/别名 `a`）、用量采集管线（Claude/Codex/Fireworks 本地 transcript 扫描 + 官方限额端点 → 面板）、崩溃自动诊断（coredumpctl → 默认 agent + diagnose-crash skill）、以及 AGENTS.md/skills 的 agent 工程约定。工程侧的 bash 元数据路由、Lua 分层 Hyprland 配置、Btrfs+Snapper+Limine 快照回滚 update 管线、Quickshell 插件 IPC 桌面，都是可迁移的系统设计范式。
> **本地**：`/data/usershare/linux-src/omarchy-quattro`（v4.0.0.alpha 分叉，即上游 v4 线的本地工作副本）｜**深读**：deepwiki 39 子页归档 `deepwiki/omarchy/full.md`（2026-08-25 抓取，wiki 索引 2026-08-18 @ fa955b）｜**文档产出**：向 quattro `docs/` 新增 10 页（见 `quattro文档映射-2026-08-25.md`）

## 一、组件栈（DeepWiki 蒸馏 + quattro 本地修正）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 会话层 | uwsm Wayland 会话、环境注入 | `uwsm`/`uwsm-app`、`$OMARCHY_PATH`、`default/hypr/autostart.lua` |
| 合成器层 | Hyprland（Lua 配置，非 conf） | `config/hypr/hyprland.lua`（用户层）→ `default/hypr/`（默认层）→ theme 层；`o`/`hl` helper API |
| 桌面 shell 层 | 单实例 Quickshell 插件化桌面 | `shell/plugins/*`（bar/menu/clipboard/agents…）、PluginRegistry、`omarchy-shell` IPC |
| 命令层 | bash 元数据路由 | `bin/omarchy` 扫 `# omarchy:summary=` 头 → 分组命令树（capture/pkg/theme/hw/agent…前缀族） |
| AI agent 层 | agent 全生命周期 | `omarchy-default-agent`（mise 安装 10 种 agent）、`omarchy-agent`（无值守启动）、`omarchy-agent-usage-*`（用量采集）、`omarchy-agent-crash`（coredump 诊断）、`shell/plugins/agents/` 面板 |
| 包/更新层 | 三源 + 四通道 + 快照迁移 | Arch 官方 + OPR + AUR(yay)；stable/rc/edge/dev 通道；`omarchy-update`→snapshot→migrations |
| 恢复层 | Btrfs 快照回滚 | Snapper（NUMBER_LIMIT=5）+ Limine + `limine-snapper-sync` + `btrfs-overlayfs` initramfs 钩子 |
| 硬件层 | DMI/GPU/外设检测 | 26 个 `omarchy-hw-*` 谓词、`omarchy-apply-hardware`、T2/ROG/Surface/Framework 特化 |

**quattro 本地修正**（deepwiki 部分页基于 v3 残留，已对本地代码核实）：3.2 Waybar / 3.3 Walker 两页对 v4 **失效**——quattro 无 waybar/walker 包，状态栏=Quickshell `shell/plugins/bar/`，应用启动=Quickshell 菜单（`omarchy-menu.jsonc`）；6.2 清单页的 waybar/mako 行同样失效（quattro 通知走 shell 内建）。其余 37 页与本地代码抽样一致。

## 二、核心机制

1. **bash 元数据路由**（1 Overview/3.1）：无注册表、无构建步骤——`bin/omarchy` 运行时扫同目录脚本的 `# omarchy:summary=/args=/aliases=` 注释头（80 行内）建分组命令树；`GROUP_DESCRIPTIONS` 是唯一权威分组表。加命令=加一个带头的脚本。"约定即接口"的范本。
2. **三层 Lua Hyprland 配置**（4.1）：`bootstrap.lua` 把 `~/.config/?.lua` 与 `$OMARCHY_PATH/?.lua` 都塞进 `package.path`，用户模块按名遮蔽默认模块——分层靠 Lua require 语义而非模板渲染；theme 经 `require_optional("omarchy.current.theme.hyprland")` 存在才加载；`omarchy_default_bindings=false` / `preinstalls-removed` 标记改加载集。
3. **窗口规则三阶段管线**（4.2）：全局基线（suppress maximize + `+default-opacity` 标签）→ `apps/*.lua` 逐应用改写（媒体应用摘标签免透明）→ 末段对存活标签统一 `opacity 0.985 0.96`。"先打标后结算"的规则编译思路。
4. **快照优先的 update 管线**（6.4/2.2/10.2）：`omarchy-update` = 预清理缓存 → `omarchy-snapshot create`（版本号当描述，snapper 缺失退 127 不阻塞）→ pacman guard 强制所有升级走此口（`OMARCHY_UPDATE_PACMAN=1` 是豁免）→ 逐条幂等 migrations（`~/.local/state/omarchy/migrations/` 记账）→ AUR(yay)。回滚单位=boot menu 快照（`btrfs-overlayfs` 保证快照启动可写）。
5. **AI agent 三层集成**（10.3，quattro 全核实）：管理 CLI（`omarchy-default-agent`：10 agent，mise 安装，`~/.config/omarchy/defaults/agent` 单词存档）→ 执行包装（`omarchy-agent`：HOME→~/Work、按 agent 翻译"别停下来问"、`--app-id=org.omarchy.agent` 统一窗口类）→ 用量管线（每 agent 一个 collector 打一条 display-ready JSON 到 `~/.local/state/omarchy/agents/usage/`，面板 watch 目录即渲染——加 agent=加 collector）。
6. **Quickshell 插件桌面**（3.1/10.4）：一切 UI 皆插件（manifest.json 声明），CLI 经 `omarchy-shell` IPC 路由调用；菜单内容=数据（`omarchy-menu.jsonc`，JSONC 去注释解析），逻辑=纯 JS（MenuModel.js，Node 可直接跑测试）。

## 三、与讲透系列的对位

| omarchy 机制 | 讲透系列对应主题 | 备注 |
|---|---|---|
| `omarchy-agent` 家族 + agents 面板 | 讲透 Agent 运行环境 / 端侧 Agent | agent 的 OS 级运维：选择、安装、无值守、用量、诊断五件事全做成系统命令 |
| usage collectors（本地 transcript 扫描 + 限额端点缓存） | 讲透 Agent 可观测性 / token 经济学 | Claude `.jsonl` 去重聚合、opencode SQLite 复用、OAuth 端点缓存——端侧计量的工程现实 |
| `omarchy-agent-crash` + crash-watch.service | 讲透 Agent 工程化 | coredump → 默认 agent + skill 的自动诊断闭环，崩溃处理 agent 化 |
| AGENTS.md + agents/skills/ 约定 | 讲透 Skills / agent 工程约定 | "OS 仓库先给 agent 写说明书"——DHH 把 agent 协作当一等文档类型 |
| pacman guard + migrations | 讲透工程化/部署 | "所有变更走带快照的入口 + 幂等迁移"=数据库 migration 思想移植到 OS |
| Lua require 遮蔽分层 | （通用）配置系统设计 | 比 conf 片段拼接更强的分层原语 |
| Quickshell 插件 IPC | （通用）插件架构 | 数据/逻辑/渲染分离，JS 逻辑可 headless 测试 |

## 四、关键入口（quattro 本地树）

```text
omarchy-quattro/
├── AGENTS.md                  # agent 工程约定总纲（风格/命令/测试/特权升级）
├── bin/                       # ~200 个 omarchy-* 命令（元数据头路由）
│   ├── omarchy                # ★ 路由器：扫注释头 + GROUP_DESCRIPTIONS
│   ├── omarchy-agent*         # ★ agent 家族 7 件套
│   ├── omarchy-update / -migrate / -snapshot / -update-pacman-guard
│   └── omarchy-hw-*           # 26 个硬件谓词 + apply-hardware
├── default/                   # 只读默认层（refresh 拷贝到 ~/.config）
│   ├── hypr/                  # ★ Lua 配置（helpers/omarchy/windows/apps/bindings/）
│   ├── bash/                  # rc→envs/shell/aliases/functions/init + fns/*
│   ├── systemd/user/          # 受监督用户单元（sleep-lock/fcitx5/crash-watch…）
│   ├── pacman/ + snapper/ + limine/
│   └── omarchy/omarchy-menu.jsonc  # 菜单数据源
├── shell/                     # Quickshell 桌面（plugins/{bar,menu,clipboard,agents,…}）
├── config/                    # ~/.config 种子 ｜ themes/ 色板 ｜ manual/ 用户手册
├── install/ + migrations/     # 安装器 + 时间戳幂等迁移 ｜ docs/ 代码库参考文档
└── test/{cli,shell.d,acceptance.d}
```

## 五、深读子页地图（39 页精选 7）

| 子页 | 价值 |
|---|---|
| 10.3 AI Agent Integration | 本仓最相关：agent 三层集成全图（mermaid 数据流） |
| 10.4 Quickshell Plugin Architecture | 插件注册/IPC/QML 结构，桌面架构一页通 |
| 4.1 Hyprland Configuration | Lua 三层配置 + `o` helper API 逐函数表 |
| 6.4 Update System + 10.2 Migration System | 快照+guard+migrations 的完整 update 契约 |
| 2.2 Boot Management and Snapshots | Limine/Snapper/initramfs 钩子（NVIDIA kms 裁剪/拉丁键盘锁定细节） |
| 6.1 Package Repositories | 三源四通道 + channel-set 状态机 |
| 11 Glossary | Seed vs Resync、OPR 等内部黑话权威定义 |

（另：3.2 Waybar / 3.3 Walker 两页为 v3 残留，读时对照 §一修正注）

## 六、与"我们"的关系（一句话）

quattro 是当前活跃开发区——深读它=同时获得「讲透 Agent 的端侧运行环境活教材」（agent 进 OS 的完整设计）与「对分叉仓库的代码库级文档」（本卡产出的 10 页 docs/ 已直接落进 quattro），后续 shell/ 插件与 agent 面板的改动都有这张地图兜底。

---
生成：2026-08-25 · deepwiki 39 页全归档（索引 2026-08-18 @ fa955b）· 关键断言逐条对 quattro 本地代码核实
