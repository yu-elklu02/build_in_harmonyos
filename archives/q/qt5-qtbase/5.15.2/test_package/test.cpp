#include <QCoreApplication>
#include <QLocalServer>
#include <QLocalSocket>
#include <QMatrix4x4>
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

    void testGuiMath() {
        QMatrix4x4 transform;
        transform.translate(1.0f, 2.0f, 3.0f);
        const QVector3D point = transform.map(QVector3D(0.0f, 0.0f, 0.0f));
        QCOMPARE(point, QVector3D(1.0f, 2.0f, 3.0f));
    }
};

QTEST_GUILESS_MAIN(Qt5QtbaseTest)
#include "test.moc"
