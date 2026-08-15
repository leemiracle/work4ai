# 代码运行说明

## 依赖

所有代码设计为**零/极轻外部依赖**，便于在任何环境跑：

| 包 | 必需 | 用途 |
|----|------|------|
| `numpy` | ✅ 全部 | 数组运算 |
| `scipy` | ✅ 多数 | FFT/DCT/signal |
| `torch` | ✅ video/ 7-12 | DiT/VAE/Flow Matching |
| `matplotlib` | 可选 | 画图（缺失则只 print）|
| `librosa` / `soundfile` | ❌ 不用 | 用 scipy.io.wavfile + 标准库 wave 替代 |
| `transformers` / `diffusers` | 仅 10/12 | 调真实大模型（可选）|

安装最小依赖：

```bash
pip install numpy scipy torch matplotlib
# 可选（跑 10/12 大模型推理）：
pip install transformers diffusers accelerate
```

## 输出

- 音频代码会写出 `.wav` 文件（用 scipy.io.wavfile 写 16-bit PCM）
- 视频代码会 print 数值结果 / 写出 `.png` 图（matplotlib 在则画，否则跳过）
- DiT/VAE 等用随机权重做前向 demo（不下载预训练权重）

## 跑通顺序建议

按编号顺序跑，难度递增。每个文件独立可跑，无相互依赖。
