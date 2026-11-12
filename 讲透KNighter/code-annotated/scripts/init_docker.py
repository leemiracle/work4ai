# Init the docker container
# It will:
# 1. Git clone the Linux kernel source code
# 2. Prepare the LLVM source code
# ============================================================================
# 【模块定位】KNighter 复现环境的容器首次初始化脚本：克隆 Linux 内核源码、准备
#   LLVM（含 SAGenTestPlugin 编译环境）、落盘占位 key 文件与 5 份三阶段配置
#   YAML，让 src/main.py 的 generate/refine/triage 三个子命令开箱即用。
#
# 【论文映射】§5 实验环境（论文的 Docker 化复现入口）。配置项与论文参数一一对
#   应：checker_nums=10 即 Algorithm 1 的 maxIterations（每 commit 最多 10 次
#   合成尝试，出 perfect checker 提前 break，见 checker_gen.py 的
#   for i in range(len(checker_results), checker_nums)）；refine 的
#   scan_timeout=3600 即 §3.2 的 refine 期全库扫描 1 小时上限；model="o3-mini"
#   为论文默认模型（消融另有 GPT-4o/DeepSeek-R1/Gemini-2-flash，见 src/model.py）。
#
# 【管线角色】上游 = Dockerfile / docker-compose.yml（容器内 /app 工作区）；
#   下游 = src/main.py 读这些 config-*.yaml 分阶段执行。
#
# 【关键依赖与坑】① 内核必须全量 clone（差分验证要 checkout 到任意 buggy/
#   patched 父子提交，不能 --depth 浅克隆）。② scripts/setup_llvm.py 会把
#   llvm_utils/utility.{h,cpp} 注入 LLVM 源码树并注册 SAGenTestPlugin 编译目标
#   （scripts/README.md 有等价手工流程，基于 LLVM-18.1.8）。③ key_config 里是
#   占位 "XXX"，真跑前必须替换。④ debug 变体通过【原地改】dict 再 dump 实现
#   ——正式版 yaml 先写、改字段后写 debug 版，顺序保证正式版仍是原值；但 dict
#   从此被污染，init_docker() 不可重入（重跑会把 debug 值写进正式配置）。
# ============================================================================

import subprocess as sp  # 子进程：git clone 与 setup_llvm.py
from pathlib import Path  # 路径对象（clone 的工作目录）

import yaml  # PyYAML：把配置 dict dump 成 YAML 文件

llvm_path = "/app/llvm"  # 容器内 LLVM 源码树路径（CSA/checker 编译环境）
linux_path = "/app/linux"  # 容器内 Linux 内核仓路径（差分验证的 checkout 对象）
key_file_path = "/app/llm_keys.yaml"  # LLM API key 文件路径（src/model.py 读取）

gen_result_path = "/app/result-generate"  # 阶段一 Checker Synthesis（§3.1）结果目录
refine_result_path = "/app/result-refine"  # 阶段二 Checker Refinement（§3.2）结果目录
triage_result_path = "/app/result-triage"  # triage agent 逐报告判 FP（§3.2）结果目录

model = "o3-mini"  # 论文默认模型（§5：O3-mini；消融含 GPT-4o/DeepSeek-R1/Gemini-2-flash）

# 阶段一配置：result_dir 输出目录 / LLVM_dir 与 linux_dir 两大环境路径 /
# checker_nums=10 即论文 Algorithm 1 的 maxIterations（每 commit 最多 10 次合成
# 尝试）/ key_file 凭据文件 / model 模型名
generate_config_in_docker = {
    "result_dir": gen_result_path,
    "LLVM_dir": llvm_path,
    "linux_dir": linux_path,
    "checker_nums": 10,
    "key_file": key_file_path,
    "model": model,
}

# 阶段二 refine 配置：在生成配置基础上多三个键——jobs=32（全库扫描的 make 并行
# 度）、scan_timeout=3600（§3.2 refine 期单次扫描 1 小时上限；正式找 bug 时不
# 限）、scan_commit="v6.11"（refine 全库扫描所锚定的内核版本）
refine_config_in_docker = {
    "result_dir": refine_result_path,
    "LLVM_dir": llvm_path,
    "linux_dir": linux_path,
    "checker_nums": 10,
    "key_file": key_file_path,
    "model": model,
    "jobs": 32,
    "scan_timeout": 3600,
    "scan_commit": "v6.11",
}

# triage 配置：报告蒸馏后的 FP 判定阶段（triage agent 读 refine 产出的报告，
# 逐条判定是否对齐目标 pattern——§3.2 的 79 报告 7TP/22FP/50TN/0FN 那组数据）
triage_config_in_docker = {
    "result_dir": triage_result_path,
    "LLVM_dir": llvm_path,
    "linux_dir": linux_path,
    "checker_nums": 10,
    "key_file": key_file_path,
    "model": model,
}

key_config_in_docker = {"openai_key": "XXX"}  # 占位 key：真跑前须替换成真实 OpenAI 凭据（写入 llm_keys.yaml 供 src/model.py 读取）


# 容器初始化主流程：六步顺序执行（内核 -> LLVM -> key -> 三份正式配置 + 两份 debug 配置）。
# 任一子进程失败即 raise，让初始化尽早暴露问题。
def init_docker():
    # 1. Git clone the Linux kernel source code
    res = sp.run(  # 全量克隆 torvalds/linux（差分验证需 checkout 任意历史提交，不能浅克隆）
        ["git", "clone", "https://github.com/torvalds/linux.git", linux_path],
        cwd=Path("/app"),
    )
    if res.returncode != 0:  # 非零退出码 = 克隆失败
        raise RuntimeError("Failed to clone Linux kernel source code")

    # 2. Prepare the LLVM source code
    res = sp.run(["python3", "scripts/setup_llvm.py", llvm_path])  # 准备 LLVM 源码树：下载/解包 + 注入 utility.{h,cpp} + 注册 SAGenTestPlugin 编译目标（checker 将编译为 CSA plugin .so）
    if res.returncode != 0:
        raise RuntimeError("Failed to prepare LLVM source code")

    # 3. Copy the key file
    with open(key_file_path, "w") as f:
        yaml.dump(key_config_in_docker, f)  # 落盘 llm_keys.yaml（占位 key，格式：openai_key: XXX）

    # 4. Generate the config file
    with open("/app/config-generate.yaml", "w") as f:
        yaml.dump(generate_config_in_docker, f)  # 阶段一配置（src/main.py generate 子命令的输入）

    # 5. Generate the refine config file
    with open("/app/config-refine.yaml", "w") as f:
        yaml.dump(refine_config_in_docker, f)  # 阶段二 refine 正式配置（先写，此时 dict 还是原值）
    with open("/app/config-refine-debug.yaml", "w") as f:
        refine_config_in_docker["result_dir"] = "/app/result-refine-debug"  # 【原地改】debug 版：结果目录切到独立目录，避免污染正式结果
        refine_config_in_docker["scan_commit"] = "v6.9"  # 【原地改】debug 版：锚定更旧的 v6.9 内核，缩小扫描面快速验证流程
        yaml.dump(refine_config_in_docker, f)  # 后写 debug 版——顺序保证 config-refine.yaml 保留原值；但 dict 已被污染（不可重入）

    # 6. Generate the triage config file
    with open("/app/config-triage.yaml", "w") as f:
        yaml.dump(triage_config_in_docker, f)  # triage 正式配置
    with open("/app/config-triage-debug.yaml", "w") as f:
        triage_config_in_docker["result_dir"] = "/app/result-triage-debug"  # 【原地改】debug 版只换结果目录（triage 不涉及 scan_commit）
        yaml.dump(triage_config_in_docker, f)


if __name__ == "__main__":
    init_docker()  # 直接执行全部初始化（在容器内 /app 工作区运行）
