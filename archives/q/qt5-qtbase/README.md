# qt5-qtbase

Qt5 Base module for OpenHarmony. Includes Core, Network, Test, Concurrent libraries.

## Key adaptations for OHOS
- Abstract socket namespace patch (QLocalServer/QLocalSocket)
- Qt5Test module enabled
- No stripping (QMAKE_STRIP="")
- libz.so built from source
