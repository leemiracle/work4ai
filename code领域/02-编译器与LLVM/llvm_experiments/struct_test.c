#include <stdio.h>

struct normal_struct {
    char c;
    int i;
    short s;
};

struct packed_struct {
    char c;
    int i;
    short s;
} __attribute__((packed));

int main() {
    printf("normal_struct offsets:\n");
    printf("  c: %zu\n", __builtin_offsetof(struct normal_struct, c));
    printf("  i: %zu\n", __builtin_offsetof(struct normal_struct, i));
    printf("  s: %zu\n", __builtin_offsetof(struct normal_struct, s));
    printf("  size: %zu\n", sizeof(struct normal_struct));
    
    printf("packed_struct offsets:\n");
    printf("  c: %zu\n", __builtin_offsetof(struct packed_struct, c));
    printf("  i: %zu\n", __builtin_offsetof(struct packed_struct, i));
    printf("  s: %zu\n", __builtin_offsetof(struct packed_struct, s));
    printf("  size: %zu\n", sizeof(struct packed_struct));
    
    return 0;
}
