# 02 · NCCL 参数系统 — misc/param.cc、include/param.h 与 param/ 子系统

## 一、角色定位

NCCL 有数百个 `NCCL_*` 环境变量（channel 数、算法开关、调试级别……），参数系统是它们统一的读取入口。v2.32.3 是**双轨制**，正处一代向二代迁移中途：

- **旧轨（主力）**：`src/include/param.h:21-31` 的 `NCCL_PARAM(name, env, deftVal)` 宏 + `src/misc/param.cc` 运行时支撑，宏在调用点展开成 `int64_t ncclParam##name()` 函数并内嵌静态缓存。全库 **232 处**调用（grep 实测，如 src/init.cc:64-77）。
- **新轨（v2.32 落地）**：`src/include/param/param.h:37-42` 的 `DEFINE_NCCL_PARAM(name, type, key, default, flags, parser, desc)` 定义强类型 `ncclParam<T>` 全局对象，构造时自动登记进 `ncclParamRegistry`，经 `src/param/c_api.cc` 暴露为 `src/nccl.h.in:938-1019` 的 param C API。目前仅 **10 处**（**2026-11-03 勘误**：原记 11 处，verify-deepseek 全库 grep 实证为 10 = debug.cc 8 个〔第 8 个 `SetThreadName` 在 :479，不在 43-117 段〕+ param/param.cc 2 个自举参数）。

两轨共享基础设施：conf 文件加载（`src/misc/param.cc:27-67`）、env plugin 链（`src/plugin/env.cc`）、缓存禁用策略（`src/param/param.cc:23-41`）。113 行的 param.cc 是参数"读环境"的最后一公里。

## 二、内部结构

### 旧轨：两段式宏展开

`NCCL_PARAM(Name, "ENV_NAME", default)` 在调用点生成 `ncclParamName()` 函数，内含 `static int64_t cache = INT64_MIN` 与 `static int8_t noCache`——缓存未命中（一次 relaxed 原子读）才进 `src/misc/param.cc:78-108` 的 `ncclLoadParam` 慢路径。**第一段在调用点（每参数一份缓存，热路径零锁），第二段集中管理（进程级互斥锁）**——这就是"两段式展开"。

`ncclLoadParam` 逻辑：首次用 `ncclParamIsCacheDisabled` 决定 noCache（`src/misc/param.cc:83`）；缓存命中直接返回（`src/misc/param.cc:85-87`）；`ncclGetEnv` 取值（`src/misc/param.cc:90`）；`strtoll(str,&end,0)` 解析（`src/misc/param.cc:96`）——base 0 意味着 `0x` 十六进制、前导 0 八进制都合法且数字前缀容错，完全非数字回退默认并 ATTN（`src/misc/param.cc:98-100`）；非 noCache 才写缓存（`src/misc/param.cc:106`）。

conf 文件三级优先级在 `src/misc/param.cc:52-67`：`NCCL_CONF_FILE` > `$HOME/.nccl.conf` > `/etc/nccl.conf`；setEnvFile（src/misc/param.cc:27-50）逐行解析 KEY=VALUE 喂给 ncclOsSetEnv——本质是"批量 setenv"。触发链：参数首读 → `ncclGetEnv`（`src/misc/param.cc:110-113`）→ `ncclInitEnv`（`src/init.cc:196-199`）→ `ncclEnvPluginInit`（`src/plugin/env.cc:96-97`）→ `initEnv()`（`src/misc/param.cc:69-72`）→ conf 解析。

### 新轨：模板对象 + 注册表 + C API

`DEFINE_NCCL_PARAM` 生成 `constexpr char nameKey[]`、全局 `ncclParam<T>` 对象与键唯一性 guard（`src/include/param/param.h:37-42`）。`ncclParam<T>` 模板（`src/include/param/param.h:52-174`）持有 info 元数据、默认值、当前值、字符串落地 cstrData、srcStr 值来源、mutex、`atomic<bool> loaded`、可插拔 parser。`ensureLoaded`（`src/include/param/param.h:134-153`）：已加载且带 CACHED flag 且不在 NO_CACHE 名单 → 零锁快路径；否则持锁 `loadValue`（`src/include/param/param.h:156-173`）——经 `ncclParamEnvPluginGet`（`src/param/param.cc:47-56`）取串，`parser.resolve+validate`，失败回默认并记来源。

六个 flag（`src/include/param/common.h:22-32`）：PUBLISHED（进官方文档，dump 默认只显示）、DEPRECATED、CACHED（缓存后改了不生效）、UNUSED、NO_ENVPLUGIN_INIT、SENSITIVE（dump 时 `<redacted>`）。

**注册表**（`src/include/param/param_registry.h:45-81`）：静态类 + `registryState{map,mutex}`，state 经 **C 链接单例 `ncclParamRegistryInstance()`**（`src/param/param_registry.cc:11-14`）取得——NCCL 被静态链接进多个 DSO 时仍共享同一张 map（`src/include/param/param_registry.h:31-34`）。参数对象在 `main()` 前完成注册，外部 .so 在 dlopen 时注册；重复 key 报错（`src/param/param_registry.cc:19-24`）。

**C API**（`src/param/c_api.cc`）：`ncclParamBind` 把 mapEntry* 当不透明 handle，bind 时三查（UNUSED/DEPRECATED/非 PUBLISHED 警告，`src/param/c_api.cc:28-66`）；typed getter 先验 typeId 再 getRawData（`src/param/c_api.cc:72-94`）；GetStr 用 thread_local buffer 保指针有效期（`src/param/c_api.cc:109-111`）；GetAllParameterKeys/DumpAll 默认只列 PUBLISHED（`src/param/c_api.cc:124-154`）。

**meta 自举**：`NCCL_NO_CACHE` 自身是新轨参数（`src/param/param.cc:20-21`），`ncclParamIsCacheDisabled`（`src/param/param.cc:23-41`）解析它（逗号列表或 ALL）并对自身短路防循环依赖（`src/param/param.cc:24-25`），同时服务新旧两轨（旧轨入口 `src/misc/param.cc:74-76`）。

## 三、外部连接

- **旧轨 include 面**：`src/include/param.h` 被全库 31 个文件 import（图谱实测），`src/init.cc:34`、`src/bootstrap.cc:14` 等靠它声明 `ncclParamXxx()`；跨单元访问另有手写前置声明（`src/init.cc:79-82`）。
- **新轨 include 面**：src/param/*.cc 与 src/debug.cc；`src/include/param/common.h` 特意 C/C++ 双兼容（`src/include/param/common.h:18-21`）。
- **上游**：`src/plugin/env.cc`（env plugin——外部 .so 可接管环境变量来源）。**下游**：`src/nccl.h.in:938-1019` 的 C API 面 → ncclparam CLI 与 RAS/诊断。

## 四、数据流

以 `NCCL_MAX_CTAS`（定义 `src/init.cc:2000`）走一遍旧轨生命周期：① 首次调用 `ncclParamMaxCTAs()` 进 ncclLoadParam；② 全局锁 → 定 noCache 策略 → `ncclGetEnv` 触发 once 链（env plugin init + conf 解析）；③ `strtoll`：设了 8 得 8 并 INFO 打点（`src/misc/param.cc:102`），没设保持默认 INT_MIN（即 `NCCL_CONFIG_UNDEF_INT` 哨兵——旧轨用 UNDEF 表达"用户没说"，src/init.cc:64-77 大量依赖）；④ 写回静态 cache，此后每次调用只是一次原子读，**中途改环境变量无效**——除非 key 进了 `NCCL_NO_CACHE` 名单（每次穿透，可热更）。

## 五、设计决策

1. **宏生成函数而非集中表**：每参数独立符号、读取零间接、缓存对编译器可见；代价是类型单一（int64 一把抓）与无法运行期枚举——正是新轨要补的。
2. **两段式**：慢路径要互斥锁（`src/misc/param.cc:79-82`），若每次读取过锁热路径会被序列化；静态缓存把锁摊销成一次。
3. **conf 用 setenv 而非自建配置树**：conf 值与 env 值走同一条后续管线（plugin/打点全套免费）；三级优先级即"站点配置当兜底"。
4. **新轨 C 链接单例**：跨 DSO 共享 registry 的唯一稳妥做法——C 符号全进程唯一，静态链接多份 libnccl 也不分裂。**SENSITIVE redact 与 bind 三查**：参数系统同时是运维接口，dump 会进工单与日志。
5. **迁移策略**：debug 系先迁新轨，行为参数留旧轨。

## 六、新人提示

- **加参数最小改动**：对应 `.cc` 顶部一行 `NCCL_PARAM(MyFlag, "MY_FLAG", 0);` 即可用 `ncclParamMyFlag()`；要可枚举/带废弃警告走新轨 DEFINE_NCCL_PARAM（参考 `src/debug.cc:43-49`）。
- **调"参数没生效"三板斧**：① 看 NCCL_ENV 日志行（每次命中都有 "set by environment to ..."）；② 变量名必须带 `NCCL_` 前缀（宏内已拼好）；③ 参数首读发生在很早阶段，之后 setenv 已晚。
- **改 `~/.nccl.conf` 不生效**：conf 只在 once 时读一次（`src/misc/param.cc:70-71`）。
- 旧轨 `strtoll` base=0 的坑：纯字符串值（如 NCCL_DEBUG=info）回退默认且只 ATTN——字符串型参数实际走新轨 parser（`src/include/param/parser_default.h`）。
- 看全部参数清单：跑 `ncclparam -l` 或 `ncclParamDumpAll()`；`NCCL_PARAM_DUMP_ALL=TRUE` 才含未公开参数。
