#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "db.h"

int main(void)
{
    DB *db = NULL;
    DBT key = {0};
    DBT value = {0};
    DBT result = {0};
    const char key_data[] = "key";
    const char value_data[] = "value";
    int rc = db_create(&db, NULL, 0);

    if (rc != 0)
        return 1;
    rc = db->open(db, NULL, "test.db", NULL, DB_BTREE, DB_CREATE | DB_TRUNCATE, 0600);
    if (rc == 0) {
        key.data = (void *)key_data;
        key.size = sizeof(key_data);
        value.data = (void *)value_data;
        value.size = sizeof(value_data);
        rc = db->put(db, NULL, &key, &value, 0);
    }
    if (rc == 0) {
        result.flags = DB_DBT_MALLOC;
        rc = db->get(db, NULL, &key, &result, 0);
        if (rc == 0 && (result.size != sizeof(value_data) || memcmp(result.data, value_data, result.size) != 0))
            rc = DB_NOTFOUND;
        if (result.data != NULL)
            free(result.data);
    }
    if (db->close(db, 0) != 0)
        rc = 1;
    if (rc != 0)
        return 1;
    puts("Berkeley DB put/get test passed");
    return 0;
}
