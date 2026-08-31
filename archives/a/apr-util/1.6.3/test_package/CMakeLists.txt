cmake_minimum_required(VERSION 3.15)
project(test_apr_util C)

find_package(apr-util REQUIRED CONFIG)

add_executable(apr_util_xml_test test.c)
target_link_libraries(apr_util_xml_test PRIVATE apr-util::apr-util)

enable_testing()
add_test(NAME apr_util_xml_test COMMAND apr_util_xml_test)
