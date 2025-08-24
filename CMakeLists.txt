cmake_minimum_required(VERSION 3.10)

project(MyCV)

# Include custom cmake modules for configuration
include(${CMAKE_CURRENT_SOURCE_DIR}/build_environment/cmake_common/venv.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/build_environment/cmake_common/doxygen.cmake)

add_subdirectory(docs
)
