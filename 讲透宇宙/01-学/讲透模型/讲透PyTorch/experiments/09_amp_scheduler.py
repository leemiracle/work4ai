"""
实验 09 —— 混合精度 AMP + 学习率调度器 + 梯度累积/裁剪 (训练工程三件套)
对应文档: 03-训练循环.md & 05-混合精度AMP.md
核心: 独立搭模型必须会的三个训练加速/稳定技巧:
  1. AMP 混合精度: autocast(前向用低精度) + GradScaler(防梯度下溢)
  2. lr scheduler: 训练中动态调学习率 (warmup/cosine/onecycle)
  3. 梯度累积(模拟大batch) + 梯度裁剪(防爆)
跑法: python3 09_amp_scheduler.py
"""
import torch
import torch.nn as nn
import time

torch.manual_seed(0)

X = torch.randn(512, 32); Y = torch.randint(0, 5, (512,))
model = nn.Sequential(nn.Linear(32,128), nn.ReLU(), nn.Linear(128,5))
loss_fn = nn.CrossEntropyLoss()

print("=" * 66)
print("一、混合精度 AMP: 用低精度前向, 省1半内存+加速(GPU), CPU 也能跑(bfloat16)")
print("=" * 66)
# AMP 两件套: autocast(前向自动选低精度) + GradScaler(缩放梯度防float16下溢)
scaler = torch.cuda.amp.GradScaler(enabled=False)  # CPU 上 enabled=False, 仅演示API
print("  AMP 工作流:")
print("    with torch.autocast(device_type):   # 前向自动用 bf16/fp16")
print("        out = model(x); loss = loss_fn(out,y)")
print("    scaler.scale(loss).backward()       # 缩放loss防梯度下溢(fp16才需要)")
print("    scaler.step(opt); scaler.update()   # 反缩放后更新")
# CPU autocast (bfloat16) 演示
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
t0=time.time()
for _ in range(20):
    opt.zero_grad()
    with torch.autocast("cpu", dtype=torch.bfloat16):   # CPU 支持 bfloat16 autocast
        out = model(X); loss = loss_fn(out, Y)
    loss.backward(); opt.step()
t_amp = time.time()-t0
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
t0=time.time()
for _ in range(20):
    opt.zero_grad()
    out = model(X); loss = loss_fn(out, Y)
    loss.backward(); opt.step()
t_fp32 = time.time()-t0
print(f"  CPU bf16 autocast: {t_amp*1000:.1f}ms vs fp32: {t_fp32*1000:.1f}ms (20步)")
print("  注: GPU 上 fp16 加速显著(1.5-3x); CPU bf16 主要省内存, 加速有限")
print("  GradScaler 只在 GPU+fp16 需要(bf16 不用, 因 bf16 指数位宽不下溢)")

print("\n" + "=" * 66)
print("二、学习率调度器: 训练中动态调 lr (收敛质量的关键)")
print("=" * 66)
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
# 几种常用 scheduler
schedulers = {
    "StepLR(每10步*0.5)": torch.optim.lr_scheduler.StepLR(opt, step_size=10, gamma=0.5),
}
# 单独演示 CosineAnnealing 的 lr 曲线
opt2 = torch.optim.SGD(model.parameters(), lr=0.1)
cos = torch.optim.lr_scheduler.CosineAnnealingLR(opt2, T_max=50)
lrs = []
for step in range(50):
    lrs.append(opt2.param_groups[0]['lr'])
    cos.step()
print(f"  CosineAnnealingLR (50步): lr 从 {lrs[0]:.4f} -> {lrs[-1]:.4f} (余弦衰减)")
print(f"  中段 lr ≈ {lrs[25]:.4f}")
print("  常用 scheduler 选型:")
print("    CosineAnnealingLR / CosineAnnealingWarmRestarts: 平滑衰减, 通用")
print("    OneCycleLR: 先升后降(super-convergence), 快速训练")
print("    LinearWarmup + Cosine: 大模型标配(前几百步小lr稳定, 再衰减)")
print("    ReduceLROnPlateau: 验证 loss 不降时自动降 lr (省心)")
print("  铁律: scheduler.step() 在 optimizer.step() 之后调用 (每个 epoch 或每步)")

print("\n" + "=" * 66)
print("三、梯度累积: 小显存模拟大 batch")
print("=" * 66)
# 真实大batch: optimizer.step 每 batch 一次
# 梯度累积: 累积 N 个小batch 的梯度再 step, 等效 batch_size = N * small_batch
accum_steps = 4
real_batch = 32
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
opt.zero_grad()
for micro_step, (bx, by) in enumerate(zip(X.split(real_batch), Y.split(real_batch))):
    with torch.autocast("cpu", dtype=torch.bfloat16):
        loss = loss_fn(model(bx), by) / accum_steps   # 注意: loss 要除以累积步数!
    loss.backward()
    if (micro_step + 1) % accum_steps == 0:
        opt.step(); opt.zero_grad()   # 攒够 4 个小batch 才更新
print(f"  显存只能放 batch=32, 但想用 effective batch=128 -> 累积 {accum_steps} 步再 step")
print("  关键: loss 要除以 accum_steps (否则梯度被放大 accum_steps 倍)")
print("  用途: 消费级 GPU 训大模型 / 模拟大batch 的泛化收益('讲透泛化')")

print("\n" + "=" * 66)
print("四、梯度裁剪: 防梯度爆炸 (RNN/Transformer 必备)")
print("=" * 66)
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
opt.zero_grad()
loss = loss_fn(model(X), Y)
loss.backward()
gnorm_before = torch.sqrt(sum(p.grad.norm()**2 for p in model.parameters()))
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.05)   # 故意设小, 触发实际裁剪
gnorm_after = torch.sqrt(sum(p.grad.norm()**2 for p in model.parameters()))
print(f"  裁剪前梯度总范数: {gnorm_before:.4f}")
print(f"  clip_grad_norm_(max_norm=0.05) 后: {gnorm_after:.4f}  <- 被缩放到 0.05!")
print("  => 把所有参数梯度按比例缩放, 使总范数 = max_norm (超过才缩, 不超过不动)")
print("  => 把所有参数梯度按比例缩放, 使总范数 <= max_norm")
print("  => 防止训练 loss 突然 NaN(梯度爆炸), RNN/Transformer 训练标配")

print("\n核心洞察 (训练工程三件套):")
print("  AMP(加速省显存) + scheduler(收敛质量) + 梯度累积/裁剪(稳定性)")
print("  这三样是从'能跑通教程'到'能独立训出可用模型'的分水岭")
