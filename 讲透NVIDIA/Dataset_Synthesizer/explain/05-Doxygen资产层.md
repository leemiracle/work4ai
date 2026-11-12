# 05 · Doxygen 资产层：332 页类详情与 563 个图源缓存

## 角色定位

`Documentation/ClassDetails/` 是全仓**体积占比最大的"目录"——895 个生成文件占图谱 1373 个分析文件的 65%**，也是"文档即构建输出"的完整标本：它不是手写文档，而是 Doxygen 1.8.8 从源码批量生成的 HTML API 参考（`index.html:6` 的 generator meta 实证），与 `NDDS.pdf`（readme 指引见 `readme.md:19`）并为 Documentation 两态。对新人价值：比源码更快的类 API 速查入口（带继承图/协作图/成员表/源码跳转）；对静态分析价值：文件名本身编码了符号命名规则，解码即得类名。生成配置 Doxyfile **并未入仓**（全仓 find 无 Doxyfile*）——想本地重生成文档得自建配置。

## 内部结构

两层（对应图谱 L09/L10）：

- **可读层 332 文件 = 328 html + 4 css**：116 个 `class_*.html` 类详情页（每个 UCLASS/USTRUCT 一页，如 `class_a_d_r_scene_manager.html` 对应 ADRSceneManager，页首 `<title>` 即 "ADRSceneManager Class Reference"，`class_a_d_r_scene_manager.html:7` 实证）；50 个 `*_8h_source.html` 带行号高亮的源码浏览页（含 include 依赖跳转）；`index.html` 总入口、`annotated.html` 注解类列表、`hierarchy.html` 继承树；search/ 子目录 52 个 html 索引页。
- **支持层 563 文件 = 202 dot + 202 md5 + 159 js**：dot 是 graphviz 类继承/协作图的**源文件**（每类两个：`__inherit__graph` 与 `__coll__graph`）；md5 是 dot 的渲染缓存指纹——内容未变 Doxygen 跳过重渲染，是增量构建机制的直接证据；js 是 `annotated.js`（类列表数据 103 行：`annotated.js:1` 开 `var annotated =`，`:3` 首条即 ADRSceneManager）+ `class_*.js`（每类成员索引）+ search/ 的 `all_0.js~all_N.js` 全文搜索分片与 `search.js`。另有 235 个 png（dot 的渲染产物）与 201 个 map（图片热区映射）——图谱把 png 归入二进制排除清单（`.understandignore:4` 的 *.png），只统计 dot/md5/js 三类文本源。

## 外部连接

向上直连 L02-L05 的 C++ 源码层：`class_*.html` 页内链向 `*_source.html` 源码页，源码页内链向被 include 的头文件页——形成"API 参考→源码→依赖图"闭环；`annotated.js` 是 DeepWiki/静态站点想做类索引时的现成数据源。与仓库根 `readme.md:19` 的指引（"For further details, please see .../Documentation/NDDS.pdf"）及 `readme.md:11` 的 NVDU 可视化工具指引呼应，HTML 层是 pdf 的超集活版本。

## 数据流（命名解码算法）

Doxygen 文件名转义两规则，**解码是逆向工程刚需**：

1. **大写字母 → 下划线+小写**：类名每个大写字母前插 `_`。ADRSceneManager → `a_d_r_scene_manager`；前缀 A/U/F/I（Actor/UObject/Struct/Interface 记号）也被同样拆解——`class_a_n_v_scene_capturer_actor.html` 反解为 ANVSceneCapturerActor。
2. **原名内下划线 → 双下划线 `__`**：NVSceneMarker_FocalPoint 中的 `_` 转义为 `__`。
3. **两规则叠加产生三连下划线 `___`**：`..._marker` + `__`（原名下划线）+ `_f`（FocalPoint 的 F 拆解）= `class_a_n_v_scene_marker___focal_point`（页内 `:7` 行 title 即 "ANVSceneMarker_FocalPoint Class Reference"）——看到 `___` 就知道原名有个下划线且下一个字母大写。**双料铁证**：`annotated.js:65-66` 里 UNVObjectMaskMananger（源码双 n 拼写勘误 `NVObjectMaskManager.h:68` 原样进文档）及其派生 `UNVObjectMaskMananger_Stencil` 的页面文件名是 `class_u_n_v_object_mask_mananger___stencil.html`——双 n+三连下划线一屏同现；改名重定向的终点类也有页：`class_u_n_v_scene_feature_extractor___vertex_color_mask.html`（对应 `DefaultEngine.ini:24` 的 redirect 目标、源码 `NVSceneFeatureExtractor_ImageExport.h:148` 的 VertexColorMask）。

生成流：Doxygen 扫描 Plugins 头文件 → 产 dot（图源）→ 对比 md5 决定是否重渲染 png → 写 html/js。想刷新文档：装 Doxygen 重跑即可，全目录皆可再生——**这层资产永远不该手工编辑**。

## 设计决策

1. **生成物进 git**：895 个文件全提交进仓库——2018 年的选择：让无 Doxygen 环境的用户直接开 index.html；代价是每次文档刷新的 diff 巨大且 LFS 外的噪声提交。
2. **md5 缓存指纹**：202 个 md5 与 dot 一一对应，重跑时未变图跳过渲染——构建系统级优化泄漏到产物目录，是研究"文档 CI"的天然样本。
3. **搜索前端本地化**：search/ 分片 js 让 API 站无后端也能全文搜索（Doxygen 1.8.x 静态搜索方案），离线可用——与插件本身的离线工具气质一致。

## 新人提示

- 手工拼 Doxygen URL 先过命名解码：找 NVSceneMarker_FocalPoint 类页，正确 URL 是 `Documentation/ClassDetails/class_a_n_v_scene_marker___focal_point.html`（三连下划线），漏一个 `_` 就是 404。
- `*_8h_source.html` 里的 `8h` 也是转义：原名 `NVDataObject.h` 的 `.` 转 `_8`，`h` 是扩展名残部——搜源码页用 `*8h_source` glob。
- 类详情页三看：顶部继承图（谁派生谁）、Public Attributes 表（即 UPROPERTY 清单）、底部源码链接；比开 IDE 快。
- 想统计类清单别解析 html——直接 `grep '"class_' Documentation/ClassDetails/annotated.js` 一行拿全 116 类。
