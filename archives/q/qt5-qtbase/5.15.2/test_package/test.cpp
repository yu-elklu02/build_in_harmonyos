#include <QCoreApplication>
#include <QLocalServer>
#include <QLocalSocket>
#include <QLibrary>
#include <QMatrix4x4>
#include <QtTest/QtTest>

int main(int argc, char *argv[]) {
    QCoreApplication application(argc, argv);
    QLocalServer::removeServer("test_socket");
    QLocalServer server;
    if (!server.listen("test_socket"))
        return 1;

    QLocalSocket client;
    client.connectToServer("test_socket");
    if (!client.waitForConnected(1000))
        return 2;

    QMatrix4x4 transform;
    transform.translate(1.0f, 2.0f, 3.0f);
    if (transform.map(QVector3D(0.0f, 0.0f, 0.0f)) != QVector3D(1.0f, 2.0f, 3.0f))
        return 3;

    // Verify QtGui and its EGL/GLES runtime dependencies can be loaded.
    QLibrary gui("Qt5Gui");
    if (!gui.load())
        return 4;
    gui.unload();

    QTest::qWait(1);
    return 0;
}
