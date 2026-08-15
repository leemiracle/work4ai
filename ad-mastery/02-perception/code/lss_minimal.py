"""
LSS (Lift-Splat-Shoot) 最小实现 —— camera-only BEV 投影
Philion & Fidler, ECCV 2020, arXiv:2008.05711
三层: 直觉(射线展开) -> 数学(深度分布外积) -> 代码(跑通BEV)
"""
import torch, torch.nn as nn

class LiftSplat(nn.Module):
    def __init__(self, CamC=32, D=12, H=8, W=22, fx=400, fy=400, cx=11, cy=4,
                 grid=20.0, dx=1.0):
        super().__init__()
        self.D, self.CamC, self.H, self.W = D, CamC, H, W
        self.fx, self.fy, self.cx, self.cy = fx, fy, cx, cy
        self.bx = torch.tensor([-grid/2, -grid/2])
        self.nx = [int(grid/dx)]*2
        self.dx = dx
        self.depth_net = nn.Sequential(
            nn.Conv2d(CamC, CamC, 3, padding=1), nn.ReLU(),
            nn.Conv2d(CamC, D, 1))
        self.feat_net = nn.Sequential(
            nn.Conv2d(CamC, CamC, 3, padding=1), nn.ReLU(),
            nn.Conv2d(CamC, CamC, 1))

    def create_frustum(self):
        ds = torch.arange(self.D)*self.dx + 1.0
        xs = torch.linspace(0, self.W-1, self.W) - self.cx
        ys = torch.linspace(0, self.H-1, self.H) - self.cy
        P, H, W = self.D, self.H, self.W
        pts = torch.stack(torch.meshgrid(ds, ys, xs, indexing='ij'), -1).float()
        pts[..., 0] = pts[..., 0]*pts[..., 2]/self.fx
        pts[..., 1] = pts[..., 1]*pts[..., 2]/self.fy
        return pts                                         # [D,H,W,3]

    def lift(self, cam_feat, pts, cam2ego):
        B, C = cam_feat.shape[0], self.CamC
        depth = self.depth_net(cam_feat).softmax(1)        # [B,D,H,W]
        feat = self.feat_net(cam_feat)                     # [B,CamC,H,W]
        feat_3d = depth.unsqueeze(2)*feat.unsqueeze(1)     # [B,D,CamC,H,W] 外积
        # 视锥 -> 自车坐标 (向量化)
        N = pts.reshape(-1,3).shape[0]
        pts_h = torch.cat([pts.reshape(-1,3), torch.ones(N,1)], -1)   # [N,4]
        pts_ego = torch.einsum('bij,nj->bni', cam2ego, pts_h)[...,:3]  # [B,N,3]
        return feat_3d.reshape(B, self.D, self.CamC, self.H, self.W), pts_ego.reshape(B, self.D, self.H, self.W, 3)

    def splat(self, feat_3d, pts_ego):
        # 向量化 splat (用 index_add)
        B, D, C, H, W = feat_3d.shape
        bev = torch.zeros(B, C, *self.nx)
        ix = ((pts_ego[...,0]-self.bx[0])/self.dx).long()
        iy = ((pts_ego[...,1]-self.bx[1])/self.dx).long()
        valid = (ix>=0)&(ix<self.nx[0])&(iy>=0)&(iy<self.nx[1])
        for b in range(B):
            f3p = feat_3d[b].permute(0,2,3,1)               # [D,H,W,CamC]
            f = f3p[valid[b]]                                # [M, CamC]
            idx = ix[b][valid[b]]*self.nx[1]+iy[b][valid[b]]  # 扁平BEV索引
            flat = bev[b].reshape(C, -1)
            flat.index_add_(1, idx, f.t())
        return bev

    def forward(self, cam_feat, cam2ego):
        pts = self.create_frustum().to(cam_feat.device)
        f3, pe = self.lift(cam_feat, pts, cam2ego)
        return self.splat(f3, pe)

torch.manual_seed(0)
m = LiftSplat()
cam = torch.randn(2, 32, 8, 22)
c2e = torch.eye(4).repeat(2,1,1)
bev = m(cam, c2e)
print(f"✅ LSS 跑通 (向量化 splat)")
print(f"   输入 cam_feat: {tuple(cam.shape)}  输出 BEV: {tuple(bev.shape)}")
print(f"   视锥点/像素 D={m.D}, BEV 覆盖 {m.nx[0]*m.dx}m²")
print(f"   💡 LSS=像素预测深度分布→展开成3D点→splat到BEV→丢弃z得鸟瞰图")
print(f"   💡 深度准=BEV准, 这是BEVDepth加depth监督的根本原因")
