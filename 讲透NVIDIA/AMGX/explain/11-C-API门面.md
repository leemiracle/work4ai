# 11 C API 门面（amgx_c.h / amgx_c.cu / amgx_config.h）

## 角色定位

C API 是 AMGX 对外唯一稳定出口：Fortran/Python/求解器集成全部经此进入，动态库符号边界划在 `include/amgx_config.h`（184 行，ABI 定义）与 `include/amgx_c.h`（611 行，72 个导出声明）之间，实现全压在 `src/amgx_c.cu`（5358 行，库对外最大文件）。三方语言靠这套纯 C 接口免受 C++ 模板地狱，代价是所有类型擦除为不透明句柄（AMGX_solver_handle 等 void** 风格传出）。

## 内部结构

导出宏三分支（`amgx_c.h:8-26`）：SWIG 下 AMGX_API 展开为空、Windows 走 `__declspec(dllexport/dllimport)`（L12-18）、其余平台 `__attribute__((visibility("default")))`（L21）。真实导出声明 72 个，形如 `AMGX_RC AMGX_API AMGX_xxx`：从 `amgx_c.h:150` AMGX_get_api_version、`amgx_c.h:165` initialize、`amgx_c.h:167` initialize_plugins、`amgx_c.h:169` finalize，到 `amgx_c.h:575` matrix_upload_distributed、`amgx_c.h:603` solver_resetup 收尾（勘误：常见说法"81 个导出"是 AMGX_API 的原始 grep 命中数，含 9 行宏定义/条件编译上下文）。ABI 核心 `amgx_config.h:79-89` AMGX_ModeNums 定义四个精度维度的位组合基数（MemorySpaceBase=1 起，逐维相乘）；`amgx_config.h:91-97` AMGX_ASSEMBLE_MODE 宏按"内存空间×向量精度×矩阵精度×索引位宽"组装 mode 整数；`amgx_config.h:99-100` 的 GET/SET_MODE_VAL 宏做按域存取；`amgx_config.h:102-127` AMGX_Mode 枚举列出全部合法组合（hDDI=8192、dDDI=8193 等）。头部 L8-9 的 WARNING 明示契约："Always use enums, do NOT use knowledge about the formulas for AMGX_Mode because it might change in the future"——数值布局是公开 ABI 的一部分但语义上禁止依赖公式。

## 外部连接

`amgx_config.h:132` 起的 AMGX_FORALL_BUILDS 宏族（host/device/complex 三组）把 mode 枚举批量展开成代码行，amgx_c.cu 49 处 `switch (mode)` 分派点全靠它填充 case。实现侧的标准范式见 getResourcesFromSolverHandle（`amgx_c.cu:45-76`）：AMGX_TRIES/AMGX_CATCHES try-catch 包裹 → switch(mode) → AMGX_CASE_LINE 宏（`amgx_c.cu:58-60`）内 get_mode_object_from<CASE,...> 按编译期 mode 取回正确模板实例 → AMGX_FORALL_BUILDS + AMGX_FORCOMPLEX_BUILDS 双宏展开。每个 C 入口先 getResourcesFrom*Handle 三姊妹取出 Resources 再干活（`amgx_c.cu:45` solver 版、`amgx_c.cu:80` matrix 版、`amgx_c.cu:108` vector 版）。典型入口 AMGX_solver_setup 在 `amgx_c.cu:2745`。辅助 `amgx_c_common.cu` 仅 54 行。mode 的运行时去向：get_mode_from 从句柄对象头读回，模板世界按 mode 整数定位实例。

## 数据流

标准调用链：amgx_initialize → amgx_config_build（读配置字符串）→ amgx_matrix_create+upload（host/device 指针均可，`src/tests/capi_upload_tests.cu` 验证四类指针等价）→ amgx_solver_create+setup（amgx_c.cu:2745）→ amgx_solver_solve → download/destroy/finalize。mode 在 create 时烙进每个对象，之后 setup/solve 的 switch 用它选模板实例，全程无 RTTI。错误路径：C++ 异常在 AMGX_CATCHES 捕获翻译成 AMGX_ERROR 码返回，绝不穿透 C 边界（`src/tests/capi_graceful_failure.cu` 专测此契约）。

## 设计决策

其一，句柄+mode 整数实现 C 边界上的类型擦除，替代 C++ 虚表——mode 本质是"手工 vtable 索引"。其二，警告式 ABI：枚举数值用宏组装保证自洽，但显式警告外部不得写死数值——介于强 ABI 与松 ABI 之间的务实折中。其三，49 处 switch 靠宏族批量生成，加新 mode 只改 amgx_config.h 宏列表即可全量扩散。实测发现一处源码陈旧注释：hZZI/hZCI/hCCI 行尾的 `// mode == 8192/8448/8464`（`amgx_config.h:116-118`）是从 DDI 系复制粘贴的错值——编译实测 hZZI=9008、dZZI=9009，枚举值本身正确，注释失真。

## 新人提示

绑定层开发者只认 amgx_c.h 的 72 个声明+amgx_config.h 的枚举标识符，永远用 AMGX_ASSEMBLE_MODE/枚举名，不写 8192 这类字面量（注释都可能骗你，见上）。排查"BAD_MODE"沿 switch 的 default 分支（如 amgx_c.cu:63-64）入手，多半是 host build 里传了 device mode。加新导出函数照抄 L45-76 范式：TRIES/CATCHES+getResources+CASE_LINE 三件套，缺一件就是资源泄漏或异常穿透。amgx_c.cu 5358 行不要通读，49 个 switch 是同一模板的复制，读懂 L45-76 即读懂全部。
