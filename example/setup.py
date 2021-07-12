import inspect
import os
import sys
from pathlib import Path

import cmake_build_extension
import setuptools

init_py = inspect.cleandoc(
    """
    import cmake_build_extension

    with cmake_build_extension.build_extension_env():
        from . import bindings
    """
)

# Extra options passed to the CI/CD pipeline that uses cibuildwheel
CIBW_CMAKE_OPTIONS = []
if "CIBUILDWHEEL" in os.environ and os.environ["CIBUILDWHEEL"] == "1":

    # The manylinux variant runs in Debian Stretch and it uses lib64 folder
    if sys.platform == "linux":
        CIBW_CMAKE_OPTIONS += ["-DCMAKE_INSTALL_LIBDIR=lib"]

    # Eigen is not found when installed with vcpkg because we don't pass the toolchain.
    # Passing directly the right folder as workaround. This is meant to work just in CI.
    if os.name == "nt":
        CIBW_CMAKE_OPTIONS += [
            "-DEigen3_DIR:PATH=C:/vcpkg/packages/eigen3_x64-windows/share/eigen3",
        ]

setuptools.setup(
    ext_modules=[
        cmake_build_extension.CMakeExtension(
            name="SwigBindings",
            install_prefix="mymath_swig",
            expose_binaries=["bin/print_answer"],
            write_top_level_init=init_py,
            source_dir=str(Path(__file__).parent.absolute()),
            cmake_configure_options=[
                f"-DPython3_ROOT_DIR={Path(sys.prefix)}",
                "-DCALL_FROM_SETUP_PY:BOOL=ON",
                "-DBUILD_SHARED_LIBS:BOOL=OFF",
                "-DEXAMPLE_WITH_SWIG:BOOL=ON",
                "-DEXAMPLE_WITH_PYBIND11:BOOL=OFF",
            ]
            + CIBW_CMAKE_OPTIONS,
        ),
        cmake_build_extension.CMakeExtension(
            name="Pybind11Bindings",
            install_prefix="mymath_pybind11",
            cmake_depends_on=["pybind11"],
            expose_binaries=["bin/print_answer"],
            write_top_level_init=init_py,
            source_dir=str(Path(__file__).parent.absolute()),
            cmake_configure_options=[
                f"-DPython3_ROOT_DIR={Path(sys.prefix)}",
                "-DCALL_FROM_SETUP_PY:BOOL=ON",
                "-DBUILD_SHARED_LIBS:BOOL=OFF",
                "-DEXAMPLE_WITH_SWIG:BOOL=OFF",
                "-DEXAMPLE_WITH_PYBIND11:BOOL=ON",
            ]
            + CIBW_CMAKE_OPTIONS,
        ),
    ],
    cmdclass=dict(build_ext=cmake_build_extension.BuildExtension),
)
