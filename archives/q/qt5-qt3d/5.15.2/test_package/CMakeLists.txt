cmake_minimum_required(VERSION 3.15)
project(test_qt5_qt3d LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt5Qt3D CONFIG REQUIRED)

add_executable(test_qt5_qt3d test.cpp)
target_link_libraries(test_qt5_qt3d PRIVATE Qt5Qt3D::Qt53DCore)

