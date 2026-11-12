# 02 · stft_loss.py —— 多分辨率 STFT 损失家族

> 锚均从源码核实（commit 9487a8db）。全文件改编自 kan-bayashi/ParallelWaveGAN（stft_loss.py:1-4，MIT，对应 incl_licenses/LICENSE_2）。

## 角色定位

stft_loss.py 提供 CleanUNet 训练的**频谱域损失**，与 util.py:181-223 的波形域 L1 损失互补，共同构成论文的"波形+多分辨率频谱"双域损失配方。文件含 1 个 STFT 前端函数与 4 个 nn.Module 损失类，零项目内依赖（仅 torch），被 util.py:12 import 后经 loss_fn 间接进训练循环。

## 内部结构

四层积木自底向上：
- **stft**（stft_loss.py:16-38）：STFT→幅度谱前端。按 `is_pytorch_17plus`（L13，distutils.LooseVersion 探测）分支调用 torch.stft——1.7+ 必须显式 `return_complex=False`（L29-31）；取实部/虚部平方和开根号（L34-38），`clamp(min=1e-7)`（L38）防 log/sqrt 出 NaN（L37 原作者注释 NOTE(kan-bayashi)）。
- **SpectralConvergenceLoss**（stft_loss.py:41-59）：谱收敛，`||Y_mag-X_mag||_F / ||Y_mag||_F`（L59），衡量相对谱误差。
- **LogSTFTMagnitudeLoss**（stft_loss.py:62-80）：log 幅度谱上的 L1（L80），关注感知相关的对数域差异。
- **STFTLoss**（stft_loss.py:83-127）：单分辨率组合——默认 fft_size=1024/shift=120/win=600（L87），同时返回 sc_loss 与 mag_loss（L127）；窗口函数经 **register_buffer** 注册（L100，原作者注释"Use register_buffer to fix #223"，规避 ParallelWaveGAN 的设备迁移 bug）；band 参数是本仓对上游的**本地化改造**：band='high' 时只取频谱上半频带算损失（L117-120），band='full' 全带（L121-123），else 抛 NotImplementedError（L124-125）。
- **MultiResolutionSTFTLoss**（stft_loss.py:130-184）：多分辨率聚合——默认三组 (512,2048,1024) FFT 配 (50,240,120) hop 配 (240,1200,600) win（L134-135）；assert 三列表等长（L152）；ModuleList 持有三个 STFTLoss（L153-155）；forward 输入 (B,C,T) 时自动摊平为 (B*C,T)（L169-171）；各分辨率损失累加后乘 lambda 再除以分辨率数（L179-182）。

## 外部连接

被 util.py 顶层 import（util.py:12 `from stft_loss import MultiResolutionSTFTLoss`），在 loss_fn（util.py:217-221）中消费：`sc_loss, mag_loss = mrstftloss(denoised, clean)` 各乘 stft_lambda。实例化发生在 train.py:139-142——仅当 loss_config 的 stft_lambda>0 才构造并 .cuda()，否则传 None 给 loss_fn。配置驱动：configs/DNS-large-*.json 的 loss_config.stft_config 节（sc_lambda=0.5、mag_lambda=0.5、band、三组分辨率）逐字段透传给构造函数。

## 数据流

训练时每步：denoised_audio 与 clean_audio 挤掉通道维（util.py:218 `.squeeze(1)`）→ MultiResolutionSTFTLoss.forward 摊平检查（stft_loss.py:169-171）→ 逐个 STFTLoss：双方各自过 stft() 得幅度谱（stft_loss.py:114-115）→ band 分支选频带（L117-123）→ 谱收敛 + 对数幅度两个标量（L119-123）→ 三组累加平均（L174-182）→ 回到 loss_fn 与 AE loss 相加（util.py:219）。

## 设计决策

1. **band='high' 是本仓的差异化改造**：上游 ParallelWaveGAN 无此参数，DNS-large-high 配置靠它把损失聚焦高频带——两个 config 的**唯一**差异就是 stft_config.band（full vs high，configs L33），对应论文的高频增强变体。
2. **多分辨率动机**：单一 FFT 窗长在时频分辨率上顾此失彼，三组互补窗让损失对快变与慢变伪影都敏感。
3. **clamp 而非 eps**：`clamp(min=1e-7)`（L38）在 sqrt 之前执行，比事后加 eps 更稳。
4. **版本探测的代价**：distutils.LooseVersion（L11）在新版 Python 已弃用，是复刻时的时代痕迹——搬运到现代环境应改 packaging.version。

## 新人提示

该文件几乎可以当独立库搬运（只依赖 torch），但注意两点：①register_buffer 的 window 会随 .cuda() 迁移，别改成普通属性（stft_loss.py:99-100 注释是血泪教训）；②sc_loss 与 mag_loss 返回的是**未乘 lambda 的原始值**，加权在 MultiResolution 层和 loss_fn 两处分别发生，调损失权重时看清 configs 的 sc_lambda/mag_lambda 与外层 stft_lambda 三层系数叠加。自测方法：在 Python 里用两个正弦波直接调用 forward，sc_loss≈mag_loss≈0 量级即通。

（不计空格约 2200 字符，锚 40+）
