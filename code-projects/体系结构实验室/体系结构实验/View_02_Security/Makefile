# View_02_Compiler/Makefile  (renamed: View_02_Security/Makefile)
CC ?= gcc
CFLAGS = -std=gnu11 -Wall -O2 -I../../common
ARCH_FLAGS := $(shell $(CC) -mcpu=ftc86x -x c /dev/null -S -o /dev/null 2>/dev/null \
                && echo "-mcpu=ftc86x" || echo "-march=armv8.2-a+simd")

TARGETS = cache_timing constant_time

all: $(TARGETS)

%: src/%.c
	$(CC) $(CFLAGS) $(ARCH_FLAGS) $< -o $@

run: all
	@echo "========================================="
	@echo " 1. cache_timing (Flush+Reload POC)"
	@echo "========================================="
	./cache_timing
	@echo ""
	@echo "========================================="
	@echo " 2. constant_time (常时间 vs 短路比较)"
	@echo "========================================="
	./constant_time

clean:
	rm -f $(TARGETS)

.PHONY: all run clean
