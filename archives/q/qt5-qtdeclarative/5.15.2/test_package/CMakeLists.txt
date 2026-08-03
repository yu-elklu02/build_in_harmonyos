cmake_minimum_required(VERSION 3.15)
project(test_qt5_qtdeclarative LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt5QtDeclarative CONFIG REQUIRED)
add_executable(test_qt5_qtdeclarative test.cpp)
target_link_libraries(test_qt5_qtdeclarative PRIVATE Qt5QtDeclarative::Qt5Qml)
