cmake_minimum_required(VERSION 3.15)
project(test_qt5_qtbase CXX)
set(CMAKE_AUTOMOC ON)
find_package(Qt5Core REQUIRED)
find_package(Qt5Gui REQUIRED)
find_package(Qt5Network REQUIRED)
find_package(Qt5Test REQUIRED)
add_executable(test_qt5_qtbase test.cpp)
target_link_libraries(test_qt5_qtbase Qt5::Core Qt5::Gui Qt5::Network Qt5::Test)
target_link_options(test_qt5_qtbase PRIVATE -stdlib=libc++)
if(DEFINED OHOS_CXX_RUNTIME_DIR)
    target_link_libraries(test_qt5_qtbase PRIVATE
        "${OHOS_CXX_RUNTIME_DIR}/libc++.so"
        "${OHOS_CXX_RUNTIME_DIR}/libc++abi.a"
        "${OHOS_CXX_RUNTIME_DIR}/libunwind.a"
    )
endif()
enable_testing()
add_test(NAME test_qt5_qtbase COMMAND test_qt5_qtbase)
