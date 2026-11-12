# =============================================================================
# 模块定位：src/backends/__init__.py —— 分析后端包的占位入口
# 论文映射：后端抽象对应论文 §3.1.3（把 checker 编译进 CSA 并执行扫描）与
#           §3.1.4（差分验证）。当前唯一实现是 Clang Static Analyzer（csa.py），
#           论文 §6 Generability 讨论了换 CodeQL/Semgrep 等其他引擎的可能性。
# 说明：下方 factory 导入被注释掉，包内模块（csa/factory）由使用方显式 import，
#       此处保持空包语义，避免 import 副作用。
# =============================================================================
# from backends.factory import BackendFactory
