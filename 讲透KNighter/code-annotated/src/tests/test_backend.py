# =============================================================================
# 模块定位：src/tests/test_backend.py —— CSA 后端的最小回归测试（unittest）
# 论文映射：不直接对应论文章节，属工程配套质量保障；测试对象是论文 §3.1.3/§3.1.4
#           中"checker 必须能编译、能被 repair agent 修复、能通过 buggy/patched
#           差分验证（validate_checker → 返回 (N_buggy, N_patched)）"这三件事。
# 管线角色：开发者改动了 backends/csa.py 或 checker_repair.py 后跑本测试确认
#           基础链路（编译 checker → 修复坏 checker → 双版本验证）没有被破坏。
# 关键依赖：config.yaml（真实 LLVM/Linux 路径）+ tests/clang-{correct,incorrect}.cpp
#           （一好一坏两个示例 checker 源码）+ commit_id.txt / commit_v8.txt（验证用
#           真实 commit）。注意：跑测试需要完整 LLVM 环境，不是纯单元测试。
# =============================================================================
# 把上级目录（src/）加入 sys.path，使包内模块可以按平铺方式 import（如 import global_config）
import sys
from pathlib import Path

# 计算本文件上上级目录 = src/，插入 sys.path 首位，保证优先命中仓库内模块而非环境里同名包
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
# 标准库 unittest：本文件用类组织测试（非 pytest 风格）
import unittest

# 被测三件套：全局配置单例、多 LLM 客户端、语法修复 agent（论文 §3.1.3 Syntax Repair）
import global_config
import model
from checker_repair import repair_checker
# 目标系统抽象：Linux 内核（论文主目标）与 V8（fork 增量，对应论文 §6 Generability）
from targets.factory import TargetFactory


# CSA 后端集成测试类：编译/修复/差分验证三条基础能力各一个用例
class TestClangBackend(unittest.TestCase):

    def setUp(self):
        # 每个用例前重建环境：读取 config.yaml 初始化全局配置单例（LLVM 路径、kernel 路径、backend 等）
        global_config.global_config.setup("config.yaml")

        # 依配置里的模型/key 初始化多 LLM 客户端（repair 用例需要真实调用 LLM）
        model.init_llm()
        # backend 是全局配置装配出的 CSA 后端实例（src/backends/csa.py）
        self.backend = global_config.global_config.backend

        # 读入"应当编译成功"的示例 checker 源码（一个合法的 CSA checker）
        self.correct_checker_code = (
            Path(__file__).parent / "clang-correct.cpp"
        ).read_text()
        # 读入"应当编译失败"的示例 checker 源码（故意含语法/接口错误，供 repair 用例使用）
        self.incorrect_checker_code = (
            Path(__file__).parent / "clang-incorrect.cpp"
        ).read_text()
        # Linux 目标验证用的真实 bug-fix commit id（txt 内为单行 40 位 hash）
        self.commit_id = (Path(__file__).parent / "commit_id.txt").read_text().strip()

        # 测试日志目录（编译输出/扫描报告落点），不存在则递归创建
        self.log_dir = Path("logs_test")
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def test_build_checker(self):
        # 验证 build_checker：合法 checker 源码应编译成功（return_code == 0）
        return_code, _ = self.backend.build_checker(
            self.correct_checker_code, self.log_dir, attempt="correct"
        )
        # 编译产物按 attempt 名区分存放，故两个编译用例互不覆盖
        self.assertEqual(
            return_code, 0, "Build checker failed with non-zero return code."
        )

    def test_build_checker_incorrect(self):
        # 反向用例：含错误的 checker 源码必须编译失败（return_code != 0），
        # 否则说明编译链路没有真正校验代码（例如误用了缓存产物）
        return_code, _ = self.backend.build_checker(
            self.incorrect_checker_code, self.log_dir, attempt="incorrect"
        )
        self.assertNotEqual(
            return_code, 0, "Build checker succeeded with incorrect code."
        )

    def test_repair_checker(self):
        # 验证论文 §3.1.3 的 Syntax Repair agent：喂编译失败的 checker 源码，
        # repair_checker 应基于编译错误信息用 LLM 修出一份能编译的新代码
        result = repair_checker(
            "test_id", "1", checker_code=self.incorrect_checker_code
        )
        # result[0]=是否修复成功（True）；result[1]=修复后的 checker 源码（非 None）
        self.assertTrue(result[0], "Repair checker failed.")
        self.assertIsNotNone(result[1], "Repair checker returned None code.")

    def test_evaluate_linux(self):
        # 验证论文 §3.1.4 Validation（差分验证）：对 Linux 目标，
        # 用 clang-correct.cpp 这个 checker 扫 buggy/patched 两个版本，
        # 期望返回 (N_buggy=1, N_patched=1)——即原 bug 报出且补丁后无残留报告
        # （阈值判据 N_buggy > N_patched 在上层调用方实现，这里只断言原始计数）
        linux: TargetFactory = global_config.global_config.get("linux")
        # 从内核仓提取该 commit 的 patch 文本（差分验证需要知道改了哪些文件）
        patch = linux.get_patch(self.commit_id)

        # validate_checker 返回 (N_buggy, N_patched) 二元组
        result = self.backend.validate_checker(
            self.correct_checker_code, self.commit_id, patch, linux
        )
        self.assertEqual(result, (1, 1), "Validation failed for Linux target.")

    def test_evaluate_v8(self):
        # 同上，但目标是 V8（fork 增量能力，论文 §6 Generability 提到可迁移到 Chromium）：
        # V8 用独立的 commit id 与专用示例 checker（clang-v8.cpp）
        # Initialize the correct checker code and commit id for V8 target
        v8: TargetFactory = global_config.global_config.get("v8")
        # 读取 V8 目标的 commit id（覆盖 setUp 里设置的 Linux 用 self.commit_id）
        self.commit_id = (Path(__file__).parent / "commit_v8.txt").read_text().strip()
        # V8 示例 checker 源码（针对 V8 代码库 API 的 checker）
        v8_checker_code = (Path(__file__).parent / "clang-v8.cpp").read_text()

        # 提取 V8 仓该 commit 的 patch，执行同样的差分验证
        patch = v8.get_patch(self.commit_id)
        result = self.backend.validate_checker(
            v8_checker_code, self.commit_id, patch, v8
        )
        self.assertEqual(result, (1, 1), "Validation failed for V8 target.")


# 直接运行本文件时进入 unittest 主流程（python3 test_backend.py）
if __name__ == "__main__":
    unittest.main()
