#include <QCoreApplication>
#include <QLocalServer>
#include <QLocalSocket>
#include <QtTest/QtTest>

class Qt5QtbaseTest : public QObject {
    Q_OBJECT
private slots:
    void testLocalSocket() {
        QLocalServer server;
        QVERIFY(server.listen("test_socket"));
        QLocalSocket client;
        client.connectToServer("test_socket");
        QVERIFY(client.waitForConnected(1000));
        server.close();
    }
};

QTEST_MAIN(Qt5QtbaseTest)
#include "test.moc"
