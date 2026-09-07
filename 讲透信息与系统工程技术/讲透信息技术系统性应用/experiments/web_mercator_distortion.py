# -*- coding: utf-8 -*-
"""
Web Mercator 面积畸变:格陵兰看起来与非洲同大,实为 1/14(纯标准库,assert 自验证)
================================================================================
家族:讲透信息与系统工程技术/讲透信息技术系统性应用(GB/T 41330)
配套:04-信息技术系统性应用转代码.md · 走廊①(坐标变换走廊)
      00-体系结构.md §五-2(反直觉发现:Web Mercator 面积畸变)

方法:球面近似的墨卡托投影,纬度带 [φ1,φ2] × 经度宽 Δλ 的投影面积为
        A_web = R² · Δλ · (tanφ2 − tanφ1)      —— sec² 因子积分的原函数就是 tan
      真实球面面积为
        A_true = R² · Δλ · (sinφ2 − sinφ1)
      用格陵兰/非洲的外接经纬带做量级演示,另用官方公布的陆地面积核对 1/14。

运行:python web_mercator_distortion.py
全部 assert 通过则 exit 0。
"""
import math
import sys

R = 6378137.0  # WGS84 长半轴(Web Mercator 球体半径)

GREENLAND_BOX = (60.0, 83.5, -73.0, -12.0)   # 外接带:纬 60→83.5°N,经 73°W→12°W
AFRICA_BOX = (-35.0, 37.0, -17.0, 51.0)      # 外接带:纬 35°S→37°N,经 17°W→51°E
GREENLAND_TRUE_KM2 = 2166086.0               # 公认陆地面积 km²
AFRICA_TRUE_KM2 = 30370000.0                 # 公认陆地面积 km²


def band_area_km2(lat1, lat2, lon1, lon2, mercator):
    """经纬带的投影(mercator=True)或真实(False)面积,km²"""
    dlon = math.radians(abs(lon2 - lon1))
    if mercator:
        integrand = (math.tan(math.radians(lat2)) - math.tan(math.radians(lat1)))
    else:
        integrand = (math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)))
    return R * R * dlon * integrand / 1e6


def main():
    print("=" * 64)
    print("Web Mercator 面积畸变 · 格陵兰 vs 非洲(GB/T 41330 家族实验)")
    print("=" * 64)

    gl_app = band_area_km2(*GREENLAND_BOX, mercator=True)
    af_app = band_area_km2(*AFRICA_BOX, mercator=True)
    gl_band = band_area_km2(*GREENLAND_BOX, mercator=False)
    af_band = band_area_km2(*AFRICA_BOX, mercator=False)

    true_ratio = AFRICA_TRUE_KM2 / GREENLAND_TRUE_KM2          # 官方面积比 ≈ 14.0
    app_ratio = af_app / gl_app                                # 屏幕上看起来 ≈ 0.2
    inflate_gl = gl_app / gl_band                              # 格陵兰带被放大倍数

    print(f"\n[1] 真实陆地面积(公认值):")
    print(f"    格陵兰 {GREENLAND_TRUE_KM2/1e6:.2f} M km² | 非洲 {AFRICA_TRUE_KM2/1e6:.2f} M km²"
          f" | 非洲/格陵兰 = {true_ratio:.1f} 倍")
    print(f"\n[2] 外接经纬带在 Web Mercator 下的屏幕面积:")
    print(f"    格陵兰带 {gl_app/1e6:.2f} M km² | 非洲带 {af_app/1e6:.2f} M km²"
          f" | 非洲/格陵兰 = {app_ratio:.2f}")
    print(f"    → 屏幕上格陵兰反而比非洲大 {1/app_ratio:.1f} 倍!")
    print(f"\n[3] 格陵兰外接带面积放大倍数 = {inflate_gl:.1f}×"
          f"(高纬 sec² 因子主导;非洲跨赤道,带内近似抵消)")

    # ---- 断言(自验证) ----
    assert 12.0 < true_ratio < 15.0, f"真实面积比应≈14,实测 {true_ratio:.2f}"
    assert app_ratio < 0.5, "Web Mercator 上非洲外接带应明显小于格陵兰外接带"
    assert inflate_gl > 4.0, "格陵兰带(60-83.5°N)应被放大约一个数量级"

    # ---- 逐纬度失真因子:sec²φ —— 面积失真;60°N=4 倍,75°N≈14.9 倍 ----
    def area_factor(lat):
        return 1.0 / math.cos(math.radians(lat)) ** 2

    assert abs(area_factor(60.0) - 4.0) < 1e-9
    assert abs(area_factor(45.0) - 2.0) < 1e-9
    assert 13.0 < area_factor(75.0) < 16.0
    print(f"\n[4] 面积失真因子 sec²(纬度):45°={area_factor(45.0):.1f}×,"
          f" 60°={area_factor(60.0):.0f}×, 75°={area_factor(75.0):.1f}×"
          f"(北京 40°={area_factor(40.0):.2f}×)")

    # ---- 顺带验证墨卡托正算与 Web 地图切割纬度 ±85.0511° ----
    def webmerc_y(lat_deg):  # EPSG:3857 的 y(米)
        return R * math.log(math.tan(math.pi / 4 + math.radians(lat_deg) / 2))
    y_top = webmerc_y(85.0511287798066)
    assert abs(y_top - R * math.pi) < 1.0, "切割纬度应使 y 恰为半个周长(方形世界)"
    print(f"[5] Web Mercator 在 ±85.0511° 切割,投影域恰为正方形"
          f"(y_top/Rπ = {y_top/(R*math.pi):.6f})——极地在这套语言里没有词")

    print("\n" + "=" * 64)
    print("ALL TESTS PASSED (exit 0)")
    sys.exit(0)


if __name__ == "__main__":
    main()
