cmake_minimum_required(VERSION 3.15)
project(test_xcalc NONE)

enable_testing()
add_test(NAME xcalc_package_test
    COMMAND "${CMAKE_COMMAND}" -E true)
