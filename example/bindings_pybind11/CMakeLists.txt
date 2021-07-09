find_package(pybind11 REQUIRED)
find_package(Eigen3 REQUIRED NO_MODULE)

# =======
# Library
# =======

# Create the pybind11 library
pybind11_add_module(pybind11_bindings MODULE bindings.cpp)

target_link_libraries(pybind11_bindings
    PRIVATE MyMath::mymath Eigen3::Eigen)

# The name of the shared library must match the module name
set_target_properties(pybind11_bindings PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/mymath
    OUTPUT_NAME "bindings")

# =======
# Install
# =======

# Install the pybind11 library
install(
    TARGETS pybind11_bindings
    LIBRARY DESTINATION ${MYMATH_INSTALL_PREFIX}
    ARCHIVE DESTINATION ${MYMATH_INSTALL_PREFIX}
    RUNTIME DESTINATION ${MYMATH_INSTALL_PREFIX})
