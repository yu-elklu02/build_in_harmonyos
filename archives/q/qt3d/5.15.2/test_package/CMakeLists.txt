cmake_minimum_required(VERSION 3.15)
project(test_qt3d CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(qt3d CONFIG REQUIRED)
find_package(qt5-qtbase CONFIG REQUIRED)

add_executable(test_qt3d test.cpp)
target_link_libraries(test_qt3d PRIVATE qt3d::Render qt5-qtbase::qt5-qtbase)
set_target_properties(test_qt3d PROPERTIES
    LINK_FLAGS "-Wl,--disable-new-dtags"
)

add_executable(test_upstream_qaspectjob test_upstream_qaspectjob.cpp)
target_link_libraries(test_upstream_qaspectjob PRIVATE
    qt3d::Core
    qt5-qtbase::qt5-qtbase
)
set_target_properties(test_upstream_qaspectjob PROPERTIES AUTOMOC ON)

enable_testing()
add_test(NAME test_qt3d COMMAND test_qt3d)
add_test(NAME test_upstream_qaspectjob COMMAND test_upstream_qaspectjob)
