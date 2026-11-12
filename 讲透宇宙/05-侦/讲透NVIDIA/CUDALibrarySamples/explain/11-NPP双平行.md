# 11 · NPP 双平行：NPP 与 NPP+ 的同构对照

## 角色定位

NPP 域（L13 层，143 节点）是全仓唯一的**同构双目录**结构：NPP/ 与 NPP+/ 各含 batchedLabelMarkersAndCompression/distanceTransform/findContour/watershedSegmentation 四个同主题示例，NPP 独有 nppCanny（C++），NPP+ 独有 cannyEdgeDetectorPython 与 floodFillVariousRegionTypes。两条产品线的差异全部编码在 API 前缀：NPP 用全局 `nppi*` 函数，NPP+ 用 `nppPlusV::` 命名空间（头文件 `#include <nppPlus/nppPlus.h>`，batchedLabelMarkersAndCompressionNPPPlus.cpp:20）。

## 内部结构

以两份 698/707 行的 batchedLabelMarkers 为镜像样本：NPP 版调全局 `nppiLabelMarkersUF_8u32u_C1R_Ctx`（batchedLabelMarkersAndCompression.cpp:334）与批量版 `nppiLabelMarkersUFBatch_8u32u_C1R_Advanced_Ctx`（:523）；NPP+ 版逐行对应换 `nppPlusV::nppiLabelMarkersUF_8u32u_C1R_Ctx`（NPPPlus.cpp:340）与 `nppPlusV::nppiLabelMarkersUFBatch_...`（:529），压缩步骤同理（NPP :401 vs NPP+ :407）。两端各带一份 **1160 行 vendored dirent.h**（Toni Ronkko MIT 实现，dirent.h:1-8 版权头）——Windows/MSVC 无 POSIX 目录接口，两份副本同源，图谱按共享枢纽原则只建 file 节点不深析。

## 外部连接

两线的"厚薄"并不对称：watershedSegmentation 在 NPP 是 115 行单图循环（watershedSegmentation.cpp:91-96 的 GetBufferSize+Segment 两调），NPP+ 版 503 行带批量、多 pass 与着色输出（watershedSegmentationNPPPlus.cpp:232 GetBufferSize、:261/:384/:444 三处 Segment）——NPP+ 才是功能全量版。Canny 线则跨三形态：NPP/nppCanny 有 C++（npp_canny_simple.cpp）+**同目录 Python 孪生**（npp_canny_simple.py）+BLOG.md，NPP+/cannyEdgeDetectorPython 的 cannyEdgeDetector.py（164 行）做多分辨率扫描性能测试——"NPP 域无 Python"的直觉是错的。

## 数据流

batchedLabelMarkers 主链两段式：LabelMarkersUF 无并查集标记（逐图 GetBufferSize :320→标记 :334；批量 :523）→CompressMarkerLabels 压缩标号（逐图 :391/:401；批量 :616）。NPP+ 数据流一致，差别只在调用是否带命名空间限定——把两份文件 diff 开读是最快的 API 迁移教材。

## 设计决策

NPP+ 的命名空间化是版本共存策略：`nppPlusV::` 允许新旧两套符号在同一进程链接不冲突，示例目录双平行本身就是迁移指南。`_Ctx` 后缀（显式 NppStreamContext）是两线共同的无默认流依赖姿势；`Batch_..._Advanced` 变体接受逐图尺寸数组（非常量 batch），弥补老批量 API 的等尺寸限制。vendored dirent.h 的取舍是示例工程的典型妥协：为 Windows 编译可用引入第三方单头，代价是两目录重复维护。

## 新人提示

学 API 迁移读 batchedLabelMarkers 双版 diff（约 20 处前缀差异）；学功能全量看 NPP+ watershed；比较性能数据读 NPP+/cannyEdgeDetectorPython 的分辨率扫描输出。 dirent.h 不要改也不要在 NPP+ 目录重新引入第三份——它只在 MSVC 下被 include（`#if defined(_MSC_VER)` 守卫）。测试图 Lena/coins 等 .raw 以固定尺寸硬编码进源码（watershedSegmentation.cpp:34 文件名表 + :67 ROI 表），改图需同步改两处。
