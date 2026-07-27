cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(berkeley-db CONFIG REQUIRED)
add_executable(test_package test.c)
target_link_libraries(test_package PRIVATE berkeley-db::berkeley-db)
