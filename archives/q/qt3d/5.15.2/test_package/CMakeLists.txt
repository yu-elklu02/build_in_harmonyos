cmake_minimum_required(VERSION 3.15)
project(test_qt3d CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(qt3d CONFIG REQUIRED)
find_package(Qt5Core CONFIG REQUIRED)

add_executable(test_qt3d test.cpp)
target_link_libraries(test_qt3d PRIVATE qt3d::Core Qt5::Core)
set_target_properties(test_qt3d PROPERTIES
    LINK_FLAGS "-Wl,--disable-new-dtags"
)

enable_testing()
add_test(NAME test_qt3d COMMAND test_qt3d)
