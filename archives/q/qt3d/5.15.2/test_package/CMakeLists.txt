cmake_minimum_required(VERSION 3.15)
project(test_qt3d CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(qt3d CONFIG REQUIRED)

if(DEFINED ENV{QTDIR} AND EXISTS "$ENV{QTDIR}/include/QtCore")
    set(QT5_ROOT "$ENV{QTDIR}")
elseif(EXISTS "/storage/Users/currentUser/usr/local/include/QtCore")
    set(QT5_ROOT "/storage/Users/currentUser/usr/local")
else()
    set(QT5_ROOT "/storage/Users/currentUser/usr/local/Qt5")
endif()

add_executable(test_qt3d test.cpp)
target_include_directories(test_qt3d PRIVATE
    "${QT5_ROOT}/include"
    "${QT5_ROOT}/include/QtCore"
)
target_link_directories(test_qt3d PRIVATE "${QT5_ROOT}/lib")
target_link_libraries(test_qt3d PRIVATE qt3d::Core Qt5Core)
set_target_properties(test_qt3d PROPERTIES
    BUILD_RPATH "${QT5_ROOT}/lib"
    LINK_FLAGS "-Wl,--disable-new-dtags"
)

enable_testing()
add_test(NAME test_qt3d COMMAND test_qt3d)
