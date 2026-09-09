# Lab01/src/Makefile — 更新版，加入 ARMv8.x 扩展实验
include ../../common/Makefile.inc

# 编译 fp16/dot_product/fcmla 必须显式启用对应修饰符
CFLAGS_FP16_ONLY = -march=armv8.2-a+simd+crypto+fp16 -fopenmp
# dot_product 需 +dotprod 才能编译 UDOT intrinsic（vdotq），真测 v8.4 点积加速
# ⚠ 旧版漏 +dotprod，__ARM_FEATURE_DOTPROD 未定义，UDOT 路径被 #ifdef 排除，从未测到
CFLAGS_DOTPROD   = -march=armv8.4-a+simd+crypto+fp16+dotprod -fopenmp
LDLIBS += -lm -lpthread

TARGETS = c_to_asm isa_features fp16_perf dot_product fcmla_complex calling_conv basic_math

.PHONY: all clean disasm_sum_array
.DEFAULT_GOAL := all

all: $(TARGETS)

# c_to_asm 用 default flags
c_to_asm: c_to_asm.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

# 这 4 个用 v8.2-a+fp16，避免 intrinsic 严格检查
isa_features: isa_features.c
	$(CC) $(CFLAGS_BASE) $(CFLAGS_FP16_ONLY) $(CFLAGS_OPT) -o $@ $< $(LDFLAGS) $(LDLIBS)

fp16_perf: fp16_perf.c
	$(CC) $(CFLAGS_BASE) $(CFLAGS_FP16_ONLY) $(CFLAGS_OPT) -o $@ $< $(LDFLAGS) $(LDLIBS)

# dot_product 用 +dotprod 启用 UDOT intrinsic（真测 v8.4 点积）
dot_product: dot_product.c
	$(CC) $(CFLAGS_BASE) $(CFLAGS_DOTPROD) $(CFLAGS_OPT) -o $@ $< $(LDFLAGS) $(LDLIBS)

fcmla_complex: fcmla_complex.c
	$(CC) $(CFLAGS_BASE) $(CFLAGS_FP16_ONLY) $(CFLAGS_OPT) -o $@ $< $(LDFLAGS) $(LDLIBS)

calling_conv: calling_conv.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

basic_math: basic_math.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

clean:
	rm -f *.o *.s $(TARGETS)

disasm_sum_array:
	@./disasm_diff.sh sum_array
