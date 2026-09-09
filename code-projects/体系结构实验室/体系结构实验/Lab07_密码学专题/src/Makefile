# Lab07/src/Makefile
include ../../common/Makefile.inc

TARGETS = crc_test aes_test sha_compare sm_test

.PHONY: all clean
.DEFAULT_GOAL := all

all: $(TARGETS)

crc_test: crc_test.c
	$(CC) $(CFLAGS) -march=armv8-a+simd+crc -o $@ $< $(LDFLAGS) $(LDLIBS)

aes_test: aes_test.c
	$(CC) $(CFLAGS) -march=armv8-a+simd+crypto -o $@ $< $(LDFLAGS) $(LDLIBS)

sha_compare: sha_compare.c
	$(CC) $(CFLAGS) -march=armv8-a+simd+crypto -o $@ $< $(LDFLAGS) $(LDLIBS)

# sm_test 用 armv8.4-a 启用 SM4 指令支持（v8.4 自带 SM3/SM4），
# 软件实现已用 GB/T 32907 标准向量校验；硬件 vsm4e intrinsic 留作扩展
sm_test: sm_test.c
	$(CC) $(CFLAGS) -march=armv8.4-a+simd+crypto+sm4 -o $@ $< $(LDFLAGS) $(LDLIBS)

clean:
	rm -f *.o *.s $(TARGETS)
