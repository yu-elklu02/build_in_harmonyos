cmake_minimum_required(VERSION 3.15)
project(test_ncurses C)

find_package(ncurses REQUIRED)

add_executable(test_ncurses test.c)
target_link_libraries(test_ncurses ncurses::ncurses)

enable_testing()
add_test(NAME test_ncurses COMMAND test_ncurses)
