# ============================================================================
# Makefile — Kernel-Lab 现代构建系统（v0.8+，替代/补充 build.sh）
#
# 用法：
#   make            # 编译全部目标
#   make test       # 跑正确性回归（CI ready）
#   make bench      # 跑全套 benchmark，生成 results/bench-<date>.md
#   make clean      # 清理 bin/
#   make list       # 列出所有目标
#   make gemm_f32   # 单目标编译
# ============================================================================

# === 工具链（PhyGCC 优先，回退系统 gcc）===
PHYGCC   ?= /opt/apps/phygcc-12.3.2/bin/gcc
GCC      ?= gcc
CC       := $(shell if [ -x "$(PHYGCC)" ]; then echo "$(PHYGCC)"; else echo "$(GCC)"; fi)

# === 编译 flags ===
ARCH_FLAGS := -march=armv8.2-a+fp16+dotprod
OPT_FLAGS  := -O3 -fno-omit-frame-pointer -g -fno-inline-functions
CFLAGS     := $(ARCH_FLAGS) $(OPT_FLAGS)
LIBS       := -lm

# === 路径 ===
SRC_DIR := src
BIN_DIR := bin
SCR_DIR := scripts

# === 目标定义（name: extra-flags）===
# OpenMP 标记的目标会自动加 -fopenmp
TARGETS := \
    gemm_f32 \
    gemm_s8 \
    gemm_f16 \
    gemm_tune \
    gemm_autotune \
    gemm_mr8_verify \
    conv_benchmark \
    conv_winograd \
    conv_winograd_f44 \
    conv_winograd_int8 \
    conv_sizes \
    conv_dispatcher \
    multicore \
    multicore_tiled \
    multicore_winograd \
    multicore_winograd_f44 \
    attention \
    attention_neon \
    asm_kernel \
    bench_gemm

# 需要 OpenMP 的目标
OMP_TARGETS := conv_dispatcher multicore multicore_tiled multicore_winograd multicore_winograd_f44 attention_neon

# === Lens 视角分析目标 ===
LENS_TARGETS := \
    lens-roofline \
    lens-pmu \
    lens-thermal \
    lens-precision \
    lens-latency

# 从目标名推源文件
src_of = $(SRC_DIR)/$1.c

# 推导每个目标的 flags
define GET_FLAGS
$(if $(filter $1,$(OMP_TARGETS)),-fopenmp,)
endef

# === 默认目标 ===
.PHONY: all clean test bench list help lens analyze
all: $(addprefix $(BIN_DIR)/,$(TARGETS))

# === Lens 目标：技术维度视角分析 ===
lens: $(addprefix $(BIN_DIR)/,$(LENS_TARGETS))
	@echo "✅ 5 个 lens 编译完，跑 make analyze 一键分析"

# === analyze：跑全部 lens 生成报告 ===
analyze: lens
	@$(SCR_DIR)/analyze-all.sh

# === 编译规则（模式规则）===
# src/ 下的源码
$(BIN_DIR)/%: $(SRC_DIR)/%.c | $(BIN_DIR)
	@echo "[CC] $@"
	@$(CC) $(CFLAGS) $(call GET_FLAGS,$*) $< -o $@ $(LIBS)

# analysis/ 下的 lens 源码（特殊规则）
$(BIN_DIR)/lens-%: analysis/lens-%.c | $(BIN_DIR)
	@echo "[CC-LENS] $@"
	@$(CC) $(CFLAGS) $< -o $@ $(LIBS)

$(BIN_DIR):
	@mkdir -p $@

# === list：列出所有目标 ===
list:
	@echo "可用目标（$(words $(TARGETS)) 个）："
	@$(foreach t,$(TARGETS),echo "  $(t)$(if $(filter $(t),$(OMP_TARGETS)), [+OpenMP])";)

# === test：正确性回归（CI ready，任一 FAIL 退出码非 0）===
test: all
	@echo "=== 正确性回归测试 ==="
	@$(SCR_DIR)/test.sh

# === bench：全套 benchmark，自动生成报告 ===
bench: all
	@echo "=== 全套 Benchmark ==="
	@$(SCR_DIR)/bench-all.sh

# === clean ===
clean:
	@rm -rf $(BIN_DIR)
	@echo "✅ 已清理 $(BIN_DIR)/"

# === help ===
help:
	@echo "Kernel-Lab Makefile (v0.9+ multi-lens)"
	@echo ""
	@echo "  make                编译全部 $(words $(TARGETS)) 个算子目标"
	@echo "  make lens           编译 $(words $(LENS_TARGETS)) 个 lens 视角分析"
	@echo "  make analyze        跑全套 lens，生成 results/lenses/ 报告"
	@echo "  make test           正确性回归（CI ready）"
	@echo "  make bench          全套算子 bench + 自动 markdown 报告"
	@echo "  make clean          清理 bin/"
	@echo "  make list           列出所有目标"
	@echo "  make <target>       编译单个目标"
	@echo ""
	@echo "多视角审查报告: docs/lenses/"
	@echo "CC = $(CC)"
