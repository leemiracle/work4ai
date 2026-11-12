# B-05 `giampaolo/psutil`（11.3K★）[结构档-未克隆]
> 来源：deepwiki（索引 2025-10-20, a07e87）+ GitHub README/tree ｜ Python+C ｜ BSD-3
> 一句话定位：跨平台**进程与系统指标**统一 API——ps/top/free/df/netstat 的库化，三层架构（公共 API / 平台抽象 / C 扩展）是"同一接口多后端"的经典实现

## 1. 定位与形态
- 等价 CLI 映射（deepwiki Key Features 表）：ps→`Process`/`process_iter()`、top→`cpu_percent()`、free→`virtual_memory()`/`swap_memory()`、df→`disk_*()`、netstat→`net_connections()`、lsof→`open_files()`、iostat/iotop→`io_counters()`。
- 当前版本 7.1.1（deepwiki 引 `psutil/__init__.py:208`）；Python 2.7 支持在 7.0.0 移除。
- 平台矩阵：Linux/Windows/macOS/*BSD/Solaris/AIX 全支持（deepwiki 平台表，引 `__init__.py:88-134`）。

## 2. 架构与核心模块（来源：deepwiki High-Level Architecture + git tree）
三层架构：
1. **公共 API 层** `psutil/__init__.py`：
   - `Process` 类 + 系统级函数（`cpu_times()/virtual_memory()/swap_memory()/disk_*/net_*`）；
   - 用户唯一入口，平台无关。
2. **平台抽象层**：
   - import 时检测平台并别名引入 `_psplatform`（deepwiki 引 `__init__.py:88-134`）；
   - 每平台一模块（tree 实证）：`_pslinux.py / _pswindows.py / _psosx.py / _psbsd.py / _pssunos.py / _psaix.py`；
   - POSIX 公共代码沉淀在 `_psposix.py`；公共 namedtuple/工具在 `_common.py`/`_ntuples.py`。
3. **C 扩展层**（性能关键路径）：
   - `_psutil_windows.c`：约 70 个函数，走 NtQuerySystemInformation 等原生/未文档 API（deepwiki Platform Strategies）；
   - `_psutil_linux.c / _psutil_osx.c / _psutil_bsd.c / _psutil_sunos.c / _psutil_aix.c`；
   - arch/ 子目录按平台再分（tree 实证 arch/{aix,bsd,linux,osx,sunos,windows,all}/）。
- 平台策略分化（deepwiki 引各平台模块行号）：
  - Linux：主要解析 `/proc`、`/sys` 文本（`_pslinux.py:540-573` 读 /proc/stat 取 CPU times）；
  - Windows：重 C 代码；macOS：Mach 内核 API + sysctl（task_for_pid 需提权）；BSD：kvm 库 + sysctl。

## 3. 关键机制（deepwiki Core Components）
- **PID + create_time 双键**：`Process` 实例由 PID 与创建时间共同标识，防 PID 复用导致"查错进程"（deepwiki Core Components）。
- **`oneshot()` 批量上下文**（deepwiki 引 `__init__.py:479-544`）：一次 `with p.oneshot():` 内取多个属性时缓存系统调用结果，大幅减少重复 syscall。
- **异常翻译**：`@wrap_exceptions` 装饰器把 OS 错误统一为 `NoSuchProcess / AccessDenied / ZombieProcess` 异常层级。
- **版本自检**：import 时校验 C 扩展版本与 Python 模块一致，不匹配报带修复指引的 ImportError（deepwiki 引 `__init__.py:222-239`）。
- 内存指标族（README.md:119-125,170）：
  - 系统级：`virtual_memory()`（含 available 估算）/`swap_memory()`；
  - 进程级：`memory_info()`（RSS/VMS）与 `memory_full_info()`（USS/PSS/shared）。

## 4. 常用 API 速览（README.md 实证行号）
```python
# 内存（README.md:119-125）
>>> psutil.virtual_memory()   # total/available/percent/used/free
>>> psutil.swap_memory()      # total/used/free/percent/sin/sout
# 进程（README.md:170）
>>> p = psutil.Process(pid)
>>> p.memory_info()           # rss/vms
>>> p.memory_full_info()      # uss/pss/shared（platform-dependent）
# 进程枚举与管理
>>> for p in psutil.process_iter(['pid','name','memory_info']): ...
>>> p.suspend()/resume()/terminate()/kill()
```
- `process_iter()` 的 attrs 参数即"一次遍历批量取"设计——与 oneshot 同源的省调用思想。

## 5. 与 Agent 记忆的可迁移机制
1. **平台抽象层模式**：记忆系统的存储/检索后端（SQLite/向量库/文件）应像 `_psplatform` 一样被别名化注入，公共 API 完全不感知后端差异——A 层各库各自造轮子，不如这个自 2009 年起的成熟范式。
2. **PID+create_time 双键**：记忆条目身份 = (id, 生成纪元)，防 id 复用/重写后新旧混淆（与 B03 的状态内版本号同理）。
3. **oneshot() 预取上下文**：一次任务内批量读取记忆时开缓存上下文、退出失效——"记忆读取会话缓冲"，读多写少场景的省调用模式。
4. **异常层级化**：`NoSuchProcess/AccessDenied/ZombieProcess` 对应记忆访问的"条目已删 / 无权读 / 条目存在但不可用（半写入）"三态，调用方可据此降级而非一律裸 try/except。
5. **USS/PSS 区分独占与共享的计费**：记忆成本核算要区分"独占内容"与"共享引用"（与 B02 保留大小同理）。
6. **版本自检**：记忆子系统多组件（schema/索引/存储）混布时，启动时校验互版本，不匹配快速失败。

## 6. 局限
- 快照式只读指标，无内建历史（时间序列要靠外部采样，参见 B09 wgcloud / B12 sysstat）。
- /proc 文本解析对内核版本变化脆弱；Windows 未文档 API 依赖随系统更新漂移。
- 结构档：未克隆，源码细节以 deepwiki 行号引用为准，未逐一复核。
