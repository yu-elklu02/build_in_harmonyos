#include <QCoreApplication>
#include <Qt3DCore/qentity.h>
#include <Qt3DCore/qtransform.h>
#include <Qt3DRender/qrendersettings.h>

#include <cstdio>

int main(int argc, char *argv[]) {
    QCoreApplication app(argc, argv);

    Qt3DCore::QEntity root;
    Qt3DCore::QEntity child(&root);
    if (child.parentEntity() != &root) {
        std::fprintf(stderr, "Qt3D entity parent relationship failed\n");
        return 1;
    }

    Qt3DCore::QTransform transform;
    child.addComponent(&transform);
    if (!child.components().contains(&transform)) {
        std::fprintf(stderr, "Qt3D component attachment failed\n");
        return 2;
    }

    Qt3DRender::QRenderSettings render_settings(&root);
    render_settings.setRenderPolicy(Qt3DRender::QRenderSettings::Always);
    if (render_settings.renderPolicy() != Qt3DRender::QRenderSettings::Always) {
        std::fprintf(stderr, "Qt3D Render settings policy failed\n");
        return 3;
    }

    std::puts("Qt3D Core and Render consumer test passed");
    return 0;
}
