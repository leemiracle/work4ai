# Lab06/src/Makefile
include ../../common/Makefile.inc

TARGETS = mem_order_cost store_store_reorder message_passing

.PHONY: all clean
.DEFAULT_GOAL := all

all: $(TARGETS)

mem_order_cost: mem_order_cost.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

store_store_reorder: store_store_reorder.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

message_passing: message_passing.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

clean:
	rm -f *.o *.s $(TARGETS)
