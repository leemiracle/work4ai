# common/Makefile.inc — 各 Lab 复用的编译规则
#
# 用法：在各 Lab 的 Makefile 里 include ../../common/Makefile.inc
# 然后定义 TARGETS = ... 即可
#
# 变量：
#   PHY_CPU     : 飞腾微架构 tune (-mcpu=ftc66x / ftc86x / native)
#   CC          : 默认 gcc，飞腾建议用 kpgcc
#   CFLAGS_BASE : 通用 flags
#   CFLAGS_OPT  : 优化 flags（默认 -O2，可被 -O3/-Ofast 覆盖）
#   ARCH        : 架构探测（编译时若不指定，运行时自动检测）

CC          ?= gcc
PHY_CPU     ?= native
ARCH        ?= arm64

CFLAGS_BASE  = -std=gnu11 -Wall -Wextra -g -fno-omit-frame-pointer
# 通过 Makefile.inc 自身路径推导 common 目录（无论 Lab/src 还是 Lab/ 都能工作）
COMMON_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
CFLAGS_BASE += -I$(COMMON_DIR)
# 飞腾专用：
#   -mcpu=ftc66x 对应 D3000 (FTC663)，ftc86x 对应 D3000M (FTC862)
#   若没有 PhyGCC，用 -march=armv8.4-a 兜底（项目锚点是 ARMv8.4-A）。
#   ⚠ 旧版兜底 -march=armv8.2-a+simd+lse 漏 crypto/fp16/dotprod，
#      导致 Lab01/Lab07 的 ARMv8.x intrinsic 编译失败。现已修正为 v8.4 全特性。
ifneq ($(PHY_CPU),)
  ifeq ($(shell $(CC) -mcpu=$(PHY_CPU) -x c /dev/null -S -o /dev/null 2>/dev/null; echo $$?),0)
    CFLAGS_BASE += -mcpu=$(PHY_CPU)
  else
    $(warning [common] CC=$(CC) 不支持 -mcpu=$(PHY_CPU)，使用 -march=armv8.4-a+simd+crypto+fp16+dotprod+lse)
    CFLAGS_BASE += -march=armv8.4-a+simd+crypto+fp16+dotprod+lse
  endif
endif

# 默认 -O2；可被命令行覆盖：make CFLAGS_OPT=-O3
CFLAGS_OPT  ?= -O2
CFLAGS      := $(CFLAGS_BASE) $(CFLAGS_OPT)
LDFLAGS     ?=
LDLIBS      ?= -lm -lpthread

# PHYGCC 多版本对比工具（如已安装）
KPGCC       ?= kpgcc

# 注意：默认目标 all 和 clean 规则由各 Lab 的 Makefile 自行定义。
# 这里只提供编译参数，避免子 Makefile 的 .DEFAULT_GOAL 被覆盖。
