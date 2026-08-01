cmake_minimum_required(VERSION 3.15)
project(test_libtorrent LANGUAGES CXX)

find_package(libtorrent CONFIG REQUIRED)

add_executable(test_libtorrent test_libtorrent.cpp)
target_link_libraries(test_libtorrent PRIVATE libtorrent::libtorrent)

enable_testing()
add_test(NAME libtorrent_functional COMMAND test_libtorrent)

