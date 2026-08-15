"""多目标跟踪: Kalman预测 + IoU匹配 (SORT/ByteTrack思想)
关键: ByteTrack不丢低分检测(低分常是遮挡目标)"""
import numpy as np
np.random.seed(0)

def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x2-x1)*max(0, y2-y1)
    area = (a[2]-a[0])*(a[3]-a[1]) + (b[2]-b[0])*(b[3]-b[1]) - inter
    return inter/area if area > 0 else 0

class Track:
    def __init__(self, tid, box):
        self.id, self.box, self.v = tid, np.asarray(box, dtype=float), np.zeros(4)
        self.missed = 0
    def predict(self):
        self.box = self.box + self.v  # 最简Kalman(匀速)

def track_sequence(dets_per_frame):
    """dets_per_frame: 每帧 [(box, score)]"""
    tracks, next_id = [], 0
    for dets in dets_per_frame:
        for t in tracks: t.predict()
        # ByteTrack两阶段: 先高分后低分
        high = [(b, s) for b, s in dets if s >= 0.5]
        low  = [(b, s) for b, s in dets if s < 0.5]
        for dets_stage in (high, low):
            used = set()
            for t in tracks:
                if t.missed > 2 or not dets_stage: continue
                best, bi = 0, -1
                for i, (b, s) in enumerate(dets_stage):
                    if i in used: continue
                    v = iou(t.box, b)
                    if v > best: best, bi = v, i
                if best > 0.3 and bi >= 0:
                    b = dets_stage[bi][0]
                    t.v = b - t.box      # 更新速度
                    t.box = b; t.missed = 0; used.add(bi)
            # 未匹配低分检测不开新track(防误检)
            if dets_stage is high:
                for i, (b, s) in enumerate(dets_stage):
                    if i not in used:
                        tracks.append(Track(next_id, b)); next_id += 1
        for t in tracks:
            if not any(np.allclose(t.box, b) for b, _ in dets): t.missed += 1
    return tracks

# 合成: 2个目标交叉运动, 一个目标第3帧被遮挡(低分)
T = 5
frames = []
for t in range(T):
    dets = [((t*0.6, t*0.6, t*0.6+2, t*0.6+2), 0.9), ((10-t*0.6, t*0.6, 12-t*0.6, t*0.6+2), 0.9)]
    if t == 3: dets[0] = (dets[0][0], 0.3)   # 目标0被遮挡->低分
    frames.append(dets)
tracks = track_sequence(frames)
print(f"✅ 跟踪完成: {len(tracks)} 个track (GT=2, 若丢低分检测会碎成3+)")
print("💡 ByteTrack: 低分检测只做'关联'不做'新建' -> 遮挡时ID不碎")
