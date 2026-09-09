# View_03_Compiler/Makefile (实际: View_03_Perf)
CC ?= gcc
CFLAGS = -std=gnu11 -Wall -O2 -I../../common -pthread
ARCH_FLAGS := $(shell $(CC) -mcpu=ftc86x -x c /dev/null -S -o /dev/null 2>/dev/null \
                && echo "-mcpu=ftc86x" || echo "-march=armv8.2-a+simd")
LDFLAGS = -lm

TARGETS = matmul_evolution false_sharing branch_patterns

all: $(TARGETS)

%: src/%.c
	$(CC) $(CFLAGS) $(ARCH_FLAGS) $< -o $@ $(LDFLAGS)

run: all
	@echo "============================================="
	@echo " 1. matmul_evolution (矩阵乘 8 步优化阶梯)"
	@echo "============================================="
	./matmul_evolution
	@echo ""
	@echo "============================================="
	@echo " 2. false_sharing (多核 false sharing demo)"
	@echo "============================================="
	./false_sharing
	@echo ""
	@echo "============================================="
	@echo " 3. branch_patterns (分支模式对 IPC 的影响)"
	@echo "============================================="
	./branch_patterns

clean:
	rm -f $(TARGETS)

.PHONY: all run clean
