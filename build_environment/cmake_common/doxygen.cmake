#[=======================================================================[
Setup the paths for Doxygen

#]=======================================================================]
set(DOCS_SOURCE_DIR ${CMAKE_SOURCE_DIR}/docs)

#[=======================================================================[
Configuring Doxygen

#]=======================================================================]
message(STATUS " Configuring Doxygen")

set(DOXYGEN_IN ${CMAKE_SOURCE_DIR}/build_environment/tool/doxygen/Doxyfile.in)
set(DOXYGEN_OUT ${CMAKE_BINARY_DIR}/Doxyfile)

find_package(Doxygen REQUIRED)
if (DOXYGEN_FOUND)
    message(STATUS "Doxygen found: version ${DOXYGEN_VERSION}")
else()
    message(FATAL_ERROR "Doxygen not found. Please install it to build the documentation.")
endif()

# Configure the Doxyfile with @ substitutions
configure_file(${DOXYGEN_IN} ${DOXYGEN_OUT} @ONLY)
