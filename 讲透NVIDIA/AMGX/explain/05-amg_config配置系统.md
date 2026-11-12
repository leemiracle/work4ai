# 05 · amg_config 配置系统：类型擦除、scope 树与 62 份预设 JSON

## 角色定位

配置系统是 AMGX 的"基因层"：一个 AMG_Config 携带从求解器类型到粗化细节的全部参数，以 scope（作用域）树组织嵌套求解器（PCG 外层+AMG 预条件+smoother 各占一个 scope）。机制在 include/amg_config.h+src/amg_config.cu（1545 行），但参数模式定义不在本文件——151 条 registerParameter 集中在 src/core.cu:307 起的 registerParameters()（solver 默认 AMG :382、selector 默认 PMIS :459）。62 份预设 JSON（src/configs/）的 configures 边全部汇入 amg_config.cu——它们最终都被这里的解析器吃进来。

## 内部结构

三层。①存储：`Parameter` 是 64 字节裸存储的类型擦除（amg_config.h:26-35 `char data[64]`），模板 set/get 直接 reinterpret_cast（:50-76），字符串限长 64（:52-57）；`ParameterDescription` 挂类型/描述/默认值/合法值（:107-118，合法值有 min-max 与枚举两模式 :80-98）。②解析：`parseParameterString`（amg_config.cu:60）先探测 JSON（rapidjson 全局 Document :28），失败走 key=value；`getConfigVersion`（:148-180）抠 config_version（1/2，非法 FatalError :167）；`convertToCurrentConfigVersion`（:185-249）把 v1 老参数名翻译上来（smoother_weight→relaxation_factor :218、JACOBI→BLOCK_JACOBI :226）且 v1 禁 scope（:207-210）。字符串逐行 setParameter（:303-311）。JSON 路：parse_json_file（:610）→Parse→`import_json_object`（:545）递归遍历，遇 Object 自动注入 "scope" 键（:580-582）实现嵌套。③scope：m_solver_list 六键名（solver/preconditioner/smoother/coarse_solver/cpr 两段，:1412-1416）决定切 scope 时机；getParameter 四参重载顺带返回 new_scope，工厂 allocate 链靠它串起子求解器配置。

## 外部连接

上游：C API 的 setup 把 JSON 路径/参数串喂进来（parseParameterStringAndFile :104，str 先于 file）；预设名由 testframework 解析成 src/configs 路径。下游：全库工厂 allocate 第一参都是 AMG_Config+scope；registerParameters 在 initialize 时调（core.cu:778）。schema 自省：getAllSolvers/getAllCoarseGenerators（core.cu:210/133）遍历已注册工厂动态生成合法值清单——参数描述与注册表自动同步。restricted 参数（determinism_flag 等）只许 default scope（amg_config.cu:526/1346 双守卫）。

## 数据流

两条输入殊途同归：JSON 嵌套对象→递归 import_json_object→(scope,name)→setParameter；key=value 串逐行 setParameter。setParameter 经 setNamedParameter 类型分发（:428-452，按 param_desc 的 typeid 把字符串转 AlgorithmType/ViewType/NormType 等枚举）落进 m_params（键=scope::name）。消费端 getParameter<T>(name,scope) 找不到按默认值兜底。62 份预设即 62 个入口快照：PCG_V.json 定义 main→PCG→preconditioner amg→V cycle D2→smoother jacobi 四层嵌套；AGGREGATION_JACOBI.json 单层 flat——两种典型形态。eigen_configs 8 份是 key=value 格式特征值配置。

## 设计决策

64 字节定长而非 union/variant 是 C++03 时代的务实选择，代价：字符串 64 上限、无类型安全（get 错类型得垃圾不报错）。config_version 内嵌迁移而非双解析器：v2→当前是空操作（:241-245）、v1 走翻译表，老配置永不失效。scope 用字符串拼接而非树结构体，查询 O(map)，换来 JSON 与 key=value 同构。默认值集中注册表+工厂枚举自动同步是全库最值得抄的设计。坑：getParameterStringFromFile（:327）逐行 trim+跳 # 注释（:348-355）后以 ", " 拼接（:355），key=value 文件里换行等价逗号。

## 新人提示

查参数权威定义去 core.cu:307-540 读原文，README 可能滞后（strength 描述漏 AFFINITY 已是一例）。写新预设从最接近的 JSON 拷改；嵌套 "scope" 键名可自定义（PCG_V 用 main/amg/jacobi）。报 "Scopes only supported with config_version=2" 就是 v1 串写了 scope 前缀（:207）。调试解析开 verbosity_level>2（parseString :263-272 提前探测）。determinism_flag 等必须在顶层，放子 scope 会被 :526 守卫拦下。改存储上限记得同步 amg_config.h:31 检查与文案。
