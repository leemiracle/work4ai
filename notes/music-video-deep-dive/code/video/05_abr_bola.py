"""
05_abr_bola.py
==============
BOLA (Buffer Occupancy based Lyapunov Algorithm) - 现代流媒体默认 ABR 算法。

MIT 2016 INFOCOM 最佳论文。dash.js 默认用 BOLA-BASIC。
核心思想：只看缓冲区水位 → Lyapunov 优化证明接近最优。

直觉：
- 缓冲区满 → 选高码率（享受质量）
- 缓冲区空 → 选低码率（避免卡顿）
- BOLA 用 Lyapunov 给出具体的"水位阈值"，避免手调。

本文件实现 BOLA-U（basic version）+ 模拟流式播放。
"""
import numpy as np


class BOLA:
    """
    BOLA-U: 单个 chunk 选择码率。
    公式（简化）：
        对每个码率 m，计算效用 V * utility(m) + (V * gamma + buffer_now - chunk_size_m / throughput)
        选使该值最大的 m。
    其中 V 是 Lyapunov 参数，gamma 是缓冲区目标。
    """
    def __init__(self, bitrates, chunk_dur=4.0, buffer_max=20.0,
                 V=0.93, gamma=0.93):
        # bitrates: [bps] 列表，从低到高
        self.bitrates = sorted(bitrates)
        self.chunk_dur = chunk_dur
        self.buffer_max = buffer_max
        self.V = V  # Lyapunov 参数
        self.gamma = gamma
        self.n = len(bitrates)
        # utility: 简单用 log(bitrate)
        self.utility = [np.log(m + 1) / np.log(self.bitrates[-1] + 1) for m in self.bitrates]

    def select(self, buffer_now, throughput):
        """
        buffer_now: 当前缓冲区（秒）
        throughput: 估计下载速率（bps）
        返回选中的 bitrate index
        """
        best_score = -np.inf
        best_idx = 0
        for m in range(self.n):
            chunk_size_bytes = self.bitrates[m] * self.chunk_dur / 8  # bytes
            download_time = chunk_size_bytes * 8 / max(throughput, 1)  # 秒
            # BOLA 决策函数
            # 高码率效用高但下载时间长（消耗 buffer）
            score = (self.V * self.utility[m]
                     + (self.V * self.gamma + buffer_now - download_time))
            # 防止 buffer 超过 max（强迫留出空间）
            if buffer_now + self.chunk_dur - download_time > self.buffer_max:
                score = -np.inf
            if score > best_score:
                best_score = score
                best_idx = m
        # 紧急回退：buffer 太小，强制选最低码率
        if buffer_now < self.chunk_dur * 1.5:
            best_idx = 0
        return best_idx


def simulate_abr(abr, throughput_trace, total_chunks=60, verbose=False):
    """
    模拟流式播放：
    - throughput_trace: 每个 chunk 的下载速率
    返回 (avg_bitrate, rebuffer_ratio, switches)
    """
    buffer_now = 5.0  # 初始缓冲 5 秒
    playback_done = 0
    bitrates_chosen = []
    total_played = 0
    total_rebuf = 0
    for i in range(total_chunks):
        idx = abr.select(buffer_now, throughput_trace[i])
        br = abr.bitrates[idx]
        bitrates_chosen.append(br)
        chunk_size_bits = br * abr.chunk_dur
        download_time = chunk_size_bits / max(throughput_trace[i], 1)
        # 下载过程中：buffer 在减少（除非 download_time < chunk_dur 才增长）
        if download_time > buffer_now:
            # 卡顿
            total_rebuf += download_time - buffer_now
            buffer_now = 0
        else:
            buffer_now -= download_time
        # 下载完，加入 buffer
        buffer_now += abr.chunk_dur
        buffer_now = min(buffer_now, abr.buffer_max)
        total_played += abr.chunk_dur

    avg_br = np.mean(bitrates_chosen)
    rebuf_ratio = total_rebuf / total_played
    switches = sum(1 for i in range(1, len(bitrates_chosen)) if bitrates_chosen[i] != bitrates_chosen[i-1])
    if verbose:
        print(f"  avg bitrate: {avg_br/1e6:.2f} Mbps")
        print(f"  rebuffer ratio: {rebuf_ratio*100:.1f}%")
        print(f"  bitrate switches: {switches}/{total_chunks}")
    return avg_br, rebuf_ratio, switches


if __name__ == "__main__":
    bitrates = [300e3, 800e3, 1.5e6, 3e6, 6e6]  # 5 个码率档（240p~4K）
    abr = BOLA(bitrates, chunk_dur=4.0, buffer_max=20.0)

    print("=" * 60)
    print("BOLA ABR 模拟")
    print("=" * 60)

    # 场景 1：稳定带宽
    np.random.seed(0)
    trace1 = np.full(60, 5e6)  # 5 Mbps 稳定
    print("\n[场景 1] 稳定 5 Mbps 带宽：")
    avg1, rb1, sw1 = simulate_abr(abr, trace1, verbose=True)

    # 场景 2：波动带宽（地铁通勤）
    trace2 = np.concatenate([
        np.full(15, 8e6),    # WiFi
        np.full(15, 1e6),    # 信号差
        np.full(15, 500e3),  # 信号更差
        np.full(15, 4e6),    # 恢复
    ]) + np.random.randn(60) * 200e3
    print("\n[场景 2] 波动带宽（模拟通勤）：")
    avg2, rb2, sw2 = simulate_abr(abr, np.abs(trace2), verbose=True)

    # 场景 3：极差带宽
    trace3 = np.full(60, 200e3)  # 0.2 Mbps
    print("\n[场景 3] 极差带宽 0.2 Mbps：")
    avg3, rb3, sw3 = simulate_abr(abr, trace3, verbose=True)

    print("\n" + "=" * 60)
    print("洞察：")
    print("  - BOLA 公式简单（只看 buffer + throughput）但有理论最优性证明")
    print("  - dash.js (Shaka Player) 默认就是 BOLA-BASIC")
    print("  - 真实 ABR（如 Netflix）还会考虑 chunk 大小、屏幕分辨率、用户偏好")
    print("  - 进阶：MPC（2015）、Pensieve（2017, RL）、Puffer（2019+, 在线 RL）")
    print("=" * 60)
