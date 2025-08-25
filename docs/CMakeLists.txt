add_custom_target(doc
    COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYGEN_OUT}
    COMMAND ${CMAKE_MAKE_PROGRAM} -C ${CMAKE_BINARY_DIR}/docs/latex -j
    COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_BINARY_DIR}/docs/latex/refman.pdf ${CMAKE_SOURCE_DIR}/LePhucDuc_CV.pdf
    BYPRODUCTS ${CMAKE_BINARY_DIR}/docs/latex/refman.pdf ${CMAKE_SOURCE_DIR}/LePhucDuc_CV.pdf
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    USES_TERMINAL
    COMMENT "Generating PDF CV (Doxygen → LaTeX → PDF) and copying to project root"
    VERBATIM
)

add_custom_target(clean-doc
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_BINARY_DIR}/docs
    COMMAND ${CMAKE_COMMAND} -E remove -f ${CMAKE_SOURCE_DIR}/LePhucDuc_CV.pdf
    COMMENT "Cleaning generated documentation and PDF"
    VERBATIM
)
