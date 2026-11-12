# =============================================================================
# 【模块定位】全局配置中心：GlobalConfig 单例集中管理 YAML 配置、LLM 密钥、
#              文件日志、扫描目标（target）与分析后端（backend）。
# 【论文映射】论文两阶段管线（§3.1 Checker Synthesis / §3.2 Refinement）的
#   运行时参数与实验设置载入层；各模式（gen/refine/scan/triage/label）经
#   main.init_config → setup() 统一初始化。关键配置项的论文语义：
#   - model："o3-mini"（论文默认 LLM；GPT-4o/DeepSeek-R1/Gemini-2-flash 为
#     §4 消融模型，见 model.py）；
#   - group_scan_timeout=3600s ↔ 论文 §3.2 "refine 期间全库扫描限 1 小时"；
#   - max_fp_reports_for_refinement=5 ↔ 论文 §3.2 "采样 5 条报告判 FP"；
#   - refine 期间的 100 warnings 上限在 checker_scan.collect_reports 的
#     max_num_reports=100；论文接受阈值 T_valid=50 / T_plausible=20 不在本
#     文件，属生成/精化模块内部的判定逻辑（若硬编码也应在彼处寻找）。
# 【管线角色】被所有 src/ 模块共享：agent.py 读 result_dir 组织 prompt 历史
#   目录；model.py 读密钥初始化 LLM 客户端；checker_scan/checker_refine 读
#   扫描超时/并行度/FP 采样数；targets/（Linux/V8）与 backends/（CSA）的
#   实例也缓存在本单例的 _config 里。
# 【依赖与坑】①单例只防重复 setup、不防重复 __init__：GlobalConfig() 再被
#   调用一次，__init__ 会把已载入的 _config/_keys 清空（当前安全仅因全仓
#   只在文件尾实例化一次）；②配置/密钥文件缺失直接 exit(-1) 杀进程（快速
#   失败策略）；③loguru 文件日志按天轮转、保留 7 天、DEBUG 级，文件名带
#   result_dir 末段名与时间戳。
# =============================================================================
import time  # 给日志文件名生成 %Y-%m-%d-%H-%M-%S 时间戳
from pathlib import Path  # 日志目录与 result_dir 的路径处理
from typing import Any, Dict, List, Optional  # 配置字典/属性返回值的类型标注

import loguru  # 日志框架：logger.add 挂文件 sink（轮转/保留策略见 _init_logger）
import yaml  # 配置文件与密钥文件均为 YAML；safe_load 只解析不执行（安全）

from backends.csa import ClangBackend  # CSA 分析后端（论文核心引擎：plugin
# 编译 / scan-build 扫描 / ExplodedGraph 报告解析的封装，见 csa.py）
from backends.factory import AnalysisBackendFactory  # 后端抽象基类（仅作类型标注）
from targets.factory import TargetFactory  # 目标抽象基类（仅作类型标注）
from targets.linux import Linux  # Linux 内核目标（论文主实验：allyesconfig 构建）
from targets.v8 import V8  # V8 目标（fork 增量：Chromium/V8 泛化，对应论文
# Generability 讨论部分）

logger = loguru.logger  # 模块级日志器：默认输出 stderr；setup 后追加文件 sink


# 单例模式：保证全进程共享同一份配置（agent/model/scan/refine 读到同状态）
class GlobalConfig:
    """Singleton class to manage global configuration settings."""

    # 类级单例槽位：首次实例化后缓存于 _instance，后续 GlobalConfig() 复用
    _instance = None

    def __new__(cls, *args, **kwargs):
        # 仅第一次调用真正分配对象；之后直接返回缓存实例
        if not cls._instance:
            # 走父类 object.__new__ 分配内存（透传 *args/**kwargs 兼容协议）
            cls._instance = super(GlobalConfig, cls).__new__(cls, *args, **kwargs)
            # 创建时置 _initialized=False：标记"尚未 setup"，允许首次 setup
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # 【坑】__new__ 复用实例时 __init__ 仍会执行：若再有人调
        # GlobalConfig()，这里会把已载入的配置/密钥清空成空字典。单例
        # 只挡住了重复 setup，没挡住重复 __init__。
        # _config：config.yaml 解析结果（setup 后还会塞入 v8/linux/target/
        # backend 等运行时对象，配置字典与对象注册表混用）
        self._config: Dict[str, Any] = {}
        # _keys：llm_keys.yaml 解析结果（openai_key/claude_key/base_url/
        # providers 等），供 model.init_llm 消费
        self._keys: Dict[str, Any] = {}

    def setup(self, config_path: str = "config.yaml"):
        # 【职责】一次性完成初始化：载入配置 → 载入密钥 → 初始化文件日志
        #   → 构建 target（Linux/V8）与 backend（ClangBackend）对象。
        # 【参数】config_path：YAML 主配置路径（缺省当前目录 config.yaml）。
        # 【防重入】已初始化则告警并直接返回（重复 setup 不覆盖旧配置）
        if self._initialized:
            logger.warning("GlobalConfig is already initialized.")
            return

        # 解析主配置 YAML（文件缺失则 exit(-1)，见 _load_config）
        self._load_config(config_path)

        # 密钥文件路径可由配置项 key_file 指定，缺省 llm_keys.yaml
        keys_path = self.get("key_file", "llm_keys.yaml")
        self._load_keys(keys_path)
        # 置位初始化标志：此后再调 setup() 只告警返回
        self._initialized = True
        # 把 config.yaml 的 model 项同步进密钥字典——model.init_llm 从
        # get_key_config() 读 model（两份 YAML 的粘合点，故 keys 字典里
        # 除密钥外还混有模型名）
        self._keys["model"] = self.get("model")

        # 初始化 loguru 文件日志（logs/<result_dir 名>-<时间戳>.log）
        self._init_logger()

        # Init the target and backend
        # FIXME: This should be extended to support other targets and backends
        # 目标类型：linux（论文默认）或 v8（fork 增量）
        target_type = self.get("target_type", "linux")

        # 惰性构建目标对象：配置里给了哪个目录（v8_dir/linux_dir）就实例化
        # 哪个 target（V8/Linux 封装了仓库路径、checkout_commit、
        # olddefconfig 等差分验证与全库扫描所需操作）
        if "v8_dir" in self._config:
            self._config["v8"] = V8(self.get("v8_dir"))
        if "linux_dir" in self._config:
            self._config["linux"] = Linux(self.get("linux_dir"))

        # 按 target_type 选定活跃目标存入 "target" 键；注意 else 兜底——
        # 任何非 "v8" 的取值（含拼错的 linux 名）都落到 linux 分支
        if target_type == "v8":
            self._config["target"] = self._config["v8"]
        else:
            self._config["target"] = self._config["linux"]
        # 分析后端固定 ClangBackend（CSA）：传入 LLVM 构建目录（LLVM_dir），
        # 负责 checker plugin 编译、scan-build 扫描与报告解析
        self._config["backend"] = ClangBackend(self.get("LLVM_dir"))

    def _init_logger(self):
        """Initialize the logger."""
        # 日志统一落 ./logs/ 目录（不存在则创建）
        log_dir = Path("logs")
        if not log_dir.exists():
            log_dir.mkdir()

        # 日志文件名 = result_dir 的末段名 + 本地时间戳，按轮次区分日志
        result_name = Path(self.get("result_dir")).stem
        # 时间戳格式 年-月-日-时-分-秒（time.localtime 取本地时区）
        time_stamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        # 追加文件 sink：按天轮转、保留 7 天、DEBUG 级全量落盘
        # （调试 LLM prompt 全文回放就靠这个级别）
        logger.add(
            f"{log_dir}/{result_name}-{time_stamp}.log",
            rotation="1 day",
            retention="7 days",
            level="DEBUG",
        )

    def _load_config(self, path: str):
        # 载入主配置 YAML；空文件归一化为 {}；文件缺失记错误后 exit(-1)
        # （快速失败：没有配置后续必然全错，不如直接终止进程）
        try:
            with open(path, "r") as f:
                self._config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.error(f"Config file '{path}' not found.")
            exit(-1)

    def _load_keys(self, path: str):
        # 载入 LLM 密钥 YAML（openai_key/claude_key/google_key/deepseek_key/
        # base_url/api_key/providers 自定义表）；同样缺文件即 exit(-1)
        try:
            with open(path, "r") as f:
                self._keys = yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.error(f"Keys file '{path}' not found.")
            exit(-1)

    def get_key_config(self) -> Dict[str, Any]:
        """Get the keys configuration."""
        # 暴露密钥字典给 model.init_llm（里面混有密钥 + model 名）
        return self._keys

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        # 通用配置读取原语：key 不存在返回 default（下方各 property 的底层）
        return self._config.get(key, default)

    @property
    def target(self) -> Optional[TargetFactory]:
        """Get the target."""
        # 当前扫描目标（Linux/V8 实例）：提供仓库路径、checkout_commit、
        # olddefconfig 等（Validation 差分验证与全库扫描都经它操作仓库）
        return self._config.get("target")

    @property
    def backend(self) -> Optional[AnalysisBackendFactory]:
        """Get the backend."""
        # 分析后端（ClangBackend 实例）：CSA 引擎封装
        return self._config.get("backend")

    @property
    def result_dir(self) -> Optional[Path]:
        """Get the result directory."""
        # 本轮产物根目录（checker 元数据/prompt 历史/报告都挂在它下面）
        return Path(self.get("result_dir"))

    @property
    def scan_timeout(self) -> Optional[int]:
        """Get the scan timeout."""
        # 单次扫描（单对象/单文件）超时秒数，缺省 600s=10min：防个别翻译
        # 单元在符号执行中状态爆炸（ExplodedGraph 膨胀）拖死整轮扫描
        return self.get("scan_timeout", 600)

    @property
    def scan_commit(self) -> Optional[str]:
        """Get the scan commit."""
        # 扫描时目标仓库 checkout 的 commit，缺省 "main"（scan 模式用；
        # 注意 Validation 差分验证的 buggy/patched commit 由 gen/refine
        # 内部另行指定，不走这个配置）
        return self.get("scan_commit", "main")

    @property
    def max_fp_reports_for_refinement(self) -> int:
        """Get the maximum number of false positive reports to use for refinement."""
        # 单 checker refine 时喂给 refinement agent 的 FP 报告采样上限，
        # 缺省 5 ↔ 论文 §3.2 "采样 5 条报告、其中 FP ≤ 1" 的采样口径
        return self.get("max_fp_reports_for_refinement", 5)

    @property
    def max_fp_reports_for_batch(self) -> int:
        """Get the maximum number of false positive reports to use for batch refinement."""
        # 批量 refine（refine_unrefined 断点续跑）时每 checker 的 FP 报告
        # 采样上限，缺省 5（与单次 refine 同口径）
        return self.get("max_fp_reports_for_batch", 5)

    @property
    def group_scan_targets(self) -> List[str]:
        """Get the default scan targets for group scanning."""
        # 全库扫描（group scan）默认目录范围：缺省只扫 drivers/——论文
        # 全库扫描主战场（内核 bug 历来密度最高的子系统）
        return self.get("group_scan_targets", ["drivers/"])

    @property
    def group_scan_timeout(self) -> int:
        """Get the timeout for group scanning in seconds."""
        # 组扫描超时秒数，缺省 3600s ↔ 论文 §3.2 "refine 期间限 1 小时"
        # （正式找 bug 的 scan 阶段另说）
        return self.get("group_scan_timeout", 3600)  # 60 minutes for large groups

    @property
    def group_scan_jobs(self) -> int:
        """Get the number of parallel jobs for group scanning."""
        # 组扫描的并行 make 作业数，缺省 32（内核全量构建吞吐参数）
        return self.get("group_scan_jobs", 32)

    @property
    def jobs(self) -> int:
        """Get the number of parallel jobs."""
        # 通用并行作业数（plugin 编译等场景），缺省 32
        return self.get("jobs", 32)


# 模块级单例：全仓统一 from global_config import global_config 拿配置
# （model/agent/checker_scan/checker_refine 皆然；也正因无人二次实例化，
# __init__ 重置配置的隐患从未爆雷）
global_config = GlobalConfig()
