#include <botan/hash.h>

#include <iostream>
#include <string>

int main()
{
    auto hash = Botan::HashFunction::create("SHA-256");
    if (!hash)
        return 1;
    const std::string payload = "OpenHarmony Botan";
    hash->update(payload);
    const std::string digest = hash->final_hex();
    const std::string expected =
        "c7c738acb29ccbdbb549e51733d6969b7da58b6783a9354b39ba5f2d7fd23d6c";
    if (digest != expected)
    {
        std::cerr << digest << std::endl;
        return 2;
    }
    return 0;
}
