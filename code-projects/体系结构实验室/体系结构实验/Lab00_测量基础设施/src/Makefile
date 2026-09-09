# Lab00/src/Makefile — 测量基础设施实验
include ../../common/Makefile.inc

CFLAGS += -fopenmp
LDLIBS += -fopenmp

TARGETS = arch_probe null_loop amdahl_law iron_law

.PHONY: all clean
.DEFAULT_GOAL := all

all: $(TARGETS)

clean:
	rm -f *.o *.s $(TARGETS)

arch_probe: arch_probe.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

null_loop: null_loop.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

amdahl_law: amdahl_law.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

iron_law: iron_law.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

# 用 PhyGCC 对比编译（如已安装）
phygcc: PHY_CPU = ftc86x
phygcc: CC = kpgcc
phygcc:
	$(MAKE) clean
	$(MAKE) all

# 汇编对比
disasm: null_loop
	objdump -d null_loop | sed -n '/<loop_empty>:/,/ret/p'
	@echo "---"
	objdump -d null_loop | sed -n '/<loop_volatile>:/,/ret/p'
	@echo "---"
	objdump -d null_loop | sed -n '/<loop_nop>:/,/ret/p'

.PHONY: all clean phygcc disasm
