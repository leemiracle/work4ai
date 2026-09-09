# Lab04/src/Makefile
include ../../common/Makefile.inc

TARGETS = rename_capacity rob_size load_store_spec

.PHONY: all clean summary
.DEFAULT_GOAL := all

all: $(TARGETS)

# rename_capacity: 关掉 FMA 融合 + 关自动向量化。
# -ffp-contract=off：让 v*v 与 +1.0 保持两条独立指令，否则编译器生成 fmadd，IPC 基准失真。
# -fno-tree-vectorize：阻止 NEON 把 N 条标量链打包成 SIMD 通道，否则测的是 FPU 通道数。
rename_capacity: rename_capacity.c
	$(CC) $(CFLAGS) -ffp-contract=off -fno-tree-vectorize -o $@ $< $(LDFLAGS) $(LDLIBS)

rob_size: rob_size.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

load_store_spec: load_store_spec.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

summary: $(TARGETS)
	@./reverse_engineer_summary.sh

clean:
	rm -f *.o *.s $(TARGETS)
