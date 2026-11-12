# =============================================================================
# 【模块定位】V8 JavaScript 引擎目标实现——fork 增量（上游 PR #14/#16），论文
#   §6 Generability 讨论"KNighter 可迁移到 Chromium 生态"的代码落地：TargetFactory
#   四接口的 gn/ninja（C++）版本。与 Linux 目标的本质差异：V8 无 kbuild，因此
#   ① 没有 make allyesconfig，构建改由 gn gen 生成 ninja 文件；
#   ② CSA 扫描不再靠 .o 反查唯一支撑——gn gen --export-compile-commands 额外产出
#      out/{arch}.release/compile_commands.json，backends/csa.py 按源文件从中提取
#      精确编译命令（get_source_files_from_patch() 即为此配套，专返回源文件列表）。
#
# 【论文映射】
#   - checkout_commit()：§3.1.4 差分验证的环境准备（is_before=True/False 分别对
#     buggy/patched 两侧），V8 语义下多了依赖同步（gclient）与版本兼容补丁；
#   - get_objects_from_patch()/get_object_name()：与 Linux 同构的"扫 patch 涉及
#     对象"，只是对象路径带 obj/ 前缀（ninja 布局）；
#   - get_source_files_from_patch()：V8 特有——compile_commands.json 按源文件
#     （而非 .o）索引，差分验证两轮各取一次对应 commit 的编译命令集。
#
# 【管线角色】上游：src/global_config.py 读 v8_dir 配置实例化 V8（target_type
#   =="v8" 时装配）；下游：src/backends/csa.py（checkout_commit、
#   get_source_files_from_patch + out/x64.release/compile_commands.json 提取编译
#   条目、V8.get_object_name 对象路径换算）。
#
# 【依赖与坑】
#   - 数据文件 v8-build-commands.txt（同目录，约 200KB）：ninja 构建输出日志，对象
#     路径形如 obj/xxx/foo.o，是 get_object_name 反查数据源（import 时读入）。
#   - depot_tools 工具链：gclient（依赖同步）与 gn（构建文件生成）都可能不在
#     PATH，代码里做了多路径探测；gclient 缺失仅告警跳过（依赖已有缓存时可继续）。
#   - 坑：V8 全量构建极耗时，kwargs 提供 skip_v8_build 复用已有 out/ 目录（迭代
#     refine 时省去重编译）；
#   - 坑：checker plugin 针对自带 LLVM 编译，必须用 clang_base_path 钉死同一
#     工具链并禁用 Chromium 自带 clang 插件，否则构建/分析不兼容；
#   - 坑：跨年代 checkout 会踩 GN 配置改名（exec_script_whitelist → allowlist），
#     _fix_exec_script_naming() 在 gn gen 前自动打双向补丁。
# =============================================================================
import re                                    # 正则：构建日志反查 obj/*.o、从 diff 提取文件名
import subprocess as sp                      # 子进程：rm/gclient sync/gn gen
from datetime import datetime                # 历史遗留导入：当前文件体内并未使用
from pathlib import Path                     # 路径处理：.gn 文件定位、LLVM 路径转换、stem 提取
from shutil import which                     # 在 PATH 中查找可执行文件（gclient/gn）
from typing import List                      # 类型注解 List[str]

from loguru import logger                    # loguru 结构化日志（info/warning/error）

from targets.factory import TargetFactory    # 抽象基类：本类实现其四个接口（+1 个 V8 特有）


# -----------------------------------------------------------------------------
# V8（Chromium 的 JavaScript 引擎，C++/gn/ninja）仓库目标。
# -----------------------------------------------------------------------------
class V8(TargetFactory):
    """
    A class representing the V8 JavaScript engine repository.
    """
    # ↑ 原有 docstring 原样保留

    _target_type = "v8"                      # 类型标识："v8"——global_config 按
                                             # target_type=="v8" 选用本类实例
    _build_commands = (Path(__file__).parent / "v8-build-commands.txt").read_text()
                                             # 类属性（import 时求值）：读入同目录 ninja
                                             # 构建输出日志——对象路径形如
                                             # obj/<target>/<file>.o，是 get_object_name
                                             # 反查对象名的数据源

    # -----------------------------------------------------------------------------
    # 【接口 1 实现】checkout + V8 构建环境准备（差分验证前置）。流程：
    #   1) （可选 skip_v8_build=True 跳过清理，保留已有 out/ 目录省重编译）；
    #   2) rm -rf out 清旧构建产物；
    #   3) is_before=True 时 commit_id 改写为 "<id>^"（父提交 = buggy 版本）；
    #   4) git reset --hard + clean -fd 清未提交改动（上次 _fix_exec_script_naming
    #      会改 .gn 留下脏工作区）；
    #   5) git checkout；
    #   6) gclient sync 同步 Chromium 依赖（gclient 与 .gclient 配置都可用才做）；
    #   7) gn gen out/{arch}.release --args=... --export-compile-commands 生成
    #      ninja 文件 + compile_commands.json（V8 路线的核心产物）。
    # kwargs 参数：arch（默认 "x64"）；llvm_path 自定义 LLVM 路径；
    #   skip_v8_build 是否保留已有构建。
    # -----------------------------------------------------------------------------
    def checkout_commit(self, commit_id, is_before=False, **kwargs):
        """
        Checkout a specific commit in the V8 repository and prepare the build environment.

        Args:
            commit_id (str): The commit ID to checkout.
            is_before (bool): Whether to checkout before the commit.
            arch (str): The architecture to build for.
            build_config (str): The build configuration (debug/release).
            llvm_path (str/Path): Custom LLVM path to use (optional).
            skip_v8_build (bool): Skip V8 build (preserve existing out/ directory).
        """
        # Extract skip_v8_build flag from kwargs
        skip_v8_build = kwargs.get("skip_v8_build", False)
                                             # 迭代 refine/重复验证时可传 True 复用已有
                                             # out/（含 compile_commands.json），免去全量重编

        logger.info(
            f"Checking out commit {commit_id} {'before' if is_before else 'after'}"
        )
                                             # 记录 checkout 方向：before=父提交（buggy，
                                             # N_buggy 侧）/ after=补丁提交（patched 侧）

        if skip_v8_build:
            logger.info("Skipping V8 build - preserving existing out/ directory")
                                             # 跳过分支：只记日志，out/ 原样保留
        else:
            # Clean previous build artifacts
            logger.info("Cleaning previous build artifacts")
            res = sp.run(
                ["rm", "-rf", "out"], cwd=self.repo.working_dir, capture_output=True
            )
                                             # rm -rf out：删除整个构建输出目录——旧
                                             # compile_commands.json/对象文件与新 commit
                                             # 不符会误导差分验证
            if res.returncode != 0:
                logger.warning(f"Failed to clean out directory: {res.stderr.decode()}")
                                             # 仅告警不抛错（out/ 不存在等场景可继续）

        if is_before:
            commit_id = commit_id + "^"      # 与 Linux 同款的 buggy 定义：父提交 = 补丁
                                             # 尚未合入（bug 还在）的版本

        # Reset any uncommitted changes from previous runs
        try:
            self.repo.git.reset("--hard")    # 硬重置：丢弃工作区/暂存区的全部未提交改动
            self.repo.git.clean("-fd")       # 删除未跟踪文件与目录（-f 强制 -d 含目录）——
                                             # 上一轮 _fix_exec_script_naming 改写的 .gn
                                             # 与残留补丁文件都在清理之列
        except Exception as e:
            logger.warning(f"Failed to clean repository state: {e}")
                                             # 清理失败仅告警：后面 checkout 若被脏状态
                                             # 阻塞会自然报错，信息更准确

        self.repo.git.checkout(commit_id)    # 工作树切到目标提交（buggy 或 patched）

        # Try to sync dependencies with gclient only if available and configured
        repo_dir = Path(self.repo.working_dir)   # 仓库根目录（后面找 .gclient/gn 都基于它）
        gclient_exe = which("gclient")           # 先在 PATH 里找 gclient（depot_tools 入口）

        # If gclient not in PATH, try common locations
        if not gclient_exe:
            potential_paths = [                  # depot_tools 的常见安装位置（人工经验清单）：
                Path.home() / "depot_tools" / "gclient",   # 用户目录源码安装
                Path("/usr/local/bin/gclient"),             # 系统级软链
                Path("/opt/depot_tools/gclient"),           # /opt 安装
            ]
            for path in potential_paths:
                if path.exists():                # 逐个探测，找到即用
                    gclient_exe = str(path)
                    break

        has_gclient_config = (repo_dir / ".gclient").exists() or (
            repo_dir.parent / ".gclient"
        ).exists()
                                                 # .gclient 是 gclient workspace 的标识文件，
                                                 # 可能在仓库根或其父目录（V8 作为 workspace
                                                 # 内的子 checkout 时在父目录）——两处都查

        if gclient_exe and has_gclient_config:
            logger.info("Syncing dependencies with gclient...")
            res = sp.run(
                [gclient_exe, "sync"],           # 按 DEPS 文件把 buildtools/icu/test262 等
                                                 # 第三方依赖同步到该 commit 钉住的版本
                cwd=self.repo.working_dir,
                capture_output=True,
                timeout=600,                     # 10 分钟超时：依赖同步可能很慢
                text=True,                       # 文本模式（stdout/stderr 直接是 str）
            )
            if res.returncode != 0:
                logger.error(f"Failed to sync dependencies: {res.stderr}")
                logger.warning("Dependency sync failed, attempting build anyway...")
                                                 # 同步失败不中断：本地依赖缓存大概率够用，
                                                 # 让 gn gen 自己暴露真正的缺口
            else:
                logger.info("Dependency sync completed.")
        else:
            if not gclient_exe:
                logger.warning("Skipping gclient sync: 'gclient' not found on PATH.")
                                                 # 无 gclient：多数 CI/离线场景，明确告警原因
            if not has_gclient_config:
                logger.warning(
                    "Skipping gclient sync: .gclient not found (client not configured)."
                )
                                                 # 无 .gclient：这不是 gclient workspace，
                                                 # 同样跳过（两个条件可同时缺失，两条都打）

        # Generate build files using gn
        arch = kwargs.get("arch", "x64")     # 目标架构，V8 默认 x64（与 csa.py 消费的
                                             # out/x64.release/compile_commands.json 对齐）
        # build_config = kwargs.get('build_config', 'release')
        build_dir = f"out/{arch}.release"    # 构建输出目录：gn 布局固定为 out/<arch>.<config>
                                             # （release 后缀硬编码；上面被注释掉的
                                             # build_config 参数是未完成的扩展点）

        # Check if we should use custom LLVM (from kwargs or fallback to hardcoded path)
        custom_llvm_path = kwargs.get("llvm_path")
                                             # 调用方可指定自带 LLVM 目录——KNighter 的
                                             # checker plugin 针对该版本编译，分析用的
                                             # clang 必须与构建工具链同源

        # Convert to Path if string provided
        if custom_llvm_path and not isinstance(custom_llvm_path, Path):
            custom_llvm_path = Path(custom_llvm_path)
                                             # 归一化为 Path（str 入参兼容），下面统一
                                             # 用 .exists() 探测

        if custom_llvm_path and custom_llvm_path.exists():
            logger.info(f"Using custom LLVM from {custom_llvm_path}")

            gn_args = [                      # 自带 LLVM 分支：完整 gn 参数集——核心诉求
                                             # 是"绕开 Chromium clang 发行版，改用 KNighter
                                             # 自带 LLVM 重建 V8"（分析/构建工具链同源）
                f'target_cpu="{arch}"',      # 目标 CPU 架构
                f"is_debug=false",           # release 构建（f 前缀无占位符，冗余但无害）
                "v8_static_library=true",    # V8 产出静态库而非组件化共享库
                f'clang_base_path="{custom_llvm_path}"',
                                             # clang 工具链根目录：指向自带 LLVM
                "clang_use_chrome_plugins=false",
                                             # 禁用 Chromium clang 发行版自带插件（与新
                                             # LLVM 版本不兼容，会构建失败）
                'clang_version="21"',        # 声明 clang 版本号（配合 base_path 定位安装）
                "use_custom_libcxx=true",    # 用 Chromium 捆绑的 libc++（V8 代码假定其行为）
                "is_clang=true",             # 明确走 clang（同 Linux 侧 LLVM=1 的动机）
                # Use LLVM's ar and ranlib to avoid index issues
                f'ar="{custom_llvm_path}/bin/llvm-ar"',
                                             # 归档工具换 LLVM 系（原注释：避免索引问题）
                f'ranlib="{custom_llvm_path}/bin/llvm-ranlib"',
                                             # 归档索引工具同上
                "treat_warnings_as_errors=false",
                                             # 关 -Werror：历史代码告警多，防构建被警告打断
                "use_lld=true",              # 链接器用 lld（LLVM 全家桶，配合自定义工具链）
                "llvm_android_mainline=true",# V8 上游 gn 参数（主线 Android 配置），随上游引入
            ]
        else:
            logger.info(
                "Using system clang (no custom LLVM path provided or path doesn't exist)"
            )
                                             # 未提供/路径无效 → 退回系统 clang

            gn_args = [                      # 系统 clang 分支：最小参数集（保持 V8 默认
                                             # 工具链，仅保证扫描所需的基本形态）
                f'target_cpu="{arch}"',      # 目标 CPU 架构
                f"is_debug=false",           # release 构建
                "v8_static_library=true",    # 静态库
            ]

        # Locate gn from PATH or common V8 location
        gn_exe = which("gn")                 # 先查 PATH（depot_tools 在 PATH 时可用）
        if not gn_exe:
            candidate = repo_dir / "buildtools" / "linux64" / "gn"
                                             # V8 仓自带 gn 的固定位置（gclient sync 拉取）
            if candidate.exists():
                gn_exe = str(candidate)      # 命中则直接用仓内 gn
        if not gn_exe:
            raise RuntimeError(
                "GN executable not found. Install depot_tools or ensure 'gn' is on PATH (or at buildtools/linux64/gn)."
            )
                                             # 两处都找不到 → 硬失败并给出修复指引
                                             # （没有 gn 就无法生成 ninja/compile_commands）

        # Apply version-specific patches before generating build files
        self._apply_version_patches()
                                             # gn gen 前打版本兼容补丁（当前只有 .gn
                                             # 命名改名一处，见 _fix_exec_script_naming）；
                                             # 必须在 gen 之前——gen 解析 .gn 时就要求一致

        logger.info(
            f"Generating build files for {arch.upper()} with arguments: {' '.join(gn_args)}"
        )
                                             # 记录架构与完整 gn 参数（复现构建的依据）
        # Also export compile_commands.json for CodeChecker analysis
        res = sp.run(
            [
                gn_exe,
                "gen",                       # 生成构建文件（ninja 文件 + 声明的导出产物）
                build_dir,                   # 输出目录 out/<arch>.release
                f"--args={' '.join(gn_args)}",
                                             # 全部 gn 参数拼成一行传入
                "--export-compile-commands", # 关键开关：额外导出 compile_commands.json——
                                             # V8 路线里 CSA 按源文件从这里取精确编译
                                             # 命令（替代 Linux 的 .o 反查路线）
            ],
            cwd=self.repo.working_dir,
            capture_output=True,
            text=True,                       # 文本模式收集输出
        )
        if res.returncode != 0:
            logger.error(f"Failed to generate build files: {res.stderr}")
            logger.error(res.stdout)         # gn 的错误详情常在 stdout（如参数拼写错误）
            raise RuntimeError(f"Failed to generate build files: {res.stderr}")
                                             # 构建文件生成失败 = 无 compile_commands 可
                                             # 用，差分验证无法进行，硬中断

    # -----------------------------------------------------------------------------
    # 【内部方法】应用版本相关的兼容补丁（checkout 之后、gn gen 之前调用）。
    # 当前仅一处：GN 配置项改名导致的跨版本构建失败（见下方具体补丁方法）。
    # -----------------------------------------------------------------------------
    def _apply_version_patches(self):
        """
        Apply version-specific patches to handle build system incompatibilities.
        This method is called after checking out a commit to fix known issues.
        """
        # Fix exec_script_whitelist -> exec_script_allowlist change
        self._fix_exec_script_naming()       # .gn 与 build/dotfile_settings.gni 的命名
                                             # 一致性修补（双向）

    # -----------------------------------------------------------------------------
    # 【内部方法】修补 exec_script_whitelist ↔ exec_script_allowlist 命名错配。
    # 背景：2025-04 前后 V8 上游把 GN 的 exec_script_whitelist 改名为
    #   exec_script_allowlist（commit 51d69ed8f8d）；KNighter 会 checkout 不同年代
    #   的 commit，可能出现 ".gn 用新名、build/dotfile_settings.gni 还是旧名"（或
    #   反向）的错配——gn gen 直接报"未定义变量"。
    # 策略：读 .gn 与 build/dotfile_settings.gni，按"gni 定义什么名、.gn 就用什么名"
    #   双向替换。任何异常只告警不中断（非致命，让构建用自身报错定位更直观）。
    # -----------------------------------------------------------------------------
    def _fix_exec_script_naming(self):
        """
        Fix the exec_script_whitelist -> exec_script_allowlist naming change.
        This change occurred in V8 around April 2025 (commit 51d69ed8f8d).
        """
        gn_file = Path(self.repo.working_dir) / ".gn"
                                             # V8 仓根的 .gn 配置文件（GN 的入口 dotfile）
        if not gn_file.exists():
            return                           # 没有 .gn 就无事可做（异常仓库布局）

        try:
            content = gn_file.read_text()    # 读 .gn 全文准备检测/替换

            # Check if we need to patch (has old naming)
            if "exec_script_whitelist" in content:
                # .gn 还是旧名——再看构建系统（gni）用的是哪个名
                # First check if build_dotfile_settings has the new naming
                dotfile_settings = (
                    Path(self.repo.working_dir) / "build" / "dotfile_settings.gni"
                )
                                             # exec_script_*list 的定义处（随 V8 构建脚本走）
                if dotfile_settings.exists():
                    settings_content = dotfile_settings.read_text()
                    if (
                        "exec_script_allowlist" in settings_content
                        and "exec_script_whitelist" not in settings_content
                    ):
                        # gni 已全面切到新名（有新无旧）→ .gn 必须跟着改
                        # The build system uses new naming but .gn uses old - need to patch
                        logger.info(
                            "Patching .gn file: exec_script_whitelist -> exec_script_allowlist"
                        )
                        patched_content = content.replace(
                            "exec_script_whitelist", "exec_script_allowlist"
                        )
                                             # 全文替换为新名（旧→新方向）
                        gn_file.write_text(patched_content)
                                             # 就地写回 .gn（这也是 checkout 前要
                                             # git reset --hard 的原因：会弄脏工作区）
                        logger.info("Successfully patched .gn file for compatibility")

            # Handle the reverse case (old build system, new .gn file)
            elif "exec_script_allowlist" in content:
                # .gn 已是新名——反向检查 gni 是否还停在旧名
                dotfile_settings = (
                    Path(self.repo.working_dir) / "build" / "dotfile_settings.gni"
                )
                if dotfile_settings.exists():
                    settings_content = dotfile_settings.read_text()
                    if (
                        "exec_script_whitelist" in settings_content
                        and "exec_script_allowlist" not in settings_content
                    ):
                        # gni 还是旧名（有旧无新）→ 把 .gn 回退成旧名
                        # The build system uses old naming but .gn uses new - need to patch
                        logger.info(
                            "Patching .gn file: exec_script_allowlist -> exec_script_whitelist"
                        )
                        patched_content = content.replace(
                            "exec_script_allowlist", "exec_script_whitelist"
                        )
                                             # 反向替换（新→旧），保证与老构建系统一致
                        gn_file.write_text(patched_content)
                        logger.info("Successfully patched .gn file for compatibility")

        except Exception as e:
            logger.warning(f"Failed to apply exec_script patch: {e}")
            # Non-fatal - let the build fail with proper error message if needed
                                             # 补丁失败不致命：交给 gn gen 用原生报错暴露

    # -----------------------------------------------------------------------------
    # 【接口 2 实现】源文件名 → V8 ninja 对象(.o)路径（静态方法）。
    # 与 Linux 版同构：v8-build-commands.txt（ninja 输出）里对象都在 obj/ 下，
    # 用 "obj/.*?<stem>\.o" 捞同 stem 候选，path_similarity 消歧取最相似。
    # 参数 file_name：patch 中的源文件路径（如 src/objects/objects.cc）。
    # 返回：对象路径字符串；查不到时回退 "obj/<源路径换 .o>"。
    # -----------------------------------------------------------------------------
    @staticmethod
    def get_object_name(file_name: str) -> str:
        """
        Get the object file name for a given source file in V8 build system.
        """
        file_path = Path(file_name)           # 包装 Path 取 stem
        stem_name = file_path.stem            # 源文件主名（objects.cc → objects）

        # V8 uses ninja build system, object files are typically in obj/ subdirectory
        pattern = rf"obj/.*?{stem_name}\.o"
                                             # 匹配 "obj/<若干字符><stem>.o"：obj/ 是
                                             # ninja 对象目录前缀；.*? 非贪婪吃掉 target
                                             # 名/子目录；{stem_name} f-string 注入主名；
                                             # \.o 对象后缀（raw 串保住 \ 语义）
        match = re.search(pattern, V8._build_commands)
                                             # 先探测是否存在任一匹配
        if match:
            all_matches = re.findall(pattern, V8._build_commands)
                                             # 全量捞出所有匹配串（整个匹配，形如
                                             # obj/xxx/objects.o——无需像 Linux 那样
                                             # 剥 "-o " 前缀，ninja 行本身就是路径）
            # Sort by path similarity to the file name
            all_matches.sort(
                key=lambda x: V8.path_similarity(x, file_name), reverse=True
            )
                                             # 同 stem 多候选（如 objects.cc 与
                                             # objects-inl 相关同名）按路径组件 Jaccard
                                             # 相似度降序，最相似的排最前
            return str(all_matches[0])        # 取最相似者
        else:
            # If not found, return the default name based on V8 build structure
            # V8 typically puts objects in obj/ with directory structure preserved
            relative_path = file_path.with_suffix(".o")
                                             # 源路径把 .cc/.cpp/.c 换成 .o
            return f"obj/{relative_path}"    # 再冠以 obj/ 前缀（保目录结构的兜底猜测）

    # -----------------------------------------------------------------------------
    # 【接口 3 实现】bug-fix patch → 待分析对象列表（静态方法）。
    # 与 Linux 版同构，差别只在文件过滤集合：V8 主体是 C++（.cc），同时兜住
    # .cpp/.c（仓库里少数 C 文件）。
    # 参数 patch：unified diff 文本。返回：obj/ 对象路径列表。
    # -----------------------------------------------------------------------------
    @staticmethod
    def get_objects_from_patch(patch: str) -> List[str]:
        """
        Get the objects to analyze from a patch.
        """
        # Find `--- a/` lines in the patch
        pattern = r"^--- a/(.*)$"             # unified diff 旧文件行：--- a/<路径>，
                                             # 捕获组取相对路径
        matches = re.findall(pattern, patch, re.MULTILINE)
                                             # MULTILINE 逐行匹配，捞出全部涉及文件
        # Filter for C++ files (V8 is primarily C++)
        matches = [match for match in matches if match.endswith((".cc", ".cpp", ".c"))]
                                             # 元组形式 endswith：留 .cc/.cpp/.c；
                                             # .h 等头文件被过滤（影响体现在包含它的
                                             # 源文件里）
        # Convert to object file names
        matches = [V8.get_object_name(match) for match in matches]
                                             # 逐个映射成 obj/ 对象路径
        return matches                        # 交给 csa.py 驱动 CSA 扫描

    # -----------------------------------------------------------------------------
    # 【V8 特有】bug-fix patch → 源文件列表（静态方法，TargetFactory 没有的扩展）。
    # 存在原因：V8 路线的 CSA 扫描以 compile_commands.json 为准，而它按"源文件
    #   路径"索引（不是 .o）；backends/csa.py 差分验证两轮分别用它取 buggy/
    #   patched 各自的精确编译命令。
    # 参数 patch：unified diff 文本。返回：源文件路径列表（原样，不做对象映射）。
    # -----------------------------------------------------------------------------
    @staticmethod
    def get_source_files_from_patch(patch: str) -> List[str]:
        """
        Get the source files to analyze from a patch.
        """
        # Find `--- a/` lines in the patch
        pattern = r"^--- a/(.*)$"             # 同上：diff 旧文件行
        matches = re.findall(pattern, patch, re.MULTILINE)
                                             # 捞出全部涉及文件
        # Filter for C++ files (V8 is primarily C++)
        matches = [match for match in matches if match.endswith((".cc", ".cpp", ".c"))]
                                             # 同款 C/C++ 过滤
        return matches                        # 直接返回源文件路径（与上面两步走形成
                                             # 对照：这里刻意不做 .o 映射）
