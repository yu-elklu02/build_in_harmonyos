#include <QuaZip.h>
#include <QDebug>

int main() {
    QuaZip zip("test.zip");
    qDebug() << "QuaZIP test passed!";
    return 0;
}
