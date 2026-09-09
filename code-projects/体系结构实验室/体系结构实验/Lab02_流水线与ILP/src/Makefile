# Lab02/src/Makefile
include ../../common/Makefile.inc

TARGETS = data_hazards branch_predict lse_vs_llsc loop_unroll ooo_magic

.PHONY: all clean
.DEFAULT_GOAL := all

all: $(TARGETS)

data_hazards: data_hazards.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

branch_predict: branch_predict.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

lse_vs_llsc: lse_vs_llsc.c
	$(CC) $(CFLAGS) -march=armv8-a+simd+lse -o $@ $< $(LDFLAGS) $(LDLIBS)

loop_unroll: loop_unroll.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

ooo_magic: ooo_magic.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

clean:
	rm -f *.o *.s $(TARGETS)
