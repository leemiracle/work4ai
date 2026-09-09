# View_01_Compiler/Makefile
# 跑同一份代码 × 6 个 -O 等级，输出反汇编 + 性能对比

CC      ?= gcc
CFLAGS_BASE = -std=gnu11 -Wall -I../../common
ARCH_FLAGS  := $(shell $(CC) -mcpu=ftc86x -x c /dev/null -S -o /dev/null 2>/dev/null \
                  && echo "-mcpu=ftc86x" || echo "-march=armv8.2-a+simd+lse")
OPT_LEVELS := 0 1 2 3 s fast
SRC := src/opt_compare.c

.PHONY: all compare disasm vectorize clean

all: compare

# 编译所有 -O 版本 + 反汇编
compare: $(SRC)
	@mkdir -p build
	@for O in $(OPT_LEVELS); do \
	    flag="$$O"; \
	    [ "$$O" = "s" ] && flag="s"; \
	    [ "$$O" = "fast" ] && flag="fast"; \
	    echo "[build] -O$$flag"; \
	    $(CC) $(CFLAGS_BASE) $(ARCH_FLAGS) -O$$flag $(SRC) -o build/opt_O$$O -lm; \
	done
	@echo ""
	@echo "=== 性能对比（1000 次 dot_product, ms; 越小越快）==="
	@printf "%-12s %12s %12s\n" "Opt-level" "time(ms)" "binary(B)"
	@for O in $(OPT_LEVELS); do \
	    t=$$(./build/opt_O$$O | grep "1000 次 dot_product" | awk '{print $$(NF-1)}'); \
	    sz=$$(stat -c %s build/opt_O$$O); \
	    printf "%-12s %12s %12s\n" "-O$$O" "$$t" "$$sz"; \
	done
	@echo ""
	@echo "=== 反汇编已生成在 build/opt_O{0,1,2,3,s,fast}.s ==="

# 详细反汇编
disasm: compare
	@for O in $(OPT_LEVELS); do \
	    objdump -d build/opt_O$$O > build/opt_O$$O.s; \
	done
	@echo "反汇编完成: ls build/*.s"
	@echo ""
	@echo "=== dot_product 函数大小（行数；越少越优化）==="
	@printf "%-12s %12s\n" "Opt-level" "lines"
	@for O in $(OPT_LEVELS); do \
	    lines=$$(sed -n '/<dot_product>:/,/^$$/p' build/opt_O$$O.s | wc -l); \
	    printf "%-12s %12s\n" "-O$$O" "$$lines"; \
	done

# 向量化报告
vectorize: $(SRC)
	@mkdir -p build
	@echo "=== -O2 向量化报告（默认不开）==="
	@$(CC) $(CFLAGS_BASE) $(ARCH_FLAGS) -O2 -fopt-info-vec $(SRC) -o /dev/null 2>&1 | head -20 || true
	@echo ""
	@echo "=== -O3 -ftree-vectorize 向量化报告 ==="
	@$(CC) $(CFLAGS_BASE) $(ARCH_FLAGS) -O3 -ftree-vectorize -fopt-info-vec-optimized $(SRC) -o build/vec_test 2>&1 | head -20
	@echo ""
	@echo "=== -O3 -ftree-vectorize 未向量化原因 ==="
	@$(CC) $(CFLAGS_BASE) $(ARCH_FLAGS) -O3 -ftree-vectorize -fopt-info-vec-missed $(SRC) -o build/vec_test 2>&1 | head -10
	@echo ""
	@echo "=== 关键观察 ==="
	@echo "- -O2 默认开启 SIMD 但不开启激进向量化"
	@echo "- -O3 默认 -ftree-vectorize -funroll-loops"
	@echo "- -fopt-info-vec-* 系列能看到为何向量化失败（依赖/别名/分支）"

clean:
	rm -rf build
