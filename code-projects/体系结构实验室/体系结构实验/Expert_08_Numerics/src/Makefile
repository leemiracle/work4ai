# Expert_08_Numerics — 浮点精度演示 Makefile
# 用法：
#   make          # 编译全部 -O 变体
#   make run      # 跑 -O2 版本
#   make compare  # 跑全部变体并对比 Kahan 是否被 -ffast-math 破坏
#   make clean
#
# 飞腾 D3000M 编译（启用 FP16/NEON）：
#   make EXTRA="-march=armv8.4-a+simd+crypto"

CC      ?= gcc
CFLAGS  ?= -O2
EXTRA   ?=
LIBS    := -lm
SRC     := fp_precision_demo.c

VARIANTS := O0 O2 O3 fast
VFLAG_O0  := -O0
VFLAG_O2  := -O2
VFLAG_O3  := -O3
VFLAG_fast:= -O3 -ffast-math

BINS := $(addprefix demo_,$(VARIANTS))

.PHONY: all run compare clean
all: $(BINS)

demo_%: $(SRC)
	$(CC) $(VFLAG_$*) $(EXTRA) $(SRC) -o $@ $(LIBS)

run: demo_O2
	./demo_O2

compare: $(BINS)
	@echo "############## -O2（Kahan 正常工作）##############"
	@./demo_O2 | sed -n '/实验 A/,/实验 B/p'
	@echo ""
	@echo "############## -O3 -ffast-math（Kahan 被破坏！）##############"
	@./demo_fast | sed -n '/实验 A/,/实验 B/p'
	@echo ""
	@echo "→ 对比 Kahan 行：-O2 时误差 8e-9；-ffast-math 时退化到 2e-3（与朴素相同）"

clean:
	rm -f $(BINS) demo_O1 demo_Ofast
