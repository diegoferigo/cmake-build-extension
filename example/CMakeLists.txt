cmake_minimum_required(VERSION 3.18.2)
project(MyMath VERSION 1.0)

# C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Common installation directories
include(GNUInstallDirs)

# Use -fPIC even if statically compiled
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# ============
# math library
# ============

# Create the mymath library
add_library(mymath
    src/mymath.h
    src/mymath.cpp)
add_library(MyMath::mymath ALIAS mymath)

set_target_properties(mymath PROPERTIES
    PUBLIC_HEADER src/mymath.h)

target_include_directories(mymath PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)

# =======================
# print_answer executable
# =======================

# Create the print_answer executable
add_executable(print_answer src/print_answer.cpp)

# =======
# Install
# =======

# See official documentation on exporting targets:
# https://cmake.org/cmake/help/latest/guide/importing-exporting/index.html#exporting-targets

# Install the target with C++ code
install(
    TARGETS mymath print_answer
    EXPORT MyMathTargets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

# Install the exported targets
install(
    EXPORT MyMathTargets
    FILE MyMathTargets.cmake
    NAMESPACE MyMath::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/MyMath)

# Create a CMake package
include(CMakePackageConfigHelpers)

# Prepare the Config.cmake.in content
set(PACKAGE_INIT_MACRO "@PACKAGE_INIT@")
set(CONFIG_CMAKE_IN "\
@PACKAGE_INIT_MACRO@\n\
include(\"\${CMAKE_CURRENT_LIST_DIR}/MyMathTargets.cmake\")\n\
check_required_components(MyMath)\n"
)

# Create Config.cmake.in
file(CONFIGURE
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/Config.cmake.in
    CONTENT ${CONFIG_CMAKE_IN}
    @ONLY)

# Create MyMathConfig.cmake
configure_package_config_file(
    ${CMAKE_CURRENT_BINARY_DIR}/Config.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/MyMathConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/MyMath)

# Create MyMathConfigVersion.cmake
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/MyMathConfigVersion.cmake"
    VERSION "${version}"
    COMPATIBILITY AnyNewerVersion
)

# Install CMake package files
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/MyMathConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/MyMathConfigVersion.cmake"
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/MyMath
)

# ===============
# Python bindings
# ===============

# Find Python3 and NumPy
find_package(Python3 COMPONENTS Interpreter Development.Module NumPy REQUIRED)

# Handle where to install the resulting Python package
if(CALL_FROM_SETUP_PY)
    # The CMakeExtension will set CMAKE_INSTALL_PREFIX to the root
    # of the resulting wheel archive
    set(MYMATH_INSTALL_PREFIX ${CMAKE_INSTALL_PREFIX})
else()
    # The Python package is installed directly in the folder of the
    # detected interpreter (system, user, or virtualenv)
    set(MYMATH_INSTALL_PREFIX ${Python3_SITELIB})
endif()

# =============
# SWIG bindings
# =============

if(EXAMPLE_WITH_SWIG)
    # Rename the executable
    set_target_properties(print_answer PROPERTIES OUTPUT_NAME print_answer_swig)

    # Add the bindings
    add_subdirectory(bindings_swig)
endif()

# =================
# Pybind11 bindings
# =================

if(EXAMPLE_WITH_PYBIND11)
    # Rename the executable
    set_target_properties(print_answer PROPERTIES OUTPUT_NAME print_answer_pybind11)

    # Add the bindings
    add_subdirectory(bindings_pybind11)
endif()
