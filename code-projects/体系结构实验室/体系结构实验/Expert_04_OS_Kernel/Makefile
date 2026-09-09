# Expert_04_OS_Kernel/Makefile
CC ?= gcc
CFLAGS = -std=gnu11 -Wall -O2 -I../../common
ARCH_FLAGS := $(shell $(CC) -mcpu=ftc86x -x c /dev/null -S -o /dev/null 2>/dev/null \
                && echo "-mcpu=ftc86x" || echo "-march=armv8.2-a+simd")

TARGETS = syscall_bench tlb_cost

all: $(TARGETS)

%: src/%.c
	$(CC) $(CFLAGS) $(ARCH_FLAGS) $< -o $@

run: all
	@echo "===== syscall_bench ====="
	./syscall_bench
	@echo ""
	@echo "===== tlb_cost ====="
	./tlb_cost

clean:
	rm -f $(TARGETS)

.PHONY: all run clean
