cmake_minimum_required(VERSION 3.18)
project(MyMath VERSION 1.0)

include(GNUInstallDirs)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Use -fPIC even if statically compiled
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Find Python3 and NumPy
find_package(Python3 COMPONENTS Interpreter Development.Module NumPy REQUIRED)

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

# =============
# SWIG bindings
# =============

cmake_policy(SET CMP0078 NEW)
cmake_policy(SET CMP0086 NEW)

find_package(SWIG 4.0 REQUIRED)
set(UseSWIG_MODULE_VERSION 2)
include(${SWIG_USE_FILE})

set(swig_name "bindings")
set_source_files_properties(bindings/${swig_name}.i PROPERTIES
    CPLUSPLUS ON
    SWIG_MODULE_NAME "bindings")

swig_add_library(${swig_name}
    TYPE MODULE
    LANGUAGE python
    OUTPUT_DIR ${CMAKE_CURRENT_BINARY_DIR}/mymath
    OUTFILE_DIR ${CMAKE_CURRENT_BINARY_DIR}
    SOURCES bindings/${swig_name}.i)

target_link_libraries(${swig_name}
    PRIVATE mymath Python3::NumPy)

set_target_properties(${swig_name} PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/mymath)

set_property(TARGET ${swig_name} PROPERTY
    SWIG_USE_TARGET_INCLUDE_DIRECTORIES TRUE)

set_property(TARGET ${swig_name}
    PROPERTY SWIG_COMPILE_OPTIONS -doxygen)

set_property(
    TARGET ${swig_name}
    PROPERTY SWIG_DEPENDS bindings/numpy.i)

# TODO: in the README explain why static, and how to overcome the problem
#       with RPATH support (+ link of gitlab)
# TODO: mention auditwheel
# TODO: this example can be adapted for pybind11, that however requires
#       manually wrapping all the exposed methods

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
if(CALL_FROM_SETUP_PY)
    # The CMakeExtension will set CMAKE_INSTALL_PREFIX to the root
    # of the resulting sdist / wheel archive
    set(MYMATH_INSTALL_PREFIX ${CMAKE_INSTALL_PREFIX})
else()
    # The Python package is installed directly in the folder of the
    # detected interpreter (system, user, or virtualenv)
    set(MYMATH_INSTALL_PREFIX ${Python3_SITELIB})
endif()

get_property(WRAPPER_PY_FILE
    TARGET ${swig_name}
    PROPERTY SWIG_SUPPORT_FILES)

# Install the .py file
install(
    FILES ${WRAPPER_PY_FILE}
    DESTINATION ${MYMATH_INSTALL_PREFIX})

# Install the SWIG library
install(
    TARGETS ${swig_name}
    LIBRARY DESTINATION ${MYMATH_INSTALL_PREFIX}
    ARCHIVE DESTINATION ${MYMATH_INSTALL_PREFIX}
    RUNTIME DESTINATION ${MYMATH_INSTALL_PREFIX})
