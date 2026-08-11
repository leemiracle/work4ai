"""
CS148 - Computer Graphics & Imaging
覆盖课程模块：CS148 L 光线追踪 + 渲染管线

实现内容：
1. 向量 / 矩阵数学
2. 球体 / 平面几何
3. 光线-几何求交
4. Phong 光照模型
5. 简化光线追踪（输出 ASCII 或 PPM 图像）

参考：Fedkiw CS148 / "Ray Tracing in One Weekend"
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Optional


# ============ 1. 向量数学 ============

@dataclass(frozen=True)
class Vec3:
    x: float
    y: float
    z: float

    def __add__(self, o): return Vec3(self.x+o.x, self.y+o.y, self.z+o.z)
    def __sub__(self, o): return Vec3(self.x-o.x, self.y-o.y, self.z-o.z)
    def __mul__(self, s): return Vec3(self.x*s, self.y*s, self.z*s)
    def dot(self, o): return self.x*o.x + self.y*o.y + self.z*o.z
    def cross(self, o):
        return Vec3(self.y*o.z - self.z*o.y,
                    self.z*o.x - self.x*o.z,
                    self.x*o.y - self.y*o.x)
    def length(self): return math.sqrt(self.dot(self))
    def normalize(self):
        l = self.length()
        return Vec3(self.x/l, self.y/l, self.z/l) if l > 0 else self


# ============ 2. Ray + Geometry ============

@dataclass
class Ray:
    origin: Vec3
    direction: Vec3  # normalized

    def at(self, t: float) -> Vec3:
        return self.origin + self.direction * t


@dataclass
class Sphere:
    center: Vec3
    radius: float
    color: Vec3
    specular: float = 32  # Phong exponent

    def intersect(self, ray: Ray) -> Optional[float]:
        """光线-球体求交（解析法）"""
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = 2 * oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        disc = b*b - 4*a*c
        if disc < 0:
            return None
        sqrt_d = math.sqrt(disc)
        t1 = (-b - sqrt_d) / (2*a)
        t2 = (-b + sqrt_d) / (2*a)
        # 返回最近的正 t
        if t1 > 1e-4: return t1
        if t2 > 1e-4: return t2
        return None

    def normal_at(self, point: Vec3) -> Vec3:
        return (point - self.center).normalize()


@dataclass
class Plane:
    point: Vec3
    normal: Vec3
    color: Vec3

    def intersect(self, ray: Ray) -> Optional[float]:
        denom = ray.direction.dot(self.normal)
        if abs(denom) < 1e-6:
            return None
        t = (self.point - ray.origin).dot(self.normal) / denom
        return t if t > 1e-4 else None

    def normal_at(self, point: Vec3) -> Vec3:
        return self.normal


# ============ 3. 光照（Phong 模型） ============

@dataclass
class Light:
    position: Vec3
    color: Vec3 = None
    intensity: float = 1.0

    def __post_init__(self):
        if self.color is None:
            self.color = Vec3(1, 1, 1)


def phong_shading(point: Vec3, normal: Vec3, view_dir: Vec3,
                   surface_color: Vec3, lights: list[Light],
                   ambient: float = 0.1, specular_strength: float = 0.5,
                   shininess: float = 32) -> Vec3:
    """Phong 光照"""
    color = surface_color * ambient

    for light in lights:
        light_dir = (light.position - point).normalize()
        # Diffuse
        diff = max(0, normal.dot(light_dir))
        # Specular
        reflect_dir = (normal * (2 * normal.dot(light_dir)) - light_dir).normalize()
        spec = max(0, reflect_dir.dot(view_dir)) ** shininess

        color = color + Vec3(
            surface_color.x * light.color.x * diff * light.intensity
              + specular_strength * spec * light.color.x,
            surface_color.y * light.color.y * diff * light.intensity
              + specular_strength * spec * light.color.y,
            surface_color.z * light.color.z * diff * light.intensity
              + specular_strength * spec * light.color.z,
        )
    # Clamp
    return Vec3(min(1, color.x), min(1, color.y), min(1, color.z))


# ============ 4. 简化光线追踪 ============

class Scene:
    def __init__(self):
        self.objects: list = []
        self.lights: list[Light] = []

    def add(self, obj):
        self.objects.append(obj)


def trace_ray(ray: Ray, scene: Scene, max_depth: int = 3) -> Vec3:
    """追踪光线"""
    if max_depth <= 0:
        return Vec3(0, 0, 0)

    # 找最近交点
    closest_t = float('inf')
    closest_obj = None
    for obj in scene.objects:
        t = obj.intersect(ray)
        if t is not None and t < closest_t:
            closest_t = t
            closest_obj = obj

    if closest_obj is None:
        # 背景：渐变
        t = 0.5 * (ray.direction.y + 1)
        return Vec3(1, 1, 1) * (1 - t) + Vec3(0.5, 0.7, 1) * t

    # 着色
    hit_point = ray.at(closest_t)
    normal = closest_obj.normal_at(hit_point)
    view_dir = ray.direction * (-1)
    color = phong_shading(hit_point, normal, view_dir, closest_obj.color, scene.lights,
                            shininess=getattr(closest_obj, 'specular', 32))

    # 阴影
    for light in scene.lights:
        shadow_ray = Ray(hit_point + normal * 1e-3,
                         (light.position - hit_point).normalize())
        for obj in scene.objects:
            if obj is closest_obj: continue
            t = obj.intersect(shadow_ray)
            if t is not None and t < (light.position - hit_point).length():
                # 在阴影中
                color = color * 0.4
                break

    return color


def render_ascii(scene: Scene, width=60, height=20) -> str:
    """渲染 ASCII 图像"""
    chars = " .:-=+*#%@"
    output = []
    camera = Vec3(0, 0, -5)

    for y in range(height):
        row = ""
        for x in range(width):
            # 屏幕坐标 → 世界坐标
            screen_x = (x / width - 0.5) * 2
            screen_y = (0.5 - y / height) * 1.5
            ray_dir = Vec3(screen_x, screen_y, 1).normalize()
            ray = Ray(camera, ray_dir)
            color = trace_ray(ray, scene)
            brightness = (color.x + color.y + color.z) / 3
            char_idx = min(int(brightness * (len(chars)-1)), len(chars)-1)
            row += chars[char_idx]
        output.append(row)
    return "\n".join(output)


def render_ppm(scene: Scene, filename: str, width=200, height=100):
    """渲染 PPM 图像（可被图像软件打开）"""
    with open(filename, "w") as f:
        f.write(f"P3\n{width} {height}\n255\n")
        camera = Vec3(0, 0, -5)
        for y in range(height):
            for x in range(width):
                screen_x = (x / width - 0.5) * 2
                screen_y = (0.5 - y / height) * 1.5
                ray = Ray(camera, Vec3(screen_x, screen_y, 1).normalize())
                color = trace_ray(ray, scene)
                r = int(color.x * 255)
                g = int(color.y * 255)
                b = int(color.z * 255)
                f.write(f"{r} {g} {b}\n")


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CS148: Ray Tracer")
    print("=" * 60)

    scene = Scene()
    # 添加物体
    scene.add(Sphere(Vec3(-1, 0, 2), 0.7, Vec3(1, 0.2, 0.2)))  # 红球
    scene.add(Sphere(Vec3(0.5, 0, 2), 0.5, Vec3(0.2, 1, 0.2)))  # 绿球
    scene.add(Sphere(Vec3(0, -100, 5), 100, Vec3(0.5, 0.5, 0.5)))  # 地面
    # 光源
    scene.lights.append(Light(Vec3(2, 3, -1), intensity=0.8))
    scene.lights.append(Light(Vec3(-3, 1, 0), intensity=0.4))

    print("\n📋 ASCII 渲染:")
    print(render_ascii(scene, width=70, height=20))

    # 写 PPM
    # render_ppm(scene, "scene.ppm", width=200, height=100)
    # print("\n   PPM 图像已保存到 scene.ppm（用图片查看器打开）")

    print("\n💡 CS148 关键概念:")
    print("   - 光线-几何求交（球体解析法 / 平面代数法）")
    print("   - Phong 光照（ambient + diffuse + specular）")
    print("   - 阴影（shadow ray）")
    print("   - 背景渐变（天空色）")
    print("\n✅ CS148 完成！")


if __name__ == "__main__":
    demo()
