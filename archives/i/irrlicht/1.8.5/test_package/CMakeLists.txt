cmake_minimum_required(VERSION 3.16)
project(test_irrlicht CXX)

find_package(Irrlicht REQUIRED CONFIG)

add_executable(test_irrlicht test_irrlicht.cpp)
target_link_libraries(test_irrlicht PRIVATE Irrlicht::Irrlicht)

