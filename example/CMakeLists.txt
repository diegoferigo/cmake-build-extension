cmake_minimum_required(VERSION 3.18)
project(MyMath VERSION 1.0)

include(GNUInstallDirs)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Use -fPIC even if statically compiled
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# ============
# math library
# ============

add_library(mymath
    src/mymath.h
    src/mymath.cpp)

set_target_properties(mymath PROPERTIES
    PUBLIC_HEADER src/mymath.h)

target_include_directories(mymath PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)

# =======================
# print_answer executable
# =======================

add_executable(print_answer src/print_answer.cpp)

# =======
# Install
# =======

# Install the target with C++ code
install(
    TARGETS mymath print_answer
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

# Handle where to install the resulting Python package
#if(CALL_FROM_SETUP_PY)
    # The CMakeExtension will set CMAKE_INSTALL_PREFIX to the root
    # of the resulting sdist / wheel archive
#    set(MYMATH_INSTALL_PREFIX ${CMAKE_INSTALL_PREFIX})
#else()
    # The Python package is installed directly in the folder of the
    # detected interpreter (system, user, or virtualenv)
#    set(MYMATH_INSTALL_PREFIX ${Python3_SITELIB})
#endif()

# =============
# SWIG bindings
# =============

if(EXAMPLE_WITH_SWIG)
    add_subdirectory(bindings_swig)
endif()

# TODO: in the README explain why static, and how to overcome the problem
#       with RPATH support (+ link of gitlab)
# TODO: mention auditwheel
# TODO: this example can be adapted for pybind11, that however requires
#       manually wrapping all the exposed methods
