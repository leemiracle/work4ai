# ② 感知层深挖：BEV / 占用 / 检测 / 跟踪 全算法

> 感知是 AD 的"眼睛"。感知错了，一切皆错。本篇覆盖感知全部主流算法 + 三层讲解 + 跑通代码。

---

## 1. 感知的六大任务

| 任务 | 输出 | 评价 | 为什么 |
|------|------|------|--------|
| 3D 检测 | [x,y,z,w,l,h,θ,cls] | nuScenes mAP/NDS | 知道车/人在哪 |
| BEV 感知 | 鸟瞰图特征 | mAP | 统一坐标系 |
| 占用预测 | 3D voxel 占用 | IoU | 长尾（测不出类别但知"有东西"）|
| 车道线/建图 | 矢量地图 | mAP | 知道路怎么走 |
| 多目标跟踪 | [id,box,t] | AMOTA | 时序、速度 |
| 语义分割 | 每像素类别 | mIoU | 可行驶区域 |

---

## 2. 3D 检测：LiDAR 派 vs 相机派 vs 融合派

### 2.1 LiDAR 检测（点云，几何金标准）

**Voxel/Pillar 类**（体素化，主流）
- **PointPillars**（CVPR'19）：点→pillar→2D 伪图→2D CNN。极快，工业基线。
- **SECOND**（'18）：稀疏 3D 卷积（SparseConv），只算非空 voxel。
- **CenterPoint**（CVPR'20）：**anchor-free**，预测中心点+回归属性。两阶段精修。**LiDAR 检测标杆**。代码：`open-mmlab/OpenPCDet`
- **VoxelNeXt**（CVPR'23）：全稀疏，直接从 voxel 预测。

**Point 类**
- **PointRCNN**（CVPR'18）：PointNet++ 提点特征→proposal。
- **PV-RCNN(++)**（CVPR'20/22）：voxel+point 双分支，精度高。

> 工业主流：**CenterPoint + SparseConv backbone**。

### 2.2 相机 3D 检测（成本驱动，Tesla 主推）

**① LSS 派（前向投影）**—— 必跑代码 `code/lss_minimal.py`
- **LSS（Lift-Splat-Shoot，ECCV'20）**：**奠基**。像素预测深度分布→展开成 3D 点云→splat 到 BEV。
- **BEVDet / BEVDepth**：LSS + depth 监督。

**② Transformer/Query 派（当前主流）**
- **DETR3D**（CoRL'21）：DETR 的 3D 版。
- **PETR / PETRv2**（ECCV'22）：**3D 位置编码**替代可变形采样。
- **StreamPETR**（ICCV'23）：时序 memory bank，**camera-only SOTA**。

**③ BEV 类**
- **BEVFormer**（ECCV'22）：时空 Transformer，Deformable Attention。**量产主流**。

### 2.3 LiDAR-Camera 融合
- **BEVFusion**（MIT/阿里，ICRA'22）：各自 BEV 后空间融合。**最流行**。
- **TransFusion(-L)**（CVPR'22）：query 层融合，鲁棒（掉一个传感器也能跑）。
- **CMT**（CVPR'23）：双向 attention。

> 趋势争议：Tesla/华为 ADS 3.0 主张**纯视觉**；Waymo/百度坚持**融合**。收敛到"视觉为主+LiDAR兜底"。

---

## 3. BEV 感知：统一坐标系

**为什么 BEV**：6 个相机各看一个角度。BEV 投影到统一顶视网格，下游直接用。

**两大流派**：
```
LSS 派（前向）              BEVFormer 派（反向）
图像→预测深度→投BEV          BEV query→采图像特征
BEVDet/BEVDepth/BEVFusion    BEVFormer/PolarDETR
显式几何、快                  端到端、精度高
```

**LSS 核心数学**（已跑通验证）：
$$\text{BEV}(x,y) \mathrel{+}= \sum_{d} \underbrace{p(d|u,v)}_{\text{深度分布}} \cdot \underbrace{f_{u,v}}_{\text{像素特征}} \cdot \mathbb{1}[\text{对应}]$$

---

## 4. 占用预测（Occupancy）—— Tesla 引爆的新方向

**直觉**：检测必须有类别。但现实有无数检测器没见过的东西（异形障碍物、纸箱）。占用网络**不分类，只答"这个 3D 位置是否被占"**——长尾终极武器。Tesla AI Day 2022 引爆。

| 算法 | 特点 |
|------|------|
| **OccNet** | 3D 稀疏 voxel，二分类+可选语义 |
| **SurroundOcc** | 稠密占用 |
| **TPVFormer**（CVPR'23）| **Tri-Perspective View** 三正交平面近似 3D，省显存 |
| **VoxFormer**（CVPR'23）| 两阶段稀疏扩散 |
| **FB-Occ** | 前背景分离，nuScenes 冠军 |
| **OccWorld**（ECCV'24）| **4D 占用世界模型**（见 ⑤ 前沿）|

> 💡 占用是革命：把"检测什么"变成"空间什么被占"，泛化极强。

---

## 5. 车道线与在线建图（Online Mapping）

传统依赖**高精地图（HD Map）**——厘米级但采集贵、更新慢。"**无图化**" = 在线建图。

- **CLRNet**（CVPR'22）：anchor 车道线。
- **MapTR / MapTRv2**（ICLR'23）：**向量化在线建图**，车道线/边界/人行道统一为有序点集。**主流**。
- **StreamMapNet**：时序 MapTR。

---

## 6. 多目标跟踪（MOT）

- **SORT**（'16）：Kalman + IoU 匹配，工业基线。
- **ByteTrack**（ECCV'22）：**不丢低分检测**（低分常是遮挡），两阶段匹配。**2D MOT SOTA**。
- **SimpleTrack**：3D 跟踪。

> UniAD 把 MOT 端到端化：用 **track query** 帧间传递。

---

## 7. 跑通验证（已实现）

`code/lss_minimal.py` 跑通结果：
```
输入 cam_feat: (2, 32, 8, 22)  输出 BEV: (2, 32, 20, 20)
视锥点/像素 D=12, BEV 覆盖 20m²
💡 LSS=像素预测深度分布→展开成3D点→splat到BEV→丢弃z得鸟瞰图
💡 深度准=BEV准, 这是BEVDepth加depth监督的根本原因
```

## ✍️ 练习

1. 手画 LSS 的数据流：从 6 个相机图像到一张 BEV 特征图，标出每步 tensor 形状。
2. 为什么占用预测比检测更适合处理"一辆侧翻的卡车"？从训练数据分布角度分析。
3. BEVFormer（反向采样）相比 LSS（前向投影），在"深度信息利用"上的本质区别？各自失败模式？
4. （动手）修改 `lss_minimal.py`：把深度分布从 softmax 换成**均匀分布**（不学深度），观察 BEV 是否还能成形，解释现象。
5. 跑 OpenPCDet 的 CenterPoint demo：`git clone OpenPCDet` → 按 `docs/DEMO.md` 跑 KITTI 预训练模型。

## 📌 下一步

→ 进入 `03-classics/` 精读 UniAD（感知端到端奠基）+ EMMA（大模型端到端）。
