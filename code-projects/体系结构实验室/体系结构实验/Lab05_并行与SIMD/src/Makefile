# Lab05/src/Makefile
include ../../common/Makefile.inc

TARGETS = gemm_full_stack neon_intrinsics auto_vectorize

.PHONY: all clean
.DEFAULT_GOAL := all

all: $(TARGETS)

gemm_full_stack: gemm_full_stack.c
	$(CC) $(CFLAGS) -fopenmp -o $@ $< $(LDFLAGS) $(LDLIBS)

neon_intrinsics: neon_intrinsics.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

auto_vectorize: auto_vectorize.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

clean:
	rm -f *.o *.s $(TARGETS)
