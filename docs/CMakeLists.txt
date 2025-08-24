add_custom_target(doc
    COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYGEN_OUT}
    COMMAND ${CMAKE_MAKE_PROGRAM} -C ${CMAKE_BINARY_DIR}/docs/latex -j
    BYPRODUCTS ${CMAKE_BINARY_DIR}/docs/latex/refman.pdf
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    USES_TERMINAL
    COMMENT "Generating PDF docs (Doxygen → LaTeX → PDF)"
    VERBATIM
)
