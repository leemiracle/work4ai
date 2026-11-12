# =============================================================================
# 模块定位：src/tests/__init__.py —— 测试包的空占位入口
# 说明：真正的测试在 test_backend.py（需要真实 LLVM/内核环境的集成测试）；
#       本目录同时寄放测试夹具：clang-correct.cpp / clang-incorrect.cpp /
#       clang-v8.cpp（一好两坏的示例 checker 源码）与 commit_id.txt /
#       commit_v8.txt（Linux/V8 各一条真实 bug-fix commit id）。
# =============================================================================
