#include <Qt3DCore/QEntity>
#include <Qt3DCore/QTransform>
#include <Qt3DCore/QNode>
#include <QCoreApplication>
#include <cassert>

int main(int argc, char **argv) {
    QCoreApplication app(argc, argv);
    Qt3DCore::QEntity root;
    Qt3DCore::QEntity child(&root);
    Qt3DCore::QTransform transform;
    transform.setScale(2.0f);
    child.addComponent(&transform);

    assert(child.parentNode() == &root);
    assert(child.components().size() == 1);
    assert(transform.scale() == 2.0f);
    return 0;
}
