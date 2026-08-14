# CS147L: Mobile App Development

> Stanford University, Autumn 2026
> 领域: 移动开发 / HCI 实践
> Prerequisites: CS106B 或同等编程经验
> Units: 1-2（实验课，配合 CS147）
> Difficulty: ⭐⭐

---

## 📚 定位

从设计到代码构建移动应用——掌握响应式 UI、状态管理、原生 API，配合 CS147 HCI 理论。

---

## 🎯 学习目标

- 掌握响应式 UI 编程范式
- 理解移动端状态管理
- 能调用平台原生 API（相机、定位、存储）
- 完成从原型到发布的完整流程

---

## 📅 核心模块

### Module 1: 响应式 UI 基础
- 声明式 UI vs 命令式 UI
- Widget / Component 树
- 状态驱动渲染（setState → rebuild）

### Module 2: 状态管理
- 单向数据流
- 局部状态 vs 全局状态
- Provider / Riverpod / Redux / Zustand
- 持久化状态（SharedPreferences / SQLite）

### Module 3: 导航与生命周期
- 页面路由与导航栈
- App 生命周期事件
- 平台差异（iOS vs Android）

### Module 4: 原生集成
- 相机与图库
- 定位与地图
- 推送通知
- 后台任务

### Module 5: 发布与优化
- 性能优化（列表懒加载、图片缓存）
- 无障碍（Accessibility）
- App Store / Play Store 发布流程
- 热更新与 A/B 测试

---

## 💻 项目代码

📁 `supplementary/undergrad_projects.py::cs147l_demo`

**实现内容**:
1. ✅ 响应式状态管理模拟（React/Flutter 风格）
2. ✅ setState → 通知监听者 → 重新渲染
3. ✅ Widget 树概念与操作序列演示

**运行**:
```bash
cd supplementary
python3 undergrad_projects.py
```

**输出示例**:
```
初始: Counter: 0 | User: None | Loading: False
操作序列:
  [Re-render] Counter: 1 | User: None | Loading: False
  [Re-render] Counter: 2 | User: None | Loading: False
  [Re-render] Counter: 2 | User: None | Loading: True
  [Re-render] Counter: 2 | User: Alice | Loading: False
关键: Widget tree / State management / Hooks
```

---

## 📊 关键概念

| 概念 | 说明 |
|------|------|
| **声明式 UI** | 描述"是什么"而非"怎么做" |
| **状态管理** | 单一数据源 + 响应式更新 |
| **Widget 树** | 组合式 UI 构建方式 |
| **生命周期** | App 前后台切换的资源管理 |

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **CS147 学生** | 理论 + 实践配对 |
| **移动开发入门** | Flutter / React Native |
| **创业者** | 快速原型到 MVP |
| **全栈方向** | 移动端补充 |

---

## 🚀 扩展方向

1. 学习 Flutter（Dart）或 React Native（JS）
2. 阅读 *Designing Data-Intensive Applications*（后端配合）
3. 探索 SwiftUI / Jetpack Compose（原生声明式）
4. 发布一个 App 到 App Store

---

**对应代码**: `supplementary/undergrad_projects.py::cs147l_demo`
