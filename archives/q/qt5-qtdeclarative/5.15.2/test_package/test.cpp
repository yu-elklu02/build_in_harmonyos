#include <QCoreApplication>
#include <QQmlEngine>
#include <cassert>

int main(int argc, char **argv) {
    QCoreApplication app(argc, argv);
    QQmlEngine engine;
    assert(engine.rootContext() != nullptr);
    return 0;
}
