#include <stdio.h>

#include <apr_general.h>
#include <apr_pools.h>
#include <apr_xml.h>

int main(void) {
    /* Use explicit error handling rather than assert(): NDEBUG (Release)
     * strips asserts, which would silently skip apr_initialize() and make
     * the pool allocation crash. */
    if (apr_initialize() != APR_SUCCESS) {
        fprintf(stderr, "apr_initialize failed\n");
        return 1;
    }

    apr_pool_t *pool = NULL;
    if (apr_pool_create(&pool, NULL) != APR_SUCCESS || pool == NULL) {
        fprintf(stderr, "apr_pool_create failed\n");
        return 1;
    }

    apr_xml_parser *parser = apr_xml_parser_create(pool);
    if (parser == NULL) {
        fprintf(stderr, "apr_xml_parser_create failed\n");
        return 1;
    }

    apr_pool_destroy(pool);
    apr_terminate();

    printf("test_apr passed\n");
    printf("APR initialization / memory pool lifecycle OK\n");
    return 0;
}
