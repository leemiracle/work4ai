# 01 · CompositeGenerator：掩码融合双分支（models/networks.py）

## 角色定位

CompositeGenerator（`models/networks.py:117`）是 vid2vid 生成器的主体网络，是论文「光流复用 + 软掩码仲裁」思想的直接代码化身：对每一帧，它同时产出一份从头生成的图像（raw 分支）、一份上帧到当前帧的光流（flow 头）和一份逐像素置信权重（weight 头），最终由 weight 决定每个像素信任 warp 复用还是信任重新生成。`options/base_options.py:21` 的默认 `--netG composite` 即指向它；金字塔细尺度用变体 CompositeLocalGenerator（`models/networks.py:234`）。

## 内部结构

输入编码是两条同构下采样支路：语义/关键点走 `model_down_seg`，上一帧生成结果走 `model_down_img`，后者对前者的 resnet 段整体 `copy.deepcopy`（`models/networks.py:153-163`），两支特征逐元素相加（`models/networks.py:204`）。解码三头共享这段联合特征：raw 头 `model_res_img → model_up_img → model_final_img`（`models/networks.py:205-206`）以 Tanh 收尾；flow 头 `model_res_flow`（deepcopy 自 raw 的 res 段，`models/networks.py:169-170`）经 `model_up_flow` 出 2 通道光流并乘尺度 20（`models/networks.py:212`）；weight 头 1 通道 Sigmoid（`models/networks.py:183`）。Local 变体的 flow 乘数随尺度放大 `20 * 2^scale`（`models/networks.py:297`），并把粗尺度图像/光流特征注入解码输入（`models/networks.py:298-299`）。

## 外部连接

上游调用方是 `Vid2VidModelG`：`models/vid2vid_model_G.py:38-43` 经 `networks.define_G` 按空间尺度族构建 netG0..netG{s}；每帧 forward 的七元组返回 `(img_final, flow, weight, img_raw, img_feat, flow_feat, img_fg_feat)` 被 G 模型逐帧传递（`models/vid2vid_model_G.py:176-178`）。warp 执行依赖 `BaseNetwork.resample`（`models/networks.py:108`）：先把 flow 除以宽高一半归一化到 [-1,1]（`models/networks.py:112`），再 `grid_sample` 双线性采样、border 填充（`models/networks.py:102-106`，fp16 时临时升 float）。`use_fg_model` 时额外挂前景独立支路 `indv_*`（`models/networks.py:128-149`）。

## 数据流

单帧 forward（`models/networks.py:203-232`）：`down = down_seg(input) + down_img(img_prev)` → raw 解码 → flow/weight 头 → 融合核心 `models/networks.py:219-221`：`img_warp = resample(img_prev, flow)`，`img_final = img_raw * weight + img_warp * (1-weight)`。首帧或 `--no_flow` 时跳过融合直出 raw（`models/networks.py:216-217`，对应 G 模型 `use_raw_only` 开关 `models/vid2vid_model_G.py:173`）。fg 模式下再按前景掩码与 indv 支路输出二次混合（`models/networks.py:224-230`），掩码由 `compute_mask` 从 fg_labels 通道求和 clamp 而来（`models/vid2vid_model_G.py:322-329`）。

## 设计决策

- **学软掩码而非二值掩码**：Sigmoid 权重（`models/networks.py:183`）让梯度可传，网络在遮挡/大位移区自动压低 warp 权重。
- **flow 头 deepcopy raw 头结构**（`models/networks.py:169-170`）：光流回归与图像生成共享感受野先验，但参数独立演化。
- **flow 乘 20 的定标**（`models/networks.py:212`）：Tanh 输出范围有限，常数放大让 flow 头只需学小数值，训练更稳；Local 尺度按分辨率翻倍（`models/networks.py:297`）。
- **跨尺度特征注入**（`models/networks.py:298-305`）：细尺度只补高频细节，粗尺度语义由 img_feat_coarse/flow_feat_coarse 直通，这是 pix2pixHD 多尺度思想的时序版延伸。

## 新人提示

先精读 `models/networks.py:203-232` 这 30 行 forward，再回头看 `models/networks.py:153-201` 的模块拼装，最后对照 `models/networks.py:296-325` 的 Local 变体找差异（无独立 res 段、有 coarse 特征注入、flow 乘数变尺度）。注意 weight 头与 flow 头共用 flow_feat（`models/networks.py:211-213`）——掩码是从光流特征读出的，不是从图像特征；想改融合行为应从这条共享通路下手。
