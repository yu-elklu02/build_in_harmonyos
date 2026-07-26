#include <QGuiApplication>
#include <QHostAddress>
#include <QLibrary>
#include <QMatrix4x4>
#include <QOffscreenSurface>
#include <QOpenGLContext>
#include <QSurfaceFormat>
#include <QtTest/QtTest>

int main(int argc, char *argv[]) {
    QGuiApplication application(argc, argv);

    // Use a QtNetwork API that does not require an AF_UNIX socket bind, which
    // is restricted by the OHOS sandbox.
    const QHostAddress loopback(QStringLiteral("127.0.0.1"));
    if (!loopback.isLoopback())
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

    QOffscreenSurface surface;
    surface.setFormat(QSurfaceFormat::defaultFormat());
    surface.create();
    if (!surface.isValid())
        return 5;

    QOpenGLContext context;
    context.setFormat(surface.format());
    if (!context.create())
        return 6;
    if (!context.makeCurrent(&surface))
        return 7;
    context.doneCurrent();

    QTest::qWait(1);
    return 0;
}
