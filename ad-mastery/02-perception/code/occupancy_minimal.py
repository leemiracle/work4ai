"""占用预测最小版: 稀疏LiDAR观测 -> 预测完整3D占用 (OccNet思想)
直觉: 检测器答'那是什么', 占用网络答'哪里不能去'(可泛化到未知物体)
任务: 合成场景放2~4个方块/圆柱 -> 只给稀疏采样点(30%) -> 3D CNN补全
"""
import torch, torch.nn as nn
torch.manual_seed(0)
G = 16  # 16^3 体素

def make_scene():
    occ = torch.zeros(1, G, G, G)
    for _ in range(torch.randint(2, 5, (1,)).item()):
        cx, cy, cz = torch.randint(3, G-3, (3,))
        s = torch.randint(2, 5, (1,)).item()
        shape = torch.randint(0, 2, (1,)).item()  # 0方块 1球
        x, y, z = torch.meshgrid(torch.arange(G), torch.arange(G), torch.arange(G), indexing='ij')
        if shape:  # 球
            m = ((x-cx)**2 + (y-cy)**2 + (z-cz)**2) <= s**2
        else:      # 方块
            m = (abs(x-cx)<=s) & (abs(y-cy)<=s) & (abs(z-cz)<=s)
        occ[0][m] = 1.0
    obs = occ * (torch.rand(1, G, G, G) < 0.3).float()  # 30%稀疏观测
    return obs, occ

class OccNet(nn.Module):
    """3D UNet-lite: 稀疏观测 -> 完整占用"""
    def __init__(self):
        super().__init__()
        self.enc = nn.Sequential(
            nn.Conv3d(1, 16, 3, 2, 1), nn.ReLU(),    # 8
            nn.Conv3d(16, 32, 3, 2, 1), nn.ReLU(),   # 4
            nn.Conv3d(32, 64, 3, 2, 1), nn.ReLU())   # 2
        self.dec = nn.Sequential(
            nn.ConvTranspose3d(64, 32, 4, 2, 1), nn.ReLU(),  # 4
            nn.ConvTranspose3d(32, 16, 4, 2, 1), nn.ReLU(),  # 8
            nn.ConvTranspose3d(16, 8, 4, 2, 1), nn.ReLU(),   # 16
            nn.Conv3d(8, 1, 1))
    def forward(self, x):
        return self.dec(self.enc(x))

m = OccNet()
opt = torch.optim.Adam(m.parameters(), lr=2e-3)
print("训练 OccNet (稀疏观测->完整占用)...")
for i in range(150):
    obs, gt = make_scene()
    loss = nn.functional.binary_cross_entropy_with_logits(m(obs[None])[0,0], gt[0])
    opt.zero_grad(); loss.backward(); opt.step()
    if (i+1) % 50 == 0: print(f"  iter{i+1} BCE={loss.item():.3f}")
# 评估 IoU
iou, n = 0.0, 30
with torch.no_grad():
    for _ in range(n):
        obs, gt = make_scene()
        pred = (m(obs[None])[0,0] > 0).float()
        inter = (pred*gt).sum(); union = ((pred+gt)>0).sum()
        iou += (inter/union).item()
print(f"✅ 占用补全 IoU = {iou/n:.3f} (随机猜~0.1)")
print("💡 占用网络只问'哪里被占'不问'是什么' -> 异形障碍物也能兜底")
