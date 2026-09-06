#include <assert.h>
int main() {
    int a[3];
    for (int i = 0; i < 3; i++) a[i] = i;
    assert(a[0] + a[1] + a[2] == 7);  /* 故意写错: 实际=3, cbmc 会给反例 */
    return 0;
}
