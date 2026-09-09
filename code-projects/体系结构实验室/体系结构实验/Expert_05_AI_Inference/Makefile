# Expert_05_AI_Inference/Makefile
CC ?= gcc
CFLAGS = -std=gnu11 -Wall -O3 -I../../common
ARCH_FLAGS := $(shell $(CC) -mcpu=ftc86x -x c /dev/null -S -o /dev/null 2>/dev/null \
                && echo "-mcpu=ftc86x" || echo "-march=armv8.4-a+simd+dotprod")

TARGETS = int8_gemm_udot

all: $(TARGETS)

%: src/%.c
	$(CC) $(CFLAGS) $(ARCH_FLAGS) $< -o $@

run: all
	@echo "===== int8_gemm_udot ====="
	./int8_gemm_udot

clean:
	rm -f $(TARGETS)

.PHONY: all run clean
