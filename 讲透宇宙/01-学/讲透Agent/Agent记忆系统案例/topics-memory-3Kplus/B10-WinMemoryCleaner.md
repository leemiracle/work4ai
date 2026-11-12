# B-10 `IgorMundstein/WinMemoryCleaner`（4.9K★）[结构档-未克隆]
> 来源：deepwiki（索引 2025-04-21, 0e6b77）+ GitHub README/tree ｜ C#/.NET Framework 4 + WPF（MVVM）｜ MIT
> 一句话定位：Windows **原生内存优化器**（零第三方 DLL、单文件便携）——把 Win32/SystemMemoryListInformation 级别的"内部组件如何工作"写成清晰的六区内存模型与命令行接口

## 1. 定位与形态
- 设计原则（deepwiki 引 README.md:130-141）：极简 UI、零第三方库/DLL 依赖、便携单 exe、**只用 Windows 原生方法**做内存管理、MVVM + S.O.L.I.D.。
- 需管理员权限（深度清理必需）；兼容 XP~Win11 与各 Server 版（README.md:26-30）。
- 24 语言 JSON 本地化（src/Resources/Localization/，含 RTL 文本支持）。

## 2. 架构与核心模块（来源：deepwiki Technical Architecture + tree）
### 2.1 分层（MVVM，deepwiki 引 README.md:132）
- UI 层：主窗口（内存统计 + 优化按钮 + compact 模式）/ 系统托盘（图标或内存占用着色）/ 热键检测；
- ViewModel 层：MainViewModel 协调 UI 与服务；
- Service 层：**ComputerService**（内存优化操作）/ NotificationService（托盘+气球通知）/ HotKeyService（默认 Ctrl+Alt+M）；
- Interop 层：`src/Interop/NativeMethods.cs`（P/Invoke 原生调用）+ ShellInterop（tree 实证）；
- 接口先行：`src/Interfaces/` 下 IComputerService/IHotKeyService/IMemoryService/IOperatingSystem/INotificationService 等（tree 实证）；
- Core：DependencyInjection/Settings（注册表 `HKCU\Software\WinMemoryCleaner`）/Logger（写 Event Viewer）/Localizer/Updater/Migrator。

### 2.2 六类可优化内存区（README.md:94-101 表，逐条摘译——语义比 B06 更清晰）
| 区域 | 机制 | 版本 |
|---|---|---|
| Combined Page List | 冲刷页合并列表（相同内容页合并后的一次性释放） | Win8+/Server2012+ |
| Modified File Cache | 所有固定磁盘的卷文件缓存落盘 | XP+ |
| Modified Page List | 脏页写盘 → 移入 standby | Vista+ |
| Standby List / (low priority) | 清已关闭程序的缓存页（激进全量 / 温和低优先两档） | Vista+ |
| System Working Set | 系统缓存工作集逐出 | XP+ |
| Working Set | 所有用户+系统进程工作集逐出，强迫进程释放非必要内存 | XP+ |

- README.md:105-121 提供可复现实验：开资源监视器观察 Standby 蓝条 → 开关大程序 → 只清 Standby → 蓝条瞬时转入 Free——**"standby 是关闭程序的缓存，清掉立即变 free"**。

### 2.3 触发与编排（deepwiki Automation and Triggers，引 README.md:34-37,66,102-114）
- 四通道：手动 Optimize 按钮 / 全局热键 / 定时 / **空闲内存低于阈值% 自动**；
- 命令行静默模式（可脚本编排）：`/CombinedPageList /ModifiedPageList /ProcessesWorkingSet /StandbyList 或 /StandbyListLowPriority /SystemWorkingSet`；
- 进程排除列表（Process Exclusion List）豁免关键进程。

### 2.4 设置项速览（deepwiki Settings Management，引 README.md:69-78,142-144）
- Always on top / Auto update（24h 检查）/ Close after optimization / Close to notification area；
- Run on low priority（自降进程优先级）/ Run on startup（Task Scheduler+注册表双路）/ Start minimized；
- Show optimization notifications（气球提示）/ Show virtual memory（监控虚拟内存）；
- 全部设置存注册表 `HKCU\Software\WinMemoryCleaner`，docs/ 附 WMC-RESET-SETTINGS.reg 一键重置（tree 实证）；
- 日志写 Windows Event Viewer（eventvwr 可查，README.md:116-125）——**治理操作自带审计日志**。

## 3. 与 Agent 记忆的可迁移机制
1. **六区模型 = 记忆 GC 的细粒度操作菜单**：
   - 每类区域语义（待写盘/可牺牲缓存/工作集/合并重复）不同、代价不同、恢复路径不同；
   - 记忆清理不应是单一 `clear()`，而应暴露"按区域命名"的操作集：
     `flush-pending`（待写记忆落盘）/ `evict-standby`（逐出冷缓存但保留可恢复性）/ `trim-workingset`（缩热集不删内容）/ **`dedup-combined`（合并内容相同的记忆条目——页合并的直译）**。
2. **温和/激进两档**（low-priority standby vs 全量 standby）：同一操作分级暴露，先动最不重要的。
3. **四通道触发 + CLI 可组合**：记忆维护任务（夜间凝缩、定期去重）应是可编程独立操作，而非埋在读写路径里。
4. **排除列表 = pinned 记忆**：关键进程工作集不可动——Agent 记忆应支持钉住条目豁免一切清理。
5. **副作用收敛于接口化服务**（IComputerService/IMemoryService + DI）：对 OS 的全部副作用可替换、可测试——记忆治理操作同理应服务化。
6. **可复现实验文档**：用系统监视器验证清理效果的 README 写法，值得记忆系统做"可观测的治理操作"时效仿。
7. **操作即审计**：每次优化写 Event Viewer——记忆 GC/凝缩也应留操作日志（谁在何时清了什么区域、释放了多少）。

## 5. 局限
- 仅 Windows、需管理员；与 B06 同样的性能争议（清 standby 可能引发回读抖动，README 用"游戏前腾内存"场景自辩）；
- 结构档：NativeMethods.cs 的具体 API 序列未逐行核（P/Invoke 细节缺行号）；
- .NET Framework 4 绑定（无 Core 移植），长期可维护性受限；
- 无自动化测试痕迹（tree 未见 test 工程）——治理类工具的回归风险自担；
- 内存区域名与 B06 不完全对齐（如 Modified File Cache 的归类差异），两仓语义需交叉校对后引用。
