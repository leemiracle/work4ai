"""
实验 06 —— 导出 ONNX + 用 ONNX Runtime 推理 (衔接你的 ONNX 经验)
对应文档: 04-性能与部署.md
核心: 训练好的 PyTorch 模型如何脱离 PyTorch 部署 -> 导出 ONNX -> 用 onnxruntime 推理.
      这正是你做过 Execution Provider 的那条链路.
跑法: python3 06_onnx_export.py
"""
import torch
import torch.nn as nn
import numpy as np
import time

torch.manual_seed(0)

print("=" * 66)
print("一、定义一个可导出的模型 (带动态 batch)")
print("=" * 66)
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(8,32), nn.ReLU(), nn.Linear(32,2))
    def forward(self, x):
        return self.net(x)
model = Net().eval()
dummy = torch.randn(4, 8)   # 导出用的示例输入 (定义输入形状)

print("=" * 66)
print("二、导出 ONNX (torch.onnx.export)")
print("=" * 66)
import os
onnx_path = "/tmp/opencode/model.onnx"
os.makedirs(os.path.dirname(onnx_path), exist_ok=True)
torch.onnx.export(
    model, dummy, onnx_path,
    input_names=["input"], output_names=["logits"],
    dynamic_axes={"input": {0: "batch"}, "logits": {0: "batch"}},  # 动态 batch
    opset_version=14,
)
print(f"  已导出: {onnx_path}")
print(f"  dynamic_axes 让 batch 维可变 (部署时任意 batch 大小都能跑)")

print("\n" + "=" * 66)
print("三、用 ONNX Runtime 加载并推理")
print("=" * 66)
try:
    import onnxruntime as ort
except ImportError:
    print("[skip] 未装 onnxruntime"); import sys; sys.exit(0)
sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
print(f"  ONNX Runtime 加载成功. 可用 providers: {ort.get_available_providers()}")
print(f"  输入: {[(i.name, i.shape, i.type) for i in sess.get_inputs()]}")
print(f"  输出: {[(o.name, o.shape, o.type) for o in sess.get_outputs()]}")

# 任意 batch 推理 (验证动态轴)
for bs in [1, 16, 100]:
    x = np.random.randn(bs, 8).astype(np.float32)
    out = sess.run(["logits"], {"input": x})[0]
    print(f"  batch={bs}: ONNX 输出 shape={out.shape}  (动态轴生效)")

print("\n" + "=" * 66)
print("四、数值一致性: PyTorch vs ONNX Runtime")
print("=" * 66)
x = torch.randn(50, 8)
with torch.no_grad():
    pt_out = model(x).numpy()
ort_out = sess.run(["logits"], {"input": x.numpy()})[0]
diff = np.abs(pt_out - ort_out).max()
print(f"  50 样本, PyTorch vs ONNXRuntime 最大输出差: {diff:.2e}")
print(f"  数值一致 (差在浮点误差量级): {diff < 1e-5}")

print("\n" + "=" * 66)
print("五、推理速度对比 (CPU, 方向性参考)")
print("=" * 66)
def bench(fn, x, n=100):
    fn(x)  # warmup
    t0=time.time()
    for _ in range(n): fn(x)
    return (time.time()-t0)/n*1000
x = torch.randn(64, 8); xn = x.numpy()
t_pt = bench(lambda v: model(v), x)
t_ort = bench(lambda v: sess.run(["logits"], {"input": v}), xn)
print(f"  PyTorch (eager): {t_pt:.3f} ms/次")
print(f"  ONNX Runtime:    {t_ort:.3f} ms/次")
print(f"  ORT 加速: {t_pt/max(t_ort,1e-9):.2f}x")
print("  => ONNX Runtime 做了图优化(算子融合/常量折叠), 推理通常比 PyTorch eager 快")
print("     大模型+GPU(TensorRT/CUDA EP)时差距更大. 这就是部署用 ORT 的理由")

print("\n核心洞察 (整条部署链):")
print("  PyTorch 训练 -> torch.onnx.export -> .onnx 文件 -> ONNX Runtime 推理")
print("  好处: 部署只依赖 onnxruntime(轻量), 不需要整个 PyTorch; 跨框架(C++/Python/C#)通用")
print("  你的经验: 自定义 EP/CUDA 算子 -> 对应 ONNX 的自定义算子注册 (与实验05的 Function 呼应)")
