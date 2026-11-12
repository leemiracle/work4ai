# 讲透 nurec-skills（NVIDIA NuRec agent 技能包）

上游：github.com/NVIDIA/nurec-skills · 本地克隆 /usr-data/data2/repos/agent-repos/NVIDIA/nurec-skills · HEAD `5b9d287e`（Merge PR #14 synthetic-target-rig）。
定位：NuRec 神经重建生态的 coding agent 技能包（thin coordination layer，六技能：nurec-index/physical-ai-datasets/ncore/nre/asset-harvester/nurec-fixer）。

## 全链状态表

| 阶段 | 产物 | 状态 |
|------|------|------|
| deepwiki | deepwiki/（8 章 32 页 + INDEX/_coverage-check/wiki_full） | ✅ 100%（32/32，2026-10-26） |
| understand 图谱 | 仓内 .understand-anything/knowledge-graph.json | ✅ 164 节点/207 边/8 层/10 步 tour，validator 0 issues，fingerprints 108 文件@5b9d287e（2026-11-10） |
| onboarding | onboarding/ONBOARDING.md | ✅ 7 节 / 非空白 9564 字符 / 严格锚 63 |
| explain | explain/ 3 篇 | ✅ 01 五技能体系与路由 / 02 nre 渲染链 thin_client+rig / 03 Hydra 配置组合（1954/2209/2142 字符，锚 18/19/14，六节结构） |

## 源码级勘误与甄别（8 条，全部行号实证）

1. **nre BENCHMARK 的 FAIL 要甄别着读**：skills/nre/BENCHMARK.md:12 判 FAIL，但成分是 Tier 1 静态扫描 15630 条 findings（:43），Top 项全是 references 文档里的真实 GPS 坐标（nre-image-notes.md:187-188、local-render.md:72、asset-editing.md:61/111）+ Tier 2 重复内容告警；Tier 3 live agent 评估 "not available"。同框架下 asset-harvester/nurec-index/nurec-fixer 全 PASS（各自 BENCHMARK.md:12）。结论：FAIL=发布合规问题（文档泄露采集地坐标），非功能不可用。
2. **pai.yaml 的 intensity 是成对开关**：configs/pai.yaml:12-20（extra_signal 覆盖）与 :53-58（intensity loss）必须一起解注释；只开前者则 intensity"发射但从未学习"，预测点云 intensity 无意义（注释原文自证）。:12-16 还警告 car2sim 每个已定义 layer 都要列出，漏列退回 semantics-only。
3. **augmented_rig.json 不是新 rig**：与 rig.json（1096 行/33 传感器）全量 diff 仅 2 键——sensors[4] 相机的 windshield-horizontal/vertical-polynomial-approx-inverse（augmented_rig.json:260-263）。"增强"= 补挡风玻璃畸变逆多项式，任务口径"唯一 diff=挡风玻璃逆多项式"成立。
4. **`.agents/skills/` 是 symlink 不是第二棵树**：README.md:53 图示 + readlink 实证 `skills -> ../skills`；跨技能相对链接靠它保持双前缀兼容（README.md:82-84）。
5. **osmo 工作流的 /home/builder/ncore 是容器内路径**：osmo/pai-nurec.yaml:91-100 在容器内 clone 上游 ncore 并 bazel 构建，宿主侧照抄必错。
6. **__pycache__ 产物被 git 追踪**：`skills/nurec-fixer/scripts/__pycache__/validate_setup.cpython-312.pyc` 在 git ls-files 里，且全仓无 .gitignore——本地跑 validate_setup 的副产物进了版本库（仓库卫生问题）。
7. **thin_client 的几何代码是从 NRE 复刻的静态副本**：thin_client.py:159-167 注释明言 "lifted from nre.utils.geometry"；上游 NRE 改位姿轴序/内参约定时，这里不会自动跟进，是跨仓漂移点。
8. **physical-ai-datasets 是唯一无 BENCHMARK.md 的重文档技能**（887 行 SKILL.md，skills/ 下仅它没有评估报告）；且它 frontmatter description 末尾自带负触发 "Do NOT use as a runtime — it routes you elsewhere"（skills/physical-ai-datasets/SKILL.md:3-22）。

## 导读顺序

README（上游总入口）→ 本仓 ONBOARDING.md → explain 01/02/03 → 上游 skills/nurec-index/SKILL.md 决策表 → nre/SKILL.md。
