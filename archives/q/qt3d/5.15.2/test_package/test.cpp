#include <QCoreApplication>
#include <Qt3DCore/QEntity>
#include <Qt3DCore/QTransform>

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

    std::puts("Qt3D Core consumer test passed");
    return 0;
}
