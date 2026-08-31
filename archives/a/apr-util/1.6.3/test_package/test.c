#include <assert.h>

#include <apr_general.h>
#include <apr_pools.h>
#include <apr_xml.h>

int main(void) {
    apr_pool_t *pool = NULL;
    apr_xml_parser *parser = NULL;
    assert(apr_initialize() == APR_SUCCESS);
    assert(apr_pool_create(&pool, NULL) == APR_SUCCESS);
    parser = apr_xml_parser_create(pool);
    assert(parser != NULL);
    apr_pool_destroy(pool);
    apr_terminate();
    return 0;
}
