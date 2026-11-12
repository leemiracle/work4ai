# 01 · nvtx3 C/C++ 头族：nvToolsExt.h 与 nvtx3.hpp

## 角色定位
`c/include/nvtx3/nvToolsExt.h`（1688 行）是整个 NVTX 体系的 C API 锚点——图谱 fanIn=72，全仓被引最多；`c/include/nvtx3/nvtx3.hpp`（4992 行）则是面向 C++ 用户的 header-only RAII 封装。两者共同构成"零成本标注"的门面：声明与 Doxygen 文档一体（`README.md:81` 与 `README.md:90` 分别给出两种 include 示例），实现细节全部下沉到 nvtxDetail 目录。

## 内部结构
nvToolsExt.h 的四个层次：
1. **核心事件 API**——`nvtxMarkA:784`（时间点标记）、`nvtxRangePushEx:1023`+`nvtxRangePop:1114`（线程栈区间）、`nvtxRangeStartEx:863`+`nvtxRangeEnd:942`（跨线程句柄区间）。A/W 后缀=ASCII/宽字符双编码入口。
2. **事件属性结构** `nvtxEventAttributes_v2:597-688`——消息/类别/颜色/负载的联合槽位描述，`version+size` 首字段保证前向兼容。
3. **域 API**——`nvtxDomainCreateA:1617`/`nvtxDomainDestroy:1642`、字符串注册 `nvtxDomainRegisterStringA:1551`、类别命名 `nvtxDomainNameCategoryA:1404`；资源属性 `nvtxResourceAttributes_v0:1235-1292`。
4. **注入入口** `nvtxInitialize:495` 与文件末尾的版本保护 include（约 `:1681-1686`，`NVTX_IMPL_GUARD` 后引入 `nvtxDetail/nvtxTypes.h` 与 `nvtxDetail/nvtxImpl.h`）。

nvtx3.hpp 的类地图（`namespace nvtx3:801`）：`semantic_base:911` 继承基座 → `domain:1049`、`color:1339`（ARGB+CSS 名）、`category:1446`/`named_category_in:1529`、`registered_string_in:1755`（字符串句柄复用）、`message:1978`、`payload:2112`、`schema:2225`/`payload_data:2295`（C++ 结构化负载）、`event_attributes:2439`（链式 builder）、`scoped_range_in:2640`（析构自动 pop 的核心人体工学件）。

## 外部连接
领域扩展头全部依赖主头：`nvToolsExtPayload.h`（1794 行）的 schema 体系 `nvtxPayloadData_t:859-990`/`nvtxPayloadSchemaEntry_t:991-1078`/`nvtxPayloadSchemaRegister:1343`；`nvToolsExtSync.h`（412 行）`nvtxDomainSyncUserCreate:308`；`nvToolsExtCuda.h` 的 `nvtxNameCuDeviceA:84`/`nvtxNameCuStreamA:121`；语义头四件套（`nvToolsExtSemanticsTime.h` 49 行/`SemanticsScope.h` 55 行/`SemanticsCorrelation.h` 68 行/`SemanticsCounters.h` 140 行）为 Payload 提供类型化语义槽。下游：C++ 测试 `tests/src/CoverageCpp.cpp` 验证封装层全覆盖，Doxygen C++ 站（`docs/doxygen-cpp/`，63 页）渲染此类地图。

## 数据流
用户构造 `event_attributes`（或直接传字符串）→ push/mark 调用展开为 C API → 未注入工具时经 nvtxDetail 降级为空操作；注入工具后跳转工具函数表（`nvtxInitialize` 或首次调用的懒加载触发）→ 工具把事件连同属性槽位写入自己的时间线缓冲。C++ 侧 `scoped_range_in` 构造即 push、析构即 pop，异常路径也能正确闭合区间。

## 设计决策
- **A/W 双编码**而非统一 wchar：Windows 与 POSIX 的宽字符尺寸不同，双入口让各平台选最小阻力路径。
- **_v2/_v0 后缀版本化结构**：以 `version+size` 开头的可扩展布局取代宏重命名，工具可安全读旧结构。
- **声明/实现分离**：主头只留声明+文档，实现全部进 nvtxDetail（被 21 个内部头分摊），保证公共 API 面稳定。
- C++ 层**零虚函数**的值语义设计：封装即内联透传，不引入额外开销。

## 新人提示
先读 `README.md:49`（标注分类）再看 nvtx3.hpp 的 `scoped_range_in:2640`——90% 场景只需要 `nvtx3::scoped_range`。改主头时注意 `tests/scripts/validate-source-files.sh` 的版权头/行尾校验（CI Source Validation 强制）；新增导出函数务必同步 `tests/src/UseExportedApi.cpp:50` 的 X-macro 清单（`:55` 注释保留了 `nm -D` 自动生成配方），否则导出面测试不会覆盖到。
