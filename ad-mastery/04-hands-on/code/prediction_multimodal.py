import numpy as np

# ===== 轨迹预测的多模态性演示 =====
# 关键洞察：一个行人/车的未来是"多模态"的(可能左转/直行/右转)
# 损失函数必须用 minADE/minFDE(挑最接近GT的那条)，不能用平均(否则学出"原地不动")

np.random.seed(0)
gt = np.array([0,1,2,3,4,5.0])  # 真实轨迹(直行)
# 模型预测 6 条候选轨迹(多模态)
preds = np.array([
    [0,1,2,3,4,5.0],   # 直行 ✓
    [0,1,2,3,4,10.0],  # 右转加速
    [0,1,2,3,4,0.0],   # 左转减速
])

def ade(traj):  return np.mean(np.abs(traj-gt))
def fde(traj):  return np.abs(traj[-1]-gt[-1])

# 错误做法: 平均所有轨迹 -> 学到"不动"
avg_pred = preds.mean(axis=0)
print(f"错误(平均): ADE={ade(avg_pred):.2f}, FDE={fde(avg_pred):.2f}")

# 正确做法: minADE/minFDE - 挑最接近GT的那条
ades = [ade(p) for p in preds]
fdes = [fde(p) for p in preds]
print(f"正确(minADE): {min(ades):.2f}m,  minFDE: {min(fdes):.2f}m")
print("→ 这就是为什么运动预测都用 minDE/minFDE: 未来不唯一，评估必须多模态")
