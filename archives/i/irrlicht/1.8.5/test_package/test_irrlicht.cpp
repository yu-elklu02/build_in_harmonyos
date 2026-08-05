#include <cassert>
#include <cstring>
#include <irrlicht.h>

int main() {
    using namespace irr;

    static_assert(sizeof(u32) == 4, "Irrlicht u32 type must be 32-bit");
    assert(std::strlen(IRRLICHT_SDK_VERSION) > 0);

    IrrlichtDevice* device = createDevice(
        video::EDT_NULL,
        core::dimension2d<u32>(16, 16),
        16,
        false,
        false,
        false,
        nullptr);

    assert(device != nullptr);
    assert(device->getVideoDriver() != nullptr);
    assert(device->getVideoDriver()->getDriverType() == video::EDT_NULL);

    device->drop();
    return 0;
}
