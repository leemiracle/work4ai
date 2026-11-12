# 讲透 soma-retargeter（NVIDIA）

BVH 人体动作 → 人形机器人关节 CSV 的 Warp/Newton IK 重定向工具（v0.2.1 @ cbdb2b49，Apache-2.0，动作数据另附 Sample Data Evaluation License）。

## 产物状态

| 产物 | 状态 | 位置 |
|---|---|---|
| DeepWiki 全量 | ✅ 34 页 100% | `deepwiki/` |
| 知识图谱 | ✅ 766n/866e/10 层/11 步 tour，validator 0 issues，fingerprints 548@cbdb2b49 | 仓内 `.understand-anything/knowledge-graph.json` |
| Onboarding | ✅ 8 节 | `onboarding/ONBOARDING.md` |
| Explain | ✅ 3 篇 | `explain/01-soma-retargeting-pipeline.md`（主管线 608 行）/ `02-ik-weight-optimizer.md`（优化器 3004 行）/ `03-usd-io.md`（USD IO 893 行） |

## 勘误（文档/直觉 vs 源码实证）

1. **"五家机器人 manifest 同构、都用 URDF"——不成立。** unitree_g1 的 manifest 是唯一用 `targets` 数组包裹的（`soma_retargeter/assets/robotics/unitree/g1/manifest.json:3`），且唯一走 MJCF（同文件 :6 `"xml_path": "desc/mjcf/g1_29dof_rev_1_0.xml"`）；其余四家是顶层 `name`+`urdf_path` 扁平形态（如 `soma_retargeter/assets/robotics/booster/t1/manifest.json:2-5`）。`robot_registry.py:34` 的类文档明示 targets 数组是可选多目标语法。写 manifest 解析代码时必须兼容两种形态。

2. **机器人目标名命名不统一。** 官方名单（README.md:74-80）：`agibot-a3t3` 用连字符，`agibot_x2ultra`/`unitree_g1` 等用下划线。脚本批量传参/做字符串归一化时会踩坑，须逐字照抄 manifest 的 name 字段。

3. **优化器文档与出厂配置脱节两处。** ① documentation/ik-weight-optimizer.md:22-25 称捆绑默认配置 `"input_folder": ""` "不能不改直接跑"，实际 `app/tools/assets/ik_optimizer/ik_weight_optimizer_config.json:3` 已填 `"../../../../assets/motions/optimizer"`，开箱即可跑；② 同文档 :16/:55 的 `unitree_h1` 全部是"配置器新增机器人"教学语境，仓内并无 H1 资产，默认 target_type 是 `unitree_h2`（配置 :2）。

4. **两份出厂配置的 extra_robot_paths 指向不存在的目录。** 转换器 `assets/default_bvh_to_csv_converter_config.json` 与优化器配置都写 `"assets/robotics"`，但仓库根的 `assets/` 下只有 motions/docs，机器人资产实际在包内 `soma_retargeter/assets/robotics/`。该路径相对解析后是死目录，`robot_registry.py:132-134` 的 `register_robots_path` 不校验存在性、os.walk 静默空扫——功能不炸（内置注册表兜底），但文档声称的"让优化器发现 H1"路径（ik-weight-optimizer.md:107）在默认布局下永不生效。

5. **"pip install 就能用 GUI 和捆绑动作"——错。** `pyproject.toml:29` `exclude = ["app*", "assets*"]`，:31-32 package-data 只打包 `soma_retargeter/assets/**`。GUI 转换器（app/）、配置器、示例 BVH 与参考 CSV（assets/motions/）都不随 wheel 分发，完整功能必须 clone 仓库 + `git lfs pull`（installation.md:94-97；未 pull 时 362 个 STL 全是 ~134B 的 LFS 指针，实测 `unitree/g1/desc/meshes/pelvis.STL` 头部即 `version https://git-lfs.github.com/spec/v1`）。

6. **CSV 单位口径易误读。** 内部全链路是米+四元数（wp.transform），仅导出层换算：`io/csv.py:71` 根平移 ×100.0 成厘米、:73 欧拉角 degrees=True、:76 关节角 rad2deg；`load_csv:35` ×0.01 反向。interactive-retargeting.md:112/114 的说法与代码一致，但下游消费方常默认 SI 单位，对接前必核对。

7. **图谱阶段假边记录（知识库层面）。** `io/csv.py:6` 的 stdlib `import csv` 曾被依赖扫描误解析为自引用假边，批阶段已剔除；引用本图谱 imports 时该文件无需自环。

8. **捆绑资产规模钉版。** STL 实测 362 个（L10 资产层文件总数 386），动作库=10 条示例 BVH + 15 条优化器 BVH + 5 机器人 ×10 条参考 CSV（assets/motions/），与 README.md:29/:34 声称一致；源动作来自 Bones 的 BONES-SEED 数据集（README.md:37 授权说明）。

## 延伸

生态伙伴：GEM-X（视频人体动捕）→ 本仓（重定向）→ ProtoMotions/SONIC（仿真与全身控制）（README.md:96-102）。调参链路：foot-contact 阈值（`contact_detection.py:95-101`）→ ik_match_table 权重 → IK 权重优化器自动搜索。
