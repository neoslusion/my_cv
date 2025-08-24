#[=======================================================================[
Checking for current Python version

    Extracts the Python version from a given Python executable by running
    '--version' and parsing the output. Sets the result in the provided VERSION_VAR
    in the parent scope or warns if the version cannot be determined.

#]=======================================================================]

find_program(SYSTEM_PYTHON_EXECUTABLE
    NAMES python3 python
    DOC "System Python executable"
)

if(SYSTEM_PYTHON_EXECUTABLE)
    message(STATUS "Python Executable found, checking for the current version.")
    execute_process(
        COMMAND "${SYSTEM_PYTHON_EXECUTABLE}" --version
        OUTPUT_VARIABLE PYTHON_VERSION_OUTPUT
        ERROR_VARIABLE PYTHON_VERSION_OUTPUT
        RESULT_VARIABLE PYTHON_VERSION_RESULT
    )
    if(PYTHON_VERSION_RESULT EQUAL 0)
        string(REGEX MATCH "Python ([0-9]+\\.[0-9]+\\.[0-9]+)" VERSION "${PYTHON_VERSION_OUTPUT}")
        set(${PYTHON_VERSION_OUTPUT} "${CMAKE_MATCH_1}")
        message(STATUS "Found Python version: ${PYTHON_VERSION_OUTPUT}")
    else()
        message(WARNING "Failed to determine Python version from ${EXECUTABLE}")
    endif()
else()
    message(FATAL_ERROR "Python Executable is not found, please make sure to install Python in order to deploy Virtual Environment")
endif()

#[=======================================================================[
Check if the environment is externally managed

    Locates the system Python executable and determines if it is externally managed.
    This is to avoid breaking system package, we will use venv instead.
    Uses file existence or a pip dry-run test to detect this state, setting
    IS_EXTERNALLY_MANAGED accordingly. Warns if Python is not found.

#]=======================================================================]

if(NOT SYSTEM_PYTHON_EXECUTABLE)
    message(WARNING "System Python not found; assuming non-externally managed environment")
    set(IS_EXTERNALLY_MANAGED FALSE)
else()
    # Check if Python environment is externally managed
    set(EXTERNALLY_MANAGED_FILE "/usr/lib/python${PYTHON_VERSION}/EXTERNALLY-MANAGED")
    if(EXISTS "${EXTERNALLY_MANAGED_FILE}")
        set(IS_EXTERNALLY_MANAGED TRUE)
        message(STATUS "Detected EXTERNALLY-MANAGED file at ${EXTERNALLY_MANAGED_FILE}. Forcing venv usage.")
    else()
        set(IS_EXTERNALLY_MANAGED FALSE)
        message(STATUS "No EXTERNALLY-MANAGED file found for Python ${PYTHON_VERSION}.")
    endif()
    
    # Found python and assuming that the environment is not externally managed
    if(SYSTEM_PYTHON_EXECUTABLE AND NOT IS_EXTERNALLY_MANAGED)
        execute_process(
            COMMAND "${SYSTEM_PYTHON_EXECUTABLE}" -m pip install --dry-run --user nonexistentpackage123
            RESULT_VARIABLE PIP_TEST_RESULT
            OUTPUT_QUIET
            ERROR_VARIABLE PIP_TEST_ERROR
        )
        if(PIP_TEST_RESULT AND "${PIP_TEST_ERROR}" MATCHES "externally-managed-environment")
            set(IS_EXTERNALLY_MANAGED TRUE)
            message(STATUS "Pip indicates an externally managed environment. Forcing venv usage.")
        endif()
    endif()
endif()

