#include <aalib.h>

int main(void) {
    aa_context *context = aa_init(&aa_defparams, &aa_defrenderparams);
    if (context == 0) {
        return 1;
    }
    aa_close(context);
    return 0;
}

