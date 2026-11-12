# 讲透 NVIDIA Dataset_Utilities（NVDU）

NVIDIA 2018 年开源的 NDDS 合成数据集标注检视工具（pyglet+OpenGL 立即模式），姊妹仓 Dataset_Synthesizer（UE 合成器）的下游消费端；含 YCB 模型下载-对齐资产管线（FAT 数据集工具链）。

## 全链状态

| 阶段 | 状态 | 产物 |
|---|---|---|
| understand 图谱 | ✅ 2026-11-07 | 仓内 `.understand-anything/knowledge-graph.json`：**89 节点 / 208 边 / 10 层 / 15 步 tour**，validator 0 issues/0 warnings，fingerprints 37 文件基线@532b8c76 |
| onboarding | ✅ | `onboarding/ONBOARDING.md`（7971 不计空格字符，8 节，55 锚） |
| explain | ✅ | `explain/` 5 篇（微仓简档），合计 16289 不计空格字符，106 锚 |
| deepwiki | — | 未做（本仓由 understand 图谱任务直接覆盖） |

批分析 7 批（37 文件）主会话全链自做：imports 64/64 对账、merge 零悬空、layers 全覆盖 89 节点零重复、explain+onboarding 161 锚经"界内感知消歧 + 符号语义抽验"两轮终验 0 坏。

## explain 索引

1. `01-nvdu_data-数据解析枢纽.md` — NDDS 数据集解析核心：帧扫描二分计数/设置解析/逐帧标注重建
2. `02-cuboid-几何协议与渲染.md` — CuboidVertexType 协议三消费方 + 顶点数组渲染器（core/viz 成对读）
3. `03-visualizer-window-编排与交互.md` — 三级编排 + pyglet 窗口键盘/自动播放/逐帧导出
4. `04-nvdu_ycb-资产管线.md` — YCB 模型下载/解压/逐顶点对齐（法线去平移变换教科书实现）
5. `05-坐标变换三系桥接.md` — OpenCV/UE/OpenGL 三坐标系修正散布的四段代码串讲

## 源码级勘误精选（详录见 ONBOARDING 第 8 节，12 条）

- `test_nvdu_visualizer.py` 非测试，是 `nvdu_viz` 控制台命令的正式入口（setup.py:74-79 entry_points 钉板）
- `Box2d` 实例化即 NameError（core/box.py:10 引用未定义的 BoundingBox2d）——死代码
- Rotator 的 yaw/pitch/roll 属性与两个工厂方法全坏（self.angle 拼写 / 未定义的 rotator()）
- `_ycb_aligned_m.json` 与 `_ycb_aligned_cm.json` md5 完全一致；AlignedOnly 档目录从不产出
- `AnnotatedObjectViz.update_transform` 引用不存在的 self.location（nvdu_visualizer.py:57-70 潜伏地雷）
- core 与 viz 两套 Camera 的 DEFAULT_ZFAR 分别是 1（退化）与 100000
