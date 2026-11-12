# 05 · PaDiM 模型精讲（src/anomalib/models/image/padim/）

## ① 角色定位

PaDiM（Patch Distribution Modeling，arXiv:2011.08785）是 anomalib"免训练"路线的代表：不更新任何权重，只对预训练 CNN 各空间位置的 patch 嵌入拟合逐位置多元高斯，推理用马氏距离（Mahalanobis）衡量偏离程度，同时产出图像分数与像素热图。四个文件分工：`__init__.py` 导出 `Padim`（19-21 行）；`torch_model.py` 纯 PyTorch 实现；`anomaly_map.py` 管马氏距离→上采样→平滑后处理链；`lightning_model.py` 包装成 Lightning Module。它与 PatchCore 同属记忆库类（MemoryBankMixin），但用参数化高斯替代核心集近邻搜索，是理解一类学习（ONE_CLASS）范式的最小样本。

## ② 内部结构

**torch_model.py（241 行）**

- `_N_FEATURES_DEFAULTS`（53-56 行）：论文随机降维默认值——resnet18 留 100 维、wide_resnet50_2 留 550 维。
- `_deduce_dims`（59-92 行）：干跑推特征图尺寸；在 padim 内是死代码（见⑥-3）。
- `PadimModel.__init__`（109-149 行）：构造 `TimmFeatureExtractor` 并 `.eval()`（121-125）；校验 `0 < n_features <= n_features_original`（135-137），backbone 不在默认表且未传参则 ValueError（127-133）；`register_buffer` 保存 `randperm(n_original)[:n_features]` 作降维索引（140-143），注释明言 idx 必须随模型保存才可复现。成员：`AnomalyMapGenerator`（146）、`MultiVariateGaussian`（148）、`memory_bank` 列表（149）。
- `forward`（151-195 行）：可选 tiler 前后钩子（174-175、181-182）；全程 no_grad（177）。训练态把嵌入追加进 memory_bank 返回（184-186）；推理态生成热图（188-193），`pred_score = torch.amax(anomaly_map, dim=(-2,-1))`（194）。
- `generate_embedding`（197-220 行）：以分辨率最高的 `layers[0]` 为基准，后续层 `F.interpolate(mode="nearest")` 后沿通道 concat（212-216），再按 idx `index_select` 降维（219-220）。
- `fit`（222-241 行）：`vstack` 拼接（235）→ `gaussian.fit`（238）→ 清空 memory_bank 释放显存（241）。

**anomaly_map.py（193 行）**

- `__init__`（64-67 行）：sigma=4 时核尺寸 `2*int(4*4+0.5)+1=33`，预计算 33×33 `GaussianBlur2d`（channels=1）。
- `compute_distance`（69-95 行）：论文 III-C 公式 (2)。嵌入 reshape 成 `(B,C,H*W)`（87），`delta=(embedding-mean).permute(2,0,1)`（91），距离 `((delta@inv_cov)*delta).sum(2)`（93）reshape 回 `(B,1,H,W)` 后 `clamp(0).sqrt()`（95）。
- `up_sample`（97-115 行）：bilinear 到原图尺寸，`align_corners=False`（110-115）。
- `smooth_anomaly_map`（117-127 行）：过预计算高斯核。
- `compute_anomaly_map`（129-157 行）：三步串联；mean/inv_covariance 先 `.to(device)`（151-154）。
- `forward`（159-193 行）：kwargs 键校验（184-186）。

**lightning_model.py（213 行）**

- `class Padim(MemoryBankMixin, AnomalibModule)`（64 行）——fit 钩子自动触发与 `_is_fitted` buffer 都由此而来。
- `configure_optimizers` 返回 None（134-137）；`training_step` 返回 `torch.tensor(0.0, requires_grad=True)` 哑损失（152-157）。
- `fit`（159-162）转调 `model.fit()`。
- `trainer_arguments`（184-195）：`max_epochs=1, val_check_interval=1.0, num_sanity_val_steps=0, devices=1`。
- `learning_type` 为 ONE_CLASS（197-204）。

## ③ 外部连接

- 上游：`TimmFeatureExtractor`/`MultiVariateGaussian`/`GaussianBlur2d` 均从 `anomalib.models.components` 导入（`torch_model.py:44`、`anomaly_map.py:38`）。实际定义：`MultiVariateGaussian` 在 `models/components/stats/multi_variate_gaussian.py:30`（forward 约定 mean 为 `(C,H*W)`、inv_covariance 为 `(H*W,C,C)`）；`GaussianBlur2d` 在 `models/components/filters/blur.py:48`；`MemoryBankMixin` 在 `models/components/base/memory_bank_module.py:33`，其 `on_validation_start`/`on_train_epoch_end` 在 `_is_fitted` 为 False 时自动调 `fit()`（66-89 行）——"训练结束自动拟高斯"即此机制。
- Tiler 弱依赖：仅 TYPE_CHECKING 导入（`torch_model.py:49-50`），运行时由 `TilerConfigurationCallback.setup` 注入（`callbacks/tiler_configuration.py:118-127`）。
- 图谱边：入边 `config:examples/configs/model/padim.yaml`、`f:models/image/__init__.py`、docs 参考页、`examples/cli/03_models/padim.sh`；出边连 data/post_processing/visualization 各 `__init__` 及 9 个集成测试文件（test_engine、test_checkpoint_io 等）——PaDiM 轻量，常被选作 engine/checkpoint/deploy 测试的被测模型。

## ④ 数据流

resnet18、输入 256×256：`(N,3,256,256)` →（可选 tile）→ TimmFeatureExtractor 出三张图 `layer1 (N,64,64,64)`、`layer2 (N,128,32,32)`、`layer3 (N,256,16,16)` → 后两层 nearest 上采样到 64×64 concat 得 `(N,448,64,64)` → 随机降维 `(N,100,64,64)`。训练态入 memory_bank；epoch 末 fit 拼成 `(N_total,100,4096)` 交给 `MultiVariateGaussian.fit`，得 `mean (100,4096)`、`inv_covariance (4096,100,100)`。推理态同一嵌入过 `AnomalyMapGenerator`：距离 `(N,1,64,64)` → 上采样 `(N,1,256,256)` → 平滑 → amax 得分数，打包 `InferenceBatch(pred_score, anomaly_map)`（194-195 行）。全链路无梯度更新，"训练"只是收集统计量。

## ⑤ 设计决策

1. **随机降维替代 PCA**：`randperm` 直接抽 100/550 通道（140-143），省去逐位置 PCA 开销；idx 存 buffer 保证可复现，比省算力更关键。
2. **nearest 上采样对齐多层**（215 行）：避免插值出原图没有的中间值污染分布统计。
3. **哑损失 + devices=1**：Lightning 需要 loss 才走标准循环（157 行）；memory_bank 是 Python list、fit 单进程 vstack，不支持 DDP，故锁单卡（195 行）。
4. **后处理三段解耦**：距离/上采样/平滑各自可单测，`image_size=None` 可跳过上采样（155-156），方便 tiled 调用方。
5. **模糊核预计算**（66-67 行）：forward 零核构建开销，代价是通道数固定为 1。

## ⑥ 新人提示（含勘误）

1. **勘误（复制残留）**：`PadimModel.fit` 空库报错写 "Cannot perform **coreset selection**"（233 行）——coreset 是 PatchCore 的概念，PaDiM 不做核心集选取，消息是复制粘贴残留。
2. **勘误（提示与键名不符）**：`forward` 校验消息说期望 `covariance` 键（185 行），实际检查的是 `inv_covariance`。
3. **勘误（死代码）**：`_deduce_dims`（59-92 行）在 padim 内零调用；真正用同名函数的是 glass（`glass/torch_model.py:126` 调自己的副本）。`n_features_original` 改由 `out_dims` 求和（126 行）。
4. **fit 别手动调**：MemoryBankMixin 钩子自动触发且只拟一次（`memory_bank_module.py:66-89`）；`num_sanity_val_steps=0` 正是为防 sanity check 提前触发空库 fit。
5. **换 backbone 必传 n_features**：默认表只有两个 key（53-56 行），否则构造即 ValueError。
6. **性能直觉**：inv_covariance 形状 `(H*W,C,C)` 随分辨率四次方增长（256² 输入约 4096×100×100），大图须配 Tiler 或降分辨率，否则显存与 checkpoint 体积都会爆。

---

### 自检报告

- 字数：总字符（含空格）5147 / 去空格字符 4744（达标区间 2500-4800）
- 行号锚：65 处（file.py:行号与段内行号引用，去重计），全部打开源文件核实
- 实测验证：未运行模型代码；形状依据 `torch_model.py:168-171` docstring 与逐行阅读，组件文件均已打开核对行号
