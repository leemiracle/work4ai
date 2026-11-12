# explain 01 · data_generation/blocks_render_image.py——Isaac Sim 合成数据生产线

## 角色定位

4825 行、约 180 个函数/类，全仓最大单文件，是基准的**地基**：一个文件包办"程序化搭积木 → 多方位渲染 → 遮挡可见性掩码 → 逐任务真值 JSON → 异步 S3 上传"。上游只有 Isaac Sim 运行时，下游是一切 runner 与评测脚本的 `sample_NN/view_NN/offset_X_fov_Y_dist_Z/` 目录约定（inference/view_utils.py:57 反向消费）。

## 内部结构

启动序有时序硬约束：Kit 设置必须在 `SimulationApp` 之前（data_generation/blocks_render_image.py:33），随后 headless 起 App（data_generation/blocks_render_image.py:36）、import Replicator（data_generation/blocks_render_image.py:54）。难度驱动器 5 级×多场景×4 基础方位（:124-131）。资产三形态由 `BLOCK_SHAPE` 切换（:293）：UV 立方体/纹理盒/USD 资产（默认 `soup_can` data_generation/blocks_render_image.py:297）。真值子系统按 `GENERATE_GT_T1..T11` 开关量产（:191-203），task10/11 做跨视角差集；几何枢纽 `save_scene_json`（:574）——`height_map` 高度图即场景的完整代数描述（`total_blocks` 顺带求和 data_generation/blocks_render_image.py:577）。

## 外部连接

输出契约：`_view_fov_dir` 生成 `offset{X}_fov{Y}_dist{Z}` 子目录（data_generation/blocks_render_image.py:603），`gt.json` 由 `_update_gt_json` 增量合并（data_generation/blocks_render_image.py:620），被 evaluation/evaluation_text.py:205 读取。S3 栈四件套：client（:502）→ 执行器（:518）→ 上传（:525）→ 收尾屏障（:547），渲染不等网络。质控配套 summarize_gt_stats.py 拼缩略图网格（data_generation/summarize_gt_stats.py:47）+字段直方图（:154）。

## 数据流

单场景循环：采样 height_map → 逐方位渲染（`_set_camera_to_azimuth` :836）→ **back-to-front 排序**（列序 data_generation/blocks_render_image.py:733、块序 data_generation/blocks_render_image.py:761）→ `_build_mask_back_to_front`（:789）从远到近叠掩码 → 像素级可见块集合（`get_visible_blocks_from_replicator` :858）→ 各 task 真值落盘（主任务 MCQ 正确字母 data_generation/blocks_render_image.py:1905、data_generation/blocks_render_image.py:1961）→ scene.json + S3 异步上传。RTX 质量旁路注入：path tracing（:423）与 DLSS execMode（:435-438）。

## 设计决策

1. **像素级真值优于几何投影**：可见性由分割注解器+深度排序实证（data_generation/blocks_render_image.py:789、:858），杜绝"算法可见但物理被挡"的脏标签。
2. **height_map 单一真相源**：列数/层数/隐藏块（:1591）等计数真值全部可从高度图推导，渲染只是它的"视图函数"。
3. **难度与视角变体解耦**：方位与 offset/fov/dist 正交组合（:603），一套场景出多难度样本。
4. **渲染上传异步化**：执行器+屏障（:518-547）保单文件吞吐。
5. **GT 按 task 前缀成组**（:191），下游按需取子集。

## 新人提示

先读 data_generation/blocks_render_image.py:124-131（难度驱动）与 :191-203（GT 开关表）建全局感，再追 `_build_mask_back_to_front`（:789）一条链到底；跑 summarize_gt_stats.py 看拼贴图比读代码快。改资产形态只动 `BLOCK_SHAPE`/`ASSET_BLOCK_MODE`（:293、:297），别碰几何代码。切记 :33 的时序——Kit 设置晚于 `SimulationApp` 会静默失效。
