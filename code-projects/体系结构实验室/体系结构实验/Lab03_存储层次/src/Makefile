# Lab03/src/Makefile
include ../../common/Makefile.inc

TARGETS = cache_sizes cache_line associativity false_sharing tlb_hugepage

.PHONY: all clean
.DEFAULT_GOAL := all

all: $(TARGETS)

cache_sizes: cache_sizes.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

cache_line: cache_line.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

associativity: associativity.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

false_sharing: false_sharing.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

tlb_hugepage: tlb_hugepage.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

clean:
	rm -f *.o *.s $(TARGETS)
