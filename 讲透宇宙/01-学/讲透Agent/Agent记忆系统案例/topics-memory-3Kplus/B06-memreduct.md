# B-06 `henrypp/memreduct`（10.2K★）[结构档-未克隆]
> 来源：deepwiki（索引 2025-04-19, ae7bb8）+ GitHub README/tree ｜ C 语言（纯 Win32）｜ GNU GPL
> 一句话定位：轻量 Windows **实时内存清理器**——用未文档 Native API 按内存列表（working set/standby/modified...）选择性修剪，C 单体程序（src/main.c 一个文件撑起全部逻辑）

## 1. 定位与形态
- 自述使用"未文档内部系统特性（Native API）"清理各类系统缓存，宣称典型可降 10-50% 内存（deepwiki 引 README.md:17-26）。
- 兼容 Windows XP SP3+（高级功能 Vista+）；安装版与便携版双形态；配置存注册表或便携 INI（memreduct.ini）。
- 代码体积极小（tree 实证）：核心仅 `src/main.c + main.h + app.h + resource.h + resource.rc`，无构建系统复杂依赖；
- 国际化走 `bin/i18n/*.ini` 键值文件，tree 实证 30+ 语言文件（含简繁中文）。
- 依赖：SSE2 CPU + 管理员权限（内存管理操作必需）；Win7 需 KB3063858。

## 2. 架构与核心模块（来源：deepwiki Core Memory Management / Features）
### 2.1 九类可清理内存区（deepwiki Memory Area 表，引 CHANGELOG.md:2-3,14-15,74）
| 内存区 | 含义 | 版本要求 |
|---|---|---|
| Working Set | 运行中进程的工作集（热页逐出） | 全版本 |
| System Working Set | Windows 系统缓存工作集 | 全版本 |
| Standby List | 已关闭程序的缓存页（可牺牲） | Vista+ |
| Standby List Priority-0 | 最低优先级 standby（温和档） | Win8+ |
| Modified List | 待写盘页 | Vista+ |
| System File Cache | 文件缓存 | Vista+ |
| Modified File Cache | 待写盘文件缓存 | 全版本 |
| Registry Cache | 注册表内存缓存 | Win8.1+ |
| Combined Memory Lists | 页合并列表优化 | Win10+ |

### 2.2 触发与交互（deepwiki Core Functionality / User Interface）
- 四通道触发：手动 UI / 内存占用超阈值自动 / 可定制热键 / 命令行参数（可脚本化）。
- 托盘图标按内存占用百分比着色（warning/danger 两档可配），支持单击/中键/右键自定义动作；
- 托盘外观高度可配（透明度/边框/圆角/抗锯齿）。
- 设置五分类（deepwiki Settings 表）：General / 内存清理 / 外观 / 托盘 / 高级（standby 清理选项、结果日志）。

## 3. 与 B10 的对照（同为 Windows 清理器，取向不同）
| 维度 | memreduct（本仓） | WinMemoryCleaner（B10） |
|---|---|---|
| 技术栈 | C / 纯 Win32，单 main.c | C#/.NET WPF MVVM |
| 可清区域 | 9 类（含注册表缓存） | 6 类（语义文档更清晰） |
| 配置 | 注册表或便携 INI | 注册表（含重置脚本） |
| 国际化 | INI 键值 30+ 语言 | JSON 24 语言 |
| 触发 | 手动/阈值/热键/命令行 | 手动/热键/定时/阈值/CLI 五通道 |
| 进程排除 | 无 | 有（Process Exclusion List） |
| 依赖 | 零运行时依赖 | .NET Framework 4 |
- 两仓共同点：都需管理员权限、都把"内存区域语义"作为一等概念暴露给用户——印证洞见：**清理操作必须按区域命名而非一键全清**。

## 4. 与 Agent 记忆的可迁移机制
1. **Windows 内存列表模型 = 记忆分层的原生教科书**：
   - active（工作集）→ standby（可回收缓存，内容还在但随时可让出）→ modified（待持久化）→ free；
   - Agent 记忆可直接套用同款状态机：热上下文 / 冷缓存（可被新写入挤出、可按需调回）/ 待落盘 / 可复用槽位；
   - **"逐出工作集" ≠ "删除数据"**（页进 standby 仍可召回）——比"删或留"二值更细腻的记忆淘汰观。
2. **选择性修剪菜单**：不是笼统"清内存"，而是九类区域各配开关——记忆 GC 应按类目（会话缓存/实体索引/摘要/原文）独立开关、独立阈值。
3. **三通道并存**：阈值自动 + 热键手动 + 定时/命令行——自动策略之上永远保留人工即时干预与脚本编排入口。
4. **Priority-0 分级驱逐**：先清最低优先级 standby，"最不重要的先走"——记忆淘汰从低价值分级开始，而非全局扫描。
5. **单体极简部署**：记忆治理工具的便携形态（单文件+INI 配置）对边缘/嵌入式 Agent 有参考价值。
6. **状态可视化先于操作**：托盘按占用百分比着色（warning/danger 两档）——治理触发条件（阈值）与状态呈现（着色）同源，用户所见即触发器。

## 5. 局限
- 结构档未核源码：main.c 未读，具体 Native API 调用序列（如 `NtSetSystemInformation(SystemMemoryListInformation)`）未钉行号；
- 效果争议大：清 standby 常导致后续缺页回读反而变慢（社区长期争论）；仅 Windows；
- 九类区域随 Windows 版本碎片化，维护成本内建；
- 无进程级排除（对照 B10 的 Process Exclusion List）——粒度停留在系统级列表；
- 命令行细节与退出码未文档化，脚本编排可靠性弱于 B10。
