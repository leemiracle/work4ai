"""
11_karplus_bowed.py
===================
Extended Karplus-Strong：从"拨弦"升级到"弓弦"。

经典 KS（03 文件）用一次性噪声激发 = 拨弦。
弓弦的本质区别：**能量持续注入**（弓毛反复抓-放弦）。

参照 Karjalainen et al. 的 EKS (Extended KS) 框架：
  1. 持续激发：每周期注入 filtered noise burst（弓的抓放）
   2. Bridge 反射滤波（模拟琴码能量损耗，低通）
  3. 拾音位置梳状滤波（pickup comb：不同位置音色不同）
  4. 动态阻尼（模拟指压/弓压变化）

物理对应：
  - 弓速快 → 注入能量多 → 更亮更大声
  - 弓压大 → 抓住时间长 → 高频衰减慢 → 更亮
  - 拾音靠近琴码 → 高频分量多 → 更亮更细
"""
import numpy as np
from scipy.io import wavfile
from scipy import signal as sg

SR = 44100


def extended_karplus(
    freq=196.0,          # G3（小提琴 G 弦）
    dur=3.0,
    bow_force=0.8,       # 弓压 0-1
    bow_position=0.12,   # 拾音/触弓位置（0=琴码, 1=指板）
    brightness=0.6,      # 环路滤波截止（音色亮度）
    sr=SR,
):
    """
    Extended KS 弓弦合成。
    环路：buf → [bridge lowpass] → [comb 拾音] → 回到 buf
    激发：每周期开头注入低通噪声（弓抓放）+ 持续小噪声（弓毛摩擦）
    """
    N = max(int(sr / freq), 2)
    n_out = int(dur * sr)

    # 初始缓冲：静音（弓弦从静开始），靠持续激发起振
    buf = np.zeros(N, dtype=np.float64)
    out = np.zeros(n_out, dtype=np.float64)

    # bridge 反射滤波（一阶低通：高频每次经过琴码都损耗）
    alpha = 0.15 + 0.75 * brightness   # 亮度 → 低通系数
    bridge_state = 0.0

    # 环路阻尼（整体衰减，受弓压影响：压大 → 阻尼小 → 持续长）
    damping = 0.995 + 0.004 * bow_force

    # 持续激发参数
    noise_amp = 0.35 * bow_force        # 弓压 → 摩擦噪声强度
    excite_lp_state = 0.0
    excite_alpha = 0.2 + 0.6 * bow_force  # 激发低通：压大 → 更亮

    # 起振：前一周期注入一个较强脉冲（弓第一次抓住）
    buf[: N // 8] = np.random.uniform(-1, 1, N // 8) * 0.5

    idx = 0
    period_counter = 0
    for i in range(n_out):
        # --- 持续激发（弓毛摩擦：低通噪声，每周期重抓一次时更强）---
        phase_in_period = period_counter / N
        # 抓放包络：每周期开始时强（抓），随后弱（滑）
        grab_env = np.exp(-phase_in_period * 8) * 0.7 + 0.3
        raw_noise = np.random.uniform(-1, 1)
        excite_lp_state += excite_alpha * (raw_noise - excite_lp_state)
        excitation = noise_amp * grab_env * excite_lp_state

        # --- 环路：读 → bridge 滤波 → 写回 ---
        s = buf[idx] + excitation * 0.3
        bridge_state += alpha * (s - bridge_state)
        loop_out = bridge_state
        buf[idx] = loop_out * damping

        # --- 拾音：梳状滤波（位置 → 相位差叠加，模拟距琴码 d 处）---
        d = max(int(N * bow_position), 1)
        s_pickup = loop_out - 0.85 * buf[(idx + d) % N]
        out[i] = s_pickup * 0.5

        idx = (idx + 1) % N
        period_counter = (period_counter + 1) % N

    # 归一化 + 轻微淡入淡出
    out /= np.max(np.abs(out)) + 1e-9
    fade = min(2000, n_out // 10)
    out[:fade] *= np.linspace(0, 1, fade)
    out[-fade:] *= np.linspace(1, 0, fade)
    return out


def envelope(x, attack_s=0.02, release_s=0.15, sr=SR):
    n_a, n_r = int(attack_s * sr), int(release_s * sr)
    env = np.ones_like(x)
    env[:n_a] = np.linspace(0, 1, n_a)
    env[-n_r:] = np.linspace(1, 0, n_r)
    return x * env


if __name__ == "__main__":
    print("=" * 60)
    print("Extended Karplus-Strong：弓弦合成")
    print("=" * 60)

    variants = [
        ("弓弦-正常弓压", dict(bow_force=0.7, bow_position=0.12, brightness=0.6)),
        ("弓弦-轻压靠指板（暗、柔和）", dict(bow_force=0.3, bow_position=0.25, brightness=0.3)),
        ("弓弦-重压靠琴码（亮、紧张）", dict(bow_force=1.0, bow_position=0.07, brightness=0.9)),
    ]

    for name, kw in variants:
        print(f"\n[{name}] freq=196Hz (G3), {kw}")
        y = extended_karplus(freq=196.0, dur=2.5, **kw)
        fname = "bowed_" + name.split("(")[0].strip().replace("-", "_") + ".wav"
        wavfile.write(fname, SR, np.int16(y * 32767))
        print(f"  saved {fname}")

    # 一小段"旋律"（正常弓压）：G-A-B-D（小提琴入门音阶感）
    print("\n[弓弦旋律 G3-A3-B3-D4]")
    notes = [196.0, 220.0, 246.94, 293.66]
    melody = np.concatenate([
        envelope(extended_karplus(f, dur=0.7, bow_force=0.7)) for f in notes
    ])
    wavfile.write("bowed_melody.wav", SR, np.int16(melody * 32767))
    print("  saved bowed_melody.wav")

    print("\n" + "=" * 60)
    print("与经典拨弦 KS（03 文件）的物理区别：")
    print("  拨弦：一次性噪声激发 → 能量只出不进 → 自然衰减")
    print("  弓弦：持续噪声注入（每周期'重抓'）→ 能量泵入 → 自激振荡")
    print("  ↑ 这就是小提琴能无限持续一个音的物理机制（limit cycle）")
    print("=" * 60)
